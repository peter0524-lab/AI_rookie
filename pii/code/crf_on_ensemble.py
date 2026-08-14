"""
최고 앙상블(distill_aug 3-seed) 위에 CRF 얹기 — 어절 단위 선형체인 CRF

아이디어:
  - 기존 3개 모델의 '어절 첫 서브워드' softmax 확률을 평균 → 어절별 emission 확률.
    (unary 결정은 챔피언 soft-voting 과 동일 → 전이 0이면 0.9510 재현)
  - 그 emission(log-prob) 을 고정하고, 그 위에 **CRF 전이 파라미터만 학습**.
    → 모델 재학습 불필요, 전이(B/I 전이 규칙 등 라벨 시퀀스 구조)만 추가.
  - 학습/검증/평가 모두 eval_baseline 과 동일한 char-span 매칭/후처리로 채점(공정 비교).

비교:
  - CRF OFF (argmax)  ← 챔피언 앙상블과 동일해야 함(sanity)
  - CRF ON  (Viterbi) ← CRF 효과

실행:
    python3 crf_on_ensemble.py \
        --model_dirs models/skt_encoder_distill_aug/seed42 \
                     models/skt_encoder_distill_aug/seed43 \
                     models/skt_encoder_distill_aug/seed44 \
        --epochs 60 --lr 0.01
"""

import argparse
from collections import defaultdict

import numpy as np
import torch
import torch.nn as nn
from torchcrf import CRF
from transformers import AutoModelForTokenClassification, AutoTokenizer

import eval_baseline as eb

ID2LABEL      = eb.ID2LABEL
LABEL2ID      = eb.LABEL2ID
TARGET_LABELS = eb.TARGET_LABELS
DATA_DIR      = eb.DATA_DIR
NUM_LABELS    = len(ID2LABEL)
_O            = LABEL2ID["O"]


# ── 앙상블 어절 emission(평균 softmax) + 어절 span 추출 ────────────────────────
@torch.inference_mode()
def ensemble_word_probs(models, tokenizer, sentences, batch_size, max_length, device):
    out = []  # per sentence: (probs[Lw, C] float32, spans list[(ws,we)])
    for bs in range(0, len(sentences), batch_size):
        batch = sentences[bs: bs + batch_size]
        enc = tokenizer(batch, truncation=True, max_length=max_length,
                        padding=True, return_offsets_mapping=True, return_tensors="pt")
        offs = enc.pop("offset_mapping").tolist()
        wids = [enc.word_ids(i) for i in range(len(batch))]
        ids  = enc["input_ids"].to(device)
        mask = enc["attention_mask"].to(device)

        prob_sum = None
        for m in models:
            logits = m(input_ids=ids, attention_mask=mask).logits
            p = torch.softmax(logits.float(), dim=-1)
            prob_sum = p if prob_sum is None else prob_sum + p
        prob_avg = (prob_sum / len(models)).cpu().numpy()

        for si in range(len(batch)):
            span, prob = {}, {}
            for tpos, (wid, (cs, ce)) in enumerate(zip(wids[si], offs[si])):
                if wid is None or ce == 0:
                    continue
                if wid not in span:
                    span[wid] = [cs, ce]; prob[wid] = prob_avg[si, tpos]
                else:
                    span[wid][0] = min(span[wid][0], cs)
                    span[wid][1] = max(span[wid][1], ce)
            order = sorted(span)
            probs = np.stack([prob[w] for w in order]) if order else np.zeros((0, NUM_LABELS), np.float32)
            spans = [tuple(span[w]) for w in order]
            out.append((probs.astype(np.float32), spans))
    return out


def gold_word_tags(item, spans):
    cl = item["labelling_seq"]
    return [LABEL2ID.get(cl[ws] if ws < len(cl) else "O", _O) for (ws, _we) in spans]


