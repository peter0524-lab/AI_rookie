"""
Paired three-class feature extraction for Korean indirect prompt injection.

This script has two stages:

1. head-stats
   Extracts per-sample head summaries u_{b,v,l,h}: top-R mean attention
   over the tool-response x user-prompt token-pair region.

2. pair-features
   Uses train-only paired head sets to extract branch-specific Enc-first
   features for a hierarchical detector:
     - instruction branch: selected instruction heads over S_I union S_R
     - conflict branch: selected conflict heads over S_C union S_R

The original AlignSentinel extractor is left untouched. This script is an
experimental implementation of paired_three_class_ipi_methodology.pdf.
"""

from __future__ import annotations

import argparse
import json
import time
from collections import defaultdict
from pathlib import Path

import numpy as np

LABEL_TO_ID = {"misaligned": 0, "aligned": 1, "non_instruction": 2}
TOOL_RESPONSE_TEMPLATE = "<tool_response>\n{content}\n</tool_response>"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    def add_common(sp):
        sp.add_argument("--data", nargs="+", required=True, help="full_train.json full_test.json")
        sp.add_argument("--out", required=True)
        sp.add_argument("--model", default="skt/A.X-4.0-Light")
        sp.add_argument("--trust-remote-code", action="store_true")
        sp.add_argument("--tool-message-mode", default="auto", choices=["auto", "separate", "append"])
        sp.add_argument("--max-seq-len", type=int, default=4096)
        sp.add_argument("--dtype", default="bfloat16", choices=["bfloat16", "float16", "float32"])
        sp.add_argument("--device", default="cuda")
        sp.add_argument("--seed", type=int, default=42)
        sp.add_argument("--domains", nargs="*", default=None)
        sp.add_argument("--limit-per-group", type=int, default=None)

    s1 = sub.add_parser("head-stats", help="extract top-R head summaries")
    add_common(s1)
    s1.add_argument("--top-r", type=int, default=32)

    s2 = sub.add_parser("pair-features", help="extract head-guided pair features")
    add_common(s2)
    s2.add_argument("--heads", required=True, help="heads JSON from select_paired_heads.py")
    s2.add_argument("--max-pairs", type=int, default=1024)
    s2.add_argument("--ki", type=int, default=None, help="instruction top pairs, default K/4")
    s2.add_argument("--kc", type=int, default=None, help="conflict top pairs, default K/4")
    s2.add_argument("--kr", type=int, default=None, help="random pairs, default K/2")
    return p.parse_args()


def char_span_to_token_indices(offsets: list[tuple[int, int]], start: int, end: int) -> list[int]:
    idx = []
    for i, (a, b) in enumerate(offsets):
        if a == b:
            continue
        if a < end and b > start:
            idx.append(i)
    return idx


def locate_spans(text: str, user_prompt: str, tool_response: str) -> tuple[tuple[int, int], tuple[int, int]]:
    u_start = text.find(user_prompt)
    if u_start < 0:
        raise ValueError("user_prompt not found in rendered chat")
    u_end = u_start + len(user_prompt)
    x_start = text.find(tool_response, u_end)
    if x_start < 0:
        raise ValueError("tool_response not found in rendered chat")
    return (u_start, u_end), (x_start, x_start + len(tool_response))


def append_tool_response_by_default(model_id: str) -> bool:
    return "mistral" in model_id.lower()


def build_messages(record: dict, append_tool_response: bool) -> list[dict[str, str]]:
    tool_message = TOOL_RESPONSE_TEMPLATE.format(content=record["tool_response"])
    if append_tool_response:
        return [
            {"role": "system", "content": record["system_prompt"]},
            {"role": "user", "content": f"{record['user_prompt']}\n\n{tool_message}"},
        ]
    return [
        {"role": "system", "content": record["system_prompt"]},
        {"role": "user", "content": record["user_prompt"]},
        {"role": "user", "content": tool_message},
    ]


