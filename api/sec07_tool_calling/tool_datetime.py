from datetime import datetime, timedelta
import logging
from typing import Annotated
from zoneinfo import ZoneInfo
from fastapi import Depends
from langchain.agents import create_agent
from langchain.tools import tool

from api.common.utils import LoggingCallbackHandler

# 로거 설정
logger = logging.getLogger(__name__)

############################################################
# 도구 정의
############################################################
@tool
def get_current_datetime() -> str:
    """
    현재 날짜와 시간 정보를 제공합니다.
    
    Returns:
        str: ISO-8601 형식의 한국 시간 문자열
    """
    logger.info("실행")
    time_zone = ZoneInfo("Asia/Seoul")
    now_time = datetime.now(time_zone).isoformat()
    logger.info(f"현재 날짜와 시간: {now_time}")
    return now_time

@tool
def set_alarm(time: str) -> str:
    """지정된 시간에 알람을 설정합니다.    
    Args:
        time: ISO-8601 형식의 시간 (예: 2025-07-03T14:30:00+09:00)        
    Returns:
        str: 알람 설정 성공 메시지 또는 실패 시 에러 메시지
    """
    logger.info("실행")
    # LLM이 잘못된 시간 형식을 제공할 수 있음 (예: T24:12:29)
    # ISO-8601에서는 24시는 유효하지 않으므로 0시로 변환하고 날짜를 +1
    if "T24:" in time:
        # "T" 기준으로 날짜와 시간 분리
        t_index = time.index("T")
        date_part = time[:t_index]
        time_part = time[t_index + 1:]        
        # 날짜 +1일
        date_obj = datetime.fromisoformat(date_part)
        date_obj = date_obj + timedelta(days=1)
        date_part = date_obj.strftime("%Y-%m-%d")        
        # "24:" → "00:"으로 교체
        time_part = time_part.replace("24:", "00:", 1)        
        # 재조합
        time = f"{date_part}T{time_part}"    
    # ISO-8601 형식으로 파싱
    alarm_time = datetime.fromisoformat(time)
    logger.info(f"알람 설정 시간: {alarm_time}")
    return f"알람이 {alarm_time.strftime('%Y-%m-%d %H:%M:%S')}에 설정되었습니다."
    
############################################################
# Agent 클래스 정의
############################################################
class DateTimeAgent:
    def __init__(self, model:str="openai:gpt-4o-mini") -> None:
        self.logger = logging.getLogger(f"{__name__}.DateTimeAgent")
        self.agent = create_agent(
            model=model,
            tools=[get_current_datetime, set_alarm]
        )

    async def run(self, question: str) -> str:
        result = await self.agent.ainvoke(
            {"messages": [{"role":"user", "content": question}]},
            {"callbacks":[LoggingCallbackHandler()]}
        )
        
        return result["messages"][-1].content
    
# 의존성 주입을 위한 타입 힌트 정의
DateTimeAgentDep = Annotated[DateTimeAgent, Depends(DateTimeAgent)]