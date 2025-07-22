-- PostgreSQL 초기화 스크립트
-- knowledge_user 생성 및 권한 부여

-- knowledge_user 생성
CREATE USER knowledge_user WITH PASSWORD 'secure_test_password';

-- knowledge_user에게 모든 권한 부여
ALTER USER knowledge_user CREATEDB;
ALTER USER knowledge_user WITH SUPERUSER;

-- knowledge_board 데이터베이스에 대한 권한 부여
GRANT ALL PRIVILEGES ON DATABASE knowledge_board TO knowledge_user;

-- 확인용 쿼리
\du