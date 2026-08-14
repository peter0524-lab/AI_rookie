"""진단용 추출 (GPU 1회 패스).

한 forward에서 두 종류의 신호를 뽑아 dump/ 에 저장한다:

  (1) g 통계  — tool→user grounding.
      g[l,h,i] = Σ_{j∈user} attention(query=tool토큰 i, key=user토큰 j)
               = tool 토큰 i가 상위 지시(user)에 보낸 attention 비율.
      head별로 tool 토큰 축을 요약: g_mean, g_std, g_max, 그리고
      위치 프로파일 g_prof(B bins, head↔tail 구조 보존).
      → 진단①(판별력) · 진단②(부호/스팬).

  (2) hidden state — 몇 개 레이어에서 tool 토큰 평균 / 마지막 토큰 풀링.
      → 진단③(hidden-state 프로브 = attention이 넘어야 할 바닥선).

기본은 qwen(비 gated), train split, 라벨당 도메인당 N개 균형 샘플. 소규모라 로컬/서버 모두 가볍게 돈다.

실행:
  python src/diag_extract.py --model-key qwen --out dump \
      --splits train --per-class 100 --bins 10
"""

from __future__ import annotations

import argparse
import json
import random
import time
from collections import defaultdict
from pathlib import Path

import numpy as np

import diag_common as C


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--data", nargs="+", default=["data/full_train.json", "data/full_test.json"])
    p.add_argument("--out", default="dump")
    p.add_argument("--model", default=None)
    p.add_argument("--model-key", default="qwen")
    p.add_argument("--trust-remote-code", action="store_true")
    p.add_argument("--tool-msg-mode", default="auto", choices=["auto", "separate", "merged"])
    p.add_argument("--splits", nargs="+", default=["train"], help="추출할 split (train/test)")
    p.add_argument("--domains", nargs="*", default=None, help="지정 시 해당 도메인만")
    p.add_argument("--per-class", type=int, default=100,
                   help="(split,domain,label)별 샘플 수. misaligned는 append/replace 반반")
    p.add_argument("--bins", type=int, default=10, help="g 위치 프로파일 bin 수")
    p.add_argument("--hs-fracs", nargs="+", type=float, default=[0.25, 0.5, 0.75, 1.0],
                   help="hidden state를 뽑을 레이어 깊이 비율")
    p.add_argument("--max-seq-len", type=int, default=4096)
    p.add_argument("--dtype", default="bfloat16", choices=["bfloat16", "float16", "float32"])
    p.add_argument("--device", default="cuda")
    p.add_argument("--seed", type=int, default=42)
    args = p.parse_args()
    args.model, args.trust_remote_code = C.resolve_model_args(args.model_key, args.model, args.trust_remote_code)
    return args


def bin_profile(x: np.ndarray, B: int) -> np.ndarray:
    """(LH, m) g 시퀀스를 (LH, B) 위치 프로파일로. m>=B면 구간평균, 아니면 선형보간."""
    LH, m = x.shape
    if m == 0:
        return np.zeros((LH, B), dtype=np.float32)
    if m >= B:
        edges = np.linspace(0, m, B + 1).astype(int)
        cols = [x[:, edges[b]:max(edges[b] + 1, edges[b + 1])].mean(1) for b in range(B)]
        return np.stack(cols, axis=1).astype(np.float32)
    xp = np.linspace(0.0, 1.0, m)
    xq = np.linspace(0.0, 1.0, B)
    return np.stack([np.interp(xq, xp, x[i]) for i in range(LH)], axis=0).astype(np.float32)


