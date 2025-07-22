"""간단한 Gemini 기반 RAG 시스템"""

import os
import json
import asyncio
from typing import List, Dict, Any, Optional
from pathlib import Path
import numpy as np
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
import chromadb
from chromadb.config import Settings

class SimpleRAGSystem:
    """간단한 RAG 시스템 (Gemini 사용)"""
    
    def __init__(self, gemini_api_key: str):
        """RAG 시스템 초기화"""
        self.gemini_api_key = gemini_api_key
        
        # Gemini 설정
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        
        # 임베딩 모델 (로컬)
        self.embedding_model = SentenceTransformer('distiluse-base-multilingual-cased')
        
        # ChromaDB 클라이언트
        try:
            self.chroma_client = chromadb.HttpClient(
                host="localhost",
                port=8000,
                settings=Settings(allow_reset=True)
            )
            print("✅ ChromaDB 연결 성공")
        except Exception as e:
            print(f"⚠️ ChromaDB 연결 실패: {e}")
            self.chroma_client = None
        
        # 벡터 스토어 초기화
        self.collection = None
        self._initialize_collection()
    
    def _initialize_collection(self):
        """컬렉션 초기화"""
        if not self.chroma_client:
            return
        
        try:
            # 기존 컬렉션 확인
            try:
                self.collection = self.chroma_client.get_collection("medical_simple_rag")
                count = self.collection.count()
                if count > 0:
                    print(f"✅ 기존 의료 RAG 컬렉션 사용 ({count}개 문서)")
                    return
            except:
                pass
            
            # 새 컬렉션 생성
            print("🔄 새로운 의료 RAG 컬렉션 생성 중...")
            self.collection = self.chroma_client.create_collection("medical_simple_rag")
            
            # 의료 데이터 로드
            self._load_medical_data()
            
        except Exception as e:
            print(f"❌ 컬렉션 초기화 실패: {e}")
    
    def _load_medical_data(self):
        """의료 데이터 로드"""
        # 현재 프로젝트의 의료 데이터 경로
        data_paths = [
            "/Users/ohhalim/git_box/test_llm_backend/knowledge-board/ai-agent/09.필수의료 의학지식 데이터/3.개방데이터/1.데이터/Training/01.원천데이터/TS_국문_기타",
            "./09.필수의료 의학지식 데이터/3.개방데이터/1.데이터/Training/01.원천데이터/TS_국문_기타"
        ]
        
        data_path = None
        for path in data_paths:
            if os.path.exists(path):
                data_path = path
                break
        
        if not data_path:
            print("⚠️ 의료 데이터 경로를 찾을 수 없습니다")
            # 테스트용 샘플 데이터 추가
            self._add_sample_data()
            return
        
        print(f"📁 의료 데이터 로드 중: {data_path}")
        
        json_files = list(Path(data_path).glob("*.json"))
        processed_count = 0
        
        documents = []
        metadatas = []
        ids = []
        
        for json_file in json_files[:50]:  # 처음 50개만 로드
            try:
                with open(json_file, 'r', encoding='utf-8-sig') as f:
                    data = json.load(f)
                
                content = data.get('content', '').strip()
                if not content or len(content) < 50:
                    continue
                
                # 긴 텍스트는 분할
                chunks = self._split_text(content, max_length=500)
                
                for i, chunk in enumerate(chunks):
                    doc_id = f"{data.get('c_id', processed_count)}_{i}"
                    
                    documents.append(chunk)
                    metadatas.append({
                        "source": data.get("source_spec", "의료기관"),
                        "domain": str(data.get("domain", "")),
                        "type": "medical_procedure",
                        "c_id": data.get("c_id", "")
                    })
                    ids.append(doc_id)
                
                processed_count += 1
                if processed_count % 10 == 0:
                    print(f"📊 처리됨: {processed_count}개 파일")
                    
            except Exception as e:
                continue
        
        if documents:
            # 임베딩 생성
            print("🔄 임베딩 생성 중...")
            embeddings = self.embedding_model.encode(documents).tolist()
            
            # ChromaDB에 추가
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids,
                embeddings=embeddings
            )
            
            print(f"✅ {len(documents)}개 문서 청크 저장 완료")
    
    def _add_sample_data(self):
        """테스트용 샘플 데이터 추가"""
        print("📝 테스트용 샘플 의료 데이터 추가 중...")
        
        sample_data = [
            {
                "content": "흉막천자는 흉막강에 고인 액체나 공기를 제거하기 위해 바늘을 삽입하는 의료 시술입니다. 진단 목적과 치료 목적으로 시행됩니다.",
                "metadata": {"type": "medical_procedure", "domain": "호흡기내과", "source": "의료 지식 데이터베이스"}
            },
            {
                "content": "당뇨병 치료는 혈당 조절을 목표로 합니다. 식이요법, 운동요법, 약물치료를 병행하며, 인슐린 치료가 필요한 경우도 있습니다.",
                "metadata": {"type": "medical_treatment", "domain": "내분비내과", "source": "의료 지식 데이터베이스"}
            },
            {
                "content": "고혈압 치료에는 ACE 억제제, 베타 차단제, 칼슘 채널 차단제, 이뇨제 등의 약물이 사용됩니다. 생활습관 개선도 중요합니다.",
                "metadata": {"type": "medical_treatment", "domain": "순환기내과", "source": "의료 지식 데이터베이스"}
            }
        ]
        
        documents = []
        metadatas = []
        ids = []
        
        for i, item in enumerate(sample_data):
            documents.append(item["content"])
            metadatas.append(item["metadata"])
            ids.append(f"sample_{i}")
        
        # 임베딩 생성
        embeddings = self.embedding_model.encode(documents).tolist()
        
        # ChromaDB에 추가
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
            embeddings=embeddings
        )
        
        print(f"✅ {len(documents)}개 샘플 문서 추가 완료")
    
    def _split_text(self, text: str, max_length: int = 500) -> List[str]:
        """텍스트 분할"""
        if len(text) <= max_length:
            return [text]
        
        chunks = []
        sentences = text.split('.')
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk + sentence) <= max_length:
                current_chunk += sentence + "."
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + "."
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    async def similarity_search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """유사도 검색"""
        if not self.collection:
            return []
        
        try:
            # 쿼리 임베딩 생성
            query_embedding = self.embedding_model.encode([query]).tolist()[0]
            
            # 유사도 검색
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=limit
            )
            
            search_results = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    distance = results['distances'][0][i] if results['distances'] else 0
                    similarity_score = max(0, 1 - distance)  # 거리를 유사도로 변환
                    
                    search_results.append({
                        "content": doc,
                        "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                        "similarity_score": similarity_score,
                        "source": results['metadatas'][0][i].get('source', '') if results['metadatas'] else '',
                        "type": results['metadatas'][0][i].get('type', '') if results['metadatas'] else ''
                    })
            
            return search_results
            
        except Exception as e:
            print(f"❌ 검색 실패: {e}")
            return []
    
    async def search_and_answer(self, question: str, limit: int = 5) -> Dict[str, Any]:
        """RAG 기반 질의응답"""
        try:
            # 관련 문서 검색
            docs = await self.similarity_search(question, limit)
            
            if not docs:
                return {
                    "answer": "관련된 의료 지식을 찾을 수 없습니다.",
                    "source_documents": [],
                    "question": question,
                    "total_sources": 0
                }
            
            # 컨텍스트 구성
            context = "\n\n".join([f"[문서 {i+1}] {doc['content']}" for i, doc in enumerate(docs)])
            
            # 프롬프트 생성
            prompt = f"""당신은 의료 전문 AI 어시스턴트입니다. 
주어진 의료 지식을 바탕으로 정확하고 도움이 되는 답변을 제공해주세요.

의료 지식 컨텍스트:
{context}

질문: {question}

답변 지침:
1. 주어진 의료 지식만을 기반으로 답변하세요
2. 정확하지 않거나 불확실한 정보는 제공하지 마세요
3. 필요시 의료 전문가 상담을 권하세요
4. 한국어로 명확하고 이해하기 쉽게 답변하세요

답변:"""
            
            # Gemini로 답변 생성
            response = self.model.generate_content(prompt)
            answer = response.text if response.text else "답변을 생성할 수 없습니다."
            
            return {
                "answer": answer,
                "source_documents": docs,
                "question": question,
                "total_sources": len(docs)
            }
            
        except Exception as e:
            print(f"❌ 답변 생성 실패: {e}")
            return {
                "answer": f"답변 생성 중 오류가 발생했습니다: {str(e)}",
                "source_documents": [],
                "question": question,
                "total_sources": 0,
                "error": str(e)
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """시스템 통계"""
        try:
            if self.collection:
                count = self.collection.count()
                return {
                    "total_documents": count,
                    "status": "active",
                    "vector_store": "ChromaDB",
                    "embedding_model": "SentenceTransformer (multilingual)",
                    "llm_model": "gemini-pro",
                    "system_ready": True
                }
            else:
                return {
                    "total_documents": 0,
                    "status": "not_initialized",
                    "system_ready": False
                }
        except Exception as e:
            return {
                "error": str(e),
                "status": "error",
                "system_ready": False
            }
    
    def health_check(self) -> Dict[str, Any]:
        """시스템 헬스 체크"""
        health = {
            "chroma_db": False,
            "collection": False,
            "embedding_model": False,
            "llm_model": False,
            "overall": False
        }
        
        try:
            # ChromaDB 연결 확인
            if self.chroma_client:
                self.chroma_client.heartbeat()
                health["chroma_db"] = True
            
            # 컬렉션 확인
            health["collection"] = bool(self.collection)
            
            # 임베딩 모델 확인
            health["embedding_model"] = bool(self.embedding_model)
            
            # LLM 모델 확인
            health["llm_model"] = bool(self.model)
            
            # 전체 상태
            health["overall"] = all([
                health["chroma_db"],
                health["collection"],
                health["embedding_model"],
                health["llm_model"]
            ])
            
        except Exception as e:
            health["error"] = str(e)
        
        return health

# 전역 RAG 시스템 인스턴스
_simple_rag_system: Optional[SimpleRAGSystem] = None

def get_simple_rag_system() -> Optional[SimpleRAGSystem]:
    """간단한 RAG 시스템 인스턴스 반환"""
    return _simple_rag_system

def initialize_simple_rag_system(gemini_api_key: str) -> SimpleRAGSystem:
    """간단한 RAG 시스템 초기화"""
    global _simple_rag_system
    
    if _simple_rag_system is None:
        _simple_rag_system = SimpleRAGSystem(gemini_api_key)
    
    return _simple_rag_system