import getpass
import os
import json

from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser

class LLModel:
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
        return prompts
    
    def _loadKeys(self) -> None:
        if "OPENAI_API_KEY" not in os.environ:
            os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")
        return None
