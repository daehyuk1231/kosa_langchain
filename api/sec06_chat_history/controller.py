import logging
from typing import Annotated
from fastapi import APIRouter, Form, Query
from fastapi.responses import JSONResponse, PlainTextResponse
from api.sec06_chat_history.agent_history_inmemory import HistoryInMemoryAgentDep

# 로거 생성
logger = logging.getLogger(__name__)

# 라우터 생성
router = APIRouter(prefix="/sec06", tags=["sec06"])

############################################################
# Agent를 사용하는 대화 엔드포인트
############################################################
@router.post("/chat-history-inmemory",
             response_class=PlainTextResponse)
async def chat_history_inmemory(
    message: Annotated[str, Form()],
    conversation_id: Annotated[str, Form()],
    agent: HistoryInMemoryAgentDep
):
    response = await agent.run(message, conversation_id)
    return response

# 대화 ID의 지난 대화 내용을 응답을 제공
@router.get("/get-history-inmemory", response_class=JSONResponse)
async def get_history_inmemory(
    conversation_id: Annotated[str, Query()],
    agent: HistoryInMemoryAgentDep
):
    history = await agent.get_history(conversation_id)
    return history

# 대화 ID의 지난 대화 내용을 모두 삭제
@router.post("/clear-history-inmemory", response_class=JSONResponse)
async def clear_history_inmemory(
    conversation_id: Annotated[str, Form()],
    agent: HistoryInMemoryAgentDep
):
    result = await agent.clear_history(conversation_id)
    return result