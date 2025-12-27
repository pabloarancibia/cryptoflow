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
        """
        Generates a response from the LLM, potentially calling a tool.
        
        Args:
            prompt: The user's input prompt.
            tools: A list of tool definitions (dictionaries).
            system_instruction: Optional system instruction.
            
        Returns:
            Either the text response (str) or a ToolCall object.
        """
        import json
        
        try:
            messages = []
            if system_instruction:
                messages.append({"role": "system", "content": system_instruction})
            messages.append({"role": "user", "content": prompt})
            
            # OpenAI expects tools in a specific format: {"type": "function", "function": { ... }}
            formatted_tools = []
            for tool_def in tools:
                formatted_tools.append({
                    "type": "function",
                    "function": tool_def
                })
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                tools=formatted_tools,
                tool_choice="auto"
            )
            
            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls
            
            if tool_calls:
                # For now, we handle the first tool call
                # In a more complex scenario, we might handle multiple
                first_tool_call = tool_calls[0]
                function_name = first_tool_call.function.name
                arguments_str = first_tool_call.function.arguments
                
                try:
                    arguments = json.loads(arguments_str)
                except json.JSONDecodeError:
                    print(f"Error parsing arguments for tool {function_name}: {arguments_str}")
                    arguments = {}
                    
                return ToolCall(name=function_name, arguments=arguments)
            else:
                return response_message.content or ""
                
        except Exception as e:
            print(f"OpenAI Tool Calling Error: {e}")
            return "Error generating response with tools."
