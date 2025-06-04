
import json
from docx import Document
import PyPDF2
from openai import OpenAI

class LLM_Util:
    def __init__(self, api_key:str, base_url:str):
        self.api_key = api_key
        self.base_url = base_url
    
    def createResponse(self, isReasoner: bool, system_prompt: bool, user_prompt: bool = None, isJSON: bool = False, messages = None):
        client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        
        response = client.chat.completions.create(
            model= "deepseek-reasoner" if isReasoner else "deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
        ] if messages == None else messages,
            max_tokens=512,
            response_format= {'type': 'json_object' if isJSON else 'text'},
            stream=False
        )
        
        return response
    
    def callDeepseek(self, system_prompt, user_prompt, messages):
        response = self.createResponse(False, system_prompt, user_prompt, False, messages)
        return response.choices[0].message.content

    def callDeepseekCoT(self, system_prompt, user_prompt):
        print("reasoning...")
        response = self.createResponse(True, system_prompt, user_prompt, False)
        print("finished reasoning")
        
        return response.choices[0].message
    
    def callDeepseekJson(self, system_prompt, user_prompt):
        response = self.createResponse(False, system_prompt, user_prompt, True)
        return response.choices[0].message.content
    
    def callDeepseekJsonWithCoT(self, system_prompt, user_prompt):
        response = self.createResponse(False, system_prompt, user_prompt + "\n Here are some thoughts: " + self.callDeepseekCoT(system_prompt, user_prompt).reasoning_content, True)
        
        return response.choices[0].message.content