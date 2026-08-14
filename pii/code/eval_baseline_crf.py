"""
CRF 모델 단일 평가 — Viterbi 디코딩 + eval_baseline 후처리 동일
"""

import argparse
import datetime
import json
import sys
from collections import defaultdict
from pathlib import Path

import torch
from transformers import AutoTokenizer

import eval_baseline as eb
from crf_model import TokenClassifierCRF

ID2LABEL = eb.ID2LABEL
TARGET_LABELS = eb.TARGET_LABELS
DATA_DIR = eb.DATA_DIR
EXAMPLE_CAP = eb.EXAMPLE_CAP


def predict_batch_crf(model, tokenizer, sentences, batch_size=64, max_length=256, device="cuda"):
    all_entities = []
    model.eval()

    for bs in range(0, len(sentences), batch_size):
        batch_sents = sentences[bs: bs + batch_size]
        enc = tokenizer(
            batch_sents, truncation=True, max_length=max_length,
            padding=True, return_offsets_mapping=True, return_tensors="pt",
        )
        offset_mapping = enc.pop("offset_mapping").tolist()
        ids = enc["input_ids"].to(device)
        mask = enc["attention_mask"].to(device)

        with torch.inference_mode():
            decoded = model.decode(ids, mask)

        for si, sent in enumerate(batch_sents):
            offs = offset_mapping[si]
            preds = decoded[si]
            char_labels = ["O"] * len(sent)
            for tpos, (cs, ce) in enumerate(offs):
                if ce == 0 or tpos >= len(preds):
                    continue
                tag = ID2LABEL.get(preds[tpos], "O")
                if tag == "O":
                    continue
                for k, c in enumerate(range(cs, min(ce, len(sent)))):
                    char_labels[c] = tag if k == 0 else (
                        "I-" + tag[2:] if tag.startswith("B-") else tag
                    )
            ents = eb.char_bio_to_entities(sent, char_labels)
            ents = eb.merge_lc_address(ents, sent)
            ents = eb.regex_postprocess(sent, ents)
            all_entities.append(ents)

    return all_entities


def evaluate(args):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model_dir = Path(args.model_dir)
    print(f"[CRF] 모델: {model_dir}  split={args.split}")

    tok = AutoTokenizer.from_pretrained(str(model_dir), trust_remote_code=True, use_fast=True)
    if not tok.is_fast:
        sys.exit("[ERROR] fast tokenizer 필요")
    model = TokenClassifierCRF.load_pretrained(model_dir).to(device)

    data = json.load(open(DATA_DIR / f"{args.split}.json", encoding="utf-8"))
    sentences = [d["sentence"] for d in data]
    gold_list = [d["PII_set"] for d in data]

    print(f"총 {len(sentences):,}문장 예측 중...")
    pred_list = predict_batch_crf(
        model, tok, sentences, args.batch_size, args.max_length, device)

    micro_tp = micro_fp = micro_fn = 0
    per_label = defaultdict(lambda: [0, 0, 0])

    for item, gold_piis, pred_ents in zip(data, gold_list, pred_list):
        sent = item["sentence"]
        sent_idx = item["sent_idx"]
        matched_gold, matched_pred = set(), set()
        for pi, pe in enumerate(pred_ents):
            for gi, ge in enumerate(gold_piis):
                if pe["label"] != ge["label"]:
                    continue
                if pe["begin"] < ge["end"] and ge["begin"] < pe["end"]:
                    matched_gold.add(gi)
                    matched_pred.add(pi)
        micro_tp += len(matched_gold)
        micro_fp += len(pred_ents) - len(matched_pred)
        micro_fn += len(gold_piis) - len(matched_gold)
        for gi in matched_gold:
            per_label[gold_piis[gi]["label"]][0] += 1
        for pi, pe in enumerate(pred_ents):
            if pi not in matched_pred:
                per_label[pe["label"]][1] += 1
        for gi, ge in enumerate(gold_piis):
            if gi not in matched_gold:
                per_label[ge["label"]][2] += 1

    micro_f1, micro_p, micro_r = eb.safe_f1(micro_tp, micro_fp, micro_fn)
    print(f"\n{'='*68}")
    print(f"[{args.split}]  Micro F1={micro_f1:.4f}  P={micro_p:.4f}  R={micro_r:.4f}")
    print(f"  TP={micro_tp}  FP={micro_fp}  FN={micro_fn}")
    print(f"{'='*68}")
    label_rows = []
    for lbl in TARGET_LABELS:
        tp, fp, fn = per_label[lbl]
        f1, p, r = eb.safe_f1(tp, fp, fn)
        label_rows.append((lbl, f1, p, r, tp, fp, fn))
        print(f"  {lbl:28s} F1={f1:.4f} P={p:.4f} R={r:.4f}  "
              f"TP={tp:5d} FP={fp:5d} FN={fn:5d}")

    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    tag = f"{args.tag}_" if args.tag else ""
    results_dir = eb._results_dir_for(model_dir)
    md_path = results_dir / f"eval_crf_{args.split}_{tag}{ts}.md"
    lines = [
        f"# CRF 평가: {args.split} ({ts})",
        f"모델: `{model_dir}`",
        "",
        f"| Micro F1 | **{micro_f1:.4f}** |",
        f"| P | {micro_p:.4f} | R | {micro_r:.4f} |",
        "",
        "| 레이블 | F1 | P | R | TP | FP | FN |",
        "|--------|-----|---|---|----|----|-----|",
    ]
    for lbl, f1, p, r, tp, fp, fn in sorted(label_rows, key=lambda x: -x[1]):
        lines.append(f"| {lbl} | {f1:.4f} | {p:.4f} | {r:.4f} | {tp} | {fp} | {fn} |")
    md_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nMD 저장: {md_path}")
    return micro_f1


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default="test", choices=["test", "valid"])
    ap.add_argument("--model_dir", required=True)
    ap.add_argument("--tag", default="")
    ap.add_argument("--batch_size", type=int, default=64)
    ap.add_argument("--max_length", type=int, default=256)
    evaluate(ap.parse_args())
