from database.user_queries import (
    get_user_by_email, create_user, update_user, authenticate_user
)
from models.user import UserCreate, UserUpdate
from database import get_sync_engine
from sqlmodel import Session
from typing import Optional
import uuid


def get_user_by_email_service(email: str) -> Optional[dict]:
    """Service to get user by email"""
    engine = get_sync_engine()
    with Session(engine) as session:
        user = get_user_by_email(session, email)
        if user:
            return {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "is_active": user.is_active,
                "created_at": user.created_at,
                "updated_at": user.updated_at
            }
        return None


def create_user_service(user_create: UserCreate) -> dict:
    """Service to create a new user"""
    engine = get_sync_engine()
    with Session(engine) as session:
        user = create_user(session, user_create)
        return {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "created_at": user.created_at,
            "updated_at": user.updated_at
        }


def update_user_service(user_id: uuid.UUID, user_update: UserUpdate) -> Optional[dict]:
    """Service to update a user"""
    engine = get_sync_engine()
    with Session(engine) as session:
        user = update_user(session, user_id, user_update)
        if user:
            return {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "is_active": user.is_active,
                "created_at": user.created_at,
                "updated_at": user.updated_at
            }
        return None


def authenticate_user_service(email: str, password: str) -> Optional[dict]:
    """Service to authenticate a user"""
    engine = get_sync_engine()
    with Session(engine) as session:
        user = authenticate_user(session, email, password)
        if user:
            return {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "is_active": user.is_active,
                "created_at": user.created_at,
                "updated_at": user.updated_at
            }
        return None