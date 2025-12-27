import os
from typing import Optional
from src.ai.domain.ports import ILLMProvider
from src.ai.adapters.llm.google import GoogleGenAIAdapter
from src.ai.adapters.llm.openai import OpenAIAdapter

class LLMFactory:
    @staticmethod
    def create_provider() -> Optional[ILLMProvider]:
        google_key = os.getenv("GOOGLE_API_KEY")
        if google_key:
            print("LLMFactory: Using Google Gemini")
            return GoogleGenAIAdapter(api_key=google_key)
        
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            print("LLMFactory: Using OpenAI")
            return OpenAIAdapter(api_key=openai_key)
            
        print("LLMFactory: No API Key found.")
        return None
