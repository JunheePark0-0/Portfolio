import os
import sys
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
# 1. 유틸리티 함수 (프롬프트 로드)
# ==========================================
def load_dynamic_prompt(file_path, var_names=["system_prompt", "baseline_prompt"]):
    """지정된 경로의 파이썬 파일에서 프롬프트 변수를 로드"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"프롬프트 파일을 찾을 수 없습니다: {file_path}")

    abs_path = os.path.abspath(file_path)
    module_name = os.path.basename(file_path).replace(".py", "")

    spec = importlib.util.spec_from_file_location(module_name, abs_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    for var_name in var_names:
        if hasattr(module, var_name):
            print(f"✅ Loaded '{var_name}' from {os.path.basename(file_path)}")
            return getattr(module, var_name)
    
    raise ValueError(f"파일 {file_path} 안에 변수({var_names})가 없습니다.")

# ==========================================
# 2. 전역 설정 (Upstage, ChromaDB)
# ==========================================
api_key = os.getenv("UPSTAGE_API_KEY")
if not api_key:
    raise ValueError("UPSTAGE_API_KEY not found in .env file")

client = OpenAI(api_key=api_key, base_url="https://api.upstage.ai/v1")

print("Loading Embedding Model (BAAI/bge-m3)...")
embedding_function = HuggingFaceEmbeddings(
    model_name="BAAI/bge-m3",
    model_kwargs={'device': 'cpu'}, 
    encode_kwargs={'normalize_embeddings': True}
)

print("Connecting to Vector DB...")
vectorstore = Chroma(
    persist_directory="./chroma_db_bge", 
    collection_name="translation_memory",
    embedding_function=embedding_function
)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# ==========================================
# 3. 핵심 작업 함수 (RAG + Generation)
# ==========================================
def generate_with_rag(text, model_name, system_prompt_text):
    try:
        # [Step 1] 유사 예시 검색
        docs = retriever.invoke(text)
        
        # [Step 2] Few-shot 예시 텍스트 구성
        examples_text = ""
        for i, doc in enumerate(docs, 1):
            examples_text += f"참고 예시 {i}:\n[원문] {doc.page_content}\n[변환] {doc.metadata['answer']}\n\n"
            
        # [Step 3] 유저 프롬프트 구성
        # 외부에서 불러온 system_prompt는 '규칙' 역할을 하고,
        # 여기서는 '예시'와 '입력'을 제공합니다.
        user_prompt = f"""
다음은 당신이 참고해야 할 [유사 변환 예시]입니다.
이 예시들의 문체와 단어 선택을 참고하여 작업을 수행하세요.

{examples_text}
--------------------------------------------------
[처리할 원문]
{text}
"""

        # [Step 4] API 호출
        resp = client.chat.completions.create(
            model=model_name,
            messages=[
                # [핵심] 파일에서 불러온 시스템 프롬프트를 여기에 주입
                {"role": "system", "content": system_prompt_text},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.0,
        )
        
        return resp.choices[0].message.content.strip()

    except Exception as e:
        print(f"[ERROR] {text[:30]}... - {e}")
        return text

# ==========================================
# 4. 메인 실행부
# ==========================================
def main():
    parser = argparse.ArgumentParser(description="Generate with RAG using Solar-pro2")
    parser.add_argument("--input", default="data/train_sampled.csv", help="Input CSV path")
    parser.add_argument("--output", default="submissions/submission_rag_sampled.csv", help="Output CSV path")
    parser.add_argument("--model", default="solar-pro2", help="Model name")
    
    # [추가] 시스템 프롬프트 경로 옵션
    parser.add_argument("--system_prompt_path", default="prompts/prompt_5.py", help="Path to system prompt file")
    
    args = parser.parse_args()

    # 데이터 로드
    df = pd.read_csv(args.input)
    
    # 시스템 프롬프트 로드
    print(f"📂 Loading system prompt from: {args.system_prompt_path}")
    try:
        loaded_system_prompt = load_dynamic_prompt(args.system_prompt_path)
    except Exception as e:
        print(f"❌ Error loading prompt: {e}")
        return

    print(f"Model: {args.model}")
    print(f"Input: {args.input} ({len(df)} rows)")
    print(f"System Prompt Preview: {loaded_system_prompt[:50]}...")
    
    results = {idx: None for idx in range(len(df))}
    max_workers = 4
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # generate_with_rag 함수에 loaded_system_prompt를 함께 전달
        futures = {
            executor.submit(generate_with_rag, text, args.model, loaded_system_prompt): idx
            for idx, text in enumerate(df["original_sentence"].astype(str).tolist())
        }

        for future in tqdm(as_completed(futures), total=len(futures), desc="RAG Generating"):
            idx = futures[future]
            results[idx] = future.result()

    final_results = []
    for idx in range(len(df)):
        final_results.append({
            "id": df.iloc[idx]["id"],
            "original_sentence": df.iloc[idx]["original_sentence"],
            "answer_sentence": results[idx] if results[idx] is not None else df.iloc[idx]["original_sentence"]
        })
    
    out_df = pd.DataFrame(final_results)
    out_df.to_csv(args.output, index=False)
    print(f"✅ Saved to {args.output}")

if __name__ == "__main__":
    main()