from typing import List, Dict, Set, Tuple, Optional
from pathlib import Path
import random
import logging
from abc import ABC, abstractmethod
import yaml

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SamplingStrategy(ABC):
    """Abstract base class for sampling strategies."""
    @abstractmethod
    def sample(self, answers: List[str], sample_size: int, used_indices: Set[int], current_rubric: Dict) -> Tuple[List[str], Set[int]]:
        """
        Sample answers from the pool of available answers.
        
        Args:
            answers: List of all student answers
            sample_size: Number of samples to select
            used_indices: Set of indices that have already been used
            current_rubric: Current rubric being used for grading
            
        Returns:
            Tuple containing:
            - List of selected answers
            - Set of indices of selected answers
        """
        pass

class RandomSampling(SamplingStrategy):
    """Implementation of random sampling strategy."""
    def sample(self, answers: List[str], sample_size: int, used_indices: Set[int], current_rubric: Dict = None) -> Tuple[List[str], Set[int]]:
        """
        Randomly sample answers from the pool of available answers.
        
        Args:
            answers: List of all student answers
            sample_size: Number of samples to select
            used_indices: Set of indices that have already been used
            current_rubric: Current rubric (not used in random sampling)
            
        Returns:
            Tuple containing:
            - List of randomly selected answers
            - Set of indices of selected answers
        """
        available_indices = set(range(len(answers))) - used_indices
        if len(available_indices) < sample_size:
            logger.warning(f"Only {len(available_indices)} samples available, less than requested {sample_size}")
            sample_size = len(available_indices)
        
        selected_indices = random.sample(list(available_indices), sample_size)
        selected_answers = [answers[i] for i in selected_indices]
        return selected_answers, set(selected_indices)

class DistributionAwareSampling(SamplingStrategy):
    """Implementation of distribution-aware sampling strategy."""
    def __init__(self, llm_grader):
        """
        Initialize with LLM grader interface.
        
        Args:
            llm_grader: Interface to LLM for grading answers
        """
        self.llm_grader = llm_grader
        
    def sample(self, answers: List[str], sample_size: int, used_indices: Set[int], current_rubric: Dict) -> Tuple[List[str], Set[int]]:
        """
        Sample answers based on score distribution.
        
        Args:
            answers: List of all student answers
            sample_size: Number of samples to select
            used_indices: Set of indices that have already been used
            current_rubric: Current rubric used for grading
            
        Returns:
            Tuple containing:
            - List of selected answers
            - Set of indices of selected answers
        """
        # Get scores for all answers using LLM with current rubric
        scores = self.llm_grader.grade_batch(answers, current_rubric)
        
        # Create strata based on scores
        strata = self._create_strata(scores, 5)  # Using 5 strata as default
        
        # Calculate proportional samples for each stratum
        available_indices = set(range(len(answers))) - used_indices
        selected_indices = set()
        selected_answers = []
        
        for stratum in strata:
            # Filter out already used indices
            available_stratum = [idx for idx in stratum if idx in available_indices]
            if not available_stratum:
                continue
                
            # Calculate proportional sample size for this stratum
            stratum_size = max(1, int(len(stratum) / len(scores) * sample_size))
            if len(available_stratum) < stratum_size:
                stratum_size = len(available_stratum)
                
            # Sample from stratum
            stratum_indices = random.sample(available_stratum, stratum_size)
            selected_indices.update(stratum_indices)
            selected_answers.extend([answers[i] for i in stratum_indices])
        
        # Handle case where we didn't get enough samples
        if len(selected_answers) < sample_size and available_indices - selected_indices:
            remaining_indices = available_indices - selected_indices
            additional_needed = min(sample_size - len(selected_answers), len(remaining_indices))
            additional_indices = random.sample(list(remaining_indices), additional_needed)
            selected_indices.update(additional_indices)
            selected_answers.extend([answers[i] for i in additional_indices])
        
        return selected_answers, selected_indices

    def _create_strata(self, scores: List[float], num_strata: int) -> List[List[int]]:
        """
        Create score-based strata for sampling.
        
        Args:
            scores: List of scores for all answers
            num_strata: Number of strata to create
            
        Returns:
            List of lists, where each inner list contains indices for that stratum
        """
        if not scores:
            return []
            
        min_score = min(scores)
        max_score = max(scores)
        if min_score == max_score:
            # If all scores are the same, put all indices in one stratum
            return [[i for i in range(len(scores))]]
            
        stride = (max_score - min_score) / num_strata
        
        strata = [[] for _ in range(num_strata)]
        for idx, score in enumerate(scores):
            stratum_idx = min(num_strata - 1, 
                            int((score - min_score) / stride))
            strata[stratum_idx].append(idx)
            
        return strata

