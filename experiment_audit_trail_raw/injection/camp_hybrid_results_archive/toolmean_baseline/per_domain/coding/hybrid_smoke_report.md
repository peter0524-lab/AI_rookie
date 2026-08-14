# Hybrid 스모크 테스트 결과 (features=dump_hybrid_coding)

| variant | Acc | macroF1 | FPR | FNR | n_test |
|---|---|---|---|---|---|
| attn | 0.900 | 0.887 | 0.1175 | 0.025 | 800 |
| hidden | 0.894 | 0.881 | 0.115 | 0.0375 | 800 |
| hybrid | 0.900 | 0.887 | 0.0775 | 0.0525 | 800 |

Δ macroF1 (hybrid − attn) = **-0.000**
→ 이 규모에선 뚜렷한 이득 없음 (표본이 작아 잡음일 수 있음, 본 실험 필요).