import json
from collections import Counter

tr = json.load(open("data/train.json", encoding="utf-8"))
te = json.load(open("data/test.json", encoding="utf-8"))

CUES = ["사옥", "입사", "이직", "합격", "다니", "근무", "일하", "사장",
        "운영", "취업", "회사", "지점", "본사", "현장", "거래처"]


def og_context_counts(data):
    c = Counter()
    for ex in data:
        s = ex["sentence"]
        for p in ex["PII_set"]:
            if p["label"] != "OG_WORKPLACE":
                continue
            around = s[max(0, p["begin"] - 6):p["end"] + 8]
            for cue in CUES:
                if cue in around:
                    c[cue] += 1
    return c


tc = og_context_counts(tr)
ec = og_context_counts(te)

ntr = sum(1 for ex in tr for p in ex["PII_set"] if p["label"] == "OG_WORKPLACE")
nte = sum(1 for ex in te for p in ex["PII_set"] if p["label"] == "OG_WORKPLACE")

head = "cue".ljust(6) + " | train | test"
print(head)
print("-" * len(head))
for cue in CUES:
    print(cue.ljust(6) + " | " + str(tc.get(cue, 0)).rjust(5) + " | " + str(ec.get(cue, 0)).rjust(4))
print()
print("총 OG 개체: train " + str(ntr) + ", test " + str(nte))
print("train OG 개체당 평균 단서 매치: " + str(round(sum(tc.values()) / ntr, 3)))
