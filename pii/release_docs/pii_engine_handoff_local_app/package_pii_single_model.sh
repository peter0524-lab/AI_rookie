#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 1 ] || [ "$#" -gt 2 ]; then
  echo "Usage: bash package_pii_single_model.sh MODEL_DIR [OUT_TARBALL]" >&2
  exit 2
fi

MODEL_DIR="$1"
OUT_TARBALL="${2:-pii_skt_crf_gaz_mixed_single_$(date +%Y%m%d_%H%M%S).tar.gz}"

if [ ! -d "$MODEL_DIR" ]; then
  echo "[error] model directory not found: $MODEL_DIR" >&2
  exit 1
fi

required_model_files=("config.json" "label_map.json" "gazetteer.json")
for f in "${required_model_files[@]}"; do
  if [ ! -f "$MODEL_DIR/$f" ]; then
    echo "[error] missing required model file: $MODEL_DIR/$f" >&2
    exit 1
  fi
done

if [ ! -f "$MODEL_DIR/model.safetensors" ] && [ ! -f "$MODEL_DIR/pytorch_model.bin" ]; then
  echo "[error] missing model weights: expected model.safetensors or pytorch_model.bin" >&2
  exit 1
fi

required_code_files=("pii_model.py" "crf_bio.py" "gazetteer.py" "eval_crf_gaz.py")
for f in "${required_code_files[@]}"; do
  if [ ! -f "$f" ]; then
    echo "[error] run this script from the project root; missing $f" >&2
    exit 1
  fi
done

STAGE="$(mktemp -d)"
cleanup() {
  rm -rf "$STAGE"
}
trap cleanup EXIT

mkdir -p "$STAGE/model" "$STAGE/inference"
cp -R "$MODEL_DIR"/. "$STAGE/model/"
for f in "${required_code_files[@]}"; do
  cp "$f" "$STAGE/inference/"
done

python3 - "$MODEL_DIR" "$STAGE/manifest.json" <<'PY'
import json
import sys
from datetime import datetime
from pathlib import Path

model_dir = Path(sys.argv[1])
manifest_path = Path(sys.argv[2])
label_map_path = model_dir / "label_map.json"
label_map = json.loads(label_map_path.read_text(encoding="utf-8"))
manifest = {
    "bundle_name": "pii_skt_crf_gaz_mixed_single",
    "created_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
    "source_model_dir": str(model_dir),
    "base_model": label_map.get("model_id", "skt/A.X-Encoder-base"),
    "training_data": "KDPII + cleaned synthetic PII",
    "single_model": True,
    "ensemble": False,
    "use_crf": label_map.get("use_crf"),
    "use_gazetteer": label_map.get("use_gazetteer"),
    "use_rdrop": label_map.get("use_rdrop"),
    "use_fgm": label_map.get("use_fgm"),
    "target_labels": label_map.get("target_labels", []),
    "load_note": "Load with trust_remote_code=True and use gazetteer features before CRF decoding.",
}
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
PY

tar -czf "$OUT_TARBALL" -C "$STAGE" .
echo "[done] wrote $OUT_TARBALL"
