import logging
from typing import Annotated, TypedDict
from fastapi import Depends
from langchain.agents import create_agent
from langgraph.graph import add_messages
from langchain.tools import tool
from langgraph.prebuilt import ToolRuntime
from langgraph.types import Command
from langchain_core.messages import ToolMessage

# 로거 생성
logger = logging.getLogger(__name__)

###############################################################
# 상태 클래스 정의
###############################################################
class CustomState(TypedDict):
    # 필수 필드
    messages: Annotated[list, add_messages]
    # 추가 필드
    user_id: str
    user_role: str

###############################################################
# 도구 정의
###############################################################
@tool
def check_role(runtime: ToolRuntime) -> Command:
    """
    user_id를 기반으로 user_role을 확인합니다.
    """
    # 상태에서 user_id를 읽기
    user_id = runtime.state["user_id"]

    # 데이터베이스에서 user_id로 user_role을 가져온다.(가정)
    role_db = {"user1": "admin", "user2": "user", "user3": "guest"}
    user_role = role_db.get(user_id, "guest")
    
    # 도구 호출 결과
    tool_result = f"상태 업데이트함"
    
    return Command(update={
        # user_role을 새로운 값으로 대체
        "user_role": user_role,
        # 기존 메시지 리스트 맨 뒤에 추가
        "messages": [ToolMessage(content=tool_result, tool_call_id=runtime.tool_call_id)]
    })

@tool
def check_permission(runtime: ToolRuntime) -> list[str]:
    """
    user_role에 따라 사용자가 할 수 있는 작업을 확인합니다.
    Returns:
        "admin"일 경우: ["read", "write", "delete"],
        "user"일 경우: ["read", "write"],
        "guest"일 경우: ["read"],
    """
    user_role = runtime.state.get("user_role", "guest")
    
    # 데이터베이스에서 user_role에 따른 할 수 있는 작업 가져오기
    available_task = {
        "admin": ["read", "write", "delete"],
        "user": ["read", "write"],
        "guest": ["read"]
    }
    
    # 사용자가 할 수 있는 작업 반환
    return available_task.get(user_role, [])
    

###############################################################
# Agent 클래스 정의
###############################################################
class StateAgent:
    def __init__(self, model:str="openai:gpt-4o-mini") -> None:
        self.logger = logging.getLogger(f"{__name__}.StateAgent")
        self.agent = create_agent(
            model=model,
            tools=[check_role, check_permission],
            state_schema=CustomState, # type: ignore
            system_prompt="""
                사용자의 요청을 처리할 때 반드시 다음 순서를 따르세요:
                1. check_role 도구로 user_role을 상태에 저장합니다.
                2. check_permission 도구로 현재 user_role의 작업 목록을 확인합니다.
                3. 작업 목록을 기준으로 요청 작업의 가능 여부를 사용자에게 안내합니다.
            """
        )

    async def run(self, question: str, user_id: str) -> str:
        result = await self.agent.ainvoke(
            # 초기 상태값
            {
                "messages": [{"role":"user", "content": question}],
                "user_id": user_id
            } # type: ignore
        )
        
        return result["messages"][-1].content
    
# 의존성 주입을 위한 타입 힌트 정의
StateAgentDep = Annotated[StateAgent, Depends(StateAgent)]