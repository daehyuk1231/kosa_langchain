import logging

from api.sec09_multi_agent.langgraph.state import ShareState

# 로거 생성
logger = logging.getLogger(__name__)

# 사용자 정보 조회 노드 정의
async def user_info_node(state: ShareState) -> dict:
    logger.info("사용자 정보 조회 노드 실행")
    
    # 상태에서 사용자 ID 가져오기
    user_id = state["user_id"]
    # ... 데이터베이스에서 사용자 정보 가져오기(에이전트 이용)
    user_info = "홍길동"
    
    # 상태 업데이트
    return {"user_info": user_info}