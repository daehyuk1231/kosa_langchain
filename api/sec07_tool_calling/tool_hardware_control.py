import base64
import logging
from typing import Annotated
from fastapi import Depends
from langchain.agents import create_agent
from langchain.tools import tool

logger = logging.getLogger(__name__)

####################################################################
# 도구 정의
####################################################################
@tool
def check_car_number(car_number: str) -> bool:
    """
    인식된 차량 번호가 등록되어 있는지 확인합니다.
    Args:
        car_number: 차량 번호    
    Returns:
        bool: 등록된 차량이면 True, 아니면 False
    """
    logger.info("실행")

    # 데이터베이스에 차량 번호가 등록되어 있다고 가정
    registered_cars = ["23가4567", "234부8372", "345가6789"]
    
    # 차량 번호에 포함된 모든 공백 제거
    car_number = car_number.replace(" ", "")
    logger.info(f"LLM이 인식한 차량 번호: {car_number}")
    
    # 데이터베이스에 차량 번호가 등록되어 있는지 확인
    result = car_number in registered_cars
    logger.info(f"차량 번호 확인 결과: {result}")
    return result

@tool
def boom_barrier_up() -> str:
    """
    차단기를 올립니다.
    
    Returns:
        str: "차단기 올림"
    """
    logger.info("차단기를 올립니다.")
    return "차단기 올림"

@tool
def boom_barrier_down() -> str:
    """
    차단기를 내립니다.
    
    Returns:
        str: "차단기 내림"
    """
    logger.info("차단기를 내립니다.")
    return "차단기 내림"

####################################################################
# Agent 클래스 정의
####################################################################
class BoomBarrierAgent:
    def __init__(self, model:str="openai:gpt-4o-mini") -> None:
        self.logger = logging.getLogger(f"{__name__}.BoomBarrierAgent")
        self.agent = create_agent(
            model=model,
            tools=[check_car_number, boom_barrier_up, boom_barrier_down]
        )

    async def run(self, image_data: bytes, content_type: str) -> str:
        # 이미지 데이터 -> 문자열로 변환
        image_base64 = base64.b64encode(image_data).decode("utf-8")
        
        # 사용자 메시지 구성
        user_message = {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": """다음 단계별로 처리해 주세요.
                        1단계: 이미지에서 '(숫자 2개~3개)-(한글 1자)-(숫자 4개)'로 구성된 차량 번호를 인식하세요. 예: 78라1234, 567바2558
                        2단계: 인식된 차량 번호에서 끝에서부터 5번째 문자가 한글 완성형 음절이 아닐 경우에는 다시 1단계로 돌아가세요.
                        3단계: 1단계에서 인식된 차량 번호가 등록된 차량 번호인지 도구로 확인을 하세요.
                        4단계: 3단계의 결과가 False라면 도구로 차단기를 내리고, True라면 도구로 차단기를 올리세요.
                        최종 답변은 차단기 내림 또는 차단기 올림으로 하고 추가 설명은 하지마세요."""
                },
                {
                    "type": "image",
                    "base64": image_base64,
                    "mime_type": content_type   # image/jpeg, image/png
                }
            ]
        }
        
        result = await self.agent.ainvoke(
            {"messages": [user_message]}
        )
        
        return result["messages"][-1].content
    
# 의존성 주입을 위한 타입 힌트 정의
BoomBarrierAgentDep = Annotated[BoomBarrierAgent, Depends(BoomBarrierAgent)]