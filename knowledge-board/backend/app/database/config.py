from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL 환경변수가 설정되지 않았습니다!")

# 데이터베이스 엔진 설정 (커넥션 풀링 및 성능 최적화)
engine = create_engine(
    DATABASE_URL,
    pool_size=5,          # 커넥션 풀 크기
    max_overflow=10,      # 최대 추가 커넥션
    pool_timeout=30,      # 커넥션 대기 시간
    pool_recycle=3600,    # 커넥션 재사용 시간 (1시간)
    echo=os.getenv("DEBUG", "False").lower() == "true"  # SQL 로그 출력
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """데이터베이스 세션을 제공하는 의존성 함수"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()