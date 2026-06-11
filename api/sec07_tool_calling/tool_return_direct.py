import logging
import json
from typing import Annotated, List
from fastapi import Depends
from langchain.agents import create_agent
from langchain.tools import tool

# 로거 설정
logger = logging.getLogger(__name__)

##############################################################
# Agent 전용 도구들
##############################################################
@tool
def get_movie_list_by_user_id(user_id: str) -> List[str]:
    """사용자가 관람한 영화 목록을 제공합니다.
    Args:
        user_id: 사용자 ID
    Returns:
        List[str]: 사용자가 관람한 영화 목록
    """
    logger.info(f"get_movie_list_by_user_id({user_id}) 호출")
    # 데이터베이스에서 검색해서 가져온 내용 (시뮬레이션)
    movies = [
        "엣지오브투모로우", "투모로우", "아이언맨", "혹성탈출", "타이타닉", "엘리시움",
        "인터스텔라", "아바타", "마션"
    ]
    logger.info(f"사용자 {user_id}의 관람 영화 목록: {movies}")
    return movies

# return_direct=True 옵션을 사용하여 도구의 반환값이 Agent의 응답 메시지로 직접 반환되도록 설정
@tool
def recommend_movie(genre: str) -> dict:
    """주어진 장르의 추천 영화 목록을 제공합니다.    
    Args:
        genre: 영화 장르        
    Returns:
        dict: 추천 영화 정보
    """
    logger.info(f"recommend_movie({genre}) 호출")
    # 데이터베이스에서 검색해서 가져온 내용 (시뮬레이션)
    movies = ["크레이븐", "베놈", "메이드"]    
    # 딕셔너리 형식으로 반환
    return {"genre": genre, "movies": movies}

##############################################################
# Agent 클래스
##############################################################
class RecommendMovieAgent:
    # 초기화 메소드
    def __init__(self, model: str = "openai:gpt-4o-mini"):
        self.logger = logging.getLogger(f"{__name__}.RecommendMovieAgent")
        self.agent = create_agent(
            model=model,
            tools=[get_movie_list_by_user_id, recommend_movie]
        )
        
    
    # 에이전트 실행 메소드
    async def run(self, question: str) -> str:
        """사용자 질문에 대한 답변을 생성합니다.
        Args:
            question: 사용자 질문
        Returns:
            str: Agent의 응답 메시지 (문자열 또는 JSON 문자열)
        """
        result = await self.agent.ainvoke(
            {"messages": [{"role": "user", "content": question}]}
        )
        return result["messages"][-1].content


##############################################################
# 의존성 타입 별칭 정의
##############################################################
RecommendMovieAgentDep = Annotated[RecommendMovieAgent, Depends(RecommendMovieAgent)]