def render_chat(tokenizer, messages: list[dict[str, str]]) -> str:
    try:
        return tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=False, enable_thinking=False
        )
    except TypeError:
        return tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)


def grouped_records(paths: list[str], domains: list[str] | None, limit_per_group: int | None):
    records = []
    for path in paths:
        with open(path, "r", encoding="utf-8") as f:
            records.extend(json.load(f))
    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for r in records:
        if domains and r["domain"] not in domains:
            continue
        groups[(r["split"], r["domain"])].append(r)
    for key in list(groups):
        if limit_per_group:
            groups[key] = groups[key][:limit_per_group]
    return groups


def load_model(args):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    print(f"loading {args.model} (attn_implementation=eager, dtype={args.dtype})")
    tokenizer = AutoTokenizer.from_pretrained(args.model, trust_remote_code=args.trust_remote_code)
    model = AutoModelForCausalLM.from_pretrained(
        args.model,
        torch_dtype=getattr(torch, args.dtype),
        attn_implementation="eager",
        device_map=args.device,
        trust_remote_code=args.trust_remote_code,
    )
    model.eval()
    L = model.config.num_hidden_layers
    H = model.config.num_attention_heads
    print(f"L={L} H={H} -> LH={L * H}")
    return tokenizer, model, L, H


def attention_block(record: dict, tokenizer, model, args, append_tool_response: bool):
    import torch

    messages = build_messages(record, append_tool_response)
    try:
        text = render_chat(tokenizer, messages)
    except Exception:
        if args.tool_message_mode != "auto" or append_tool_response:
            raise
        text = render_chat(tokenizer, build_messages(record, True))

    (u_a, u_b), (x_a, x_b) = locate_spans(text, record["user_prompt"], record["tool_response"])
    enc = tokenizer(
        text,
        return_offsets_mapping=True,
        return_tensors="pt",
        truncation=True,
        max_length=args.max_seq_len,
        add_special_tokens=False,
    )
    offsets = enc.pop("offset_mapping")[0].tolist()
    s_idx = char_span_to_token_indices(offsets, u_a, u_b)
    x_idx = char_span_to_token_indices(offsets, x_a, x_b)
    if not s_idx or not x_idx:
        return None

    enc = {k: v.to(model.device) for k, v in enc.items()}
    with torch.no_grad():
        outputs = model(**enc, output_attentions=True, use_cache=False)

    s_t = torch.tensor(s_idx, device=model.device)
    x_t = torch.tensor(x_idx, device=model.device)
    blocks = []
    for att in outputs.attentions:
        blocks.append(att[0].index_select(1, x_t).index_select(2, s_t).float())
    del outputs
    return torch.stack(blocks, dim=0)  # (L,H,|tool|,|user|)


def base_meta(args, L: int, H: int) -> dict:
    return {
        "model": args.model,
        "L": L,
        "H": H,
        "tool_message_mode": args.tool_message_mode,
        "ids": [],
        "labels": [],
        "agent_ids": [],
        "base_pair_ids": [],
        "construction_modes": [],
        "domains": [],
        "skipped": [],
    }


def append_meta(meta: dict, r: dict) -> None:
    meta["ids"].append(r["id"])
    meta["labels"].append(LABEL_TO_ID[r["label"]])
    meta["agent_ids"].append(r["agent_id"])
    meta["base_pair_ids"].append(r["base_pair_id"])
    meta["construction_modes"].append(r["construction_mode"])
    meta["domains"].append(r["domain"])


