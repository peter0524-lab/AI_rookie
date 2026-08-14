"""
DAPT (Domain-Adaptive Pre-Training) — SKT 0.1B(ModernBERT) MLM 이어학습

목적: skt/A.X-Encoder-base 를 한국어 위키 코퍼스로 MLM 이어학습(도메인 적응)하여
      '세상지식(회사·인명 등)' 을 주입한 뒤, 그 체크포인트를 파인튜닝/증류의
      MODEL_ID 로 사용한다.

핵심:
  - AutoModelForMaskedLM (ModernBertForMaskedLM) — 베이스와 동일 아키텍처/토크나이저.
  - DataCollatorForLanguageModeling(mlm_probability) 로 동적 마스킹.
    ModernBERT 권장 마스킹률 0.30(기본값). 파일럿은 보수적으로 조정 가능.
  - '무개선이 최악' 이 되도록 보수적 하이퍼파라미터(낮은 LR, 짧은 에폭).
  - vocab 은 그대로 → 파인튜닝 코드(train_baseline / distill_train)가 MODEL_ID 로
    이 폴더를 그대로 물릴 수 있음.

출력: models/skt_encoder_dapt  (config + weights + tokenizer)

실행:
    CORPUS=dapt/dapt_corpus.txt EPOCHS=1 LR=5e-5 python3 dapt_train.py
    # flash-attn 설치 환경이면:
    ATTN_IMPL=flash_attention_2 python3 dapt_train.py
"""

import math
import os
from pathlib import Path

import torch
from torch.utils.data import Dataset
from transformers import (
    AutoModelForMaskedLM,
    AutoTokenizer,
    DataCollatorForLanguageModeling,
    Trainer,
    TrainingArguments,
)

BASE_DIR   = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "models"

MODEL_ID   = os.environ.get("MODEL_ID", "skt/A.X-Encoder-base")
CORPUS     = os.environ.get("CORPUS", str(BASE_DIR / "dapt" / "dapt_corpus.txt"))
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", str(MODELS_DIR / "skt_encoder_dapt"))

MAX_LEN    = int(os.environ.get("MAX_LEN", "256"))          # 파인튜닝과 동일
MLM_PROB   = float(os.environ.get("MLM_PROB", "0.30"))       # ModernBERT 권장
MICRO_BSZ  = int(os.environ.get("MICRO_BSZ", "64"))
GRAD_ACCUM = int(os.environ.get("GRAD_ACCUM", "1"))
EPOCHS     = float(os.environ.get("EPOCHS", "1"))
LR         = float(os.environ.get("LR", "5e-5"))            # 보수적(이어학습)
WARMUP_R   = float(os.environ.get("WARMUP_R", "0.06"))
WEIGHT_DECAY = float(os.environ.get("WEIGHT_DECAY", "0.01"))
SEED       = int(os.environ.get("SEED", "42"))
SAVE_STEPS = int(os.environ.get("SAVE_STEPS", "2000"))
LOG_STEPS  = int(os.environ.get("LOG_STEPS", "100"))
ATTN_IMPL  = os.environ.get("ATTN_IMPL", "sdpa")           # flash-attn 없어도 동작
MAX_LINES  = int(os.environ.get("MAX_LINES", "0"))          # 0=전체


class LineByLineDataset(Dataset):
    """코퍼스 각 줄 = 1 example. 동적 마스킹은 collator 가 담당."""

    def __init__(self, path: str, tokenizer, max_length: int, max_lines: int = 0):
        self.lines = []
        with open(path, encoding="utf-8") as f:
            for i, line in enumerate(f):
                line = line.strip()
                if line:
                    self.lines.append(line)
                if max_lines and len(self.lines) >= max_lines:
                    break
        self.tok = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.lines)

    def __getitem__(self, idx):
        enc = self.tok(
            self.lines[idx],
            truncation=True,
            max_length=self.max_length,
        )
        return {"input_ids": enc["input_ids"],
                "attention_mask": enc["attention_mask"]}


def main():
    use_bf16 = torch.cuda.is_available() and torch.cuda.is_bf16_supported()

    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True, use_fast=True)
    if tokenizer.mask_token is None:
        raise SystemExit(f"[ERROR] '{MODEL_ID}' mask_token 없음 → MLM 불가.")

    model = AutoModelForMaskedLM.from_pretrained(
        MODEL_ID,
        trust_remote_code=True,
        attn_implementation=ATTN_IMPL,
        dtype=torch.bfloat16 if use_bf16 else None,
    )

    if not Path(CORPUS).exists():
        raise SystemExit(f"[ERROR] 코퍼스 없음: {CORPUS} (먼저 dapt_prep.py 실행)")

    ds = LineByLineDataset(CORPUS, tokenizer, MAX_LEN, MAX_LINES)

    if torch.cuda.is_available():
        print(f"GPU: {torch.cuda.get_device_name(0)}  attn={ATTN_IMPL}")
    print(f"[DAPT] model={MODEL_ID}  corpus={CORPUS}")
    print(f"       lines={len(ds):,}  MLM_prob={MLM_PROB}  max_len={MAX_LEN}")
    print(f"       epochs={EPOCHS}  LR={LR}  eff_bsz={MICRO_BSZ*GRAD_ACCUM}  seed={SEED}")
    print(f"       OUTPUT_DIR={OUTPUT_DIR}")

    collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer, mlm=True, mlm_probability=MLM_PROB,
    )

    args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        num_train_epochs=EPOCHS,
        per_device_train_batch_size=MICRO_BSZ,
        gradient_accumulation_steps=GRAD_ACCUM,
        learning_rate=LR,
        warmup_ratio=WARMUP_R,
        lr_scheduler_type="cosine",
        weight_decay=WEIGHT_DECAY,
        max_grad_norm=1.0,
        bf16=use_bf16,
        fp16=not use_bf16 and torch.cuda.is_available(),
        logging_steps=LOG_STEPS,
        save_strategy="steps",
        save_steps=SAVE_STEPS,
        save_total_limit=1,
        report_to="none",
        seed=SEED,
        dataloader_num_workers=4,
    )

    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=ds,
        data_collator=collator,
        processing_class=tokenizer,
    )

    result = trainer.train()

    trainer.save_model(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)

    loss = result.training_loss
    try:
        ppl = math.exp(loss)
    except OverflowError:
        ppl = float("inf")
    print(f"\n[DAPT 완료] train_loss={loss:.4f}  ppl≈{ppl:.2f}")
    print(f"  → {OUTPUT_DIR}")
    print(f"  이후: MODEL_ID={OUTPUT_DIR} 로 train_baseline.py / distill_train.py 실행")


if __name__ == "__main__":
    main()
