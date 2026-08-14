"""8도메인 pooled 스케일 — hybrid concat(A) + attn_bigK(B) 앙상블, RAM 상주 방식.

배경: coding 도메인 하나로 attn_bigK(K=2048, 낮은 FPR)와 hybrid-concat(K=1024+hidden,
낮은 FNR)를 앙상블(확률 평균)했더니 둘 다 baseline보다 낮아졌다(FPR 0.075/FNR 0.010).
이걸 8도메인 pooled(train 25,600 / test 6,400) 규모로 재검증한다.

디스크를 전혀 쓰지 않는 이유:
  - forward pass를 한 번만 돌려 K=2048 토큰쌍을 뽑고, K=1024가 필요한 곳(hybrid concat)에는
    그 배열의 앞 1024개를 그대로 슬라이스해서 쓴다 — v1/v2 두 번 추출할 필요가 없다
    (추출 시간 절반, RAM도 179GB→약 120GB로 감소).
  - 8도메인분을 디스크에 다 쓰고 다시 읽으면 그만큼 I/O 낭비이므로, 추출 결과를
    바로 전역 RAM 배열(fp16)에 채워 넣는다. 디스크에는 메타/결과 리포트만 남는다.

메모리 안전장치:
  - 학습 시 전체 배열을 float32로 한 번에 올리지 않는다. CPU에 fp16으로 유지하고
    배치 단위로만 float32 변환 + GPU 이동한다.
  - 표준화(평균/표준편차)도 전체를 한 번에 upcast하지 않고 청크 단위로 누적 계산한다
    (streaming mean/std) — 순간적으로도 전체 이중 사본이 생기지 않게.

주의: 이 스크립트는 아직 실행되지 않았다(준비만 됨) — 처음 실행이 곧 최초 테스트다.
사용자가 시작하라고 할 때까지 호출하지 말 것.

실행:
  python src/run_pooled_ensemble.py --out results_pooled_ensemble
"""

from __future__ import annotations

import argparse
import gc
import json
import time
from collections import defaultdict
from pathlib import Path

import numpy as np

import diag_common as C
from train_hybrid import build_model as build_model_v1, stratified_train_val, metrics_from_preds
from train_hybrid_v2 import make_mean_pool_attn

ALL_DOMAINS = ["cloud", "coding", "finance", "messaging", "project", "shopping", "social_media", "web"]


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--data", nargs="+", default=["data/full_train.json", "data/full_test.json"])
    p.add_argument("--model-key", default="exaone-1.2b")
    p.add_argument("--trust-remote-code", action="store_true", default=True)
    p.add_argument("--domains", nargs="*", default=None, help="미지정 시 8개 전체")
    p.add_argument("--max-pairs", type=int, default=2048, help="K (attn_bigK / v2)")
    p.add_argument("--k-small", type=int, default=1024, help="hybrid concat용 K (max-pairs의 앞부분 슬라이스)")
    p.add_argument("--hs-fracs", nargs="+", type=float, default=[0.25, 0.5, 0.75, 1.0])
    p.add_argument("--tool-msg-mode", default="auto", choices=["auto", "separate", "merged"])
    p.add_argument("--max-seq-len", type=int, default=4096)
    p.add_argument("--dtype", default="bfloat16", choices=["bfloat16", "float16", "float32"])
    p.add_argument("--device", default="cuda")
    p.add_argument("--out", default="results_pooled_ensemble")
    # 학습
    p.add_argument("--epochs", type=int, default=200)
    p.add_argument("--lr", type=float, default=1e-3)
    p.add_argument("--batch-size", type=int, default=32)
    p.add_argument("--dropout", type=float, default=0.2)
    p.add_argument("--weight-decay", type=float, default=1e-4)
    p.add_argument("--val-ratio", type=float, default=0.15)
    p.add_argument("--patience", type=int, default=25)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--stat-chunk", type=int, default=64, help="표준화 통계 계산 시 청크 크기(샘플 수)")
    args = p.parse_args()
    args.model, args.trust_remote_code = C.resolve_model_args(args.model_key, None, args.trust_remote_code)
    if args.domains is None:
        args.domains = ALL_DOMAINS
    return args


# ==================== 1단계: 추출 (GPU, 모델 1회 로드, forward 1회/샘플) ====================

