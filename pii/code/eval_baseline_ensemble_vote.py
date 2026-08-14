"""
entity-level 다수결 앙상블 (chan ensemble_chan.py 이식).

표준 HF 모델(eval_baseline.predict_batch)과 CRF+gaz 모델(eval_crf_gaz) 모두 지원.
각 모델을 독립 예측(후처리 포함) 후 span 겹침 클러스터링 → min_votes 이상 채택.

사용법:
    # 기존 챔피언 3-seed + entity voting
    python3 eval_baseline_ensemble_vote.py --split test --min_votes 2 --tag reg_x3_vote \\
        --model_dirs models/skt_encoder_distill_aug_reg/seed42 \\
                     models/skt_encoder_distill_aug_reg/seed43 \\
                     models/skt_encoder_distill_aug_reg/seed44

    # CRF+gaz 3-seed
    python3 eval_baseline_ensemble_vote.py --split test --min_votes 2 \\
        --model_dirs models/skt_encoder_distill_crf_gaz_reg/seed42 ...
"""

import argparse
import datetime
import json
from collections import Counter, defaultdict
from pathlib import Path

import torch
from transformers import AutoModelForTokenClassification, AutoTokenizer

import eval_baseline as eb
import eval_crf_gaz as ecg
from pii_model import TokenClassifierForPII

BASE_DIR = eb.BASE_DIR
DATA_DIR = eb.DATA_DIR
TARGET_LABELS = eb.TARGET_LABELS
EXAMPLE_CAP = eb.EXAMPLE_CAP
RESULTS_DIR = BASE_DIR / "results" / "ensemble_vote"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def parse_label_csv(raw: str) -> list[str]:
    if not raw:
        return []
    return [x.strip() for x in raw.split(",") if x.strip()]


def resolve_eval_labels(args) -> tuple[list[str], list[str]]:
    include = parse_label_csv(getattr(args, "include_labels", ""))
    exclude = parse_label_csv(getattr(args, "exclude_labels", ""))
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


def filter_entities(entities: list[dict], allowed_labels: set[str]) -> list[dict]:
    return [e for e in entities if e.get("label") in allowed_labels]


def load_and_predict(model_dir: Path, sentences, device, batch_size, max_length):
    label_map = ecg.load_label_map(model_dir)
    if ecg.is_pii_model(model_dir):
        tokenizer_src = label_map.get("model_id") or str(model_dir)
        tokenizer = AutoTokenizer.from_pretrained(tokenizer_src, trust_remote_code=True, use_fast=True)
        model = TokenClassifierForPII.from_pretrained(str(model_dir), trust_remote_code=True)
        model = model.to(torch.float32).to(device)
        model.eval()
        target_labels = label_map.get("target_labels", TARGET_LABELS)
        gaz_trie = ecg.load_gazetteer_trie(model_dir, target_labels) if label_map.get("use_gazetteer") else None
        id2label = {int(k): v for k, v in label_map.get("id2label", {}).items()} or model.config.id2label
        preds = ecg.predict_batch_bio(
            model, tokenizer, sentences, device, id2label, gaz_trie=gaz_trie,
            num_gaz_labels=len(target_labels), batch_size=batch_size, max_length=max_length,
        )
        arch = "pii_hwan"
    else:
        tokenizer = AutoTokenizer.from_pretrained(str(model_dir), trust_remote_code=True, use_fast=True)
        model = AutoModelForTokenClassification.from_pretrained(
            str(model_dir), trust_remote_code=True).to(device)
        model.eval()
        preds = eb.predict_batch(
            model, tokenizer, sentences, batch_size=batch_size,
            max_length=max_length, device=device,
        )
        arch = "baseline"
    del model
    torch.cuda.empty_cache()
    return preds, arch