def word_tags_to_char_labels(sent, spans, tags):
    cl = ["O"] * len(sent)
    for (ws, we), tid in zip(spans, tags):
        tag = ID2LABEL[int(tid)]
        if tag == "O":
            continue
        cont = "I-" + tag[2:] if tag.startswith("B-") else tag
        for k, c in enumerate(range(ws, min(we, len(sent)))):
            cl[c] = tag if k == 0 else cont
    return cl


def build_entities(sent, spans, tags):
    cl = word_tags_to_char_labels(sent, spans, tags)
    ents = eb.char_bio_to_entities(sent, cl)
    ents = eb.merge_lc_address(ents, sent)
    ents = eb.regex_postprocess(sent, ents)
    return ents


# ── 채점 (eval_baseline 방식 span-overlap 매칭) ───────────────────────────────
def score(data, emis_spans, tags_list, per_label=False):
    tp = fp = fn = 0
    pl = defaultdict(lambda: [0, 0, 0])
    for item, (_probs, spans), tags in zip(data, emis_spans, tags_list):
        sent = item["sentence"]
        gold = item["PII_set"]
        pred = build_entities(sent, spans, tags)
        mg, mp = set(), set()
        for pi, pe in enumerate(pred):
            for gi, ge in enumerate(gold):
                if pe["label"] != ge["label"]:
                    continue
                if pe["begin"] < ge["end"] and ge["begin"] < pe["end"]:
                    mg.add(gi); mp.add(pi)
        tp += len(mg); fp += len(pred) - len(mp); fn += len(gold) - len(mg)
        if per_label:
            for gi in mg:
                pl[gold[gi]["label"]][0] += 1
            for pi, pe in enumerate(pred):
                if pi not in mp:
                    pl[pe["label"]][1] += 1
            for gi, ge in enumerate(gold):
                if gi not in mg:
                    pl[ge["label"]][2] += 1
    f, p, r = eb.safe_f1(tp, fp, fn)
    return (f, p, r, tp, fp, fn), pl


def argmax_tags(emis_spans):
    return [list(probs.argmax(-1)) if len(probs) else [] for probs, _s in emis_spans]


# ── CRF 학습 (emission 고정, 전이만) ──────────────────────────────────────────
def make_emissions(emis_spans, device):
    """list of (probs, spans) → list of emission 텐서 [Lw, C] (log-prob)."""
    ems = []
    for probs, _spans in emis_spans:
        if len(probs) == 0:
            ems.append(torch.zeros((1, NUM_LABELS)))  # 빈 문장 방지용 더미
        else:
            ems.append(torch.log(torch.from_numpy(probs).clamp_min(1e-9)))
    return ems


def pad_batch(ems, tags, idxs, device):
    L = max(len(ems[i]) for i in idxs)
    B = len(idxs)
    E = torch.zeros(B, L, NUM_LABELS)
    T = torch.zeros(B, L, dtype=torch.long)
    M = torch.zeros(B, L, dtype=torch.bool)
    for b, i in enumerate(idxs):
        li = len(ems[i])
        E[b, :li] = ems[i]
        if tags is not None:
            T[b, :li] = torch.tensor(tags[i][:li], dtype=torch.long)
        M[b, :li] = True
    return E.to(device), T.to(device), M.to(device)


