"""공용 유틸 — 진단 스크립트가 공유하는 메시지 구성 / 세그먼트 식별 / 모델 로딩.

alignsentinel_replicate/src/extract_features.py 의 로직을 그대로 재사용한다:
입력은 (system, user, tool_response) 이고, attention/hidden state를 뽑을 때
tool_response 토큰 구간(x)과 user_prompt 토큰 구간(s)을 offset mapping으로 특정한다.
이 진단은 논문/기존 파이프라인과 동일하게 **user↔tool 상호작용만** 사용한다(system 배제).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from models_config import resolve as resolve_model  # noqa: E402

# 라벨 → 정수 (extract_features.py와 동일)
LABEL_TO_ID = {"misaligned": 0, "aligned": 1, "non_instruction": 2}
ID_TO_LABEL = {v: k for k, v in LABEL_TO_ID.items()}
# construction_mode → 정수 (misaligned를 append/replace로 세분)
CMODE_TO_ID = {
    "non_instruction": 0,
    "aligned": 1,
    "misaligned_append": 2,
    "misaligned_replace": 3,
}
ID_TO_CMODE = {v: k for k, v in CMODE_TO_ID.items()}

TOOL_RESPONSE_TEMPLATE = "<tool_response>\n{content}\n</tool_response>"


def build_messages(record: dict, mode: str) -> list[dict]:
    """tool_msg_mode에 맞춰 chat 메시지 구성 (extract_features.build_messages와 동일)."""
    wrapped = TOOL_RESPONSE_TEMPLATE.format(content=record["tool_response"])
    system = {"role": "system", "content": record["system_prompt"]}
    if mode == "merged":
        return [system, {"role": "user", "content": record["user_prompt"] + "\n\n" + wrapped}]
    return [system,
            {"role": "user", "content": record["user_prompt"]},
            {"role": "user", "content": wrapped}]


def char_span_to_token_indices(offsets, start: int, end: int) -> list[int]:
    idx = []
    for i, (a, b) in enumerate(offsets):
        if a == b:  # special token
            continue
        if a < end and b > start:
            idx.append(i)
    return idx


def locate_spans(text: str, user_prompt: str, tool_response: str):
    u_start = text.find(user_prompt)
    if u_start < 0:
        raise ValueError("user_prompt를 템플릿 문자열에서 찾지 못함")
    u_end = u_start + len(user_prompt)
    x_start = text.find(tool_response, u_end)
    if x_start < 0:
        raise ValueError("tool_response를 템플릿 문자열에서 찾지 못함")
    return (u_start, u_end), (x_start, x_start + len(tool_response))


def resolve_model_args(model_key: str | None, model: str | None, trust_remote_code: bool):
    cfg = resolve_model(model_key) if model_key else None
    if cfg:
        if model is None:
            model = cfg["hf_id"]
        if not trust_remote_code:
            trust_remote_code = cfg["trust_remote_code"]
    if model is None:
        model = "Qwen/Qwen3-8B"
    return model, trust_remote_code


def load_model_and_tokenizer(model_id: str, dtype: str, device: str, trust_remote_code: bool):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    print(f"loading {model_id} (attn=eager, dtype={dtype}, trust_remote_code={trust_remote_code})")
    tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=trust_remote_code)
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=getattr(torch, dtype),
        attn_implementation="eager",  # output_attentions에 필수
        device_map=device,
        trust_remote_code=trust_remote_code,
    )
    model.eval()
    return model, tokenizer


def make_apply_template(tokenizer):
    def apply_template(messages):
        try:
            return tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=False, enable_thinking=False)
        except TypeError:
            return tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)
    return apply_template


def resolve_tool_msg_mode(mode: str, apply_template, probe_record: dict) -> str:
    """auto면 chat template이 연속 user 메시지를 허용하는지 1회 probe."""
    if mode != "auto":
        return mode
    try:
        apply_template(build_messages(probe_record, "separate"))
        print("[auto] 연속 user 메시지 허용 → separate 모드(논문식)")
        return "separate"
    except Exception as e:  # noqa: BLE001
        print(f"[auto] separate 렌더 실패({type(e).__name__}) → merged 폴백")
        return "merged"


def load_records(paths) -> list[dict]:
    records = []
    for path in paths:
        with open(path, "r", encoding="utf-8") as f:
            records.extend(json.load(f))
    return records
