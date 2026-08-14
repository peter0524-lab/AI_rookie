#!/usr/bin/env bash
# XLM/OpenAI-privacy cross-domain baseline batch.
#
# Runs:
#   1) XLM-large KDPII-trained -> synthetic/test
#   2) OpenAI/privacy Korean LoRA KDPII-trained -> KDPII/test
#   3) OpenAI/privacy Korean LoRA KDPII-trained -> synthetic/test
#   4) Train XLM-large on synthetic if missing
#   5) Train OpenAI/privacy Korean synthetic LoRA if missing
#   6) XLM-large synthetic-trained -> KDPII/test common-15
#   7) XLM-large synthetic-trained -> synthetic/test
#   8) OpenAI/privacy Korean synthetic LoRA -> KDPII/test common-15
#   9) OpenAI/privacy Korean synthetic LoRA -> synthetic/test
#
# Default OpenAI/privacy model is the stronger Korean LoRA inference checkpoint.
set -euo pipefail

cd "$(dirname "$0")"
mkdir -p logs

KDPII_DATA_DIR="${KDPII_DATA_DIR:-data}"
SYNTH_DATA_DIR="${SYNTH_DATA_DIR:-synthetic}"
SPLIT="${SPLIT:-test}"

EXCLUDED_LABELS="${EXCLUDED_LABELS:-FD_MAJOR,OGG_EDUCATION,QT_AGE,QT_ALIEN_NUMBER}"

XLM_KDPII_DIR="${XLM_KDPII_DIR:-models/xlm_roberta_large/seed42}"
XLM_SYNTH_DIR="${XLM_SYNTH_DIR:-models/xlm_roberta_large_synthetic/seed42}"
PRIVACY_KDPII_DIR="${PRIVACY_KDPII_DIR:-${PRIVACY_MODEL_DIR:-models/privacy_filter_korean_Lora/seed42/inference}}"
PRIVACY_BASE_MODEL_DIR="${PRIVACY_BASE_MODEL_DIR:-models/privacy_filter_korean}"
PRIVACY_SYNTH_DIR="${PRIVACY_SYNTH_DIR:-models/privacy_filter_korean_Lora_synthetic/seed42}"
PRIVACY_SYNTH_INFERENCE_DIR="${PRIVACY_SYNTH_INFERENCE_DIR:-${PRIVACY_SYNTH_DIR}/inference}"

XLM_EVAL_BSZ="${XLM_EVAL_BSZ:-32}"
PRIVACY_EVAL_BSZ="${PRIVACY_EVAL_BSZ:-64}"
PRIVACY_TRAIN_BSZ="${PRIVACY_TRAIN_BSZ:-256}"
MAX_LENGTH="${MAX_LENGTH:-256}"

# Set MAX_EVAL_JOBS manually to override auto. On A100 80GB, 3 eval jobs is usually safe.
MAX_EVAL_JOBS="${MAX_EVAL_JOBS:-auto}"
MAX_TRAIN_JOBS="${MAX_TRAIN_JOBS:-auto}"

gpu_free_mib() {
  nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -1 | tr -d ' '
}

auto_eval_jobs() {
  local free
  free="$(gpu_free_mib || echo 0)"
  if [ "${free}" -ge 70000 ]; then
    echo 3
  elif [ "${free}" -ge 40000 ]; then
    echo 2
  else
    echo 1
  fi
}

if [ "${MAX_EVAL_JOBS}" = "auto" ]; then
  MAX_EVAL_JOBS="$(auto_eval_jobs)"
fi

if [ "${MAX_TRAIN_JOBS}" = "auto" ]; then
  if [ "$(gpu_free_mib || echo 0)" -ge 70000 ]; then
    MAX_TRAIN_JOBS=2
  else
    MAX_TRAIN_JOBS=1
  fi
fi

echo "=== XLM/OpenAI privacy cross-domain batch ==="
echo "gpu: $(nvidia-smi --query-gpu=name,memory.total,memory.free --format=csv,noheader | head -1)"
echo "KDPII_DATA_DIR=${KDPII_DATA_DIR}  SYNTH_DATA_DIR=${SYNTH_DATA_DIR}  split=${SPLIT}"
echo "MAX_EVAL_JOBS=${MAX_EVAL_JOBS}"
echo "MAX_TRAIN_JOBS=${MAX_TRAIN_JOBS}"
echo "XLM_KDPII_DIR=${XLM_KDPII_DIR}"
echo "XLM_SYNTH_DIR=${XLM_SYNTH_DIR}"
echo "PRIVACY_KDPII_DIR=${PRIVACY_KDPII_DIR}"
echo "PRIVACY_BASE_MODEL_DIR=${PRIVACY_BASE_MODEL_DIR}"
echo "PRIVACY_SYNTH_INFERENCE_DIR=${PRIVACY_SYNTH_INFERENCE_DIR}"
echo

