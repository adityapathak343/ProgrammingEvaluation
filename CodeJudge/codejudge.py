import getpass
import os
import json

from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser

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
    
    def _getLLMResponseTaxonomical(self, problem: str, code: str) -> dict:
        finalPrompt = self.prompts["faultlocalization"][0]["prompt"].replace(r"{PROBLEM}", problem).replace(r"{CODE}", code)
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
    
    def evaluateTaxonomical(self, problem:str, code:str) -> tuple:
        response = self._getLLMResponseTaxonomical(problem, code)
        score = self._assignScoreTaxonomical(response)
        return {"inconsistencies": response["inconsistencies"], "score": score}
    