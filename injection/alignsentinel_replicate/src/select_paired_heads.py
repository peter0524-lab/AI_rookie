"""
Select paired instruction/conflict attention heads from train-only summaries.

Inputs are produced by:
  python src/extract_paired_features.py head-stats ...

The score follows paired_three_class_ipi_methodology.pdf:
  Delta_I = u_AL - u_NI
  Delta_C = u_MIS - u_AL

Scores are standardized within each domain, then penalized for instability
across domains and attack variants. The output JSON is consumed by
extract_paired_features.py pair-features.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import numpy as np


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--stats", required=True, help="directory with *_head_topR.npy and *_meta.json")
    p.add_argument("--out", required=True)
    p.add_argument("--top-r", type=int, default=32)
    p.add_argument("--mi", type=int, default=64, help="number of instruction heads")
    p.add_argument("--mc", type=int, default=64, help="number of conflict heads")
    p.add_argument("--lambda-i", type=float, default=0.5)
    p.add_argument("--lambda-c", type=float, default=0.5)
    p.add_argument("--tau", type=float, default=1.0)
    p.add_argument("--eps", type=float, default=1e-8)
    return p.parse_args()


def softmax_weights(scores: np.ndarray, tau: float) -> np.ndarray:
    if len(scores) == 0:
        return scores.astype(np.float32)
    z = scores.astype(np.float64) / max(tau, 1e-8)
    z = z - z.max()
    w = np.exp(z)
    w = w / np.maximum(w.sum(), 1e-12)
    return w.astype(np.float32)


def top_indices(q: np.ndarray, m: int) -> np.ndarray:
    m = min(m, len(q))
    if m <= 0:
        return np.asarray([], dtype=np.int64)
    return np.argsort(-q)[:m].astype(np.int64)


def layer_head(idx: int, H: int) -> dict:
    return {"index": int(idx), "layer": int(idx // H), "head": int(idx % H)}


def load_train_groups(stats_dir: Path, top_r: int):
    groups: dict[str, dict[str, dict[str, tuple[np.ndarray, str]]]] = defaultdict(lambda: defaultdict(dict))
    L = H = None
    model = None
    for meta_path in sorted(stats_dir.glob("train_*_meta.json")):
        domain = meta_path.name[len("train_"):-len("_meta.json")]
        arr_path = stats_dir / f"train_{domain}_head_top{top_r}.npy"
        if not arr_path.exists():
            raise SystemExit(f"missing head summary: {arr_path}")
        with meta_path.open("r", encoding="utf-8") as f:
            meta = json.load(f)
        arr = np.load(arr_path)
        if L is None:
            L, H, model = int(meta["L"]), int(meta["H"]), meta.get("model")
        if int(meta["L"]) != L or int(meta["H"]) != H:
            raise SystemExit("mixed L/H in stats directory")
        modes = meta["construction_modes"]
        base_ids = meta["base_pair_ids"]
        for i, (bid, mode) in enumerate(zip(base_ids, modes)):
            groups[domain][bid][mode] = (arr[i], meta["ids"][i])
    return groups, L, H, model


def standardized_effect(deltas: list[np.ndarray], eps: float) -> np.ndarray:
    X = np.stack(deltas, axis=0)
    return X.mean(axis=0) / (X.std(axis=0) + eps)


def main() -> None:
    args = parse_args()
    stats_dir = Path(args.stats)
    groups, L, H, model = load_train_groups(stats_dir, args.top_r)
    LH = L * H

    eI_by_domain = []
    eC_by_domain_attack = []
    counts = {"instruction_pairs": 0, "conflict_pairs": 0, "complete_base_pairs": 0}

    for domain, by_base in sorted(groups.items()):
        dI = []
        dC_append = []
        dC_replace = []
        for variants in by_base.values():
            if not {"non_instruction", "aligned", "misaligned_append", "misaligned_replace"} <= set(variants):
                continue
            counts["complete_base_pairs"] += 1
            ni = variants["non_instruction"][0]
            al = variants["aligned"][0]
            ma = variants["misaligned_append"][0]
            mr = variants["misaligned_replace"][0]
            dI.append(al - ni)
            dC_append.append(ma - al)
            dC_replace.append(mr - al)
        if dI:
            eI_by_domain.append(standardized_effect(dI, args.eps))
            counts["instruction_pairs"] += len(dI)
        if dC_append:
            eC_by_domain_attack.append(standardized_effect(dC_append, args.eps))
            eC_by_domain_attack.append(standardized_effect(dC_replace, args.eps))
            counts["conflict_pairs"] += len(dC_append) + len(dC_replace)

    if not eI_by_domain or not eC_by_domain_attack:
        raise SystemExit("not enough complete paired groups to select heads")

    EI = np.stack(eI_by_domain, axis=0)
    EC = np.stack(eC_by_domain_attack, axis=0)
    mean_I = EI.mean(axis=0)
    mean_C = EC.mean(axis=0)
    qI = np.maximum(np.abs(mean_I) - args.lambda_i * EI.std(axis=0), 0.0)
    qC = np.maximum(np.abs(mean_C) - args.lambda_c * EC.std(axis=0), 0.0)
    sign_I = np.sign(mean_I)
    sign_C = np.sign(mean_C)
    sign_I[sign_I == 0] = 1
    sign_C[sign_C == 0] = 1

    idx_I = top_indices(qI, args.mi)
    idx_C = top_indices(qC, args.mc)
    out = {
        "method": "paired_three_class_head_selection",
        "model": model,
        "stats_dir": str(stats_dir),
        "top_r": args.top_r,
        "L": L,
        "H": H,
        "LH": LH,
        "lambda_i": args.lambda_i,
        "lambda_c": args.lambda_c,
        "tau": args.tau,
        "counts": counts,
        "instruction": {
            "indices": idx_I.tolist(),
            "heads": [layer_head(int(i), H) for i in idx_I],
            "scores": qI[idx_I].astype(float).tolist(),
            "signs": sign_I[idx_I].astype(float).tolist(),
            "weights": softmax_weights(qI[idx_I], args.tau).astype(float).tolist(),
        },
        "conflict": {
            "indices": idx_C.tolist(),
            "heads": [layer_head(int(i), H) for i in idx_C],
            "scores": qC[idx_C].astype(float).tolist(),
            "signs": sign_C[idx_C].astype(float).tolist(),
            "weights": softmax_weights(qC[idx_C], args.tau).astype(float).tolist(),
        },
    }

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"[done] selected heads -> {out_path}")
    print(f"  instruction heads={len(idx_I)} conflict heads={len(idx_C)}")
    print(f"  complete train base pairs={counts['complete_base_pairs']}")


if __name__ == "__main__":
    main()