require_model() {
  local path="$1"
  if [ ! -f "${path}/config.json" ]; then
    echo "[ERROR] model not found or missing config.json: ${path}" >&2
    exit 1
  fi
}

require_model "${XLM_KDPII_DIR}"
require_model "${PRIVACY_KDPII_DIR}"
require_model "${PRIVACY_BASE_MODEL_DIR}"

PIDS=()
NAMES=()

wait_for_slot() {
  local max_jobs="$1"
  while [ "$(jobs -rp | wc -l | tr -d ' ')" -ge "${max_jobs}" ]; do
    sleep 5
  done
}

launch_eval() {
  local name="$1"
  shift
  wait_for_slot "${MAX_EVAL_JOBS}"
  local safe_name
  safe_name="$(echo "${name}" | tr ' /' '__' | tr -cd '[:alnum:]_.-')"
  local log="logs/${safe_name}_$(date +%Y%m%d_%H%M%S).log"
  echo "[launch] ${name}"
  echo "         log=${log}"
  "$@" > "${log}" 2>&1 &
  PIDS+=("$!")
  NAMES+=("${name}")
}

launch_train() {
  local name="$1"
  shift
  wait_for_slot "${MAX_TRAIN_JOBS}"
  local safe_name
  safe_name="$(echo "${name}" | tr ' /' '__' | tr -cd '[:alnum:]_.-')"
  local log="logs/${safe_name}_$(date +%Y%m%d_%H%M%S).log"
  echo "[train-launch] ${name}"
  echo "               log=${log}"
  "$@" > "${log}" 2>&1 &
  PIDS+=("$!")
  NAMES+=("${name}")
}

wait_group() {
  local failed=0
  local i
  for i in "${!PIDS[@]}"; do
    if wait "${PIDS[$i]}"; then
      echo "[done] ${NAMES[$i]}"
    else
      echo "[FAIL] ${NAMES[$i]}" >&2
      failed=1
    fi
  done
  PIDS=()
  NAMES=()
  if [ "${failed}" -ne 0 ]; then
    echo "[ERROR] One or more jobs failed. Check logs/." >&2
    exit 1
  fi
}

echo "=== Phase 1: existing-model evals in parallel ==="

launch_eval "xlm_kdpii_to_synthetic" \
  python3 eval_baseline_ensemble_vote.py \
    --data-dir "${SYNTH_DATA_DIR}" \
    --split "${SPLIT}" \
    --min_votes 1 \
    --no_cache \
    --tag xlm_kdpii_seed42_to_synth \
    --batch_size "${XLM_EVAL_BSZ}" \
    --max_length "${MAX_LENGTH}" \
    --model_dirs "${XLM_KDPII_DIR}"

launch_eval "privacy_kdpii_lora_to_kdpii" \
  python3 eval_baseline_ensemble_vote.py \
    --data-dir "${KDPII_DATA_DIR}" \
    --split "${SPLIT}" \
    --min_votes 1 \
    --no_cache \
    --tag privacy_korean_lora_to_kdpii \
    --batch_size "${PRIVACY_EVAL_BSZ}" \
    --max_length "${MAX_LENGTH}" \
    --model_dirs "${PRIVACY_KDPII_DIR}"

launch_eval "privacy_kdpii_lora_to_synthetic" \
  python3 eval_baseline_ensemble_vote.py \
    --data-dir "${SYNTH_DATA_DIR}" \
    --split "${SPLIT}" \
    --min_votes 1 \
    --no_cache \
    --tag privacy_korean_lora_to_synth \
    --batch_size "${PRIVACY_EVAL_BSZ}" \
    --max_length "${MAX_LENGTH}" \
    --model_dirs "${PRIVACY_KDPII_DIR}"

wait_group

