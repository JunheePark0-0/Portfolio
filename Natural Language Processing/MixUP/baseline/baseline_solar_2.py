import os
import argparse

import pandas as pd
from tqdm import tqdm
from dotenv import load_dotenv
from openai import OpenAI
from prompts import baseline_prompt
from concurrent.futures import ThreadPoolExecutor, as_completed

# Load environment variables
load_dotenv()

def call_api_single(client, model, text, prompt_template):
    try:
        prompt = prompt_template.format(text=text)
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "당신은 한자, 고어, 한문, 영어 혼용문을 현대 기사체로 자연스럽게 현대화하는 전문가입니다. "
                        "원문의 의미와 맥락을 유지하면서 2025년의 일반 독자가 이해하기 쉬운 표현으로 바꾸고, "
                        "불필요한 설명 없이 변환된 텍스트만 출력하세요."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.0,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        print(f"[ERROR] {text[:40]}... - {e}")
        return text  # fallback


def main():
    parser = argparse.ArgumentParser(description="Generate modified sentences using Upstage API")
    parser.add_argument("--input", default="data/train_dataset.csv", help="Input CSV path containing body_archaic_hangul column")
    parser.add_argument("--output", default="submission1.csv", help="Output CSV path")
    parser.add_argument("--model", default="solar-pro2", help="Model name (default: solar-pro2)")
    args = parser.parse_args()

    # Load data
    df = pd.read_csv(args.input)
    
    if "original_sentence" not in df.columns:
        raise ValueError("Input CSV must contain 'original_sentence' column")
    
    if "id" not in df.columns:
        raise ValueError("Input CSV must contain 'id' column")

    # Setup Upstage client
    api_key = os.getenv("UPSTAGE_API_KEY")
    if not api_key:
        raise ValueError("UPSTAGE_API_KEY not found in environment variables")
    
    client = OpenAI(api_key=api_key, base_url="https://api.upstage.ai/v1")
    
    print(f"Model: {args.model}")
    print(f"Output: {args.output}")

    results = []
    
    # Process each sentence
    max_workers = 4
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(call_api_single, client, args.model, text, baseline_prompt): (idx, text)
            for idx, text in enumerate(df["original_sentence"].astype(str).tolist())
        }

        for future in tqdm(as_completed(futures), total=len(futures), desc="Generating"):
            idx, text = futures[future]
            answer = future.result()
            
            results.append({
                "sort_index": idx,          # 나중에 정렬하기 위한 인덱스
                "id": df.iloc[idx]["id"],   # 원본 ID
                "original_sentence": text,
                "answer_sentence": answer
            })

    out_df = pd.DataFrame(results)
    out_df = out_df.sort_values("sort_index").drop(columns=["sort_index"]) # 정렬 후 임시 인덱스 삭제

    # 저장
    out_df.to_csv(args.output, index=False)
    print(f"Wrote {len(out_df)} rows to {args.output}")

if __name__ == "__main__":
    main()