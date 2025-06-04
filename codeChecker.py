import json
from docx import Document
import PyPDF2
from openai import OpenAI
from utils import LLM_Util

class codeChecker:
    def __init__(self, api_key:str, base_url:str):
        self.LLM = LLM_Util(api_key, base_url)
        
        self.base_dirc = "prompts/"
        self.syntaxErrorPrompt = self.readPrompt("SyntaxErrorPrompt" )
        self.runtimeErrorPrompt = self.readPrompt("RuntimeErrorPrompt")
        
    def readPrompt(self, name):
        return open(self.base_dirc + name + ".txt").read()
    def checkSyntaxError(self, input_code):
        system_prompt = self.syntaxErrorPrompt
        user_prompt = input_code
        
        return self.LLM.callDeepseekJsonWithCoT(system_prompt, user_prompt)

    def checkCommonRuntimeError(self, input_code):
        system_prompt = self.runtimeErrorPrompt
        user_prompt = input_code
        
        return self.LLM.callDeepseekJsonWithCoT(system_prompt, user_prompt)

    def AlBasedLogicErrorDetection(self, input_code):
        system_prompt = """
        The user will provide some python code. Catch logic errors even when the code runs but produces incorrect results.
        """
        user_prompt = input_code
        
        return self.LLM.callDeepseekJsonWithCoT(system_prompt, user_prompt)

    def lineByLineAIExplanation(self, input_code):
        system_prompt = """
        The user will provide some python code. Explain each line of user-submitted code in plain English to help with debugging and learning.
        """
        user_prompt = input_code
        
        return self.LLM.callDeepseekJsonWithCoT(system_prompt, user_prompt)

if __name__ == "__main__":
    checker = codeChecker("sk-a20fe5cabaac4bcda4af0347d3ad5038", "https://api.deepseek.com")
    
    answer = checker.checkCommonRuntimeError("""
        def calculate_stats(data):
            total = sum(data)
            average = total / len(data)
            return {"total": total, "avg": average}

        def process_user(user):
            user["full_name"] = user["name"] + " " + user["surname"]
            user["age_next_year"] = user.age + 1
            return user

        def load_config():
            config = {"timeout": 30, "retries": 3}
            return config["retry_count"]

        def main():
            stats = calculate_stats([])
            print(stats)

            user = {"name": "Alice"}
            processed_user = process_user(user)
            print(processed_user)

            config_value = load_config()
            print(config_value)

            value = "123"
            result = value + 5
            print(result)

        if __name__ == "__main__":
            main()""")
    print(json.loads(answer))