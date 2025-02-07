"""
Re-evaluator module for reviewing and refining grading results.
Implements group comparison and re-grouping strategies for detecting anomalies.
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Set, Tuple
import pandas as pd
import numpy as np
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser

from src.data import DataManager, Question, Rubric, Submission

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ReEvaluator:
    """
    Implements post-grading review and re-evaluation using group comparison.
    Supports re-grouping strategy for better anomaly detection.
    """
    
    def __init__(self, model_name: str = "gpt-4", data_dir: str = "./data"):
        """
        Initialize the re-evaluator.
        
        Args:
            model_name: Name of the LLM model to use
            data_dir: Directory containing data files
        """
        self.llm = ChatOpenAI(model=model_name, temperature=0)
        self.json_parser = JsonOutputParser()
        self.data_manager = DataManager(data_dir)
        
        # Load prompt templates
        with open(Path(data_dir).parent / "prompts/reeval_prompts.json", 'r') as f:
            self.prompts = json.load(f)

    def re_evaluate(self,
                   question_path: str,
                   rubric_path: str,
                   evaluations_path: str,
                   batch_size: int = 10,
                   regroup_rounds: int = 2) -> Dict[str, Any]:
        """
        Re-evaluate grading results to identify and correct anomalies.
        
        Args:
            question_path: Path to question file
            rubric_path: Path to rubric file
            evaluations_path: Path to evaluation results
            batch_size: Size of groups for comparison
            regroup_rounds: Number of regrouping rounds
            
        Returns:
            Re-evaluation results including corrections
        """
        logger.info("Starting re-evaluation process")
        
        # Load data
        question = Question.from_file(question_path)
        rubric = Rubric.from_file(rubric_path)
        with open(evaluations_path, 'r') as f:
            initial_evaluations = json.load(f)
        
        # Track anomalies across rounds
        all_anomalies: Set[str] = set()
        
        # Initial grouping and review
        groups = self._create_groups(initial_evaluations['evaluations'], batch_size)
        anomalies = self._review_groups(question, rubric, groups)
        all_anomalies.update(anomalies)
        
        # Perform regrouping rounds
        for round in range(regroup_rounds):
            logger.info(f"Starting regrouping round {round + 1}/{regroup_rounds}")
            
            # Create new groups with regrouping strategy
            new_groups = self._regroup_submissions(
                evaluations=initial_evaluations['evaluations'],
                previous_anomalies=all_anomalies,
                batch_size=batch_size
            )
            
            # Review new groups
            round_anomalies = self._review_groups(question, rubric, new_groups)
            all_anomalies.update(round_anomalies)
        
        # Re-grade anomalous submissions
        final_results = self._process_anomalies(
            question=question,
            rubric=rubric,
            evaluations=initial_evaluations['evaluations'],
            anomalies=all_anomalies
        )
        
        logger.info(f"Completed re-evaluation. Found {len(all_anomalies)} anomalies")
        return final_results

    def _create_groups(self, 
                      evaluations: List[Dict[str, Any]], 
                      batch_size: int) -> List[List[Dict[str, Any]]]:
        """Create initial groups for review."""
        return [evaluations[i:i + batch_size] 
                for i in range(0, len(evaluations), batch_size)]

    def _review_groups(self,
                      question: Question,
                      rubric: Rubric,
                      groups: List[List[Dict[str, Any]]]) -> Set[str]:
        """
        Review groups of evaluations to identify anomalies.
        """
        anomalies = set()
        
        for group in groups:
            prompt = self.prompts["group_review"].format(
                question=question.text,
                rubric=rubric.content,
                evaluations=json.dumps(group, indent=2),
                max_points=question.max_points
            )
            
            response = self.llm.invoke(prompt)
            result = self.json_parser.parse(response.content)
            
            if result.get('anomalies'):
                anomalies.update(result['anomalies'])
                
        return anomalies

    def _regroup_submissions(self,
                           evaluations: List[Dict[str, Any]],
                           previous_anomalies: Set[str],
                           batch_size: int) -> List[List[Dict[str, Any]]]:
        """
        Implement regrouping strategy for better anomaly detection.
        """
        # Convert to DataFrame for easier manipulation
        df = pd.DataFrame(evaluations)
        
        # Ensure anomalous submissions are distributed across groups
        anomalous = df[df['submission_id'].isin(previous_anomalies)]
        non_anomalous = df[~df['submission_id'].isin(previous_anomalies)]
        
        # Sort by score to group similar scores together
        non_anomalous = non_anomalous.sort_values('score')
        
        # Create new groups
        new_groups = []
        current_group = []
        
        # Add one anomalous submission to each group if available
        for _, row in non_anomalous.iterrows():
            current_group.append(row.to_dict())
            
            if len(current_group) == batch_size - 1 and not anomalous.empty:
                # Add an anomalous submission to the group
                current_group.append(anomalous.iloc[0].to_dict())
                anomalous = anomalous.iloc[1:]
                
                new_groups.append(current_group)
                current_group = []
            elif len(current_group) == batch_size:
                new_groups.append(current_group)
                current_group = []
        
        # Add any remaining submissions
        if current_group:
            new_groups.append(current_group)
            
        return new_groups

    def _process_anomalies(self,
                          question: Question,
                          rubric: Rubric,
                          evaluations: List[Dict[str, Any]],
                          anomalies: Set[str]) -> Dict[str, Any]:
        """
        Re-grade anomalous submissions and prepare final results.
        """
        final_evaluations = []
        
        for eval in evaluations:
            if eval['submission_id'] in anomalies:
                # Re-grade anomalous submission
                new_grade = self._regrade_submission(
                    question=question,
                    rubric=rubric,
                    evaluation=eval
                )
                final_evaluations.append(new_grade)
            else:
                final_evaluations.append(eval)
        
        return {
            'question_id': question.id,
            'total_evaluations': len(evaluations),
            'anomalies_found': len(anomalies),
            'evaluations': final_evaluations
        }

    def _regrade_submission(self,
                          question: Question,
                          rubric: Rubric,
                          evaluation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Re-grade a single anomalous submission.
        """
        prompt = self.prompts["regrade"].format(
            question=question.text,
            rubric=rubric.content,
            previous_evaluation=json.dumps(evaluation, indent=2),
            max_points=question.max_points
        )
        
        response = self.llm.invoke(prompt)
        result = self.json_parser.parse(response.content)
        
        return {
            'submission_id': evaluation['submission_id'],
            'original_score': evaluation['score'],
            'revised_score': result['score'],
            'feedback': result['feedback'],
            'revision_reason': result.get('revision_reason', '')
        }

    def save_results(self, results: Dict[str, Any], output_path: str) -> None:
        """Save re-evaluation results to file."""
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)

if __name__ == "__main__":
    # Example usage
    re_evaluator = ReEvaluator()
    
    results = re_evaluator.re_evaluate(
        question_path="data/questions/q1.txt",
        rubric_path="data/rubrics/q1_improved.txt",
        evaluations_path="data/results/q1_evaluations.json",
        batch_size=10,
        regroup_rounds=2
    )
    
    re_evaluator.save_results(results, "data/results/q1_final_evaluations.json")
    print(f"Re-evaluated {results['total_evaluations']} submissions")
    print(f"Found and corrected {results['anomalies_found']} anomalies")