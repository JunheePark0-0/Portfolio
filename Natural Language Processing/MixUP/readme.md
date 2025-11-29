# MixUP: Multi-turn 기반 고문헌 현대화 프로젝트

## 📖 프로젝트 개요

해당 프로젝트는 한자, 고어, 영어 등이 혼용된 오래된 문헌을 일반 독자가 이해하기 쉬운 현대적인 문체로 변환하는 프로젝트로, **연합 해커톤 MixUP의 Track 2 태스크**입니다.

다양한 접근법을 실험한 결과, 최종적으로 **Multi-turn (다단계 대화)** 프롬프팅 전략이 가장 우수한 성능을 보여 핵심 모델로 채택되었으며, 그 성과를 인정받아 **최우수상을 수상**하였습니다.

## 🕐 개발 기간 
- 2025.11.22 ~ 11.23

## ✨ 핵심 전략: 3-Turn (생성 → 윤문 → 검수)

단순히 한 번의 프롬프트로 문장을 변환하는 대신, 세 단계의 체계적인 프로세스를 통해 품질을 극대화합니다. 이 전략은 RAG 없이도 높은 성능을 달성했습니다.

### 1. 1단계: 의미 보존 번역 (초벌 직역)
-   `LLM`: 원문의 의미와 정보가 누락되지 않도록 최대한 직역에 가까운 초벌 번역을 생성합니다.

### 2. 2단계: 자연스러운 문체 변환 (윤문)
-   `LLM`: 1단계에서 생성된 딱딱한 직역 문장을 입력받아, 현대적인 신문 기사체와 같이 자연스럽고 읽기 편한 문장으로 다듬습니다.

### 3. 3단계: 원문 대조 및 최종 검수 (품질 관리)
-   `LLM`: 원문과 2단계에서 윤문된 문장을 최종적으로 비교합니다. 혹시 누락된 정보(인명, 지명, 날짜 등)나 의미 왜곡이 없는지 검수하고, 문제가 있다면 복원하여 최종 결과물을 완성합니다.

## 🧪 실험 과정: RAG (Retrieval-Augmented Generation)

성능 개선을 위한 가설 중 하나로, LLM에 유사한 변환 예시(Few-shot)를 동적으로 제공하면 더 일관성 있고 수준 높은 결과물을 생성할 것이라 판단하여 RAG를 실험했습니다.

-   **Vector DB 구축**: `BAAI/bge-m3` 임베딩 모델과 `ChromaDB`를 활용하여 고문헌-현대어 문장 쌍을 저장했습니다.
-   **결과**: 이 접근법은 모델이 특정 패턴이나 문체를 학습하는 데 도움을 주었으나, 최종 성능 평가에서는 잘 설계된 3-Turn 프롬프트 전략이 더 우수한 결과를 보여 최종 모델에서는 제외되었습니다.

## 📂 프로젝트 구조

```
MixUP/
├── MixUP_비비빅_발표자료.pdf
├── readme.md
├── baseline/
│   ├── baseline_openai.py  # OpenAI 모델 기본 성능 측정
│   └── baseline_solar.py   # Solar 모델 기본 성능 측정
├── Evaluate/
│   ├── evaluate.py         # 결과물 성능 평가 스크립트
│   └── metrics.py          # 평가 지표 정의
├── Experiments/
│   ├── solar_generate_test.py
│   └── solar_run_experiments.py # 실험 실행 스크립트
├── Multi Turn/
│   ├── multi_turn2.py      # 3-Turn 핵심 로직 (RAG 없음)
│   └── multi_turn2_rag_re.py # [실험용] RAG + 3-Turn 로직
├── prompts/
│   ├── prompt_1.py         # 다양한 프롬프트 템플릿
│   └── ...
└── RAG/
    ├── rag.py              # RAG 관련 유틸리티
    ├── run_rag.py          # RAG DB 생성 및 관리
    └── chroma_db_bge/      # Vector DB (Chroma)
```

## 🛠️ 주요 구성 요소

-   **`Multi Turn/`**: 본 프로젝트의 최종 모델인 **3-Turn 변환 전략**의 핵심 코드가 있습니다.
-   **`RAG/`**: 성능 개선을 위해 시도했던 RAG 실험 코드입니다.
-   **`prompts/`**: 각 변환 단계(직역, 윤문, 검수)에서 사용되는 다양한 프롬프트 템플릿을 관리합니다.

## 🚀 실행 방법

1.  **필요 라이브러리 설치**: `requirements.txt`에 명시된 라이브러리를 설치합니다.
2.  **실행**: 터미널에서 `Multi Turn` 폴더의 메인 스크립트를 실행합니다.
    ```bash
    python "Multi Turn/multi_turn2.py" --input "data/test.csv" --output "submissions/result.csv" --model "gpt-4o-mini"
    ```
