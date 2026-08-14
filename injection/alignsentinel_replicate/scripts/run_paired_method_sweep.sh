#!/usr/bin/env bash
set -euo pipefail

MODEL_ID="${MODEL_ID:-skt/A.X-4.0-Light}"
SAFE_MODEL_ID="$(echo "$MODEL_ID" | sed 's#[/:.]#_#g')"

DATA_ARGS="${DATA_ARGS:-data/full_train.json data/full_test.json}"
STATS_DIR="${STATS_DIR:-features_paired_stats/${SAFE_MODEL_ID}}"
FEATURE_DIR="${FEATURE_DIR:-features_paired/${SAFE_MODEL_ID}}"
RESULTS_DIR="${RESULTS_DIR:-results_paired/${SAFE_MODEL_ID}}"
MODELS_DIR="${MODELS_DIR:-models_paired/${SAFE_MODEL_ID}}"
HEADS_FILE="${HEADS_FILE:-${STATS_DIR}/paired_heads.json}"

TOP_R="${TOP_R:-32}"
MI="${MI:-64}"
MC="${MC:-64}"
MAX_PAIRS="${MAX_PAIRS:-1024}"
EPOCHS="${EPOCHS:-120}"
RUN_MODES="${RUN_MODES:-domain pooled cross}"
TOOL_MESSAGE_MODE="${TOOL_MESSAGE_MODE:-auto}"
PYTHON_BIN="${PYTHON_BIN:-python}"
TRUST_REMOTE_CODE="${TRUST_REMOTE_CODE:-1}"

export HF_HOME="${HF_HOME:-/data/team/hwan/.cache/huggingface}"
export HF_HUB_CACHE="${HF_HUB_CACHE:-/data/team/hwan/.cache/huggingface/hub}"
export HF_MODULES_CACHE="${HF_MODULES_CACHE:-/data/team/hwan/.cache/huggingface/modules}"
export TRANSFORMERS_CACHE="${TRANSFORMERS_CACHE:-/data/team/hwan/.cache/huggingface/transformers}"
export TORCH_HOME="${TORCH_HOME:-/data/team/hwan/.cache/torch}"

TRUST_ARGS=()
if [[ "$TRUST_REMOTE_CODE" == "1" ]]; then
  TRUST_ARGS+=(--trust-remote-code)
fi

mkdir -p "$STATS_DIR" "$FEATURE_DIR" "$RESULTS_DIR" "$MODELS_DIR"

echo "================================================================"
echo "[paired-method] $MODEL_ID"
echo "[dirs] stats=$STATS_DIR features=$FEATURE_DIR results=$RESULTS_DIR"
echo "================================================================"

if [[ ! -f "$HEADS_FILE" ]]; then
  echo "[stage 1] head summaries"
  "$PYTHON_BIN" src/extract_paired_features.py head-stats \
    --data $DATA_ARGS \
    --out "$STATS_DIR" \
    --model "$MODEL_ID" \
    --tool-message-mode "$TOOL_MESSAGE_MODE" \
    --top-r "$TOP_R" \
    "${TRUST_ARGS[@]}"

  echo "[stage 2] paired head selection"
  "$PYTHON_BIN" src/select_paired_heads.py \
    --stats "$STATS_DIR" \
    --out "$HEADS_FILE" \
    --top-r "$TOP_R" \
    --mi "$MI" \
    --mc "$MC"
else
  echo "[skip] head file exists: $HEADS_FILE"
fi

echo "[stage 3] head-guided pair features"
"$PYTHON_BIN" src/extract_paired_features.py pair-features \
  --data $DATA_ARGS \
  --out "$FEATURE_DIR" \
  --model "$MODEL_ID" \
  --tool-message-mode "$TOOL_MESSAGE_MODE" \
  --heads "$HEADS_FILE" \
  --max-pairs "$MAX_PAIRS" \
  "${TRUST_ARGS[@]}"

echo "[stage 4] hierarchical paired detector"
"$PYTHON_BIN" src/train_paired_detector.py \
  --features "$FEATURE_DIR" \
  --results "$RESULTS_DIR" \
  --models-dir "$MODELS_DIR" \
  --epochs "$EPOCHS" \
  --run $RUN_MODES

echo "[done] paired-method $MODEL_ID -> $RESULTS_DIR/summary.md"
