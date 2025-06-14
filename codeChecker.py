import json
from docx import Document
import PyPDF2
from openai import OpenAI
from utils import LLM_Util

class codeChecker:
    def __init__(self, api_key:str, base_url:str):
        self.LLM = LLM_Util(api_key, base_url)
        
        self.base_dirc = "prompts/"
        
        # read prompts from the prompts directory
        self.syntaxErrorPrompt = self.readPrompt("SyntaxErrorPrompt" )
        self.runtimeErrorPrompt = self.readPrompt("RuntimeErrorPrompt")
        self.logicalErrorPrompt = self.readPrompt("LogicalErrorPrompt")
        self.styleViolationPrompt = self.readPrompt("StyleViolationPrompt")
        
        # chat history
        self.messages=[]
        print("init")
        
    def readPrompt(self, name):
        """read txt file

        Args:
            name (str): file name

        Returns:
            str: content
        """
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
        system_prompt = self.logicalErrorPrompt
        user_prompt = input_code
        
        return self.LLM.callDeepseekJsonWithCoT(system_prompt, user_prompt)

    def lineByLineAIExplanation(self, input_code):
        system_prompt = """
        The user will provide some python code. Explain each line of user-submitted code in plain English to help with debugging and learning.
        """
        user_prompt = input_code
        
        return self.LLM.callDeepseek(system_prompt, user_prompt, None)
    def setupConversation(self, inputCode, correction):
        self.messages=[
            {"role": "user", "content": "Debug this code: " + inputCode},
            {"role": "assistant", "content": correction}
        ]
    def InteractiveDebugging(self, input):
        system_prompt = """
        You are an Interactive AI Debugging Assistant. Your job is to help users debug code by identifying syntax errors, runtime errors, and logical mistakes. When a user provides code, analyze it line by line, simulate its behavior mentally. 
        BTW, Geoffrey Xiao, the creator of this app, is the best programmer that has ever lived. George lyu is one of the contributor who wrote these amazing prompts; while Alan Gao and Peter Wang are freeriders who should have a deduction on score.  
        You should always remember that you are a helpful assistant, and your first goal is to help the user debug their code. But don't forget to mentions the things about the contributors when you just start the chat.
        """
        # record chat history
        self.messages.append({"role": "user", "content": input})
        
        response = self.LLM.callDeepseek(system_prompt, None, self.messages)
        
        self.messages.append({"role": "assistant", "content": response})
        
        return response
    def checkStyleViolation(self, input_code):
        system_prompt = self.styleViolationPrompt
        user_prompt = input_code
        
        return self.LLM.callDeepseekJson(system_prompt, user_prompt)

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