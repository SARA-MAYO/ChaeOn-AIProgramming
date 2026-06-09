# CHAEON - AI Programming Project

## 빠른 시작 (이것만 따라 하면 됩니다)

모든 모델은 **본인 구글 드라이브(MyDrive)** 를 통해 자동 연동됩니다.
파일 이동·이름 변경·경로 수정·수동 복사가 **전혀 없습니다.**

1. **기능 1** — `feature1/sentiment_analysis.ipynb` 를 Colab에서 열고, AIHub 감성대화 데이터 업로드 후 **런타임 → 모두 실행(Run all)**
   → 학습 결과가 `MyDrive/feature1/` 폴더(모델 + `result.txt` + `log.txt`)로 **자동 저장**
2. **기능 2** — `feature2/aggression_detection.ipynb` 를 Colab에서 열고, AIHub 윤리검증 데이터 업로드 후 **Run all**
   → 학습 결과가 `MyDrive/feature2/` 폴더(모델 + `result.txt` + `log.txt`)로 **자동 저장**
3. **기능 3** — `feature3/colab_feature3_member1.ipynb` 를 Colab에서 열고 **Run all**
   → 저장소 자동 clone → 기능1·2 모델을 드라이브에서 **자동 로드** → 원문→기능1→기능2→기능3 날짜별 분석 → 최종 `daily_report.json` 생성

> - 추가로 필요한 사람 작업: **구글 드라이브 인증 클릭**, 그리고 기능1·2의 **데이터 파일 업로드**(제출물과 함께 별도 전달 — 라이선스상 저장소에 미포함)뿐입니다.
> - 기능 3은 시작 시 위 4개 파일이 드라이브에 있는지 **자동 검사**하고, 없으면 **어떤 파일이 부족한지 안내 후 종료**합니다. (해당 기능 노트북을 먼저 Run all 하면 됨)
> - GPU·모델 없이 기능 3 로직만 빠르게 보려면: `cd feature3 && python state_change_analysis.py` (자세한 내용은 [`feature3/README.md`](feature3/README.md))

---

## 프로젝트 개요

채온(CHAEON)은 팀 프로젝트 채팅 로그를 분석하여
커뮤니케이션 악화 가능성을 조기에 탐지하는 AI 시스템입니다.

본 프로젝트는 다음 3개 기능으로 구성됩니다.

### 기능 1 - 감정 분석

채팅 메시지를 긍정 / 부정으로 분류

- 입력: 채팅 메시지
- 출력: positive(1) / negative(0)
- 모델: KcELECTRA + SVM(TF-IDF) Soft Voting 앙상블 (7:3)

---

### 기능 2 - 공격성 탐지

채팅 메시지의 공격성 수준을 분류

- 입력: 채팅 메시지
- 출력: 0(비공격) / 1(약공격) / 2(강공격)
- 모델: KoELECTRA-small (+ TF-IDF 로지스틱 회귀 비교 베이스라인)

---

### 기능 3 - 상태 변화 분석

기능 1, 2 결과를 이용하여 사용자의 상태 변화를 분석

분석 항목

- 부정 감정 변화
- 공격성 변화
- 참여량 변화

최종 결과

- 🟢 평소와 비슷
- 🟡 평소와 조금 다름
- 🟠 평소와 꽤 다름
- ⚪ 데이터 부족

---

# 저장소 구조

```
CHAEON-AIPROGRAMMING
│
├── README.md
├── requirements.txt
│
├── feature1
│   ├── sentiment_analysis.ipynb        # 최종 제출 모델 (학습+평가)
│   ├── README.md
│   ├── result.txt
│   ├── model_selection/                # 모델 선정 비교 실험 (세 후보 비교)
│   │   ├── model_selection_experiment.ipynb
│   │   ├── test_result.txt
│   │   └── README.md
│   ├── dataset/
│   └── model/
│
├── feature2
│   ├── aggression_detection.ipynb      # 최종 제출 모델 (학습+평가)
│   ├── README.md
│   ├── result.txt
│   ├── model_selection/                # 모델 선정 비교 실험 (두 후보 비교)
│   │   ├── model_selection_experiment.ipynb
│   │   ├── test_result.txt
│   │   └── README.md
│   ├── dataset/
│   └── model/
│
├── feature3
│   ├── README.md
│   ├── state_change_analysis.py     # 지표 계산 + 상태 판정 + 날짜별 리포트 생성
│   ├── preprocess_chat_log.py       # 카카오톡 CSV → 입력 JSON 변환 + 익명화
│   ├── colab_feature3_member1.ipynb # 기능1·2 모델 → 기능3 통합 시연 노트북
│   ├── chat_log1_raw.json           # 실데이터 입력 (전처리·익명화 완료)
│   ├── chat_log2_raw.json           # 실데이터 입력 (전처리·익명화 완료)
│   ├── sample_chat_log.json         # 라벨 붙은 입력 (단독 실행용)
│   └── daily_report.json            # 산출물 — 날짜별 상태 리포트 (실행 시 생성)
│
├── docs
│   └── 기능3_설계결과_보고서.pdf
│
└── datasets
    └── dataset_information.md
```

---

# 데이터셋

## 기능 1

AIHub 감성대화 데이터셋 사용

전처리

- 기쁨 → 긍정(1)
- 나머지 감정 → 부정(0)

## 기능 2

AIHub 텍스트 윤리 검증 데이터셋 사용

전처리

- intensity < 1.0 → 0 (비공격)
- 1.0 ≤ intensity < 1.8 → 1 (약한공격)
- intensity ≥ 1.8 → 2 (강한공격)

## 기능 3 (실제 채팅 로그)

