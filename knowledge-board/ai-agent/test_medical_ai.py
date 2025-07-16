#!/usr/bin/env python3
"""의료 AI 답변 테스트 스크립트"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent.graph import knowledge_agent
from agent.tools import vector_tools

async def test_medical_search():
    """의료 지식 검색 테스트"""
    print("=== 의료 지식 검색 테스트 ===")
    
    # 테스트 쿼리들
    test_queries = [
        "흉막천자",
        "당뇨병 치료",
        "고혈압 약물",
        "심전도 검사",
        "폐렴 증상"
    ]
    
    for query in test_queries:
        print(f"\n🔍 검색: {query}")
        results = vector_tools.search_medical_knowledge(query, limit=3)
        
        if results:
            print(f"✅ {len(results)}개 결과 발견:")
            for i, result in enumerate(results, 1):
                print(f"  {i}. 관련도: {result.get('similarity_score', 0):.2f}")
                print(f"     출처: {result['metadata'].get('source', 'N/A')}")
                print(f"     내용: {result['content'][:100]}...")
        else:
            print("❌ 검색 결과 없음")
        print("-" * 50)

async def test_ai_chat():
    """AI 채팅 테스트"""
    print("\n=== AI 채팅 테스트 ===")
    
    # 의료 관련 질문들
    medical_questions = [
        "흉막천자는 어떤 시술인가요?",
        "당뇨병 환자가 주의해야 할 점은?",
        "고혈압 치료에 사용되는 약물은?",
        "심전도 검사는 언제 받나요?",
        "폐렴의 주요 증상은 무엇인가요?"
    ]
    
    for question in medical_questions:
        print(f"\n❓ 질문: {question}")
        try:
            result = await knowledge_agent.chat(question)
            
            print(f"🤖 답변: {result['answer']}")
            print(f"📊 컨텍스트 개수: {len(result['context'])}")
            
            # 컨텍스트 출처 표시
            if result['context']:
                print("📚 참고 자료:")
                for i, ctx in enumerate(result['context'][:3], 1):
                    source_type = ctx['metadata'].get('source_type', 'post')
                    if source_type == 'medical_knowledge':
                        print(f"  {i}. [의료지식] {ctx['metadata'].get('source', 'N/A')}")
                    else:
                        print(f"  {i}. [게시글] {ctx['metadata'].get('title', 'N/A')}")
            
        except Exception as e:
            print(f"❌ 오류: {e}")
        
        print("-" * 80)

def test_medical_stats():
    """의료 지식 DB 통계 테스트"""
    print("\n=== 의료 지식 DB 통계 ===")
    
    try:
        stats = vector_tools.get_medical_knowledge_stats()
        print(f"📊 총 문서 수: {stats.get('total_documents', 0)}")
        print(f"📦 컬렉션 이름: {stats.get('collection_name', 'N/A')}")
        print(f"🔄 상태: {stats.get('status', 'N/A')}")
        
        if stats.get('error'):
            print(f"❌ 오류: {stats['error']}")
            
    except Exception as e:
        print(f"❌ 통계 조회 오류: {e}")

async def interactive_test():
    """대화형 테스트"""
    print("\n=== 대화형 테스트 ===")
    print("의료 관련 질문을 입력하세요. 'quit' 입력시 종료됩니다.")
    
    while True:
        try:
            question = input("\n❓ 질문: ").strip()
            
            if question.lower() in ['quit', 'exit', '종료']:
                print("👋 테스트를 종료합니다.")
                break
            
            if not question:
                continue
                
            print("🤔 생각 중...")
            result = await knowledge_agent.chat(question)
            
            print(f"\n🤖 답변:")
            print(result['answer'])
            
            if result['context']:
                print(f"\n📚 참고 자료 ({len(result['context'])}개):")
                for i, ctx in enumerate(result['context'][:3], 1):
                    source_type = ctx['metadata'].get('source_type', 'post')
                    if source_type == 'medical_knowledge':
                        print(f"  {i}. [의료지식] {ctx['metadata'].get('source', 'N/A')}")
                    else:
                        print(f"  {i}. [게시글] {ctx['metadata'].get('title', 'N/A')}")
            
        except KeyboardInterrupt:
            print("\n👋 테스트를 종료합니다.")
            break
        except Exception as e:
            print(f"❌ 오류: {e}")

async def main():
    """메인 테스트 함수"""
    print("🏥 의료 AI 시스템 테스트")
    print("=" * 50)
    
    # 1. 의료 지식 DB 통계 확인
    test_medical_stats()
    
    # 2. 의료 지식 검색 테스트
    await test_medical_search()
    
    # 3. AI 채팅 테스트
    await test_ai_chat()
    
    # 4. 대화형 테스트 (선택사항)
    choice = input("\n대화형 테스트를 진행하시겠습니까? (y/n): ").strip().lower()
    if choice in ['y', 'yes', '예']:
        await interactive_test()

if __name__ == "__main__":
    # 환경 변수 확인
    if not os.getenv("GEMINI_API_KEY"):
        print("❌ GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.")
        sys.exit(1)
    
    # 비동기 실행
    asyncio.run(main())