import getpass
import os
import json

from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser

def promptInjection(promptString, keys, vals):
    if len(keys) != len(vals):
        raise ValueError("Length of keys and values should be the same.")
    for i in range(len(keys)):
        promptString = promptString.replace("{"+keys[i]+"}", vals[i])
    return promptString

class RubricGen:
    def __init__(self, promptLocation="./prompts.json", model="gpt-4o-mini") -> None:
        self._loadLLM()
        self.llm = ChatOpenAI(model=model, temperature=0)
        self.prompts = self._loadPrompts(promptLocation)
        return None

    def _loadPrompts(self, promptLocation: str) -> list[str]:
        with open(promptLocation, "r+") as file:
            prompts = json.loads(file.read())
        return prompts
    
    def _loadLLM(self) -> None:
        if "OPENAI_API_KEY" not in os.environ:
            os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")
        return None