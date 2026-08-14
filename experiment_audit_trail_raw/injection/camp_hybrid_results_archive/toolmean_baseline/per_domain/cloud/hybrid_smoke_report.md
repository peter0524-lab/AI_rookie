# Hybrid 스모크 테스트 결과 (features=dump_hybrid_cloud)

| variant | Acc | macroF1 | FPR | FNR | n_test |
|---|---|---|---|---|---|
| attn | 0.915 | 0.907 | 0.0125 | 0.0975 | 800 |
| hidden | 0.949 | 0.942 | 0.0375 | 0.0275 | 800 |
| hybrid | 0.953 | 0.947 | 0.0275 | 0.035 | 800 |

Δ macroF1 (hybrid − attn) = **+0.040**
→ hidden 결합이 attention 단독 대비 이득 있음 (본 실험 규모로 재검증 권장).