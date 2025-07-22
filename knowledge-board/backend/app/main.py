from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .database.config import engine
from .models import User, Post
from .routers import auth_router, posts_router
from .utils.logger import setup_logger

# 로거 설정
logger = setup_logger("knowledge_board_api")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 시작/종료 시 실행되는 이벤트 핸들러"""
    logger.info("애플리케이션 시작 중...")
    try:
        # 데이터베이스 테이블 생성
        User.metadata.create_all(bind=engine)
        Post.metadata.create_all(bind=engine)
        logger.info("데이터베이스 테이블 생성 완료")
        yield
    except Exception as e:
        logger.error(f"애플리케이션 시작 중 오류 발생: {e}")
        raise
    finally:
        logger.info("애플리케이션 종료")

app = FastAPI(
    title="AI 기반 지식 공유 게시판",
    description="LangGraph와 RAG를 활용한 지식 공유 플랫폼",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 설정 (개발/운영 환경 대응)
import os
cors_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000", 
    "http://localhost:3001",  # 추가 개발 포트
    "http://127.0.0.1:3001"
]

# 환경변수에서 추가 허용 origin 읽기
env_origins = os.getenv("CORS_ORIGINS", "").split(",")
if env_origins and env_origins[0]:  # 빈 문자열 체크
    cors_origins.extend([origin.strip() for origin in env_origins])

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
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