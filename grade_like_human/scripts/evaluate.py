#!/usr/bin/env python3
"""
Script to evaluate student submissions using the improved rubric.
Part of the Grade Like a Human system.
"""

import sys
import json
import logging
import argparse
from pathlib import Path
from typing import Dict, Any
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.append(project_root)

from src.evaluator import Evaluator
from src.utils import Timer, EvaluationMetrics
from src.config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Evaluate student submissions using improved rubric'
    )
    
    parser.add_argument(
        '--question',
        required=True,
        help='Path to question file'
    )
    
    parser.add_argument(
        '--rubric',
        required=True,
        help='Path to rubric file'
    )
    
    parser.add_argument(
        '--submissions',
        required=True,
        help='Path to submissions file'
    )
    
    parser.add_argument(
        '--output',
        required=True,
        help='Output path for evaluation results'
    )
    
    parser.add_argument(
        '--config',
        default='config.yaml',
        help='Path to configuration file'
    )
    
    parser.add_argument(
        '--prompt-strategy',
        choices=['one-shot', 'self-reflection', 'batching'],
        default='one-shot',
        help='Prompting strategy for evaluation'
    )
    
    parser.add_argument(
        '--batch-size',
        type=int,
        default=10,
        help='Batch size for batch processing'
    )
    
    parser.add_argument(
        '--calculate-metrics',
        action='store_true',
        help='Calculate evaluation metrics if true scores available'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    return parser.parse_args()

def validate_paths(args: argparse.Namespace) -> None:
    """Validate input and output paths."""
    # Check input files exist
    for path_arg in ['question', 'rubric', 'submissions']:
        path = Path(getattr(args, path_arg))
        if not path.exists():
            raise FileNotFoundError(f"{path_arg.title()} file not found: {path}")
    
    # Check output directory exists/can be created
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

def calculate_metrics(results: Dict[str, Any], 
                     true_scores: Dict[str, float]) -> Dict[str, float]:
    """Calculate evaluation metrics if true scores are available."""
    predicted_scores = []
    actual_scores = []
    
    for evaluation in results['evaluations']:
        submission_id = evaluation['submission_id']
        if submission_id in true_scores:
            predicted_scores.append(evaluation['score'])
            actual_scores.append(true_scores[submission_id])
    
    if not predicted_scores:
        logger.warning("No matching submissions found for metrics calculation")
        return {}
    
    metrics = EvaluationMetrics.calculate(predicted_scores, actual_scores)
    return {
        'mae': metrics.mae,
        'rmse': metrics.rmse,
        'nrmse': metrics.nrmse,
        'pearson': metrics.pearson
    }

def load_true_scores(submissions_path: str) -> Dict[str, float]:
    """Load true scores from submissions file if available."""
    try:
        import pandas as pd
        df = pd.read_csv(submissions_path)
        if 'Score' in df.columns and 'Folder Name' in df.columns:
            return dict(zip(df['Folder Name'].astype(str), df['Score']))
    except Exception as e:
        logger.warning(f"Could not load true scores: {str(e)}")
    return {}

def save_results(results: Dict[str, Any], 
                metrics: Dict[str, float],
                output_path: str,
                args: argparse.Namespace) -> None:
    """Save evaluation results and metadata."""
    output = {
        'metadata': {
            'prompt_strategy': args.prompt_strategy,
            'batch_size': args.batch_size,
            'input_files': {
                'question': str(args.question),
                'rubric': str(args.rubric),
                'submissions': str(args.submissions)
            }
        },
        'results': results,
        'metrics': metrics,
        'statistics': {
            'total_submissions': len(results['evaluations']),
            'average_score': sum(e['score'] for e in results['evaluations']) / len(results['evaluations']),
            'average_confidence': sum(e.get('confidence', 0) for e in results['evaluations']) / len(results['evaluations'])
        }
    }
    
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
    
    logger.info(f"Results saved to: {output_path}")

def main() -> None:
    """Main execution function."""
    try:
        # Parse arguments
        args = parse_arguments()
        
        # Set logging level
        if args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)
        
        # Load configuration
        config = Config(args.config)
        logger.debug("Configuration loaded")
        
        # Validate paths
        validate_paths(args)
        logger.debug("Paths validated")
        
        # Initialize evaluator
        evaluator = Evaluator(
            model_name=config.get_model_config()['name']
        )
        logger.info("Evaluator initialized")
        
        # Load true scores if metrics calculation requested
        true_scores = {}
        if args.calculate_metrics:
            true_scores = load_true_scores(args.submissions)
            logger.info(f"Loaded {len(true_scores)} true scores")
        
        # Time the evaluation process
        with Timer() as timer:
            # Evaluate submissions
            results = evaluator.evaluate_submissions(
                question_path=args.question,
                rubric_path=args.rubric,
                submissions_path=args.submissions,
                prompt_strategy=args.prompt_strategy,
                batch_size=args.batch_size
            )
            
            # Calculate metrics if requested
            metrics = {}
            if args.calculate_metrics and true_scores:
                metrics = calculate_metrics(results, true_scores)
                logger.info(f"Evaluation metrics calculated: {metrics}")
            
            # Save results
            save_results(results, metrics, args.output, args)
        
        # Log completion
        logger.info(f"Evaluation completed in {timer.elapsed:.2f} seconds")
        logger.info(f"Processed {len(results['evaluations'])} submissions")
        if metrics:
            logger.info(f"MAE: {metrics['mae']:.3f}, RMSE: {metrics['rmse']:.3f}")
        
    except KeyboardInterrupt:
        logger.error("Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error during evaluation: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()