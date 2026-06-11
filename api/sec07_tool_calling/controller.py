import json
import logging
from typing import Annotated
from api.sec07_tool_calling.tool_context import HeatingSystemAgentDep
from api.sec07_tool_calling.tool_return_direct import RecommendMovieAgentDep
from api.sec07_tool_calling.tool_web_search import InternetSearchAgentDep
from fastapi import APIRouter, Form, UploadFile
from fastapi.responses import PlainTextResponse

from api.sec07_tool_calling.tool_datetime import DateTimeAgentDep
from api.sec07_tool_calling.tool_file_system import FileSystemAgentDep
from api.sec07_tool_calling.tool_hardware_control import BoomBarrierAgentDep

# 로거 생성
logger = logging.getLogger(__name__)

# 라우터 생성
router = APIRouter(prefix="/sec07", tags=["sec07"])

############################################################
# Agent를 사용하는 대화 엔드포인트
############################################################
@router.post("/tool-datetime", response_class=PlainTextResponse)
async def tool_datetime(
    question: Annotated[str, Form()],
    agent: DateTimeAgentDep
):
    response = await agent.run(question)
    return response

#-----------------------------------------------------------
@router.post("/tool-hardware-control", response_class=PlainTextResponse)
async def tool_hardware_control(
    attach: Annotated[UploadFile, Form()],
    agent: BoomBarrierAgentDep
):
    # 첨부 파일에 대한 정보 얻기
    image_data = await attach.read()
    content_type = attach.content_type
    
    response = await agent.run(image_data, content_type) # type: ignore
    return response
#-----------------------------------------------------------
@router.post("/tool-file-system", response_class=PlainTextResponse)
async def tool_file_system(
    question: Annotated[str, Form()],
    agent: FileSystemAgentDep
):
    response = await agent.run(question)
    return response
#-----------------------------------------------------------
@router.post("/tool-web-search", response_class=PlainTextResponse)
async def tool_web_search(
    question: Annotated[str, Form()],
    agent: InternetSearchAgentDep
):
    response = await agent.run(question)
    return response
#---------------------------------------------------------------------
@router.post("/tool-return-direct")
async def tool_return_direct(
    question: Annotated[str, Form()],
    agent: RecommendMovieAgentDep
):
    response = await agent.run(question)
    logger.info(f"response 타입: {type(response)}, 값: {response}") # str 반환
    # data = json.loads(response)
    return response
#---------------------------------------------------------------------
@router.post("/tool-context", response_class=PlainTextResponse)
async def tool_context(
    question: Annotated[str, Form()],
    agent: HeatingSystemAgentDep
):
    response = await agent.run(question)
    return response