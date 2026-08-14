"""
Train/evaluate the paired three-class detector.

Expected features are produced by:
  python src/extract_paired_features.py pair-features ...

The detector factorizes the labels as:
  p(NI)  = 1 - pI
  p(AL)  = pI * (1 - pC)
  p(MIS) = pI * pC

where pI detects whether the tool response contains an instruction and pC
detects whether that instruction conflicts with user/system intent.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

ID_TO_LABEL = {0: "misaligned", 1: "aligned", 2: "non_instruction"}
LABEL_TO_ID = {v: k for k, v in ID_TO_LABEL.items()}
GROUP_A = ["coding", "cloud", "project", "shopping"]
GROUP_B = ["finance", "messaging", "social_media", "web"]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--features", required=True)
    p.add_argument("--results", required=True)
    p.add_argument("--models-dir", required=True)
    p.add_argument("--domains", nargs="+", default=["all"])
    p.add_argument("--epochs", type=int, default=120)
    p.add_argument("--lr", type=float, default=3e-4)
    p.add_argument("--batch-groups", type=int, default=16)
    p.add_argument("--hidden", type=int, default=128)
    p.add_argument("--dropout", type=float, default=0.2)
    p.add_argument("--weight-decay", type=float, default=1e-4)
    p.add_argument("--lambda-cls", type=float, default=1.0)
    p.add_argument("--lambda-pair", type=float, default=0.2)
    p.add_argument("--gamma-i", type=float, default=0.5)
    p.add_argument("--gamma-c", type=float, default=0.5)
    p.add_argument("--val-ratio", type=float, default=0.15)
    p.add_argument("--patience", type=int, default=20)
    p.add_argument("--standardize", action="store_true", default=True)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--device", default=None)
    p.add_argument("--run", nargs="+", default=["domain", "pooled", "cross"],
                   choices=["domain", "pooled", "cross"])
    return p.parse_args()


def discover_domains(feat_dir: Path) -> list[str]:
    return sorted({p.name[len("train_"):-len("_paired_meta.json")]
                   for p in feat_dir.glob("train_*_paired_meta.json")})


def load_split(feat_dir: Path, split: str, domain: str):
    meta_path = feat_dir / f"{split}_{domain}_paired_meta.json"
    with meta_path.open("r", encoding="utf-8") as f:
        meta = json.load(f)
    n = len(meta["labels"])
    XI = np.load(feat_dir / f"{split}_{domain}_pairs_I.npy", mmap_mode="r")[:n]
    XC = np.load(feat_dir / f"{split}_{domain}_pairs_C.npy", mmap_mode="r")[:n]
    y = np.asarray(meta["labels"], dtype=np.int64)
    return XI, XC, y, meta


class ConcatRows:
    def __init__(self, arrays):
        self.arrays = arrays
        self.offsets = np.cumsum([0] + [len(a) for a in arrays])
        self.shape = (int(self.offsets[-1]),) + tuple(arrays[0].shape[1:])

    def __len__(self):
        return self.shape[0]

    def __getitem__(self, idx):
        if isinstance(idx, slice):
            idx = np.arange(*idx.indices(len(self)))
        idx = np.asarray(idx)
        out = np.empty((len(idx),) + self.shape[1:], dtype=self.arrays[0].dtype)
        which = np.searchsorted(self.offsets, idx, side="right") - 1
        for k, arr in enumerate(self.arrays):
            pos = np.flatnonzero(which == k)
            if len(pos):
                out[pos] = arr[idx[pos] - self.offsets[k]]
        return out


def load_group(feat_dir: Path, domains: list[str], splits=("train",)):
    XIs, XCs, ys = [], [], []
    ids, base_ids, modes, doms = [], [], [], []
    backend = None
    for d in domains:
        for split in splits:
            XI, XC, y, meta = load_split(feat_dir, split, d)
            XIs.append(XI)
            XCs.append(XC)
            ys.append(y)
            ids.extend(meta["ids"])
            base_ids.extend(meta["base_pair_ids"])
            modes.extend(meta["construction_modes"])
            doms.extend(meta.get("domains", [d] * len(y)))
            backend = meta.get("model", backend)
    return {
        "XI": ConcatRows(XIs) if len(XIs) > 1 else XIs[0],
        "XC": ConcatRows(XCs) if len(XCs) > 1 else XCs[0],
        "y": np.concatenate(ys),
        "ids": ids,
        "base_ids": np.asarray(base_ids),
        "modes": np.asarray(modes),
        "domains": np.asarray(doms),
        "backend": backend,
    }


def materialize(X, device, torch_mod):
    torch = torch_mod
    n = len(X)
    t = torch.empty((n,) + tuple(X.shape[1:]), dtype=torch.float16)
    for i in range(0, n, 256):
        t[i:i + 256] = torch.from_numpy(np.array(X[i:i + 256], copy=True))
    gb = t.numel() * t.element_size() / 1e9
    if device.startswith("cuda"):
        try:
            t = t.to(device)
            print(f"    data resident on GPU ({gb:.1f} GB)")
            return t, True
        except torch.cuda.OutOfMemoryError:
            torch.cuda.empty_cache()
            print(f"    GPU OOM; using pinned CPU ({gb:.1f} GB)")
            return t.pin_memory(), False
    print(f"    data resident on CPU ({gb:.1f} GB)")
    return t, False


def metrics_from_preds(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    acc = float((y_true == y_pred).mean())
    pos = y_true == LABEL_TO_ID["misaligned"]
    neg = ~pos
    fnr = float((y_pred[pos] != LABEL_TO_ID["misaligned"]).mean()) if pos.any() else None
    fpr = float((y_pred[neg] == LABEL_TO_ID["misaligned"]).mean()) if neg.any() else None
    cm = np.zeros((3, 3), dtype=int)
    for t, p in zip(y_true, y_pred):
        cm[t, p] += 1
    per_class = {}
    for c, name in ID_TO_LABEL.items():
        tp = int(cm[c, c])
        pred = int(cm[:, c].sum())
        true = int(cm[c, :].sum())
        prec = tp / pred if pred else None
        rec = tp / true if true else None
        f1 = 2 * prec * rec / (prec + rec) if prec and rec and (prec + rec) else 0.0
        per_class[name] = {
            "precision": round(prec, 4) if prec is not None else None,
            "recall": round(rec, 4) if rec is not None else None,
            "f1": round(f1, 4),
            "support": true,
        }
    macro_f1 = float(np.mean([v["f1"] for v in per_class.values()]))
    return {
        "acc": round(acc, 4),
        "fpr": round(fpr, 4) if fpr is not None else None,
        "fnr": round(fnr, 4) if fnr is not None else None,
        "macro_f1": round(macro_f1, 4),
        "confusion": cm.tolist(),
        "per_class": per_class,
        "n_test": int(len(y_true)),
    }


def split_groups(base_ids: np.ndarray, val_ratio: float, seed: int):
    rng = np.random.default_rng(seed)
    groups = np.unique(base_ids)
    rng.shuffle(groups)
    n_val = int(round(len(groups) * val_ratio)) if val_ratio > 0 else 0
    val_groups = set(groups[:n_val])
    val_idx = np.flatnonzero(np.asarray([b in val_groups for b in base_ids]))
    train_idx = np.flatnonzero(np.asarray([b not in val_groups for b in base_ids]))
    return train_idx.astype(np.int64), val_idx.astype(np.int64)


def group_batches(base_ids: np.ndarray, train_idx: np.ndarray, batch_groups: int, rng):
    by = {}
    train_set = set(int(i) for i in train_idx)
    for i, bid in enumerate(base_ids):
        if i in train_set:
            by.setdefault(bid, []).append(i)
    gids = np.asarray(list(by.keys()), dtype=object)
    rng.shuffle(gids)
    for i in range(0, len(gids), batch_groups):
        idx = []
        for g in gids[i:i + batch_groups]:
            idx.extend(by[g])
        yield np.asarray(idx, dtype=np.int64)


def compute_standardizer(T, on_gpu, device, torch_mod):
    torch = torch_mod
    sample = T[: min(len(T), 512)]
    if not on_gpu:
        sample = sample.to(device, non_blocking=True)
    flat = sample.float().reshape(-1, sample.shape[-1])
    mu = flat.mean(dim=0)
    sd = flat.std(dim=0).clamp_min(1e-6)
    return mu, sd


def build_model(d_i: int, d_c: int, hidden: int, dropout: float):
    import torch
    import torch.nn as nn

    class Branch(nn.Module):
        def __init__(self, d):
            super().__init__()
            self.net = nn.Sequential(
                nn.LayerNorm(d),
                nn.Linear(d, 256),
                nn.GELU(),
                nn.Dropout(dropout),
                nn.Linear(256, hidden),
                nn.GELU(),
                nn.Dropout(dropout),
            )

        def forward(self, z):
            return self.net(z).mean(dim=1)

    class HierarchicalDetector(nn.Module):
        def __init__(self):
            super().__init__()
            self.instruction = Branch(d_i)
            self.conflict = Branch(d_c)
            self.logit_i = nn.Sequential(nn.LayerNorm(hidden), nn.Linear(hidden, 1))
            self.logit_c = nn.Sequential(nn.LayerNorm(hidden), nn.Linear(hidden, 1))

        def forward(self, xi, xc):
            hi = self.instruction(xi)
            hc = self.conflict(xc)
            return self.logit_i(hi).squeeze(-1), self.logit_c(hc).squeeze(-1)

        @staticmethod
        def probs(eta_i, eta_c):
            p_i = torch.sigmoid(eta_i)
            p_c = torch.sigmoid(eta_c)
            p_mis = p_i * p_c
            p_al = p_i * (1.0 - p_c)
            p_ni = 1.0 - p_i
            return torch.stack([p_mis, p_al, p_ni], dim=1)

    return HierarchicalDetector()


def train_eval(name: str, train, test, args, result_prefix: str):
    import time
    import torch
    import torch.nn.functional as F

    device = args.device or ("cuda" if torch.cuda.is_available() else "cpu")
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    rng = np.random.default_rng(args.seed)

    print(f"[{name}] loading features")
    XItr, i_gpu = materialize(train["XI"], device, torch)
    XCtr, c_gpu = materialize(train["XC"], device, torch)
    XIte, i_te_gpu = materialize(test["XI"], device, torch)
    XCte, c_te_gpu = materialize(test["XC"], device, torch)
    ytr = train["y"]
    yte = test["y"]
    ytr_t = torch.as_tensor(ytr, device=device)

    mu_i = sd_i = mu_c = sd_c = None
    if args.standardize:
        mu_i, sd_i = compute_standardizer(XItr, i_gpu, device, torch)
        mu_c, sd_c = compute_standardizer(XCtr, c_gpu, device, torch)

    def batch(T, on_gpu, idx, mu, sd):
        xb = T[idx] if on_gpu else T[idx].to(device, non_blocking=True)
        xb = xb.float()
        if mu is not None:
            xb = (xb - mu) / sd
        return xb

    train_idx, val_idx = split_groups(train["base_ids"], args.val_ratio, args.seed)
    print(f"[{name}] train rows={len(train_idx)} val rows={len(val_idx)}")

    model = build_model(XItr.shape[-1], XCtr.shape[-1], args.hidden, args.dropout).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)

    a_all = (ytr_t != LABEL_TO_ID["non_instruction"]).float()
    c_all = (ytr_t == LABEL_TO_ID["misaligned"]).float()
    a_train = (ytr[train_idx] != LABEL_TO_ID["non_instruction"]).astype(np.float32)
    c_train = (ytr[train_idx] == LABEL_TO_ID["misaligned"]).astype(np.float32)
    pos_i = max(a_train.sum(), 1.0)
    neg_i = max(len(a_train) - a_train.sum(), 1.0)
    inst_mask = a_train > 0
    pos_c = max(c_train[inst_mask].sum(), 1.0)
    neg_c = max(inst_mask.sum() - c_train[inst_mask].sum(), 1.0)
    pos_weight_i = torch.tensor(neg_i / pos_i, device=device)
    pos_weight_c = torch.tensor(neg_c / pos_c, device=device)

    def paired_margin_loss(idx_np, eta_i, eta_c):
        local = {int(global_i): j for j, global_i in enumerate(idx_np.tolist())}
        by = defaultdict(dict)
        for gi in idx_np:
            by[train["base_ids"][gi]][train["modes"][gi]] = local[int(gi)]
        li, lc = [], []
        for modes in by.values():
            if "non_instruction" in modes and "aligned" in modes:
                li.append(F.relu(args.gamma_i - eta_i[modes["aligned"]] + eta_i[modes["non_instruction"]]))
            if "aligned" in modes:
                for atk in ("misaligned_append", "misaligned_replace"):
                    if atk in modes:
                        lc.append(F.relu(args.gamma_c - eta_c[modes[atk]] + eta_c[modes["aligned"]]))
        zero = eta_i.sum() * 0.0
        loss_i = torch.stack(li).mean() if li else zero
        loss_c = torch.stack(lc).mean() if lc else zero
        return loss_i + loss_c

    def loss_for(idx_t, idx_np, eval_mode=False):
        xi = batch(XItr, i_gpu, idx_t, mu_i, sd_i)
        xc = batch(XCtr, c_gpu, idx_t, mu_c, sd_c)
        eta_i, eta_c = model(xi, xc)
        y_idx = idx_t.to(device)
        a = a_all[y_idx]
        c = c_all[y_idx]
        loss_i = F.binary_cross_entropy_with_logits(eta_i, a, pos_weight=pos_weight_i)
        mask = a > 0
        if mask.any():
            loss_c = F.binary_cross_entropy_with_logits(eta_c[mask], c[mask], pos_weight=pos_weight_c)
        else:
            loss_c = eta_c.sum() * 0.0
        loss = loss_i + args.lambda_cls * loss_c
        if not eval_mode and args.lambda_pair > 0:
            loss = loss + args.lambda_pair * paired_margin_loss(idx_np, eta_i, eta_c)
        return loss

    val_idx_t = torch.as_tensor(val_idx, device=device if i_gpu and c_gpu else "cpu")

    def val_loss():
        if len(val_idx) == 0:
            return 0.0
        model.eval()
        losses, seen = 0.0, 0
        with torch.no_grad():
            for b0 in range(0, len(val_idx), 256):
                part_np = val_idx[b0:b0 + 256]
                part_t = val_idx_t[b0:b0 + 256]
                loss = loss_for(part_t, part_np, eval_mode=True)
                losses += loss.item() * len(part_np)
                seen += len(part_np)
        return losses / max(seen, 1)

    best_state, best_val, bad = None, float("inf"), 0
    t0 = time.time()
    for epoch in range(args.epochs):
        model.train()
        total, seen = 0.0, 0
        for idx_np in group_batches(train["base_ids"], train_idx, args.batch_groups, rng):
            idx_t = torch.as_tensor(idx_np, device=device if i_gpu and c_gpu else "cpu")
            opt.zero_grad()
            loss = loss_for(idx_t, idx_np)
            loss.backward()
            opt.step()
            total += loss.item() * len(idx_np)
            seen += len(idx_np)
        cur_val = val_loss()
        if cur_val < best_val - 1e-5:
            best_val = cur_val
            best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
            bad = 0
        else:
            bad += 1
        if (epoch + 1) % 10 == 0:
            print(f"[{name}] epoch {epoch+1}/{args.epochs} loss={total/max(seen,1):.4f} "
                  f"val_loss={cur_val:.4f} elapsed={time.time()-t0:.0f}s", flush=True)
        if args.patience > 0 and bad >= args.patience:
            print(f"[{name}] early stop at epoch {epoch+1} (best_val={best_val:.4f})")
            break

    if best_state is not None:
        model.load_state_dict(best_state)

    model.eval()
    preds = []
    with torch.no_grad():
        for b0 in range(0, len(yte), 256):
            idx = torch.arange(b0, min(b0 + 256, len(yte)), device=XIte.device if i_te_gpu else "cpu")
            xi = batch(XIte, i_te_gpu, idx, mu_i, sd_i)
            xc = batch(XCte, c_te_gpu, idx, mu_c, sd_c)
            eta_i, eta_c = model(xi, xc)
            preds.append(model.probs(eta_i, eta_c).argmax(dim=1).cpu().numpy())
    y_pred = np.concatenate(preds)
    m = metrics_from_preds(yte, y_pred)
    m.update({
        "domain": name,
        "method": "paired_three_class",
        "backend_model": train["backend"],
        "input_dim_I": int(XItr.shape[-1]),
        "input_dim_C": int(XCtr.shape[-1]),
        "pairs_I": int(XItr.shape[1]),
        "pairs_C": int(XCtr.shape[1]),
        "epochs": args.epochs,
        "lr": args.lr,
        "batch_groups": args.batch_groups,
        "hidden": args.hidden,
        "dropout": args.dropout,
        "weight_decay": args.weight_decay,
        "lambda_cls": args.lambda_cls,
        "lambda_pair": args.lambda_pair,
        "gamma_i": args.gamma_i,
        "gamma_c": args.gamma_c,
        "n_train": int(len(ytr)),
        "n_fit": int(len(train_idx)),
        "best_val_loss": round(best_val, 6) if best_state is not None else None,
    })
    if test.get("domains") is not None:
        m["per_domain"] = {
            d: metrics_from_preds(yte[test["domains"] == d], y_pred[test["domains"] == d])
            for d in sorted(set(test["domains"]))
        }
    err = np.flatnonzero(y_pred != yte)
    m["n_errors"] = int(len(err))
    m["errors"] = [{"id": test["ids"][i], "true": ID_TO_LABEL[int(yte[i])],
                    "pred": ID_TO_LABEL[int(y_pred[i])]} for i in err[:500]]

    print(f"[{name}] Acc={m['acc']:.3f} MacroF1={m['macro_f1']:.3f} "
          f"FPR={m['fpr']:.3f} FNR={m['fnr']:.3f}")
    Path(args.models_dir).mkdir(parents=True, exist_ok=True)
    Path(args.results).mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), Path(args.models_dir) / f"{result_prefix}_{name}.pt")
    with (Path(args.results) / f"{result_prefix}_{name}.json").open("w", encoding="utf-8") as f:
        json.dump(m, f, ensure_ascii=False, indent=1)

    del XItr, XCtr, XIte, XCte
    if device.startswith("cuda"):
        torch.cuda.empty_cache()
    return m


def fmt(v, nd=3):
    return f"{v:.{nd}f}" if isinstance(v, (int, float)) else "-"


def write_summary(results_dir: Path, metrics: list[dict]) -> None:
    if not metrics:
        return
    backend = metrics[0].get("backend_model")
    lines = [
        "# Paired Three-Class IPI Results",
        "",
        f"- Backend LLM: `{backend}`",
        "- Method: paired head discovery + head-guided token-pair sampling + hierarchical detector",
        "- Labels: MIS=misaligned, AL=aligned, NI=non_instruction",
        "",
        "| setting | FPR | FNR | Acc | Macro-F1 | n_errors |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for m in metrics:
        lines.append(
            f"| {m['domain']} | {fmt(m['fpr'])} | {fmt(m['fnr'])} | {fmt(m['acc'])} | "
            f"{fmt(m['macro_f1'])} | {m.get('n_errors', '-')} |"
        )
    lines.append("")
    lines.append("## Per-Domain Breakdowns")
    for m in metrics:
        if "per_domain" not in m:
            continue
        lines.append("")
        lines.append(f"### {m['domain']}")
        lines.append("")
        lines.append("| domain | FPR | FNR | Acc | Macro-F1 |")
        lines.append("|---|---:|---:|---:|---:|")
        for d, dm in sorted(m["per_domain"].items()):
            lines.append(f"| {d} | {fmt(dm['fpr'])} | {fmt(dm['fnr'])} | {fmt(dm['acc'])} | {fmt(dm['macro_f1'])} |")
    with (results_dir / "summary.md").open("w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    with (results_dir / "summary_full.json").open("w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=1)


def main() -> None:
    args = parse_args()
    feat_dir = Path(args.features)
    domains = discover_domains(feat_dir) if args.domains == ["all"] else args.domains
    if not domains:
        raise SystemExit("no paired features found")

    metrics = []
    if "domain" in args.run:
        for d in domains:
            tr = load_group(feat_dir, [d], splits=("train",))
            te = load_group(feat_dir, [d], splits=("test",))
            metrics.append(train_eval(d, tr, te, args, "paired_domain"))

    if "pooled" in args.run:
        tr = load_group(feat_dir, domains, splits=("train",))
        te = load_group(feat_dir, domains, splits=("test",))
        metrics.append(train_eval("pooled", tr, te, args, "paired_pooled"))

    if "cross" in args.run:
        tr = load_group(feat_dir, GROUP_A, splits=("train", "test"))
        te = load_group(feat_dir, GROUP_B, splits=("train", "test"))
        metrics.append(train_eval("A2B", tr, te, args, "paired_cross"))
        tr = load_group(feat_dir, GROUP_B, splits=("train", "test"))
        te = load_group(feat_dir, GROUP_A, splits=("train", "test"))
        metrics.append(train_eval("B2A", tr, te, args, "paired_cross"))

    write_summary(Path(args.results), metrics)


if __name__ == "__main__":
    main()
