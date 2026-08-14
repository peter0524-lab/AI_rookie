#!/usr/bin/env bash
# 환경 변수 (Hugging Face 인증 등). run_*.sh들이 실행 시 자동으로 source 한다.
#
# 보안: 실제 HF 액세스 토큰은 저장소에 커밋하지 않는다.
# 필요하면 실행 환경에서 HF_TOKEN을 export 하거나 .env를 별도로 관리한다.
#
# transformers/huggingface_hub는 HF_TOKEN 환경변수를 자동으로 읽어 gated 모델
# (exaone, exaone-1.2b, mistral, llama, Prompt-Guard-2)을 인증한다. 별도 로그인 불필요.
# 단, 각 gated 모델 페이지에서 계정으로 "라이선스 동의"는 한 번 눌러둬야 한다.

export HF_TOKEN="${HF_TOKEN:-}"
export HUGGING_FACE_HUB_TOKEN="$HF_TOKEN"   # 구버전 라이브러리 호환

# 모델은 이 서버에선 hwan 계정 캐시에 이미 받아져 있으므로 그걸 그대로 사용
export HF_HOME="/home/tta/team/hwan/.cache/huggingface"
