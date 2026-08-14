#!/usr/bin/env bash
# Run the original full-attention regularized backend sweep on two dataset bundles.
#
# DATASET_SPECS format:
#   "name1:train_json:test_json name2:train_json:test_json"
#
# Example:
#   DATASET_SPECS="setA:data_32k_a/full_train.json:data_32k_a/full_test.json setB:data_32k_b/full_train.json:data_32k_b/full_test.json" \
#   nohup bash scripts/run_two_datasets_original_regularized_no_llama.sh \
#     > logs/two_datasets_original_$(date +%Y%m%d_%H%M%S).log 2>&1 &
set -euo pipefail
cd "$(dirname "$0")/.."

RUN_TAG_PREFIX="${RUN_TAG_PREFIX:-32k}"
SKIP_DONE="${SKIP_DONE:-1}"
CONTINUE_ON_ERROR="${CONTINUE_ON_ERROR:-1}"
CONTINUE_DATASETS_ON_ERROR="${CONTINUE_DATASETS_ON_ERROR:-1}"

MODEL_IDS_TEXT="${MODEL_IDS_TEXT:-skt/A.X-4.0-Light LGAI-EXAONE/EXAONE-Deep-7.8B NCSOFT/Llama-VARCO-8B-Instruct upstage/SOLAR-10.7B-Instruct-v1.0 Qwen/Qwen3-8B mistralai/Mistral-7B-Instruct-v0.3}"
export MODEL_IDS_TEXT SKIP_DONE CONTINUE_ON_ERROR

if [[ -z "${DATASET_SPECS:-}" ]]; then
    if [[ -f data_32k_1/full_train.json && -f data_32k_1/full_test.json && -f data_32k_2/full_train.json && -f data_32k_2/full_test.json ]]; then
        DATASET_SPECS="set1:data_32k_1/full_train.json:data_32k_1/full_test.json set2:data_32k_2/full_train.json:data_32k_2/full_test.json"
    elif [[ -f data_32k_a/full_train.json && -f data_32k_a/full_test.json && -f data_32k_b/full_train.json && -f data_32k_b/full_test.json ]]; then
        DATASET_SPECS="setA:data_32k_a/full_train.json:data_32k_a/full_test.json setB:data_32k_b/full_train.json:data_32k_b/full_test.json"
    else
        cat >&2 <<'EOF'
[error] DATASET_SPECS가 필요합니다.

사용 예:
  DATASET_SPECS="setA:data_32k_a/full_train.json:data_32k_a/full_test.json setB:data_32k_b/full_train.json:data_32k_b/full_test.json" \
  bash scripts/run_two_datasets_original_regularized_no_llama.sh
EOF
        exit 2
    fi
fi

mkdir -p logs

echo "================================================================"
echo "[two-datasets] original full-attention regularized sweep"
echo "[two-datasets] RUN_TAG_PREFIX=${RUN_TAG_PREFIX}"
echo "[two-datasets] SKIP_DONE=${SKIP_DONE}"
echo "[two-datasets] CONTINUE_ON_ERROR=${CONTINUE_ON_ERROR}"
echo "[two-datasets] CONTINUE_DATASETS_ON_ERROR=${CONTINUE_DATASETS_ON_ERROR}"
echo "[two-datasets] models=6"
printf ' - %s\n' ${MODEL_IDS_TEXT}
echo "[two-datasets] dataset specs:"
printf ' - %s\n' ${DATASET_SPECS}
echo "================================================================"

FAILED_DATASETS=()
TOTAL_DATASETS=0

for SPEC in ${DATASET_SPECS}; do
    TOTAL_DATASETS=$((TOTAL_DATASETS + 1))
    IFS=':' read -r DATASET_NAME TRAIN_JSON TEST_JSON EXTRA <<<"${SPEC}"

    if [[ -z "${DATASET_NAME}" || -z "${TRAIN_JSON}" || -z "${TEST_JSON}" || -n "${EXTRA:-}" ]]; then
        echo "[error] invalid DATASET_SPECS item: ${SPEC}" >&2
        exit 2
    fi
    if [[ ! "${DATASET_NAME}" =~ ^[A-Za-z0-9_.-]+$ ]]; then
        echo "[error] dataset name must match [A-Za-z0-9_.-]+: ${DATASET_NAME}" >&2
        exit 2
    fi
    if [[ ! -f "${TRAIN_JSON}" ]]; then
        echo "[error] missing train json: ${TRAIN_JSON}" >&2
        exit 2
    fi
    if [[ ! -f "${TEST_JSON}" ]]; then
        echo "[error] missing test json: ${TEST_JSON}" >&2
        exit 2
    fi

    RUN_TAG="${RUN_TAG_PREFIX}_${DATASET_NAME}"
    FEATURES_ROOT="features_${RUN_TAG}"
    RESULTS_ROOT="results_${RUN_TAG}"
    MODELS_ROOT="models_${RUN_TAG}"

    echo "================================================================"
    echo "[dataset-start] ${DATASET_NAME}"
    echo "[dataset] train=${TRAIN_JSON}"
    echo "[dataset] test=${TEST_JSON}"
    echo "[dataset] features=${FEATURES_ROOT}"
    echo "[dataset] results=${RESULTS_ROOT}"
    echo "[dataset] models=${MODELS_ROOT}"
    echo "================================================================"

    set +e
    TRAIN_DATA="${TRAIN_JSON}" \
    TEST_DATA="${TEST_JSON}" \
    RUN_TAG="${RUN_TAG}" \
    FEATURES_ROOT="${FEATURES_ROOT}" \
    RESULTS_ROOT="${RESULTS_ROOT}" \
    MODELS_ROOT="${MODELS_ROOT}" \
    bash scripts/run_original_regularized_no_llama.sh
    STATUS=$?
    set -e

    if [[ "${STATUS}" -ne 0 ]]; then
        echo "[dataset-fail] ${DATASET_NAME} exit=${STATUS}"
        FAILED_DATASETS+=("${DATASET_NAME}")
        if [[ "${CONTINUE_DATASETS_ON_ERROR}" != "1" ]]; then
            exit "${STATUS}"
        fi
        continue
    fi

    echo "[dataset-done] ${DATASET_NAME}"
done

echo "================================================================"
echo "[two-datasets-complete] datasets=${TOTAL_DATASETS} failures=${#FAILED_DATASETS[@]}"
if [[ "${#FAILED_DATASETS[@]}" -gt 0 ]]; then
    printf ' - failed: %s\n' "${FAILED_DATASETS[@]}"
    exit 1
fi
echo "전체 2-dataset backend sweep 완료"
echo "================================================================"
