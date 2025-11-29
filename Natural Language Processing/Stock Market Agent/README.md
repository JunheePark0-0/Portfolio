# 📈 Stock Market Agent: 미국 주식 시장 마감 브리핑 에이전트

## 📖 프로젝트 개요

**Stock Market Agent**는 미국 주식 시장이 마감된 후(한국 시간 오전 7시경), 하루 동안의 시장 흐름과 주요 기업의 이슈를 종합하여 **"장 마감 브리핑"을 자동으로 생성하는 AI 에이전트** 프로젝트입니다.

방대한 뉴스 기사와 공시 자료를 에이전트가 스스로 수집, 분석하여 **[오프닝] 시장 요약 -> [본문] 기업별 심층 분석 -> [결론] 전망**으로 이어지는 체계적인 방송 대본을 작성합니다. (현재 개발 진행 중인 프로젝트입니다.)

## 🕐 개발 기간 
2025.10 ~  (진행 중)

## ✨ 핵심 프로세스 및 전략

### 1. 뉴스 및 공시 데이터 수집 (Crawling & DB)
-   **News Crawler**: 주요 금융 뉴스 사이트에서 기업별 최신 기사의 제목, 본문, 메타데이터를 수집합니다.
-   **SEC Crawler**: EDGAR 시스템을 통해 기업의 주요 공시(Form 4 등 내부자 거래) 정보를 수집합니다.
-   **SQLite DB**: 수집된 비정형 텍스트 데이터를 기업별로 구조화된 데이터베이스(`News_DB`, `SEC_DB`)에 저장하여 에이전트가 효율적으로 검색할 수 있게 합니다.

### 2. 브리핑 작성 에이전트 (Agent)
-   **LangGraph 기반 ReAct 에이전트**: 에이전트가 **탐색(Search) -> 선별(Select) -> 독해(Read)**의 과정을 스스로 수행하며 정보를 수집합니다.
-   **Role-Playing 프롬프트**: 딱딱한 요약문이 아닌, 실제 방송처럼 **Host(진행자)**와 **Analyst(분석가)**가 대화를 주고받는 형식의 대본을 생성하도록 페르소나를 부여했습니다.

### 3. 향후 계획 (Future Works)
-   **Multi-Agent Debate**: 하나의 이슈에 대해 긍정론/부정론 등 서로 다른 관점을 가진 에이전트들이 토론을 통해 더 깊이 있는 분석을 도출하는 구조를 도입할 예정입니다.
-   **웹 서비스 확장**: 사용자가 관심 종목을 등록하면 매일 아침 맞춤형 브리핑을 제공하는 서비스로 발전시킬 계획입니다.

## 📂 프로젝트 구조

```
Stock Market Agent/
├── agent_main.py          # 에이전트 실행 메인 스크립트
├── crawling_main.py       # 크롤링 실행 메인 스크립트
│
├── config/                # 설정 파일 (Ticker 리스트 등)
│   ├── tickers.json
│   └── ticker_map.json
│
├── data/                  # 수집된 데이터 및 결과물 저장소
│   ├── News_DB/           # 기업별 뉴스 SQLite DB
│   ├── SEC_DB/            # SEC 공시 SQLite DB
│   └── Briefings/         # 생성된 브리핑 파일 (.md, .txt)
│
├── src/
│   ├── Agent/             # 에이전트 관련 코드
│   │   ├── prompts/       # 프롬프트 관리 (yaml)
│   │   ├── tools/         # 에이전트 사용 도구 (검색, 읽기 등)
│   │   └── data_fetcher.py
│   │
│   ├── Crawling/          # 크롤러 관련 코드
│   │   ├── news_crawling.py
│   │   ├── sec_crawling.py
│   │   └── *_db.py        # DB 핸들러
│   │
│   └── utils/             # 유틸리티 함수
│
└── README.md              # 프로젝트 설명 파일
```

## 🛠️ 주요 구성 요소

-   **`crawling_main.py`**: 뉴스 및 SEC 공시 데이터 수집을 실행하는 진입점입니다. `--ticker` 인자로 대상 기업을 지정합니다.
-   **`agent_main.py`**: 수집된 데이터를 바탕으로 브리핑을 생성하는 에이전트를 실행합니다.
-   **`src/Agent/tools/`**: 에이전트가 DB에서 뉴스를 검색(`search_news_headlines`)하고 본문을 읽는(`read_news_content`) 도구들이 정의되어 있습니다.
-   **`src/Agent/prompts/`**: 에이전트의 페르소나와 작업 지침이 담긴 YAML 프롬프트 파일들이 위치합니다.

## 🚀 실행 방법

1.  **뉴스 및 공시 데이터 수집**:
    ```bash
    # 예: 엔비디아(NVDA) 데이터 수집
    python crawling_main.py --ticker NVDA
    ```
2.  **브리핑 에이전트 실행**:
    ```bash
    # 예: 엔비디아(NVDA) 브리핑 생성
    python agent_main.py --ticker NVDA
    ```
