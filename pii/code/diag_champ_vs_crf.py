"""
챔피언(distill_aug) vs CRF 앙상블 — 엔티티 단위 차이 진단

목적: CRF 가 얻은 recall(회수 TP)과 치른 대가(신규 FP)를 분해하여,
      "CRF-recall + FP필터" 로 0.9510 을 넘길 수 있는지 판정.

버킷:
  A. CRF가 회수한 TP  : gold ∩ CRF, but 챔피언은 놓침     → recall 이득
  B. CRF가 새로 낸 FP : CRF 오탐, 챔피언엔 없던 것          → precision 손해
  C. 공통 FN          : gold 인데 둘 다 놓침                → 진짜 천장
  D. 챔피언이 잃은 TP : gold ∩ 챔피언, but CRF는 놓침        → CRF 회귀
"""

import argparse
import json
from collections import defaultdict
from pathlib import Path

import torch
from transformers import AutoModelForTokenClassification, AutoTokenizer

import eval_baseline as eb
from eval_baseline_ensemble import predict_ensemble_baseline
from eval_baseline_ensemble_crf import predict_ensemble_crf
from crf_model import TokenClassifierCRF

DATA_DIR = eb.DATA_DIR


def match(pred_ents, gold_piis):
    """overlap+label 매칭 → (matched_gold_idx set, matched_pred_idx set)."""
    mg, mp = set(), set()
    for pi, pe in enumerate(pred_ents):
        for gi, ge in enumerate(gold_piis):
            if pe["label"] != ge["label"]:
                continue
            if pe["begin"] < ge["end"] and ge["begin"] < pe["end"]:
                mg.add(gi)
                mp.add(pi)
    return mg, mp


def ent_key(e):
    return (e["begin"], e["end"], e["label"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default="test")
    ap.add_argument("--champ_dirs", nargs="+", required=True)
    ap.add_argument("--crf_dirs", nargs="+", required=True)
    ap.add_argument("--out", default="results/diag_champ_vs_crf.md")
    args = ap.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"

    tok = AutoTokenizer.from_pretrained(args.champ_dirs[0], trust_remote_code=True, use_fast=True)

    champ = [AutoModelForTokenClassification.from_pretrained(d, trust_remote_code=True).to(device).eval()
             for d in args.champ_dirs]
    crf = [TokenClassifierCRF.load_pretrained(d).to(device) for d in args.crf_dirs]

    data = json.load(open(DATA_DIR / f"{args.split}.json", encoding="utf-8"))
    sentences = [d["sentence"] for d in data]
    gold_list = [d["PII_set"] for d in data]

    print("챔피언 예측...")
    champ_pred = predict_ensemble_baseline(champ, tok, sentences, device=device)
    print("CRF 예측...")
    crf_pred = predict_ensemble_crf(crf, tok, sentences, device=device)

    # 버킷별 집계
    A = defaultdict(list)  # CRF 회수 TP
    B = defaultdict(list)  # CRF 신규 FP
    C = defaultdict(list)  # 공통 FN
    D = defaultdict(list)  # 챔피언이 잃은 TP

    champ_fp_total = defaultdict(int)
    crf_fp_total = defaultdict(int)

    for item, gold, cp, rp in zip(data, gold_list, champ_pred, crf_pred):
        sent = item["sentence"]
        sidx = item["sent_idx"]

        cg, cpp = match(cp, gold)   # champ matched gold/pred
        rg, rpp = match(rp, gold)   # crf matched gold/pred

        for gi, ge in enumerate(gold):
            in_champ = gi in cg
            in_crf = gi in rg
            rec = {"sent_idx": sidx, "sentence": sent, "form": ge["form"],
                   "begin": ge["begin"], "end": ge["end"]}
            if in_crf and not in_champ:
                A[ge["label"]].append(rec)
            elif in_champ and not in_crf:
                D[ge["label"]].append(rec)
            elif not in_champ and not in_crf:
                C[ge["label"]].append(rec)

        # FP: 매칭 안 된 예측
        champ_fp = {ent_key(cp[pi]): cp[pi] for pi in range(len(cp)) if pi not in cpp}
        crf_fp = {ent_key(rp[pi]): rp[pi] for pi in range(len(rp)) if pi not in rpp}
        for k, e in champ_fp.items():
            champ_fp_total[e["label"]] += 1
        for k, e in crf_fp.items():
            crf_fp_total[e["label"]] += 1
            if k not in champ_fp:  # CRF 신규 FP
                B[e["label"]].append({"sent_idx": sidx, "sentence": sent,
                                      "form": e["form"], "begin": e["begin"], "end": e["end"]})

    def total(d):
        return sum(len(v) for v in d.values())

    print("\n" + "=" * 60)
    print(f"A. CRF 회수 TP (recall 이득)   : {total(A)}")
    print(f"B. CRF 신규 FP (precision 대가): {total(B)}")
    print(f"C. 공통 FN (진짜 천장)         : {total(C)}")
    print(f"D. 챔피언이 잃은 TP (CRF 회귀) : {total(D)}")
    print("=" * 60)
    print(f"순 recall 이득 = A - D = {total(A) - total(D)}")
    print(f"순 FP 변화     = B(신규) vs 총 FP: champ={sum(champ_fp_total.values())} crf={sum(crf_fp_total.values())}")

    def by_label(name, d):
        print(f"\n[{name}] 라벨별:")
        for lbl, items in sorted(d.items(), key=lambda x: -len(x[1])):
            print(f"  {lbl:20s} {len(items)}")

    by_label("A. CRF 회수 TP", A)
    by_label("B. CRF 신규 FP", B)
    by_label("D. 챔피언이 잃은 TP", D)

    # MD 리포트 (예시 포함)
    L = ["# 챔피언 vs CRF 엔티티 진단", ""]
    L += [f"- A. CRF 회수 TP: **{total(A)}**",
          f"- B. CRF 신규 FP: **{total(B)}**",
          f"- C. 공통 FN(천장): **{total(C)}**",
          f"- D. 챔피언이 잃은 TP: **{total(D)}**",
          f"- 순 recall 이득 (A-D): **{total(A)-total(D)}**", ""]

    def dump(name, d, gold_side):
        L.append(f"## {name}")
        for lbl, items in sorted(d.items(), key=lambda x: -len(x[1])):
            L.append(f"### {lbl} ({len(items)})")
            L.append("| sent_idx | form | 문장 |")
            L.append("|---|---|---|")
            for ex in items[:40]:
                ctx = eb.highlight(ex["sentence"], ex["begin"], ex["end"])
                L.append(f"| {ex['sent_idx']} | `{ex['form']}` | {ctx} |")
            L.append("")

    dump("A. CRF 회수 TP (recall 이득)", A, True)
    dump("B. CRF 신규 FP (precision 대가 — 걸러야 할 대상)", B, False)
    dump("C. 공통 FN (둘 다 놓침 — 진짜 천장)", C, True)
    dump("D. 챔피언이 잃은 TP (CRF 회귀)", D, True)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"\nMD 저장: {out}")


if __name__ == "__main__":
    main()
