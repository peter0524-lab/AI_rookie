#!/usr/bin/env bash
# 논문 backend와 한국어 후보 backend를 한 줄로 순차 실행하는 상위 스크립트.
#
# 사용 예시:
#   MODEL_SET=paper bash scripts/run_sequential_backends.sh
#   MODEL_SET=korean SKIP_DONE=1 bash scripts/run_sequential_backends.sh
#   MODEL_SET=all CONTINUE_ON_ERROR=1 bash scripts/run_sequential_backends.sh
#
# 직접 모델 지정:
#   MODEL_IDS_TEXT="Qwen/Qwen3-8B mistralai/Mistral-7B-Instruct-v0.3" bash scripts/run_sequential_backends.sh
set -euo pipefail
cd "$(dirname "$0")/.."

MODEL_SET="${MODEL_SET:-all}"
DETECTOR="${DETECTOR:-regularized}"
SKIP_DONE="${SKIP_DONE:-1}"
CONTINUE_ON_ERROR="${CONTINUE_ON_ERROR:-1}"
TRAIN_DATA="${TRAIN_DATA:-data/full_train.json}"
TEST_DATA="${TEST_DATA:-data/full_test.json}"
FEATURES_ROOT="${FEATURES_ROOT:-features}"
RESULTS_ROOT="${RESULTS_ROOT:-results}"
MODELS_ROOT="${MODELS_ROOT:-models}"
export TRAIN_DATA TEST_DATA FEATURES_ROOT RESULTS_ROOT MODELS_ROOT

DEFAULT_EXAONE_PYTHON_BIN="${DEFAULT_EXAONE_PYTHON_BIN:-/data/team/hwan/.venvs/alignsentinel_exaone/bin/python}"
DEFAULT_EXAONE_MODULES_CACHE="${DEFAULT_EXAONE_MODULES_CACHE:-/data/team/hwan/.cache/huggingface/modules_exaone_py5.1.0}"
DEFAULT_HF_HUB_CACHE="${DEFAULT_HF_HUB_CACHE:-${HF_HUB_CACHE:-/data/team/hwan/.cache/huggingface/hub}}"
if [[ -z "${EXAONE_PYTHON_BIN:-}" && -x "${DEFAULT_EXAONE_PYTHON_BIN}" ]]; then
    EXAONE_PYTHON_BIN="${DEFAULT_EXAONE_PYTHON_BIN}"
fi

PAPER_MODELS=(
    "Qwen/Qwen3-8B"
    "meta-llama/Llama-3.1-8B-Instruct"
    "mistralai/Mistral-7B-Instruct-v0.3"
)

KOREAN_MODELS=(
    "skt/A.X-4.0-Light"
    "LGAI-EXAONE/EXAONE-Deep-7.8B"
    "NCSOFT/Llama-VARCO-8B-Instruct"
    "upstage/SOLAR-10.7B-Instruct-v1.0"
)

slugify() {
    printf "%s" "$1" | tr '/:.' '___' | tr -c 'A-Za-z0-9_-' '_'
}

hf_cache_dir_name() {
    printf "models--%s" "$(printf "%s" "$1" | sed 's#/#--#g')"
}

hf_local_snapshot() {
    local model_id="$1"
    local cache_dir="${DEFAULT_HF_HUB_CACHE}/$(hf_cache_dir_name "${model_id}")"
    local commit
    local snapshot

    if [[ ! -f "${cache_dir}/refs/main" ]]; then
        return 1
    fi

    commit="$(tr -d '\n' < "${cache_dir}/refs/main")"
    snapshot="${cache_dir}/snapshots/${commit}"
    if [[ -f "${snapshot}/config.json" ]]; then
        printf "%s" "${snapshot}"
        return 0
    fi
    return 1
}

select_models() {
    if [[ -n "${MODEL_IDS_TEXT:-}" ]]; then
        # shellcheck disable=SC2206
        SELECTED_MODELS=(${MODEL_IDS_TEXT})
        return
    fi

    case "${MODEL_SET}" in
        paper)
            SELECTED_MODELS=("${PAPER_MODELS[@]}")
            ;;
        korean)
            SELECTED_MODELS=("${KOREAN_MODELS[@]}")
            ;;
        all)
            SELECTED_MODELS=("${KOREAN_MODELS[@]}" "${PAPER_MODELS[@]}")
            ;;
        *)
            echo "[error] MODEL_SET은 paper, korean, all 중 하나여야 합니다: ${MODEL_SET}" >&2
            exit 2
            ;;
    esac
}

