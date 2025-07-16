#!/usr/bin/env python3
"""간단한 의료 지식 테스트"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent.tools import vector_tools

def test_medical_knowledge():
    """의료 지식 검색 테스트"""
    print("=== 의료 지식 검색 테스트 ===")
    
    # 통계 확인
    print("\n📊 의료 지식 DB 통계:")
    stats = vector_tools.get_medical_knowledge_stats()
    print(f"   총 문서 수: {stats.get('total_documents', 0)}")
    print(f"   상태: {stats.get('status', 'N/A')}")
    if stats.get('error'):
        print(f"   오류: {stats['error']}")
    
    # 검색 테스트
    test_queries = [
        "흉막천자",
        "당뇨병", 
        "고혈압",
        "심전도",
        "폐렴"
    ]
    
    for query in test_queries:
        print(f"\n🔍 검색: '{query}'")
        results = vector_tools.search_medical_knowledge(query, limit=3)
        
        if results:
            print(f"   ✅ {len(results)}개 결과:")
            for i, result in enumerate(results, 1):
                content = result['content'][:100] + "..." if len(result['content']) > 100 else result['content']
                print(f"   {i}. {content}")
                print(f"      출처: {result['metadata'].get('source', 'N/A')}")
        else:
            print("   ❌ 검색 결과 없음")

if __name__ == "__main__":
    test_medical_knowledge()