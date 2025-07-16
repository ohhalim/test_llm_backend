# AI 기반 지식 공유 게시판 시스템

LangGraph와 RAG 기술을 활용한 지능적인 지식 공유 플랫폼입니다. 사용자가 작성한 과거 게시글을 기반으로 AI가 관련 질문에 답변을 제공합니다.

## 🚀 주요 기능

- **게시글 CRUD**: 사용자 인증 기반 게시글 작성, 수정, 삭제
- **AI 어시스턴트**: LangGraph를 사용한 지능적인 질의응답
- **RAG 시스템**: ChromaDB 기반 벡터 검색으로 관련 게시글 찾기
- **사용자 인증**: JWT 기반 회원가입/로그인
- **페이지네이션**: 효율적인 게시글 목록 조회

## 🛠 기술 스택

### Backend
- **FastAPI**: 고성능 웹 API 프레임워크
- **PostgreSQL**: 관계형 데이터베이스
- **SQLAlchemy**: ORM
- **Alembic**: 데이터베이스 마이그레이션
- **JWT**: 사용자 인증

### Frontend
- **React**: 사용자 인터페이스
- **React Router**: 클라이언트 사이드 라우팅
- **Tailwind CSS**: 스타일링
- **Axios**: HTTP 클라이언트
- **Context API**: 상태 관리

### AI & Vector Database
- **LangGraph**: AI 에이전트 워크플로우
- **Google Gemini**: 언어 모델
- **ChromaDB**: 벡터 데이터베이스
- **Sentence Transformers**: 텍스트 임베딩

### DevOps
- **Docker & Docker Compose**: 컨테이너화
- **환경 변수**: 설정 관리

## 📁 프로젝트 구조

```
knowledge-board/
├── backend/                    # FastAPI 백엔드
│   ├── app/
│   │   ├── main.py            # FastAPI 애플리케이션
│   │   ├── models/            # SQLAlchemy 모델
│   │   ├── schemas/           # Pydantic 스키마
│   │   ├── routers/           # API 라우터
│   │   ├── services/          # 비즈니스 로직
│   │   ├── database/          # 데이터베이스 설정
│   │   └── auth/              # 인증 시스템
│   ├── alembic/               # 데이터베이스 마이그레이션
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                   # React 프론트엔드
│   ├── src/
│   │   ├── components/        # React 컴포넌트
│   │   ├── pages/             # 페이지 컴포넌트
│   │   ├── services/          # API 서비스
│   │   └── contexts/          # React Context
│   ├── package.json
│   └── Dockerfile.dev
├── ai-agent/                   # AI 에이전트
│   ├── agent/
│   │   ├── graph.py           # LangGraph 구현
│   │   ├── tools.py           # AI 도구들
│   │   └── prompts.py         # 프롬프트 템플릿
│   ├── main.py                # FastAPI AI 서비스
│   ├── requirements.txt
│   └── Dockerfile
├── docker-compose.yml          # 서비스 오케스트레이션
├── .env.example               # 환경 변수 예시
└── README.md
```

## 🔧 설치 및 실행

### 1. 필수 요구사항

- Docker & Docker Compose
- Google Gemini API 키

### 2. 환경 설정

```bash
# 저장소 클론
git clone <repository-url>
cd knowledge-board

# 환경 변수 설정
cp .env.example .env
# .env 파일에서 GEMINI_API_KEY 설정
```

### 3. Docker Compose로 실행

```bash
# 모든 서비스 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f
```

### 4. 개별 서비스 실행 (개발 모드)

#### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

#### Frontend
```bash
cd frontend
npm install
npm start
```

#### AI Agent
```bash
cd ai-agent
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```

## 🌐 서비스 접속

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8080
- **AI Agent API**: http://localhost:8081
- **API 문서**: http://localhost:8080/docs

## 📚 API 문서

### Backend API 엔드포인트

#### 인증
- `POST /auth/register` - 회원가입
- `POST /auth/login` - 로그인

#### 게시글
- `GET /posts` - 게시글 목록 (페이지네이션)
- `POST /posts` - 게시글 작성 (인증 필요)
- `GET /posts/{id}` - 게시글 상세 조회
- `PUT /posts/{id}` - 게시글 수정 (작성자만)
- `DELETE /posts/{id}` - 게시글 삭제 (작성자만)

### AI Agent API 엔드포인트

#### AI 기능
- `POST /ai/chat` - AI 질의응답
- `GET /ai/summary/{user_id}` - 사용자 게시글 요약
- `POST /ai/embed-post` - 게시글 벡터화
- `DELETE /ai/embed-post/{post_id}` - 벡터 데이터 삭제
- `GET /ai/search` - 벡터 검색

## 🤖 LangGraph AI 에이전트 구조

### 상태 관리 (AgentState)
```python
@dataclass
class AgentState:
    user_id: int = None           # 사용자 ID
    query: str = ""               # 사용자 질문
    expanded_query: str = ""      # 확장된 검색 쿼리
    context: List[Dict] = None    # 검색된 관련 게시글
    answer: str = ""              # AI 생성 답변
    error: str = ""               # 오류 메시지
    metadata: Dict = None         # 추가 메타데이터
```

### 노드 구조
1. **expand_query_node**: 검색 쿼리 확장 및 최적화
2. **retrieve_posts_node**: 벡터 검색으로 관련 게시글 찾기
3. **generate_answer_node**: Gemini API로 답변 생성
4. **save_interaction_node**: 상호작용 기록 저장

### 워크플로우
```
사용자 질문 → 쿼리 확장 → 관련 게시글 검색 → AI 답변 생성 → 기록 저장
```

## 🔐 환경 변수 설정

```env
# 데이터베이스
DATABASE_URL=postgresql://user:password@localhost:5432/knowledge_board

# JWT 인증
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI 설정
GEMINI_API_KEY=your-gemini-api-key

# ChromaDB
CHROMA_HOST=localhost
CHROMA_PORT=8000

# 서비스 포트
BACKEND_PORT=8080
AI_AGENT_PORT=8081
FRONTEND_PORT=3000
```

## 🧪 테스트

```bash
# Backend 테스트
cd backend
pytest

# Frontend 테스트
cd frontend
npm test
```

## 📈 사용 시나리오

1. **회원가입/로그인**: 사용자가 계정을 생성하고 로그인
2. **게시글 작성**: 지식, 경험, 정보를 게시글로 공유
3. **AI 질의응답**: 과거 게시글을 기반으로 AI에게 질문
4. **지식 탐색**: 다른 사용자의 게시글 탐색 및 학습

## 🚀 배포

### 프로덕션 배포
```bash
# 프로덕션 빌드
docker-compose -f docker-compose.prod.yml up -d
```

### 환경별 설정
- **개발**: `.env.development`
- **스테이징**: `.env.staging`  
- **프로덕션**: `.env.production`

## 🤝 기여

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 🔮 향후 계획

- [ ] 실시간 채팅 기능
- [ ] 게시글 태그 시스템
- [ ] 고급 검색 필터
- [ ] 사용자 프로필 페이지
- [ ] 게시글 좋아요/북마크
- [ ] 다국어 지원
- [ ] 모바일 앱 개발

## 📞 지원

문제가 발생하거나 질문이 있으시면 이슈를 생성해주세요.

---

**Made with ❤️ using LangGraph, FastAPI, React, and ChromaDB**