# -*- coding: utf-8 -*-
"""Cross-domain generalization (Table 1/2의 Cross A->B / Cross B->A와 동일 정의) —
이미 추출된 dump_hybrid_seg_<domain>/ 을 재사용, 재추출 없음.

GROUP_A={coding,cloud,project,shopping} 학습 -> GROUP_B={finance,messaging,social_media,web} 평가 (A2B)
또는 반대(B2A). 학습/평가 도메인이 아예 겹치지 않으므로 각 그룹의 train+test 전체를 사용한다
(hwan train_detector.py의 --cross 로직과 동일 정의).
"""
from __future__ import annotations

import argparse
import gc
import json
import time
from pathlib import Path

import numpy as np

GROUP_A = ["coding", "cloud", "project", "shopping"]
GROUP_B = ["finance", "messaging", "social_media", "web"]


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--dumps-prefix", default="dump_hybrid_seg_")
    p.add_argument("--cross", choices=["A2B", "B2A"], required=True)
    p.add_argument("--out", default="results_cross")
    p.add_argument("--epochs", type=int, default=200)
    p.add_argument("--lr", type=float, default=0.01)
    p.add_argument("--batch-size", type=int, default=16)
    p.add_argument("--dropout", type=float, default=0.2)
    p.add_argument("--weight-decay", type=float, default=1e-4)
    p.add_argument("--val-ratio", type=float, default=0.15)
    p.add_argument("--patience", type=int, default=25)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--stat-chunk", type=int, default=64)
    p.add_argument("--device", default="cuda")
    return p.parse_args()


def load_group_all(dumps_prefix, domains):
    """도메인 목록의 train+test 전체를 이어붙여 반환 (cross-domain은 8:2 split 안 씀)."""
    Ps, Hs, ys, doms = [], [], [], []
    for d in domains:
        feat_dir = Path(f"{dumps_prefix}{d}")
        for split in ["train", "test"]:
            meta = json.load(open(feat_dir / f"{split}_{d}_meta.json"))
            y = np.asarray(meta["labels"], dtype=np.int64)
            n = len(y)
            pairs = np.load(feat_dir / f"{split}_{d}_pairs.npy", mmap_mode="r")[:n]
            hidden = np.load(feat_dir / f"{split}_{d}_hidden.npy")[:n].reshape(n, -1)
            Ps.append(np.asarray(pairs))
            Hs.append(np.asarray(hidden))
            ys.append(y)
            doms.extend([d] * n)
            print(f"  [load] {split}/{d}: n={n}")
    return np.concatenate(Ps, 0), np.concatenate(Hs, 0), np.concatenate(ys, 0), np.array(doms)


def streaming_mean_std(arr_np, chunk):
    import torch
    d = arr_np.shape[-1]
    s = np.zeros(d, dtype=np.float64)
    ss = np.zeros(d, dtype=np.float64)
    cnt = 0
    N = arr_np.shape[0]
    for i in range(0, N, chunk):
        c = arr_np[i:i + chunk].astype(np.float64).reshape(-1, d)
        s += c.sum(0)
        ss += (c ** 2).sum(0)
        cnt += c.shape[0]
    mean = s / cnt
    var = (ss / cnt) - mean ** 2
    std = np.sqrt(np.clip(var, 1e-12, None))
    return torch.tensor(mean, dtype=torch.float32), torch.tensor(std, dtype=torch.float32)


def stratified_train_val(y, val_ratio, seed):
    rng = np.random.default_rng(seed)
    train_idx, val_idx = [], []
    for c in sorted(set(y.tolist())):
        idx = np.flatnonzero(y == c)
        rng.shuffle(idx)
        n_val = max(1, int(round(len(idx) * val_ratio))) if val_ratio > 0 and len(idx) > 1 else 0
        val_idx.extend(idx[:n_val])
        train_idx.extend(idx[n_val:])
    train_idx = np.asarray(train_idx); val_idx = np.asarray(val_idx)
    rng.shuffle(train_idx); rng.shuffle(val_idx)
    return train_idx, val_idx


W_FPR, W_FNR = 0.25, 0.75


def weighted_risk(fpr, fnr):
    if fpr is None or fnr is None:
        return None
    return round(W_FPR * fpr + W_FNR * fnr, 4)


