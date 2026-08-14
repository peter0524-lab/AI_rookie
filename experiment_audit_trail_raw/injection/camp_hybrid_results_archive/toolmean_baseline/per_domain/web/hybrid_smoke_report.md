# Hybrid 스모크 테스트 결과 (features=dump_hybrid_web)

| variant | Acc | macroF1 | FPR | FNR | n_test |
|---|---|---|---|---|---|
| attn | 0.930 | 0.918 | 0.0175 | 0.05 | 800 |
| hidden | 0.946 | 0.941 | 0.025 | 0.0475 | 800 |
| hybrid | 0.932 | 0.929 | 0.005 | 0.1 | 800 |

Δ macroF1 (hybrid − attn) = **+0.011**
→ hidden 결합이 attention 단독 대비 이득 있음 (본 실험 규모로 재검증 권장).