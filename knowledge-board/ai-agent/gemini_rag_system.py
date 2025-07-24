"""Gemini 기반 간단 RAG 시스템"""

import os
import json
import asyncio
from typing import List, Dict, Any, Optional
from pathlib import Path
import google.generativeai as genai

class GeminiRAGSystem:
    """Gemini 기반 RAG 시스템"""
    
    def __init__(self, gemini_api_key: str):
        """RAG 시스템 초기화"""
        self.gemini_api_key = gemini_api_key
        
        # Gemini 설정
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
        # 의료 데이터 저장소
        self.medical_data = {}
        self.load_medical_data()
    
    def load_medical_data(self):
        """의료 데이터 로드"""
        # 현재 프로젝트의 의료 데이터 경로들
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
            print("⚠️ 의료 데이터 경로를 찾을 수 없습니다. 샘플 데이터를 사용합니다.")
            self._load_sample_data()
            return
        
        print(f"📁 의료 데이터 로드 중: {data_path}")
        
        json_files = list(Path(data_path).glob("*.json"))
        loaded_count = 0
        
        for json_file in json_files[:100]:  # 처음 100개만 로드
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
        
        if loaded_count == 0:
            self._load_sample_data()
    
    def _load_sample_data(self):
        """테스트용 샘플 데이터 로드"""
        print("📝 테스트용 샘플 의료 데이터 로드 중...")
        
        sample_data = {
            'sample_001': {
                'id': 'sample_001',
                'content': '''흉막천자(Thoracentesis)는 흉막강에 고인 액체나 공기를 제거하기 위해 
                바늘이나 카테터를 삽입하는 의료 시술입니다. 진단 목적과 치료 목적으로 시행됩니다.
                
                적응증:
                - 흉막삼출 진단
                - 흉막삼출로 인한 호흡곤란 완화
                - 감염성 흉막염 치료
                
                금기증:
                - 출혈 경향
                - 혈소판 감소증
                - 기흉의 위험이 높은 경우''',
                'source': '의료 지식 데이터베이스',
                'domain': '호흡기내과',
                'year': '2024'
            },
            'sample_002': {
                'id': 'sample_002',
                'content': '''당뇨병 치료는 혈당 조절을 목표로 합니다. 
                
                치료법:
                1. 식이요법: 탄수화물 제한, 규칙적인 식사
                2. 운동요법: 유산소 운동, 근력 운동
                3. 약물치료: 메트포르민, 설포닐우레아 등
                4. 인슐린 치료: 제1형 당뇨병, 중증 제2형 당뇨병
                
                목표 혈당:
                - 공복혈당: 80-130 mg/dL
                - 식후 2시간 혈당: <180 mg/dL
                - 당화혈색소: <7%''',
                'source': '의료 지식 데이터베이스',
                'domain': '내분비내과',
                'year': '2024'
            },
            'sample_003': {
                'id': 'sample_003',
                'content': '''고혈압 치료에는 다양한 약물이 사용됩니다.
                
                주요 약물군:
                1. ACE 억제제: 리시노프릴, 에날라프릴
                2. ARB: 로사르탄, 발사르탄
                3. 베타 차단제: 메토프롤롤, 아테놀롤
                4. 칼슘채널차단제: 암로디핀, 니페디핀
                5. 이뇨제: 하이드로클로로티아지드
                
                치료 목표:
                - 일반인: <140/90 mmHg
                - 당뇨병/신장질환: <130/80 mmHg
                
                생활습관 개선도 중요합니다.''',
                'source': '의료 지식 데이터베이스',
                'domain': '순환기내과',
                'year': '2024'
            }
        }
        
        self.medical_data = sample_data
        print(f"✅ {len(sample_data)}개 샘플 의료 데이터 로드 완료")
    
    async def similarity_search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """간단한 키워드 기반 검색"""
        if not self.medical_data:
            return []
        
        # 간단한 키워드 매칭 검색 (개선된 버전)
        query_lower = query.lower()
        query_keywords = query_lower.split()
        results = []
        
        for doc_id, doc_data in self.medical_data.items():
            content = str(doc_data['content']).lower()
            
            # 키워드 점수 계산
            score = 0
            for keyword in query_keywords:
                if keyword in content:
                    score += content.count(keyword)
            
            # 제목이나 주요 키워드 일치 시 보너스 점수
            domain_str = str(doc_data.get('domain', '')).lower()
            if any(keyword in domain_str for keyword in query_keywords):
                score += 2
            
            if score > 0:
                # 관련도 점수를 0-1 사이로 정규화
                similarity_score = min(score / 10, 1.0)
                
                content_text = str(doc_data['content'])
                results.append({
                    'content': content_text[:300] + '...' if len(content_text) > 300 else content_text,
                    'metadata': {
                        'source': str(doc_data.get('source', '')),
                        'domain': str(doc_data.get('domain', '')),
                        'type': 'medical_knowledge',
                        'id': str(doc_data.get('id', ''))
                    },
                    'similarity_score': similarity_score,
                    'source': str(doc_data.get('source', '')),
                    'type': 'medical_knowledge'
                })
        
        # 점수 순으로 정렬
        results.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        return results[:limit]
    
    async def search_and_answer(self, question: str, limit: int = 5) -> Dict[str, Any]:
        """Gemini RAG 기반 질의응답"""
        try:
            # 관련 문서 검색
            docs = await self.similarity_search(question, limit)
            
            if not docs:
                # Fallback to general LLM
                print("🤔 관련된 의료 지식을 찾지 못했습니다. 일반 LLM으로 답변을 시도합니다.")
                
                prompt = f"""당신은 의료 전문 AI 어시스턴트입니다. 
                당신이 가진 일반적인 의학 지식을 바탕으로 다음 질문에 답해주세요. 
                단, 이 답변은 전문 데이터베이스를 참고한 것이 아님을 명확히 밝혀주세요.

                사용자 질문: {question}

                답변:"""
                
                response = self.model.generate_content(prompt)
                answer = response.text if response.text else "답변을 생성할 수 없습니다."
                
                # 의료 면책 조항 추가
                disclaimer = "\n\n⚠️ 이 답변은 일반적인 의학 지식을 바탕으로 생성되었으며, 전문 의료 데이터베이스의 검증을 거치지 않았습니다. 정확한 진단과 치료를 위해서는 반드시 의료진과 상담하시기 바랍니다."
                answer += disclaimer
                
                return {
                    "answer": answer,
                    "source_documents": [],
                    "question": question,
                    "total_sources": 0,
                    "fallback": True 
                }
            
            # 컨텍스트 구성
            context_parts = []
            for i, doc in enumerate(docs, 1):
                context_parts.append(f"[참고문서 {i}]\n{doc['content']}\n")
            
            context = "\n".join(context_parts)
            
            # Gemini용 프롬프트 생성
            prompt = f"""당신은 의료 전문 AI 어시스턴트입니다. 
주어진 의료 지식을 바탕으로 정확하고 도움이 되는 답변을 제공해주세요.

의료 지식 컨텍스트:
{context}

사용자 질문: {question}

답변 지침:
1. 주어진 의료 지식만을 기반으로 답변하세요
2. 정확하지 않거나 불확실한 정보는 제공하지 마세요  
3. 의료진 상담의 필요성을 강조하세요
4. 한국어로 명확하고 이해하기 쉽게 답변하세요
5. 참고문서 번호를 언급하여 근거를 명시하세요

답변:"""
            
            # Gemini로 답변 생성
            response = self.model.generate_content(prompt)
            answer = response.text if response.text else "답변을 생성할 수 없습니다."
            
            # 의료 면책 조항 추가
            disclaimer = "\n\n⚠️ 이 답변은 의료 지식을 바탕으로 한 일반적인 정보입니다. 정확한 진단과 치료를 위해서는 반드시 의료진과 상담하시기 바랍니다."
            answer += disclaimer
            
            return {
                "answer": answer,
                "source_documents": docs,
                "question": question,
                "total_sources": len(docs)
            }
            
        except Exception as e:
            print(f"❌ 답변 생성 실패: {e}")
            return {
                "answer": f"답변 생성 중 오류가 발생했습니다. 다시 시도해 주세요.",
                "source_documents": [],
                "question": question,
                "total_sources": 0,
                "error": str(e)
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """시스템 통계"""
        return {
            "total_documents": len(self.medical_data),
            "status": "active" if self.medical_data else "empty",
            "vector_store": "In-Memory",
            "embedding_model": "Keyword-based",
            "llm_model": "gemini-2.5-flash",
            "system_ready": bool(self.medical_data)
        }
    
    def health_check(self) -> Dict[str, Any]:
        """시스템 헬스 체크"""
        health = {
            "gemini_model": False,
            "medical_data": False,
            "overall": False
        }
        
        try:
            # Gemini 모델 확인
            health["gemini_model"] = bool(self.model)
            
            # 의료 데이터 확인
            health["medical_data"] = bool(self.medical_data)
            
            # 전체 상태
            health["overall"] = health["gemini_model"] and health["medical_data"]
            
        except Exception as e:
            health["error"] = str(e)
        
        return health

# 전역 RAG 시스템 인스턴스
_gemini_rag_system: Optional[GeminiRAGSystem] = None

def get_gemini_rag_system() -> Optional[GeminiRAGSystem]:
    """Gemini RAG 시스템 인스턴스 반환"""
    return _gemini_rag_system

def initialize_gemini_rag_system(gemini_api_key: str) -> GeminiRAGSystem:
    """Gemini RAG 시스템 초기화"""
    global _gemini_rag_system
    
    if _gemini_rag_system is None:
        _gemini_rag_system = GeminiRAGSystem(gemini_api_key)
    
    return _gemini_rag_system