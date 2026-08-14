"""
AlignSentinel 재현 — 1단계: attention 특징 추출 (indirect prompt injection).

논문 §4.2: backend LLM에 (system prompt, user prompt, tool response)를 넣고,
tool response 토큰(x)이 user prompt 토큰(s, 상위 우선순위 지시)을 바라보는
attention A ∈ R^{L×H×|x|×|s|} 를 추출한다. 이를 토큰쌍 상호작용 벡터
z_ij ∈ R^{L·H} 들로 재구성해 두 변형의 입력을 만든다:

  - Avg-first 용: 전체 토큰쌍 평균 벡터  z̄ ∈ R^{L·H}      → {split}_{domain}_avg.npy   (N, L·H) fp32
  - Enc-first 용: 토큰쌍 벡터들의 서브샘플(K개)             → {split}_{domain}_pairs.npy (N, K, L·H) fp16

tool response 삽입 방식은 기본적으로 논문(Qwen-Agent 관례)을 따라
<tool_response>...</tool_response>로 감싼 별도 user 메시지로 넣는다. 단, Mistral처럼
연속 user 메시지를 허용하지 않는 chat template에서는 같은 user 메시지 뒤에 이어 붙인다.

메모리 주의: 전체 토큰쌍을 다 저장하면 수백 GB가 되므로(§README 편차 D2),
Enc-first용으로는 토큰쌍을 균등 무작위 K개(기본 1024)로 서브샘플해 저장한다.
Avg-first의 평균은 서브샘플이 아니라 **전체** 토큰쌍에서 계산한다.

실행 (A100 서버):
  python src/extract_features.py \
      --data data/full_train.json data/full_test.json \
      --out features --model skt/A.X-4.0-Light --max-pairs 1024
"""

from __future__ import annotations

import argparse
import json
import time
from collections import defaultdict
from pathlib import Path

import numpy as np

LABEL_TO_ID = {"misaligned": 0, "aligned": 1, "non_instruction": 2}
TOOL_RESPONSE_TEMPLATE = "<tool_response>\n{content}\n</tool_response>"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--data", nargs="+", required=True, help="full_train.json full_test.json")
    p.add_argument("--out", default="features")
    p.add_argument("--model", default="skt/A.X-4.0-Light")
    p.add_argument("--model-label", default=None,
                   help="로컬 snapshot 경로로 로드할 때 결과/메타에 기록할 원래 backend 모델 id")
    p.add_argument("--trust-remote-code", action="store_true",
                   help="EXAONE 등 custom model code가 필요한 HF 모델을 로드할 때 사용")
    p.add_argument("--tool-message-mode", default="auto", choices=["auto", "separate", "append"],
                   help="tool response 삽입 방식: 별도 user 메시지, user prompt 뒤 append, 또는 모델별 자동")
    p.add_argument("--max-pairs", type=int, default=1024,
                   help="Enc-first용으로 저장할 토큰쌍 수 (0=전체 저장, 저장량 주의)")
    p.add_argument("--max-seq-len", type=int, default=4096)
    p.add_argument("--dtype", default="bfloat16", choices=["bfloat16", "float16", "float32"])
    p.add_argument("--device", default="cuda")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--limit-per-group", type=int, default=None, help="디버그용: (split,domain)별 샘플 수 제한")
    p.add_argument("--domains", nargs="*", default=None, help="지정 시 해당 도메인만 추출")
    return p.parse_args()


def char_span_to_token_indices(offsets: list[tuple[int, int]], start: int, end: int) -> list[int]:
    """오프셋 매핑에서 [start, end) 문자 구간과 겹치는 토큰 인덱스를 반환."""
    idx = []
    for i, (a, b) in enumerate(offsets):
        if a == b:  # special token
            continue
        if a < end and b > start:
            idx.append(i)
    return idx


def locate_spans(text: str, user_prompt: str, tool_response: str) -> tuple[tuple[int, int], tuple[int, int]]:
    """chat template 적용 문자열에서 user_prompt / tool_response 내용의 문자 구간을 찾는다.

    템플릿은 내용을 원문 그대로 삽입하므로 부분 문자열 탐색으로 충분하다.
    user_prompt를 먼저 찾고, tool_response는 그 뒤에서 찾는다(중복 대비).
    """
    u_start = text.find(user_prompt)
    if u_start < 0:
        raise ValueError("user_prompt를 템플릿 문자열에서 찾지 못함")
    u_end = u_start + len(user_prompt)
    x_start = text.find(tool_response, u_end)
    if x_start < 0:
        raise ValueError("tool_response를 템플릿 문자열에서 찾지 못함")
    return (u_start, u_end), (x_start, x_start + len(tool_response))


def append_tool_response_by_default(model_id: str) -> bool:
    """연속 user role을 엄격히 막는 chat template 계열만 append 모드를 기본값으로 둔다."""
    model_id = model_id.lower()
    return "mistral" in model_id


def build_messages(record: dict, append_tool_response: bool) -> list[dict[str, str]]:
    tool_message = TOOL_RESPONSE_TEMPLATE.format(content=record["tool_response"])
    if append_tool_response:
        user_content = f"{record['user_prompt']}\n\n{tool_message}"
        return [
            {"role": "system", "content": record["system_prompt"]},
            {"role": "user", "content": user_content},
        ]
    return [
        {"role": "system", "content": record["system_prompt"]},
        {"role": "user", "content": record["user_prompt"]},
        {"role": "user", "content": tool_message},
    ]


