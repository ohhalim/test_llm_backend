"""로깅 설정 모듈"""

import logging
import sys
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

def setup_logger(name: str = "knowledge_board", level: str = None) -> logging.Logger:
    """애플리케이션 로거 설정"""
    
    # 로그 레벨 설정
    log_level = level or os.getenv("LOG_LEVEL", "INFO")
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # 로거 생성
    logger = logging.getLogger(name)
    logger.setLevel(numeric_level)
    
    # 중복 핸들러 방지
    if logger.handlers:
        return logger
    
    # 로그 포맷 설정
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 콘솔 핸들러
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 파일 핸들러 (프로덕션에서만)
    if not os.getenv("DEBUG", "False").lower() == "true":
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f"{name}.log"
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

# 기본 로거 인스턴스
logger = setup_logger()

def log_request(endpoint: str, method: str, user_id: int = None, ip: str = None):
    """API 요청 로깅"""
    logger.info(f"API Request - {method} {endpoint} - User: {user_id} - IP: {ip}")

def log_error(error: Exception, context: str = "", user_id: int = None):
    """에러 로깅"""
    logger.error(f"Error in {context} - User: {user_id} - {type(error).__name__}: {str(error)}")

def log_security_event(event: str, user_id: int = None, ip: str = None, details: str = ""):
    """보안 이벤트 로깅"""
    logger.warning(f"Security Event: {event} - User: {user_id} - IP: {ip} - {details}")