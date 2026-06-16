import logging

from api.sec09_multi_agent.langgraph.state import ShareState

# 로거 생성
logger = logging.getLogger(__name__)

# 지식 베이스 검색 노드 정의
async def knowledge_node(state: ShareState) -> dict:
    logger.info("지식 베이스 검색 노드 실행")
    
    # 상태에서 사용자 문의 가져오기
    # 지식 베이스 검색 결과 얻기
    knowledge = "약관 내용"
    
    # 상태 업데이트
    return {"knowledge_base": knowledge}