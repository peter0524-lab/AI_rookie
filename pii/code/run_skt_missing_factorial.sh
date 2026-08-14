#!/usr/bin/env bash
# Fill missing SKT 0.1B CRF+gaz factorial cells:
#   1) hard x3: KDPII train -> KDPII full/common-15 + synthetic test
#   2) distill x3: KDPII+synthetic train -> KDPII full/common-15 + synthetic test
set -euo pipefail

cd "$(dirname "$0")"
mkdir -p logs results

KDPII_DATA_DIR="${KDPII_DATA_DIR:-data}"
SYNTH_DATA_DIR="${SYNTH_DATA_DIR:-synthetic}"
MIXED_DATA_DIR="${MIXED_DATA_DIR:-mixed/natural_86_14}"
SPLIT="${SPLIT:-test}"
EXCLUDED_LABELS="${EXCLUDED_LABELS:-FD_MAJOR,OGG_EDUCATION,QT_AGE,QT_ALIEN_NUMBER}"

SEEDS="${SEEDS:-42 43 44}"
MAX_TRAIN_JOBS="${MAX_TRAIN_JOBS:-3}"
MAX_EVAL_JOBS="${MAX_EVAL_JOBS:-3}"
MICRO_BSZ="${MICRO_BSZ:-64}"
EPOCHS="${EPOCHS:-5}"
MAX_LENGTH="${MAX_LENGTH:-256}"

HARD_KDPII_BASE="${HARD_KDPII_BASE:-models/skt_encoder_crf_gaz_kdpii_hard}"
DISTILL_MIX_BASE="${DISTILL_MIX_BASE:-models/skt_encoder_distill_crf_gaz_mixed_natural}"
MIX_TEACHER_DIR="${MIX_TEACHER_DIR:-models/klue_roberta_large_mixed_natural/seed42}"

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

require_dir_model() {
  local path="$1"
  if [ ! -f "${path}/config.json" ]; then
    echo "[ERROR] required teacher/base model missing: ${path}" >&2
    exit 1
  fi
}

PIDS=()
NAMES=()

wait_for_slot() {
  local max_jobs="$1"
  while [ "$(jobs -rp | wc -l | tr -d ' ')" -ge "${max_jobs}" ]; do
    sleep 10
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
    echo "[ERROR] one or more jobs failed; check logs/." >&2
    exit 1
  fi
}

train_job() {
  launch_job "train" "${MAX_TRAIN_JOBS}" "$@"
}

eval_job() {
  launch_job "eval" "${MAX_EVAL_JOBS}" "$@"
}

echo "=== SKT missing factorial ==="
echo "gpu: $(nvidia-smi --query-gpu=name,memory.total,memory.free --format=csv,noheader | head -1)"
echo "KDPII_DATA_DIR=${KDPII_DATA_DIR}  SYNTH_DATA_DIR=${SYNTH_DATA_DIR}"
echo "MIXED_DATA_DIR=${MIXED_DATA_DIR}  SPLIT=${SPLIT}"
echo "SEEDS=${SEEDS}  EPOCHS=${EPOCHS}  MICRO_BSZ=${MICRO_BSZ}"
echo "MAX_TRAIN_JOBS=${MAX_TRAIN_JOBS}  MAX_EVAL_JOBS=${MAX_EVAL_JOBS}"
echo "HARD_KDPII_BASE=${HARD_KDPII_BASE}"
echo "DISTILL_MIX_BASE=${DISTILL_MIX_BASE}"
echo "MIX_TEACHER_DIR=${MIX_TEACHER_DIR}"
echo

if [ ! -f "${MIXED_DATA_DIR}/train.json" ] || [ ! -f "${MIXED_DATA_DIR}/valid.json" ]; then
  echo "[build] mixed data missing; rebuilding ${MIXED_DATA_DIR}"
  python3 build_mixed_data.py \
    --kdpii-dir "${KDPII_DATA_DIR}" \
    --synthetic-dir "${SYNTH_DATA_DIR}" \
    --out-dir "${MIXED_DATA_DIR}"
fi

require_dir_model "${MIX_TEACHER_DIR}"

COMMON_ENV=(
  MODEL_ID=skt/A.X-Encoder-base
  USE_CRF=1
  USE_GAZETTEER=1
  USE_RDROP=1
  USE_FGM=1
  RDROP_ALPHA=4.0
  FGM_EPSILON=1.0
  MICRO_BSZ="${MICRO_BSZ}"
  GRAD_ACCUM=1
  EPOCHS="${EPOCHS}"
  LR=3e-5
  SKIP_EVAL=1
)

