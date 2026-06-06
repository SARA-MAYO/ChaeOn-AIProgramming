"""
기능 3 — 담당자 1: 원천 데이터 연산 및 내부 변수 설계

기능 1(감정)·기능 2(공격성) 추론 결과가 붙은 메시지 목록을 받아
발신자별 지표를 계산하고 analysis_result.json 규격의 dict를 반환한다.

담당자 2 영역(report_generator, sample_report, text_interpretation)은 포함하지 않는다.
"""

from __future__ import annotations

import json
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

# 한국 팀 채팅·일일 리포트 기준 시간대 (KST, UTC+9)
KST = ZoneInfo("Asia/Seoul")

# ---------------------------------------------------------------------------
# 핵심 상수 — step1.md §3.1
# ---------------------------------------------------------------------------
MIN_MSG_COUNT = 10  # 오늘 메시지 최소 기준 (미달 시 data_sufficient=False)
MIN_BASELINE_MSG_COUNT = 10  # 직전 7일 누적 메시지 최소 기준
NEGATIVE_THRESHOLD = 5  # 부정 비율 변화량 임계값 (%p)
AGGRESSIVE_THRESHOLD = 5  # 공격성 비율 변화량 임계값 (%p)
PARTICIPATION_THRESHOLD = 20  # 참여량 변화율 임계값 (%)


def _parse_timestamp(value: str) -> datetime:
    """
    timestamp를 KST 기준 datetime으로 변환.

    - 'YYYY-MM-DDTHH:MM:SS+09:00' : KST 명시
    - 'YYYY-MM-DD HH:MM:SS'       : 타임존 없으면 KST로 간주 (한국 채팅 로그 기본)
    - '...Z' (UTC)                : KST로 변환
    """
    value = value.strip()
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(value)
    except ValueError:
        dt = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=KST)
    return dt.astimezone(KST)


