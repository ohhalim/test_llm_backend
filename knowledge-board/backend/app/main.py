from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .database.config import engine
from .models import User, Post
from .routers import auth_router, posts_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 시작/종료 시 실행되는 이벤트 핸들러"""
    # 데이터베이스 테이블 생성
    User.metadata.create_all(bind=engine)
    Post.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title="AI 기반 지식 공유 게시판",
    description="LangGraph와 RAG를 활용한 지식 공유 플랫폼",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React 개발 서버
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(auth_router)
app.include_router(posts_router)

@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {"message": "AI 기반 지식 공유 게시판 API에 오신 것을 환영합니다!"}

@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {"status": "healthy"}