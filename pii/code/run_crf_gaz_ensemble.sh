#!/bin/bash
# CRF+gazetteer 3-seed 학습 + entity voting 앙상블 평가
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p logs

TEACHER_DIR="${TEACHER_DIR:-models/klue_roberta_large/seed42}"
TRAIN_FILE="${TRAIN_FILE:-train_aug.json}"
BASE_OUT="${BASE_OUT:-models/skt_encoder_distill_crf_gaz_reg}"

COMMON_ENV="TEACHER_DIR=${TEACHER_DIR} MODEL_ID=skt/A.X-Encoder-base \
USE_CRF=1 USE_GAZETTEER=1 USE_RDROP=1 USE_FGM=1 \
RDROP_ALPHA=4.0 FGM_EPSILON=1.0 KD_ALPHA=0.5 KD_T=3.0 \
TRAIN_FILE=${TRAIN_FILE} MICRO_BSZ=64 GRAD_ACCUM=1 LR=3e-5 SKIP_EVAL=1"

for SEED in 42 43 44; do
  OUT="${BASE_OUT}/seed${SEED}"
  if [ -f "${OUT}/config.json" ]; then
    echo "[skip] ${OUT} 이미 존재"
    continue
  fi
  LOG="logs/distill_crf_gaz_seed${SEED}_$(date +%Y%m%d_%H%M%S).log"
  echo "[train] seed${SEED} → ${LOG}"
  env ${COMMON_ENV} SEED=${SEED} OUTPUT_DIR=${OUT} \
    nohup python3 distill_train_crf_gaz.py > "${LOG}" 2>&1 &
  echo "  PID=$!"
  wait
done

echo "[eval] entity voting 앙상블..."
python3 eval_baseline_ensemble_vote.py --split test --min_votes 2 --no_cache \
  --tag crf_gaz_reg_x3_vote \
  --model_dirs ${BASE_OUT}/seed42 ${BASE_OUT}/seed43 ${BASE_OUT}/seed44