def run_head_stats(args) -> None:
    import torch
    from tqdm import tqdm

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    tokenizer, model, L, H = load_model(args)
    LH = L * H
    groups = grouped_records(args.data, args.domains, args.limit_per_group)
    append_default = (
        args.tool_message_mode == "append"
        or (args.tool_message_mode == "auto" and append_tool_response_by_default(args.model))
    )

    for (split, domain), recs in sorted(groups.items()):
        meta_path = out_dir / f"{split}_{domain}_meta.json"
        arr_path = out_dir / f"{split}_{domain}_head_top{args.top_r}.npy"
        if meta_path.exists() and arr_path.exists():
            print(f"[skip] {split}/{domain} head stats already exist")
            continue

        arr = np.zeros((len(recs), LH), dtype=np.float32)
        meta = base_meta(args, L, H)
        meta["top_r"] = args.top_r
        t0, row = time.time(), 0
        for r in tqdm(recs, desc=f"head {split}/{domain}"):
            A = attention_block(r, tokenizer, model, args, append_default)
            if A is None:
                meta["skipped"].append(r["id"])
                continue
            flat = A.reshape(LH, -1)
            k = min(args.top_r, flat.shape[1])
            vals = torch.topk(flat, k=k, dim=1).values.mean(dim=1)
            arr[row] = vals.cpu().numpy()
            append_meta(meta, r)
            row += 1
            del A, flat, vals
        np.save(arr_path, arr[:row])
        with meta_path.open("w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False)
        print(f"[done] head {split}/{domain}: {row}/{len(recs)} in {time.time()-t0:.0f}s")


def load_heads(path: str):
    with open(path, "r", encoding="utf-8") as f:
        h = json.load(f)
    mi = np.asarray(h["instruction"]["indices"], dtype=np.int64)
    mc = np.asarray(h["conflict"]["indices"], dtype=np.int64)
    wi = np.asarray(h["instruction"]["weights"], dtype=np.float32)
    wc = np.asarray(h["conflict"]["weights"], dtype=np.float32)
    si = np.asarray(h["instruction"]["signs"], dtype=np.float32)
    sc = np.asarray(h["conflict"]["signs"], dtype=np.float32)
    return h, mi, mc, wi, wc, si, sc


def fill_budget(args) -> tuple[int, int, int]:
    K = args.max_pairs
    ki = args.ki if args.ki is not None else K // 4
    kc = args.kc if args.kc is not None else K // 4
    kr = args.kr if args.kr is not None else K - ki - kc
    if ki < 0 or kc < 0 or kr < 0 or ki + kc + kr != K:
        raise SystemExit(f"invalid pair budgets: ki={ki}, kc={kc}, kr={kr}, K={K}")
    return ki, kc, kr


def choose_pairs(score, k: int, banned=None):
    import torch

    n = score.numel()
    if banned is not None and len(banned):
        score = score.clone()
        score[torch.as_tensor(sorted(banned), device=score.device, dtype=torch.long)] = -float("inf")
    k_eff = min(k, n)
    if k_eff <= 0:
        return torch.empty((0,), device=score.device, dtype=torch.long)
    return torch.topk(score, k=k_eff).indices


def random_pairs(P: int, k: int, banned: set[int], rng: np.random.Generator, device):
    import torch

    if k <= 0:
        return torch.empty((0,), device=device, dtype=torch.long)
    candidates = np.asarray([i for i in range(P) if i not in banned], dtype=np.int64)
    if len(candidates) == 0:
        candidates = np.arange(P, dtype=np.int64)
    sel = rng.choice(candidates, size=k, replace=(len(candidates) < k))
    return torch.as_tensor(np.sort(sel), device=device, dtype=torch.long)


def run_pair_features(args) -> None:
    import torch
    from tqdm import tqdm

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    heads, mi, mc, wi, wc, si, sc = load_heads(args.heads)
    tokenizer, model, L, H = load_model(args)
    if L != heads["L"] or H != heads["H"]:
        raise SystemExit(f"head file L/H={heads['L']}/{heads['H']} does not match model L/H={L}/{H}")

    ki, kc, kr = fill_budget(args)
    groups = grouped_records(args.data, args.domains, args.limit_per_group)
    rng = np.random.default_rng(args.seed)
    append_default = (
        args.tool_message_mode == "append"
        or (args.tool_message_mode == "auto" and append_tool_response_by_default(args.model))
    )

    mi_t = torch.as_tensor(mi, device=model.device, dtype=torch.long)
    mc_t = torch.as_tensor(mc, device=model.device, dtype=torch.long)
    wi_t = torch.as_tensor(wi, device=model.device).view(-1, 1)
    wc_t = torch.as_tensor(wc, device=model.device).view(-1, 1)
    si_t = torch.as_tensor(si, device=model.device).view(-1, 1)
    sc_t = torch.as_tensor(sc, device=model.device).view(-1, 1)

    for (split, domain), recs in sorted(groups.items()):
        meta_path = out_dir / f"{split}_{domain}_paired_meta.json"
        i_path = out_dir / f"{split}_{domain}_pairs_I.npy"
        c_path = out_dir / f"{split}_{domain}_pairs_C.npy"
        if meta_path.exists() and i_path.exists() and c_path.exists():
            print(f"[skip] {split}/{domain} paired features already exist")
            continue

        XI = np.lib.format.open_memmap(i_path, mode="w+", dtype=np.float16, shape=(len(recs), ki + kr, len(mi)))
        XC = np.lib.format.open_memmap(c_path, mode="w+", dtype=np.float16, shape=(len(recs), kc + kr, len(mc)))
        meta = base_meta(args, L, H)
        meta.update({
            "heads_file": str(args.heads),
            "max_pairs": args.max_pairs,
            "ki": ki,
            "kc": kc,
            "kr": kr,
            "instruction_heads": mi.tolist(),
            "conflict_heads": mc.tolist(),
            "n_pairs_original": [],
        })

        t0, row = time.time(), 0
        for r in tqdm(recs, desc=f"paired {split}/{domain}"):
            A = attention_block(r, tokenizer, model, args, append_default)
            if A is None:
                meta["skipped"].append(r["id"])
                continue
            flat = A.reshape(L * H, -1)
            P = flat.shape[1]
            mu = flat.mean(dim=1, keepdim=True)
            sd = flat.std(dim=1, keepdim=True).clamp_min(1e-8)
            eflat = (flat - mu) / sd

            eI = eflat.index_select(0, mi_t)
            eC = eflat.index_select(0, mc_t)
            rI = torch.clamp(si_t * eI, min=0.0).mul(wi_t).sum(dim=0)
            rC = torch.clamp(sc_t * eC, min=0.0).mul(wc_t).sum(dim=0)

            sI = choose_pairs(rI, ki)
            banned = set(int(x) for x in sI.detach().cpu().numpy())
            sC = choose_pairs(rC, kc, banned=banned)
            banned.update(int(x) for x in sC.detach().cpu().numpy())
            sR = random_pairs(P, kr, banned, rng, model.device)

            pairs_i = torch.cat([sI, sR])
            pairs_c = torch.cat([sC, sR])
            if len(pairs_i) < ki + kr:
                pad = random_pairs(P, ki + kr - len(pairs_i), set(), rng, model.device)
                pairs_i = torch.cat([pairs_i, pad])
            if len(pairs_c) < kc + kr:
                pad = random_pairs(P, kc + kr - len(pairs_c), set(), rng, model.device)
                pairs_c = torch.cat([pairs_c, pad])

            XI[row] = eI.index_select(1, pairs_i[:ki + kr]).T.cpu().numpy().astype(np.float16)
            XC[row] = eC.index_select(1, pairs_c[:kc + kr]).T.cpu().numpy().astype(np.float16)
            meta["n_pairs_original"].append(int(P))
            append_meta(meta, r)
            row += 1
            del A, flat, eflat, eI, eC, rI, rC

        XI.flush()
        XC.flush()
        with meta_path.open("w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False)
        print(f"[done] paired {split}/{domain}: {row}/{len(recs)} in {time.time()-t0:.0f}s")


def main() -> None:
    args = parse_args()
    if args.cmd == "head-stats":
        run_head_stats(args)
    elif args.cmd == "pair-features":
        run_pair_features(args)


if __name__ == "__main__":
    main()
