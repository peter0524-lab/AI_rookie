# Hybrid 검증 — attention이 hidden 위에 더하는 값  (model=qwen, N=2400)

- hidden backbone 컬럼: ['L9_last', 'L18_last']  (dim 8192)
- attention feature: A_spatial dim 4608, A_flat dim 11520
- tail_frac=0.3

| feature | in-domain acc | macroF1 | MIS recall | cross meanF1 | worstF1 |
|---|---|---|---|---|---|
| H (hidden 융합) | 0.950 | 0.951 | 0.960 | 0.953 | 0.924 |
| A_spatial (tail−head,peak,std) | 0.834 | 0.834 | 0.792 | 0.824 | 0.790 |
| A_flat (전체 프로파일) | 0.892 | 0.892 | 0.868 | 0.875 | 0.850 |
| H + A_spatial | 0.950 | 0.950 | 0.948 | 0.946 | 0.917 |
| H + A_flat | 0.945 | 0.945 | 0.948 | 0.944 | 0.913 |

## 결정 (자동)

- best 결합 = **H + A_spatial**
- Δ macroF1  = -0.001  (H 0.951 → 0.950)
- Δ MIS recall = -0.012  (H 0.960 → 0.948)
- Δ worst-domain F1 = -0.006  (H 0.924 → 0.917)

→ **attention이 hidden에 redundant** (이득 <0.01). **순수 hidden-state로 가고 attention은 분석/서사용으로만.**

참고: A_spatial 단독 macroF1 0.834 (g_mean 단독 0.775 대비 tail feature로 얼마나 회복됐나 확인)

---
*동일 dump, 동일 프로브 프로토콜. 결합은 L2 정규화 로지스틱이라 노이즈 차원은 이득으로 안 잡힘 → 비교 공정.*