# CAT-FICIAL DECODER: Vision Transformer와 GPT-2를 활용한 이미지 캡셔닝

## 📖 프로젝트 개요

**CAT-FICIAL DECODER**는 주어진 이미지를 이해하고, 그 내용을 자연어 문장으로 설명하는 이미지 캡셔닝(Image Captioning) 프로젝트입니다. 최신 딥러닝 모델인 Vision Transformer (ViT)와 GPT-2를 결합하여 이미지의 시각적 특징과 언어적 맥락을 연결하는 'VisionGPT' 모델을 구현했습니다.

이 프로젝트는 컴퓨터가 사람처럼 이미지를 '보고' '설명'하는 능력을 갖추도록 하는 것을 목표로 합니다.

## 🕐 개발 기간 
2025.02 ~ 2025.02 (1개월)

## ✨ 핵심 아키텍처 및 기술

본 프로젝트의 모델은 두 가지 주요 딥러닝 아키텍처를 결합한 Encoder-Decoder 구조를 따릅니다.

### 1. 이미지 인식 (Encoder: Vision Transformer)
-   **역할**: 이미지의 핵심적인 시각적 정보를 추출하는 인코더 역할을 수행합니다.
-   **모델**: `timm` 라이브러리를 통해 사전 학습된 **ViT (Vision Transformer)** 모델을 사용합니다. ViT는 이미지를 여러 패치로 나누어 각 패치 간의 관계를 학습하므로, 이미지의 전반적인 맥락과 세부적인 객체 정보를 효과적으로 포착합니다.

### 2. 문장 생성 (Decoder: GPT-2)
-   **역할**: ViT로부터 전달받은 이미지 정보를 바탕으로 자연스러운 설명 문장을 생성하는 디코더 역할을 수행합니다.
-   **모델**: `transformers` 라이브러리의 **GPT-2 (Generative Pre-trained Transformer 2)** 모델을 사용합니다. GPT-2는 뛰어난 문장 생성 능력을 바탕으로, 이미지의 특징을 문법적으로 자연스럽고 의미적으로 적절한 캡션으로 변환합니다.

### 3. 미세 조정 (Fine-tuning)
-   이미지와 해당 이미지를 설명하는 캡션 데이터셋을 활용하여 사전 학습된 ViT와 GPT-2 모델을 함께 미세 조정합니다. 이 과정을 통해 두 모델은 시각적 정보와 언어적 표현 사이의 연결고리를 학습하게 됩니다.

## 📂 프로젝트 구조

```
.
├── CV_Team 2_발표자료.pdf
├── README.md
├── VisionGPT.ipynb
└── Codes/
    ├── VisionGPT_Data.ipynb
    ├── VisionGPT_Prediction.ipynb
    └── VisionGPT_Structures.ipynb
```

## 🛠️ 주요 구성 요소

-   **`VisionGPT.ipynb`**: 프로젝트의 전체 워크플로우를 담고 있는 메인 노트북 파일입니다. 데이터 로딩, 모델 정의, 학습, 평가 및 예측 과정이 포함되어 있습니다.
-   **`Codes/`**: 메인 노트북의 코드를 기능별로 분리하여 관리하는 폴더입니다.
    -   `VisionGPT_Data.ipynb`: 데이터셋을 불러오고 전처리하며, DataLoader를 생성하는 과정을 다룹니다.
    -   `VisionGPT_Structures.ipynb`: ViT와 GPT-2를 결합한 모델의 아키텍처를 정의합니다.
    -   `VisionGPT_Prediction.ipynb`: 학습된 모델을 사용하여 새로운 이미지에 대한 캡션을 생성하는 예측 과정을 구현합니다.
-   **`CV_Team 2_발표자료.pdf`**: 프로젝트의 목표, 과정, 결과 등을 요약한 발표 자료입니다.

## 🚀 실행 방법

1.  **환경 설정**: `VisionGPT.ipynb` 노트북 상단에 명시된 필요 라이브러리(`torch`, `timm`, `transformers`, `albumentations` 등)를 설치합니다.
2.  **데이터 준비**: 지정된 경로에 이미지 캡셔닝 데이터셋을 준비합니다.
3.  **노트북 실행**:
    -   **데이터 처리**: `Codes/VisionGPT_Data.ipynb`를 실행하여 데이터를 모델에 입력할 형태로 변환합니다.
    -   **모델 학습**: `VisionGPT.ipynb` 또는 관련 스크립트를 실행하여 모델을 학습시킵니다.
    -   **예측**: `Codes/VisionGPT_Prediction.ipynb`를 통해 학습된 모델로 새로운 이미지에 대한 캡션을 생성합니다.
