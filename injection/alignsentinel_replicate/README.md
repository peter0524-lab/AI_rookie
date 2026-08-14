# AlignSentinel 재현 (indirect prompt injection, 한국어 벤치마크)

논문 *AlignSentinel: Alignment-Aware Detection of Prompt Injection Attacks* (Jia et al., arXiv:2602.13597)의
**indirect prompt injection 파트**를 자체 구축한 한국어 벤치마크(`data/`, 16,000건)로 재현하는 패키지.
A100 + **skt/A.X-4.0-Light** 기준. 기존 `results/`는 Qwen3-8B로 실행한 참고 결과다.

## 폴더 구성

```
data/                  한국어 indirect 벤치마크 (injection_dataset/coding_v2/final 복사본)
  full_train.json      12,800건 (도메인별 agent 8개)
  full_test.json        3,200건 (도메인별 agent 2개 — 학습에서 못 본 agent)
src/
  extract_features.py  [1단계] A.X 4.0 Light attention 특징 추출 (논문 §4.2)
  train_detector.py    [2·3단계] Avg-first/Enc-first 학습+평가 (논문 Table 5·8)
  aggregate_results.py 결과 집계 → results/summary.md (논문 Table 1b 대응 표)
  baselines/
    baseline_chen.py         Chen et al. 방식: klue/roberta 이진 파인튜닝
    baseline_promptguard.py  Prompt-Guard-2-86M zero-shot
scripts/run_all.sh     전체 파이프라인 일괄 실행
features/ models/ results/   (실행 시 생성)
```

## 논문 ↔ 구현 대응

| 논문 | 구현 |
|---|---|
| 입력 x = tool response, 상위 지시 s = user prompt (indirect) | 레코드의 `tool_response` / `user_prompt` |
| tool response를 `<tool_response>...</tool_response>`로 감싼 별도 user 메시지로 삽입 (Qwen-Agent 관례) | `extract_features.py`의 메시지 구성 동일 |
| attention A ∈ R^{L×H×\|x\|×\|s\|} → 토큰쌍 벡터 z_ij ∈ R^{L·H} | eager attention으로 전 레이어 추출, offset mapping으로 토큰 구간 식별. 특징 차원은 선택한 backend LLM의 L×H로 자동 결정 |
| Avg-first: 전 토큰쌍 평균 → Linear(L·H→128)-ReLU-Linear(128→3) | `train_detector.py --variant avg` (Table 5 그대로) |
| Enc-first: 쌍별 인코딩(L·H→128→128) → mean pool → 분류기(128→128→3) | `train_detector.py --variant enc` (Table 8 그대로) |
| 200 epochs, lr 0.01, batch 32(avg)/16(enc) | 기본값 동일 |
| 도메인별 detector, agent 8:2 train/test | 데이터의 `split` 필드가 이미 agent 단위 8:2 |
| 지표: 3-class Acc + FPR/FNR (misaligned=positive) | `metrics_from_preds` 동일 정의 |
| Cross-domain generalization (Table 3): 도메인 그룹 A↔B 교차 학습/평가 | `train_detector.py --cross A2B/B2A`. A={coding, cloud, project, shopping}, B={finance, messaging, social_media, web} (논문과 공통인 coding·shopping→A, messaging·social_media·web→B). 학습·평가 도메인이 겹치지 않으므로 각 도메인 전체 2,000건 사용 |
| (추가 실험) 8개 도메인 통합 detector | `train_detector.py --pooled`: 전체 train split 12,800건으로 하나 학습 → 전체 test 3,200건 평가, 결과에 도메인별 분해 포함. 논문에는 없는 우리 추가 설정 |
| 베이스라인: Chen et al.(DeBERTa 파인튜닝), Prompt-Guard-2 | 한국어라 인코더만 klue/roberta-base로 교체 / PG2는 다국어(mDeBERTa)라 그대로 |

## 논문과의 의도적 차이 (편차 목록)

