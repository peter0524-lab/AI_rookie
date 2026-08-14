# Hybrid 스모크 테스트 결과 (features=dump_hybrid_coding)

| variant | Acc | macroF1 | FPR | FNR | n_test |
|---|---|---|---|---|---|
| attn | 0.895 | 0.880 | 0.11 | 0.0375 | 800 |
| hidden | 0.902 | 0.889 | 0.0825 | 0.0425 | 800 |
| hybrid | 0.889 | 0.873 | 0.1425 | 0.0175 | 800 |

Δ macroF1 (hybrid − attn) = **-0.007**
→ 이 규모에선 뚜렷한 이득 없음 (표본이 작아 잡음일 수 있음, 본 실험 필요).