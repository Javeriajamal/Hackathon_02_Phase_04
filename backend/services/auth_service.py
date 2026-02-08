from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr
from sqlmodel import Session, select
from models.user import User
from utils.security import get_password_hash, create_access_token
import uuid

router = APIRouter(prefix="/auth", tags=["auth"])

# Request model
class RegisterRequest(BaseModel):
    email: EmailStr
    username: str
    password: str

# Response model
class RegisterResponse(BaseModel):
    id: str
    email: EmailStr
    username: str
    is_active: bool
    access_token: str

from database import get_session

@router.post("/register", response_model=RegisterResponse)
def register_user(
    data: RegisterRequest,
    session: Session = Depends(get_session)
):
    # Check if email or username already exists
    stmt = select(User).where((User.email == data.email) | (User.username == data.username))
    result = session.execute(stmt)
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email or username already registered")

    # Hash password
    hashed_password = get_password_hash(data.password)

    # Create user
    new_user = User(
        id=uuid.uuid4(),
        email=data.email,
        username=data.username,
        hashed_password=hashed_password,
        is_active=True
    )

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    # Create JWT token
    access_token = create_access_token({"sub": str(new_user.id), "email": new_user.email, "username": new_user.username})

    return RegisterResponse(
        id=str(new_user.id),
        email=new_user.email,
        username=new_user.username,
        is_active=new_user.is_active,
        access_token=access_token
    )
