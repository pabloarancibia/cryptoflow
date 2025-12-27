from abc import ABC, abstractmethod
from typing import List, Dict, Any, Union
from src.ai.domain.models import DocumentChunk, ToolCall

class IVectorStore(ABC):
    """Port for Vector Database operations."""
    
    @abstractmethod
    def ingest(self, docs: List[DocumentChunk]) -> None:
        """Ingests documents into the store."""
        pass

    @abstractmethod
    def query(self, text: str, n_results: int = 5) -> List[DocumentChunk]:
        """Retrieves documents relevant to the query."""
        pass

class ILLMProvider(ABC):
    """Port for Large Language Model operations."""
    
    @abstractmethod
    def generate_text(self, prompt: str, system_instruction: str = None) -> str:
        """Generates text from the LLM."""
        pass

    @abstractmethod
    def generate_with_tools(self, prompt: str, tools: List[Dict], system_instruction: str = None) -> Union[str, ToolCall]:
        """Generates text or a tool call from the LLM."""
        pass

class ITradingTool(ABC):
    """Port for Trading Operations."""
    
    @abstractmethod
    def execute(self, symbol: str, side: str, quantity: float) -> Dict[str, Any]:
        """Executes a trade."""
        pass
