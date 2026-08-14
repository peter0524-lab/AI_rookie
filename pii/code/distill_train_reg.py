"""
챔피언(증강+KD) + R-Drop + FGM 정규화 학습

distill_train.py 의 KD 레시피(teacher soft-label, α·CE + (1-α)·T²·KL)를 그대로
재사용하고, 학습 시 두 정규화만 추가한다. 데이터·모델·라벨·평가 동일(공정 비교).

  1) R-Drop : 같은 배치를 dropout 2회 통과 → 두 출력분포를 대칭 KL 로 일치
              (RDROP_COEF>0 일 때). 결정경계를 넓히지 않아 precision 보존.
  2) FGM    : 임베딩(tok_embeddings)에 적대적 섭동을 더해 backward 1회 추가
              (FGM_EPS>0 일 때). 낯선 표면형에 견고성↑.

전제: GRAD_ACCUM=1 (챔피언과 동일) — training_step override 시 grad-accum 스케일
      복잡성 회피. 다른 값이면 경고.

실행 (챔피언과 동일 설정 + 정규화):
    TEACHER_DIR=models/klue_roberta_large/seed42 \
    MODEL_ID=skt/A.X-Encoder-base LR=3e-5 SEED=42 KD_ALPHA=0.5 KD_T=3.0 \
    TRAIN_FILE=train_aug.json MICRO_BSZ=64 GRAD_ACCUM=1 \
    RDROP_COEF=1.0 FGM_EPS=1.0 \
    OUTPUT_DIR=models/skt_encoder_distill_aug_reg/seed42 \
    RUN_TAG=seed42_reg python3 distill_train_reg.py
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import torch
import torch.nn.functional as F
from transformers import (
    AutoModelForTokenClassification,
    AutoTokenizer,
    TrainingArguments,
)

import distill_train as dt

BASE_DIR   = dt.BASE_DIR
DATA_DIR   = dt.DATA_DIR
MODELS_DIR = dt.MODELS_DIR
LABEL2ID   = dt.LABEL2ID
ID2LABEL   = dt.ID2LABEL
NUM_LABELS = dt.NUM_LABELS

MODEL_ID    = os.environ.get("MODEL_ID", "skt/A.X-Encoder-base")
TEACHER_DIR = os.environ.get("TEACHER_DIR", str(MODELS_DIR / "klue_roberta_large" / "seed42"))
SEED        = int(os.environ.get("SEED", "42"))
RUN_TAG     = os.environ.get("RUN_TAG", f"seed{SEED}_reg")
OUTPUT_DIR  = os.environ.get("OUTPUT_DIR", str(MODELS_DIR / "skt_encoder_distill_aug_reg" / f"seed{SEED}"))

MAX_LEN      = int(os.environ.get("MAX_LEN", "256"))
MICRO_BSZ    = int(os.environ.get("MICRO_BSZ", "64"))
GRAD_ACCUM   = int(os.environ.get("GRAD_ACCUM", "1"))
EPOCHS       = int(os.environ.get("EPOCHS", "20"))
LR           = float(os.environ.get("LR", "3e-5"))
WARMUP_R     = float(os.environ.get("WARMUP_R", "0.06"))
WEIGHT_DECAY = float(os.environ.get("WEIGHT_DECAY", "0.01"))
EVAL_STEPS   = int(os.environ.get("EVAL_STEPS", "500"))
ES_PATIENCE  = int(os.environ.get("ES_PATIENCE", "5"))

KD_ALPHA   = float(os.environ.get("KD_ALPHA", "0.5"))
KD_T       = float(os.environ.get("KD_T", "3.0"))

RDROP_COEF = float(os.environ.get("RDROP_COEF", "1.0"))
FGM_EPS    = float(os.environ.get("FGM_EPS", "1.0"))
FGM_EMB    = os.environ.get("FGM_EMB", "tok_embeddings")
SMOKE_N    = int(os.environ.get("SMOKE_N", "0"))

_O_IDX = LABEL2ID["O"]


class FGM:
    """임베딩 파라미터에 적대적 섭동 r = eps * g/||g|| 를 더하고 복원."""

    def __init__(self, model, emb_name):
        self.model = model
        self.emb_name = emb_name
        self.backup = {}

    def attack(self, eps):
        n_hit = 0
        for name, param in self.model.named_parameters():
            if param.requires_grad and self.emb_name in name and param.grad is not None:
                norm = torch.norm(param.grad)
                if norm != 0 and not torch.isnan(norm):
                    self.backup[name] = param.data.clone()
                    param.data.add_(eps * param.grad / norm)
                    n_hit += 1
        return n_hit

    def restore(self):
        for name, param in self.model.named_parameters():
            if name in self.backup:
                param.data = self.backup[name]
        self.backup = {}


class RegDistillTrainer(dt.DistillTrainer):
    def __init__(self, *args, rdrop_coef=1.0, fgm_eps=1.0, fgm_emb="tok_embeddings", **kwargs):
        super().__init__(*args, **kwargs)
        self.rdrop_coef = rdrop_coef
        self.fgm_eps = fgm_eps
        self.fgm_emb = fgm_emb
        self.fgm = FGM(self.model, fgm_emb) if fgm_eps > 0 else None
        self._fgm_logged = False

    def _ce_kd(self, logits, labels, soft_logits, mask):
        s_logits = logits[mask]
        hard = labels[mask]
        t_logits = soft_logits[mask]
        ce = F.cross_entropy(s_logits, hard)
        T = self.kd_t
        s_logp = F.log_softmax(s_logits / T, dim=-1)
        t_prob = F.softmax(t_logits / T, dim=-1)
        kd = F.kl_div(s_logp, t_prob, reduction="batchmean") * (T * T)
        return self.kd_alpha * ce + (1.0 - self.kd_alpha) * kd, s_logits

    def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
        soft_logits = inputs["soft_logits"]        # pop 하지 않음 (FGM 재호출 대비)
        labels = inputs["labels"]
        mask = labels != -100

        out1 = model(input_ids=inputs["input_ids"], attention_mask=inputs["attention_mask"])
        logits1 = out1.logits
        if mask.sum() == 0:
            loss = logits1.sum() * 0.0
            return (loss, out1) if return_outputs else loss

        loss1, s1 = self._ce_kd(logits1, labels, soft_logits, mask)

        if self.rdrop_coef > 0 and model.training:
            out2 = model(input_ids=inputs["input_ids"], attention_mask=inputs["attention_mask"])
            loss2, s2 = self._ce_kd(out2.logits, labels, soft_logits, mask)
            p = F.log_softmax(s1, dim=-1)
            q = F.log_softmax(s2, dim=-1)
            rdrop = 0.5 * (F.kl_div(p, q.exp(), reduction="batchmean")
                           + F.kl_div(q, p.exp(), reduction="batchmean"))
            loss = 0.5 * (loss1 + loss2) + self.rdrop_coef * rdrop
        else:
            loss = loss1

        return (loss, out1) if return_outputs else loss

    def training_step(self, model, inputs, *args, **kwargs):
        model.train()
        inputs = self._prepare_inputs(inputs)

        with self.compute_loss_context_manager():
            loss = self.compute_loss(model, inputs)
        if getattr(self.args, "n_gpu", 1) > 1:
            loss = loss.mean()
        self.accelerator.backward(loss)

        if self.fgm is not None and self.fgm_eps > 0:
            n_hit = self.fgm.attack(self.fgm_eps)
            if not self._fgm_logged:
                print(f"  [FGM] 섭동 적용 파라미터 {n_hit}개 (emb='{self.fgm_emb}')", flush=True)
                self._fgm_logged = True
            with self.compute_loss_context_manager():
                loss_adv = self.compute_loss(model, inputs)
            if getattr(self.args, "n_gpu", 1) > 1:
                loss_adv = loss_adv.mean()
            self.accelerator.backward(loss_adv)
            self.fgm.restore()

        return loss.detach()


def main():
    if GRAD_ACCUM != 1:
        print(f"[경고] GRAD_ACCUM={GRAD_ACCUM} (≠1) — FGM/R-Drop 스케일이 부정확할 수 있음.")
    if not Path(TEACHER_DIR, "config.json").exists():
        sys.exit(f"[ERROR] teacher 없음: {TEACHER_DIR}")

    device = "cuda" if torch.cuda.is_available() else "cpu"
    use_bf16 = torch.cuda.is_available() and torch.cuda.is_bf16_supported()

    student_tok = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True, use_fast=True)
    if not student_tok.is_fast:
        sys.exit(f"[ERROR] '{MODEL_ID}' fast tokenizer 필요.")

    teacher_tok = AutoTokenizer.from_pretrained(TEACHER_DIR, trust_remote_code=True, use_fast=True)
    teacher = AutoModelForTokenClassification.from_pretrained(
        TEACHER_DIR, trust_remote_code=True).to(device)
    teacher.eval()
    if use_bf16:
        teacher = teacher.to(torch.bfloat16)

    def load_json(name):
        return json.load(open(DATA_DIR / name, encoding="utf-8"))

    train_file = os.environ.get("TRAIN_FILE", "train_aug.json")
    train_data = load_json(train_file)
    valid_data = load_json("valid.json")
    if SMOKE_N > 0:
        train_data = train_data[:SMOKE_N]
        valid_data = valid_data[:SMOKE_N]
        print(f"[SMOKE] train/valid {SMOKE_N}개로 축소")

    print(f"GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'cpu'}")
    print(f"[KD+REG] student={MODEL_ID}  teacher={TEACHER_DIR}")
    print(f"  α={KD_ALPHA} T={KD_T} LR={LR} eff_bsz={MICRO_BSZ*GRAD_ACCUM} seed={SEED}")
    print(f"  RDROP_COEF={RDROP_COEF}  FGM_EPS={FGM_EPS}  FGM_EMB={FGM_EMB}")
    print(f"  OUTPUT_DIR={OUTPUT_DIR}  TRAIN_FILE={train_file}")
    print("teacher soft-label 사전 추출 중...")

    train_ds = dt.KDDataset(train_data, student_tok, teacher, teacher_tok, MAX_LEN, "train")
    valid_ds = dt.KDDataset(valid_data, student_tok, teacher, teacher_tok, MAX_LEN, "valid")

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

    trainer = RegDistillTrainer(
        model=student,
        args=args,
        train_dataset=train_ds,
        eval_dataset=valid_ds,
        data_collator=dt.KDCollator(student_tok.pad_token_id or 0),
        processing_class=student_tok,
        compute_metrics=dt.make_compute_metrics(),
        kd_alpha=KD_ALPHA,
        kd_t=KD_T,
        rdrop_coef=RDROP_COEF,
        fgm_eps=FGM_EPS,
        fgm_emb=FGM_EMB,
    )

    best_cb = dt.SaveBestCallback(trainer, OUTPUT_DIR, ES_PATIENCE, WARMUP_R)
    trainer.add_callback(best_cb)

    trainer.train()

    if best_cb.best_f1 < 0:
        trainer.save_model(OUTPUT_DIR)

    if trainer.is_world_process_zero():
        student_tok.save_pretrained(OUTPUT_DIR)
        json.dump({
            "label2id": LABEL2ID,
            "id2label": {str(k): v for k, v in ID2LABEL.items()},
            "target_labels": dt.TARGET_LABELS,
            "morpheme": False,
            "model_id": MODEL_ID,
            "teacher_dir": TEACHER_DIR,
            "kd_alpha": KD_ALPHA,
            "kd_t": KD_T,
            "rdrop_coef": RDROP_COEF,
            "fgm_eps": FGM_EPS,
            "run_tag": RUN_TAG,
        }, open(Path(OUTPUT_DIR) / "label_map.json", "w", encoding="utf-8"),
            ensure_ascii=False, indent=2)
        print(f"\n학습 완료 | best entity_micro_f1={best_cb.best_f1:.4f} → {OUTPUT_DIR}")

    if torch.distributed.is_initialized():
        torch.distributed.destroy_process_group()
    if int(os.environ.get("LOCAL_RANK", "0")) != 0:
        sys.exit(0)

    if os.environ.get("SKIP_EVAL", "0") == "1":
        print("\nSKIP_EVAL=1 → test 평가 생략.")
        return

    print("\n학습 완료 — test 평가(eval_baseline.py) 시작...")
    subprocess.run(
        [sys.executable, str(BASE_DIR / "eval_baseline.py"),
         "--split", "test", "--model_dir", OUTPUT_DIR, "--tag", RUN_TAG],
        check=True,
    )


if __name__ == "__main__":
    main()
