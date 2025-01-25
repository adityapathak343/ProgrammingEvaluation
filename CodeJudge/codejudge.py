import getpass
import os
import json

from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser

def replaceKeys(inputString, keys, values):
    if len(keys) != len(values):
        raise ValueError("Length of keys and values should be the same")
    for i in range(len(keys)):
        inputString = inputString.replace("{"+keys[i]+"}", values[i])
    return inputString

class CodeJudge:
    def __init__(self, promptLocation="./prompts.json", model="gpt-4o-mini") -> None:
        self._loadLLM()
        self.llm = ChatOpenAI(model=model, temperature=0)
        self.prompts = self._loadPrompts(promptLocation)
        return None

    def _loadPrompts(self, promptLocation: str) -> list[str]:
        with open(promptLocation, "r+") as file:
            prompts = json.loads(file.read())
            print("Using CodeJudge Version: {}".format(prompts["version"]))
        return prompts
    
    def _loadLLM(self) -> None:
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
    