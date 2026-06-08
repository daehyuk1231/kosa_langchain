import logging
from typing import Annotated
from fastapi import APIRouter, Form
from fastapi.responses import PlainTextResponse

from api.sec05_create_agent.agent_chat import ChatAgentDep

# 로거 생성
logger = logging.getLogger(__name__)

# 라우터 생성
router = APIRouter(prefix="/sec05", tags=["sec05"])

############################################################
# Agent를 사용하는 대화 엔드포인트
############################################################
@router.post("/agent-chat", response_class=PlainTextResponse)
async def agent_chat(
    question: Annotated[str, Form()],
    agent: ChatAgentDep
):
    # Agent 실행
    response = await agent.run(question)
    # 반환
    return response