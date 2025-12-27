from dataclasses import dataclass
from typing import Dict, Optional, Any

@dataclass
class DocumentChunk:
    """Represents a chunk of text from the documentation."""
    content: str
    metadata: Dict[str, Any]
    id: str

@dataclass
class AgentResponse:
    """Represents the agent's decision and output."""
    response_text: str
    tool_used: Optional[str] = None
    tool_result: Optional[Dict[str, Any]] = None

@dataclass
class ToolCall:
    """Represents a request to execute a tool."""
    name: str
    arguments: Dict[str, Any]

@dataclass
class ToolDefinition:
    """Represents the schema of a tool available to the LLM."""
    name: str
    description: str
    parameters: Dict[str, Any]
