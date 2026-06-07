# -*- coding: utf-8 -*-
"""기능1·2 → 기능3 연결부(인터페이스) 통합 스모크 테스트.

목적은 모델 성능이 아니라 '배관' 검증이다.
  - 기능1·2가 내보내는 키 이름/값 형식이 기능3가 읽는 키와 맞는가?
  - 원문(raw) → 라벨링(글루) → state_change_analysis.run()이
    KeyError/구조 오류 없이 끝까지 흐르는가?

모델 추론부(run_feature1_emotion / run_feature2_aggression)만 키워드 스텁으로 대체하고,
colab 노트북의 label_messages 로직과 state_change_analysis는 실제 코드 그대로 사용한다.
→ 모델/GPU 없이도 연결부(키·구조·파일명) 버그를 잡아낸다.

실행:  python integration_check.py
"""
import sys
import json

try:
    sys.stdout.reconfigure(encoding="utf-8")  # 윈도우 콘솔에서도 이모지 출력 안전
except Exception:
    pass

import state_change_analysis as f3  # 기능3 실제 모듈


# --- 기능1 추론부 스텁: 실제는 KcELECTRA+SVM → 'positive'/'negative' (이진, neutral 없음) ---
def run_feature1_emotion(text: str) -> str:
    neg_kw = ["지치", "속상", "우울", "걱정", "힘들", "막막", "답답", "짜증", "못 해", "못해"]
    return "negative" if any(k in text for k in neg_kw) else "positive"


# --- 기능2 추론부 스텁: 실제는 KoELECTRA-small argmax → 0/1/2 (int) ---
def run_feature2_aggression(text: str) -> int:
    strong_kw = ["책임지", "똑바로", "뭡니까", "짜증", "답답", "못 해요"]
    return 2 if any(k in text for k in strong_kw) else 0


# --- colab 노트북 label_messages 로직 그대로 (통합 접합부) ---
def label_messages(raw_messages):
    labeled = []
    for msg in raw_messages:
        text = msg["text"]
        labeled.append({
            "message_id": msg["message_id"],
            "sender_id": msg["sender_id"],
            "timestamp": msg["timestamp"],
            "emotion_label": run_feature1_emotion(text),
            "aggression_label": run_feature2_aggression(text),
        })
    return labeled


def main():
    raw = json.load(open("sample_chat_log_raw.json", encoding="utf-8"))
    print(f"[1] 원문 입력 로드: {len(raw)}건  (필드: {sorted(raw[0])})")

    labeled = label_messages(raw)
    print(f"[2] 기능1·2 라벨링 완료  (필드: {sorted(labeled[0])})")

    # === 연결부 계약 검증 ===
    REQUIRED = {"sender_id", "timestamp", "emotion_label", "aggression_label"}
    missing = REQUIRED - set(labeled[0])
    assert not missing, f"[FAIL] 기능3 필수 키 누락: {missing}"

    for m in labeled:
        assert isinstance(m["emotion_label"], str), f"[FAIL] emotion_label이 str이 아님: {m}"
        assert isinstance(m["aggression_label"], int), f"[FAIL] aggression_label이 int가 아님: {m}"

    emos = {m["emotion_label"] for m in labeled}
    aggs = {m["aggression_label"] for m in labeled}
    assert emos <= {"positive", "negative", "neutral"}, f"[FAIL] 예상 밖 emotion 값: {emos}"
    assert aggs <= {0, 1, 2}, f"[FAIL] 예상 밖 aggression 값: {aggs}"
    print(f"[3] 키 계약 OK  | emotion 값={emos}  aggression 값={aggs}")

    # === end-to-end: 기능3 실행 ===
    reports = f3.run(labeled)
    print(f"[4] 기능3 리포트 생성: {len(reports)}건")
    for r in reports:
        print(f"     {r['sender_id']}: {r['overall']['state']} (wc={r['overall']['warning_count']})")

    print("\n[OK] 통합 연결부 검증 통과 — 원문 → 기능1·2 → 기능3 배관 정상")
    print("     (라벨 분류는 키워드 스텁이라 최종 판정은 실제 모델 출력과 다를 수 있음 —")
    print("      판정 정확성은 실제 기능1·2 모델로 한 번 돌려서 확인할 것)")


if __name__ == "__main__":
    main()
