
import json
from docx import Document
import PyPDF2
from openai import OpenAI

class LLM_Util:
    def __init__(self, api_key:str, base_url:str):
        self.api_key = api_key
        self.base_url = base_url
    
    def createResponse(self, isReasoner: bool, system_prompt: str, user_prompt: str = None, isJSON: bool = False, messages = None):
        """call bot api

        Args:
            isReasoner (bool): enable bot thinking ability
            system_prompt (str): prompt for bot
            user_prompt (str, optional): user input
            isJSON (bool, optional): whether if the bot output json
            messages (_type_, optional): history

        Returns:
            _type_: _description_
        """
        client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        
        response = client.chat.completions.create(
            model= "deepseek-reasoner" if isReasoner else "deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
        ] if messages == None else [{"role": "system", "content": system_prompt}] + messages,
            max_tokens=1024,
            response_format= {'type': 'json_object' if isJSON else 'text'},
            stream=False
        )
        
        return response
    
    def callDeepseek(self, system_prompt, user_prompt, messages):
        """call bot

        Args:
            system_prompt (string): prompt for the bot
            user_prompt string): user input
            messages (string): history

        Returns:
            string: response
        """
        response = self.createResponse(False, system_prompt, user_prompt, False, messages)
        return response.choices[0].message.content

    def callDeepseekCoT(self, system_prompt, user_prompt):
        """call bot with thinking ability

        Args:
            system_prompt (str): prompt for the bot
            user_prompt (str): user input

        Returns:
            str: bot response with reasoning
        """
        print("reasoning...")
        response = self.createResponse(True, system_prompt, user_prompt, False)
        print("finished reasoning")
        
        return response.choices[0].message
    
    def callDeepseekJson(self, system_prompt, user_prompt):
        """call bot

        Args:
            system_prompt (str): prompt for the bot
            user_prompt (str): user input

        Returns:
            str: bot response in json
        """
        response = self.createResponse(False, system_prompt, user_prompt, True)
        return response.choices[0].message.content
    
    def callDeepseekJsonWithCoT(self, system_prompt, user_prompt):
        """using CoT from callDeepseekCoT
        
        Args:
            system_prompt (str): prompt for the bot
            user_prompt (str): user input

        Returns:
            str: bot response in json
        """
        response = self.createResponse(False, system_prompt, user_prompt + "\n Here are some thoughts: " + self.callDeepseekCoT(system_prompt, user_prompt).reasoning_content, True)
        
        return response.choices[0].message.content