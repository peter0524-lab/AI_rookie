"""
베이스라인 1 — Chen et al. (2025b) 방식 재현 (한국어 적응).

논문 A.2: DeBERTa-v3-base를 같은 학습 데이터로 파인튜닝한 이진 분류기
(misaligned = 1, aligned/non-instruction = 0). indirect에서는 tool_response만
입력으로 사용. 도메인별로 따로 학습(본 방법과 동일 조건, Table 1b와 대응).

한국어 데이터이므로 인코더를 DeBERTa-v3-base 대신 klue/roberta-base로 교체
(README 편차 D4). 나머지 절차는 동일.

실행:
  python src/baselines/baseline_chen.py --data data/full_train.json data/full_test.json
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import numpy as np


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--data", nargs="+", default=["data/full_train.json", "data/full_test.json"])
    p.add_argument("--model", default="klue/roberta-base")
    p.add_argument("--epochs", type=int, default=3)
    p.add_argument("--lr", type=float, default=2e-5)
    p.add_argument("--batch-size", type=int, default=16)
    p.add_argument("--max-length", type=int, default=512)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--results", default="results")
    p.add_argument("--domains", nargs="*", default=None)
    return p.parse_args()


def main() -> None:
    args = parse_args()
    import torch
    import torch.nn as nn
    from tqdm import tqdm
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    device = "cuda" if torch.cuda.is_available() else "cpu"
    records = []
    for path in args.data:
        with open(path, "r", encoding="utf-8") as f:
            records.extend(json.load(f))
    by_domain: dict[str, dict[str, list]] = defaultdict(lambda: {"train": [], "test": []})
    for r in records:
        if args.domains and r["domain"] not in args.domains:
            continue
        by_domain[r["domain"]][r["split"]].append(r)

    tokenizer = AutoTokenizer.from_pretrained(args.model)

    def encode(recs):
        texts = [r["tool_response"] for r in recs]
        y = np.array([1 if r["label"] == "misaligned" else 0 for r in recs], dtype=np.int64)
        return texts, y

    for domain, splits in sorted(by_domain.items()):
        torch.manual_seed(args.seed)
        np.random.seed(args.seed)
        model = AutoModelForSequenceClassification.from_pretrained(args.model, num_labels=2).to(device)
        opt = torch.optim.AdamW(model.parameters(), lr=args.lr)
        texts_tr, y_tr = encode(splits["train"])
        texts_te, y_te = encode(splits["test"])

        n = len(y_tr)
        for epoch in range(args.epochs):
            model.train()
            perm = np.random.permutation(n)
            total = 0.0
            for b0 in tqdm(range(0, n, args.batch_size), desc=f"{domain} ep{epoch+1}", leave=False):
                idx = perm[b0:b0 + args.batch_size]
                enc = tokenizer([texts_tr[i] for i in idx], padding=True, truncation=True,
                                max_length=args.max_length, return_tensors="pt").to(device)
                yb = torch.tensor(y_tr[idx], device=device)
                out = model(**enc, labels=yb)
                opt.zero_grad()
                out.loss.backward()
                opt.step()
                total += out.loss.item() * len(idx)
            print(f"[chen/{domain}] epoch {epoch+1}: loss={total/n:.4f}")

        model.eval()
        preds = []
        with torch.no_grad():
            for b0 in range(0, len(y_te), 64):
                enc = tokenizer(texts_te[b0:b0 + 64], padding=True, truncation=True,
                                max_length=args.max_length, return_tensors="pt").to(device)
                preds.append(model(**enc).logits.argmax(dim=1).cpu().numpy())
        y_pred = np.concatenate(preds)
        pos, neg = y_te == 1, y_te == 0
        m = {"method": "chen_et_al", "domain": domain, "encoder": args.model,
             "fpr": round(float((y_pred[neg] == 1).mean()), 4),
             "fnr": round(float((y_pred[pos] != 1).mean()), 4),
             "binary_acc": round(float((y_pred == y_te).mean()), 4), "n_test": int(len(y_te))}
        print(f"[chen/{domain}] FPR={m['fpr']:.3f} FNR={m['fnr']:.3f}")
        Path(args.results).mkdir(parents=True, exist_ok=True)
        with open(Path(args.results) / f"baseline_chen_{domain}.json", "w", encoding="utf-8") as f:
            json.dump(m, f, ensure_ascii=False, indent=1)
        del model
        torch.cuda.empty_cache()


if __name__ == "__main__":
    main()
