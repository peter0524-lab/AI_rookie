#!/usr/bin/env bash
# Natural mixed training baseline:
#   mixed train = KDPII train + synthetic train
#   mixed valid = KDPII valid + synthetic valid
#
# Trains/evaluates:
#   - OpenAI/privacy Korean LoRA
#   - XLM-RoBERTa-large
#   - KLUE RoBERTa-large
#   - SKT 0.1B CRF+gaz hard recipe (default seed44; set SKT_SEEDS="42 43 44" for vote)
#
# Evaluates each trained model on:
#   - KDPII test full-19
#   - KDPII test common-15 (excludes labels missing from synthetic)
#   - synthetic test
set -euo pipefail

cd "$(dirname "$0")"
mkdir -p logs results

KDPII_DATA_DIR="${KDPII_DATA_DIR:-data}"
SYNTH_DATA_DIR="${SYNTH_DATA_DIR:-synthetic}"
MIXED_DATA_DIR="${MIXED_DATA_DIR:-mixed/natural_86_14}"
SPLIT="${SPLIT:-test}"
EXCLUDED_LABELS="${EXCLUDED_LABELS:-FD_MAJOR,OGG_EDUCATION,QT_AGE,QT_ALIEN_NUMBER}"

SEED="${SEED:-42}"
SKT_SEEDS="${SKT_SEEDS:-44}"

PRIVACY_BASE_MODEL_DIR="${PRIVACY_BASE_MODEL_DIR:-models/privacy_filter_korean}"
PRIVACY_MIX_DIR="${PRIVACY_MIX_DIR:-models/privacy_filter_korean_Lora_mixed_natural/seed${SEED}}"
PRIVACY_MIX_INFERENCE_DIR="${PRIVACY_MIX_INFERENCE_DIR:-${PRIVACY_MIX_DIR}/inference}"
XLM_MIX_DIR="${XLM_MIX_DIR:-models/xlm_roberta_large_mixed_natural/seed${SEED}}"
KLUE_MIX_DIR="${KLUE_MIX_DIR:-models/klue_roberta_large_mixed_natural/seed${SEED}}"
SKT_MIX_BASE="${SKT_MIX_BASE:-models/skt_encoder_crf_gaz_mixed_natural}"

MAX_LENGTH="${MAX_LENGTH:-256}"
MAX_EVAL_JOBS="${MAX_EVAL_JOBS:-auto}"
# Training defaults to sequential for OOM safety. Override only if the GPU is idle and you accept risk.
MAX_TRAIN_JOBS="${MAX_TRAIN_JOBS:-1}"

PRIVACY_TRAIN_BSZ="${PRIVACY_TRAIN_BSZ:-64}"
PRIVACY_EVAL_BSZ="${PRIVACY_EVAL_BSZ:-64}"
XLM_TRAIN_BSZ="${XLM_TRAIN_BSZ:-16}"
XLM_GRAD_ACCUM="${XLM_GRAD_ACCUM:-4}"
XLM_EVAL_BSZ="${XLM_EVAL_BSZ:-32}"
KLUE_TRAIN_BSZ="${KLUE_TRAIN_BSZ:-16}"
KLUE_GRAD_ACCUM="${KLUE_GRAD_ACCUM:-4}"
KLUE_EVAL_BSZ="${KLUE_EVAL_BSZ:-32}"
SKT_TRAIN_BSZ="${SKT_TRAIN_BSZ:-64}"
SKT_EVAL_BSZ="${SKT_EVAL_BSZ:-64}"

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

echo "=== mixed natural baseline batch ==="
echo "gpu: $(nvidia-smi --query-gpu=name,memory.total,memory.free --format=csv,noheader | head -1)"
echo "KDPII_DATA_DIR=${KDPII_DATA_DIR}  SYNTH_DATA_DIR=${SYNTH_DATA_DIR}"
echo "MIXED_DATA_DIR=${MIXED_DATA_DIR}  split=${SPLIT}"
echo "MAX_TRAIN_JOBS=${MAX_TRAIN_JOBS}  MAX_EVAL_JOBS=${MAX_EVAL_JOBS}"
echo "SKT_SEEDS=${SKT_SEEDS}"
echo

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

