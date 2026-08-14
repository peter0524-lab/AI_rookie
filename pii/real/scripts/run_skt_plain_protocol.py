#!/usr/bin/env python3
import importlib.util
import json
import os
import shlex
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path("/data/team/hwan/real")
CODE_ROOT = Path("/data/team/hwan")
SCRIPT_DIR = ROOT / "scripts"
LOG_DIR = ROOT / "logs"
JOB_LOG_DIR = LOG_DIR / "jobs"
MODEL_KEY = "skt_encoder_baseline"
MODEL_DISPLAY = "SKT A.X Encoder"
MODEL_ID = "skt/A.X-Encoder-base"
SEED = 42
COMMON18_EXCLUDE = "QT_ALIEN_NUMBER"

TRAIN_SPECS = [
    ("kdpii_full", "KDPII only", "0"),
    ("synthetic_only", "Synthetic only", "only"),
    ("mix_syn_all", "Mix-all", "all"),
]
TEST_SETS = ["kdpii", "synthetic", "combined"]
LABEL_SCOPES = ["full19", "common18"]

LOG_DIR.mkdir(parents=True, exist_ok=True)
JOB_LOG_DIR.mkdir(parents=True, exist_ok=True)

runner_path = SCRIPT_DIR / "run_real_experiments.py"
spec = importlib.util.spec_from_file_location("real_runner", runner_path)
runner = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = runner
spec.loader.exec_module(runner)

def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def log(msg):
    print(f"[{now()}] {msg}", flush=True)

def run_to_log(cmd, env, log_path):
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(f"\n[{now()}] $ {shlex.join(cmd)}\n")
        f.flush()
        proc = subprocess.run(cmd, cwd=str(CODE_ROOT), env=env, stdout=f, stderr=subprocess.STDOUT, text=True)
        f.write(f"\n[{now()}] exit_code={proc.returncode}\n")
        f.flush()
    return proc.returncode

def disk_guard():
    total, used, free = shutil.disk_usage(ROOT)
    free_gb = free / (1024 ** 3)
    min_free_gb = float(os.environ.get("SKT_PLAIN_MIN_FREE_GB", "10"))
    log(f"[disk] free={free_gb:.1f}GB min_required={min_free_gb:.1f}GB")
    if free_gb < min_free_gb:
        raise SystemExit(f"not enough disk space: {free_gb:.1f}GB < {min_free_gb:.1f}GB")

def query_gpus():
    try:
        out = subprocess.check_output([
            "nvidia-smi",
            "--query-gpu=index,memory.used,memory.total",
            "--format=csv,noheader,nounits",
        ], text=True, stderr=subprocess.STDOUT)
    except Exception as exc:
        log(f"[gpu] nvidia-smi unavailable ({exc}); continuing without CUDA_VISIBLE_DEVICES pinning")
        return []
    gpus = []
    for line in out.strip().splitlines():
        parts = [p.strip() for p in line.split(",")]
        if len(parts) >= 3:
            idx, used, total = int(parts[0]), int(parts[1]), int(parts[2])
            gpus.append((idx, used, total, total - used))
    return gpus

def wait_for_gpu():
    required_free = int(os.environ.get("SKT_PLAIN_REQUIRED_FREE_MB", "12000"))
    sleep_s = int(os.environ.get("SKT_PLAIN_GPU_WAIT_SEC", "60"))
    while True:
        gpus = query_gpus()
        if not gpus:
            return None
        best = max(gpus, key=lambda x: x[3])
        status = ", ".join(f"gpu{idx}:used={used}MB free={free}MB" for idx, used, total, free in gpus)
        if best[3] >= required_free:
            log(f"[gpu] selected gpu{best[0]} ({status})")
            return str(best[0])
        log(f"[gpu-wait] need free>={required_free}MB; {status}; sleep {sleep_s}s")
        time.sleep(sleep_s)

def model_dir_for(train_set):
    return ROOT / "models" / MODEL_KEY / train_set / f"seed{SEED}"