def sample_group(recs, per_class, rng: random.Random):
    """(domain 내) 라벨 균형 샘플. misaligned는 append/replace 반반."""
    by_label = defaultdict(list)
    for r in recs:
        by_label[r["label"]].append(r)
    out = []
    for label, rs in by_label.items():
        if label == "misaligned":
            ap = [r for r in rs if r["construction_mode"] == "misaligned_append"]
            rp = [r for r in rs if r["construction_mode"] == "misaligned_replace"]
            rng.shuffle(ap); rng.shuffle(rp)
            out += ap[: per_class // 2] + rp[: per_class - per_class // 2]
        else:
            rng.shuffle(rs)
            out += rs[:per_class]
    return out


def main():
    args = parse_args()
    import torch
    from tqdm import tqdm

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    rng = random.Random(args.seed)

    model, tokenizer = C.load_model_and_tokenizer(
        args.model, args.dtype, args.device, args.trust_remote_code)
    L = model.config.num_hidden_layers
    H = model.config.num_attention_heads
    hidden = model.config.hidden_size
    LH = L * H
    B = args.bins
    apply_template = C.make_apply_template(tokenizer)
    # hidden_states 인덱스(0=임베딩, 1..L=각 레이어). frac→레이어 인덱스
    layer_idxs = sorted({max(1, min(L, round(f * L))) for f in args.hs_fracs})
    pools = ["toolmean", "last"]
    hs_cols = [(li, pl) for li in layer_idxs for pl in pools]  # S = len*2
    S = len(hs_cols)
    print(f"L={L} H={H} LH={LH} hidden={hidden} | hs layers={layer_idxs} pools={pools} → S={S}")

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
        "L": L, "H": H, "LH": LH, "hidden": hidden, "bins": B,
        "hs_layer_idxs": layer_idxs, "hs_pools": pools,
        "hs_cols": [f"L{li}_{pl}" for (li, pl) in hs_cols],
        "label_to_id": C.LABEL_TO_ID, "cmode_to_id": C.CMODE_TO_ID,
        "per_class": args.per_class, "splits": args.splits,
    }
    with open(out_dir / "run_meta.json", "w", encoding="utf-8") as f:
        json.dump(run_meta, f, ensure_ascii=False, indent=2)

    for (split, domain), recs in sorted(groups.items()):
        npz_path = out_dir / f"{split}_{domain}.npz"
        if npz_path.exists():
            print(f"[skip] {split}/{domain} — 이미 있음")
            continue
        sel = sample_group(recs, args.per_class, rng)
        n = len(sel)
        g_mean = np.zeros((n, LH), np.float16)
        g_std = np.zeros((n, LH), np.float16)
        g_max = np.zeros((n, LH), np.float16)
        g_prof = np.zeros((n, LH, B), np.float16)
        hs = np.zeros((n, S, hidden), np.float16)
        labels, cmodes, ids, agents, tool_lens = [], [], [], [], []

        t0, row = time.time(), 0
        for r in tqdm(sel, desc=f"{split}/{domain}"):
            text = apply_template(C.build_messages(r, tool_msg_mode))
            try:
                (u_a, u_b), (x_a, x_b) = C.locate_spans(text, r["user_prompt"], r["tool_response"])
            except ValueError:
                continue
            enc = tokenizer(text, return_offsets_mapping=True, return_tensors="pt",
                            truncation=True, max_length=args.max_seq_len, add_special_tokens=False)
            offsets = enc.pop("offset_mapping")[0].tolist()
            s_idx = C.char_span_to_token_indices(offsets, u_a, u_b)  # user keys
            x_idx = C.char_span_to_token_indices(offsets, x_a, x_b)  # tool queries
            if not s_idx or not x_idx:
                continue
            enc = {k: v.to(model.device) for k, v in enc.items()}
            with torch.no_grad():
                outputs = model(**enc, output_attentions=True, output_hidden_states=True, use_cache=False)

            x_t = torch.tensor(x_idx, device=model.device)
            s_t = torch.tensor(s_idx, device=model.device)
            # g: 레이어별 (H,|x|,|s|) → user키 합 → (H,|x|), 적층 (L,H,|x|)
            g_layers = []
            for att in outputs.attentions:
                a = att[0]  # (H,T,T)  dim1=query, dim2=key
                g = a.index_select(1, x_t).index_select(2, s_t).sum(dim=2)  # (H,|x|)
                g_layers.append(g.float())
            G = torch.stack(g_layers, dim=0).reshape(LH, -1).cpu().numpy()  # (LH,|x|)
            g_mean[row] = G.mean(1).astype(np.float16)
            g_std[row] = G.std(1).astype(np.float16)
            g_max[row] = G.max(1).astype(np.float16)
            g_prof[row] = bin_profile(G, B).astype(np.float16)

            for c, (li, pl) in enumerate(hs_cols):
                h = outputs.hidden_states[li][0]  # (T,hidden)
                vec = h.index_select(0, x_t).mean(0) if pl == "toolmean" else h[-1]
                hs[row, c] = vec.float().cpu().numpy().astype(np.float16)
            del outputs

            labels.append(C.LABEL_TO_ID[r["label"]])
            cmodes.append(C.CMODE_TO_ID[r["construction_mode"]])
            ids.append(r["id"]); agents.append(r["agent_id"]); tool_lens.append(len(x_idx))
            row += 1

        np.savez_compressed(
            npz_path,
            g_mean=g_mean[:row], g_std=g_std[:row], g_max=g_max[:row], g_prof=g_prof[:row],
            hs=hs[:row], labels=np.array(labels, np.int64), cmodes=np.array(cmodes, np.int64),
            tool_lens=np.array(tool_lens, np.int64),
            ids=np.array(ids), agents=np.array(agents), domain=domain, split=split)
        print(f"[done] {split}/{domain}: {row}/{n} in {time.time()-t0:.0f}s → {npz_path.name}")

    print(f"\n추출 완료 → {out_dir}/  (다음: python src/diag_analyze.py --dump {out_dir})")


if __name__ == "__main__":
    main()
