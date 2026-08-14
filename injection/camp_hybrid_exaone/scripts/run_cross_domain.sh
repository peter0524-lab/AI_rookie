#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
PY=.venv/bin/python

echo "================================================================"
echo "[cross-start] A2B"
echo "================================================================"
${PY} src/train_cross_from_dumps.py --cross A2B --out results_cross
echo "[cross-done] A2B"

echo "================================================================"
echo "[cross-start] B2A"
echo "================================================================"
${PY} src/train_cross_from_dumps.py --cross B2A --out results_cross
echo "[cross-done] B2A"

echo "================================================================"
echo "[cross-all-complete]"
echo "================================================================"
