#!/usr/bin/env bash
# 합성 PII 데이터셋(synthetic/) 학습 + 벤치마크 평가
set -euo pipefail
cd /data/team/hwan
mkdir -p logs results/synthetic_benchmark

DATA_DIR=synthetic
SPLIT=test
TAG=synth_test

echo "=== [1/3] KLUE RoBERTa-large on synthetic ${SPLIT} ==="
python3 eval_baseline.py \
  --split "$SPLIT" --data-dir "$DATA_DIR" \
  --model_dir models/klue_roberta_large/seed42 \
  --tag "${TAG}_klue" 2>&1 | tee "logs/eval_${TAG}_klue.log" | grep -E "Micro F1|TP=|^\[${SPLIT}\]"

echo ""
echo "=== [2/3] SKT crf_gaz 3-seed vote (최고) on synthetic ${SPLIT} ==="
python3 eval_baseline_ensemble_vote.py \
  --split "$SPLIT" --data-dir "$DATA_DIR" --no_cache \
  --min_votes 2 --tag "${TAG}_crf_gaz_x3" \
  --model_dirs \
    models/skt_encoder_distill_crf_gaz_reg/seed42 \
    models/skt_encoder_distill_crf_gaz_reg/seed43 \
    models/skt_encoder_distill_crf_gaz_reg/seed44 \
  2>&1 | tee "logs/eval_${TAG}_crf_gaz.log" | grep -E "Micro F1|TP=|VOTE|^\[${SPLIT}"

echo ""
echo "=== [3/3] Synthetic-only SKT on synthetic ${SPLIT} ==="
if [[ -d models/skt_encoder_synthetic/seed42 ]]; then
  python3 eval_baseline.py \
    --split "$SPLIT" --data-dir "$DATA_DIR" \
    --model_dir models/skt_encoder_synthetic/seed42 \
    --tag "${TAG}_skt_synth" 2>&1 | tee "logs/eval_${TAG}_skt_synth.log" | grep -E "Micro F1|TP=|^\[${SPLIT}\]"
else
  echo "SKIP: models/skt_encoder_synthetic/seed42 없음 — 학습 완료 후 재실행"
fi

echo ""
echo "=== done ==="
