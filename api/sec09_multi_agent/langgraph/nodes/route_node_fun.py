import json
import logging
from ..state import ShareState

# 로거 설정
logger = logging.getLogger(__name__)

# 조건 분기 함수 정의
def route_node_fun(state: ShareState) -> str:
    logger.info("조건 분기 함수 실행")
    # 상태에서 문의 유형 추출
    inquiry_analysis = json.loads(state.get("inquiry_analysis", "{}"))
    inquiry_type = inquiry_analysis.get("inquiry_type", "일반문의")
    # 문의 유형에 따라 전문 Agent로 라우팅
    if inquiry_type == "기술지원":
        return "tech_support"
    elif inquiry_type == "주문/배송":
        return "order"
    elif inquiry_type == "환불/교환":
        return "refund"
    elif inquiry_type == "계정관리":
        return "account"
    else:
        return "general"