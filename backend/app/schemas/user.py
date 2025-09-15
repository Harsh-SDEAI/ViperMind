from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from uuid import UUID
from app.models.user import UserLevel

class UserBase(BaseModel):
    email: EmailStr
    username: str
    current_level: UserLevel = UserLevel.BEGINNER

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    current_level: Optional[UserLevel] = None
    is_active: Optional[bool] = None

class UserInDBBase(UserBase):
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class User(UserInDBBase):
    pass

class UserInDB(UserInDBBase):
    password_hash: str