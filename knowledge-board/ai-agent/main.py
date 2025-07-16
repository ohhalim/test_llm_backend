"""AI 에이전트 서비스 메인 파일"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uvicorn
import os
from dotenv import load_dotenv

from agent import knowledge_agent, vector_tools

load_dotenv()

app = FastAPI(
    title="Knowledge Board AI Agent",
    description="LangGraph 기반 지식 공유 게시판 AI 에이전트",
    version="1.0.0"
)

# CORS 미들웨어 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React 앱의 URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 요청/응답 스키마
class ChatRequest(BaseModel):
    """AI 채팅 요청 스키마"""
    query: str
    user_id: Optional[int] = None

class ChatResponse(BaseModel):
    """AI 채팅 응답 스키마"""
    answer: str
    context: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    error: Optional[str] = None

class SummaryResponse(BaseModel):
    """요약 응답 스키마"""
    summary: str
    user_id: int

class PostEmbeddingRequest(BaseModel):
    """게시글 임베딩 요청 스키마"""
    post_id: int
    title: str
    content: str
    user_id: int
    metadata: Optional[Dict[str, Any]] = None

class MedicalSearchRequest(BaseModel):
    """의료 지식 검색 요청 스키마"""
    query: str
    limit: Optional[int] = 5

class MedicalSearchResponse(BaseModel):
    """의료 지식 검색 응답 스키마"""
    query: str
    results: List[Dict[str, Any]]
    count: int

# AI 에이전트 엔드포인트
@app.post("/ai/chat", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest):
    """사용자 질문에 대한 AI 답변 생성"""
    try:
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="질문을 입력해주세요.")
        
        # AI 에이전트 실행
        result = await knowledge_agent.chat(
            query=request.query,
            user_id=request.user_id
        )
        
        return ChatResponse(
            answer=result["answer"],
            context=result["context"],
            metadata=result["metadata"],
            error=result.get("error")
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"AI 처리 중 오류가 발생했습니다: {str(e)}"
        )

@app.get("/ai/summary/{user_id}", response_model=SummaryResponse)
async def get_user_summary(user_id: int):
    """사용자 게시글 요약 생성"""
    try:
        if user_id <= 0:
            raise HTTPException(status_code=400, detail="유효하지 않은 사용자 ID입니다.")
        
        # 요약 생성
        summary = await knowledge_agent.generate_summary(user_id)
        
        return SummaryResponse(
            summary=summary,
            user_id=user_id
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"요약 생성 중 오류가 발생했습니다: {str(e)}"
        )

# 벡터 데이터베이스 관리 엔드포인트
@app.post("/ai/embed-post")
async def embed_post(request: PostEmbeddingRequest):
    """게시글을 벡터 데이터베이스에 추가"""
    try:
        success = vector_tools.add_post_to_vector_store(
            post_id=request.post_id,
            title=request.title,
            content=request.content,
            user_id=request.user_id,
            metadata=request.metadata
        )
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="게시글 임베딩에 실패했습니다."
            )
        
        return {"message": "게시글이 성공적으로 임베딩되었습니다.", "post_id": request.post_id}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"임베딩 처리 중 오류가 발생했습니다: {str(e)}"
        )

@app.delete("/ai/embed-post/{post_id}")
async def remove_post_embedding(post_id: int):
    """벡터 데이터베이스에서 게시글 제거"""
    try:
        success = vector_tools.delete_post_from_vector_store(post_id)
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="게시글 임베딩 삭제에 실패했습니다."
            )
        
        return {"message": "게시글 임베딩이 성공적으로 삭제되었습니다.", "post_id": post_id}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"임베딩 삭제 중 오류가 발생했습니다: {str(e)}"
        )

@app.get("/ai/search")
async def search_posts(query: str, user_id: Optional[int] = None, limit: int = 5):
    """벡터 검색을 통한 게시글 찾기"""
    try:
        if not query.strip():
            raise HTTPException(status_code=400, detail="검색어를 입력해주세요.")
        
        results = vector_tools.search_similar_posts(
            query=query,
            user_id=user_id,
            limit=limit
        )
        
        return {
            "query": query,
            "results": results,
            "count": len(results)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"검색 중 오류가 발생했습니다: {str(e)}"
        )

@app.post("/ai/search-medical", response_model=MedicalSearchResponse)
async def search_medical_knowledge(request: MedicalSearchRequest):
    """의료 지식 검색"""
    try:
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="검색어를 입력해주세요.")
        
        results = vector_tools.search_medical_knowledge(
            query=request.query,
            limit=request.limit
        )
        
        return MedicalSearchResponse(
            query=request.query,
            results=results,
            count=len(results)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"의료 지식 검색 중 오류가 발생했습니다: {str(e)}"
        )

@app.get("/ai/medical-stats")
async def get_medical_knowledge_stats():
    """의료 지식 데이터베이스 통계"""
    try:
        stats = vector_tools.get_medical_knowledge_stats()
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"통계 조회 중 오류가 발생했습니다: {str(e)}"
        )

# 헬스 체크 엔드포인트
@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {"message": "Knowledge Board AI Agent is running!"}

@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {"status": "healthy", "service": "ai-agent"}

if __name__ == "__main__":
    port = int(os.getenv("AI_AGENT_PORT", "8001"))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )