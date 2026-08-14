#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 1 ] || [ "$#" -gt 2 ]; then
  echo "Usage: bash package_pii_mix_all_ensemble_bundle.sh MODEL_ROOT [OUT_TARBALL]" >&2
  echo "Example: bash package_pii_mix_all_ensemble_bundle.sh /data/team/hwan/real/models/skt_crf_gaz_x3/mix_syn_all pii_skt_crf_gaz_mix_all_x3_local_app.tar.gz" >&2
  exit 2
fi

MODEL_ROOT="$1"
OUT_TARBALL="${2:-pii_skt_crf_gaz_mix_all_x3_local_app_$(date +%Y%m%d_%H%M%S).tar.gz}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SEEDS=(seed42 seed43 seed44)

if [ ! -d "$MODEL_ROOT" ]; then
  echo "[error] model root not found: $MODEL_ROOT" >&2
  exit 1
fi

for seed in "${SEEDS[@]}"; do
  MODEL_DIR="$MODEL_ROOT/$seed"
  if [ ! -d "$MODEL_DIR" ]; then
    echo "[error] missing seed model directory: $MODEL_DIR" >&2
    exit 1
  fi
  for f in config.json label_map.json gazetteer.json tokenizer.json tokenizer_config.json; do
    if [ ! -f "$MODEL_DIR/$f" ]; then
      echo "[error] missing required model file: $MODEL_DIR/$f" >&2
      exit 1
    fi
  done
  if [ ! -f "$MODEL_DIR/model.safetensors" ] && [ ! -f "$MODEL_DIR/pytorch_model.bin" ]; then
    echo "[error] missing model weights in $MODEL_DIR" >&2
    exit 1
  fi
done

for f in local_pii_inference.py local_pii_ensemble_inference.py requirements.txt README.md; do
  if [ ! -f "$SCRIPT_DIR/$f" ]; then
    echo "[error] missing handoff file: $SCRIPT_DIR/$f" >&2
    exit 1
  fi
done

for f in pii_model.py crf_bio.py gazetteer.py; do
  if [ ! -f "$SCRIPT_DIR/runtime_sources/$f" ]; then
    echo "[error] missing runtime source: $SCRIPT_DIR/runtime_sources/$f" >&2
    exit 1
  fi
done

STAGE_PARENT="${STAGE_PARENT:-$(dirname "$(readlink -f "$OUT_TARBALL" 2>/dev/null || python3 -c 'import os,sys; print(os.path.abspath(sys.argv[1]))' "$OUT_TARBALL")")}"
STAGE="$(mktemp -d "$STAGE_PARENT/pii_mixall_bundle.XXXXXX")"
cleanup() {
  rm -rf "$STAGE"
}
trap cleanup EXIT

copy_tree() {
  local src="$1"
  local dst="$2"
  mkdir -p "$dst"
  if ! cp -al "$src"/. "$dst"/ 2>/dev/null; then
    cp -a "$src"/. "$dst"/
  fi
}

mkdir -p "$STAGE/pii_engine/models" "$STAGE/pii_engine/runtime"
for seed in "${SEEDS[@]}"; do
  copy_tree "$MODEL_ROOT/$seed" "$STAGE/pii_engine/models/$seed"
done

cp "$SCRIPT_DIR/local_pii_inference.py" "$STAGE/pii_engine/runtime/"
cp "$SCRIPT_DIR/local_pii_ensemble_inference.py" "$STAGE/pii_engine/runtime/"
cp "$SCRIPT_DIR/requirements.txt" "$STAGE/pii_engine/runtime/requirements.txt"
cp "$SCRIPT_DIR/README.md" "$STAGE/pii_engine/README.md"
for f in pii_model.py crf_bio.py gazetteer.py; do
  cp "$SCRIPT_DIR/runtime_sources/$f" "$STAGE/pii_engine/runtime/"
done

python3 - "$MODEL_ROOT" "$STAGE/pii_engine" <<'PY'
import json
import sys
from datetime import datetime
from pathlib import Path

from transformers import AutoConfig

model_root = Path(sys.argv[1])
bundle_root = Path(sys.argv[2])
seeds = ["seed42", "seed43", "seed44"]

seed_manifests = []
base_model = None
target_labels = None
for seed in seeds:
    source_dir = model_root / seed
    bundled_dir = bundle_root / "models" / seed
    label_map = json.loads((source_dir / "label_map.json").read_text(encoding="utf-8"))
    seed_base_model = label_map.get("model_id", "skt/A.X-Encoder-base")
    base_model = base_model or seed_base_model
    target_labels = target_labels or label_map.get("target_labels", [])

    backbone_config_dir = bundled_dir / "backbone_config"
    backbone_config_dir.mkdir(parents=True, exist_ok=True)
    try:
        backbone_cfg = AutoConfig.from_pretrained(seed_base_model, trust_remote_code=True, local_files_only=True)
    except Exception:
        backbone_cfg = AutoConfig.from_pretrained(seed_base_model, trust_remote_code=True)
    backbone_cfg.save_pretrained(backbone_config_dir)

    seed_manifests.append({
        "seed": seed,
        "source_model_dir": str(source_dir),
        "base_model": seed_base_model,
        "run_tag": label_map.get("run_tag"),
        "use_crf": label_map.get("use_crf"),
        "use_gazetteer": label_map.get("use_gazetteer"),
        "use_kd": label_map.get("use_kd"),
        "use_rdrop": label_map.get("use_rdrop"),
        "use_fgm": label_map.get("use_fgm"),
    })

metrics_root = Path("/data/team/hwan/real/results/metrics")
metric_files = {
    "combined_full19": metrics_root / "eval__skt_crf_gaz_x3__mix_syn_all__combined__full19.json",
    "kdpii_full19": metrics_root / "eval__skt_crf_gaz_x3__mix_syn_all__kdpii__full19.json",
    "synthetic_full19": metrics_root / "eval__skt_crf_gaz_x3__mix_syn_all__synthetic__full19.json",
}
metrics = {}
for name, path in metric_files.items():
    if not path.exists():
        continue
    raw = json.loads(path.read_text(encoding="utf-8"))
    tp = raw.get("tp", 0) or 0
    fp = raw.get("fp", 0) or 0
    fn = raw.get("fn", 0) or 0
    precision = raw.get("precision", raw.get("micro_precision"))
    recall = raw.get("recall", raw.get("micro_recall"))
    f1 = raw.get("f1", raw.get("micro_f1"))
    if precision is None:
        precision = tp / (tp + fp) if tp + fp else 0.0
    if recall is None:
        recall = tp / (tp + fn) if tp + fn else 0.0
    if f1 is None:
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    metrics[name] = {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "model_dirs": raw.get("model_dirs"),
    }

manifest = {
    "bundle_name": "pii_skt_crf_gaz_mix_all_x3_local_app",
    "created_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
    "source_model_root": str(model_root),
    "base_model": base_model,
    "training_recipe": "SKT CRF+Gaz x3, Mix-all",
    "training_data": "KDPII + clean synthetic Mix-all training split used by real pipeline",
    "runtime": "python-sidecar-stdio",
    "single_model": False,
    "ensemble": True,
    "ensemble_method": "same-label overlapping-span majority vote",
    "default_min_votes": 2,
    "entrypoint": "runtime/local_pii_ensemble_inference.py",
    "model_dirs": [f"models/{seed}" for seed in seeds],
    "target_labels": target_labels,
    "seeds": seed_manifests,
    "metrics": metrics,
}
try:
    import torch
    import transformers

    manifest["torch_version_at_packaging"] = torch.__version__
    manifest["transformers_version_at_packaging"] = transformers.__version__
except Exception:
    pass
(bundle_root / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
PY

tar -czf "$OUT_TARBALL" -C "$STAGE" pii_engine
echo "[done] wrote $OUT_TARBALL"
