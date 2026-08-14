"""
Evaluate a rule/NLP baseline:
Microsoft Presidio PatternRecognizer + Korean spaCy NER + Korean regex recognizers.

This script intentionally uses no trainable KDPII model. Regex hits are produced
through Presidio PatternRecognizer objects, and Korean spaCy NER outputs are
conservatively mapped into the KDPII label space.
"""

import argparse
import datetime
import json
import re
from collections import defaultdict
from pathlib import Path

import eval_baseline as eb

try:
    from presidio_analyzer import Pattern, PatternRecognizer
except Exception:  # pragma: no cover - local machines may not have Presidio.
    Pattern = None
    PatternRecognizer = None


BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR / "results" / "presidio_ko_spacy_regex"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

TARGET_LABELS = eb.TARGET_LABELS
COMMON15_EXCLUDED = {"FD_MAJOR", "OGG_EDUCATION", "QT_AGE", "QT_ALIEN_NUMBER"}

DIRECT_LABELS = {
    "PS_NAME",
    "LC_ADDRESS",
    "QT_MOBILE",
    "QT_PHONE",
    "QT_RESIDENT_NUMBER",
    "QT_ALIEN_NUMBER",
    "QT_DRIVER_NUMBER",
    "QT_PLATE_NUMBER",
    "QT_ACCOUNT_NUMBER",
    "QT_CARD_NUMBER",
    "TMI_EMAIL",
    "QT_PASSPORT_NUMBER",
}

INDIRECT_LABELS = {
    "DT_BIRTH",
    "QT_AGE",
    "OG_WORKPLACE",
    "OG_DEPARTMENT",
    "CV_POSITION",
    "OGG_EDUCATION",
    "FD_MAJOR",
}


def parse_label_csv(raw: str) -> list[str]:
    if not raw:
        return []
    return [x.strip() for x in raw.split(",") if x.strip()]


def resolve_eval_labels(args) -> tuple[list[str], list[str]]:
    include = parse_label_csv(args.include_labels)
    exclude = parse_label_csv(args.exclude_labels)
    known = set(TARGET_LABELS)
    unknown = sorted((set(include) | set(exclude)) - known)
    if unknown:
        raise ValueError(f"Unknown labels in filter: {unknown}")
    labels = include if include else list(TARGET_LABELS)
    labels = [lbl for lbl in labels if lbl not in set(exclude)]
    if not labels:
        raise ValueError("No labels left after applying include/exclude filters.")
    dropped = [lbl for lbl in TARGET_LABELS if lbl not in set(labels)]
    return labels, dropped


def safe_compile(pattern: str) -> re.Pattern:
    return re.compile(pattern, re.IGNORECASE | re.MULTILINE)


