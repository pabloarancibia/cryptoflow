import os
from typing import List, Dict, Union, Any
from google import genai
from google.genai import types
from src.ai.adapters.llm.base import BaseLLMAdapter
from src.ai.domain.models import ToolCall

class GoogleGenAIAdapter(BaseLLMAdapter):
    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash-exp"):
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    def generate_text(self, prompt: str, system_instruction: str = None) -> str:
        try:
            config = types.GenerateContentConfig(
                system_instruction=system_instruction
            ) if system_instruction else None

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config
            )
            return response.text
        except Exception as e:
            print(f"Google GenAI Error: {e}")
            return "Error generating text."

    def generate_with_tools(self, prompt: str, tools: List[Dict], system_instruction: str = None) -> Union[str, ToolCall]:
        try:
            # Convert dict tools to SDK format
            function_declarations = []
            for tool in tools:
                function_declarations.append(
                    types.FunctionDeclaration(
                        name=tool["name"],
                        description=tool["description"],
                        parameters=tool["parameters"]
                    )
                )
            
            tool_config = types.Tool(function_declarations=function_declarations)

            config = types.GenerateContentConfig(
                system_instruction=system_instruction,
                tools=[tool_config]
            )

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config
            )
            
            candidates = response.candidates
            if not candidates:
                return "No response."
            
            content = candidates[0].content
            parts = content.parts
            
            for part in parts:
                if part.function_call:
                    fc = part.function_call
                    return ToolCall(
                        name=fc.name,
                        arguments=fc.args
                    )
            
            return response.text
            
        except Exception as e:
            print(f"Google GenAI Error (Tools): {e}")
            return f"Error generating with tools: {e}"
