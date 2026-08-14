#!/usr/bin/env bash
# 여러 backend LLM의 attention feature + detector 성능을 같은 조건으로 비교한다.
# 기본 후보: SKT 7B, LG 7.8B, NC 8B, Upstage 10.7B.
# KT Mi:dm은 현재 공개 주력 모델이 2B/12B라 기본 7~8B 비교군에서는 제외했다.
# 필요하면 MODEL_IDS_TEXT에 K-intelligence/Midm-2.0-Mini-Instruct 등을 직접 넣는다.
#
# 빠른 점검:
#   LIMIT_PER_GROUP=4 EPOCHS=3 MAX_PAIRS=128 bash scripts/run_model_sweep.sh
#
# 후보를 직접 지정:
#   MODEL_IDS_TEXT="skt/A.X-4.0-Light NCSOFT/Llama-VARCO-8B-Instruct" bash scripts/run_model_sweep.sh
set -euo pipefail
cd "$(dirname "$0")/.."

CACHE_ROOT="${CACHE_ROOT:-}"
if [[ -z "${CACHE_ROOT}" ]]; then
    if [[ -d "/data/team/hwan" ]]; then
        CACHE_ROOT="/data/team/hwan/.cache"
    else
        CACHE_ROOT=".cache"
    fi
fi
export HF_HOME="${HF_HOME:-${CACHE_ROOT}/huggingface}"
export HF_HUB_CACHE="${HF_HUB_CACHE:-${HF_HOME}/hub}"
export HF_MODULES_CACHE="${HF_MODULES_CACHE:-${HF_HOME}/modules}"
export TRANSFORMERS_CACHE="${TRANSFORMERS_CACHE:-${HF_HOME}/hub}"
export TORCH_HOME="${TORCH_HOME:-${CACHE_ROOT}/torch}"
mkdir -p "${HF_HOME}" "${HF_HUB_CACHE}" "${HF_MODULES_CACHE}" "${TORCH_HOME}"

if [[ -n "${MODEL_IDS_TEXT:-}" ]]; then
    # shellcheck disable=SC2206
    MODEL_IDS=(${MODEL_IDS_TEXT})
else
    MODEL_IDS=(
        "skt/A.X-4.0-Light"
        "LGAI-EXAONE/EXAONE-Deep-7.8B"
        "NCSOFT/Llama-VARCO-8B-Instruct"
        "upstage/SOLAR-10.7B-Instruct-v1.0"
    )
fi

MAX_PAIRS="${MAX_PAIRS:-1024}"
EPOCHS="${EPOCHS:-200}"
DETECTOR="${DETECTOR:-regularized}"
DROPOUT="${DROPOUT:-0.2}"
WEIGHT_DECAY="${WEIGHT_DECAY:-0.0001}"
VAL_RATIO="${VAL_RATIO:-0.15}"
PATIENCE="${PATIENCE:-25}"
TRUST_REMOTE_CODE="${TRUST_REMOTE_CODE:-1}"
RUN_BASELINES="${RUN_BASELINES:-0}"
TOOL_MESSAGE_MODE="${TOOL_MESSAGE_MODE:-auto}"
PYTHON_BIN="${PYTHON_BIN:-python}"
TRAIN_DATA="${TRAIN_DATA:-data/full_train.json}"
TEST_DATA="${TEST_DATA:-data/full_test.json}"
FEATURES_ROOT="${FEATURES_ROOT:-features}"
RESULTS_ROOT="${RESULTS_ROOT:-results}"
MODELS_ROOT="${MODELS_ROOT:-models}"
CLEAN_FEATURES_AFTER="${CLEAN_FEATURES_AFTER:-0}"

slugify() {
    printf "%s" "$1" | tr '/:.' '___' | tr -c 'A-Za-z0-9_-' '_'
}

build_extract_args() {
    EXTRACT_ARGS=(
        --data "${TRAIN_DATA}" "${TEST_DATA}"
        --max-pairs "${MAX_PAIRS}"
        --tool-message-mode "${TOOL_MESSAGE_MODE}"
    )
    if [[ "${TRUST_REMOTE_CODE}" == "1" ]]; then
        EXTRACT_ARGS+=(--trust-remote-code)
    fi
    if [[ -n "${LIMIT_PER_GROUP:-}" ]]; then
        EXTRACT_ARGS+=(--limit-per-group "${LIMIT_PER_GROUP}")
    fi
    if [[ -n "${DOMAINS:-}" ]]; then
        # shellcheck disable=SC2206
        DOMAIN_ARGS=(${DOMAINS})
        EXTRACT_ARGS+=(--domains "${DOMAIN_ARGS[@]}")
    fi
}

