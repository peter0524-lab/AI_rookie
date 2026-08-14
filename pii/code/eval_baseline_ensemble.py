"""
무형태소(baseline) 시드 앙상블 평가 — soft voting

distill_aug / baseline 계열처럼 **무형태소(offset_mapping word 정렬)** 로 학습된
동일 구조(skt/A.X-Encoder-base) 모델 N개를 받아, word(어절) 단위 softmax 확률을
평균(soft voting)한 뒤 char BIO 복원 → LC 병합 → regex 후처리.

설계 근거:
  - 모든 모델이 동일 토크나이저 → word_ids/offset 정렬이 완전히 일치하므로
    1회 인코딩 후 N개 모델 forward → '어절 첫 서브워드' 확률을 평균하면 됨.
  - 디코딩·LC 병합·regex·span-overlap F1·MD 리포트는 eval_baseline.py 를
    그대로 import 하여 단일 평가와 완전히 동일(공정 비교). 모델 1개일 때
    eval_baseline.py 의 단일 결과와 수치가 일치.

사용법:
    python eval_baseline_ensemble.py --split test --tag distill_aug_x3 \
        --model_dirs models/skt_encoder_distill_aug/seed42 \
                     models/skt_encoder_distill_aug/seed43 \
                     models/skt_encoder_distill_aug/seed44
"""

import argparse
import datetime
import json
from collections import defaultdict
from pathlib import Path

import torch
from transformers import AutoModelForTokenClassification, AutoTokenizer

import eval_baseline as eb

ID2LABEL      = eb.ID2LABEL
TARGET_LABELS = eb.TARGET_LABELS
DATA_DIR      = eb.DATA_DIR
BASE_DIR      = eb.BASE_DIR
EXAMPLE_CAP   = eb.EXAMPLE_CAP


# ── 앙상블 예측 (어절 단위 softmax 확률 soft voting) ──────────────────────────
def predict_ensemble_baseline(
    models, tokenizer, sentences: list[str],
    batch_size: int = 64, max_length: int = 256, device: str = "cuda"
) -> list[list[dict]]:
    all_entities = []

    for bs in range(0, len(sentences), batch_size):
        batch_sents = sentences[bs: bs + batch_size]
        enc = tokenizer(
            batch_sents,
            truncation=True,
            max_length=max_length,
            padding=True,
            return_offsets_mapping=True,
            return_tensors="pt",
        )
        offset_mapping = enc.pop("offset_mapping").tolist()
        word_ids_list  = [enc.word_ids(i) for i in range(len(batch_sents))]

        ids  = enc["input_ids"].to(device)
        mask = enc["attention_mask"].to(device)

        # N개 모델 softmax 확률 평균 (soft voting)
        prob_sum = None
        for model in models:
            with torch.inference_mode():
                logits = model(input_ids=ids, attention_mask=mask).logits
            probs = torch.softmax(logits.float(), dim=-1)
            prob_sum = probs if prob_sum is None else prob_sum + probs
        prob_avg = (prob_sum / len(models)).cpu().numpy()  # [B, T, C]

        for si, sent in enumerate(batch_sents):
            wids = word_ids_list[si]
            offs = offset_mapping[si]

            # 어절 단위 span 과 (첫 서브워드의) 평균 확률 집계
            word_span = {}   # wid -> [start, end]
            word_prob = {}   # wid -> 평균 확률 벡터 (첫 서브워드)
            for tpos, (wid, (cs, ce)) in enumerate(zip(wids, offs)):
                if wid is None or ce == 0:
                    continue
                if wid not in word_span:
                    word_span[wid] = [cs, ce]
                    word_prob[wid] = prob_avg[si, tpos]
                else:
                    word_span[wid][0] = min(word_span[wid][0], cs)
                    word_span[wid][1] = max(word_span[wid][1], ce)

            char_labels = ["O"] * len(sent)
            for wid, (ws, we) in word_span.items():
                pid = int(word_prob[wid].argmax())
                tag = ID2LABEL.get(pid, "O")
                if tag == "O":
                    continue
                cont = "I-" + tag[2:] if tag.startswith("B-") else tag
                for k, c in enumerate(range(ws, min(we, len(sent)))):
                    char_labels[c] = tag if k == 0 else cont

            ents = eb.char_bio_to_entities(sent, char_labels)
            ents = eb.merge_lc_address(ents, sent)
            ents = eb.regex_postprocess(sent, ents)
            all_entities.append(ents)

    return all_entities


