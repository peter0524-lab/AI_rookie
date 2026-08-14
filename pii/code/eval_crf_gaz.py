"""
CRF+gazetteer 커스텀 모델 평가 + 학습 중 quick eval.

regex/LC 병합/span-overlap F1 은 eval_baseline.py 와 동일.
"""

import argparse
import datetime
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import torch
from transformers import AutoTokenizer, TrainerCallback

import eval_baseline as eb
from gazetteer import GazetteerTrie, aggregate_to_tokens, load_gazetteer
from pii_model import TokenClassifierForPII

BASE_DIR = eb.BASE_DIR
DATA_DIR = eb.DATA_DIR
TARGET_LABELS = eb.TARGET_LABELS
ID2LABEL = eb.ID2LABEL
LABEL2ID = eb.LABEL2ID
NUM_GAZ_LABELS = len(TARGET_LABELS)


def _results_dir_for(model_dir: Path) -> Path:
    p = str(model_dir).replace("\\", "/")
    if "crf_gaz_synthetic" in p and "distill" not in p:
        d = BASE_DIR / "results" / "skt_encoder_crf_gaz_synthetic"
    elif "distill_crf_gaz" in p:
        d = BASE_DIR / "results" / "skt_encoder_distill_crf_gaz_synthetic" if "synthetic" in p else BASE_DIR / "results" / "skt_encoder_distill_crf_gaz"
    else:
        d = eb._results_dir_for(model_dir)
    d.mkdir(parents=True, exist_ok=True)
    return d


def load_label_map(model_dir: Path) -> dict:
    lm_path = model_dir / "label_map.json"
    if lm_path.exists():
        return json.loads(lm_path.read_text(encoding="utf-8"))
    return {}


def load_gazetteer_trie(model_dir: Path, target_labels):
    gaz_path = model_dir / "gazetteer.json"
    if not gaz_path.exists():
        return None
    return GazetteerTrie(load_gazetteer(str(gaz_path)), target_labels)


def is_pii_model(model_dir: Path) -> bool:
    cfg_path = model_dir / "config.json"
    if not cfg_path.exists():
        return False
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    return cfg.get("model_type") == "pii_hwan"


def predict_batch_bio(
    model, tokenizer, sentences, device, id2label, gaz_trie=None,
    num_gaz_labels=19, batch_size=64, max_length=256,
):
    all_entities = []
    for bs in range(0, len(sentences), batch_size):
        batch_sents = sentences[bs: bs + batch_size]
        enc = tokenizer(
            batch_sents, truncation=True, max_length=max_length, padding=True,
            return_offsets_mapping=True, return_tensors="pt",
        )
        offset_mapping = enc.pop("offset_mapping").tolist()
        word_ids_list = [enc.word_ids(i) for i in range(len(batch_sents))]
        ids = enc["input_ids"].to(device)
        mask = enc["attention_mask"].to(device)
        B, T = ids.shape

        label_mask = torch.zeros((B, T), dtype=torch.bool, device=device)
        for bi in range(B):
            seen = set()
            for ti, (wid, ce) in enumerate(zip(word_ids_list[bi], [o[1] for o in offset_mapping[bi]])):
                if wid is None or ce == 0 or wid in seen:
                    continue
                seen.add(wid)
                label_mask[bi, ti] = True

        gaz_features = None
        if gaz_trie is not None:
            gaz_batch = np.zeros((B, T, num_gaz_labels), dtype=np.float32)
            for bi, sent in enumerate(batch_sents):
                char_feat = gaz_trie.match_sentence(sent)
                tok_feat = aggregate_to_tokens(char_feat, offset_mapping[bi])
                gaz_batch[bi, : tok_feat.shape[0]] = tok_feat
            gaz_features = torch.tensor(gaz_batch, device=device)

        decoded = model.predict_tags(ids, mask, label_mask, gaz_features=gaz_features)

        for bi, sent in enumerate(batch_sents):
            offs = offset_mapping[bi]
            wids = word_ids_list[bi]
            word_span, word_order = {}, []
            for ti, (wid, (cs, ce)) in enumerate(zip(wids, offs)):
                if wid is None or ce == 0:
                    continue
                if wid not in word_span:
                    word_span[wid] = [cs, ce]
                    word_order.append(wid)
                else:
                    word_span[wid][0] = min(word_span[wid][0], cs)
                    word_span[wid][1] = max(word_span[wid][1], ce)

            tags = decoded[bi]
            char_labels = ["O"] * len(sent)
            for idx, wid in enumerate(word_order):
                if idx >= len(tags):
                    break
                tag = id2label.get(tags[idx], id2label.get(str(tags[idx]), "O"))
                if tag == "O":
                    continue
                ws, we = word_span[wid]
                cont = "I-" + tag[2:] if tag.startswith("B-") else tag
                for k, c in enumerate(range(ws, min(we, len(sent)))):
                    char_labels[c] = tag if k == 0 else cont

            ents = eb.char_bio_to_entities(sent, char_labels)
            ents = eb.merge_lc_address(ents, sent)
            ents = eb.regex_postprocess(sent, ents)
            all_entities.append(ents)

    return all_entities