def extract_pooled(args):
    import torch
    from tqdm import tqdm

    model, tokenizer = C.load_model_and_tokenizer(args.model, args.dtype, args.device, args.trust_remote_code)
    L = model.config.num_hidden_layers
    H = model.config.num_attention_heads
    hidden = model.config.hidden_size
    LH = L * H
    apply_template = C.make_apply_template(tokenizer)
    layer_idxs = sorted({max(1, min(L, round(f * L))) for f in args.hs_fracs})
    pools = ["toolmean", "last"]
    hs_cols = [(li, pl) for li in layer_idxs for pl in pools]
    S = len(hs_cols)
    K = args.max_pairs
    print(f"L={L} H={H} LH={LH} hidden={hidden} K={K} (hybrid concat용 K_small={args.k_small}) "
          f"hs layers={layer_idxs} → S={S}")

    records = C.load_records(args.data)
    tool_msg_mode = C.resolve_tool_msg_mode(args.tool_msg_mode, apply_template, records[0])

    groups: dict[tuple, list] = defaultdict(list)
    for r in records:
        if args.domains and r["domain"] not in args.domains:
            continue
        groups[(r["split"], r["domain"])].append(r)

    # 도메인×split별 개수 먼저 파악해서 전역 배열을 한 번에 할당 (fragmentation 방지)
    n_by_split = {"train": 0, "test": 0}
    for (split, domain), recs in groups.items():
        n_by_split[split] += len(recs)

    store = {}
    for split in ["train", "test"]:
        n = n_by_split[split]
        store[split] = {
            "pairs": np.zeros((n, K, LH), dtype=np.float16),
            "hidden": np.zeros((n, S, hidden), dtype=np.float16),
            "labels": np.zeros(n, dtype=np.int64),
            "domain": np.empty(n, dtype=object),
        }
    rng_np = np.random.default_rng(args.seed)
    row_ptr = {"train": 0, "test": 0}

    t0 = time.time()
    for (split, domain), recs in sorted(groups.items()):
        st = store[split]
        for r in tqdm(recs, desc=f"{split}/{domain}"):
            text = apply_template(C.build_messages(r, tool_msg_mode))
            try:
                (u_a, u_b), (x_a, x_b) = C.locate_spans(text, r["user_prompt"], r["tool_response"])
            except ValueError:
                continue
            enc = tokenizer(text, return_offsets_mapping=True, return_tensors="pt",
                            truncation=True, max_length=args.max_seq_len, add_special_tokens=False)
            offsets = enc.pop("offset_mapping")[0].tolist()
            s_idx = C.char_span_to_token_indices(offsets, u_a, u_b)
            x_idx = C.char_span_to_token_indices(offsets, x_a, x_b)
            if not s_idx or not x_idx:
                continue
            enc = {k: v.to(model.device) for k, v in enc.items()}
            with torch.no_grad():
                outputs = model(**enc, output_attentions=True, output_hidden_states=True, use_cache=False)

            x_t = torch.tensor(x_idx, device=model.device)
            s_t = torch.tensor(s_idx, device=model.device)

            blocks = []
            for att in outputs.attentions:
                blk = att[0].index_select(1, x_t).index_select(2, s_t)  # (H,|x|,|s|)
                blocks.append(blk.float())
            A = torch.stack(blocks, dim=0)  # (L,H,|x|,|s|)
            Z = A.permute(2, 3, 0, 1).reshape(-1, LH)  # (P, LH)
            P = Z.shape[0]
            sel = np.sort(rng_np.choice(P, size=K, replace=(P < K)))
            row = row_ptr[split]
            st["pairs"][row] = Z[torch.tensor(sel, device=Z.device)].cpu().numpy().astype(np.float16)
            del A, blocks

            for c, (li, pl) in enumerate(hs_cols):
                h = outputs.hidden_states[li][0]
                vec = h.index_select(0, x_t).mean(0) if pl == "toolmean" else h[-1]
                st["hidden"][row, c] = vec.float().cpu().numpy().astype(np.float16)
            del outputs

            st["labels"][row] = C.LABEL_TO_ID[r["label"]]
            st["domain"][row] = domain
            row_ptr[split] += 1

        print(f"  [{split}/{domain}] 누적 {row_ptr[split]} 완료 (elapsed={time.time()-t0:.0f}s)")

    # 스킵된 샘플만큼 배열 뒷부분이 남을 수 있으므로 실제 채워진 만큼만 잘라낸다
    for split in ["train", "test"]:
        n_actual = row_ptr[split]
        for k in ["pairs", "hidden", "labels", "domain"]:
            store[split][k] = store[split][k][:n_actual]

    del model, tokenizer
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    meta = {"L": L, "H": H, "LH": LH, "hidden": hidden, "K": K, "k_small": args.k_small,
            "hs_cols": [f"L{li}_{pl}" for li, pl in hs_cols], "domains": args.domains,
            "n_train": row_ptr["train"], "n_test": row_ptr["test"]}
    return store, meta