require_base_config() {
  local path="$1"
  if [ ! -f "${path}/config.json" ]; then
    echo "[ERROR] base model missing config.json: ${path}" >&2
    exit 1
  fi
}

PIDS=()
NAMES=()

wait_for_slot() {
  local max_jobs="$1"
  while [ "$(jobs -rp | wc -l | tr -d ' ')" -ge "${max_jobs}" ]; do
    sleep 5
  done
}

launch_job() {
  local kind="$1"
  local max_jobs="$2"
  local name="$3"
  shift 3
  wait_for_slot "${max_jobs}"
  local safe_name
  safe_name="$(echo "${name}" | tr ' /' '__' | tr -cd '[:alnum:]_.-')"
  local log="logs/${safe_name}_$(date +%Y%m%d_%H%M%S).log"
  echo "[${kind}] ${name}"
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
    echo "[ERROR] One or more jobs failed. Check logs/." >&2
    exit 1
  fi
}

train_job() {
  launch_job "train" "${MAX_TRAIN_JOBS}" "$@"
}

eval_job() {
  launch_job "eval" "${MAX_EVAL_JOBS}" "$@"
}

echo "=== Phase 0: build mixed data ==="
python3 build_mixed_data.py \
  --kdpii-dir "${KDPII_DATA_DIR}" \
  --synthetic-dir "${SYNTH_DATA_DIR}" \
  --out-dir "${MIXED_DATA_DIR}"

require_base_config "${PRIVACY_BASE_MODEL_DIR}"

echo
echo "=== Phase 1: train mixed models ==="

if has_model "${PRIVACY_MIX_INFERENCE_DIR}"; then
  echo "[skip] privacy mixed inference model exists: ${PRIVACY_MIX_INFERENCE_DIR}"
else
  train_job "train_privacy_korean_lora_mixed_natural" \
    env DATA_DIR="${MIXED_DATA_DIR}" TRAIN_FILE=train.json VALID_FILE=valid.json \
      BASE_MODEL_DIR="${PRIVACY_BASE_MODEL_DIR}" \
      OUTPUT_DIR="${PRIVACY_MIX_DIR}" \
      INFERENCE_DIR="${PRIVACY_MIX_INFERENCE_DIR}" \
      SEED="${SEED}" RUN_TAG="privacy_korean_lora_mixed_natural_seed${SEED}" \
      MICRO_BSZ="${PRIVACY_TRAIN_BSZ}" GRAD_ACCUM=1 LR=5e-4 SKIP_EVAL=1 \
      python3 open_ai_privacy_filter_lora_train.py
fi

if has_model "${XLM_MIX_DIR}"; then
  echo "[skip] XLM mixed model exists: ${XLM_MIX_DIR}"
else
  train_job "train_xlm_mixed_natural" \
    env DATA_DIR="${MIXED_DATA_DIR}" TRAIN_FILE=train.json VALID_FILE=valid.json \
      MODEL_ID=FacebookAI/xlm-roberta-large LR=1e-5 SEED="${SEED}" \
      MICRO_BSZ="${XLM_TRAIN_BSZ}" GRAD_ACCUM="${XLM_GRAD_ACCUM}" \
      OUTPUT_DIR="${XLM_MIX_DIR}" SKIP_EVAL=1 RUN_TAG="xlm_mixed_natural_seed${SEED}" \
      python3 train_baseline.py
fi

if has_model "${KLUE_MIX_DIR}"; then
  echo "[skip] KLUE mixed model exists: ${KLUE_MIX_DIR}"
else
  train_job "train_klue_mixed_natural" \
    env DATA_DIR="${MIXED_DATA_DIR}" TRAIN_FILE=train.json VALID_FILE=valid.json \
      MODEL_ID=klue/roberta-large LR=2e-5 SEED="${SEED}" \
      MICRO_BSZ="${KLUE_TRAIN_BSZ}" GRAD_ACCUM="${KLUE_GRAD_ACCUM}" \
      OUTPUT_DIR="${KLUE_MIX_DIR}" SKIP_EVAL=1 RUN_TAG="klue_mixed_natural_seed${SEED}" \
      python3 train_baseline.py
fi

