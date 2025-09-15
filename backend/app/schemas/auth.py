from pydantic import BaseModel, EmailStr
from typing import Optional
from app.models.user import UserLevel
from app.schemas.user import User

class UserLogin(BaseModel):
    email_or_username: str
    password: str

class UserRegister(BaseModel):
    email: EmailStr
    username: str
    password: str
    current_level: UserLevel = UserLevel.BEGINNER

class Token(BaseModel):
    access_token: str
    token_type: str
    user: User

class TokenData(BaseModel):
    user_id: Optional[str] = None