#!/usr/bin/env bash
set -euo pipefail

MODEL_IDS_TEXT="${MODEL_IDS_TEXT:-LGAI-EXAONE/EXAONE-Deep-7.8B Qwen/Qwen3-8B skt/A.X-4.0-Light}"
CONTINUE_ON_ERROR="${CONTINUE_ON_ERROR:-1}"
SKIP_DONE="${SKIP_DONE:-1}"
EXAONE_PYTHON_BIN="${EXAONE_PYTHON_BIN:-/data/team/hwan/.venvs/alignsentinel_exaone/bin/python}"
DEFAULT_PYTHON_BIN="${PYTHON_BIN:-python}"

FAILED=()

for MODEL_ID in $MODEL_IDS_TEXT; do
  SAFE_MODEL_ID="$(echo "$MODEL_ID" | sed 's#[/:.]#_#g')"
  SUMMARY="results_paired/${SAFE_MODEL_ID}/summary.md"
  echo "================================================================"
  echo "[start] paired-method $MODEL_ID"
  echo "================================================================"

  if [[ "$SKIP_DONE" == "1" && -f "$SUMMARY" ]]; then
    echo "[skip] summary exists: $SUMMARY"
    continue
  fi

  PY="$DEFAULT_PYTHON_BIN"
  if [[ "$MODEL_ID" == LGAI-EXAONE/* && -x "$EXAONE_PYTHON_BIN" ]]; then
    PY="$EXAONE_PYTHON_BIN"
  fi

  if MODEL_ID="$MODEL_ID" PYTHON_BIN="$PY" bash scripts/run_paired_method_sweep.sh; then
    echo "[done] paired-method $MODEL_ID"
  else
    echo "[fail] paired-method $MODEL_ID"
    FAILED+=("$MODEL_ID")
    if [[ "$CONTINUE_ON_ERROR" != "1" ]]; then
      exit 1
    fi
  fi
done

if [[ "${#FAILED[@]}" -gt 0 ]]; then
  echo "[summary] failed models: ${FAILED[*]}"
  exit 1
fi

echo "[summary] all paired-method models completed"
