"""
챔피언(distill_aug) 체크포인트 + CRF 파인튜닝

기존 skt_encoder_distill_aug/seed* 가중치를 로드한 뒤 CRF 레이어만 추가하고
짧게(기본 5 epoch) CRF NLL 로 미세조정. teacher KD 재추출 없음 → 빠름.

실행 (챔피언 seed42와 동일 체크포인트에서 시작):
    INIT_FROM=models/skt_encoder_distill_aug/seed42 SEED=42 \
    OUTPUT_DIR=models/skt_encoder_distill_aug_crf/seed42 \
    TRAIN_FILE=train_aug.json python3 train_crf_finetune.py
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
from transformers import AutoTokenizer, Trainer, TrainerCallback, TrainingArguments

from crf_model import TokenClassifierCRF

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

INIT_FROM  = os.environ.get("INIT_FROM", "models/skt_encoder_distill_aug/seed42")
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "models/skt_encoder_distill_aug_crf/seed42")
SEED       = int(os.environ.get("SEED", "42"))
RUN_TAG    = os.environ.get("RUN_TAG", f"seed{SEED}_crf")

MAX_LEN      = int(os.environ.get("MAX_LEN", "256"))
MICRO_BSZ    = int(os.environ.get("MICRO_BSZ", "64"))
GRAD_ACCUM   = int(os.environ.get("GRAD_ACCUM", "1"))
EPOCHS       = int(os.environ.get("EPOCHS", "5"))
LR           = float(os.environ.get("LR", "2e-5"))
WARMUP_R     = float(os.environ.get("WARMUP_R", "0.06"))
WEIGHT_DECAY = float(os.environ.get("WEIGHT_DECAY", "0.01"))
EVAL_STEPS   = int(os.environ.get("EVAL_STEPS", "500"))
ES_PATIENCE  = int(os.environ.get("ES_PATIENCE", "3"))

TARGET_LABELS = [
    "PS_NAME", "LC_ADDRESS",
    "OG_WORKPLACE", "OG_DEPARTMENT", "CV_POSITION", "OGG_EDUCATION",
    "QT_MOBILE", "QT_PHONE", "QT_RESIDENT_NUMBER", "QT_ALIEN_NUMBER",
    "QT_DRIVER_NUMBER", "QT_PLATE_NUMBER", "QT_ACCOUNT_NUMBER", "QT_CARD_NUMBER",
    "TMI_EMAIL", "QT_PASSPORT_NUMBER", "QT_AGE", "DT_BIRTH", "FD_MAJOR",
]
BIO_LABELS = ["O"] + [f"B-{l}" for l in TARGET_LABELS] + [f"I-{l}" for l in TARGET_LABELS]
LABEL2ID   = {l: i for i, l in enumerate(BIO_LABELS)}
ID2LABEL   = {i: l for l, i in LABEL2ID.items()}


def _word_tag(char_labels, cs):
    raw = char_labels[cs] if cs < len(char_labels) else "O"
    return LABEL2ID.get(raw, LABEL2ID["O"]), raw


def _cont_tag(first_raw):
    if first_raw == "O":
        return LABEL2ID["O"]
    ent = first_raw[2:] if first_raw.startswith(("B-", "I-")) else first_raw
    return LABEL2ID.get(f"I-{ent}", LABEL2ID["O"])


class CRFDataset(Dataset):
    """CRF용: 어절 내 모든 서브워드에 BIO 라벨 부여."""

    def __init__(self, data, tokenizer, max_length=256):
        self.data = data
        self.tok = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]
        enc = self.tok(
            item["sentence"], truncation=True, max_length=self.max_length,
            return_offsets_mapping=True,
        )
        word_ids = enc.word_ids()
        offsets = enc["offset_mapping"]
        char_labels = item["labelling_seq"]

        labels, seen = [], {}
        for wid, (cs, ce) in zip(word_ids, offsets):
            if wid is None or ce == 0:
                labels.append(-100)
            elif wid not in seen:
                lid, raw = _word_tag(char_labels, cs)
                seen[wid] = raw
                labels.append(lid)
            else:
                labels.append(_cont_tag(seen[wid]))

        enc.pop("offset_mapping")
        enc["labels"] = labels
        return {k: torch.tensor(v) for k, v in enc.items()}


def bio_to_entities(bio_seq):
    entities, start, cur = set(), None, None
    for i, tag in enumerate(bio_seq):
        if tag.startswith("B-"):
            if start is not None:
                entities.add((start, i, cur))
            start, cur = i, tag[2:]
        elif tag.startswith("I-") and cur == tag[2:]:
            pass
        else:
            if start is not None:
                entities.add((start, i, cur))
            start = cur = None
    if start is not None:
        entities.add((start, len(bio_seq), cur))
    return entities


def compute_entity_f1(true_seqs, pred_seqs):
    tp = fp = fn = 0
    for true_seq, pred_seq in zip(true_seqs, pred_seqs):
        gold = bio_to_entities(true_seq)
        pred = bio_to_entities(pred_seq)
        tp += len(gold & pred)
        fp += len(pred - gold)
        fn += len(gold - pred)

    def f1(t, fp_, fn_):
        p = t / (t + fp_) if (t + fp_) else 0.0
        r = t / (t + fn_) if (t + fn_) else 0.0
        return (2 * p * r / (p + r) if (p + r) else 0.0), p, r

    return f1(tp, fp, fn)


class CRFTrainer(Trainer):
    def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
        labels = inputs.pop("labels")
        out = model(
            input_ids=inputs["input_ids"],
            attention_mask=inputs["attention_mask"],
            labels=labels,
        )
        return (out["loss"], out) if return_outputs else out["loss"]

    def prediction_step(self, model, inputs, prediction_loss_only, ignore_keys=None):
        labels = inputs.get("labels")
        with torch.no_grad():
            loss_out = model(
                input_ids=inputs["input_ids"],
                attention_mask=inputs["attention_mask"],
                labels=labels,
            )
            loss = loss_out["loss"]
            decoded = model.decode(inputs["input_ids"], inputs["attention_mask"])

        if prediction_loss_only:
            return (loss, None, None)

        if labels is not None:
            lab = labels
            pred_pad = torch.full(lab.shape, -100, dtype=torch.long, device=lab.device)
            for i, seq in enumerate(decoded):
                n = min(len(seq), pred_pad.shape[1])
                pred_pad[i, :n] = torch.tensor(seq[:n], dtype=torch.long, device=lab.device)
            return (loss, pred_pad, lab)
        return (loss, None, None)


def make_compute_metrics():
    def compute_metrics(eval_preds):
        preds_arr, labels_arr = eval_preds
        true_seqs, pred_seqs = [], []
        for pred_row, label_row in zip(preds_arr, labels_arr):
            t_seq, p_seq = [], []
            for p, l in zip(pred_row, label_row):
                if l == -100:
                    continue
                t_seq.append(ID2LABEL[l])
                p_seq.append(ID2LABEL[int(p)])
            true_seqs.append(t_seq)
            pred_seqs.append(p_seq)
        micro_f1, micro_p, micro_r = compute_entity_f1(true_seqs, pred_seqs)
        print(f"\n  [Eval/CRF] Micro F1={micro_f1:.4f}  P={micro_p:.4f}  R={micro_r:.4f}")
        return {"entity_micro_f1": micro_f1}

    return compute_metrics


class SaveBestCallback(TrainerCallback):
    def __init__(self, model, save_dir, patience=3, warmup_ratio=0.06):
        self.model = model
        self.save_dir = save_dir
        self.best_f1 = -1.0
        self.patience = patience
        self.warmup_ratio = warmup_ratio
        self.no_improve = 0

    def on_evaluate(self, args, state, control, metrics=None, **kwargs):
        if not metrics:
            return
        f1 = metrics.get("eval_entity_micro_f1", -1.0)
        if f1 > self.best_f1:
            self.best_f1 = f1
            self.no_improve = 0
            if state.is_world_process_zero:
                if os.path.isdir(self.save_dir):
                    shutil.rmtree(self.save_dir, ignore_errors=True)
                self.model.save_pretrained(self.save_dir)
                print(f"  ↳ Best F1={f1:.4f} → 저장 {self.save_dir}")
        else:
            self.no_improve += 1
            warmup_steps = int(state.max_steps * self.warmup_ratio)
            if self.no_improve >= self.patience and state.global_step > warmup_steps:
                control.should_training_stop = True


class CRFCollator:
    def __init__(self, pad_id):
        self.pad_id = pad_id

    def __call__(self, features):
        max_len = max(len(f["input_ids"]) for f in features)
        ids, mask, labels = [], [], []
        for f in features:
            pad = max_len - len(f["input_ids"])
            ids.append(torch.cat([f["input_ids"], torch.full((pad,), self.pad_id, dtype=torch.long)]))
            mask.append(torch.cat([f["attention_mask"], torch.zeros(pad, dtype=torch.long)]))
            labels.append(torch.cat([f["labels"], torch.full((pad,), -100, dtype=torch.long)]))
        return {
            "input_ids": torch.stack(ids),
            "attention_mask": torch.stack(mask),
            "labels": torch.stack(labels),
        }


def main():
    if not Path(INIT_FROM, "config.json").exists():
        sys.exit(f"[ERROR] INIT_FROM 없음: {INIT_FROM}")

    tok = AutoTokenizer.from_pretrained(INIT_FROM, trust_remote_code=True, use_fast=True)
    if not tok.is_fast:
        sys.exit("[ERROR] fast tokenizer 필요")

    model = TokenClassifierCRF.from_pretrained_tc(INIT_FROM)
    use_bf16 = torch.cuda.is_available() and torch.cuda.is_bf16_supported()

    train_file = os.environ.get("TRAIN_FILE", "train_aug.json")
    train_data = json.load(open(DATA_DIR / train_file, encoding="utf-8"))
    valid_data = json.load(open(DATA_DIR / "valid.json", encoding="utf-8"))

    print(f"[CRF finetune] INIT_FROM={INIT_FROM}")
    print(f"  OUTPUT_DIR={OUTPUT_DIR}  epochs={EPOCHS}  LR={LR}  seed={SEED}")
    print(f"  train={len(train_data):,}  valid={len(valid_data):,}")

    train_ds = CRFDataset(train_data, tok, MAX_LEN)
    valid_ds = CRFDataset(valid_data, tok, MAX_LEN)

    args = TrainingArguments(
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
        remove_unused_columns=False,
        label_names=["labels"],
        metric_for_best_model="entity_micro_f1",
        greater_is_better=True,
        prediction_loss_only=False,
    )

    trainer = CRFTrainer(
        model=model,
        args=args,
        train_dataset=train_ds,
        eval_dataset=valid_ds,
        data_collator=CRFCollator(tok.pad_token_id or 0),
        processing_class=tok,
        compute_metrics=make_compute_metrics(),
    )

    best_cb = SaveBestCallback(model, OUTPUT_DIR, ES_PATIENCE, WARMUP_R)
    trainer.add_callback(best_cb)
    trainer.train()

    if best_cb.best_f1 < 0:
        model.save_pretrained(OUTPUT_DIR)
    tok.save_pretrained(OUTPUT_DIR)

    json.dump({
        "label2id": LABEL2ID,
        "id2label": {str(k): v for k, v in ID2LABEL.items()},
        "init_from": INIT_FROM,
        "crf": True,
        "run_tag": RUN_TAG,
    }, open(Path(OUTPUT_DIR) / "label_map.json", "w", encoding="utf-8"),
        ensure_ascii=False, indent=2)

    print(f"\n완료 | best valid F1={best_cb.best_f1:.4f} → {OUTPUT_DIR}")

    if os.environ.get("SKIP_EVAL", "0") != "1":
        subprocess.run(
            [sys.executable, str(BASE_DIR / "eval_baseline_crf.py"),
             "--split", "test", "--model_dir", OUTPUT_DIR, "--tag", RUN_TAG],
            check=True,
        )


if __name__ == "__main__":
    main()
