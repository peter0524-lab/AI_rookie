"""
챔피언(KD+증강) + CRF + Gazetteer + R-Drop + FGM

chan 0.964 레시피를 hwan 파이프라인에 이식:
  - gazetteer: train 표면형 + 접미사 → 모델 입력 피처
  - CRF: BIO 전이 제약 + Viterbi decode
  - KD: 기존 KLUE teacher (hwan 체크포인트 재사용)
  - R-Drop + FGM: chan 과 동일 계수 (RDROP_ALPHA=4.0)

실행:
    TEACHER_DIR=models/klue_roberta_large/seed42 \\
    MODEL_ID=skt/A.X-Encoder-base USE_CRF=1 USE_GAZETTEER=1 \\
    USE_RDROP=1 USE_FGM=1 RDROP_ALPHA=4.0 FGM_EPSILON=1.0 \\
    KD_ALPHA=0.5 KD_T=3.0 TRAIN_FILE=train_aug.json SEED=42 \\
    OUTPUT_DIR=models/skt_encoder_distill_crf_gaz_reg/seed42 \\
    python3 distill_train_crf_gaz.py
"""

import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from torch.utils.data import Dataset
from transformers import AutoModelForTokenClassification, AutoTokenizer, Trainer, TrainingArguments

import distill_train as dt
from eval_crf_gaz import ManualEvalCallback
from gazetteer import GazetteerTrie, aggregate_to_tokens, build_gazetteer, save_gazetteer
from pii_model import TokenClassifierForPII, build_model, compact_sequence
from pii_regularization import FGM, rdrop_kl_loss

BASE_DIR = dt.BASE_DIR
_data_raw = os.environ.get("DATA_DIR", "data")
DATA_DIR = Path(_data_raw) if Path(_data_raw).is_absolute() else BASE_DIR / _data_raw
MODELS_DIR = dt.MODELS_DIR
TARGET_LABELS = dt.TARGET_LABELS
LABEL2ID = dt.LABEL2ID
ID2LABEL = dt.ID2LABEL
NUM_LABELS = dt.NUM_LABELS
NUM_GAZ_LABELS = len(TARGET_LABELS)
_O_IDX = LABEL2ID["O"]

MODEL_ID = os.environ.get("MODEL_ID", "skt/A.X-Encoder-base")
TEACHER_DIR = os.environ.get("TEACHER_DIR", str(MODELS_DIR / "klue_roberta_large" / "seed42"))

USE_CRF = os.environ.get("USE_CRF", "1") == "1"
USE_GAZETTEER = os.environ.get("USE_GAZETTEER", "1") == "1"
GAZ_EMB_DIM = int(os.environ.get("GAZ_EMB_DIM", "32"))
USE_RDROP = os.environ.get("USE_RDROP", "1") == "1"
RDROP_ALPHA = float(os.environ.get("RDROP_ALPHA", "4.0"))
USE_FGM = os.environ.get("USE_FGM", "1") == "1"
FGM_EPSILON = float(os.environ.get("FGM_EPSILON", "1.0"))

USE_KD = os.environ.get("USE_KD", "1") == "1"
KD_ALPHA = float(os.environ.get("KD_ALPHA", "0.5"))
KD_T = float(os.environ.get("KD_T", "3.0"))
TEACHER_BSZ = int(os.environ.get("TEACHER_BSZ", "64"))

MAX_LEN = int(os.environ.get("MAX_LEN", "256"))
MICRO_BSZ = int(os.environ.get("MICRO_BSZ", "64"))
GRAD_ACCUM = int(os.environ.get("GRAD_ACCUM", "1"))
EPOCHS = int(os.environ.get("EPOCHS", "20"))
LR = float(os.environ.get("LR", "3e-5"))
WARMUP_R = float(os.environ.get("WARMUP_R", "0.06"))
WEIGHT_DECAY = float(os.environ.get("WEIGHT_DECAY", "0.01"))
SEED = int(os.environ.get("SEED", "42"))
EVAL_STEPS = int(os.environ.get("EVAL_STEPS", "500"))
ES_PATIENCE = int(os.environ.get("ES_PATIENCE", "5"))
SMOKE_N = int(os.environ.get("SMOKE_N", "0"))


def _combo_tag() -> str:
    parts = ["distill"] if USE_KD else ["crf_gaz"]
    if USE_CRF:
        parts.append("crf")
    if USE_GAZETTEER:
        parts.append("gaz")
    if USE_RDROP:
        parts.append("rdrop")
    if USE_FGM:
        parts.append("fgm")
    return "_".join(parts)


