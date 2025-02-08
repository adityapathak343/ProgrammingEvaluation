# src/utils.py

"""
Utility functions and helper classes for the grading system.
Includes metrics calculation, validation, and common operations.
"""

import json
import logging
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, Tuple
from dataclasses import dataclass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class EvaluationMetrics:
    """Stores evaluation metrics for grading results."""
    mae: float  # Mean Absolute Error
    rmse: float  # Root Mean Squared Error
    nrmse: float  # Normalized Root Mean Squared Error
    pearson: float  # Pearson Correlation Coefficient
    
    @classmethod
    def calculate(cls, 
                 predicted_scores: List[float], 
                 actual_scores: List[float]) -> 'EvaluationMetrics':
        """Calculate all metrics for given scores."""
        if len(predicted_scores) != len(actual_scores):
            raise ValueError("Score lists must have same length")
            
        pred = np.array(predicted_scores)
        actual = np.array(actual_scores)
        
        mae = np.mean(np.abs(pred - actual))
        rmse = np.sqrt(np.mean((pred - actual) ** 2))
        nrmse = rmse / np.mean(actual) if np.mean(actual) != 0 else np.inf
        pearson = np.corrcoef(pred, actual)[0, 1]
        
        return cls(mae=mae, rmse=rmse, nrmse=nrmse, pearson=pearson)

def validate_submission_format(submission: Dict[str, Any]) -> bool:
    """
    Validate the format of a submission dictionary.
    Returns True if valid, raises ValueError if invalid.
    """
    required_fields = {'id', 'question_id', 'content'}
    if not all(field in submission for field in required_fields):
        missing = required_fields - set(submission.keys())
        raise ValueError(f"Missing required fields: {missing}")
    return True

def validate_rubric_format(rubric: Dict[str, Any]) -> bool:
    """
    Validate the format of a rubric dictionary.
    Returns True if valid, raises ValueError if invalid.
    """
    required_fields = {'question_id', 'content', 'criteria'}
    if not all(field in rubric for field in required_fields):
        missing = required_fields - set(rubric.keys())
        raise ValueError(f"Missing required fields: {missing}")
        
    for criterion in rubric['criteria']:
        if not all(field in criterion for field in {'description', 'points'}):
            raise ValueError("Invalid criterion format")
    return True

def load_jsonl(file_path: Union[str, Path]) -> List[Dict[str, Any]]:
    """Load data from a JSONL file."""
    data = []
    with open(file_path, 'r') as f:
        for line in f:
            data.append(json.loads(line))
    return data

def save_jsonl(data: List[Dict[str, Any]], file_path: Union[str, Path]) -> None:
    """Save data to a JSONL file."""
    with open(file_path, 'w') as f:
        for item in data:
            f.write(json.dumps(item) + '\n')

def split_into_batches(items: List[Any], batch_size: int) -> List[List[Any]]:
    """Split a list into batches of specified size."""
    return [items[i:i + batch_size] for i in range(0, len(items), batch_size)]

def calculate_agreement(scores1: List[float], 
                       scores2: List[float], 
                       tolerance: float = 0.1) -> float:
    """Calculate agreement rate between two sets of scores."""
    if len(scores1) != len(scores2):
        raise ValueError("Score lists must have same length")
        
    agreements = sum(1 for s1, s2 in zip(scores1, scores2) 
                    if abs(s1 - s2) <= tolerance)
    return agreements / len(scores1)

class Timer:
    """Simple context manager for timing operations."""
    import time
    
    def __enter__(self):
        self.start = self.time.time()
        return self
    
    def __exit__(self, *args):
        self.elapsed = self.time.time() - self.start

