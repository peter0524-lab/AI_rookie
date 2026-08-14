# Hybrid 스모크 테스트 결과 (features=dump_hybrid_social_media)

| variant | Acc | macroF1 | FPR | FNR | n_test |
|---|---|---|---|---|---|
| attn | 0.922 | 0.915 | 0.0975 | 0.025 | 800 |
| hidden | 0.939 | 0.931 | 0.05 | 0.0325 | 800 |
| hybrid | 0.946 | 0.940 | 0.0325 | 0.0375 | 800 |

Δ macroF1 (hybrid − attn) = **+0.025**
→ hidden 결합이 attention 단독 대비 이득 있음 (본 실험 규모로 재검증 권장).