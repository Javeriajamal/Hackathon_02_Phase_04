from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
import uuid


class ConversationBase(SQLModel):
    """Base class for Conversation with common fields"""
    user_id: str = Field(index=True, nullable=False)
    title: Optional[str] = Field(default=None, max_length=255)


class Conversation(ConversationBase, table=True):
    """Conversation model representing a chat conversation"""
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationship to messages
    messages: List["Message"] = Relationship(back_populates="conversation", cascade_delete=True)


class ConversationRead(ConversationBase):
    """Schema for reading conversation data"""
    id: str
    created_at: datetime
    updated_at: datetime
    message_count: int


class ConversationCreate(ConversationBase):
    """Schema for creating a new conversation"""
    pass


class ConversationUpdate(SQLModel):
    """Schema for updating a conversation"""
    title: Optional[str] = None