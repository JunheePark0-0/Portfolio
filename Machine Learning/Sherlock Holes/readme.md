# 🕵️‍♂️ Sherlock Holes: 포트홀 발생 예측 및 원인 분석 AI 서비스

## 📖 프로젝트 개요

**Sherlock Holes**는 서울시의 도로, 교통, 기상, 인구 데이터를 기반으로 **포트홀(도로 파임) 발생 위험 지역을 예측**하고, **XAI(Explainable AI)** 기술을 활용하여 그 **발생 원인을 규명**함으로써 도로 유지보수의 효율성을 높이고 시민 안전을 확보하기 위한 프로젝트입니다.

단순히 위험 지역을 예측하는 것을 넘어, **"왜"** 위험한지 설명(Explain)하고, 위험도를 낮추기 위한 **개선 방향(Actionable Insight)**까지 제시하는 것을 목표로 합니다. (본 프로젝트로 **장려상을 수상**하였습니다.)

## ✨ 핵심 프로세스 및 전략

본 프로젝트는 **데이터 전처리 -> 모델링 -> 원인 분석 -> 서비스 구현**의 4단계 프로세스로 진행되었으며, 각 단계별 핵심 전략은 다음과 같습니다.

### 1. 데이터 전처리 (Data Preprocessing)
-   **지오코딩 & 역지오코딩**: `geokakao`와 `requests`를 활용하여 주소 데이터와 위경도 좌표를 상호 변환하고, 행정동 단위로 데이터를 매핑했습니다.
-   **불균형 데이터 처리 (SMOTE)**: 포트홀 발생 데이터(Positive)가 현저히 적은 문제를 해결하기 위해 SMOTE 오버샘플링 기법을 적용하여 클래스 균형을 맞췄습니다.
-   **데이터 병합**: 도로, 교통량, 기상, 인구 등 이질적인 데이터를 시공간 기준으로 통합했습니다.

### 2. 머신러닝 모델링 (Modeling)
-   **XGBoost Classifier**: 결측치 처리와 특성 중요도 파악에 용이한 XGBoost를 메인 모델로 채택했습니다.
-   **최적화**: `GridSearchCV`를 통해 Hyperparameter를 튜닝하고, Stratified Split을 통해 검증 신뢰도를 높였습니다.

### 3. XAI 기반 원인 분석 (Explainable AI)
-   **SHAP (Global/Local Importance)**: 모델이 왜 특정 지역을 위험하다고 판단했는지, 변수별 기여도(교통량, 배수 등급 등)를 시각화하여 설명했습니다.
-   **DiCE (Counterfactual Explanations)**: "트럭 통행량이 10% 줄어든다면 안전할까?"와 같은 반사실적 질문을 통해 구체적인 개선 방향을 제시했습니다.

### 4. 웹 서비스 구현 (Web Service)
-   **Streamlit 대시보드**: 분석 결과를 직관적으로 보여주는 웹 서비스를 구축했습니다. 사용자가 주소와 날짜를 입력하면 위험도와 상세 리포트를 즉시 확인할 수 있습니다.

## 📂 프로젝트 구조

```
Sherlock Holes/
├── DATA/                  # 데이터 전처리 관련 코드
│   ├── 1. Pothole_전처리.ipynb
│   ├── 2. 역지오코딩.ipynb
│   ├── 3. 자치구별 기온, 습도, 강수량, 인구 수.ipynb
│   └── 4. 자치구 Merge.ipynb
│
├── Model/                 # 모델링 및 실험 코드
│   ├── 1. 전처리+Classification.ipynb
│   ├── 2. Regression.ipynb
│   ├── 3. Classification_Again.ipynb
│   ├── 4. Prediction.ipynb
│   └── 5. final_model.ipynb   # 최종 모델링 코드
│
├── XAI/                   # XAI 분석 코드
│   ├── XAI_Model_SHAP.ipynb            # SHAP 분석
│   └── XAI_Model_Counterfactual.ipynb  # DiCE 분석
│
├── Report/                # 웹 서비스 및 리포트 관련 파일
│   ├── streamlit.py       # Streamlit 웹 애플리케이션 메인 코드
│   ├── Pothole_Report.ipynb
│   └── (이미지 및 리소스 파일들)
│
└── README.md              # 프로젝트 설명 파일
```

## 🛠️ 주요 구성 요소

-   **`DATA/`**: 다양한 원천 데이터(도로, 기상, 인구)를 정제하고 하나로 병합하는 전처리 스크립트 모음입니다. 지오코딩 로직이 포함되어 있습니다.
-   **`Model/`**: XGBoost 모델의 학습, 튜닝, 평가 과정이 담겨 있습니다. `final_model.ipynb`에서 최종 모델을 생성하고 저장합니다.
-   **`XAI/`**: 학습된 모델을 바탕으로 SHAP과 DiCE 분석을 수행하는 노트북입니다. 분석 결과는 리포트 생성에 활용됩니다.
-   **`Report/`**: `streamlit.py`를 통해 웹 서비스를 실행하며, 사용자와 상호작용하는 UI/UX를 담당합니다.

## 🚀 실행 방법

1.  **라이브러리 설치**: 필요한 패키지(`xgboost`, `shap`, `streamlit`, `geokakao` 등)를 설치합니다.
2.  **웹 서비스 실행**:
    ```bash
    cd Report
    streamlit run streamlit.py
    ```
3.  **모델 재학습 (선택)**: `Model/final_model.ipynb`를 실행하여 모델을 새로 학습시킬 수 있습니다.