- **D1 — 범위**: indirect만 재현 (direct 파트는 데이터셋에 의도적으로 없음). 언어는 한국어, 데이터 생성기는 GPT-4o 대신 Solar Pro3+EXAONE 검수, 규모는 agent당 200건(논문 400건, 비율 2:1:1 동일).
- **D2 — Enc-first 토큰쌍 서브샘플링**: 전체 토큰쌍(평균 ~7천 쌍/샘플)을 다 저장하면 수백 GB라, 샘플당 균등 무작위 **1,024쌍**을 fp16으로 저장해 학습(`--max-pairs`, 총 ~38GB). 평균 추정이므로 통계적 영향은 미미. Avg-first의 평균은 **전체 쌍**에서 계산(서브샘플 아님).
- **D3 — 옵티마이저**: 논문 미명시 → Adam 사용.
- **D4 — Chen et al. 인코더**: DeBERTa-v3-base(영어) → klue/roberta-base(한국어).
- **D5 — Backend LLM**: Qwen3-8B → `skt/A.X-4.0-Light`(국산 7B 한국어 특화 모델). A.X 4.0 Light는 Qwen2.5 기반이라 현재 attention 추출 코드와 호환성이 높은 편이다.
- 도메인 구성 차이: 논문의 Entertainment/Language/Teaching 대신 finance/cloud/project (우리 벤치마크 구성).

## 서버로 옮기기 (Windows → A100 서버)

```bash
# Git Bash 등에서 (USER/HOST는 실제 값으로):
scp -r "C:/Users/TH/Desktop/HY/4-1/ai_rookie/alignsentinel_replicate" USER@HOST:~/
# rsync가 있으면 (재전송에 유리):
rsync -avz --progress "C:/Users/TH/Desktop/HY/4-1/ai_rookie/alignsentinel_replicate" USER@HOST:~/
```

## 서버에서 실행

```bash
cd ~/alignsentinel_replicate

# 1) 환경 (conda 예시 — venv도 무방)
conda create -n asrep python=3.11 -y && conda activate asrep
pip install -r requirements.txt        # CUDA torch가 필요하면: pip install torch --index-url https://download.pytorch.org/whl/cu121

# 2) Hugging Face 로그인 (Prompt-Guard-2가 gated — 모델 페이지에서 사전 접근 승인 필요.
#    skt/A.X-4.0-Light, klue/roberta-base는 공개라 로그인 없이도 됨)
huggingface-cli login

# 3) 전체 실행
bash scripts/run_all.sh

# 결과 확인
cat results/summary.md
```

### 4개 backend LLM sweep + custom detector

국산/국내 후보 backend를 같은 조건으로 비교하려면 sweep 스크립트를 쓴다. 기본 후보는
`skt/A.X-4.0-Light`, `LGAI-EXAONE/EXAONE-Deep-7.8B`,
`NCSOFT/Llama-VARCO-8B-Instruct`, `upstage/SOLAR-10.7B-Instruct-v1.0`이다.
Upstage SOLAR는 10.7B라 7~8B 범위 밖이지만 국내 강한 후보라 비교군으로 포함했다.
KT Mi:dm은 현재 공개 주력 모델이 2B/12B라 기본 7~8B 비교군에서는 제외했다.

```bash
# 먼저 smoke test: 각 split/domain 4건만 추출하고 3 epoch만 학습
LIMIT_PER_GROUP=4 EPOCHS=3 MAX_PAIRS=128 bash scripts/run_model_sweep.sh

# 전체 sweep: 모델별 features/results/models를 분리해 저장
bash scripts/run_model_sweep.sh

# 후보를 직접 지정하고 싶을 때
MODEL_IDS_TEXT="skt/A.X-4.0-Light NCSOFT/Llama-VARCO-8B-Instruct" \
  bash scripts/run_model_sweep.sh
```

기본 detector는 `regularized`다. 논문 원형 detector로 비교하려면:

```bash
DETECTOR=paper bash scripts/run_model_sweep.sh
```

결과는 모델별로 `results/{model_slug}_regularized/summary.md`에 저장된다. 전체 4개를 기본
`--max-pairs 1024`로 돌리면 attention feature만 대략 4배로 커지므로 디스크를 넉넉히 잡는다.

## 결과물 가져오기 (서버 → 로컬)

