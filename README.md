# 채온(CHAEON) — AI Programming Project

> 명지대학교 AI프로그래밍 팀 프로젝트 / 팀명: 채온(CHAEON)
> 팀 단체 채팅 로그의 **감정·공격성**을 분석해 구성원의 **커뮤니케이션 상태 변화를 조기 탐지**하는 AI 시스템.

이 README 하나로 **환경 세팅 → 데이터 배치 → 실행 → 결과 확인**을 끝까지 따라 할 수 있습니다.

---

## 실행 환경 (먼저 읽어 주세요)

- 본 프로젝트는 **Google Colab 전용**으로 설계되었습니다.
  드라이브 마운트·세션 업로드(`/content/`)·GPU 사용을 전제로 작성되어 **로컬 PC / 가상환경(venv)에서는 실행되지 않습니다.**
  채점·재현은 **반드시 Google Colab에서** 진행해 주세요.
- 학습(기능 1·2)에는 **GPU 런타임 권장**: 런타임 → 런타임 유형 변경 → 하드웨어 가속기: **GPU(T4 등)**
- 사람이 직접 하는 일은 3가지뿐입니다 → **① 데이터 업로드  ② 구글 드라이브 인증 클릭  ③ Run all**

---

## 실행 순서 (Colab에서 Run all 3번)

반드시 **기능 1 → 기능 2 → 기능 3 순서**로 실행합니다.
(기능 3은 기능 1·2가 **드라이브에 저장한 모델**을 불러와 동작하므로, 먼저 돌리지 않으면 멈춥니다.)

| 순서 | 노트북 | Colab에서 열기 | 할 일 | 자동으로 일어나는 것 |
|---|---|---|---|---|
| 1 | `feature1/sentiment_analysis.ipynb` | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/SARA-MAYO/ChaeOn-AIProgramming/blob/main/feature1/sentiment_analysis.ipynb) | 데이터 업로드 후 **Run all** | 학습 → `MyDrive/feature1/` 에 모델 + `result.txt` + `log.txt` 자동 저장 |
| 2 | `feature2/aggression_detection.ipynb` | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/SARA-MAYO/ChaeOn-AIProgramming/blob/main/feature2/aggression_detection.ipynb) | 데이터 업로드 후 **Run all** | 학습 → `MyDrive/feature2/` 에 모델 + `result.txt` + `log.txt` 자동 저장 |
| 3 | `feature3/colab_feature3_member1.ipynb` | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/SARA-MAYO/ChaeOn-AIProgramming/blob/main/feature3/colab_feature3_member1.ipynb) | **Run all** (업로드할 데이터 없음) | 저장소 자동 clone → 기능1·2 모델 드라이브에서 자동 로드 → 원문→기능1→기능2→기능3 날짜별 분석 → `daily_report.json` 생성 |

> 위 **Open In Colab** 배지를 누르면 노트북이 Colab에서 바로 열립니다. (다운로드·업로드 불필요)
> 기능 3은 시작 시 기능 1·2 모델이 드라이브에 있는지 **자동 검사**하고, 없으면 **어떤 파일이 부족한지 안내하고 멈춥니다.** → 해당 기능 노트북을 먼저 Run all 하세요.

---

## 0단계 — 데이터 파일 배치 (별도 전달, 저장소에 없음)

아래 데이터는 라이선스(로그인·재배포 제한)·개인정보 문제로 **GitHub에 포함하지 않으며, 제출물과 함께 별도로 전달**합니다.
기능 1·2 노트북을 연 뒤 **Colab 세션(`/content/`)에 업로드**하세요. (파일명이 노트북이 읽는 이름과 정확히 같아야 합니다.)

| 전달 파일명 | 사용 기능 | 두는 위치 | 비고 |
|---|---|---|---|
| `감성대화말뭉치(최종데이터)_Training.xlsx` | 기능 1 | Colab `/content/` 에 업로드 | 필수 |
| `감성대화말뭉치(최종데이터)_Validation.xlsx` | 기능 1 | Colab `/content/` 에 업로드 | 필수 |
| `talksets-train-1_aihub.csv` | 기능 2 | Colab `/content/` 에 업로드 | 필수 |
| `chat_log1_raw.json`, `chat_log2_raw.json` | 기능 3 | 이미 `feature3/`에 포함 | 업로드 불필요 |

