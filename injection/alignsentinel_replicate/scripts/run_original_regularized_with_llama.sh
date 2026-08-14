#!/usr/bin/env bash
# Original full-attention Enc-first/Avg-first regularized sweep, including Meta Llama.
# Use a separate RUN_TAG to keep old results and new 32k results apart.
set -euo pipefail
cd "$(dirname "$0")/.."

RUN_TAG="${RUN_TAG:-32k_llama_$(date +%Y%m%d_%H%M%S)}"

export TRAIN_DATA="${TRAIN_DATA:-data/full_train.json}"
export TEST_DATA="${TEST_DATA:-data/full_test.json}"
export FEATURES_ROOT="${FEATURES_ROOT:-features_${RUN_TAG}}"
export RESULTS_ROOT="${RESULTS_ROOT:-results_${RUN_TAG}}"
export MODELS_ROOT="${MODELS_ROOT:-models_${RUN_TAG}}"
export DETECTOR="${DETECTOR:-regularized}"
export SKIP_DONE="${SKIP_DONE:-1}"
export CONTINUE_ON_ERROR="${CONTINUE_ON_ERROR:-1}"
export CLEAN_FEATURES_AFTER="${CLEAN_FEATURES_AFTER:-1}"

export MODEL_IDS_TEXT="${MODEL_IDS_TEXT:-skt/A.X-4.0-Light LGAI-EXAONE/EXAONE-Deep-7.8B NCSOFT/Llama-VARCO-8B-Instruct upstage/SOLAR-10.7B-Instruct-v1.0 Qwen/Qwen3-8B mistralai/Mistral-7B-Instruct-v0.3 meta-llama/Llama-3.1-8B-Instruct}"

echo "[run] tag=${RUN_TAG}"
echo "[run] data=${TRAIN_DATA} ${TEST_DATA}"
echo "[run] features=${FEATURES_ROOT}"
echo "[run] results=${RESULTS_ROOT}"
echo "[run] models=${MODELS_ROOT}"
echo "[run] clean_features_after=${CLEAN_FEATURES_AFTER}"
echo "[run] model_ids=${MODEL_IDS_TEXT}"

bash scripts/run_sequential_backends.sh
