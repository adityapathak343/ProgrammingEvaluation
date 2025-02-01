import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Any, Optional
import json
import os
import getpass
import logging
from pathlib import Path
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RubricEvaluatorError(Exception):
    """Base exception class for RubricEvaluator errors"""
    pass

class FileNotFoundError(RubricEvaluatorError):
    """Raised when a required file is not found"""
    pass

class APIKeyError(RubricEvaluatorError):
    """Raised when there are issues with the API key"""
    pass

class DataError(RubricEvaluatorError):
    """Raised when there are issues with data processing"""
    pass

class RubricEvaluator:
    def __init__(self, model_name: str = "gpt-4o-mini", prompts_file: str = "prompts.json") -> None:
        """Initialize the RubricEvaluator with specified LLM model and prompts file."""
        try:
            self._load_api_key()
            self.llm = ChatOpenAI(model=model_name, temperature=0)
            self.json_parser = JsonOutputParser()
            self.prompts = self._load_prompts(prompts_file)
            logger.info(f"Successfully initialized RubricEvaluator with model {model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize RubricEvaluator: {str(e)}")
            raise RubricEvaluatorError(f"Initialization failed: {str(e)}")

    def _load_prompts(self, prompts_file: str) -> dict:
        """Load prompts from JSON file with error handling."""
        try:
            prompts_path = Path(prompts_file)
            if not prompts_path.exists():
                raise FileNotFoundError(f"Prompts file not found: {prompts_file}")
                
            with prompts_path.open('r') as f:
                prompts_data = json.load(f)
                
            eval_prompt = next(
                (prompt["prompt"] for prompt in prompts_data.get("rubricbasedevaluation", [])
                 if prompt.get("promptNumber") == "CricketAnalytics"),
                None
            )
            
            reeval_prompt = next(
                (prompt["prompt"] for prompt in prompts_data.get("re-evaluation", [])
                 if prompt.get("promptNumber") == "CricketAnalytics"),
                None
            )
            
            if not eval_prompt or not reeval_prompt:
                raise ValueError("Required prompts not found in prompts.json")
                
            return {
                "eval_prompt": eval_prompt,
                "reeval_prompt": reeval_prompt
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse prompts file: {str(e)}")
            raise RubricEvaluatorError(f"Invalid prompts file format: {str(e)}")
        except Exception as e:
            logger.error(f"Error loading prompts: {str(e)}")
            raise RubricEvaluatorError(f"Failed to load prompts: {str(e)}")

    def _load_api_key(self) -> None:
        """Load OpenAI API key with error handling."""
        try:
            if "OPENAI_API_KEY" not in os.environ:
                api_key = getpass.getpass("Enter your OpenAI API key: ")
                if not api_key:
                    raise APIKeyError("No API key provided")
                os.environ["OPENAI_API_KEY"] = api_key
            logger.info("Successfully loaded API key")
        except Exception as e:
            logger.error(f"Failed to load API key: {str(e)}")
            raise APIKeyError(f"Failed to load API key: {str(e)}")

    async def read_excel_submissions(self, file_path: str) -> pd.DataFrame:
        """Read the Excel file containing submissions with error handling."""
        try:
            excel_path = Path(file_path)
            if not excel_path.exists():
                raise FileNotFoundError(f"Excel file not found: {file_path}")
                
            df = pd.read_excel(excel_path)
            
            if 'Folder Name' not in df.columns:
                raise DataError("Required column 'Folder Name' not found in Excel file")
            
            submissions_df = df[['Folder Name']].copy()
            submissions_df['Folder Name'] = submissions_df['Folder Name'].astype(int).astype(str)
            submissions_df = submissions_df.dropna()
            
            if len(submissions_df) == 0:
                raise DataError("No valid submissions found in Excel file")
                
            logger.info(f"Successfully read {len(submissions_df)} submissions from Excel file")
            return submissions_df
            
        except pd.errors.EmptyDataError:
            logger.error("Excel file is empty")
            raise DataError("Excel file is empty")
        except Exception as e:
            logger.error(f"Error reading Excel file: {str(e)}")
            raise DataError(f"Failed to read Excel file: {str(e)}")

    async def read_submission_for_id(self, folder_id: str, submissions_dir: str) -> str:
        """Read a specific submission file for a student ID."""
        try:
            folder_id_str = str(int(folder_id)).strip()
            base_path = Path(submissions_dir) / "solutions" / folder_id_str
            possible_files = ["p1.java", "P1.java"]
            
            submission_content = None
            used_path = None
            
            for filename in possible_files:
                file_path = base_path / filename
                if file_path.exists():
                    submission_content = file_path.read_text()
                    used_path = file_path
                    break
            
            if submission_content is None:
                paths_tried = "\n".join(str(base_path / f) for f in possible_files)
                raise FileNotFoundError(f"No submission file found for ID {folder_id_str}. Tried:\n{paths_tried}")
                
            if not submission_content.strip():
                raise DataError(f"Empty submission for ID {folder_id_str}")
                
            logger.info(f"Successfully read submission for ID {folder_id_str} from {used_path}")
            return submission_content
            
        except Exception as e:
            logger.error(f"Error reading submission file: {str(e)}")
            raise DataError(f"Failed to read submission for ID {folder_id_str}: {str(e)}")

    def evaluate_submission(self, 
                          question: str,
                          codebase: str,
                          final_rubric: str,
                          submission: str,
                          max_points: int = 35) -> Dict[str, Any]:
        """Evaluate a submission using the rubric."""
        try:
            prompt_values = {
                "question": question,
                "codebase": codebase,
                "final_rubric": final_rubric,
                "full_points": str(max_points),
                "submission": submission
            }
            
            prompt = self.prompts["eval_prompt"]
            for key, value in prompt_values.items():
                prompt = prompt.replace("{" + key + "}", str(value))

            response = self.llm.invoke(prompt)
            
            if not response.content:
                raise RubricEvaluatorError("Empty response from LLM")
                
            evaluation = self.json_parser.parse(response.content)
            logger.info("Successfully evaluated submission")
            return evaluation
            
        except Exception as e:
            logger.error(f"Error evaluating submission: {str(e)}")
            raise RubricEvaluatorError(f"Failed to evaluate submission: {str(e)}")

    def re_evaluate_submission(self, previous_evaluation: Dict[str, Any]) -> Dict[str, Any]:
        """Re-evaluate a previous evaluation."""
        try:
            prompt = self.prompts["reeval_prompt"].replace(
                "{Previous_evaluation}",
                json.dumps(previous_evaluation)
            )

            response = self.llm.invoke(prompt)
            
            if not response.content:
                raise RubricEvaluatorError("Empty response from LLM")
                
            re_evaluation = self.json_parser.parse(response.content)
            logger.info("Successfully re-evaluated submission")
            return re_evaluation
            
        except Exception as e:
            logger.error(f"Error in re-evaluation: {str(e)}")
            raise RubricEvaluatorError(f"Failed to re-evaluate submission: {str(e)}")

    async def evaluate_submissions(self,
                                 question_path: str,
                                 codebase_path: str,
                                 rubric_path: str,
                                 excel_path: str,
                                 submissions_dir: str) -> List[Tuple[str, Dict[str, Any], Dict[str, Any]]]:
        """Main method to evaluate all submissions from the Excel file."""
        try:
            # Convert all paths to Path objects
            paths = {
                "Question": Path(question_path),
                "Codebase template": Path(codebase_path),
                "Rubric": Path(rubric_path),
                "Excel submissions list": Path(excel_path)
            }
            
            # Validate input files
            for desc, path in paths.items():
                if not path.exists():
                    raise FileNotFoundError(f"{desc} file not found: {path}")

            # Read input files
            question = paths["Question"].read_text()
            codebase = paths["Codebase template"].read_text()
            rubric = paths["Rubric"].read_text()
                
            # Read submissions from Excel
            submissions_df = await self.read_excel_submissions(excel_path)
            results = []
            
            # Process each submission
            for folder_id in submissions_df['Folder Name']:
                try:
                    submission = await self.read_submission_for_id(folder_id, submissions_dir)
                    
                    # Perform evaluation
                    evaluation = self.evaluate_submission(
                        question=question,
                        codebase=codebase,
                        final_rubric=rubric,
                        submission=submission
                    )
                    
                    # Perform re-evaluation
                    re_evaluation = self.re_evaluate_submission(evaluation)
                    
                    results.append((folder_id, evaluation, re_evaluation))
                    logger.info(f"Successfully evaluated submission for ID {folder_id}")
                    
                except Exception as e:
                    logger.error(f"Failed to evaluate submission {folder_id}: {str(e)}")
                    results.append((folder_id, {"error": str(e)}, None))
            
            logger.info(f"Successfully completed evaluation process for {len(results)} submissions")
            return results
            
        except Exception as e:
            logger.error(f"Error in evaluate_submissions: {str(e)}")
            raise RubricEvaluatorError(f"Submission evaluation failed: {str(e)}")

async def main():
    """Main function with error handling."""
    try:
        evaluator = RubricEvaluator()
        
        # Define paths
        current_dir = Path.cwd()
        input_files = {
            "question_path": current_dir / "question.txt",
            "codebase_path": current_dir / "CBT_PART_1_QP.java",
            "rubric_path": current_dir / "rubrick.txt",
            "excel_path": current_dir / "cleaned_oops.xlsx",
        }
        
        # Use WSL path for submissions directory
        submissions_dir = Path("/home/krishna27/Projects/ProgrammingEvaluation/OOPS_dataset_v1")
        
        print("Looking for files at:")
        for desc, path in input_files.items():
            print(f"{desc}: {path}")
        print(f"Submissions directory: {submissions_dir}")

        # Perform evaluation
        logger.info("Starting evaluation process...")
        results = await evaluator.evaluate_submissions(
            **input_files,
            submissions_dir=str(submissions_dir)
        )
        
        # Create output structure
        output = {
            "evaluations": {},
            "summary": {
                "total_submissions": len(results),
                "successful_evaluations": 0,
                "failed_evaluations": 0,
                "missing_submissions": []
            }
        }
        
        # Process results
        for folder_id, evaluation, re_evaluation in results:
            output["evaluations"][folder_id] = {
                "initial_evaluation": evaluation,
                "re_evaluation": re_evaluation
            }
            
            if "error" in evaluation:
                output["summary"]["failed_evaluations"] += 1
                if "No submission file found" in str(evaluation["error"]):
                    output["summary"]["missing_submissions"].append(folder_id)
            else:
                output["summary"]["successful_evaluations"] += 1
        
        # Create output directory and save results
        output_dir = current_dir / "output"
        output_dir.mkdir(exist_ok=True)
        
        results_path = output_dir / "evaluation_results.json"
        with results_path.open('w') as f:
            json.dump(output, f, indent=2)
        print(f"\nAll evaluation results saved to: {results_path}")
        
        # Print summary
        print("\n=== Evaluation Summary ===")
        print(f"Total submissions processed: {output['summary']['total_submissions']}")
        print(f"Successfully evaluated: {output['summary']['successful_evaluations']}")
        print(f"Failed evaluations: {output['summary']['failed_evaluations']}")
        print(f"Missing submissions: {len(output['summary']['missing_submissions'])}")
        
        logger.info("Successfully completed all processes")
        
    except RubricEvaluatorError as e:
        logger.error(f"RubricEvaluator error: {str(e)}")
        print(f"Error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        print(f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())