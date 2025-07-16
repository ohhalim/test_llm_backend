"""게시글 관련 테스트"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database.config import get_db, Base

# 테스트용 인메모리 SQLite 데이터베이스
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def auth_headers(client):
    """인증된 사용자의 헤더 반환"""
    # 사용자 등록
    response = client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_create_post(client, auth_headers):
    """게시글 작성 테스트"""
    response = client.post(
        "/posts",
        json={
            "title": "테스트 게시글",
            "content": "이것은 테스트 게시글의 내용입니다."
        },
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "테스트 게시글"
    assert data["content"] == "이것은 테스트 게시글의 내용입니다."

def test_create_post_unauthorized(client):
    """인증 없이 게시글 작성 테스트"""
    response = client.post(
        "/posts",
        json={
            "title": "테스트 게시글",
            "content": "이것은 테스트 게시글의 내용입니다."
        }
    )
    assert response.status_code == 401

def test_get_posts(client, auth_headers):
    """게시글 목록 조회 테스트"""
    # 게시글 작성
    client.post(
        "/posts",
        json={
            "title": "첫 번째 게시글",
            "content": "첫 번째 게시글 내용"
        },
        headers=auth_headers
    )
    
    # 게시글 목록 조회
    response = client.get("/posts")
    assert response.status_code == 200
    data = response.json()
    assert "posts" in data
    assert data["total"] >= 1

def test_get_post_detail(client, auth_headers):
    """게시글 상세 조회 테스트"""
    # 게시글 작성
    create_response = client.post(
        "/posts",
        json={
            "title": "상세 조회 테스트",
            "content": "상세 조회 테스트 내용"
        },
        headers=auth_headers
    )
    post_id = create_response.json()["id"]
    
    # 게시글 상세 조회
    response = client.get(f"/posts/{post_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "상세 조회 테스트"

def test_update_post(client, auth_headers):
    """게시글 수정 테스트"""
    # 게시글 작성
    create_response = client.post(
        "/posts",
        json={
            "title": "수정 전 제목",
            "content": "수정 전 내용"
        },
        headers=auth_headers
    )
    post_id = create_response.json()["id"]
    
    # 게시글 수정
    response = client.put(
        f"/posts/{post_id}",
        json={
            "title": "수정 후 제목",
            "content": "수정 후 내용"
        },
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "수정 후 제목"

def test_delete_post(client, auth_headers):
    """게시글 삭제 테스트"""
    # 게시글 작성
    create_response = client.post(
        "/posts",
        json={
            "title": "삭제할 게시글",
            "content": "삭제할 게시글 내용"
        },
        headers=auth_headers
    )
    post_id = create_response.json()["id"]
    
    # 게시글 삭제
    response = client.delete(f"/posts/{post_id}", headers=auth_headers)
    assert response.status_code == 204
    
    # 삭제된 게시글 조회 시도
    response = client.get(f"/posts/{post_id}")
    assert response.status_code == 404