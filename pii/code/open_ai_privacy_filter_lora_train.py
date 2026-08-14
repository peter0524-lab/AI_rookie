"""
OpenAI privacy-filter LoRA 파인튜닝 (대회 19라벨 BIO)

풀 파인튜닝(open_ai_privacy_filter_train.py) 대신 PEFT LoRA로 일부만 학습합니다.
  - LoRA: attention q/k/v/o_proj
  - 전체 학습: 분류 헤드 score (33→39 클래스 교체)

저장:
  - 어댑터: models/privacy_filter_lora/seed<N>/
  - 추론용 병합: models/privacy_filter_lora/seed<N>/inference/  (eval_baseline 호환)

실행:
    python3 open_ai_privacy_filter_lora_train.py
    SEED=42 LORA_R=16 LR=2e-4 python3 open_ai_privacy_filter_lora_train.py
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import torch
from peft import LoraConfig, PeftModel, TaskType, get_peft_model
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
BASE_DIR       = Path(__file__).resolve().parent
_DATA_DIR_RAW  = os.environ.get("DATA_DIR", "data")
DATA_DIR       = Path(_DATA_DIR_RAW)
if not DATA_DIR.is_absolute():
    DATA_DIR = BASE_DIR / DATA_DIR
TRAIN_FILE     = os.environ.get("TRAIN_FILE", "train.json")
VALID_FILE     = os.environ.get("VALID_FILE", "valid.json")
MODELS_DIR     = BASE_DIR / "models"
BASE_MODEL_DIR = os.environ.get(
    "BASE_MODEL_DIR", str(MODELS_DIR / "privacy_filter")
)
SEED           = int(os.environ.get("SEED", "42"))
RUN_TAG        = os.environ.get("RUN_TAG", f"seed{SEED}_lora")
OUTPUT_DIR     = os.environ.get(
    "OUTPUT_DIR", str(MODELS_DIR / "privacy_filter_lora" / f"seed{SEED}")
)
INFERENCE_DIR  = os.environ.get(
    "INFERENCE_DIR", str(Path(OUTPUT_DIR) / "inference")
)

# ── LoRA ──────────────────────────────────────────────────────────────────────
LORA_R       = int(os.environ.get("LORA_R",       "16"))
LORA_ALPHA   = int(os.environ.get("LORA_ALPHA",   "32"))
LORA_DROPOUT = float(os.environ.get("LORA_DROPOUT", "0.05"))

# ── 하이퍼파라미터 ────────────────────────────────────────────────────────────
MAX_LEN      = int(os.environ.get("MAX_LEN",      "256"))
MICRO_BSZ    = int(os.environ.get("MICRO_BSZ",    "512"))
GRAD_ACCUM   = int(os.environ.get("GRAD_ACCUM",   "1"))
EPOCHS       = int(os.environ.get("EPOCHS",       "20"))
LR           = float(os.environ.get("LR",         "5e-4"))
WARMUP_R     = float(os.environ.get("WARMUP_R",   "0.06"))
WEIGHT_DECAY = float(os.environ.get("WEIGHT_DECAY","0.01"))
EVAL_STEPS   = int(os.environ.get("EVAL_STEPS",   "1000"))
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

LORA_TARGET_MODULES = [
    m.strip() for m in os.environ.get(
        "LORA_TARGET_MODULES", "q_proj,k_proj,v_proj,o_proj"
    ).split(",") if m.strip()
]


class PIIDataset(Dataset):
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
                print(f"  ↳ Best F1={f1:.4f} → LoRA 어댑터 저장 {self.save_dir}")
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


def _load_base_model():
    return AutoModelForTokenClassification.from_pretrained(
        BASE_MODEL_DIR,
        num_labels=NUM_LABELS,
        id2label=ID2LABEL,
        label2id=LABEL2ID,
        trust_remote_code=True,
        ignore_mismatched_sizes=True,
    )


def _apply_lora(model):
    lora_config = LoraConfig(
        r=LORA_R,
        lora_alpha=LORA_ALPHA,
        lora_dropout=LORA_DROPOUT,
        target_modules=LORA_TARGET_MODULES,
        modules_to_save=["score"],
        task_type=TaskType.TOKEN_CLS,
        bias="none",
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()
    return model


def export_merged_for_inference(adapter_dir: str, inference_dir: str, tokenizer) -> None:
    """LoRA 어댑터 + 베이스를 병합해 eval_baseline.py 가 읽을 수 있는 전체 모델로 저장."""
    print(f"\n병합 모델 export → {inference_dir}")
    if os.path.isdir(inference_dir):
        shutil.rmtree(inference_dir, ignore_errors=True)

    base  = _load_base_model()
    model = PeftModel.from_pretrained(base, adapter_dir)
    model = model.merge_and_unload()
    model.save_pretrained(inference_dir)
    tokenizer.save_pretrained(inference_dir)


def _write_label_map(out_dir: str, extra: dict | None = None) -> None:
    payload = {
        "label2id": LABEL2ID,
        "id2label": {str(k): v for k, v in ID2LABEL.items()},
        "target_labels": TARGET_LABELS,
        "morpheme": False,
        "base_model_dir": BASE_MODEL_DIR,
        "model_id": "openai/privacy-filter",
        "run_tag": RUN_TAG,
        "finetune": "lora",
        "lora_r": LORA_R,
        "lora_alpha": LORA_ALPHA,
        "lora_target_modules": LORA_TARGET_MODULES,
    }
    if extra:
        payload.update(extra)
    json.dump(
        payload,
        open(Path(out_dir) / "label_map.json", "w", encoding="utf-8"),
        ensure_ascii=False, indent=2,
    )


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

    train_data = json.load(open(DATA_DIR / TRAIN_FILE, encoding="utf-8"))
    valid_data = json.load(open(DATA_DIR / VALID_FILE, encoding="utf-8"))

    train_ds = PIIDataset(train_data, tokenizer, MAX_LEN)
    valid_ds = PIIDataset(valid_data, tokenizer, MAX_LEN)

    model = _apply_lora(_load_base_model())

    use_bf16 = torch.cuda.is_available() and torch.cuda.is_bf16_supported()
    n_gpu    = torch.cuda.device_count()
    if torch.cuda.is_available():
        print(f"GPU: {torch.cuda.get_device_name(0)} ×{n_gpu}")
    print(f"[privacy-filter LoRA] 사전학습: {BASE_MODEL_DIR}")
    print(f"LoRA r={LORA_R} alpha={LORA_ALPHA} targets={LORA_TARGET_MODULES}")
    print(f"DATA_DIR={DATA_DIR}  TRAIN_FILE={TRAIN_FILE}  VALID_FILE={VALID_FILE}")
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
        _write_label_map(OUTPUT_DIR)
        print(f"\n학습 완료  |  best entity_micro_f1={best_cb.best_f1:.4f}  →  {OUTPUT_DIR}")

    if torch.distributed.is_initialized():
        torch.distributed.destroy_process_group()

    local_rank = int(os.environ.get("LOCAL_RANK", "0"))
    if local_rank != 0:
        sys.exit(0)

    if not os.path.isdir(OUTPUT_DIR) or not os.path.exists(
        os.path.join(OUTPUT_DIR, "adapter_config.json")
    ):
        sys.exit("[ERROR] LoRA 어댑터가 저장되지 않았습니다.")

    export_merged_for_inference(OUTPUT_DIR, INFERENCE_DIR, tokenizer)

    if trainer.is_world_process_zero():
        _write_label_map(INFERENCE_DIR, extra={"adapter_dir": OUTPUT_DIR})

    if os.environ.get("SKIP_EVAL", "0") == "1":
        print("\n학습 완료 — SKIP_EVAL=1 → test 평가 생략.")
        return

    print("\n학습 완료 — test split 평가(eval_baseline.py)를 시작합니다...")
    subprocess.run(
        [sys.executable, str(BASE_DIR / "eval_baseline.py"),
         "--split", "test", "--model_dir", INFERENCE_DIR, "--tag", RUN_TAG],
        check=True,
    )


if __name__ == "__main__":
    main()
