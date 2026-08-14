"""
지식 증류(Knowledge Distillation) — Teacher(KLUE 등) → Student(SKT 0.1B)

목적: 0.1B SKT A.X-Encoder-base 가 큰 teacher(KLUE RoBERTa-large)의
      세만틱 엔티티 인식력(OG_WORKPLACE / CV_POSITION / PS_NAME 등 recall)을
      흡수해 단일 large 모델을 추월하도록 학습.

핵심 설계:
  - Student/Teacher 토크나이저가 다르므로 **char 단위로 teacher logit 을 정렬**.
      teacher token 의 logit 을 그 토큰이 덮는 모든 char 에 복사 → student
      라벨 토큰의 시작 char 위치에서 teacher 분포를 gather.
  - 라벨 공간(39 BIO)은 teacher config.id2label 로 재정렬하여 일치 보장.
  - Loss = α·CE(hard) + (1-α)·T²·KL(teacher_soft ∥ student_soft)
      (라벨 위치, 즉 어절 첫 서브워드에서만 적용 — hard 라벨과 동일 위치)

정렬/평가/지표는 train_baseline.py 와 동일(무형태소, eval_baseline.py).

실행:
    TEACHER_DIR=models/klue_roberta_large/seed42 \
    MODEL_ID=skt/A.X-Encoder-base LR=3e-5 SEED=42 \
    KD_ALPHA=0.5 KD_T=3.0 python3 distill_train.py
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from torch.utils.data import Dataset
from transformers import (
    AutoModelForTokenClassification,
    AutoTokenizer,
    Trainer,
    TrainerCallback,
    TrainingArguments,
)

# ── 경로 / 모델 ─────────────────────────────────────────────────────────────────
BASE_DIR    = Path(__file__).resolve().parent
_data_raw   = os.environ.get("DATA_DIR", "data")
DATA_DIR    = Path(_data_raw) if Path(_data_raw).is_absolute() else BASE_DIR / _data_raw
MODELS_DIR  = BASE_DIR / "models"

MODEL_ID    = os.environ.get("MODEL_ID", "skt/A.X-Encoder-base")          # student
TEACHER_DIR = os.environ.get("TEACHER_DIR", str(MODELS_DIR / "klue_roberta_large" / "seed42"))

SEED        = int(os.environ.get("SEED", "42"))
RUN_TAG     = os.environ.get("RUN_TAG", f"seed{SEED}_distill")
OUTPUT_DIR  = os.environ.get(
    "OUTPUT_DIR", str(MODELS_DIR / "skt_encoder_distill" / f"seed{SEED}")
)

# ── 하이퍼파라미터 ────────────────────────────────────────────────────────────
MAX_LEN      = int(os.environ.get("MAX_LEN",      "256"))
MICRO_BSZ    = int(os.environ.get("MICRO_BSZ",    "64"))
GRAD_ACCUM   = int(os.environ.get("GRAD_ACCUM",   "1"))
EPOCHS       = int(os.environ.get("EPOCHS",       "20"))
LR           = float(os.environ.get("LR",         "3e-5"))
WARMUP_R     = float(os.environ.get("WARMUP_R",   "0.06"))
WEIGHT_DECAY = float(os.environ.get("WEIGHT_DECAY","0.01"))
EVAL_STEPS   = int(os.environ.get("EVAL_STEPS",   "500"))
ES_PATIENCE  = int(os.environ.get("ES_PATIENCE",  "5"))

# ── 증류 하이퍼파라미터 ───────────────────────────────────────────────────────
KD_ALPHA     = float(os.environ.get("KD_ALPHA", "0.5"))   # hard CE 비중
KD_T         = float(os.environ.get("KD_T",     "3.0"))   # 온도
TEACHER_BSZ  = int(os.environ.get("TEACHER_BSZ", "64"))   # teacher 사전추출 배치

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

_O_IDX = LABEL2ID["O"]


# ── Teacher logit 사전 추출 (char 단위 → student 라벨 토큰 정렬) ───────────────
def _teacher_column_map(teacher_model) -> list[int]:
    """teacher logit 열 → 우리 LABEL2ID 순서로 재정렬하기 위한 인덱스."""
    cfg = teacher_model.config
    id2label = getattr(cfg, "id2label", None)
    if not id2label:
        # 동일 순서 가정
        return list(range(NUM_LABELS))
    # teacher_col_for_our[our_idx] = teacher 열 인덱스
    label_to_tcol = {}
    for tcol, lab in id2label.items():
        label_to_tcol[lab] = int(tcol)
    cols = []
    for our_idx in range(NUM_LABELS):
        lab = ID2LABEL[our_idx]
        cols.append(label_to_tcol.get(lab, _O_IDX))
    return cols


class KDDataset(Dataset):
    """
    student 인코딩(무형태소 offset 정렬) + teacher soft logit 동시 보유.

    각 example:
      input_ids, attention_mask, labels(hard, -100 패딩),
      soft_logits[seq_len, 39]  (라벨 위치엔 teacher 분포, 그 외 O-favor fallback)
    """

    def __init__(self, data, student_tok, teacher_model, teacher_tok,
                 max_length=256, split_name=""):
        self.examples = []
        col_map = _teacher_column_map(teacher_model)
        device = next(teacher_model.parameters()).device

        # 1) student 인코딩 + 라벨 토큰의 char 시작 위치(cs) 기록
        enc_inputs, enc_masks, enc_labels, enc_cs, sentences = [], [], [], [], []
        for item in data:
            sentence    = item["sentence"]
            char_labels = item["labelling_seq"]
            enc = student_tok(sentence, truncation=True, max_length=max_length,
                              return_offsets_mapping=True)
            word_ids = enc.word_ids()
            offsets  = enc["offset_mapping"]
            labels, cs_list, seen = [], [], set()
            for wid, (cs, ce) in zip(word_ids, offsets):
                if wid is None or ce == 0 or wid in seen:
                    labels.append(-100)
                    cs_list.append(-1)
                else:
                    seen.add(wid)
                    raw = char_labels[cs] if cs < len(char_labels) else "O"
                    labels.append(LABEL2ID.get(raw, _O_IDX))
                    cs_list.append(cs)
            enc_inputs.append(enc["input_ids"])
            enc_masks.append(enc["attention_mask"])
            enc_labels.append(labels)
            enc_cs.append(cs_list)
            sentences.append(sentence)

        # 2) teacher 배치 추론 → char 단위 logit → student cs 위치에서 gather
        n = len(sentences)
        fallback = np.full(NUM_LABELS, -10.0, dtype=np.float32)
        fallback[_O_IDX] = 10.0

        for bs in range(0, n, TEACHER_BSZ):
            bsent = sentences[bs: bs + TEACHER_BSZ]
            t_enc = teacher_tok(bsent, truncation=True, max_length=max_length,
                                padding=True, return_offsets_mapping=True,
                                return_tensors="pt")
            offs = t_enc.pop("offset_mapping")
            t_enc = {k: v.to(device) for k, v in t_enc.items()}
            with torch.inference_mode():
                logits = teacher_model(**t_enc).logits.float().cpu().numpy()  # [B,T,Ct]
            logits = logits[:, :, col_map]  # 우리 라벨 순서로 재정렬 → [B,T,39]

            for bi, sent in enumerate(bsent):
                gi = bs + bi
                slen = len(sent)
                char_logit = np.tile(fallback, (slen, 1))  # [slen,39]
                tok_off = offs[bi].tolist()
                for tpos, (ts, te) in enumerate(tok_off):
                    if te == 0 or ts >= slen:   # 특수/패딩
                        continue
                    char_logit[ts:min(te, slen)] = logits[bi, tpos]
                # student 라벨 토큰 위치에 teacher 분포 매핑
                cs_list = enc_cs[gi]
                soft = np.tile(fallback, (len(cs_list), 1)).astype(np.float16)
                for k, cs in enumerate(cs_list):
                    if 0 <= cs < slen:
                        soft[k] = char_logit[cs]
                self.examples.append({
                    "input_ids": enc_inputs[gi],
                    "attention_mask": enc_masks[gi],
                    "labels": enc_labels[gi],
                    "soft_logits": soft,   # [seq_len,39] float16
                })
            if split_name and (bs // TEACHER_BSZ) % 20 == 0:
                print(f"  [teacher:{split_name}] {min(bs+TEACHER_BSZ, n)}/{n}", flush=True)

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, idx):
        ex = self.examples[idx]
        return {
            "input_ids": torch.tensor(ex["input_ids"], dtype=torch.long),
            "attention_mask": torch.tensor(ex["attention_mask"], dtype=torch.long),
            "labels": torch.tensor(ex["labels"], dtype=torch.long),
            "soft_logits": torch.tensor(ex["soft_logits"], dtype=torch.float),
        }


# ── Collator (soft_logits 까지 패딩) ──────────────────────────────────────────
class KDCollator:
    def __init__(self, pad_token_id):
        self.pad_token_id = pad_token_id

    def __call__(self, features):
        max_len = max(len(f["input_ids"]) for f in features)
        input_ids, attn, labels, soft = [], [], [], []
        for f in features:
            L = len(f["input_ids"])
            pad = max_len - L
            input_ids.append(torch.cat([f["input_ids"],
                              torch.full((pad,), self.pad_token_id, dtype=torch.long)]))
            attn.append(torch.cat([f["attention_mask"],
                              torch.zeros(pad, dtype=torch.long)]))
            labels.append(torch.cat([f["labels"],
                              torch.full((pad,), -100, dtype=torch.long)]))
            soft.append(torch.cat([f["soft_logits"],
                              torch.zeros(pad, NUM_LABELS, dtype=torch.float)], dim=0))
        return {
            "input_ids": torch.stack(input_ids),
            "attention_mask": torch.stack(attn),
            "labels": torch.stack(labels),
            "soft_logits": torch.stack(soft),
        }


# ── KD Trainer ────────────────────────────────────────────────────────────────
class DistillTrainer(Trainer):
    def __init__(self, *args, kd_alpha=0.5, kd_t=3.0, **kwargs):
        super().__init__(*args, **kwargs)
        self.kd_alpha = kd_alpha
        self.kd_t     = kd_t

    def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
        soft_logits = inputs.pop("soft_logits")
        labels      = inputs["labels"]
        outputs     = model(input_ids=inputs["input_ids"],
                            attention_mask=inputs["attention_mask"])
        logits = outputs.logits  # [B,T,39]

        mask = labels != -100
        if mask.sum() == 0:
            loss = logits.sum() * 0.0
            return (loss, outputs) if return_outputs else loss

        s_logits = logits[mask]              # [N,39]
        hard     = labels[mask]              # [N]
        t_logits = soft_logits[mask]         # [N,39]

        ce = F.cross_entropy(s_logits, hard)

        T = self.kd_t
        s_logp = F.log_softmax(s_logits / T, dim=-1)
        t_prob = F.softmax(t_logits / T, dim=-1)
        kd = F.kl_div(s_logp, t_prob, reduction="batchmean") * (T * T)

        loss = self.kd_alpha * ce + (1.0 - self.kd_alpha) * kd
        return (loss, outputs) if return_outputs else loss


# ── 평가 지표 (train_baseline.py 와 동일) ─────────────────────────────────────
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
    per_label = {l: [0, 0, 0] for l in TARGET_LABELS}
    for true_seq, pred_seq in zip(true_seqs, pred_seqs):
        gold = bio_to_entities(true_seq)
        pred = bio_to_entities(pred_seq)
        tp += len(gold & pred); fp += len(pred - gold); fn += len(gold - pred)
        for s in gold & pred:
            if s[2] in per_label: per_label[s[2]][0] += 1
        for s in pred - gold:
            if s[2] in per_label: per_label[s[2]][1] += 1
        for s in gold - pred:
            if s[2] in per_label: per_label[s[2]][2] += 1

    def f1(t, fp_, fn_):
        p = t / (t + fp_) if (t + fp_) else 0.0
        r = t / (t + fn_) if (t + fn_) else 0.0
        return (2 * p * r / (p + r) if (p + r) else 0.0), p, r

    micro_f1, micro_p, micro_r = f1(tp, fp, fn)
    res = {"micro_f1": micro_f1, "micro_p": micro_p, "micro_r": micro_r}
    for lbl, (t, fp_, fn_) in per_label.items():
        res[f"f1_{lbl}"], _, _ = f1(t, fp_, fn_)
    return res


def make_compute_metrics():
    def compute_metrics(eval_preds):
        logits, labels_arr = eval_preds
        preds_arr = np.argmax(logits, axis=-1)
        true_seqs, pred_seqs = [], []
        for pred_row, label_row in zip(preds_arr, labels_arr):
            t_seq, p_seq = [], []
            for p, l in zip(pred_row, label_row):
                if l == -100:
                    continue
                t_seq.append(ID2LABEL[l]); p_seq.append(ID2LABEL[int(p)])
            true_seqs.append(t_seq); pred_seqs.append(p_seq)
        m = compute_entity_f1(true_seqs, pred_seqs)
        print(f"\n  [Eval] Micro F1={m['micro_f1']:.4f}  "
              f"P={m['micro_p']:.4f}  R={m['micro_r']:.4f}")
        label_f1 = [(l, m[f"f1_{l}"]) for l in TARGET_LABELS if m.get(f"f1_{l}", 0) > 0]
        if label_f1:
            print("  " + "  ".join(f"{l}={v:.3f}" for l, v in sorted(label_f1, key=lambda x: -x[1])))
        return {"entity_micro_f1": m["micro_f1"]}
    return compute_metrics


class SaveBestCallback(TrainerCallback):
    def __init__(self, trainer, save_dir, patience=5, warmup_ratio=0.06):
        self.trainer = trainer; self.save_dir = save_dir
        self.best_f1 = -1.0; self.patience = patience
        self.warmup_ratio = warmup_ratio; self.no_improve = 0

    def on_evaluate(self, args, state, control, metrics=None, **kwargs):
        if not metrics:
            return
        f1 = metrics.get("eval_entity_micro_f1", -1.0)
        if f1 > self.best_f1:
            self.best_f1 = f1; self.no_improve = 0
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
                    print(f"  Early stopping: {self.patience}번 연속 미개선")
                control.should_training_stop = True


# ── main ─────────────────────────────────────────────────────────────────────
def main():
    if not Path(TEACHER_DIR, "config.json").exists():
        sys.exit(f"[ERROR] teacher 모델 없음: {TEACHER_DIR}")

    device = "cuda" if torch.cuda.is_available() else "cpu"
    use_bf16 = torch.cuda.is_available() and torch.cuda.is_bf16_supported()

    student_tok = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True, use_fast=True)
    if not student_tok.is_fast:
        sys.exit(f"[ERROR] '{MODEL_ID}' fast tokenizer 필요(offset 정렬).")

    teacher_tok = AutoTokenizer.from_pretrained(TEACHER_DIR, trust_remote_code=True, use_fast=True)
    teacher = AutoModelForTokenClassification.from_pretrained(
        TEACHER_DIR, trust_remote_code=True).to(device)
    teacher.eval()
    if use_bf16:
        teacher = teacher.to(torch.bfloat16)

    def load_json(name):
        return json.load(open(DATA_DIR / name, encoding="utf-8"))

    train_file = os.environ.get("TRAIN_FILE", "train.json")
    valid_file = os.environ.get("VALID_FILE", "valid.json")
    train_data = load_json(train_file)
    valid_data = load_json(valid_file)
    if train_file != "train.json" or valid_file != "valid.json" or str(DATA_DIR) != str(BASE_DIR / "data"):
        print(f"[data] DATA_DIR={DATA_DIR}  TRAIN_FILE={train_file}  VALID_FILE={valid_file}")

    print(f"GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'cpu'}")
    print(f"[KD] student={MODEL_ID}  teacher={TEACHER_DIR}")
    print(f"     α={KD_ALPHA}  T={KD_T}  LR={LR}  eff_bsz={MICRO_BSZ*GRAD_ACCUM}  seed={SEED}")
    print(f"     OUTPUT_DIR={OUTPUT_DIR}")
    print("teacher soft-label 사전 추출 중...")

    train_ds = KDDataset(train_data, student_tok, teacher, teacher_tok, MAX_LEN, "train")
    valid_ds = KDDataset(valid_data, student_tok, teacher, teacher_tok, MAX_LEN, "valid")

    # teacher 해제 (student 학습 VRAM 확보)
    del teacher
    torch.cuda.empty_cache()

    student = AutoModelForTokenClassification.from_pretrained(
        MODEL_ID, num_labels=NUM_LABELS, id2label=ID2LABEL, label2id=LABEL2ID,
        trust_remote_code=True, ignore_mismatched_sizes=True,
    )

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
    )

    trainer = DistillTrainer(
        model=student,
        args=args,
        train_dataset=train_ds,
        eval_dataset=valid_ds,
        data_collator=KDCollator(student_tok.pad_token_id or 0),
        processing_class=student_tok,
        compute_metrics=make_compute_metrics(),
        kd_alpha=KD_ALPHA,
        kd_t=KD_T,
    )

    best_cb = SaveBestCallback(trainer, OUTPUT_DIR, ES_PATIENCE, WARMUP_R)
    trainer.add_callback(best_cb)

    trainer.train()

    if best_cb.best_f1 < 0:
        trainer.save_model(OUTPUT_DIR)

    if trainer.is_world_process_zero():
        student_tok.save_pretrained(OUTPUT_DIR)
        json.dump({
            "label2id": LABEL2ID,
            "id2label": {str(k): v for k, v in ID2LABEL.items()},
            "target_labels": TARGET_LABELS,
            "morpheme": False,
            "model_id": MODEL_ID,
            "teacher_dir": TEACHER_DIR,
            "use_crf": False,
            "use_gazetteer": False,
            "use_rdrop": False,
            "use_fgm": False,
            "use_kd": True,
            "kd_alpha": KD_ALPHA,
            "kd_t": KD_T,
            "run_tag": RUN_TAG,
        }, open(Path(OUTPUT_DIR) / "label_map.json", "w", encoding="utf-8"),
            ensure_ascii=False, indent=2)
        print(f"\n학습 완료  |  best entity_micro_f1={best_cb.best_f1:.4f}  →  {OUTPUT_DIR}")

    if torch.distributed.is_initialized():
        torch.distributed.destroy_process_group()
    if int(os.environ.get("LOCAL_RANK", "0")) != 0:
        sys.exit(0)

    if os.environ.get("SKIP_EVAL", "0") == "1":
        print("\n학습 완료 — SKIP_EVAL=1 → test 평가 생략.")
        return

    data_dir = os.environ.get("DATA_DIR", "data")
    print(f"\n학습 완료 — test split 평가(eval_baseline.py)를 시작합니다... (data-dir={data_dir})")
    subprocess.run(
        [sys.executable, str(BASE_DIR / "eval_baseline.py"),
         "--split", "test", "--model_dir", OUTPUT_DIR, "--tag", RUN_TAG,
         "--data-dir", data_dir],
        check=True,
    )


if __name__ == "__main__":
    main()