def build_regex_specs() -> list[tuple[str, str, float]]:
    plate_mid = eb._PLATE_MID
    plate_region = eb._PLATE_REGION
    bank = (
        r"(?:국민|KB국민|신한|우리|하나|농협|NH농협|기업|IBK기업|카카오뱅크|케이뱅크|"
        r"토스뱅킹|SC제일|제일|씨티|우체국|수협|새마을|신협|부산|대구|전북|광주|경남|"
        r"산업|제주|수출입|저축|은행)"
    )
    return [
        ("QT_RESIDENT_NUMBER", r"(?<!\d)\d{6}-[1-4]\d{6}(?!\d)", 0.95),
        ("QT_ALIEN_NUMBER", r"(?<!\d)\d{6}-[5-9]\d{6}(?!\d)", 0.95),
        ("QT_ALIEN_NUMBER", r"(?<![A-Z0-9])[A-Z]\d{12}(?![A-Z0-9])", 0.90),
        ("QT_DRIVER_NUMBER", r"(?<!\d)(?:[가-힣]{2,4}\s+)?\d{2}-\d{2}-\d{6}-\d{2}(?!\d)", 0.93),
        ("QT_CARD_NUMBER", r"(?<!\d)\d{4}[\-\s]\d{4}[\-\s]\d{4}[\-\s]\d{4}(?!\d)", 0.93),
        ("QT_CARD_NUMBER", r"(?<!\d)\d{4}[\-\s]\d{6}[\-\s]\d{4,5}(?!\d)", 0.90),
        ("QT_MOBILE", r"(?<!\d)01[016789][\-.\s]?\d{3,4}[\-.\s]?\d{4}(?!\d)", 0.92),
        ("QT_PHONE", r"(?<!\d)0(?:2|[3-9]\d)[\-.\s]\d{3,4}[\-.\s]\d{4}(?!\d)", 0.90),
        ("QT_PLATE_NUMBER", rf"(?:{plate_region})?\d{{2,3}}\s?[{plate_mid}]\s?\d{{4}}(?!\d)", 0.90),
        ("TMI_EMAIL", r"(?<![A-Z0-9._%+-])[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}(?![A-Z0-9._%+-])", 0.95),
        ("QT_PASSPORT_NUMBER", r"(?<![A-Z0-9])M[A-Z0-9]{8}(?![A-Z0-9])", 0.90),
        ("QT_ACCOUNT_NUMBER", rf"{bank}\s*\d{{2,6}}[\-\s]\d{{2,6}}[\-\s]\d{{2,6}}(?:[\-\s]\d{{1,6}})?", 0.80),
        ("QT_ACCOUNT_NUMBER", rf"\d{{2,6}}[\-\s]\d{{2,6}}[\-\s]\d{{4,6}}(?:[\-\s]\d{{1,6}})?\s*{bank}", 0.80),
        ("QT_ACCOUNT_NUMBER", r"(?<!\d)\d{2,6}[-]\d{2,6}[-]\d{4,7}(?:[-]\d{1,4})?(?!\d)", 0.74),
        ("QT_ACCOUNT_NUMBER", r"(?<!\d)\d{2,6}\s\d{2,6}\s\d{2,6}\s\d{2,6}(?!\d)", 0.70),
    ]


def build_presidio_recognizers():
    if Pattern is None or PatternRecognizer is None:
        return None
    recognizers = []
    for idx, (label, regex, score) in enumerate(build_regex_specs()):
        recognizers.append(
            PatternRecognizer(
                supported_entity=label,
                supported_language="ko",
                name=f"ko_regex_{label}_{idx}",
                patterns=[Pattern(name=f"{label}_{idx}", regex=regex, score=score)],
            )
        )
    return recognizers


def regex_predict_with_presidio(sentence: str, recognizers) -> list[dict]:
    if recognizers is None:
        hits = []
        for label, regex, score in build_regex_specs():
            for m in safe_compile(regex).finditer(sentence):
                hits.append({
                    "form": m.group(),
                    "label": label,
                    "begin": m.start(),
                    "end": m.end(),
                    "score": score,
                    "source": "regex_fallback",
                })
        return hits

    hits = []
    for recognizer in recognizers:
        for res in recognizer.analyze(sentence, entities=[recognizer.supported_entities[0]]):
            hits.append({
                "form": sentence[res.start:res.end],
                "label": res.entity_type,
                "begin": res.start,
                "end": res.end,
                "score": float(res.score),
                "source": "presidio_regex",
            })
    return hits


SPACY_LABEL_MAP = {
    "PERSON": "PS_NAME",
    "PER": "PS_NAME",
    "PS": "PS_NAME",
    "ORG": "OG_WORKPLACE",
    "OG": "OG_WORKPLACE",
    "GPE": "LC_ADDRESS",
    "LOC": "LC_ADDRESS",
    "LC": "LC_ADDRESS",
    "FAC": "LC_ADDRESS",
    "DATE": "DT_BIRTH",
    "DT": "DT_BIRTH",
}


def load_spacy(model_name: str):
    import spacy

    return spacy.load(model_name)


def spacy_predict(sentence: str, nlp, use_date: bool = True) -> list[dict]:
    if nlp is None:
        return []
    doc = nlp(sentence)
    hits = []
    for ent in doc.ents:
        kdpii_label = SPACY_LABEL_MAP.get(ent.label_)
        if kdpii_label is None:
            continue
        if kdpii_label == "DT_BIRTH" and not use_date:
            continue
        hits.append({
            "form": ent.text,
            "label": kdpii_label,
            "begin": ent.start_char,
            "end": ent.end_char,
            "score": 0.55,
            "source": f"spacy:{ent.label_}",
        })
    return hits


