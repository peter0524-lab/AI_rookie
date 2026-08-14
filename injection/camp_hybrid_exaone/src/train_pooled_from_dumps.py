"""8도메인 pooled 학습 — 이미 도메인별로 추출된 dump_hybrid_<domain>/ 을 그대로 재사용.

train_hybrid.py의 attn/hybrid 아키텍처(EncFirstRegularized와 동일 구조 + hidden 융합)를
그대로 쓰되, pooled 규모(train 25,600 / test 6,400, K=1024)에서 GPU OOM 없이 학습하려고
run_pooled_ensemble.py의 방식(CPU에 fp16으로 유지, 배치 단위로만 float32+GPU 이동,
표준화 통계도 청크 단위 스트리밍)을 차용한다. 재추출은 하지 않는다(디스크의 8개
dump_hybrid_<domain>/을 그대로 읽어 concat).

hwan(alignsentinel_replicate) baseline과 같은 하이퍼파라미터: lr=0.01, batch=16,
epochs=200, dropout=0.2, weight_decay=1e-4, val_ratio=0.15, patience=25, seed=42,
standardize + class_weights 항상 적용.

실행:
  python src/train_pooled_from_dumps.py --dumps-prefix dump_hybrid_ --out results_hybrid_pooled
"""

from __future__ import annotations

import argparse
import gc
import json
import time
from pathlib import Path

import numpy as np

ALL_DOMAINS = ["cloud", "coding", "finance", "messaging", "project", "shopping", "social_media", "web"]
ID_TO_LABEL = {0: "misaligned", 1: "aligned", 2: "non_instruction"}


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--dumps-prefix", default="dump_hybrid_")
    p.add_argument("--domains", nargs="+", default=ALL_DOMAINS)
    p.add_argument("--out", default="results_hybrid_pooled")
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
    p.add_argument("--checkpoint-metric", choices=["risk", "loss"], default="risk",
                   help="체크포인트 선택 기준. risk=val weighted-risk(신규), loss=val cross-entropy(기존 방식) — "
                        "ablation 비교용으로 loss도 남겨둠")
    p.add_argument("--save-dir", default=None,
                   help="지정하면 학습된 모델(state_dict)+표준화 통계+보정 bias+메타데이터를 저장 "
                        "(배포/재사용용). 미지정 시 기존과 동일하게 저장 안 함")
    return p.parse_args()


# ==================== 데이터 로드 (디스크의 도메인별 dump 재사용, RAM에 concat) ====================

def load_pooled(args):
    Ptr_parts, Htr_parts, ytr_parts, dom_tr = [], [], [], []
    Pte_parts, Hte_parts, yte_parts, dom_te = [], [], [], []
    LABEL_TO_ID = {"misaligned": 0, "aligned": 1, "non_instruction": 2}

    for d in args.domains:
        feat_dir = Path(f"{args.dumps_prefix}{d}")
        for split, Ps, Hs, ys, doms in [
            ("train", Ptr_parts, Htr_parts, ytr_parts, dom_tr),
            ("test", Pte_parts, Hte_parts, yte_parts, dom_te),
        ]:
            meta = json.load(open(feat_dir / f"{split}_{d}_meta.json"))
            y = np.asarray(meta["labels"], dtype=np.int64)
            n = len(y)
            pairs = np.load(feat_dir / f"{split}_{d}_pairs.npy", mmap_mode="r")[:n]
            hidden = np.load(feat_dir / f"{split}_{d}_hidden.npy")[:n].reshape(n, -1)
            Ps.append(np.asarray(pairs))  # fp16 copy into RAM
            Hs.append(np.asarray(hidden))
            ys.append(y)
            doms.extend([d] * n)
            print(f"  [load] {split}/{d}: n={n}")

    Ptr = np.concatenate(Ptr_parts, axis=0)
    Htr = np.concatenate(Htr_parts, axis=0)
    ytr = np.concatenate(ytr_parts, axis=0)
    Pte = np.concatenate(Pte_parts, axis=0)
    Hte = np.concatenate(Hte_parts, axis=0)
    yte = np.concatenate(yte_parts, axis=0)
    dom_te = np.array(dom_te)
    del Ptr_parts, Htr_parts, Pte_parts, Hte_parts
    gc.collect()
    return Ptr, Htr, ytr, Pte, Hte, yte, dom_te


# ==================== 표준화 (청크 스트리밍, 전체 upcast 없음) ====================

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


W_FPR, W_FNR = 0.25, 0.75  # PDF Table 1/2와 동일한 weighted risk 정의 (FNR을 3배 중시)


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


# ==================== 학습 (CPU 상주 fp16, 배치 단위 float32 변환) ====================

