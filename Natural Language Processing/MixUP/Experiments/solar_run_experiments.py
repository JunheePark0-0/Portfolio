import os
import sys
import subprocess
import importlib.util
import pandas as pd
import glob
from datetime import datetime
import argparse


def load_prompt_from_file(file_path):
    """프롬프트 파일에서 baseline_prompt를 로드"""
    spec = importlib.util.spec_from_file_location("prompt_module", file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    if not hasattr(module, "baseline_prompt"):
        raise ValueError(f"File {file_path} does not contain 'baseline_prompt'")
    
    return module.baseline_prompt


def run_generate(prompt_file, input_file, output_file, model="solar-pro2"):
    """baseline_generate_multi.py 실행"""
    prompt = load_prompt_from_file(prompt_file)
    
    cmd = [
        sys.executable,
        "-u",
        "baseline_generate_multi.py",
        "--input", input_file,
        "--output", output_file,
        "--model", model,
        "--prompt", prompt
    ]
    
    print(f"\n{'='*60}")
    print(f"🔄 Generating with prompt: {os.path.basename(prompt_file)}")
    print(f"{'='*60}")
    
    # 실시간 출력을 위해 capture_output=False로 설정
    # stdout과 stderr를 직접 연결하여 tqdm이 실시간으로 보이도록 함
    result = subprocess.run(cmd)
    
    if result.returncode != 0:
        print(f"\n❌ Generation failed with return code {result.returncode}")
        return False
    
    return True


def run_evaluate(true_df_path, pred_df_path):
    """evaluate.py 실행하고 결과 반환"""
    from evaluate import evaluate
    import pandas as pd
    
    true_df = pd.read_csv(true_df_path)
    pred_df = pd.read_csv(pred_df_path)
    
    # evaluate 함수가 내부에서 metrics.evaluate_correction을 호출하므로
    # 한 번만 호출하여 결과 재사용
    result_df, summary_text = evaluate(true_df, pred_df)
    
    # average_scores는 evaluate 함수 내부에서 계산되지만 반환되지 않으므로
    # 다시 계산 (또는 evaluate 함수 수정 필요)
    import metrics
    _, average_scores = metrics.evaluate_correction(true_df, pred_df)
    
    return average_scores, summary_text


def main():
    parser = argparse.ArgumentParser(description="Run experiments with all prompts")
    parser.add_argument("--input", default="data/train_dataset.csv", help="Input CSV path")
    parser.add_argument("--prompt_dir", default="prompt", help="Directory containing prompt files")
    parser.add_argument("--output_dir", default="experiments", help="Output directory for experiment results")
    parser.add_argument("--model", default="solar-pro2", help="Model name")
    args = parser.parse_args()
    
    # 출력 디렉토리 생성
    os.makedirs(args.output_dir, exist_ok=True)
    os.makedirs("submissions", exist_ok=True)
    
    # 프롬프트 파일 찾기
    prompt_files = sorted(glob.glob(os.path.join(args.prompt_dir, "*.py")))
    
    if not prompt_files:
        print(f"❌ No prompt files found in {args.prompt_dir}")
        return
    
    print(f"📋 Found {len(prompt_files)} prompt files")
    
    # 실험 결과 저장용 리스트
    experiment_results = []
    
    for i, prompt_file in enumerate(prompt_files, 1):
        prompt_name = os.path.basename(prompt_file).replace(".py", "")
        temp_output = f"submissions/submission_{prompt_name}.csv"
        
        print(f"\n{'#'*60}")
        print(f"# Experiment {i}/{len(prompt_files)}: {prompt_name}")
        print(f"{'#'*60}")
        
        try:
            # 1. Generate
            if not run_generate(prompt_file, args.input, temp_output, args.model):
                print(f"❌ Skipping {prompt_name} due to generation failure")
                continue
            
            # 2. Evaluate
            print(f"\n{'='*60}")
            print(f"📊 Evaluating: {prompt_name}")
            print(f"{'='*60}")
            
            average_scores, summary_text = run_evaluate(args.input, temp_output)
            
            # 3. 결과 저장
            result_row = {
                "prompt_file": prompt_name,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "model": args.model,
            }
            
            # 카테고리별 점수 추가
            for category, stats in average_scores.items():
                if category == "overall":
                    result_row["overall_score"] = stats.get("average_score", 0.0)
                else:
                    result_row[f"{category}_score"] = stats.get("average_score", 0.0)
            
            experiment_results.append(result_row)
            
            # 실험 결과를 즉시 저장 (중간 저장)
            if experiment_results:
                exp_df = pd.DataFrame(experiment_results)
                intermediate_path = os.path.join(args.output_dir, f"experiment_{args.prompt_dir}.csv")
                exp_df.to_csv(intermediate_path, index=False, encoding="utf-8-sig")
                print(f"\n💾 Experiment results saved to {intermediate_path}")
            
            print(f"\n✅ Completed: {prompt_name}")
            print(f"   Overall Score: {result_row.get('overall_score', 'N/A')}")
            
        except Exception as e:
            print(f"❌ Error processing {prompt_name}: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    # 최종 결과 저장
    if experiment_results:
        final_output_path = os.path.join(args.output_dir, f"experiment_{args.prompt_dir}.csv")
        exp_df = pd.DataFrame(experiment_results)
        exp_df.to_csv(final_output_path, index=False, encoding="utf-8-sig")
        print(f"\n{'='*60}")
        print(f"✅ All experiments completed!")
        print(f"📊 Results saved to {final_output_path}")
        print(f"{'='*60}")
        
        # 결과 요약 출력
        if "overall_score" in exp_df.columns:
            best_idx = exp_df["overall_score"].idxmax()
            best_prompt = exp_df.loc[best_idx, "prompt_file"]
            best_score = exp_df.loc[best_idx, "overall_score"]
            print(f"\n🏆 Best prompt: {best_prompt} (score: {best_score:.3f})")
    else:
        print("\n❌ No experiments completed successfully")


if __name__ == "__main__":
    main()

