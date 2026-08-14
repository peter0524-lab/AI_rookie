"""진단 분석 (CPU, GPU 불필요, 빠름). dump/ 를 읽어 세 질문에 숫자로 답한다.

진단① g가 3-class를 가르는가?
  - head별 g_mean으로 misaligned-vs-rest AUC 랭킹 → 신호를 담은 head가 존재하는지.
  - 전체 head g 벡터로 로지스틱 회귀(in-domain CV, cross-domain LODO) → 집단적 판별력.

진단② 부호/스팬: MIS의 grounding이 AL보다 낮은가(내 가정) 높은가(반례)?
  - 클래스별(NI/AL/MIS-append/MIS-replace) g_mean 평균 + AL↔MIS Cohen's d.
  - 상위 판별 head들의 위치 프로파일(head→tail) 플롯: 주입 스팬에서 g가 내려가나.

진단③ hidden-state 프로브 바닥선:
  - 레이어·풀링별 로지스틱 회귀(in-domain CV, cross-domain LODO).
  - g 기반 프로브와 같은 표에서 비교 → attention이 hidden state를 이기는가.

출력: results/diag_report.md + results/*.png

실행:  python src/diag_analyze.py --dump dump --out results
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from sklearn.linear_model import LogisticRegression  # noqa: E402
from sklearn.preprocessing import StandardScaler  # noqa: E402
from sklearn.pipeline import make_pipeline  # noqa: E402
from sklearn.model_selection import StratifiedKFold  # noqa: E402
from sklearn.metrics import f1_score, roc_auc_score, recall_score  # noqa: E402

MIS, ALIGNED, NONINSTR = 0, 1, 2  # LABEL_TO_ID
CMODE = {0: "NI", 1: "AL", 2: "MIS-append", 3: "MIS-replace"}


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--dump", default="dump")
    p.add_argument("--out", default="results")
    p.add_argument("--top-heads", type=int, default=20)
    p.add_argument("--seed", type=int, default=42)
    return p.parse_args()


def load_all(dump: Path):
    meta = json.load(open(dump / "run_meta.json", encoding="utf-8"))
    files = sorted(dump.glob("*_*.npz"))
    parts = {k: [] for k in ["g_mean", "g_std", "g_max", "g_prof", "hs", "labels", "cmodes", "tool_lens"]}
    domains = []
    for fp in files:
        d = np.load(fp, allow_pickle=True)
        for k in parts:
            parts[k].append(d[k])
        domains += [str(d["domain"])] * len(d["labels"])
    data = {k: np.concatenate(v, 0) for k, v in parts.items()}
    data["domain"] = np.array(domains)
    # fp16 → fp32 (sklearn 안정성)
    for k in ["g_mean", "g_std", "g_max", "hs"]:
        data[k] = data[k].astype(np.float32)
    data["g_prof"] = data["g_prof"].astype(np.float32)
    return meta, data


def probe_cv(X, y, seed, k=5):
    """in-domain stratified k-fold: (acc, macroF1, misaligned recall)."""
    skf = StratifiedKFold(n_splits=k, shuffle=True, random_state=seed)
    yp = np.zeros_like(y)
    for tr, te in skf.split(X, y):
        clf = make_pipeline(StandardScaler(),
                            LogisticRegression(max_iter=2000, C=1.0))
        clf.fit(X[tr], y[tr])
        yp[te] = clf.predict(X[te])
    acc = (yp == y).mean()
    mf1 = f1_score(y, yp, average="macro")
    mis_recall = recall_score(y, yp, labels=[MIS], average="macro")
    return acc, mf1, mis_recall


def probe_lodo(X, y, domain):
    """leave-one-domain-out: (mean macroF1, worst macroF1)."""
    f1s = []
    for d in np.unique(domain):
        tr, te = domain != d, domain == d
        if len(np.unique(y[tr])) < 2 or te.sum() == 0:
            continue
        clf = make_pipeline(StandardScaler(),
                            LogisticRegression(max_iter=2000, C=1.0))
        clf.fit(X[tr], y[tr])
        f1s.append(f1_score(y[te], clf.predict(X[te]), average="macro"))
    return (float(np.mean(f1s)), float(np.min(f1s))) if f1s else (float("nan"), float("nan"))


def cohens_d(a, b):
    na, nb = len(a), len(b)
    sp = np.sqrt(((na - 1) * a.var(ddof=1) + (nb - 1) * b.var(ddof=1)) / max(na + nb - 2, 1))
    return (a.mean() - b.mean()) / (sp + 1e-9)


def main():
    args = parse_args()
    dump, out = Path(args.dump), Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    meta, D = load_all(dump)
    L, H, LH, B = meta["L"], meta["H"], meta["LH"], meta["bins"]
    y = D["labels"]; dom = D["domain"]; cm = D["cmodes"]
    n = len(y)
    lines = []
    def w(s=""): lines.append(s); print(s)

    w(f"# Injection 진단 리포트  (model={meta['model_key']}, N={n})\n")
    w(f"- 샘플 {n}개 · 도메인 {len(np.unique(dom))}개 · L={L} H={H} (head {LH}개)")
    counts = {CMODE[k]: int((cm == k).sum()) for k in sorted(CMODE)}
    w(f"- 구성모드별: {counts}")
    w(f"- 클래스(3): MIS={int((y==MIS).sum())} AL={int((y==ALIGNED).sum())} NI={int((y==NONINSTR).sum())}\n")

    # ================= 진단① g 판별력 =================
    w("## 진단① — g(tool→user grounding)가 클래스를 가르는가\n")
    gm = D["g_mean"]  # (n, LH)
    y_mis = (y == MIS).astype(int)
    # head별 misaligned-vs-rest AUC
    aucs = np.array([roc_auc_score(y_mis, gm[:, h]) for h in range(LH)])
    strength = np.abs(aucs - 0.5)
    order = np.argsort(-strength)
    top = order[:args.top_heads]
    w(f"**head별 misaligned-vs-rest AUC** (0.5=무신호). 최상위 {args.top_heads}개:\n")
    w("| rank | layer | head | AUC | 방향(g↑=MIS?) |")
    w("|---|---|---|---|---|")
    for rank, h in enumerate(top, 1):
        w(f"| {rank} | {h // H} | {h % H} | {aucs[h]:.3f} | {'높음' if aucs[h] > 0.5 else '낮음'} |")
    w(f"\n- 최고 단일 head AUC = **{aucs[top[0]]:.3f}** (|AUC-0.5|={strength[top[0]]:.3f})")
    w(f"- |AUC-0.5|>0.10 인 head 수: **{int((strength>0.10).sum())} / {LH}**")
    w(f"- |AUC-0.5|>0.15 인 head 수: **{int((strength>0.15).sum())} / {LH}**\n")

    # 집단 프로브 (g_mean 전체, 그리고 g_mean+std+max)
    w("**전체 head g로 3-class 로지스틱 회귀** (신호가 head들에 흩어져 있는가):\n")
    w("| feature | in-domain acc | macroF1 | MIS recall | cross-domain meanF1 | worstF1 |")
    w("|---|---|---|---|---|---|")
    feats = {"g_mean (LH)": gm,
             "g_mean+std+max (3·LH)": np.concatenate([gm, D["g_std"], D["g_max"]], 1)}
    g_indomain_f1 = None
    for name, X in feats.items():
        acc, mf1, mr = probe_cv(X, y, args.seed)
        cmean, cworst = probe_lodo(X, y, dom)
        if g_indomain_f1 is None:
            g_indomain_f1 = mf1; g_cross_f1 = cmean
        w(f"| {name} | {acc:.3f} | {mf1:.3f} | {mr:.3f} | {cmean:.3f} | {cworst:.3f} |")
    w("")

    # ================= 진단② 부호 / 스팬 =================
    w("## 진단② — grounding의 부호와 위치(주입 스팬)\n")
    # 상위 head들에서 클래스별 g_mean 평균
    topH = order[:max(args.top_heads, 30)]
    g_top = gm[:, topH].mean(1)  # 샘플별, 상위 head 평균 g
    w("**상위 판별 head 평균 g의 구성모드별 분포** (부호 확인):\n")
    w("| 구성모드 | mean g | std |")
    w("|---|---|---|")
    for k in sorted(CMODE):
        v = g_top[cm == k]
        if len(v):
            w(f"| {CMODE[k]} | {v.mean():+.4f} | {v.std():.4f} |")
    d_al = g_top[cm == 1]
    d_ap = g_top[cm == 2]
    d_rp = g_top[cm == 3]
    w("")
    if len(d_al) and len(d_ap):
        w(f"- AL vs MIS-append  Cohen's d = **{cohens_d(d_al, d_ap):+.3f}**  "
          f"(양수=AL이 grounding 높음=내 가정과 일치)")
    if len(d_al) and len(d_rp):
        w(f"- AL vs MIS-replace Cohen's d = **{cohens_d(d_al, d_rp):+.3f}**")
    w("")

    # 위치 프로파일 플롯: 상위 head 평균, 구성모드별
    prof = D["g_prof"][:, topH, :].mean(1)  # (n, B)  상위 head 평균 위치 프로파일
    plt.figure(figsize=(7, 4.5))
    for k in sorted(CMODE):
        m = cm == k
        if m.sum():
            plt.plot(np.linspace(0, 1, B), prof[m].mean(0), marker="o", label=f"{CMODE[k]} (n={m.sum()})")
    plt.xlabel("position in tool response (0=start, 1=end)")
    plt.ylabel("mean g (top heads)")
    plt.title(f"tool->user grounding by position - {meta['model_key']}")
    plt.legend(); plt.grid(alpha=0.3); plt.tight_layout()
    p1 = out / "g_position_profile.png"
    plt.savefig(p1, dpi=130); plt.close()
    w(f"![위치 프로파일]({p1.name})\n")
    w(f"→ **{p1.name}**: MIS-append의 tail(오른쪽)이 AL보다 내려가면 '주입 스팬이 grounding을 끊는다'는 가정 지지.\n")

    # head AUC 막대
    plt.figure(figsize=(7, 3.8))
    plt.bar(range(len(top)), aucs[top])
    plt.axhline(0.5, color="k", lw=0.8)
    plt.xlabel(f"top {len(top)} heads"); plt.ylabel("misaligned-vs-rest AUC")
    plt.title("per-head g discriminability"); plt.tight_layout()
    p2 = out / "head_auc.png"
    plt.savefig(p2, dpi=130); plt.close()
    w(f"![head AUC]({p2.name})\n")

    # ================= 진단③ hidden-state 바닥선 =================
    w("## 진단③ — hidden-state 프로브 바닥선 (attention이 넘어야 할 선)\n")
    hs = D["hs"]  # (n, S, hidden)
    cols = meta["hs_cols"]
    w("| feature | in-domain acc | macroF1 | MIS recall | cross meanF1 | worstF1 |")
    w("|---|---|---|---|---|---|")
    best_hs_f1 = -1; best_hs_name = None
    for c, name in enumerate(cols):
        X = hs[:, c, :]
        acc, mf1, mr = probe_cv(X, y, args.seed)
        cmean, cworst = probe_lodo(X, y, dom)
        star = ""
        if mf1 > best_hs_f1:
            best_hs_f1 = mf1; best_hs_name = name; best_hs_cross = cmean
        w(f"| hidden {name} | {acc:.3f} | {mf1:.3f} | {mr:.3f} | {cmean:.3f} | {cworst:.3f} |")
    w("")

    # ================= 종합 판정 =================
    w("## 종합 판정 (자동 요약)\n")
    n_strong = int((strength > 0.15).sum())
    w(f"1. **g 신호 존재?** 최고 head |AUC-0.5|={strength[top[0]]:.3f} (AUC {aucs[top[0]]:.3f}, "
      f"{'g↑=MIS' if aucs[top[0]]>0.5 else 'g↓=MIS'}), |AUC-.5|>0.15 head {n_strong}개 "
      f"→ {'있음 (attention-g에 신호)' if n_strong >= 3 or strength[top[0]] > 0.15 else '약함 — attention-g 재고 필요'}")
    dsign = cohens_d(d_al, d_ap) if len(d_al) and len(d_ap) else float('nan')
    w(f"2. **부호 가정?** AL vs MIS-append d={dsign:+.3f} "
      f"→ {'가정과 일치(AL grounding↑)' if dsign > 0.2 else ('반대 부호!' if dsign < -0.2 else '분리 미미')}")
    w(f"3. **hidden-state 대비?** g best macroF1={g_indomain_f1:.3f} (cross {g_cross_f1:.3f}) vs "
      f"hidden best={best_hs_f1:.3f}@{best_hs_name} (cross {best_hs_cross:.3f})")
    if best_hs_f1 > g_indomain_f1 + 0.05:
        w("   → hidden-state가 g를 유의하게 앞섬. **attention 접고 hidden-state 선회 검토.**")
    elif g_cross_f1 > best_hs_cross + 0.03:
        w("   → g가 cross-domain에서 앞섬. **요약-불변성이 강점 → attention-g 유지 근거.**")
    else:
        w("   → 접전. 두 신호 결합(hybrid) 또는 스팬-aware 통계로 g 보강 검토.")
    w("\n---\n*주의: 추출 forward 비용은 attention/hidden 유사. 여기 결론은 '신호 존재/부호/상대우열'까지다.*")

    report = out / "diag_report.md"
    report.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n리포트 → {report}\n플롯 → {p1}, {p2}")


if __name__ == "__main__":
    main()