def train_eval_pooled(variant, Ptr, Htr, ytr, Pte, Hte, yte, dom_te, args, lh, hd,
                       pmu, psd, hmu, hsd, save_dir=None):
    import torch
    import torch.nn as nn
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from train_hybrid import build_model

    device = args.device if args.device != "cuda" or torch.cuda.is_available() else "cpu"
    torch.manual_seed(args.seed); np.random.seed(args.seed)

    # fp16 데이터를 통째로 GPU에 올려서(배치마다 CPU→GPU 전송 안 하게) 학습 속도를 크게
    # 올린다. 안 들어가면(OOM) CPU 상주로 폴백 — 느리지만 항상 동작은 하게.
    data_device = device
    Ptr_t = Htr_t = Pte_t = Hte_t = None
    try:
        Ptr_t = torch.from_numpy(Ptr).to(device)
        Htr_t = torch.from_numpy(Htr).to(device)
        Pte_t = torch.from_numpy(Pte).to(device)
        Hte_t = torch.from_numpy(Hte).to(device)
        print(f"    [{variant}] fp16 데이터 GPU 상주 성공 (device={device})")
    except torch.cuda.OutOfMemoryError:
        print(f"    [{variant}] GPU 상주 실패(OOM) → CPU 상주로 폴백")
        del Ptr_t, Htr_t, Pte_t, Hte_t
        gc.collect()
        torch.cuda.empty_cache()
        data_device = "cpu"
        Ptr_t = torch.from_numpy(Ptr)
        Htr_t = torch.from_numpy(Htr)
        Pte_t = torch.from_numpy(Pte)
        Hte_t = torch.from_numpy(Hte)

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
        pb = (pb - pmu_d) / psd_d
        hb = (hb - hmu_d) / hsd_d
        return pb, hb

    def eval_logits(idx):
        model.eval()
        with torch.no_grad():
            outs = []
            for b0 in range(0, len(idx), 64):
                bi = idx[b0:b0 + 64]
                pb, hb = batch_of(bi)
                outs.append(model(pb, hb).cpu())
        return torch.cat(outs, dim=0)

    def val_risk(idx):
        logits = eval_logits(idx)
        yv = ytr[idx.cpu().numpy()]
        loss = loss_fn(logits.to(device), torch.tensor(yv, dtype=torch.long, device=device)).item()
        pred = logits.argmax(1).numpy()
        m = metrics_from_preds(yv, pred)
        return loss, m["acc"], m["risk"] if m["risk"] is not None else 1.0

    ckpt_metric = getattr(args, "checkpoint_metric", "risk")  # "risk" 또는 "loss" — 어느 기준으로 best 체크포인트를 고를지
    best_state, best_score, bad = None, float("inf"), 0
    t0 = time.time()
    for epoch in range(args.epochs):
        model.train()
        perm = train_idx[torch.randperm(len(train_idx), device=data_device)]
        for b0 in range(0, len(perm), args.batch_size):
            bi = perm[b0:b0 + args.batch_size]
            opt.zero_grad()
            pb, hb = batch_of(bi)
            loss = loss_fn(model(pb, hb), ytr_t[bi.to(device)])
            loss.backward()
            opt.step()
        if val_idx is not None:
            vloss, vacc, vrisk = val_risk(val_idx)
            score = vloss if ckpt_metric == "loss" else vrisk
            if score < best_score - 1e-5:
                best_score = score
                best_state = {k: v.detach().clone() for k, v in model.state_dict().items()}
                bad = 0
            else:
                bad += 1
            if bad >= args.patience:
                print(f"    [{variant}] early stop @ epoch {epoch+1} (ckpt_metric={ckpt_metric} best={best_score:.4f})")
                break
        if (epoch + 1) % 5 == 0:
            print(f"    [{variant}] epoch {epoch+1}/{args.epochs} elapsed={time.time()-t0:.0f}s"
                  + (f" val_acc={vacc:.3f} val_risk={vrisk:.4f}" if val_idx is not None else ""))

    if best_state is not None:
        model.load_state_dict(best_state)

    # ---- 임계값 보정: misaligned(class 0) 로짓에 bias를 더해 val에서 weighted-risk를 최소화하는
    #      bias를 찾고 test에도 동일 적용 (재학습 없이 FPR↔FNR 트레이드오프를 목표 지표로 이동) ----
    bias = 0.0
    if val_idx is not None:
        val_logits = eval_logits(val_idx)
        yv = ytr[val_idx.cpu().numpy()]
        raw_risk = metrics_from_preds(yv, val_logits.argmax(1).numpy())["risk"]
        best_bias, best_bias_risk = 0.0, raw_risk
        for b in np.arange(-3.0, 3.01, 0.1):
            shifted = val_logits.clone(); shifted[:, 0] += b
            r = metrics_from_preds(yv, shifted.argmax(1).numpy())["risk"]
            if r is not None and r < best_bias_risk - 1e-6:
                best_bias_risk, best_bias = r, float(b)
        bias = best_bias
        print(f"    [{variant}] 임계값 보정: misaligned bias={bias:+.2f} (val risk {raw_risk} → {best_bias_risk})")

    test_logits = eval_logits(torch.arange(Pte_t.shape[0], device=data_device))
    y_pred_raw = test_logits.argmax(1).numpy()
    test_logits[:, 0] += bias
    y_pred_calibrated = test_logits.argmax(1).numpy()

    m_raw = metrics_from_preds(yte, y_pred_raw, domains=dom_te)
    m_cal = metrics_from_preds(yte, y_pred_calibrated, domains=dom_te)
    m_cal["bias"] = round(bias, 2)
    m_cal["raw"] = m_raw

    if save_dir is not None:
        vdir = Path(save_dir) / variant
        vdir.mkdir(parents=True, exist_ok=True)
        torch.save(model.state_dict(), vdir / "model.pt")
        torch.save({"pair_mu": pmu, "pair_sd": psd, "hidden_mu": hmu, "hidden_sd": hsd}, vdir / "norm_stats.pt")
        json.dump({"misaligned_bias": bias, "misaligned_class_id": 0,
                    "note": "추론 시 classifier 출력 로짓 중 misaligned(class 0)에 이 값을 더한 뒤 argmax"},
                   open(vdir / "calibration.json", "w"), ensure_ascii=False, indent=2)
        print(f"    [{variant}] 저장 완료 → {vdir}/ (model.pt, norm_stats.pt, calibration.json)")

    del model, opt, Ptr_t, Htr_t, Pte_t, Hte_t, ytr_t
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    return m_cal


