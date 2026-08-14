"""Hybrid 개선안 5종 — baseline(attn/hidden/hybrid, train_hybrid.py) 대비 각각 단독 효과를 보고,
좋은 것들을 묶어 combo까지 시도한다.

  #1 attn_pool     mean-pool → 학습되는 attention-pooling (쿼리 벡터로 쌍별 가중합)
  #2 hidden_tok    미리 뭉갠 hidden 요약 대신, tool-response 토큰 단위로 인코딩 후 masked mean-pool
  #3 attn_headsel  LH=960개 head 중 train에서 AUC(misaligned vs rest) 상위 N개만 선택해 입력 차원 축소
  #4 attn_bigK     mean-pool 그대로, 토큰쌍 수만 1024→2048 (dump_hybrid_coding_v2 사용)
  #5 hybrid_gated  h_attn/h_hidden을 concat 대신 학습되는 gate(sigmoid)로 섞음
  #6 combo         위에서 이긴 것들을 조합 (실행 후 --combo로 구성 요소 지정)

#1,#3,#5는 dump_hybrid_coding(K=1024, pre-pooled hidden)을 쓰고,
#2,#4는 dump_hybrid_coding_v2(K=2048, token-level hidden 추가)를 쓴다.

실행:
  python src/train_hybrid_v2.py --features dump_hybrid_coding --features-v2 dump_hybrid_coding_v2 \
      --variant all --out results_hybrid_v2
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from train_hybrid import (
    discover_domains, load_split, load_group, stratified_train_val,
    metrics_from_preds, build_encoder, build_classifier, MIS,
)


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--features", default="dump_hybrid_coding", help="K=1024, pre-pooled hidden (v1)")
    p.add_argument("--features-v2", default="dump_hybrid_coding_v2", help="K=2048 + token-hidden (v2)")
    p.add_argument("--variant", default="all",
                    choices=["attn_pool", "hidden_tok", "attn_headsel", "attn_bigK", "hybrid_gated",
                             "combo", "all"])
    p.add_argument("--out", default="results_hybrid_v2")
    p.add_argument("--epochs", type=int, default=200)
    p.add_argument("--lr", type=float, default=1e-3)
    p.add_argument("--batch-size", type=int, default=16)
    p.add_argument("--dropout", type=float, default=0.2)
    p.add_argument("--weight-decay", type=float, default=1e-4)
    p.add_argument("--val-ratio", type=float, default=0.15)
    p.add_argument("--patience", type=int, default=25)
    p.add_argument("--n-heads-select", type=int, default=200, help="attn_headsel: 선택할 head 수 (전체 960)")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--device", default=None)
    p.add_argument("--combo", nargs="*", default=None,
                    help="combo 조합에 쓸 요소: attn_pool|attn_headsel|attn_bigK, hidden_tok|hidden, gated|concat")
    return p.parse_args()


# ---------------- 데이터 로더 (v2: pairs + token-hidden) ----------------

def load_split_v2(feat_dir: Path, split: str, domain: str):
    with open(feat_dir / f"{split}_{domain}_meta.json", "r", encoding="utf-8") as f:
        meta = json.load(f)
    n = len(meta["labels"])
    y = np.asarray(meta["labels"], dtype=np.int64)
    pairs = np.asarray(np.load(feat_dir / f"{split}_{domain}_pairs.npy", mmap_mode="r")[:n])
    tok = np.load(feat_dir / f"{split}_{domain}_hidden_tok.npy")[:n]
    mask = np.load(feat_dir / f"{split}_{domain}_hidden_tok_mask.npy")[:n]
    return pairs, tok, mask, y, meta


def load_group_v2(feat_dir: Path, domains, split: str):
    Ps, Ts, Ms, Ys = [], [], [], []
    for d in domains:
        pairs, tok, mask, y, _ = load_split_v2(feat_dir, d, split) if False else load_split_v2(feat_dir, split, d)
        Ps.append(pairs); Ts.append(tok); Ms.append(mask); Ys.append(y)
    return (np.concatenate(Ps, 0), np.concatenate(Ts, 0), np.concatenate(Ms, 0), np.concatenate(Ys, 0))


# ---------------- 모델 ----------------

def build_learned_pool(d, torch, nn):
    class LearnedAttnPool(nn.Module):
        def __init__(self):
            super().__init__()
            self.query = nn.Parameter(torch.randn(d) * 0.02)
            self.scale = d ** -0.5

        def forward(self, h, mask=None):  # h: (B,K,d)
            scores = (h * self.query).sum(-1) * self.scale  # (B,K)
            if mask is not None:
                scores = scores.masked_fill(mask == 0, float("-inf"))
            w = torch.softmax(scores, dim=1).unsqueeze(-1)
            return (h * w).sum(1)
    return LearnedAttnPool()


def make_mean_pool_attn(lh, dropout):
    import torch.nn as nn

    class MeanPoolAttn(nn.Module):
        def __init__(self):
            super().__init__()
            self.enc = build_encoder(lh, dropout)
            self.clf = build_classifier(128, dropout)

        def forward(self, pairs):
            return self.clf(self.enc(pairs).mean(dim=1))
    return MeanPoolAttn()


def make_attn_pool_model(lh, dropout):
    import torch
    import torch.nn as nn

    class AttnPoolModel(nn.Module):
        def __init__(self):
            super().__init__()
            self.enc = build_encoder(lh, dropout)
            self.pool = build_learned_pool(128, torch, nn)
            self.clf = build_classifier(128, dropout)

        def forward(self, pairs):
            return self.clf(self.pool(self.enc(pairs)))
    return AttnPoolModel()


def make_hidden_tok_model(hidden_dim, dropout):
    import torch.nn as nn

    class HiddenTokModel(nn.Module):
        def __init__(self):
            super().__init__()
            self.enc = build_encoder(hidden_dim, dropout)
            self.clf = build_classifier(128, dropout)

        def forward(self, tok, mask):
            h = self.enc(tok)                       # (B,T,128)
            mf = mask.unsqueeze(-1).float()
            pooled = (h * mf).sum(1) / mf.sum(1).clamp_min(1.0)
            return self.clf(pooled)
    return HiddenTokModel()


def make_gated_hybrid(lh, hd, dropout):
    import torch
    import torch.nn as nn

    class GatedHybrid(nn.Module):
        def __init__(self):
            super().__init__()
            self.attn_enc = build_encoder(lh, dropout)
            self.hidden_enc = build_encoder(hd, dropout)
            self.gate = nn.Sequential(nn.Linear(256, 128), nn.Sigmoid())
            self.clf = build_classifier(128, dropout)

        def forward(self, pairs, hidden):
            a = self.attn_enc(pairs).mean(dim=1)
            h = self.hidden_enc(hidden)
            g = self.gate(torch.cat([a, h], dim=1))
            return self.clf(g * a + (1 - g) * h)
    return GatedHybrid()


# ---------------- 학습 루프 (variant별 forward 시그니처만 다름) ----------------

def _standardize(train_arrs, test_arrs, flatten_dims):
    """train 통계로 표준화. flatten_dims[i]=True인 배열만 (마지막 축 기준) 표준화."""
    out_tr, out_te = [], []
    for tr, te, do in zip(train_arrs, test_arrs, flatten_dims):
        if not do:
            out_tr.append(tr); out_te.append(te); continue
        d = tr.shape[-1]
        flat = tr.reshape(-1, d)
        mu = flat.mean(0, keepdim=True); sd = flat.std(0, keepdim=True).clamp_min(1e-8)
        shape_tr = [1] * (tr.dim() - 1) + [d]
        out_tr.append((tr - mu.view(*shape_tr)) / sd.view(*shape_tr))
        out_te.append((te - mu.view(*shape_tr)) / sd.view(*shape_tr))
    return out_tr, out_te


def train_eval_generic(model, forward_fn, train_arrays, ytr, test_arrays, yte, args):
    """train_arrays/test_arrays는 CPU 텐서로 받는다 — 배치만 GPU로 올려서 큰 K(토큰쌍)에서도
    OOM 없이 돌게 한다(yeon의 pooled Enc-first와 동일한 메모리 전략)."""
    import time
    import torch
    import torch.nn as nn

    device = args.device or ("cuda" if torch.cuda.is_available() else "cpu")
    torch.manual_seed(args.seed); np.random.seed(args.seed)
    model = model.to(device)

    train_idx_np, val_idx_np = stratified_train_val(ytr, args.val_ratio, args.seed)
    train_idx = torch.tensor(train_idx_np)                    # CPU
    val_idx = torch.tensor(val_idx_np) if len(val_idx_np) else None  # CPU
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
                batch = batch_of(train_arrays, bi)
                yb = ytr_t[bi.to(device)]
                logits = forward_fn(model, batch)
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
            batch = batch_of(train_arrays, bi)
            yb = ytr_t[bi.to(device)]
            opt.zero_grad()
            loss = loss_fn(forward_fn(model, batch), yb)
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
        if (epoch + 1) % 40 == 0:
            print(f"    epoch {epoch+1}/{args.epochs} elapsed={time.time()-t0:.0f}s"
                  + (f" val_acc={vacc:.3f}" if val_idx is not None else ""))

    if best_state is not None:
        model.load_state_dict(best_state)
    model.eval()
    with torch.no_grad():
        preds = []
        n_te = len(yte)
        idx_all = torch.arange(n_te)
        for b0 in range(0, n_te, 64):
            batch = batch_of(test_arrays, idx_all[b0:b0 + 64])
            preds.append(forward_fn(model, batch).argmax(1).cpu().numpy())
    y_pred = np.concatenate(preds)
    return metrics_from_preds(yte, y_pred)


def to_tensor(x, device, dtype):
    import torch
    return torch.tensor(np.asarray(x), dtype=dtype, device=device)


def run_attn_pool(feat_dir, domains, args):
    import torch
    device = "cpu"
    Ptr, Htr, ytr, _, _ = load_group(feat_dir, domains, "train")
    Pte, Hte, yte, _, _ = load_group(feat_dir, domains, "test")
    lh = Ptr.shape[-1]
    Ptr_t = to_tensor(Ptr, device, torch.float32); Pte_t = to_tensor(Pte, device, torch.float32)
    [Ptr_t], [Pte_t] = _standardize([Ptr_t], [Pte_t], [True])
    model = make_attn_pool_model(lh, args.dropout)
    return train_eval_generic(model, lambda m, b: m(b[0]), [Ptr_t], ytr, [Pte_t], yte, args)


def run_attn_bigK(feat_dir_v2, domains, args):
    import torch
    device = "cpu"
    Ptr, Ttr, Mtr, ytr = load_group_v2(feat_dir_v2, domains, "train")
    Pte, Tte, Mte, yte = load_group_v2(feat_dir_v2, domains, "test")
    lh = Ptr.shape[-1]
    Ptr_t = to_tensor(Ptr, device, torch.float32); Pte_t = to_tensor(Pte, device, torch.float32)
    [Ptr_t], [Pte_t] = _standardize([Ptr_t], [Pte_t], [True])
    model = make_mean_pool_attn(lh, args.dropout)
    return train_eval_generic(model, lambda m, b: m(b[0]), [Ptr_t], ytr, [Pte_t], yte, args)


def run_hidden_tok(feat_dir_v2, domains, args):
    import torch
    device = "cpu"
    Ptr, Ttr, Mtr, ytr = load_group_v2(feat_dir_v2, domains, "train")
    Pte, Tte, Mte, yte = load_group_v2(feat_dir_v2, domains, "test")
    hd = Ttr.shape[-1]
    Ttr_t = to_tensor(Ttr, device, torch.float32); Tte_t = to_tensor(Tte, device, torch.float32)
    Mtr_t = to_tensor(Mtr, device, torch.float32); Mte_t = to_tensor(Mte, device, torch.float32)
    model = make_hidden_tok_model(hd, args.dropout)
    return train_eval_generic(model, lambda m, b: m(b[0], b[1]), [Ttr_t, Mtr_t], ytr, [Tte_t, Mte_t], yte, args)


def rank_heads_by_auc(Ptr, ytr, H_layers_x_heads=None):
    """train에서 head별 g_mean-like 값(K축 평균)으로 misaligned-vs-rest AUC 랭킹."""
    from sklearn.metrics import roc_auc_score
    g = Ptr.mean(axis=1)  # (n, LH) — K(토큰쌍) 축 평균
    y_mis = (ytr == MIS).astype(int)
    aucs = np.array([roc_auc_score(y_mis, g[:, h]) for h in range(g.shape[1])])
    order = np.argsort(-np.abs(aucs - 0.5))
    return order, aucs


def run_attn_headsel(feat_dir, domains, args):
    import torch
    device = "cpu"
    Ptr, Htr, ytr, _, _ = load_group(feat_dir, domains, "train")
    Pte, Hte, yte, _, _ = load_group(feat_dir, domains, "test")
    order, aucs = rank_heads_by_auc(Ptr, ytr)
    sel = order[: args.n_heads_select]
    print(f"    top head AUC(|.-.5|)={np.abs(aucs[sel]-0.5).max():.3f}..{np.abs(aucs[sel]-0.5).min():.3f}, "
          f"selected {len(sel)}/{Ptr.shape[-1]} heads")
    Ptr_sel, Pte_sel = Ptr[:, :, sel], Pte[:, :, sel]
    Ptr_t = to_tensor(Ptr_sel, device, torch.float32); Pte_t = to_tensor(Pte_sel, device, torch.float32)
    [Ptr_t], [Pte_t] = _standardize([Ptr_t], [Pte_t], [True])
    model = make_mean_pool_attn(len(sel), args.dropout)
    return train_eval_generic(model, lambda m, b: m(b[0]), [Ptr_t], ytr, [Pte_t], yte, args), sel


def run_hybrid_gated(feat_dir, domains, args):
    import torch
    device = "cpu"
    Ptr, Htr, ytr, _, _ = load_group(feat_dir, domains, "train")
    Pte, Hte, yte, _, _ = load_group(feat_dir, domains, "test")
    lh, hd = Ptr.shape[-1], Htr.shape[-1]
    Ptr_t = to_tensor(Ptr, device, torch.float32); Pte_t = to_tensor(Pte, device, torch.float32)
    Htr_t = to_tensor(Htr, device, torch.float32); Hte_t = to_tensor(Hte, device, torch.float32)
    [Ptr_t, Htr_t], [Pte_t, Hte_t] = _standardize([Ptr_t, Htr_t], [Pte_t, Hte_t], [True, True])
    model = make_gated_hybrid(lh, hd, args.dropout)
    return train_eval_generic(model, lambda m, b: m(b[0], b[1]), [Ptr_t, Htr_t], ytr, [Pte_t, Hte_t], yte, args)


def main():
    args = parse_args()
    feat_dir = Path(args.features)
    feat_dir_v2 = Path(args.features_v2)
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    domains = discover_domains(feat_dir)
    print(f"domains: {domains}")

    baseline = {"attn": {"acc": 0.895, "macro_f1": 0.880, "fpr": 0.11, "fnr": 0.0375},
                "hidden": {"acc": 0.902, "macro_f1": 0.889, "fpr": 0.0825, "fnr": 0.0425},
                "hybrid": {"acc": 0.889, "macro_f1": 0.873, "fpr": 0.1425, "fnr": 0.0175}}

    results = dict(baseline)
    variants = ["attn_pool", "hidden_tok", "attn_headsel", "attn_bigK", "hybrid_gated"] \
        if args.variant == "all" else [args.variant]

    head_sel_idx = None
    for v in variants:
        print(f"\n=== [{v}] ===")
        if v == "attn_pool":
            results[v] = run_attn_pool(feat_dir, domains, args)
        elif v == "hidden_tok":
            results[v] = run_hidden_tok(feat_dir_v2, domains, args)
        elif v == "attn_headsel":
            results[v], head_sel_idx = run_attn_headsel(feat_dir, domains, args)
        elif v == "attn_bigK":
            results[v] = run_attn_bigK(feat_dir_v2, domains, args)
        elif v == "hybrid_gated":
            results[v] = run_hybrid_gated(feat_dir, domains, args)
        m = results[v]
        print(f"[{v}] Acc={m['acc']:.3f} macroF1={m['macro_f1']:.3f} FPR={m['fpr']} FNR={m['fnr']}")
        import gc
        import torch
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    lines = ["# Hybrid 개선안 5종 결과 (coding 도메인)\n",
             "| variant | Acc | macroF1 | FPR | FNR |", "|---|---|---|---|---|"]
    for name in ["attn", "hidden", "hybrid", "attn_pool", "hidden_tok", "attn_headsel", "attn_bigK", "hybrid_gated"]:
        if name in results:
            m = results[name]
            lines.append(f"| {name} | {m['acc']:.3f} | {m['macro_f1']:.3f} | {m['fpr']} | {m['fnr']} |")
    report = out / "improvements_report.md"
    report.write_text("\n".join(lines), encoding="utf-8")
    json.dump(results, open(out / "improvements_metrics.json", "w"), ensure_ascii=False, indent=2)
    print(f"\n리포트 → {report}")


if __name__ == "__main__":
    main()
