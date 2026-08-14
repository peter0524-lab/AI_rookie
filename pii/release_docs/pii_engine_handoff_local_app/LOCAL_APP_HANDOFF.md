# 로컬 앱 배포용 PII 모델 전달 방식

## 결론

GPU 서버에서 실행시키는 모델이 아니라 사용자의 로컬 앱 안에서 쓰는 모델이면, 개발자에게는 체크포인트 원본이 아니라 **로컬 추론 엔진 번들**로 전달하는 것이 맞다.

권장 전달물:

```text
pii_skt_crf_gaz_local_app_seed44.tar.gz
```

압축을 풀면 아래 구조가 된다.

```text
pii_engine/
  manifest.json
  README_LOCAL_APP.md
  model/
    config.json
    model.safetensors 또는 pytorch_model.bin
    tokenizer.json
    tokenizer_config.json
    special_tokens_map.json
    label_map.json
    gazetteer.json
    backbone_config/config.json
  runtime/
    local_pii_inference.py
    pii_model.py
    crf_bio.py
    gazetteer.py
    requirements.txt
```

## 왜 이 형식이어야 하는가

이 모델은 단순 Hugging Face NER 모델이 아니다. `SKT A.X Encoder` 출력 위에 `gazetteer feature`를 붙이고, 마지막 예측을 `CRF`로 디코딩한다. 따라서 앱에는 weight만 넣으면 안 되고, gazetteer 생성/정렬 코드와 CRF decoding 코드가 같이 들어가야 한다.

또한 일반 사용자 PC에는 Hugging Face 캐시가 없을 수 있으므로 `backbone_config/config.json`을 번들에 포함해야 한다. 그래야 앱이 인터넷 없이도 모델 구조를 만들 수 있다.

## 앱 통합 방식

가장 안정적인 v1 방식은 Node/React 앱에서 Python sidecar를 한 번 띄워두고 JSON Lines로 통신하는 방식이다.

앱 시작 시:

```bash
cd pii_engine/runtime
python3 local_pii_inference.py --model-dir ../model --stdio
```

요청:

```json
{"id":"req-1","text":"홍길동 [PHONE_PLACEHOLDER]"}
```

응답:

```json
{"id":"req-1","entities":[{"form":"[PHONE_PLACEHOLDER]","label":"QT_MOBILE","begin":4,"end":17}]}
```

## 모델 생성 위치와 실행 위치

압축 번들은 체크포인트가 존재하는 머신에서 한 번 만들면 된다. 그 위치가 GPU 서버여도 괜찮다. 다만 최종 사용자는 GPU 서버를 쓰지 않고, 로컬 앱이 이 번들 안의 `runtime/local_pii_inference.py`를 실행한다.

## 패키징 명령

체크포인트가 있는 프로젝트 루트에서 실행:

```bash
bash pii_engine_handoff/package_pii_local_app_bundle.sh \
  models/skt_encoder_crf_gaz_mixed_natural/seed44 \
  pii_skt_crf_gaz_local_app_seed44.tar.gz
```

`seed44`가 최종 단일 모델이 아니면 해당 seed 디렉토리로 바꾸면 된다. `x3`는 앙상블 평가 결과이므로 로컬 앱 배포물로 넘기지 않는다.

## 배포 전 필수 smoke test

압축을 푼 뒤, 네트워크 없이 로드되는지 확인해야 한다.

```bash
tar -xzf pii_skt_crf_gaz_local_app_seed44.tar.gz
cd pii_engine/runtime
python3 -m pip install -r requirements.txt
TRANSFORMERS_OFFLINE=1 HF_HUB_OFFLINE=1 \
  python3 local_pii_inference.py \
  --model-dir ../model \
  --text "홍길동 [PHONE_PLACEHOLDER]"
```

이 테스트가 실패하면 일반 사용자 PC에서도 실패할 가능성이 높다. 특히 `skt/A.X-Encoder-base` 관련 파일을 찾지 못한다는 오류가 나면, backbone config 또는 remote-code 의존성이 번들에 빠진 것이다.

## 개발자에게 같이 말할 한 줄

“이 모델은 KDPII+clean synthetic mixed 데이터로 학습한 SKT A.X Encoder 기반 단일 PII detector이며, local Python sidecar에서 gazetteer feature와 CRF decoding을 같이 사용해야 합니다.”
