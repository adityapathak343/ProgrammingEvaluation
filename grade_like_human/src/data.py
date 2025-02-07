
"""
Data management module for the Grade Like a Human system.
Handles loading and processing of questions, rubrics, and submissions.
"""

import os
import json
import logging
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Rest of the file remains the same...
# Rest of the file remains the same, just remove the setuptools import
@dataclass
class Question:
    """Question data structure"""
    id: str
    text: str
    max_points: int
    
    @classmethod
    def from_file(cls, file_path: str) -> 'Question':
        """Load question from a file"""
        with open(file_path, 'r') as f:
            content = f.read()
            # Extract max points from the question text
            # Example format: "(Full points: 15) Question text..."
            import re
            points_match = re.search(r'\(Full points:\s*(\d+)\)', content)
            max_points = int(points_match.group(1)) if points_match else 0
            
            # Clean the question text
            question_text = re.sub(r'\(Full points:\s*\d+\)\s*', '', content).strip()
            
            return cls(
                id=Path(file_path).stem,
                text=question_text,
                max_points=max_points
            )

@dataclass
class Rubric:
    """Rubric data structure"""
    question_id: str
    content: str
    criteria: List[Dict[str, Any]]
    
    @classmethod
    def from_file(cls, file_path: str) -> 'Rubric':
        """Load rubric from a file"""
        with open(file_path, 'r') as f:
            content = f.read()
            
            # Parse criteria from the content
            # Example format:
            # "● Step 1: Description [X marks]"
            import re
            criteria = []
            for line in content.split('\n'):
                if match := re.search(r'●\s*([^[]+)\[(\d+)\s*marks?\]', line):
                    criteria.append({
                        'description': match.group(1).strip(),
                        'points': int(match.group(2))
                    })
            
            return cls(
                question_id=Path(file_path).stem,
                content=content,
                criteria=criteria
            )

@dataclass
class Submission:
    """Student submission data structure"""
    id: str
    question_id: str
    content: str
    score: Optional[float] = None

class DataManager:
    """Manages data loading and processing for the grading system"""
    
    def __init__(self, data_dir: str):
        """
        Initialize DataManager with data directory path.
        
        Args:
            data_dir: Root directory containing questions, rubrics, and submissions
        """
        self.data_dir = Path(data_dir)
        self.questions_dir = self.data_dir / "questions"
        self.rubrics_dir = self.data_dir / "rubrics"
        self.submissions_dir = self.data_dir / "submissions"
        
        # Create directories if they don't exist
        self.questions_dir.mkdir(parents=True, exist_ok=True)
        self.rubrics_dir.mkdir(parents=True, exist_ok=True)
        self.submissions_dir.mkdir(parents=True, exist_ok=True)

    def load_question(self, question_id: str) -> Question:
        """Load a specific question"""
        question_path = self.questions_dir / f"{question_id}.txt"
        if not question_path.exists():
            raise FileNotFoundError(f"Question file not found: {question_path}")
        return Question.from_file(str(question_path))

    def load_rubric(self, question_id: str, version: str = "original") -> Rubric:
        """
        Load a rubric for a specific question.
        
        Args:
            question_id: ID of the question
            version: Which version of the rubric to load ("original" or "improved")
        """
        rubric_path = self.rubrics_dir / f"{question_id}_{version}.txt"
        if not rubric_path.exists():
            raise FileNotFoundError(f"Rubric file not found: {rubric_path}")
        return Rubric.from_file(str(rubric_path))

    def load_submissions(self, question_id: str) -> List[Submission]:
        """Load all submissions for a specific question"""
        submissions_path = self.submissions_dir / f"{question_id}.csv"
        if not submissions_path.exists():
            raise FileNotFoundError(f"Submissions file not found: {submissions_path}")
                
        logger.info(f"Loading submissions for question {question_id}")
        
        try:
            df = pd.read_csv(submissions_path)
            logger.debug(f"CSV columns found: {df.columns.tolist()}")
            
            submissions = []
            for _, row in df.iterrows():
                try:
                    folder_name = str(row['Folder Name'])
                    # Construct path to the java file
                    java_file = self.submissions_dir / folder_name / "p1.java"
                    
                    if not java_file.exists():
                        logger.warning(f"Submission file not found: {java_file}")
                        continue
                        
                    # Read the actual submission content
                    with open(java_file, 'r') as f:
                        content = f.read()
                    
                    submissions.append(Submission(
                        id=folder_name,
                        question_id=question_id,
                        content=content,
                        score=row.get('Part1 Total')  # Get score from Part1 Total
                    ))
                    logger.debug(f"Loaded submission for {folder_name}")
                    
                except Exception as e:
                    logger.warning(f"Error processing submission {folder_name}: {str(e)}")
                    continue
                    
            logger.info(f"Successfully loaded {len(submissions)} submissions")
            return submissions
            
        except Exception as e:
            logger.error(f"Error loading submissions file: {str(e)}")
            raise

    def save_rubric(self, rubric: Rubric, version: str = "improved") -> None:
        """Save a rubric"""
        output_path = self.rubrics_dir / f"{rubric.question_id}_{version}.txt"
        with open(output_path, 'w') as f:
            f.write(rubric.content)

    def save_evaluation_results(self, results: Dict[str, Any], 
                              question_id: str,
                              version: str = "initial") -> None:
        """Save evaluation results"""
        output_path = self.submissions_dir / f"{question_id}_results_{version}.json"
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)

    def load_evaluation_results(self, question_id: str,
                              version: str = "initial") -> Dict[str, Any]:
        """Load evaluation results"""
        results_path = self.submissions_dir / f"{question_id}_results_{version}.json"
        if not results_path.exists():
            raise FileNotFoundError(f"Results file not found: {results_path}")
            
        with open(results_path, 'r') as f:
            return json.load(f)

    def get_all_questions(self) -> List[Question]:
        """Get list of all available questions"""
        questions = []
        for file_path in self.questions_dir.glob("*.txt"):
            questions.append(Question.from_file(str(file_path)))
        return questions

# Example usage
if __name__ == "__main__":
    data_manager = DataManager("./data")
    
    # Load a question
    question = data_manager.load_question("q1")
    print(f"Loaded question: {question}")
    
    # Load rubric
    rubric = data_manager.load_rubric("q1")
    print(f"Loaded rubric: {rubric}")
    
    # Load submissions
    submissions = data_manager.load_submissions("q1")
    print(f"Loaded {len(submissions)} submissions")