import os
import argparse

import pandas as pd
from tqdm import tqdm
from dotenv import load_dotenv
from openai import OpenAI
from prompts import baseline_prompt

# Load environment variables
load_dotenv()

def main():
    parser = argparse.ArgumentParser(description="Generate modified sentences using Upstage API")
    parser.add_argument("--input", default="../data/train_dataset.csv", help="Input CSV path containing body_archaic_hangul column")
    parser.add_argument("--output", default="../submissions/submission_openai.csv", help="Output CSV path")
    parser.add_argument("--model", default="gpt-4o-mini", help="Model name (default: gpt-4o-mini)")
    args = parser.parse_args()

    # Load data
    df = pd.read_csv(args.input)
    
    if "original_sentence" not in df.columns:
        raise ValueError("Input CSV must contain 'original_sentence' column")
    
    if "id" not in df.columns:
        raise ValueError("Input CSV must contain 'id' column")

    # Setup Upstage client
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    
    client = OpenAI(api_key=api_key)
    
    print(f"Model: {args.model}")
    print(f"Output: {args.output}")

    ids = []
    original_sentence = []
    answer_sentence = []
    
    # Process each sentence
    for idx, text in enumerate(tqdm(df["original_sentence"].astype(str).tolist(), desc="Generating")):
        ids.append(df.iloc[idx]["id"])  # Get id from original data
        original_sentence.append(text)
        
        try:
            prompt = baseline_prompt.format(text=text)
            resp = client.chat.completions.create(
                model=args.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "당신은 한자, 고어, 한문, 영어 혼용문을 현대 기사체로 자연스럽게 현대화하는 전문가입니다. 원문의 의미와 맥락을 유지하면서 2025년의 일반 독자가 이해하기 쉬운 표현으로 바꾸고, 불필요한 설명 없이 변환된 텍스트만 출력하세요."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.0,
            )
            corrected = resp.choices[0].message.content.strip()
            answer_sentence.append(corrected)
            
        except Exception as e:
            print(f"Error processing: {text[:50]}... - {e}")
            answer_sentence.append(text)  # fallback to original

    # Save results with required column names (including id)
    out_df = pd.DataFrame({
        "id": ids,
        "original_sentence": original_sentence, 
        "answer_sentence": answer_sentence
    })
    out_df.to_csv(args.output, index=False)
    print(f"Wrote {len(out_df)} rows to {args.output}")


if __name__ == "__main__":
    main()

