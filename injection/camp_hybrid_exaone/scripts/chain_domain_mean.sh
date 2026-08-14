#!/usr/bin/env bash
set -uo pipefail
cd /data/team/ho/injection_diag

while ! grep -qE "cross-all-complete" logs/cross_domain_run.log 2>/dev/null; do
    if ! pgrep -f "run_cross_domain.sh" > /dev/null; then
        echo "[chain] cross_domain 프로세스가 cross-all-complete 없이 종료됨 — 확인 필요"
        break
    fi
    sleep 15
done
echo "[chain] cross-domain 완료 확인, domain-mean(8개 개별) 학습 시작 (안전한 GPU-resident 스크립트 재사용, 순차 실행)"

DOMAINS="cloud coding finance messaging project shopping social_media web"
for D in ${DOMAINS}; do
    echo "================================================================"
    echo "[domain-mean-start] ${D}"
    echo "================================================================"
    .venv/bin/python src/train_pooled_from_dumps.py --dumps-prefix dump_hybrid_seg_ \
        --domains ${D} --out results_domain_seg_${D}
    echo "[domain-mean-done] ${D}"
done
echo "[domain-mean-all-complete]"
