#!/usr/bin/env python3
"""
Script to re-evaluate grading results and detect anomalies.
Part of the Grade Like a Human system.
"""

import sys
import json
import logging
import argparse
from pathlib import Path
from typing import Dict, Any, List, Set
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.append(project_root)

from src.re_evaluator import ReEvaluator
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
        description='Re-evaluate grading results to detect and correct anomalies'
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
        '--evaluations',
        required=True,
        help='Path to initial evaluation results'
    )
    
    parser.add_argument(
        '--output',
        required=True,
        help='Output path for re-evaluation results'
    )
    
    parser.add_argument(
        '--config',
        default='config.yaml',
        help='Path to configuration file'
    )
    
    parser.add_argument(
        '--batch-size',
        type=int,
        default=10,
        help='Size of groups for comparison'
    )
    
    parser.add_argument(
        '--regroup-rounds',
        type=int,
        default=2,
        help='Number of regrouping rounds'
    )
    
    parser.add_argument(
        '--anomaly-threshold',
        type=float,
        default=0.1,
        help='Threshold for anomaly detection'
    )
    
    parser.add_argument(
        '--calculate-metrics',
        action='store_true',
        help='Calculate metrics comparing original and revised grades'
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
    for path_arg in ['question', 'rubric', 'evaluations']:
        path = Path(getattr(args, path_arg))
        if not path.exists():
            raise FileNotFoundError(f"{path_arg.title()} file not found: {path}")
    
    # Check output directory exists/can be created
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

def load_evaluations(path: str) -> Dict[str, Any]:
    """Load initial evaluation results."""
    with open(path, 'r') as f:
        evaluations = json.load(f)
    
    if 'results' not in evaluations or 'evaluations' not in evaluations['results']:
        raise ValueError("Invalid evaluation results format")
        
    return evaluations

def calculate_comparison_metrics(original_scores: List[float], 
                              revised_scores: List[float],
                              submission_ids: List[str]) -> Dict[str, Any]:
    """Calculate metrics comparing original and revised grades."""
    metrics = EvaluationMetrics.calculate(revised_scores, original_scores)
    
    # Find largest changes
    changes = [(sid, rev - orig) for sid, rev, orig 
               in zip(submission_ids, revised_scores, original_scores)]
    largest_changes = sorted(changes, key=lambda x: abs(x[1]), reverse=True)[:5]
    
    return {
        'comparison_metrics': {
            'mae': metrics.mae,
            'rmse': metrics.rmse,
            'nrmse': metrics.nrmse,
            'pearson': metrics.pearson
        },
        'grade_changes': {
            'total_changes': sum(1 for _, change in changes if change != 0),
            'average_change': sum(abs(change) for _, change in changes) / len(changes),
            'largest_changes': [
                {'submission_id': sid, 'change': change}
                for sid, change in largest_changes
            ]
        }
    }

def save_results(results: Dict[str, Any],
                comparison_metrics: Dict[str, Any],
                output_path: str,
                args: argparse.Namespace) -> None:
    """Save re-evaluation results and metadata."""
    output = {
        'metadata': {
            'batch_size': args.batch_size,
            'regroup_rounds': args.regroup_rounds,
            'anomaly_threshold': args.anomaly_threshold,
            'input_files': {
                'question': str(args.question),
                'rubric': str(args.rubric),
                'evaluations': str(args.evaluations)
            }
        },
        'results': results,
        'comparison_metrics': comparison_metrics,
        'statistics': {
            'total_submissions': len(results['evaluations']),
            'anomalies_found': results.get('anomalies_found', 0),
            'grades_revised': sum(1 for e in results['evaluations'] 
                                if e.get('revised_score') is not None)
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
        
        # Initialize re-evaluator
        re_evaluator = ReEvaluator(
            model_name=config.get_model_config()['name']
        )
        logger.info("Re-evaluator initialized")
        
        # Load initial evaluations
        initial_evaluations = load_evaluations(args.evaluations)
        logger.info(f"Loaded {len(initial_evaluations['results']['evaluations'])} evaluations")
        
        # Time the re-evaluation process
        with Timer() as timer:
            # Re-evaluate submissions
            results = re_evaluator.re_evaluate(
                question_path=args.question,
                rubric_path=args.rubric,
                evaluations_path=args.evaluations,
                batch_size=args.batch_size,
                regroup_rounds=args.regroup_rounds
            )
            
            # Calculate comparison metrics if requested
            comparison_metrics = {}
            if args.calculate_metrics:
                original_scores = [e['score'] for e in initial_evaluations['results']['evaluations']]
                revised_scores = [e.get('revised_score', e['score']) for e in results['evaluations']]
                submission_ids = [e['submission_id'] for e in results['evaluations']]
                
                comparison_metrics = calculate_comparison_metrics(
                    original_scores, revised_scores, submission_ids
                )
                logger.info(f"Comparison metrics calculated: {comparison_metrics}")
            
            # Save results
            save_results(results, comparison_metrics, args.output, args)
        
        # Log completion
        logger.info(f"Re-evaluation completed in {timer.elapsed:.2f} seconds")
        logger.info(f"Found {results.get('anomalies_found', 0)} anomalies")
        logger.info(f"Revised {sum(1 for e in results['evaluations'] if e.get('revised_score') is not None)} grades")
        
    except KeyboardInterrupt:
        logger.error("Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error during re-evaluation: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()