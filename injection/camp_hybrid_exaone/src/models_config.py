"""
멀티모델 실험용 backend LLM 레지스트리.

각 모델을 짧은 key로 참조한다(예: --model-key llama). 모든 산출물은 이 key로
네임스페이스가 나뉜다: features/<key>/, models/<key>/, results/<key>/.

모델은 모두 Qwen3-8B와 비슷한 규모(~7~11B)로 골랐고, 벤치마크가 한국어라
한국어에 강한 모델(EXAONE, A.X, VARCO)을 우선 포함했다. feature 차원(L·H)은
모델마다 다르지만(아래 approx_dim은 참고값), 코드가 config에서 L·H를 동적으로
읽으므로 하드코딩된 곳은 없다.

필드:
  hf_id             : Hugging Face repo id
  trust_remote_code : 커스텀 모델 코드가 필요한지 (EXAONE 등)
  gated             : HF에서 라이선스 동의 + huggingface-cli login 필요 여부
  approx_dim        : L*H 참고값(= attention feature 차원). 실제값은 실행 시 config에서 읽음
  note              : 비고
"""

from __future__ import annotations

MODELS: dict[str, dict] = {
    "qwen": {
        "hf_id": "Qwen/Qwen3-8B",
        "trust_remote_code": False,
        "gated": False,
        "approx_dim": 1152,   # L=36, H=32
        "note": "기준 모델(논문 재현 대상). Qwen3-8B.",
    },
    "exaone": {
        "hf_id": "LGAI-EXAONE/EXAONE-Deep-7.8B",
        "trust_remote_code": True,
        "gated": True,        # HF에서 EXAONE 라이선스 동의 필요
        "approx_dim": 1024,   # L=32, H=32 (approx)
        "note": "LG AI Research EXAONE-Deep 7.8B (이미 캐시된 모델 재사용). 한국어/영어. ~7.8B.",
    },
    "exaone-1.2b": {
        "hf_id": "LGAI-EXAONE/EXAONE-4.0-1.2B",
        "trust_remote_code": True,
        "gated": True,        # EXAONE 라이선스 동의 필요
        "approx_dim": 960,    # ~L=30, H=32 (approx) — 실제값은 config에서 읽음
        "note": "LG AI Research EXAONE 4.0 소형(1.2B). 소형이라 병렬 패킹에 유리. reasoning 모드는 enable_thinking=False로 끔.",
    },
    "mistral": {
        "hf_id": "mistralai/Mistral-7B-Instruct-v0.3",
        "trust_remote_code": False,
        "gated": True,
        "approx_dim": 1024,   # L=32, H=32 (approx)
        "note": "Mistral AI Mistral-7B-Instruct-v0.3 (이미 캐시된 모델 재사용). chat template이 연속 user 메시지를 금지할 수 있음 → tool-msg 자동 폴백 대상.",
    },
    "skt": {
        "hf_id": "skt/A.X-4.0-Light",
        "trust_remote_code": True,
        "gated": False,
        "approx_dim": 896,    # Qwen2.5-7B 계열 (approx)
        "note": "SKT A.X 4.0 Light. 한국어 특화. ~7B (Qwen2.5 기반).",
    },
    "solar": {
        "hf_id": "upstage/SOLAR-10.7B-Instruct-v1.0",
        "trust_remote_code": False,
        "gated": False,
        "approx_dim": 1536,   # L=48, H=32 (approx) — 레이어 많아 attention 추출 메모리 큼
        "note": "Upstage SOLAR. 10.7B(8B보다 약간 큼, 가장 근접한 공개 Solar). seq len 주의.",
    },
    "nc": {
        "hf_id": "NCSOFT/Llama-VARCO-8B-Instruct",
        "trust_remote_code": False,
        "gated": False,
        "approx_dim": 1024,   # Llama3-8B 기반: L=32, H=32
        "note": "NCSOFT VARCO. 한국어 특화. 8B (Llama3-8B 기반).",
    },
    "llama": {
        "hf_id": "meta-llama/Llama-3.1-8B-Instruct",
        "trust_remote_code": False,
        "gated": True,
        "approx_dim": 1024,   # L=32, H=32
        "note": "Meta Llama-3.1-8B-Instruct.",
    },
}

# run_all_models.sh 기본 실행 순서 (한국어 모델 → 나머지). 총 8개.
DEFAULT_ORDER = ["qwen", "exaone", "exaone-1.2b", "skt", "nc", "solar", "mistral", "llama"]


def resolve(key: str) -> dict:
    if key not in MODELS:
        raise KeyError(f"알 수 없는 model-key: {key!r}. 사용 가능: {list(MODELS)}")
    return MODELS[key]


if __name__ == "__main__":
    # `python src/models_config.py` 로 목록 확인
    import json
    print(json.dumps(MODELS, ensure_ascii=False, indent=2))
    print("\nDEFAULT_ORDER:", DEFAULT_ORDER)
