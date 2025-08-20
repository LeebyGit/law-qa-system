from flask import Flask, render_template, request, jsonify
import requests
import xml.etree.ElementTree as ET
import os
import re
import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

class LawAPI:
    def __init__(self):
        self.api_key = os.getenv('LAW_API_KEY', '')
        self.search_url = "http://www.law.go.kr/DRF/lawSearch.do"
        self.detail_url = "http://www.law.go.kr/DRF/lawService.do"
    
    def save_debug_xml(self, xml_content, filename):
        """XML 응답을 파일로 저장하여 구조 분석"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        debug_file = f"debug_{filename}_{timestamp}.xml"
        
        try:
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(xml_content)
            print(f"🔍 디버그 XML 저장: {debug_file}")
            return debug_file
        except Exception as e:
            print(f"❌ XML 저장 실패: {e}")
            return None
    
    def analyze_xml_structure(self, xml_content):
        """XML 구조를 상세히 분석"""
        try:
            root = ET.fromstring(xml_content)
            print(f"\n📊 XML 구조 분석:")
            print(f"루트 태그: {root.tag}")
            
            # 모든 태그 수집
            all_tags = set()
            tag_counts = {}
            for elem in root.iter():
                all_tags.add(elem.tag)
                tag_counts[elem.tag] = tag_counts.get(elem.tag, 0) + 1
            
            print(f"발견된 태그들 ({len(all_tags)}개): {sorted(all_tags)}")
            
            # 조문 관련 태그 찾기
            article_tags = ['조문', '조문단위', '조', '조문번호', '조문제목', '조문내용', '조문여부', '조문본문']
            found_article_tags = [tag for tag in article_tags if tag in all_tags]
            print(f"🎯 조문 관련 태그: {found_article_tags}")
            
            # 조문단위 태그 상세 분석
            article_units = root.findall('.//조문단위')
            print(f"📋 조문단위 개수: {len(article_units)}")
            
            # 첫 번째 조문단위의 구조 출력
            if article_units:
                print(f"\n🔍 첫 번째 조문단위 구조:")
                first_article = article_units[0]
                for child in first_article:
                    content_preview = (child.text[:100] + "...") if child.text and len(child.text) > 100 else (child.text or "None")
                    print(f"  📌 {child.tag}: {content_preview}")
                    
            return {'tags': all_tags, 'article_count': len(article_units)}
                
        except Exception as e:
            print(f"❌ XML 분석 오류: {e}")
            return {}
    
    def clean_article_content(self, content):
        """조문 내용에서 불필요한 메타데이터 제거"""
        if not content:
            return ""
        
        content = content.strip()
        
        # CDATA 처리
        if content.startswith('<![CDATA[') and content.endswith(']]>'):
            content = content[9:-3]
        
        # 개정 이력 및 메타데이터 제거
        content = re.sub(r'<개정[^>]*?>', '', content)
        content = re.sub(r'<신설[^>]*?>', '', content)
        content = re.sub(r'<전부개정[^>]*?>', '', content)
        content = re.sub(r'<제정[^>]*?>', '', content)
        
        # HTML 태그 제거
        content = re.sub(r'<[^>]+>', '', content)
        
        # 연속 공백 및 줄바꿈 정리
        content = re.sub(r'\s+', ' ', content)
        content = re.sub(r'\n\s*\n', '\n', content)
        
        # 앞뒤 공백 제거
        content = content.strip()
        
        return content
    
    def search_laws(self, query):
        """법령 검색 (디버깅 강화)"""
        params = {
            "OC": "ssswut",
            "target": "law", 
            "query": query,
            "type": "XML"
        }
        
        try:
            print(f"🔍 법령 검색 시작: '{query}'")
            response = requests.get(self.search_url, params=params, timeout=10)
            print(f"📡 검색 응답 상태: {response.status_code}")
            
            if response.status_code == 200:
                # 검색 결과 XML 저장
                self.save_debug_xml(response.text, f"search_{query}")
                return self.parse_search_results(response.text)
            else:
                print(f"❌ 검색 실패: HTTP {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ 검색 API 오류: {e}")
            return []
    
    def get_law_detail(self, law_id, law_name=""):
        """법령 상세 조문 가져오기 (디버깅 강화)"""
        params = {
            "OC": "ssswut",
            "target": "law",
            "ID": law_id,
            "type": "XML"
        }
        
        try:
            print(f"📋 상세 조회 시작: {law_name} (ID: {law_id})")
            response = requests.get(self.detail_url, params=params, timeout=15)
            print(f"📡 상세 조회 응답 상태: {response.status_code}")
            
            if response.status_code == 200:
                # 상세 조회 XML 저장
                filename = f"detail_{law_id}_{law_name.replace(' ', '_')}"
                self.save_debug_xml(response.text, filename)
                
                # XML 구조 분석
                structure_info = self.analyze_xml_structure(response.text)
                
                # 파싱 시도
                return self.parse_law_detail_debug(response.text)
            else:
                print(f"❌ 상세 조회 실패: HTTP {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ 상세 조회 API 오류: {e}")
            return []
    
    def parse_search_results(self, xml_text):
        """XML 검색 결과 파싱"""
        try:
            root = ET.fromstring(xml_text)
            laws = []
            
            for law in root.findall('.//law'):
                law_name_elem = law.find('법령명한글')
                law_type_elem = law.find('법령구분명')
                law_id_elem = law.find('법령ID')
                
                if law_name_elem is not None and law_id_elem is not None:
                    law_info = {
                        'id': law_id_elem.text,
                        'name': law_name_elem.text,
                        'type': law_type_elem.text if law_type_elem is not None else '법령'
                    }
                    laws.append(law_info)
                    print(f"✅ 검색된 법령: {law_info['name']} (ID: {law_info['id']})")
            
            print(f"🎯 총 검색된 법령: {len(laws)}개")
            return laws[:3]  # 최대 3개만
        except Exception as e:
            print(f"❌ 검색 결과 파싱 오류: {e}")
            return []
    
    def parse_law_detail_debug(self, xml_text):
        """디버깅이 강화된 법령 상세 파싱"""
        try:
            root = ET.fromstring(xml_text)
            articles = []
            
            # 조문단위 태그 찾기
            article_units = root.findall('.//조문단위')
            print(f"\n🔍 조문단위 발견: {len(article_units)}개")
            
            for i, article in enumerate(article_units):
                print(f"\n--- 📋 조문 {i+1} 상세 분석 ---")
                
                # 모든 하위 태그 출력
                child_info = {}
                for child in article:
                    content_preview = (child.text[:50] + "...") if child.text and len(child.text) > 50 else (child.text or "None")
                    child_info[child.tag] = child.text
                    print(f"  {child.tag}: {content_preview}")
                
                # 파싱 시도
                number_elem = article.find('조문번호')
                title_elem = article.find('조문제목')
                content_elem = article.find('조문내용')
                type_elem = article.find('조문여부')
                
                number = number_elem.text if number_elem is not None else ""
                title = title_elem.text if title_elem is not None else ""
                raw_content = content_elem.text if content_elem is not None else ""
                article_type = type_elem.text if type_elem is not None else ""
                
                print(f"🎯 파싱 결과:")
                print(f"  번호: '{number}'")
                print(f"  제목: '{title}'")
                print(f"  타입: '{article_type}'")
                print(f"  원본 내용 길이: {len(raw_content)}")
                
                # 내용 정제
                cleaned_content = self.clean_article_content(raw_content)
                print(f"  정제된 내용 길이: {len(cleaned_content)}")
                print(f"  정제된 내용 미리보기: {cleaned_content[:100]}...")
                
                # 조문 추가 조건 확인
                should_include = False
                exclude_reasons = []
                
                if article_type != "조문":
                    exclude_reasons.append(f"타입이 '조문'이 아님: '{article_type}'")
                elif not cleaned_content.strip():
                    exclude_reasons.append("정제된 내용이 비어있음")
                elif len(cleaned_content.strip()) < 10:
                    exclude_reasons.append(f"내용이 너무 짧음: {len(cleaned_content)}자")
                else:
                    should_include = True
                
                if should_include:
                    article_info = {
                        'number': number,
                        'title': title,
                        'content': cleaned_content,
                        'type': article_type,
                        'raw_content_length': len(raw_content),
                        'cleaned_content_length': len(cleaned_content)
                    }
                    articles.append(article_info)
                    print(f"✅ 조문 포함됨: 제{number}조")
                else:
                    print(f"❌ 조문 제외됨: {', '.join(exclude_reasons)}")
            
            print(f"\n🎯 최종 파싱된 조문 수: {len(articles)}개")
            return articles
            
        except Exception as e:
            print(f"❌ 상세 파싱 오류: {e}")
            import traceback
            traceback.print_exc()
            return []

def extract_keywords(question):
    """질문에서 키워드 추출 (개선된 버전)"""
    keywords = []
    
    # 복합 키워드 우선 처리
    compound_keywords = ['산업단지', '공공주택', '국가산업단지', '일반산업단지', '도시첨단산업단지']
    for keyword in compound_keywords:
        if keyword in question:
            keywords.append(keyword)
    
    # 단일 키워드 처리 (복합 키워드가 없을 때만)
    if not keywords:
        single_keywords = ['주택', '산업', '임대', '분양']
        for keyword in single_keywords:
            if keyword in question:
                keywords.append(keyword)
    
    # 키워드가 여전히 없으면 질문의 첫 단어들 사용
    if not keywords:
        words = question.split()
        keywords = [word for word in words[:2] if len(word) > 1]
    
    print(f"🔍 추출된 키워드: {keywords}")
    return keywords[:2]  # 최대 2개 키워드만

def analyze_question_type(question):
    """질문 유형 분석"""
    question_lower = question.lower()
    
    if any(word in question_lower for word in ['종류', '분류', '구분', '유형']):
        return 'classification'
    elif any(word in question_lower for word in ['지정', '선정', '결정', '권자']):
        return 'authority'
    elif any(word in question_lower for word in ['절차', '과정', '방법']):
        return 'process'
    elif any(word in question_lower for word in ['요건', '조건', '기준']):
        return 'requirements'
    elif any(word in question_lower for word in ['정의', '의미', '개념']):
        return 'definition'
    else:
        return 'general'

def find_relevant_articles(articles, question, question_type, question_keywords):
    """질문 유형에 따른 관련 조문 찾기"""
    if not articles:
        return []
    
    relevant_articles = []
    question_lower = question.lower()
    
    # 질문 유형별 키워드 매칭
    type_keywords = {
        'classification': ['종류', '분류', '구분', '유형', '정의'],
        'authority': ['지정', '선정', '결정', '권자', '장관', '시장', '지사'],
        'process': ['절차', '과정', '방법', '신청', '승인'],
        'requirements': ['요건', '조건', '기준', '자격'],
        'definition': ['정의', '의미', '개념']
    }
    
    target_keywords = type_keywords.get(question_type, ['정의'])
    
    # 조문 점수 계산
    article_scores = []
    for article in articles:
        score = 0
        title = article.get('title', '').lower()
        content = article.get('content', '').lower()
        number = article.get('number', '')
        
        # 제목 매칭 (높은 가중치)
        for keyword in target_keywords:
            if keyword in title:
                score += 10
        
        # 내용 매칭 (중간 가중치)
        for keyword in target_keywords:
            score += content.count(keyword) * 3
        
        # 정의조 우선 처리
        if '정의' in title or number in ['1', '2']:
            score += 5
        
        # 질문의 핵심 키워드 매칭 (이미 추출된 키워드 사용)
        for q_keyword in question_keywords:
            if q_keyword in title:
                score += 8
            if q_keyword in content:
                score += content.count(q_keyword) * 2
        
        if score > 0:
            article_scores.append((article, score))
    
    # 점수순 정렬
    article_scores.sort(key=lambda x: x[1], reverse=True)
    
    # 상위 조문 선택 (최대 3개)
    relevant_articles = [article for article, score in article_scores[:3]]
    
    # 관련 조문이 없으면 처음 2개 조문 반환
    if not relevant_articles and articles:
        relevant_articles = articles[:2]
    
    print(f"🎯 관련 조문 선별: {len(relevant_articles)}개")
    for i, article in enumerate(relevant_articles):
        print(f"  {i+1}. 제{article.get('number')}조 {article.get('title')}")
    
    return relevant_articles

def generate_law_based_answer(question, laws_with_articles, question_keywords):
    """실제 법령 조문을 기반으로 답변 생성 (개선된 버전)"""
    if not laws_with_articles:
        return f"'{question}'에 대한 관련 법령을 찾을 수 없습니다. 더 구체적인 질문을 해주세요."
    
    # 질문 유형 분석
    question_type = analyze_question_type(question)
    print(f"🤔 질문 유형: {question_type}")
    
    answer = f"**질문:** {question}\n\n**답변:**\n"
    
    total_articles_found = 0
    
    for law_info in laws_with_articles:
        law_name = law_info['name']
        articles = law_info.get('articles', [])
        
        if not articles:
            print(f"❌ {law_name}: 조문 없음")
            continue
        
        print(f"📚 {law_name}: {len(articles)}개 조문 분석")
        
        # 질문과 관련된 조문 찾기 (이미 추출된 키워드 사용)
        relevant_articles = find_relevant_articles(articles, question, question_type, question_keywords)
        print(f"🔍 {law_name}: 관련 조문 {len(relevant_articles)}개 찾음")
        if relevant_articles:
            print(f"  - 제{relevant_articles[0].get('number')}조: {relevant_articles[0].get('title')}")
        else:
            print(f"  - 관련 조문 없음, 전체 조문 {len(articles)}개 중에서 선택")
        
        if relevant_articles:
            answer += f"\n**{law_name}에 따르면:**\n"
            
            for article in relevant_articles:
                number = article.get('number', '')
                title = article.get('title', '')
                content = article.get('content', '')
                
                if content:
                    # 내용이 너무 길면 핵심 부분만 추출
                    if len(content) > 400:
                        sentences = content.split('.')
                        important_sentences = []
                        
                        # 질문 키워드가 포함된 문장 우선 선택
                        for sentence in sentences:
                            if any(keyword in sentence for keyword in question_keywords):
                                important_sentences.append(sentence.strip())
                        
                        # 중요 문장이 없으면 처음 2-3 문장 사용
                        if not important_sentences:
                            important_sentences = sentences[:3]
                        
                        content = '. '.join(important_sentences[:3]) + ('.' if important_sentences else '')
                    
                    answer += f"\n**제{number}조 ({title}):**\n"
                    answer += f"{content}\n"
                    total_articles_found += 1
        else:
            # 관련 조문이 없으면 처음 2개 조문 사용
            print(f"⚠️ {law_name}: 관련 조문 없음, 처음 2개 조문 사용")
            for article in articles[:2]:
                number = article.get('number', '')
                title = article.get('title', '')
                content = article.get('content', '')
                
                if content:
                    if len(content) > 400:
                        content = content[:400] + "..."
                    
                    answer += f"\n**제{number}조 ({title}):**\n"
                    answer += f"{content}\n"
                    total_articles_found += 1
    
    if total_articles_found == 0:
        answer += "\n조문 내용을 정상적으로 파싱할 수 없었습니다. API 응답을 확인 중입니다."
    
    answer += f"\n**법적 근거:** 위 조문들은 국가법령정보센터에서 제공하는 현행 법령입니다."
    answer += f"\n**국가법령정보센터:** https://www.law.go.kr"
    answer += f"\n\n*총 {total_articles_found}개 조문 기반 답변*"
    
    return answer

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask_question():
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({'error': '질문을 입력해주세요.'})
        
        print(f"\n🤔 새로운 질문: {question}")
        print("=" * 60)
        
        # 1. 키워드 추출
        keywords = extract_keywords(question)
        
        # 2. 질문 유형 분석
        question_type = analyze_question_type(question)
        
        # 3. 법령 API 초기화
        law_api = LawAPI()
        laws_with_articles = []
        
        # 4. 각 키워드로 법령 검색 및 상세 조문 가져오기
        for keyword in keywords:
            print(f"\n🔍 키워드 '{keyword}' 검색 중...")
            laws = law_api.search_laws(keyword)
            
            for law in laws:
                print(f"\n📖 법령 상세 조회: {law['name']}")
                articles = law_api.get_law_detail(law['id'], law['name'])
                
                if articles:
                    law_with_articles = {
                        'id': law['id'],
                        'name': law['name'],
                        'type': law['type'],
                        'articles': articles
                    }
                    laws_with_articles.append(law_with_articles)
                    print(f"✅ {law['name']}: {len(articles)}개 조문 수집 완료")
                    break  # 키워드당 첫 번째 법령만 상세 조회
        
        # 5. 실제 법령 조문 기반 답변 생성
        if laws_with_articles:
            answer = generate_law_based_answer(question, laws_with_articles, keywords)
            print(f"\n✅ 답변 생성 완료")
        else:
            answer = f"""'{question}'에 대한 관련 법령을 찾을 수 없습니다.

