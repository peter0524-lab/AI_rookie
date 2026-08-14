#!/usr/bin/env bash
#
# SK+Kiwi 시드 앙상블 한 번에 실행
#   1) SEEDS 각 시드로 train.py 학습 (시드별 디렉토리에 best 저장, 단일 eval 생략)
#   2) 학습된 모델들을 eval_ensemble.py 로 soft-voting 앙상블 평가
#
# 사용:
#   bash run_sk_ensemble.sh
#   SEEDS="42 43 44 45 46" bash run_sk_ensemble.sh        # 시드 개수 변경
#   nohup bash run_sk_ensemble.sh > logs/ensemble_all.log 2>&1 &   # 백그라운드
#
set -euo pipefail
cd "$(dirname "$0")"

SEEDS="${SEEDS:-42 43 44}"
MODEL_ID="${MODEL_ID:-skt/A.X-Encoder-base}"
ENS_DIR="${ENS_DIR:-models/skt_encoder_ens}"
SPLIT="${SPLIT:-test}"

mkdir -p logs "$ENS_DIR"

DIRS=()
for S in $SEEDS; do
  OUT="$ENS_DIR/seed$S"
  echo "=================================================================="
  echo "[Train] seed=$S  →  $OUT"
  echo "=================================================================="
  OUTPUT_DIR="$OUT" MODEL_ID="$MODEL_ID" SEED="$S" SKIP_EVAL=1 \
    python3 train.py
  DIRS+=("$OUT")
done

echo "=================================================================="
echo "[Ensemble Eval] ${DIRS[*]}"
echo "=================================================================="
python3 eval_ensemble.py --split "$SPLIT" --model_dirs "${DIRS[@]}"

echo "완료. results/skt_encoder_ens/ 의 eval_ensemble_*.md 확인."