RUN_TAG = os.environ.get("RUN_TAG", f"{_combo_tag()}_seed{SEED}")
OUTPUT_DIR = os.environ.get(
    "OUTPUT_DIR", str(MODELS_DIR / "skt_encoder_distill_crf_gaz_reg" / f"seed{SEED}")
)


class KDGazDataset(Dataset):
    """distill_train.KDDataset + gazetteer 피처."""

    def __init__(self, data, student_tok, teacher_model, teacher_tok, device,
                 max_length=256, gaz_trie=None, split_name=""):
        self.examples = []
        col_map = dt._teacher_column_map(teacher_model)
        fallback = np.full(NUM_LABELS, -10.0, dtype=np.float32)
        fallback[_O_IDX] = 10.0

        sentences = [item["sentence"] for item in data]
        char_labels_all = [item["labelling_seq"] for item in data]
        enc_list = [
            student_tok(s, truncation=True, max_length=max_length, return_offsets_mapping=True)
            for s in sentences
        ]

        n = len(sentences)
        for bs in range(0, n, TEACHER_BSZ):
            b_idx = list(range(bs, min(bs + TEACHER_BSZ, n)))
            b_sent = [sentences[i] for i in b_idx]
            t_enc = teacher_tok(
                b_sent, truncation=True, max_length=max_length, padding=True,
                return_offsets_mapping=True, return_tensors="pt",
            )
            t_offs = t_enc.pop("offset_mapping").tolist()
            t_enc = {k: v.to(device) for k, v in t_enc.items()}
            with torch.inference_mode():
                t_logits = teacher_model(**t_enc).logits.float().cpu().numpy()
            t_logits = t_logits[:, :, col_map]

            for bi, gi in enumerate(b_idx):
                sent = sentences[gi]
                slen = len(sent)
                char_logit = np.tile(fallback, (slen, 1))
                for tpos, (ts, te) in enumerate(t_offs[bi]):
                    if te == 0 or ts >= slen:
                        continue
                    char_logit[ts:min(te, slen)] = t_logits[bi, tpos]

                enc = enc_list[gi]
                word_ids = enc.word_ids()
                offsets = enc["offset_mapping"]
                char_labels = char_labels_all[gi]
                labels, soft, seen = [], [], set()
                for wid, (cs, ce) in zip(word_ids, offsets):
                    if wid is None or ce == 0 or wid in seen:
                        labels.append(-100)
                        soft.append(fallback)
                    else:
                        seen.add(wid)
                        raw = char_labels[cs] if cs < len(char_labels) else "O"
                        labels.append(LABEL2ID.get(raw, _O_IDX))
                        soft.append(char_logit[cs] if cs < slen else fallback)

                ex = {
                    "input_ids": enc["input_ids"],
                    "attention_mask": enc["attention_mask"],
                    "labels": labels,
                    "soft_logits": np.array(soft, dtype=np.float32),
                }
                if gaz_trie is not None:
                    gfeat = gaz_trie.match_sentence(sent)
                    ex["gaz_features"] = aggregate_to_tokens(gfeat, offsets)
                self.examples.append(ex)

            if split_name and (bs // TEACHER_BSZ) % 20 == 0:
                print(f"  [teacher:{split_name}] {min(bs + TEACHER_BSZ, n)}/{n}", flush=True)

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, idx):
        ex = self.examples[idx]
        out = {
            "input_ids": torch.tensor(ex["input_ids"], dtype=torch.long),
            "attention_mask": torch.tensor(ex["attention_mask"], dtype=torch.long),
            "labels": torch.tensor(ex["labels"], dtype=torch.long),
            "soft_logits": torch.tensor(ex["soft_logits"], dtype=torch.float32),
        }
        if "gaz_features" in ex:
            out["gaz_features"] = torch.tensor(ex["gaz_features"], dtype=torch.float32)
        return out


