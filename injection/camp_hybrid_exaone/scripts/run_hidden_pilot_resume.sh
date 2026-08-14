#!/usr/bin/env bash
# 재개: shopping은 feature 이미 있으니 학습만 재실행(메모리 누수 fix 적용), web은 처음부터.
set -euo pipefail
cd "$(dirname "$0")/.."
PY=.venv/bin/python

echo "================================================================"
echo "[domain-start] shopping (재학습, features 재사용)"
echo "================================================================"
${PY} src/train_hybrid.py --features dump_hybrid_shopping --variant all \
    --lr 0.01 --batch-size 16 --out results_hybrid_shopping
echo "[domain-done] shopping"

echo "================================================================"
echo "[domain-start] web"
echo "================================================================"
${PY} src/extract_hybrid.py --model-key exaone-1.2b --trust-remote-code \
    --out dump_hybrid_web --domains web --splits train test --max-pairs 1024
${PY} src/train_hybrid.py --features dump_hybrid_web --variant all \
    --lr 0.01 --batch-size 16 --out results_hybrid_web
echo "[domain-done] web"

echo "================================================================"
echo "[pilot-complete] resume run finished"
echo "================================================================"
