from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional
from .user import UserResponse

class PostBase(BaseModel):
    """게시글 기본 스키마"""
    title: str = Field(..., min_length=1, max_length=200, description="게시글 제목 (1-200자)")
    content: str = Field(..., min_length=10, max_length=10000, description="게시글 내용 (10-10000자)")
    
    @validator('title')
    def validate_title(cls, v):
        """제목 검증: 공백 제거 및 특수문자 체크"""
        v = v.strip()
        if not v:
            raise ValueError('제목을 입력해주세요')
        return v
    
    @validator('content')
    def validate_content(cls, v):
        """내용 검증: 공백 제거"""
        v = v.strip()
        if not v:
            raise ValueError('내용을 입력해주세요')
        return v

class PostCreate(PostBase):
    """게시글 생성 스키마"""
    pass

class PostUpdate(BaseModel):
    """게시글 수정 스키마"""
    title: Optional[str] = None
    content: Optional[str] = None

class PostResponse(PostBase):
    """게시글 응답 스키마"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    author: UserResponse
    
    class Config:
        from_attributes = True

class PostListResponse(BaseModel):
    """게시글 목록 응답 스키마"""
    posts: list[PostResponse]
    total: int
    page: int
    size: int
    total_pages: int