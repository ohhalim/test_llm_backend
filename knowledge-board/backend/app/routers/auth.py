from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from datetime import timedelta

from ..database.config import get_db
from ..models.user import User
from ..schemas.user import UserCreate, UserLogin, Token, UserResponse
from ..auth.security import (
    get_password_hash, 
    authenticate_user, 
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, response: Response, db: Session = Depends(get_db)):
    """사용자 회원가입"""
    # 사용자명 중복 확인
    existing_user = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.email)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )
    
    # 새 사용자 생성
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hashed_password
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # 토큰 생성 및 보안 쿠키 설정
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": new_user.username}, 
        expires_delta=access_token_expires
    )
    
    # httpOnly 쿠키로 JWT 토큰 설정 (XSS 공격 방지)
    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,  # JavaScript에서 접근 불가
        secure=True,    # HTTPS에서만 전송
        samesite="lax"  # CSRF 공격 방지
    )
    
    return {
        "access_token": access_token,  # 호환성을 위해 일시적으로 유지
        "token_type": "bearer",
        "user": UserResponse.from_orm(new_user)
    }

@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin, response: Response, db: Session = Depends(get_db)):
    """사용자 로그인"""
    user = authenticate_user(db, user_credentials.username, user_credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 토큰 생성 및 보안 쿠키 설정
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, 
        expires_delta=access_token_expires
    )
    
    # httpOnly 쿠키로 JWT 토큰 설정 (XSS 공격 방지)
    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,  # JavaScript에서 접근 불가
        secure=True,    # HTTPS에서만 전송
        samesite="lax"  # CSRF 공격 방지
    )
    
    return {
        "access_token": access_token,  # 호환성을 위해 일시적으로 유지
        "token_type": "bearer",
        "user": UserResponse.from_orm(user)
    }