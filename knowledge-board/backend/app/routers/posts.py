from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from typing import Optional
import math

from ..database.config import get_db
from ..models.user import User
from ..models.post import Post
from ..schemas.post import PostCreate, PostUpdate, PostResponse, PostListResponse
from ..auth.security import get_current_user

router = APIRouter(prefix="/posts", tags=["Posts"])

@router.get("", response_model=PostListResponse)
async def get_posts(
    page: int = Query(1, ge=1, description="페이지 번호"),
    size: int = Query(10, ge=1, le=100, description="페이지 크기"),
    db: Session = Depends(get_db)
):
    """게시글 목록 조회 (페이지네이션 포함)"""
    # 전체 게시글 수 계산
    total = db.query(Post).count()
    
    # 페이지네이션 적용 (N+1 문제 해결: 작성자 정보 eager loading)
    offset = (page - 1) * size
    posts = db.query(Post)\
        .options(joinedload(Post.author))\
        .order_by(desc(Post.created_at))\
        .offset(offset)\
        .limit(size)\
        .all()
    
    total_pages = math.ceil(total / size)
    
    return PostListResponse(
        posts=[PostResponse.from_orm(post) for post in posts],
        total=total,
        page=page,
        size=size,
        total_pages=total_pages
    )

@router.post("", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    post_data: PostCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """새 게시글 작성 (인증 필요)"""
    new_post = Post(
        title=post_data.title,
        content=post_data.content,
        user_id=current_user.id
    )
    
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    
    return PostResponse.from_orm(new_post)

@router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: int, db: Session = Depends(get_db)):
    """특정 게시글 조회"""
    post = db.query(Post)\
        .options(joinedload(Post.author))\
        .filter(Post.id == post_id)\
        .first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    return PostResponse.from_orm(post)

@router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: int,
    post_data: PostUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """게시글 수정 (작성자만 가능)"""
    post = db.query(Post).filter(Post.id == post_id).first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    # 작성자 확인
    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this post"
        )
    
    # 업데이트할 필드만 수정
    update_data = post_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(post, field, value)
    
    db.commit()
    db.refresh(post)
    
    return PostResponse.from_orm(post)

@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """게시글 삭제 (작성자만 가능)"""
    post = db.query(Post).filter(Post.id == post_id).first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    # 작성자 확인
    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this post"
        )
    
    db.delete(post)
    db.commit()
    
    return None