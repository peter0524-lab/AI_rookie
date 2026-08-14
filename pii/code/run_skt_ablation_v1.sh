#!/usr/bin/env bash
# Train and evaluate SKT 0.1B ablation models under a fresh protocol.
#
# Fresh outputs are written under:
#   models/skt_ablation_v1/{variant}/{train_domain}/seed${SEED}
#
# Evaluation policy:
#   - KDPII train / mixed train: KDPII full-19 + KDPII common-15 + synthetic test
#   - synthetic train: KDPII common-15 + synthetic test only
set -euo pipefail

cd "$(dirname "$0")"
mkdir -p logs results models

export CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0}"

SEED="${SEED:-42}"
EPOCHS="${EPOCHS:-5}"
MAX_LEN="${MAX_LEN:-256}"
EVAL_STEPS="${EVAL_STEPS:-500}"
ES_PATIENCE="${ES_PATIENCE:-5}"
LR="${LR:-3e-5}"
KD_ALPHA="${KD_ALPHA:-0.5}"
KD_T="${KD_T:-3.0}"

KDPII_DATA_DIR="${KDPII_DATA_DIR:-data}"
SYNTH_DATA_DIR="${SYNTH_DATA_DIR:-synthetic}"
MIXED_DATA_DIR="${MIXED_DATA_DIR:-mixed/natural_86_14}"
SPLIT="${SPLIT:-test}"
EXCLUDED_LABELS="${EXCLUDED_LABELS:-FD_MAJOR,OGG_EDUCATION,QT_AGE,QT_ALIEN_NUMBER}"

BASE_OUT="${BASE_OUT:-models/skt_ablation_v1}"
RESULTS_OUT="${RESULTS_OUT:-results/skt_ablation_v1}"
mkdir -p "${RESULTS_OUT}"

PLAIN_MICRO_BSZ="${PLAIN_MICRO_BSZ:-64}"
PLAIN_GRAD_ACCUM="${PLAIN_GRAD_ACCUM:-1}"
DISTILL_MICRO_BSZ="${DISTILL_MICRO_BSZ:-64}"
DISTILL_GRAD_ACCUM="${DISTILL_GRAD_ACCUM:-1}"
PII_MICRO_BSZ="${PII_MICRO_BSZ:-64}"
PII_GRAD_ACCUM="${PII_GRAD_ACCUM:-1}"
EVAL_BSZ="${EVAL_BSZ:-64}"

KDPII_TEACHER_DIR="${KDPII_TEACHER_DIR:-models/klue_roberta_large/seed42}"
SYNTH_TEACHER_DIR="${SYNTH_TEACHER_DIR:-models/klue_roberta_large_synthetic/seed42}"
MIXED_TEACHER_DIR="${MIXED_TEACHER_DIR:-models/klue_roberta_large_mixed_natural/seed42}"

MODEL_ID="${MODEL_ID:-skt/A.X-Encoder-base}"

MASTER_LOG="${RESULTS_OUT}/run_seed${SEED}_$(date +%Y%m%d_%H%M%S).log"
EVAL_MANIFEST="${RESULTS_OUT}/eval_manifest_seed${SEED}.tsv"
SUMMARY_MD="${RESULTS_OUT}/summary_seed${SEED}.md"
SUMMARY_TSV="${RESULTS_OUT}/summary_seed${SEED}.tsv"

has_model() {
  local path="$1"
  [ -f "${path}/config.json" ] && { [ -f "${path}/model.safetensors" ] || [ -f "${path}/pytorch_model.bin" ]; }
}

require_file() {
  local path="$1"
  if [ ! -f "${path}" ]; then
    echo "[ERROR] missing file: ${path}" >&2
    exit 1
  fi
}

require_model_dir() {
  local path="$1"
  if [ ! -f "${path}/config.json" ]; then
    echo "[ERROR] missing model dir: ${path}" >&2
    exit 1
  fi
}

domain_data_dir() {
  case "$1" in
    kdpii) echo "${KDPII_DATA_DIR}" ;;
    synthetic) echo "${SYNTH_DATA_DIR}" ;;
    mixed) echo "${MIXED_DATA_DIR}" ;;
    *) echo "[ERROR] unknown domain: $1" >&2; exit 1 ;;
  esac
}

