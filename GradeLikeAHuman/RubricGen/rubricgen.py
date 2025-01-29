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

class RubricGeneratorError(Exception):
    """Base exception class for RubricGenerator errors"""
    pass

class FileNotFoundError(RubricGeneratorError):
    """Raised when a required file is not found"""
    pass

class APIKeyError(RubricGeneratorError):
    """Raised when there are issues with the API key"""
    pass

class DataError(RubricGeneratorError):
    """Raised when there are issues with data processing"""
    pass

class RubricGenerator:
    def __init__(self, model_name: str = "gpt-4", prompts_file: str = r"prompts.json") -> None:
        """Initialize the RubricGenerator with specified LLM model and prompts file."""
        try:
            self._load_api_key()
            self.llm = ChatOpenAI(model=model_name, temperature=0)
            self.json_parser = JsonOutputParser()
            self.prompts = self._load_prompts(prompts_file)
            logger.info(f"Successfully initialized RubricGenerator with model {model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize RubricGenerator: {str(e)}")
            raise RubricGeneratorError(f"Initialization failed: {str(e)}")

    def _load_prompts(self, prompts_file: str) -> dict:
        """Load prompts from JSON file with error handling."""
        try:
            if not os.path.exists(prompts_file):
                raise FileNotFoundError(f"Prompts file not found: {prompts_file}")
                
            with open(prompts_file, 'r') as f:
                prompts_data = json.load(f)
                
            rubric_gen_prompt = next(
                (prompt["prompt"] for prompt in prompts_data.get("rubricgeneration", [])
                 if prompt.get("Dataset") == "CricketAnalytics"),
                None
            )
            
            if not rubric_gen_prompt:
                raise ValueError("CricketAnalytics prompt not found in prompts.json")
                
            return {"rubric_gen_prompt": rubric_gen_prompt}
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse prompts file: {str(e)}")
            raise RubricGeneratorError(f"Invalid prompts file format: {str(e)}")
        except Exception as e:
            logger.error(f"Error loading prompts: {str(e)}")
            raise RubricGeneratorError(f"Failed to load prompts: {str(e)}")

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

    async def read_excel_data(self, file_path: str) -> pd.DataFrame:
        """Read the Excel file with error handling."""
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Excel file not found: {file_path}")
                
            df = pd.read_excel(file_path)
            
            if 'Folder Name' not in df.columns or 'Part1 Total' not in df.columns:
                raise DataError("Required columns 'Folder Name' and 'Part1 Total' not found in Excel file")
                
            grades_df = df[['Folder Name', 'Part1 Total']].copy()
            grades_df = grades_df.dropna()
            
            if len(grades_df) == 0:
                raise DataError("No valid data found after processing Excel file")
                
            logger.info(f"Successfully read {len(grades_df)} rows from Excel file")
            return grades_df
            
        except pd.errors.EmptyDataError:
            logger.error("Excel file is empty")
            raise DataError("Excel file is empty")
        except Exception as e:
            logger.error(f"Error reading Excel file: {str(e)}")
            raise DataError(f"Failed to read Excel file: {str(e)}")

    def random_sampling(self, data: pd.DataFrame, sample_size: int) -> pd.DataFrame:
        """Perform random sampling with error handling."""
        try:
            if sample_size > len(data):
                raise ValueError(f"Sample size ({sample_size}) cannot be larger than dataset size ({len(data)})")
            
            sampled_data = data.sample(n=sample_size)
            logger.info(f"Successfully sampled {sample_size} records randomly")
            return sampled_data
            
        except Exception as e:
            logger.error(f"Error in random sampling: {str(e)}")
            raise DataError(f"Random sampling failed: {str(e)}")

    def distribution_aware_sampling(self, data: pd.DataFrame, sample_size: int, n_strata: int = 5) -> pd.DataFrame:
        """Perform distribution-aware sampling with error handling."""
        try:
            if sample_size > len(data):
                raise ValueError(f"Sample size ({sample_size}) cannot be larger than dataset size ({len(data)})")

            if n_strata > len(data):
                raise ValueError(f"Number of strata ({n_strata}) cannot be larger than dataset size ({len(data)})")

            data = data.copy()
            data['score_bin'] = pd.qcut(data['Part1 Total'], q=n_strata, labels=False)
            
            samples_per_stratum = max(1, sample_size // n_strata)
            sampled_data = pd.DataFrame()
            
            for stratum in range(n_strata):
                stratum_data = data[data['score_bin'] == stratum]
                if len(stratum_data) > 0:
                    n_samples = min(samples_per_stratum, len(stratum_data))
                    sampled_data = pd.concat([sampled_data, stratum_data.sample(n=n_samples)])
            
            remaining_samples = sample_size - len(sampled_data)
            if remaining_samples > 0:
                remaining_data = data[~data.index.isin(sampled_data.index)]
                if len(remaining_data) > 0:
                    additional_samples = remaining_data.sample(n=min(remaining_samples, len(remaining_data)))
                    sampled_data = pd.concat([sampled_data, additional_samples])
            
            result = sampled_data.drop('score_bin', axis=1)
            logger.info(f"Successfully performed distribution-aware sampling with {len(result)} records")
            return result
            
        except Exception as e:
            logger.error(f"Error in distribution-aware sampling: {str(e)}")
            raise DataError(f"Distribution-aware sampling failed: {str(e)}")

    def generate_improved_rubric(self, 
                               initial_rubric: str, 
                               sampled_data: pd.DataFrame,
                               question: str,
                               max_points: int) -> str:
        """Generate improved rubric with error handling."""
        try:
            prompt_values = {
                "question": question,
                "init_rubric": initial_rubric,
                "full_points": str(max_points),
                "sample_studata": sampled_data.to_string(),
                "codebase": ""
            }
            
            prompt = self.prompts["rubric_gen_prompt"]
            for key, value in prompt_values.items():
                prompt = prompt.replace("{" + key + "}", value)

            response = self.llm.invoke(prompt)
            
            if not response.content:
                raise RubricGeneratorError("Empty response from LLM")
                
            logger.info("Successfully generated improved rubric")
            return response.content
            
        except Exception as e:
            logger.error(f"Error generating improved rubric: {str(e)}")
            raise RubricGeneratorError(f"Failed to generate improved rubric: {str(e)}")

    async def improve_rubric(self, 
                           excel_path: str,
                           initial_rubric_path: str,
                           question_path: str,
                           sample_size: int = 10,
                           use_distribution: bool = True) -> Tuple[str, pd.DataFrame]:
        """Main method to improve rubric with error handling."""
        try:
            # Validate input files
            for path, desc in [(excel_path, "Excel"), (initial_rubric_path, "Initial rubric"), (question_path, "Question")]:
                if not os.path.exists(path):
                    raise FileNotFoundError(f"{desc} file not found: {path}")

            # Read input files
            with open(initial_rubric_path, 'r') as f:
                initial_rubric = f.read()
            with open(question_path, 'r') as f:
                question = f.read()
                
            grades_df = await self.read_excel_data(excel_path)
            
            # Perform sampling
            if use_distribution:
                sampled_data = self.distribution_aware_sampling(grades_df, sample_size)
            else:
                sampled_data = self.random_sampling(grades_df, sample_size)
                
            # Generate improved rubric
            improved_rubric = self.generate_improved_rubric(
                initial_rubric,
                sampled_data,
                question,
                max_points=35
            )
            
            logger.info("Successfully completed rubric improvement process")
            return improved_rubric, sampled_data
            
        except Exception as e:
            logger.error(f"Error in improve_rubric: {str(e)}")
            raise RubricGeneratorError(f"Rubric improvement failed: {str(e)}")

async def main():
    """Main function with error handling."""
    try:
        generator = RubricGenerator()
        
        # Define file paths
        base_path = "OOPS_dataset_v1"
        excel_path = os.path.join(base_path, "cleaned_oops.xlsx")
        initial_rubric_path = os.path.join(base_path, "questions", "rubrick.txt")
        question_path = os.path.join(base_path, "questions", "question.txt")

        # Generate rubric using distribution-aware sampling
        logger.info("Starting distribution-aware sampling process...")
        dist_rubric, dist_samples = await generator.improve_rubric(
            excel_path=excel_path,
            initial_rubric_path=initial_rubric_path,
            question_path=question_path,
            sample_size=10,
            use_distribution=True
        )
        
        # Generate rubric using random sampling
        logger.info("Starting random sampling process...")
        random_rubric, random_samples = await generator.improve_rubric(
            excel_path=excel_path,
            initial_rubric_path=initial_rubric_path,
            question_path=question_path,
            sample_size=10,
            use_distribution=False
        )
        
        # Print results
        print("\n=== Distribution-Aware Sampling Results ===")
        print("Sampled Data:\n", dist_samples)
        print("\nImproved Rubric:\n", dist_rubric)
        
        print("\n=== Random Sampling Results ===")
        print("Sampled Data:\n", random_samples)
        print("\nImproved Rubric:\n", random_rubric)
        
        logger.info("Successfully completed all processes")
        
    except RubricGeneratorError as e:
        logger.error(f"RubricGenerator error: {str(e)}")
        print(f"Error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        print(f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())