def render_chat(tokenizer, messages: list[dict[str, str]]) -> str:
    try:
        return tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=False, enable_thinking=False
        )
    except TypeError:  # 템플릿이 enable_thinking 미지원인 경우
        return tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)


def main() -> None:
    args = parse_args()
    import torch
    from tqdm import tqdm
    from transformers import AutoModelForCausalLM, AutoTokenizer

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(args.seed)

    model_label = args.model_label or args.model
    print(f"loading {args.model} (label={model_label}, attn_implementation=eager, dtype={args.dtype})")
    tokenizer = AutoTokenizer.from_pretrained(args.model, trust_remote_code=args.trust_remote_code)
    model = AutoModelForCausalLM.from_pretrained(
        args.model,
        torch_dtype=getattr(torch, args.dtype),
        attn_implementation="eager",  # output_attentions에 필요 (sdpa/flash는 attention을 반환하지 않음)
        device_map=args.device,
        trust_remote_code=args.trust_remote_code,
    )
    model.eval()
    L = model.config.num_hidden_layers
    H = model.config.num_attention_heads
    LH = L * H
    print(f"L={L} H={H} → feature dim {LH}")

    # (split, domain) 별로 그룹핑
    records = []
    for path in args.data:
        with open(path, "r", encoding="utf-8") as f:
            records.extend(json.load(f))
    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for r in records:
        if args.domains and r["domain"] not in args.domains:
            continue
        groups[(r["split"], r["domain"])].append(r)

    for (split, domain), recs in sorted(groups.items()):
        if args.limit_per_group:
            recs = recs[: args.limit_per_group]
        meta_path = out_dir / f"{split}_{domain}_meta.json"
        if meta_path.exists():
            print(f"[skip] {split}/{domain} — meta 존재 (재실행하려면 features/ 파일 삭제)")
            continue
        n = len(recs)
        K = args.max_pairs
        avg_arr = np.zeros((n, LH), dtype=np.float32)
        pairs_path = out_dir / f"{split}_{domain}_pairs.npy"
        pairs_arr = None
        if K > 0:
            pairs_arr = np.lib.format.open_memmap(pairs_path, mode="w+", dtype=np.float16, shape=(n, K, LH))
        meta: dict = {"model": model_label, "model_load_path": args.model,
                      "L": L, "H": H, "max_pairs": K,
                      "tool_message_mode": args.tool_message_mode,
                      "ids": [], "labels": [], "agent_ids": [], "n_pairs_original": [], "skipped": []}

        t0 = time.time()
        row = 0  # skip된 샘플과 배열 행이 어긋나지 않도록 성공한 샘플만 카운트
        append_tool_response = (
            args.tool_message_mode == "append"
            or (args.tool_message_mode == "auto" and append_tool_response_by_default(args.model))
        )
        for r in tqdm(recs, desc=f"{split}/{domain}"):
            messages = build_messages(r, append_tool_response)
            try:
                text = render_chat(tokenizer, messages)
            except Exception:
                if args.tool_message_mode != "auto" or append_tool_response:
                    raise
                append_tool_response = True
                text = render_chat(tokenizer, build_messages(r, append_tool_response))

            (u_a, u_b), (x_a, x_b) = locate_spans(text, r["user_prompt"], r["tool_response"])
            enc = tokenizer(text, return_offsets_mapping=True, return_tensors="pt",
                            truncation=True, max_length=args.max_seq_len, add_special_tokens=False)
            offsets = enc.pop("offset_mapping")[0].tolist()
            s_idx = char_span_to_token_indices(offsets, u_a, u_b)
            x_idx = char_span_to_token_indices(offsets, x_a, x_b)
            if not s_idx or not x_idx:
                meta["skipped"].append(r["id"])
                continue

            enc = {k: v.to(model.device) for k, v in enc.items()}
            with torch.no_grad():
                outputs = model(**enc, output_attentions=True, use_cache=False)

            s_t = torch.tensor(s_idx, device=model.device)
            x_t = torch.tensor(x_idx, device=model.device)
            # 레이어별 (1,H,T,T) → x행/s열 블록 (H,|x|,|s|) 를 뽑아 (L,H,|x|,|s|)로 적층
            blocks = []
            for att in outputs.attentions:
                blk = att[0].index_select(1, x_t).index_select(2, s_t)  # (H,|x|,|s|)
                blocks.append(blk.float())
            A = torch.stack(blocks, dim=0)  # (L,H,|x|,|s|)
            del outputs

            avg_arr[row] = A.mean(dim=(2, 3)).flatten().cpu().numpy()  # 전체 토큰쌍 평균 (논문 Avg-first)

            if pairs_arr is not None:
                Z = A.permute(2, 3, 0, 1).reshape(-1, LH)  # (P, L·H), P=|x|·|s|
                P = Z.shape[0]
                sel = rng.choice(P, size=K, replace=(P < K))
                pairs_arr[row] = Z[torch.tensor(np.sort(sel), device=Z.device)].cpu().numpy().astype(np.float16)
                meta["n_pairs_original"].append(int(P))
            del A

            meta["ids"].append(r["id"])
            meta["labels"].append(LABEL_TO_ID[r["label"]])
            meta["agent_ids"].append(r["agent_id"])
            row += 1

        np.save(out_dir / f"{split}_{domain}_avg.npy", avg_arr[: len(meta["ids"])])
        if pairs_arr is not None:
            pairs_arr.flush()
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False)
        print(f"[done] {split}/{domain}: {len(meta['ids'])}/{n} in {time.time()-t0:.0f}s "
              f"(skipped {len(meta['skipped'])})")


if __name__ == "__main__":
    main()
