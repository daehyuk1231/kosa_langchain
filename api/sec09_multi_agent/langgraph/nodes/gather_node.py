import logging

from api.sec09_multi_agent.langgraph.state import ShareState

# 로거 설정
logger = logging.getLogger(__name__)

# 병렬 실행 완료 대기 노드 정의
def gather_node(state: ShareState) -> dict:
    logger.info("병렬 실행 완료 대기 노드 실행")    
    # 병렬 처리 결과 얻기
    logger.info(f"user_info: {state["user_info"]}")
    logger.info(f"knowledge_base: {state["knowledge_base"]}")
    return {}