#!/usr/bin/env bash
# EXAONE custom code 호환성 확인용 별도 Python 환경을 만든다.
# 기본 환경은 건드리지 않고, EXAONE 실행 때만 EXAONE_PYTHON_BIN으로 이 venv를 사용한다.
set -euo pipefail
cd "$(dirname "$0")/.."

EXAONE_VENV="${EXAONE_VENV:-/data/team/hwan/.venvs/alignsentinel_exaone}"
CACHE_ROOT="${CACHE_ROOT:-/data/team/hwan/.cache}"
PIP_CACHE_DIR="${PIP_CACHE_DIR:-${CACHE_ROOT}/pip}"
TRANSFORMERS_VERSION="${TRANSFORMERS_VERSION:-5.1.0}"

export PIP_CACHE_DIR
export HF_HOME="${HF_HOME:-${CACHE_ROOT}/huggingface}"
export HF_HUB_CACHE="${HF_HUB_CACHE:-${HF_HOME}/hub}"
export HF_MODULES_CACHE="${HF_MODULES_CACHE:-${HF_HOME}/modules_exaone_py${TRANSFORMERS_VERSION}}"
export TRANSFORMERS_CACHE="${TRANSFORMERS_CACHE:-${HF_HOME}/hub}"
export TORCH_HOME="${TORCH_HOME:-${CACHE_ROOT}/torch}"
mkdir -p "${PIP_CACHE_DIR}" "${HF_HOME}" "${HF_HUB_CACHE}" "${HF_MODULES_CACHE}" "${TORCH_HOME}" "$(dirname "${EXAONE_VENV}")"

if [[ ! -x "${EXAONE_VENV}/bin/python" ]]; then
    if python3 -m venv --system-site-packages "${EXAONE_VENV}" 2>/tmp/alignsentinel_venv_error.log; then
        :
    else
        if ! PYTHONUSERBASE=/data/team/hwan/.local_user python3 -m virtualenv --version >/dev/null 2>&1; then
            PYTHONUSERBASE=/data/team/hwan/.local_user python3 -m pip install --user virtualenv
        fi
        PYTHONUSERBASE=/data/team/hwan/.local_user python3 -m virtualenv --system-site-packages "${EXAONE_VENV}"
    fi
fi

"${EXAONE_VENV}/bin/python" -m pip install --upgrade pip wheel setuptools
"${EXAONE_VENV}/bin/python" -m pip install \
    "transformers==${TRANSFORMERS_VERSION}" \
    "huggingface_hub>=1.3.0,<2.0" \
    "tokenizers>=0.22,<0.23" \
    "safetensors>=0.4.1" \
    "accelerate>=0.30" \
    "sentencepiece" \
    "protobuf"

"${EXAONE_VENV}/bin/python" - <<'PY'
import torch
import transformers
import sklearn

print(f"python ok")
print(f"torch={torch.__version__}")
print(f"transformers={transformers.__version__}")
print(f"sklearn={sklearn.__version__}")
print(f"cuda_available={torch.cuda.is_available()}")
if not torch.cuda.is_available():
    raise SystemExit("CUDA unavailable")
PY

echo "[done] EXAONE_PYTHON_BIN=${EXAONE_VENV}/bin/python"