`results/summary.md` 하나에 상세 리포트가 전부 담긴다 (도메인별/pooled/cross 표 + 논문 참조 수치,
confusion matrix 전체, 클래스별 precision/recall/F1, **오분류 샘플 목록에 원문 스니펫 포함**,
베이스라인 상세, 특징 추출 통계). 보통 이 파일 하나만 받으면 분석에 충분하다:

```bash
scp USER@HOST:~/alignsentinel_replicate/results/summary.md .
# 원본 수치까지 전부 (기계용 통합 json 포함, 몇 MB 수준):
scp -r USER@HOST:~/alignsentinel_replicate/results .
# 학습된 MLP 가중치까지 (수십 MB):
scp -r USER@HOST:~/alignsentinel_replicate/models .
```

### 개별 실행 / 부분 재실행

```bash
# 특징 추출만 (이미 추출된 도메인은 자동 skip; 다시 하려면 features/의 해당 파일 삭제)
python src/extract_features.py --data data/full_train.json data/full_test.json \
    --out features --model skt/A.X-4.0-Light --max-pairs 1024
# 특정 도메인만: --domains coding web / 소규모 동작 확인: --limit-per-group 20

python src/train_detector.py --features features --variant avg --domains all
python src/train_detector.py --features features --variant enc --domains all
python src/train_detector.py --features features --variant enc --pooled \
    --detector regularized --standardize --class-weights
# pooled (8개 도메인 통합): run_all.sh에 포함돼 있음
python src/train_detector.py --features features --variant avg --pooled
python src/train_detector.py --features features --variant enc --pooled
# cross-domain (논문 Table 3): run_all.sh에 포함돼 있음
python src/train_detector.py --features features --variant avg --cross A2B
python src/train_detector.py --features features --variant enc --cross A2B
python src/train_detector.py --features features --variant avg --cross B2A
python src/train_detector.py --features features --variant enc --cross B2A
python src/baselines/baseline_chen.py
python src/baselines/baseline_promptguard.py
python src/aggregate_results.py
```

## 예상 소요 (A100 80GB 기준)

| 단계 | 예상 |
|---|---|
| 특징 추출 (16,000 forward, eager attention) | 1.5~3시간, features/ 디스크 ~40GB |
| Avg/Enc 학습 (8도메인 × 2변형, 200ep) | 수십 분 |
| Chen 베이스라인 (8도메인 파인튜닝 3ep) | ~20분 |
| Prompt-Guard-2 (추론만) | 수 분 |

## 판정 기준 (무엇이 나오면 재현 성공인가)

논문 Table 1b/11b/12b(indirect, Qwen3-8B)은 참고 기준이며, 현재 기본 backend는 `skt/A.X-4.0-Light`다:
- **Ours 두 변형**: FPR·FNR ≈ 0.00~0.01, 3-class Acc ≥ 0.92 (Enc ≥ 0.96) 수준이면 재현 성공.
  잔여 오류가 aligned↔non_instruction 혼동에 몰려 있으면 논문 관찰과도 일치.
- **Prompt-Guard-2**: FNR이 매우 높게(0.7+) 나와야 논문 관찰(이진 탐지기의 한계) 재현.
- **Chen et al.**: Ours보다 나쁘지만 PG2보다는 나은 중간 성능이 논문 패턴.
- Enc-first ≥ Avg-first 경향 확인.
- **Cross-domain (Table 3)**: 처음 보는 도메인 그룹에서도 Acc 0.90+ (Enc-first가 우위, 논문은 A→B 0.94 / B→A 0.98)이면 일반화 재현 성공.

## 트러블슈팅

- `output_attentions` 오류 → `attn_implementation="eager"`가 필수 (코드에 이미 설정됨). transformers ≥ 4.51 권장.
- 추출 OOM → `--max-seq-len 3072`로 낮추기 (attention map은 시퀀스 길이 제곱으로 커짐).
- Prompt-Guard-2 401/403 → HF 모델 페이지에서 접근 신청 후 승인된 계정으로 login.
- GPU 없이 동작 확인 → `--limit-per-group 4`로 추출을 몇 샘플만 돌려 shape 확인 가능(느림).
