# 채팅로그 분석 결과 (chat_log_result)

실데이터 단톡방 2개(`chat_log1_raw.json` · `chat_log2_raw.json`)를 통합 노트북
(`colab_feature3_member1.ipynb`)으로 **실제로 돌려서 나온 산출물**을 입력별로 모아둔 폴더입니다.

> 채점 필수는 아닙니다. (코드 + 데이터 + 시드(42)로 Colab에서 그대로 **재현**됩니다.)
> 노트북·GPU를 직접 돌리지 않고도 기능3의 **최종 산출물(날짜별 × 사용자별 상태 리포트)** 을
> 바로 확인할 수 있도록 첨부합니다.

## 구조

```
chat_log_result/
├─ chat_log1/        # chat_log1_raw.json 실행 결과
│  ├─ daily_report.json     # 최종 산출물 — 날짜별 × 발신자별 🟢🟡🟠⚪ 판정
│  └─ label_review.csv      # (선택) 원문 ↔ 감정/공격성 라벨 검수
└─ chat_log2/        # chat_log2_raw.json 실행 결과
   ├─ daily_report.json
   └─ label_review.csv
```

> **두 로그는 서로 다른 단톡방**이라 각각 따로 분석합니다.
> (기능3 baseline이 "한 채팅방 안 직전 7일 vs 당일" 비교라 합치면 의미가 없음.)

## 결과 파일 만드는 법 (Colab)

- 노트북을 **Run all** 한 번 하면 `INPUTS_TO_RUN = ["chat_log1_raw.json", "chat_log2_raw.json"]`에
  따라 두 로그가 순서대로 자동 실행되어 `outputs/chat_log1_raw_<시각>/`·`outputs/chat_log2_raw_<시각>/`가 각각 생성됩니다.
- 각 실행의 `daily_report.json`(+ `label_review.csv`)을 위 폴더(`chat_log1/`·`chat_log2/`)로 복사하면 끝.
