#!/usr/bin/env bash
# KLUE synthetic 모델 평가 (합성 test + 대회 test 전이)
set -euo pipefail
cd /data/team/hwan
MODEL=models/klue_roberta_large_synthetic/seed42

echo "=== synthetic test ==="
python3 eval_baseline.py --split test --data-dir synthetic \
  --model_dir "$MODEL" --tag synth_test 2>&1 | grep -E "Micro F1|TP=|^\[test\]"

echo ""
echo "=== competition test (전이) ==="
python3 eval_baseline.py --split test --data-dir data \
  --model_dir "$MODEL" --tag comp_test 2>&1 | grep -E "Micro F1|TP=|^\[test\]"
