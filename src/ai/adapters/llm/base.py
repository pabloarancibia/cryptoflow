from abc import ABC
from typing import List, Dict, Union
from src.ai.domain.ports import ILLMProvider
from src.ai.domain.models import ToolCall

class BaseLLMAdapter(ILLMProvider, ABC):
    """Base class for LLM Adapters."""
    pass
