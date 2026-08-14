#!/usr/bin/env python3
"""Fail-fast checks before launching the long real experiment run."""

from __future__ import annotations

import argparse
import importlib
import os
import shutil
import subprocess
import sys
from pathlib import Path


MIN_GPU_FREE_GB = 60
MIN_DISK_FREE_GB = 120


def ok(message: str) -> None:
    print(f"[OK] {message}")


def warn(message: str) -> None:
    print(f"[WARN] {message}")


def fail(message: str) -> None:
    print(f"[FAIL] {message}")
    raise SystemExit(1)


def require_path(path: Path, kind: str = "path") -> None:
    if not path.exists():
        fail(f"missing {kind}: {path}")
    ok(f"{kind}: {path}")


def require_import(name: str) -> None:
    try:
        module = importlib.import_module(name)
    except Exception as exc:
        fail(f"cannot import {name}: {exc!r}")
    version = getattr(module, "__version__", "")
    ok(f"import {name} {version}".rstrip())


def check_gpu() -> None:
    require_import("torch")
    import torch

    if not torch.cuda.is_available():
        fail("CUDA is not available to torch")
    if torch.cuda.device_count() < 1:
        fail("no CUDA devices visible")

    free_bytes, total_bytes = torch.cuda.mem_get_info(0)
    free_gb = free_bytes / 1024**3
    total_gb = total_bytes / 1024**3
    name = torch.cuda.get_device_name(0)
    if free_gb < MIN_GPU_FREE_GB:
        fail(f"GPU memory too occupied: {free_gb:.1f}GB free / {total_gb:.1f}GB total on {name}")
    ok(f"GPU {name}: {free_gb:.1f}GB free / {total_gb:.1f}GB total")


def check_disk(path: Path) -> None:
    usage = shutil.disk_usage(path)
    free_gb = usage.free / 1024**3
    if free_gb < MIN_DISK_FREE_GB:
        fail(f"not enough disk on {path}: {free_gb:.1f}GB free, need >= {MIN_DISK_FREE_GB}GB")
    ok(f"disk {path}: {free_gb:.1f}GB free")


def check_no_conflicting_processes() -> None:
    proc = subprocess.run(
        ["ps", "-eo", "pid,user,args"],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    )
    needles = [
        "run_real_experiments.py",
        "train_baseline.py",
        "distill_train_crf_gaz.py",
        "open_ai_privacy_filter_lora_train.py",
    ]
    current_pid = str(os.getpid())
    conflicts = []
    for line in proc.stdout.splitlines():
        parts = line.strip().split(None, 2)
        if len(parts) < 3:
            continue
        pid, _user, args = parts
        if pid == current_pid:
            continue
        if any(needle in args for needle in needles) and "preflight_real.py" not in args:
            conflicts.append(line.strip())
    if conflicts:
        fail("conflicting experiment/training process already running:\n" + "\n".join(conflicts[:20]))
    ok("no conflicting experiment/training process")


def check_spacy() -> None:
    require_import("spacy")
    require_import("presidio_analyzer")
    import spacy

    try:
        nlp = spacy.load("ko_core_news_lg")
    except Exception as exc:
        fail(f"cannot load spaCy model ko_core_news_lg: {exc!r}")
    ok(f"spaCy model ko_core_news_lg: {','.join(nlp.pipe_names)}")


def check_local_imports(code_root: Path) -> None:
    sys.path.insert(0, str(code_root))
    for name in [
        "train_baseline",
        "distill_train_crf_gaz",
        "eval_baseline_ensemble_vote",
        "open_ai_privacy_filter_lora_train",
        "eval_presidio_ko_spacy_regex",
    ]:
        require_import(name)


def check_failed_markers(root: Path) -> None:
    failed = sorted((root / "status").glob("*.failed"))
    if failed:
        warn("existing failed markers found; rerun can still proceed, but inspect if unexpected:")
        for path in failed[:20]:
            print(f"       {path}")
    else:
        ok("no failed markers")


def run(args: argparse.Namespace) -> None:
    root = Path(args.root)
    code_root = Path(args.code_root)
    kdpii_dir = Path(args.kdpii_dir)
    synthetic_dir = Path(args.synthetic_dir)
    privacy_base_model = Path(args.privacy_base_model)

    require_path(code_root, "code_root")
    require_path(root / "scripts" / "run_all.sh", "runner")
    require_path(root / "scripts" / "run_real_experiments.py", "runner")
    require_path(kdpii_dir / "train.json", "kdpii train")
    require_path(kdpii_dir / "valid.json", "kdpii valid")
    require_path(kdpii_dir / "test.json", "kdpii test")
    require_path(synthetic_dir / "train.json", "synthetic train")
    require_path(synthetic_dir / "valid.json", "synthetic valid")
    require_path(synthetic_dir / "test.json", "synthetic test")
    require_path(synthetic_dir / "split_manifest.json", "synthetic manifest")

    for path in [
        code_root / "models" / "skt_encoder_crf_gaz_kdpii_hard" / "seed42" / "config.json",
        code_root / "models" / "skt_encoder_crf_gaz_kdpii_hard" / "seed43" / "config.json",
        code_root / "models" / "skt_encoder_crf_gaz_kdpii_hard" / "seed44" / "config.json",
        code_root / "models" / "klue_roberta_large" / "seed42" / "config.json",
        code_root / "models" / "xlm_roberta_large" / "seed42" / "config.json",
        code_root / "models" / "privacy_filter_korean_Lora" / "seed42" / "inference" / "config.json",
        privacy_base_model / "config.json",
    ]:
        require_path(path, "model config")

    for name in ["transformers", "peft", "numpy"]:
        require_import(name)
    check_spacy()
    check_local_imports(code_root)
    check_gpu()
    check_disk(root)
    check_no_conflicting_processes()
    check_failed_markers(root)
    ok("preflight complete")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="/data/team/hwan/real")
    parser.add_argument("--code-root", default="/data/team/hwan")
    parser.add_argument("--kdpii-dir", default="/data/team/hwan/data/kpii")
    parser.add_argument("--synthetic-dir", default="/data/team/hwan/data/synthetic_clean_kdpii")
    parser.add_argument("--privacy-base-model", default="/data/team/hwan/models/privacy_filter_korean")
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
