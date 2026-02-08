from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime
import uuid as uuid_pkg


class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in v):
            raise ValueError('Password must contain at least one special character')
        return v

    @validator('username')
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters long')
        if len(v) > 50:
            raise ValueError('Username must be less than 50 characters')
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username can only contain alphanumeric characters, underscores, and hyphens')
        return v


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    is_active: Optional[bool] = None


class UserPublic(BaseModel):
    id: uuid_pkg.UUID
    email: str
    username: str
    is_active: bool
    created_at: datetime
    uuid: uuid_pkg.UUID

    class Config:
        orm_mode = True


class UserLoginRequest(BaseModel):
    email: str  # Can be email or username for login
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int


class TokenData(BaseModel):
    user_id: uuid_pkg.UUID
    email: str
    username: str


class ErrorResponse(BaseModel):
    detail: str
    error_code: str
    timestamp: datetime
    request_id: str


class UserRegistrationResponse(BaseModel):
    id: uuid_pkg.UUID
    email: str
    username: str
    is_active: bool
    created_at: datetime
    uuid: uuid_pkg.UUID
    access_token: str
    token_type: str = "bearer"
    expires_in: int