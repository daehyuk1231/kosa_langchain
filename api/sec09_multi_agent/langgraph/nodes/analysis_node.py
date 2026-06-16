import logging

from api.sec09_multi_agent.langgraph.state import ShareState

# 로거 생성
logger = logging.getLogger(__name__)

# 문의 분석 노드 정의
async def analysis_node(state: ShareState) -> dict:
    logger.info("문의 분석 노드 실행")
    
    # 상태에서 고객 문의 내용 가져오기
    inquiry = state["user_inquiry"]
    # ... 분석 작업(에이전트 이용)
    
    # 상태 업데이트: 분석 결과 저장
    return {"inquiry_analysis": "분석 결과"}