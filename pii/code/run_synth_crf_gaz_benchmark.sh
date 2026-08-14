#!/usr/bin/env bash
# 합성 데이터 crf_gaz 벤치마크:
#   A) hard-only (USE_KD=0) seed 42/43/44 + vote×3
#   B) distill (KLUE synthetic teacher) seed 42/43/44 + vote×3
#
# GPU 1장 기준 MAX_JOBS 로 동시 학습 수 제한 (기본 3).
#   - hard-only 3개 동시 → distill 3개 동시 (2 wave)
#   - MAX_JOBS=6 + MICRO_BSZ=32 로 6개 동시 시도 가능 (OOM 시 MAX_JOBS 낮추기)
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p logs

MAX_JOBS="${MAX_JOBS:-3}"
MICRO_BSZ="${MICRO_BSZ:-64}"
DATA_DIR="${DATA_DIR:-synthetic}"
TRAIN_FILE="${TRAIN_FILE:-train.json}"
VALID_FILE="${VALID_FILE:-valid.json}"
TEACHER_DIR="${TEACHER_DIR:-models/klue_roberta_large_synthetic/seed42}"
BASE_HARD="${BASE_HARD:-models/skt_encoder_crf_gaz_synthetic}"
BASE_DISTILL="${BASE_DISTILL:-models/skt_encoder_distill_crf_gaz_synthetic}"

COMMON="DATA_DIR=${DATA_DIR} TRAIN_FILE=${TRAIN_FILE} VALID_FILE=${VALID_FILE} \
MODEL_ID=skt/A.X-Encoder-base USE_CRF=1 USE_GAZETTEER=1 \
USE_RDROP=1 USE_FGM=1 RDROP_ALPHA=4.0 FGM_EPSILON=1.0 \
MICRO_BSZ=${MICRO_BSZ} GRAD_ACCUM=1 LR=3e-5 SKIP_EVAL=1"

wait_for_slot() {
  while [ "$(jobs -rp | wc -l | tr -d ' ')" -ge "${MAX_JOBS}" ]; do
    sleep 20
  done
}

launch_train() {
  local mode="$1" seed="$2" out="$3"
  if [ -f "${out}/pytorch_model.bin" ] || [ -f "${out}/model.safetensors" ]; then
    echo "[skip] ${out} 이미 존재"
    return 0
  fi
  wait_for_slot
  local log="logs/synth_${mode}_seed${seed}_$(date +%Y%m%d_%H%M%S).log"
  echo "[train] ${mode} seed${seed} → ${out}  log=${log}"
  if [ "${mode}" = "hard" ]; then
    env ${COMMON} USE_KD=0 KD_ALPHA=1.0 SEED=${seed} OUTPUT_DIR=${out} \
      RUN_TAG="crf_gaz_synth_hard_seed${seed}" \
      nohup python3 distill_train_crf_gaz.py > "${log}" 2>&1 &
  else
    env ${COMMON} USE_KD=1 KD_ALPHA=0.5 KD_T=3.0 TEACHER_DIR=${TEACHER_DIR} \
      SEED=${seed} OUTPUT_DIR=${out} \
      RUN_TAG="crf_gaz_synth_distill_seed${seed}" \
      nohup python3 distill_train_crf_gaz.py > "${log}" 2>&1 &
  fi
  echo "  PID=$!"
}

echo "=== 합성 crf_gaz 벤치마크 시작 (MAX_JOBS=${MAX_JOBS}, MICRO_BSZ=${MICRO_BSZ}) ==="

for SEED in 42 43 44; do
  launch_train hard "${SEED}" "${BASE_HARD}/seed${SEED}"
done
for SEED in 42 43 44; do
  launch_train distill "${SEED}" "${BASE_DISTILL}/seed${SEED}"
done

echo "=== 6개 학습 job 대기 중... ==="
wait
echo "=== 학습 완료 — per-seed test 평가 ==="

for SEED in 42 43 44; do
  python3 eval_crf_gaz.py --data-dir "${DATA_DIR}" --split test \
    --model_dir "${BASE_HARD}/seed${SEED}" --tag "crf_gaz_synth_hard_seed${SEED}" || true
done
for SEED in 42 43 44; do
  python3 eval_crf_gaz.py --data-dir "${DATA_DIR}" --split test \
    --model_dir "${BASE_DISTILL}/seed${SEED}" --tag "crf_gaz_synth_distill_seed${SEED}" || true
done

echo "=== entity voting 앙상블 ==="
python3 eval_baseline_ensemble_vote.py --data-dir "${DATA_DIR}" --split test \
  --min_votes 2 --no_cache --tag crf_gaz_synth_hard_x3_vote \
  --model_dirs "${BASE_HARD}/seed42" "${BASE_HARD}/seed43" "${BASE_HARD}/seed44"

python3 eval_baseline_ensemble_vote.py --data-dir "${DATA_DIR}" --split test \
  --min_votes 2 --no_cache --tag crf_gaz_synth_distill_x3_vote \
  --model_dirs "${BASE_DISTILL}/seed42" "${BASE_DISTILL}/seed43" "${BASE_DISTILL}/seed44"

echo "=== 완료 ==="
