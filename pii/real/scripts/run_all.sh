#!/usr/bin/env bash
set -u

ROOT="${ROOT:-/data/team/hwan/real}"
CODE_ROOT="${CODE_ROOT:-/data/team/hwan}"
KDPII_DIR="${KDPII_DIR:-/data/team/hwan/data/kpii}"
SYNTHETIC_DIR="${SYNTHETIC_DIR:-/data/team/hwan/data/synthetic_clean_kdpii}"
RATIOS="${RATIOS:-0.25,0.5,1.0,2.0,all}"
SEED="${SEED:-42}"
MODELS="${MODELS:-all}"
TRAIN_SETS="${TRAIN_SETS:-all}"
PRIVACY_BASE_MODEL="${PRIVACY_BASE_MODEL:-/data/team/hwan/models/privacy_filter_korean}"

mkdir -p "${ROOT}/logs" "${ROOT}/scripts"

echo "[run_all] start $(date)"
echo "[run_all] ROOT=${ROOT}"
echo "[run_all] CODE_ROOT=${CODE_ROOT}"

python3 "${ROOT}/scripts/preflight_real.py" \
  --root "${ROOT}" \
  --code-root "${CODE_ROOT}" \
  --kdpii-dir "${KDPII_DIR}" \
  --synthetic-dir "${SYNTHETIC_DIR}" \
  --privacy-base-model "${PRIVACY_BASE_MODEL}"

PREPARE_FORCE_ARG=""
if [ "${PREPARE_FORCE:-0}" = "1" ]; then
  PREPARE_FORCE_ARG="--force"
fi

python3 "${ROOT}/scripts/prepare_real_data.py" \
  --root "${ROOT}" \
  --kdpii-dir "${KDPII_DIR}" \
  --synthetic-dir "${SYNTHETIC_DIR}" \
  --ratios "${RATIOS}" \
  --seed "${SEED}" \
  ${PREPARE_FORCE_ARG}

REQUIRE_PRESIDIO_ARG="--require-presidio"
if [ "${REQUIRE_PRESIDIO:-1}" = "0" ]; then
  REQUIRE_PRESIDIO_ARG="--no-require-presidio"
fi

DRY_RUN_ARG=""
if [ "${DRY_RUN:-0}" = "1" ]; then
  DRY_RUN_ARG="--dry-run"
fi

SKIP_TRAIN_ARG=""
if [ "${SKIP_TRAIN:-0}" = "1" ]; then
  SKIP_TRAIN_ARG="--skip-train"
fi

python3 "${ROOT}/scripts/run_real_experiments.py" \
  --root "${ROOT}" \
  --code-root "${CODE_ROOT}" \
  --models "${MODELS}" \
  --train-sets "${TRAIN_SETS}" \
  --privacy-base-model "${PRIVACY_BASE_MODEL}" \
  ${REQUIRE_PRESIDIO_ARG} \
  ${DRY_RUN_ARG} \
  ${SKIP_TRAIN_ARG}

echo "[run_all] end $(date)"
