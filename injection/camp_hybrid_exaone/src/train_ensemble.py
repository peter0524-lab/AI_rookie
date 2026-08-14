"""앙상블 — attn_bigK(낮은 FPR)와 hybrid baseline-concat(낮은 FNR)를 확률 평균으로 결합해
FPR·FNR을 동시에 낮출 수 있는지 검증한다.

배경: 지금까지 시도한 5개 개선안(attn_pool/hidden_tok/attn_headsel/attn_bigK/hybrid_gated)은
전부 "FPR을 낮추는 대신 FNR을 희생"하는 방향으로만 움직였다. FNR이 제일 낮았던 건 오히려
제일 처음의 단순 hybrid(concat) baseline(FNR 0.018, FPR 0.143)이었고, FPR이 제일 낮았던 건
attn_bigK(FPR 0.020, FNR 0.088)였다. 두 모델이 서로 다른 샘플에서 실수하고 있다면(에러가
완전히 겹치지 않는다면), 확률을 평균 내는 것만으로 둘 다 낮아질 수 있다 — 재학습 없이
이미 학습 가능한 두 모델을 같은 test set(동일 순서 확인됨)에 대해 따로 학습해 얻은
softmax 확률을 평균낸다.

실행: python src/train_ensemble.py
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from train_hybrid import discover_domains, load_group as load_group_v1, stratified_train_val, metrics_from_preds
from train_hybrid_v2 import load_group_v2, make_mean_pool_attn, _standardize, to_tensor


class Args:
    epochs = 200
    lr = 1e-3
    batch_size = 16
    dropout = 0.2
    weight_decay = 1e-4
    val_ratio = 0.15
    patience = 25
    seed = 42
    device = None


def train_get_probs(model, forward_fn, train_arrays, ytr, test_arrays, args):
    """train_hybrid_v2.train_eval_generic과 동일한 학습 루프이되, argmax가 아니라 test softmax 확률을 반환."""
    import time
    import torch
    import torch.nn as nn

    device = args.device or ("cuda" if torch.cuda.is_available() else "cpu")
    torch.manual_seed(args.seed); np.random.seed(args.seed)
    model = model.to(device)

    train_idx_np, val_idx_np = stratified_train_val(ytr, args.val_ratio, args.seed)
    train_idx = torch.tensor(train_idx_np)
    val_idx = torch.tensor(val_idx_np) if len(val_idx_np) else None
    ytr_t = torch.tensor(ytr, dtype=torch.long, device=device)

    opt = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)
    counts = np.bincount(ytr[train_idx_np], minlength=3).astype(np.float32)
    weight = torch.tensor(counts.sum() / (3 * np.maximum(counts, 1.0)), dtype=torch.float32, device=device)
    loss_fn = nn.CrossEntropyLoss(weight=weight)

    def batch_of(arrays, idx_cpu):
        return [a[idx_cpu].to(device, non_blocking=True) for a in arrays]

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
            vloss, _ = eval_idx(val_idx)
            if vloss < best_val - 1e-5:
                best_val = vloss
                best_state = {k: v.detach().clone() for k, v in model.state_dict().items()}
                bad = 0
            else:
                bad += 1
            if bad >= args.patience:
                print(f"    early stop @ epoch {epoch+1} (best_val={best_val:.4f})")
                break

    if best_state is not None:
        model.load_state_dict(best_state)
    model.eval()
    with torch.no_grad():
        probs = []
        n = test_arrays[0].shape[0]
        idx_all = torch.arange(n)
        for b0 in range(0, n, 64):
            batch = batch_of(test_arrays, idx_all[b0:b0 + 64])
            probs.append(torch.softmax(forward_fn(model, batch), dim=1).cpu().numpy())
    return np.concatenate(probs, 0)


def main():
    import torch
    args = Args()
    feat_v1 = Path("dump_hybrid_coding")
    feat_v2 = Path("dump_hybrid_coding_v2")
    domains = discover_domains(feat_v1)
    print(f"domains: {domains}")

    # ---- 모델 A: hybrid baseline (concat) — 낮은 FNR ----
    from train_hybrid import build_model as build_model_v1
    Ptr1, Htr1, ytr, _, _ = load_group_v1(feat_v1, domains, "train")
    Pte1, Hte1, yte, _, _ = load_group_v1(feat_v1, domains, "test")
    lh1, hd1 = Ptr1.shape[-1], Htr1.shape[-1]
    Ptr1_t = to_tensor(Ptr1, "cpu", torch.float32); Pte1_t = to_tensor(Pte1, "cpu", torch.float32)
    Htr1_t = to_tensor(Htr1, "cpu", torch.float32); Hte1_t = to_tensor(Hte1, "cpu", torch.float32)
    [Ptr1_t, Htr1_t], [Pte1_t, Hte1_t] = _standardize([Ptr1_t, Htr1_t], [Pte1_t, Hte1_t], [True, True])
    model_a = build_model_v1("hybrid", lh1, hd1, args.dropout)
    print("\n=== 모델 A: hybrid baseline(concat) 학습 ===")
    probs_a = train_get_probs(model_a, lambda m, b: m(b[0], b[1]),
                                [Ptr1_t, Htr1_t], ytr, [Pte1_t, Hte1_t], args)
    pred_a = probs_a.argmax(1)
    m_a = metrics_from_preds(yte, pred_a)
    print(f"[A: hybrid concat] Acc={m_a['acc']:.3f} FPR={m_a['fpr']} FNR={m_a['fnr']}")

    # ---- 모델 B: attn_bigK (K=2048, mean-pool) — 낮은 FPR ----
    Ptr2, Ttr2, Mtr2, ytr2 = load_group_v2(feat_v2, domains, "train")
    Pte2, Tte2, Mte2, yte2 = load_group_v2(feat_v2, domains, "test")
    assert (ytr2 == ytr).all() and (yte2 == yte).all(), "v1/v2 라벨 순서 불일치"
    lh2 = Ptr2.shape[-1]
    Ptr2_t = to_tensor(Ptr2, "cpu", torch.float32); Pte2_t = to_tensor(Pte2, "cpu", torch.float32)
    [Ptr2_t], [Pte2_t] = _standardize([Ptr2_t], [Pte2_t], [True])
    model_b = make_mean_pool_attn(lh2, args.dropout)
    print("\n=== 모델 B: attn_bigK 학습 ===")
    probs_b = train_get_probs(model_b, lambda m, b: m(b[0]), [Ptr2_t], ytr, [Pte2_t], args)
    pred_b = probs_b.argmax(1)
    m_b = metrics_from_preds(yte, pred_b)
    print(f"[B: attn_bigK] Acc={m_b['acc']:.3f} FPR={m_b['fpr']} FNR={m_b['fnr']}")

    # ---- 에러 겹침 확인 ----
    err_a = pred_a != yte
    err_b = pred_b != yte
    both = (err_a & err_b).sum()
    only_a = (err_a & ~err_b).sum()
    only_b = (~err_a & err_b).sum()
    print(f"\n에러 겹침: 둘 다 틀림={both}, A만 틀림={only_a}, B만 틀림={only_b}, "
          f"(A 전체 에러={err_a.sum()}, B 전체 에러={err_b.sum()})")

    # ---- 앙상블 (확률 평균) ----
    for w_name, wa, wb in [("평균(0.5/0.5)", 0.5, 0.5), ("A쪽 가중(0.7/0.3)", 0.7, 0.3),
                           ("B쪽 가중(0.3/0.7)", 0.3, 0.7)]:
        probs_ens = wa * probs_a + wb * probs_b
        pred_ens = probs_ens.argmax(1)
        m_ens = metrics_from_preds(yte, pred_ens)
        print(f"[ensemble {w_name}] Acc={m_ens['acc']:.3f} macroF1={m_ens['macro_f1']:.3f} "
              f"FPR={m_ens['fpr']} FNR={m_ens['fnr']}")

    report = {
        "A_hybrid_concat": m_a, "B_attn_bigK": m_b,
        "error_overlap": {"both": int(both), "only_a": int(only_a), "only_b": int(only_b)},
    }
    Path("results_ensemble").mkdir(exist_ok=True)
    json.dump(report, open("results_ensemble/ensemble_metrics.json", "w"), ensure_ascii=False, indent=2)
    print("\n결과 → results_ensemble/ensemble_metrics.json")


if __name__ == "__main__":
    main()
