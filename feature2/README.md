# 기능 2 - 공격성 탐지 (Aggression Detection)

채팅 메시지의 **공격성 수준을 3단계**로 분류합니다.

- 입력: 채팅 메시지(문장)
- 출력: 0(비공격) / 1(약한공격) / 2(강한공격)
- 모델: **KoELECTRA-small** (메인) + TF-IDF 로지스틱 회귀(비교 베이스라인)

---

## 폴더 구성

```
feature2/
├─ aggression_detection.ipynb   # 전처리 + 학습 + 평가 전체 코드 (셀 순서대로 실행)
├─ result.txt                    # 사용 시드, 데이터 분할, 최종 metric 기록
├─ dataset/                      # (참고용 빈 폴더 — 원본은 Colab 세션 /content/ 에 업로드)
└─ model/                        # (참고용 빈 폴더 — 학습 모델은 /content/ 및 MyDrive 에 저장됨)
```

> 의존성은 저장소 루트의 `requirements.txt` 하나로 통합되어 있습니다.

---

## 1. 환경 세팅 (Google Colab 기준)

본 프로젝트는 **Google Colab** 환경에서 작업·실행하는 것을 기준으로 합니다.

1. `aggression_detection.ipynb` 를 Google Colab 으로 엽니다.
2. 상단 메뉴 **런타임 → 런타임 유형 변경 → 하드웨어 가속기: GPU (T4 등)** 로 설정합니다.
3. **첫 번째 셀(환경 세팅)** 을 실행하면 필요한 패키지가 자동 설치됩니다.

- Colab 기본 런타임 (Python 3) 기준
- 학습에는 **GPU 런타임 권장**

---

## 2. 데이터셋 준비

본 기능은 **AIHub 텍스트 윤리 검증 데이터셋** 원본을 사용합니다.

> ⚠️ 원본 데이터는 AIHub 라이선스(로그인·이용 신청 필요, 재배포 제한)상 **저장소에 포함하지 않습니다.**
> 제출물과 함께 **원본 파일을 직접 전달**하며, AIHub에서 직접 받을 수도 있습니다.

**배치 방법** — 원본 파일을 **Colab 세션(`/content/`)** 에 업로드하되,
파일명은 노트북이 읽는 이름과 정확히 같아야 합니다.

- `talksets-train-1_aihub.csv`  ← 노트북이 읽는 이름 (AIHub 원본 파일명 그대로)

원본을 AIHub에서 직접 받는 경우: https://www.aihub.or.kr/
(정확한 데이터셋 페이지는 `../datasets/dataset_information.md` 참고)

### 데이터 준비 과정 (노트북의 '1. 데이터 전처리' 셀에서 자동 수행)

원본을 읽어 **노트북 실행 중에** 아래 순서로 가공하고, 중간 산출물을 저장합니다.

1. **로드** — `talksets-train-1_aihub.csv` → **70,593행** (컬럼: `text`, `intensity` 등)
2. **라벨링 (intensity binning, 3단계)**
   - intensity < 1.0 → 비공격(0)
   - 1.0 ≤ intensity < 1.8 → 약한공격(1)
   - 1.8 이상 → 강한공격(2)
3. **정제** — 결측·공백·중복(text 기준) 제거 → **69,309행**
4. **다운샘플링 생략** — 기능1과 달리 클래스 균등 샘플링을 하지 않고 **원본 규모를 그대로 유지**
   (정제 후 분포: 0=29,487 / 1=21,995 / 2=17,827)
5. **중간 파일 저장** — `aggression_processed_subset.csv` 생성 (이 파일도 깃에 올리지 않음 / 실행 시 재생성됨)
6. 이후 Cell 8(KoELECTRA)이 이 파일을 **Stratified 8:1:1 분할** (seed=42) → Train 55,447 / Validation 6,931 / Test 6,931
   (TF-IDF 베이스라인도 KoELECTRA와 동일한 train_df/test_df 를 재사용해 공정 비교)

