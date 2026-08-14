# injection_diag — AlignFocus 지반 진단

AlignFocus(attention `g` 기반 3-class 탐지) 설계에 **본격 착수하기 전**, 세 가지 전제를
서버에서 소규모로 실측하는 독립 패키지. "집을 예쁘게 짓기" 전에 "이 땅에 지반이 있나"를 먼저 판다.

## 무엇을 재는가

핵심 신호 `g[l,h,i] = Σ_{j∈user} attention(query=tool 토큰 i, key=user 토큰 j)`
= tool response 토큰 i가 상위 지시(user prompt)에 보낸 attention 비율(**grounding**). system은 안 씀.

- **진단① g가 3-class를 가르는가** — head별 misaligned-vs-rest AUC 랭킹 + 전체 head 로지스틱 회귀(in-domain / cross-domain).
- **진단② 부호·스팬** — MIS의 grounding이 AL보다 낮은가(가정) 높은가(반례: "위 지시 무시…"처럼 user를 오히려 더 참조)? 구성모드별 g 평균 + Cohen's d + 위치 프로파일(head→tail) 플롯.
- **진단③ hidden-state 바닥선** — 중간 레이어 hidden state 로지스틱 회귀. attention `g`가 이걸 못 이기면 attention 자체를 재고.

세 숫자로 φ를 몇 개 쓸지·attention을 유지할지·hidden-state로 선회할지가 관찰로 정해진다.

## 폴더

```
data/            full_train.json / full_test.json (복사본, 32,000건)
src/
  models_config.py   backend 레지스트리 (복사본)
  diag_common.py     메시지/세그먼트/모델 로딩 (extract_features.py 로직 재사용)
  diag_extract.py    [GPU] g 통계 + hidden state 덤프 → dump/
  diag_analyze.py    [CPU] 진단①②③ 계산 → results/diag_report.md + *.png
scripts/
  run_diag.sh        추출→분석 원커맨드
  setup_env.sh       HF_TOKEN (qwen은 불필요, gated 모델 쓸 때만)
dump/  results/      실행 시 생성
```

## 서버에서 실행

```bash
cd ~/injection_diag
conda create -n diag python=3.11 -y && conda activate diag
pip install -r requirements.txt        # CUDA torch 필요 시: pip install torch --index-url https://download.pytorch.org/whl/cu121

# 원커맨드 (기본: qwen, train split, 도메인당 라벨당 100개 ≈ 2,400 샘플)
CUDA_VISIBLE_DEVICES=0 bash scripts/run_diag.sh

# 결과
cat results/diag_report.md
#   results/g_position_profile.png , results/head_auc.png
```

옵션(환경변수):
```bash
PER_CLASS=200 bash scripts/run_diag.sh                 # 표본 늘리기(신뢰도↑, 느려짐)
DOMAINS="coding finance web" bash scripts/run_diag.sh  # 일부 도메인만(빠른 확인)
MODEL_KEY=llama bash scripts/run_diag.sh               # 다른 backend (gated면 setup_env.sh의 HF_TOKEN + 라이선스 동의 필요)
```

부분 실행:
```bash
python src/diag_extract.py --model-key qwen --splits train --per-class 100   # 추출만
python src/diag_analyze.py --dump dump --out results                          # 분석만(재실행 저렴)
```

## 규모/시간 (A100, qwen 기준, 대략)
- 추출 2,400 샘플 × (attention+hidden) forward ≈ 15~40분, `dump/` 수백 MB.
- 분석은 CPU 수 분. `dump/`만 로컬로 가져오면 분석은 로컬에서도 가능.

## 판정 가이드 (리포트 마지막 "종합 판정"이 자동 요약)
- 진단①: |AUC-0.5|>0.15 head가 여럿이고 최고 head AUC>0.65면 → g에 신호 있음.
- 진단②: AL vs MIS-append Cohen's d가 **양수**면 "주입이 grounding을 끊는다"는 가정 지지. **음수면 부호 가정 뒤집힘** → 축 정의 수정 필요.
- 진단③: hidden best macroF1이 g보다 +0.05 이상이면 → attention 접고 hidden-state 선회 검토. g가 cross-domain에서 앞서면 → 요약-불변성이 강점(유지 근거).

## 주의(과대주장 금지)
추출 forward 비용은 attention이든 hidden이든 유사하다. 이 진단이 답하는 건 **신호 존재/부호/상대우열**까지이고, 최종 방법의 우열은 본실험에서 가린다.
