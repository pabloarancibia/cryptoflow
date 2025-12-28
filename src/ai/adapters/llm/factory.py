import os
from typing import Optional
from src.ai.domain.ports import ILLMProvider
from src.ai.adapters.llm.google import GoogleGenAIAdapter
from src.ai.adapters.llm.openai import OpenAIAdapter

class LLMFactory:
    @staticmethod
    def create_provider() -> Optional[ILLMProvider]:
        """
        Create an LLM provider instance based on available configuration.
        
        Priority:
        1. Azure OpenAI (if AZURE_OPENAI_ENDPOINT is set)
        2. Google Gemini (if GOOGLE_API_KEY is set)
        3. OpenAI (if OPENAI_API_KEY is set)
        
        Returns:
            ILLMProvider instance or None if no configuration found
        """
        # Check for Azure OpenAI
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        azure_key = os.getenv("AZURE_OPENAI_API_KEY")
        
        if azure_endpoint and azure_key:
            try:
                from src.ai.adapters.azure.llm_adapter import AzureSemanticKernelAdapter
                print("LLMFactory: Using Azure OpenAI (Semantic Kernel)")
                return AzureSemanticKernelAdapter(
                    endpoint=azure_endpoint,
                    api_key=azure_key
                )
            except ImportError as e:
                print(f"LLMFactory: Azure adapter not available: {e}")
                print("LLMFactory: Falling back to other providers")
        
        # Check for Google Gemini
        google_key = os.getenv("GOOGLE_API_KEY")
        if google_key:
            print("LLMFactory: Using Google Gemini")
            return GoogleGenAIAdapter(api_key=google_key)
        
        # Check for OpenAI
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            print("LLMFactory: Using OpenAI")
            return OpenAIAdapter(api_key=openai_key)
            
        print("LLMFactory: No API Key found.")
        return None
