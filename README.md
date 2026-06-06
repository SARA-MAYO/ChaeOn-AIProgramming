# CHAEON - AI Programming Project

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
│   ├── sentiment_analysis.ipynb
│   ├── README.md
│   ├── result.txt
│   ├── dataset/
│   └── model/
│
├── feature2
│   ├── aggression_detection.ipynb
│   ├── README.md
│   ├── result.txt
│   ├── dataset/
│   └── model/
│
├── feature3
│   ├── README.md
│   ├── report_generator.py          # (작성 예정)
│   ├── sample_chat_log.json         # (작성 예정)
│   ├── analysis_result.json         # (작성 예정)
│   └── sample_report.json           # (작성 예정)
│
├── docs
│   ├── 기능3_설계서.pdf              # (작성 예정)
│   └── 발표자료.pdf                  # (작성 예정)
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

---

# 실행 환경

- **Google Colab 기준** (Python 3 런타임)
- 학습 시 **GPU 런타임 권장** (런타임 → 런타임 유형 변경 → 하드웨어 가속기: GPU)
- 각 기능 상세 실행법: [`feature1/README.md`](feature1/README.md), [`feature2/README.md`](feature2/README.md) 참고

---

# 제출 구성

교수님 제출 파일

- GitHub Repository 링크
- 최종 보고서 PDF
- 발표 자료 PDF

코드 제출 파일

- 기능1 학습 코드
- 기능2 학습 코드
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