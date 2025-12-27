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
        from google import genai
        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-1.5-flash"

    def generate_text(self, prompt: str, system_instruction: str = None) -> str:
        try:
            # google-genai supports system instructions via config
            config = None
            if system_instruction:
                # Basic prompting with system instruction in the message flow logic
                # or simplified by just calling generate_content
                pass
            
            # For simplicity with the new SDK:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config={'system_instruction': system_instruction} if system_instruction else None
            )
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
