"""Hybrid 학습/평가 — attention(Enc-first류) vs hidden-state vs 결합, 같은 프로토콜로 3-way 비교.

yeon의 EncFirstRegularized(alignsentinel_replicate/src/train_detector.py)를 그대로 재사용해
attention 브랜치로 쓰고, 그 옆에 hidden-state 브랜치(같은 구조의 MLP)를 하나 더 붙여
128차원씩 인코딩한 뒤 concat(256) → classifier로 이어 붙인다(=Hybrid). attention 단독,
hidden 단독, 결합 셋을 같은 설정(AdamW, lr, dropout, class-weight, standardize,
val-based early stopping)으로 학습해 macroF1/FPR/FNR을 직접 비교한다.

입력: extract_hybrid.py가 만든 {split}_{domain}_pairs.npy / _hidden.npy / _meta.json.

실행 (pooled — 전체 도메인 train으로 학습, 전체 test로 평가):
  python src/train_hybrid.py --features dump_hybrid --variant attn
  python src/train_hybrid.py --features dump_hybrid --variant hidden
  python src/train_hybrid.py --features dump_hybrid --variant hybrid
  python src/train_hybrid.py --features dump_hybrid --variant all   # 셋 다 돌리고 리포트까지
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

ID_TO_LABEL = {0: "misaligned", 1: "aligned", 2: "non_instruction"}
MIS = 0


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--features", default="dump_hybrid")
    p.add_argument("--variant", choices=["attn", "hidden", "hybrid", "all"], default="all")
    p.add_argument("--out", default="results_hybrid")
    p.add_argument("--epochs", type=int, default=200)
    p.add_argument("--lr", type=float, default=1e-3)
    p.add_argument("--batch-size", type=int, default=16)
    p.add_argument("--dropout", type=float, default=0.2)
    p.add_argument("--weight-decay", type=float, default=1e-4)
    p.add_argument("--val-ratio", type=float, default=0.15)
    p.add_argument("--patience", type=int, default=25)
    p.add_argument("--class-weights", action="store_true", default=True)
    p.add_argument("--standardize", action="store_true", default=True)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--device", default=None)
    return p.parse_args()


def discover_domains(feat_dir: Path) -> list[str]:
    return sorted({p.name[len("train_"):-len("_meta.json")] for p in feat_dir.glob("train_*_meta.json")})


def load_split(feat_dir: Path, split: str, domain: str):
    with open(feat_dir / f"{split}_{domain}_meta.json", "r", encoding="utf-8") as f:
        meta = json.load(f)
    n = len(meta["labels"])
    y = np.asarray(meta["labels"], dtype=np.int64)
    pairs = np.load(feat_dir / f"{split}_{domain}_pairs.npy", mmap_mode="r")[:n]
    hidden = np.load(feat_dir / f"{split}_{domain}_hidden.npy")[:n]
    return pairs, hidden, y, meta


def load_group(feat_dir: Path, domains: list[str], split: str):
    Ps, Hs, Ys, doms, ids = [], [], [], [], []
    for d in domains:
        pairs, hidden, y, meta = load_split(feat_dir, split, d)
        Ps.append(np.asarray(pairs))
        Hs.append(hidden.reshape(len(y), -1))
        Ys.append(y)
        doms.extend([d] * len(y))
        ids.extend(meta["ids"])
    return (np.concatenate(Ps, 0), np.concatenate(Hs, 0), np.concatenate(Ys, 0),
            np.array(doms), ids)


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


def metrics_from_preds(y_true, y_pred):
    acc = float((y_true == y_pred).mean())
    pos = y_true == MIS
    neg = ~pos
    fnr = float((y_pred[pos] != MIS).mean()) if pos.any() else None
    fpr = float((y_pred[neg] == MIS).mean()) if neg.any() else None
    from sklearn.metrics import f1_score
    macro_f1 = float(f1_score(y_true, y_pred, average="macro"))
    return {"acc": round(acc, 4), "fpr": round(fpr, 4) if fpr is not None else None,
            "fnr": round(fnr, 4) if fnr is not None else None, "macro_f1": round(macro_f1, 4),
            "risk": weighted_risk(fpr, fnr), "n_test": int(len(y_true))}


def build_encoder(d, dropout):
    import torch.nn as nn
    return nn.Sequential(
        nn.LayerNorm(d), nn.Linear(d, 256), nn.GELU(), nn.Dropout(dropout),
        nn.Linear(256, 128), nn.GELU(), nn.Dropout(dropout))


def build_classifier(d, dropout):
    import torch.nn as nn
    return nn.Sequential(
        nn.LayerNorm(d), nn.Linear(d, 128), nn.GELU(), nn.Dropout(dropout), nn.Linear(128, 3))


def build_model(variant, lh, hd, dropout):
    import torch.nn as nn

    class AttnOnly(nn.Module):
        """encoder는 per-pair(B,K,lh)->128 후 K축 mean-pool (yeon EncFirstRegularized와 동일 구조)."""
        def __init__(self):
            super().__init__()
            self.enc = build_encoder(lh, dropout)
            self.clf = build_classifier(128, dropout)

        def forward(self, pairs, hidden):
            h = self.enc(pairs)            # (B,K,128)
            return self.clf(h.mean(dim=1))  # pool 후 분류

    class HiddenOnly(nn.Module):
        def __init__(self):
            super().__init__()
            self.enc = build_encoder(hd, dropout)
            self.clf = build_classifier(128, dropout)

        def forward(self, pairs, hidden):
            return self.clf(self.enc(hidden))

    class Hybrid(nn.Module):
        def __init__(self):
            super().__init__()
            self.attn_enc = build_encoder(lh, dropout)
            self.hidden_enc = build_encoder(hd, dropout)
            self.clf = build_classifier(256, dropout)

        def forward(self, pairs, hidden):
            a = self.attn_enc(pairs).mean(dim=1)   # (B,128) 토큰쌍 pool
            h = self.hidden_enc(hidden)            # (B,128)
            return self.clf(torch.cat([a, h], dim=1))

    import torch  # noqa: F401  (Hybrid.forward에서 torch.cat 참조)
    return {"attn": AttnOnly, "hidden": HiddenOnly, "hybrid": Hybrid}[variant]()


def train_eval(variant, Ptr, Htr, ytr, Pte, Hte, yte, args, lh, hd):
    import time
    import torch
    import torch.nn as nn

    device = args.device or ("cuda" if torch.cuda.is_available() else "cpu")
    torch.manual_seed(args.seed); np.random.seed(args.seed)

    Ptr_t = torch.tensor(np.asarray(Ptr), dtype=torch.float32, device=device)
    Htr_t = torch.tensor(Htr, dtype=torch.float32, device=device)
    ytr_t = torch.tensor(ytr, dtype=torch.long, device=device)
    Pte_t = torch.tensor(np.asarray(Pte), dtype=torch.float32, device=device)
    Hte_t = torch.tensor(Hte, dtype=torch.float32, device=device)

    if args.standardize:
        pmu = Ptr_t.reshape(-1, lh).mean(0); psd = Ptr_t.reshape(-1, lh).std(0).clamp_min(1e-8)
        hmu = Htr_t.mean(0); hsd = Htr_t.std(0).clamp_min(1e-8)
        Ptr_t = (Ptr_t - pmu) / psd; Pte_t = (Pte_t - pmu) / psd
        Htr_t = (Htr_t - hmu) / hsd; Hte_t = (Hte_t - hmu) / hsd

    train_idx_np, val_idx_np = stratified_train_val(ytr, args.val_ratio, args.seed)
    train_idx = torch.tensor(train_idx_np, device=device)
    val_idx = torch.tensor(val_idx_np, device=device) if len(val_idx_np) else None

    model = build_model(variant, lh, hd, args.dropout).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)
    weight = None
    if args.class_weights:
        counts = np.bincount(ytr[train_idx_np], minlength=3).astype(np.float32)
        weight = torch.tensor(counts.sum() / (3 * np.maximum(counts, 1.0)), dtype=torch.float32, device=device)
    loss_fn = nn.CrossEntropyLoss(weight=weight)

    def eval_logits(idx, Ptensor, Htensor):
        model.eval()
        with torch.no_grad():
            outs = []
            for b0 in range(0, len(idx), 64):
                bi = idx[b0:b0 + 64]
                outs.append(model(Ptensor[bi], Htensor[bi]).cpu())
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
        perm = train_idx[torch.randperm(len(train_idx), device=device)]
        for b0 in range(0, len(perm), args.batch_size):
            bi = perm[b0:b0 + args.batch_size]
            opt.zero_grad()
            logits = model(Ptr_t[bi], Htr_t[bi])
            loss = loss_fn(logits, ytr_t[bi])
            loss.backward()
            opt.step()
        if val_idx is not None:
            vloss, vacc, vrisk = val_risk(val_idx)
            # 체크포인트 기준: val loss가 아니라 val weighted-risk(0.25*FPR+0.75*FNR) 최소화.
            # 단순 정확도/loss는 FNR을 3배 중요시하는 목표와 안 맞을 수 있어서 직접 이 지표로 고른다.
            if vrisk < best_risk - 1e-5:
                best_risk = vrisk
                best_state = {k: v.detach().clone() for k, v in model.state_dict().items()}
                bad = 0
            else:
                bad += 1
            if bad >= args.patience:
                print(f"  [{variant}] early stop @ epoch {epoch+1} (best_val_risk={best_risk:.4f})")
                break
        if (epoch + 1) % 20 == 0:
            print(f"  [{variant}] epoch {epoch+1}/{args.epochs} elapsed={time.time()-t0:.0f}s"
                  + (f" val_acc={vacc:.3f} val_risk={vrisk:.4f}" if val_idx is not None else ""))

    if best_state is not None:
        model.load_state_dict(best_state)

    # ---- 임계값 보정: misaligned(class 0) 로짓에 bias를 더해 val에서 weighted-risk를 최소화하는
    #      bias를 찾고, 그 값을 test에도 그대로 적용한다. 재학습 없이 FPR↔FNR을 원하는 방향으로
    #      옮기는 저비용 보정(0.25*FPR+0.75*FNR이 목표면 misaligned를 더 잘 잡는 쪽으로 밀 유인이 큼).
    bias = 0.0
    if val_idx is not None:
        val_logits = eval_logits(val_idx, Ptr_t, Htr_t)
        yv = ytr[val_idx.cpu().numpy()]
        best_bias, best_bias_risk = 0.0, metrics_from_preds(yv, val_logits.argmax(1).numpy())["risk"]
        for b in np.arange(-3.0, 3.01, 0.1):
            shifted = val_logits.clone(); shifted[:, MIS] += b
            r = metrics_from_preds(yv, shifted.argmax(1).numpy())["risk"]
            if r is not None and r < best_bias_risk - 1e-6:
                best_bias_risk, best_bias = r, float(b)
        bias = best_bias
        print(f"  [{variant}] 임계값 보정: misaligned bias={bias:+.2f} (val risk {metrics_from_preds(yv, val_logits.argmax(1).numpy())['risk']} → {best_bias_risk})")

    test_logits = eval_logits(torch.arange(len(yte)), Pte_t, Hte_t)
    y_pred_raw = test_logits.argmax(1).numpy()
    test_logits[:, MIS] += bias
    y_pred_calibrated = test_logits.argmax(1).numpy()

    m_raw = metrics_from_preds(yte, y_pred_raw)
    m_cal = metrics_from_preds(yte, y_pred_calibrated)
    m_cal["bias"] = round(bias, 2)
    m_cal["raw"] = m_raw
    return m_cal


def run_variant(variant, feat_dir, domains, args):
    Ptr, Htr, ytr, _, _ = load_group(feat_dir, domains, "train")
    Pte, Hte, yte, _, _ = load_group(feat_dir, domains, "test")
    lh, hd = Ptr.shape[-1], Htr.shape[-1]
    m = train_eval(variant, Ptr, Htr, ytr, Pte, Hte, yte, args, lh, hd)
    print(f"[{variant}] Acc={m['acc']:.3f} macroF1={m['macro_f1']:.3f} "
          f"FPR={m['fpr']} FNR={m['fnr']} risk={m['risk']} bias={m['bias']:+.2f} "
          f"(raw: FPR={m['raw']['fpr']} FNR={m['raw']['fnr']} risk={m['raw']['risk']}) (n_test={m['n_test']})")
    return m


def main():
    args = parse_args()
    feat_dir = Path(args.features)
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    domains = discover_domains(feat_dir)
    if not domains:
        raise SystemExit(f"{feat_dir}에 추출된 도메인이 없습니다 — extract_hybrid.py 먼저 실행")
    print(f"pooled: 도메인 {domains}")

    variants = ["attn", "hidden", "hybrid"] if args.variant == "all" else [args.variant]
    results = {}
    for v in variants:
        results[v] = run_variant(v, feat_dir, domains, args)
        import gc
        import torch
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    if len(results) > 1:
        lines = [f"# Hybrid 스모크 테스트 결과 (features={feat_dir})\n",
                 "| variant | Acc | macroF1 | FPR | FNR | risk(0.25FPR+0.75FNR) | bias | n_test |",
                 "|---|---|---|---|---|---|---|---|"]
        for v, m in results.items():
            lines.append(f"| {v} | {m['acc']:.3f} | {m['macro_f1']:.3f} | {m['fpr']} | {m['fnr']} | "
                          f"{m['risk']} | {m['bias']:+.2f} | {m['n_test']} |")
        if "hybrid" in results and "attn" in results:
            d = results["hybrid"]["macro_f1"] - results["attn"]["macro_f1"]
            dr = results["hybrid"]["risk"] - results["attn"]["risk"]
            lines.append(f"\nΔ macroF1 (hybrid − attn) = **{d:+.3f}**")
            lines.append(f"\nΔ risk (hybrid − attn) = **{dr:+.4f}** (음수면 hybrid가 목표 지표상 더 좋음)")
            lines.append("→ hidden 결합이 attention 단독 대비 이득 있음 (본 실험 규모로 재검증 권장)."
                          if d >= 0.01 else "→ 이 규모에선 뚜렷한 이득 없음 (표본이 작아 잡음일 수 있음, 본 실험 필요).")
        report = out / "hybrid_smoke_report.md"
        report.write_text("\n".join(lines), encoding="utf-8")
        print(f"\n리포트 → {report}")
    json.dump(results, open(out / "hybrid_smoke_metrics.json", "w"), ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
