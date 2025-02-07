"""
Main evaluator module for grading submissions using LLMs.
Implements different prompting strategies and batch processing.
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import pandas as pd
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser

from src.data import DataManager, Question, Rubric, Submission

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Evaluator:
    """
    Implements submission grading using different prompting strategies.
    Supports one-shot, self-reflection, and batching approaches.
    """
    
    def __init__(self, model_name: str = "gpt-4", data_dir: str = "./data"):
        """
        Initialize the evaluator.
        
        Args:
            model_name: Name of the LLM model to use
            data_dir: Directory containing data files
        """
        self.llm = ChatOpenAI(model=model_name, temperature=0)
        self.json_parser = JsonOutputParser()
        self.data_manager = DataManager(data_dir)
        
        # Load prompt templates
        with open(Path(data_dir).parent / "prompts/eval_prompts.json", 'r') as f:
            self.prompts = json.load(f)

    def evaluate_submissions(self,
                           question_path: str,
                           rubric_path: str,
                           submissions_path: str,
                           prompt_strategy: str = 'one-shot',
                           batch_size: int = 10) -> Dict[str, Any]:
        """
        Evaluate a set of submissions using specified strategy.
        
        Args:
            question_path: Path to question file
            rubric_path: Path to rubric file
            submissions_path: Path to submissions file
            prompt_strategy: Strategy to use ('one-shot', 'self-reflection', 'batching')
            batch_size: Size of batches for batch processing
            
        Returns:
            Evaluation results including scores and feedback
        """
        logger.info(f"Starting evaluation using {prompt_strategy} strategy")
        
        # Load data
        question = Question.from_file(question_path)
        rubric = Rubric.from_file(rubric_path)
        submissions = self._load_submissions(submissions_path)
        
        results = {
            'question_id': question.id,
            'strategy': prompt_strategy,
            'evaluations': []
        }
        
        if prompt_strategy == 'batching':
            # Process in batches
            for i in range(0, len(submissions), batch_size):
                batch = submissions[i:i + batch_size]
                batch_results = self._evaluate_batch(
                    question=question,
                    rubric=rubric,
                    submissions=batch
                )
                results['evaluations'].extend(batch_results)
                
        else:
            # Process individually
            for submission in submissions:
                evaluation = self._evaluate_single(
                    question=question,
                    rubric=rubric,
                    submission=submission,
                    strategy=prompt_strategy
                )
                results['evaluations'].append(evaluation)
                
        logger.info(f"Completed evaluation of {len(submissions)} submissions")
        return results

    def _evaluate_single(self,
                        question: Question,
                        rubric: Rubric,
                        submission: Submission,
                        strategy: str) -> Dict[str, Any]:
        """
        Evaluate a single submission using specified strategy.
        """
        if strategy == 'one-shot':
            return self._one_shot_evaluation(question, rubric, submission)
        elif strategy == 'self-reflection':
            return self._self_reflection_evaluation(question, rubric, submission)
        else:
            raise ValueError(f"Unknown strategy: {strategy}")

    def _one_shot_evaluation(self,
                           question: Question,
                           rubric: Rubric,
                           submission: Submission) -> Dict[str, Any]:
        """
        Evaluate using one-shot prompting strategy.
        """
        prompt = self.prompts["one_shot"].format(
            question=question.text,
            rubric=rubric.content,
            submission=submission.content,
            max_points=question.max_points
        )
        
        response = self.llm.invoke(prompt)
        result = self.json_parser.parse(response.content)
        
        return {
            'submission_id': submission.id,
            'score': result['score'],
            'feedback': result['feedback'],
            'confidence': result.get('confidence', 0)
        }

    def _self_reflection_evaluation(self,
                                  question: Question,
                                  rubric: Rubric,
                                  submission: Submission) -> Dict[str, Any]:
        """
        Evaluate using self-reflection strategy.
        First grades normally, then reflects and potentially revises.
        """
        # Initial grading
        initial_result = self._one_shot_evaluation(question, rubric, submission)
        
        # Self-reflection
        reflection_prompt = self.prompts["self_reflection"].format(
            question=question.text,
            rubric=rubric.content,
            submission=submission.content,
            initial_evaluation=json.dumps(initial_result, indent=2),
            max_points=question.max_points
        )
        
        response = self.llm.invoke(reflection_prompt)
        final_result = self.json_parser.parse(response.content)
        
        return {
            'submission_id': submission.id,
            'score': final_result['score'],
            'feedback': final_result['feedback'],
            'confidence': final_result.get('confidence', 0),
            'reflection': final_result.get('reflection', '')
        }

    def _evaluate_batch(self,
                       question: Question,
                       rubric: Rubric,
                       submissions: List[Submission]) -> List[Dict[str, Any]]:
        """
        Evaluate a batch of submissions together for consistency.
        """
        batch_prompt = self.prompts["batching"].format(
            question=question.text,
            rubric=rubric.content,
            submissions=json.dumps([s.content for s in submissions], indent=2),
            max_points=question.max_points
        )
        
        response = self.llm.invoke(batch_prompt)
        results = self.json_parser.parse(response.content)
        
        # Match results with submission IDs
        evaluations = []
        for submission, result in zip(submissions, results['evaluations']):
            evaluation = {
                'submission_id': submission.id,
                'score': result['score'],
                'feedback': result['feedback'],
                'confidence': result.get('confidence', 0)
            }
            evaluations.append(evaluation)
            
        return evaluations

    def _load_submissions(self, submissions_path: str) -> List[Submission]:
        """Load and parse submissions file."""
        df = pd.read_csv(submissions_path)
        submissions = []
        
        for _, row in df.iterrows():
            submission = Submission(
                id=str(row['Folder Name']),
                question_id='',  # Will be set based on context
                content=row['Answer'],
                score=row.get('Score')
            )
            submissions.append(submission)
            
        return submissions

    def save_results(self, results: Dict[str, Any], output_path: str) -> None:
        """Save evaluation results to file."""
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)

if __name__ == "__main__":
    # Example usage
    evaluator = Evaluator()
    
    results = evaluator.evaluate_submissions(
        question_path="data/questions/q1.txt",
        rubric_path="data/rubrics/q1_improved.txt",
        submissions_path="data/submissions/q1_submissions.csv",
        prompt_strategy='batching',
        batch_size=10
    )
    
    evaluator.save_results(results, "data/results/q1_evaluations.json")
    print(f"Evaluated {len(results['evaluations'])} submissions")