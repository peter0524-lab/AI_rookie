"""
DAPT 코퍼스 생성 — 한국어 위키피디아(완전 공개) → 문단 단위 텍스트

목적: SKT 0.1B(ModernBERT) 에 '세상지식(회사·인명 등)' 을 MLM 으로 주입하기
      위한 도메인 적응 사전학습(DAPT) 코퍼스를 만든다.

설계 / 안전장치:
  - 소스: HF `wikimedia/wikipedia` 의 한국어 스냅샷(공개, 인증 불필요).
          AI Hub(라벨 원본)와 완전히 다른 소스라 test 누수 위험 없음.
  - 정제: 문단 분리 후 길이/마크업 필터 → 노이즈 학습 방지.
  - 누수 방지: data/test.json / valid.json 문장과 (정규화 후) 겹치는 문단 제거.
  - 규모 상한(MAX_PARAGRAPHS)으로 파일럿용 가벼운 코퍼스 생성.

출력: dapt/dapt_corpus.txt  (문단당 1줄)

실행:
    # 파일럿(기본): 위키 한국어, 문단 상한 500k
    python3 dapt_prep.py
    # 규모/필터 조정
    MAX_PARAGRAPHS=800000 MIN_CHARS=40 python3 dapt_prep.py
    WIKI_CONFIG=20231101.ko python3 dapt_prep.py
"""

import json
import os
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
OUT_DIR  = BASE_DIR / "dapt"
OUT_DIR.mkdir(exist_ok=True)
OUT_PATH = OUT_DIR / os.environ.get("OUT_NAME", "dapt_corpus.txt")

WIKI_PATH      = os.environ.get("WIKI_PATH", "wikimedia/wikipedia")
WIKI_CONFIG    = os.environ.get("WIKI_CONFIG", "20231101.ko")
MAX_PARAGRAPHS = int(os.environ.get("MAX_PARAGRAPHS", "500000"))
MIN_CHARS      = int(os.environ.get("MIN_CHARS", "30"))
MAX_CHARS      = int(os.environ.get("MAX_CHARS", "1000"))

# 마크업/표/목록 잔재가 많은 문단을 걸러내기 위한 신호
_BULLET   = re.compile(r"^[\s>*#\-|=]")
_TABLEISH = re.compile(r"[|}{]{2,}")
_HANGUL   = re.compile(r"[가-힣]")


def _norm(s: str) -> str:
    """dedup 비교용 정규화 — 공백/문장부호 제거 후 비교."""
    return re.sub(r"\s+", "", re.sub(r"[^\w가-힣]", "", s)).lower()


def load_eval_norms() -> set[str]:
    """test/valid 문장의 정규화 집합 — 누수 차단용."""
    norms: set[str] = set()
    for name in ("test.json", "valid.json"):
        p = DATA_DIR / name
        if not p.exists():
            continue
        for ex in json.load(open(p, encoding="utf-8")):
            s = ex.get("sentence", "")
            if s:
                norms.add(_norm(s))
    return norms


def clean_paragraph(p: str) -> str | None:
    p = p.strip()
    if not (MIN_CHARS <= len(p) <= MAX_CHARS):
        return None
    if _BULLET.match(p) or _TABLEISH.search(p):
        return None
    # 한글 비율이 낮은 문단(수식/영문 나열 등) 제외
    hangul = len(_HANGUL.findall(p))
    if hangul < len(p) * 0.3:
        return None
    return p


def main():
    from datasets import load_dataset

    eval_norms = load_eval_norms()
    print(f"[dedup] test/valid 정규화 문장 {len(eval_norms):,}개 로드")
    print(f"[wiki ] {WIKI_PATH}:{WIKI_CONFIG} 스트리밍 로드...")

    ds = load_dataset(WIKI_PATH, WIKI_CONFIG, split="train", streaming=True)

    written = 0
    scanned = 0
    dropped_leak = 0
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        for row in ds:
            text = row.get("text", "")
            if not text:
                continue
            for para in text.split("\n"):
                scanned += 1
                cleaned = clean_paragraph(para)
                if cleaned is None:
                    continue
                if _norm(cleaned) in eval_norms:
                    dropped_leak += 1
                    continue
                f.write(cleaned.replace("\t", " ") + "\n")
                written += 1
                if written >= MAX_PARAGRAPHS:
                    break
            if written >= MAX_PARAGRAPHS:
                break

    print(f"[done ] 문단 스캔 {scanned:,} → 저장 {written:,}줄  (누수 제거 {dropped_leak})")
    print(f"        → {OUT_PATH}")


if __name__ == "__main__":
    main()
