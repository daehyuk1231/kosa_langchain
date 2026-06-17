import logging

from api.sec09_multi_agent.langgraph.agents.order_agent import OrderAgent
from api.sec09_multi_agent.langgraph.state import ShareState

# 로거 생성
logger = logging.getLogger(__name__)

# 모듈 싱글톤 에이전트 생성
agent = OrderAgent()

# 주문/배송 관리 노드 정의
async def order_node(state: ShareState) -> dict:
    logger.info("주문/배송 관리 노드 실행")
    # Agent 실행하여 최종 답변 생성
    response = await agent.run(
        inquiry=state["user_inquiry"],
        analysis=state["inquiry_analysis"],
        user_info=state["user_info"],
        knowledge=state["knowledge_base"]
    )    
    # 상태 업데이트: 최종 답변 저장
    return { "final_response": response }