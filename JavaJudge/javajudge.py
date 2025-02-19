import subprocess
import re
import json
import getpass
import os

from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser

logicalMarks = None

def calculate_score(error_count: int) -> float:
    """Calculates score by deducting 0.75 marks for each error."""
    score = max(5.0 - (0.75 * error_count), 0.0)
    return round(score, 2)  # Rounds to 2 decimal places

def check_java_syntax(java_file_path: str) -> tuple[int, float, dict]:
    """
    Reads Java code from a file and checks for syntax errors using `javac`.
    Returns the error count, score, and a dictionary of errors.
    """
    error_dict = {}  # Dictionary to store errors by line number
    
    try:
        # Compile the Java file using javac
        result = subprocess.run(
            ["javac", java_file_path],
            capture_output=True,
            text=True
        )
        
        error_count = 0
        if result.stderr:
            print("Compilation Errors:")
            errors = result.stderr.strip().split('\n')
            
            # Process each error message
            for error in errors:
                # Skip the last line which contains error count
                if 'error' in error and not re.search(r'\d+ errors?$', error):
                    # Extract line number using regex
                    line_match = re.search(r':(\d+):', error)
                    if line_match:
                        line_num = int(line_match.group(1))
                        # Remove the file path and line number from the error message
                        error_msg = re.sub(r'^.*?:\d+:', '', error).strip()
                        
                        # Add error to dictionary
                        if line_num not in error_dict:
                            error_dict[line_num] = []
                        error_dict[line_num].append(error_msg)
                        print(f"- Line {line_num}: {error_msg}")
            
            # Extract the total error count
            last_line = errors[-1]
            if match := re.search(r'(\d+) errors?', last_line):
                error_count = int(match.group(1))
        else:
            print("No syntax errors found!")

        # Calculate score based on error count
        score = calculate_score(len(error_dict))
        print(f"\nCompiler reported errors: {error_count}")
        print(f"Number of lines with errors: {len(error_dict)}")
        print(f"Score: {score}/5")
        print("\nError Dictionary:")
        print(json.dumps(error_dict, indent=2))
        
        return error_count, score, error_dict
        
    except Exception as e:
        print(f"An error occurred: {e}")
        return -1, 0.0, {}

class APIKeyMissingException(Exception):
    """Exception raised when an API key is missing."""
    def __init__(self, message="API key is missing. Please provide a valid API key."):
        self.message = message
        super().__init__(self.message)

class JavaJudge:
    def __init__(self, model="gpt-4o-mini", baseURL=None, api_key=None) -> None:
        self._loadKeys()
        if baseURL == None:
            self.llm = ChatOpenAI(model=model, temperature=0).bind(response_format={"type": "json_object"})
        else:
            if api_key == None:
                print(f"Please provide an API key for the {baseURL} model.")
                raise APIKeyMissingException
                return None
            self.llm = ChatOpenAI(model=model, temperature=0, base_url=baseURL, api_key=api_key).bind(response_format={"type": "json_object"})
        self._loadPrompts()
        return None

    def _loadPrompts(self) -> list[str]:
        self.oneStepPrompt = '''You are an expert code evaluator, evaluating code submissions for a Java based Object Oriented Programming test at a university level.
You will be provided with the question and a rubric that describes the criteria for evaluation, with a marking scheme. 
The question is a code sample that the examiner provides, containing a template wherein the student is required to write the code as well as comments and instructions from the examiner's end.
Following this you will be provided with the code submission, along with the response from the Java compiler that runs this code.
Note that the code may be formatted liberally, the specific positioning of the code within the methods are not important.
Code may be present either before or after the comments prepared by the instructor.
You are to evaluate the code based only on logical correctness. You are to ignore any syntax errors that the compiler may have thrown. 
Any syntax errors that you encounter can be treated as correct syntax, and you are to infer the student's logical flow and intention from the code.
You are to return your response as a JSON dictionary containing a detailed, nested evaluation of the student's marks for each line in the rubric.
For each line in the rubric, you are to provide the line as the key and your assigned marks as the value.
DO NOT RETURN ANY ADDITIONAL TEXT ASIDE FROM THE JSON DICTIONARY.
Question: {}
Rubric: {}
Code Submission: {}
Compiler Response: {}
'''
        self.twoStepPrompt = [
            '''You are an expert code evaluator, evaluating code submissions for a Java based Object Oriented Programming test at a university level.
You will be provided with the code submission and no context whatsoever. You are to infer the student's logical flow and intention from the code.
You are to ignore any syntaxical errors, and are solely to evaluate the code based on logical correctness.
Code Submission: {}
''', 
'''You are an expert code evaluator, evaluating code submissions for a Java based Object Oriented Programming test at a university level.
You will be provided a question, a marking rubric, and also with the logical flow and intention of a student's code. 
The question is a code sample that the examiner provides, containing a template wherein the student is required to write the code as well as comments and instructions from the examiner's end.
You are to compare the student's logic with what was asked by the question and the rubric.
Question: {}
Rubric: {}
Logical Flow and Intention: {}
'''
    ]
        

    def _loadKeys(self) -> None:
        if "OPENAI_API_KEY" not in os.environ:
            os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")
        return None

    def _getOneStepResponse(self, question, rubric, code, compilerResponse):
        finalPrompt = self.oneStepPrompt.format(question, rubric, code, compilerResponse)
        response = json.loads(self.llm.invoke(finalPrompt).content)
        return response

    def _syntaxMarks(self, compilerResponse, syntaxMarks, penalty):
        errorCount = len(compilerResponse.keys())
        for key in compilerResponse:
            if key == '283':
                errorCount -= 1
        return max(syntaxMarks - (penalty * errorCount), 0)
    
    def _debug(self, compilerResponse=None, response=None, logicalMarks=None, syntaxMarks=None, finalMarks=None):
        print("Debugging Information:")
        print("compilerResponse: ", compilerResponse)
        print("response: ", response)
        print("logicalMarks: ", logicalMarks)
        print("syntaxMarks: ", syntaxMarks)
        print("finalMarks: ", finalMarks)
        return None

    def evaluateAIO(self, question, rubric, codeFilepath, syntaxMarks=5, penalty=1, debug=False):
        compilerResponse = check_java_syntax(codeFilepath)[2]
        global logicalMarks
        logicalMarks = 0
        try:
            solution = open(codeFilepath, "r").read()
        except Exception as e:
            print(f"Error reading file {solutionFilepath}\n Error details: {e}")

        response = self._getOneStepResponse(question, rubric, solution, compilerResponse)
        
        def getMarks(evaluation: dict):
            global logicalMarks
            for key in evaluation:
                if type(evaluation[key]) == dict:
                    getMarks(evaluation[key])
                elif type(evaluation[key]) == int:
                    logicalMarks += evaluation[key]
        getMarks(response)
        syntaxMarks = self._syntaxMarks(compilerResponse, syntaxMarks, penalty)
        finalMarks = logicalMarks + syntaxMarks
        if debug:
            self._debug(compilerResponse, response, logicalMarks, syntaxMarks, finalMarks)
        return logicalMarks, syntaxMarks, finalMarks

