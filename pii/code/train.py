"""
skt/A.X-Encoder-base 기반 PII NER 풀 파인튜닝 (19개 라벨)

형태소 분석: kiwipiepy (Kiwi)
  - 형태소 단위 선분리 → BERT 서브워드 토크나이징
  - character-level BIO 태그를 word_ids() 로 토큰 단위 정렬
  - 첫 서브워드만 실제 레이블, 이후 서브워드는 -100 (loss 제외)

실행:
    python train.py                               # 기본 설정
    EPOCHS=30 LR=2e-5 python train.py            # 환경변수로 하이퍼파라미터 조정
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import torch
from kiwipiepy import Kiwi
from torch.utils.data import Dataset
from transformers import (
    AutoModelForTokenClassification,
    AutoTokenizer,
    DataCollatorForTokenClassification,
    Trainer,
    TrainerCallback,
    TrainingArguments,
)

# ── 형태소 분석기 (전역 1회 초기화) ──────────────────────────────────────────
_kiwi = Kiwi()

# ── 경로 ──────────────────────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).resolve().parent
DATA_DIR   = BASE_DIR / "data"
MODEL_ID   = os.environ.get("MODEL_ID",   "skt/A.X-Encoder-base")
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", str(BASE_DIR / "models" / "skt_encoder"))

# ── 하이퍼파라미터 ────────────────────────────────────────────────────────────
MAX_LEN      = int(os.environ.get("MAX_LEN",      "256"))
MICRO_BSZ    = int(os.environ.get("MICRO_BSZ",    "64"))   # A100 80GB → 64 충분
EPOCHS       = int(os.environ.get("EPOCHS",       "20"))
LR           = float(os.environ.get("LR",         "3e-5"))
WARMUP_R     = float(os.environ.get("WARMUP_R",   "0.06"))
WEIGHT_DECAY = float(os.environ.get("WEIGHT_DECAY","0.01"))
SEED         = int(os.environ.get("SEED",         "42"))
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


# ── Dataset ───────────────────────────────────────────────────────────────────
class PIIDataset(Dataset):
    """
    character-level BIO 태그를 Kiwi 형태소 → 서브워드 토큰 단위로 정렬.

    정렬 전략:
      - Kiwi.tokenize()로 형태소 목록 + 원문 시작 위치(start) 확보
      - tokenizer(morphemes, is_split_into_words=True)로 서브워드 인코딩
      - word_ids()로 각 서브워드 → 형태소 인덱스 매핑
      - 형태소의 원문 시작 위치 → labelling_seq[char] → LABEL2ID
      - 같은 형태소의 첫 서브워드만 실제 레이블, 이후는 -100
    """

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

        kiwi_toks   = _kiwi.tokenize(sentence)
        morphemes   = [t.form  for t in kiwi_toks] if kiwi_toks else [sentence]
        morph_start = [t.start for t in kiwi_toks] if kiwi_toks else [0]

        encoding = self.tokenizer(
            morphemes,
            is_split_into_words=True,
            truncation=True,
            max_length=self.max_length,
        )

        labels = []
        seen   = set()
        for wid in encoding.word_ids():
            if wid is None:
                labels.append(-100)
            elif wid in seen:
                labels.append(-100)
            else:
                seen.add(wid)
                c   = morph_start[wid]
                raw = char_labels[c] if c < len(char_labels) else "O"
                labels.append(LABEL2ID.get(raw, LABEL2ID["O"]))

        encoding["labels"] = labels
        return {k: torch.tensor(v) for k, v in encoding.items()}


# ── BIO → entity span 변환 ────────────────────────────────────────────────────
def bio_to_entities(bio_seq: list[str]) -> set[tuple]:
    """BIO 시퀀스 → {(start_idx, end_idx, label)} 집합."""
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


# ── Entity-level F1 계산 ──────────────────────────────────────────────────────
def compute_entity_f1(
    true_seqs: list[list[str]],
    pred_seqs: list[list[str]],
) -> dict:
    tp = fp = fn = 0
    per_label = {l: [0, 0, 0] for l in TARGET_LABELS}

    for true_seq, pred_seq in zip(true_seqs, pred_seqs):
        gold = bio_to_entities(true_seq)
        pred = bio_to_entities(pred_seq)

        tp += len(gold & pred)
        fp += len(pred - gold)
        fn += len(gold - pred)

        for span in gold & pred:
            if span[2] in per_label: per_label[span[2]][0] += 1
        for span in pred - gold:
            if span[2] in per_label: per_label[span[2]][1] += 1
        for span in gold - pred:
            if span[2] in per_label: per_label[span[2]][2] += 1

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


# ── compute_metrics (Trainer용) ───────────────────────────────────────────────
def make_compute_metrics(eval_dataset: PIIDataset):
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
        # 레이블별 F1 요약 출력 (0.0 제외)
        label_f1 = [(l, m[f"f1_{l}"]) for l in TARGET_LABELS if m.get(f"f1_{l}", 0) > 0]
        if label_f1:
            print("  " + "  ".join(f"{l}={v:.3f}" for l, v in sorted(label_f1, key=lambda x: -x[1])))
        return {"entity_micro_f1": m["micro_f1"]}

    return compute_metrics


# ── EarlyStopping + BestModel 콜백 ───────────────────────────────────────────
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
            self.best_f1  = f1
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


# ── main ─────────────────────────────────────────────────────────────────────
def main():
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)

    def load_json(name):
        return json.load(open(DATA_DIR / name, encoding="utf-8"))

    train_data = load_json("train.json")
    valid_data = load_json("valid.json")

    train_ds = PIIDataset(train_data, tokenizer, MAX_LEN)
    valid_ds = PIIDataset(valid_data, tokenizer, MAX_LEN)

    model = AutoModelForTokenClassification.from_pretrained(
        MODEL_ID,
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
    print(f"모델: {MODEL_ID}  |  레이블 {NUM_LABELS}개")
    print(f"Train {len(train_ds):,}  Valid {len(valid_ds):,}")
    print(f"Epochs={EPOCHS}  LR={LR}  BatchSize={MICRO_BSZ}  "
          f"MaxLen={MAX_LEN}  {'bf16' if use_bf16 else 'fp16'}")

    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        num_train_epochs=EPOCHS,
        per_device_train_batch_size=MICRO_BSZ,
        per_device_eval_batch_size=MICRO_BSZ,
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

    # 앙상블 모드(run_sk_ensemble.sh)에서는 시드별 단일 eval 을 건너뛰고
    # 마지막에 eval_ensemble.py 로 한 번에 평가한다.
    if os.environ.get("SKIP_EVAL", "0") == "1":
        print("\n학습 완료 — SKIP_EVAL=1 → 단일 eval 생략 (앙상블 모드).")
        return

    print("\n학습 완료 — test split 평가를 시작합니다...")
    subprocess.run(
        [sys.executable, str(BASE_DIR / "eval.py"), "--split", "test",
         "--model_dir", OUTPUT_DIR],
        check=True,
    )


if __name__ == "__main__":
    main()