def train_one(train_set, train_display, ratio):
    train_dir = ROOT / "data" / "train_sets" / train_set
    out_dir = model_dir_for(train_set)
    if (out_dir / "config.json").exists() and (out_dir / "label_map.json").exists():
        log(f"[train-skip] {train_display}: {out_dir}")
        return True
    if not (train_dir / "train.json").exists() or not (train_dir / "valid.json").exists():
        log(f"[train-fail] {train_display}: missing train/valid in {train_dir}")
        return False
    disk_guard()
    gpu = wait_for_gpu()
    env = os.environ.copy()
    env.update({
        "DATA_DIR": str(train_dir),
        "TRAIN_FILE": "train.json",
        "VALID_FILE": "valid.json",
        "MODEL_ID": MODEL_ID,
        "LR": os.environ.get("SKT_PLAIN_LR", "3e-5"),
        "SEED": str(SEED),
        "MICRO_BSZ": os.environ.get("SKT_PLAIN_MICRO_BSZ", "32"),
        "GRAD_ACCUM": os.environ.get("SKT_PLAIN_GRAD_ACCUM", "2"),
        "EPOCHS": os.environ.get("SKT_PLAIN_EPOCHS", "20"),
        "OUTPUT_DIR": str(out_dir),
        "SKIP_EVAL": "1",
        "RUN_TAG": f"real_{MODEL_KEY}_{train_set}_seed{SEED}",
    })
    if gpu is not None:
        env["CUDA_VISIBLE_DEVICES"] = gpu
    job_log = JOB_LOG_DIR / f"train__{MODEL_KEY}__{train_set}__seed{SEED}.log"
    log(f"[train-start] {train_display} -> {out_dir}")
    code = run_to_log([sys.executable, "train_baseline.py"], env, job_log)
    if code != 0:
        log(f"[train-fail] {train_display} exit={code} log={job_log}")
        return False
    ok = (out_dir / "config.json").exists()
    log(f"[train-done] {train_display} ok={ok} log={job_log}")
    return ok

def eval_one(train_set, train_display, ratio, test_set, scope):
    model_dir = model_dir_for(train_set)
    if not (model_dir / "config.json").exists():
        log(f"[eval-skip] {train_display}->{test_set}/{scope}: missing model {model_dir}")
        return False
    test_dir = ROOT / "data" / "test_sets" / test_set
    if not (test_dir / "test.json").exists():
        log(f"[eval-fail] missing test set {test_dir}")
        return False
    job_id = f"eval__{MODEL_KEY}__{train_set}__{test_set}__{scope}"
    metric_path = ROOT / "results" / "metrics" / f"{job_id}.json"
    if metric_path.exists():
        log(f"[eval-skip] {job_id}: metric exists")
        return True
    disk_guard()
    gpu = wait_for_gpu()
    env = os.environ.copy()
    if gpu is not None:
        env["CUDA_VISIBLE_DEVICES"] = gpu
    tag = f"real_{MODEL_KEY}_{train_set}_to_{test_set}_{scope}"
    cmd = [
        sys.executable,
        "eval_baseline_ensemble_vote.py",
        "--data-dir",
        str(test_dir),
        "--split",
        "test",
        "--min_votes",
        "1",
        "--no_cache",
        "--tag",
        tag,
        "--batch_size",
        os.environ.get("SKT_PLAIN_EVAL_BSZ", "64"),
        "--max_length",
        os.environ.get("SKT_PLAIN_MAX_LEN", "256"),
    ]
    if scope == "common18":
        cmd.extend(["--exclude-labels", COMMON18_EXCLUDE])
    cmd.append("--model_dirs")
    cmd.append(str(model_dir))
    job_log = JOB_LOG_DIR / f"{job_id}.log"
    log(f"[eval-start] {train_display} -> {test_set}/{scope}")
    code = run_to_log(cmd, env, job_log)
    if code != 0:
        log(f"[eval-fail] {job_id} exit={code} log={job_log}")
        return False
    try:
        metrics = runner.parse_metrics_from_log(job_log)
    except Exception as exc:
        log(f"[eval-fail] {job_id}: parse failed: {exc} log={job_log}")
        return False
    row = {
        "model": MODEL_KEY,
        "model_display": MODEL_DISPLAY,
        "train_set": train_set,
        "synthetic_ratio": ratio,
        "test_set": test_set,
        "label_scope": scope,
        **metrics,
        "job_id": job_id,
        "log_path": str(job_log),
        "model_dirs": [str(model_dir)],
    }
    runner.write_metric(ROOT, row)
    log(
        f"[eval-done] {job_id} P={metrics['precision_micro']:.4f} "
        f"R={metrics['recall_micro']:.4f} F1={metrics['f1_micro']:.4f}"
    )
    return True

def main():
    log(f"[protocol-start] model={MODEL_DISPLAY} train_sets={[x[0] for x in TRAIN_SPECS]} tests={TEST_SETS} scopes={LABEL_SCOPES}")
    failures = []
    for train_set, train_display, ratio in TRAIN_SPECS:
        ok = train_one(train_set, train_display, ratio)
        if not ok:
            failures.append(f"train:{train_set}")
            continue
        for test_set in TEST_SETS:
            for scope in LABEL_SCOPES:
                ok = eval_one(train_set, train_display, ratio, test_set, scope)
                if not ok:
                    failures.append(f"eval:{train_set}:{test_set}:{scope}")
    if failures:
        log(f"[protocol-complete-with-failures] n={len(failures)} failures={failures}")
        raise SystemExit(1)
    log("[protocol-complete] all requested SKT plain metrics are ready")

if __name__ == "__main__":
    main()