def remove_overlaps(candidates: list[dict]) -> list[dict]:
    def length(ent):
        return ent["end"] - ent["begin"]

    accepted = []
    for ent in sorted(candidates, key=lambda e: (-e["score"], -length(e), e["begin"], e["end"])):
        if ent["begin"] >= ent["end"]:
            continue
        if any(ent["begin"] < old["end"] and old["begin"] < ent["end"] for old in accepted):
            continue
        accepted.append(dict(ent))
    accepted.sort(key=lambda e: (e["begin"], e["end"]))
    for ent in accepted:
        ent.pop("score", None)
        ent.pop("source", None)
    return accepted


def predict_dataset(sentences: list[str], recognizers, nlp, use_spacy_date: bool) -> list[list[dict]]:
    pred_list = []
    for i, sentence in enumerate(sentences, start=1):
        if i % 500 == 0:
            print(f"  predicted {i:,}/{len(sentences):,}")
        candidates = []
        candidates.extend(regex_predict_with_presidio(sentence, recognizers))
        candidates.extend(spacy_predict(sentence, nlp, use_date=use_spacy_date))
        ents = remove_overlaps(candidates)
        ents = eb.merge_lc_address(ents, sentence)
        pred_list.append(ents)
    return pred_list


def find_overlapping(entities, begin, end):
    for ent in entities:
        if ent["begin"] < end and ent["end"] > begin:
            return ent
    return None


def filter_entities(entities: list[dict], allowed_labels: set[str]) -> list[dict]:
    return [e for e in entities if e.get("label") in allowed_labels]


def group_metric(per_label: dict, labels: set[str]) -> tuple[float, float, float, int, int, int]:
    tp = fp = fn = 0
    for label in labels:
        t, f, n = per_label[label]
        tp += t
        fp += f
        fn += n
    f1, p, r = eb.safe_f1(tp, fp, fn)
    return f1, p, r, tp, fp, fn


