# 기능 1 - 감성 분석 (Sentiment Analysis)

채팅 메시지를 **긍정(1) / 부정(0)** 으로 분류합니다.

- 입력: 채팅 메시지(문장)
- 출력: positive(1) / negative(0)
- 모델: **KcELECTRA + SVM(TF-IDF) Soft Voting 앙상블 (7:3)**

---

## 폴더 구성

```
feature1/
├─ sentiment_analysis.ipynb   # 학습 + 평가 전체 코드 (셀 순서대로 실행)
├─ result.txt                 # 사용 시드, 데이터 분할, 최종 metric 기록
├─ dataset/                   # (참고용 빈 폴더 — 원본은 Colab 세션 /content/ 에 업로드)
└─ model/                     # (참고용 빈 폴더 — 학습 모델은 /content/ 및 MyDrive 에 저장됨)
```

> 의존성은 저장소 루트의 `requirements.txt` 하나로 통합되어 있습니다.

---

## 1. 환경 세팅 (Google Colab 기준)

본 프로젝트는 **Google Colab** 환경에서 작업·실행하는 것을 기준으로 합니다.

1. `sentiment_analysis.ipynb` 를 Google Colab 으로 엽니다.
2. 상단 메뉴 **런타임 → 런타임 유형 변경 → 하드웨어 가속기: GPU (T4 등)** 로 설정합니다.
3. **첫 번째 셀(라이브러리 설치)** 을 실행하면 필요한 패키지가 자동 설치됩니다.

- Colab 기본 런타임 (Python 3) 기준
- 학습에는 **GPU 런타임 권장**

---

## 2. 데이터셋 준비

본 기능은 **AIHub 감성대화 말뭉치** 원본을 사용합니다.

> ⚠️ 원본 데이터는 AIHub 라이선스(로그인·이용 신청 필요, 재배포 제한)상 **저장소에 포함하지 않습니다.**
> 제출물과 함께 **원본 파일을 직접 전달**하며, AIHub에서 직접 받을 수도 있습니다.

**배치 방법** — 아래 두 파일을 **Colab 세션(`/content/`)** 에 업로드합니다. (노트북이 읽는 이름과 정확히 같아야 함)

- `감성대화말뭉치(최종데이터)_Training.xlsx`
- `감성대화말뭉치(최종데이터)_Validation.xlsx`

원본을 AIHub에서 직접 받는 경우: https://www.aihub.or.kr/ 에서 "감성대화 말뭉치" 검색·신청
(정확한 데이터셋 페이지는 `../datasets/dataset_information.md` 참고)

### 데이터 준비 과정 (노트북의 '2. 데이터 로드·전처리·8:1:1 분할' 셀에서 자동 수행)

원본을 그대로 읽어 **노트북 실행 중에** 아래 순서로 가공합니다. 별도 전처리 스크립트나 중간 저장 파일은 없습니다.

1. **로드·통합** — 두 xlsx에서 `감정_대분류`, `사람문장1~3` 컬럼만 읽어 통합
2. **텍스트 결합** — 사람문장1·2·3을 한 문장으로 합침
3. **중복 제거** — `text` 기준 중복 행 제거 (train/test 누출 방지)
4. **이진 라벨링** — `기쁨` → 긍정(1) / 그 외 감정 → 부정(0)
5. **1:1 다운샘플링** (seed=42) — 부정을 긍정 수에 맞춰 무작위 추출
6. **Stratified 8:1:1 분할** (seed=42) → Train / Validation / Test

> 정확한 행 수와 metric은 노트북 실행 후 출력 및 [`result.txt`](result.txt) 에서 확인하세요.

---

## 3. 실행 방법 (Colab)

1. `sentiment_analysis.ipynb` 를 Colab 에서 엽니다.
2. 위 2번대로 두 xlsx 파일을 세션(`/content/`)에 업로드합니다.
3. 상단 메뉴 **런타임 → 모두 실행 (Run all)**, 또는 셀을 **위에서부터 순서대로** 실행합니다.

실행하면 학습 → Test 평가 → 앙상블 추론까지 진행되고,
**Accuracy / Macro-F1 / Confusion Matrix** 와 예시 10개가 출력됩니다.

> 🔗 **기능 3 연동**: 마지막 셀이 산출물을 **본인 구글 드라이브의 `MyDrive/feature1/` 폴더**에 모아 자동 저장합니다.
> (`chaeon_feature1_checkpoint/`, `svm_model.pkl`, `vectorizer.pkl`, `result.txt`, `log.txt`)
> 기능 3 노트북이 이 경로를 그대로 읽으므로 별도 작업이 필요 없습니다. (드라이브 인증 클릭만)

### 실행 시 자동 생성되는 파일

노트북을 끝까지 실행하면 작업 경로(`/content/`)에 아래 파일들이 생성됩니다. (모두 코드 실행 중 자동 생성되며, 별도 제출은 필수가 아닙니다)

| 파일 / 폴더 | 생성 위치 | 내용 | 비고 |
|---|---|---|---|
| `log.txt` | 노트북 마지막 셀 | 실행 시작~최종 metric 전체 기록 | 결과 증빙용 |
| `confusion_matrix_sentiment_only.png` | 마지막 평가 셀 | 혼동행렬 이미지 | 결과 시각화 |
| `final_model/` | `trainer.save_model()` | 학습 완료된 최종 모델(가중치 + 토크나이저) | 용량 큼 · 코드 실행 시 재생성됨 |
| `saved_models/` | `TrainingArguments(output_dir)` | 학습 중 체크포인트 | 임시 파일 (`save_total_limit=1`로 1개만 유지) |

> 재현에 필요한 것은 **코드 + 데이터 + 시드(42)** 입니다. 모델 파일(`final_model/`, `saved_models/`)은 실행하면 다시 생성되므로 제출에서 빼도 무방합니다.

---

## 4. 데이터셋 정보

- 출처: AIHub 감성대화 말뭉치
- 전처리:
  - `기쁨` → 긍정(1)
  - 나머지 감정 → 부정(0)
  - 클래스 균형을 위해 1:1 다운샘플링
- 자세한 정보: [`../datasets/dataset_information.md`](../datasets/dataset_information.md)

---

## 5. 재현성 & 결과

| 항목 | 값 |
|------|----|
| Seed | 42 (random / numpy / torch / transformers) |
| Split | Train 11,742 / Validation 1,468 / Test 1,468 (80:10:10, Stratified) |
| Model | KcELECTRA(0.7) + SVM TF-IDF(0.3) Soft Voting |
| **Accuracy** | **0.9714** |
| **Macro-F1** | **0.9714** |

- 평가 지표: Accuracy, Macro-F1, Confusion Matrix
- 상세 결과는 [`result.txt`](result.txt) 참고

### 적법성 (테스트셋 누출 방지)
- 학습: **Train + Validation 만** 사용 (KcELECTRA · SVM · TF-IDF 모두 Train 으로만 fit)
- 모델 선택: Validation 기준 (`load_best_model_at_end=True`)
- 테스트: 학습 종료 후 Test 로 **1회만** 측정
