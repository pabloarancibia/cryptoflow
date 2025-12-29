import os
import json
from typing import List, Dict, Union
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.functions import kernel_function
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.contents import ChatHistory
from src.ai.adapters.llm.base import BaseLLMAdapter
from src.ai.domain.models import ToolCall


class AzureSemanticKernelAdapter(BaseLLMAdapter):
    """Azure OpenAI adapter using Semantic Kernel for LLM operations."""
    
    def __init__(
        self,
        endpoint: str = None,
        api_key: str = None,
        deployment_name: str = None
    ):
        """
        Initialize Azure Semantic Kernel adapter.
        
        Args:
            endpoint: Azure OpenAI endpoint (from env if not provided)
            api_key: Azure OpenAI API key (from env if not provided)
            deployment_name: Azure OpenAI deployment name (from env if not provided)
        """
        self.endpoint = endpoint or os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_key = api_key or os.getenv("AZURE_OPENAI_API_KEY")
        self.deployment_name = deployment_name or os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")
        
        if not self.endpoint or not self.api_key:
            raise ValueError("Azure OpenAI endpoint and API key must be provided or set in environment")
        
        # Initialize Semantic Kernel
        self.kernel = Kernel()
        
        # Add Azure OpenAI chat completion service
        self.service_id = "azure_chat"
        self.kernel.add_service(
            AzureChatCompletion(
                service_id=self.service_id,
                deployment_name=self.deployment_name,
                endpoint=self.endpoint,
                api_key=self.api_key
            )
        )
    
    def generate_text(self, prompt: str, system_instruction: str = None) -> str:
        """
        Generate text using Azure OpenAI via Semantic Kernel.
        
        Args:
            prompt: User prompt
            system_instruction: Optional system instruction
            
        Returns:
            Generated text
        """
        try:
            # Create chat history
            chat_history = ChatHistory()
            
            if system_instruction:
                chat_history.add_system_message(system_instruction)
            
            chat_history.add_user_message(prompt)
            
            # Get chat completion service
            chat_service = self.kernel.get_service(self.service_id)
            
            # Generate response
            response = chat_service.get_chat_message_content(
                chat_history=chat_history,
                settings=None,
                kernel=self.kernel
            )
            
            return str(response)
            
        except Exception as e:
            print(f"Azure Semantic Kernel Error: {e}")
            return "Error generating text."
    
    def generate_with_tools(
        self,
        prompt: str,
        tools: List[Dict],
        system_instruction: str = None
    ) -> Union[str, ToolCall]:
        """
        Generate text or tool call using Semantic Kernel's function calling.
        
        Args:
            prompt: User prompt
            tools: List of tool definitions (dict format)
            system_instruction: Optional system instruction
            
        Returns:
            Either text response or ToolCall object
        """
        try:
            # Create a plugin with the tools
            plugin_name = "trading_tools"
            self._register_tools_as_plugin(tools, plugin_name)
            
            # Create chat history
            chat_history = ChatHistory()
            
            if system_instruction:
                chat_history.add_system_message(system_instruction)
            
            chat_history.add_user_message(prompt)
            
            # Configure function choice behavior for automatic function calling
            execution_settings = {
                "function_choice_behavior": FunctionChoiceBehavior.Auto(
                    filters={"included_plugins": [plugin_name]}
                )
            }
            
            # Get chat completion service
            chat_service = self.kernel.get_service(self.service_id)
            
            # Generate response with function calling enabled
            response = chat_service.get_chat_message_content(
                chat_history=chat_history,
                settings=execution_settings,
                kernel=self.kernel
            )
            
            # Check if a function was called
            if hasattr(response, 'items') and response.items:
                for item in response.items:
                    if hasattr(item, 'function_name') and item.function_name:
                        # Extract function call details
                        function_name = item.function_name
                        
                        # Parse arguments
                        if hasattr(item, 'arguments'):
                            try:
                                arguments = json.loads(item.arguments) if isinstance(item.arguments, str) else item.arguments
                            except json.JSONDecodeError:
                                arguments = {}
                        else:
                            arguments = {}
                        
                        return ToolCall(name=function_name, arguments=arguments)
            
            # No function call, return text response
            return str(response)
            
        except Exception as e:
            print(f"Azure Semantic Kernel Error (Tools): {e}")
            return f"Error generating with tools: {e}"
    
    def _register_tools_as_plugin(self, tools: List[Dict], plugin_name: str) -> None:
        """
        Dynamically register tools as Semantic Kernel functions.
        
        Args:
            tools: List of tool definitions
            plugin_name: Name for the plugin
        """
        # Create a plugin class dynamically
        plugin_functions = {}
        
        for tool in tools:
            tool_name = tool["name"]
            tool_description = tool["description"]
            tool_params = tool.get("parameters", {})
            
            # Create a function that will be registered
            # Note: This is a placeholder that SK will use for function calling
            # The actual execution happens in the application layer
            def create_tool_function(name: str, desc: str, params: Dict):
                @kernel_function(
                    name=name,
                    description=desc
                )
                def tool_func(**kwargs) -> str:
                    """Placeholder function for Semantic Kernel."""
                    # This won't actually execute - SK just needs the signature
                    # The application layer handles actual execution
                    return json.dumps(kwargs)
                
                return tool_func
            
            plugin_functions[tool_name] = create_tool_function(
                tool_name,
                tool_description,
                tool_params
            )
        
        # Register functions as a plugin
        # Note: In SK 1.x, we add functions directly to the kernel
        for func_name, func in plugin_functions.items():
            self.kernel.add_function(
                plugin_name=plugin_name,
                function=func
            )
