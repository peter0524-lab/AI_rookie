#!/usr/bin/env bash
# Compatibility wrapper for the EXAONE-only original regularized sweep.
set -euo pipefail
cd "$(dirname "$0")/.."

export RUN_TAG_PREFIX="${RUN_TAG_PREFIX:-32k_exaone}"
exec bash scripts/run_two_datasets_exaone_small_regularized.sh "$@"
