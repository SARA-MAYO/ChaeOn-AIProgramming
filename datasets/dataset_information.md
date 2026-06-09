# 데이터셋 정보

> **원본 데이터는 이 저장소에 포함하지 않습니다.**
> AIHub 라이선스(로그인·이용 신청 필요, 재배포 제한)상 깃에 올리지 않으며,
> 원본 파일은 **제출물과 함께 직접 전달**합니다. AIHub에서 직접 받을 수도 있습니다.
> 전처리/분할은 모두 각 기능의 노트북 안에서 자동 수행되며, 중간 산출물도 깃에 올리지 않습니다.

---

## 기능 1 - 감정 분석 (Sentiment Analysis)

- **출처**: AIHub 감성대화 말뭉치
- **링크**: https://www.aihub.or.kr/ → "감성대화 말뭉치" 검색·신청
- **원본 파일** (feature1/ 폴더에 배치):
  - `감성대화말뭉치(최종데이터)_Training.xlsx`
  - `감성대화말뭉치(최종데이터)_Validation.xlsx`

### 준비 과정 (sentiment_analysis.ipynb, Cell 3에서 자동 수행)

1. 두 xlsx에서 `감정_대분류`, `사람문장1~3` 컬럼만 읽어 통합 → **58,271행**
2. 사람문장 1·2·3을 한 문장으로 결합
3. 이진 라벨링: `기쁨` → 긍정(1) / 그 외 감정 → 부정(0)
   - 원본 분포: 긍정 7,339 / 부정 50,932
4. **1:1 다운샘플링** (seed=42) → **14,678행** (긍정 7,339 / 부정 7,339)
5. **Stratified 8:1:1 분할** (seed=42) → Train 11,742 / Val 1,468 / Test 1,468

- 중간 저장 파일 없음 (매 실행 시 원본에서 재생성)

---

## 기능 2 - 공격성 탐지 (Aggression Detection)

- **출처**: AIHub 텍스트 윤리 검증 데이터셋
- **링크**: https://www.aihub.or.kr/ → 해당 데이터셋 신청·다운로드
- **원본 파일** (feature2/ 폴더에 배치, 파일명 정확히 일치 필요):
  - `talksets-train-1_aihub.csv`
### 준비 과정 (aggression_detection.ipynb, Cell 4에서 자동 수행)

1. `talksets-train-1_aihub.csv` 로드 → **70,593행**
2. 라벨링 (intensity binning, 3단계):
   - intensity < 1.0 → 비공격(0)
   - 1.0 ≤ intensity < 1.8 → 약한공격(1)
   - intensity ≥ 1.8 → 강한공격(2)
3. 결측·공백·중복(text 기준) 제거 → **69,309행** (0=29,487 / 1=21,995 / 2=17,827)
4. **다운샘플링 생략** — 원본 규모 유지 (기능1과 반대)
5. 중간 파일 `aggression_processed_subset.csv` 저장 (깃 제외, 실행 시 재생성)
6. **Stratified 8:1:1 분할** (seed=42) → Train 55,447 / Val 6,931 / Test 6,931

---

## 공통 재현성 설정

- Seed = 42
- Train / Validation / Test = 80 / 10 / 10 (Stratified Split)
- 평가 지표: Accuracy, Macro-F1, Confusion Matrix
