import os
import json
import uuid
from typing import List, Dict, Any
from pathlib import Path
import chromadb
from chromadb.config import Settings
import hashlib

class MedicalDataParser:
    def __init__(self, chroma_host: str = "localhost", chroma_port: int = 8000):
        self.chroma_client = chromadb.HttpClient(
            host=chroma_host,
            port=chroma_port,
            settings=Settings(allow_reset=True)
        )
        self.collection = self.chroma_client.get_or_create_collection(
            name="medical_knowledge",
            metadata={"description": "Korean medical knowledge database"}
        )
        
    def parse_source_data(self, file_path: str) -> Dict[str, Any]:
        """원천데이터 파일 파싱"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 원천데이터 구조에 맞춘 파싱
            parsed_data = {
                "id": data.get("c_id", ""),
                "type": "medical_procedure",
                "domain": data.get("domain", ""),
                "source": data.get("source_spec", ""),
                "year": data.get("creation_year", ""),
                "content": data.get("content", ""),
                "file_path": file_path
            }
            
            return parsed_data
            
        except Exception as e:
            print(f"Error parsing source data {file_path}: {e}")
            return None
    
    def parse_qa_data(self, file_path: str) -> Dict[str, Any]:
        """QA 라벨링데이터 파일 파싱"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # QA 데이터 구조에 맞춘 파싱
            parsed_data = {
                "id": f"qa_{data.get('qa_id', '')}",
                "type": "medical_qa",
                "domain": data.get("domain", ""),
                "question_type": data.get("q_type", ""),
                "question": data.get("question", ""),
                "answer": data.get("answer", ""),
                "file_path": file_path
            }
            
            return parsed_data
            
        except Exception as e:
            print(f"Error parsing QA data {file_path}: {e}")
            return None
    
    def create_document_chunks(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """문서를 검색 가능한 청크로 분할"""
        chunks = []
        
        if data["type"] == "medical_procedure":
            # 의료 시술 설명을 문단별로 분할
            content = data["content"]
            sentences = content.split('. ')
            
            # 긴 문장들을 적절한 크기로 청크화
            current_chunk = ""
            for sentence in sentences:
                if len(current_chunk + sentence) < 500:  # 500자 이하로 유지
                    current_chunk += sentence + ". "
                else:
                    if current_chunk.strip():
                        chunks.append({
                            "id": f"{data['id']}_chunk_{len(chunks)}",
                            "content": current_chunk.strip(),
                            "metadata": {
                                "source": data["source"],
                                "domain": data["domain"],
                                "year": data["year"],
                                "type": data["type"],
                                "original_id": data["id"]
                            }
                        })
                    current_chunk = sentence + ". "
            
            # 마지막 청크 추가
            if current_chunk.strip():
                chunks.append({
                    "id": f"{data['id']}_chunk_{len(chunks)}",
                    "content": current_chunk.strip(),
                    "metadata": {
                        "source": data["source"],
                        "domain": data["domain"],
                        "year": data["year"],
                        "type": data["type"],
                        "original_id": data["id"]
                    }
                })
        
        elif data["type"] == "medical_qa":
            # QA 데이터는 질문과 답변을 합쳐서 하나의 청크로 생성
            qa_content = f"질문: {data['question']}\n답변: {data['answer']}"
            chunks.append({
                "id": data["id"],
                "content": qa_content,
                "metadata": {
                    "domain": data["domain"],
                    "question_type": data["question_type"],
                    "type": data["type"],
                    "original_id": data["id"]
                }
            })
        
        return chunks
    
    def add_to_vector_store(self, chunks: List[Dict[str, Any]]):
        """벡터 스토어에 문서 추가"""
        try:
            documents = []
            metadatas = []
            ids = []
            
            for chunk in chunks:
                documents.append(chunk["content"])
                metadatas.append(chunk["metadata"])
                ids.append(chunk["id"])
            
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            print(f"Added {len(chunks)} chunks to vector store")
            
        except Exception as e:
            print(f"Error adding to vector store: {e}")
    
    def process_directory(self, directory_path: str, data_type: str = "source"):
        """디렉토리 내의 모든 JSON 파일 처리"""
        processed_count = 0
        
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                if file.endswith('.json'):
                    file_path = os.path.join(root, file)
                    
                    # 데이터 타입에 따라 다른 파싱 함수 사용
                    if data_type == "source":
                        parsed_data = self.parse_source_data(file_path)
                    elif data_type == "qa":
                        parsed_data = self.parse_qa_data(file_path)
                    else:
                        continue
                    
                    if parsed_data:
                        chunks = self.create_document_chunks(parsed_data)
                        if chunks:
                            self.add_to_vector_store(chunks)
                            processed_count += 1
                            
                            if processed_count % 100 == 0:
                                print(f"Processed {processed_count} files...")
        
        print(f"Total processed files: {processed_count}")
    
    def search_medical_knowledge(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """의료 지식 검색"""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )
            
            search_results = []
            for i, doc in enumerate(results['documents'][0]):
                search_results.append({
                    "content": doc,
                    "metadata": results['metadatas'][0][i],
                    "distance": results['distances'][0][i]
                })
            
            return search_results
            
        except Exception as e:
            print(f"Error searching medical knowledge: {e}")
            return []

def main():
    # 데이터 파서 초기화
    parser = MedicalDataParser()
    
    # 기본 데이터 경로
    base_path = "/Users/ohhalim/git_box/test_llm_backend/knowledge-board/ai-agent/09.필수의료 의학지식 데이터"
    
    # 원천데이터 처리
    source_data_path = os.path.join(base_path, "3.개방데이터/1.데이터/Training/01.원천데이터/TS_국문_기타")
    if os.path.exists(source_data_path):
        print("Processing source data...")
        parser.process_directory(source_data_path, "source")
    
    # QA 라벨링데이터 처리
    qa_data_path = os.path.join(base_path, "3.개방데이터/1.데이터/Training/02.라벨링데이터/TL_내과")
    if os.path.exists(qa_data_path):
        print("Processing QA data...")
        parser.process_directory(qa_data_path, "qa")
    
    print("Medical data parsing completed!")
    
    # 테스트 검색
    print("\n=== 테스트 검색 ===")
    results = parser.search_medical_knowledge("흉막천자")
    for i, result in enumerate(results):
        print(f"\n결과 {i+1}:")
        print(f"내용: {result['content'][:200]}...")
        print(f"메타데이터: {result['metadata']}")

if __name__ == "__main__":
    main()