- **업로드 방법(Colab):** 왼쪽 파일 영역(폴더 아이콘) → 드래그&드롭, 또는 우클릭 → 업로드.
  (Colab 세션이 끊기면 업로드 파일은 사라지므로, 그 기능을 다시 돌릴 땐 재업로드합니다.)
- **원본 출처(AIHub):** https://www.aihub.or.kr/ — 데이터셋 상세·전처리는 아래 [데이터셋](#데이터셋) 섹션 참고.
- **기능 3 입력**(`chat_log1_raw.json`, `chat_log2_raw.json`)은 익명화·PII 마스킹을 마친 JSON으로 **이미 저장소에 포함**되어 있어 추가 업로드가 필요 없습니다.

---

## 단계별 상세 (Colab)

### 1) 기능 1 — 감정 분석  `feature1/sentiment_analysis.ipynb`
1. Colab에서 열기 → 런타임 유형 **GPU(T4)** 설정
2. `감성대화말뭉치(최종데이터)_Training.xlsx`, `..._Validation.xlsx`를 `/content/`에 업로드
3. **런타임 → 모두 실행(Run all)**
4. 학습 → Test 평가 → 앙상블 추론이 진행되고 **Accuracy / Macro-F1 / Confusion Matrix**가 출력됩니다.
5. 산출물이 **`MyDrive/feature1/`** 에 자동 저장: `chaeon_feature1_checkpoint/`, `svm_model.pkl`, `vectorizer.pkl`, `result.txt`, `log.txt`

### 2) 기능 2 — 공격성 탐지  `feature2/aggression_detection.ipynb`
1. Colab에서 열기 → **GPU(T4)** 설정
2. `talksets-train-1_aihub.csv`를 `/content/`에 업로드
3. **Run all** → 전처리 → KoELECTRA 학습·평가 → TF-IDF 베이스라인 비교
4. 산출물이 **`MyDrive/feature2/`** 에 자동 저장: `chaeon_feature2_model/`, `result.txt`, `log.txt`

### 3) 기능 3 — 상태 변화 분석  `feature3/colab_feature3_member1.ipynb`
1. Colab에서 열기 → **Run all** (업로드할 데이터 없음)
2. 자동으로: 저장소 clone → 드라이브 인증 클릭 → 기능 1·2 모델 자동 로드
   → 실제 채팅(`chat_log1_raw.json`) → 기능 1·2 라벨링 → 기능 3 날짜별 분석
3. 결과: **`daily_report.json` 생성** + 화면에 날짜별 × 발신자별 상태 표·해석 시각화

> **자주 묻는 문제**
> - *기능 3이 "모델이 없다"며 멈춰요* → 기능 1·2 노트북을 먼저 **Run all** 해 드라이브에 모델을 만든 뒤 다시 실행하세요.
> - *드라이브 인증 창이 떠요* → 본인 구글 계정으로 **허용**을 누르면 됩니다. (모델 저장·로드에 필요)
> - *업로드한 데이터가 사라졌어요* → Colab 세션이 끊기면 `/content/` 업로드 파일은 삭제됩니다. 다시 돌릴 때 재업로드하세요.

---

## 실행하면 생성되는 파일

> 모델·체크포인트 등 용량 큰 산출물은 **코드 실행 시 재생성**되므로 제출 필수는 아닙니다.
> 재현에 꼭 필요한 것은 **코드 + 데이터 + 시드(42)** 입니다.

| 기능 | 파일 | 위치 | 내용 |
|---|---|---|---|
| 1 | `chaeon_feature1_checkpoint/`, `svm_model.pkl`, `vectorizer.pkl` | `MyDrive/feature1/` | 기능 3이 불러올 모델 |
| 1 | `result.txt`, `log.txt` | `MyDrive/feature1/` | 시드·최종 metric / 실행 로그 |
| 2 | `chaeon_feature2_model/` | `MyDrive/feature2/` | 기능 3이 불러올 모델 |
| 2 | `result.txt`, `log.txt` | `MyDrive/feature2/` | 시드·최종 metric / 실행 로그 |
| 3 | `daily_report.json` | `MyDrive/feature3_outputs/<입력명>_<실행시각>/` | **날짜별 × 발신자별 상태 리포트 (최종 산출물)** |
| 3 | `labeled.json`, `label_review.csv/.txt` | 〃 | 기능1·2 라벨링 결과 / 라벨 검수 |

