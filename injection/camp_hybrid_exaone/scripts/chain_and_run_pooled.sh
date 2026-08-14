#!/usr/bin/env bash
set -uo pipefail
cd /data/team/ho/injection_diag

# 1) 나머지 4도메인 파이프라인이 끝날 때까지 대기
while ! grep -qE "pilot-complete" logs/hidden_pilot_remaining4.log 2>/dev/null; do
    if ! pgrep -f "run_hidden_pilot_remaining4.sh" > /dev/null; then
        echo "[chain] remaining4 프로세스가 pilot-complete 없이 종료됨 — 확인 필요" 
        break
    fi
    sleep 15
done
echo "[chain] remaining4 완료 확인, pooled 학습 시작"

# 2) 8도메인 pooled 본실행 (K=1024, hwan 하이퍼파라미터 그대로, epochs=200 patience=25)
.venv/bin/python src/train_pooled_from_dumps.py \
    --domains cloud coding finance messaging project shopping social_media web \
    --out results_hybrid_pooled_8domain
echo "[chain-complete] pooled 학습 완료"
