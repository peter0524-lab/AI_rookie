#!/usr/bin/env bash
# 전체 backend sweep 전에 중간 중단 가능성을 줄이기 위한 사전 점검.
#
# 빠른 점검:
#   MODEL_SET=all bash scripts/preflight_backend_sweep.sh
#
# 모델 접근까지 확인:
#   MODEL_SET=all CHECK_MODEL_ACCESS=1 bash scripts/preflight_backend_sweep.sh
#
# 가장 강한 점검(각 모델 weight 로드 + output_attentions forward 1회):
#   MODEL_SET=all CHECK_MODEL_ACCESS=1 CHECK_TINY_FORWARD=1 bash scripts/preflight_backend_sweep.sh
set -euo pipefail
cd "$(dirname "$0")/.."

MODEL_SET="${MODEL_SET:-all}"
DETECTOR="${DETECTOR:-regularized}"
CHECK_MODEL_ACCESS="${CHECK_MODEL_ACCESS:-1}"
CHECK_TINY_FORWARD="${CHECK_TINY_FORWARD:-0}"
STRICT_MODEL_ACCESS="${STRICT_MODEL_ACCESS:-0}"
MIN_ROOT_GB="${MIN_ROOT_GB:-3}"
MIN_DATA_GB="${MIN_DATA_GB:-80}"
TRUST_REMOTE_CODE="${TRUST_REMOTE_CODE:-1}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
TRAIN_DATA="${TRAIN_DATA:-data/full_train.json}"
TEST_DATA="${TEST_DATA:-data/full_test.json}"
RESULTS_ROOT="${RESULTS_ROOT:-results}"

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
mkdir -p "${HF_HOME}" "${HF_HUB_CACHE}" "${HF_MODULES_CACHE}" "${TORCH_HOME}" logs

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

check_available_gb() {
    local path="$1"
    local min_gb="$2"
    local label="$3"
    local avail_kb
    avail_kb="$(df -Pk "${path}" | awk 'NR==2 {print $4}')"
    local avail_gb=$((avail_kb / 1024 / 1024))
    echo "[disk] ${label}: ${avail_gb}GB available at ${path} (min ${min_gb}GB)"
    if (( avail_gb < min_gb )); then
        echo "[error] ${label} 여유 공간 부족" >&2
        exit 1
    fi
}

select_models

echo "================================================================"
echo "[preflight] MODEL_SET=${MODEL_SET} DETECTOR=${DETECTOR}"
echo "[preflight] CHECK_MODEL_ACCESS=${CHECK_MODEL_ACCESS} CHECK_TINY_FORWARD=${CHECK_TINY_FORWARD}"
echo "[preflight] CACHE_ROOT=${CACHE_ROOT}"
echo "[preflight] data=${TRAIN_DATA} ${TEST_DATA}"
echo "[preflight] RESULTS_ROOT=${RESULTS_ROOT}"
echo "[preflight] models=${#SELECTED_MODELS[@]}"
printf ' - %s\n' "${SELECTED_MODELS[@]}"
echo "================================================================"

for required in "${TRAIN_DATA}" "${TEST_DATA}" src/extract_features.py src/train_detector.py scripts/run_sequential_backends.sh scripts/run_model_sweep.sh; do
    if [[ ! -f "${required}" ]]; then
        echo "[error] required file missing: ${required}" >&2
        exit 1
    fi
done

check_available_gb "/" "${MIN_ROOT_GB}" "root"
check_available_gb "." "${MIN_DATA_GB}" "project/data"
check_available_gb "${CACHE_ROOT}" "${MIN_DATA_GB}" "cache"

echo "[python] import + CUDA check (${PYTHON_BIN})"
"${PYTHON_BIN}" - <<'PY'
import sys
import torch
import transformers

print(f"python={sys.version.split()[0]}")
print(f"torch={torch.__version__}")
print(f"transformers={transformers.__version__}")
print(f"cuda_available={torch.cuda.is_available()}")
if not torch.cuda.is_available():
    raise SystemExit("CUDA unavailable")
print(f"cuda_device={torch.cuda.get_device_name(0)}")
PY

echo "[gpu]"
nvidia-smi --query-gpu=index,name,utilization.gpu,memory.used,memory.total --format=csv,noheader || true
echo "[gpu processes]"
nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv,noheader || true

