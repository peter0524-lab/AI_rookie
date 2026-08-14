# Hybrid 스모크 테스트 결과 (features=dump_hybrid_smoke)

| variant | Acc | macroF1 | FPR | FNR | n_test |
|---|---|---|---|---|---|
| attn | 0.575 | 0.568 | 0.1375 | 0.475 | 160 |
| hidden | 0.844 | 0.839 | 0.0 | 0.225 | 160 |
| hybrid | 0.900 | 0.896 | 0.025 | 0.1375 | 160 |

Δ macroF1 (hybrid − attn) = **+0.328**
→ hidden 결합이 attention 단독 대비 이득 있음 (본 실험 규모로 재검증 권장).