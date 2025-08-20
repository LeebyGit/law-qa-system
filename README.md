# 🏛️ 법령 질의응답 시스템 (Law Q&A System)

국가법령정보센터 API를 활용하여 법령에 대한 질문에 답변하는 웹 애플리케이션입니다.

## ✨ 주요 기능

- **실시간 법령 검색**: 국가법령정보센터 공개 API 활용
- **정확한 조문 파싱**: XML 기반 법령 조문 자동 추출
- **지능형 답변 생성**: 질문 유형별 관련 조문 자동 선별
- **디버깅 시스템**: XML 구조 분석 및 상세 로깅
- **사용자 친화적 UI**: 토글 기능과 깔끔한 인터페이스

## 🚀 기술 스택

- **Backend**: Python Flask
- **API**: 국가법령정보센터 공개 API
- **Frontend**: HTML, CSS, JavaScript
- **데이터 처리**: XML 파싱, 정규표현식
- **패키지 관리**: pip, requirements.txt

## 📋 설치 방법

### 1. 저장소 클론
```bash
git clone https://github.com/[사용자명]/law-qa-system.git
cd law-qa-system
```

### 2. Python 환경 설정
```bash
# Python 3.8+ 설치 필요
python --version

# 가상환경 생성 (권장)
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux
```

### 3. 의존성 설치
```bash
pip install -r requirements.txt
```

### 4. 환경 변수 설정
```bash
# .env 파일 생성
cp env_sample.txt .env

# .env 파일 편집하여 API 키 설정
LAW_API_KEY=your_api_key_here
```

### 5. 애플리케이션 실행
```bash
python app.py
```

브라우저에서 `http://127.0.0.1:5000` 접속

## 🔑 API 키 발급

1. [국가법령정보센터](https://www.law.go.kr) 접속
2. 회원가입 및 로그인
3. "공개API" → "API 신청" 메뉴에서 신청
4. 승인 후 발급받은 API 키를 `.env` 파일에 설정

## 📖 사용 방법

### 예시 질문
- "공공주택 종류는 무엇인가요?"
- "산업단지 지정권자는 누구인가요?"
- "주택법 제2조 내용을 알려주세요"

### 답변 구성
- **질문**: 사용자 입력 질문
- **답변**: 관련 법령 조문 기반 답변
- **법적 근거**: 조문 번호, 제목, 내용
- **출처**: 국가법령정보센터 링크

## 🏗️ 프로젝트 구조

```
law-qa-system/
├── app.py                 # 메인 Flask 애플리케이션
├── config.py             # 설정 파일
├── requirements.txt      # Python 패키지 의존성
├── .env                  # 환경 변수 (API 키 등)
├── .gitignore           # Git 제외 파일 목록
├── README.md            # 프로젝트 설명서
├── templates/           # HTML 템플릿
│   └── index.html      # 메인 페이지
└── static/              # 정적 파일
    ├── style.css        # 스타일시트
    └── script.js        # JavaScript 코드
```

## 🔧 주요 클래스 및 함수

### LawAPI 클래스
- `search_laws(query)`: 법령 검색
- `get_law_detail(law_id, law_name)`: 법령 상세 조문 조회
- `parse_law_detail_debug(xml_text)`: XML 파싱 및 디버깅

### 핵심 함수
- `extract_keywords(question)`: 질문에서 키워드 추출
- `analyze_question_type(question)`: 질문 유형 분석
- `find_relevant_articles(articles, question, type, keywords)`: 관련 조문 선별
- `generate_law_based_answer(question, laws, keywords)`: 답변 생성

## 🐛 디버깅 기능

- **XML 저장**: API 응답을 파일로 저장하여 구조 분석
- **상세 로깅**: 각 단계별 처리 과정 상세 출력
- **구조 분석**: XML 태그 구조 및 조문 개수 분석
- **에러 추적**: 예외 발생 시 상세 스택 트레이스 출력

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 문의사항

프로젝트에 대한 문의사항이나 버그 리포트는 GitHub Issues에 등록해주세요.

## 🙏 감사의 말

- [국가법령정보센터](https://www.law.go.kr) - 공개 API 제공
- [Flask](https://flask.palletsprojects.com/) - 웹 프레임워크
- [Python](https://www.python.org/) - 프로그래밍 언어

---

**⭐ 이 프로젝트가 도움이 되었다면 Star를 눌러주세요!**
