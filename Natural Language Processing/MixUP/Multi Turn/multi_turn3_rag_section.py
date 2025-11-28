import os
import argparse
import importlib.util
import pandas as pd
from tqdm import tqdm
from dotenv import load_dotenv
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor, as_completed

# RAG 관련 라이브러리
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# Load environment variables
load_dotenv()

# ==========================================
# 1. 설정 및 초기화
# ==========================================

import os
import argparse
import importlib.util

import pandas as pd
from tqdm import tqdm
from dotenv import load_dotenv
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor, as_completed

# Load environment variables
load_dotenv()

def load_prompt_from_file(file_path):
    """프롬프트 파일에서 baseline_prompt를 로드"""
    spec = importlib.util.spec_from_file_location("prompt_module", file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    if not hasattr(module, "baseline_prompt"):
        raise ValueError(f"File {file_path} does not contain 'baseline_prompt'")
    
    return module.baseline_prompt

def initialize_rag():
    """ChromaDB와 임베딩 모델을 로드하여 반환"""
    print("Loading Embedding Model (BAAI/bge-m3)...")
    embedding_function = HuggingFaceEmbeddings(
        model_name="BAAI/bge-m3",
        model_kwargs={'device': 'cpu'}, 
        encode_kwargs={'normalize_embeddings': True}
    )

    print("Connecting to Vector DB...")
    vectorstore = Chroma(
        persist_directory="chroma_db_bge", 
        collection_name="translation_memory",
        embedding_function=embedding_function
    )
    # k=3: 유사한 예시 3개를 가져옴
    return vectorstore

# ==========================================
# 2. 핵심 로직: RAG + Multi-Turn
# ==========================================
def call_api_rag_multi_turn(client, model, text, prompt_template, vectorstore):
    """
    3턴 API 호출 함수: 
    1턴 - 의미 보존, 
    2턴 - 자연스러움 + 의미 보존, 
    3턴 - 원문과 비교하여 내용 보존 확인 및 보강
    """
    try:

        # -------------------------------------------------
        # [Step 0] section 분류
        # -------------------------------------------------

        valid_sections = "광고, 사회, 경제, 스포츠, 정치, 문화"
        classify_prompt = (
            f"아래 기사를 읽고 다음 분류 중 가장 적절한 하나를 선택하여 단어만 출력하세요.\n"
            f"분류 목록: [{valid_sections}]\n"
            f"출력 형식: 분류명 (다른 말 없이 딱 단어 하나만 출력)\n\n"
            f"텍스트: {text}"
        )

        resp_class = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": classify_prompt}],
            temperature=0.0
        )
        predicted_section = resp_class.choices[0].message.content.strip()

        # -------------------------------------------------
        # [Step 1] RAG 검색 (유사 예시 찾기)
        # -------------------------------------------------

        try:
            docs = vectorstore.similarity_search(
                text, 
                k=3, 
                filter={"section": predicted_section} # <--- 여기가 핵심입니다!
            )
        except Exception:
            # 분류된 섹션이 DB에 없거나 에러 발생 시 전체 검색
            docs = vectorstore.similarity_search(text, k=3)
            
        # 검색 결과가 없으면(분류 오류 등) 전체에서 다시 검색
        if not docs:
            docs = vectorstore.similarity_search(text, k=3)

        examples_text = ""
        for i, doc in enumerate(docs, 1):
            answer = doc.metadata.get('answer', '변환 결과 없음')
            examples_text += f"참고 예시 {i}:\n[원문] {doc.page_content}\n[변환] {answer}\n\n"

        # -------------------------------------------------
        # [Step 2] Turn 1: RAG 기반 의미 보존 번역
        # -------------------------------------------------
        base_instruction = prompt_template.format(text=text)

        rag_augmented_prompt = (
            f"다음은 당신이 참고해야 할 '{predicted_section}' 분야의 유사한 변환 사례들입니다(Few-shot):\n"
            f"{examples_text}"
            f"--------------------------------------------------\n"
            f"위 예시들의 변환 패턴을 참고하여, 아래 [지시사항]에 따라 아래 원문을 현대어로 변환하세요.\n\n"
            f"지시사항:\n{base_instruction}"
        )

        # 1차 시스템 프롬프트: 정확성 강조
        first_system_prompt = (
            "당신은 한자, 고어, 한문, 영어 혼용문을 현대 기사체로 변환하는 전문가입니다. "
            "주어진 [참고 예시]를 활용하되, 아래 [지시사항]을 준수하여 변환하세요."
            "가장 중요한 것은 원문의 모든 의미와 정보를 빠짐없이 보존하는 것입니다. "
            "원문에 있는 모든 내용을 누락 없이 변환하고, 의미를 왜곡하거나 축약하지 마세요. "
            "변환된 텍스트만 출력하세요."
        )

        # 1차 유저 프롬프트: 예시 + 원문 결합
        # prompt_template에 {text} 자리에 RAG 내용을 포함시켜서 넣거나, 아래처럼 직접 구성
        resp_first = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": first_system_prompt},
                {"role": "user", "content": rag_augmented_prompt},
            ],
            temperature=0.0,
        )
        first_result = resp_first.choices[0].message.content.strip()
        
        # -------------------------------------------------
        # [Step 3] Turn 2: 자연스러운 윤문 (Refinement)
        # -------------------------------------------------
        second_system_prompt = (
            f"당신은 {predicted_section} 분야의 뉴스 전문 교정자입니다. "
            "주어진 문장을 더 자연스럽고 읽기 쉽게 개선하되, "
            "원문의 의미와 정보는 절대 누락하거나 왜곡하지 마세요. "
            "자연스러운 현대 한국어 표현으로 다듬으면서도 의미 보존도를 최대한 유지하세요. "
            "개선된 텍스트만 출력하세요. "
            "단, 문장을 다듬은 이유나 판단 과정은 절대 출력하지 마세요. "
        )
        
        second_user_prompt = (
            f"원문:\n{text}\n\n"
            f"1차 직역 결과:\n{first_result}\n\n"
            "위 1차 직역 결과는 원문의 의미를 빠짐없이 담기 위해 다소 딱딱하게 번역되었습니다. "
            "이를 바탕으로,[원문]의 뉘앙스를 살려 자연스럽고 매끄러운 현대 신문 기사 문체로 완성해주세요. "
            "단, 원문의 모든 의미와 정보는 반드시 보존해야 합니다."
        )
        
        resp_second = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": second_system_prompt},
                {"role": "user", "content": second_user_prompt},
            ],
            temperature=0.2,
        )

        second_result = resp_second.choices[0].message.content.strip()

        # -------------------------------------------------
        # [Step 4] Turn 3: 최종 검토
        # -------------------------------------------------
        third_system_prompt = (
            "당신은 원문과 변환 결과를 비교하여 내용 보존을 검증하는 전문가입니다. "
            "원문의 모든 의미, 정보, 세부사항이 변환 결과에 제대로 포함되어 있는지 철저히 확인하세요. "
            "누락된 내용이 있다면 반드시 보강하고, 왜곡된 내용이 있다면 수정하세요. "
            "원문의 모든 정보를 빠짐없이 포함하면서도 자연스러운 현대 한국어로 표현하세요. "
            "최종 보강된 텍스트만 출력하세요."
        )

        third_user_prompt = (
            f"원문:\n{text}\n\n"
            f"두 번째 변환 결과:\n{second_result}\n\n"
            "위 변환 결과를 원문과 비교하여 다음을 확인하고 보강해주세요:\n"
            "1. 원문의 모든 의미와 정보가 포함되어 있는지 확인\n"
            "2. 누락된 내용이 있다면 반드시 추가\n"
            "3. 왜곡되거나 잘못된 내용이 있다면 수정\n"
            "4. 자연스러운 현대 한국어 표현 유지\n\n"
            "원문의 모든 내용을 빠짐없이 보존하면서도 자연스러운 최종 결과를 출력하세요."
        )

        resp_third = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": third_system_prompt},
                {"role": "user", "content": third_user_prompt},
            ],
            temperature=0.0,
        )
        final_result = resp_third.choices[0].message.content.strip()
        
        return final_result

    except Exception as e:
        print(f"[ERROR] {text[:30]}... - {e}")
        return text  # 에러 시 원문 반환

