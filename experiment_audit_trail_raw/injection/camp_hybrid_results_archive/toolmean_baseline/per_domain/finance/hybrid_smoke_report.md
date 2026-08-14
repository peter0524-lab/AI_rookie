# Hybrid 스모크 테스트 결과 (features=dump_hybrid_finance)

| variant | Acc | macroF1 | FPR | FNR | n_test |
|---|---|---|---|---|---|
| attn | 0.921 | 0.916 | 0.045 | 0.08 | 800 |
| hidden | 0.934 | 0.925 | 0.02 | 0.055 | 800 |
| hybrid | 0.950 | 0.943 | 0.0275 | 0.0275 | 800 |

Δ macroF1 (hybrid − attn) = **+0.026**
→ hidden 결합이 attention 단독 대비 이득 있음 (본 실험 규모로 재검증 권장).