#!/usr/bin/env bash
set -euo pipefail

MODEL_IDS_TEXT="${MODEL_IDS_TEXT:-meta-llama/Llama-3.1-8B-Instruct Qwen/Qwen3-8B LGAI-EXAONE/EXAONE-Deep-7.8B skt/A.X-4.0-Light}"
CONTINUE_ON_ERROR="${CONTINUE_ON_ERROR:-1}"
SKIP_DONE="${SKIP_DONE:-1}"
EXAONE_PYTHON_BIN="${EXAONE_PYTHON_BIN:-/data/team/hwan/.venvs/alignsentinel_exaone/bin/python}"
DEFAULT_PYTHON_BIN="${PYTHON_BIN:-python}"
DETECTOR="${DETECTOR:-regularized}"
HEAD_MODE="${HEAD_MODE:-union}"
SCORE_MODE="${SCORE_MODE:-union}"

FAILED=()

for MODEL_ID in $MODEL_IDS_TEXT; do
  SAFE_MODEL_ID="$(echo "$MODEL_ID" | sed 's#[/:.]#_#g')"
  SUMMARY="results_selected/${SAFE_MODEL_ID}_${DETECTOR}_${HEAD_MODE}_${SCORE_MODE}/summary.md"
  echo "================================================================"
  echo "[start] selected-head $MODEL_ID"
  echo "================================================================"

  if [[ "$SKIP_DONE" == "1" && -f "$SUMMARY" ]]; then
    echo "[skip] summary exists: $SUMMARY"
    continue
  fi

  PY="$DEFAULT_PYTHON_BIN"
  if [[ "$MODEL_ID" == LGAI-EXAONE/* && -x "$EXAONE_PYTHON_BIN" ]]; then
    PY="$EXAONE_PYTHON_BIN"
  fi

  if MODEL_ID="$MODEL_ID" PYTHON_BIN="$PY" DETECTOR="$DETECTOR" HEAD_MODE="$HEAD_MODE" SCORE_MODE="$SCORE_MODE" \
      bash scripts/run_selected_head_sweep.sh; then
    echo "[done] selected-head $MODEL_ID"
  else
    echo "[fail] selected-head $MODEL_ID"
    FAILED+=("$MODEL_ID")
    if [[ "$CONTINUE_ON_ERROR" != "1" ]]; then
      exit 1
    fi
  fi
done

if [[ "${#FAILED[@]}" -gt 0 ]]; then
  echo "[summary] failed selected-head models: ${FAILED[*]}"
  exit 1
fi

echo "[summary] all selected-head models completed"