def evaluate(args):
    data_dir = eb.resolve_data_dir(args.data_dir)
    eval_labels, dropped_labels = resolve_eval_labels(args)
    allowed_labels = set(eval_labels)

    print("[Presidio+ko spaCy+KO regex]")
    print(f"data={data_dir / (args.split + '.json')}")
    print(f"spacy_model={args.spacy_model}")
    print(f"include={args.include_labels or '-'} exclude={args.exclude_labels or '-'}")
    if dropped_labels:
        print(f"dropped_labels={', '.join(dropped_labels)}")

    if Pattern is None or PatternRecognizer is None:
        if args.require_presidio:
            raise RuntimeError("presidio_analyzer is not installed.")
        print("[WARN] presidio_analyzer not installed; using local regex fallback.")
    recognizers = build_presidio_recognizers()

    nlp = None
    if not args.disable_spacy:
        nlp = load_spacy(args.spacy_model)
        print(f"loaded spaCy pipeline: {nlp.pipe_names}")

    data = json.load(open(data_dir / f"{args.split}.json", encoding="utf-8"))
    sentences = [d["sentence"] for d in data]
    gold_pii_list = [d["PII_set"] for d in data]
    print(f"sentences={len(sentences):,}")

    pred_list = predict_dataset(sentences, recognizers, nlp, args.use_spacy_date)

    micro_tp = micro_fp = micro_fn = 0
    per_label = defaultdict(lambda: [0, 0, 0])
    per_label_fp = defaultdict(list)
    per_label_fn = defaultdict(list)
    confusion = defaultdict(int)
    excluded_gold = 0
    excluded_pred = 0

    for item, raw_gold_piis, raw_pred_ents in zip(data, gold_pii_list, pred_list):
        sent = item["sentence"]
        sent_idx = item["sent_idx"]
        excluded_gold += sum(1 for e in raw_gold_piis if e.get("label") not in allowed_labels)
        excluded_pred += sum(1 for e in raw_pred_ents if e.get("label") not in allowed_labels)
        gold_piis = filter_entities(raw_gold_piis, allowed_labels)
        pred_ents = filter_entities(raw_pred_ents, allowed_labels)

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
            gold_here = find_overlapping(gold_piis, pe["begin"], pe["end"])
            gold_lbl = gold_here["label"] if gold_here else "O"
            confusion[(gold_lbl, lbl)] += 1
            per_label_fp[lbl].append({
                "sent_idx": sent_idx,
                "sentence": sent,
                "form": pe["form"],
                "begin": pe["begin"],
                "end": pe["end"],
                "gold_label": gold_lbl,
                "gold_form": gold_here["form"] if gold_here else "",
            })

        for gi, ge in enumerate(gold_piis):
            if gi in matched_gold:
                continue
            lbl = ge["label"]
            per_label[lbl][2] += 1
            pred_here = find_overlapping(pred_ents, ge["begin"], ge["end"])
            pred_lbl = pred_here["label"] if pred_here else "O"
            per_label_fn[lbl].append({
                "sent_idx": sent_idx,
                "sentence": sent,
                "form": ge["form"],
                "begin": ge["begin"],
                "end": ge["end"],
                "pred_label": pred_lbl,
                "pred_form": pred_here["form"] if pred_here else "",
            })

    micro_f1, micro_p, micro_r = eb.safe_f1(micro_tp, micro_fp, micro_fn)
    direct_labels = DIRECT_LABELS & allowed_labels
    indirect_labels = INDIRECT_LABELS & allowed_labels
    direct = group_metric(per_label, direct_labels)
    indirect = group_metric(per_label, indirect_labels)

    print(f"\n{'=' * 72}")
    print(f"[{args.split}] Micro F1={micro_f1:.4f} P={micro_p:.4f} R={micro_r:.4f}")
    print(f"TP={micro_tp} FP={micro_fp} FN={micro_fn}")
    print(f"Direct   F1={direct[0]:.4f} P={direct[1]:.4f} R={direct[2]:.4f} TP={direct[3]} FP={direct[4]} FN={direct[5]}")
    print(f"Indirect F1={indirect[0]:.4f} P={indirect[1]:.4f} R={indirect[2]:.4f} TP={indirect[3]} FP={indirect[4]} FN={indirect[5]}")
    if dropped_labels:
        print(f"excluded gold={excluded_gold} pred={excluded_pred}")
    print(f"{'=' * 72}")

    label_rows = []
    for lbl in eval_labels:
        tp, fp, fn = per_label[lbl]
        f1, p, r = eb.safe_f1(tp, fp, fn)
        label_rows.append((lbl, f1, p, r, tp, fp, fn))
        print(f"  {lbl:22s} F1={f1:.4f} P={p:.4f} R={r:.4f} TP={tp:4d} FP={fp:4d} FN={fn:4d}")

    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    tag = f"{args.tag}_" if args.tag else ""
    md_path = RESULTS_DIR / f"eval_presidio_ko_spacy_regex_{args.split}_{tag}{ts}.md"
    summary_path = RESULTS_DIR / f"eval_presidio_ko_spacy_regex_{args.split}_{tag}{ts}.json"

    lines = [
        f"# Microsoft Presidio + Korean spaCy NER + KO regex: {args.split} ({ts})",
        "",
        f"data_dir=`{data_dir}`",
        f"spaCy model=`{args.spacy_model}`",
        f"evaluated_labels={len(eval_labels)}: `{', '.join(eval_labels)}`",
        f"excluded_labels={len(dropped_labels)}: `{', '.join(dropped_labels) if dropped_labels else '-'}`",
        f"excluded_gold_entities={excluded_gold}  excluded_predicted_entities={excluded_pred}",
        "",
        "## Overall",
        "",
        "| Metric | F1 | P | R | TP | FP | FN |",
        "|---|---:|---:|---:|---:|---:|---:|",
        f"| Entity Micro | **{micro_f1:.4f}** | {micro_p:.4f} | {micro_r:.4f} | {micro_tp} | {micro_fp} | {micro_fn} |",
        f"| Direct PII | **{direct[0]:.4f}** | {direct[1]:.4f} | {direct[2]:.4f} | {direct[3]} | {direct[4]} | {direct[5]} |",
        f"| Indirect PII | **{indirect[0]:.4f}** | {indirect[1]:.4f} | {indirect[2]:.4f} | {indirect[3]} | {indirect[4]} | {indirect[5]} |",
        "",
        "## Per Label",
        "",
        "| Label | F1 | P | R | TP | FP | FN |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for lbl, f1, p, r, tp, fp, fn in sorted(label_rows, key=lambda x: -x[1]):
        lines.append(f"| {lbl} | {f1:.4f} | {p:.4f} | {r:.4f} | {tp} | {fp} | {fn} |")

    conf_items = [(cnt, g, p) for (g, p), cnt in confusion.items() if g != p]
    conf_items.sort(reverse=True)
    if conf_items:
        lines += ["", "## Confusion", "", "| Count | Gold | Pred |", "|---:|---|---|"]
        for cnt, gold_label, pred_label in conf_items[:40]:
            lines.append(f"| {cnt} | {gold_label} | {pred_label} |")

    for lbl, f1, p, r, tp, fp, fn in sorted(label_rows, key=lambda x: -x[1]):
        fps = per_label_fp[lbl]
        fns = per_label_fn[lbl]
        lines += [
            "",
            f"### {lbl}",
            f"F1={f1:.4f} | P={p:.4f} | R={r:.4f} | TP={tp} | FP={fp} | FN={fn}",
            "",
            f"#### FP ({len(fps)})",
            "",
            "| sent_idx | pred form | gold-at-span | sentence |",
            "|---|---|---|---|",
        ]
        for ex in fps[: eb.EXAMPLE_CAP]:
            ctx = eb.highlight(ex["sentence"], ex["begin"], ex["end"])
            gold = f"{ex['gold_form']} ({ex['gold_label']})" if ex["gold_form"] else ex["gold_label"]
            lines.append(f"| {ex['sent_idx']} | `{ex['form']}` | {gold} | {ctx} |")

        lines += [
            "",
            f"#### FN ({len(fns)})",
            "",
            "| sent_idx | gold form | pred-at-span | sentence |",
            "|---|---|---|---|",
        ]
        for ex in fns[: eb.EXAMPLE_CAP]:
            ctx = eb.highlight(ex["sentence"], ex["begin"], ex["end"])
            pred = f"{ex['pred_form']} ({ex['pred_label']})" if ex["pred_form"] else ex["pred_label"]
            lines.append(f"| {ex['sent_idx']} | `{ex['form']}` | {pred} | {ctx} |")

    md_path.write_text("\n".join(lines), encoding="utf-8")
    summary = {
        "split": args.split,
        "data_dir": str(data_dir),
        "tag": args.tag,
        "spacy_model": args.spacy_model,
        "labels": eval_labels,
        "excluded_labels": dropped_labels,
        "micro": {"f1": micro_f1, "p": micro_p, "r": micro_r, "tp": micro_tp, "fp": micro_fp, "fn": micro_fn},
        "direct": {"f1": direct[0], "p": direct[1], "r": direct[2], "tp": direct[3], "fp": direct[4], "fn": direct[5]},
        "indirect": {"f1": indirect[0], "p": indirect[1], "r": indirect[2], "tp": indirect[3], "fp": indirect[4], "fn": indirect[5]},
        "per_label": {
            lbl: {"f1": f1, "p": p, "r": r, "tp": tp, "fp": fp, "fn": fn}
            for lbl, f1, p, r, tp, fp, fn in label_rows
        },
    }
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nMD 저장: {md_path}")
    print(f"JSON 저장: {summary_path}")
    return micro_f1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", default="test", choices=["test", "valid"])
    parser.add_argument("--data-dir", default="", help="JSON directory. Defaults to data or DATA_DIR.")
    parser.add_argument("--tag", default="")
    parser.add_argument("--spacy-model", default="ko_core_news_lg")
    parser.add_argument("--disable-spacy", action="store_true")
    parser.add_argument("--use-spacy-date", action="store_true", default=True)
    parser.add_argument("--no-spacy-date", action="store_false", dest="use_spacy_date")
    parser.add_argument("--require-presidio", action="store_true")
    parser.add_argument("--include-labels", default="")
    parser.add_argument("--exclude-labels", default="")
    args = parser.parse_args()
    evaluate(args)
