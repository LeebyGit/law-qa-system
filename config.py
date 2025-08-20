import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

class Config:
    # 국가법령정보센터 API 설정
    LAW_API_KEY = os.getenv('LAW_API_KEY', '')
    LAW_API_BASE_URL = "http://www.law.go.kr/DRF/lawSearch.do"  # 검색용
    LAW_DETAIL_API_URL = "http://www.law.go.kr/DRF/lawService.do"  # 상세조회용
    
    # AI 답변 기능은 제거됨 (키워드 기반 구조화된 답변 사용)
    
    # Flask 설정
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    # API 사용량 제한 설정
    MAX_LAWS_PER_SEARCH = 5
    MAX_ARTICLES_PER_LAW = 10
    MAX_KEYWORDS = 3
    
    @staticmethod
    def validate_config():
        """필수 설정 값들이 있는지 확인"""
        missing = []
        
        if not Config.LAW_API_KEY:
            missing.append('LAW_API_KEY')
        
        return missing