domain_teacher_dir() {
  case "$1" in
    kdpii) echo "${KDPII_TEACHER_DIR}" ;;
    synthetic) echo "${SYNTH_TEACHER_DIR}" ;;
    mixed) echo "${MIXED_TEACHER_DIR}" ;;
    *) echo "[ERROR] unknown domain: $1" >&2; exit 1 ;;
  esac
}

model_dir() {
  local variant="$1"
  local domain="$2"
  echo "${BASE_OUT}/${variant}/${domain}/seed${SEED}"
}

log_name() {
  local name="$1"
  echo "logs/skt_ablation_v1_${name}_seed${SEED}_$(date +%Y%m%d_%H%M%S).log"
}

run_train() {
  local name="$1"
  shift
  local log
  log="$(log_name "train_${name}")"
  echo
  echo "[train] ${name}"
  echo "        log=${log}"
  "$@" > "${log}" 2>&1
  echo "[done] ${name}"
}

run_eval() {
  local variant="$1"
  local domain="$2"
  local eval_name="$3"
  local data_dir="$4"
  local tag="$5"
  local out="$6"
  shift 6
  local log
  log="$(log_name "eval_${tag}")"
  echo
  echo "[eval] ${variant}/${domain} -> ${eval_name}"
  echo "       log=${log}"
  printf "%s\t%s\t%s\t%s\n" "${variant}" "${domain}" "${eval_name}" "${tag}" >> "${EVAL_MANIFEST}"
  python3 eval_baseline_ensemble_vote.py \
    --data-dir "${data_dir}" \
    --split "${SPLIT}" \
    --min_votes 1 \
    --no_cache \
    --tag "${tag}" \
    --batch_size "${EVAL_BSZ}" \
    --max_length "${MAX_LEN}" \
    "$@" \
    --model_dirs "${out}" > "${log}" 2>&1
  echo "[done] ${variant}/${domain} -> ${eval_name}"
}

train_plain() {
  local domain="$1"
  local out
  local data_dir
  out="$(model_dir plain "${domain}")"
  data_dir="$(domain_data_dir "${domain}")"
  if has_model "${out}"; then
    echo "[skip] plain/${domain} exists: ${out}"
    return
  fi
  run_train "plain_${domain}" \
    env MODEL_ID="${MODEL_ID}" DATA_DIR="${data_dir}" TRAIN_FILE=train.json VALID_FILE=valid.json \
      SEED="${SEED}" OUTPUT_DIR="${out}" RUN_TAG="skt_ablation_v1_plain_${domain}_seed${SEED}" \
      EPOCHS="${EPOCHS}" LR="${LR}" MAX_LEN="${MAX_LEN}" MICRO_BSZ="${PLAIN_MICRO_BSZ}" \
      GRAD_ACCUM="${PLAIN_GRAD_ACCUM}" EVAL_STEPS="${EVAL_STEPS}" ES_PATIENCE="${ES_PATIENCE}" \
      SKIP_EVAL=1 python3 train_baseline.py
}

train_plain_distill() {
  local domain="$1"
  local out
  local data_dir
  local teacher_dir
  out="$(model_dir plain_distill "${domain}")"
  data_dir="$(domain_data_dir "${domain}")"
  teacher_dir="$(domain_teacher_dir "${domain}")"
  if has_model "${out}"; then
    echo "[skip] plain_distill/${domain} exists: ${out}"
    return
  fi
  require_model_dir "${teacher_dir}"
  run_train "plain_distill_${domain}" \
    env MODEL_ID="${MODEL_ID}" DATA_DIR="${data_dir}" TRAIN_FILE=train.json VALID_FILE=valid.json \
      TEACHER_DIR="${teacher_dir}" KD_ALPHA="${KD_ALPHA}" KD_T="${KD_T}" \
      SEED="${SEED}" OUTPUT_DIR="${out}" RUN_TAG="skt_ablation_v1_plain_distill_${domain}_seed${SEED}" \
      EPOCHS="${EPOCHS}" LR="${LR}" MAX_LEN="${MAX_LEN}" MICRO_BSZ="${DISTILL_MICRO_BSZ}" \
      GRAD_ACCUM="${DISTILL_GRAD_ACCUM}" EVAL_STEPS="${EVAL_STEPS}" ES_PATIENCE="${ES_PATIENCE}" \
      SKIP_EVAL=1 python3 distill_train.py
}

