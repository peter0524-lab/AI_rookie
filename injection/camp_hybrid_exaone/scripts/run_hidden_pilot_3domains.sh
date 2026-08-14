#!/usr/bin/env bash
# 3-domain pilot: baseline attn(K=1024, hwan hyperparams: lr=0.01 batch=16) vs
# attn+hidden hybrid, per domain (coding 제외, 다른 3개 도메인).
set -euo pipefail
cd "$(dirname "$0")/.."

DOMAINS="finance shopping web"
PY=.venv/bin/python

for D in ${DOMAINS}; do
    echo "================================================================"
    echo "[domain-start] ${D}"
    echo "================================================================"
    OUT_DUMP="dump_hybrid_${D}"
    OUT_RES="results_hybrid_${D}"
    if [[ ! -f "${OUT_DUMP}/train_${D}_meta.json" ]]; then
        ${PY} src/extract_hybrid.py --model-key exaone-1.2b --trust-remote-code \
            --out "${OUT_DUMP}" --domains "${D}" --splits train test --max-pairs 1024
    else
        echo "[skip-extract] ${OUT_DUMP} 이미 존재"
    fi
    ${PY} src/train_hybrid.py --features "${OUT_DUMP}" --variant all \
        --lr 0.01 --batch-size 16 --out "${OUT_RES}"
    echo "[domain-done] ${D}"
done

echo "================================================================"
echo "[pilot-complete] domains=${DOMAINS}"
echo "================================================================"
