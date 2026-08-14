#!/usr/bin/env python3
"""Build a KDPII-label version of the synthetic_clean document dataset."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import re
import shutil
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path


TARGET_LABELS = [
    "PS_NAME",
    "LC_ADDRESS",
    "OG_WORKPLACE",
    "OG_DEPARTMENT",
    "CV_POSITION",
    "OGG_EDUCATION",
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
    "QT_AGE",
    "DT_BIRTH",
    "FD_MAJOR",
]


SYNTH_TO_KDPII = {
    "NAME": "PS_NAME",
    "WORKPLACE": "OG_WORKPLACE",
    "DEPARTMENT": "OG_DEPARTMENT",
    "POSITION": "CV_POSITION",
    "EMAIL": "TMI_EMAIL",
    "MOBILE_PHONE": "QT_MOBILE",
    "TELEPHONE": "QT_PHONE",
    "ADDRESS": "LC_ADDRESS",
    "BANK_ACCOUNT_NUMBER": "QT_ACCOUNT_NUMBER",
    "CARD_NUMBER": "QT_CARD_NUMBER",
    "RRN": "QT_RESIDENT_NUMBER",
    "PASSPORT_NUMBER": "QT_PASSPORT_NUMBER",
    "DRIVER_LICENSE_NUMBER": "QT_DRIVER_NUMBER",
    "VEHICLE_NUMBER": "QT_PLATE_NUMBER",
    "DATE_OF_BIRTH": "DT_BIRTH",
    "AGE": "QT_AGE",
    "SCHOOL": "OGG_EDUCATION",
    "MAJOR": "FD_MAJOR",
}
for _label in TARGET_LABELS:
    SYNTH_TO_KDPII.setdefault(_label, _label)


SPLITS = ("train", "valid", "test")
SPLIT_RATIOS = {"train": 0.8, "valid": 0.1, "test": 0.1}

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


def remap_tag(tag: str) -> str:
    if tag == "O":
        return tag
    if "-" not in tag:
        mapped = SYNTH_TO_KDPII.get(tag)
        if not mapped:
            raise ValueError(f"unknown BIO entity label: {tag}")
        return mapped
    prefix, entity = tag.split("-", 1)
    mapped = SYNTH_TO_KDPII.get(entity)
    if not mapped:
        raise ValueError(f"unknown BIO entity label: {entity}")
    return f"{prefix}-{mapped}"


def convert_record(row: dict, source_file: str, source_domain: str, local_idx: int) -> dict:
    out = dict(row)
    out["_source_dataset"] = "synthetic_clean"
    out["_source_domain"] = source_domain
    out["_source_file"] = source_file
    out["sent_idx"] = f"{Path(source_file).stem}:{row.get('sent_idx', local_idx)}"

    converted_pii = []
    for ent in row.get("PII_set", []):
        copied = dict(ent)
        old = copied.get("label")
        new = SYNTH_TO_KDPII.get(old)
        if not new:
            raise ValueError(f"{source_file}: unknown PII label {old!r}")
        copied["label"] = new
        converted_pii.append(copied)
    out["PII_set"] = converted_pii

    if "labelling_seq" in row:
        out["labelling_seq"] = [remap_tag(tag) for tag in row["labelling_seq"]]
    return out


def validate_record(row: dict, source_file: str, target_set: set[str]) -> None:
    sent_seq = row.get("sent_seq")
    labelling_seq = row.get("labelling_seq")
    if sent_seq is not None and labelling_seq is not None and len(sent_seq) != len(labelling_seq):
        raise ValueError(f"{source_file}: sent_seq/labelling_seq length mismatch")
    sentence = row.get("sentence")
    if isinstance(sentence, str) and sent_seq is not None and len(sentence) != len(sent_seq):
        raise ValueError(f"{source_file}: sentence/sent_seq length mismatch")
    for ent in row.get("PII_set", []):
        label = ent.get("label")
        if label not in target_set:
            raise ValueError(f"{source_file}: non-KDPII label after conversion {label!r}")
        begin = ent.get("begin")
        end = ent.get("end")
        form = ent.get("form")
        if isinstance(sentence, str) and isinstance(begin, int) and isinstance(end, int):
            if sentence[begin:end] != form:
                raise ValueError(f"{source_file}: span mismatch for {form!r} at {begin}:{end}")


def write_json(path: Path, data: list[dict], *, indent: int | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=indent)


def normalize_date(value: str) -> str:
    value = value.strip()
    groups = re.findall(r"\d+", value)
    if len(groups) >= 3:
        year, month, day = groups[:3]
        if len(year) == 4:
            return f"{year}{int(month):02d}{int(day):02d}"
        if len(year) == 2:
            return f"{year}{int(month):02d}{int(day):02d}"
    digits = re.sub(r"\D", "", value)
    return digits or value


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
        row_names = set()
        row_births = set()
        for ent in row.get("PII_set", []):
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
                row_names.add(normalized)
            elif label == "DT_BIRTH":
                row_births.add(normalized)

        # Names alone are too collision-prone, but name+birth in the same row is
        # a useful fallback when no stronger identifier appears.
        for name in row_names:
            for birth in row_births:
                keys.add(("PS_NAME+DT_BIRTH", name, birth))

    return keys


def build_identity_components(docs: list[dict]) -> tuple[dict[int, list[int]], dict[str, int]]:
    uf = UnionFind(len(docs))
    first_doc_by_key: dict[tuple[str, ...], int] = {}
    repeated_keys = 0

    for doc_idx, doc in enumerate(docs):
        for key in doc["identity_keys"]:
            owner = first_doc_by_key.get(key)
            if owner is None:
                first_doc_by_key[key] = doc_idx
            else:
                repeated_keys += 1
                uf.union(owner, doc_idx)

    components: dict[int, list[int]] = defaultdict(list)
    for doc_idx in range(len(docs)):
        components[uf.find(doc_idx)].append(doc_idx)

    stats = {
        "identity_keys": len(first_doc_by_key),
        "repeated_identity_key_links": repeated_keys,
        "components": len(components),
        "multi_document_components": sum(1 for members in components.values() if len(members) > 1),
        "documents_in_multi_document_components": sum(
            len(members) for members in components.values() if len(members) > 1
        ),
        "documents_without_identity_keys": sum(1 for doc in docs if not doc["identity_keys"]),
    }
    return components, stats


def split_targets(total_docs: int) -> dict[str, int]:
    train = round(total_docs * SPLIT_RATIOS["train"])
    valid = round(total_docs * SPLIT_RATIOS["valid"])
    return {
        "train": train,
        "valid": valid,
        "test": total_docs - train - valid,
    }


def component_id(files: list[str]) -> str:
    joined = "\n".join(sorted(files))
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()[:16]


def assign_components(
    docs: list[dict],
    components: dict[int, list[int]],
    seed: int,
) -> tuple[dict[str, list[int]], dict[str, list[str]], dict]:
    targets = split_targets(len(docs))
    rng = random.Random(seed)
    ordered_components = list(components.values())
    rng.shuffle(ordered_components)
    ordered_components.sort(key=len, reverse=True)

    assigned_indices: dict[str, list[int]] = {split: [] for split in SPLITS}
    assigned_components: dict[str, list[str]] = {split: [] for split in SPLITS}
    counts = {split: 0 for split in SPLITS}

    for members in ordered_components:
        member_domains = Counter(docs[idx]["domain"] for idx in members)

        def score(split: str) -> tuple[int, int, int]:
            total_deficit = targets[split] - counts[split]
            domain_deficit = 0
            current_domains = Counter(docs[idx]["domain"] for idx in assigned_indices[split])
            for domain, n_docs in member_domains.items():
                domain_target = round(
                    sum(1 for doc in docs if doc["domain"] == domain) * SPLIT_RATIOS[split]
                )
                domain_deficit += domain_target - current_domains[domain]
                domain_deficit -= n_docs
            return (total_deficit, domain_deficit, -counts[split])

        split = max(SPLITS, key=score)
        assigned_indices[split].extend(members)
        assigned_components[split].append(component_id([docs[idx]["rel"] for idx in members]))
        counts[split] += len(members)

    assignment_stats = {
        "ratios": SPLIT_RATIOS,
        "target_documents": targets,
        "actual_documents": counts,
    }
    return assigned_indices, assigned_components, assignment_stats


def verify_no_leakage(docs: list[dict], assigned_indices: dict[str, list[int]]) -> dict:
    doc_to_split = {}
    key_to_split: dict[tuple[str, ...], str] = {}
    document_leaks = []
    identity_leaks = []

    for split, indices in assigned_indices.items():
        for idx in indices:
            rel = docs[idx]["rel"]
            previous = doc_to_split.get(rel)
            if previous and previous != split:
                document_leaks.append((rel, previous, split))
            doc_to_split[rel] = split

            for key in docs[idx]["identity_keys"]:
                previous_split = key_to_split.get(key)
                if previous_split and previous_split != split:
                    identity_leaks.append((previous_split, split))
                key_to_split[key] = split

    return {
        "document_leak_count": len(document_leaks),
        "identity_key_leak_count": len(identity_leaks),
        "checked_identity_keys": len(key_to_split),
        "ok": not document_leaks and not identity_leaks,
    }


def build_dataset(source_dir: Path, output_dir: Path, seed: int, force: bool) -> None:
    target_set = set(TARGET_LABELS)
    json_files = sorted(source_dir.glob("*_clean_*/json/*.json"))
    if not json_files:
        raise SystemExit(f"no json files found under {source_dir}")

    if output_dir.exists():
        if not force:
            raise SystemExit(f"destination already exists: {output_dir}")
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup = output_dir.with_name(f"{output_dir.name}.backup.{stamp}")
        output_dir.rename(backup)
        print(f"[backup] moved existing output to {backup}")

    tmp_dir = output_dir.with_name(f"{output_dir.name}.tmp.{os.getpid()}")
    tmp_dir.mkdir(parents=True)

    docs: list[dict] = []
    raw_counts: Counter[str] = Counter()
    mapped_counts: Counter[str] = Counter()
    row_count = 0

    try:
        for path in json_files:
            rel = path.relative_to(source_dir)
            domain = rel.parts[0]
            with path.open(encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, list):
                raise ValueError(f"{path}: expected JSON list")

            converted = []
            for idx, row in enumerate(data):
                for ent in row.get("PII_set", []):
                    raw_counts[ent.get("label")] += 1
                out = convert_record(row, str(rel), domain, idx)
                validate_record(out, str(rel), target_set)
                for ent in out.get("PII_set", []):
                    mapped_counts[ent.get("label")] += 1
                converted.append(out)

            row_count += len(converted)
            write_json(tmp_dir / "by_document" / rel, converted)
            docs.append(
                {
                    "path": path,
                    "rel": str(rel),
                    "domain": domain,
                    "records": converted,
                    "rows": len(converted),
                    "identity_keys": identity_keys_for_records(converted),
                }
            )

        components, component_stats = build_identity_components(docs)
        assigned_indices, assigned_components, assignment_stats = assign_components(
            docs, components, seed
        )
        leakage_report = verify_no_leakage(docs, assigned_indices)
        if not leakage_report["ok"]:
            raise ValueError(f"split leakage detected: {leakage_report}")

        splits: dict[str, list[dict]] = {}
        split_docs_out: dict[str, list[str]] = {}
        for split in SPLITS:
            indices = sorted(assigned_indices[split], key=lambda idx: docs[idx]["rel"])
            split_docs_out[split] = [docs[idx]["rel"] for idx in indices]
            splits[split] = [
                record
                for idx in indices
                for record in docs[idx]["records"]
            ]
            write_json(tmp_dir / f"{split}.json", splits[split])

        component_summaries = []
        for members in sorted(components.values(), key=len, reverse=True)[:20]:
            files = [docs[idx]["rel"] for idx in members]
            component_summaries.append(
                {
                    "component_id": component_id(files),
                    "documents": len(files),
                    "domains": dict(sorted(Counter(docs[idx]["domain"] for idx in members).items())),
                    "files_sample": sorted(files)[:20],
                }
            )

        manifest = {
            "source_dir": str(source_dir),
            "output_dir": str(output_dir),
            "seed": seed,
            "split_strategy": (
                "document-level, identity-component grouped 80/10/10. "
                "Components are connected by shared normalized strong PII "
                "values or row-local PS_NAME+DT_BIRTH pairs; names alone are "
                "not used as identity keys."
            ),
            "identity_key_policy": {
                "strong_labels": sorted(STRONG_IDENTITY_LABELS),
                "pair_keys": ["row-local PS_NAME+DT_BIRTH"],
                "normalization": {
                    "TMI_EMAIL": "lowercase",
                    "QT_* identifiers": "remove punctuation/space and uppercase",
                    "DT_BIRTH": "normalize common numeric date forms",
                    "PS_NAME": "remove whitespace, only used in pair keys",
                    "LC_ADDRESS": "collapse whitespace",
                },
            },
            "component_stats": component_stats,
            "assignment_stats": assignment_stats,
            "leakage_check": leakage_report,
            "largest_components": component_summaries,
            "label_mapping": SYNTH_TO_KDPII,
            "target_labels": TARGET_LABELS,
            "source_json_files": len(json_files),
            "source_rows": row_count,
            "raw_label_counts": dict(sorted(raw_counts.items())),
            "mapped_label_counts": {label: mapped_counts.get(label, 0) for label in TARGET_LABELS},
            "missing_target_labels": [label for label in TARGET_LABELS if mapped_counts.get(label, 0) == 0],
            "splits": {},
        }
        for split in SPLITS:
            indices = assigned_indices[split]
            manifest["splits"][split] = {
                "documents": len(split_docs_out[split]),
                "rows": len(splits[split]),
                "components": len(assigned_components[split]),
                "domains": dict(sorted(Counter(docs[idx]["domain"] for idx in indices).items())),
                "files": split_docs_out[split],
            }
        write_json(tmp_dir / "split_manifest.json", manifest, indent=2)

        tmp_dir.rename(output_dir)
        print(f"created {output_dir}")
        print(f"source_json_files={len(json_files)} source_rows={row_count}")
        print(
            "identity_components="
            f"{component_stats['components']} "
            f"multi_doc={component_stats['multi_document_components']} "
            f"docs_without_keys={component_stats['documents_without_identity_keys']}"
        )
        for split in SPLITS:
            print(
                f"{split}: documents={len(split_docs_out[split])} "
                f"rows={len(splits[split])}"
            )
        missing = ",".join(manifest["missing_target_labels"]) or "none"
        print(f"missing_target_labels={missing}")
        print("mapped_label_counts")
        for label in TARGET_LABELS:
            print(f"{label}\t{mapped_counts.get(label, 0)}")
    except Exception:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", default="/data/team/hwan/data/synthetic_clean")
    parser.add_argument("--output-dir", default="/data/team/hwan/data/synthetic_clean_kdpii")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    build_dataset(Path(args.source_dir), Path(args.output_dir), args.seed, args.force)


if __name__ == "__main__":
    main()
