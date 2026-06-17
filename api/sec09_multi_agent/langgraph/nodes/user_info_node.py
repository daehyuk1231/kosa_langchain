import logging

from api.sec09_multi_agent.langgraph.agents.user_info_agent import UserInfoAgent
from api.sec09_multi_agent.langgraph.state import ShareState

# 로거 생성
logger = logging.getLogger(__name__)

# 모델 싱글톤으로 에이전트 생성
agent = UserInfoAgent()

# 사용자 정보 조회 노드 정의
async def user_info_node(state: ShareState) -> dict:
    logger.info("사용자 정보 조회 노드 실행")
    
    # 상태에서 사용자 ID 가져오기
    user_id = state["user_id"]
    
    # 에이전트를 실행해서 사용자 정보 가져오기
    user_info = await agent.run(user_id)
    logger.info(f"user_info: {user_info}")
    
    # 상태 업데이트
    return {"user_info": user_info}