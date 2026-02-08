from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import String, DateTime, Boolean
from typing import Optional, List
from datetime import datetime
from uuid import UUID, uuid4
import uuid as uuid_pkg
from sqlalchemy import Column as SQLAlchemyColumn
from enum import Enum


class UserRole(str, Enum):
    user = "user"
    admin = "admin"


class UserBase(SQLModel):
    email: str = Field(sa_column=SQLAlchemyColumn(String, unique=True, index=True, nullable=False))
    username: str = Field(sa_column=SQLAlchemyColumn(String, unique=True, index=True, nullable=False))
    is_active: bool = Field(sa_column=SQLAlchemyColumn(Boolean, default=True, nullable=False))
    role: UserRole = Field(sa_column=SQLAlchemyColumn(String, default="user", nullable=False))
    created_at: datetime = Field(sa_column=SQLAlchemyColumn(DateTime, default=datetime.utcnow, nullable=False))
    updated_at: datetime = Field(sa_column=SQLAlchemyColumn(DateTime, default=datetime.utcnow, nullable=False))
    uuid: uuid_pkg.UUID = Field(default_factory=uuid4, sa_column=SQLAlchemyColumn(String, unique=True, nullable=False))



class User(UserBase, table=True):
    __tablename__ = "users"

    id: uuid_pkg.UUID = Field(
        default_factory=uuid_pkg.uuid4,
        primary_key=True
    )
    hashed_password: str = Field(sa_column=SQLAlchemyColumn(String, nullable=False))

    # Relationship with tasks
    tasks: List["Task"] = Relationship(back_populates="owner")


class UserCreate(SQLModel):
    email: str
    username: str
    password: str


class UserPublic(SQLModel):
    id: uuid_pkg.UUID
    email: str
    username: str
    is_active: bool
    created_at: datetime
    uuid: uuid_pkg.UUID


class UserUpdate(SQLModel):
    email: Optional[str] = None
    username: Optional[str] = None
    is_active: Optional[bool] = None


class UserLogin(SQLModel):
    email_or_username: str
    password: str