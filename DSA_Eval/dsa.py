import os
import yaml
import openai
import re
from typing import Dict, Any, Optional
import json
from datetime import datetime

class DSAGrader:
    def __init__(self, api_key: str, rubric_path: str):
        """Initialize grader with OpenAI API key and path to rubric YAML."""
        self.api_key = api_key
        self.client = openai.OpenAI(api_key=api_key)
        
        # Load rubric
        with open(rubric_path, 'r') as f:
            self.rubric = yaml.safe_load(f)

    def grade_submission(self, problem_text: str, student_code: str, test_case_ratio: Optional[float] = None) -> Dict:
        """
        Grade a student submission using the rubric and OpenAI API.
        
        Args:
            problem_text: Description of the DSA problem
            student_code: Student's submitted code
            test_case_ratio: Ratio of passing test cases (0.0 to 1.0), optional
        
        Returns:
            Dictionary containing detailed grading feedback
        """
        prompt = self._create_evaluation_prompt(problem_text, student_code, test_case_ratio)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",  # Changed from gpt-4o-mini to gpt-4
                messages=[
                    {"role": "system", "content": "You are an expert programming evaluator. Your responses must be valid JSON objects. For each category, explain point allocations clearly but concisely. Show how points were awarded or deducted for specific aspects. Limit each feedback point to one sentence."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0
            )
            
            # Debug the response
            response_content = response.choices[0].message.content
            print("Raw API Response:", response_content)
            
            try:
                evaluation = json.loads(response_content)
            except json.JSONDecodeError as json_err:
                print(f"JSON Parsing Error: {str(json_err)}")
                print(f"Response content type: {type(response_content)}")
                print(f"Response content length: {len(response_content)}")
                raise Exception("Failed to parse API response as JSON") from json_err
            
            validated_evaluation = self._validate_evaluation(evaluation, test_case_ratio)
            
            # Debug the validated evaluation
            print("Validated evaluation:", json.dumps(validated_evaluation, indent=2))
            
            if not hasattr(self, '_generate_grade_report'):
                return validated_evaluation  # Return validated evaluation if _generate_grade_report doesn't exist
                
            grade_report = self._generate_grade_report(validated_evaluation, test_case_ratio)
            
            return grade_report
            
        except Exception as e:
            raise Exception(f"Error grading submission: {str(e)}")

    def _create_evaluation_prompt(self, problem_text: str, student_code: str, test_case_ratio: Optional[float]) -> str:
        """Create the prompt for OpenAI API."""
        categories_prompt = ""
        for cat_key, cat_data in self.rubric['categories'].items():
            categories_prompt += f"\n{cat_data['name']} (0-{cat_data['max_points']}):\n"
            for score, desc in cat_data['scale'].items():
                categories_prompt += f"  {score}: {desc}\n"
        
        test_case_info = f"- Pass Ratio: {test_case_ratio * 100}%" if test_case_ratio is not None else "- Test case results are unavailable"

        return f"""
        Evaluate the following DSA problem submission:

        Problem Description:
        {problem_text}

        Student Code:
        {student_code}

        Test Case Performance:
        {test_case_info}

        Evaluate according to these criteria:
        {categories_prompt}

        Provide evaluation as JSON with this structure for each category:
        {{
            "category_name": {{
                "score": X,
                "feedback": "Detailed justification for the score"
            }}
        }}
        """

    def _validate_evaluation(self, evaluation: Dict[str, Any], test_case_ratio: Optional[float]) -> Dict[str, Any]:
        """Validate evaluation scores against rubric ranges."""
        validated = {}
        
        # Create a mapping between normalized keys and actual response keys
        key_mapping = {k.lower().replace(' ', '_'): k for k in evaluation.keys()}
        
        for cat_key, cat_data in self.rubric['categories'].items():
            response_key = key_mapping.get(cat_key)
            if not response_key:
                raise ValueError(f"Missing evaluation for {cat_key}")
            
            score = evaluation[response_key]["score"]
            if not (0 <= score <= cat_data['max_points']):
                raise ValueError(
                    f"Invalid score for {cat_key}: {score}. Must be between 0 and {cat_data['max_points']}."
                )
            
            if (cat_key == "logical_correctness" and test_case_ratio is not None and 
                self.rubric['test_cases']['impact_on_logical_correctness']):
                max_score = cat_data['max_points']
                min_ratio = self.rubric['test_cases']['minimum_pass_ratio']
                
                if test_case_ratio < min_ratio:
                    score = min(score, max_score * (test_case_ratio / min_ratio))
                
            validated[cat_key] = {
                "score": score,
                "feedback": evaluation[response_key]["feedback"]
            }
        
        return validated

    def _generate_grade_report(self, evaluation: Dict[str, Any], test_case_ratio: Optional[float] = None) -> Dict[str, Any]:
        """Generate the final grade report."""
        total_points = 0
        max_points = 0
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "categories": evaluation,
            "test_case_ratio": test_case_ratio,
        }
        
        for cat_key, cat_data in self.rubric['categories'].items():
            if cat_key in evaluation:
                total_points += evaluation[cat_key]["score"]
                max_points += cat_data["max_points"]
        
        report["total_score"] = total_points
        report["max_score"] = max_points
        report["percentage"] = (total_points / max_points * 100) if max_points > 0 else 0
        
        return report

    def save_grade_report(self, report: Dict[str, Any], output_path: str):
        """Save the grade report as YAML with structured feedback including point allocations."""
        formatted_report = {
            "timestamp": report["timestamp"],
            "total_score": report["total_score"],
            "max_score": report["max_score"],
            "percentage": report["percentage"],
            "categories": {}
        }
        
        if "test_case_ratio" in report:
            formatted_report["test_case_ratio"] = report["test_case_ratio"]
            
        for cat_name, cat_data in report["categories"].items():
            feedback = cat_data["feedback"]
            rubric_category = next((cat for cat in self.rubric["categories"].values() 
                                  if cat["name"].lower() == cat_name.lower().replace("_", " ")), None)
            
            def split_feedback(comment, points):
                """Split a comment into strength and weakness parts."""
                if " but " in comment:
                    parts = comment.split(" but ")
                    pos_parts = []
                    neg_parts = []
                    
                    for part in parts:
                        # Check for negative indicators
                        if any(neg in part.lower() for neg in [
                            "lacks", "missing", "doesn't", "does not", 
                            "unclear", "poor", "improper", "invalid",
                            "needs", "should", "could", "would"
                        ]):
                            neg_parts.append(part.strip())
                        else:
                            pos_parts.append(part.strip())
                            
                    return (
                        [{"points": points, "comment": p} for p in pos_parts] if pos_parts else [],
                        [{"points": points, "comment": n} for n in neg_parts] if neg_parts else []
                    )
                elif "," in comment and any(neg in comment.lower() for neg in [
                    "lacks", "missing", "doesn't", "does not", 
                    "unclear", "poor", "improper", "invalid",
                    "needs", "should", "could", "would"
                ]):
                    parts = comment.split(",")
                    pos_parts = []
                    neg_parts = []
                    
                    for part in parts:
                        if any(neg in part.lower() for neg in [
                            "lacks", "missing", "doesn't", "does not", 
                            "unclear", "poor", "improper", "invalid",
                            "needs", "should", "could", "would"
                        ]):
                            neg_parts.append(part.strip())
                        else:
                            pos_parts.append(part.strip())
                            
                    return (
                        [{"points": points, "comment": p} for p in pos_parts] if pos_parts else [],
                        [{"points": points, "comment": n} for n in neg_parts] if neg_parts else []
                    )
                else:
                    return ([{"points": points, "comment": comment}], [])
            
            def format_feedback(comment):
                """Format feedback to be a complete, standalone statement."""
                # Remove connecting words at the start
                comment = re.sub(r'^(which|this|that|and|but)\s+', '', comment.strip(), flags=re.IGNORECASE)
                
                # Capitalize first letter if it's not
                if comment and comment[0].islower():
                    comment = comment[0].upper() + comment[1:]
                    
                # Ensure it ends with proper punctuation
                if comment and not comment[-1] in ['.', '!', '?']:
                    comment += '.'
                    
                return comment

            if isinstance(feedback, str):
                strengths, weaknesses = split_feedback(feedback, 1)
                # Format each feedback item
                strengths = [{"points": s["points"], "comment": format_feedback(s["comment"])} for s in strengths]
                weaknesses = [{"points": w["points"], "comment": format_feedback(w["comment"])} for w in weaknesses]
                
                formatted_report["categories"][cat_name] = {
                    "score": cat_data["score"],
                    "feedback": {
                        "strengths": strengths,
                        "weaknesses": weaknesses
                    }
                }
            elif isinstance(feedback, dict):
                # Format feedback for dictionary input
                all_strengths = []
                all_weaknesses = []
                
                # Process strengths
                strength_items = feedback.get("strengths", []) or feedback.get("positive", []) or feedback.get("positives", [])
                for item in strength_items:
                    if isinstance(item, dict):
                        s, w = split_feedback(format_feedback(item.get("comment", "")), item.get("points", 1))
                        all_strengths.extend(s)
                        all_weaknesses.extend(w)
                    else:
                        s, w = split_feedback(format_feedback(str(item)), 1)
                        all_strengths.extend(s)
                        all_weaknesses.extend(w)
                
                # Process explicit weaknesses
                weakness_items = feedback.get("weaknesses", []) or feedback.get("negative", []) or feedback.get("negatives", [])
                for item in weakness_items:
                    if isinstance(item, dict):
                        _, w = split_feedback(format_feedback(item.get("comment", "")), item.get("points", 1))
                        all_weaknesses.extend(w)
                    else:
                        _, w = split_feedback(format_feedback(str(item)), 1)
                        all_weaknesses.extend(w)
                
                formatted_report["categories"][cat_name] = {
                    "score": cat_data["score"],
                    "feedback": {
                        "strengths": all_strengths,
                        "weaknesses": all_weaknesses
                    }
                }
            
        with open(output_path, 'w') as f:
            yaml.dump(formatted_report, f, sort_keys=False, default_flow_style=False, allow_unicode=True, width=1000)
            
        with open(output_path, 'w') as f:
            yaml.dump(formatted_report, f, sort_keys=False, default_flow_style=False, allow_unicode=True, width=1000)
            
        with open(output_path, 'w') as f:
            yaml.dump(formatted_report, f, sort_keys=False, default_flow_style=False, allow_unicode=True, width=1000)

