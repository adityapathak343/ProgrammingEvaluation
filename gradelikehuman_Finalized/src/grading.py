from typing import List, Dict, Optional, Tuple
import logging
import yaml
from abc import ABC, abstractmethod
from pathlib import Path
import pandas as pd

logger = logging.getLogger(__name__)

class GradingStrategy(ABC):
    """Abstract base class for grading strategies."""
    @abstractmethod
    def grade(self, 
             question: str, 
             rubric: Dict, 
             answers: List[str], 
             llm_interface) -> List[float]:
        """
        Grade answers using the strategy.
        
        Args:
            question: The question being evaluated
            rubric: Rubric to use for grading
            answers: List of answers to grade
            llm_interface: Interface to LLM for grading
            
        Returns:
            List of scores
        """
        pass

class OneShot(GradingStrategy):
    """Implementation of one-shot grading strategy."""
    def grade(self, 
             question: str, 
             rubric: Dict, 
             answers: List[str], 
             llm_interface) -> List[float]:
        """Grade each answer individually with one-shot prompting."""
        scores = []
        
        for answer in answers:
            prompt = self._construct_prompt(question, rubric, answer)
            try:
                score = llm_interface.grade_batch([answer], rubric)[0]
                scores.append(score)
            except Exception as e:
                logger.error(f"Error grading answer: {str(e)}")
                scores.append(0.0)
                
        return scores
        
    def _construct_prompt(self, question: str, rubric: Dict, answer: str) -> str:
        """Construct one-shot grading prompt."""
        return f"""Grade the following programming answer according to the provided rubric.

Question:
{question}

Rubric:
{yaml.dump(rubric)}

Answer to Grade:
{answer}

Please provide:
1. Score for each criterion in the rubric
2. Brief justification for each score
3. Total score between 0 and {rubric['total_points']}

Focus on being consistent and fair in your grading.
"""

class SelfReflection(GradingStrategy):
    """Implementation of self-reflection grading strategy."""
    def __init__(self, reflection_rounds: int = 2):
        """
        Initialize strategy.
        
        Args:
            reflection_rounds: Number of reflection rounds
        """
        self.reflection_rounds = reflection_rounds
    
    def grade(self, 
             question: str, 
             rubric: Dict, 
             answers: List[str], 
             llm_interface) -> List[float]:
        """Grade with self-reflection rounds."""
        scores = []
        
        for answer in answers:
            try:
                # Initial grading
                initial_score = llm_interface.grade_batch([answer], rubric)[0]
                current_score = initial_score
                
                # Reflection rounds
                for _ in range(self.reflection_rounds):
                    reflection_prompt = self._construct_reflection_prompt(
                        question, rubric, answer, current_score
                    )
                    
                    response = llm_interface.client.chat.completions.create(
                        model=llm_interface.model,
                        messages=[
                            {"role": "system", "content": "You are an expert at grading programming assignments."},
                            {"role": "user", "content": reflection_prompt}
                        ],
                        temperature=0.3
                    )
                    
                    response_text = response.choices[0].message.content
                    try:
                        # Extract revised score
                        import re
                        numbers = re.findall(r'\d+(?:\.\d+)?', response_text)
                        if numbers:
                            current_score = float(numbers[0])
                    except ValueError:
                        logger.warning("Could not extract revised score")
                        
                scores.append(current_score)
                
            except Exception as e:
                logger.error(f"Error in self-reflection grading: {str(e)}")
                scores.append(0.0)
                
        return scores
        
    def _construct_reflection_prompt(self, 
                                   question: str, 
                                   rubric: Dict, 
                                   answer: str, 
                                   current_score: float) -> str:
        """Construct self-reflection prompt."""
        return f"""You previously graded this programming answer with a score of {current_score}.

Question:
{question}

Rubric:
{yaml.dump(rubric)}

Answer:
{answer}

Please reflect on your grading:
1. Review the score for each criterion
2. Consider if you overlooked any aspects
3. Ensure consistency with the rubric
4. Provide a revised total score if needed (between 0 and {rubric['total_points']})

Explain your reasoning for any score adjustments.
"""

