"""
Threshold 스윕 — reg 앙상블(soft voting)의 어절 확률에 라벨별 τ 적용

argmax 대신 "최고 non-O 확률 >= τ 이면 그 라벨, 아니면 O" 규칙.
  - 전역 τ 그리드 스윕 (valid F1 최대)
  - 라벨별 τ greedy 최적화 (valid F1 최대)
그 다음 valid 최적 τ 를 test 에 적용해 성능 보고.

주의: τ 는 valid 분포에 맞춘 추론 규칙 → 도메인 이식성 약함(단일 test 한정 보조 기법).

실행:
    python3 threshold_sweep.py --model_dirs models/skt_encoder_distill_aug_reg/seed{42,43,44}
"""

import argparse
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForTokenClassification, AutoTokenizer

import eval_baseline as eb

ID2LABEL = eb.ID2LABEL
LABEL2ID = {v: k for k, v in ID2LABEL.items()}
TARGET_LABELS = eb.TARGET_LABELS
DATA_DIR = eb.DATA_DIR
_O_IDX = LABEL2ID["O"]


def collect_word_probs(models, tokenizer, sentences, batch_size=64, max_length=256, device="cuda"):
    """각 문장 → [(start, end, prob_vec[39]), ...] (어절 첫 서브워드 평균확률)."""
    out = []
    for bs in range(0, len(sentences), batch_size):
        batch = sentences[bs: bs + batch_size]
        enc = tokenizer(batch, truncation=True, max_length=max_length,
                        padding=True, return_offsets_mapping=True, return_tensors="pt")
        offs = enc.pop("offset_mapping").tolist()
        wids = [enc.word_ids(i) for i in range(len(batch))]
        ids = enc["input_ids"].to(device)
        mask = enc["attention_mask"].to(device)

        psum = None
        for m in models:
            with torch.inference_mode():
                logit = m(input_ids=ids, attention_mask=mask).logits
            p = torch.softmax(logit.float(), dim=-1)
            psum = p if psum is None else psum + p
        pavg = (psum / len(models)).cpu().numpy()

        for si in range(len(batch)):
            wspan, wprob = {}, {}
            for tpos, (wid, (cs, ce)) in enumerate(zip(wids[si], offs[si])):
                if wid is None or ce == 0:
                    continue
                if wid not in wspan:
                    wspan[wid] = [cs, ce]
                    wprob[wid] = pavg[si, tpos]
                else:
                    wspan[wid][0] = min(wspan[wid][0], cs)
                    wspan[wid][1] = max(wspan[wid][1], ce)
            words = [(wspan[w][0], wspan[w][1], wprob[w]) for w in wspan]
            out.append(words)
    return out


def decode(sent, words, tau):
    """tau: dict label->threshold. non-O 최고확률>=tau 이면 채택."""
    char_labels = ["O"] * len(sent)
    for (ws, we, prob) in words:
        p = prob.copy()
        p_o = p[_O_IDX]
        p[_O_IDX] = -1
        pid = int(p.argmax())
        tag = ID2LABEL.get(pid, "O")
        if tag == "O":
            continue
        base = tag[2:] if tag.startswith(("B-", "I-")) else tag
        thr = tau.get(base, 0.5)
        if p[pid] < thr:
            continue
        cont = "I-" + base if tag.startswith("B-") else tag
        for k, c in enumerate(range(ws, min(we, len(sent)))):
            char_labels[c] = tag if k == 0 else cont
    ents = eb.char_bio_to_entities(sent, char_labels)
    ents = eb.merge_lc_address(ents, sent)
    ents = eb.regex_postprocess(sent, ents)
    return ents


