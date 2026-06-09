# 기능 2 — 모델 선정 비교 실험

> 이 폴더는 **최종 제출 모델이 아니라**, 어떤 모델을 쓸지 "정하기 위한" 비교(시뮬레이션) 과정입니다.
> 여기서 선정된 모델의 정식 학습·평가는 상위 폴더의 `aggression_detection.ipynb` 에서 진행합니다.

## 구성

| 파일 | 내용 |
|---|---|
| `model_selection_experiment.ipynb` | 두 후보를 동일 분할·동일 지표로 비교하는 노트북 |
| `test_result.txt` | 비교 실험 요약 결과 (실행 시 자동 생성) |

## 비교한 후보 (동일 Test set / Seed=42 / Stratified 8:1:1)

| 후보 | 구성 | Accuracy | Macro-F1 |
|---|---|---|---|
| 후보1 | TF-IDF + 로지스틱 회귀 (베이스라인) | 0.5501 | 0.50 |
| **후보2** | **KoELECTRA-small (3-class)** | **0.64** | **0.60** |

- Accuracy·Macro-F1 모두에서 베이스라인보다 우수한 **후보2(KoELECTRA-small)** 를 최종 채택했습니다.
  (클래스 불균형을 고려해 Macro-F1을 1차 선정 기준으로 사용)
- **적법성**: 두 후보 모두 학습=Train만 / 측정=동일 Test 1회 (테스트셋 누출 없음)

## 실행 방법 (Colab)

1. `model_selection_experiment.ipynb` 를 Colab(GPU)에서 엽니다.
2. AIHub 텍스트 윤리 검증 데이터셋 원본(`talksets-train-1_aihub.csv`)을 `/content/` 에 업로드합니다.
3. **런타임 → 모두 실행(Run all)** → 두 후보 비교표 출력 + `test_result.txt` 자동 생성.

> 데이터 준비·전처리 상세는 상위 폴더 [`../README.md`](../README.md) 참고.
