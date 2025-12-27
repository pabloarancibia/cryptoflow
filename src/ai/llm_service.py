from abc import ABC, abstractmethod
import os
from typing import Optional

class LLMProvider(ABC):
    @abstractmethod
    def generate_text(self, prompt: str, system_instruction: str = None) -> str:
        pass

class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str):
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4o-mini" # or gpt-3.5-turbo

    def generate_text(self, prompt: str, system_instruction: str = None) -> str:
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI Error: {e}")
            raise

class GoogleGeminiProvider(LLMProvider):
    def __init__(self, api_key: str):
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')

    def generate_text(self, prompt: str, system_instruction: str = None) -> str:
        # Gemini specific handling
        # System instructions can be tricky with Gemini-Pro basic API, often just prepended to prompt
        # But 'gemini-1.5-pro' supports system instructions properly. 
        # For 'gemini-pro' (cheaper/standard), prepending is safer.
        
        full_prompt = prompt
        if system_instruction:
            full_prompt = f"System Instruction: {system_instruction}\n\nUser Question: {prompt}"

        try:
            response = self.model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            print(f"Google Gemini Error: {e}")
            raise

class LLMFactory:
    @staticmethod
    def create_provider() -> Optional[LLMProvider]:
        # Priority: GOOGLE_API_KEY -> OPENAI_API_KEY
        
        google_key = os.getenv("GOOGLE_API_KEY")
        if google_key:
            print("Using Google Gemini Provider")
            return GoogleGeminiProvider(google_key)
            
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            print("Using OpenAI Provider")
            return OpenAIProvider(openai_key)
            
        print("No valid API Key found (GOOGLE_API_KEY or OPENAI_API_KEY). LLM features disabled.")
        return None
