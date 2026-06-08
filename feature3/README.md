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
├─ state_change_analysis.py   # 채팅 로그 → 지표 계산 + 상태 판정 + 날짜별 리포트 생성 (전 과정)
├─ preprocess_chat_log.py     # 카카오톡 채팅 CSV → 기능1·2 입력 JSON 변환 + 익명화 전처리기
├─ chat_log1_raw.json         # 실데이터 ① 통합 노트북 기본 입력 (전처리·익명화 완료, 메시지 다수)
├─ chat_log2_raw.json         # 실데이터 ② cleaned_chat_log2.csv 전처리 결과
├─ sample_chat_log_raw.json   # 데모용 원문 text 입력 (폴백)
├─ sample_chat_log.json       # 기능1·2 라벨이 붙은 입력 (기능3 단독 실행용)
├─ daily_report.json          # 단독 스크립트(①) 산출물 — 날짜별 × 사용자별 상태 리포트
├─ outputs/                   # 통합 노트북(②) 산출물 — 실행마다 <입력명>_<실행시각>/ 폴더로 분리 저장
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
- 출력: `daily_report.json` (날짜별 × 발신자별로 🟢🟡🟠⚪ 판정 + 자연어 해석)
- **이 입력 파일은 라벨이 포함된 채로 저장소에 들어 있어, 기능1·2를 먼저 돌리지 않아도 즉시 실행됩니다.**
  (기능1·2 모델·GPU·드라이브 인증 모두 불필요 — 기능3 로직만 단독 검증하는 경로입니다.)
- 파이썬 내장 라이브러리만 사용하므로 별도 설치가 없어도 동작합니다.
  (`requirements.txt`는 전체 프로젝트 연계 검수용 명세입니다.)

### ② 기능1·2 모델까지 통합 (GPU 필요) — **Run all만 하면 끝**

`colab_feature3_member1.ipynb`를 코랩에서 열고 **런타임 → 모두 실행(Run all)** 하면 됩니다.
파일 이동·업로드·경로 수정이 필요 없습니다.

자동으로 일어나는 일:
1. **저장소 자동 clone** → `state_change_analysis.py`, `chat_log1_raw.json`(실데이터) 확보
2. **드라이브 자동 마운트 + 필수 파일 검사** — 아래 4개가 `MyDrive`에 있는지 확인
   (없으면 **부족한 파일을 안내하고 종료**)
   - `chaeon_feature1_checkpoint/`, `svm_model.pkl`, `vectorizer.pkl` (기능1 Run all 시 생성)
   - `chaeon_feature2_model/` (기능2 Run all 시 생성)
3. 기능1·2 모델 **자동 로드** → 원문 → 기능1 추론 → 기능2 추론 → 라벨 검수(CELL 4.7)
   → 기능3 날짜별 분석 → 전체 요약 표·개인별 멘트 시각화(CELL 5.6)
   → 산출물은 `outputs/<입력명>_<실행시각>/` 폴더에 모아 저장 (실행마다 새 폴더, 덮어쓰기 없음)

> 전제: 기능1·2 노트북을 먼저 Run all 해두면 위 4개 파일이 드라이브에 자동 저장돼 있습니다.

> 통합 노트북은 실행마다 `outputs/<입력명>_<실행시각>/` 폴더를 새로 만들어 산출물을 저장합니다.
> 채팅 로그를 여러 개 돌려도 서로 덮어쓰지 않으며, 저장소의 원본 입력 파일(`sample_chat_log.json` 등)도 보존됩니다.

### 실행 시 자동 생성되는 파일

코드를 실행하면 아래 파일이 생성됩니다. (모두 재생성되므로 제출 필수는 아닙니다)

**통합 노트북(②)** — 실행마다 `outputs/<입력명>_<실행시각>/` 폴더 안에 저장 (+ `MyDrive/feature3_outputs/`에 백업):

| 파일 | 만드는 셀 | 내용 |
|---|---|---|
| `labeled.json` | CELL 4 | 기능1·2가 라벨링한 결과(감정·공격성). 원문을 모델로 돌렸을 때만 생성 |
| `label_review.csv` / `.txt` | CELL 4.7 | 라벨 검수 — 원문 ↔ 감정/공격성 전체 (정답이 없는 실데이터를 사람이 눈으로 확인) |
| `daily_report.json` | CELL 5.5 | **날짜별 × 사용자별 상태 리포트 (최종 산출물)** |

**단독 스크립트(①)** `python state_change_analysis.py`:

| 파일 | 내용 |
|---|---|
| `daily_report.json` | 날짜별 × 사용자별 상태 리포트 (`feature3/` 루트에 생성) |

> 기능 3은 별도 학습이 없어 `result.txt`에 성능 metric(Accuracy 등)은 없지만,
> 재현성·적법성 기록용으로 `feature3/log.txt`·`feature3/result.txt`를 둡니다.
> (Seed=42, 판정 기준 상수, "학습/검증/테스트셋 미사용" 등. 모델 자체 성능은 기능1·2의 `result.txt` 참조.)

---

## 실제 카카오톡 로그 전처리 (`preprocess_chat_log.py`)

데모용 `sample_chat_log_raw.json` 외에, **실제 카카오톡 채팅 로그**를 기능1·2 입력 형식으로
변환·익명화하는 전처리 코드와 그 결과물을 함께 제공합니다.

### 입력 / 출력

| 입력 CSV (원본)                         | 전처리 코드                  | 출력 JSON (결과물)        |
| --------------------------------------- | ---------------------------- | ------------------------- |
| `../.데이터셋/cleaned_chat_log1.csv`    | `preprocess_chat_log.py`     | `chat_log1_raw.json`      |
| `../.데이터셋/cleaned_chat_log2.csv`    | `preprocess_chat_log.py`     | `chat_log2_raw.json`      |

- 입력 CSV 컬럼: `timestamp, sender_id, message`
- `sender_id`는 원본이 이미 `User_A`~`User_D`로 가명화되어 있습니다.

### 전처리가 하는 일

1. **timestamp 변환** — 한국식 표기(`2025. 4. 7. 오후 4:58`) → ISO 8601 KST(`2025-04-07T16:58:00+09:00`)
2. **placeholder 제거** — `이모티콘`·`사진`·`사진 3장`·`동영상`·`삭제된 메시지입니다.` 등 문장이 아닌 미디어/시스템 표기 제거
3. **PII 익명화(마스킹)** — 전화번호·주민번호·이메일·링크·계좌/카드번호 등을 `[전화번호]`·`[이메일]`·`[번호]`로 치환

### 실행 방법

```bash
cd feature3

# cleaned_chat_log1.csv → chat_log1_raw.json (기본값)
python preprocess_chat_log.py

# cleaned_chat_log2.csv → chat_log2_raw.json (입력/출력 직접 지정)
python preprocess_chat_log.py --input ../.데이터셋/cleaned_chat_log2.csv --output chat_log2_raw.json

# 이모티콘/사진 등 placeholder도 제거하지 않고 유지하려면
python preprocess_chat_log.py --keep-placeholders
```

> 파이썬 내장 라이브러리만 사용하므로 별도 설치 없이 동작합니다.
> 통합 노트북은 입력 우선순위 1번이 `chat_log1_raw.json`이라, 별도 복사·이름변경 없이
> 실데이터를 자동으로 사용합니다. (`chat_log2_raw.json`을 쓰려면 노트북의 `INPUT_CANDIDATES` 순서를 조정)

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