> 별도 전처리 스크립트는 필요 없습니다. 노트북 셀만 순서대로 실행하면 위 과정이 자동 수행됩니다.

---

## 3. 실행 방법 (Colab)

1. `aggression_detection.ipynb` 를 Colab 에서 엽니다.
2. 위 2번대로 `talksets-train-1_aihub.csv` 를 세션(`/content/`)에 업로드합니다.
3. 상단 메뉴 **런타임 → 모두 실행 (Run all)**, 또는 셀을 **위에서부터 순서대로** 실행합니다.

실행 순서: 환경설정 → 데이터 확인 → 전처리 → KoELECTRA 학습·평가 → TF-IDF 베이스라인 비교

> 🔗 **기능 3 연동**: 마지막 셀이 학습된 KoELECTRA 모델을 **본인 구글 드라이브(MyDrive)** 의
> `chaeon_feature2_model/` 에 자동 저장합니다. 기능 3 노트북이 이 경로를 그대로 읽으므로
> 별도 작업이 필요 없습니다. (드라이브 인증 클릭만)

### 실행 시 자동 생성되는 파일

노트북을 끝까지 실행하면 작업 경로(`/content/`)에 아래 파일들이 생성됩니다.

| 파일 / 폴더 | 생성 위치 | 내용 | 비고 |
|---|---|---|---|
| `log.txt` | 노트북 마지막 셀 | 실행 시작~최종 metric 전체 기록 | 결과 증빙용 |
| `aggression_processed_subset.csv` | 전처리 셀 (`df.to_csv()`) | **전처리 완료된 데이터셋** | 전처리 산출물 (코드 실행 시 재생성됨) |
| `results/` | `TrainingArguments(output_dir)` | 학습 중 체크포인트 | 임시 파일 (`save_total_limit=1`로 1개만 유지) |

> `aggression_processed_subset.csv`는 원본을 전처리한 결과물입니다. 노트북 실행 시 자동 재생성되므로, 원본 CSV와 코드만 있으면 동일하게 복원됩니다. `results/`는 학습 중 임시 파일이라 제출에서 빼도 무방합니다.

---

## 4. 데이터셋 정보

- 출처: AIHub 텍스트 윤리 검증 데이터셋
- 전처리(intensity 점수 → 3단계 라벨):
  - intensity < 1.0 → 비공격(0)
  - 1.0 ≤ intensity < 1.8 → 약한공격(1)
  - 그 외 → 강한공격(2)
- 자세한 정보: [`../datasets/dataset_information.md`](../datasets/dataset_information.md)

---

## 5. 재현성 & 결과

| 항목 | 값 |
|------|----|
| Seed | 42 (transformers set_seed + random_state) |
| Split | Train 55,447 / Validation 6,931 / Test 6,931 (80:10:10, Stratified) |
| Model | KoELECTRA-small (3-class) |
| **Accuracy** | **0.64** |
| **Macro-F1** | **0.60** |
| Binary(공격 vs 비공격) | Accuracy 0.8145 / F1 0.8263 |

> ⚠️ 위 수치는 best-epoch(validation) 선택 적용 **이전** 기준입니다.
> 노트북을 다시 Run all 한 뒤 `result.txt`/`log.txt` 와 위 표를 최신 값으로 갱신하세요.

- 평가 지표: Accuracy, Macro-F1, Confusion Matrix
- 상세 결과는 [`result.txt`](result.txt) 참고

### 적법성 (테스트셋 누출 방지)
- 학습: **Train + Validation 만** 사용
- 모델 선택: **Validation Macro-F1 기준** 가장 좋은 epoch 모델 채택 (`load_best_model_at_end=True`, `metric_for_best_model="f1"`)
- 테스트: 학습 종료 후 Test 로 **1회만** 측정
- 베이스라인(TF-IDF + 로지스틱 회귀)도 **KoELECTRA와 동일한 8:1:1 분할**로 평가하여 공정하게 비교합니다. (공식 성능은 KoELECTRA 기준)
