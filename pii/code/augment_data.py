"""
엔티티 치환 데이터 증강 (entity substitution augmentation)

목적:
  0.1B encoder 가 '처음 보는 고유명사(OOV)'를 문맥으로 잡지 못하는 문제를 완화.
  실패 분석 결과 OG_WORKPLACE 등은 라벨 혼동이 아니라 **span 미탐(FN)** 이 대부분이며,
  "다니는 ___", "운영하는 가게 ___", "___입니다" 처럼 **문맥 단서는 충분**했다.
  → 문맥 틀은 그대로 두고 **엔티티 이름만 수백 종으로 갈아끼워** 학습시키면,
    모델이 '이름이 무엇이든 이 문맥이면 해당 엔티티'라는 규칙을 일반화한다.

방식:
  1) train 에서 라벨별 표면형 풀(pool) 수집.
  2) 타겟 라벨(AUG_LABELS) 엔티티를 가진 문장마다 N개의 증강 복제본 생성.
     - 각 복제본은 그 문장의 모든 타겟 엔티티를 같은 라벨의 다른 풀 이름으로 치환.
     - 비타겟 엔티티는 표면형 유지(offset 만 재계산).
  3) 조사(은/는, 이/가, 을/를, 과/와, 아/야) 받침 일치 보정(동일 길이 1글자 치환).
  4) sentence / PII_set(begin·end) / sent_seq / labelling_seq 전부 재생성 후 정합성 검증.

원본은 그대로 포함(KEEP_ORIGINAL=1). valid/test 는 증강하지 않는다.

실행:
    python3 augment_data.py \
        --input data/train.json --output data/train_aug.json \
        --labels OG_WORKPLACE,CV_POSITION,LC_ADDRESS,PS_NAME \
        --per-sent 3 --ogw-boost 2 --seed 42
"""

import argparse
import json
import os
import random
from collections import defaultdict


# ── 조사 받침 보정 ─────────────────────────────────────────────────────────────
JOSA_GROUPS = [("은", "는"), ("이", "가"), ("을", "를"), ("과", "와"), ("아", "야")]


def _has_batchim(word: str) -> bool:
    """단어 마지막 글자에 받침이 있으면 True (한글 음절만 판정)."""
    if not word:
        return False
    ch = word[-1]
    if "가" <= ch <= "힣":
        return (ord(ch) - 0xAC00) % 28 != 0
    # 숫자/영문/기호로 끝나면 받침 유무 모호 → 받침 없음(모음 종결)으로 취급
    return False


def _fix_josa(josa_ch: str, prev_word: str) -> str:
    """엔티티 직후 1글자가 교체형 조사면 받침에 맞춰 교정."""
    bat = _has_batchim(prev_word)
    for b_form, v_form in JOSA_GROUPS:
        if josa_ch in (b_form, v_form):
            return b_form if bat else v_form
    return josa_ch


# ── 풀 수집 ───────────────────────────────────────────────────────────────────
def build_pools(data, labels):
    pools = defaultdict(set)
    for ex in data:
        for p in ex["PII_set"]:
            if p["label"] in labels:
                pools[p["label"]].add(p["form"])
    return {k: sorted(v) for k, v in pools.items()}


# ── 문장 재구성 (모든 엔티티 offset 재계산 + 타겟 치환) ─────────────────────────
def rebuild(sentence, pii_set, repl_form):
    """
    repl_form: {entity_id: new_form}  (치환 대상만)
    반환: new_sentence, new_pii(begin·end·form 갱신)
    """
    spans = sorted(pii_set, key=lambda x: x["begin"])
    out, new_pii, cursor = [], [], 0
    cur_len = 0
    for ent in spans:
        b, e = ent["begin"], ent["end"]
        pre = sentence[cursor:b]
        out.append(pre)
        cur_len += len(pre)
        new_form = repl_form.get(ent["id"], sentence[b:e])
        out.append(new_form)
        nb = cur_len
        ne = cur_len + len(new_form)
        ent2 = dict(ent)
        ent2["form"], ent2["begin"], ent2["end"] = new_form, nb, ne
        new_pii.append(ent2)
        cur_len = ne
        cursor = e
    out.append(sentence[cursor:])
    return "".join(out), new_pii


def apply_josa_fix(sentence, new_pii, changed_ids):
    """치환된 엔티티 직후 조사를 받침에 맞춰 보정(동일 길이)."""
    chars = list(sentence)
    for ent in new_pii:
        if ent["id"] not in changed_ids:
            continue
        pos = ent["end"]
        if pos < len(chars):
            fixed = _fix_josa(chars[pos], ent["form"])
            chars[pos] = fixed
    return "".join(chars)


def make_labelling(sentence, new_pii):
    seq = ["O"] * len(sentence)
    for ent in new_pii:
        b, e, lab = ent["begin"], ent["end"], ent["label"]
        if b >= len(seq):
            continue
        seq[b] = f"B-{lab}"
        for i in range(b + 1, min(e, len(seq))):
            seq[i] = f"I-{lab}"
    return seq


