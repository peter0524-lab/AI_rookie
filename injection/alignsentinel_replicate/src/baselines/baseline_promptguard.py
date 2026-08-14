"""
베이스라인 2 — Llama Prompt-Guard-2-86M (zero-shot).

논문 A.2: 학습 없이 기성 이진 탐지 모델을 그대로 사용. indirect에서는
tool_response를 입력으로 넣고, malicious 판정 시 misaligned(positive)로 간주.
Prompt-Guard-2-86M은 mDeBERTa 기반 다국어 모델이라 한국어 입력에 적용 가능.

주의: meta-llama/Llama-Prompt-Guard-2-86M 은 gated model — Hugging Face에서
라이선스 동의 후 `huggingface-cli login` 필요.

실행:
  python src/baselines/baseline_promptguard.py --data data/full_test.json
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import numpy as np


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--data", nargs="+", default=["data/full_test.json"])
    p.add_argument("--model", default="meta-llama/Llama-Prompt-Guard-2-86M")
    p.add_argument("--batch-size", type=int, default=64)
    p.add_argument("--max-length", type=int, default=512)
    p.add_argument("--results", default="results")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    import torch
    from tqdm import tqdm
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    device = "cuda" if torch.cuda.is_available() else "cpu"
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForSequenceClassification.from_pretrained(args.model).to(device)
    model.eval()
    # Prompt-Guard-2 라벨: 0=BENIGN, 1=MALICIOUS (config.id2label로 확인)
    malicious_id = next((i for i, name in model.config.id2label.items()
                         if "malicious" in str(name).lower() or "jailbreak" in str(name).lower()), 1)

    records = []
    for path in args.data:
        with open(path, "r", encoding="utf-8") as f:
            records.extend(json.load(f))
    records = [r for r in records if r["split"] == "test"]
    by_domain = defaultdict(list)
    for r in records:
        by_domain[r["domain"]].append(r)

    for domain, recs in sorted(by_domain.items()):
        y_true = np.array([1 if r["label"] == "misaligned" else 0 for r in recs])
        preds = []
        with torch.no_grad():
            for b0 in tqdm(range(0, len(recs), args.batch_size), desc=f"pg2/{domain}", leave=False):
                texts = [r["tool_response"] for r in recs[b0:b0 + args.batch_size]]
                enc = tokenizer(texts, padding=True, truncation=True,
                                max_length=args.max_length, return_tensors="pt").to(device)
                pred = model(**enc).logits.argmax(dim=1).cpu().numpy()
                preds.append(pred == int(malicious_id))
        y_pred = np.concatenate(preds).astype(int)
        pos, neg = y_true == 1, y_true == 0
        m = {"method": "prompt_guard_2", "domain": domain, "model": args.model,
             "fpr": round(float((y_pred[neg] == 1).mean()), 4),
             "fnr": round(float((y_pred[pos] != 1).mean()), 4),
             "binary_acc": round(float((y_pred == y_true).mean()), 4), "n_test": int(len(recs))}
        print(f"[pg2/{domain}] FPR={m['fpr']:.3f} FNR={m['fnr']:.3f}")
        Path(args.results).mkdir(parents=True, exist_ok=True)
        with open(Path(args.results) / f"baseline_promptguard_{domain}.json", "w", encoding="utf-8") as f:
            json.dump(m, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
