from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from uuid import UUID


class ChatRequest(BaseModel):
    """
    Schema for chat requests.
    """
    message: str
    conversation_id: Optional[str] = None
    timestamp: Optional[str] = None
    context_window_size: Optional[int] = 10
    response_format: Optional[str] = "natural_language"


class ToolCall(BaseModel):
    """
    Schema for tool call information.
    """
    tool_name: str
    parameters: Dict[str, Any]
    result: Dict[str, Any]


class ContextSummary(BaseModel):
    """
    Schema for conversation context summary.
    """
    last_intent: str
    referenced_tasks: List[str]
    conversation_state: str


class ChatResponse(BaseModel):
    """
    Schema for chat responses.
    """
    conversation_id: str
    response: str
    timestamp: str
    tool_calls: List[ToolCall]
    context_summary: ContextSummary


class ConversationHistoryResponse(BaseModel):
    """
    Schema for conversation history responses.
    """
    conversation_id: str
    title: Optional[str]
    created_at: str
    updated_at: str
    messages: List[Dict[str, Any]]


class DeleteConversationResponse(BaseModel):
    """
    Schema for conversation deletion responses.
    """
    conversation_id: str
    deleted_at: str
    message: str