class HardGazDataset(Dataset):
    """hard-label only (no teacher) — CRF+gazetteer+R-Drop+FGM."""

    def __init__(self, data, student_tok, max_length=256, gaz_trie=None):
        self.examples = []
        fallback = np.full(NUM_LABELS, -10.0, dtype=np.float32)
        fallback[_O_IDX] = 10.0

        for item in data:
            sent = item["sentence"]
            char_labels = item["labelling_seq"]
            enc = student_tok(
                sent, truncation=True, max_length=max_length, return_offsets_mapping=True
            )
            word_ids = enc.word_ids()
            offsets = enc["offset_mapping"]
            labels, soft, seen = [], [], set()
            for wid, (cs, ce) in zip(word_ids, offsets):
                if wid is None or ce == 0 or wid in seen:
                    labels.append(-100)
                    soft.append(fallback)
                else:
                    seen.add(wid)
                    raw = char_labels[cs] if cs < len(char_labels) else "O"
                    lid = LABEL2ID.get(raw, _O_IDX)
                    labels.append(lid)
                    onehot = fallback.copy()
                    onehot[lid] = 10.0
                    soft.append(onehot)

            ex = {
                "input_ids": enc["input_ids"],
                "attention_mask": enc["attention_mask"],
                "labels": labels,
                "soft_logits": np.array(soft, dtype=np.float32),
            }
            if gaz_trie is not None:
                gfeat = gaz_trie.match_sentence(sent)
                ex["gaz_features"] = aggregate_to_tokens(gfeat, offsets)
            self.examples.append(ex)

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, idx):
        ex = self.examples[idx]
        out = {
            "input_ids": torch.tensor(ex["input_ids"], dtype=torch.long),
            "attention_mask": torch.tensor(ex["attention_mask"], dtype=torch.long),
            "labels": torch.tensor(ex["labels"], dtype=torch.long),
            "soft_logits": torch.tensor(ex["soft_logits"], dtype=torch.float32),
        }
        if "gaz_features" in ex:
            out["gaz_features"] = torch.tensor(ex["gaz_features"], dtype=torch.float32)
        return out


class KDGazCollator:
    def __init__(self, tokenizer, use_gazetteer=False, num_gaz_labels=19):
        self.tokenizer = tokenizer
        self.use_gazetteer = use_gazetteer
        self.num_gaz_labels = num_gaz_labels

    def __call__(self, features):
        features = [dict(f) for f in features]
        gaz_list = [f.pop("gaz_features") for f in features] if self.use_gazetteer else None
        labels = [f.pop("labels") for f in features]
        soft = [f.pop("soft_logits") for f in features]
        batch = self.tokenizer.pad(features, padding=True, return_tensors="pt")
        max_len = batch["input_ids"].shape[1]
        padded_labels = torch.full((len(labels), max_len), -100, dtype=torch.long)
        padded_soft = torch.zeros((len(soft), max_len, NUM_LABELS), dtype=torch.float32)
        for i, (lab, sf) in enumerate(zip(labels, soft)):
            padded_labels[i, : lab.shape[0]] = lab
            padded_soft[i, : sf.shape[0]] = sf
        batch["labels"] = padded_labels
        batch["soft_logits"] = padded_soft
        if self.use_gazetteer:
            padded_gaz = torch.zeros((len(gaz_list), max_len, self.num_gaz_labels), dtype=torch.float32)
            for i, g in enumerate(gaz_list):
                padded_gaz[i, : g.shape[0]] = g
            batch["gaz_features"] = padded_gaz
        return batch