echo
echo "=== Phase 2: train synthetic models if needed ==="
if [ -f "${XLM_SYNTH_DIR}/model.safetensors" ] || [ -f "${XLM_SYNTH_DIR}/pytorch_model.bin" ]; then
  echo "[skip] XLM synthetic model already exists: ${XLM_SYNTH_DIR}"
else
  launch_train "train_xlm_synthetic" \
    env DATA_DIR="${SYNTH_DATA_DIR}" TRAIN_FILE=train.json VALID_FILE=valid.json \
      MODEL_ID=FacebookAI/xlm-roberta-large LR=1e-5 SEED=42 \
      MICRO_BSZ=16 GRAD_ACCUM=4 OUTPUT_DIR="${XLM_SYNTH_DIR}" SKIP_EVAL=1 \
      RUN_TAG=xlm_synth_seed42 \
      python3 train_baseline.py
fi

if [ -f "${PRIVACY_SYNTH_INFERENCE_DIR}/config.json" ]; then
  echo "[skip] privacy synthetic LoRA inference model already exists: ${PRIVACY_SYNTH_INFERENCE_DIR}"
else
  launch_train "train_privacy_korean_lora_synthetic" \
    env DATA_DIR="${SYNTH_DATA_DIR}" TRAIN_FILE=train.json VALID_FILE=valid.json \
      BASE_MODEL_DIR="${PRIVACY_BASE_MODEL_DIR}" \
      OUTPUT_DIR="${PRIVACY_SYNTH_DIR}" \
      INFERENCE_DIR="${PRIVACY_SYNTH_INFERENCE_DIR}" \
      SEED=42 RUN_TAG=privacy_korean_lora_synth_seed42 \
      MICRO_BSZ="${PRIVACY_TRAIN_BSZ}" GRAD_ACCUM=1 LR=5e-4 SKIP_EVAL=1 \
      python3 open_ai_privacy_filter_lora_train.py
fi

wait_group

require_model "${XLM_SYNTH_DIR}"
require_model "${PRIVACY_SYNTH_INFERENCE_DIR}"

echo
echo "=== Phase 3: synthetic-trained evals in parallel ==="

launch_eval "xlm_synth_to_kdpii_common15" \
  python3 eval_baseline_ensemble_vote.py \
    --data-dir "${KDPII_DATA_DIR}" \
    --split "${SPLIT}" \
    --min_votes 1 \
    --no_cache \
    --tag xlm_synth_seed42_to_kdpii_common15 \
    --batch_size "${XLM_EVAL_BSZ}" \
    --max_length "${MAX_LENGTH}" \
    --exclude-labels "${EXCLUDED_LABELS}" \
    --model_dirs "${XLM_SYNTH_DIR}"

launch_eval "xlm_synth_to_synthetic" \
  python3 eval_baseline_ensemble_vote.py \
    --data-dir "${SYNTH_DATA_DIR}" \
    --split "${SPLIT}" \
    --min_votes 1 \
    --no_cache \
    --tag xlm_synth_seed42_to_synth \
    --batch_size "${XLM_EVAL_BSZ}" \
    --max_length "${MAX_LENGTH}" \
    --model_dirs "${XLM_SYNTH_DIR}"

launch_eval "privacy_synth_lora_to_kdpii_common15" \
  python3 eval_baseline_ensemble_vote.py \
    --data-dir "${KDPII_DATA_DIR}" \
    --split "${SPLIT}" \
    --min_votes 1 \
    --no_cache \
    --tag privacy_korean_lora_synth_seed42_to_kdpii_common15 \
    --batch_size "${PRIVACY_EVAL_BSZ}" \
    --max_length "${MAX_LENGTH}" \
    --exclude-labels "${EXCLUDED_LABELS}" \
    --model_dirs "${PRIVACY_SYNTH_INFERENCE_DIR}"

launch_eval "privacy_synth_lora_to_synthetic" \
  python3 eval_baseline_ensemble_vote.py \
    --data-dir "${SYNTH_DATA_DIR}" \
    --split "${SPLIT}" \
    --min_votes 1 \
    --no_cache \
    --tag privacy_korean_lora_synth_seed42_to_synth \
    --batch_size "${PRIVACY_EVAL_BSZ}" \
    --max_length "${MAX_LENGTH}" \
    --model_dirs "${PRIVACY_SYNTH_INFERENCE_DIR}"

wait_group

echo
echo "=== Done ==="
echo "Reports: results/ensemble_vote/"
echo "Logs: logs/"
