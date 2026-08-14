#!/usr/bin/env bash
# 합성 데이터만으로 SKT 0.1B PII NER 학습
set -euo pipefail
cd /data/team/hwan
mkdir -p logs

export DATA_DIR=synthetic
export TRAIN_FILE=train.json
export VALID_FILE=valid.json
export MODEL_ID=skt/A.X-Encoder-base
export LR=3e-5
export SEED=42
export MICRO_BSZ=64
export GRAD_ACCUM=1
export OUTPUT_DIR=models/skt_encoder_synthetic/seed42
export SKIP_EVAL=1

LOG="logs/train_synth_$(date +%Y%m%d_%H%M%S).log"
echo "학습 시작 → $OUTPUT_DIR"
echo "로그: $LOG"

nohup python3 train_baseline.py > "$LOG" 2>&1 &
echo "PID: $!"
echo "tail -f $LOG"