class DistillCrfGazTrainer(Trainer):
    def __init__(self, *args, kd_alpha=0.5, kd_t=3.0, use_crf=False,
                 use_rdrop=False, rdrop_alpha=4.0, use_fgm=False, fgm_epsilon=1.0, **kwargs):
        super().__init__(*args, **kwargs)
        self.kd_alpha = kd_alpha
        self.kd_t = kd_t
        self.use_crf = use_crf
        self.use_rdrop = use_rdrop
        self.rdrop_alpha = rdrop_alpha
        self.use_fgm = use_fgm
        self._fgm = FGM(self.model, epsilon=fgm_epsilon) if use_fgm else None

    def _forward_logits(self, model, inputs):
        return model(
            input_ids=inputs["input_ids"],
            attention_mask=inputs["attention_mask"],
            gaz_features=inputs.get("gaz_features"),
        ).logits

    def _hard_kd_loss(self, model, logits, labels, soft_logits):
        mask = labels != -100
        if mask.sum() == 0:
            return logits.sum() * 0.0
        s_logits_flat = logits[mask]
        t_logits_flat = soft_logits[mask]
        T = self.kd_t
        s_logp = F.log_softmax(s_logits_flat / T, dim=-1)
        t_prob = F.softmax(t_logits_flat / T, dim=-1)
        kd = F.kl_div(s_logp, t_prob, reduction="batchmean") * (T * T)
        if self.use_crf:
            underlying = model.module if hasattr(model, "module") else model
            compact_logits, compact_mask = compact_sequence(logits, mask)
            compact_labels, _ = compact_sequence(labels.unsqueeze(-1), mask)
            compact_labels = compact_labels.squeeze(-1)
            hard = -underlying.crf(compact_logits, compact_labels, mask=compact_mask, reduction="mean")
        else:
            hard = F.cross_entropy(logits.view(-1, logits.size(-1)), labels.view(-1), ignore_index=-100)
        return self.kd_alpha * hard + (1.0 - self.kd_alpha) * kd

    def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
        labels = inputs["labels"]
        soft_logits = inputs["soft_logits"]
        if self.use_rdrop:
            logits1 = self._forward_logits(model, inputs)
            logits2 = self._forward_logits(model, inputs)
            loss1 = self._hard_kd_loss(model, logits1, labels, soft_logits)
            loss2 = self._hard_kd_loss(model, logits2, labels, soft_logits)
            label_mask = labels != -100
            kl = rdrop_kl_loss(logits1, logits2, label_mask)
            loss = 0.5 * (loss1 + loss2) + self.rdrop_alpha * kl
            logits = logits1
        else:
            logits = self._forward_logits(model, inputs)
            loss = self._hard_kd_loss(model, logits, labels, soft_logits)
        if return_outputs:
            from transformers.modeling_outputs import TokenClassifierOutput
            return loss, TokenClassifierOutput(loss=loss, logits=logits)
        return loss

    def training_step(self, model, inputs, num_items_in_batch=None):
        model.train()
        inputs = self._prepare_inputs(inputs)
        loss = self.compute_loss(model, inputs)
        if self.args.n_gpu > 1:
            loss = loss.mean()
        self._backward(loss)
        if self.use_fgm:
            self._fgm.attack()
            loss_adv = self.compute_loss(model, inputs)
            if self.args.n_gpu > 1:
                loss_adv = loss_adv.mean()
            self._backward(loss_adv)
            self._fgm.restore()
        return loss.detach() / max(self.args.gradient_accumulation_steps, 1)

    def _backward(self, loss):
        scaled = loss / max(self.args.gradient_accumulation_steps, 1)
        accelerator = getattr(self, "accelerator", None)
        if accelerator is not None:
            accelerator.backward(scaled)
        else:
            scaled.backward()