# ── 메인 평가 (eval_baseline.evaluate 와 동일 집계/리포트) ─────────────────────
def evaluate(args):
    device     = "cuda" if torch.cuda.is_available() else "cpu"
    model_dirs = [Path(d) for d in args.model_dirs]

    print(f"[BASELINE ENSEMBLE / soft voting] 모델 {len(model_dirs)}개:")
    for d in model_dirs:
        print(f"  - {d}")
    print(f"평가: {args.split}.json  →  {device}")

    # 동일 토크나이저 가정: 첫 모델 토크나이저로 1회 인코딩
    tokenizer = AutoTokenizer.from_pretrained(
        str(model_dirs[0]), trust_remote_code=True, use_fast=True)
    if not tokenizer.is_fast:
        raise SystemExit(f"[ERROR] '{model_dirs[0]}' fast tokenizer 없음 → offset 평가 불가.")

    models = []
    for d in model_dirs:
        mdl = AutoModelForTokenClassification.from_pretrained(
            str(d), trust_remote_code=True).to(device)
        mdl.eval()
        models.append(mdl)

    data          = json.load(open(DATA_DIR / f"{args.split}.json", encoding="utf-8"))
    sentences     = [d["sentence"] for d in data]
    gold_pii_list = [d["PII_set"]  for d in data]

    print(f"총 {len(sentences):,}문장 앙상블 예측 중...")
    pred_list = predict_ensemble_baseline(
        models, tokenizer, sentences,
        batch_size=args.batch_size, max_length=args.max_length, device=device)

    micro_tp = micro_fp = micro_fn = 0
    per_label    = defaultdict(lambda: [0, 0, 0])
    per_label_fp = defaultdict(list)
    per_label_fn = defaultdict(list)
    confusion    = defaultdict(int)

    for item, gold_piis, pred_ents in zip(data, gold_pii_list, pred_list):
        sent     = item["sentence"]
        sent_idx = item["sent_idx"]

        matched_gold = set()
        matched_pred = set()
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
            if pi in matched_pred:
                continue
            lbl = pe["label"]
            per_label[lbl][1] += 1
            gold_here = eb.find_overlapping(gold_piis, pe["begin"], pe["end"])
            gold_lbl  = gold_here["label"] if gold_here else "O"
            confusion[(gold_lbl, lbl)] += 1
            per_label_fp[lbl].append({
                "sent_idx": sent_idx, "sentence": sent,
                "form": pe["form"], "begin": pe["begin"], "end": pe["end"],
                "gold_label": gold_lbl,
                "gold_form":  gold_here["form"] if gold_here else "",
            })

        for gi, ge in enumerate(gold_piis):
            if gi in matched_gold:
                continue
            lbl = ge["label"]
            per_label[lbl][2] += 1
            pred_here = eb.find_overlapping(pred_ents, ge["begin"], ge["end"])
            pred_lbl  = pred_here["label"] if pred_here else "O"
            per_label_fn[lbl].append({
                "sent_idx": sent_idx, "sentence": sent,
                "form": ge["form"], "begin": ge["begin"], "end": ge["end"],
                "pred_label": pred_lbl,
                "pred_form":  pred_here["form"] if pred_here else "",
            })

    micro_f1, micro_p, micro_r = eb.safe_f1(micro_tp, micro_fp, micro_fn)

    print(f"\n{'='*68}")
    print(f"[{args.split}]  Micro F1={micro_f1:.4f}  P={micro_p:.4f}  R={micro_r:.4f}")
    print(f"  TP={micro_tp}  FP={micro_fp}  FN={micro_fn}")
    print(f"{'='*68}")
    label_rows = []
    for lbl in TARGET_LABELS:
        tp, fp, fn = per_label[lbl]
        f1, p, r   = eb.safe_f1(tp, fp, fn)
        label_rows.append((lbl, f1, p, r, tp, fp, fn))
        print(f"  {lbl:28s} F1={f1:.4f} P={p:.4f} R={r:.4f}  "
              f"TP={tp:5d} FP={fp:5d} FN={fn:5d}")

    ts          = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    tag         = f"{args.tag}_" if args.tag else ""
    results_dir = eb._results_dir_for(model_dirs[0])
    md_path     = results_dir / f"eval_ensemble_{args.split}_{tag}{ts}.md"
    L = [
        f"# 앙상블 평가 결과 (baseline/무형태소, soft voting): {args.split}  ({ts})",
        f"",
        f"모델 {len(model_dirs)}개:",
    ]
    for d in model_dirs:
        L.append(f"- `{d}`")
    L += [
        f"",
        f"tag: `{args.tag}`",
        f"",
        f"## 전체 성능",
        f"",
        f"| 지표 | 값 |",
        f"|------|------|",
        f"| Entity Micro F1 | **{micro_f1:.4f}** |",
        f"| Precision       | {micro_p:.4f} |",
        f"| Recall          | {micro_r:.4f} |",
        f"| TP | {micro_tp} |  FP | {micro_fp} |  FN | {micro_fn} |",
        f"",
        f"## 레이블별 성능 (F1 내림차순)",
        f"",
        f"| 레이블 | F1 | P | R | TP | FP | FN |",
        f"|--------|-----|---|---|----|----|-----|",
    ]
    for lbl, f1, p, r, tp, fp, fn in sorted(label_rows, key=lambda x: -x[1]):
        L.append(f"| {lbl} | {f1:.4f} | {p:.4f} | {r:.4f} | {tp} | {fp} | {fn} |")

    conf_items = [(cnt, g, p) for (g, p), cnt in confusion.items() if g != "O" and g != p]
    conf_items.sort(reverse=True)
    if conf_items:
        L += ["", "## 레이블 혼동", "",
              "| 건수 | 정답 | 예측 |", "|------|------|------|"]
        for cnt, g, p in conf_items[:30]:
            L.append(f"| {cnt} | {g} | {p} |")

    pure_fp = sorted([(cnt, p) for (g, p), cnt in confusion.items() if g == "O"], reverse=True)
    if pure_fp:
        L += ["", "## 순수 오탐 (해당 위치 정답 없음)", "",
              "| 건수 | 예측 |", "|------|------|"]
        for cnt, p in pure_fp:
            L.append(f"| {cnt} | {p} |")

    L += ["", "---", "", "## 레이블별 상세 분석", ""]
    for lbl, f1, p, r, tp, fp, fn in sorted(label_rows, key=lambda x: -x[1]):
        fps = per_label_fp[lbl]
        fns = per_label_fn[lbl]
        L += [
            f"### {lbl}",
            f"F1={f1:.4f} | P={p:.4f} | R={r:.4f} | TP={tp} | FP={fp} | FN={fn}",
            f"",
            f"#### 오탐 (FP) — 총 {len(fps)}건"
            + (f"  *(상위 {EXAMPLE_CAP}건)*" if len(fps) > EXAMPLE_CAP else ""),
            f"",
            f"| sent_idx | 예측 form | 해당위치 정답 | 문장 |",
            f"|----------|-----------|--------------|------|",
        ]
        for ex in fps[:EXAMPLE_CAP]:
            ctx = eb.highlight(ex["sentence"], ex["begin"], ex["end"])
            gs  = f"{ex['gold_form']} ({ex['gold_label']})" if ex["gold_form"] else ex["gold_label"]
            L.append(f"| {ex['sent_idx']} | `{ex['form']}` | {gs} | {ctx} |")

        L += [
            f"",
            f"#### 미탐 (FN) — 총 {len(fns)}건"
            + (f"  *(상위 {EXAMPLE_CAP}건)*" if len(fns) > EXAMPLE_CAP else ""),
            f"",
            f"| sent_idx | 정답 form | 해당위치 예측 | 문장 |",
            f"|----------|-----------|--------------|------|",
        ]
        for ex in fns[:EXAMPLE_CAP]:
            ctx = eb.highlight(ex["sentence"], ex["begin"], ex["end"])
            ps  = f"{ex['pred_form']} ({ex['pred_label']})" if ex["pred_form"] else ex["pred_label"]
            L.append(f"| {ex['sent_idx']} | `{ex['form']}` | {ps} | {ctx} |")
        L.append("")

    md_path.write_text("\n".join(L), encoding="utf-8")
    print(f"\nMD 저장: {md_path}")
    return micro_f1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--split",      default="test", choices=["test", "valid"])
    parser.add_argument("--model_dirs", nargs="+", required=True)
    parser.add_argument("--tag",        default="")
    parser.add_argument("--batch_size", type=int, default=64)
    parser.add_argument("--max_length", type=int, default=256)
    args = parser.parse_args()
    evaluate(args)