def main():
    args = parse_args()
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)

    print("=== [1/3] 8도메인 dump 로드 (재추출 없음, 디스크 → RAM concat) ===")
    t0 = time.time()
    Ptr, Htr, ytr, Pte, Hte, yte, dom_te = load_pooled(args)
    lh, hd = Ptr.shape[-1], Htr.shape[-1]
    print(f"n_train={len(ytr)} n_test={len(yte)} lh={lh} hd={hd} (elapsed={time.time()-t0:.0f}s)")

    print("\n=== [2/3] 표준화 통계 (청크 스트리밍) ===")
    t0 = time.time()
    pmu, psd = streaming_mean_std(Ptr.reshape(-1, lh), args.stat_chunk * 32)
    hmu, hsd = streaming_mean_std(Htr, args.stat_chunk)
    print(f"표준화 통계 완료 (elapsed={time.time()-t0:.0f}s)")

    if args.save_dir is not None:
        save_root = Path(args.save_dir)
        save_root.mkdir(parents=True, exist_ok=True)
        # 추출 config를 그대로 복사해서 배포 패키지에 같이 담아둔다 — 다른 곳에서 재현하려면
        # 이 backend/전처리 설정을 100% 동일하게 맞춰야 하기 때문에 필수.
        src_run_meta = Path(f"{args.dumps_prefix}{args.domains[0]}") / "run_meta.json"
        if src_run_meta.exists():
            extract_cfg = json.load(open(src_run_meta))
            extract_cfg["domains_trained_on"] = args.domains
            extract_cfg["lh"] = lh
            extract_cfg["hd"] = hd
            json.dump(extract_cfg, open(save_root / "extract_config.json", "w"), ensure_ascii=False, indent=2)
        print(f"배포용 저장 위치: {save_root}/ (variant별 하위 폴더 + extract_config.json)")

    print("\n=== [3/3] 학습: baseline(attn, K=1024) vs hybrid(attn+hidden) ===")
    results = {}
    for variant in ["attn", "hybrid"]:
        t0 = time.time()
        m = train_eval_pooled(variant, Ptr, Htr, ytr, Pte, Hte, yte, dom_te, args, lh, hd,
                               pmu, psd, hmu, hsd, save_dir=args.save_dir)
        results[variant] = m
        print(f"[{variant}] Acc={m['acc']:.3f} FPR={m['fpr']} FNR={m['fnr']} risk={m['risk']} "
              f"bias={m['bias']:+.2f} macroF1={m['macro_f1']} "
              f"(raw: FPR={m['raw']['fpr']} FNR={m['raw']['fnr']} risk={m['raw']['risk']}) "
              f"(elapsed={time.time()-t0:.0f}s)")

    json.dump(results, open(out / "pooled_metrics.json", "w"), ensure_ascii=False, indent=2)
    print(f"\n결과 → {out / 'pooled_metrics.json'}")


if __name__ == "__main__":
    main()
