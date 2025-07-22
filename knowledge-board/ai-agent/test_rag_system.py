#!/usr/bin/env python3
"""RAG 시스템 테스트 스크립트"""

import os
import asyncio
import sys
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

from rag_medical_system import initialize_rag_system

async def test_rag_system():
    """RAG 시스템 테스트"""
    print("🧪 RAG 시스템 테스트 시작")
    print("=" * 50)
    
    # API 키 확인
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY가 설정되지 않았습니다.")
        print("   .env 파일에 GEMINI_API_KEY를 설정해주세요.")
        return False
    
    try:
        # RAG 시스템 초기화
        print("🔄 RAG 시스템 초기화 중...")
        rag_system = initialize_rag_system(api_key)
        
        # 헬스 체크
        print("\n🏥 시스템 헬스 체크")
        health = rag_system.health_check()
        for component, status in health.items():
            if component != "error":
                print(f"   {component}: {'✅' if status else '❌'}")
        
        if not health.get("overall", False):
            print("❌ RAG 시스템이 완전히 초기화되지 않았습니다.")
            if "error" in health:
                print(f"   오류: {health['error']}")
            return False
        
        # 통계 확인
        print("\n📊 시스템 통계")
        stats = rag_system.get_stats()
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        # 테스트 검색 수행
        test_queries = [
            "흉막천자",
            "당뇨병 치료",
            "고혈압 약물"
        ]
        
        print("\n🔍 검색 테스트")
        for query in test_queries:
            print(f"\n📝 검색어: '{query}'")
            
            # 유사도 검색 테스트
            search_results = await rag_system.similarity_search(query, limit=2)
            print(f"   검색 결과: {len(search_results)}개")
            
            if search_results:
                for i, result in enumerate(search_results, 1):
                    score = result.get('similarity_score', 0)
                    content_preview = result['content'][:100] + "..."
                    print(f"   [{i}] 유사도: {score:.3f}")
                    print(f"       내용: {content_preview}")
        
        # QA 테스트 (RAG 체인)
        print("\n🤖 RAG 질의응답 테스트")
        qa_questions = [
            "흉막천자는 어떤 시술인가요?",
            "당뇨병 치료법에는 무엇이 있나요?"
        ]
        
        for question in qa_questions:
            print(f"\n❓ 질문: '{question}'")
            
            qa_result = await rag_system.search_and_answer(question, limit=2)
            
            if qa_result.get("error"):
                print(f"   ❌ 오류: {qa_result['error']}")
            else:
                answer = qa_result.get("answer", "답변 없음")
                source_count = qa_result.get("total_sources", 0)
                print(f"   💬 답변: {answer[:200]}...")
                print(f"   📚 참고 문서: {source_count}개")
        
        print("\n✅ RAG 시스템 테스트 완료!")
        return True
        
    except Exception as e:
        print(f"❌ RAG 시스템 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🏥 의료 지식 RAG 시스템 테스트")
    print("=" * 50)
    
    # 비동기 테스트 실행
    success = asyncio.run(test_rag_system())
    
    if success:
        print("\n🎉 모든 테스트 통과!")
        sys.exit(0)
    else:
        print("\n💥 테스트 실패!")
        sys.exit(1)