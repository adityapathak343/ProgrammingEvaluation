# main.py
import yaml
import json
import os
from codev import CodEv
from datetime import datetime
from pathlib import Path
import pandas as pd

def load_api_key() -> str:
    """Load API key from environment variable or config file."""
    api_key = open(".openai", "r").read().strip()
    if not api_key:
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
                api_key = config.get('api_key')
        except FileNotFoundError:
            raise ValueError("API key not found in environment variables or config.json")
    return api_key

def save_results(result: dict, submission_id: str, output_dir: Path):
    """Save evaluation results in multiple formats."""
    try:
        # Create directories if they don't exist
        yaml_dir = output_dir / 'yaml_results'
        ensemble_dir = output_dir / 'ensemble_analysis'
        csv_dir = output_dir / 'csv_results'
        
        for directory in [yaml_dir, ensemble_dir, csv_dir]:
            directory.mkdir(parents=True, exist_ok=True)

        # 1. Save YAML result
        yaml_file = yaml_dir / f'submission_{submission_id}.yaml'
        with yaml_file.open('w', encoding='utf-8') as f:
            yaml.dump(result, f, default_flow_style=False, allow_unicode=True)

        # 2. Save detailed ensemble analysis
        if 'ensemble_statistics' in result:
            ensemble_file = ensemble_dir / f'ensemble_analysis_{submission_id}.json'
            ensemble_data = {
                'submission_id': submission_id,
                'evaluation_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'ensemble_statistics': result['ensemble_statistics'],
                'function_scores': {
                    func_name: {
                        'final_score': details['score'],
                        'max_score': details['max_score'],
                        'variance': result['ensemble_statistics']['score_variance'].get(func_name, 0)
                    }
                    for func_name, details in result['function_scores'].items()
                }
            }
            with ensemble_file.open('w', encoding='utf-8') as f:
                json.dump(ensemble_data, f, indent=2)

        # 3. Create CSV row data
        csv_data = {
            'submission_id': submission_id,
            'total_score': result['total_score'],
            'evaluations_count': result['ensemble_statistics']['evaluations_count'],
            'total_score_variance': result['ensemble_statistics']['total_score_variance']
        }
        
        # Add individual function scores
        for func_name, details in result['function_scores'].items():
            csv_data[f'{func_name}_score'] = details['score']
            csv_data[f'{func_name}_variance'] = result['ensemble_statistics']['score_variance'].get(func_name, 0)

        # Update or create CSV file
        csv_file = csv_dir / 'evaluation_summary.csv'
        if csv_file.exists():
            df = pd.read_csv(csv_file)
            df = df[df['submission_id'] != submission_id]  # Remove if exists
            df = pd.concat([df, pd.DataFrame([csv_data])], ignore_index=True)
        else:
            df = pd.DataFrame([csv_data])
        
        df.to_csv(csv_file, index=False)

        print(f"Results saved for submission {submission_id}:")
        print(f"- YAML result: {yaml_file}")
        print(f"- Ensemble analysis: {ensemble_file}")
        print(f"- Updated CSV summary: {csv_file}")

    except Exception as e:
        print(f"Error saving results for submission {submission_id}: {str(e)}")

def main():
    # Create results directory with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_dir = Path('results/CodEv') / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Results will be saved to: {output_dir}")

    try:
        # Initialize CodEv
        api_key = load_api_key()
        codev = CodEv(api_key)
        
        # Read model solution
        with open('files/SS_24_25_CBT/CBT_PART_1_QP.java', 'r', encoding='utf-8') as f:
            model_solution = f.read()
        
        # Process submissions
        dataset_path = Path('files/OOPS/solutions_cleaned')
        
        for folder in dataset_path.iterdir():
            if not folder.is_dir() or not folder.name.isdigit():
                continue
                
            submission_id = folder.name
            print(f"\nProcessing submission {submission_id}...")
            
            try:
                # Read student's code
                student_code_path = folder / 'p1.java'
                if not student_code_path.exists():
                    print(f"No p1.java found for submission {submission_id}")
                    continue
                    
                with open(student_code_path, 'r', encoding='utf-8') as f:
                    student_code = f.read()
                
                # Evaluate submission
                result = codev.evaluate_submission(
                    code=student_code,
                    model_solution=model_solution
                )
                
                if result:
                    # Save results
                    save_results(result, submission_id, output_dir)
                    
                    # Print summary
                    print(f"Evaluation complete for {submission_id}:")
                    print(f"Total Score: {result['total_score']}/35")
                    print(f"Ensemble Size: {result['ensemble_statistics']['evaluations_count']}")
                else:
                    print(f"No evaluation results for submission {submission_id}")
                    
            except Exception as e:
                print(f"Error processing submission {submission_id}: {str(e)}")
                continue

        # Generate final summary
        try:
            csv_file = output_dir / 'csv_results' / 'evaluation_summary.csv'
            if csv_file.exists():
                df = pd.read_csv(csv_file)
                summary = {
                    'total_submissions': len(df),
                    'average_score': df['total_score'].mean(),
                    'median_score': df['total_score'].median(),
                    'min_score': df['total_score'].min(),
                    'max_score': df['total_score'].max(),
                    'score_std': df['total_score'].std()
                }
                
                summary_file = output_dir / 'final_summary.yaml'
                with summary_file.open('w', encoding='utf-8') as f:
                    yaml.dump(summary, f, default_flow_style=False)
                
                print("\nFinal Summary:")
                for key, value in summary.items():
                    print(f"{key}: {value:.2f}")
        
        except Exception as e:
            print(f"Error generating final summary: {str(e)}")
        
        print(f"\nEvaluation complete! Results saved in: {output_dir}")
        
    except Exception as e:
        print(f"Error during evaluation process: {str(e)}")

if __name__ == "__main__":
    main()