def metrics_from_preds(y_true, y_pred, domains=None):
    acc = float((y_true == y_pred).mean())
    pos = y_true == 0
    neg = ~pos
    fnr = float((y_pred[pos] != 0).mean()) if pos.any() else None
    fpr = float((y_pred[neg] == 0).mean()) if neg.any() else None
    from sklearn.metrics import f1_score
    macro_f1 = float(f1_score(y_true, y_pred, average="macro"))
    out = {"acc": round(acc, 4), "fpr": round(fpr, 4) if fpr is not None else None,
           "fnr": round(fnr, 4) if fnr is not None else None, "macro_f1": round(macro_f1, 4),
           "risk": weighted_risk(fpr, fnr), "n_test": int(len(y_true))}
    if domains is not None:
        per_domain = {}
        for d in sorted(set(domains.tolist())):
            m = domains == d
            yt, yp = y_true[m], y_pred[m]
            pos_d = yt == 0; neg_d = ~pos_d
            fnr_d = float((yp[pos_d] != 0).mean()) if pos_d.any() else None
            fpr_d = float((yp[neg_d] == 0).mean()) if neg_d.any() else None
            per_domain[d] = {"acc": round(float((yt == yp).mean()), 4),
                              "fpr": round(fpr_d, 4) if fpr_d is not None else None,
                              "fnr": round(fnr_d, 4) if fnr_d is not None else None}
        out["per_domain"] = per_domain
    return out


def train_eval_cross(variant, Ptr, Htr, ytr, Pte, Hte, yte, dom_te, args, lh, hd, pmu, psd, hmu, hsd):
    import torch
    import torch.nn as nn
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from train_hybrid import build_model

    device = args.device if args.device != "cuda" or torch.cuda.is_available() else "cpu"
    torch.manual_seed(args.seed); np.random.seed(args.seed)

    data_device = device
    Ptr_t = Htr_t = Pte_t = Hte_t = None
    try:
        Ptr_t = torch.from_numpy(Ptr).to(device)
        Htr_t = torch.from_numpy(Htr).to(device)
        Pte_t = torch.from_numpy(Pte).to(device)
        Hte_t = torch.from_numpy(Hte).to(device)
        print(f"    [{variant}] fp16 데이터 GPU 상주 성공 (device={device})")
    except torch.cuda.OutOfMemoryError:
        print(f"    [{variant}] GPU 상주 실패(OOM) -> CPU 상주로 폴백")
        del Ptr_t, Htr_t, Pte_t, Hte_t
        gc.collect(); torch.cuda.empty_cache()
        data_device = "cpu"
        Ptr_t = torch.from_numpy(Ptr); Htr_t = torch.from_numpy(Htr)
        Pte_t = torch.from_numpy(Pte); Hte_t = torch.from_numpy(Hte)

    train_idx_np, val_idx_np = stratified_train_val(ytr, args.val_ratio, args.seed)
    train_idx = torch.tensor(train_idx_np, device=data_device)
    val_idx = torch.tensor(val_idx_np, device=data_device) if len(val_idx_np) else None
    ytr_t = torch.tensor(ytr, dtype=torch.long, device=device)
    pmu_d, psd_d = pmu.to(device), psd.to(device)
    hmu_d, hsd_d = hmu.to(device), hsd.to(device)

    model = build_model(variant, lh, hd, args.dropout).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)
    counts = np.bincount(ytr[train_idx_np], minlength=3).astype(np.float32)
    weight = torch.tensor(counts.sum() / (3 * np.maximum(counts, 1.0)), dtype=torch.float32, device=device)
    loss_fn = nn.CrossEntropyLoss(weight=weight)

    def batch_of(idx):
        pb = Ptr_t[idx].to(device, non_blocking=True).float()
        hb = Htr_t[idx].to(device, non_blocking=True).float()
        return (pb - pmu_d) / psd_d, (hb - hmu_d) / hsd_d

    def eval_logits(idx, Ptensor, Htensor):
        model.eval()
        with torch.no_grad():
            outs = []
            for b0 in range(0, len(idx), 64):
                bi = idx[b0:b0 + 64]
                pb = Ptensor[bi].to(device).float(); pb = (pb - pmu_d) / psd_d
                hb = Htensor[bi].to(device).float(); hb = (hb - hmu_d) / hsd_d
                outs.append(model(pb, hb).cpu())
        return torch.cat(outs, dim=0)

    def val_risk(idx):
        logits = eval_logits(idx, Ptr_t, Htr_t)
        yv = ytr[idx.cpu().numpy()]
        loss = loss_fn(logits.to(device), torch.tensor(yv, dtype=torch.long, device=device)).item()
        pred = logits.argmax(1).numpy()
        m = metrics_from_preds(yv, pred)
        return loss, m["acc"], m["risk"] if m["risk"] is not None else 1.0

    best_state, best_risk, bad = None, float("inf"), 0
    t0 = time.time()
    for epoch in range(args.epochs):
        model.train()
        perm = train_idx[torch.randperm(len(train_idx), device=data_device)]
        for b0 in range(0, len(perm), args.batch_size):
            bi = perm[b0:b0 + args.batch_size]
            opt.zero_grad()
            pb, hb = batch_of(bi)
            loss = loss_fn(model(pb, hb), ytr_t[bi.to(device)])
            loss.backward(); opt.step()
        if val_idx is not None:
            vloss, vacc, vrisk = val_risk(val_idx)
            if vrisk < best_risk - 1e-5:
                best_risk = vrisk
                best_state = {k: v.detach().clone() for k, v in model.state_dict().items()}
                bad = 0
            else:
                bad += 1
            if bad >= args.patience:
                print(f"    [{variant}] early stop @ epoch {epoch+1} (best_val_risk={best_risk:.4f})")
                break
        if (epoch + 1) % 10 == 0:
            print(f"    [{variant}] epoch {epoch+1}/{args.epochs} elapsed={time.time()-t0:.0f}s"
                  + (f" val_acc={vacc:.3f} val_risk={vrisk:.4f}" if val_idx is not None else ""))

    if best_state is not None:
        model.load_state_dict(best_state)

    bias = 0.0
    if val_idx is not None:
        val_logits = eval_logits(val_idx, Ptr_t, Htr_t)
        yv = ytr[val_idx.cpu().numpy()]
        raw_risk = metrics_from_preds(yv, val_logits.argmax(1).numpy())["risk"]
        best_bias, best_bias_risk = 0.0, raw_risk
        for b in np.arange(-3.0, 3.01, 0.1):
            shifted = val_logits.clone(); shifted[:, 0] += b
            r = metrics_from_preds(yv, shifted.argmax(1).numpy())["risk"]
            if r is not None and r < best_bias_risk - 1e-6:
                best_bias_risk, best_bias = r, float(b)
        bias = best_bias
        print(f"    [{variant}] 임계값 보정: misaligned bias={bias:+.2f} (val risk {raw_risk} -> {best_bias_risk})")

    test_logits = eval_logits(torch.arange(Pte_t.shape[0], device=data_device), Pte_t, Hte_t)
    y_pred_raw = test_logits.argmax(1).numpy()
    test_logits[:, 0] += bias
    y_pred_cal = test_logits.argmax(1).numpy()

    m_raw = metrics_from_preds(yte, y_pred_raw, domains=dom_te)
    m_cal = metrics_from_preds(yte, y_pred_cal, domains=dom_te)
    m_cal["bias"] = round(bias, 2)
    m_cal["raw"] = m_raw

    del model, opt, Ptr_t, Htr_t, Pte_t, Hte_t, ytr_t
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    return m_cal


