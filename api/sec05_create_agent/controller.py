import logging
from typing import Annotated
from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse, PlainTextResponse, StreamingResponse

from api.sec04_structured_output.model import Movie
from api.sec05_create_agent.agent_chat import ChatAgentDep
from api.sec05_create_agent.agent_chat_stream import ChatStreamAgentDep
from api.sec05_create_agent.agent_structured_output import StructuredOutputAgentDep

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
    logger.info("/sec05/agent-chat 엔드포인트 실행")
    # Agent 실행
    response = await agent.run(question)
    # 반환
    return response

@router.post("/agent-chat-stream", response_class=StreamingResponse)
async def agent_chat_stream(
    question: Annotated[str, Form()],
    agent: ChatStreamAgentDep
):
    async_generator = agent.run(question)

    return StreamingResponse(
        content=async_generator,
        media_type="application/x-ndjson"
    )
    
# ---------------------------------------------------------
@router.post("/agent-structured-output",
             response_class=JSONResponse,
             response_model=Movie)
async def agent_structured_output(
    content: Annotated[str, Form()],
    agent: StructuredOutputAgentDep
):
    movie = await agent.run(content)
    return movie