class RubricGenerator:
    """Main class for rubric generation process."""
    def __init__(self, 
                 sampling_strategy: SamplingStrategy,
                 llm_interface,
                 sample_size: int = 5,
                 max_epochs: Optional[int] = None):
        """
        Initialize the rubric generator.
        
        Args:
            sampling_strategy: Strategy for sampling answers
            llm_interface: Interface to LLM for generating rubrics
            sample_size: Number of samples per iteration
            max_epochs: Maximum number of iterations (None for no limit)
        """
        self.sampling_strategy = sampling_strategy
        self.llm_interface = llm_interface
        self.sample_size = sample_size
        self.max_epochs = max_epochs
        self.used_indices: Set[int] = set()
        
    def generate_rubric(self, 
                       question: str,
                       initial_rubric: Dict,
                       answers: List[str]) -> Dict:
        """
        Generate improved rubric through multiple iterations.
        
        Args:
            question: The question being evaluated
            initial_rubric: Initial rubric as dictionary
            answers: List of student answers
            
        Returns:
            Final improved rubric as dictionary
        """
        current_rubric = initial_rubric
        epoch = 0
        
        while True:
            epoch += 1
            logger.info(f"Starting epoch {epoch}")
            
            # Check termination conditions
            if self.max_epochs and epoch > self.max_epochs:
                logger.info("Reached maximum number of epochs")
                break
            if len(self.used_indices) >= len(answers):
                logger.info("All answers have been used")
                break
                
            # Sample answers with current rubric
            sampled_answers, new_indices = self.sampling_strategy.sample(
                answers, 
                self.sample_size,
                self.used_indices,
                current_rubric
            )
            
            if not sampled_answers:
                logger.info("No more answers available for sampling")
                break
                
            self.used_indices.update(new_indices)
            
            # Get scores for sampled answers using current rubric
            scored_samples = []
            for answer in sampled_answers:
                score = self.llm_interface.grade_batch([answer], current_rubric)[0]
                scored_samples.append((answer, score))
            
            # Generate improved rubric
            prompt = self._construct_prompt(question, current_rubric, scored_samples)
            new_rubric = self.llm_interface.generate_rubric(prompt)
            
            # Save intermediate rubric
            if hasattr(self.llm_interface, 'save_intermediate_rubric'):
                self.llm_interface.save_intermediate_rubric(new_rubric, epoch)
            
            # Update current rubric
            current_rubric = new_rubric
            
        return current_rubric
    
    def _construct_prompt(self, 
                         question: str, 
                         current_rubric: Dict, 
                         scored_samples: List[Tuple[str, float]]) -> str:
        """
        Construct prompt for LLM rubric generation.
        
        Args:
            question: The question being evaluated
            current_rubric: Current rubric dictionary
            scored_samples: List of (answer, score) tuples
            
        Returns:
            Constructed prompt string
        """
        prompt = f"""You are a professional teacher creating a grading rubric. 
        Review and improve the current rubric based on these graded examples.
        
        Question:
        {question}
        
        Current Rubric:
        {yaml.dump(current_rubric)}
        
        Sample Answers and Scores:
        """
        
        for answer, score in scored_samples:
            prompt += f"\nAnswer: {answer}\nScore: {score}\n"
            
        prompt += "\nBased on these examples, please generate an improved rubric that better captures the important aspects of the solutions. Maintain the same YAML structure as the current rubric."
        
        return prompt

# Utility functions for file operations
def load_yaml(path: Path) -> Dict:
    """Load YAML file."""
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def save_yaml(data: Dict, path: Path) -> None:
    """Save dictionary to YAML file."""
    with open(path, 'w') as f:
        yaml.dump(data, f)

def load_answers(path: Path) -> List[str]:
    """Load student answers from text file."""
    with open(path, 'r') as f:
        return f.read().splitlines()