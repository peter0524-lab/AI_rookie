# Hybrid 스모크 테스트 결과 (features=dump_hybrid_shopping)

| variant | Acc | macroF1 | FPR | FNR | n_test |
|---|---|---|---|---|---|
| attn | 0.929 | 0.918 | 0.025 | 0.05 | 800 |
| hidden | 0.901 | 0.890 | 0.0875 | 0.05 | 800 |
| hybrid | 0.902 | 0.896 | 0.165 | 0.0125 | 800 |

Δ macroF1 (hybrid − attn) = **-0.022**
→ 이 규모에선 뚜렷한 이득 없음 (표본이 작아 잡음일 수 있음, 본 실험 필요).