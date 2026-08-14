"""
PII NER 평가 — 형태소 분석 없는(baseline) 버전 / 모델 무관

eval.py(Kiwi) 와의 유일한 차이는 예측 시 토큰→char 정렬 방식입니다.
  - eval.py        : Kiwi 형태소 시작 위치로 char 라벨 복원
  - eval_baseline  : fast tokenizer 의 offset_mapping/word_ids 로 '어절' 단위 복원

라벨셋, regex 후처리(REGEX_RULES), LC_ADDRESS 병합, span-overlap F1 집계,
markdown 리포트 형식은 eval.py 와 완전히 동일합니다(공정 비교).

사용법:
    python eval_baseline.py --split test \
        --model_dir models/xlm_roberta_large/seed42 --tag seed42
"""

import argparse
import datetime
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

import torch
from transformers import AutoModelForTokenClassification, AutoTokenizer

# ── 경로 ──────────────────────────────────────────────────────────────────────
BASE_DIR    = Path(__file__).resolve().parent


def resolve_data_dir(path: str | None = None) -> Path:
    raw = path or os.environ.get("DATA_DIR", "data")
    p = Path(raw)
    return p if p.is_absolute() else BASE_DIR / p


DATA_DIR    = resolve_data_dir()
RESULTS_ROOT = BASE_DIR / "results"


def _results_dir_for(model_dir: Path) -> Path:
    p = str(model_dir).replace("\\", "/")
    if "skt_encoder_distill" in p:
        key = "skt_encoder_distill"
    elif "skt_encoder_baseline" in p:
        key = "skt_encoder_baseline"
    elif "privacy_filter_korean_Lora" in p or "privacy_filter_korean_lora" in p:
        key = "privacy_filter_korean_Lora"
    elif "privacy_filter_lora" in p:
        key = "privacy_filter_lora"
    elif "privacy_filter_korean" in p:
        key = "privacy_filter_korean"
    elif "privacy_filter" in p:
        key = "privacy_filter"
    elif "xlm_roberta_large" in p:
        key = "xlm_roberta_large"
    elif "klue_roberta_large" in p:
        key = "klue_roberta_large"
    else:
        key = "baseline"
    d = RESULTS_ROOT / key
    d.mkdir(parents=True, exist_ok=True)
    return d

# ── 레이블 ────────────────────────────────────────────────────────────────────
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

EXAMPLE_CAP = 100

# ── 정규식 후처리 (eval.py 와 완전히 동일) ─────────────────────────────────────
_PLATE_MID = "가나다라마바사아자차카타파하거너더러머버서어저처커터퍼허고노도로모보소오조초코토포호구누두루무부수우주"
_PLATE_REGION = (
    r"(?:서울|경기|경남|경북|전남|전북|충남|충북|강원|울산|부산|대구|인천|광주|대전|세종|제주"
    r"|경상남도|경상북도|전라남도|전라북도|충청남도|충청북도|강원도"
    r"|서울특별시|부산광역시|대구광역시|인천광역시|광주광역시|대전광역시|울산광역시)\s+"
)
REGEX_RULES = [
    ("QT_DRIVER_NUMBER",   re.compile(r"(?<!\d)\d{2}-\d{2}-\d{6}-\d{2}(?!\d)")),
    ("QT_CARD_NUMBER",     re.compile(r"(?<!\d)\d{4}[\-\s]\d{4}[\-\s]\d{4}[\-\s]\d{4}(?!\d)")),
    ("QT_RESIDENT_NUMBER", re.compile(r"(?<!\d)\d{6}-[1-4]\d{6}(?!\d)")),
    ("QT_ALIEN_NUMBER",    re.compile(r"(?<!\d)\d{6}-[5-9]\d{6}(?!\d)")),
    ("QT_ALIEN_NUMBER",    re.compile(r"(?<![A-Z0-9])[A-Z]\d{12}(?![A-Z0-9])")),
    ("QT_MOBILE",          re.compile(r"(?<!\d)01[016789][\-\s]?\d{3,4}[\-\s]?\d{4}(?!\d)")),
    ("QT_PHONE",           re.compile(r"(?<!\d)0(?:2|[3-9]\d)[\-]\d{3,4}[\-]\d{4}(?!\d)")),
    ("QT_PLATE_NUMBER",    re.compile(rf"(?:{_PLATE_REGION})?\d{{2,3}}[{_PLATE_MID}]\s?\d{{4}}(?!\d)")),
    ("QT_ACCOUNT_NUMBER",  re.compile(r"(?<!\d)\d{3,4}[\-]\d{3,4}[\-]\d{3,6}(?!\d)")),
]


