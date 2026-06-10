# 기능 2 - 공격성 탐지 (Aggression Detection)

채팅 메시지의 **공격성 수준을 3단계**로 분류합니다.

- 입력: 채팅 메시지(문장)
- 출력: 0(비공격) / 1(약한공격) / 2(강한공격)
- 모델: **KoELECTRA-small** (메인) + TF-IDF 로지스틱 회귀(비교 베이스라인)

> 환경 세팅·실행 순서·데이터 배치·전처리 상세는 **루트 [`../README.md`](../README.md)** 에 통합되어 있습니다.
> 이 문서는 기능 2의 **폴더 구성 · 고유 디테일 · 결과**만 담습니다.

---

## 폴더 구성

```
feature2/
├─ aggression_detection.ipynb   # 전처리 + 학습 + 평가 전체 코드 (셀 순서대로 실행) — 최종 제출 모델
├─ result.txt                    # 사용 시드, 데이터 분할, 최종 metric 기록
└─ model_selection/              # 모델 선정 비교 실험 (두 후보 비교 — 최종 제출 모델 아님)
   ├─ model_selection_experiment.ipynb
   ├─ test_result.txt
   └─ README.md
```

> 의존성은 저장소 루트의 `requirements.txt` 하나로 통합되어 있습니다.

---

## 실행 (요약)

> 전체 실행 순서·환경(Colab/GPU)·데이터셋 배치·전처리는 루트 README 참고. 여기엔 기능 2 고유 사항만 적습니다.

- **업로드 파일** (Colab `/content/`, 파일명 정확히 일치): `talksets-train-1_aihub.csv`
- `aggression_detection.ipynb` → **Run all** → 환경설정 → 전처리 → KoELECTRA 학습·평가 → TF-IDF 베이스라인 비교
- 전처리 중간파일 `aggression_processed_subset.csv` 생성 (깃 제외, 실행 시 재생성 — 원본 CSV + 코드로 동일 복원)
- **기능 3 연동**: 마지막 셀이 산출물을 `MyDrive/feature2/` 에 자동 저장 (`chaeon_feature2_model/`, `result.txt`, `log.txt`) → 기능 3이 이 경로를 그대로 로드 (드라이브 인증 클릭만 필요)

---

## 재현성 & 결과

| 항목 | 값 |
|------|----|
| Seed | 42 (transformers set_seed + random_state) |
| Split | Train 55,447 / Validation 6,931 / Test 6,931 (80:10:10, Stratified) |
| Model | KoELECTRA-small (3-class) |
| **Accuracy** | **0.6432** |
| **Macro-F1** | **0.6026** |
| Binary(공격 vs 비공격) | Accuracy 0.8156 / F1 0.8273 |

- 평가 지표: Accuracy, Macro-F1, Confusion Matrix · 상세는 [`result.txt`](result.txt)
- 데이터셋·전처리 상세: 루트 [`../README.md`](../README.md) 의 데이터셋 섹션

### 적법성 (테스트셋 누출 방지)
- 학습: **Train + Validation 만** 사용
- 모델 선택: **Validation Macro-F1 기준** 가장 좋은 epoch 모델 채택 (`load_best_model_at_end=True`, `metric_for_best_model="f1"`)
- 테스트: 학습 종료 후 Test 로 **1회만** 측정
- 베이스라인(TF-IDF + 로지스틱 회귀)도 **KoELECTRA와 동일한 8:1:1 분할**로 평가하여 공정 비교 (공식 성능은 KoELECTRA 기준)
