#!/usr/bin/env bash
# KLUE RoBERTa-large — 합성 데이터(synthetic/) 전용 학습 + synthetic test 평가
set -euo pipefail
cd /data/team/hwan
mkdir -p logs

export DATA_DIR=synthetic
export TRAIN_FILE=train.json
export VALID_FILE=valid.json
export MODEL_ID=klue/roberta-large
export LR=2e-5
export SEED=42
export MICRO_BSZ=16
export GRAD_ACCUM=4
export OUTPUT_DIR=models/klue_roberta_large_synthetic/seed42
export RUN_TAG=synth_seed42

LOG="logs/train_klue_synth_$(date +%Y%m%d_%H%M%S).log"
echo "KLUE 합성 학습 → $OUTPUT_DIR"
echo "로그: $LOG"

nohup python3 train_baseline.py > "$LOG" 2>&1 &
echo "PID: $!"
echo "tail -f $LOG"
