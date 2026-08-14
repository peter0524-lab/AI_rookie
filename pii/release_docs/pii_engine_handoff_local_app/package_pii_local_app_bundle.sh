#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 1 ] || [ "$#" -gt 2 ]; then
  echo "Usage: bash package_pii_local_app_bundle.sh MODEL_DIR [OUT_TARBALL]" >&2
  exit 2
fi

MODEL_DIR="$1"
OUT_TARBALL="${2:-pii_skt_crf_gaz_local_app_$(date +%Y%m%d_%H%M%S).tar.gz}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ ! -d "$MODEL_DIR" ]; then
  echo "[error] model directory not found: $MODEL_DIR" >&2
  exit 1
fi

for f in config.json label_map.json gazetteer.json; do
  if [ ! -f "$MODEL_DIR/$f" ]; then
    echo "[error] missing required model file: $MODEL_DIR/$f" >&2
    exit 1
  fi
done

if [ ! -f "$MODEL_DIR/model.safetensors" ] && [ ! -f "$MODEL_DIR/pytorch_model.bin" ]; then
  echo "[error] missing model weights: expected model.safetensors or pytorch_model.bin" >&2
  exit 1
fi

for f in local_pii_inference.py requirements-pii-engine.txt; do
  if [ ! -f "$SCRIPT_DIR/$f" ]; then
    echo "[error] missing handoff file: $SCRIPT_DIR/$f" >&2
    exit 1
  fi
done

for f in pii_model.py crf_bio.py gazetteer.py; do
  if [ ! -f "$SCRIPT_DIR/runtime_sources/$f" ] && [ ! -f "$f" ]; then
    echo "[error] missing runtime source: $f" >&2
    echo "        expected either $SCRIPT_DIR/runtime_sources/$f or ./$f" >&2
    exit 1
  fi
done

STAGE="$(mktemp -d)"
cleanup() {
  rm -rf "$STAGE"
}
trap cleanup EXIT

mkdir -p "$STAGE/pii_engine/model" "$STAGE/pii_engine/runtime"
cp -R "$MODEL_DIR"/. "$STAGE/pii_engine/model/"
cp "$SCRIPT_DIR/local_pii_inference.py" "$STAGE/pii_engine/runtime/"
cp "$SCRIPT_DIR/requirements-pii-engine.txt" "$STAGE/pii_engine/runtime/requirements.txt"
for f in pii_model.py crf_bio.py gazetteer.py; do
  if [ -f "$SCRIPT_DIR/runtime_sources/$f" ]; then
    cp "$SCRIPT_DIR/runtime_sources/$f" "$STAGE/pii_engine/runtime/"
  else
    cp "$f" "$STAGE/pii_engine/runtime/"
  fi
done

python3 - "$MODEL_DIR" "$STAGE/pii_engine/model/backbone_config" "$STAGE/pii_engine/manifest.json" <<'PY'
import json
import sys
from datetime import datetime
from pathlib import Path

from transformers import AutoConfig

model_dir = Path(sys.argv[1])
backbone_config_dir = Path(sys.argv[2])
manifest_path = Path(sys.argv[3])

label_map = json.loads((model_dir / "label_map.json").read_text(encoding="utf-8"))
base_model = label_map.get("model_id", "skt/A.X-Encoder-base")

backbone_config_dir.mkdir(parents=True, exist_ok=True)
AutoConfig.from_pretrained(base_model, trust_remote_code=True).save_pretrained(backbone_config_dir)

manifest = {
    "bundle_name": "pii_skt_crf_gaz_local_app",
    "created_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
    "source_model_dir": str(model_dir),
    "base_model": base_model,
    "training_data": "KDPII + cleaned synthetic PII",
    "runtime": "python-sidecar-stdio",
    "single_model": True,
    "ensemble": False,
    "use_crf": label_map.get("use_crf"),
    "use_gazetteer": label_map.get("use_gazetteer"),
    "target_labels": label_map.get("target_labels", []),
    "entrypoint": "runtime/local_pii_inference.py",
    "model_dir": "model",
}
try:
    import torch
    import transformers

    manifest["torch_version"] = torch.__version__
    manifest["transformers_version"] = transformers.__version__
except Exception:
    pass
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
PY

cat > "$STAGE/pii_engine/README_LOCAL_APP.md" <<'EOF'
# Local App PII Engine Bundle

Run once:

```bash
cd pii_engine/runtime
python3 -m pip install -r requirements.txt
```

Single request:

```bash
python3 local_pii_inference.py --model-dir ../model --text "홍길동 [PHONE_PLACEHOLDER]"
```

Long-running local-app mode:

```bash
python3 local_pii_inference.py --model-dir ../model --stdio
```

STDIO input:

```json
{"id":"req-1","text":"홍길동 [PHONE_PLACEHOLDER]"}
```

STDIO output:

```json
{"id":"req-1","entities":[{"form":"[PHONE_PLACEHOLDER]","label":"QT_MOBILE","begin":4,"end":17}]}
```
EOF

tar -czf "$OUT_TARBALL" -C "$STAGE" pii_engine
echo "[done] wrote $OUT_TARBALL"
