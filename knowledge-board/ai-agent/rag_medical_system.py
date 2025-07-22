"""의료지식 RAG 시스템 (LangChain 기반)"""

import os
import json
import asyncio
from typing import List, Dict, Any, Optional
from pathlib import Path

# LangChain imports
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.schema import Document

# ChromaDB import
import chromadb
from chromadb.config import Settings

class MedicalRAGSystem:
    """의료지식 RAG 시스템"""
    
    def __init__(self, 
                 gemini_api_key: str,
                 chroma_host: str = "chromadb",
                 chroma_port: int = 8000):
        """
        RAG 시스템 초기화
        
        Args:
            gemini_api_key: Google Gemini API 키
            chroma_host: ChromaDB 호스트
            chroma_port: ChromaDB 포트
        """
        self.gemini_api_key = gemini_api_key
        self.chroma_host = chroma_host
        self.chroma_port = chroma_port
        
        # LangChain 컴포넌트 초기화 (Gemini 사용)
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=gemini_api_key
        )
        self.llm = GoogleGenerativeAI(
            model="gemini-pro",
            google_api_key=gemini_api_key,
            temperature=0.1
        )
        
        # 텍스트 분할기
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        
        # ChromaDB 클라이언트
        self.chroma_client = None
        self.vector_store = None
        self.qa_chain = None
        
        # 의료 데이터 경로
        self.medical_data_path = "/app/09.필수의료 의학지식 데이터/3.개방데이터/1.데이터/Training/01.원천데이터/TS_국문_기타"
        
        # 시스템 초기화
        self._initialize_system()
    
    def _initialize_system(self):
        """시스템 초기화"""
        try:
            # ChromaDB 연결
            self.chroma_client = chromadb.HttpClient(
                host=self.chroma_host,
                port=self.chroma_port,
                settings=Settings(allow_reset=True)
            )
            print("✅ ChromaDB 연결 성공")
            
            # 벡터 스토어 초기화
            self._initialize_vector_store()
            
            # QA 체인 초기화
            self._initialize_qa_chain()
            
        except Exception as e:
            print(f"❌ RAG 시스템 초기화 실패: {e}")
            raise
    
    def _initialize_vector_store(self):
        """벡터 스토어 초기화"""
        try:
            # 기존 컬렉션 확인 및 생성
            try:
                collection = self.chroma_client.get_collection("medical_rag")
                count = collection.count()
                if count > 0:
                    print(f"✅ 기존 의료 RAG 컬렉션 사용 ({count}개 문서)")
                    self.vector_store = Chroma(
                        client=self.chroma_client,
                        collection_name="medical_rag",
                        embedding_function=self.embeddings
                    )
                    return
            except:
                pass
            
            # 새 컬렉션 생성 및 데이터 로드
            print("🔄 새로운 의료 RAG 컬렉션 생성 중...")
            documents = self._load_medical_documents()
            
            if documents:
                self.vector_store = Chroma.from_documents(
                    documents=documents,
                    embedding=self.embeddings,
                    client=self.chroma_client,
                    collection_name="medical_rag"
                )
                print(f"✅ 의료 RAG 벡터 스토어 생성 완료 ({len(documents)}개 문서)")
            else:
                print("⚠️ 로드할 의료 문서가 없습니다")
                
        except Exception as e:
            print(f"❌ 벡터 스토어 초기화 실패: {e}")
            raise
    
    def _load_medical_documents(self) -> List[Document]:
        """의료 문서 로드"""
        documents = []
        
        if not os.path.exists(self.medical_data_path):
            print(f"⚠️ 의료 데이터 경로 없음: {self.medical_data_path}")
            return documents
        
        json_files = list(Path(self.medical_data_path).glob("*.json"))
        print(f"📁 의료 데이터 파일 {len(json_files)}개 발견")
        
        processed_count = 0
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8-sig') as f:
                    data = json.load(f)
                
                content = data.get('content', '').strip()
                if not content:
                    continue
                
                # 긴 텍스트는 청크로 분할
                text_chunks = self.text_splitter.split_text(content)
                
                for i, chunk in enumerate(text_chunks):
                    doc = Document(
                        page_content=chunk,
                        metadata={
                            "source": data.get("source_spec", "의료기관"),
                            "domain": str(data.get("domain", "")),
                            "year": data.get("creation_year", ""),
                            "type": "medical_procedure",
                            "c_id": data.get("c_id", ""),
                            "chunk_id": f"{data.get('c_id', '')}_chunk_{i}",
                            "file_name": json_file.name
                        }
                    )
                    documents.append(doc)
                
                processed_count += 1
                if processed_count % 100 == 0:
                    print(f"📊 처리됨: {processed_count}개 파일")
                    
            except Exception as e:
                continue
        
        print(f"✅ 총 {len(documents)}개 문서 청크 생성")
        return documents
    
    def _initialize_qa_chain(self):
        """QA 체인 초기화"""
        if not self.vector_store:
            print("❌ 벡터 스토어가 초기화되지 않음")
            return
        
        # 의료 전문 프롬프트 템플릿
        prompt_template = """당신은 의료 전문 AI 어시스턴트입니다. 
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

        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        
        # RetrievalQA 체인 생성
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 5}
            ),
            chain_type_kwargs={"prompt": PROMPT},
            return_source_documents=True
        )
        
        print("✅ 의료 QA 체인 초기화 완료")
    
    async def search_and_answer(self, 
                               question: str, 
                               limit: int = 5) -> Dict[str, Any]:
        """의료 질문에 대한 RAG 답변 생성"""
        try:
            if not self.qa_chain:
                return {
                    "answer": "RAG 시스템이 초기화되지 않았습니다.",
                    "source_documents": [],
                    "error": "System not initialized"
                }
            
            # QA 체인 실행
            result = await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: self.qa_chain({"query": question})
            )
            
            # 소스 문서 정보 추출
            source_docs = []
            for doc in result.get("source_documents", []):
                source_docs.append({
                    "content": doc.page_content[:300] + "..." if len(doc.page_content) > 300 else doc.page_content,
                    "metadata": doc.metadata,
                    "source": doc.metadata.get("source", ""),
                    "domain": doc.metadata.get("domain", ""),
                    "type": doc.metadata.get("type", "")
                })
            
            return {
                "answer": result["result"],
                "source_documents": source_docs[:limit],
                "question": question,
                "total_sources": len(result.get("source_documents", []))
            }
            
        except Exception as e:
            print(f"❌ RAG 답변 생성 실패: {e}")
            return {
                "answer": f"답변 생성 중 오류가 발생했습니다: {str(e)}",
                "source_documents": [],
                "error": str(e)
            }
    
    async def similarity_search(self, 
                               query: str, 
                               limit: int = 5) -> List[Dict[str, Any]]:
        """유사도 검색"""
        try:
            if not self.vector_store:
                return []
            
            # 유사도 검색 실행
            docs = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.vector_store.similarity_search_with_score(query, k=limit)
            )
            
            results = []
            for doc, score in docs:
                results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "similarity_score": 1 - score,  # 유사도 점수 변환
                    "source": doc.metadata.get("source", ""),
                    "domain": doc.metadata.get("domain", ""),
                    "type": doc.metadata.get("type", "")
                })
            
            return results
            
        except Exception as e:
            print(f"❌ 유사도 검색 실패: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """RAG 시스템 통계"""
        try:
            if self.vector_store and self.chroma_client:
                collection = self.chroma_client.get_collection("medical_rag")
                count = collection.count()
                
                return {
                    "total_documents": count,
                    "status": "active",
                    "vector_store": "ChromaDB",
                    "embedding_model": "Google Gemini Embedding",
                    "llm_model": "gemini-pro",
                    "system_ready": bool(self.qa_chain)
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
                "status": "error"
            }
    
    def health_check(self) -> Dict[str, Any]:
        """시스템 헬스 체크"""
        health = {
            "chroma_db": False,
            "vector_store": False,
            "qa_chain": False,
            "overall": False
        }
        
        try:
            # ChromaDB 연결 확인
            if self.chroma_client:
                self.chroma_client.heartbeat()
                health["chroma_db"] = True
            
            # 벡터 스토어 확인
            health["vector_store"] = bool(self.vector_store)
            
            # QA 체인 확인
            health["qa_chain"] = bool(self.qa_chain)
            
            # 전체 상태
            health["overall"] = all([
                health["chroma_db"],
                health["vector_store"], 
                health["qa_chain"]
            ])
            
        except Exception as e:
            health["error"] = str(e)
        
        return health

# 전역 RAG 시스템 인스턴스
_rag_system: Optional[MedicalRAGSystem] = None

def get_rag_system() -> Optional[MedicalRAGSystem]:
    """RAG 시스템 인스턴스 반환"""
    return _rag_system

def initialize_rag_system(gemini_api_key: str) -> MedicalRAGSystem:
    """RAG 시스템 초기화"""
    global _rag_system
    
    if _rag_system is None:
        _rag_system = MedicalRAGSystem(gemini_api_key)
    
    return _rag_system