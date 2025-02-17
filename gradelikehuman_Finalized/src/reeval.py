from typing import List, Dict, Set, Tuple, Optional
import logging
import yaml
import random
from dataclasses import dataclass
import pandas as pd
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class GradedAnswer:
    """Data class to hold a graded answer and its metadata."""
    problem_id: str
    answer: str
    score: float
    original_index: int

class ReEvaluator:
    """Main class for re-evaluating grading results."""
    
    def __init__(self, 
                 llm_interface,
                 group_size: int = 3,
                 num_subgroups: int = 2,
                 regroup_iterations: int = 2):
        """
        Initialize re-evaluator.
        
        Args:
            llm_interface: Interface to LLM
            group_size: Number of answers to compare in each group
            num_subgroups: Number of subgroups for regrouping
            regroup_iterations: Number of regrouping iterations
        """
        self.llm = llm_interface
        self.group_size = group_size
        self.num_subgroups = num_subgroups
        self.regroup_iterations = regroup_iterations
    
    def evaluate_group(self, 
                      question: str,
                      rubric: Dict,
                      group: List[GradedAnswer]) -> List[Tuple[str, float]]:
        """
        Evaluate a group of graded answers for inconsistencies.
        
        Args:
            question: Original question
            rubric: Grading rubric
            group: List of graded answers to evaluate
            
        Returns:
            List of (problem_id, adjusted_score) tuples
        """
        prompt = self._construct_eval_prompt(question, rubric, group)
        
        try:
            response = self.llm.client.chat.completions.create(
                model=self.llm.model,
                messages=[
                    {"role": "system", "content": "You are an expert at reviewing and calibrating programming assignment grades."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            # Parse response to get adjusted scores
            return self._parse_eval_response(response.choices[0].message.content, group)
            
        except Exception as e:
            logger.error(f"Error evaluating group: {str(e)}")
            return [(answer.problem_id, answer.score) for answer in group]
    
    def _construct_eval_prompt(self, 
                             question: str,
                             rubric: Dict,
                             group: List[GradedAnswer]) -> str:
        """Construct prompt for evaluating a group of answers."""
        prompt = f"""Review the following group of graded programming answers for consistency and adherence to the rubric.

Question:
{question}

Rubric:
{yaml.dump(rubric)}

Graded Answers to Review:
"""
        
        for i, answer in enumerate(group, 1):
            prompt += f"""
Answer {i}:
{answer.answer}
Current Score: {answer.score}
"""
        
        prompt += f"""
Please review these answers and their scores for:
1. Adherence to rubric criteria
2. Consistency between scores
3. Any significant scoring anomalies

For each answer, either:
- Confirm the current score if it's appropriate
- Provide an adjusted score with justification

Format your response as:
Answer 1: [Score] (Confirmed/Adjusted) - [Brief justification]
Answer 2: [Score] (Confirmed/Adjusted) - [Brief justification]
...etc.
"""
        return prompt
    
    def _parse_eval_response(self, 
                            response: str,
                            group: List[GradedAnswer]) -> List[Tuple[str, float]]:
        """Parse LLM response to extract adjusted scores."""
        adjusted_scores = []
        
        try:
            lines = response.strip().split('\n')
            for answer, line in zip(group, lines):
                if 'Answer' not in line:
                    continue
                    
                # Extract score from response
                import re
                numbers = re.findall(r'\d+(?:\.\d+)?', line)
                if numbers:
                    score = float(numbers[0])
                    adjusted_scores.append((answer.problem_id, score))
                else:
                    adjusted_scores.append((answer.problem_id, answer.score))
                    
        except Exception as e:
            logger.error(f"Error parsing evaluation response: {str(e)}")
            return [(answer.problem_id, answer.score) for answer in group]
            
        return adjusted_scores
    
    def create_groups(self, answers: List[GradedAnswer]) -> List[List[GradedAnswer]]:
        """Create initial groups for evaluation."""
        random.shuffle(answers)  # Randomize order
        groups = []
        
        for i in range(0, len(answers), self.group_size):
            group = answers[i:i + self.group_size]
            if len(group) == self.group_size:  # Only use complete groups
                groups.append(group)
            
        return groups
    
    def regroup(self, 
                groups: List[List[GradedAnswer]]) -> List[List[GradedAnswer]]:
        """Implement regrouping strategy."""
        all_answers = [answer for group in groups for answer in group]
        new_groups = []
        
        # Create subgroups
        subgroup_size = self.group_size // self.num_subgroups
        subgroups = []
        
        for group in groups:
            for i in range(0, len(group), subgroup_size):
                subgroup = group[i:i + subgroup_size]
                if len(subgroup) == subgroup_size:
                    subgroups.append(subgroup)
        
        # Recombine subgroups
        random.shuffle(subgroups)
        for i in range(0, len(subgroups), self.num_subgroups):
            if i + self.num_subgroups <= len(subgroups):
                new_group = []
                for j in range(self.num_subgroups):
                    new_group.extend(subgroups[i + j])
                new_groups.append(new_group)
        
        return new_groups
    
    def re_evaluate(self,
                    question: str,
                    rubric: Dict,
                    graded_answers: Dict[str, Tuple[str, float]]) -> Dict[str, float]:
        """
        Re-evaluate graded answers using group comparison and regrouping.
        
        Args:
            question: Original question
            rubric: Grading rubric
            graded_answers: Dictionary mapping problem_id to (answer, score) pairs
            
        Returns:
            Dictionary mapping problem_id to adjusted scores
        """
        # Convert to GradedAnswer objects
        answers = [
            GradedAnswer(
                problem_id=pid,
                answer=answer,
                score=score,
                original_index=i
            )
            for i, (pid, (answer, score)) in enumerate(graded_answers.items())
        ]
        
        # Track all evaluations
        all_evaluations: Dict[str, List[float]] = {
            answer.problem_id: [answer.score] for answer in answers
        }
        
        # Initial grouping and evaluation
        groups = self.create_groups(answers)
        
        for iteration in range(self.regroup_iterations + 1):
            logger.info(f"Starting evaluation iteration {iteration}")
            
            for group in groups:
                results = self.evaluate_group(question, rubric, group)
                
                # Store results
                for pid, score in results:
                    all_evaluations[pid].append(score)
            
            # Regroup if not last iteration
            if iteration < self.regroup_iterations:
                groups = self.regroup(groups)
        
        # Calculate final scores (median of all evaluations)
        final_scores = {}
        for pid, scores in all_evaluations.items():
            final_scores[pid] = float(pd.Series(scores).median())
        
        return final_scores

def save_reeval_grades(grades: Dict[str, float], 
                      output_path: Path,
                      problem_number: int,
                      timestamp: str) -> None:
    """Save re-evaluated grades to CSV."""
    df = pd.DataFrame([
        {"Problem": problem, "Expected Score": score}
        for problem, score in grades.items()
    ])
    
    output_file = output_path / f'reeval_grades_problem{problem_number}_{timestamp}.csv'
    df.to_csv(output_file, index=False)
    logger.info(f"Saved re-evaluated grades to {output_file}")