import logging
import os
from typing import Annotated, Any
from bs4 import BeautifulSoup
from fastapi import Depends
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults
import requests

# 로거 생성
logger = logging.getLogger(__name__)

# Tavily API 키 확인
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
if not TAVILY_API_KEY:
    logger.info("TAVILY_API_KEY 환경 변수가 설정되지 않았음")

###############################################################
# 도구 정의
###############################################################
@tool
def search_web(query: str, max_results: int = 5) -> list[dict[str, Any]]:
    """
    웹에서 키워드를 검색하여 관련 페이지 목록을 제공합니다.
    실시간 웹 검색을 수행합니다.
    검색 결과로 제목, URL, 요약 내용을 제공합니다.
    Args:
        query: 검색할 키워드
        max_results: 최대 결과 개수 (기본값: 5)
    Returns:
        list[dict[str, Any]]: 검색 결과 목록 (url, title, content, score)
        예시:
        [ {"url": "링크", "title": "제목", "content": "내용", "score": "점수"}, ... ]
    """
    logger.info(f"search_web({query}) 호출")
    
    # Tavily 검색을 위한 객체 생성
    tavily_search = TavilySearchResults(
        max_results=max_results,
        search_depth="basic"
    )
    
    # 검색 결과 가져오기
    results = tavily_search.invoke(query)
    # [ {"url": "링크", "title": "제목", "content": "내용", "score": "점수"}, ... ]
    return results

@tool
def fetch_webpage(url: str) -> str:
    """특정 URL의 웹페이지 내용을 가져와서 파싱합니다.    
    HTTP 요청으로 웹페이지를 가져온 후 파싱하여 텍스트 내용만 추출합니다. 
    검색 결과에서 특정 페이지의 상세 내용이 필요할 때 사용합니다.    
    Args:
        url: 가져올 웹페이지 URL        
    Returns:
        str: 파싱된 웹페이지의 텍스트 내용
    """
    logger.info(f"fetch_webpage({url}) 호출")
    
    # URL 검증
    if not url.startswith(("http://", "https://")):
        return ("오류: 유효하지 않은 URL 형식입니다. " 
                "URL은 http:// 또는 https://로 시작해야 합니다.")
    
    # HTTP 요청 헤더 설정
    # 많은 웹사이트가 봇 차단 정책을 가지고 있기 때문에, User-Agent가 없는 요청을 차단할 수 있음
    # 브라우저의 User-Agent와 동일하게 설정하면 브라우저에서 요청하는 것 처럼 가장할 수 있으므로 
    # 차단을 우회할 수 있음.
    headers = {
        'User-Agent': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/91.0.4472.124 Safari/537.36'
        )
    }

    # 요청 헤더 및 타임아웃 설정하고 GET 방식으로 요청
    response = requests.get(url, headers=headers, timeout=15)

    # HTTP 응답 상태를 확인하고 자동으로 예외를 발생시킴(400번대, 500번대 등)
    response.raise_for_status()

    # HTML 파싱
    soup = BeautifulSoup(response.content, 'html.parser')

    # 불필요한 태그 제거
    for tag in soup(['script', 'style', 'nav', 'footer', 'header', 
                        'aside', 'iframe', 'noscript']):
        # 태그와 그 안의 내용 전체를 제거
        tag.decompose()

    # 모든 태그를 제거하고 순수 텍스트만 추출
    # separator='\n': 태그 사이의 텍스트 조각을 연결할 때 사용할 구분자
    # strip=True: 텍스트 조각의 앞뒤 공백 제거
    text = soup.get_text(separator='\n', strip=True)

    # 문자열을 줄 단위로 분리하고, 공백 제거후, 빈문자열이 아닌것만 리스트에 포함
    text_content = '\n'.join(
        line.strip() for line in text.splitlines() if line.strip()
    )

    # 컨텐츠 길이 제한 (너무 길면 잘라냄)
    max_length = 8000
    if len(text_content) > max_length:
        text_content = (text_content[:max_length] + 
                        "\n\n... (내용이 너무 길어 일부만 표시됨. 전체 내용은 " 
                        + url + " 에서 확인하세요.)")
        
    # 결과 반환 (URL과 함께)
    result = f"URL: {url}\n{'='*80}\n\n{text_content}"
    return result

###############################################################
# Agent 클래스 정의
###############################################################
class InternetSearchAgent:
    def __init__(self, model:str="openai:gpt-4o-mini") -> None:
        self.logger = logging.getLogger(f"{__name__}.InternetSearchAgent")
        self.agent = create_agent(
            model=model,
            tools=[search_web, fetch_webpage]
        )
        self.system_message = """
            당신은 인터넷 검색 및 웹페이지 분석 전문가입니다.            
            
            [사용 가능한 도구]            
            1. **search_web**: 키워드로 웹 검색
            - 웹페이지 목록을 가져옵니다
            - 각 결과에는 제목, URL, 요약 내용이 포함됩니다
            - 처음에 정보를 찾을 때 사용하세요
            
            2. **fetch_webpage**: 특정 URL의 내용 가져오기
            - URL을 입력받아 해당 웹페이지의 전체 내용을 가져옵니다
            - HTTP 요청 후 HTML을 파싱하여 텍스트만 추출합니다
            - 검색 결과 중 특정 페이지의 상세 내용이 필요할 때 사용하세요
            
            [작업 흐름]
            1. 먼저 search_web으로 관련 페이지들을 검색합니다
            2. 검색 결과의 요약만으로 답변이 가능하면 그대로 답변합니다
            3. 더 상세한 내용이 필요하면 fetch_webpage로 특정 URL의 전체 내용을 가져옵니다
            
            출처 URL을 명시하여 신뢰성 있는 답변을 제공하세요.
        """

    async def run(self, question: str) -> str:
        result = await self.agent.ainvoke(
            {"messages": [
                {"role":"system", "content": self.system_message},
                {"role":"user", "content": question}]}
        )
        
        return result["messages"][-1].content
    
# 의존성 주입을 위한 타입 힌트 정의
InternetSearchAgentDep = Annotated[InternetSearchAgent, Depends(InternetSearchAgent)]