build_train_args() {
    TRAIN_ARGS=(
        --epochs "${EPOCHS}"
        --detector "${DETECTOR}"
        --standardize
    )
    if [[ "${DETECTOR}" == "regularized" ]]; then
        TRAIN_ARGS+=(
            --dropout "${DROPOUT}"
            --weight-decay "${WEIGHT_DECAY}"
            --val-ratio "${VAL_RATIO}"
            --patience "${PATIENCE}"
            --class-weights
        )
    fi
}

for MODEL_ID in "${MODEL_IDS[@]}"; do
    SLUG="$(slugify "${MODEL_ID}")"
    FEATURES_DIR="${FEATURES_ROOT}/${SLUG}"
    RESULTS_DIR="${RESULTS_ROOT}/${SLUG}_${DETECTOR}"
    MODELS_DIR="${MODELS_ROOT}/${SLUG}_${DETECTOR}"
    LOAD_MODEL_ID="${MODEL_LOAD_PATH:-${MODEL_ID}}"

    echo "================================================================"
    echo "[model] ${MODEL_ID}"
    if [[ "${LOAD_MODEL_ID}" != "${MODEL_ID}" ]]; then
        echo "[load-model] ${LOAD_MODEL_ID}"
    fi
    echo "[dirs] features=${FEATURES_DIR} results=${RESULTS_DIR} models=${MODELS_DIR}"
    echo "================================================================"

    build_extract_args
    "${PYTHON_BIN}" src/extract_features.py \
        "${EXTRACT_ARGS[@]}" \
        --out "${FEATURES_DIR}" \
        --model "${LOAD_MODEL_ID}" \
        --model-label "${MODEL_ID}"

    build_train_args
    "${PYTHON_BIN}" src/train_detector.py --features "${FEATURES_DIR}" --variant avg --domains all \
        --results "${RESULTS_DIR}" --models-dir "${MODELS_DIR}" "${TRAIN_ARGS[@]}"
    "${PYTHON_BIN}" src/train_detector.py --features "${FEATURES_DIR}" --variant enc --domains all \
        --results "${RESULTS_DIR}" --models-dir "${MODELS_DIR}" "${TRAIN_ARGS[@]}"

    "${PYTHON_BIN}" src/train_detector.py --features "${FEATURES_DIR}" --variant avg --pooled \
        --results "${RESULTS_DIR}" --models-dir "${MODELS_DIR}" "${TRAIN_ARGS[@]}"
    "${PYTHON_BIN}" src/train_detector.py --features "${FEATURES_DIR}" --variant enc --pooled \
        --results "${RESULTS_DIR}" --models-dir "${MODELS_DIR}" "${TRAIN_ARGS[@]}"

    "${PYTHON_BIN}" src/train_detector.py --features "${FEATURES_DIR}" --variant avg --cross A2B \
        --results "${RESULTS_DIR}" --models-dir "${MODELS_DIR}" "${TRAIN_ARGS[@]}"
    "${PYTHON_BIN}" src/train_detector.py --features "${FEATURES_DIR}" --variant enc --cross A2B \
        --results "${RESULTS_DIR}" --models-dir "${MODELS_DIR}" "${TRAIN_ARGS[@]}"
    "${PYTHON_BIN}" src/train_detector.py --features "${FEATURES_DIR}" --variant avg --cross B2A \
        --results "${RESULTS_DIR}" --models-dir "${MODELS_DIR}" "${TRAIN_ARGS[@]}"
    "${PYTHON_BIN}" src/train_detector.py --features "${FEATURES_DIR}" --variant enc --cross B2A \
        --results "${RESULTS_DIR}" --models-dir "${MODELS_DIR}" "${TRAIN_ARGS[@]}"

    if [[ "${RUN_BASELINES}" == "1" ]]; then
        "${PYTHON_BIN}" src/baselines/baseline_chen.py --data "${TRAIN_DATA}" "${TEST_DATA}" \
            --results "${RESULTS_DIR}"
        "${PYTHON_BIN}" src/baselines/baseline_promptguard.py --data "${TEST_DATA}" \
            --results "${RESULTS_DIR}" \
            || echo "[warn] Prompt-Guard-2 실패 — gated model 접근 승인 + huggingface-cli login 필요"
    fi

    "${PYTHON_BIN}" src/aggregate_results.py --results "${RESULTS_DIR}" \
        --out "${RESULTS_DIR}/summary.md" \
        --features "${FEATURES_DIR}" --data "${TEST_DATA}"

    echo "[done] ${MODEL_ID}: ${RESULTS_DIR}/summary.md"
    if [[ "${CLEAN_FEATURES_AFTER}" == "1" ]]; then
        echo "[cleanup] removing features after summary: ${FEATURES_DIR}"
        rm -rf -- "${FEATURES_DIR}"
    fi
done

echo "전체 sweep 완료"