def regex_postprocess(sentence: str, entities: list[dict]) -> list[dict]:
    hits = []
    claimed: list[tuple[int, int]] = []

    def overlaps_claimed(b, e):
        return any(b < ce and cb < e for cb, ce in claimed)

    for label, pattern in REGEX_RULES:
        for m in pattern.finditer(sentence):
            b, e = m.start(), m.end()
            if overlaps_claimed(b, e):
                continue
            hits.append({"form": m.group(), "label": label, "begin": b, "end": e})
            claimed.append((b, e))

    if not hits:
        return entities

    def overlaps(a0, a1, b0, b1):
        return a0 < b1 and b0 < a1

    kept = [e for e in entities if not any(
        overlaps(e["begin"], e["end"], h["begin"], h["end"]) for h in hits
    )]
    return kept + hits


# ── character BIO → entity 변환 (eval.py 와 동일) ─────────────────────────────
def char_bio_to_entities(sentence: str, char_labels: list[str]) -> list[dict]:
    entities = []
    start = cur_label = None
    n = len(char_labels)
    i = 0
    while i < n:
        tag = char_labels[i]
        if tag.startswith("B-"):
            if start is not None:
                entities.append({"form": sentence[start:i], "label": cur_label,
                                  "begin": start, "end": i})
            start, cur_label = i, tag[2:]
        elif tag.startswith("I-") and cur_label == tag[2:]:
            pass
        elif tag == "O" and cur_label and i < len(sentence) and sentence[i] == " ":
            j = i + 1
            while j < n and char_labels[j] == "O" and j < len(sentence) and sentence[j] == " ":
                j += 1
            if j < n and char_labels[j] == f"I-{cur_label}":
                i = j
                continue
            else:
                entities.append({"form": sentence[start:i], "label": cur_label,
                                  "begin": start, "end": i})
                start = cur_label = None
        else:
            if start is not None:
                entities.append({"form": sentence[start:i], "label": cur_label,
                                  "begin": start, "end": i})
            start = cur_label = None
        i += 1
    if start is not None:
        entities.append({"form": sentence[start:], "label": cur_label,
                          "begin": start, "end": n})
    return entities


def merge_lc_address(entities: list[dict], sentence: str) -> list[dict]:
    merged = []
    for e in entities:
        if (e["label"] == "LC_ADDRESS" and merged
                and merged[-1]["label"] == "LC_ADDRESS"):
            gap = sentence[merged[-1]["end"]:e["begin"]]
            if gap and all(c == " " for c in gap):
                prev = merged[-1]
                prev["end"]  = e["end"]
                prev["form"] = sentence[prev["begin"]:prev["end"]]
                continue
        merged.append(e)
    return merged


def safe_f1(tp, fp, fn):
    p = tp / (tp + fp) if (tp + fp) else 0.0
    r = tp / (tp + fn) if (tp + fn) else 0.0
    f = 2 * p * r / (p + r) if (p + r) else 0.0
    return f, p, r