# ==================== 2단계: 학습 (CPU 상주 fp16, 배치 단위 float32 변환) ====================

def streaming_mean_std(t, chunk):
    """t: CPU tensor (N,D) 또는 (N,K,D), fp16. 청크 단위로 순회하며 평균/표준편차 계산
    (전체를 한 번에 float로 올리지 않음)."""
    import torch
    d = t.shape[-1]
    s = torch.zeros(d, dtype=torch.float64)
    ss = torch.zeros(d, dtype=torch.float64)
    cnt = 0
    N = t.shape[0]
    for i in range(0, N, chunk):
        c = t[i:i + chunk].float().reshape(-1, d)
        s += c.sum(0).double()
        ss += (c.double() ** 2).sum(0)
        cnt += c.shape[0]
    mean = (s / cnt).float()
    var = (ss / cnt) - mean.double() ** 2
    std = var.clamp_min(1e-12).sqrt().float()
    return mean, std


def train_eval_fp16(model, forward_fn, train_arrays, ytr, test_arrays, yte, args, stats=None):
    """train_arrays/test_arrays: CPU fp16 tensor 리스트. stats: [(mu,sd) or None, ...] — 배치
    단위로만 float32 변환 + 표준화한다(전체 upcast 없음)."""
    import time
    import torch
    import torch.nn as nn

    device = args.device if args.device != "cuda" or torch.cuda.is_available() else "cpu"
    torch.manual_seed(args.seed); np.random.seed(args.seed)
    model = model.to(device)
    stats = stats or [None] * len(train_arrays)

    train_idx_np, val_idx_np = stratified_train_val(ytr, args.val_ratio, args.seed)
    train_idx = torch.tensor(train_idx_np)
    val_idx = torch.tensor(val_idx_np) if len(val_idx_np) else None
    ytr_t = torch.tensor(ytr, dtype=torch.long, device=device)

    opt = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)
    counts = np.bincount(ytr[train_idx_np], minlength=3).astype(np.float32)
    weight = torch.tensor(counts.sum() / (3 * np.maximum(counts, 1.0)), dtype=torch.float32, device=device)
    loss_fn = nn.CrossEntropyLoss(weight=weight)

    def batch_of(arrays, idx_cpu):
        out = []
        for a, st in zip(arrays, stats):
            xb = a[idx_cpu].to(device, non_blocking=True).float()
            if st is not None:
                mu, sd = st
                xb = (xb - mu.to(device)) / sd.to(device)
            out.append(xb)
        return out

    def eval_idx(idx_cpu):
        model.eval()
        with torch.no_grad():
            preds, losses = [], []
            for b0 in range(0, len(idx_cpu), 64):
                bi = idx_cpu[b0:b0 + 64]
                logits = forward_fn(model, batch_of(train_arrays, bi))
                yb = ytr_t[bi.to(device)]
                losses.append(loss_fn(logits, yb).item() * len(bi))
                preds.append(logits.argmax(1).cpu().numpy())
        yv = ytr[idx_cpu.numpy()]
        return sum(losses) / len(idx_cpu), (np.concatenate(preds) == yv).mean()

    best_state, best_val, bad = None, float("inf"), 0
    t0 = time.time()
    for epoch in range(args.epochs):
        model.train()
        perm = train_idx[torch.randperm(len(train_idx))]
        for b0 in range(0, len(perm), args.batch_size):
            bi = perm[b0:b0 + args.batch_size]
            opt.zero_grad()
            loss = loss_fn(forward_fn(model, batch_of(train_arrays, bi)), ytr_t[bi.to(device)])
            loss.backward()
            opt.step()
        if val_idx is not None:
            vloss, vacc = eval_idx(val_idx)
            if vloss < best_val - 1e-5:
                best_val = vloss
                best_state = {k: v.detach().clone() for k, v in model.state_dict().items()}
                bad = 0
            else:
                bad += 1
            if bad >= args.patience:
                print(f"    early stop @ epoch {epoch+1} (best_val={best_val:.4f})")
                break
        if (epoch + 1) % 10 == 0:
            print(f"    epoch {epoch+1}/{args.epochs} elapsed={time.time()-t0:.0f}s"
                  + (f" val_acc={vacc:.3f}" if val_idx is not None else ""))

    if best_state is not None:
        model.load_state_dict(best_state)
    model.eval()
    with torch.no_grad():
        probs = []
        n_te = test_arrays[0].shape[0]
        idx_all = torch.arange(n_te)
        for b0 in range(0, n_te, 64):
            batch = batch_of(test_arrays, idx_all[b0:b0 + 64])
            probs.append(torch.softmax(forward_fn(model, batch), dim=1).cpu().numpy())
    return np.concatenate(probs, 0)


