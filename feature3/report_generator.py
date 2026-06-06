# -*- coding: utf-8 -*-
"""
기능 3 — 담당자 2: 상태 변화 리포트 생성

파이프라인 2단계: analysis_result.json → sample_report.json

담당자 1이 만든 발신자별 지표(analysis_result.json)를 읽어,
심리적 방어선을 반영한 자연어 해석 문구를 붙여 최종 리포트를 생성한다.
"""

import json
import os
from datetime import datetime, timezone


def generate_text_interpretation(metrics, overall, data_sufficient, reason=""):
    """
    [기능 3 담당자 2 핵심] 심리적 방어선을 반영한 문구 매핑 알고리즘 (9대 경우의 수 전수 확장)
    """
    if not data_sufficient:
        if reason == "baseline_insufficient":
            return "비교 대상인 과거 7일간의 대화 데이터가 부족하여 신뢰할 수 있는 기저선을 수립할 수 없습니다. 정확한 분석을 위해 팀 활동을 조금 더 지속해 주세요! (최소 필요 기준: 10건)"
        return "오늘 작성한 메시지가 부족하여 평소 대비 변화를 분석하기 어렵습니다. 정확한 상태 거울을 보여드리기 위해 내일은 조금 더 많은 대화를 나눠보세요! (최소 필요 기준: 10건)"

    neg_state = metrics["negative"]["state"]
    agg_state = metrics["aggressive"]["state"]
    part_state = metrics["participation"]["state"]

    # [언니 피드백 반영] 9가지 세부 분기 조건 완벽 매핑
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

def main():
    input_file = "analysis_result.json"
    output_file = "sample_report.json"

    if not os.path.exists(input_file):
        print(f"[Error] '{input_file}' 파일이 없습니다. 데이터를 업로드해주세요.")
        return

    with open(input_file, "r", encoding="utf-8") as f:
        analysis_list = json.load(f)

    final_reports = []
    current_time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    for analysis_data in analysis_list:
        sender_id = analysis_data.get("sender_id")
        data_sufficient = analysis_data.get("data_sufficient", False)
        reason = analysis_data.get("reason", "")

        report = {
            "report_generated_at": current_time,
            "sender_id": sender_id,
            "data_sufficient": data_sufficient
        }

        if data_sufficient:
            metrics = {
                "negative": analysis_data.get("negative"),
                "aggressive": analysis_data.get("aggressive"),
                "participation": analysis_data.get("participation")
            }
            overall = analysis_data.get("overall", {"warning_count": 0, "state": "🟢 평소와 비슷"})

            report["metrics"] = metrics
            report["overall"] = {
                "warning_count": overall.get("warning_count"),
                "state": overall.get("state"),  # 이모지 조합 상태 통일 유지
                "text_interpretation": generate_text_interpretation(metrics, overall, True)
            }
        else:
            # 데이터 부족 케이스 예외 처리 세분화 (오늘 부족 / 과거 부족)
            report["overall"] = {
                "warning_count": 0,
                "state": "⚪ 판단 보류 (데이터 부족)",
                "text_interpretation": generate_text_interpretation(None, None, False, reason=reason)
            }
            if reason == "today_insufficient":
                report["today_message_count"] = analysis_data.get("today_message_count", 0)
                report["required_message_count"] = 10
            elif reason == "baseline_insufficient":
                report["baseline_message_count"] = analysis_data.get("baseline_message_count", 0)
                report["required_message_count"] = 10

        final_reports.append(report)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(final_reports, f, ensure_ascii=False, indent=2)

    print(f"[정상 완료] '{output_file}' 생성 완료. (리포트 {len(final_reports)}건)")

if __name__ == "__main__":
    main()