@torch.inference_mode()
def crf_decode(crf, ems, emis_spans, device, batch_size=128):
    n = len(ems)
    out = [None] * n
    order = sorted(range(n), key=lambda i: len(ems[i]))
    for bs in range(0, n, batch_size):
        idxs = order[bs: bs + batch_size]
        E, _T, M = pad_batch(ems, None, idxs, device)
        paths = crf.decode(E, mask=M)
        for i, path in zip(idxs, paths):
            real = len(emis_spans[i][1])   # 실제 어절 수(더미 제외)
            out[i] = path[:real]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model_dirs", nargs="+", required=True)
    ap.add_argument("--epochs", type=int, default=60)
    ap.add_argument("--lr", type=float, default=0.01)
    ap.add_argument("--batch_size", type=int, default=128)
    ap.add_argument("--max_length", type=int, default=256)
    args = ap.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    import json
    tok = AutoTokenizer.from_pretrained(args.model_dirs[0], trust_remote_code=True, use_fast=True)
    models = []
    for d in args.model_dirs:
        m = AutoModelForTokenClassification.from_pretrained(d, trust_remote_code=True).to(device)
        m.eval(); models.append(m)

    def load(split):
        return json.load(open(DATA_DIR / f"{split}.json", encoding="utf-8"))

    train, valid, test = load("train"), load("valid"), load("test")
    print(f"[emission 추출] train {len(train)} / valid {len(valid)} / test {len(test)}")

    tr_es = ensemble_word_probs(models, tok, [d["sentence"] for d in train], args.batch_size, args.max_length, device)
    va_es = ensemble_word_probs(models, tok, [d["sentence"] for d in valid], args.batch_size, args.max_length, device)
    te_es = ensemble_word_probs(models, tok, [d["sentence"] for d in test],  args.batch_size, args.max_length, device)

    tr_tags = [gold_word_tags(it, sp) for it, (_p, sp) in zip(train, tr_es)]
    tr_ems  = make_emissions(tr_es, device)
    va_ems  = make_emissions(va_es, device)
    te_ems  = make_emissions(te_es, device)

    # ── CRF OFF (argmax) sanity ──
    (f, p, r, tp, fp, fn), _ = score(test, te_es, argmax_tags(te_es))
    print(f"\n[CRF OFF / argmax]  test  F1={f:.4f} P={p:.4f} R={r:.4f}  (TP{tp} FP{fp} FN{fn})")

    # ── CRF 학습 ──
    crf = CRF(NUM_LABELS, batch_first=True).to(device)
    opt = torch.optim.Adam(crf.parameters(), lr=args.lr)
    idx_all = list(range(len(tr_ems)))

    best_f1, best_state = -1.0, None
    for ep in range(args.epochs):
        crf.train()
        np.random.shuffle(idx_all)
        tot = 0.0
        for bs in range(0, len(idx_all), args.batch_size):
            idxs = idx_all[bs: bs + args.batch_size]
            E, T, M = pad_batch(tr_ems, tr_tags, idxs, device)
            loss = -crf(E, T, mask=M, reduction="mean")
            opt.zero_grad(); loss.backward(); opt.step()
            tot += loss.item()
        crf.eval()
        va_pred = crf_decode(crf, va_ems, va_es, device, args.batch_size)
        (vf, vp, vr, *_), _ = score(valid, va_es, va_pred)
        flag = ""
        if vf > best_f1:
            best_f1 = vf
            best_state = {k: v.detach().clone() for k, v in crf.state_dict().items()}
            flag = "  ← best"
        print(f"  ep{ep:02d}  loss={tot:.1f}  valid F1={vf:.4f}{flag}")

    crf.load_state_dict(best_state)
    crf.eval()

    # ── CRF ON test ──
    te_pred = crf_decode(crf, te_ems, te_es, device, args.batch_size)
    (f, p, r, tp, fp, fn), pl = score(test, te_es, te_pred, per_label=True)
    print(f"\n[CRF ON / Viterbi]  test  F1={f:.4f} P={p:.4f} R={r:.4f}  (TP{tp} FP{fp} FN{fn})")
    print("  레이블별:")
    rows = []
    for lbl in TARGET_LABELS:
        t, fpp, fnn = pl[lbl]
        lf, lp, lr_ = eb.safe_f1(t, fpp, fnn)
        rows.append((lbl, lf, lp, lr_, t, fpp, fnn))
    for lbl, lf, lp, lr_, t, fpp, fnn in sorted(rows, key=lambda x: x[1]):
        print(f"    {lbl:20s} F1={lf:.4f} P={lp:.4f} R={lr_:.4f}  TP={t} FP={fpp} FN={fnn}")


if __name__ == "__main__":
    main()
