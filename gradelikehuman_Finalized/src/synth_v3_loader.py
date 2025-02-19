import pandas as pd
from pathlib import Path
import logging
from typing import List, Dict, Tuple
import os
import glob

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SynthV3DataLoader:
    """Data loader for Synthetic V3 dataset"""
    
    def __init__(self, base_path: Path):
        """
        Initialize the data loader with base path to synth-v3 directory.
        
        Args:
            base_path: Path to synth-v3 directory
        """
        self.base_path = Path(base_path)
        self.correct_solutions_path = self.base_path / 'correct_solutions_v3'
        self.incorrect_solutions_path = self.base_path / 'incorrect_solutions_v3'
        self.problem_statements_path = self.base_path / 'problem_statements_v3'
        self.rubrics_path = self.base_path / 'rubrics_v3'
        
        # Load and process the CSV file
        self.df = pd.read_csv(self.base_path / 'report_fixed_v3.csv')
        
        # Validate directory structure
        self._validate_directories()
    
    def _validate_directories(self):
        """Validate that all required directories exist."""
        required_dirs = [
            self.correct_solutions_path,
            self.incorrect_solutions_path,
            self.problem_statements_path,
            self.rubrics_path
        ]
        
        for dir_path in required_dirs:
            if not dir_path.exists():
                raise FileNotFoundError(f"Required directory not found: {dir_path}")
    
    def _calculate_average_prompt_score(self, solution_file: str) -> float:
        """Calculate average score across all prompts for a given solution."""
        solution_row = self.df[self.df['Submitted Code'] == solution_file]
        if solution_row.empty:
            logger.warning(f"No scores found for solution: {solution_file}")
            return 0.0
            
        prompt_scores = []
        for i in range(1, 5):  # Prompts 1 to 4
            score_col = f'Prompt{i}_Score'
            if score_col in solution_row.columns:
                score = solution_row[score_col].iloc[0]
                if pd.notna(score):  # Check if score is not NaN
                    prompt_scores.append(score)
                    
        if not prompt_scores:
            return 0.0
        return sum(prompt_scores) / len(prompt_scores)
    
    def get_problem_data(self, problem_number: int) -> Tuple[str, str, List[str]]:
        """
        Get all data related to a specific problem.
        
        Args:
            problem_number: The problem number to load
            
        Returns:
            Tuple containing:
            - Problem statement
            - Initial rubric
            - List of student solutions (correct solution first, followed by incorrect solutions)
        """
        # Load problem statement
        problem_statement_file = self.problem_statements_path / f'problem{problem_number}_statement.txt'
        logger.info(f"Loading problem statement from: {problem_statement_file}")
        with open(problem_statement_file, 'r') as f:
            problem_statement = f.read().strip()
            
        # Load initial rubric
        rubric_file = self.rubrics_path / f'problem{problem_number}_rubric.txt'
        logger.info(f"Loading rubric from: {rubric_file}")
        with open(rubric_file, 'r') as f:
            initial_rubric = f.read().strip()
            
        solutions = []
        
        # Load correct solution
        correct_file = self.correct_solutions_path / f'problem{problem_number}_solution.txt'
        logger.info(f"Loading correct solution from: {correct_file}")
        if not correct_file.exists():
            raise FileNotFoundError(f"Correct solution file not found: {correct_file}")
        with open(correct_file, 'r') as f:
            solutions.append(f.read().strip())
        
        # Load incorrect solutions in specific order
        incorrect_files = [
            f'problem{problem_number}-0pt.txt',
            f'problem{problem_number}-2pt.txt',
            f'problem{problem_number}-4pt.txt',
            f'problem{problem_number}-6pt.txt',
            f'problem{problem_number}-8pt.txt'
        ]
        
        for filename in incorrect_files:
            file_path = self.incorrect_solutions_path / filename
            logger.info(f"Loading incorrect solution from: {file_path}")
            if not file_path.exists():
                raise FileNotFoundError(f"Expected incorrect solution file not found: {file_path}")
            with open(file_path, 'r') as f:
                solutions.append(f.read().strip())
        
        logger.info(f"Loaded {len(solutions)} total solutions:")
        logger.info(f"- 1 correct solution: problem{problem_number}_solution.txt")
        logger.info(f"- {len(solutions)-1} incorrect solutions: {incorrect_files}")
        
        return problem_statement, initial_rubric, solutions
    
    def get_solution_scores(self, problem_number: int) -> Dict[str, float]:
        """
        Get average prompt scores for all solutions of a specific problem.
        
        Args:
            problem_number: The problem number to get scores for
            
        Returns:
            Dictionary mapping solution files to their average scores
        """
        problem_solutions = self.df[self.df['Problem'] == f'problem{problem_number}']
        scores = {}
        
        for _, row in problem_solutions.iterrows():
            solution_file = row['Submitted Code']
            avg_score = self._calculate_average_prompt_score(solution_file)
            scores[solution_file] = avg_score
            
        return scores
    
    def format_initial_rubric(self, rubric_text: str) -> Dict:
        """
        Convert rubric text to dictionary format expected by rubric generator.
        
        Args:
            rubric_text: Raw rubric text
            
        Returns:
            Dictionary containing formatted rubric
        """
        # This is a simple implementation - modify based on your rubric format
        return {
            "criteria": [
                {
                    "description": rubric_text,
                    "points": 10,
                    "key_elements": []
                }
            ],
            "total_points": 10
        }