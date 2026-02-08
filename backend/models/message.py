from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime
import uuid
from enum import Enum


class MessageRole(str, Enum):
    """Enumeration of possible message roles"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class MessageBase(SQLModel):
    """Base class for Message with common fields"""
    conversation_id: str = Field(foreign_key="conversation.id", index=True, nullable=False)
    user_id: str = Field(index=True, nullable=False)
    role: MessageRole = Field(nullable=False)
    content: str = Field(nullable=False, max_length=10000)


class Message(MessageBase, table=True):
    """Message model representing a single message in a conversation"""
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationship to conversation
    conversation: "Conversation" = Relationship(back_populates="messages")


class MessageRead(MessageBase):
    """Schema for reading message data"""
    id: str
    created_at: datetime
    updated_at: datetime


class MessageCreate(MessageBase):
    """Schema for creating a new message"""
    pass


class MessageUpdate(SQLModel):
    """Schema for updating a message"""
    content: Optional[str] = None
    role: Optional[MessageRole] = None