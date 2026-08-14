#!/usr/bin/env python3
"""Prepare data folders for the real KDPII/synthetic experiment grid."""

from __future__ import annotations

import argparse
import json
import random
import re
import shutil
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


SPLITS = ("train", "valid")
TEST_SETS = ("kdpii", "synthetic", "combined")
DEFAULT_RATIOS = ("0.25", "0.5", "1.0", "2.0", "all")

STRONG_IDENTITY_LABELS = {
    "LC_ADDRESS",
    "QT_MOBILE",
    "QT_PHONE",
    "QT_RESIDENT_NUMBER",
    "QT_ALIEN_NUMBER",
    "QT_DRIVER_NUMBER",
    "QT_PLATE_NUMBER",
    "QT_ACCOUNT_NUMBER",
    "QT_CARD_NUMBER",
    "TMI_EMAIL",
    "QT_PASSPORT_NUMBER",
}

ALNUM_IDENTITY_LABELS = {
    "QT_MOBILE",
    "QT_PHONE",
    "QT_RESIDENT_NUMBER",
    "QT_ALIEN_NUMBER",
    "QT_DRIVER_NUMBER",
    "QT_PLATE_NUMBER",
    "QT_ACCOUNT_NUMBER",
    "QT_CARD_NUMBER",
    "QT_PASSPORT_NUMBER",
}


class UnionFind:
    def __init__(self, n_items: int) -> None:
        self.parent = list(range(n_items))
        self.size = [1] * n_items

    def find(self, item: int) -> int:
        while self.parent[item] != item:
            self.parent[item] = self.parent[self.parent[item]]
            item = self.parent[item]
        return item

    def union(self, left: int, right: int) -> None:
        root_left = self.find(left)
        root_right = self.find(right)
        if root_left == root_right:
            return
        if self.size[root_left] < self.size[root_right]:
            root_left, root_right = root_right, root_left
        self.parent[root_right] = root_left
        self.size[root_left] += self.size[root_right]


def read_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data: Any, *, indent: int | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=indent)


