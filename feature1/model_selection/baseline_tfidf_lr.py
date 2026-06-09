# -*- coding: utf-8 -*-
"""
[기능1 - 베이스라인] TF-IDF + 로지스틱 회귀
- 목적: 개발 모델(KcELECTRA + SVM 7:3 앙상블)의 비교 기준선.
- 분할: sentiment_analysis.ipynb 와 100% 동일한 전처리/분할을 재현한다.
        (기쁨=긍정(1)/그 외=부정(0), 중복제거, 1:1 다운샘플 seed=42,
         Stratified 8:1:1 seed=42 -> Train 11742 / Val 1468 / Test 1468)
- 평가: 개발 모델과 동일한 Test 1468개로 1회 측정 (Accuracy, Macro-F1)
- 적법성: 학습=Train만 / 측정=Test 1회 (테스트셋 누출 없음)
"""
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, classification_report

DATA_DIR = "../../.데이터셋"
TRAIN_XLSX = f"{DATA_DIR}/감성대화말뭉치(최종데이터)_Training.xlsx"
VALID_XLSX = f"{DATA_DIR}/감성대화말뭉치(최종데이터)_Validation.xlsx"
TARGET_COLS = ['감정_대분류', '사람문장1', '사람문장2', '사람문장3']

print("데이터 로드 + 전처리 (sentiment_analysis.ipynb 와 동일 분할)...")
raw = pd.concat([
    pd.read_excel(TRAIN_XLSX, usecols=TARGET_COLS),
    pd.read_excel(VALID_XLSX, usecols=TARGET_COLS),
], ignore_index=True)

def combine(row):
    s = []
    for c in ['사람문장1', '사람문장2', '사람문장3']:
        if pd.notna(row[c]):
            s.append(str(row[c]).strip())
    return " ".join(s)

raw['text'] = raw.apply(combine, axis=1)
raw = raw.drop_duplicates(subset=["text"]).reset_index(drop=True)
raw['감정_대분류'] = raw['감정_대분류'].str.strip()
raw['label'] = raw['감정_대분류'].apply(lambda x: 1 if x == '기쁨' else 0)

# 1:1 다운샘플링 (seed=42)
pos = raw[raw['label'] == 1]
neg = raw[raw['label'] == 0]
m = min(len(pos), len(neg))
balanced = pd.concat([
    pos.sample(n=m, random_state=42),
    neg.sample(n=m, random_state=42),
]).sample(frac=1, random_state=42).reset_index(drop=True)

# Stratified 8:1:1 (seed=42)
train_df, temp_df = train_test_split(
    balanced, test_size=0.20, random_state=42, stratify=balanced['label'])
valid_df, test_df = train_test_split(
    temp_df, test_size=0.50, random_state=42, stratify=temp_df['label'])

print(f"Train {len(train_df)} / Val {len(valid_df)} / Test {len(test_df)}")

# 베이스라인: TF-IDF + 로지스틱 회귀 (개발 모델과 동일한 Train/Test)
tfidf = TfidfVectorizer(max_features=5000)
X_train = tfidf.fit_transform(train_df['text'])
X_test = tfidf.transform(test_df['text'])

clf = LogisticRegression(max_iter=1000, random_state=42)
clf.fit(X_train, train_df['label'])
y_pred = clf.predict(X_test)
y_test = test_df['label']

acc = accuracy_score(y_test, y_pred)
mf1 = f1_score(y_test, y_pred, average='macro')

print("\n" + "=" * 60)
print(f"[기능1 베이스라인 / TF-IDF + 로지스틱 회귀 / Test {len(y_test)}개]")
print("=" * 60)
print(f"Accuracy : {acc:.4f}")
print(f"Macro-F1 : {mf1:.4f}")
print(classification_report(y_test, y_pred, target_names=['부정(0)', '긍정(1)'], digits=4))
