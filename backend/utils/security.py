from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlmodel import Session
from models.user import User
from schemas.user import TokenData
import os
import uuid as uuid_pkg
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "supersecretkeyforjwttokensthatchangestemporarilyfordebugging")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)

def authenticate_user(session: Session, email_or_username: str, password: str) -> Optional[User]:
    """Authenticate a user by email/username and password."""
    # Try to find user by email first, then by username
    user = session.query(User).filter(User.email == email_or_username).first()
    if not user:
        user = session.query(User).filter(User.username == email_or_username).first()

    if not user or not verify_password(password, user.hashed_password):
        return None

    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "iat": datetime.utcnow()})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[TokenData]:
    """Verify a JWT token and return the token data."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        email: str = payload.get("email")
        username: str = payload.get("username")

        if user_id is None or email is None or username is None:
            return None

        token_data = TokenData(user_id=uuid_pkg.UUID(user_id), email=email, username=username)
        return token_data
    except JWTError:
        return None

def get_current_user_from_token(token: str) -> Optional[TokenData]:
    """Extract user information from a token."""
    return verify_token(token)

def get_current_user_id(token: str = Depends(oauth2_scheme)) -> uuid_pkg.UUID:
    """FastAPI dependency to get the current logged-in user's ID from the JWT token."""
    token_data = verify_token(token)

    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    return token_data.user_id


def create_refresh_token(data: dict):
    return create_access_token(data)


def hash_and_verify_password_pair(password: str, hashed_password: str):
    return verify_password(password, hashed_password)