echo "[result status]"
for model_id in "${SELECTED_MODELS[@]}"; do
    slug="$(slugify "${model_id}")"
    summary="${RESULTS_ROOT}/${slug}_${DETECTOR}/summary.md"
    if [[ -f "${summary}" ]]; then
        echo "[done] ${model_id} -> ${summary}"
    else
        echo "[todo] ${model_id}"
    fi
done

if [[ "${CHECK_MODEL_ACCESS}" == "1" ]]; then
    echo "[hf] model config/tokenizer access check"
    PREFLIGHT_MODEL_IDS_TEXT="${SELECTED_MODELS[*]}" STRICT_MODEL_ACCESS="${STRICT_MODEL_ACCESS}" TRUST_REMOTE_CODE="${TRUST_REMOTE_CODE}" "${PYTHON_BIN}" - <<'PY'
import os
import sys
from transformers import AutoConfig, AutoTokenizer

models = os.environ["PREFLIGHT_MODEL_IDS_TEXT"].split()
strict = os.environ.get("STRICT_MODEL_ACCESS") == "1"
trust_remote_code = os.environ.get("TRUST_REMOTE_CODE", "1") == "1"
errors = []

for model_id in models:
    try:
        AutoConfig.from_pretrained(model_id, trust_remote_code=trust_remote_code)
        AutoTokenizer.from_pretrained(model_id, trust_remote_code=trust_remote_code)
        print(f"[ok] {model_id}")
    except Exception as exc:
        msg = str(exc).splitlines()[0][:300]
        print(f"[warn] {model_id}: {type(exc).__name__}: {msg}")
        errors.append(model_id)

if errors:
    print(f"[warn] access check failed for {len(errors)} model(s): {', '.join(errors)}")
    if strict:
        sys.exit(1)
PY
fi

if [[ "${CHECK_TINY_FORWARD}" == "1" ]]; then
    echo "[tiny-forward] loading each model and checking output_attentions once"
    PREFLIGHT_MODEL_IDS_TEXT="${SELECTED_MODELS[*]}" TRUST_REMOTE_CODE="${TRUST_REMOTE_CODE}" "${PYTHON_BIN}" - <<'PY'
import gc
import os
import sys

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

models = os.environ["PREFLIGHT_MODEL_IDS_TEXT"].split()
trust_remote_code = os.environ.get("TRUST_REMOTE_CODE", "1") == "1"
errors = []

def render(tokenizer, model_id):
    tool = "<tool_response>\n테스트 도구 응답입니다.\n</tool_response>"
    if "mistral" in model_id.lower():
        messages = [
            {"role": "system", "content": "사용자 지시를 우선하세요."},
            {"role": "user", "content": "한 문장으로 답하세요.\n\n" + tool},
        ]
    else:
        messages = [
            {"role": "system", "content": "사용자 지시를 우선하세요."},
            {"role": "user", "content": "한 문장으로 답하세요."},
            {"role": "user", "content": tool},
        ]
    try:
        return tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=False, enable_thinking=False
        )
    except TypeError:
        return tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)

for model_id in models:
    try:
        print(f"[load] {model_id}", flush=True)
        tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=trust_remote_code)
        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            torch_dtype=torch.bfloat16,
            attn_implementation="eager",
            device_map="cuda",
            trust_remote_code=trust_remote_code,
        )
        model.eval()
        text = render(tokenizer, model_id)
        enc = tokenizer(text, return_tensors="pt", truncation=True, max_length=256, add_special_tokens=False)
        enc = {k: v.to(model.device) for k, v in enc.items()}
        with torch.no_grad():
            out = model(**enc, output_attentions=True, use_cache=False)
        if not getattr(out, "attentions", None):
            raise RuntimeError("output_attentions is empty")
        print(f"[ok] {model_id}")
    except Exception as exc:
        msg = str(exc).splitlines()[0][:300]
        print(f"[warn] {model_id}: {type(exc).__name__}: {msg}")
        errors.append(model_id)
    finally:
        try:
            del model
        except NameError:
            pass
        try:
            del tokenizer
        except NameError:
            pass
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

if errors:
    print(f"[warn] tiny forward failed for {len(errors)} model(s): {', '.join(errors)}")
    sys.exit(1)
PY
fi

echo "[ok] preflight 완료"