def main(folder_name: str, use_test_case_ratio: bool = False):
    rubric_path = "dsa_rubric.yaml"
    api_key = "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"
    grader = DSAGrader(api_key, rubric_path)
    
    question_path = os.path.join(folder_name, "question.txt")
    if not os.path.exists(question_path):
        raise FileNotFoundError("question.txt not found in the provided folder.")
    
    with open(question_path, "r") as f:
        problem_text = f.read().strip()
    
    for subfolder in os.listdir(folder_name):
        if not subfolder.startswith("_language"):
            continue
        
        subfolder_path = os.path.join(folder_name, subfolder)
        if not os.path.isdir(subfolder_path):
            continue
        
        for file_name in os.listdir(subfolder_path):
            if file_name.endswith(".txt"):
                student_code_path = os.path.join(subfolder_path, file_name)
                
                with open(student_code_path, "r") as f:
                    student_code = f.read().strip()
                
                test_case_ratio = None
                if use_test_case_ratio:
                    test_case_ratio = float(input(f"Enter test case ratio for {file_name} in {subfolder}: "))
                
                report = grader.grade_submission(problem_text, student_code, test_case_ratio)
                # Remove .txt suffix and create report filename
                base_name = file_name[:-4] if file_name.endswith('.txt') else file_name
                output_report_path = os.path.join(subfolder_path, f"grade_report_{base_name}.yaml")
                grader.save_grade_report(report, output_report_path)
                print(f"Grading completed for {file_name} in {subfolder}. Report saved at {output_report_path}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python dsa.py <folder_name> [use_test_case_ratio]")
        sys.exit(1)
    
    folder_name = sys.argv[1]
    use_test_case_ratio = bool(int(sys.argv[2])) if len(sys.argv) > 2 else False
    
    main(folder_name, use_test_case_ratio)