# ==========================================
# 3. 메인 실행
# ==========================================
def main():
    parser = argparse.ArgumentParser(description="Multi-turn RAG Generation")
    parser.add_argument("--input", default="data/test_dataset.csv", help="Input CSV path")
    parser.add_argument("--output", default="submissions/test_rag_turn3_section.csv", help="Output CSV path")
    parser.add_argument("--model", default="solar-pro2", help="Model name")
    parser.add_argument("--prompt", default="prompts/prompt_7.py", help="Path to prompt file")
    parser.add_argument("--max_workers", type=int, default=6, help="Number of parallel workers")
    args = parser.parse_args()

    # 데이터 로드
    df = pd.read_csv(args.input)
    
    # API 및 DB 설정
    api_key = os.getenv("UPSTAGE_API_KEY")
    client = OpenAI(api_key=api_key, base_url="https://api.upstage.ai/v1")
    
    # [중요] RAG 검색기 초기화 (메인 스레드에서 한 번만 수행)
    vectorstore = initialize_rag()
    
    # 프롬프트 파일 로드 (여기서는 파일 내용은 쓰지 않고 구조만 참고하거나, 필요시 사용)
    prompt_template = load_prompt_from_file(args.prompt)

    print(f"Model: {args.model}")
    print(f"Mode: RAG + Multi-turn (Search -> Translate -> Refine)")
    
    results = {idx: None for idx in range(len(df))}
    completed_count = 0
    save_interval = 10
    
    with ThreadPoolExecutor(max_workers=args.max_workers) as executor:
        # call_api_rag_multi_turn에 retriever를 전달
        futures = {
            executor.submit(call_api_rag_multi_turn, client, args.model, text, prompt_template, vectorstore): idx
            for idx, text in enumerate(df["original_sentence"].astype(str).tolist())
        }

        for future in tqdm(as_completed(futures), total=len(futures), desc="Generating"):
            idx = futures[future]
            results[idx] = future.result()
            completed_count += 1
            
            if completed_count % save_interval == 0:
                completed_results = []
                for i in range(len(df)):
                    ans = results[i] if results[i] is not None else df.iloc[i]["original_sentence"]
                    completed_results.append({
                        "id": df.iloc[i]["id"],
                        "original_sentence": df.iloc[i]["original_sentence"],
                        "answer_sentence": ans
                    })
                pd.DataFrame(completed_results).to_csv(args.output, index=False)

    # 최종 저장
    final_results = []
    for idx in range(len(df)):
        ans = results[idx] if results[idx] is not None else df.iloc[idx]["original_sentence"]
        final_results.append({
            "id": df.iloc[idx]["id"],
            "original_sentence": df.iloc[idx]["original_sentence"],
            "answer_sentence": ans
        })
    
    pd.DataFrame(final_results).to_csv(args.output, index=False)
    print(f"\n✅ All done! Saved to {args.output}")

if __name__ == "__main__":
    main()