# Injection 진단 리포트  (model=qwen, N=2400)

- 샘플 2400개 · 도메인 8개 · L=36 H=32 (head 1152개)
- 구성모드별: {'NI': 800, 'AL': 800, 'MIS-append': 400, 'MIS-replace': 400}
- 클래스(3): MIS=800 AL=800 NI=800

## 진단① — g(tool→user grounding)가 클래스를 가르는가

**head별 misaligned-vs-rest AUC** (0.5=무신호). 최상위 20개:

| rank | layer | head | AUC | 방향(g↑=MIS?) |
|---|---|---|---|---|
| 1 | 26 | 5 | 0.723 | 높음 |
| 2 | 17 | 20 | 0.714 | 높음 |
| 3 | 22 | 29 | 0.705 | 높음 |
| 4 | 22 | 19 | 0.704 | 높음 |
| 5 | 25 | 21 | 0.701 | 높음 |
| 6 | 27 | 27 | 0.694 | 높음 |
| 7 | 27 | 26 | 0.692 | 높음 |
| 8 | 22 | 30 | 0.691 | 높음 |
| 9 | 25 | 23 | 0.688 | 높음 |
| 10 | 9 | 0 | 0.688 | 높음 |
| 11 | 27 | 10 | 0.685 | 높음 |
| 12 | 20 | 25 | 0.680 | 높음 |
| 13 | 19 | 11 | 0.679 | 높음 |
| 14 | 34 | 8 | 0.675 | 높음 |
| 15 | 34 | 9 | 0.675 | 높음 |
| 16 | 15 | 30 | 0.674 | 높음 |
| 17 | 22 | 28 | 0.673 | 높음 |
| 18 | 26 | 6 | 0.670 | 높음 |
| 19 | 30 | 19 | 0.670 | 높음 |
| 20 | 27 | 20 | 0.670 | 높음 |

- 최고 단일 head AUC = **0.723** (|AUC-0.5|=0.223)
- |AUC-0.5|>0.10 인 head 수: **478 / 1152**
- |AUC-0.5|>0.15 인 head 수: **46 / 1152**

**전체 head g로 3-class 로지스틱 회귀** (신호가 head들에 흩어져 있는가):

| feature | in-domain acc | macroF1 | MIS recall | cross-domain meanF1 | worstF1 |
|---|---|---|---|---|---|
| g_mean (LH) | 0.775 | 0.775 | 0.740 | 0.738 | 0.674 |
| g_mean+std+max (3·LH) | 0.755 | 0.755 | 0.715 | 0.739 | 0.697 |

## 진단② — grounding의 부호와 위치(주입 스팬)

**상위 판별 head 평균 g의 구성모드별 분포** (부호 확인):

| 구성모드 | mean g | std |
|---|---|---|
| NI | +0.0280 | 0.0139 |
| AL | +0.0262 | 0.0114 |
| MIS-append | +0.0300 | 0.0127 |
| MIS-replace | +0.0520 | 0.0233 |

- AL vs MIS-append  Cohen's d = **-0.316**  (양수=AL이 grounding 높음=내 가정과 일치)
- AL vs MIS-replace Cohen's d = **-1.574**

![위치 프로파일](g_position_profile.png)

→ **g_position_profile.png**: MIS-append의 tail(오른쪽)이 AL보다 내려가면 '주입 스팬이 grounding을 끊는다'는 가정 지지.

![head AUC](head_auc.png)

## 진단③ — hidden-state 프로브 바닥선 (attention이 넘어야 할 선)

| feature | in-domain acc | macroF1 | MIS recall | cross meanF1 | worstF1 |
|---|---|---|---|---|---|
| hidden L9_toolmean | 0.912 | 0.913 | 0.892 | 0.896 | 0.842 |
| hidden L9_last | 0.942 | 0.942 | 0.948 | 0.929 | 0.913 |
| hidden L18_toolmean | 0.923 | 0.924 | 0.902 | 0.896 | 0.868 |
| hidden L18_last | 0.934 | 0.934 | 0.935 | 0.930 | 0.917 |
| hidden L27_toolmean | 0.913 | 0.913 | 0.890 | 0.861 | 0.809 |
| hidden L27_last | 0.877 | 0.878 | 0.886 | 0.860 | 0.793 |
| hidden L36_toolmean | 0.866 | 0.866 | 0.850 | 0.813 | 0.773 |
| hidden L36_last | 0.818 | 0.819 | 0.841 | 0.793 | 0.741 |

## 종합 판정 (자동 요약)

1. **g 신호 존재?** 최고 head |AUC-0.5|=0.223 (AUC 0.723, g↑=MIS), |AUC-.5|>0.15 head 46개 → 있음 (attention-g에 신호)
2. **부호 가정?** AL vs MIS-append d=-0.316 → 반대 부호!
3. **hidden-state 대비?** g best macroF1=0.775 (cross 0.738) vs hidden best=0.942@L9_last (cross 0.929)
   → hidden-state가 g를 유의하게 앞섬. **attention 접고 hidden-state 선회 검토.**

---
*주의: 추출 forward 비용은 attention/hidden 유사. 여기 결론은 '신호 존재/부호/상대우열'까지다.*