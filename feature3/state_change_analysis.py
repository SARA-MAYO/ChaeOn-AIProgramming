# -*- coding: utf-8 -*-
"""
기능 3 — 상태 변화 분석

기능 1(감정)·기능 2(공격성) 추론 라벨이 붙은 채팅 로그를 입력으로 받아,
데이터에 존재하는 모든 날짜를 각각 '오늘'로 두고 직전 7일과 비교해 3대 지표(부정·공격성·참여량)
변화를 계산하고, 종합 상태(🟢🟡🟠⚪)와 자연어 해석 문구를 붙인 날짜별 리포트를 생성한다.

이 모듈은 함수 라이브러리로, 통합 노트북(colab_feature3_member1.ipynb)에서 기능 1·2 모델의
출력 라벨을 받아 run_daily() 등을 호출하는 방식으로 사용한다.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from typing import Any
from zoneinfo import ZoneInfo

# 한국 팀 채팅·일일 리포트 기준 시간대 (KST, UTC+9)
KST = ZoneInfo("Asia/Seoul")

# ---------------------------------------------------------------------------
# 핵심 상수
# ---------------------------------------------------------------------------
MIN_MSG_COUNT = 10  # 오늘 메시지 최소 기준 (미달 시 data_sufficient=False)
MIN_BASELINE_MSG_COUNT = 10  # 직전 7일 누적 메시지 최소 기준
NEGATIVE_THRESHOLD = 5  # 부정 비율 변화량 임계값 (%p)
AGGRESSION_THRESHOLD = 5  # 공격성 비율 변화량 임계값 (%p)
PARTICIPATION_THRESHOLD = 20  # 참여량 변화율 임계값 (%)


# ---------------------------------------------------------------------------
# 시간 윈도우 분리
# ---------------------------------------------------------------------------
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
        # 명시적으로 하드코딩된 날짜를 주입했더라도,
        # 입력 데이터의 최신 날짜와 다르면 데이터 기준으로 자동 보정 (시연용 JSON 대응)
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


# ---------------------------------------------------------------------------
# 지표 계산
# ---------------------------------------------------------------------------
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
    data_sufficient 판정.

    today_count >= MIN_MSG_COUNT AND baseline_count >= MIN_BASELINE_MSG_COUNT
    """
    return today_count >= MIN_MSG_COUNT and baseline_count >= MIN_BASELINE_MSG_COUNT


def build_insufficient_result(
    sender_id: str,
    today_count: int,
    baseline_count: int,
) -> dict[str, Any]:
    """
    데이터 부족 가드레일 — 부족 사유(reason)를 구분해 고정 구조 반환.

    리포트 단계가 사유별로 올바른 안내 문구를 고르도록 reason 필드를 함께 둔다.
    (오늘 부족을 우선 사유로 본다.)
    """
    overall = {
        "warning_count": 0,
        "state": "⚪ 데이터 부족",
    }
    if today_count < MIN_MSG_COUNT:
        return {
            "sender_id": sender_id,
            "data_sufficient": False,
            "reason": "today_insufficient",
            "today_message_count": today_count,
            "required_message_count": MIN_MSG_COUNT,
            "overall": overall,
        }
    return {
        "sender_id": sender_id,
        "data_sufficient": False,
        "reason": "baseline_insufficient",
        "baseline_message_count": baseline_count,
        "required_message_count": MIN_BASELINE_MSG_COUNT,
        "overall": overall,
    }


# ---------------------------------------------------------------------------
# 상태 판정 — 개별 지표 상태와 warning_count 기반 종합 상태를 결정한다.
# 최고 위험 등급 🔴는 의도적으로 제외하고 🟠까지를 상한으로 둔다.
# ---------------------------------------------------------------------------
def classify_negative_state(change: float) -> str:
    """
    부정 비율 변화량(%p) 상태 판정.

    +5%p 이상 → 평소보다 높음 / -5~+5%p → 평소와 비슷 / -5%p 이하 → 평소보다 낮음
    """
    if change >= NEGATIVE_THRESHOLD:
        return "평소보다 높음"
    if change <= -NEGATIVE_THRESHOLD:
        return "평소보다 낮음"
    return "평소와 비슷"


