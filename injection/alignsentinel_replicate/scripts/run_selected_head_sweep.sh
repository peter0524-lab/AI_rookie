#!/usr/bin/env bash
set -euo pipefail

MODEL_ID="${MODEL_ID:-skt/A.X-4.0-Light}"
SAFE_MODEL_ID="$(echo "$MODEL_ID" | sed 's#[/:.]#_#g')"

DATA_ARGS="${DATA_ARGS:-data/full_train.json data/full_test.json}"
STATS_DIR="${STATS_DIR:-features_paired_stats/${SAFE_MODEL_ID}}"
HEADS_FILE="${HEADS_FILE:-${STATS_DIR}/paired_heads.json}"
FEATURE_DIR="${FEATURE_DIR:-features_selected/${SAFE_MODEL_ID}_${HEAD_MODE:-union}_${SCORE_MODE:-union}}"
RESULTS_DIR="${RESULTS_DIR:-results_selected/${SAFE_MODEL_ID}_${DETECTOR:-regularized}_${HEAD_MODE:-union}_${SCORE_MODE:-union}}"
MODELS_DIR="${MODELS_DIR:-models_selected/${SAFE_MODEL_ID}_${DETECTOR:-regularized}_${HEAD_MODE:-union}_${SCORE_MODE:-union}}"

TOP_R="${TOP_R:-32}"
MI="${MI:-64}"
MC="${MC:-64}"
MAX_HEADS="${MAX_HEADS:-128}"
MAX_PAIRS="${MAX_PAIRS:-1024}"
TOP_PAIRS="${TOP_PAIRS:-768}"
RANDOM_PAIRS="${RANDOM_PAIRS:-256}"
HEAD_MODE="${HEAD_MODE:-union}"
SCORE_MODE="${SCORE_MODE:-union}"
INSTRUCTION_SCORE_WEIGHT="${INSTRUCTION_SCORE_WEIGHT:-0.5}"
CONFLICT_SCORE_WEIGHT="${CONFLICT_SCORE_WEIGHT:-1.0}"

EPOCHS="${EPOCHS:-200}"
DETECTOR="${DETECTOR:-regularized}"
DROPOUT="${DROPOUT:-0.2}"
WEIGHT_DECAY="${WEIGHT_DECAY:-0.0001}"
VAL_RATIO="${VAL_RATIO:-0.15}"
PATIENCE="${PATIENCE:-25}"
TRUST_REMOTE_CODE="${TRUST_REMOTE_CODE:-1}"
TOOL_MESSAGE_MODE="${TOOL_MESSAGE_MODE:-auto}"
PYTHON_BIN="${PYTHON_BIN:-python}"

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
echo "[selected-head] $MODEL_ID"
echo "[dirs] stats=$STATS_DIR features=$FEATURE_DIR results=$RESULTS_DIR"
echo "[config] head_mode=$HEAD_MODE score_mode=$SCORE_MODE heads<=$MAX_HEADS K=$MAX_PAIRS top=$TOP_PAIRS random=$RANDOM_PAIRS"
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

echo "[stage 3] selected-head top-k Enc-first features"
"$PYTHON_BIN" src/extract_selected_features.py \
  --data $DATA_ARGS \
  --out "$FEATURE_DIR" \
  --model "$MODEL_ID" \
  --tool-message-mode "$TOOL_MESSAGE_MODE" \
  --heads "$HEADS_FILE" \
  --head-mode "$HEAD_MODE" \
  --score-mode "$SCORE_MODE" \
  --max-heads "$MAX_HEADS" \
  --max-pairs "$MAX_PAIRS" \
  --top-pairs "$TOP_PAIRS" \
  --random-pairs "$RANDOM_PAIRS" \
  --instruction-score-weight "$INSTRUCTION_SCORE_WEIGHT" \
  --conflict-score-weight "$CONFLICT_SCORE_WEIGHT" \
  "${TRUST_ARGS[@]}"

TRAIN_ARGS=(
  --epochs "$EPOCHS"
  --detector "$DETECTOR"
  --standardize
)
if [[ "$DETECTOR" == "regularized" ]]; then
  TRAIN_ARGS+=(
    --dropout "$DROPOUT"
    --weight-decay "$WEIGHT_DECAY"
    --val-ratio "$VAL_RATIO"
    --patience "$PATIENCE"
    --class-weights
  )
fi

echo "[stage 4] original regularized Enc-first detector on selected features"
"$PYTHON_BIN" src/train_detector.py --features "$FEATURE_DIR" --variant enc --domains all \
  --results "$RESULTS_DIR" --models-dir "$MODELS_DIR" "${TRAIN_ARGS[@]}"
"$PYTHON_BIN" src/train_detector.py --features "$FEATURE_DIR" --variant enc --pooled \
  --results "$RESULTS_DIR" --models-dir "$MODELS_DIR" "${TRAIN_ARGS[@]}"
"$PYTHON_BIN" src/train_detector.py --features "$FEATURE_DIR" --variant enc --cross A2B \
  --results "$RESULTS_DIR" --models-dir "$MODELS_DIR" "${TRAIN_ARGS[@]}"
"$PYTHON_BIN" src/train_detector.py --features "$FEATURE_DIR" --variant enc --cross B2A \
  --results "$RESULTS_DIR" --models-dir "$MODELS_DIR" "${TRAIN_ARGS[@]}"

"$PYTHON_BIN" src/aggregate_results.py --results "$RESULTS_DIR" \
  --out "$RESULTS_DIR/summary.md" \
  --features "$FEATURE_DIR" --data data/full_test.json

echo "[done] selected-head $MODEL_ID -> $RESULTS_DIR/summary.md"