def score(data, word_data, tau):
    tp = fp = fn = 0
    per_label = defaultdict(lambda: [0, 0, 0])
    for item, words in zip(data, word_data):
        sent = item["sentence"]
        gold = item["PII_set"]
        pred = decode(sent, words, tau)
        mg, mp = set(), set()
        for pi, pe in enumerate(pred):
            for gi, ge in enumerate(gold):
                if pe["label"] != ge["label"]:
                    continue
                if pe["begin"] < ge["end"] and ge["begin"] < pe["end"]:
                    mg.add(gi); mp.add(pi)
        tp += len(mg); fp += len(pred) - len(mp); fn += len(gold) - len(mg)
        for gi in mg:
            per_label[gold[gi]["label"]][0] += 1
        for pi in range(len(pred)):
            if pi not in mp:
                per_label[pred[pi]["label"]][1] += 1
        for gi in range(len(gold)):
            if gi not in mg:
                per_label[gold[gi]["label"]][2] += 1
    f1, p, r = eb.safe_f1(tp, fp, fn)
    return f1, p, r, per_label


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model_dirs", nargs="+", required=True)
    ap.add_argument("--tag", default="reg")
    ap.add_argument("--batch_size", type=int, default=64)
    args = ap.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    tok = AutoTokenizer.from_pretrained(args.model_dirs[0], trust_remote_code=True, use_fast=True)
    models = [AutoModelForTokenClassification.from_pretrained(d, trust_remote_code=True).to(device).eval()
              for d in args.model_dirs]

    valid = json.load(open(DATA_DIR / "valid.json", encoding="utf-8"))
    test = json.load(open(DATA_DIR / "test.json", encoding="utf-8"))
    vs = [d["sentence"] for d in valid]
    ts = [d["sentence"] for d in test]

    print(f"확률 수집: valid {len(vs)}, test {len(ts)} ...")
    vw = collect_word_probs(models, tok, vs, args.batch_size, device=device)
    tw = collect_word_probs(models, tok, ts, args.batch_size, device=device)

    # 기준선: argmax (τ=0.5 상당이 아니라 순수 argmax) → tau 모두 0.0 이면 non-O 항상? 아님.
    # argmax 기준선 = "non-O가 O보다 크면 채택" = tau -inf 상당. 여기선 tau=0.0 로 근사.
    base_tau = {l: 0.0 for l in TARGET_LABELS}
    vf, vp, vr, _ = score(valid, vw, base_tau)
    tf, tp_, tr, _ = score(test, tw, base_tau)
    print(f"\n[argmax 기준] valid F1={vf:.4f}  test F1={tf:.4f} (P={tp_:.4f} R={tr:.4f})")

    # 1) 전역 τ 스윕
    grid = [round(x, 2) for x in np.arange(0.0, 0.95, 0.05)]
    best_g, best_gtau = -1, 0.0
    for t in grid:
        f1, *_ = score(valid, vw, {l: t for l in TARGET_LABELS})
        if f1 > best_g:
            best_g, best_gtau = f1, t
    gf, gp, gr, _ = score(test, tw, {l: best_gtau for l in TARGET_LABELS})
    print(f"[전역 τ={best_gtau}] valid F1={best_g:.4f}  test F1={gf:.4f} (P={gp:.4f} R={gr:.4f})")

    # 2) 라벨별 τ greedy (전역 최적에서 출발)
    tau = {l: best_gtau for l in TARGET_LABELS}
    cur, *_ = score(valid, vw, tau)
    for lbl in TARGET_LABELS:
        best_t, best_f = tau[lbl], cur
        for t in grid:
            trial = dict(tau); trial[lbl] = t
            f1, *_ = score(valid, vw, trial)
            if f1 > best_f:
                best_f, best_t = f1, t
        tau[lbl] = best_t
        cur = best_f
    lf, lp, lr, lpl = score(test, tw, tau)
    print(f"[라벨별 τ] valid F1={cur:.4f}  test F1={lf:.4f} (P={lp:.4f} R={lr:.4f})")

    print("\n라벨별 최적 τ (0.5에서 벗어난 것만):")
    for l in TARGET_LABELS:
        if abs(tau[l] - best_gtau) > 1e-9:
            print(f"  {l:20s} τ={tau[l]}")

    print("\n=== 요약 (test) ===")
    print(f"  argmax     F1={tf:.4f}")
    print(f"  전역 τ     F1={gf:.4f}")
    print(f"  라벨별 τ   F1={lf:.4f}")

    out = Path("results/threshold_sweep_" + args.tag + ".md")
    out.parent.mkdir(parents=True, exist_ok=True)
    L = [f"# Threshold 스윕: {args.tag}", "",
         "| 방식 | valid F1 | test F1 | test P | test R |",
         "|------|----------|---------|--------|--------|",
         f"| argmax | {vf:.4f} | {tf:.4f} | {tp_:.4f} | {tr:.4f} |",
         f"| 전역 τ={best_gtau} | {best_g:.4f} | {gf:.4f} | {gp:.4f} | {gr:.4f} |",
         f"| 라벨별 τ | {cur:.4f} | {lf:.4f} | {lp:.4f} | {lr:.4f} |",
         "", "## 라벨별 최적 τ", "", "| 라벨 | τ |", "|------|---|"]
    for l in TARGET_LABELS:
        L.append(f"| {l} | {tau[l]} |")
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"\nMD 저장: {out}")


if __name__ == "__main__":
    main()
