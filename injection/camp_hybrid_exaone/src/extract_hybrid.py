"""Hybrid 특징 추출 — attention token-pair(yeon의 Enc-first 입력)와 hidden state를
한 forward pass에서 같이 뽑는다 (재추출 비용 2배 방지).

배경: alignsentinel_replicate(yeon)의 EXAONE-Deep-7.8B Enc-first(토큰쌍을 먼저
인코딩한 뒤 mean-pool)가 pooled Acc 0.967로 지금까지 최고 결과. 여기에 hidden-state를
같이 얹어 더 오르는지 보려면, 같은 forward에서 attention과 hidden을 동시에 저장해야
한다(따로 두 번 뽑으면 GPU 비용 2배).

저장:
  {split}_{domain}_pairs.npy   (n, K, LH) fp16   — yeon extract_features.py와 동일 로직
                                (전체 토큰쌍 중 K개 균등 무작위 서브샘플)
  {split}_{domain}_hidden.npy  (n, S, hidden) fp16 — diag_extract.py와 동일 로직
                                (레이어 비율 × {toolmean, last} 풀링)
  {split}_{domain}_meta.json   ids/labels/cmodes/agent_ids

실행 (소규모 스모크 — 도메인당 N건만):
  python src/extract_hybrid.py --model-key qwen --out dump_hybrid \
      --splits train test --limit-per-group 20 --max-pairs 256

실행 (본 실험 — yeon과 동일 backend):
  python src/extract_hybrid.py --model-key exaone --trust-remote-code \
      --out dump_hybrid_exaone --splits train test --max-pairs 1024
"""

from __future__ import annotations

import argparse
import json
import time
from collections import defaultdict
from pathlib import Path

import numpy as np

import diag_common as C


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--data", nargs="+", default=["data/full_train.json", "data/full_test.json"])
    p.add_argument("--out", default="dump_hybrid")
    p.add_argument("--model", default=None)
    p.add_argument("--model-key", default="qwen")
    p.add_argument("--trust-remote-code", action="store_true")
    p.add_argument("--tool-msg-mode", default="auto", choices=["auto", "separate", "merged"])
    p.add_argument("--splits", nargs="+", default=["train", "test"])
    p.add_argument("--domains", nargs="*", default=None)
    p.add_argument("--limit-per-group", type=int, default=None,
                   help="(split,domain)별 샘플 수 제한 — 스모크 테스트용. 미지정 시 전체")
    p.add_argument("--max-pairs", type=int, default=1024, help="샘플당 저장할 토큰쌍 수(K)")
    p.add_argument("--hs-fracs", nargs="+", type=float, default=[0.25, 0.5, 0.75, 1.0],
                   help="hidden state를 뽑을 레이어 깊이 비율")
    p.add_argument("--hs-segments", type=int, default=1,
                   help="tool_response를 N등분해 구간별로 hidden mean-pool (기본 1=기존 toolmean과 동일). "
                        "N>1이면 위치 프로파일을 hidden에 반영(attn의 mean-pool이 버리는 위치 정보 보완)")
    p.add_argument("--token-hidden", action="store_true",
                   help="tool-response 토큰별 hidden state(한 층)도 저장 (hidden 토큰-단위 인코딩용)")
    p.add_argument("--token-hidden-frac", type=float, default=0.75,
                   help="토큰 단위 hidden을 뽑을 레이어 깊이 비율")
    p.add_argument("--token-max-len", type=int, default=128,
                   help="토큰 단위 hidden 저장 시 tool-response 토큰 최대 길이(앞에서부터 truncate)")
    p.add_argument("--max-seq-len", type=int, default=4096)
    p.add_argument("--dtype", default="bfloat16", choices=["bfloat16", "float16", "float32"])
    p.add_argument("--device", default="cuda")
    p.add_argument("--seed", type=int, default=42)
    args = p.parse_args()
    args.model, args.trust_remote_code = C.resolve_model_args(args.model_key, args.model, args.trust_remote_code)
    return args


