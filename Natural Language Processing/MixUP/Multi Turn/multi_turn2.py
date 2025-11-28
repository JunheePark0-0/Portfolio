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


def call_api_multi_turn(client, model, text, prompt_template):
    """멀티턴 API 호출 함수: 첫 턴은 의미 보존, 두 번째 턴은 자연스러움과 의미 보존"""
    try:
        prompt = prompt_template.format(text=text)
        
        # 첫 번째 턴: 의미 보존도가 중요
        first_system_prompt = (
            "당신은 한자, 고어, 한문, 영어 혼용문을 현대 기사체로 변환하는 전문가입니다. "
            "가장 중요한 것은 원문의 모든 의미와 정보를 빠짐없이 보존하는 것입니다. "
            "원문에 있는 모든 내용을 누락 없이 변환하고, 의미를 왜곡하거나 축약하지 마세요. "
            "변환된 텍스트만 출력하세요."
        )
        
        resp_first = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": first_system_prompt},
                {"role": "user", "content": prompt},
            ],
            temperature=0.0,
        )
        first_result = resp_first.choices[0].message.content.strip()
        
        # 두 번째 턴: 자연스러움과 의미 보존도가 중요
        second_system_prompt = (
            "당신은 현대 한국어 기사체 문장을 다듬는 전문가입니다. "
            "주어진 문장을 더 자연스럽고 읽기 쉽게 개선하되, "
            "원문의 의미와 정보는 절대 누락하거나 왜곡하지 마세요. "
            "자연스러운 현대 한국어 표현으로 다듬으면서도 의미 보존도를 최대한 유지하세요. "
            "개선된 텍스트만 출력하세요."
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
            temperature=0.0,
        )
        final_result = resp_second.choices[0].message.content.strip()
        
        return final_result
    except Exception as e:
        print(f"[ERROR] {text[:40]}... - {e}")
        return text  # fallback


def main():
    parser = argparse.ArgumentParser(description="Generate modified sentences using Upstage API (multi-turn conversation mode)")
    parser.add_argument("--input", default="data/test_dataset.csv", help="Input CSV path containing original_sentence column")
    parser.add_argument("--output", default="submissions/submission_multi.csv", help="Output CSV path")
    parser.add_argument("--model", default="solar-pro2", help="Model name (default: solar-pro2)")
    parser.add_argument("--prompt", required=True, help="Path to prompt file (e.g., prompts/prompt_lee.py)")
    parser.add_argument("--max_workers", type=int, default=8, help="Number of parallel workers (default: 3)")
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
    
    # Load prompt from file
    prompt_template = load_prompt_from_file(args.prompt)
    
    print(f"Model: {args.model}")
    print(f"Output: {args.output}")
    print(f"Prompt file: {args.prompt}")
    print(f"Max workers: {args.max_workers}")
    print(f"Mode: Multi-turn (1st: meaning preservation, 2nd: naturalness + meaning preservation)")

    # Initialize results dictionary to maintain original order
    results = {idx: None for idx in range(len(df))}
    completed_count = 0
    save_interval = 10  # Save every 10 completed items
    
    # Process each sentence with parallel workers (multi-turn)
    with ThreadPoolExecutor(max_workers=args.max_workers) as executor:
        futures = {
            executor.submit(call_api_multi_turn, client, args.model, text, prompt_template): idx
            for idx, text in enumerate(df["original_sentence"].astype(str).tolist())
        }

        for future in tqdm(as_completed(futures), total=len(futures), desc="Generating"):
            idx = futures[future]
            result = future.result()
            results[idx] = result
            completed_count += 1
            
            # Periodically save intermediate results
            if completed_count % save_interval == 0:
                # Create DataFrame with completed results in original order
                completed_results = []
                for i in range(len(df)):
                    if results[i] is not None:
                        completed_results.append({
                            "id": df.iloc[i]["id"],
                            "original_sentence": df.iloc[i]["original_sentence"],
                            "answer_sentence": results[i]
                        })
                    else:
                        # For incomplete items, use original sentence as placeholder
                        completed_results.append({
                            "id": df.iloc[i]["id"],
                            "original_sentence": df.iloc[i]["original_sentence"],
                            "answer_sentence": df.iloc[i]["original_sentence"]
                        })
                
                out_df = pd.DataFrame(completed_results)
                out_df.to_csv(args.output, index=False)
                # print(f"\n[Progress] Saved {completed_count}/{len(df)} results to {args.output}")

    # Final save with all results in original order
    final_results = []
    for idx in range(len(df)):
        final_results.append({
            "id": df.iloc[idx]["id"],
            "original_sentence": df.iloc[idx]["original_sentence"],
            "answer_sentence": results[idx] if results[idx] is not None else df.iloc[idx]["original_sentence"]
        })
    
    out_df = pd.DataFrame(final_results)
    out_df.to_csv(args.output, index=False)
    print(f"\n✅ Wrote {len(out_df)} rows to {args.output}")

if __name__ == "__main__":
    main()

