from dataclasses import dataclass
import logging
import random
from typing import Annotated
from fastapi import Depends
from langchain.agents import create_agent
from langchain.tools import tool, ToolRuntime

# 로거 생성
logger = logging.getLogger(__name__)

###############################################################
# 컨텍스트 클래스 정의
###############################################################
@dataclass(frozen=True)
class HeatingSystemContext:
    control_key: str

###############################################################
# 도구 정의
###############################################################
@tool
def start_heating_system(target_temperature: int, runtime: ToolRuntime[HeatingSystemContext]) -> str:
    """
    타겟 온도까지 난방 시스템을 가동합니다.
    Args:
        target_temperature: 타겟 온도
    Returns:
        str: 난방 시스템 가동이 성공되었을 경우 "success",
             난방 시스템 가동이 실패되었을 경우 "failure"를 반환합니다.
    """
    logger.info(f"start_heating_system({target_temperature}) 실행")
    heating_system_context = runtime.context
    if heating_system_context and heating_system_context.control_key == "12345":
        # 난방 시스템을 켜는 코드
        return "success"
    else:
        return "failure"

@tool
def stop_heating_system(runtime: ToolRuntime[HeatingSystemContext]) -> str:
    """
    난방 시스템을 중지합니다.    
    Returns:
        str: 난방 시스템 중지가 성공되었을 경우 "success",
             난방 시스템 중지가 실패되었을 경우 "failure"를 반환합니다.
    """
    logger.info(f"stop_heating_system() 실행")
    heating_system_context = runtime.context
    if heating_system_context and heating_system_context.control_key == "12345":
        # 난방 시스템을 끄는 코드
        return "success"
    else:
        return "failure"
    
@tool
def get_temperature() -> int:
    """
    현재 온도를 제공합니다.
    Returns:
        int: 현재 온도(18~30도 범위의 정수값)
    """
    logger.info("get_temperature() 실행")
    temperature = random.randint(18, 30)
    return temperature
    

###############################################################
# Agent 클래스 정의
###############################################################
class HeatingSystemAgent:
    def __init__(self, model:str="openai:gpt-4o-mini") -> None:
        self.logger = logging.getLogger(f"{__name__}.HeatingSystemAgent")
        self.agent = create_agent(
            model=model,
            tools=[start_heating_system, stop_heating_system, get_temperature],
            context_schema=HeatingSystemContext, 
            system_prompt="""
                현재 온도가 사용자가 원하는 온도 이상이라면 난방 시스템을 중지하세요.
                현재 온도가 사용자가 원하는 온도 이하라면 난방 시스템을 가동시켜주세요.
            """
        )

    async def run(self, question: str) -> str:
        result = await self.agent.ainvoke(
            {"messages": [{"role":"user", "content": question}]},
            context=HeatingSystemContext(control_key="12345")
        )
        
        return result["messages"][-1].content
    
# 의존성 주입을 위한 타입 힌트 정의
HeatingSystemAgentDep = Annotated[HeatingSystemAgent, Depends(HeatingSystemAgent)]