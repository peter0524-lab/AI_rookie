#!/usr/bin/env bash
# AlignSentinel 재현 전체 파이프라인 (A100 서버용).
# 사용법: bash scripts/run_all.sh
# 단계별 재실행: 이미 만들어진 features/*_meta.json, results/*.json 은 건너뛰지 않으므로
# 부분 재실행이 필요하면 해당 산출물만 지우고 개별 명령을 실행할 것.
set -euo pipefail
cd "$(dirname "$0")/.."

MODEL_ID="${MODEL_ID:-skt/A.X-4.0-Light}"

echo "=== [1/5] attention 특징 추출 (${MODEL_ID}, 16,000 forward passes — 가장 오래 걸림) ==="
python src/extract_features.py \
    --data data/full_train.json data/full_test.json \
    --out features --model "${MODEL_ID}" --max-pairs 1024

echo "=== [2/5] Avg-first 학습+평가 (8개 도메인) ==="
python src/train_detector.py --features features --variant avg --domains all

echo "=== [3/5] Enc-first 학습+평가 (8개 도메인) ==="
python src/train_detector.py --features features --variant enc --domains all

echo "=== [3.3/5] Pooled — 8개 도메인 통합 학습/평가 ==="
python src/train_detector.py --features features --variant avg --pooled
python src/train_detector.py --features features --variant enc --pooled

echo "=== [3.6/5] Cross-domain generalization (논문 Table 3: A→B, B→A) ==="
python src/train_detector.py --features features --variant avg --cross A2B
python src/train_detector.py --features features --variant enc --cross A2B
python src/train_detector.py --features features --variant avg --cross B2A
python src/train_detector.py --features features --variant enc --cross B2A

echo "=== [4/5] 베이스라인 ==="
python src/baselines/baseline_chen.py --data data/full_train.json data/full_test.json
python src/baselines/baseline_promptguard.py --data data/full_test.json \
    || echo "[warn] Prompt-Guard-2 실패 — gated model 접근 승인 + huggingface-cli login 필요"

echo "=== [5/5] 결과 집계 (상세 리포트) ==="
python src/aggregate_results.py --results results --out results/summary.md \
    --features features --data data/full_test.json
echo "완료: results/summary.md (+ results/summary_full.json)"
