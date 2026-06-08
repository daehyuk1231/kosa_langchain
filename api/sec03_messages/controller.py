import logging
from typing import Annotated
from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse, PlainTextResponse, StreamingResponse
from api.sec03_messages.service import CoTServiceDep, FewShotServiceDep, RoleServiceDep, SelfConsistencyServiceDep, StepBackServiceDep
import json

# 로거 생성
logger = logging.getLogger(__name__)

# 라우터 생성
router = APIRouter(prefix="/sec03", tags=["sec03"])

# 엔드포인트 정의--------------------------------------------------------------
@router.post("/chat-with-system", response_class=PlainTextResponse)
async def chat_model(
    question: Annotated[str, Form()],
    chat_service: RoleServiceDep
):
    response = await chat_service.chat(question)
    return response
# -------------------------------------------------------------------------
@router.post("/chat-with-system-stream", response_class=StreamingResponse)
async def chat_model_stream(
    question: Annotated[str, Form()],
    chat_service: RoleServiceDep
):
    response = StreamingResponse(
        chat_service.chat_stream(question),
        media_type="application/x-ndjson"
    )
    return response
# -------------------------------------------------------------------------
@router.post("/few-shot-prompt", response_class=JSONResponse)
async def few_shot_prompt(
    order: Annotated[str, Form()],
    service: FewShotServiceDep
):
    json_text = await service.chat(order)
    dict_content = json.loads(json_text)
    return JSONResponse(dict_content)
# -------------------------------------------------------------------------
@router.post("/step-back-prompt", response_class=PlainTextResponse)
async def step_back_prompt(
    question: Annotated[str, Form()],
    service: StepBackServiceDep
):
    response = await service.chat(question)
    return response
# -------------------------------------------------------------------------
@router.post("/chain-of-thought", response_class=StreamingResponse)
async def chain_of_thought(
    question: Annotated[str, Form()],
    service: CoTServiceDep
):
    response = StreamingResponse(
        service.chat(question),
        media_type="application/x-ndjson"
    )
    return response
# -------------------------------------------------------------------------
@router.post("/self-consistency", response_class=PlainTextResponse)
async def self_consistency(
    content: Annotated[str, Form()],
    service: SelfConsistencyServiceDep
):
    response = await service.chat(content)
    return response