"""
AlignSentinel 재현 — 2·3단계: 분류기 학습 + 평가 (indirect).

논문 설정을 그대로 따른다:
  - 도메인별 detector. 도메인 안에서 agent 8개 train / 2개 test (데이터의 split 필드 사용).
  - Avg-first (Table 5): Linear(L·H→128) → ReLU → Linear(128→3). batch 32.
  - Enc-first (Table 8): 인코더 Linear(L·H→128)→ReLU→Linear(128→128)→ReLU,
    토큰쌍 mean pooling, 분류기 Linear(128→128)→ReLU→Linear(128→3). batch 16.
  - 공통: 200 epochs, lr 0.01. (옵티마이저는 논문 미명시 → Adam 사용, README 편차 D3)
  - 지표: 3-class Acc + 이진 FPR/FNR (misaligned=positive, aligned/non-instruction=negative).

Cross-domain generalization (논문 Table 3): 도메인을 두 그룹으로 나눠 한 그룹 전체로
학습하고 다른 그룹 전체로 평가한다. 논문의 그룹 구성(Coding/Ent./Shopping/Teaching vs
Lang./Msg./Media/Web)에 대응해 우리 도메인은 A={coding, cloud, project, shopping},
B={finance, messaging, social_media, web}로 나눈다 (논문과 공통인 coding·shopping은 A,
messaging·social_media·web은 B에 배치). 학습 도메인과 평가 도메인이 아예 겹치지 않으므로
그룹 내부의 agent 8:2 split은 쓰지 않고 각 도메인의 전체 샘플(2,000건)을 사용한다.

실행:
  python src/train_detector.py --features features --variant avg --domains all
  python src/train_detector.py --features features --variant enc --domains all
  python src/train_detector.py --features features --variant avg --cross A2B
  python src/train_detector.py --features features --variant enc --cross B2A

Pooled 모드: 8개 도메인의 train split 전체(12,800건)로 detector 하나를 학습하고
전체 test split(3,200건, 학습에서 못 본 agent들)로 평가한다. 결과에는 도메인별
분해 지표도 함께 기록된다.

  python src/train_detector.py --features features --variant avg --pooled

커스텀 detector: 데이터가 논문보다 작을 때 과적합을 줄이기 위해 dropout, AdamW,
class weighting, train 내부 stratified validation 기반 early stopping을 추가한
regularized detector를 쓸 수 있다.

  python src/train_detector.py --features features --variant enc --pooled \
      --detector regularized --standardize --class-weights
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

ID_TO_LABEL = {0: "misaligned", 1: "aligned", 2: "non_instruction"}

# 논문 Table 3의 그룹 분할에 대응하는 우리 도메인 구성
GROUP_A = ["coding", "cloud", "project", "shopping"]
GROUP_B = ["finance", "messaging", "social_media", "web"]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--features", default="features")
    p.add_argument("--variant", choices=["avg", "enc"], required=True)
    p.add_argument("--domains", nargs="+", default=["all"])
    p.add_argument("--cross", choices=["A2B", "B2A"], default=None,
                   help="cross-domain 모드: A2B=그룹A 학습→그룹B 평가, B2A=반대 (논문 Table 3)")
    p.add_argument("--pooled", action="store_true",
                   help="8개 도메인 통합: 전체 train split으로 학습, 전체 test split으로 평가")
    p.add_argument("--epochs", type=int, default=200)
    p.add_argument("--lr", type=float, default=0.01)
    p.add_argument("--batch-size", type=int, default=None, help="기본: avg=32, enc=16 (논문)")
    p.add_argument("--detector", choices=["paper", "regularized"], default="paper",
                   help="paper=논문 MLP, regularized=작은 데이터용 정규화 detector")
    p.add_argument("--dropout", type=float, default=0.2)
    p.add_argument("--weight-decay", type=float, default=1e-4)
    p.add_argument("--class-weights", action="store_true",
                   help="train label 빈도 역비례 class weight를 CrossEntropy에 적용")
    p.add_argument("--val-ratio", type=float, default=0.15,
                   help="regularized detector의 train 내부 validation 비율")
    p.add_argument("--patience", type=int, default=25,
                   help="regularized detector early stopping patience (0이면 비활성)")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--device", default=None)
    p.add_argument("--standardize", action="store_true",
                   help="train 통계로 특징을 z-score 정규화 (attention 값이 ~0.001 스케일로 작아서 도움이 될 수 있음)")
    p.add_argument("--results", default="results")
    p.add_argument("--models-dir", default="models")
    return p.parse_args()


def discover_domains(feat_dir: Path) -> list[str]:
    return sorted({p.name[len("train_"):-len("_meta.json")] for p in feat_dir.glob("train_*_meta.json")})


def build_model(variant: str, input_dim: int, detector: str = "paper", dropout: float = 0.0):
    import torch.nn as nn

    if detector == "paper" and variant == "avg":
        # 논문 Table 5
        return nn.Sequential(nn.Linear(input_dim, 128), nn.ReLU(), nn.Linear(128, 3))

    if detector == "regularized" and variant == "avg":
        return nn.Sequential(
            nn.LayerNorm(input_dim),
            nn.Linear(input_dim, 256),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(256, 128),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(128, 3),
        )

    class EncFirstPaper(nn.Module):
        # 논문 Table 8: 토큰쌍별 인코딩 → mean pool → 분류
        def __init__(self, d):
            super().__init__()
            self.encoder = nn.Sequential(nn.Linear(d, 128), nn.ReLU(), nn.Linear(128, 128), nn.ReLU())
            self.classifier = nn.Sequential(nn.Linear(128, 128), nn.ReLU(), nn.Linear(128, 3))

        def forward(self, z):          # z: (B, K, d)
            h = self.encoder(z)        # (B, K, 128)
            return self.classifier(h.mean(dim=1))

    class EncFirstRegularized(nn.Module):
        # 작은 데이터셋에서 과적합을 줄이기 위한 LayerNorm + Dropout 변형
        def __init__(self, d):
            super().__init__()
            self.encoder = nn.Sequential(
                nn.LayerNorm(d),
                nn.Linear(d, 256),
                nn.GELU(),
                nn.Dropout(dropout),
                nn.Linear(256, 128),
                nn.GELU(),
                nn.Dropout(dropout),
            )
            self.classifier = nn.Sequential(
                nn.LayerNorm(128),
                nn.Linear(128, 128),
                nn.GELU(),
                nn.Dropout(dropout),
                nn.Linear(128, 3),
            )

        def forward(self, z):          # z: (B, K, d)
            h = self.encoder(z)        # (B, K, 128)
            return self.classifier(h.mean(dim=1))

    return EncFirstRegularized(input_dim) if detector == "regularized" else EncFirstPaper(input_dim)


def load_split(feat_dir: Path, split: str, domain: str, variant: str):
    with open(feat_dir / f"{split}_{domain}_meta.json", "r", encoding="utf-8") as f:
        meta = json.load(f)
    n = len(meta["labels"])
    y = np.asarray(meta["labels"], dtype=np.int64)
    if variant == "avg":
        X = np.load(feat_dir / f"{split}_{domain}_avg.npy")[:n]
    else:
        X = np.load(feat_dir / f"{split}_{domain}_pairs.npy", mmap_mode="r")[:n]
    return X, y, meta


class ConcatRows:
    """여러 (memmap) 배열을 RAM에 합치지 않고 하나처럼 인덱싱하는 래퍼.

    Enc-first의 pairs 배열은 도메인당 수 GB라 cross-domain 학습 시 np.concatenate로
    합치면 RAM을 20GB 가까이 먹는다. 배치 단위 gather만 지원하면 되므로 lazy로 처리.
    """

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
        parts = []
        which = np.searchsorted(self.offsets, idx, side="right") - 1
        for k in range(len(self.arrays)):
            local = idx[which == k] - self.offsets[k]
            if len(local):
                parts.append((np.flatnonzero(which == k), np.asarray(self.arrays[k][local])))
        out = np.empty((len(idx),) + self.shape[1:], dtype=parts[0][1].dtype)
        for pos, block in parts:
            out[pos] = block
        return out


def load_group(feat_dir: Path, domains: list[str], variant: str, splits=("train", "test")):
    """도메인 목록의 지정 split 샘플들을 이어붙여 반환.

    cross-domain은 splits=('train','test') 전체, pooled는 한쪽 split만 쓴다.
    반환: (X, y, backend_model, 샘플별 도메인 배열, 샘플별 id 리스트)
    """
    Xs, ys, doms, ids = [], [], [], []
    backend = None
    for d in domains:
        for split in splits:
            X, y, meta = load_split(feat_dir, split, d, variant)
            Xs.append(X)
            ys.append(y)
            doms.extend([d] * len(y))
            ids.extend(meta["ids"])
            backend = meta.get("model")
    y_all = np.concatenate(ys)
    X_all = np.concatenate(Xs) if variant == "avg" else ConcatRows(Xs)
    return X_all, y_all, backend, np.array(doms), ids


def metrics_from_preds(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    acc = float((y_true == y_pred).mean())  # 3-class accuracy
    pos = y_true == 0                       # misaligned = positive
    neg = ~pos
    fnr = float((y_pred[pos] != 0).mean()) if pos.any() else None
    fpr = float((y_pred[neg] == 0).mean()) if neg.any() else None
    cm = np.zeros((3, 3), dtype=int)
    for t, p in zip(y_true, y_pred):
        cm[t, p] += 1
    per_class = {}
    for c, cname in ID_TO_LABEL.items():
        tp = int(cm[c, c])
        pred_c = int(cm[:, c].sum())
        true_c = int(cm[c, :].sum())
        prec = tp / pred_c if pred_c else None
        rec = tp / true_c if true_c else None
        f1 = 2 * prec * rec / (prec + rec) if prec and rec and (prec + rec) else 0.0
        per_class[cname] = {"precision": round(prec, 4) if prec is not None else None,
                            "recall": round(rec, 4) if rec is not None else None,
                            "f1": round(f1, 4), "support": true_c}
    return {"acc": round(acc, 4),
            "fpr": round(fpr, 4) if fpr is not None else None,
            "fnr": round(fnr, 4) if fnr is not None else None,
            "confusion": cm.tolist(), "per_class": per_class, "n_test": int(len(y_true))}


def stratified_train_val_indices(y: np.ndarray, val_ratio: float, seed: int) -> tuple[np.ndarray, np.ndarray]:
    """train split 안에서 label 비율을 유지해 validation index를 만든다."""
    rng = np.random.default_rng(seed)
    train_idx, val_idx = [], []
    for c in sorted(set(y.tolist())):
        idx = np.flatnonzero(y == c)
        rng.shuffle(idx)
        n_val = max(1, int(round(len(idx) * val_ratio))) if val_ratio > 0 and len(idx) > 1 else 0
        val_idx.extend(idx[:n_val])
        train_idx.extend(idx[n_val:])
    train_idx = np.asarray(train_idx, dtype=np.int64)
    val_idx = np.asarray(val_idx, dtype=np.int64)
    rng.shuffle(train_idx)
    rng.shuffle(val_idx)
    return train_idx, val_idx


def materialize(X, device, storage_dtype, torch_mod):
    """memmap/ConcatRows를 물리 메모리 텐서로 올린다. 가능하면 GPU, OOM이면 CPU 폴백.

    기존 구현은 배치마다 디스크 memmap에서 무작위 행을 읽어 epoch당 수 GB I/O가
    발생했다 (Enc-first가 극단적으로 느렸던 원인). 한 번만 통째로 올리면
    도메인당 3.8GB(fp16), pooled 30GB로 A100 80GB에 들어간다.
    """
    torch = torch_mod
    n = len(X)
    t = torch.empty((n,) + tuple(X.shape[1:]), dtype=storage_dtype)
    chunk = 256
    for i in range(0, n, chunk):
        t[i:i + chunk] = torch.from_numpy(np.array(X[i:i + chunk], copy=True))
    gb = t.numel() * t.element_size() / 1e9
    if device.startswith("cuda"):
        try:
            t = t.to(device)
            print(f"    data resident on GPU ({gb:.1f} GB)")
            return t, True
        except torch.cuda.OutOfMemoryError:
            torch.cuda.empty_cache()
            print(f"    GPU에 안 들어가서 CPU RAM 상주로 폴백 ({gb:.1f} GB)")
            return t.pin_memory(), False
    print(f"    data resident on CPU ({gb:.1f} GB)")
    return t, False


def train_eval(name: str, Xtr, ytr, Xte, yte, args, backend_model: str | None,
               ids_te: list[str] | None = None, domains_te: np.ndarray | None = None):
    import time

    import torch
    import torch.nn as nn

    device = args.device or ("cuda" if torch.cuda.is_available() else "cpu")
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)

    input_dim = Xtr.shape[-1]
    batch = args.batch_size or (32 if args.variant == "avg" else 16)

    storage_dtype = torch.float32 if args.variant == "avg" else torch.float16
    print(f"  [{name}/{args.variant}] loading features into memory…")
    Xtr_t, tr_on_gpu = materialize(Xtr, device, storage_dtype, torch)
    Xte_t, te_on_gpu = materialize(Xte, device, storage_dtype, torch)

    mu = sd = None
    if args.standardize:
        sample = Xtr_t[: min(len(Xtr_t), 512)].float()
        flat = sample.reshape(-1, input_dim)
        mu = flat.mean(dim=0).to(device)
        sd = flat.std(dim=0).clamp_min(1e-8).to(device)

    def get_batch(T, on_gpu, idx):
        xb = T[idx] if on_gpu else T[idx].to(device, non_blocking=True)
        xb = xb.float()
        if mu is not None:
            xb = (xb - mu) / sd
        return xb

    n = len(ytr)
    use_val = args.detector == "regularized" and args.patience > 0 and args.val_ratio > 0
    if use_val:
        train_idx_np, val_idx_np = stratified_train_val_indices(ytr, args.val_ratio, args.seed)
        print(f"  [{name}/{args.variant}] regularized split: train={len(train_idx_np)} val={len(val_idx_np)}")
    else:
        train_idx_np, val_idx_np = np.arange(n, dtype=np.int64), None

    model = build_model(args.variant, input_dim, args.detector, args.dropout).to(device)
    opt = (torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)
           if args.detector == "regularized" else torch.optim.Adam(model.parameters(), lr=args.lr))
    weight = None
    if args.class_weights:
        counts = np.bincount(ytr[train_idx_np], minlength=3).astype(np.float32)
        weight_np = counts.sum() / (len(counts) * np.maximum(counts, 1.0))
        weight = torch.tensor(weight_np, dtype=torch.float32, device=device)
        print(f"  [{name}/{args.variant}] class weights={np.round(weight_np, 3).tolist()}")
    loss_fn = nn.CrossEntropyLoss(weight=weight)
    ytr_t = torch.tensor(ytr, device=device)
    train_indices = torch.tensor(train_idx_np, device=device if tr_on_gpu else "cpu")
    val_indices = None if val_idx_np is None else torch.tensor(val_idx_np, device=device if tr_on_gpu else "cpu")

    def eval_indices(indices_t):
        model.eval()
        losses, preds = [], []
        with torch.no_grad():
            for b0 in range(0, len(indices_t), 64):
                idx = indices_t[b0:b0 + 64]
                xb = get_batch(Xtr_t, tr_on_gpu, idx)
                yb = ytr_t[idx.to(device)]
                logits = model(xb)
                losses.append(loss_fn(logits, yb).item() * len(idx))
                preds.append(logits.argmax(dim=1).cpu().numpy())
        y_val = ytr[indices_t.cpu().numpy()]
        y_pred_val = np.concatenate(preds)
        return sum(losses) / len(indices_t), float((y_pred_val == y_val).mean())

    best_state, best_val, bad_epochs = None, float("inf"), 0
    t0 = time.time()
    for epoch in range(args.epochs):
        model.train()
        perm = torch.randperm(len(train_indices), device=train_indices.device)
        total = 0.0
        for b0 in range(0, len(train_indices), batch):
            idx = train_indices[perm[b0:b0 + batch]]
            xb = get_batch(Xtr_t, tr_on_gpu, idx)
            yb = ytr_t[idx.to(device)]
            opt.zero_grad()
            loss = loss_fn(model(xb), yb)
            loss.backward()
            opt.step()
            total += loss.item() * len(idx)
        val_msg = ""
        if val_indices is not None:
            val_loss, val_acc = eval_indices(val_indices)
            val_msg = f" val_loss={val_loss:.4f} val_acc={val_acc:.3f}"
            if val_loss < best_val - 1e-5:
                best_val = val_loss
                best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
                bad_epochs = 0
            else:
                bad_epochs += 1
            if bad_epochs >= args.patience:
                print(f"  [{name}/{args.variant}] early stop at epoch {epoch+1} "
                      f"(best_val={best_val:.4f})", flush=True)
                break
        if (epoch + 1) % 20 == 0:
            print(f"  [{name}/{args.variant}] epoch {epoch+1}/{args.epochs} "
                  f"loss={total/len(train_indices):.4f}{val_msg} elapsed={time.time()-t0:.0f}s", flush=True)

    if best_state is not None:
        model.load_state_dict(best_state)

    model.eval()
    preds = []
    with torch.no_grad():
        for b0 in range(0, len(yte), 64):
            idx = torch.arange(b0, min(b0 + 64, len(yte)), device=Xte_t.device)
            xb = get_batch(Xte_t, te_on_gpu, idx)
            preds.append(model(xb).argmax(dim=1).cpu().numpy())
    y_pred = np.concatenate(preds)
    del Xtr_t, Xte_t
    if device.startswith("cuda"):
        torch.cuda.empty_cache()
    m = metrics_from_preds(yte, y_pred)
    m.update({"domain": name, "variant": args.variant, "epochs": args.epochs, "lr": args.lr,
              "batch_size": batch, "input_dim": int(input_dim), "n_train": int(n),
              "n_fit": int(len(train_idx_np)), "backend_model": backend_model,
              "detector": args.detector, "dropout": args.dropout,
              "weight_decay": args.weight_decay if args.detector == "regularized" else 0.0,
              "standardize": bool(args.standardize), "class_weights": bool(args.class_weights),
              "val_ratio": args.val_ratio if use_val else 0.0,
              "patience": args.patience if use_val else 0,
              "best_val_loss": round(best_val, 6) if best_state is not None else None})
    if domains_te is not None:  # pooled/cross: 도메인별 분해 지표
        m["per_domain"] = {d: metrics_from_preds(yte[domains_te == d], y_pred[domains_te == d])
                           for d in sorted(set(domains_te))}
    if ids_te is not None:      # 오분류 샘플 id 기록 (summary에서 원문 대조용)
        err = np.flatnonzero(y_pred != yte)
        m["n_errors"] = int(len(err))
        m["errors"] = [{"id": ids_te[i], "true": ID_TO_LABEL[int(yte[i])],
                        "pred": ID_TO_LABEL[int(y_pred[i])]} for i in err[:500]]
    print(f"[{name}/{args.variant}] Acc={m['acc']:.3f} FPR={m['fpr']:.3f} FNR={m['fnr']:.3f}")

    Path(args.models_dir).mkdir(parents=True, exist_ok=True)
    suffix = f"{args.variant}_{name}" if args.detector == "paper" else f"{args.variant}_{name}_{args.detector}"
    torch.save(model.state_dict(), Path(args.models_dir) / f"{suffix}.pt")
    Path(args.results).mkdir(parents=True, exist_ok=True)
    if name in ("A2B", "B2A"):
        prefix = "ours_cross"
    elif name == "pooled":
        prefix = "ours_pooled"
    else:
        prefix = "ours"
    with open(Path(args.results) / f"{prefix}_{suffix}.json", "w", encoding="utf-8") as f:
        json.dump(m, f, ensure_ascii=False, indent=1)
    return m


def main() -> None:
    args = parse_args()
    feat_dir = Path(args.features)

    if args.cross:
        tr_doms, te_doms = (GROUP_A, GROUP_B) if args.cross == "A2B" else (GROUP_B, GROUP_A)
        missing = [d for d in tr_doms + te_doms if not (feat_dir / f"train_{d}_meta.json").exists()]
        if missing:
            raise SystemExit(f"특징 미추출 도메인: {missing} — extract_features.py 먼저 실행")
        print(f"cross-domain {args.cross}: train={tr_doms} → test={te_doms}")
        Xtr, ytr, backend, _, _ = load_group(feat_dir, tr_doms, args.variant)
        Xte, yte, _, dom_te, ids_te = load_group(feat_dir, te_doms, args.variant)
        train_eval(args.cross, Xtr, ytr, Xte, yte, args, backend, ids_te, dom_te)
        return

    if args.pooled:
        domains = discover_domains(feat_dir)
        print(f"pooled: 전체 {len(domains)}개 도메인 train split 학습 → 전체 test split 평가")
        Xtr, ytr, backend, _, _ = load_group(feat_dir, domains, args.variant, splits=("train",))
        Xte, yte, _, dom_te, ids_te = load_group(feat_dir, domains, args.variant, splits=("test",))
        train_eval("pooled", Xtr, ytr, Xte, yte, args, backend, ids_te, dom_te)
        return

    domains = discover_domains(feat_dir) if args.domains == ["all"] else args.domains
    if not domains:
        raise SystemExit(f"{feat_dir}에 추출된 도메인이 없습니다 — extract_features.py 먼저 실행")
    print(f"domains: {domains}")
    for d in domains:
        Xtr, ytr, _ = load_split(feat_dir, "train", d, args.variant)
        Xte, yte, meta_te = load_split(feat_dir, "test", d, args.variant)
        train_eval(d, Xtr, ytr, Xte, yte, args, meta_te.get("model"),
                   meta_te["ids"], np.array([d] * len(yte)))


if __name__ == "__main__":
    main()