# ── 배치 예측 (형태소 없이 offset_mapping 기반 어절 복원) ─────────────────────
def predict_batch(
    model, tokenizer, sentences: list[str],
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
        with torch.inference_mode():
            logits = model(input_ids=ids, attention_mask=mask).logits
        token_preds = logits.argmax(-1).cpu().tolist()

        for si, sent in enumerate(batch_sents):
            preds = token_preds[si]
            wids  = word_ids_list[si]
            offs  = offset_mapping[si]

            # 어절(word) 단위로 span 과 (첫 서브워드의) 예측 태그 집계
            word_span = {}   # wid -> [start, end]
            word_tag  = {}   # wid -> 태그 (첫 서브워드 예측)
            for wid, pid, (cs, ce) in zip(wids, preds, offs):
                if wid is None or ce == 0:
                    continue
                if wid not in word_span:
                    word_span[wid] = [cs, ce]
                    word_tag[wid]  = ID2LABEL.get(pid, "O")
                else:
                    word_span[wid][0] = min(word_span[wid][0], cs)
                    word_span[wid][1] = max(word_span[wid][1], ce)

            char_labels = ["O"] * len(sent)
            for wid, (ws, we) in word_span.items():
                tag = word_tag[wid]
                if tag == "O":
                    continue
                cont = "I-" + tag[2:] if tag.startswith("B-") else tag
                for k, c in enumerate(range(ws, min(we, len(sent)))):
                    char_labels[c] = tag if k == 0 else cont

            ents = char_bio_to_entities(sent, char_labels)
            ents = merge_lc_address(ents, sent)
            ents = regex_postprocess(sent, ents)
            all_entities.append(ents)

    return all_entities


def find_overlapping(entities, begin, end):
    for e in entities:
        if e["begin"] < end and e["end"] > begin:
            return e
    return None


def highlight(sentence, begin, end):
    return sentence[:begin] + "**" + sentence[begin:end] + "**" + sentence[end:]


# ── 메인 평가 (eval.py 와 동일 구조) ──────────────────────────────────────────
def evaluate(args):
    device    = "cuda" if torch.cuda.is_available() else "cpu"
    model_dir = Path(args.model_dir)

    print(f"[BASELINE / 무형태소] 모델: {model_dir}")
    print(f"평가: {args.split}.json  →  {device}")

    tokenizer = AutoTokenizer.from_pretrained(str(model_dir), trust_remote_code=True, use_fast=True)
    if not tokenizer.is_fast:
        sys.exit(f"[ERROR] '{model_dir}' fast tokenizer 없음 → offset_mapping 평가 불가.")
    model = AutoModelForTokenClassification.from_pretrained(
        str(model_dir), trust_remote_code=True).to(device)
    model.eval()

    data_dir      = resolve_data_dir(getattr(args, "data_dir", None))
    data          = json.load(open(data_dir / f"{args.split}.json", encoding="utf-8"))
    sentences     = [d["sentence"] for d in data]
    gold_pii_list = [d["PII_set"]  for d in data]

    print(f"총 {len(sentences):,}문장 예측 중...")
    pred_list = predict_batch(model, tokenizer, sentences,
                              batch_size=args.batch_size,
                              max_length=args.max_length, device=device)

    micro_tp = micro_fp = micro_fn = 0
    per_label     = defaultdict(lambda: [0, 0, 0])
    per_label_fp  = defaultdict(list)
    per_label_fn  = defaultdict(list)
    confusion     = defaultdict(int)

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
            if pi in matched_pred: continue
            lbl = pe["label"]
            per_label[lbl][1] += 1
            gold_here = find_overlapping(gold_piis, pe["begin"], pe["end"])
            gold_lbl  = gold_here["label"] if gold_here else "O"
            confusion[(gold_lbl, lbl)] += 1
            per_label_fp[lbl].append({
                "sent_idx": sent_idx, "sentence": sent,
                "form": pe["form"], "begin": pe["begin"], "end": pe["end"],
                "gold_label": gold_lbl,
                "gold_form":  gold_here["form"] if gold_here else "",
            })

        for gi, ge in enumerate(gold_piis):
            if gi in matched_gold: continue
            lbl = ge["label"]
            per_label[lbl][2] += 1
            pred_here = find_overlapping(pred_ents, ge["begin"], ge["end"])
            pred_lbl  = pred_here["label"] if pred_here else "O"
            per_label_fn[lbl].append({
                "sent_idx": sent_idx, "sentence": sent,
                "form": ge["form"], "begin": ge["begin"], "end": ge["end"],
                "pred_label": pred_lbl,
                "pred_form":  pred_here["form"] if pred_here else "",
            })

    micro_f1, micro_p, micro_r = safe_f1(micro_tp, micro_fp, micro_fn)

    print(f"\n{'='*68}")
    print(f"[{args.split}]  Micro F1={micro_f1:.4f}  P={micro_p:.4f}  R={micro_r:.4f}")
    print(f"  TP={micro_tp}  FP={micro_fp}  FN={micro_fn}")
    print(f"{'='*68}")
    label_rows = []
    for lbl in TARGET_LABELS:
        tp, fp, fn = per_label[lbl]
        f1, p, r   = safe_f1(tp, fp, fn)
        label_rows.append((lbl, f1, p, r, tp, fp, fn))
        print(f"  {lbl:28s} F1={f1:.4f} P={p:.4f} R={r:.4f}  "
              f"TP={tp:5d} FP={fp:5d} FN={fn:5d}")

    ts          = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    tag         = f"{args.tag}_" if args.tag else ""
    results_dir = _results_dir_for(model_dir)
    md_path     = results_dir / f"eval_{args.split}_{tag}{ts}.md"
    L = [
        f"# 평가 결과 (baseline/무형태소): {args.split}  ({ts})",
        f"",
        f"모델: `{model_dir}`  |  tag: `{args.tag}`",
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
            ctx = highlight(ex["sentence"], ex["begin"], ex["end"])
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
            ctx = highlight(ex["sentence"], ex["begin"], ex["end"])
            ps  = f"{ex['pred_form']} ({ex['pred_label']})" if ex["pred_form"] else ex["pred_label"]
            L.append(f"| {ex['sent_idx']} | `{ex['form']}` | {ps} | {ctx} |")
        L.append("")

    md_path.write_text("\n".join(L), encoding="utf-8")
    print(f"\nMD 저장: {md_path}")
    return micro_f1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--split",      default="test", choices=["test", "valid"])
    parser.add_argument("--data-dir",   default="", help="train/valid/test JSON 디렉터리 (기본: data 또는 DATA_DIR)")
    parser.add_argument("--model_dir",  default=str(BASE_DIR / "models" / "xlm_roberta_large" / "seed42"))
    parser.add_argument("--tag",        default="")
    parser.add_argument("--batch_size", type=int, default=64)
    parser.add_argument("--max_length", type=int, default=256)
    args = parser.parse_args()
    evaluate(args)