def classify_aggression_state(change: float) -> str:
    """공격성 비율 변화량(%p) 상태 판정 — 부정과 동일 임계값."""
    if change >= AGGRESSION_THRESHOLD:
        return "평소보다 높음"
    if change <= -AGGRESSION_THRESHOLD:
        return "평소보다 낮음"
    return "평소와 비슷"


def classify_participation_state(change: float) -> str:
    """
    참여량 변화율(%) 상태 판정.

    +20% 이상 → 평소보다 많음 / -20~+20% → 평소와 비슷 / -20% 이하 → 평소보다 적음
    """
    if change >= PARTICIPATION_THRESHOLD:
        return "평소보다 많음"
    if change <= -PARTICIPATION_THRESHOLD:
        return "평소보다 적음"
    return "평소와 비슷"


def count_warnings(
    negative_change: float,
    aggression_change: float,
    participation_change: float,
) -> int:
    """
    warning_count — 주의 방향 지표 개수 합산.

    ① 부정 변화량 >= +5%p  ② 공격성 변화량 >= +5%p  ③ 참여량 변화율 <= -20%
    """
    warning_count = 0
    if negative_change >= NEGATIVE_THRESHOLD:
        warning_count += 1
    if aggression_change >= AGGRESSION_THRESHOLD:
        warning_count += 1
    if participation_change <= -PARTICIPATION_THRESHOLD:
        warning_count += 1
    return warning_count


def classify_overall_state(
    negative_change: float,
    aggression_change: float,
    participation_change: float,
) -> dict[str, int | str]:
    """
    종합 상태 판정 — warning_count 기반.

    0개 → 🟢 평소와 비슷 / 1개 → 🟡 평소와 조금 다름 / 2개 이상 → 🟠 평소와 꽤 다름
    """
    warning_count = count_warnings(
        negative_change, aggression_change, participation_change
    )
    if warning_count == 0:
        state = "🟢 평소와 비슷"
    elif warning_count == 1:
        state = "🟡 평소와 조금 다름"
    else:
        state = "🟠 평소와 꽤 다름"

    return {"warning_count": warning_count, "state": state}


def classify_metric_states(
    negative_change: float,
    aggression_change: float,
    participation_change: float,
) -> dict[str, str]:
    """3대 지표 각각의 상태 문자열을 한 번에 반환."""
    return {
        "negative": classify_negative_state(negative_change),
        "aggressive": classify_aggression_state(aggression_change),
        "participation": classify_participation_state(participation_change),
    }


