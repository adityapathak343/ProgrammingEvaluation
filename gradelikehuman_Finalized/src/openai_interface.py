from typing import Dict, List
import openai
import logging
import yaml
import json

logger = logging.getLogger(__name__)

class OpenAIInterface:
    """Interface for OpenAI models"""
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        """
        Initialize OpenAI interface.
        
        Args:
            api_key: OpenAI API key
            model: Model to use 
        """
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        
    def generate_rubric(self, prompt: str) -> Dict:
        """
        Generate improved rubric using OpenAI.
        
        Args:
            prompt: Prompt for rubric generation
            
        Returns:
            Dictionary containing the generated rubric
        """
        try:
            system_prompt = """You are an expert at creating detailed grading rubrics for programming assignments.
            Generate a structured rubric with clear criteria, point allocations, and descriptions.
            The rubric should be detailed and cover both functionality and code quality aspects.
            Format the output as a valid YAML document with the following structure:
            
            criteria:
              - name: "Criterion Name"
                points: <total_points>
                descriptions:
                  - score: <point_value>
                    description: "Description for this score level"
                  # ... more score levels
              # ... more criteria
            total_points: <total>
            """
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )
            
            # Parse the response
            rubric_text = response.choices[0].message.content
            try:
                # Try parsing as YAML
                rubric = yaml.safe_load(rubric_text)
                return rubric
            except yaml.YAMLError:
                # If YAML parsing fails, try to extract YAML content
                if '```yaml' in rubric_text:
                    yaml_content = rubric_text.split('```yaml')[1].split('```')[0]
                    return yaml.safe_load(yaml_content)
                raise
                
        except Exception as e:
            logger.error(f"Error generating rubric: {str(e)}")
            raise
            
    def grade_batch(self, answers: List[str], rubric: Dict) -> List[float]:
        """
        Grade a batch of answers using the rubric.
        
        Args:
            answers: List of student answers to grade
            rubric: Rubric to use for grading
                
        Returns:
            List of scores
        """
        scores = []
        
        for answer in answers:
            try:
                prompt = f"""Grade the following answer using the provided rubric. For each criterion in the rubric, provide a specific score and justification.
    Then sum up the total score. The maximum possible score is {rubric['total_points']}.

    Rubric:
    {yaml.dump(rubric)}

    Answer to Grade:
    {answer}

    For each criterion, specify:
    1. Criterion name
    2. Score awarded (using the exact point values from the rubric)
    3. Brief justification

    Then provide the final total score out of {rubric['total_points']} points.
    Your response should end with a single number representing the total score."""
                
                messages = [
                    {"role": "system", "content": "You are an expert at grading programming assignments. Grade precisely according to the rubric criteria and point values."},
                    {"role": "user", "content": prompt}
                ]
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.3,
                    max_tokens=2000
                )
                
                # Extract score from response
                response_text = response.choices[0].message.content.strip()
                
                # Look for the final number in the response
                import re
                numbers = re.findall(r'\d+(?:\.\d+)?', response_text.split('\n')[-1])
                if numbers:
                    score = float(numbers[0])
                    if score > rubric['total_points']:
                        logger.warning(f"Score {score} exceeds maximum {rubric['total_points']}, capping at maximum")
                        score = float(rubric['total_points'])
                else:
                    logger.warning("Could not extract score from response, defaulting to 0")
                    score = 0.0
                
                scores.append(score)
                
            except Exception as e:
                logger.error(f"Error grading answer: {str(e)}")
                scores.append(0.0)
                    
        return scores

    def format_initial_rubric(self, rubric_text: str) -> Dict:
        """
        Convert text rubric to structured format using OpenAI.
        
        Args:
            rubric_text: Raw rubric text
            
        Returns:
            Structured rubric dictionary
        """
        try:
            prompt = f"""Convert the following rubric text into a structured format:

{rubric_text}

Format it as a YAML document with clear criteria, point allocations, and descriptions."""
            
            return self.generate_rubric(prompt)
            
        except Exception as e:
            logger.error(f"Error formatting rubric: {str(e)}")
            raise