def ensemble_vote(pred_lists, sentences, min_votes):
    n_models = len(pred_lists)
    n_sent = len(sentences)
    combined = []
    for i in range(n_sent):
        cands = []
        for m in range(n_models):
            for e in pred_lists[m][i]:
                cands.append((m, e))
        k = len(cands)
        parent = list(range(k))

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(a, b):
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[ra] = rb

        for a in range(k):
            ea = cands[a][1]
            for b in range(a + 1, k):
                eb_ = cands[b][1]
                if ea["label"] != eb_["label"]:
                    continue
                if ea["begin"] < eb_["end"] and eb_["begin"] < ea["end"]:
                    union(a, b)

        clusters = defaultdict(list)
        for idx in range(k):
            clusters[find(idx)].append(idx)

        final_ents = []
        for members in clusters.values():
            model_votes = set(cands[idx][0] for idx in members)
            if len(model_votes) < min_votes:
                continue
            span_counts = Counter((cands[idx][1]["begin"], cands[idx][1]["end"]) for idx in members)
            best_span, _ = span_counts.most_common(1)[0]
            rep = None
            for m_priority in range(n_models):
                for idx in members:
                    if cands[idx][0] == m_priority and (cands[idx][1]["begin"], cands[idx][1]["end"]) == best_span:
                        rep = cands[idx][1]
                        break
                if rep is not None:
                    break
            final_ents.append(dict(rep))

        final_ents.sort(key=lambda e: e["begin"])
        sent = sentences[i]
        final_ents = eb.merge_lc_address(final_ents, sent)
        final_ents = eb.regex_postprocess(sent, final_ents)
        combined.append(final_ents)
    return combined


def _cache_path(model_dir: Path, data_dir: Path, split: str) -> Path:
    cache_dir = RESULTS_DIR / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    safe_name = str(model_dir).replace("\\", "/").strip("/").replace("/", "__")
    safe_data = str(data_dir.resolve()).replace("\\", "/").strip("/").replace("/", "__")
    return cache_dir / f"{safe_name}__{safe_data}__{split}.json"


