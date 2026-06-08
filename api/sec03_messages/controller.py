import logging
from typing import Annotated
from fastapi import APIRouter, Form
from fastapi.responses import PlainTextResponse, StreamingResponse
from api.sec03_messages.service import ChatServiceDep

# 로거 생성
logger = logging.getLogger(__name__)

# 라우터 생성
router = APIRouter(prefix="/sec03", tags=["sec03"])

# 엔드포인트 정의
@router.post("/chat-with-system", response_class=PlainTextResponse)
async def chat_model(
    question: Annotated[str, Form()],
    chat_service: ChatServiceDep
):
    response = await chat_service.chat(question)
    return response

@router.post("/chat-with-system-stream", response_class=StreamingResponse)
async def chat_model_stream(
    question: Annotated[str, Form()],
    chat_service: ChatServiceDep
):
    response = StreamingResponse(
        chat_service.chat_stream(question),
        media_type="application/x-ndjson"
    )
    return response