# 기능 3 - 상태 변화 분석 (State Change Analysis)

기능 1(감정), 기능 2(공격성) 결과를 이용해 사용자의 **상태 변화**를 분석합니다.
별도 학습이 없으며, 기능 1·2의 출력과 채팅 로그를 입력으로 받아 리포트를 생성합니다.

> 환경 세팅·전체 실행 순서(기능 1→2→3)·드라이브 저장 구조·생성 파일 목록은 **루트 [`../README.md`](../README.md)** 참고.
> 이 문서는 기능 3의 **폴더 구성 · 통합 실행 · 카카오톡 전처리 · 입력 형식** 등 고유 디테일을 담습니다.

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
│  # ── 코드 ──
├─ state_change_analysis.py        # 기능3 엔진: 지표 계산 + 상태 판정 + 날짜별 리포트 (노트북에서 호출하는 함수 모듈)
├─ colab_feature3_member1.ipynb    # 기능1·2 모델 → 기능3 통합 시연 노트북
├─ preprocess_chat_log.py          # 카카오톡 CSV → 기능1·2 입력 JSON 변환 + 익명화 전처리기
│  # ── 입력 데이터 ──
├─ chat_log1_raw.json              # 실데이터 ① 통합 노트북 기본 입력 (원문, 전처리·익명화 완료)
├─ chat_log2_raw.json              # 실데이터 ② cleaned_chat_log2.csv 전처리 결과 (원문)
│  # ── 산출물 (실행 시 생성·갱신) ──
├─ result.txt                      # 재현성·적법성 기록 (Seed·판정 기준·학습 미사용)
├─ outputs/                        # 통합 노트북 산출물 — 실행마다 <입력명>_<실행시각>/ 폴더로 분리 (gitignore)
├─ chat_log_result/                # 실데이터 2개를 실제로 돌린 산출물 (chat_log1/ · chat_log2/)
│  # ── 문서 ──
├─ README.md
└─ requirements.txt                # 패키지 명세 (pandas / numpy / scikit-learn)
```

> 통합 노트북은 시작 시 `MyDrive/feature1/`·`MyDrive/feature2/` 의 기능1·2 모델을 검사·로드하고, 없으면 부족한 파일을 안내하고 종료합니다. (드라이브 저장 구조 상세는 루트 README)

---

## 실행 방법

### 통합 실행 (Colab — 정식 경로)

`colab_feature3_member1.ipynb` 를 Colab에서 **Run all** → 저장소 자동 clone → 드라이브 인증 → 기능1·2 모델 자동 로드 → 원문 → 기능1 추론 → 기능2 추론 → 라벨 검수 → 기능3 날짜별 분석 → `outputs/<입력명>_<실행시각>/` 에 산출물 저장 (실행마다 새 폴더, 덮어쓰기 없음). 업로드·경로 수정 불필요.

기능3은 반드시 **기능1·2 모델 추론 결과로 돌립니다.** `state_change_analysis.py` 는 노트북이 호출하는 함수 모듈이며, 단독 실행 진입점은 없습니다. (전체 실행 순서·전제 조건은 루트 README 참고)

> 기능 3은 별도 학습이 없어 `result.txt`에 성능 metric(Accuracy 등)은 없지만, 재현성·적법성 기록용으로 `result.txt`를 둡니다.
> (Seed=42, 판정 기준 상수, "학습/검증/테스트셋 미사용" 등. 모델 자체 성능은 기능1·2의 `result.txt` 참조.)

---

## 실제 분석 결과물 (`chat_log_result/`)

실데이터 단톡방 2개를 통합 노트북으로 **실제로 돌려 나온 산출물**(날짜별 × 발신자별 상태 리포트)을 입력별로 모아둔 폴더입니다. 노트북·GPU를 직접 돌리지 않고도 기능3의 최종 결과를 바로 확인할 수 있습니다. (채점 필수 아님 — 코드 + 데이터 + 시드(42)로 Colab에서 그대로 재현)

→ 폴더 구조·생성 방법 상세는 [`chat_log_result/README.md`](chat_log_result/README.md) 참고.

---

## 실제 카카오톡 로그 전처리 (`preprocess_chat_log.py`)

**실제 카카오톡 채팅 로그**를 기능1·2 입력 형식(`chat_log1_raw.json`·`chat_log2_raw.json`)으로
변환·익명화하는 전처리 코드와 그 결과물을 함께 제공합니다.

### 입력 / 출력

| 입력 CSV (원본) | 전처리 코드 | 출력 JSON (결과물) |
| --------------------------------------- | ---------------------------- | ------------------------- |
| `../.데이터셋/cleaned_chat_log1.csv` | `preprocess_chat_log.py` | `chat_log1_raw.json` |
| `../.데이터셋/cleaned_chat_log2.csv` | `preprocess_chat_log.py` | `chat_log2_raw.json` |

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
> 통합 노트북은 `INPUTS_TO_RUN = ["chat_log1_raw.json", "chat_log2_raw.json"]`에 따라
> 별도 복사·이름변경 없이 두 실데이터를 **Run all 한 번에 순서대로 자동 실행**합니다.

---

## 입력 데이터 형식

기능 3은 **기능 1·2의 출력 규격**(라벨이 붙은 메시지 리스트)을 입력으로 받습니다.

```json
// 기능1·2 출력 = 기능3 입력 (라벨이 붙은 메시지 리스트)
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
// chat_log1_raw.json — 기능1·2 입력 (원문)
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
