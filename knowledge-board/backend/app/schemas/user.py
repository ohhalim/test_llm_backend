from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    """사용자 기본 스키마"""
    username: str
    email: EmailStr

class UserCreate(UserBase):
    """사용자 생성 스키마"""
    password: str

class UserResponse(UserBase):
    """사용자 응답 스키마"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    """사용자 로그인 스키마"""
    username: str
    password: str

class Token(BaseModel):
    """토큰 응답 스키마"""
    access_token: str
    token_type: str
    user: UserResponse