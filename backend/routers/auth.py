from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from datetime import timedelta
import uuid
from typing import Dict, Any
from uuid import UUID

from models.user import User
from schemas.user import UserCreate, UserLoginRequest
from utils.security import get_password_hash, create_access_token, verify_password
from database import get_session

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
def register_user(user: UserCreate, session: Session = Depends(get_session)):
    # Check if user with email or username already exists using sync operations
    existing_user_query = select(User).where(
        (User.email == user.email) | (User.username == user.username)
    )
    existing_user_result = session.exec(existing_user_query)
    existing_user = existing_user_result.first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email or username already registered")

    # Hash the password
    hashed_password = get_password_hash(user.password)

    # Create new user
    new_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        is_active=True
    )

    # Add to database using sync operations
    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    # Create access token
    access_token = create_access_token(
        data={"sub": str(new_user.id), "email": new_user.email, "username": new_user.username},
        expires_delta=timedelta(minutes=15)
    )

    # Return registration response
    return {
        "id": str(new_user.id),
        "email": new_user.email,
        "username": new_user.username,
        "is_active": new_user.is_active,
        "created_at": new_user.created_at.isoformat(),
        "uuid": str(new_user.uuid),
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 900
    }

@router.post("/login")
def login_user(login_data: UserLoginRequest, session: Session = Depends(get_session)):
    # Find user by email or username using sync operations
    user_query = select(User).where(
        (User.email == login_data.email) | (User.username == login_data.email)
    )
    user_result = session.exec(user_query)
    user = user_result.first()

    # Check if user exists and password is correct
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Check if user is active
    if not user.is_active:
        raise HTTPException(status_code=401, detail="User account is deactivated")

    # Create access token
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "username": user.username},
        expires_delta=timedelta(minutes=15)
    )

    # Return login response
    return {
        "id": str(user.id),
        "email": user.email,
        "username": user.username,
        "is_active": user.is_active,
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 900
    }