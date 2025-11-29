# PORTFOLIO - 박준희

## 👋 About Me
**"데이터의 가치를 발굴하고, 현실의 문제를 해결하는 개발자 박준희입니다."**

숫자로 현실을 표현하고 미래를 예측하는 데이터 분석에 흥미를 느껴 데이터에서 최대한의 가치를 창출하는 **데이터 사이언티스트**가 되고자 끊임없이 공부하고 있습니다. 

최근에는 사람의 언어로 컴퓨터와 소통하는 **자연어처리** 분야에 새로운 충격을 받아 Fine-tuning, RAG, Agent 등 다양한 방면으로 지식을 넓혀 나가고 있습니다. 

음악, 주식 등 **실생활과 밀접**하고 **해석이 직관적**인 주제를 좋아하며, 데이터에서 의미 있는 인사이트를 도출하고, 도메인 지식과 연결지어 제대로 된 해석을 할 때 보람을 느낍니다. 

빠르게 발전하는 데이터 사이언스 분야의 특성에 발맞추어 지속적으로 탐구하고 성장하는 중입니다 :)

---

## 📅 Timeline

| 기간 | 프로젝트 / 활동 | 주요 역할 | 성과 |
|:---:|:---|:---|:---|
| 2025.10 ~ Current | **Stock Market Agent** | 뉴스/공시 크롤링, LangGraph 기반 브리핑 에이전트 개발 | (진행 중) 미국 장 마감 브리핑 자동화 |
| 2025.10 ~ 2025.10 | **Gmail Agent** | LangGraph 기반 멀티 에이전트 워크플로우 설계 | 이메일 비서 에이전트 프로토타입 개발 |
| 2025.11.22 ~ 2025.11.23 | **MixUP (고문헌 현대화)** | RAG 기반 번역 실험, Multi-turn 프롬프트 전략 수립 | **최우수상 수상**, 고문헌 번역 성능 최적화 |
| 2025.07 ~ 2025.08 | **LG Aimers 7기** | 시계열 Feature Engineering, LSTM 수요 예측 모델링 | 복잡한 시계열 패턴 학습 모델 구현 |
| 2025.03 ~ 2025.06 | **Sherlock Holes** | 포트홀 예측 모델링(XGBoost), XAI 분석, 웹 서비스 | **장려상 수상**, 도로 위험도 예측 서비스 |
| 2025.05 ~ 2025.05 | **Spine X-ray Analysis** | YOLOv8 기반 척추뼈 탐지 및 질환 분류 파이프라인 구축 | 척추 질환 진단 보조 시스템 개발 |
| 2025.02 ~ 2025.02 | **CAT-FICIAL DECODER** | ViT + GPT-2 결합 Image Captioning 모델 구현 | 이미지의 문맥을 이해하는 캡셔닝 모델 개발 |
| 2024.11 ~ 2024.11 | **Vision Map (청소년 데이터 공모전)** | 상담 챗봇용 데이터 전처리 및 T5 모델 Fine-tuning | 진로 상담 챗봇 프로토타입 개발 |
| 2024.09 ~ 2024.12 | **#오늘 #듣기 #좋은 #노래** | 멜론 크롤링 최적화, LLM 태깅, 임베딩(Word2Vec) 추천 | 일기 기반 맞춤형 노래 추천 시스템 구현 |
| 2024.07 ~ 2024.10 | **FSI AIxData Challenge** | 금융 도메인 NER 튜닝, 숫자 마스킹 로직 개발 | **최우수상 수상**, 개인정보 비식별화 모델 구축 |

---

## 🚀 Projects

### 🧠 Natural Language Processing (NLP) & Agent

#### 1. [Stock Market Agent](Natural%20Language%20Processing/Stock%20Market%20Agent/README.md) (Work In Progress)
- **주제**: 미국 주식 시장 마감 후, 시장 흐름과 주요 기업 이슈를 분석하여 브리핑을 작성하는 AI 에이전트
- **Tech**: `LangGraph`, `OpenAI`, `Crawling`, `SQLite`
- **My Role**:
    - 뉴스 및 SEC 공시 데이터 수집 크롤러 및 DB 구축
    - **Host(진행자)-Analyst(분석가)** 페르소나 기반의 브리핑 작성 에이전트 개발

