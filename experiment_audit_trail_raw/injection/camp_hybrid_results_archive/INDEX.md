# results_archive — 실험 결과 모음 (정리일: 2026-07-26)

원본 raw feature dump(`dump_hybrid_*`, 수십 GB)는 디스크 확보를 위해 대부분 삭제했다.
여기 있는 건 학습이 끝난 뒤 나온 **지표(json/md)만** — 용량 작고, 재현 없이도 결과 확인 가능.

## 폴더 구조

```
results_archive/
  toolmean_baseline/     backend=EXAONE-4.0-1.2B, hidden=toolmean+last(4층×2) — 1차 pilot
    per_domain/<domain>/   coding엔 두 버전: coding(lr=0.01, hwan 재현) / coding_lr1e-3_original(최초 실행, lr 버그 있던 버전)
    pooled/                8도메인 pooled (attn baseline vs hybrid)
  segment_hidden/         1순위 추천 반영: hidden을 head/mid/tail 3구간으로 나눠 위치정보 보존
    per_domain/<domain>/    + weighted-risk(0.25*FPR+0.75*FNR) 기준 체크포인트 선택 + 임계값 보정 적용
    pooled/                 ✅ 완료 — Acc 0.992 / FPR 0.0025 / FNR 0.0063 / risk 0.0053 (목표 2.4B risk 0.0188 대비 3.5배 우수, 목표 달성)
  legacy_k2048_experiments/  폐기된 실험(K=2048 attn_bigK, ensemble 등) — 참고용, baseline보다 대체로 나쁨
  alignfocus_diag/         원래 AlignFocus 진단①②③ (attention g 신호 존재 여부 체크, 이 hybrid 실험들과는 별개 목적)
```

## 핵심 비교 기준점 (외부, 여기 없음)

- hwan `alignsentinel_replicate` 원본 PDF: EXAONE-3.5-2.4B pooled Enc-first = **Acc 0.967, FPR 0.006, FNR 0.023**
  (`/data/team/hwan/alignsentinel_replicate/results_32k_exaone_data/`)
- 이 저장소의 모든 실험은 백본을 **EXAONE-4.0-1.2B**로 고정하고 위 2.4B 숫자를 넘는 게 목표.

## 읽는 법

- 도메인 단독: 각 폴더의 `hybrid_smoke_metrics.json` (attn/hidden/hybrid 3-way) 또는 `.md` 리포트
- pooled: `pooled_metrics.json` (attn/hybrid 2-way, `per_domain` 분해 포함)
- `risk` 필드 = `0.25*FPR + 0.75*FNR` (낮을수록 좋음, PDF Table 1/2와 동일 정의)
- segment_hidden 쪽 json엔 `raw`(보정 전)와 최상위(`bias` 적용 후, 보정값) 두 버전이 다 들어있음