def main():
    if GRAD_ACCUM != 1:
        print(f"[경고] GRAD_ACCUM={GRAD_ACCUM} (≠1) — FGM/R-Drop 스케일이 부정확할 수 있음.")
    if USE_KD and not Path(TEACHER_DIR, "config.json").exists():
        sys.exit(f"[ERROR] teacher 없음: {TEACHER_DIR}")

    device = "cuda" if torch.cuda.is_available() else "cpu"
    use_bf16 = torch.cuda.is_available() and torch.cuda.is_bf16_supported()

    student_tok = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True, use_fast=True)
    if not student_tok.is_fast:
        sys.exit(f"[ERROR] '{MODEL_ID}' fast tokenizer 필요.")

    def load_json(name):
        return json.load(open(DATA_DIR / name, encoding="utf-8"))

    train_file = os.environ.get("TRAIN_FILE", "train_aug.json")
    valid_file = os.environ.get("VALID_FILE", "valid.json")
    train_data = load_json(train_file)
    valid_data = load_json(valid_file)
    if SMOKE_N > 0:
        train_data = train_data[:SMOKE_N]
        valid_data = valid_data[:SMOKE_N]
        print(f"[SMOKE] train/valid {SMOKE_N}개로 축소")

    gaz_trie = None
    if USE_GAZETTEER:
        gaz_path = Path(OUTPUT_DIR) / "gazetteer.json"
        gaz_path.parent.mkdir(parents=True, exist_ok=True)
        gaz = build_gazetteer(train_data, TARGET_LABELS)
        save_gazetteer(gaz, str(gaz_path))
        gaz_trie = GazetteerTrie(gaz, TARGET_LABELS)
        print(f"[gazetteer] exact={gaz_trie.n_entries} suffix={gaz_trie.n_suffixes} → {gaz_path}")

    print(f"GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'cpu'}")
    mode = "KD+CRF+GAZ" if USE_KD else "CRF+GAZ (hard-only)"
    print(f"[{mode}] student={MODEL_ID}")
    if USE_KD:
        print(f"  teacher={TEACHER_DIR}")
    print(f"  DATA_DIR={DATA_DIR}  combo={_combo_tag()}  α={KD_ALPHA} T={KD_T} LR={LR} seed={SEED}")
    print(f"  RDROP={USE_RDROP}(α={RDROP_ALPHA})  FGM={USE_FGM}(ε={FGM_EPSILON})")
    print(f"  OUTPUT_DIR={OUTPUT_DIR}  TRAIN_FILE={train_file}  VALID_FILE={valid_file}")

    if USE_KD:
        teacher_tok = AutoTokenizer.from_pretrained(TEACHER_DIR, trust_remote_code=True, use_fast=True)
        teacher = AutoModelForTokenClassification.from_pretrained(
            TEACHER_DIR, trust_remote_code=True).to(device)
        teacher.eval()
        if use_bf16:
            teacher = teacher.to(torch.bfloat16)
        print("teacher soft-label 사전 추출 중...")
        train_ds = KDGazDataset(
            train_data, student_tok, teacher, teacher_tok, device,
            max_length=MAX_LEN, gaz_trie=gaz_trie, split_name="train",
        )
        del teacher
        torch.cuda.empty_cache()
    else:
        print("hard-label 데이터셋 구성 중...")
        train_ds = HardGazDataset(
            train_data, student_tok, max_length=MAX_LEN, gaz_trie=gaz_trie,
        )

    student = build_model(
        backbone_model_id=MODEL_ID,
        num_labels=NUM_LABELS,
        id2label=ID2LABEL,
        label2id=LABEL2ID,
        use_crf=USE_CRF,
        use_gazetteer=USE_GAZETTEER,
        num_gaz_labels=NUM_GAZ_LABELS,
        gaz_emb_dim=GAZ_EMB_DIM,
    )

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
        eval_strategy="no",
        save_strategy="no",
        report_to="none",
        seed=SEED,
        dataloader_num_workers=4,
        remove_unused_columns=False,
    )

    collator = KDGazCollator(student_tok, use_gazetteer=USE_GAZETTEER, num_gaz_labels=NUM_GAZ_LABELS)
    trainer = DistillCrfGazTrainer(
        model=student,
        args=training_args,
        train_dataset=train_ds,
        data_collator=collator,
        processing_class=student_tok,
        kd_alpha=KD_ALPHA,
        kd_t=KD_T,
        use_crf=USE_CRF,
        use_rdrop=USE_RDROP,
        rdrop_alpha=RDROP_ALPHA,
        use_fgm=USE_FGM,
        fgm_epsilon=FGM_EPSILON,
    )

    best_cb = ManualEvalCallback(
        trainer, student_tok, valid_data, OUTPUT_DIR,
        eval_steps=EVAL_STEPS, patience=ES_PATIENCE, device=device,
        gaz_trie=gaz_trie, num_gaz_labels=NUM_GAZ_LABELS,
    )
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
            "run_tag": RUN_TAG,
            "use_crf": USE_CRF,
            "use_gazetteer": USE_GAZETTEER,
            "use_rdrop": USE_RDROP,
            "use_fgm": USE_FGM,
            "use_kd": USE_KD,
            "teacher_dir": TEACHER_DIR if USE_KD else "",
            "kd_alpha": KD_ALPHA,
            "kd_t": KD_T,
            "rdrop_alpha": RDROP_ALPHA,
            "fgm_epsilon": FGM_EPSILON,
        }, open(Path(OUTPUT_DIR) / "label_map.json", "w", encoding="utf-8"),
            ensure_ascii=False, indent=2)
        print(f"\n학습 완료 | best(근사) F1={best_cb.best_f1:.4f} → {OUTPUT_DIR}")

    if torch.distributed.is_initialized():
        torch.distributed.destroy_process_group()
    if int(os.environ.get("LOCAL_RANK", "0")) != 0:
        sys.exit(0)

    if os.environ.get("SKIP_EVAL", "0") == "1":
        print("\nSKIP_EVAL=1 → test 평가 생략.")
        return

    data_dir = os.environ.get("DATA_DIR", "data")
    print(f"\n학습 완료 — test 평가(eval_crf_gaz.py) 시작... (data-dir={data_dir})")
    subprocess.run(
        [sys.executable, str(BASE_DIR / "eval_crf_gaz.py"),
         "--split", "test", "--model_dir", OUTPUT_DIR, "--tag", RUN_TAG,
         "--data-dir", data_dir],
        check=True,
    )


if __name__ == "__main__":
    main()
