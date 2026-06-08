# -*- coding: utf-8 -*-
"""
실제 카카오톡 채팅 로그(CSV) → 기능 1·2·3 입력 JSON 변환 + 익명화 전처리기

카카오톡에서 내보낸 채팅 CSV(`timestamp, sender_id, message`)를 받아
기능 1·2 모델이 바로 추론할 수 있는 원문 입력 형식(`sample_chat_log_raw.json`)으로 변환한다.

수행하는 일:
  1. 한국식 timestamp("2025. 4. 7. 오후 4:58") → ISO 8601 KST("2025-04-07T16:58:00+09:00")
  2. placeholder 메시지("이모티콘", "사진", "사진 3장", "동영상", "삭제된 메시지입니다." 등) 제거
     - 문장이 아니라 모델에 넣으면 의미 없는 라벨이 나오므로 분석 대상에서 제외한다.
     - 부정/공격성 비율은 '실제 텍스트'에 대해서만 계산되므로 오히려 더 정확해진다.
  3. 본문 익명화(PII 마스킹): 전화번호·주민번호·이메일·링크·계좌/카드번호 등
     - sender_id는 원본이 이미 User_A~D로 가명화되어 있어 그대로 둔다(필요 시 --remap).

    cleaned_chat_log1.csv  ──→  python preprocess_chat_log.py  ──→  chat_log1_raw.json

사용 예:
    # 기본값: ../.데이터셋/cleaned_chat_log1.csv → ./chat_log1_raw.json
    python preprocess_chat_log.py

    # 입력/출력 직접 지정
    python preprocess_chat_log.py --input ../.데이터셋/cleaned_chat_log1.csv --output sample_chat_log_raw.json

    # placeholder도 남기고 싶을 때(참여량을 메시지 전수로 보고 싶은 경우)
    python preprocess_chat_log.py --keep-placeholders
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# 1) timestamp 변환 — 카카오톡 한국식 표기 → ISO 8601 (KST, UTC+9)
# ---------------------------------------------------------------------------
# 예: "2025. 4. 7. 오후 4:58"  /  "2025. 4. 10. 오전 11:50"
_TS_PATTERN = re.compile(
    r"^\s*(\d{4})\.\s*(\d{1,2})\.\s*(\d{1,2})\.\s*(오전|오후)\s*(\d{1,2}):(\d{2})\s*$"
)


def parse_kakao_timestamp(value: str) -> str:
    """
    '2025. 4. 7. 오후 4:58' → '2025-04-07T16:58:00+09:00'

    - 오전 12:xx → 00:xx (자정)
    - 오후 12:xx → 12:xx (정오)
    - 오후 1~11시 → +12시간
    """
    m = _TS_PATTERN.match(value)
    if not m:
        raise ValueError(f"인식할 수 없는 timestamp 형식입니다: {value!r}")

    year, month, day, ampm, hour, minute = m.groups()
    year, month, day, hour, minute = (int(year), int(month), int(day), int(hour), int(minute))

    if ampm == "오전":
        if hour == 12:  # 오전 12시 = 자정 00시
            hour = 0
    else:  # 오후
        if hour != 12:  # 오후 12시(정오)는 그대로, 1~11시는 +12
            hour += 12

    return f"{year:04d}-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:00+09:00"


# ---------------------------------------------------------------------------
# 2) placeholder 판별 — 문장이 아닌 시스템/미디어 표기
# ---------------------------------------------------------------------------
_PLACEHOLDER_EXACT = {
    "이모티콘",
    "사진",
    "동영상",
    "음성메시지",
    "보이스톡",
    "페이스톡",
    "삭제된 메시지입니다.",
    "삭제된 메시지입니다",
}
# "사진 3장", "사진 12장" 같은 묶음, "파일: xxx" 첨부
_PLACEHOLDER_PATTERNS = [
    re.compile(r"^사진\s*\d+\s*장$"),
    re.compile(r"^동영상\s*\d+\s*개$"),
    re.compile(r"^파일\s*:\s*.+$"),
    re.compile(r"^.+\.(jpg|jpeg|png|gif|mp4|mov|pdf|zip|hwp|docx?|pptx?|xlsx?)$", re.I),
]


def is_placeholder(text: str) -> bool:
    """미디어/시스템 표기처럼 모델 입력으로 부적절한 메시지인지 판별."""
    t = text.strip()
    if not t:
        return True
    if t in _PLACEHOLDER_EXACT:
        return True
    return any(p.match(t) for p in _PLACEHOLDER_PATTERNS)


# ---------------------------------------------------------------------------
# 3) 본문 익명화(PII 마스킹)
# ---------------------------------------------------------------------------
# 순서 중요: URL·이메일을 먼저 빼낸 뒤 숫자 계열을 처리한다.
_PII_RULES: list[tuple[re.Pattern[str], str]] = [
    # 링크
    (re.compile(r"https?://\S+", re.I), "[링크]"),
    (re.compile(r"\bwww\.\S+", re.I), "[링크]"),
    # 이메일
    (re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"), "[이메일]"),
    # 주민등록번호 (6자리-7자리, 뒤 첫자리 1~4)
    (re.compile(r"\b\d{6}[-\s]?[1-4]\d{6}\b"), "[주민번호]"),
    # 휴대폰 번호
    (re.compile(r"\b01[016789][-\s.]?\d{3,4}[-\s.]?\d{4}\b"), "[전화번호]"),
    # 일반 전화(지역번호 02/0xx)
    (re.compile(r"\b0\d{1,2}[-\s.]?\d{3,4}[-\s.]?\d{4}\b"), "[전화번호]"),
    # 계좌/카드 등: 연속 9자리 이상 숫자, 또는 하이픈으로 끊긴 계좌(총 9자리 이상)
    #   - 공백 구분은 단순 숫자 나열("30 15 5 1")을 오인하므로 제외한다.
    (re.compile(r"\b\d{9,}\b"), "[번호]"),
    (re.compile(r"\b\d{2,6}-\d{2,6}-\d{2,6}(?:-\d{1,6})?\b"), "[번호]"),
]


def anonymize_text(text: str) -> str:
    """본문에서 개인정보(전화·주민·이메일·링크·계좌번호 등)를 마스킹한다."""
    masked = text
    for pattern, repl in _PII_RULES:
        masked = pattern.sub(repl, masked)
    return masked


# ---------------------------------------------------------------------------
# 변환 파이프라인
# ---------------------------------------------------------------------------
def convert(
    rows: list[dict[str, str]],
    keep_placeholders: bool = False,
    sender_remap: dict[str, str] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    """
    CSV 행 목록 → 기능1·2 입력 메시지 목록.

    Returns:
        (messages, stats)
    """
    messages: list[dict[str, Any]] = []
    stats = {"total": len(rows), "placeholder_removed": 0, "masked": 0, "kept": 0}
    msg_id = 0

    for row in rows:
        raw_text = (row.get("message") or "").strip()

        if not keep_placeholders and is_placeholder(raw_text):
            stats["placeholder_removed"] += 1
            continue

        masked = anonymize_text(raw_text)
        if masked != raw_text:
            stats["masked"] += 1

        sender = (row.get("sender_id") or "").strip()
        if sender_remap:
            sender = sender_remap.get(sender, sender)

        msg_id += 1
        messages.append(
            {
                "message_id": msg_id,
                "sender_id": sender,
                "timestamp": parse_kakao_timestamp(row["timestamp"]),
                "text": masked,
            }
        )

    stats["kept"] = len(messages)
    return messages, stats


def main() -> None:
    here = Path(__file__).resolve().parent
    default_input = here.parent / ".데이터셋" / "cleaned_chat_log1.csv"
    # 데모용 sample_chat_log_raw.json 을 덮어쓰지 않도록 실데이터는 별도 파일로 출력한다.
    # 통합 노트북에서 실데이터를 돌리려면 이 파일을 sample_chat_log_raw.json 으로 복사/이름변경하면 된다.
    default_output = here / "chat_log1_raw.json"

    parser = argparse.ArgumentParser(
        description="카카오톡 채팅 CSV → 기능1·2 입력 JSON 변환 + 익명화"
    )
    parser.add_argument("--input", "-i", type=Path, default=default_input,
                        help=f"입력 CSV 경로 (기본: {default_input})")
    parser.add_argument("--output", "-o", type=Path, default=default_output,
                        help=f"출력 JSON 경로 (기본: {default_output})")
    parser.add_argument("--keep-placeholders", action="store_true",
                        help="이모티콘/사진 등 placeholder도 제거하지 않고 유지")
    args = parser.parse_args()

    if not args.input.exists():
        print(f"[Error] 입력 파일이 없습니다: {args.input}")
        sys.exit(1)

    # 카카오톡 CSV는 BOM이 붙는 경우가 많아 utf-8-sig로 읽는다.
    with args.input.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    required = {"timestamp", "sender_id", "message"}
    if rows and not required.issubset(rows[0].keys()):
        print(f"[Error] CSV 컬럼이 맞지 않습니다. 필요: {sorted(required)}, 실제: {list(rows[0].keys())}")
        sys.exit(1)

    messages, stats = convert(rows, keep_placeholders=args.keep_placeholders)

    with args.output.open("w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)

    print(f"[정상 완료] '{args.output}' 생성")
    print(f"  - 전체 행            : {stats['total']}")
    print(f"  - placeholder 제거   : {stats['placeholder_removed']}")
    print(f"  - 익명화(마스킹) 적용: {stats['masked']}건")
    print(f"  - 최종 메시지        : {stats['kept']}건")


if __name__ == "__main__":
    main()