class BatchGrading(GradingStrategy):
    """Implementation of batch grading strategy."""
    def __init__(self, batch_size: int = 3):
        """
        Initialize strategy.
        
        Args:
            batch_size: Number of answers to grade in each batch
        """
        self.batch_size = batch_size
    
    def grade(self, 
             question: str, 
             rubric: Dict, 
             answers: List[str], 
             llm_interface) -> List[float]:
        """Grade answers in batches."""
        scores = []
        
        # Process answers in batches
        for i in range(0, len(answers), self.batch_size):
            batch = answers[i:i + self.batch_size]
            try:
                prompt = self._construct_prompt(question, rubric, batch)
                batch_scores = llm_interface.grade_batch(batch, rubric)
                scores.extend(batch_scores)
            except Exception as e:
                logger.error(f"Error grading batch: {str(e)}")
                scores.extend([0.0] * len(batch))
                
        return scores
        
    def _construct_prompt(self, 
                         question: str, 
                         rubric: Dict, 
                         answers: List[str]) -> str:
        """Construct batch grading prompt."""
        prompt = f"""Grade the following set of programming answers according to the rubric.
Ensure consistent and fair grading across all answers.

Question:
{question}

Rubric:
{yaml.dump(rubric)}

"""
        
        for i, answer in enumerate(answers, 1):
            prompt += f"""
Answer {i}:
{answer}
"""
        
        prompt += f"""
For each answer, provide:
1. Scores for each criterion
2. Brief justification
3. Total score between 0 and {rubric['total_points']}

Maintain consistency across all answers in the batch.
"""
        return prompt

class Grader:
    """Main class for grading system."""
    def __init__(self, 
                 llm_interface,
                 strategy: str = 'batch',
                 batch_size: int = 3,
                 reflection_rounds: int = 2):
        """
        Initialize grader.
        
        Args:
            llm_interface: Interface to LLM
            strategy: Grading strategy ('one-shot', 'self-reflection', or 'batch')
            batch_size: Batch size for batch grading
            reflection_rounds: Number of reflection rounds
        """
        self.llm = llm_interface
        
        # Initialize strategy
        if strategy == 'one-shot':
            self.strategy = OneShot()
        elif strategy == 'self-reflection':
            self.strategy = SelfReflection(reflection_rounds)
        else:
            self.strategy = BatchGrading(batch_size)
    
    def grade_solutions(self, 
                       question: str,
                       rubric: Dict,
                       answers: List[str]) -> List[float]:
        """
        Grade solutions using selected strategy.
        
        Args:
            question: Question being evaluated
            rubric: Rubric to use for grading
            answers: List of answers to grade
            
        Returns:
            List of scores
        """
        return self.strategy.grade(question, rubric, answers, self.llm)

def save_grades(scores: List[float], 
                problem_number: int, 
                output_path: Path,
                timestamp: str) -> None:
    """
    Save grades to CSV file.
    
    Args:
        scores: List of scores
        problem_number: Problem number
        output_path: Path to save CSV
        timestamp: Timestamp for filename
    """
    grades = []
    
    # First entry is the correct solution
    grades.append({
        'Problem': f'problem{problem_number}_solution',
        'Expected Score': scores[0]
    })
    
    # Remaining entries are the incorrect solutions with point values
    point_values = [0, 2, 4, 6, 8]  # Point values for incorrect solutions
    for i, score in enumerate(scores[1:]):
        if i < len(point_values):
            grades.append({
                'Problem': f'problem{problem_number}-{point_values[i]}pt',
                'Expected Score': score
            })
    
    df = pd.DataFrame(grades)
    output_file = output_path / f'grades_problem{problem_number}_{timestamp}.csv'
    df.to_csv(output_file, index=False)
    logger.info(f"Saved grades to {output_file}")