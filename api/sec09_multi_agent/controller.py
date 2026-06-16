import logging
from typing import Annotated
from fastapi import APIRouter, Depends, Form
from fastapi.responses import PlainTextResponse, Response

from api.sec09_multi_agent.langgraph.supervisor import CustomerSupportSupervisorDep

# 로거 설정
logger = logging.getLogger(__name__)

# API 라우터 설정
router = APIRouter(prefix="/sec09", tags=["sec09"])

#-------------------------------------------------
# 고객 지원 Multi-Agent API 엔드포인트
#-------------------------------------------------
@router.post("/customer-support", response_class=PlainTextResponse)
async def customer_support(
    inquiry: Annotated[str, Form()],
    supervisor: CustomerSupportSupervisorDep
):
    response = await supervisor.run(inquiry, "user1")
    return response

#-------------------------------------------------
# 고객 지원 Multi-Agent 그래프 구조를 반환 엔드포인트(디버깅용)
#-------------------------------------------------
@router.get("/graph-structure", response_class=Response)
async def get_graph_structure(
    supervisor: CustomerSupportSupervisorDep
):
    graph_image = supervisor.get_graph_image()
    return Response(content=graph_image, media_type="image/png")