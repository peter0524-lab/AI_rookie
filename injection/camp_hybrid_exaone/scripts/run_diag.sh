#!/usr/bin/env bash
# 진단 전체: 추출(GPU) → 분석(CPU). 서버에서 이 한 줄이면 끝.
#
#   bash scripts/run_diag.sh
#
# 환경변수(옵션):
#   MODEL_KEY   backend 모델 (기본 qwen; 비 gated라 HF_TOKEN 불필요)
#   PER_CLASS   (split,domain,label)별 샘플 수 (기본 100 → 8도메인×3클래스×100 ≈ 2400)
#   SPLITS      추출 split (기본 "train")
#   DOMAINS     특정 도메인만 (기본 전체)
#   MAX_SEQ_LEN attention 추출 최대 토큰 (기본 4096)
#   OUT_DUMP / OUT_RES  출력 폴더 (기본 dump / results)
set -euo pipefail
cd "$(dirname "$0")/.."
[ -f scripts/setup_env.sh ] && source scripts/setup_env.sh   # HF_TOKEN (gated 모델 쓸 때만 필요)

MODEL_KEY="${MODEL_KEY:-qwen}"
PER_CLASS="${PER_CLASS:-100}"
SPLITS="${SPLITS:-train}"
MAX_SEQ_LEN="${MAX_SEQ_LEN:-4096}"
OUT_DUMP="${OUT_DUMP:-dump}"
OUT_RES="${OUT_RES:-results}"
DOM_FLAG=""
[ -n "${DOMAINS:-}" ] && DOM_FLAG="--domains ${DOMAINS}"

echo "############################################################"
echo "# 진단  model=$MODEL_KEY  per_class=$PER_CLASS  splits=$SPLITS"
echo "#   GPU(CUDA_VISIBLE_DEVICES)=${CUDA_VISIBLE_DEVICES:-unset}"
echo "############################################################"

echo "=== [1/2] 추출 (GPU) ==="
python src/diag_extract.py \
    --model-key "$MODEL_KEY" --out "$OUT_DUMP" \
    --splits $SPLITS --per-class "$PER_CLASS" \
    --max-seq-len "$MAX_SEQ_LEN" $DOM_FLAG

echo "=== [2/2] 분석 (CPU) ==="
python src/diag_analyze.py --dump "$OUT_DUMP" --out "$OUT_RES"

echo ""
echo "=== 완료 ==="
echo "리포트:  $OUT_RES/diag_report.md"
echo "플롯:    $OUT_RES/g_position_profile.png , $OUT_RES/head_auc.png"
