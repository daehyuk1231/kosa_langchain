import logging

from api.sec09_multi_agent.langgraph.agents.tech_support_agent import TechSupportAgent
from api.sec09_multi_agent.langgraph.state import ShareState

# 로거 생성
logger = logging.getLogger(__name__)

# 모듈 싱글톤 에이전트 생성
agent = TechSupportAgent()

# 기술 지원 노드 정의
async def tech_support_node(state: ShareState) -> dict:
    logger.info("기술 지원 노드 실행")
    # Agent 실행하여 최종 답변 생성
    response = await agent.run(
        inquiry=state["user_inquiry"],
        analysis=state["inquiry_analysis"],
        user_info=state["user_info"],
        knowledge=state["knowledge_base"]
    )    
    # 상태 업데이트: 최종 답변 저장
    return { "final_response": response }