#### 2. [Gmail Agent](Natural%20Language%20Processing/Gmail%20Agent/README.md)
- **주제**: 이메일 검색(Fetcher)과 답장 작성(Responder)을 수행하는 LangGraph 기반 멀티 에이전트
- **Tech**: `LangGraph`, `Gmail API`, `Python`
- **My Role**: 이메일 처리 워크플로우 설계 및 사용자 피드백 루프 구현

#### 3. [FSI AIxData Challenge 2024](Natural%20Language%20Processing/FSI%20AIxData%20Challenge/README.md) 🏆
- **주제**: 금융 데이터 내 개인정보 비식별화(Masking) 및 위험 평가 서비스
- **Tech**: `KLUE-BERT`, `Solar LLM`, `RAG`, `Regex`
- **My Role**: 금융 도메인 특화 NER Fine-tuning, 숫자 데이터(전화번호 등) 마스킹 로직 고도화
- **성과**: **금융보안원장상(최우수상) 수상**

#### 4. [#오늘 #듣기 #좋은 #노래](Natural%20Language%20Processing/%23오늘%23듣기%23좋은%23노래/README.md)
- **주제**: 사용자의 일기에서 감정을 추출하여 상황에 맞는 노래를 추천하는 시스템
- **Tech**: `Recommendation System`, `Word2Vec`, `FastText`, `Crawling`
- **My Role**: 멜론 데이터 크롤링 속도 50% 단축, LLM 활용 감정 태깅 및 임베딩 모델 구현

#### 5. [MixUP](Natural%20Language%20Processing/MixUP/README.md) 🏆
- **주제**: 고문헌을 현대적인 문체로 변환하는 번역 프로젝트
- **Tech**: `RAG (ChromaDB)`, `Prompt Engineering (Multi-turn)`
- **My Role**: RAG 실험 및 3-Turn(직역-윤문-검수) 프롬프트 전략 수립
- **성과**: **최우수상 수상** (연합 해커톤 MixUP Track 2)

#### 6. [Vision Map](Natural%20Language%20Processing/Vision%20Map/README.md)
- **주제**: 청소년 진로 상담을 위한 챗봇
- **Tech**: `T5`, `Fine-tuning`
- **My Role**: 상담 데이터 전처리 및 T5 모델 Fine-tuning

---

### 🤖 Machine Learning (ML)

#### 1. [Sherlock Holes](Machine%20Learning/Sherlock%20Holes/README.md) 🏆
- **주제**: 서울시 포트홀 발생 위험 지역 예측 및 XAI 기반 원인 분석
- **Tech**: `XGBoost`, `SHAP`, `DiCE`, `Streamlit`, `Geocoding`
- **My Role**: 데이터 전처리(SMOTE, 지오코딩), 예측 모델링, 위험 평가 리포트 작성, 웹 서비스(Streamlit) 구현
- **성과**: **장려상 수상**

#### 2. [LG Aimers 7기](Machine%20Learning/LG%20Aimers%207기/README.md)
- **주제**: 시계열 데이터를 활용한 제품 수요 예측
- **Tech**: `LSTM`, `XGBoost`, `Time-series Analysis`
- **My Role**: 시계열 Feature Engineering 및 LSTM 모델링

---

### 👁️ Computer Vision (CV)

#### 1. [Spine X-ray Analysis](Computer%20Vision/Spine_XRAY/README.md)
- **주제**: 척추 X-ray 이미지 기반 뼈 탐지 및 질환 분류 시스템
- **Tech**: `YOLOv8`, `Object Detection`
- **My Role**: 탐지(Detection) 및 분류(Classification) 2-Stage 파이프라인 구축

#### 2. [CAT-FICIAL DECODER](Computer%20Vision/CAT-FICIAL%20DECODER/readme.md)
- **주제**: Vision Transformer와 GPT-2를 결합한 이미지 캡셔닝
- **Tech**: `ViT`, `GPT-2`, `PyTorch`
- **My Role**: VisionGPT 모델 아키텍처 구현 및 학습

---

## 🛠️ Skills
- **Languages**: Python, R, SQL
- **AI/ML**: PyTorch, Scikit-learn, LangChain, LangGraph, Hugging Face
- **Data & Etc**: Pandas, NumPy, Selenium, BeautifulSoup, Streamlit, SQLite, Git
