"""
skt/A.X-Encoder-base PII NER 평가 스크립트 (19개 라벨)

사용법:
    python eval.py --split test
    python eval.py --split valid
    python eval.py --split test --model_dir /path/to/model
"""

import argparse
import datetime
import json
import re
from collections import defaultdict
from pathlib import Path

import torch
from kiwipiepy import Kiwi
from transformers import AutoModelForTokenClassification, AutoTokenizer

_kiwi = Kiwi()

# ── 경로 ──────────────────────────────────────────────────────────────────────
BASE_DIR    = Path(__file__).resolve().parent
DATA_DIR    = BASE_DIR / "data"
RESULTS_DIR = BASE_DIR / "results" / "skt_encoder"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

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

# ── 정규식 후처리 ──────────────────────────────────────────────────────────────
_PLATE_MID = "가나다라마바사아자차카타파하거너더러머버서어저처커터퍼허고노도로모보소오조초코토포호구누두루무부수우주"
_PLATE_REGION = (
    r"(?:서울|경기|경남|경북|전남|전북|충남|충북|강원|울산|부산|대구|인천|광주|대전|세종|제주"
    r"|경상남도|경상북도|전라남도|전라북도|충청남도|충청북도|강원도"
    r"|서울특별시|부산광역시|대구광역시|인천광역시|광주광역시|대전광역시|울산광역시)\s+"
)
# 규칙은 '우선순위 순서'로 정의 (위 = 더 구체적/신뢰도 높음).
# 한국어가 숫자 바로 뒤에 붙으면(예: "5908로", "1230644입니다") \b 가 깨지므로
# 단어경계(\b) 대신 숫자경계 (?<!\d)/(?!\d) 를 사용한다.
# 주민/외국인등록번호는 형식이 \d{6}-\d{7} 로 동일하므로 7번째 자리(뒷자리 첫 숫자)로 구분:
#   1~4 = 주민등록번호, 5~9 = 외국인등록번호
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
    """
    정규식 후처리. 우선순위 순서대로 적용하며, 이미 상위 규칙이 점유한 span 과
    겹치는 하위 규칙 매치는 버린다.
    예) 카드번호 4854-6263-9733-5908 를 카드(상위)가 먼저 점유 →
        계좌 정규식(하위)이 앞 3그룹(4854-6263-9733)을 훔치지 못함.
    """
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


# ── character BIO → entity 변환 ───────────────────────────────────────────────
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
            # 공백을 가운데 둔 I- 연결 허용 (주소 스팬 등)
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
    """인접한 LC_ADDRESS 스팬을 공백 기준으로 합침 (주소 분리 방지)."""
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


# ── F1 계산 ───────────────────────────────────────────────────────────────────
def safe_f1(tp, fp, fn):
    p = tp / (tp + fp) if (tp + fp) else 0.0
    r = tp / (tp + fn) if (tp + fn) else 0.0
    f = 2 * p * r / (p + r) if (p + r) else 0.0
    return f, p, r


# ── 배치 예측 ─────────────────────────────────────────────────────────────────
def predict_batch(
    model, tokenizer, sentences: list[str],
    batch_size: int = 64, max_length: int = 256, device: str = "cuda"
) -> list[list[dict]]:
    kiwi_all = [_kiwi.tokenize(s) for s in sentences]

    def encode(sent, kiwi_toks):
        morphemes = [t.form for t in kiwi_toks] if kiwi_toks else [sent]
        return tokenizer(morphemes, is_split_into_words=True,
                         truncation=True, max_length=max_length)

    all_encodings = [encode(s, k) for s, k in zip(sentences, kiwi_all)]
    all_entities  = []

    for bs in range(0, len(sentences), batch_size):
        batch_encs  = all_encodings[bs: bs + batch_size]
        batch_sents = sentences[bs: bs + batch_size]
        batch_kiwi  = kiwi_all[bs: bs + batch_size]
        max_len     = max(len(e["input_ids"]) for e in batch_encs)
        pad_id      = tokenizer.pad_token_id or 0

        ids_list, mask_list = [], []
        for e in batch_encs:
            pad = max_len - len(e["input_ids"])
            ids_list.append(e["input_ids"]       + [pad_id] * pad)
            mask_list.append(e["attention_mask"] + [0]      * pad)

        ids  = torch.tensor(ids_list,  dtype=torch.long).to(device)
        mask = torch.tensor(mask_list, dtype=torch.long).to(device)
        with torch.inference_mode():
            logits = model(input_ids=ids, attention_mask=mask).logits
        token_preds = logits.argmax(-1).cpu().tolist()

        for sent, enc, kiwi_toks, preds in zip(batch_sents, batch_encs, batch_kiwi, token_preds):
            morphemes   = [t.form  for t in kiwi_toks] if kiwi_toks else [sent]
            morph_start = [t.start for t in kiwi_toks] if kiwi_toks else [0]
            word_ids    = enc.word_ids()

            char_labels = ["O"] * len(sent)
            seen_morph  = set()
            for wid, pid in zip(word_ids, preds):
                if wid is None or wid in seen_morph:
                    continue
                seen_morph.add(wid)
                tag        = ID2LABEL.get(pid, "O")
                orig_start = morph_start[wid]
                orig_end   = orig_start + len(morphemes[wid])
                cont       = "I-" + tag[2:] if tag.startswith("B-") else tag
                for k, c in enumerate(range(orig_start, min(orig_end, len(sent)))):
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


# ── 메인 평가 ─────────────────────────────────────────────────────────────────
def evaluate(args):
    device    = "cuda" if torch.cuda.is_available() else "cpu"
    model_dir = Path(args.model_dir)

    print(f"모델: {model_dir}")
    print(f"평가: {args.split}.json  →  {device}")

    tokenizer = AutoTokenizer.from_pretrained(str(model_dir), trust_remote_code=True)
    model     = AutoModelForTokenClassification.from_pretrained(
        str(model_dir), trust_remote_code=True).to(device)
    model.eval()

    data          = json.load(open(DATA_DIR / f"{args.split}.json", encoding="utf-8"))
    sentences     = [d["sentence"] for d in data]
    gold_pii_list = [d["PII_set"]  for d in data]

    print(f"총 {len(sentences):,}문장 예측 중...")
    pred_list = predict_batch(model, tokenizer, sentences,
                              batch_size=args.batch_size,
                              max_length=args.max_length, device=device)

    # ── 집계 ─────────────────────────────────────────────────────────────────
    micro_tp = micro_fp = micro_fn = 0
    per_label     = defaultdict(lambda: [0, 0, 0])
    per_label_fp  = defaultdict(list)
    per_label_fn  = defaultdict(list)
    confusion     = defaultdict(int)

    for item, gold_piis, pred_ents in zip(data, gold_pii_list, pred_list):
        sent     = item["sentence"]
        sent_idx = item["sent_idx"]

        # span-overlap 기반 TP 매칭 (같은 레이블끼리만)
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

    # ── 터미널 출력 ───────────────────────────────────────────────────────────
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

    # ── Markdown 저장 ─────────────────────────────────────────────────────────
    ts      = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    md_path = RESULTS_DIR / f"eval_{args.split}_{ts}.md"
    L = [
        f"# 평가 결과: {args.split}  ({ts})",
        f"",
        f"모델: `{model_dir}`",
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

    # 혼동 분석
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
    parser.add_argument("--model_dir",  default=str(BASE_DIR / "models" / "skt_encoder"))
    parser.add_argument("--batch_size", type=int, default=64)
    parser.add_argument("--max_length", type=int, default=256)
    args = parser.parse_args()
    evaluate(args)