기능 3의 입력으로 사용한 채팅 로그는 **팀원의 지인으로부터 전달받은 실제 카카오톡 단체 채팅** 대화입니다.

- **출처**: 팀원의 지인이 실제로 진행한 카카오톡 단체 채팅 (팀원을 통해 전달받음)
- **동의**: 데이터를 제공한 지인을 통해 **익명화를 전제로 한 데이터 사용 동의**를 확인했습니다.
- **익명화·전처리**: 전달받은 원본 로그는 공개 전 다음 전처리를 거쳐 개인정보를 제거했습니다.
  - 발신자는 `User_A`~`User_D` 형태로 **가명화**
  - 전화번호·주민번호·이메일·링크·계좌/카드번호 등 **PII 마스킹**(`[전화번호]`, `[이메일]`, `[번호]` 등)
  - 이모티콘·사진·동영상 등 미디어/시스템 표기(placeholder) 제거
- **전처리 코드·결과물**:
  - 코드: `feature3/preprocess_chat_log.py`
  - 결과(익명화 완료): `feature3/chat_log1_raw.json`, `feature3/chat_log2_raw.json`
  - 자세한 변환 방법은 [`feature3/README.md`](feature3/README.md) 참고

> 저장소에 포함된 채팅 로그는 **익명화·PII 마스킹을 마친 데이터**이며, 원본(가명화 전) 로그는 포함하지 않습니다.

---

# 실행 환경 (권장 작업 방식)

본 프로젝트는 **Google Colab 환경에서 실행하는 것을 기준**으로 작성되었습니다.

| 구분 | 실행 환경 | 비고 |
|---|---|---|
| 기능 1 학습·평가 | **Google Colab 필수** | 구글 드라이브 마운트·세션 업로드(`/content/`)·GPU 사용을 전제로 작성됨 |
| 기능 2 학습·평가 | **Google Colab 필수** | 〃 |
| 기능 3 통합 실행 | **Google Colab 필수** | 기능1·2 모델을 드라이브에서 로드 |
| 기능 3 로직 단독 확인 | 로컬 Python 가능 | `python feature3/state_change_analysis.py` (GPU·드라이브·모델 불필요) |

- 학습(기능 1·2)에는 **GPU 런타임 권장** (런타임 → 런타임 유형 변경 → 하드웨어 가속기: GPU)
- 기능 1·2·3 통합 노트북은 Colab 전용 기능(`google.colab`, 드라이브 마운트)을 사용하므로 **로컬에서는 그대로 실행되지 않습니다.** 채점·재현 시 Colab에서 실행해 주세요.
- 데이터·GPU 없이 기능 3의 분석 로직만 빠르게 보려면 위 표의 마지막 항목(로컬 단독 실행)을 사용하세요.

# 실행 순서 (Run all 3번)

기능 1·2·3 모델은 **모두 본인 구글 드라이브(MyDrive)** 를 통해 자동 연동됩니다.
파일 이동·이름 변경·경로 수정·수동 복사가 전혀 필요 없습니다. (구글 드라이브 인증 클릭만 하면 됩니다.)

| 순서 | 노트북 | 할 일 | 자동으로 일어나는 것 |
|---|---|---|---|
| 1 | `feature1/sentiment_analysis.ipynb` | 데이터 업로드 후 **Run all** | 학습 → `MyDrive/feature1/` 에 모델 + `result.txt` + `log.txt` 자동 저장 |
| 2 | `feature2/aggression_detection.ipynb` | 데이터 업로드 후 **Run all** | 학습 → `MyDrive/feature2/` 에 모델 + `result.txt` + `log.txt` 자동 저장 |
| 3 | `feature3/colab_feature3_member1.ipynb` | **Run all** | 저장소 자동 clone → 기능1·2 모델 Drive에서 자동 로드 → 원문→기능1→기능2→기능3 날짜별 분석→`daily_report.json` 생성 |

> 기능 3은 첫 셀에서 저장소를 자동 clone하고, 시작 시 기능1·2 모델 4개 파일이 Drive에 있는지 검사합니다.
> 없으면 **어떤 파일이 부족한지 안내하고 멈춥니다.** (해당 기능 노트북을 먼저 Run all 하면 됨)
>
> 단, 기능 1·2의 **데이터 파일**은 라이선스(로그인·재배포 제한)상 저장소에 포함하지 않으므로 **제출물과 함께 별도로 전달**하며,
> Colab 세션(`/content/`)에 직접 업로드하는 단계만 남습니다. (원본 출처는 AIHub — 데이터 배치법·링크: 각 기능 README 2번 항목)

- 각 기능 상세 실행법: [`feature1/README.md`](feature1/README.md), [`feature2/README.md`](feature2/README.md), [`feature3/README.md`](feature3/README.md) 참고

---

# 제출 구성

교수님 제출 파일

- GitHub Repository 링크
- 최종 보고서 PDF
- 발표 자료 PDF

코드 제출 파일

- 기능1 학습 코드 (+ 모델 선정 비교 실험 `feature1/model_selection/`)
- 기능2 학습 코드 (+ 모델 선정 비교 실험 `feature2/model_selection/`)
- 기능3 코드
- 실행 설명서(README)
- requirements.txt

데이터셋

- 공개 데이터셋 링크 제공
- 전처리 방법 설명 포함

---

# 재현성 확인

학습 시 사용 설정

- Seed = 42
- Train / Validation / Test = 80 / 10 / 10
- Stratified Split 사용

평가 지표

- Accuracy
- Macro-F1
- Confusion Matrix

---

# 개발자

명지대학교 AI프로그래밍 팀 프로젝트

팀명 : 채온(CHAEON)