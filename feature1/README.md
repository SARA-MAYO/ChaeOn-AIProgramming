# 기능 1 - 감성 분석 (Sentiment Analysis)

채팅 메시지를 **긍정(1) / 부정(0)** 으로 분류합니다.

- 입력: 채팅 메시지(문장)
- 출력: positive(1) / negative(0)
- 모델: **KcELECTRA + SVM(TF-IDF) Soft Voting 앙상블 (7:3)**

> 환경 세팅·실행 순서·데이터 배치·전처리 상세는 **루트 [`../README.md`](../README.md)** 에 통합되어 있습니다.
> 이 문서는 기능 1의 **폴더 구성 · 고유 디테일 · 결과**만 담습니다.

---

## 폴더 구성

```
feature1/
├─ sentiment_analysis.ipynb   # 학습 + 평가 전체 코드 (셀 순서대로 실행) — 최종 제출 모델
├─ result.txt                 # 사용 시드, 데이터 분할, 최종 metric 기록
├─ model_selection/           # 모델 선정 비교 실험 (세 후보 비교 — 최종 제출 모델 아님)
│  ├─ model_selection_experiment.ipynb
│  ├─ test_result.txt
│  └─ README.md
├─ dataset/                   # (참고용 빈 폴더 — 원본은 Colab 세션 /content/ 에 업로드)
└─ model/                     # (참고용 빈 폴더 — 학습 모델은 /content/ 및 MyDrive 에 저장됨)
```

> 의존성은 저장소 루트의 `requirements.txt` 하나로 통합되어 있습니다.

---

## 실행 (요약)

> 전체 실행 순서·환경(Colab/GPU)·데이터셋 배치·전처리는 루트 README 참고. 여기엔 기능 1 고유 사항만 적습니다.

- **업로드 파일** (Colab `/content/`): `감성대화말뭉치(최종데이터)_Training.xlsx`, `..._Validation.xlsx`
- `sentiment_analysis.ipynb` → **Run all** → 학습 → Test 평가 → 앙상블 추론, **Accuracy / Macro-F1 / Confusion Matrix** 출력
- **기능 3 연동**: 마지막 셀이 산출물을 `MyDrive/feature1/` 에 자동 저장 (`chaeon_feature1_checkpoint/`, `svm_model.pkl`, `vectorizer.pkl`, `result.txt`, `log.txt`) → 기능 3이 이 경로를 그대로 로드 (드라이브 인증 클릭만 필요)
- 모델·체크포인트는 실행 시 재생성되므로 제출 필수 아님 — 재현에 필요한 건 **코드 + 데이터 + 시드(42)**

---

## 재현성 & 결과

| 항목 | 값 |
|------|----|
| Seed | 42 (random / numpy / torch / transformers) |
| Split | Train 11,742 / Validation 1,468 / Test 1,468 (80:10:10, Stratified) |
| Model | KcELECTRA(0.7) + SVM TF-IDF(0.3) Soft Voting |
| **Accuracy** | **0.9714** |
| **Macro-F1** | **0.9714** |

- 평가 지표: Accuracy, Macro-F1, Confusion Matrix · 상세는 [`result.txt`](result.txt)
- 데이터셋·전처리 상세: 루트 [`../README.md`](../README.md) 의 데이터셋 섹션

### 적법성 (테스트셋 누출 방지)
- 학습: **Train + Validation 만** 사용 (KcELECTRA · SVM · TF-IDF 모두 Train 으로만 fit)
- 모델 선택: Validation 기준 (`load_best_model_at_end=True`)
- 테스트: 학습 종료 후 Test 로 **1회만** 측정