# ---------------------------------------------------------------------------
# 발신자별 분석
# ---------------------------------------------------------------------------
def analyze_sender(
    sender_id: str,
    user_messages: list[dict[str, Any]],
    reference_date: date | None = None,
) -> dict[str, Any]:
    """단일 발신자에 대한 지표 계산 + 상태 판정."""
    today_messages, baseline_messages = split_time_window(user_messages, reference_date)
    today_count = len(today_messages)
    baseline_count = len(baseline_messages)

    if not is_data_sufficient(today_count, baseline_count):
        return build_insufficient_result(sender_id, today_count, baseline_count)

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
    part_change_value = participation_change if participation_change is not None else 0.0

    states = classify_metric_states(
        negative_change=negative_change,
        aggression_change=aggression_change,
        participation_change=part_change_value,
    )
    overall = classify_overall_state(
        negative_change=negative_change,
        aggression_change=aggression_change,
        participation_change=part_change_value,
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
    """sender_id 기준으로 메시지를 묶는다 — 집계의 핵심 키."""
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for msg in messages:
        grouped[msg["sender_id"]].append(msg)
    return dict(grouped)


# ---------------------------------------------------------------------------
# 자연어 해석 문구 + 리포트 조립
# ---------------------------------------------------------------------------
def generate_text_interpretation(metrics, overall, data_sufficient, reason=""):
    """심리적 방어선을 반영한 문구 매핑 (9대 경우의 수 전수 확장)."""
    if not data_sufficient:
        if reason == "baseline_insufficient":
            return "비교 대상인 과거 7일간의 대화 데이터가 부족하여 신뢰할 수 있는 기저선을 수립할 수 없습니다. 정확한 분석을 위해 팀 활동을 조금 더 지속해 주세요! (최소 필요 기준: 10건)"
        return "오늘 작성한 메시지가 부족하여 평소 대비 변화를 분석하기 어렵습니다. 정확한 상태 거울을 보여드리기 위해 내일은 조금 더 많은 대화를 나눠보세요! (최소 필요 기준: 10건)"

    neg_state = metrics["negative"]["state"]
    agg_state = metrics["aggressive"]["state"]
    part_state = metrics["participation"]["state"]

    # 9가지 세부 분기 조건 매핑
    if neg_state == "평소보다 높음" and agg_state == "평소보다 높음" and part_state == "평소보다 적음":
        return "부정·공격적 표현이 늘고 대화 참여는 줄어들어, 팀 프로젝트로 인해 다소 지친 상태일 수 있습니다. 따뜻한 휴식이 필요해 보여요."

    elif neg_state == "평소보다 높음" and agg_state == "평소보다 높음":
        return "조원들과의 대화에서 부정적인 감정과 공격적인 표현이 동시에 증가했습니다. 감정이 앞서 오해가 생기지 않도록 잠시 대화를 멈추고 환기해 보는 건 어떨까요?"

    elif neg_state == "평소보다 높음" and part_state == "평소보다 적음":
        return "부정적인 감정 표현은 늘어난 반면 소통량은 줄어들었습니다. 프로젝트 과정에서 말 못 할 고민이나 소외감을 느끼고 계신 건 아닌지 돌아봐 주세요."

    elif neg_state == "평소보다 높음" and part_state == "평소보다 많음":
        return "평소보다 대화 참여량이 급격히 늘어난 가운데, 부정적인 감정 표현이 함께 증가한 것이 관측되었습니다. 과도한 열정이나 피로로 인해 날카로워진 것은 아닌지 조원들과 잠시 숨을 골라보세요."

    elif neg_state == "평소보다 높음":
        return "평소 대비 부정적인 감정의 기류가 관측되었습니다. 스스로를 지치게 만드는 요인이 무엇인지 잠시 점검해 보는 시간을 가져보세요."

    elif agg_state == "평소보다 높음" and part_state == "평소보다 적음":
        return "참여량은 감소했으나 간헐적인 소통에서 공격적인 표현이 두드러집니다. 팀원들과의 관계적 스트레스가 한계에 다다랐을 수 있으니 휴식을 권장합니다."

    elif agg_state == "평소보다 높음":
        return "평소 대비 날카롭거나 공격적인 표현이 관측되었습니다. 메시지를 전송하기 전, 상대방의 입장에서 한 번만 더 읽어보는 건 어떨까요?"

    elif part_state == "평소보다 적음":
        return "조원들과의 소통 참여량이 평소보다 눈에 띄게 감소했습니다. 활동 참여에 어려움이 있거나 동기부여가 떨어진 상태일 수 있으니 조원들과 이야기를 나눠보세요."

    elif part_state == "평소보다 많음":
        return "팀 프로젝트에 적극적으로 참여하며 소통 참여량을 활발히 끌어올리고 계시네요! 조원들에게 든든한 에너지가 되고 있습니다."

    return "평소의 안정적인 소통 기저선을 잘 유지하고 있습니다. 지금처럼 건강하고 건설적인 커뮤니케이션을 이어가세요!"


def build_report(analysis: dict[str, Any], generated_at: str) -> dict[str, Any]:
    """발신자 분석 결과에 자연어 해석을 붙여 배포용 리포트 dict로 변환."""
    report: dict[str, Any] = {
        "report_generated_at": generated_at,
        "sender_id": analysis.get("sender_id"),
        "data_sufficient": analysis.get("data_sufficient", False),
    }

    if analysis.get("data_sufficient"):
        metrics = {
            "negative": analysis["negative"],
            "aggressive": analysis["aggressive"],
            "participation": analysis["participation"],
        }
        overall = analysis["overall"]
        report["metrics"] = metrics
        report["overall"] = {
            "warning_count": overall["warning_count"],
            "state": overall["state"],
            "text_interpretation": generate_text_interpretation(metrics, overall, True),
        }
    else:
        reason = analysis.get("reason", "")
        report["overall"] = {
            "warning_count": 0,
            "state": "⚪ 데이터 부족",
            "text_interpretation": generate_text_interpretation(None, None, False, reason=reason),
        }
        if reason == "today_insufficient":
            report["today_message_count"] = analysis.get("today_message_count", 0)
            report["required_message_count"] = MIN_MSG_COUNT
        elif reason == "baseline_insufficient":
            report["baseline_message_count"] = analysis.get("baseline_message_count", 0)
            report["required_message_count"] = MIN_BASELINE_MSG_COUNT

    return report


# ---------------------------------------------------------------------------
# 파이프라인 실행
# ---------------------------------------------------------------------------
def run(
    labeled_messages: list[dict[str, Any]],
    reference_date: date | None = None,
    generated_at: str | None = None,
) -> list[dict[str, Any]]:
    """라벨된 메시지 목록 → 발신자별 최종 리포트 리스트 (메모리 내 전 과정 수행)."""
    if generated_at is None:
        generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    grouped = group_messages_by_sender(labeled_messages)
    reports = []
    for sender_id in sorted(grouped.keys()):
        analysis = analyze_sender(sender_id, grouped[sender_id], reference_date)
        reports.append(build_report(analysis, generated_at))
    return reports


def analyze_sender_on_date(
    sender_id: str,
    user_messages: list[dict[str, Any]],
    ref_date: date,
) -> dict[str, Any] | None:
    """ref_date를 '오늘'로 고정(자동 보정 없음)하고 직전 7일과 비교한 단일 결과.

    그날 메시지가 없는 경우 None을 반환한다(생략 대상).
    """
    today_start = datetime.combine(ref_date, datetime.min.time(), tzinfo=KST)
    today_end = today_start + timedelta(days=1)
    base_start = today_start - timedelta(days=7)

    today_msgs: list[dict[str, Any]] = []
    base_msgs: list[dict[str, Any]] = []
    for m in user_messages:
        ts = _parse_timestamp(m["timestamp"])
        if today_start <= ts < today_end:
            today_msgs.append(m)
        elif base_start <= ts < today_start:
            base_msgs.append(m)

    today_count, baseline_count = len(today_msgs), len(base_msgs)
    if today_count == 0:
        return None
    if not is_data_sufficient(today_count, baseline_count):
        reason = "today_insufficient" if today_count < MIN_MSG_COUNT else "baseline_insufficient"
        return {
            "date": ref_date.isoformat(),
            "sender_id": sender_id,
            "data_sufficient": False,
            "today_count": today_count,
            "baseline_count": baseline_count,
            "overall": {
                "state": "⚪ 데이터 부족",
                "text_interpretation": generate_text_interpretation(None, None, False, reason=reason),
            },
        }

    today_neg = calculate_negative_ratio(today_msgs)
    base_neg = calculate_negative_ratio(base_msgs)
    today_agg = calculate_aggression_ratio(today_msgs)
    base_agg = calculate_aggression_ratio(base_msgs)
    participation = calculate_participation_change(today_msgs, base_msgs)

    negative_change = calculate_percentage_point(
        today_neg["negative_ratio"], base_neg["negative_ratio"]
    )
    aggression_change = calculate_percentage_point(
        today_agg["aggression_ratio"], base_agg["aggression_ratio"]
    )
    participation_change = participation["participation_change"] or 0.0

    states = classify_metric_states(negative_change, aggression_change, participation_change)
    overall = classify_overall_state(negative_change, aggression_change, participation_change)
    metrics = {
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
            "change": participation["participation_change"],
            "state": states["participation"],
        },
    }
    return {
        "date": ref_date.isoformat(),
        "sender_id": sender_id,
        "data_sufficient": True,
        "today_count": today_count,
        "baseline_count": baseline_count,
        "metrics": metrics,
        "overall": {**overall, "text_interpretation": generate_text_interpretation(metrics, overall, True)},
    }


def run_daily(labeled_messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """라벨된 메시지 → 날짜별 × 발신자별 리포트 리스트.

    데이터에 존재하는 모든 날짜를 각각 '오늘'로 두고 직전 7일과 비교한다.
    그날 메시지가 없는 (발신자, 날짜) 조합은 생략한다.
    """
    grouped = group_messages_by_sender(labeled_messages)
    all_dates = sorted({_parse_timestamp(m["timestamp"]).date() for m in labeled_messages})
    daily: list[dict[str, Any]] = []
    for ref_date in all_dates:
        for sender_id in sorted(grouped):
            result = analyze_sender_on_date(sender_id, grouped[sender_id], ref_date)
            if result is not None:
                daily.append(result)
    return daily
