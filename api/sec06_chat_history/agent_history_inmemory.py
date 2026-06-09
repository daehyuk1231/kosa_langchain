import logging
from typing import Annotated, cast

from fastapi import Depends
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents import create_agent

from api.common.utils import LoggingCallbackHandler

######################################################
# InMemorySaver 생성, 모듈 싱글톤
######################################################
in_memory_saver = InMemorySaver()

######################################################
# HistoryInMemoryAgent 클래스 정의
######################################################
class HistoryInMemoryAgent:
    # 초기화 메소드
    def __init__(self, model:str = "openai:gpt-4o-mini") -> None:
        self.logger = logging.getLogger(f"{__name__}.HistoryInMemoryAgent")
        # Agent 생성
        self.agent = create_agent(
            model,
            checkpointer=in_memory_saver
        )
    
    # 에이전트 실행 메소드
    async def run(self, message:str, conversation_id:str) -> str:
        # LLM에게 요청하고 응답얻기
        result = await self.agent.ainvoke(
            {"messages": [{"role":"user", "content": message}]},
            {"configurable": {"thread_id": conversation_id},
             "callbacks":[LoggingCallbackHandler()]}
        )
        # 응답에서 AiMessage 얻기
        # result 타입: <class 'dict'>
        # result 내용: {'messages’: [
        #                 HumanMessage(...),
        #                 AIMessage(...)
        #              ]}
        # AIMessage는 result["messages"] 리스트의 마지막 요소
        return result["messages"][-1].content
    
    # 대화 히스토리 조회하기
    async def get_history(self, conversation_id:str) -> dict:
        # 현재 Agent의 상태(저장정보) 가져오기
        state = await self.agent.aget_state({
            "configurable": {"thread_id": conversation_id}
        })
        
        # Agent 상태에서 지난 과거 대화 내용이 없는 경우
        if not state or not state.values.get("messages"):
            return {
                "conversation_id": conversation_id,
                "messages":[]
            }
        
        # Agent 상태에서 지난 과거 대화 내용이 있는 경우
        messages = []
        # [{'role': 'human', 'content': '너의 이름을 자비스로하자'}, 
        #  {'role': 'ai', 'content': '좋아요! 이제부터 저는 "자비스"로 불러주세요'}]
        for msg in state.values["messages"]:
            messages.append({
                "role": msg.type,
                "content": msg.content
            })
        return {
            "conversation_id": conversation_id,
            "messages": messages
        }
        
    async def clear_history(self, conversation_id:str) -> dict:
        # 해당 대화 ID를 완전 삭제
        
        # [방법1]
        # adelete_thread()를 사용하기 위해 InMemorySaver 타입으로 변환
        checkpointer = cast(InMemorySaver, self.agent.checkpointer)
        await checkpointer.adelete_thread(conversation_id)
        
        # [방법2]
        # await in_memory_saver.adelete_thread(conversation_id)
        
        return {
            "conversation_id": conversation_id,
            "message": "대화 기록이 삭제되었습니다."
        }
    
# 의존성 주입을 위한 타입 힌트 정의
HistoryInMemoryAgentDep = Annotated[HistoryInMemoryAgent, Depends(HistoryInMemoryAgent)]