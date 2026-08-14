#!/usr/bin/env bash
# Evaluate Microsoft Presidio + Korean spaCy NER + Korean regex recognizers.
# No training is performed.
set -euo pipefail

cd "$(dirname "$0")"
mkdir -p logs results

SPACY_MODEL="${SPACY_MODEL:-ko_core_news_lg}"
KDPII_DATA_DIR="${KDPII_DATA_DIR:-data}"
SYNTH_DATA_DIR="${SYNTH_DATA_DIR:-synthetic}"
SPLIT="${SPLIT:-test}"
EXCLUDED_LABELS="${EXCLUDED_LABELS:-FD_MAJOR,OGG_EDUCATION,QT_AGE,QT_ALIEN_NUMBER}"

echo "=== Presidio + Korean spaCy NER + KO regex eval ==="
echo "SPACY_MODEL=${SPACY_MODEL}"
echo "KDPII_DATA_DIR=${KDPII_DATA_DIR}"
echo "SYNTH_DATA_DIR=${SYNTH_DATA_DIR}"
echo "SPLIT=${SPLIT}"
echo

python3 - <<PY
import importlib.util
import sys

required = ["presidio_analyzer", "spacy"]
missing = [name for name in required if importlib.util.find_spec(name) is None]
if missing:
    sys.exit("[ERROR] missing packages: " + ", ".join(missing))

model = "${SPACY_MODEL}"
if importlib.util.find_spec(model) is None:
    sys.exit("[ERROR] missing spaCy Korean model: " + model)
print("[deps] OK")
PY

run_eval() {
  local name="$1"
  shift
  local log="logs/presidio_${name}_$(date +%Y%m%d_%H%M%S).log"
  echo "[eval] ${name}"
  echo "       log=${log}"
  "$@" 2>&1 | tee "${log}"
}

run_eval "kdpii_full19" \
  python3 eval_presidio_ko_spacy_regex.py \
    --data-dir "${KDPII_DATA_DIR}" \
    --split "${SPLIT}" \
    --tag "kdpii_full19" \
    --spacy-model "${SPACY_MODEL}" \
    --require-presidio

run_eval "kdpii_common15" \
  python3 eval_presidio_ko_spacy_regex.py \
    --data-dir "${KDPII_DATA_DIR}" \
    --split "${SPLIT}" \
    --tag "kdpii_common15" \
    --spacy-model "${SPACY_MODEL}" \
    --exclude-labels "${EXCLUDED_LABELS}" \
    --require-presidio

run_eval "synthetic_test" \
  python3 eval_presidio_ko_spacy_regex.py \
    --data-dir "${SYNTH_DATA_DIR}" \
    --split "${SPLIT}" \
    --tag "synthetic_test" \
    --spacy-model "${SPACY_MODEL}" \
    --require-presidio

echo
echo "=== Result JSON files ==="
find results/presidio_ko_spacy_regex -type f -name "*.json" | sort | tail -20
