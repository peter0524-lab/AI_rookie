# Enc-lite 검증 — encode-before-pool이 g_mean(Avg-style) 대비 오르는가  (model=qwen, N=2400)

- 입력: g_prof을 (bins=10, LH=1152)로 취급, bin마다 LH→128 MLP 인코딩 후 bin 축 mean-pool → Linear→3
- device=cuda, epochs=200, lr=0.01

| feature | in-domain acc | macroF1 | MIS recall | cross meanF1 | worstF1 |
|---|---|---|---|---|---|
| g_mean (Avg-style, 기존 diag①) | 0.775 | 0.775 | 0.740 | 0.738 | 0.674 |
| Enc-lite (encode-before-pool) | 0.858 | 0.858 | 0.843 | 0.831 | 0.748 |
| hidden-state 최고 (기존 diag③, L9_last) | 0.942 | 0.942 | 0.948 | 0.929 | 0.913 |

## 판정 (자동)

- Δ macroF1 (Enc-lite − g_mean) = **+0.083**
→ encode-before-pool이 뚜렷하게 신호를 회복시킴. attention의 진짜 천장은 g_mean(0.775)보다 높다 → 정통 Enc-first(전체 토큰쌍) 재현으로 hidden(0.94)과 정식 비교할 가치 있음.

---
*참고: bins는 위치 프로파일 버킷(기본 10개)이며 논문의 실제 토큰쌍 수(샘플당 ~수천)보다 훨씬 성긴 근사다.*