train_pii_variant() {
  local variant="$1"
  local domain="$2"
  local use_crf="$3"
  local use_gaz="$4"
  local out
  local data_dir
  out="$(model_dir "${variant}" "${domain}")"
  data_dir="$(domain_data_dir "${domain}")"
  if has_model "${out}"; then
    echo "[skip] ${variant}/${domain} exists: ${out}"
    return
  fi
  run_train "${variant}_${domain}" \
    env MODEL_ID="${MODEL_ID}" DATA_DIR="${data_dir}" TRAIN_FILE=train.json VALID_FILE=valid.json \
      USE_KD=0 KD_ALPHA=1.0 KD_T="${KD_T}" USE_CRF="${use_crf}" USE_GAZETTEER="${use_gaz}" \
      USE_RDROP=0 USE_FGM=0 RDROP_ALPHA=0.0 FGM_EPSILON=0.0 \
      SEED="${SEED}" OUTPUT_DIR="${out}" RUN_TAG="skt_ablation_v1_${variant}_${domain}_seed${SEED}" \
      EPOCHS="${EPOCHS}" LR="${LR}" MAX_LEN="${MAX_LEN}" MICRO_BSZ="${PII_MICRO_BSZ}" \
      GRAD_ACCUM="${PII_GRAD_ACCUM}" EVAL_STEPS="${EVAL_STEPS}" ES_PATIENCE="${ES_PATIENCE}" \
      SKIP_EVAL=1 python3 distill_train_crf_gaz.py
}

eval_model() {
  local variant="$1"
  local domain="$2"
  local out
  out="$(model_dir "${variant}" "${domain}")"
  if ! has_model "${out}"; then
    echo "[ERROR] model not found for eval: ${out}" >&2
    exit 1
  fi

  if [ "${domain}" != "synthetic" ]; then
    run_eval "${variant}" "${domain}" "kdpii_full19" "${KDPII_DATA_DIR}" \
      "skt_ablation_v1_${variant}_${domain}_to_kdpii_full19" "${out}"
  else
    echo "[skip-eval] ${variant}/${domain} -> KDPII full-19 (synthetic train lacks 4 labels)"
  fi

  run_eval "${variant}" "${domain}" "kdpii_common15" "${KDPII_DATA_DIR}" \
    "skt_ablation_v1_${variant}_${domain}_to_kdpii_common15" "${out}" \
    --exclude-labels "${EXCLUDED_LABELS}"

  run_eval "${variant}" "${domain}" "synthetic_test" "${SYNTH_DATA_DIR}" \
    "skt_ablation_v1_${variant}_${domain}_to_synthetic_test" "${out}"
}

collect_summary() {
  python3 - "${EVAL_MANIFEST}" "${SUMMARY_MD}" "${SUMMARY_TSV}" <<'PY'
import glob
import os
import re
import sys
from collections import OrderedDict

manifest_path, md_path, tsv_path = sys.argv[1:4]
rows = OrderedDict()
with open(manifest_path, encoding="utf-8") as f:
    header = next(f, None)
    for line in f:
        variant, domain, eval_name, tag = line.rstrip("\n").split("\t")
        key = (variant, domain)
        rows.setdefault(key, {"variant": variant, "train": domain})
        pattern = f"results/ensemble_vote/eval_vote_test_{tag}_*.md"
        files = sorted(glob.glob(pattern), key=os.path.getmtime)
        value = "-"
        if files:
            text = open(files[-1], encoding="utf-8").read()
            m = re.search(r"\| Entity Micro F1 \| \*\*([0-9.]+)\*\* \|", text)
            if m:
                value = m.group(1)
        rows[key][eval_name] = value

headers = ["variant", "train", "kdpii_full19", "kdpii_common15", "synthetic_test"]
with open(tsv_path, "w", encoding="utf-8") as f:
    f.write("\t".join(headers) + "\n")
    for row in rows.values():
        f.write("\t".join(row.get(h, "-") for h in headers) + "\n")

lines = [
    "# SKT Ablation v1 Summary",
    "",
    "| variant | train | KDPII full-19 | KDPII common-15 | synthetic test |",
    "|---|---|---:|---:|---:|",
]
for row in rows.values():
    lines.append(
        "| {variant} | {train} | {kdpii_full19} | {kdpii_common15} | {synthetic_test} |".format(
            variant=row.get("variant", "-"),
            train=row.get("train", "-"),
            kdpii_full19=row.get("kdpii_full19", "-"),
            kdpii_common15=row.get("kdpii_common15", "-"),
            synthetic_test=row.get("synthetic_test", "-"),
        )
    )
with open(md_path, "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")
print(md_path)
print(tsv_path)
PY
}

