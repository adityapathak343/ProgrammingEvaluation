import argparse
from pathlib import Path
import logging
import yaml
import os
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

from src.rubric_generator import (
    RubricGenerator,
    RandomSampling,
    DistributionAwareSampling,
    save_yaml
)
from src.synth_v3_loader import SynthV3DataLoader
from src.openai_interface import OpenAIInterface
from src.grading import Grader, save_grades
from src.reeval import ReEvaluator, save_reeval_grades

# Load environment variables
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Three-Stage Pipeline: Rubric Generation, Grading, and Re-evaluation')
    
    # Required arguments
    parser.add_argument(
        '--problem-number',
        type=int,
        required=True,
        help='Problem number to process'
    )
    
    parser.add_argument(
        '--synth-v3-path',
        type=str,
        required=True,
        help='Path to synth-v3 directory'
    )
    
    # Pipeline control
    parser.add_argument(
        '--stages',
        nargs='+',
        choices=['rubric', 'grade', 'reeval'],
        default=['rubric', 'grade', 'reeval'],
        help='Stages to run'
    )
    
    # Rubric generation arguments
    parser.add_argument(
        '--sampling-method',
        choices=['random', 'distribution'],
        default='distribution',
        help='Sampling method for rubric generation'
    )
    
    parser.add_argument(
        '--sample-size',
        type=int,
        default=5,
        help='Number of samples per iteration'
    )
    
    parser.add_argument(
        '--max-epochs',
        type=int,
        default=3,
        help='Maximum number of epochs'
    )
    
    # Grading arguments
    parser.add_argument(
        '--grading-strategy',
        choices=['one-shot', 'self-reflection', 'batch'],
        default='batch',
        help='Grading strategy to use'
    )
    
    parser.add_argument(
        '--batch-size',
        type=int,
        default=3,
        help='Batch size for batch grading'
    )
    
    # Re-evaluation arguments
    parser.add_argument(
        '--reeval-group-size',
        type=int,
        default=3,
        help='Group size for re-evaluation'
    )
    
    parser.add_argument(
        '--reeval-iterations',
        type=int,
        default=2,
        help='Number of regrouping iterations'
    )
    
    # General arguments
    parser.add_argument(
        '--output-dir',
        type=str,
        default='output',
        help='Directory to save output files'
    )
    
    parser.add_argument(
        '--model',
        type=str,
        default='gpt-4o-mini',
        help='OpenAI model to use'
    )
    
    # Optional file inputs
    parser.add_argument(
        '--existing-rubric',
        type=str,
        help='Path to existing rubric YAML file (to skip rubric generation)'
    )
    
    parser.add_argument(
        '--existing-grades',
        type=str,
        help='Path to existing grades CSV file (to skip grading)'
    )
    
    return parser.parse_args()

def setup_directories(output_dir: str) -> dict[Path, Path]:
    """Create necessary directories."""
    base_dir = Path.cwd()
    paths = {
        'output': base_dir / output_dir,
        'logs': base_dir / 'logs',
        'rubrics': base_dir / output_dir / 'rubrics',
        'grades': base_dir / output_dir / 'grades',
        'reeval': base_dir / output_dir / 'reeval'
    }
    
    for path in paths.values():
        path.mkdir(exist_ok=True, parents=True)
        
    return paths

def run_rubric_generation(args, paths: dict[Path, Path], llm, data_loader, timestamp: str):
    """Run rubric generation stage."""
    logger.info("Starting rubric generation stage")
    
    if args.existing_rubric:
        logger.info(f"Using existing rubric from {args.existing_rubric}")
        with open(args.existing_rubric, 'r') as f:
            rubric = yaml.safe_load(f)
        problem_statement, _, solutions = data_loader.get_problem_data(args.problem_number)
        return problem_statement, rubric, solutions
    
    # Load problem data
    problem_statement, initial_rubric_text, solutions = data_loader.get_problem_data(
        args.problem_number
    )
    
    # Format initial rubric
    initial_rubric = llm.format_initial_rubric(initial_rubric_text)
    
    # Initialize sampling strategy
    sampling_strategy = (
        RandomSampling() if args.sampling_method == 'random'
        else DistributionAwareSampling(llm)
    )
    
    # Initialize generator
    generator = RubricGenerator(
        sampling_strategy=sampling_strategy,
        llm_interface=llm,
        sample_size=args.sample_size,
        max_epochs=args.max_epochs
    )
    
    # Generate improved rubric
    final_rubric = generator.generate_rubric(
        question=problem_statement,
        initial_rubric=initial_rubric,
        answers=solutions
    )
    
    # Save rubric
    rubric_file = paths['rubrics'] / f'problem{args.problem_number}_rubric_{timestamp}.yaml'
    save_yaml(final_rubric, rubric_file)
    logger.info(f"Saved generated rubric to {rubric_file}")
    
    return problem_statement, final_rubric, solutions

