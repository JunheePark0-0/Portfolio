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
    return vectorstore.as_retriever(search_kwargs={"k": 3})

# ==========================================
# 2. 핵심 로직: RAG + 3-Turn (생성 -> 교정 -> 검수)
# ==========================================
def call_api_rag_multi_turn(client, model, text, prompt_template, retriever):
    """
    [Turn 1] RAG + Prompt: 직역 (의미 보존)
    [Turn 2] Refine: 윤문 (자연스러움)
    [Turn 3] Review: 검수 (원문 대조 후 누락 복원)
    """
    try:
        # -------------------------------------------------
        # [Step 1] RAG 검색 (유사 예시 찾기)
        # -------------------------------------------------
        docs = retriever.invoke(text)
        
        examples_text = ""
        for i, doc in enumerate(docs, 1):
            answer = doc.metadata.get('answer', '변환 결과 없음')
            examples_text += f"참고 예시 {i}:\n[원문] {doc.page_content}\n[변환] {answer}\n\n"

        # -------------------------------------------------
        # [Step 2] Turn 1: RAG 기반 의미 보존 번역 (직역)
        # -------------------------------------------------
        base_instruction = prompt_template.format(text=text)

        rag_augmented_prompt = (
            f"다음은 당신이 변환 작업을 할 때 참고해야 할 유사한 사례들입니다(Few-shot):\n"
            f"{examples_text}\n"
            f"--------------------------------------------------\n"
            f"위 예시들의 변환 패턴을 참고하여, 아래 [지시사항]에 따라 원문을 변환하세요.\n\n"
            f"{base_instruction}"
        )

        first_system_prompt = (
            "당신은 고전 문헌 현대화 전문가입니다. "
            "가장 중요한 것은 원문의 모든 의미와 정보를 빠짐없이 보존하는 것입니다. "
            "문장이 딱딱하더라도 원문의 내용을 100% 직역하여 출력하세요."
        )

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
            "당신은 현대 한국어 기사체 교정 전문가입니다. "
            "1차 번역 결과를 바탕으로, 원문의 의미를 해치지 않는 선에서 "
            "가장 자연스럽고 읽기 편한 현대 신문 기사체로 문장을 다듬으세요."
        )
        
        second_user_prompt = (
            f"원문:\n{text}\n\n"
            f"1차 직역 결과:\n{first_result}\n\n"
            "위 1차 직역 결과는 의미 보존을 위해 다소 딱딱하게 번역되었습니다. "
            "이를 바탕으로,[원문]의 뉘앙스를 살려 매끄러운 현대어로 완성하세요. "
            "단, 정보의 누락이나 왜곡이 없어야 합니다."
        )
        
        resp_second = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": second_system_prompt},
                {"role": "user", "content": second_user_prompt},
            ],
            temperature=0.0,
        )
        second_result = resp_second.choices[0].message.content.strip()

        # -------------------------------------------------
        # [Step 4] Turn 3: 최종 검수 및 복원 (Review)
        # -------------------------------------------------
        third_system_prompt = (
            "당신은 번역 품질 관리자(QA Specialist)입니다. "
            "원문과 변환된 문장을 대조하여 '누락된 정보'나 '왜곡된 의미'가 있는지 엄격히 확인합니다. "
            "문체가 자연스럽다면 그대로 두되, 원문의 핵심 정보가 빠졌다면 그 부분만 자연스럽게 채워 넣으세요."
        )

        third_user_prompt = (
            f"원문:\n{text}\n\n"
            f"변환된 문장(후보):\n{second_result}\n\n"
            "[검수 지침]\n"
            "1. 원문의 인명, 지명, 날짜, 수치, 핵심 서술어가 변환된 문장에 모두 포함되었는지 확인하세요.\n"
            "2. 만약 정보가 누락되었거나 오역이 있다면, '변환된 문장'의 자연스러운 톤을 유지하면서 정보를 복원하세요.\n"
            "3. 만약 결함이 없다면, '변환된 문장'을 그대로 출력하세요.\n"
            "4. 부연 설명 없이 최종 결과 문장만 출력하세요."
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
    parser = argparse.ArgumentParser(description="Multi-turn RAG Generation (3-Turn)")
    parser.add_argument("--input", default="data/test_dataset.csv", help="Input CSV path")
    parser.add_argument("--output", default="submissions/submission_rag_turn_re3.csv", help="Output CSV path")
    parser.add_argument("--model", default="solar-pro2", help="Model name")
    parser.add_argument("--prompt", default="prompts/prompt_6.py", help="Path to prompt file")
    parser.add_argument("--max_workers", type=int, default=8, help="Number of parallel workers")
    args = parser.parse_args()

    # 데이터 로드
    df = pd.read_csv(args.input)
    
    # API 및 DB 설정
    api_key = os.getenv("UPSTAGE_API_KEY")
    client = OpenAI(api_key=api_key, base_url="https://api.upstage.ai/v1")
    
    # [중요] RAG 검색기 초기화
    retriever = initialize_rag()
    
    # 프롬프트 파일 로드
    prompt_template = load_prompt_from_file(args.prompt)

    print(f"Model: {args.model}")
    print(f"Mode: RAG + 3-Turn (Direct -> Refine -> Review)")
    
    results = {idx: None for idx in range(len(df))}
    completed_count = 0
    save_interval = 10
    
    with ThreadPoolExecutor(max_workers=args.max_workers) as executor:
        futures = {
            executor.submit(call_api_rag_multi_turn, client, args.model, text, prompt_template, retriever): idx
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