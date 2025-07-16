"""AI 에이전트에서 사용할 도구들"""

import chromadb
from typing import List, Dict, Any
import httpx
import os
from dotenv import load_dotenv
import json

load_dotenv()

class VectorStoreTools:
    """벡터 데이터베이스 관련 도구들"""
    
    def __init__(self):
        # ChromaDB 클라이언트 초기화
        chroma_host = os.getenv("CHROMA_HOST", "localhost")
        chroma_port = int(os.getenv("CHROMA_PORT", "8000"))
        
        try:
            self.client = chromadb.HttpClient(
                host=chroma_host,
                port=chroma_port,
                settings=chromadb.Settings(anonymized_telemetry=False)
            )
            
            # 일반 게시글 컬렉션 생성 또는 가져오기
            try:
                self.collection = self.client.create_collection(
                    name="knowledge_posts",
                    metadata={"description": "Knowledge board posts collection"}
                )
            except Exception:
                # 컬렉션이 이미 존재하는 경우
                self.collection = self.client.get_collection("knowledge_posts")
            
            # 의료 지식 컬렉션 생성 또는 가져오기
            try:
                self.medical_collection = self.client.create_collection(
                    name="medical_knowledge",
                    metadata={"description": "Korean medical knowledge database"}
                )
            except Exception:
                # 컬렉션이 이미 존재하는 경우
                self.medical_collection = self.client.get_collection("medical_knowledge")
                
        except Exception as e:
            print(f"ChromaDB connection error: {e}")
            self.client = None
            self.collection = None
            self.medical_collection = None
    
    def add_post_to_vector_store(self, post_id: int, title: str, content: str, user_id: int, metadata: Dict[str, Any] = None):
        """게시글을 벡터 스토어에 추가"""
        if not self.collection:
            return False
        try:
            # 게시글 전체 텍스트 결합
            full_text = f"{title}\n\n{content}"
            
            # 메타데이터 준비
            post_metadata = {
                "post_id": post_id,
                "user_id": user_id,
                "title": title,
                "type": "post"
            }
            if metadata:
                post_metadata.update(metadata)
            
            # 벡터 스토어에 추가
            self.collection.add(
                documents=[full_text],
                metadatas=[post_metadata],
                ids=[f"post_{post_id}"]
            )
            
            return True
        except Exception as e:
            print(f"Error adding post to vector store: {e}")
            return False
    
    def search_similar_posts(self, query: str, user_id: int = None, limit: int = 5) -> List[Dict[str, Any]]:
        """유사한 게시글 검색"""
        if not self.collection:
            return []
        try:
            # 검색 조건 설정
            where_filter = {"type": "post"}
            if user_id:
                where_filter["user_id"] = user_id
            
            # 유사도 검색 실행
            results = self.collection.query(
                query_texts=[query],
                n_results=limit,
                where=where_filter
            )
            
            # 결과 포맷팅
            similar_posts = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    metadata = results['metadatas'][0][i]
                    distance = results['distances'][0][i] if results['distances'] else None
                    
                    similar_posts.append({
                        "content": doc,
                        "metadata": metadata,
                        "similarity_score": 1 - distance if distance else None
                    })
            
            return similar_posts
        except Exception as e:
            print(f"Error searching similar posts: {e}")
            return []
    
    def delete_post_from_vector_store(self, post_id: int):
        """벡터 스토어에서 게시글 삭제"""
        if not self.collection:
            return False
        try:
            self.collection.delete(ids=[f"post_{post_id}"])
            return True
        except Exception as e:
            print(f"Error deleting post from vector store: {e}")
            return False
    
    def search_medical_knowledge(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """의료 지식 검색"""
        if not self.medical_collection:
            return []
        try:
            # 의료 지식 검색 실행
            results = self.medical_collection.query(
                query_texts=[query],
                n_results=limit,
                include=["documents", "metadatas", "distances"]
            )
            
            # 결과 포맷팅
            medical_results = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    metadata = results['metadatas'][0][i]
                    distance = results['distances'][0][i] if results['distances'] else None
                    
                    medical_results.append({
                        "content": doc,
                        "metadata": metadata,
                        "similarity_score": 1 - distance if distance else None
                    })
            
            return medical_results
        except Exception as e:
            print(f"Error searching medical knowledge: {e}")
            return []
    
    def get_medical_knowledge_stats(self) -> Dict[str, Any]:
        """의료 지식 데이터베이스 통계 정보"""
        if not self.medical_collection:
            return {"total_documents": 0, "error": "Collection not available"}
        
        try:
            count = self.medical_collection.count()
            return {
                "total_documents": count,
                "collection_name": "medical_knowledge",
                "status": "active"
            }
        except Exception as e:
            return {"total_documents": 0, "error": str(e)}

class BackendAPITools:
    """백엔드 API 통신 도구들"""
    
    def __init__(self):
        self.backend_url = "http://localhost:8000"
        self.client = httpx.AsyncClient()
    
    async def get_user_posts(self, user_id: int, page: int = 1, size: int = 50) -> List[Dict[str, Any]]:
        """특정 사용자의 게시글 목록 가져오기"""
        try:
            # 사용자별 게시글 조회를 위한 엔드포인트 호출
            # 실제 구현에서는 백엔드에 사용자별 게시글 조회 API가 필요함
            response = await self.client.get(
                f"{self.backend_url}/posts",
                params={"page": page, "size": size}
            )
            
            if response.status_code == 200:
                data = response.json()
                # 특정 사용자의 게시글만 필터링
                user_posts = [post for post in data.get("posts", []) if post.get("user_id") == user_id]
                return user_posts
            else:
                print(f"Error fetching user posts: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"Error in get_user_posts: {e}")
            return []
    
    async def get_post_details(self, post_id: int) -> Dict[str, Any]:
        """특정 게시글의 상세 정보 가져오기"""
        try:
            response = await self.client.get(f"{self.backend_url}/posts/{post_id}")
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error fetching post details: {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"Error in get_post_details: {e}")
            return {}
    
    async def save_interaction(self, user_id: int, query: str, answer: str) -> bool:
        """사용자 상호작용 기록 저장 (향후 구현)"""
        try:
            # 향후 대화 기록 저장을 위한 엔드포인트
            # 현재는 로그만 출력
            print(f"Interaction saved - User: {user_id}, Query: {query[:50]}...")
            return True
            
        except Exception as e:
            print(f"Error saving interaction: {e}")
            return False
    
    async def close(self):
        """HTTP 클라이언트 종료"""
        await self.client.aclose()

# 도구 인스턴스들
vector_tools = VectorStoreTools()
api_tools = BackendAPITools()