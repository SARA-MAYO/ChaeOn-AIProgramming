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
├─ state_change_analysis.py   # 채팅 로그 → 지표 계산 + 상태 판정 + 리포트 생성 (전 과정)
├─ sample_chat_log.json       # 입력 ① 기능1·2 라벨이 붙은 채팅 로그 (기능3 단독 실행용)
├─ sample_chat_log_raw.json   # 입력 ② 원문 text만 있는 로그 (기능1·2 모델 통합 시연용)
├─ sample_report.json         # 산출물 예시 (실행 시 생성됨)
├─ colab_feature3_member1.ipynb  # 기능1·2 모델 → 기능3 통합 시연 노트북
└─ requirements.txt           # 패키지 명세
```

---

## 실행 방법

### ① 기능 3 단독 (GPU·모델 불필요 — 권장)

```bash
cd feature3
python state_change_analysis.py
```

- 입력: `sample_chat_log.json` (기능1·2 라벨이 붙은 채팅 로그)
- 출력: `sample_report.json` (발신자별로 🟢🟡🟠⚪ 중 하나로 판정 + 자연어 해석)
- 파이썬 내장 라이브러리만 사용하므로 별도 설치가 없어도 동작합니다.
  (`requirements.txt`는 전체 프로젝트 연계 검수용 명세입니다.)

### ② 기능1·2 모델까지 통합 (GPU 필요) — **Run all만 하면 끝**

`colab_feature3_member1.ipynb`를 코랩에서 열고 **런타임 → 모두 실행(Run all)** 하면 됩니다.
파일 이동·업로드·경로 수정이 필요 없습니다.

자동으로 일어나는 일:
1. **저장소 자동 clone** → `state_change_analysis.py`, `sample_chat_log_raw.json` 확보
2. **드라이브 자동 마운트 + 필수 파일 검사** — 아래 4개가 `MyDrive`에 있는지 확인
   (없으면 **부족한 파일을 안내하고 종료**)
   - `chaeon_feature1_checkpoint/`, `svm_model.pkl`, `vectorizer.pkl` (기능1 Run all 시 생성)
   - `chaeon_feature2_model/` (기능2 Run all 시 생성)
3. 기능1·2 모델 **자동 로드** → 원문 → 기능1 추론 → 기능2 추론 → 기능3 분석 → `sample_report.json` 생성

> 전제: 기능1·2 노트북을 먼저 Run all 해두면 위 4개 파일이 드라이브에 자동 저장돼 있습니다.

> `sample_report.json`은 실행하면 다시 생성되는 산출물입니다. 저장소의 파일은 예시 결과입니다.

---

## 입력 데이터 형식

기능 3은 **기능 1·2의 출력 규격**(라벨이 붙은 메시지 리스트)을 입력으로 받습니다.

```json
// sample_chat_log.json — 기능1·2 출력 = 기능3 입력
[
  {
    "message_id": 1,
    "sender_id": "user_A",
    "timestamp": "2026-06-03T10:00:00+09:00",
    "emotion_label": "positive",     // 기능 1 출력: positive | negative | neutral
    "aggression_label": 0             // 기능 2 출력: 0(비공격) | 1(약) | 2(강)
  }
]
```

통합 실행 시에는 라벨 대신 **원문 `text`** 가 든 입력을 사용하며, 기능1·2 모델이 라벨을 채웁니다.

```json
// sample_chat_log_raw.json — 기능1·2 입력 (원문)
[
  {
    "message_id": 1,
    "sender_id": "user_A",
    "timestamp": "2026-06-03T10:00:00+09:00",
    "text": "오늘 회의 자료 정리 다 끝냈어요! 다들 확인 부탁드려요"
  }
]
```

---

## 비고

- 별도 학습이 없으며, 학습/테스트 데이터셋도 사용하지 않습니다.
