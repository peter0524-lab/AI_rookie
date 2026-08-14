#!/usr/bin/env bash
# 1순위 추천 검증: tool_response를 head/mid/tail 3구간으로 나눠 hidden을 위치별로 뽑고,
# risk(0.25*FPR+0.75*FNR) 기준으로 체크포인트 선택 + 임계값 보정까지 적용해서
# 8도메인 개별 + pooled를 전부 다시 확인한다.
set -euo pipefail
cd "$(dirname "$0")/.."
PY=.venv/bin/python
DOMAINS="cloud coding finance messaging project shopping social_media web"

for D in ${DOMAINS}; do
    echo "================================================================"
    echo "[domain-start] ${D}"
    echo "================================================================"
    OUT_DUMP="dump_hybrid_seg_${D}"
    OUT_RES="results_hybrid_seg_${D}"
    if [[ ! -f "${OUT_DUMP}/train_${D}_meta.json" ]]; then
        ${PY} src/extract_hybrid.py --model-key exaone-1.2b --trust-remote-code \
            --out "${OUT_DUMP}" --domains "${D}" --splits train test --max-pairs 1024 --hs-segments 3
    else
        echo "[skip-extract] ${OUT_DUMP} 이미 존재"
    fi
    ${PY} src/train_hybrid.py --features "${OUT_DUMP}" --variant all \
        --lr 0.01 --batch-size 16 --out "${OUT_RES}"
    echo "[domain-done] ${D}"
done

echo "================================================================"
echo "[pooled-start]"
echo "================================================================"
${PY} src/train_pooled_from_dumps.py --dumps-prefix dump_hybrid_seg_ \
    --domains ${DOMAINS} --out results_hybrid_pooled_seg
echo "[pooled-done]"

echo "================================================================"
echo "[all-complete] segment-hidden 8도메인+pooled 검증 완료"
echo "================================================================"
