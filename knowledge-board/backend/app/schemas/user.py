from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
from typing import Optional
import re

class UserBase(BaseModel):
    """사용자 기본 스키마"""
    username: str = Field(..., min_length=3, max_length=20, description="사용자명 (3-20자)")
    email: EmailStr = Field(..., description="이메일 주소")
    
    @validator('username')
    def validate_username(cls, v):
        """사용자명 검증: 영문, 숫자, 언더스코어만 허용"""
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('사용자명은 영문, 숫자, 언더스코어만 사용 가능합니다')
        return v

class UserCreate(UserBase):
    """사용자 생성 스키마"""
    password: str = Field(..., min_length=8, max_length=100, description="비밀번호 (8자 이상)")
    
    @validator('password')
    def validate_password(cls, v):
        """비밀번호 강도 검증"""
        if len(v) < 8:
            raise ValueError('비밀번호는 최소 8자 이상이어야 합니다')
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('비밀번호에 영문자가 포함되어야 합니다')
        if not re.search(r'\d', v):
            raise ValueError('비밀번호에 숫자가 포함되어야 합니다')
        return v

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