def main():
    args = parse_args()
    import torch
    from tqdm import tqdm

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    rng_np = np.random.default_rng(args.seed)

    model, tokenizer = C.load_model_and_tokenizer(
        args.model, args.dtype, args.device, args.trust_remote_code)
    L = model.config.num_hidden_layers
    H = model.config.num_attention_heads
    hidden = model.config.hidden_size
    LH = L * H
    apply_template = C.make_apply_template(tokenizer)
    layer_idxs = sorted({max(1, min(L, round(f * L))) for f in args.hs_fracs})
    n_seg = max(1, args.hs_segments)
    pools = [f"seg{i}" for i in range(n_seg)] + ["last"]  # n_seg=1이면 seg0=기존 toolmean과 동일
    hs_cols = [(li, pl) for li in layer_idxs for pl in pools]
    S = len(hs_cols)
    tok_layer_idx = max(1, min(L, round(args.token_hidden_frac * L))) if args.token_hidden else None
    print(f"L={L} H={H} LH={LH} hidden={hidden} max_pairs={args.max_pairs} | "
          f"hs layers={layer_idxs} pools={pools} → S={S}"
          + (f" | token_hidden layer={tok_layer_idx} max_len={args.token_max_len}" if args.token_hidden else ""))

    records = C.load_records(args.data)
    tool_msg_mode = C.resolve_tool_msg_mode(args.tool_msg_mode, apply_template, records[0])

    groups: dict[tuple, list] = defaultdict(list)
    for r in records:
        if r["split"] not in args.splits:
            continue
        if args.domains and r["domain"] not in args.domains:
            continue
        groups[(r["split"], r["domain"])].append(r)

    run_meta = {
        "model": args.model, "model_key": args.model_key, "tool_msg_mode": tool_msg_mode,
        "L": L, "H": H, "LH": LH, "hidden": hidden, "max_pairs": args.max_pairs,
        "hs_layer_idxs": layer_idxs, "hs_pools": pools,
        "hs_cols": [f"L{li}_{pl}" for (li, pl) in hs_cols],
        "label_to_id": C.LABEL_TO_ID, "cmode_to_id": C.CMODE_TO_ID,
        "limit_per_group": args.limit_per_group, "splits": args.splits,
        "token_hidden": args.token_hidden, "token_hidden_layer": tok_layer_idx,
        "token_max_len": args.token_max_len if args.token_hidden else None,
    }
    with open(out_dir / "run_meta.json", "w", encoding="utf-8") as f:
        json.dump(run_meta, f, ensure_ascii=False, indent=2)

    for (split, domain), recs in sorted(groups.items()):
        meta_path = out_dir / f"{split}_{domain}_meta.json"
        if meta_path.exists():
            print(f"[skip] {split}/{domain} — meta 존재 (재실행하려면 파일 삭제)")
            continue
        if args.limit_per_group:
            recs = recs[: args.limit_per_group]
        n = len(recs)
        K = args.max_pairs
        pairs_path = out_dir / f"{split}_{domain}_pairs.npy"
        pairs_arr = np.lib.format.open_memmap(pairs_path, mode="w+", dtype=np.float16, shape=(n, K, LH))
        hs_arr = np.zeros((n, S, hidden), dtype=np.float16)
        if args.token_hidden:
            tok_arr = np.zeros((n, args.token_max_len, hidden), dtype=np.float16)
            tok_mask = np.zeros((n, args.token_max_len), dtype=np.int8)
        meta: dict = {"model": args.model, "L": L, "H": H, "max_pairs": K, "hs_cols": run_meta["hs_cols"],
                      "ids": [], "labels": [], "cmodes": [], "agent_ids": [],
                      "n_pairs_original": [], "skipped": []}

        t0, row = time.time(), 0
        for r in tqdm(recs, desc=f"{split}/{domain}"):
            text = apply_template(C.build_messages(r, tool_msg_mode))
            try:
                (u_a, u_b), (x_a, x_b) = C.locate_spans(text, r["user_prompt"], r["tool_response"])
            except ValueError:
                meta["skipped"].append(r["id"])
                continue
            enc = tokenizer(text, return_offsets_mapping=True, return_tensors="pt",
                            truncation=True, max_length=args.max_seq_len, add_special_tokens=False)
            offsets = enc.pop("offset_mapping")[0].tolist()
            s_idx = C.char_span_to_token_indices(offsets, u_a, u_b)   # user keys
            x_idx = C.char_span_to_token_indices(offsets, x_a, x_b)   # tool queries
            if not s_idx or not x_idx:
                meta["skipped"].append(r["id"])
                continue

            enc = {k: v.to(model.device) for k, v in enc.items()}
            with torch.no_grad():
                outputs = model(**enc, output_attentions=True, output_hidden_states=True, use_cache=False)

            x_t = torch.tensor(x_idx, device=model.device)
            s_t = torch.tensor(s_idx, device=model.device)

            # ---- attention token-pair 서브샘플 (yeon extract_features.py와 동일 로직) ----
            blocks = []
            for att in outputs.attentions:
                blk = att[0].index_select(1, x_t).index_select(2, s_t)  # (H,|x|,|s|)
                blocks.append(blk.float())
            A = torch.stack(blocks, dim=0)  # (L,H,|x|,|s|)
            Z = A.permute(2, 3, 0, 1).reshape(-1, LH)  # (P, LH)
            P = Z.shape[0]
            sel = rng_np.choice(P, size=K, replace=(P < K))
            pairs_arr[row] = Z[torch.tensor(np.sort(sel), device=Z.device)].cpu().numpy().astype(np.float16)
            meta["n_pairs_original"].append(int(P))
            del A, blocks

            # ---- hidden state 풀링 (n_seg=1: 기존 toolmean/last와 동일. n_seg>1: tool_response를
            #      N등분해서 구간별 mean-pool → attn의 mean-pool이 버리는 위치 정보를 hidden에 보존) ----
            n_x = x_t.shape[0]
            seg_bounds = torch.linspace(0, n_x, n_seg + 1).round().long()
            for li in layer_idxs:
                h = outputs.hidden_states[li][0]  # (T,hidden)
                x_h = h.index_select(0, x_t)      # (n_x,hidden) — tool_response 토큰만
                for s in range(n_seg):
                    a, b = seg_bounds[s].item(), max(seg_bounds[s + 1].item(), seg_bounds[s].item() + 1)
                    c = hs_cols.index((li, f"seg{s}"))
                    hs_arr[row, c] = x_h[a:b].mean(0).float().cpu().numpy().astype(np.float16)
                c_last = hs_cols.index((li, "last"))
                hs_arr[row, c_last] = h[-1].float().cpu().numpy().astype(np.float16)

            if args.token_hidden:
                h_tok = outputs.hidden_states[tok_layer_idx][0]  # (T,hidden)
                seq = h_tok.index_select(0, x_t)[: args.token_max_len]  # (m<=maxlen, hidden)
                m = seq.shape[0]
                tok_arr[row, :m] = seq.float().cpu().numpy().astype(np.float16)
                tok_mask[row, :m] = 1
            del outputs

            meta["ids"].append(r["id"])
            meta["labels"].append(C.LABEL_TO_ID[r["label"]])
            meta["cmodes"].append(C.CMODE_TO_ID[r["construction_mode"]])
            meta["agent_ids"].append(r["agent_id"])
            row += 1

        pairs_arr.flush()
        np.save(out_dir / f"{split}_{domain}_hidden.npy", hs_arr[:row])
        if args.token_hidden:
            np.save(out_dir / f"{split}_{domain}_hidden_tok.npy", tok_arr[:row])
            np.save(out_dir / f"{split}_{domain}_hidden_tok_mask.npy", tok_mask[:row])
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False)
        print(f"[done] {split}/{domain}: {row}/{n} in {time.time()-t0:.0f}s "
              f"(skipped {len(meta['skipped'])}) → {pairs_path.name}, {split}_{domain}_hidden.npy")

    print(f"\n추출 완료 → {out_dir}/  (다음: python src/train_hybrid.py --features {out_dir})")


if __name__ == "__main__":
    main()
