"""
기능 3 — 담당자 1: 지표별·종합 상태 판정

step1.md §4 기준으로 개별 지표 상태와 warning_count 기반 종합 상태를 결정한다.
최고 위험 등급 🔴는 의도적으로 제외하고 🟠까지를 상한으로 둔다.
"""

from __future__ import annotations

# step1.md §3.1 — feature3_analysis.py와 동일 값 유지
NEGATIVE_THRESHOLD = 5
AGGRESSION_THRESHOLD = 5
PARTICIPATION_THRESHOLD = 20


def classify_negative_state(change: float) -> str:
    """
    부정 비율 변화량(%p) 상태 판정.

    +5%p 이상 → 평소보다 높음
    -5~+5%p → 평소와 비슷
    -5%p 이하 → 평소보다 낮음
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

    +20% 이상 → 평소보다 많음
    -20~+20% → 평소와 비슷
    -20% 이하 → 평소보다 적음
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

    ① 부정 변화량 >= +5%p
    ② 공격성 변화량 >= +5%p
    ③ 참여량 변화율 <= -20%
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

    0개 → 🟢 평소와 비슷
    1개 → 🟡 평소와 조금 다름
    2개 이상 → 🟠 평소와 꽤 다름
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
