"""Hybrid 검증 — attention이 hidden-state 위에 무엇을 더하는가?

진단③에서 hidden-state 선형프로브가 attention g_mean을 압도했다(0.94 vs 0.78).
단, g_mean은 진단②에서 드러났듯 MIS-append의 tail 스파이크를 뭉갠다.
그래서 여기서는 **위치를 아는 attention feature**(tail−head 대비, peak 등)를 만들어,
hidden backbone 위에 그것을 얹었을 때 실제로 이득이 있는지 통제 비교한다.

재추출 불필요 — 기존 dump/*.npz 의 hs(hidden)와 g_prof(위치 프로파일)만 쓴다.

비교 대상(모두 동일 프로토콜: in-domain 5-fold CV + leave-one-domain-out):
  H         hidden backbone (중간 레이어 융합)
  A_spatial 위치-aware attention (tail−head, peak, std)  ← g_mean 아님
  A_flat    전체 위치 프로파일 (LH·B)
  H+A_spatial / H+A_flat   결합
결정: H+A 가 H 대비 macroF1·MIS recall·worst-domain에서 유의미하게(≥0.01) 오르면 hybrid 정당.
      안 오르면 attention은 hidden에 redundant → 순수 hidden-state로.

실행:  python src/diag_hybrid.py --dump dump --out results
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from diag_analyze import load_all, probe_cv, probe_lodo, MIS  # 동일 로더/프로브 재사용


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--dump", default="dump")
    p.add_argument("--out", default="results")
    p.add_argument("--hidden-cols", nargs="*", default=None,
                   help="쓸 hidden 컬럼명(예: L9_last L18_last). 미지정 시 중간 레이어 last 자동")
    p.add_argument("--tail-frac", type=float, default=0.3, help="tail로 볼 프로파일 뒷부분 비율")
    p.add_argument("--seed", type=int, default=42)
    return p.parse_args()


def build_attention_spatial(g_prof, g_std, tail_frac):
    """(n,LH,B) 위치 프로파일 → 위치-aware feature. g_mean(희석)이 아니라 스팬 신호를 살린다."""
    n, LH, B = g_prof.shape
    ntail = max(1, round(tail_frac * B))
    tail = g_prof[:, :, -ntail:].mean(2)      # tail 평균
    head = g_prof[:, :, :B - ntail].mean(2)   # head 평균
    A_tail = tail - head                       # (n,LH) tail−head 대비 (주입 스팬 신호)
    A_peak = g_prof.max(2)                      # (n,LH) 최대 grounding
    A_peakpos = g_prof.argmax(2) / max(B - 1, 1)  # (n,LH) 피크 위치(끝쪽=1)
    return np.concatenate([A_tail, A_peak, A_peakpos, g_std], axis=1).astype(np.float32)


def pick_hidden_cols(meta, requested):
    cols = meta["hs_cols"]
    if requested:
        idx = [cols.index(c) for c in requested]
        return idx, requested
    # 자동: 중간 레이어(깊이 25~50%)의 last 풀링 우선
    L = meta["L"]
    want = []
    for i, c in enumerate(cols):
        # 이름 형식 L{idx}_{pool}
        li = int(c.split("_")[0][1:]); pool = c.split("_")[1]
        if pool == "last" and 0.2 * L <= li <= 0.55 * L:
            want.append((i, c))
    if not want:  # 폴백: 전부 last
        want = [(i, c) for i, c in enumerate(cols) if c.endswith("last")]
    return [i for i, _ in want], [c for _, c in want]


def main():
    args = parse_args()
    dump, out = Path(args.dump), Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    meta, D = load_all(dump)
    y, dom = D["labels"], D["domain"]
    n = len(y)
    lines = []
    def w(s=""): lines.append(s); print(s)

    hid_idx, hid_names = pick_hidden_cols(meta, args.hidden_cols)
    H = D["hs"][:, hid_idx, :].reshape(n, -1)                 # 중간 레이어 융합
    A_spatial = build_attention_spatial(D["g_prof"], D["g_std"], args.tail_frac)
    A_flat = D["g_prof"].reshape(n, -1)                       # 전체 프로파일

    feats = {
        "H (hidden 융합)": H,
        "A_spatial (tail−head,peak,std)": A_spatial,
        "A_flat (전체 프로파일)": A_flat,
        "H + A_spatial": np.concatenate([H, A_spatial], 1),
        "H + A_flat": np.concatenate([H, A_flat], 1),
    }

    w(f"# Hybrid 검증 — attention이 hidden 위에 더하는 값  (model={meta['model_key']}, N={n})\n")
    w(f"- hidden backbone 컬럼: {hid_names}  (dim {H.shape[1]})")
    w(f"- attention feature: A_spatial dim {A_spatial.shape[1]}, A_flat dim {A_flat.shape[1]}")
    w(f"- tail_frac={args.tail_frac}\n")

    w("| feature | in-domain acc | macroF1 | MIS recall | cross meanF1 | worstF1 |")
    w("|---|---|---|---|---|---|")
    res = {}
    for name, X in feats.items():
        acc, mf1, mr = probe_cv(X, y, args.seed)
        cmean, cworst = probe_lodo(X, y, dom)
        res[name] = dict(acc=acc, mf1=mf1, mr=mr, cmean=cmean, cworst=cworst)
        w(f"| {name} | {acc:.3f} | {mf1:.3f} | {mr:.3f} | {cmean:.3f} | {cworst:.3f} |")
    w("")

    # ===== 결정 =====
    H0 = res["H (hidden 융합)"]
    best_combo_name = max(["H + A_spatial", "H + A_flat"], key=lambda k: res[k]["mf1"])
    C = res[best_combo_name]
    d_mf1 = C["mf1"] - H0["mf1"]
    d_mr = C["mr"] - H0["mr"]
    d_worst = C["cworst"] - H0["cworst"]

    w("## 결정 (자동)\n")
    w(f"- best 결합 = **{best_combo_name}**")
    w(f"- Δ macroF1  = {d_mf1:+.3f}  (H {H0['mf1']:.3f} → {C['mf1']:.3f})")
    w(f"- Δ MIS recall = {d_mr:+.3f}  (H {H0['mr']:.3f} → {C['mr']:.3f})")
    w(f"- Δ worst-domain F1 = {d_worst:+.3f}  (H {H0['cworst']:.3f} → {C['cworst']:.3f})")
    added = (d_mf1 >= 0.01) or (d_mr >= 0.01) or (d_worst >= 0.01)
    if added:
        w("\n→ **attention이 hidden 위에 이득을 더함 → hybrid 정당.** "
          "특히 이득이 MIS recall/worst-domain에 있으면 보안·일반화 관점에서 의미.")
    else:
        w("\n→ **attention이 hidden에 redundant** (이득 <0.01). "
          "**순수 hidden-state로 가고 attention은 분석/서사용으로만.**")
    w(f"\n참고: A_spatial 단독 macroF1 {res['A_spatial (tail−head,peak,std)']['mf1']:.3f} "
      f"(g_mean 단독 0.775 대비 tail feature로 얼마나 회복됐나 확인)")
    w("\n---\n*동일 dump, 동일 프로브 프로토콜. 결합은 L2 정규화 로지스틱이라 노이즈 차원은 이득으로 안 잡힘 → 비교 공정.*")

    (out / "hybrid_report.md").write_text("\n".join(lines), encoding="utf-8")
    json.dump({k: v for k, v in res.items()}, open(out / "hybrid_metrics.json", "w"),
              ensure_ascii=False, indent=2)
    print(f"\n리포트 → {out/'hybrid_report.md'}")


if __name__ == "__main__":
    main()