def bio_to_entities(bio_seq):
    entities, start, cur = set(), None, None
    for i, tag in enumerate(bio_seq):
        if tag.startswith("B-"):
            if start is not None:
                entities.add((start, i, cur))
            start, cur = i, tag[2:]
        elif tag.startswith("I-") and cur == tag[2:]:
            pass
        else:
            if start is not None:
                entities.add((start, i, cur))
            start = cur = None
    if start is not None:
        entities.add((start, len(bio_seq), cur))
    return entities


def compute_entity_f1(true_seqs, pred_seqs):
    tp = fp = fn = 0
    for true_seq, pred_seq in zip(true_seqs, pred_seqs):
        gold = bio_to_entities(true_seq)
        pred = bio_to_entities(pred_seq)
        tp += len(gold & pred)
        fp += len(pred - gold)
        fn += len(gold - pred)

    def f1(t, fp_, fn_):
        p = t / (t + fp_) if (t + fp_) else 0.0
        r = t / (t + fn_) if (t + fn_) else 0.0
        return (2 * p * r / (p + r) if (p + r) else 0.0), p, r

    micro_f1, micro_p, micro_r = f1(tp, fp, fn)
    return micro_f1, micro_p, micro_r


@torch.inference_mode()
def quick_eval_bio(
    model, tokenizer, data, device, gaz_trie=None, num_gaz_labels=19,
    batch_size=64, max_length=256,
):
    model.eval()
    true_seqs, pred_seqs = [], []
    for bs in range(0, len(data), batch_size):
        batch = data[bs: bs + batch_size]
        sentences = [d["sentence"] for d in batch]
        char_labels_list = [d["labelling_seq"] for d in batch]
        enc = tokenizer(
            sentences, truncation=True, max_length=max_length, padding=True,
            return_offsets_mapping=True, return_tensors="pt",
        )
        offset_mapping = enc.pop("offset_mapping").tolist()
        word_ids_list = [enc.word_ids(i) for i in range(len(sentences))]
        ids = enc["input_ids"].to(device)
        mask = enc["attention_mask"].to(device)
        B, T = ids.shape

        label_mask = torch.zeros((B, T), dtype=torch.bool, device=device)
        gold_ids_per_ex = [[] for _ in range(B)]
        for bi in range(B):
            seen = set()
            char_labels = char_labels_list[bi]
            for ti, (wid, (cs, ce)) in enumerate(zip(word_ids_list[bi], offset_mapping[bi])):
                if wid is None or ce == 0 or wid in seen:
                    continue
                seen.add(wid)
                label_mask[bi, ti] = True
                raw = char_labels[cs] if cs < len(char_labels) else "O"
                gold_ids_per_ex[bi].append(LABEL2ID.get(raw, LABEL2ID["O"]))

        gaz_features = None
        if gaz_trie is not None:
            gaz_batch = np.zeros((B, T, num_gaz_labels), dtype=np.float32)
            for bi, sent in enumerate(sentences):
                char_feat = gaz_trie.match_sentence(sent)
                tok_feat = aggregate_to_tokens(char_feat, offset_mapping[bi])
                gaz_batch[bi, : tok_feat.shape[0]] = tok_feat
            gaz_features = torch.tensor(gaz_batch, device=device)

        decoded = model.predict_tags(ids, mask, label_mask, gaz_features=gaz_features)
        for bi in range(B):
            gold_ids = gold_ids_per_ex[bi]
            pred_ids = decoded[bi][: len(gold_ids)]
            true_seqs.append([ID2LABEL[g] for g in gold_ids])
            pred_seqs.append([ID2LABEL[p] for p in pred_ids] + ["O"] * max(0, len(gold_ids) - len(pred_ids)))

    return compute_entity_f1(true_seqs, pred_seqs)


