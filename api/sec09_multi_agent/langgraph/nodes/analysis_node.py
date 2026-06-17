import logging

from api.sec09_multi_agent.langgraph.agents.analysis_agent import AnalysisAgent
from api.sec09_multi_agent.langgraph.state import ShareState

# 로거 생성
logger = logging.getLogger(__name__)

# 모듈 싱글톤 에이전트 생성
agent = AnalysisAgent()

# 문의 분석 노드 정의
async def analysis_node(state: ShareState) -> dict:
    logger.info("문의 분석 노드 실행")
    
    # 상태에서 고객 문의 내용 가져오기
    inquiry = state["user_inquiry"]
    
    # 에이전트를 실행하여 분석 결과 얻기
    inquiry_analysis = await agent.run(inquiry)
    
    # 상태 업데이트: 분석 결과 저장
    return {"inquiry_analysis": inquiry_analysis}