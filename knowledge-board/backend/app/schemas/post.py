from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from .user import UserResponse

class PostBase(BaseModel):
    """게시글 기본 스키마"""
    title: str
    content: str

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