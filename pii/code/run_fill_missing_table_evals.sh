#!/usr/bin/env bash
# Fill remaining table cells, excluding synthetic-trained -> KDPII full-19.
# Evaluation-only; no training.
set -euo pipefail

cd "$(dirname "$0")"
mkdir -p logs results

KDPII_DATA_DIR="${KDPII_DATA_DIR:-data}"
SYNTH_DATA_DIR="${SYNTH_DATA_DIR:-synthetic}"
SPLIT="${SPLIT:-test}"
EXCLUDED_LABELS="${EXCLUDED_LABELS:-FD_MAJOR,OGG_EDUCATION,QT_AGE,QT_ALIEN_NUMBER}"
MAX_EVAL_JOBS="${MAX_EVAL_JOBS:-3}"
MAX_LENGTH="${MAX_LENGTH:-256}"

PRIVACY_KDPII_DIR="${PRIVACY_KDPII_DIR:-models/privacy_filter_korean_Lora/seed42/inference}"
XLM_KDPII_DIR="${XLM_KDPII_DIR:-models/xlm_roberta_large/seed42}"
KLUE_KDPII_DIR="${KLUE_KDPII_DIR:-models/klue_roberta_large/seed42}"
SKT_DISTILL_KDPII_BASE="${SKT_DISTILL_KDPII_BASE:-models/skt_encoder_distill_crf_gaz_reg}"

has_model() {
  local path="$1"
  [ -f "${path}/config.json" ] && { [ -f "${path}/model.safetensors" ] || [ -f "${path}/pytorch_model.bin" ]; }
}

require_model() {
  local path="$1"
  if ! has_model "${path}"; then
    echo "[ERROR] model missing or incomplete: ${path}" >&2
    exit 1
  fi
}

PIDS=()
NAMES=()

wait_for_slot() {
  while [ "$(jobs -rp | wc -l | tr -d ' ')" -ge "${MAX_EVAL_JOBS}" ]; do
    sleep 5
  done
}

eval_job() {
  local name="$1"
  shift
  wait_for_slot
  local safe_name
  safe_name="$(echo "${name}" | tr ' /' '__' | tr -cd '[:alnum:]_.-')"
  local log="logs/${safe_name}_$(date +%Y%m%d_%H%M%S).log"
  echo "[eval] ${name}"
  echo "       log=${log}"
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
    echo "[ERROR] one or more eval jobs failed; check logs/." >&2
    exit 1
  fi
}

echo "=== fill missing table evals ==="
echo "gpu: $(nvidia-smi --query-gpu=name,memory.total,memory.free --format=csv,noheader | head -1)"
echo "KDPII_DATA_DIR=${KDPII_DATA_DIR} SYNTH_DATA_DIR=${SYNTH_DATA_DIR} SPLIT=${SPLIT}"
echo "MAX_EVAL_JOBS=${MAX_EVAL_JOBS}"
echo

require_model "${PRIVACY_KDPII_DIR}"
require_model "${XLM_KDPII_DIR}"
require_model "${KLUE_KDPII_DIR}"
for seed in 42 43 44; do
  require_model "${SKT_DISTILL_KDPII_BASE}/seed${seed}"
done

echo "=== Phase 1: KDPII-trained -> KDPII common-15 ==="
eval_job "privacy_kdpii_to_kdpii_common15" \
  python3 eval_baseline_ensemble_vote.py \
    --data-dir "${KDPII_DATA_DIR}" --split "${SPLIT}" \
    --min_votes 1 --no_cache \
    --tag "privacy_korean_lora_kdpii_seed42_to_kdpii_common15" \
    --batch_size 64 --max_length "${MAX_LENGTH}" \
    --exclude-labels "${EXCLUDED_LABELS}" \
    --model_dirs "${PRIVACY_KDPII_DIR}"

eval_job "xlm_kdpii_to_kdpii_common15" \
  python3 eval_baseline_ensemble_vote.py \
    --data-dir "${KDPII_DATA_DIR}" --split "${SPLIT}" \
    --min_votes 1 --no_cache \
    --tag "xlm_kdpii_seed42_to_kdpii_common15" \
    --batch_size 32 --max_length "${MAX_LENGTH}" \
    --exclude-labels "${EXCLUDED_LABELS}" \
    --model_dirs "${XLM_KDPII_DIR}"

eval_job "klue_kdpii_to_kdpii_common15" \
  python3 eval_baseline_ensemble_vote.py \
    --data-dir "${KDPII_DATA_DIR}" --split "${SPLIT}" \
    --min_votes 1 --no_cache \
    --tag "klue_kdpii_seed42_to_kdpii_common15" \
    --batch_size 32 --max_length "${MAX_LENGTH}" \
    --exclude-labels "${EXCLUDED_LABELS}" \
    --model_dirs "${KLUE_KDPII_DIR}"

wait_group

echo
echo "=== Phase 2: SKT distill KDPII x3 -> full/common-15/synthetic ==="
SKT_DISTILL_DIRS=(
  "${SKT_DISTILL_KDPII_BASE}/seed42"
  "${SKT_DISTILL_KDPII_BASE}/seed43"
  "${SKT_DISTILL_KDPII_BASE}/seed44"
)

eval_job "skt_distill_kdpii_to_kdpii_full" \
  python3 eval_baseline_ensemble_vote.py \
    --data-dir "${KDPII_DATA_DIR}" --split "${SPLIT}" \
    --min_votes 2 --no_cache \
    --tag "skt_distill_crf_gaz_kdpii_x3_vote_to_kdpii_full" \
    --batch_size 64 --max_length "${MAX_LENGTH}" \
    --model_dirs "${SKT_DISTILL_DIRS[@]}"

eval_job "skt_distill_kdpii_to_kdpii_common15" \
  python3 eval_baseline_ensemble_vote.py \
    --data-dir "${KDPII_DATA_DIR}" --split "${SPLIT}" \
    --min_votes 2 --no_cache \
    --tag "skt_distill_crf_gaz_kdpii_x3_vote_to_kdpii_common15" \
    --batch_size 64 --max_length "${MAX_LENGTH}" \
    --exclude-labels "${EXCLUDED_LABELS}" \
    --model_dirs "${SKT_DISTILL_DIRS[@]}"

eval_job "skt_distill_kdpii_to_synthetic" \
  python3 eval_baseline_ensemble_vote.py \
    --data-dir "${SYNTH_DATA_DIR}" --split "${SPLIT}" \
    --min_votes 2 --no_cache \
    --tag "skt_distill_crf_gaz_kdpii_x3_vote_to_synth" \
    --batch_size 64 --max_length "${MAX_LENGTH}" \
    --model_dirs "${SKT_DISTILL_DIRS[@]}"

wait_group

echo
echo "=== Done ==="
find results/ensemble_vote -type f \( \
  -name "*privacy_korean_lora_kdpii_seed42_to_kdpii_common15*.md" -o \
  -name "*xlm_kdpii_seed42_to_kdpii_common15*.md" -o \
  -name "*klue_kdpii_seed42_to_kdpii_common15*.md" -o \
  -name "*skt_distill_crf_gaz_kdpii_x3_vote_to_*.md" \
\) | sort
