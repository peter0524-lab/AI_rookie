"""
OpenAI privacy-filter 파인튜닝 (대회 19라벨 BIO)

사전학습 체크포인트(openai/privacy-filter, 33클래스 BIOES)의 백본을 로드하고
분류 헤드를 39클래스(BIO × 19 PII)로 교체한 뒤 파인튜닝합니다.

정렬·지표·early-stopping 은 train_baseline.py(무형태소)와 동일합니다.
  - fast tokenizer offset_mapping / word_ids → 어절 단위 BIO 정렬
  - entity-micro-F1, valid 기준 best 저장

경로:
  - 사전학습 로드: models/privacy_filter/          (BASE_MODEL_DIR)
  - 파인튜닝 저장:  models/privacy_filter/seed<N>/ (OUTPUT_DIR)

실행:
    python3 open_ai_privacy_filter_train.py
    SEED=43 LR=2e-5 python3 open_ai_privacy_filter_train.py
    SKIP_EVAL=1 SEED=42 python3 open_ai_privacy_filter_train.py
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import Dataset
from transformers import (
    AutoModelForTokenClassification,
    AutoTokenizer,
    DataCollatorForTokenClassification,
    Trainer,
    TrainerCallback,
    TrainingArguments,
)

# ── 경로 ──────────────────────────────────────────────────────────────────────
BASE_DIR        = Path(__file__).resolve().parent
DATA_DIR        = BASE_DIR / "data"
MODELS_DIR      = BASE_DIR / "models"
BASE_MODEL_DIR  = os.environ.get(
    "BASE_MODEL_DIR", str(MODELS_DIR / "privacy_filter")
)
SEED            = int(os.environ.get("SEED", "42"))
RUN_TAG         = os.environ.get("RUN_TAG", f"seed{SEED}")
OUTPUT_DIR      = os.environ.get(
    "OUTPUT_DIR", str(MODELS_DIR / "privacy_filter" / f"seed{SEED}")
)

# ── 하이퍼파라미터 ────────────────────────────────────────────────────────────
MAX_LEN      = int(os.environ.get("MAX_LEN",      "256"))
MICRO_BSZ    = int(os.environ.get("MICRO_BSZ",    "16"))
GRAD_ACCUM   = int(os.environ.get("GRAD_ACCUM",   "4"))
EPOCHS       = int(os.environ.get("EPOCHS",       "20"))
LR           = float(os.environ.get("LR",         "1e-5"))
WARMUP_R     = float(os.environ.get("WARMUP_R",   "0.06"))
WEIGHT_DECAY = float(os.environ.get("WEIGHT_DECAY","0.01"))
EVAL_STEPS   = int(os.environ.get("EVAL_STEPS",   "500"))
ES_PATIENCE  = int(os.environ.get("ES_PATIENCE",  "5"))

# ── 레이블 (19개 PII, 39 BIO 태그) ───────────────────────────────────────────
TARGET_LABELS = [
    "PS_NAME",
    "LC_ADDRESS",
    "OG_WORKPLACE", "OG_DEPARTMENT", "CV_POSITION",
    "OGG_EDUCATION",
    "QT_MOBILE", "QT_PHONE",
    "QT_RESIDENT_NUMBER", "QT_ALIEN_NUMBER",
    "QT_DRIVER_NUMBER", "QT_PLATE_NUMBER",
    "QT_ACCOUNT_NUMBER", "QT_CARD_NUMBER",
    "TMI_EMAIL", "QT_PASSPORT_NUMBER",
    "QT_AGE", "DT_BIRTH", "FD_MAJOR",
]
BIO_LABELS = ["O"] + [f"B-{l}" for l in TARGET_LABELS] + [f"I-{l}" for l in TARGET_LABELS]
LABEL2ID   = {l: i for i, l in enumerate(BIO_LABELS)}
ID2LABEL   = {i: l for l, i in LABEL2ID.items()}
NUM_LABELS = len(BIO_LABELS)  # 39


class PIIDataset(Dataset):
    """character-level BIO → 어절(공백 단위) 첫 서브워드 정렬 (train_baseline 과 동일)."""

    def __init__(self, data: list[dict], tokenizer, max_length: int = 256):
        self.data       = data
        self.tokenizer  = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx: int):
        item        = self.data[idx]
        sentence    = item["sentence"]
        char_labels = item["labelling_seq"]

        encoding = self.tokenizer(
            sentence,
            truncation=True,
            max_length=self.max_length,
            return_offsets_mapping=True,
        )

        word_ids = encoding.word_ids()
        offsets  = encoding["offset_mapping"]

        labels = []
        seen   = set()
        for wid, (cs, ce) in zip(word_ids, offsets):
            if wid is None or ce == 0:
                labels.append(-100)
            elif wid in seen:
                labels.append(-100)
            else:
                seen.add(wid)
                raw = char_labels[cs] if cs < len(char_labels) else "O"
                labels.append(LABEL2ID.get(raw, LABEL2ID["O"]))

        encoding.pop("offset_mapping")
        encoding["labels"] = labels
        return {k: torch.tensor(v) for k, v in encoding.items()}


def bio_to_entities(bio_seq: list[str]) -> set[tuple]:
    entities  = set()
    start = cur_label = None
    for i, tag in enumerate(bio_seq):
        if tag.startswith("B-"):
            if start is not None:
                entities.add((start, i, cur_label))
            start, cur_label = i, tag[2:]
        elif tag.startswith("I-") and cur_label == tag[2:]:
            pass
        else:
            if start is not None:
                entities.add((start, i, cur_label))
            start = cur_label = None
    if start is not None:
        entities.add((start, len(bio_seq), cur_label))
    return entities


def compute_entity_f1(true_seqs, pred_seqs) -> dict:
    tp = fp = fn = 0
    per_label = {l: [0, 0, 0] for l in TARGET_LABELS}

    for true_seq, pred_seq in zip(true_seqs, pred_seqs):
        gold = bio_to_entities(true_seq)
        pred = bio_to_entities(pred_seq)
        tp += len(gold & pred)
        fp += len(pred - gold)
        fn += len(gold - pred)
        for span in gold & pred:
            if span[2] in per_label:
                per_label[span[2]][0] += 1
        for span in pred - gold:
            if span[2] in per_label:
                per_label[span[2]][1] += 1
        for span in gold - pred:
            if span[2] in per_label:
                per_label[span[2]][2] += 1

    def f1(t, fp_, fn_):
        p = t / (t + fp_) if (t + fp_) else 0.0
        r = t / (t + fn_) if (t + fn_) else 0.0
        return (2 * p * r / (p + r) if (p + r) else 0.0), p, r

    micro_f1, micro_p, micro_r = f1(tp, fp, fn)
    result = {"micro_f1": micro_f1, "micro_p": micro_p, "micro_r": micro_r}
    for lbl, (t, fp_, fn_) in per_label.items():
        lf1, _, _ = f1(t, fp_, fn_)
        result[f"f1_{lbl}"] = lf1
    return result


def make_compute_metrics(eval_dataset):
    def compute_metrics(eval_preds):
        logits, labels_arr = eval_preds
        preds_arr = np.argmax(logits, axis=-1)

        true_seqs, pred_seqs = [], []
        for pred_row, label_row in zip(preds_arr, labels_arr):
            true_seq, pred_seq = [], []
            for p, l in zip(pred_row, label_row):
                if l == -100:
                    continue
                true_seq.append(ID2LABEL[l])
                pred_seq.append(ID2LABEL[int(p)])
            true_seqs.append(true_seq)
            pred_seqs.append(pred_seq)

        m = compute_entity_f1(true_seqs, pred_seqs)
        print(
            f"\n  [Eval] Micro F1={m['micro_f1']:.4f}  "
            f"P={m['micro_p']:.4f}  R={m['micro_r']:.4f}"
        )
        label_f1 = [(l, m[f"f1_{l}"]) for l in TARGET_LABELS if m.get(f"f1_{l}", 0) > 0]
        if label_f1:
            print("  " + "  ".join(f"{l}={v:.3f}" for l, v in sorted(label_f1, key=lambda x: -x[1])))
        return {"entity_micro_f1": m["micro_f1"]}

    return compute_metrics


class SaveBestCallback(TrainerCallback):
    def __init__(self, trainer, save_dir: str, patience: int = 5, warmup_ratio: float = 0.06):
        self.trainer      = trainer
        self.save_dir     = save_dir
        self.best_f1      = -1.0
        self.patience     = patience
        self.warmup_ratio = warmup_ratio
        self.no_improve   = 0

    def on_evaluate(self, args, state, control, metrics=None, **kwargs):
        if not metrics:
            return
        f1 = metrics.get("eval_entity_micro_f1", -1.0)

        if f1 > self.best_f1:
            self.best_f1    = f1
            self.no_improve = 0
            if state.is_world_process_zero:
                if os.path.isdir(self.save_dir):
                    shutil.rmtree(self.save_dir, ignore_errors=True)
                self.trainer.save_model(self.save_dir)
                print(f"  ↳ Best F1={f1:.4f} → 저장 {self.save_dir}")
        else:
            self.no_improve += 1
            if state.is_world_process_zero:
                print(f"  F1 개선 없음 ({self.no_improve}/{self.patience}): "
                      f"현재={f1:.4f}  best={self.best_f1:.4f}")

            warmup_steps = int(state.max_steps * self.warmup_ratio)
            if self.no_improve >= self.patience and state.global_step > warmup_steps:
                if state.is_world_process_zero:
                    print(f"  Early stopping: {self.patience}번 연속 F1 미개선")
                control.should_training_stop = True


def main():
    if not Path(BASE_MODEL_DIR, "config.json").exists():
        sys.exit(
            f"[ERROR] 사전학습 모델 없음: {BASE_MODEL_DIR}\n"
            f"        Hugging Face 에서 models/privacy_filter/ 로 다운로드하세요."
        )

    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_DIR, trust_remote_code=True)
    if not tokenizer.is_fast:
        sys.exit(
            f"[ERROR] '{BASE_MODEL_DIR}' 의 fast tokenizer 가 없어 "
            f"offset_mapping 정렬이 불가합니다."
        )

    def load_json(name):
        return json.load(open(DATA_DIR / name, encoding="utf-8"))

    train_data = load_json("train.json")
    valid_data = load_json("valid.json")

    train_ds = PIIDataset(train_data, tokenizer, MAX_LEN)
    valid_ds = PIIDataset(valid_data, tokenizer, MAX_LEN)

    model = AutoModelForTokenClassification.from_pretrained(
        BASE_MODEL_DIR,
        num_labels=NUM_LABELS,
        id2label=ID2LABEL,
        label2id=LABEL2ID,
        trust_remote_code=True,
        ignore_mismatched_sizes=True,
    )

    use_bf16 = torch.cuda.is_available() and torch.cuda.is_bf16_supported()
    n_gpu    = torch.cuda.device_count()
    if torch.cuda.is_available():
        print(f"GPU: {torch.cuda.get_device_name(0)} ×{n_gpu}")
    print(f"[privacy-filter 파인튜닝] 사전학습: {BASE_MODEL_DIR}")
    print(f"RUN_TAG={RUN_TAG}  OUTPUT_DIR={OUTPUT_DIR}")
    print(f"Train {len(train_ds):,}  Valid {len(valid_ds):,}")
    print(f"Epochs={EPOCHS}  LR={LR}  MicroBSZ={MICRO_BSZ}×Accum={GRAD_ACCUM}"
          f"(=eff {MICRO_BSZ * GRAD_ACCUM})  MaxLen={MAX_LEN}  Seed={SEED}  "
          f"{'bf16' if use_bf16 else 'fp16'}")

    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        num_train_epochs=EPOCHS,
        per_device_train_batch_size=MICRO_BSZ,
        per_device_eval_batch_size=MICRO_BSZ,
        gradient_accumulation_steps=GRAD_ACCUM,
        learning_rate=LR,
        warmup_ratio=WARMUP_R,
        lr_scheduler_type="cosine",
        weight_decay=WEIGHT_DECAY,
        max_grad_norm=1.0,
        bf16=use_bf16,
        fp16=not use_bf16 and torch.cuda.is_available(),
        logging_steps=50,
        eval_strategy="steps",
        eval_steps=EVAL_STEPS,
        save_strategy="no",
        report_to="none",
        seed=SEED,
        dataloader_num_workers=4,
        metric_for_best_model="entity_micro_f1",
        greater_is_better=True,
    )

    collator = DataCollatorForTokenClassification(
        tokenizer, padding=True, label_pad_token_id=-100
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_ds,
        eval_dataset=valid_ds,
        data_collator=collator,
        processing_class=tokenizer,
        compute_metrics=make_compute_metrics(valid_ds),
    )

    best_cb = SaveBestCallback(trainer, OUTPUT_DIR, patience=ES_PATIENCE, warmup_ratio=WARMUP_R)
    trainer.add_callback(best_cb)

    trainer.train()

    if best_cb.best_f1 < 0:
        trainer.save_model(OUTPUT_DIR)

    if trainer.is_world_process_zero():
        tokenizer.save_pretrained(OUTPUT_DIR)
        label_map = {
            "label2id": LABEL2ID,
            "id2label": {str(k): v for k, v in ID2LABEL.items()},
            "target_labels": TARGET_LABELS,
            "morpheme": False,
            "base_model_dir": BASE_MODEL_DIR,
            "model_id": "openai/privacy-filter",
            "run_tag": RUN_TAG,
        }
        json.dump(
            label_map,
            open(Path(OUTPUT_DIR) / "label_map.json", "w", encoding="utf-8"),
            ensure_ascii=False, indent=2,
        )
        print(f"\n학습 완료  |  best entity_micro_f1={best_cb.best_f1:.4f}  →  {OUTPUT_DIR}")

    if torch.distributed.is_initialized():
        torch.distributed.destroy_process_group()

    local_rank = int(os.environ.get("LOCAL_RANK", "0"))
    if local_rank != 0:
        sys.exit(0)

    if os.environ.get("SKIP_EVAL", "0") == "1":
        print("\n학습 완료 — SKIP_EVAL=1 → test 평가 생략.")
        return

    print("\n학습 완료 — test split 평가(eval_baseline.py)를 시작합니다...")
    subprocess.run(
        [sys.executable, str(BASE_DIR / "eval_baseline.py"),
         "--split", "test", "--model_dir", OUTPUT_DIR, "--tag", RUN_TAG],
        check=True,
    )


if __name__ == "__main__":
    main()
