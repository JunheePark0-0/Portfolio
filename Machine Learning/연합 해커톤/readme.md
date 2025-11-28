## KUBIGxYBIGTA 연합 해커톤

#### 기간 및 인원
기간 : 2024.11.08-2024.11.09 (1일) 

인원 : 4

#### 🎞 주요 내용
온라인 광고 클릭률 예측

#### 🪪 역할

데이터셋 전처리 

test와 교집합 필터링

변수 불균형 해소를 위한 Undersampling


#### 💻 프로젝트 흐름

**[데이터셋 전처리]**
- Undersampling
   -  데이터셋 불균형이 원인
   -  타겟 y (범주형, 0과 1) 에서 0의 비율이 1보다 훨씬 높음을 확인
   -  1의 비율에 맞춰서 0에서 undersampling 진행
   -  (oversampling도 고려했지만, 데이터셋의 크기를 고려하여 undersampling 진행)
     
- test와 교집합
   - 주목적은 ‘범용성 있는 모델’이 아닌, **‘test set을 잘 예측하는 모델’**
   - test set에 **함께 존재하는 변수**가 아니거나 test data에 **존재하지 않는 범주**의 경우 제거
   - 데이터 크기를 줄이기 위한 방법
     
- Feature Engineering
    - **Hash Encoding** (+ 파생변수 생성)
        - 고차원의 범주형 데이터를 인코딩할 때 사용하는 방법
        - 상관계수가 높았던 변수들을 골라 둘을 묶은 변수로 hash encoding 진행
    - Label Encoding
    - Clipping
        - 이상치나 특정 범주에 해당하는 데이터가 너무 적은 경우(특정 threshold 미만)
        - 가장 빈도수가 높은 값으로 대체
    - 파생변수 생성
        - Random Forest로 변수중요도 확인, 상관관계 분석 후 파생변수 생성
    - Feature Selection
        - Stepwise를 통해 선택된 조합으로 학습
     
          
**[시도 - 변수 불균형 해소를 위한 Undersampling]**
- 원인
    - 매우 큰 데이터셋
    - 범주형 변수들의 불균형
      
- 진행 과정
    - 각 변수에서 범주의 분포를 확인
    - 가장 데이터 개수가 많은 범주 제외, 나머지를 새로운 범주로 묶기
    - 가장 데이터 개수가 많은 범주에서 undersampling 진행, 나머지 데이터와 merge
            
- 평가
    - train error는 큰 폭으로 감소!
    - 하지만.. test error는 오히려 증가
    - 즉, overfitting….

**[Modeling]**
- lightgbm 과 xgb model을 base model로,

  logistic regression을 meta model 로 스태킹 진행


#### ❕ 인사이트
데이터 전처리의 중요성 - 모델 못지 않게 중요하다! 

overfitting은 생각보다 쉽게 발생한다.. 

체계적인 모델링 과정의 어려움과 필요성

#### 💡 활용 기술
`Python` `Undersampling` `Encoding` `Classification` `Model Stacking` `Logistic Regression` 

#### 🏆 성과
0.67543의 Test Accuracy