for S in ${SKT_SEEDS}; do
  out="${SKT_MIX_BASE}/seed${S}"
  if has_model "${out}"; then
    echo "[skip] SKT mixed model exists: ${out}"
  else
    train_job "train_skt_crf_gaz_mixed_natural_seed${S}" \
      env DATA_DIR="${MIXED_DATA_DIR}" TRAIN_FILE=train.json VALID_FILE=valid.json \
        MODEL_ID=skt/A.X-Encoder-base USE_KD=0 KD_ALPHA=1.0 \
        USE_CRF=1 USE_GAZETTEER=1 USE_RDROP=1 USE_FGM=1 \
        RDROP_ALPHA=4.0 FGM_EPSILON=1.0 \
        MICRO_BSZ="${SKT_TRAIN_BSZ}" GRAD_ACCUM=1 LR=3e-5 SEED="${S}" \
        OUTPUT_DIR="${out}" SKIP_EVAL=1 RUN_TAG="crf_gaz_mixed_natural_hard_seed${S}" \
        python3 distill_train_crf_gaz.py
  fi
done

wait_group

require_model "${PRIVACY_MIX_INFERENCE_DIR}"
require_model "${XLM_MIX_DIR}"
require_model "${KLUE_MIX_DIR}"

SKT_DIRS=()
for S in ${SKT_SEEDS}; do
  out="${SKT_MIX_BASE}/seed${S}"
  require_model "${out}"
  SKT_DIRS+=("${out}")
done
if [ "${#SKT_DIRS[@]}" -gt 1 ]; then
  SKT_MIN_VOTES=2
  SKT_TAG="skt_crf_gaz_mixed_natural_x${#SKT_DIRS[@]}_vote"
else
  SKT_MIN_VOTES=1
  SKT_TAG="skt_crf_gaz_mixed_natural_seed${SKT_SEEDS// /_}"
fi

echo
echo "=== Phase 2: evaluate mixed models ==="

eval_three() {
  local name="$1"
  local tag="$2"
  local bsz="$3"
  local min_votes="$4"
  shift 4
  local model_dirs=("$@")

  eval_job "${name}_to_kdpii_full" \
    python3 eval_baseline_ensemble_vote.py \
      --data-dir "${KDPII_DATA_DIR}" --split "${SPLIT}" \
      --min_votes "${min_votes}" --no_cache \
      --tag "${tag}_to_kdpii_full" \
      --batch_size "${bsz}" --max_length "${MAX_LENGTH}" \
      --model_dirs "${model_dirs[@]}"

  eval_job "${name}_to_kdpii_common15" \
    python3 eval_baseline_ensemble_vote.py \
      --data-dir "${KDPII_DATA_DIR}" --split "${SPLIT}" \
      --min_votes "${min_votes}" --no_cache \
      --tag "${tag}_to_kdpii_common15" \
      --batch_size "${bsz}" --max_length "${MAX_LENGTH}" \
      --exclude-labels "${EXCLUDED_LABELS}" \
      --model_dirs "${model_dirs[@]}"

  eval_job "${name}_to_synthetic" \
    python3 eval_baseline_ensemble_vote.py \
      --data-dir "${SYNTH_DATA_DIR}" --split "${SPLIT}" \
      --min_votes "${min_votes}" --no_cache \
      --tag "${tag}_to_synth" \
      --batch_size "${bsz}" --max_length "${MAX_LENGTH}" \
      --model_dirs "${model_dirs[@]}"
}

eval_three "privacy_mixed" "privacy_korean_lora_mixed_natural_seed${SEED}" "${PRIVACY_EVAL_BSZ}" 1 \
  "${PRIVACY_MIX_INFERENCE_DIR}"
eval_three "xlm_mixed" "xlm_mixed_natural_seed${SEED}" "${XLM_EVAL_BSZ}" 1 \
  "${XLM_MIX_DIR}"
eval_three "klue_mixed" "klue_mixed_natural_seed${SEED}" "${KLUE_EVAL_BSZ}" 1 \
  "${KLUE_MIX_DIR}"
eval_three "skt_mixed" "${SKT_TAG}" "${SKT_EVAL_BSZ}" "${SKT_MIN_VOTES}" \
  "${SKT_DIRS[@]}"

wait_group

echo
echo "=== Done ==="
echo "Mixed data: ${MIXED_DATA_DIR}"
echo "Latest reports:"
ls -t results/ensemble_vote/*mixed_natural*.md 2>/dev/null | head -40
