#!/usr/bin/env python3
"""의료 데이터 로드 스크립트"""

import os
import json
import sys
from pathlib import Path
import chromadb
from chromadb.config import Settings

def load_medical_data():
    """의료 데이터를 ChromaDB에 로드"""
    print("🏥 의료 데이터 로드 시작...")
    
    # ChromaDB 클라이언트 초기화
    try:
        client = chromadb.HttpClient(
            host="chromadb",  # 도커 컨테이너 내에서는 서비스명 사용
            port=8000,
            settings=Settings(allow_reset=True)
        )
        print("✅ ChromaDB 연결 성공")
    except Exception as e:
        print(f"❌ ChromaDB 연결 실패: {e}")
        return False
    
    # 의료 지식 컬렉션 생성
    try:
        # 기존 컬렉션 삭제 (있다면)
        try:
            client.delete_collection("medical_knowledge")
            print("🗑️ 기존 컬렉션 삭제")
        except:
            pass
        
        collection = client.create_collection(
            name="medical_knowledge",
            metadata={"description": "Korean medical knowledge database"}
        )
        print("✅ 의료 지식 컬렉션 생성")
    except Exception as e:
        print(f"❌ 컬렉션 생성 실패: {e}")
        return False
    
    # 데이터 디렉토리 경로
    base_path = "/app/09.필수의료 의학지식 데이터"
    
    # 원천데이터 처리
    source_data_path = os.path.join(base_path, "3.개방데이터/1.데이터/Training/01.원천데이터/TS_국문_기타")
    processed_count = 0
    
    if os.path.exists(source_data_path):
        print(f"📁 원천데이터 처리 중: {source_data_path}")
        
        for file_name in os.listdir(source_data_path):
            if file_name.endswith('.json'):
                file_path = os.path.join(source_data_path, file_name)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # 데이터 파싱
                    content = data.get('content', '').strip()
                    if not content:
                        continue
                    
                    # 문서 ID 생성
                    doc_id = f"src_{data.get('c_id', file_name.replace('.json', ''))}"
                    
                    # 메타데이터 준비
                    metadata = {
                        "source": data.get("source_spec", "의료기관"),
                        "domain": str(data.get("domain", "")),
                        "year": data.get("creation_year", ""),
                        "type": "medical_procedure",
                        "source_type": "medical_knowledge"
                    }
                    
                    # ChromaDB에 추가
                    collection.add(
                        documents=[content],
                        metadatas=[metadata],
                        ids=[doc_id]
                    )
                    
                    processed_count += 1
                    
                    if processed_count % 100 == 0:
                        print(f"📊 처리됨: {processed_count}개")
                        
                except Exception as e:
                    print(f"❌ 파일 처리 실패 {file_name}: {e}")
                    continue
    
    # QA 데이터 처리
    qa_data_path = os.path.join(base_path, "3.개방데이터/1.데이터/Training/02.라벨링데이터/TL_내과")
    
    if os.path.exists(qa_data_path):
        print(f"📁 QA 데이터 처리 중: {qa_data_path}")
        
        for file_name in os.listdir(qa_data_path):
            if file_name.endswith('.json'):
                file_path = os.path.join(qa_data_path, file_name)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # QA 데이터 파싱
                    question = data.get('question', '').strip()
                    answer = data.get('answer', '').strip()
                    
                    if not question or not answer:
                        continue
                    
                    # 질문과 답변 결합
                    qa_content = f"질문: {question}\n답변: {answer}"
                    
                    # 문서 ID 생성
                    doc_id = f"qa_{data.get('qa_id', file_name.replace('.json', ''))}"
                    
                    # 메타데이터 준비
                    metadata = {
                        "domain": str(data.get("domain", "")),
                        "question_type": str(data.get("q_type", "")),
                        "type": "medical_qa",
                        "source_type": "medical_knowledge"
                    }
                    
                    # ChromaDB에 추가
                    collection.add(
                        documents=[qa_content],
                        metadatas=[metadata],
                        ids=[doc_id]
                    )
                    
                    processed_count += 1
                    
                    if processed_count % 100 == 0:
                        print(f"📊 처리됨: {processed_count}개")
                        
                except Exception as e:
                    print(f"❌ 파일 처리 실패 {file_name}: {e}")
                    continue
    
    print(f"✅ 의료 데이터 로드 완료: 총 {processed_count}개 문서")
    
    # 최종 통계 확인
    try:
        count = collection.count()
        print(f"📊 최종 컬렉션 크기: {count}개 문서")
        
        # 테스트 검색
        test_results = collection.query(
            query_texts=["흉막천자"],
            n_results=3
        )
        
        if test_results['documents'][0]:
            print("✅ 검색 테스트 성공")
            print(f"   - 결과: {len(test_results['documents'][0])}개")
            print(f"   - 첫 번째 결과: {test_results['documents'][0][0][:100]}...")
        else:
            print("❌ 검색 테스트 실패")
            
    except Exception as e:
        print(f"❌ 최종 확인 실패: {e}")
    
    return processed_count > 0

if __name__ == "__main__":
    print("🏥 의료 지식 데이터 로더")
    print("=" * 50)
    
    success = load_medical_data()
    
    if success:
        print("\n🎉 의료 데이터 로드 성공!")
        sys.exit(0)
    else:
        print("\n❌ 의료 데이터 로드 실패!")
        sys.exit(1)