def copy_json(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def reset_dir(path: Path, force: bool) -> None:
    if path.exists() and force:
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def normalize_date(value: str) -> str:
    groups = re.findall(r"\d+", value.strip())
    if len(groups) >= 3:
        year, month, day = groups[:3]
        if len(year) in (2, 4):
            return f"{year}{int(month):02d}{int(day):02d}"
    digits = re.sub(r"\D", "", value)
    return digits or value.strip()


def normalize_identity_form(label: str, form: object) -> str:
    value = re.sub(r"\s+", " ", str(form).strip())
    if not value:
        return ""
    if label == "TMI_EMAIL":
        return value.lower()
    if label in ALNUM_IDENTITY_LABELS:
        return re.sub(r"[^0-9A-Za-z가-힣]", "", value).upper()
    if label == "DT_BIRTH":
        return normalize_date(value)
    if label == "PS_NAME":
        return re.sub(r"\s+", "", value)
    return value


def identity_keys_for_records(records: list[dict]) -> set[tuple[str, ...]]:
    keys: set[tuple[str, ...]] = set()
    for row in records:
        names = set()
        births = set()
        for ent in row.get("PII_set", []) or []:
            label = ent.get("label")
            form = ent.get("form")
            if not label or form is None:
                continue
            normalized = normalize_identity_form(label, form)
            if not normalized:
                continue
            if label in STRONG_IDENTITY_LABELS:
                keys.add((label, normalized))
            elif label == "PS_NAME":
                names.add(normalized)
            elif label == "DT_BIRTH":
                births.add(normalized)
        for name in names:
            for birth in births:
                keys.add(("PS_NAME+DT_BIRTH", name, birth))
    return keys


def build_components(docs: list[dict]) -> list[list[int]]:
    uf = UnionFind(len(docs))
    first_doc_by_key: dict[tuple[str, ...], int] = {}
    for doc_idx, doc in enumerate(docs):
        for key in doc["identity_keys"]:
            owner = first_doc_by_key.get(key)
            if owner is None:
                first_doc_by_key[key] = doc_idx
            else:
                uf.union(owner, doc_idx)

    components: dict[int, list[int]] = defaultdict(list)
    for idx in range(len(docs)):
        components[uf.find(idx)].append(idx)
    return list(components.values())


def load_synthetic_docs(synthetic_dir: Path, split: str) -> list[dict]:
    manifest = read_json(synthetic_dir / "split_manifest.json")
    files = manifest["splits"][split]["files"]
    docs = []
    for rel in files:
        path = synthetic_dir / "by_document" / rel
        records = read_json(path)
        docs.append(
            {
                "rel": rel,
                "domain": rel.split("/", 1)[0],
                "records": records,
                "rows": len(records),
                "identity_keys": identity_keys_for_records(records),
            }
        )
    return docs


def ordered_components(docs: list[dict], seed: int, split: str) -> list[list[int]]:
    components = build_components(docs)
    rng = random.Random(f"{seed}:{split}:synthetic-components")
    rng.shuffle(components)
    return components


def select_synthetic_docs(
    docs: list[dict],
    components: list[list[int]],
    ratio: str,
    target_base_rows: int,
) -> tuple[list[dict], dict]:
    if ratio == "all":
        selected_indices = [idx for comp in components for idx in comp]
        target_rows = sum(doc["rows"] for doc in docs)
    else:
        target_rows = int(round(target_base_rows * float(ratio)))
        selected_indices = []
        running_rows = 0
        for comp in components:
            comp_rows = sum(docs[idx]["rows"] for idx in comp)
            if running_rows >= target_rows:
                break
            selected_indices.extend(comp)
            running_rows += comp_rows

    selected_indices = sorted(set(selected_indices), key=lambda idx: docs[idx]["rel"])
    selected_docs = [docs[idx] for idx in selected_indices]
    actual_rows = sum(doc["rows"] for doc in selected_docs)
    return selected_docs, {
        "ratio": ratio,
        "target_synthetic_rows": target_rows,
        "actual_synthetic_rows": actual_rows,
        "synthetic_documents": len(selected_docs),
        "synthetic_domains": dict(Counter(doc["domain"] for doc in selected_docs)),
        "synthetic_files": [doc["rel"] for doc in selected_docs],
    }


def flatten_docs(docs: list[dict]) -> list[dict]:
    return [row for doc in docs for row in doc["records"]]


def load_rows(path: Path) -> list[dict]:
    rows = read_json(path)
    if not isinstance(rows, list):
        raise ValueError(f"expected list in {path}")
    return rows


def ratio_name(ratio: str) -> str:
    if ratio == "all":
        return "mix_syn_all"
    value = float(ratio)
    return f"mix_syn{int(round(value * 100)):03d}"


def create_symlink(target: Path, link: Path) -> None:
    link.parent.mkdir(parents=True, exist_ok=True)
    if link.is_symlink() or link.exists():
        if link.is_symlink() and Path(link.readlink()) == target:
            return
        if link.is_dir() and not link.is_symlink():
            return
        link.unlink()
    link.symlink_to(target)


def prepare(args: argparse.Namespace) -> None:
    root = Path(args.root)
    kdpii_dir = Path(args.kdpii_dir)
    synthetic_dir = Path(args.synthetic_dir)
    data_root = root / "data"
    train_root = data_root / "train_sets"
    test_root = data_root / "test_sets"
    manifest_root = root / "manifests"

    for required in [
        kdpii_dir / "train.json",
        kdpii_dir / "valid.json",
        kdpii_dir / "test.json",
        synthetic_dir / "train.json",
        synthetic_dir / "valid.json",
        synthetic_dir / "test.json",
        synthetic_dir / "split_manifest.json",
    ]:
        if not required.exists():
            raise FileNotFoundError(required)

    root.mkdir(parents=True, exist_ok=True)
    reset_dir(train_root, args.force)
    reset_dir(test_root, args.force)
    manifest_root.mkdir(parents=True, exist_ok=True)

    create_symlink(kdpii_dir, data_root / "kdpii")
    create_symlink(synthetic_dir, data_root / "synthetic")

    kdpii_train = load_rows(kdpii_dir / "train.json")
    kdpii_valid = load_rows(kdpii_dir / "valid.json")
    kdpii_test = load_rows(kdpii_dir / "test.json")
    synthetic_test = load_rows(synthetic_dir / "test.json")

    copy_json(kdpii_dir / "test.json", test_root / "kdpii" / "test.json")
    copy_json(synthetic_dir / "test.json", test_root / "synthetic" / "test.json")
    write_json(test_root / "combined" / "test.json", kdpii_test + synthetic_test)

    copy_json(kdpii_dir / "train.json", train_root / "kdpii_full" / "train.json")
    copy_json(kdpii_dir / "valid.json", train_root / "kdpii_full" / "valid.json")
    copy_json(synthetic_dir / "train.json", train_root / "synthetic_only" / "train.json")
    copy_json(synthetic_dir / "valid.json", train_root / "synthetic_only" / "valid.json")

    synth_docs_by_split = {
        split: load_synthetic_docs(synthetic_dir, split)
        for split in SPLITS
    }
    component_order = {
        split: ordered_components(synth_docs_by_split[split], args.seed, split)
        for split in SPLITS
    }

    train_set_manifest = {
        "root": str(root),
        "kdpii_dir": str(kdpii_dir),
        "synthetic_dir": str(synthetic_dir),
        "seed": args.seed,
        "ratio_definition": (
            "synthetic row target = ratio * KDPII rows for the same split; "
            "synthetic docs are selected by identity components, never by row."
        ),
        "train_sets": {
            "kdpii_full": {
                "train_rows": len(kdpii_train),
                "valid_rows": len(kdpii_valid),
                "synthetic_ratio": "0",
            },
            "synthetic_only": {
                "train_rows": len(load_rows(synthetic_dir / "train.json")),
                "valid_rows": len(load_rows(synthetic_dir / "valid.json")),
                "synthetic_ratio": "only",
            },
        },
        "test_sets": {
            "kdpii": {"rows": len(kdpii_test)},
            "synthetic": {"rows": len(synthetic_test)},
            "combined": {"rows": len(kdpii_test) + len(synthetic_test)},
        },
    }

    ratios = [item.strip() for item in args.ratios.split(",") if item.strip()]
    for ratio in ratios:
        name = ratio_name(ratio)
        out_dir = train_root / name
        selected_train_docs, train_info = select_synthetic_docs(
            synth_docs_by_split["train"],
            component_order["train"],
            ratio,
            len(kdpii_train),
        )
        selected_valid_docs, valid_info = select_synthetic_docs(
            synth_docs_by_split["valid"],
            component_order["valid"],
            ratio,
            len(kdpii_valid),
        )
        train_rows = kdpii_train + flatten_docs(selected_train_docs)
        valid_rows = kdpii_valid + flatten_docs(selected_valid_docs)
        write_json(out_dir / "train.json", train_rows)
        write_json(out_dir / "valid.json", valid_rows)
        train_set_manifest["train_sets"][name] = {
            "synthetic_ratio": ratio,
            "train_rows": len(train_rows),
            "valid_rows": len(valid_rows),
            "train_synthetic": train_info,
            "valid_synthetic": valid_info,
        }

    write_json(manifest_root / "real_data_manifest.json", train_set_manifest, indent=2)
    print(f"[prepare] root={root}")
    print(f"[prepare] train_sets={', '.join(train_set_manifest['train_sets'])}")
    print(f"[prepare] test_sets={', '.join(TEST_SETS)}")
    print(f"[prepare] manifest={manifest_root / 'real_data_manifest.json'}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="/data/team/hwan/real")
    parser.add_argument("--kdpii-dir", default="/data/team/hwan/data/kpii")
    parser.add_argument("--synthetic-dir", default="/data/team/hwan/data/synthetic_clean_kdpii")
    parser.add_argument("--ratios", default=",".join(DEFAULT_RATIOS))
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    prepare(parse_args())
