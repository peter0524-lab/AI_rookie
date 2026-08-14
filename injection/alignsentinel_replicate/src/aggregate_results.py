"""
결과 집계 — results/*.json 을 모아 상세 리포트(results/summary.md)를 만든다.

서버 왕복을 줄이기 위해 summary.md 하나에 분석에 필요한 것을 최대한 담는다:
  - 도메인별/pooled/cross 지표 표 (논문 참조 수치 병기)
  - confusion matrix 전체, 클래스별 precision/recall/F1
  - 오분류 샘플 목록 (--data 지정 시 원문 스니펫 포함)
  - 특징 추출 통계 (--features 지정 시), 학습 설정
기계가 읽을 통합본은 results/summary_full.json 으로 함께 저장된다.

실행:
  python src/aggregate_results.py --results results --out results/summary.md \
      --features features --data data/full_test.json
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

LABELS = ["misaligned", "aligned", "non_instruction"]

PAPER_TABLE_1B = {
    "Ours (Avg-first)": "FPR 0.00~0.01 / FNR 0.00~0.01 / Acc 0.92~0.99",
    "Ours (Enc-first)": "FPR 0.00 / FNR 0.00~0.01 / Acc 0.96~1.00",
    "Chen et al.": "FPR 0.00~0.03 / FNR 0.00~0.17",
    "Prompt-Guard-2": "FPR 0.00 / FNR 0.70~1.00",
}
PAPER_TABLE_3 = {
    ("A2B", "avg"): "FPR 0.00 / FNR 0.02 / Acc 0.93",
    ("A2B", "enc"): "FPR 0.00 / FNR 0.01 / Acc 0.94",
    ("B2A", "avg"): "FPR 0.04 / FNR 0.00 / Acc 0.92",
    ("B2A", "enc"): "FPR 0.00 / FNR 0.00 / Acc 0.98",
}

METHOD_ORDER = ["Ours (Avg-first)", "Ours (Enc-first)", "Chen et al. (klue/roberta)",
                "Prompt-Guard-2 (zero-shot)"]


def fmt(v, nd=3):
    return f"{v:.{nd}f}" if isinstance(v, (int, float)) else "–"


def confusion_table(cm: list[list[int]]) -> list[str]:
    head = "| true \\ pred | " + " | ".join(LABELS) + " |"
    sep = "|---|" + "---|" * 3
    rows = [f"| **{LABELS[i]}** | " + " | ".join(str(cm[i][j]) for j in range(3)) + " |" for i in range(3)]
    return [head, sep] + rows


def per_class_table(pc: dict) -> list[str]:
    lines = ["| class | precision | recall | F1 | support |", "|---|---|---|---|---|"]
    for c in LABELS:
        v = pc.get(c, {})
        lines.append(f"| {c} | {fmt(v.get('precision'))} | {fmt(v.get('recall'))} | "
                     f"{fmt(v.get('f1'))} | {v.get('support', '–')} |")
    return lines


def metric_cells(m: dict) -> str:
    return f"{fmt(m.get('fpr'), 2)} / {fmt(m.get('fnr'), 2)} / {fmt(m.get('acc'), 2)}"


def ours_method_name(m: dict) -> str:
    variant = "Avg-first" if m.get("variant") == "avg" else "Enc-first"
    detector = m.get("detector", "paper")
    if detector == "paper":
        return f"Ours ({variant})"
    return f"Ours {detector.title()} ({variant})"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", default="results")
    parser.add_argument("--out", default="results/summary.md")
    parser.add_argument("--features", default=None, help="특징 추출 통계 포함용 features/ 경로")
    parser.add_argument("--data", default=None, help="오분류 샘플에 원문 스니펫을 붙일 full_test.json")
    parser.add_argument("--max-errors-per-block", type=int, default=10)
    args = parser.parse_args()

    results_dir = Path(args.results)
    all_raw: dict[str, dict] = {}
    per_domain: dict[str, dict[str, dict]] = {}   # method → domain → metrics
    pooled: dict[str, dict] = {}                  # variant → metrics
    cross: dict[tuple[str, str], dict] = {}       # (direction, variant) → metrics

    for p in sorted(results_dir.glob("*.json")):
        if p.name in ("summary_full.json",):
            continue
        with open(p, "r", encoding="utf-8") as f:
            m = json.load(f)
        if "domain" not in m:
            continue
        all_raw[p.stem] = m
        if p.name.startswith("ours_pooled_"):
            pooled[m["variant"]] = m
        elif p.name.startswith("ours_cross_"):
            cross[(m["domain"], m["variant"])] = m
        elif p.name.startswith("ours_avg"):
            per_domain.setdefault(ours_method_name(m), {})[m["domain"]] = m
        elif p.name.startswith("ours_enc"):
            per_domain.setdefault(ours_method_name(m), {})[m["domain"]] = m
        elif p.name.startswith("baseline_chen"):
            per_domain.setdefault("Chen et al. (klue/roberta)", {})[m["domain"]] = m
        elif p.name.startswith("baseline_promptguard"):
            per_domain.setdefault("Prompt-Guard-2 (zero-shot)", {})[m["domain"]] = m

    if not all_raw:
        raise SystemExit("results/에 결과 json이 없습니다")

    # 오분류 원문 대조용 데이터
    text_by_id = {}
    if args.data and Path(args.data).exists():
        with open(args.data, "r", encoding="utf-8") as f:
            for r in json.load(f):
                text_by_id[r["id"]] = r

    domains = sorted({d for per in per_domain.values() for d in per})
    any_ours = next(iter(pooled.values()), None) or next(
        (m for per in per_domain.values() for m in per.values() if "input_dim" in m), None)

    L: list[str] = []
    L.append("# AlignSentinel 재현 결과 리포트 (indirect, 한국어 벤치마크)")
    L.append("")
    L.append(f"- 생성 시각: {datetime.now().isoformat(timespec='seconds')}")
    if any_ours:
        L.append(f"- Backend LLM: `{any_ours.get('backend_model')}` / attention 특징 차원: {any_ours.get('input_dim')}")
        L.append(f"- 학습 설정: {any_ours.get('epochs')} epochs, lr {any_ours.get('lr')}, "
                 f"batch avg=32 / enc=16, detector {any_ours.get('detector', 'paper')}")
    L.append("- 지표: FPR/FNR은 misaligned=positive 기준 이진 환산, Acc는 3-class.")
    L.append("")

    # ── 1. 도메인별 메인 표 ────────────────────────────────────────────
    L.append("## 1. 도메인별 결과 (논문 Table 1b 대응)")
    L.append("")
    L.append("셀 형식: FPR / FNR / Acc (베이스라인은 이진이라 Acc 없음)")
    L.append("")
    L.append("| method | " + " | ".join(domains) + " | **mean** | 논문 참조 |")
    L.append("|---|" + "---|" * (len(domains) + 2))
    methods = [m for m in METHOD_ORDER if m in per_domain]
    methods.extend(m for m in sorted(per_domain) if m not in methods)
    for method in methods:
        per = per_domain.get(method)
        if not per:
            continue
        cells, fprs, fnrs, accs = [], [], [], []
        for d in domains:
            m = per.get(d)
            if m is None:
                cells.append("–")
                continue
            cells.append(metric_cells(m))
            if m.get("fpr") is not None:
                fprs.append(m["fpr"])
            if m.get("fnr") is not None:
                fnrs.append(m["fnr"])
            if m.get("acc") is not None:
                accs.append(m["acc"])
        mean_cell = (f"{fmt(sum(fprs)/len(fprs), 2) if fprs else '–'} / "
                     f"{fmt(sum(fnrs)/len(fnrs), 2) if fnrs else '–'} / "
                     f"{fmt(sum(accs)/len(accs), 2) if accs else '–'}")
        ref = PAPER_TABLE_1B.get(method.split(" (")[0] if method.startswith("Chen") or method.startswith("Prompt")
                                 else method, "–")
        L.append(f"| {method} | " + " | ".join(cells) + f" | **{mean_cell}** | {ref} |")
    L.append("")

    # ── 2. Pooled ─────────────────────────────────────────────────────
    if pooled:
        L.append("## 2. Pooled — 8개 도메인 통합 학습 (train 12,800 → test 3,200)")
        L.append("")
        L.append("| variant | FPR | FNR | Acc | n_errors |")
        L.append("|---|---|---|---|---|")
        for v in ("avg", "enc"):
            m = pooled.get(v)
            if m:
                L.append(f"| {'Avg-first' if v=='avg' else 'Enc-first'} | {fmt(m['fpr'])} | "
                         f"{fmt(m['fnr'])} | {fmt(m['acc'])} | {m.get('n_errors','–')} |")
        for v in ("avg", "enc"):
            m = pooled.get(v)
            if not m or "per_domain" not in m:
                continue
            L.append("")
            L.append(f"### 2.{1 if v=='avg' else 2} Pooled {'Avg-first' if v=='avg' else 'Enc-first'} — 도메인별 분해")
            L.append("")
            L.append("| domain | FPR | FNR | Acc |")
            L.append("|---|---|---|---|")
            for d, dm in sorted(m["per_domain"].items()):
                L.append(f"| {d} | {fmt(dm['fpr'])} | {fmt(dm['fnr'])} | {fmt(dm['acc'])} |")
        L.append("")

    # ── 3. Cross-domain ───────────────────────────────────────────────
    if cross:
        L.append("## 3. Cross-domain generalization (논문 Table 3 대응)")
        L.append("")
        L.append("그룹 A={coding, cloud, project, shopping}, B={finance, messaging, social_media, web}. "
                 "한 그룹 전체(8,000건)로 학습해 반대 그룹 전체로 평가.")
        L.append("")
        L.append("| setting | FPR | FNR | Acc | n_errors | 논문 (참조) |")
        L.append("|---|---|---|---|---|---|")
        for (direction, v), m in sorted(cross.items()):
            name = f"{'A→B' if direction=='A2B' else 'B→A'} {'Avg-first' if v=='avg' else 'Enc-first'}"
            L.append(f"| {name} | {fmt(m['fpr'])} | {fmt(m['fnr'])} | {fmt(m['acc'])} | "
                     f"{m.get('n_errors','–')} | {PAPER_TABLE_3.get((direction, v), '–')} |")
        for (direction, v), m in sorted(cross.items()):
            if "per_domain" not in m:
                continue
            L.append("")
            L.append(f"### {'A→B' if direction=='A2B' else 'B→A'} {'Avg-first' if v=='avg' else 'Enc-first'} — 평가 도메인별 분해")
            L.append("")
            L.append("| domain | FPR | FNR | Acc |")
            L.append("|---|---|---|---|")
            for d, dm in sorted(m["per_domain"].items()):
                L.append(f"| {d} | {fmt(dm['fpr'])} | {fmt(dm['fnr'])} | {fmt(dm['acc'])} |")
        L.append("")

    # ── 4. Confusion matrix + 클래스별 지표 (Ours) ─────────────────────
    L.append("## 4. Confusion matrix / 클래스별 지표 (Ours)")
    L.append("")
    blocks: list[tuple[str, dict]] = []
    for method in sorted(m for m in per_domain if m.startswith("Ours")):
        for d, m in sorted(per_domain.get(method, {}).items()):
            blocks.append((f"{method} — {d}", m))
    for v, m in sorted(pooled.items()):
        blocks.append((f"Pooled {'Avg-first' if v=='avg' else 'Enc-first'} (전체)", m))
    for (direction, v), m in sorted(cross.items()):
        blocks.append((f"{'A→B' if direction=='A2B' else 'B→A'} {'Avg-first' if v=='avg' else 'Enc-first'}", m))
    for title, m in blocks:
        if "confusion" not in m:
            continue
        L.append(f"### {title}")
        L.append("")
        L.extend(confusion_table(m["confusion"]))
        if "per_class" in m:
            L.append("")
            L.extend(per_class_table(m["per_class"]))
        L.append("")

    # ── 5. 오분류 샘플 ─────────────────────────────────────────────────
    L.append("## 5. 오분류 샘플 상세")
    L.append("")
    if not text_by_id:
        L.append("(원문 스니펫을 붙이려면 --data data/full_test.json 로 실행)")
        L.append("")
    for title, m in blocks:
        errs = m.get("errors")
        if not errs:
            continue
        L.append(f"### {title} — 오분류 {m.get('n_errors', len(errs))}건" +
                 (f" (상위 {args.max_errors_per_block}건 표시)" if len(errs) > args.max_errors_per_block else ""))
        L.append("")
        for e in errs[: args.max_errors_per_block]:
            rec = text_by_id.get(e["id"])
            L.append(f"- `{e['id']}` — true **{e['true']}** → pred **{e['pred']}**")
            if rec:
                up = rec["user_prompt"][:80].replace("\n", " ")
                tr = rec["tool_response"][:160].replace("\n", " ")
                L.append(f"  - UP: {up}")
                L.append(f"  - TR: {tr}{'…' if len(rec['tool_response']) > 160 else ''}")
        L.append("")

    # ── 6. 베이스라인 상세 ─────────────────────────────────────────────
    base_rows = [(k, v) for k, v in all_raw.items() if k.startswith("baseline_")]
    if base_rows:
        L.append("## 6. 베이스라인 상세")
        L.append("")
        L.append("| method | domain | FPR | FNR | binary Acc | n_test |")
        L.append("|---|---|---|---|---|---|")
        for k, m in sorted(base_rows):
            L.append(f"| {m.get('method')} | {m['domain']} | {fmt(m['fpr'])} | {fmt(m['fnr'])} | "
                     f"{fmt(m.get('binary_acc'))} | {m.get('n_test','–')} |")
        L.append("")

    # ── 7. 특징 추출 통계 ─────────────────────────────────────────────
    if args.features and Path(args.features).exists():
        metas = sorted(Path(args.features).glob("*_meta.json"))
        if metas:
            L.append("## 7. 특징 추출 통계")
            L.append("")
            L.append("| split/domain | n | skipped | mean pairs(원본) | stored K |")
            L.append("|---|---|---|---|---|")
            for mp in metas:
                with open(mp, "r", encoding="utf-8") as f:
                    fm = json.load(f)
                npo = fm.get("n_pairs_original") or []
                mean_p = f"{sum(npo)/len(npo):.0f}" if npo else "–"
                L.append(f"| {mp.name[:-len('_meta.json')]} | {len(fm.get('ids', []))} | "
                         f"{len(fm.get('skipped', []))} | {mean_p} | {fm.get('max_pairs','–')} |")
            L.append("")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    with open(results_dir / "summary_full.json", "w", encoding="utf-8") as f:
        json.dump(all_raw, f, ensure_ascii=False, indent=1)
    print(f"→ {out}  (기계용: {results_dir/'summary_full.json'})")
    print(f"   섹션: 도메인별 표 / pooled / cross / confusion+클래스별 / 오분류 샘플 / 베이스라인 / 추출 통계")


if __name__ == "__main__":
    main()
