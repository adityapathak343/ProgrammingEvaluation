#!/usr/bin/env python3
"""
Script to redesign grading rubrics using sample-based improvement.
Part of the Grade Like a Human system.
"""

import sys
import json
import logging
import argparse
from pathlib import Path
from typing import Dict, Any
import os
import sys

# Add the parent directory to Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.append(project_root)

from src.rubric_designer import RubricDesigner
from src.utils import Timer, validate_rubric_format
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
        description='Redesign grading rubric using sample-based improvement'
    )
    
    parser.add_argument(
        '--question',
        required=True,
        help='Path to question file'
    )
    
    parser.add_argument(
        '--initial-rubric',
        required=True,
        help='Path to initial rubric file'
    )
    
    parser.add_argument(
        '--submissions',
        required=True,
        help='Path to submissions file'
    )
    
    parser.add_argument(
        '--output',
        required=True,
        help='Output path for improved rubric'
    )
    
    parser.add_argument(
        '--config',
        default='config.yaml',
        help='Path to configuration file'
    )
    
    parser.add_argument(
        '--sampling',
        choices=['random', 'distribution'],
        default='distribution',
        help='Sampling method for rubric generation'
    )
    
    parser.add_argument(
        '--sample-size',
        type=int,
        default=10,
        help='Number of samples to use per iteration'
    )
    
    parser.add_argument(
        '--iterations',
        type=int,
        default=3,
        help='Number of improvement iterations'
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
    for path_arg in ['question', 'initial_rubric', 'submissions']:
        path = Path(getattr(args, path_arg))
        if not path.exists():
            raise FileNotFoundError(f"{path_arg.replace('_', ' ').title()} file not found: {path}")
    
    # Check output directory exists/can be created
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

def save_results(results: Dict[str, Any], output_path: str, args: argparse.Namespace) -> None:
    """Save redesign results and metadata."""
    output = {
        'improved_rubric': results['rubric_content'],
        'metadata': {
            'sampling_method': args.sampling,
            'sample_size': args.sample_size,
            'iterations': args.iterations,
            'input_files': {
                'question': str(args.question),
                'initial_rubric': str(args.initial_rubric),
                'submissions': str(args.submissions)
            }
        },
        'statistics': results.get('statistics', {}),
        'criteria': results.get('criteria', [])
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
        
        # Initialize rubric designer
        # In redesign_rubric.py
        designer = RubricDesigner(
            model_name=config.get_model_config()['name'],
            prompts=config.get_prompts()  # Add this line
        )
        logger.info("Rubric designer initialized")
        
        # Time the redesign process
        with Timer() as timer:
            # Generate improved rubric
            results = designer.generate_improved_rubric(
                question_path=args.question,
                initial_rubric_path=args.initial_rubric,
                submissions_path=args.submissions,
                sampling_method=args.sampling,
                sample_size=args.sample_size,
                n_iterations=args.iterations
            )
            
            # Validate output format
            if not validate_rubric_format(results):
                raise ValueError("Generated rubric has invalid format")
            
            # Save results
            save_results(results, args.output, args)
        
        # Log completion
        logger.info(f"Rubric redesign completed in {timer.elapsed:.2f} seconds")
        logger.info(f"Improved rubric saved to: {args.output}")
        
    except KeyboardInterrupt:
        logger.error("Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error during rubric redesign: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()