다음과 같이 구체적으로 질문해주세요:
- "산업단지 종류는 무엇인가요?"
- "공공주택 지정권자는 누구인가요?" 
- "○○법 제○조 내용을 알려주세요"

**국가법령정보센터:** https://www.law.go.kr

💡 검색된 키워드: {', '.join(keywords)}
💡 질문 유형: {analyze_question_type(question)}"""
            print(f"❌ 관련 법령 없음")
        
        # 6. 법령 목록 정리 (응답용)
        law_list = []
        for law_info in laws_with_articles:
            law_list.append({
                'name': law_info['name'],
                'type': law_info['type'],
                'article_count': len(law_info['articles'])
            })
        
        print("=" * 60)
        print(f"🎯 응답 완료: {len(law_list)}개 법령, {sum(l['article_count'] for l in law_list)}개 조문")
        
        return jsonify({
            'answer': answer,
            'laws': law_list,
            'keywords': keywords,
            'question_type': analyze_question_type(question),
            'debug_info': {
                'total_laws': len(law_list),
                'total_articles': sum(l['article_count'] for l in law_list)
            }
        })
        
    except Exception as e:
        print(f"❌ 전체 오류: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'답변 생성 중 오류가 발생했습니다: {str(e)}'})

if __name__ == '__main__':
    print("🚀 법령 질의응답 시스템 시작 (디버깅 모드)")
    print("📋 XML 파일들이 프로젝트 폴더에 저장됩니다")
    app.run(debug=True)