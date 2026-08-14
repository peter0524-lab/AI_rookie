"""
Conservative selected-head/top-k Enc-first feature extraction.

This keeps the original regularized Enc-first detector unchanged. Only the
attention feature surface is changed:

  full token-pair vector z_ij in R^{L*H}
    -> selected heads z_ij[M] from train-only paired head selection
    -> top-k token pairs scored by instruction/conflict head responses

Outputs are intentionally compatible with train_detector.py:
  {split}_{domain}_pairs.npy  shape (N, K, |M|)
  {split}_{domain}_meta.json
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np

from extract_paired_features import (
    append_meta,
    append_tool_response_by_default,
    attention_block,
    base_meta,
    grouped_records,
    load_heads,
    load_model,
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--data", nargs="+", required=True, help="full_train.json full_test.json")
    p.add_argument("--out", required=True)
    p.add_argument("--model", default="skt/A.X-4.0-Light")
    p.add_argument("--heads", required=True, help="paired_heads.json from select_paired_heads.py")
    p.add_argument("--trust-remote-code", action="store_true")
    p.add_argument("--tool-message-mode", default="auto", choices=["auto", "separate", "append"])
    p.add_argument("--max-seq-len", type=int, default=4096)
    p.add_argument("--dtype", default="bfloat16", choices=["bfloat16", "float16", "float32"])
    p.add_argument("--device", default="cuda")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--domains", nargs="*", default=None)
    p.add_argument("--limit-per-group", type=int, default=None)
    p.add_argument("--max-pairs", type=int, default=1024)
    p.add_argument("--top-pairs", type=int, default=None, help="score-based token pairs; default 3/4 of K")
    p.add_argument("--random-pairs", type=int, default=None, help="random token pairs; default K - top_pairs")
    p.add_argument("--head-mode", choices=["union", "conflict", "instruction"], default="union")
    p.add_argument("--score-mode", choices=["union", "conflict", "instruction"], default="union")
    p.add_argument("--max-heads", type=int, default=128)
    p.add_argument("--instruction-score-weight", type=float, default=0.5)
    p.add_argument("--conflict-score-weight", type=float, default=1.0)
    return p.parse_args()


def selected_head_indices(mi: np.ndarray, mc: np.ndarray, mode: str, max_heads: int) -> np.ndarray:
    if mode == "instruction":
        out = mi.tolist()
    elif mode == "conflict":
        out = mc.tolist()
    else:
        out = []
        seen = set()
        for idx in mc.tolist() + mi.tolist():
            if int(idx) not in seen:
                out.append(int(idx))
                seen.add(int(idx))
    if max_heads > 0:
        out = out[:max_heads]
    return np.asarray(out, dtype=np.int64)


def pair_budget(max_pairs: int, top_pairs: int | None, random_pairs: int | None) -> tuple[int, int]:
    if max_pairs <= 0:
        raise SystemExit("--max-pairs must be positive")
    if top_pairs is None and random_pairs is None:
        top_pairs = int(round(max_pairs * 0.75))
        random_pairs = max_pairs - top_pairs
    elif top_pairs is None:
        top_pairs = max_pairs - int(random_pairs)
    elif random_pairs is None:
        random_pairs = max_pairs - int(top_pairs)
    top_pairs, random_pairs = int(top_pairs), int(random_pairs)
    if top_pairs < 0 or random_pairs < 0 or top_pairs + random_pairs != max_pairs:
        raise SystemExit(
            f"invalid pair budget: top_pairs={top_pairs}, random_pairs={random_pairs}, max_pairs={max_pairs}"
        )
    return top_pairs, random_pairs


def random_indices(P: int, k: int, banned: set[int], rng: np.random.Generator, device):
    import torch

    if k <= 0:
        return torch.empty((0,), device=device, dtype=torch.long)
    candidates = np.asarray([i for i in range(P) if i not in banned], dtype=np.int64)
    if len(candidates) == 0:
        candidates = np.arange(P, dtype=np.int64)
    sel = rng.choice(candidates, size=k, replace=(len(candidates) < k))
    return torch.as_tensor(sel, device=device, dtype=torch.long)


def select_pairs(score, k_top: int, k_random: int, rng: np.random.Generator, device):
    import torch

    P = int(score.numel())
    if P <= 0:
        raise ValueError("empty token-pair region")
    top_k = min(k_top, P)
    top = torch.topk(score, k=top_k).indices if top_k > 0 else torch.empty((0,), device=device, dtype=torch.long)
    banned = set(int(x) for x in top.detach().cpu().numpy())
    rand = random_indices(P, k_random, banned, rng, device)
    pairs = torch.cat([top, rand])
    if len(pairs) < k_top + k_random:
        pad = random_indices(P, k_top + k_random - len(pairs), set(), rng, device)
        pairs = torch.cat([pairs, pad])
    return pairs[: k_top + k_random]


def main() -> None:
    import torch
    from tqdm import tqdm

    args = parse_args()
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    heads, mi, mc, wi, wc, si, sc = load_heads(args.heads)
    selected = selected_head_indices(mi, mc, args.head_mode, args.max_heads)
    if len(selected) == 0:
        raise SystemExit("no selected heads")
    k_top, k_random = pair_budget(args.max_pairs, args.top_pairs, args.random_pairs)

    tokenizer, model, L, H = load_model(args)
    if L != heads["L"] or H != heads["H"]:
        raise SystemExit(f"head file L/H={heads['L']}/{heads['H']} does not match model L/H={L}/{H}")

    groups = grouped_records(args.data, args.domains, args.limit_per_group)
    rng = np.random.default_rng(args.seed)
    append_default = (
        args.tool_message_mode == "append"
        or (args.tool_message_mode == "auto" and append_tool_response_by_default(args.model))
    )

    mi_t = torch.as_tensor(mi, device=model.device, dtype=torch.long)
    mc_t = torch.as_tensor(mc, device=model.device, dtype=torch.long)
    selected_t = torch.as_tensor(selected, device=model.device, dtype=torch.long)
    wi_t = torch.as_tensor(wi, device=model.device).view(-1, 1)
    wc_t = torch.as_tensor(wc, device=model.device).view(-1, 1)
    si_t = torch.as_tensor(si, device=model.device).view(-1, 1)
    sc_t = torch.as_tensor(sc, device=model.device).view(-1, 1)

    for (split, domain), recs in sorted(groups.items()):
        meta_path = out_dir / f"{split}_{domain}_meta.json"
        pairs_path = out_dir / f"{split}_{domain}_pairs.npy"
        if meta_path.exists() and pairs_path.exists():
            print(f"[skip] {split}/{domain} selected features already exist")
            continue

        X = np.lib.format.open_memmap(
            pairs_path, mode="w+", dtype=np.float16, shape=(len(recs), args.max_pairs, len(selected))
        )
        meta = base_meta(args, L, H)
        meta.update(
            {
                "method": "selected_head_topk_enc_first",
                "heads_file": str(args.heads),
                "head_mode": args.head_mode,
                "score_mode": args.score_mode,
                "max_heads": args.max_heads,
                "selected_heads": selected.tolist(),
                "max_pairs": args.max_pairs,
                "top_pairs": k_top,
                "random_pairs": k_random,
                "instruction_score_weight": args.instruction_score_weight,
                "conflict_score_weight": args.conflict_score_weight,
                "n_pairs_original": [],
            }
        )

        t0, row = time.time(), 0
        for r in tqdm(recs, desc=f"selected {split}/{domain}"):
            A = attention_block(r, tokenizer, model, args, append_default)
            if A is None:
                meta["skipped"].append(r["id"])
                continue

            flat = A.reshape(L * H, -1)
            mu = flat.mean(dim=1, keepdim=True)
            sd = flat.std(dim=1, keepdim=True, unbiased=False).clamp_min(1e-8)
            eflat = (flat - mu) / sd

            eI = eflat.index_select(0, mi_t)
            eC = eflat.index_select(0, mc_t)
            rI = torch.clamp(si_t * eI, min=0.0).mul(wi_t).sum(dim=0)
            rC = torch.clamp(sc_t * eC, min=0.0).mul(wc_t).sum(dim=0)
            if args.score_mode == "instruction":
                score = rI
            elif args.score_mode == "conflict":
                score = rC
            else:
                score = args.instruction_score_weight * rI + args.conflict_score_weight * rC

            pairs = select_pairs(score, k_top, k_random, rng, model.device)
            feat = eflat.index_select(0, selected_t).index_select(1, pairs).T
            X[row] = feat.cpu().numpy().astype(np.float16)

            meta["n_pairs_original"].append(int(flat.shape[1]))
            append_meta(meta, r)
            row += 1
            del A, flat, eflat, eI, eC, rI, rC, score, pairs, feat

        X.flush()
        with meta_path.open("w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False)
        print(f"[done] selected {split}/{domain}: {row}/{len(recs)} in {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
