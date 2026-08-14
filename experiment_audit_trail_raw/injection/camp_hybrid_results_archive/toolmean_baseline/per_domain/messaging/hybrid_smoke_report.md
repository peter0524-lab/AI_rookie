# Hybrid 스모크 테스트 결과 (features=dump_hybrid_messaging)

| variant | Acc | macroF1 | FPR | FNR | n_test |
|---|---|---|---|---|---|
| attn | 0.907 | 0.898 | 0.0475 | 0.0725 | 800 |
| hidden | 0.905 | 0.894 | 0.0075 | 0.0975 | 800 |
| hybrid | 0.881 | 0.867 | 0.0325 | 0.095 | 800 |

Δ macroF1 (hybrid − attn) = **-0.031**
→ 이 규모에선 뚜렷한 이득 없음 (표본이 작아 잡음일 수 있음, 본 실험 필요).