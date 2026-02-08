from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import String, Text, DateTime, Boolean
import uuid
from sqlalchemy import Column as SQLAlchemyColumn
from enum import Enum


class TaskStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"


class TaskPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"


class TaskBase(SQLModel):
    title: str = Field(sa_column=SQLAlchemyColumn(String(255), nullable=False))
    description: Optional[str] = Field(sa_column=SQLAlchemyColumn(Text, nullable=True))
    status: TaskStatus = Field(sa_column=SQLAlchemyColumn(String(20), default="pending", nullable=False))
    priority: TaskPriority = Field(sa_column=SQLAlchemyColumn(String(20), default="medium", nullable=False))
    due_date: Optional[datetime] = Field(sa_column=SQLAlchemyColumn(DateTime, nullable=True))
    is_completed: bool = Field(sa_column=SQLAlchemyColumn(Boolean, default=False, nullable=False))
    created_at: datetime = Field(sa_column=SQLAlchemyColumn(DateTime, default=datetime.utcnow, nullable=False))
    updated_at: datetime = Field(sa_column=SQLAlchemyColumn(DateTime, default=datetime.utcnow, nullable=False))
    owner_id: uuid.UUID = Field(foreign_key="users.id")


class Task(TaskBase, table=True):
    __tablename__ = "tasks"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True
    )

    # Relationship with User
    owner: "User" = Relationship(back_populates="tasks")


class TaskCreate(SQLModel):
    title: str
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None


class TaskPublic(SQLModel):
    id: uuid.UUID
    title: str
    description: Optional[str]
    status: TaskStatus
    priority: TaskPriority
    due_date: Optional[datetime]
    owner_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    is_completed: bool


class TaskUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None
    is_completed: Optional[bool] = None