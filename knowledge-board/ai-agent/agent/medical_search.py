"""의료 지식 검색 모듈 (파일 기반)"""

import os
import json
import re
from typing import List, Dict, Any
from pathlib import Path

class MedicalKnowledgeSearch:
    """의료 지식 검색 클래스"""
    
    def __init__(self):
        self.data_path = "/app/09.필수의료 의학지식 데이터/3.개방데이터/1.데이터/Training/01.원천데이터/TS_국문_기타"
        self.medical_data = {}
        self.load_medical_data()
    
    def load_medical_data(self):
        """의료 데이터 로드"""
        if not os.path.exists(self.data_path):
            print(f"⚠️ 의료 데이터 경로를 찾을 수 없습니다: {self.data_path}")
            return
        
        json_files = list(Path(self.data_path).glob("*.json"))
        print(f"📁 의료 데이터 파일 {len(json_files)}개 발견")
        
        loaded_count = 0
        for json_file in json_files[:100]:  # 처음 100개만 로드 (메모리 절약)
            try:
                with open(json_file, 'r', encoding='utf-8-sig') as f:
                    data = json.load(f)
                
                if 'content' in data and data['content']:
                    self.medical_data[data['c_id']] = {
                        'id': data['c_id'],
                        'content': data['content'],
                        'source': data.get('source_spec', ''),
                        'domain': data.get('domain', ''),
                        'year': data.get('creation_year', '')
                    }
                    loaded_count += 1
                    
            except Exception as e:
                continue
        
        print(f"✅ {loaded_count}개 의료 지식 데이터 로드 완료")
    
    def search_medical_knowledge(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """의료 지식 검색"""
        if not self.medical_data:
            return []
        
        # 간단한 키워드 매칭 검색
        query_lower = query.lower()
        results = []
        
        for doc_id, doc_data in self.medical_data.items():
            content = doc_data['content'].lower()
            
            # 키워드가 포함되어 있는지 확인
            if query_lower in content:
                # 관련도 점수 계산 (간단한 키워드 빈도)
                score = content.count(query_lower)
                
                results.append({
                    'id': doc_data['id'],
                    'content': doc_data['content'][:300] + '...' if len(doc_data['content']) > 300 else doc_data['content'],
                    'source': doc_data['source'],
                    'score': score,
                    'metadata': {
                        'domain': doc_data['domain'],
                        'year': doc_data['year']
                    }
                })
        
        # 점수 순으로 정렬
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return results[:limit]
    
    def get_stats(self) -> Dict[str, Any]:
        """의료 지식 데이터베이스 통계"""
        return {
            'total_documents': len(self.medical_data),
            'data_path': self.data_path,
            'status': 'active' if self.medical_data else 'empty'
        }

# 전역 인스턴스
medical_search = MedicalKnowledgeSearch()