def main():
    args = parse_args()
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    tr_doms, te_doms = (GROUP_A, GROUP_B) if args.cross == "A2B" else (GROUP_B, GROUP_A)
    print(f"=== cross={args.cross}: train={tr_doms} -> eval={te_doms} ===")

    t0 = time.time()
    Ptr, Htr, ytr, _ = load_group_all(args.dumps_prefix, tr_doms)
    Pte, Hte, yte, dom_te = load_group_all(args.dumps_prefix, te_doms)
    lh, hd = Ptr.shape[-1], Htr.shape[-1]
    print(f"n_train={len(ytr)} n_test={len(yte)} lh={lh} hd={hd} (elapsed={time.time()-t0:.0f}s)")

    t0 = time.time()
    pmu, psd = streaming_mean_std(Ptr.reshape(-1, lh), args.stat_chunk * 32)
    hmu, hsd = streaming_mean_std(Htr, args.stat_chunk)
    print(f"표준화 통계 완료 (elapsed={time.time()-t0:.0f}s)")

    results = {}
    for variant in ["attn", "hybrid"]:
        t0 = time.time()
        m = train_eval_cross(variant, Ptr, Htr, ytr, Pte, Hte, yte, dom_te, args, lh, hd, pmu, psd, hmu, hsd)
        results[variant] = m
        print(f"[{variant}] Acc={m['acc']:.3f} FPR={m['fpr']} FNR={m['fnr']} risk={m['risk']} bias={m['bias']:+.2f} "
              f"(raw: FPR={m['raw']['fpr']} FNR={m['raw']['fnr']} risk={m['raw']['risk']}) (elapsed={time.time()-t0:.0f}s)")

    json.dump(results, open(out / f"cross_{args.cross}_metrics.json", "w"), ensure_ascii=False, indent=2)
    print(f"\n결과 -> {out / f'cross_{args.cross}_metrics.json'}")


if __name__ == "__main__":
    main()