---

## 데이터셋

> 원본(AIHub·실제 채팅)은 라이선스·개인정보 문제로 저장소에 포함하지 않으며, 전처리·분할은 모두 각 노트북 안에서 자동 수행됩니다. (중간 산출물도 깃에 올리지 않고 매 실행 시 원본에서 재생성)

### 기능 1 — 감정 분석
- **출처**: AIHub 감성대화 말뭉치 — https://www.aihub.or.kr/ → "감성대화 말뭉치" 검색·신청
- **원본 파일** (Colab `/content/`에 업로드): `감성대화말뭉치(최종데이터)_Training.xlsx`, `감성대화말뭉치(최종데이터)_Validation.xlsx`
- **전처리**(`sentiment_analysis.ipynb` Cell 3에서 자동 수행):
  1. 두 xlsx에서 `감정_대분류`, `사람문장1~3`만 읽어 통합 → **58,271행**, 사람문장 1·2·3을 한 문장으로 결합
  2. 이진 라벨링: `기쁨` → 긍정(1) / 그 외 감정 → 부정(0)  (원본 분포: 긍정 7,339 / 부정 50,932)
  3. **1:1 다운샘플링**(seed=42) → **14,678행** (긍정·부정 각 7,339)
  4. `text` 기준 중복 제거(누출 방지) 후 **Stratified 8:1:1 분할**(seed=42) → Train 11,742 / Val 1,468 / Test 1,468

### 기능 2 — 공격성 탐지
- **출처**: AIHub 텍스트 윤리 검증 데이터셋 — https://www.aihub.or.kr/ → 해당 데이터셋 신청·다운로드
- **원본 파일** (Colab `/content/`에 업로드, 파일명 정확히 일치 필요): `talksets-train-1_aihub.csv`
- **전처리**(`aggression_detection.ipynb` Cell 4에서 자동 수행):
  1. csv 로드 → **70,593행**
  2. intensity 점수 3단계 라벨링: `<1.0` → 비공격(0) / `1.0~1.8` → 약한공격(1) / `≥1.8` → 강한공격(2)
  3. 결측·공백·중복(text 기준) 제거 → **69,309행** (0=29,487 / 1=21,995 / 2=17,827)
  4. 다운샘플링 생략(원본 규모 유지) · 중간파일 `aggression_processed_subset.csv` 저장(깃 제외, 실행 시 재생성)
  5. **Stratified 8:1:1 분할**(seed=42) → Train 55,447 / Val 6,931 / Test 6,931

### 기능 3 — 상태 변화 분석 (실제 채팅 로그)
- **출처**: 팀원의 지인이 진행한 **실제 카카오톡 단체 채팅** (팀원을 통해 전달받음)
- **동의**: 데이터를 제공한 지인을 통해 **익명화 전제 사용 동의**를 확인했습니다.
- **익명화·전처리**(`feature3/preprocess_chat_log.py`): 발신자 `User_A`~`User_D` 가명화 · 전화번호/이메일/계좌 등 **PII 마스킹** · 이모티콘/사진/시스템 표기 제거 · timestamp ISO 8601(KST) 변환
- **결과물**(익명화 완료, 저장소 포함): `feature3/chat_log1_raw.json`, `feature3/chat_log2_raw.json`

> 저장소에 포함된 채팅 로그는 **익명화·PII 마스킹을 마친 데이터**이며, 원본(가명화 전) 로그는 포함하지 않습니다.

---

## 재현성 & 적법성 (테스트셋 누출 방지)

| 항목 | 값 |
|---|---|
| Seed | 42 (random / numpy / torch / transformers) |
| 분할 | Train / Validation / Test = 80 / 10 / 10 (Stratified) |
| 평가 지표 | Accuracy, Macro-F1, Confusion Matrix |

- **학습**: 기능 1·2 모두 **Train + Validation 만** 사용 (Test 누출 없음)
- **모델 선택**: **Validation 기준** 가장 좋은 모델 채택 (`load_best_model_at_end=True`)
- **테스트**: 학습 종료 후 **Test 로 1회만** 측정
- **기능 3**: 별도 학습이 없으며 학습/검증/테스트셋을 사용하지 않습니다. (규칙 기반 분석)
- 상세 결과: `feature1/result.txt`, `feature2/result.txt`, 각 `featureN/README.md`

