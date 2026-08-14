# Hybrid 스모크 테스트 결과 (features=dump_hybrid_project)

| variant | Acc | macroF1 | FPR | FNR | n_test |
|---|---|---|---|---|---|
| attn | 0.890 | 0.885 | 0.015 | 0.1525 | 800 |
| hidden | 0.914 | 0.909 | 0.065 | 0.075 | 800 |
| hybrid | 0.919 | 0.915 | 0.0875 | 0.0525 | 800 |

Δ macroF1 (hybrid − attn) = **+0.029**
→ hidden 결합이 attention 단독 대비 이득 있음 (본 실험 규모로 재검증 권장).