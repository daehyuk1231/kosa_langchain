import logging
from typing import Annotated
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