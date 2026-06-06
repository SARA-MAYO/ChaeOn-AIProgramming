# 기능 3 - 상태 변화 분석 (State Change Analysis)

기능 1(감정), 기능 2(공격성) 결과를 이용해 사용자의 **상태 변화**를 분석합니다.
별도 학습이 없으며, 기능 1·2의 출력과 채팅 로그를 입력으로 받아 리포트를 생성합니다.

## 분석 항목

- 부정 감정 변화
- 공격성 변화
- 참여량 변화

## 최종 결과

- 🟢 평소와 비슷
- 🟡 평소와 조금 다름
- 🟠 평소와 꽤 다름
- ⚪ 데이터 부족

---

## 폴더 구성

```
feature3/
├─ feature3_analysis.py    # [1단계] 채팅 로그 → 발신자별 지표 계산
├─ state_classifier.py     # 지표별·종합 상태(🟢🟡🟠⚪) 판정 (1단계가 import)
├─ report_generator.py     # [2단계] 지표 → 자연어 해석 붙여 최종 리포트 생성
├─ sample_chat_log.json    # 입력 예시 (기능1·2 라벨이 붙은 채팅 로그)
├─ analysis_result.json    # 1단계 산출물 (발신자별 지표)
├─ sample_report.json      # 2단계 산출물 (최종 리포트)
└─ requirements.txt        # 패키지 명세
```

---

## 실행 방법

```bash
cd feature3
pip install -r requirements.txt   # (필요 시)

# 1단계: 채팅 로그 → 지표 (sample_chat_log.json → analysis_result.json)
python feature3_analysis.py

# 2단계: 지표 → 최종 리포트 (analysis_result.json → sample_report.json)
python report_generator.py
```

- 1단계 입력: `sample_chat_log.json` / 출력: `analysis_result.json`
- 2단계 입력: `analysis_result.json` / 출력: `sample_report.json` (위 4단계 상태 중 하나로 판정)

---

## 비고

- 학습/테스트 데이터셋을 사용하지 않으므로 별도 데이터셋 다운로드가 필요 없습니다.
- 기능 1·2의 출력 포맷에 맞춰 입력 JSON을 구성합니다.
