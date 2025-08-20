// DOM 요소 선택
const questionInput = document.getElementById('questionInput');
const askButton = document.getElementById('askButton');
const resultsSection = document.getElementById('resultsSection');
const answerContent = document.getElementById('answerContent');
const sourcesContent = document.getElementById('sourcesContent');
const errorMessage = document.getElementById('errorMessage');
const spinner = document.getElementById('spinner');

// 질문하기 함수
async function askQuestion() {
    const question = questionInput.value.trim();
    
    if (!question) {
        showError('질문을 입력해주세요.');
        return;
    }
    
    // UI 상태 변경
    setLoadingState(true);
    hideError();
    hideResults();
    
    try {
        const response = await fetch('/ask', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ question: question })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.error) {
            showError(data.error);
        } else {
            displayResults(data);
        }
        
    } catch (error) {
        console.error('Error:', error);
        showError('서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.');
    } finally {
        setLoadingState(false);
    }
}

// 결과 표시 함수
function displayResults(data) {
    // 답변 표시
    answerContent.innerHTML = formatAnswer(data.answer);
    
    // 근거 법령 표시
    sourcesContent.innerHTML = formatSources(data.sources);
    
    // 결과 섹션 표시
    resultsSection.style.display = 'block';
    
    // 결과로 스크롤
    resultsSection.scrollIntoView({ 
        behavior: 'smooth',
        block: 'start'
    });
}

// 답변 형식화
function formatAnswer(answer) {
    // 개행 문자를 <br>로 변환하고 HTML 이스케이프
    return answer
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/\n/g, '<br>');
}

// 근거 법령 형식화
function formatSources(sources) {
    if (!sources || sources.length === 0) {
        return '<p>관련 법령 정보를 찾을 수 없습니다.</p>';
    }
    
    return sources.map(source => `
        <div class="source-item">
            <h4>${escapeHtml(source.law_name)}</h4>
            <div class="law-info">
                <span>구분: ${escapeHtml(source.law_type)}</span>
                ${source.law_number ? ` | 번호: ${escapeHtml(source.law_number)}` : ''}
            </div>
        </div>
    `).join('');
}

// HTML 이스케이프 함수
function escapeHtml(text) {
    if (!text) return '';
    return text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

// 로딩 상태 설정
function setLoadingState(isLoading) {
    askButton.disabled = isLoading;
    
    if (isLoading) {
        spinner.style.display = 'block';
        askButton.querySelector('.button-text').style.display = 'none';
    } else {
        spinner.style.display = 'none';
        askButton.querySelector('.button-text').style.display = 'inline';
    }
}

// 에러 메시지 표시
function showError(message) {
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
    errorMessage.scrollIntoView({ 
        behavior: 'smooth',
        block: 'center'
    });
}

// 에러 메시지 숨기기
function hideError() {
    errorMessage.style.display = 'none';
}

// 결과 섹션 숨기기
function hideResults() {
    resultsSection.style.display = 'none';
}

// 예시 질문 설정
function setQuestion(question) {
    questionInput.value = question;
    questionInput.focus();
    
    // 자동으로 질문하기 (선택사항)
    // askQuestion();
}

// 엔터키로 질문하기
questionInput.addEventListener('keydown', function(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        askQuestion();
    }
});

// 페이지 로드 시 초기화
document.addEventListener('DOMContentLoaded', function() {
    questionInput.focus();
    
    // 환경 변수 체크 (개발용)
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        console.log('개발 모드에서 실행 중입니다.');
        console.log('API 키가 설정되어 있는지 확인하세요.');
    }
});

// 법령 검색 함수 (추가 기능)
async function searchLaws(query) {
    try {
        const response = await fetch('/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query: query })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        return data.laws || [];
        
    } catch (error) {
        console.error('법령 검색 오류:', error);
        return [];
    }
}

// 자동완성 기능 (향후 구현 가능)
function initAutoComplete() {
    // TODO: 검색어 자동완성 기능 구현
}

// 검색 기록 관리 (향후 구현 가능)
function saveSearchHistory(question, answer) {
    // TODO: 로컬 스토리지에 검색 기록 저장
}

function loadSearchHistory() {
    // TODO: 로컬 스토리지에서 검색 기록 불러오기
}
