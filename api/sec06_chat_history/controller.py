import logging
from fastapi import APIRouter

# 로거 생성
logger = logging.getLogger(__name__)

# 라우터 생성
router = APIRouter(prefix="/sec06", tags=["sec06"])

############################################################
# Agent를 사용하는 대화 엔드포인트
############################################################