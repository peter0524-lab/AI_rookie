#!/usr/bin/env bash
# synthetic-trained models -> KDPII test, common-15 labels only.
#
# Excludes labels that exist in KDPII 19-label data but not in synthetic data:
#   FD_MAJOR, OGG_EDUCATION, QT_AGE, QT_ALIEN_NUMBER
#
# Usage:
#   bash run_kdpii_common15_cross_eval.sh
#   KDPII_DATA_DIR=processed bash run_kdpii_common15_cross_eval.sh
set -euo pipefail

cd "$(dirname "$0")"

KDPII_DATA_DIR="${KDPII_DATA_DIR:-data}"
SPLIT="${SPLIT:-test}"
BATCH_SIZE="${BATCH_SIZE:-64}"
MAX_LENGTH="${MAX_LENGTH:-256}"
EXCLUDED_LABELS="${EXCLUDED_LABELS:-FD_MAJOR,OGG_EDUCATION,QT_AGE,QT_ALIEN_NUMBER}"

KLUE_SYNTH_DIR="${KLUE_SYNTH_DIR:-models/klue_roberta_large_synthetic/seed42}"
SKT_HARD_BASE="${SKT_HARD_BASE:-models/skt_encoder_crf_gaz_synthetic}"
SKT_DISTILL_BASE="${SKT_DISTILL_BASE:-models/skt_encoder_distill_crf_gaz_synthetic}"

echo "=== KDPII common-15 cross-domain eval ==="
echo "data_dir=${KDPII_DATA_DIR} split=${SPLIT}"
echo "excluded_labels=${EXCLUDED_LABELS}"
echo

echo "=== 1) KLUE synthetic teacher -> KDPII common-15 ==="
python3 eval_baseline_ensemble_vote.py \
  --data-dir "${KDPII_DATA_DIR}" \
  --split "${SPLIT}" \
  --min_votes 1 \
  --no_cache \
  --tag klue_synth_seed42_kdpii_common15 \
  --batch_size "${BATCH_SIZE}" \
  --max_length "${MAX_LENGTH}" \
  --exclude-labels "${EXCLUDED_LABELS}" \
  --model_dirs "${KLUE_SYNTH_DIR}"

echo
echo "=== 2) SKT CRF+gaz hard seed44 -> KDPII common-15 ==="
python3 eval_baseline_ensemble_vote.py \
  --data-dir "${KDPII_DATA_DIR}" \
  --split "${SPLIT}" \
  --min_votes 1 \
  --no_cache \
  --tag crf_gaz_synth_hard_seed44_kdpii_common15 \
  --batch_size "${BATCH_SIZE}" \
  --max_length "${MAX_LENGTH}" \
  --exclude-labels "${EXCLUDED_LABELS}" \
  --model_dirs "${SKT_HARD_BASE}/seed44"

echo
echo "=== 3) SKT CRF+gaz hard vote x3 -> KDPII common-15 ==="
python3 eval_baseline_ensemble_vote.py \
  --data-dir "${KDPII_DATA_DIR}" \
  --split "${SPLIT}" \
  --min_votes 2 \
  --no_cache \
  --tag crf_gaz_synth_hard_x3_vote_kdpii_common15 \
  --batch_size "${BATCH_SIZE}" \
  --max_length "${MAX_LENGTH}" \
  --exclude-labels "${EXCLUDED_LABELS}" \
  --model_dirs \
    "${SKT_HARD_BASE}/seed42" \
    "${SKT_HARD_BASE}/seed43" \
    "${SKT_HARD_BASE}/seed44"

echo
echo "=== 4) SKT CRF+gaz distill seed44 -> KDPII common-15 ==="
python3 eval_baseline_ensemble_vote.py \
  --data-dir "${KDPII_DATA_DIR}" \
  --split "${SPLIT}" \
  --min_votes 1 \
  --no_cache \
  --tag crf_gaz_synth_distill_seed44_kdpii_common15 \
  --batch_size "${BATCH_SIZE}" \
  --max_length "${MAX_LENGTH}" \
  --exclude-labels "${EXCLUDED_LABELS}" \
  --model_dirs "${SKT_DISTILL_BASE}/seed44"

echo
echo "=== 5) SKT CRF+gaz distill vote x3 -> KDPII common-15 ==="
python3 eval_baseline_ensemble_vote.py \
  --data-dir "${KDPII_DATA_DIR}" \
  --split "${SPLIT}" \
  --min_votes 2 \
  --no_cache \
  --tag crf_gaz_synth_distill_x3_vote_kdpii_common15 \
  --batch_size "${BATCH_SIZE}" \
  --max_length "${MAX_LENGTH}" \
  --exclude-labels "${EXCLUDED_LABELS}" \
  --model_dirs \
    "${SKT_DISTILL_BASE}/seed42" \
    "${SKT_DISTILL_BASE}/seed43" \
    "${SKT_DISTILL_BASE}/seed44"

echo
echo "=== Done. Reports are under results/ensemble_vote/ ==="
