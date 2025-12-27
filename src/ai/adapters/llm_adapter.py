import os
from src.ai.domain.ports import ILLMProvider

class LLMAdapter(ILLMProvider):
    def __init__(self):
        self.provider_type = "none"
        self.client = None
        self.model_name = ""
        
        # Priority: Google -> OpenAI
        google_key = os.getenv("GOOGLE_API_KEY")
        if google_key:
            from google import genai
            self.client = genai.Client(api_key=google_key)
            self.model_name = "gemini-2.0-flash-exp"
            self.provider_type = "google"
            print("LLMAdapter: Using Google Gemini")
            return

        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            from openai import OpenAI
            self.client = OpenAI(api_key=openai_key)
            self.model_name = "gpt-4o-mini"
            self.provider_type = "openai"
            print("LLMAdapter: Using OpenAI")
            return

        print("LLMAdapter: No API Key found.")

    def generate_text(self, prompt: str, system_instruction: str = None) -> str:
        if self.provider_type == "google":
            # Google GenAI SDK
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config={'system_instruction': system_instruction} if system_instruction else None
                )
                return response.text
            except Exception as e:
                print(f"Google GenAI Error: {e}")
                return "Error generating text."
        
        elif self.provider_type == "openai":
            # OpenAI SDK
            try:
                messages = []
                if system_instruction:
                    messages.append({"role": "system", "content": system_instruction})
                messages.append({"role": "user", "content": prompt})
                
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=0.7
                )
                return response.choices[0].message.content
            except Exception as e:
                print(f"OpenAI Error: {e}")
                return "Error generating text."
        
        return "LLM Provider not configured."