main() {
  exec > >(tee -a "${MASTER_LOG}") 2>&1

  echo "=== SKT ablation v1 ==="
  echo "date=$(date)"
  echo "CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES}"
  nvidia-smi --query-gpu=name,memory.total,memory.free --format=csv,noheader || true
  echo "SEED=${SEED} EPOCHS=${EPOCHS} MAX_LEN=${MAX_LEN} LR=${LR}"
  echo "KDPII_DATA_DIR=${KDPII_DATA_DIR}"
  echo "SYNTH_DATA_DIR=${SYNTH_DATA_DIR}"
  echo "MIXED_DATA_DIR=${MIXED_DATA_DIR}"
  echo "BASE_OUT=${BASE_OUT}"
  echo "RESULTS_OUT=${RESULTS_OUT}"
  echo "MASTER_LOG=${MASTER_LOG}"

  require_file "${KDPII_DATA_DIR}/train.json"
  require_file "${KDPII_DATA_DIR}/valid.json"
  require_file "${KDPII_DATA_DIR}/${SPLIT}.json"
  require_file "${SYNTH_DATA_DIR}/train.json"
  require_file "${SYNTH_DATA_DIR}/valid.json"
  require_file "${SYNTH_DATA_DIR}/${SPLIT}.json"

  if [ ! -f "${MIXED_DATA_DIR}/train.json" ] || [ ! -f "${MIXED_DATA_DIR}/valid.json" ]; then
    echo "[build] mixed data missing; building ${MIXED_DATA_DIR}"
    python3 build_mixed_data.py \
      --kdpii-dir "${KDPII_DATA_DIR}" \
      --synthetic-dir "${SYNTH_DATA_DIR}" \
      --out-dir "${MIXED_DATA_DIR}" \
      --seed "${SEED}"
  fi

  require_model_dir "${KDPII_TEACHER_DIR}"
  require_model_dir "${SYNTH_TEACHER_DIR}"
  require_model_dir "${MIXED_TEACHER_DIR}"

  printf "variant\ttrain\teval\ttag\n" > "${EVAL_MANIFEST}"

  echo
  echo "=== Phase 1: train 13 fresh ablation models sequentially ==="
  train_plain mixed

  train_plain_distill kdpii
  train_plain_distill synthetic
  train_plain_distill mixed

  for domain in kdpii synthetic mixed; do
    train_pii_variant crf "${domain}" 1 0
  done
  for domain in kdpii synthetic mixed; do
    train_pii_variant gaz "${domain}" 0 1
  done
  for domain in kdpii synthetic mixed; do
    train_pii_variant crf_gaz "${domain}" 1 1
  done

  echo
  echo "=== Phase 2: evaluate according to train-domain policy ==="
  eval_model plain mixed

  eval_model plain_distill kdpii
  eval_model plain_distill synthetic
  eval_model plain_distill mixed

  for domain in kdpii synthetic mixed; do
    eval_model crf "${domain}"
  done
  for domain in kdpii synthetic mixed; do
    eval_model gaz "${domain}"
  done
  for domain in kdpii synthetic mixed; do
    eval_model crf_gaz "${domain}"
  done

  echo
  echo "=== Phase 3: collect summary ==="
  collect_summary

  echo
  echo "=== Done ==="
  echo "summary_md=${SUMMARY_MD}"
  echo "summary_tsv=${SUMMARY_TSV}"
  echo "master_log=${MASTER_LOG}"
}

main "$@"
