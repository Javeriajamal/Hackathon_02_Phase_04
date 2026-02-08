from sqlmodel import select, Session
from models.user import User, UserCreate
from passlib.context import CryptContext
from typing import Optional
import uuid

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_user_by_email(session: Session, email: str) -> Optional[User]:
    """Get a user by email"""
    statement = select(User).where(User.email == email)
    result = session.execute(statement)
    return result.scalar_one_or_none()


def get_user_by_id(session: Session, user_id: uuid.UUID) -> Optional[User]:
    """Get a user by ID"""
    statement = select(User).where(User.id == user_id)
    result = session.execute(statement)
    return result.scalar_one_or_none()


def create_user(session: Session, user_create: UserCreate) -> User:
    """Create a new user"""
    # Hash the password
    hashed_password = pwd_context.hash(user_create.password)

    # Create user object
    user = User(
        email=user_create.email,
        full_name=user_create.full_name,
        password_hash=hashed_password
    )

    # Add to session and commit
    session.add(user)
    session.commit()
    session.refresh(user)

    return user


def update_user(session: Session, user_id: uuid.UUID, user_update) -> Optional[User]:
    """Update a user"""
    user = session.get(User, user_id)
    if not user:
        return None

    # Update fields
    update_data = user_update.dict(exclude_unset=True)
    if "password" in update_data:
        update_data["password_hash"] = pwd_context.hash(update_data.pop("password"))

    for field, value in update_data.items():
        setattr(user, field, value)

    session.add(user)
    session.commit()
    session.refresh(user)

    return user


def verify_user_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a user's password"""
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(session: Session, email: str, password: str) -> Optional[User]:
    """Authenticate a user by email and password"""
    user = get_user_by_email(session, email)
    if not user or not verify_user_password(password, user.password_hash):
        return None
    return user