def evaluate(args):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model_dirs = [Path(d) for d in args.model_dirs]

    print(f"[ENTITY VOTE] 모델 {len(model_dirs)}개 (min_votes={args.min_votes}):")
    for d in model_dirs:
        print(f"  - {d}")

    data_dir = eb.resolve_data_dir(getattr(args, "data_dir", None))
    eval_labels, dropped_labels = resolve_eval_labels(args)
    allowed_labels = set(eval_labels)
    print(f"평가 데이터: {data_dir / (args.split + '.json')}")
    if dropped_labels:
        print(f"라벨 필터: {len(eval_labels)}개 평가, {len(dropped_labels)}개 제외")
        print(f"  제외: {', '.join(dropped_labels)}")
    else:
        print(f"라벨 필터: 전체 {len(eval_labels)}개 라벨 평가")

    data = json.load(open(data_dir / f"{args.split}.json", encoding="utf-8"))
    sentences = [d["sentence"] for d in data]
    gold_pii_list = [d["PII_set"] for d in data]

    pred_lists = []
    for model_dir in model_dirs:
        cpath = _cache_path(model_dir, data_dir, args.split)
        if cpath.exists() and not args.no_cache:
            print(f"\n[{model_dir}] 캐시 사용: {cpath}")
            preds = json.loads(cpath.read_text(encoding="utf-8"))
        else:
            print(f"\n[{model_dir}] 예측 중...")
            preds, arch = load_and_predict(model_dir, sentences, device, args.batch_size, args.max_length)
            print(f"  아키텍처: {arch}  ({len(preds):,}문장)")
            cpath.write_text(json.dumps(preds, ensure_ascii=False), encoding="utf-8")
        pred_lists.append(preds)

    print(f"\n다수결 앙상블 (min_votes={args.min_votes})...")
    pred_list = ensemble_vote(pred_lists, sentences, args.min_votes)

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
            if pi in matched_pred:
                continue
            lbl = pe["label"]
            per_label[lbl][1] += 1
            gold_here = eb.find_overlapping(gold_piis, pe["begin"], pe["end"])
            gold_lbl = gold_here["label"] if gold_here else "O"
            confusion[(gold_lbl, lbl)] += 1
            per_label_fp[lbl].append({
                "sent_idx": sent_idx, "sentence": sent, "form": pe["form"],
                "begin": pe["begin"], "end": pe["end"], "gold_label": gold_lbl,
                "gold_form": gold_here["form"] if gold_here else "",
            })
        for gi, ge in enumerate(gold_piis):
            if gi in matched_gold:
                continue
            lbl = ge["label"]
            per_label[lbl][2] += 1
            pred_here = eb.find_overlapping(pred_ents, ge["begin"], ge["end"])
            pred_lbl = pred_here["label"] if pred_here else "O"
            per_label_fn[lbl].append({
                "sent_idx": sent_idx, "sentence": sent, "form": ge["form"],
                "begin": ge["begin"], "end": ge["end"], "pred_label": pred_lbl,
                "pred_form": pred_here["form"] if pred_here else "",
            })

    micro_f1, micro_p, micro_r = eb.safe_f1(micro_tp, micro_fp, micro_fn)
    print(f"\n{'='*68}")
    print(f"[{args.split} / VOTE×{len(model_dirs)}]  Micro F1={micro_f1:.4f}  P={micro_p:.4f}  R={micro_r:.4f}")
    print(f"  TP={micro_tp}  FP={micro_fp}  FN={micro_fn}")
    if dropped_labels:
        print(f"  excluded gold entities={excluded_gold}  excluded predicted entities={excluded_pred}")
    print(f"{'='*68}")
    label_rows = []
    for lbl in eval_labels:
        tp, fp, fn = per_label[lbl]
        f1, p, r = eb.safe_f1(tp, fp, fn)
        label_rows.append((lbl, f1, p, r, tp, fp, fn))
        print(f"  {lbl:22s} F1={f1:.4f} P={p:.4f} R={r:.4f}  TP={tp:5d} FP={fp:5d} FN={fn:5d}")

    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    tag = f"{args.tag}_" if args.tag else ""
    md_path = RESULTS_DIR / f"eval_vote_{args.split}_{tag}{ts}.md"
    L = [
        f"# entity-level 다수결 앙상블: {args.split}  ({ts})",
        f"",
        f"min_votes={args.min_votes}",
        f"data_dir=`{data_dir}`",
        f"evaluated_labels={len(eval_labels)}: `{', '.join(eval_labels)}`",
        f"excluded_labels={len(dropped_labels)}: `{', '.join(dropped_labels) if dropped_labels else '-'}`",
        f"excluded_gold_entities={excluded_gold}  excluded_predicted_entities={excluded_pred}",
        f"",
        f"| Entity Micro F1 | **{micro_f1:.4f}** |",
        f"| Precision | {micro_p:.4f} |",
        f"| Recall | {micro_r:.4f} |",
        f"| TP | {micro_tp} | FP | {micro_fp} | FN | {micro_fn} |",
        f"",
        f"| 레이블 | F1 | P | R | TP | FP | FN |",
        f"|--------|-----|---|---|----|----|-----|",
    ]
    for lbl, f1, p, r, tp, fp, fn in sorted(label_rows, key=lambda x: -x[1]):
        L.append(f"| {lbl} | {f1:.4f} | {p:.4f} | {r:.4f} | {tp} | {fp} | {fn} |")
    md_path.write_text("\n".join(L), encoding="utf-8")
    print(f"\nMD 저장: {md_path}")
    return micro_f1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", default="test", choices=["test", "valid"])
    parser.add_argument("--data-dir", default="", help="JSON 디렉터리 (기본: data 또는 DATA_DIR)")
    parser.add_argument("--model_dirs", nargs="+", required=True)
    parser.add_argument("--min_votes", type=int, default=2)
    parser.add_argument("--tag", default="")
    parser.add_argument("--batch_size", type=int, default=64)
    parser.add_argument("--max_length", type=int, default=256)
    parser.add_argument("--no_cache", action="store_true")
    parser.add_argument("--include-labels", default="",
                        help="쉼표 구분 평가 라벨 목록. 비우면 전체 TARGET_LABELS.")
    parser.add_argument("--exclude-labels", default="",
                        help="쉼표 구분 제외 라벨 목록. 예: FD_MAJOR,OGG_EDUCATION,QT_AGE,QT_ALIEN_NUMBER")
    args = parser.parse_args()
    evaluate(args)