---

## 프로젝트 개요 (기능 설명)

### 기능 1 — 감정 분석
채팅 메시지를 긍정/부정으로 분류
- 입력: 채팅 메시지 → 출력: positive(1) / negative(0)
- 모델: **KcELECTRA + SVM(TF-IDF) Soft Voting 앙상블 (7:3)**

### 기능 2 — 공격성 탐지
채팅 메시지의 공격성 수준을 3단계로 분류
- 입력: 채팅 메시지 → 출력: 0(비공격) / 1(약한공격) / 2(강한공격)
- 모델: **KoELECTRA-small** (+ TF-IDF 로지스틱 회귀 비교 베이스라인)

### 기능 3 — 상태 변화 분석
기능 1·2 결과로 사용자의 상태 변화를 분석 (부정 감정 / 공격성 / 참여량 변화)
- 분석 당일 vs 직전 7일 baseline 비교 → 상태 판정
- 최종 결과: 🟢 평소와 비슷 / 🟡 평소와 조금 다름 / 🟠 평소와 꽤 다름 / ⚪ 데이터 부족

---

## 저장소 구조

```
CHAEON-AIPROGRAMMING
│
├── README.md                            # 본 문서 (실행 설명서)
├── requirements.txt
│
├── feature1
│   ├── sentiment_analysis.ipynb         # 최종 제출 모델 (학습+평가)
│   ├── README.md · result.txt
│   └── model_selection/                 # 모델 선정 비교 실험 (세 후보)
│
├── feature2
│   ├── aggression_detection.ipynb       # 최종 제출 모델 (학습+평가)
│   ├── README.md · result.txt
│   └── model_selection/                 # 모델 선정 비교 실험 (두 후보)
│
├── feature3
│   ├── colab_feature3_member1.ipynb     # 기능1·2 모델 → 기능3 통합 노트북
│   ├── state_change_analysis.py         # 기능3 엔진 (지표·상태 판정·리포트)
│   ├── preprocess_chat_log.py           # 카카오톡 CSV → 입력 JSON 변환·익명화
│   ├── chat_log1_raw.json · chat_log2_raw.json   # 실데이터 (익명화 완료)
│   └── README.md
│
└── docs
    └── 기능3_설계결과_보고서.pdf
```

- 각 기능 상세 실행법: [`feature1/README.md`](feature1/README.md) · [`feature2/README.md`](feature2/README.md) · [`feature3/README.md`](feature3/README.md)

---

## (옵션) 모델 선정 비교 실험 재현

각 기능의 최종 모델을 어떻게 골랐는지(후보 비교 → 선정)를 재현하려면 아래 노트북을 Colab(GPU)에서 실행합니다.
**채점 필수는 아니며**, 최종 모델의 정식 학습·평가는 위 `sentiment_analysis.ipynb` / `aggression_detection.ipynb` 에서 진행됩니다.

| 기능 | 노트북 | 비교 후보 | 업로드할 데이터 |
|---|---|---|---|
| 1 | `feature1/model_selection/model_selection_experiment.ipynb` | KLUE-RoBERTa / KcELECTRA+SVM / KcELECTRA+Bi-LSTM | 기능 1과 동일한 xlsx 2개 |
| 2 | `feature2/model_selection/model_selection_experiment.ipynb` | TF-IDF+로지스틱회귀 / KoELECTRA-small | 기능 2와 동일한 csv |

실행하면 후보 비교표가 출력되고 `test_result.txt`가 자동 생성됩니다. (동일 분할·동일 지표로 1회 측정 — 테스트셋 누출 없음)

---

## 제출 구성

- **제출 파일**: GitHub Repository 링크 · 최종 보고서 PDF · 발표 자료 PDF
- **코드**: 기능1·2·3 코드 (+ 모델 선정 비교 실험) · 실행 설명서(본 README) · `requirements.txt`
- **데이터셋**: 원본 출처(AIHub) 링크 + 별도 전달 + 전처리 방법(본 README·각 README)

---

## 개발자

명지대학교 AI프로그래밍 팀 프로젝트 — 팀명: 채온(CHAEON)