def main():
    args = parse_args()
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    import torch

    print("=== [1/3] 추출 (8도메인 pooled, forward 1회/샘플, RAM 직접 적재) ===")
    store, meta = extract_pooled(args)
    json.dump(meta, open(out / "run_meta.json", "w"), ensure_ascii=False, indent=2)
    print(f"n_train={meta['n_train']} n_test={meta['n_test']} (디스크에는 이 메타만 저장됨)")

    ytr, yte = store["train"]["labels"], store["test"]["labels"]
    pairs_tr = torch.from_numpy(store["train"]["pairs"])   # (N,K,LH) fp16, CPU
    pairs_te = torch.from_numpy(store["test"]["pairs"])
    hid_tr = torch.from_numpy(store["train"]["hidden"].reshape(len(ytr), -1))  # (N,S*hidden) fp16
    hid_te = torch.from_numpy(store["test"]["hidden"].reshape(len(yte), -1))
    lh, hd = pairs_tr.shape[-1], hid_tr.shape[-1]
    k_small = args.k_small

    print("\n=== [2/3] 학습 ===")
    print("표준화 통계 계산 중 (청크 단위, 전체 upcast 없음)...")
    pair_mu, pair_sd = streaming_mean_std(pairs_tr, args.stat_chunk)      # K=2048 기준 통계
    hid_mu, hid_sd = streaming_mean_std(hid_tr, args.stat_chunk)

    print("\n-- 모델 A: hybrid concat (K_small 슬라이스 + hidden) --")
    # attn 인코더 입력 차원은 lh(=LH, head*layer 차원) — K(토큰쌍 개수)는 pool하는 축의 길이일 뿐이라
    # K_small(1024)이든 K(2048)이든 인코더 자체는 동일한 lh 차원을 받는다.
    model_a = build_model_v1("hybrid", lh, hd, args.dropout)
    probs_a = train_eval_fp16(
        model_a, lambda m, b: m(b[0], b[1]),
        [pairs_tr[:, :k_small, :], hid_tr], ytr,
        [pairs_te[:, :k_small, :], hid_te], yte, args,
        stats=[(pair_mu, pair_sd), (hid_mu, hid_sd)])
    pred_a = probs_a.argmax(1)
    m_a = metrics_from_preds(yte, pred_a)
    print(f"[A: hybrid concat, K={k_small}] Acc={m_a['acc']:.3f} FPR={m_a['fpr']} FNR={m_a['fnr']}")

    print("\n-- 모델 B: attn_bigK (K=2048, mean-pool) --")
    model_b = make_mean_pool_attn(lh, args.dropout)
    probs_b = train_eval_fp16(
        model_b, lambda m, b: m(b[0]),
        [pairs_tr], ytr, [pairs_te], yte, args, stats=[(pair_mu, pair_sd)])
    pred_b = probs_b.argmax(1)
    m_b = metrics_from_preds(yte, pred_b)
    print(f"[B: attn_bigK, K={args.max_pairs}] Acc={m_b['acc']:.3f} FPR={m_b['fpr']} FNR={m_b['fnr']}")

    print("\n=== [3/3] 앙상블 ===")
    err_a, err_b = pred_a != yte, pred_b != yte
    both = int((err_a & err_b).sum()); only_a = int((err_a & ~err_b).sum()); only_b = int((~err_a & err_b).sum())
    print(f"에러 겹침: 둘다={both} A만={only_a} B만={only_b} (A전체={int(err_a.sum())} B전체={int(err_b.sum())})")

    results = {"A_hybrid_concat": m_a, "B_attn_bigK": m_b,
               "error_overlap": {"both": both, "only_a": only_a, "only_b": only_b}}
    for name, wa, wb in [("ensemble_0.5_0.5", 0.5, 0.5), ("ensemble_A0.7", 0.7, 0.3), ("ensemble_B0.7", 0.3, 0.7)]:
        pred_ens = (wa * probs_a + wb * probs_b).argmax(1)
        m_ens = metrics_from_preds(yte, pred_ens)
        results[name] = m_ens
        print(f"[{name}] Acc={m_ens['acc']:.3f} macroF1={m_ens['macro_f1']:.3f} "
              f"FPR={m_ens['fpr']} FNR={m_ens['fnr']}")

    json.dump(results, open(out / "pooled_ensemble_metrics.json", "w"), ensure_ascii=False, indent=2)
    print(f"\n결과 → {out / 'pooled_ensemble_metrics.json'}")


if __name__ == "__main__":
    main()
