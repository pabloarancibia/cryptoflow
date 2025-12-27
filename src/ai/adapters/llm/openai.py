from typing import List, Dict, Union
from src.ai.adapters.llm.base import BaseLLMAdapter
from src.ai.domain.models import ToolCall

class OpenAIAdapter(BaseLLMAdapter):
    def __init__(self, api_key: str, model_name: str = "gpt-4o-mini"):
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key)
        self.model_name = model_name

    def generate_text(self, prompt: str, system_instruction: str = None) -> str:
        try:
            messages = []
            if system_instruction:
                messages.append({"role": "system", "content": system_instruction})
            messages.append({"role": "user", "content": prompt})
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI Error: {e}")
            return "Error generating text."

    def generate_with_tools(self, prompt: str, tools: List[Dict], system_instruction: str = None) -> Union[str, ToolCall]:
        # Implementation skeleton for OpenAI native tool calling
        # Map response to ToolCall
        pass
