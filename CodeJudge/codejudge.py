import getpass
import os
import json

from tribal import
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser

def replaceKeys(inputString, keys, values):
    """
    Replaces placeholders in the input string with corresponding values.
    Args:
        inputString (str): The string containing placeholders in the format {key}.
        keys (list of str): A list of keys corresponding to the placeholders.
        values (list of str): A list of values to replace the placeholders.
    Returns:
        str: The input string with placeholders replaced by corresponding values.
    Raises:
        ValueError: If the length of keys and values lists are not the same.
    """
    if len(keys) != len(values):
        raise ValueError("Length of keys and values should be the same")
    for i in range(len(keys)):
        inputString = inputString.replace("{"+keys[i]+"}", values[i])
    return inputString

class CodeJudge:
    """
    CodeJudge is a class designed to evaluate code submissions based on given problem statements.
    It supports two types of evaluations: binary and taxonomical.
    Attributes:
        llm (ChatOpenAI): The language model used for generating responses.
        prompts (list[str]): The list of prompts loaded from the specified JSON file.
    Methods:
        __init__(self, promptLocation="./prompts.json", model="gpt-4o-mini", baseURL=None):
            Initializes the CodeJudge instance with the specified prompt location, model, and base URL.
        _loadPrompts(self, promptLocation: str) -> list[str]:
            Loads prompts from the specified JSON file.
        _loadKeys(self) -> None:
            Loads the OpenAI API key from the environment or prompts the user to enter it.
        _loadBinaryEvaluationPrompts(self) -> list[str]:
            Loads the binary evaluation prompts from the loaded prompts.
        _getLLMResponseBinary(self, problem: str, code: str) -> dict:
            Gets the binary evaluation response from the language model.
        _getLLMResponseTaxonomical(self, problem: str, code: str) -> dict:
            Gets the taxonomical evaluation response from the language model.
        _assignScoreTaxonomical(self, response: list) -> int:
            Assigns a score based on the taxonomical evaluation response.
        evaluateTaxonomical(self, problem: str, code: str, referenceCode: str = None) -> dict:
            Evaluates the code submission using taxonomical evaluation and returns the inconsistencies and score.
        evaluateBinary(self, problem: str, code: str, referenceCode: str = None) -> str:
            Evaluates the code submission using binary evaluation and returns the response.
    """
    def __init__(self, promptLocation="./prompts.json", model="gpt-4o-mini", baseURL = None) -> None:
        self._loadKeys()
        if baseURL = None:
            self.llm = ChatOpenAI(model=model, temperature=0)
        else:
            self.llm = ChatOpenAI(model=model, temperature=0, base_url=baseURL)
        self.prompts = self._loadPrompts(promptLocation)
        return None

    def _loadPrompts(self, promptLocation: str) -> list[str]:
        with open(promptLocation, "r+") as file:
            prompts = json.loads(file.read())
            print("Using CodeJudge Version: {}".format(prompts["version"]))
        return prompts
    
    def _loadKeys(self) -> None:
        if "OPENAI_API_KEY" not in os.environ:
            os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")
        return None

    def _loadBinaryEvaluationPrompts(self) -> list[str]:
        return self.prompts["binaryevaluation"]
    
    def _getLLMResponseBinary(self, problem: str, code: str) -> dict:
        prompts = self._loadBinaryEvaluationPrompts()
        stageOnePrompt = replaceKeys(prompts[0]["prompt"], ["PROBLEM", "CODE"], [problem, code])
        stageOneResponse = self.llm.invoke(stageOnePrompt).content
        print(stageOneResponse)
        stageTwoPrompt = replaceKeys(prompts[1]["prompt"], ["MISTAKE"], [stageOneResponse])
        stageTwoResponse = self.llm.invoke(stageTwoPrompt).content

        return stageTwoResponse
    
    def _getLLMResponseTaxonomical(self, problem: str, code: str) -> dict:
        finalPrompt = replaceKeys(self.prompts["faultlocalization"][0]["prompt"], ["PROBLEM", "CODE"], [problem, code])
        jsonLLM = self.llm.bind(response_format={"type": "json_object"})
        aiMsg = jsonLLM.invoke(finalPrompt)
        return json.loads(aiMsg.content)
    
    def _assignScoreTaxonomical(self, response: list) -> int:
        severity = {"Negligible": 0, "Small": 0, "Major": 0, "Fatal": 0}
        for element in response["inconsistencies"]:
            severity[element["severity"]] += 1
        S = severity["Small"] * 5
        M = severity["Major"] * 50
        F = severity["Fatal"] * 100
        penalty = max(-100, -(S + M + F))
        score = 1 + (penalty/100)
        return score
    
    def evaluateTaxonomical(self, problem:str, code:str, referenceCode:str = None) -> dict:
        response = self._getLLMResponseTaxonomical(problem, code)
        score = self._assignScoreTaxonomical(response)
        return {"inconsistencies": response["inconsistencies"], "score": score}

    def evaluateBinary(self, problem:str, code:str, referenceCode:str = None) -> str:
        response = self._getLLMResponseBinary(problem, code)
        return response
    