class ManualEvalCallback(TrainerCallback):
    def __init__(self, trainer, tokenizer, valid_data, save_dir, eval_steps, patience,
                 device, gaz_trie=None, num_gaz_labels=19):
        self.trainer = trainer
        self.tokenizer = tokenizer
        self.valid_data = valid_data
        self.save_dir = save_dir
        self.eval_steps = eval_steps
        self.patience = patience
        self.device = device
        self.gaz_trie = gaz_trie
        self.num_gaz_labels = num_gaz_labels
        self.best_f1 = -1.0
        self.prev_f1 = -1.0
        self.no_improve = 0

    def on_step_end(self, args, state, control, **kwargs):
        if state.global_step == 0 or state.global_step % self.eval_steps != 0:
            return
        if not state.is_world_process_zero:
            return
        f1, p, r = quick_eval_bio(
            self.trainer.model, self.tokenizer, self.valid_data, self.device,
            gaz_trie=self.gaz_trie, num_gaz_labels=self.num_gaz_labels,
            batch_size=args.per_device_eval_batch_size,
        )
        print(f"\n  [Eval-근사 step={state.global_step}] Micro F1={f1:.4f}  P={p:.4f}  R={r:.4f}")
        if f1 > self.best_f1:
            self.best_f1 = f1
            self.trainer.save_model(self.save_dir)
            print(f"  ↳ Best F1={f1:.4f} → 저장 {self.save_dir}")
        if f1 > self.prev_f1:
            self.no_improve = 0
        else:
            self.no_improve += 1
            print(f"  F1 연속 미개선 ({self.no_improve}/{self.patience}): "
                  f"현재={f1:.4f}  직전={self.prev_f1:.4f}  best={self.best_f1:.4f}")
            if self.no_improve >= self.patience:
                print(f"  Early stopping: {self.patience}번 연속 F1 미개선")
                control.should_training_stop = True
        self.prev_f1 = f1


def evaluate(args):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model_dir = Path(args.model_dir)
    label_map = load_label_map(model_dir)
    target_labels = label_map.get("target_labels", TARGET_LABELS)
    tokenizer_src = label_map.get("model_id") or str(model_dir)
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_src, trust_remote_code=True, use_fast=True)
    if not tokenizer.is_fast:
        sys.exit(f"[ERROR] '{model_dir}' fast tokenizer 필요.")

    model = TokenClassifierForPII.from_pretrained(str(model_dir), trust_remote_code=True)
    model = model.to(torch.float32).to(device)
    model.eval()

    gaz_trie = load_gazetteer_trie(model_dir, target_labels) if label_map.get("use_gazetteer") else None
    id2label = {int(k): v for k, v in label_map.get("id2label", {}).items()} or model.config.id2label

    data_dir = eb.resolve_data_dir(getattr(args, "data_dir", None))
    data = json.load(open(data_dir / f"{args.split}.json", encoding="utf-8"))
    sentences = [d["sentence"] for d in data]
    gold_pii_list = [d["PII_set"] for d in data]

    print(f"[CRF+GAZ] 모델: {model_dir}")
    print(f"평가: {args.split}.json  →  {device}")
    pred_list = predict_batch_bio(
        model, tokenizer, sentences, device, id2label, gaz_trie=gaz_trie,
        num_gaz_labels=len(target_labels), batch_size=args.batch_size, max_length=args.max_length,
    )

    micro_tp = micro_fp = micro_fn = 0
    per_label = defaultdict(lambda: [0, 0, 0])
    per_label_fp = defaultdict(list)
    per_label_fn = defaultdict(list)
    confusion = defaultdict(int)

    for item, gold_piis, pred_ents in zip(data, gold_pii_list, pred_list):
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
    print(f"[{args.split}]  Micro F1={micro_f1:.4f}  P={micro_p:.4f}  R={micro_r:.4f}")
    print(f"  TP={micro_tp}  FP={micro_fp}  FN={micro_fn}")
    print(f"{'='*68}")
    label_rows = []
    for lbl in TARGET_LABELS:
        tp, fp, fn = per_label[lbl]
        f1, p, r = eb.safe_f1(tp, fp, fn)
        label_rows.append((lbl, f1, p, r, tp, fp, fn))
        print(f"  {lbl:28s} F1={f1:.4f} P={p:.4f} R={r:.4f}  TP={tp:5d} FP={fp:5d} FN={fn:5d}")

    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    tag = f"{args.tag}_" if args.tag else ""
    md_path = _results_dir_for(model_dir) / f"eval_{args.split}_{tag}{ts}.md"
    L = [
        f"# CRF+Gazetteer 평가: {args.split}  ({ts})",
        f"",
        f"모델: `{model_dir}`",
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
    parser.add_argument("--model_dir", required=True)
    parser.add_argument("--tag", default="")
    parser.add_argument("--batch_size", type=int, default=64)
    parser.add_argument("--max_length", type=int, default=256)
    args = parser.parse_args()
    evaluate(args)
