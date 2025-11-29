# 📧 Gmail Agent: LangGraph 기반 이메일 비서

## 📖 프로젝트 개요

**Gmail Agent**는 LangGraph를 활용하여 **이메일 검색(Fetch)**과 **답장 작성(Respond)**을 자동화하는 멀티 에이전트 시스템입니다.

사용자의 자연어 명령을 이해하여 Gmail에서 필요한 메일을 찾아주고, 적절한 답장을 작성하여 전송까지 도와주는 AI 비서를 목표로 합니다. 사용자의 피드백을 반영하여 검색 결과를 정제하거나 답장 내용을 수정하는 **Human-in-the-loop** 구조를 갖추고 있습니다.

## 🕐 개발 기간 
2025.10 ~ 2025.10 (1개월)

## ✨ 핵심 프로세스 및 전략

### 1. Email Fetcher Agent (검색 에이전트)
-   **쿼리 파싱**: "지난주에 온 회의 관련 메일 찾아줘"와 같은 자연어 요청을 Gmail 검색 쿼리로 변환합니다.
-   **피드백 루프**: 검색 결과가 사용자의 의도와 다를 경우, 추가 피드백을 받아 검색 조건을 수정하고 재검색을 수행합니다.

### 2. Email Responder Agent (답장 에이전트)
-   **답장 생성**: "참석한다고 정중하게 답장해줘"라는 요청에 맞춰 LLM이 초안을 작성합니다.
-   **반복 수정 (Iterative Refinement)**: 사용자가 초안을 검토하고 수정 요청("좀 더 캐주얼하게 바꿔줘")을 하면, 에이전트가 이를 반영하여 다시 작성하는 과정을 반복합니다. 최종 승인 시에만 메일을 전송합니다.

### 3. 멀티 에이전트 오케스트레이션
-   **LangGraph**: 두 에이전트 간의 상태(State)를 공유하고 흐름을 제어하기 위해 LangGraph를 사용했습니다. Fetcher가 찾은 이메일 정보를 Responder에게 전달하여 끊김 없는 워크플로우를 구현했습니다.

## 📂 프로젝트 구조

```
Gmail Agent/
├── agent/                 # 에이전트 핵심 로직
│   ├── prompts/           # LLM 프롬프트 템플릿
│   ├── tools/             # Gmail API 호출 도구 (Tool)
│   └── py_files/          # 상태(State) 정의 및 스키마
│
├── gmail_api/             # Gmail API 연동 모듈
│   ├── get_emails.py      # 이메일 가져오기
│   └── send_emails.py     # 이메일 보내기
│
├── graphs/                # LangGraph 구조 시각화 이미지
├── ipynb_files/           # 모듈별 테스트 노트북
│
├── email_fetcher.py       # Fetcher 에이전트 정의
├── email_responder.py     # Responder 에이전트 정의
├── main.py                # 전체 파이프라인 실행 진입점
└── README.md              # 프로젝트 설명 파일
```

## 🛠️ 주요 구성 요소

-   **`email_fetcher.py`**: 사용자의 검색 요청을 처리하는 에이전트입니다. `query_parser` -> `email_collector` -> `feedback` 흐름을 가집니다.
-   **`email_responder.py`**: 답장 작성을 담당하는 에이전트입니다. `draft_generator` -> `human_review` -> `email_sender` 흐름을 가집니다.
-   **`gmail_api/`**: Google의 Gmail API와 통신하여 실제 메일을 읽고 쓰는 기능을 수행하는 저수준 함수들입니다.
-   **`main.py`**: 두 에이전트를 통합하여 실행하는 메인 스크립트입니다.

## 🚀 실행 방법

1.  **환경 설정**: 필요한 라이브러리를 설치하고 `.env` 파일에 Gmail API 인증 정보를 설정합니다.
    ```bash
    pip install -r requirements.txt
    ```
2.  **실행**: 메인 스크립트를 실행하여 에이전트와 대화를 시작합니다.
    ```bash
    python main.py
    ```
