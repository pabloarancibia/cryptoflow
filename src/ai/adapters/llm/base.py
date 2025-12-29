from abc import ABC
from src.ai.domain.ports import ILLMProvider

class BaseLLMAdapter(ILLMProvider, ABC):
    """Base class for LLM Adapters."""
    pass
