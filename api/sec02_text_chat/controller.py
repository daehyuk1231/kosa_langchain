import logging
from typing import Annotated

from fastapi import APIRouter, Form
from fastapi.responses import PlainTextResponse, StreamingResponse

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage

from api.sec02_text_chat.service import ChatServiceDep

# 로거 생성
logger = logging.getLogger(__name__)

# 라우터 생성
router = APIRouter(prefix="/sec02", tags=["sec02"])

# 엔드포인트 정의
@router.post("/chat-model", response_class=PlainTextResponse)
async def chat_model(
    question: Annotated[str, Form()],
    chat_service: ChatServiceDep
):
    response = await chat_service.chat(question)
    return response

@router.post("/chat-model-stream", response_class=StreamingResponse)
async def chat_model_stream(
    question: Annotated[str, Form()],
    chat_service: ChatServiceDep
):
    response = StreamingResponse(
        chat_service.chat_stream(question),
        media_type="application/x-ndjson"
    )
    return response