def run_grading(args, paths: dict[Path, Path], llm, problem_statement: str,
                rubric: dict, solutions: list[str], timestamp: str):
    """Run grading stage."""
    logger.info("Starting grading stage")
    
    if args.existing_grades:
        logger.info(f"Using existing grades from {args.existing_grades}")
        grades_df = pd.read_csv(args.existing_grades)
        grades = dict(zip(grades_df['Problem'], grades_df['Expected Score']))
        return grades
    
    # Initialize grader
    grader = Grader(
        llm_interface=llm,
        strategy=args.grading_strategy,
        batch_size=args.batch_size,
        reflection_rounds=2
    )
    
    # Grade solutions
    scores = grader.grade_solutions(
        question=problem_statement,
        rubric=rubric,
        answers=solutions
    )
    
    # Save grades
    save_grades(
        scores=scores,
        problem_number=args.problem_number,
        output_path=paths['grades'],
        timestamp=timestamp
    )
    
    # Create grades dictionary
    solution_names = [
        'problem{}_solution'.format(args.problem_number)
    ] + [
        'problem{}-{}pt'.format(args.problem_number, pts)
        for pts in [0, 2, 4, 6, 8]
    ]
    
    grades = dict(zip(solution_names, scores))
    return grades

def run_reeval(args, paths: dict[Path, Path], llm, problem_statement: str,
               rubric: dict, grades: dict, solutions: list[str], timestamp: str):
    """Run re-evaluation stage."""
    logger.info("Starting re-evaluation stage")
    
    # Create answer-score pairs
    graded_answers = {}
    for (problem_id, score), answer in zip(grades.items(), solutions):
        graded_answers[problem_id] = (answer, score)
    
    # Initialize re-evaluator
    reeval = ReEvaluator(
        llm_interface=llm,
        group_size=args.reeval_group_size,
        regroup_iterations=args.reeval_iterations
    )
    
    # Run re-evaluation
    final_grades = reeval.re_evaluate(
        question=problem_statement,
        rubric=rubric,
        graded_answers=graded_answers
    )
    
    # Save re-evaluated grades
    save_reeval_grades(
        grades=final_grades,
        output_path=paths['reeval'],
        problem_number=args.problem_number,
        timestamp=timestamp
    )
    
    return final_grades

def main():
    # Parse arguments
    args = parse_args()
    
    # Setup directories
    paths = setup_directories(args.output_dir)
    
    # Initialize logging
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = paths['logs'] / f'run_{timestamp}.log'
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    logger.addHandler(file_handler)
    
    try:
        # Get OpenAI API key
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OpenAI API key not found in environment variables")
        
        # Initialize components
        llm = OpenAIInterface(api_key=api_key, model=args.model)
        data_loader = SynthV3DataLoader(args.synth_v3_path)
        
        problem_statement = None
        rubric = None
        solutions = None
        grades = None
        
        # Run pipeline stages
        if 'rubric' in args.stages:
            problem_statement, rubric, solutions = run_rubric_generation(
                args, paths, llm, data_loader, timestamp
            )
        
        if 'grade' in args.stages:
            if not all([problem_statement, rubric, solutions]):
                problem_statement, rubric, solutions = run_rubric_generation(
                    args, paths, llm, data_loader, timestamp
                )
            grades = run_grading(
                args, paths, llm, problem_statement, rubric, solutions, timestamp
            )
        
        if 'reeval' in args.stages:
            if not all([problem_statement, rubric, solutions, grades]):
                if not all([problem_statement, rubric, solutions]):
                    problem_statement, rubric, solutions = run_rubric_generation(
                        args, paths, llm, data_loader, timestamp
                    )
                if not grades:
                    grades = run_grading(
                        args, paths, llm, problem_statement, rubric, solutions, timestamp
                    )
            final_grades = run_reeval(
                args, paths, llm, problem_statement, rubric, grades, solutions, timestamp
            )
        
        logger.info("Pipeline completed successfully")
        
    except Exception as e:
        logger.error(f"Error during execution: {str(e)}", exc_info=True)
        raise
    
    finally:
        file_handler.close()
        logger.removeHandler(file_handler)

if __name__ == "__main__":
    main()