#!/usr/bin/env python3
"""Build mixed KDPII + synthetic JSON splits.

Default is natural concat:
  train = KDPII train + synthetic train
  valid = KDPII valid + synthetic valid

The script only writes train/valid plus a small manifest. Test sets remain
separate and should be evaluated via their original data dirs.
"""

from __future__ import annotations

import argparse
import json
import random
from copy import deepcopy
from pathlib import Path


def load_json(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise TypeError(f"{path} must contain a JSON list")
    return data


def stamp(records: list[dict], source: str) -> list[dict]:
    out = []
    for idx, item in enumerate(records):
        copied = deepcopy(item)
        copied["_source_dataset"] = source
        if "sent_idx" in copied:
            copied["sent_idx"] = f"{source}:{copied['sent_idx']}"
        else:
            copied["sent_idx"] = f"{source}:{idx}"
        out.append(copied)
    return out


def write_json(path: Path, data: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)


def build_split(kdpii_dir: Path, synth_dir: Path, split: str, seed: int, shuffle: bool) -> tuple[list[dict], dict]:
    kd = stamp(load_json(kdpii_dir / f"{split}.json"), "kdpii")
    sy = stamp(load_json(synth_dir / f"{split}.json"), "synthetic")
    mixed = kd + sy
    if shuffle:
        rng = random.Random(seed)
        rng.shuffle(mixed)
    return mixed, {
        "split": split,
        "kdpii_count": len(kd),
        "synthetic_count": len(sy),
        "total_count": len(mixed),
        "synthetic_ratio": len(sy) / len(mixed) if mixed else 0.0,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--kdpii-dir", default="data")
    ap.add_argument("--synthetic-dir", default="synthetic")
    ap.add_argument("--out-dir", default="mixed/natural_86_14")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--no-shuffle", action="store_true")
    args = ap.parse_args()

    kdpii_dir = Path(args.kdpii_dir)
    synth_dir = Path(args.synthetic_dir)
    out_dir = Path(args.out_dir)
    shuffle = not args.no_shuffle

    manifest = {
        "type": "natural_concat",
        "kdpii_dir": str(kdpii_dir),
        "synthetic_dir": str(synth_dir),
        "out_dir": str(out_dir),
        "seed": args.seed,
        "shuffle": shuffle,
        "splits": {},
    }
    for split in ["train", "valid"]:
        data, info = build_split(kdpii_dir, synth_dir, split, args.seed, shuffle)
        write_json(out_dir / f"{split}.json", data)
        manifest["splits"][split] = info

    with (out_dir / "manifest.json").open("w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    train = manifest["splits"]["train"]
    valid = manifest["splits"]["valid"]
    print(f"[mixed] wrote {out_dir}")
    print(
        "  train: "
        f"kdpii={train['kdpii_count']} synthetic={train['synthetic_count']} "
        f"total={train['total_count']} synthetic_ratio={train['synthetic_ratio']:.4f}"
    )
    print(
        "  valid: "
        f"kdpii={valid['kdpii_count']} synthetic={valid['synthetic_count']} "
        f"total={valid['total_count']} synthetic_ratio={valid['synthetic_ratio']:.4f}"
    )


if __name__ == "__main__":
    main()
