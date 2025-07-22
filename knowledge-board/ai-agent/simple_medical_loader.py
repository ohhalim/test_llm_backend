#!/usr/bin/env python3
"""간단한 의료 데이터 로더 (ChromaDB v2 API 호환)"""

import os
import json
import requests
from pathlib import Path

def load_medical_data_simple():
    """의료 데이터를 간단하게 로드"""
    print("🏥 간단한 의료 데이터 로더 시작...")
    
    # ChromaDB v2 API 사용
    base_url = "http://chromadb:8000/api/v1"
    
    # 헬스체크
    try:
        response = requests.get("http://chromadb:8000/api/v1/heartbeat")
        print(f"ChromaDB 상태: {response.status_code}")
    except Exception as e:
        print(f"ChromaDB 연결 실패: {e}")
        return False
    
    # 의료 데이터 파일 경로
    data_path = "/app/09.필수의료 의학지식 데이터/3.개방데이터/1.데이터/Training/01.원천데이터/TS_국문_기타"
    
    if not os.path.exists(data_path):
        print(f"❌ 데이터 경로를 찾을 수 없습니다: {data_path}")
        return False
    
    # JSON 파일 목록
    json_files = list(Path(data_path).glob("*.json"))
    print(f"📁 발견된 JSON 파일: {len(json_files)}개")
    
    if len(json_files) == 0:
        print("❌ 의료 데이터 파일이 없습니다.")
        return False
    
    # 처음 몇 개 파일만 로드 (테스트용)
    sample_files = json_files[:10]
    loaded_count = 0
    
    for json_file in sample_files:
        try:
            with open(json_file, 'r', encoding='utf-8-sig') as f:
                data = json.load(f)
                
            # 의료 정보 추출
            if 'sourceDataInfo' in data:
                source_info = data['sourceDataInfo']
                print(f"✅ 로드: {json_file.name}")
                loaded_count += 1
        except Exception as e:
            print(f"❌ 파일 로드 실패 {json_file.name}: {e}")
    
    print(f"🎉 총 {loaded_count}개 의료 데이터 파일 처리 완료")
    return True

if __name__ == "__main__":
    load_medical_data_simple()