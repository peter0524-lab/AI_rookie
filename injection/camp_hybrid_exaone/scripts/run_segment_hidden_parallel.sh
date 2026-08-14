#!/usr/bin/env bash
# segment-hidden(head/mid/tail) 8도메인 검증 — 병렬판.
# GPU가 한 프로세스로는 30~40%밖에 안 써서(9.5GB/80GB) 도메인 추출을 동시에 여러 개 돌린다.
set -uo pipefail
cd "$(dirname "$0")/.."
PY=.venv/bin/python
DOMAINS=(cloud coding finance messaging project shopping social_media web)
PARALLEL=4
LOGDIR=logs/segment_parallel
mkdir -p "${LOGDIR}"

echo "================================================================"
echo "[stage-1] 8도메인 추출 — ${PARALLEL}개씩 동시 실행"
echo "================================================================"
i=0
for D in "${DOMAINS[@]}"; do
    OUT_DUMP="dump_hybrid_seg_${D}"
    (
        if [[ ! -f "${OUT_DUMP}/train_${D}_meta.json" ]]; then
            ${PY} src/extract_hybrid.py --model-key exaone-1.2b --trust-remote-code \
                --out "${OUT_DUMP}" --domains "${D}" --splits train test --max-pairs 1024 --hs-segments 3 \
                > "${LOGDIR}/extract_${D}.log" 2>&1
            echo "[extract-done] ${D} exit=$?"
        else
            echo "[extract-skip] ${D} 이미 존재"
        fi
    ) &
    i=$((i + 1))
    if (( i % PARALLEL == 0 )); then
        wait
    fi
done
wait
echo "[stage-1-complete] 추출 전체 완료"

echo "================================================================"
echo "[stage-2] 8도메인 학습(attn/hidden/hybrid) — ${PARALLEL}개씩 동시 실행"
echo "  (주의: train_hybrid.py는 도메인 전체를 float32로 GPU에 직접 올림 — 도메인당 최대 ~16GB,"
echo "   8개를 한꺼번에 돌리면 125GB로 OOM나서 extraction과 동일하게 스로틀링함)"
echo "================================================================"
i=0
for D in "${DOMAINS[@]}"; do
    OUT_DUMP="dump_hybrid_seg_${D}"
    OUT_RES="results_hybrid_seg_${D}"
    (
        ${PY} src/train_hybrid.py --features "${OUT_DUMP}" --variant all \
            --lr 0.01 --batch-size 16 --out "${OUT_RES}" \
            > "${LOGDIR}/train_${D}.log" 2>&1
        echo "[train-done] ${D} exit=$?"
    ) &
    i=$((i + 1))
    if (( i % PARALLEL == 0 )); then
        wait
    fi
done
wait
echo "[stage-2-complete] 학습 전체 완료"

echo "================================================================"
echo "[stage-3] pooled 학습 (8도메인 전부 필요 — 단독 실행)"
echo "================================================================"
${PY} src/train_pooled_from_dumps.py --dumps-prefix dump_hybrid_seg_ \
    --domains "${DOMAINS[@]}" --out results_hybrid_pooled_seg \
    > "${LOGDIR}/pooled.log" 2>&1
echo "[stage-3-complete] pooled 완료"

echo "================================================================"
echo "[all-complete] segment-hidden 8도메인+pooled 검증 완료 (병렬판)"
echo "================================================================"
