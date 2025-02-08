"""
Rubric designer module for generating and improving grading rubrics.
Uses LLM-based generation with sample-based refinement as described in the paper.
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

class RubricDesigner:
    """
    Implements rubric generation and improvement using LLMs.
    Supports both random and distribution-aware sampling strategies.
    """
    
    def __init__(self, model_name: str = "gpt-4", data_dir: str = "./data"):
        """
        Initialize the rubric designer.
        
        Args:
            model_name: Name of the LLM model to use
            data_dir: Directory containing data files
        """
        self.llm = ChatOpenAI(model=model_name, temperature=0)
        self.json_parser = JsonOutputParser()
        self.data_manager = DataManager(data_dir)
        
        # Load prompt templates
        with open(Path(data_dir).parent / "prompts/rubric_prompts.json", 'r') as f:
            self.prompts = json.load(f)

    def generate_improved_rubric(self,
                               question_path: str,
                               initial_rubric_path: str,
                               submissions_path: str,
                               sampling_method: str = 'distribution',
                               sample_size: int = 10,
                               n_iterations: int = 3) -> str:
        """
        Generate an improved rubric through iterative refinement.
        
        Args:
            question_path: Path to question file
            initial_rubric_path: Path to initial rubric
            submissions_path: Path to submissions file
            sampling_method: Sampling strategy ('random' or 'distribution')
            sample_size: Number of samples per iteration
            n_iterations: Number of improvement iterations
            
        Returns:
            Improved rubric content
        """
        logger.info(f"Starting rubric generation with {sampling_method} sampling")
        
        # Load initial data
        question = Question.from_file(question_path)
        current_rubric = Rubric.from_file(initial_rubric_path)
        submissions = self._load_submissions(submissions_path)
        
        # Perform iterative improvement
        for i in range(n_iterations):
            logger.info(f"Starting iteration {i+1}/{n_iterations}")
            
            # Sample submissions
            if sampling_method == 'distribution':
                samples = self._distribution_aware_sampling(
                    submissions=submissions,
                    rubric=current_rubric,
                    sample_size=sample_size
                )
            else:
                samples = self._random_sampling(
                    submissions=submissions,
                    sample_size=sample_size
                )
            
            # Get human scores for samples
            scored_samples = self._get_sample_scores(samples)
            
            # Generate improved rubric
            current_rubric = self._generate_rubric(
                question=question,
                current_rubric=current_rubric,
                samples=scored_samples
            )
            
            logger.info(f"Completed iteration {i+1}")
            
        return current_rubric.content

    def _distribution_aware_sampling(self,
                                   submissions: List[Submission],
                                   rubric: Rubric,
                                   sample_size: int,
                                   n_strata: int = 5) -> List[Submission]:
        """
        Implement distribution-aware sampling as described in the paper.
        
        Args:
            submissions: List of submissions to sample from
            rubric: Current rubric for initial grading
            sample_size: Number of samples to select
            n_strata: Number of score strata
            
        Returns:
            Selected sample submissions
        """
        # First grade all submissions with current rubric
        initial_scores = []
        for submission in submissions:
            score = self._grade_submission(submission, rubric)
            initial_scores.append({
                'submission': submission,
                'score': score
            })
        
        # Create score distribution
        df = pd.DataFrame(initial_scores)
        df['stratum'] = pd.qcut(df['score'], q=n_strata, labels=False)
        
        # Sample from each stratum
        samples_per_stratum = max(1, sample_size // n_strata)
        selected_samples = []
        
        for stratum in range(n_strata):
            stratum_data = df[df['stratum'] == stratum]
            if len(stratum_data) > 0:
                n_samples = min(samples_per_stratum, len(stratum_data))
                sampled = stratum_data.sample(n=n_samples)
                selected_samples.extend(sampled['submission'].tolist())
        
        return selected_samples

    def _random_sampling(self,
                        submissions: List[Submission],
                        sample_size: int) -> List[Submission]:
        """Simple random sampling of submissions."""
        df = pd.DataFrame({'submission': submissions})
        sampled = df.sample(n=min(sample_size, len(df)))
        return sampled['submission'].tolist()

    def _grade_submission(self, 
                         submission: Submission, 
                         rubric: Rubric) -> float:
        """
        Grade a submission using the current rubric and LLM.
        Used for initial grading in distribution-aware sampling.
        """
        prompt = self.prompts["grading"].format(
            submission=submission.content,
            rubric=rubric.content
        )
        
        response = self.llm.invoke(prompt)
        result = self.json_parser.parse(response.content)
        return float(result['score'])

    def _get_sample_scores(self, samples: List[Submission]) -> List[Dict[str, Any]]:
        """
        Get human scores for sample submissions.
        In practice, this would interface with a human grading system.
        For now, we'll simulate with existing scores if available.
        """
        scored_samples = []
        for sample in samples:
            if sample.score is not None:
                scored_samples.append({
                    'submission': sample.content,
                    'score': sample.score
                })
            else:
                logger.warning(f"No score available for submission {sample.id}")
        return scored_samples

    def _generate_rubric(self,
                        question: Question,
                        current_rubric: Rubric,
                        samples: List[Dict[str, Any]]) -> Rubric:
        """
        Generate improved rubric using LLM based on samples.
        """
        prompt = self.prompts["rubric_generation"].format(
            question=question.text,
            current_rubric=current_rubric.content,
            samples=json.dumps(samples, indent=2),
            max_points=question.max_points
        )
        
        response = self.llm.invoke(prompt)
        result = self.json_parser.parse(response.content)
        
        return Rubric(
            question_id=question.id,
            content=result['rubric_content'],
            criteria=result['criteria']
        )

    def _load_submissions(self, submissions_path: str) -> List[Submission]:
        """Load and parse submissions file."""
        logger.info(f"Loading submissions from {submissions_path}")
        
        try:
            # Read the CSV file with folder names and scores
            df = pd.read_csv(submissions_path)
            logger.debug(f"CSV columns found: {df.columns.tolist()}")
            
            # Get the submissions directory path
            submissions_dir = Path(submissions_path).parent
            
            submissions = []
            for _, row in df.iterrows():
                try:
                    folder_name = str()
                    # Construct path to the java file
                    java_file = submissions_dir / folder_name / "p1.java"
                    
                    if not java_file.exists():
                        logger.warning(f"Submission file not found: {java_file}")
                        continue
                        
                    # Read the actual submission content
                    with open(java_file, 'r') as f:
                        content = f.read()
                    
                    submission = Submission(
                        id=folder_name,
                        question_id='',  # Will be set based on context
                        content=content,
                        score=row.get('Part1 Total')  # Get score from Part1 Total
                    )
                    submissions.append(submission)
                    logger.debug(f"Loaded submission for {folder_name}")
                    
                except Exception as e:
                    logger.warning(f"Error processing submission {folder_name}: {str(e)}")
                    continue
                    
            logger.info(f"Successfully loaded {len(submissions)} submissions")
            return submissions
            
        except Exception as e:
            logger.error(f"Error loading submissions: {str(e)}")
            raise
    
if __name__ == "__main__":
    # Example usage
    designer = RubricDesigner()
    
    improved_rubric = designer.generate_improved_rubric(
        question_path="data/questions/q1.txt",
        initial_rubric_path="data/rubrics/q1_original.txt",
        submissions_path="data/submissions/q1_submissions.csv",
        sampling_method='distribution'
    )
    
    print("Generated improved rubric:")
    print(improved_rubric)