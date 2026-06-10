# 기능 1 — 모델 선정 비교 실험

> 이 폴더는 **최종 제출 모델이 아니라**, 어떤 모델을 쓸지 "정하기 위한" 비교(시뮬레이션) 과정입니다.
> 여기서 선정된 모델의 정식 학습·평가는 상위 폴더의 `sentiment_analysis.ipynb` 에서 진행합니다.

## 구성

| 파일 | 내용 |
|---|---|
| `model_selection_experiment.ipynb` | 세 후보를 동일 분할·동일 지표로 비교하는 노트북 |
| `baseline_tfidf_lr.py` | 베이스라인(TF-IDF + 로지스틱회귀) 재현 스크립트 |
| `test_result.txt` | 비교 실험 요약 결과 (실행 시 자동 생성) |
| `requirements.txt` | 노트북 실행에 필요한 패키지 (실행 시 자동 생성) |

## 베이스라인 + 비교한 후보 (동일 Test set / Seed=42 / Stratified 8:1:1)

| 구분 | 구성 | Accuracy | Macro-F1 |
|---|---|---|---|
| 베이스라인 | TF-IDF + 로지스틱회귀 | 0.8903 | 0.8903 |
| 후보1 | KLUE-RoBERTa 단독 | 0.9693 | 0.9693 |
| **후보2** | **KcELECTRA + SVM 7:3 앙상블** | **0.9707** | **0.9707** |
| 후보3 | KcELECTRA + Bi-LSTM 7:3 앙상블 | 0.9700 | 0.9700 |

- 베이스라인(0.8903) 대비 세 후보 모두 **0.97대로 향상**됐고, 후보 간 차이는 근소하여 가장 높은 Macro-F1을 보인 **후보2(KcELECTRA + SVM 7:3)** 를 최종 채택했습니다.
- **적법성**: 학습=Train만 / 모델 선택=Validation / 측정=Test 1회 (테스트셋 누출 없음)

## 실행 방법 (Colab)

1. `model_selection_experiment.ipynb` 를 Colab(GPU)에서 엽니다.
2. AIHub 감성대화 말뭉치 원본 2개(`감성대화말뭉치(최종데이터)_Training.xlsx`, `_Validation.xlsx`)를 `/content/` 에 업로드합니다.
3. **런타임 → 모두 실행(Run all)** → 세 후보 비교표 출력 + `test_result.txt` 자동 생성.

> 베이스라인만 따로 재현하려면: 같은 xlsx 2개를 준비한 뒤 `python baseline_tfidf_lr.py`
> (노트북과 동일한 전처리·8:1:1 분할로 Test 1468개에서 Accuracy/Macro-F1 출력)

> 데이터 준비·전처리 상세는 상위 폴더 [`../README.md`](../README.md) 참고.