echo "=== Phase 1: hard x3 on KDPII ==="
for seed in ${SEEDS}; do
  out="${HARD_KDPII_BASE}/seed${seed}"
  if has_model "${out}"; then
    echo "[skip] hard KDPII model exists: ${out}"
  else
    train_job "train_skt_crf_gaz_kdpii_hard_seed${seed}" \
      env "${COMMON_ENV[@]}" \
        DATA_DIR="${KDPII_DATA_DIR}" TRAIN_FILE=train.json VALID_FILE=valid.json \
        USE_KD=0 KD_ALPHA=1.0 SEED="${seed}" OUTPUT_DIR="${out}" \
        RUN_TAG="crf_gaz_kdpii_hard_seed${seed}" \
        python3 distill_train_crf_gaz.py
  fi
done
wait_group

echo
echo "=== Phase 2: distill x3 on KDPII+synthetic ==="
for seed in ${SEEDS}; do
  out="${DISTILL_MIX_BASE}/seed${seed}"
  if has_model "${out}"; then
    echo "[skip] distill mixed model exists: ${out}"
  else
    train_job "train_skt_distill_crf_gaz_mixed_natural_seed${seed}" \
      env "${COMMON_ENV[@]}" \
        DATA_DIR="${MIXED_DATA_DIR}" TRAIN_FILE=train.json VALID_FILE=valid.json \
        USE_KD=1 KD_ALPHA=0.5 KD_T=3.0 TEACHER_DIR="${MIX_TEACHER_DIR}" \
        SEED="${seed}" OUTPUT_DIR="${out}" \
        RUN_TAG="crf_gaz_mixed_natural_distill_seed${seed}" \
        python3 distill_train_crf_gaz.py
  fi
done
wait_group

HARD_DIRS=()
DISTILL_DIRS=()
for seed in ${SEEDS}; do
  require_model "${HARD_KDPII_BASE}/seed${seed}"
  require_model "${DISTILL_MIX_BASE}/seed${seed}"
  HARD_DIRS+=("${HARD_KDPII_BASE}/seed${seed}")
  DISTILL_DIRS+=("${DISTILL_MIX_BASE}/seed${seed}")
done

eval_three() {
  local name="$1"
  local tag="$2"
  shift 2
  local model_dirs=("$@")

  eval_job "${name}_to_kdpii_full" \
    python3 eval_baseline_ensemble_vote.py \
      --data-dir "${KDPII_DATA_DIR}" --split "${SPLIT}" \
      --min_votes 2 --no_cache \
      --tag "${tag}_to_kdpii_full" \
      --batch_size 64 --max_length "${MAX_LENGTH}" \
      --model_dirs "${model_dirs[@]}"

  eval_job "${name}_to_kdpii_common15" \
    python3 eval_baseline_ensemble_vote.py \
      --data-dir "${KDPII_DATA_DIR}" --split "${SPLIT}" \
      --min_votes 2 --no_cache \
      --tag "${tag}_to_kdpii_common15" \
      --batch_size 64 --max_length "${MAX_LENGTH}" \
      --exclude-labels "${EXCLUDED_LABELS}" \
      --model_dirs "${model_dirs[@]}"

  eval_job "${name}_to_synthetic" \
    python3 eval_baseline_ensemble_vote.py \
      --data-dir "${SYNTH_DATA_DIR}" --split "${SPLIT}" \
      --min_votes 2 --no_cache \
      --tag "${tag}_to_synth" \
      --batch_size 64 --max_length "${MAX_LENGTH}" \
      --model_dirs "${model_dirs[@]}"
}

echo
echo "=== Phase 3: evaluate missing cells ==="
eval_three "skt_hard_kdpii" "skt_crf_gaz_kdpii_hard_x3_vote" "${HARD_DIRS[@]}"
eval_three "skt_distill_mixed" "skt_distill_crf_gaz_mixed_natural_x3_vote" "${DISTILL_DIRS[@]}"
wait_group

echo
echo "=== Done ==="
find results/ensemble_vote -type f -name "*skt*kdpii_hard*x3*md" -o -name "*skt_distill_crf_gaz_mixed_natural*x3*md" | sort