def split_time_window(
    user_messages: list[dict[str, Any]],
    reference_date: date | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """
    사용자 메시지를 오늘(Current) / 직전 7일(Baseline)로 분리.

    - today: reference_date 당일 00:00~23:59 (KST)
    - baseline: reference_date 직전 7일 (당일 제외, KST)

    Returns:
        (today_messages, baseline_messages)
    """
    if not user_messages:
        return [], []

    if reference_date is None:
        # 분석 기준일 = KST 기준 메시지 중 가장 최근 날짜
        latest = max(_parse_timestamp(m["timestamp"]) for m in user_messages)
        reference_date = latest.astimezone(KST).date()
    else:
        # Colab 등에서 명시적으로 하드코딩된 날짜를 주입했을지라도,
        # 입력 데이터의 최신 날짜와 다르면 데이터 기준으로 자동 보정 (담당자 2 시연용 JSON 대응)
        latest = max(_parse_timestamp(m["timestamp"]) for m in user_messages)
        auto_ref_date = latest.astimezone(KST).date()
        if reference_date != auto_ref_date:
            reference_date = auto_ref_date

    # 당일·baseline 경계는 KST 자정 기준
    today_start = datetime.combine(reference_date, datetime.min.time(), tzinfo=KST)
    today_end = today_start + timedelta(days=1)
    baseline_start = today_start - timedelta(days=7)

    today_messages: list[dict[str, Any]] = []
    baseline_messages: list[dict[str, Any]] = []

    for msg in user_messages:
        ts = _parse_timestamp(msg["timestamp"])
        if today_start <= ts < today_end:
            today_messages.append(msg)
        elif baseline_start <= ts < today_start:
            baseline_messages.append(msg)

    return today_messages, baseline_messages


def calculate_negative_ratio(messages: list[dict[str, Any]]) -> dict[str, float | int]:
    """
    부정 비율(%) = 부정 메시지 수 / 전체 메시지 수 × 100

    emotion_label == 'negative' 인 메시지를 부정으로 집계.
    """
    total_count = len(messages)
    if total_count == 0:
        return {"negative_count": 0, "total_count": 0, "negative_ratio": 0.0}

    negative_count = sum(1 for m in messages if m.get("emotion_label") == "negative")
    negative_ratio = round(negative_count / total_count * 100, 2)
    return {
        "negative_count": negative_count,
        "total_count": total_count,
        "negative_ratio": negative_ratio,
    }


def calculate_aggression_ratio(messages: list[dict[str, Any]]) -> dict[str, float | int]:
    """
    공격성 비율(%) = 공격 메시지 수 / 전체 메시지 수 × 100

    aggression_label in (1, 2) 를 공격 메시지로 집계.
    """
    total_count = len(messages)
    if total_count == 0:
        return {"aggression_count": 0, "total_count": 0, "aggression_ratio": 0.0}

    aggression_count = sum(
        1 for m in messages if m.get("aggression_label") in (1, 2)
    )
    aggression_ratio = round(aggression_count / total_count * 100, 2)
    return {
        "aggression_count": aggression_count,
        "total_count": total_count,
        "aggression_ratio": aggression_ratio,
    }


def calculate_participation_change(
    today_messages: list[dict[str, Any]],
    baseline_messages: list[dict[str, Any]],
) -> dict[str, float | int | None]:
    """
    참여량 변화율(%) = (오늘 메시지 수 - 7일 일평균) / 7일 일평균 × 100

    baseline_daily_average = baseline 총 메시지 수 / 7
    """
    today_count = len(today_messages)
    baseline_count = len(baseline_messages)
    baseline_daily_average = round(baseline_count / 7, 2)

    if baseline_daily_average == 0:
        return {
            "today_count": today_count,
            "baseline_count": baseline_count,
            "baseline_daily_average": 0.0,
            "participation_change": None,
        }

    participation_change = round(
        (today_count - baseline_daily_average) / baseline_daily_average * 100, 2
    )
    return {
        "today_count": today_count,
        "baseline_count": baseline_count,
        "baseline_daily_average": baseline_daily_average,
        "participation_change": participation_change,
    }


def calculate_percentage_point(current_ratio: float, baseline_ratio: float) -> float:
    """부정/공격성 변화량(%p) = 오늘 비율 - baseline 비율."""
    return round(current_ratio - baseline_ratio, 2)


def is_data_sufficient(today_count: int, baseline_count: int) -> bool:
    """
    data_sufficient 판정 — step1.md §3.1.1

    today_count >= MIN_MSG_COUNT AND baseline_count >= MIN_BASELINE_MSG_COUNT
    """
    return today_count >= MIN_MSG_COUNT and baseline_count >= MIN_BASELINE_MSG_COUNT


def build_insufficient_result(
    sender_id: str,
    today_count: int,
) -> dict[str, Any]:
    """데이터 부족 가드레일 — 하위 지표 없이 고정 구조 반환."""
    return {
        "sender_id": sender_id,
        "data_sufficient": False,
        "today_message_count": today_count,
        "required_message_count": MIN_MSG_COUNT,
        "overall": {
            "warning_count": 0,
            "state": "⚪ 판단 보류 (데이터 부족)",
        },
    }


def analyze_sender(
    sender_id: str,
    user_messages: list[dict[str, Any]],
    reference_date: date | None = None,
) -> dict[str, Any]:
    """
    단일 발신자에 대한 기능 3 분석 수행.

    state_classifier 모듈을 호출해 지표별·종합 상태를 붙인다.
    """
    from state_classifier import classify_overall_state, classify_metric_states

    today_messages, baseline_messages = split_time_window(user_messages, reference_date)
    today_count = len(today_messages)
    baseline_count = len(baseline_messages)

    if not is_data_sufficient(today_count, baseline_count):
        return build_insufficient_result(sender_id, today_count)

    today_neg = calculate_negative_ratio(today_messages)
    base_neg = calculate_negative_ratio(baseline_messages)
    today_agg = calculate_aggression_ratio(today_messages)
    base_agg = calculate_aggression_ratio(baseline_messages)
    participation = calculate_participation_change(today_messages, baseline_messages)

    negative_change = calculate_percentage_point(
        today_neg["negative_ratio"], base_neg["negative_ratio"]
    )
    aggression_change = calculate_percentage_point(
        today_agg["aggression_ratio"], base_agg["aggression_ratio"]
    )
    participation_change = participation["participation_change"]

    states = classify_metric_states(
        negative_change=negative_change,
        aggression_change=aggression_change,
        participation_change=participation_change if participation_change is not None else 0.0,
    )
    overall = classify_overall_state(
        negative_change=negative_change,
        aggression_change=aggression_change,
        participation_change=participation_change if participation_change is not None else 0.0,
    )

    return {
        "sender_id": sender_id,
        "data_sufficient": True,
        "negative": {
            "baseline_ratio": base_neg["negative_ratio"],
            "today_ratio": today_neg["negative_ratio"],
            "change": negative_change,
            "state": states["negative"],
        },
        "aggressive": {
            "baseline_ratio": base_agg["aggression_ratio"],
            "today_ratio": today_agg["aggression_ratio"],
            "change": aggression_change,
            "state": states["aggressive"],
        },
        "participation": {
            "baseline_average": participation["baseline_daily_average"],
            "today_count": participation["today_count"],
            "change": participation_change,
            "state": states["participation"],
        },
        "overall": overall,
    }


def group_messages_by_sender(
    messages: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    """sender_id 기준으로 메시지를 묶는다 — 기능 3 집계의 핵심 키."""
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for msg in messages:
        grouped[msg["sender_id"]].append(msg)
    return dict(grouped)


def run_analysis(
    labeled_messages: list[dict[str, Any]],
    reference_date: date | None = None,
) -> list[dict[str, Any]]:
    """
    전체 파이프라인: 발신자별 분석 후 analysis_result 리스트 반환.

    labeled_messages: 기능 1·2 추론이 완료된 메시지 목록
        (emotion_label, aggression_label 필드 필수)
    """
    grouped = group_messages_by_sender(labeled_messages)
    results = []
    for sender_id in sorted(grouped.keys()):
        results.append(analyze_sender(sender_id, grouped[sender_id], reference_date))
    return results


def save_analysis_result(
    results: list[dict[str, Any]],
    output_path: str | Path,
) -> Path:
    """analysis_result.json 저장 — 담당자 2 인계용 중간 산출물."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    return path


def main() -> None:
    """
    파이프라인 1단계 실행: sample_chat_log.json → analysis_result.json

    기능 1·2 추론 라벨(emotion_label, aggression_label)이 붙은 채팅 로그를
    읽어 발신자별 지표를 계산하고, 담당자 2 인계용 analysis_result.json을 만든다.
    """
    input_file = Path("sample_chat_log.json")
    output_file = Path("analysis_result.json")

    if not input_file.exists():
        print(f"[Error] '{input_file}' 파일이 없습니다. 입력 채팅 로그를 준비해주세요.")
        return

    with input_file.open("r", encoding="utf-8") as f:
        labeled_messages = json.load(f)

    results = run_analysis(labeled_messages)
    save_analysis_result(results, output_file)
    print(f"[정상 완료] '{output_file}' 생성 완료. (발신자 {len(results)}명 분석)")


if __name__ == "__main__":
    main()
