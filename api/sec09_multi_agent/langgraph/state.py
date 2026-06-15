from typing import Annotated, TypedDict

from langgraph.graph import add_messages


class ShareState(TypedDict):
    # 대화 메시지 저장 (필수)
    messages: Annotated[list, add_messages]
    # 고객 원본 문의 내용
    user_inquiry: str
    # 고객 ID
    user_id: str
    # 문의 분석 결과
    inquiry_analysis: str
    # 고객 정보 조회 결과
    user_info: str
    # 지식 베이스(환불정책, 배송정책, 계정정책, ...)
    knowledge_base: str
    # 최종 응답 내용
    final_response: str