select_models
mkdir -p logs

echo "================================================================"
echo "[sequential] MODEL_SET=${MODEL_SET} DETECTOR=${DETECTOR}"
echo "[sequential] SKIP_DONE=${SKIP_DONE} CONTINUE_ON_ERROR=${CONTINUE_ON_ERROR}"
echo "[sequential] models=${#SELECTED_MODELS[@]}"
echo "[sequential] CACHE_ROOT=${CACHE_ROOT:-auto}"
echo "[sequential] data=${TRAIN_DATA} ${TEST_DATA}"
echo "[sequential] roots=${FEATURES_ROOT} ${RESULTS_ROOT} ${MODELS_ROOT}"
echo "================================================================"

FAILED_MODELS=()
for MODEL_ID in "${SELECTED_MODELS[@]}"; do
    SLUG="$(slugify "${MODEL_ID}")"
    SUMMARY_PATH="${RESULTS_ROOT}/${SLUG}_${DETECTOR}/summary.md"
    FAILED_MARKER="logs/${SLUG}_${DETECTOR}.failed"

    if [[ "${SKIP_DONE}" == "1" && -f "${SUMMARY_PATH}" ]]; then
        echo "[skip] ${MODEL_ID} — ${SUMMARY_PATH} 존재"
        continue
    fi

    echo "================================================================"
    echo "[start] ${MODEL_ID}"
    echo "================================================================"

    RUN_ENV=(MODEL_IDS_TEXT="${MODEL_ID}" DETECTOR="${DETECTOR}" MODEL_LOAD_PATH=)
    if [[ -n "${PYTHON_BIN:-}" ]]; then
        RUN_ENV+=(PYTHON_BIN="${PYTHON_BIN}")
    fi
    if [[ "${MODEL_ID}" == LGAI-EXAONE/* && -n "${EXAONE_PYTHON_BIN:-}" ]]; then
        RUN_ENV+=(PYTHON_BIN="${EXAONE_PYTHON_BIN}")
        RUN_ENV+=(HF_MODULES_CACHE="${DEFAULT_EXAONE_MODULES_CACHE}")
        EXAONE_SNAPSHOT="$(hf_local_snapshot "${MODEL_ID}" || true)"
        if [[ -n "${EXAONE_SNAPSHOT}" ]]; then
            RUN_ENV+=(MODEL_LOAD_PATH="${EXAONE_SNAPSHOT}")
            RUN_ENV+=(HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1)
            echo "[env] EXAONE local snapshot=${EXAONE_SNAPSHOT}"
            echo "[env] EXAONE offline cache mode enabled"
        else
            RUN_ENV+=(HF_HUB_OFFLINE=0 TRANSFORMERS_OFFLINE=0)
            echo "[env] EXAONE local snapshot not found; online cache/download allowed"
        fi
        echo "[env] EXAONE_PYTHON_BIN=${EXAONE_PYTHON_BIN}"
        echo "[env] EXAONE HF_MODULES_CACHE=${DEFAULT_EXAONE_MODULES_CACHE}"
    fi

    set +e
    env "${RUN_ENV[@]}" bash scripts/run_model_sweep.sh
    STATUS=$?
    set -e

    if [[ "${STATUS}" -ne 0 ]]; then
        echo "[fail] ${MODEL_ID} exit=${STATUS}" | tee "${FAILED_MARKER}"
        FAILED_MODELS+=("${MODEL_ID}")
        if [[ "${CONTINUE_ON_ERROR}" != "1" ]]; then
            exit "${STATUS}"
        fi
        continue
    fi

    echo "[done] ${MODEL_ID}"
done

if [[ "${#FAILED_MODELS[@]}" -gt 0 ]]; then
    echo "================================================================"
    echo "[complete-with-failures] ${#FAILED_MODELS[@]} model(s) failed"
    printf ' - %s\n' "${FAILED_MODELS[@]}"
    echo "================================================================"
    exit 1
fi

echo "전체 sequential backend sweep 완료"