def validate(ex):
    s = ex["sentence"]
    if list(s) != ex["sent_seq"]:
        return False
    if len(ex["labelling_seq"]) != len(s):
        return False
    for p in ex["PII_set"]:
        if s[p["begin"]:p["end"]] != p["form"]:
            return False
    return True


def augment_sentence(ex, pools, labels, n_copies, rng):
    """ex 한 문장에서 n_copies 개의 증강 복제 생성."""
    tgt_ents = [p for p in ex["PII_set"] if p["label"] in labels]
    if not tgt_ents:
        return []
    results = []
    for c in range(n_copies):
        repl = {}
        changed = set()
        for ent in tgt_ents:
            pool = pools.get(ent["label"], [])
            if len(pool) < 2:
                continue
            cand = ent["form"]
            for _ in range(5):
                cand = rng.choice(pool)
                if cand != ent["form"]:
                    break
            if cand != ent["form"]:
                repl[ent["id"]] = cand
                changed.add(ent["id"])
        if not repl:
            continue
        new_sent, new_pii = rebuild(ex["sentence"], ex["PII_set"], repl)
        new_sent = apply_josa_fix(new_sent, new_pii, changed)
        # 조사 보정으로 글자가 바뀌었을 수 있으니 PII form 은 슬라이스로 재동기화
        for p in new_pii:
            p["form"] = new_sent[p["begin"]:p["end"]]
        new_ex = {
            "sent_idx": f"{ex['sent_idx']}_aug{c}",
            "sentence": new_sent,
            "PII_set": new_pii,
            "sent_seq": list(new_sent),
            "labelling_seq": make_labelling(new_sent, new_pii),
        }
        if validate(new_ex):
            results.append(new_ex)
    return results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="data/train.json")
    ap.add_argument("--output", default="data/train_aug.json")
    ap.add_argument("--labels", default="OG_WORKPLACE,CV_POSITION,LC_ADDRESS,PS_NAME")
    ap.add_argument("--extra-pool", default="",
                    help="외부 사전 JSON {라벨: [표면형...]} — 해당 라벨 치환 풀에 병합(OOV 완화)")
    ap.add_argument("--per-sent", type=int, default=3,
                    help="문장당 증강 복제 수")
    ap.add_argument("--ogw-boost", type=int, default=2,
                    help="OG_WORKPLACE 포함 문장 추가 복제 배수(최약 라벨 집중)")
    ap.add_argument("--keep-original", type=int, default=1)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    rng = random.Random(args.seed)
    labels = [l.strip() for l in args.labels.split(",") if l.strip()]

    data = json.load(open(args.input, encoding="utf-8"))
    pools = build_pools(data, labels)

    if args.extra_pool:
        extra = json.load(open(args.extra_pool, encoding="utf-8"))
        for lab, forms in extra.items():
            if lab in labels:
                before = len(pools.get(lab, []))
                pools[lab] = sorted(set(pools.get(lab, [])) | set(forms))
                print(f"  [extra] pool[{lab}]: {before} → {len(pools[lab])} 종 (+외부 {len(forms)})")

    print(f"입력: {args.input}  ({len(data)} 문장)")
    print(f"타겟 라벨: {labels}")
    for l in labels:
        print(f"  pool[{l}] = {len(pools.get(l, []))} 종")
    print(f"per_sent={args.per_sent}  ogw_boost={args.ogw_boost}  seed={args.seed}")

    out = list(data) if args.keep_original else []
    n_aug, n_elig, n_fail = 0, 0, 0
    per_label_added = defaultdict(int)

    for ex in data:
        tgt = [p for p in ex["PII_set"] if p["label"] in labels]
        if not tgt:
            continue
        n_elig += 1
        copies = args.per_sent
        if any(p["label"] == "OG_WORKPLACE" for p in tgt):
            copies = args.per_sent * args.ogw_boost
        augs = augment_sentence(ex, pools, labels, copies, rng)
        # 생성 실패(전부 검증 탈락) 추적
        n_fail += copies - len(augs) if copies > len(augs) else 0
        for a in augs:
            for p in a["PII_set"]:
                if p["label"] in labels:
                    per_label_added[p["label"]] += 1
        out.extend(augs)
        n_aug += len(augs)

    rng.shuffle(out)
    json.dump(out, open(args.output, "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)

    print("\n── 결과 ──")
    print(f"증강대상 문장: {n_elig}")
    print(f"생성된 증강 문장: {n_aug}")
    print(f"라벨별 증강 엔티티 수: {dict(per_label_added)}")
    print(f"최종 출력: {len(out)} 문장 → {args.output}")

    # 샘플 출력
    print("\n── 증강 샘플 ──")
    shown = 0
    for ex in out:
        if "_aug" in ex["sent_idx"] and any(
            p["label"] == "OG_WORKPLACE" for p in ex["PII_set"]
        ):
            forms = [f"{p['form']}({p['label']})" for p in ex["PII_set"]]
            print(f"  {ex['sentence']}")
            print(f"     → {forms}")
            shown += 1
            if shown >= 5:
                break


if __name__ == "__main__":
    main()
