import logging
from typing import Annotated, cast
from fastapi import Depends
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from api.common.psycopg_pool_conf import psycopg_pool
from langchain.agents import create_agent

from api.common.utils import LoggingCallbackHandler

#############################################
# HistoryPostgreSQLAgent 클래스 정의
#############################################
class HistoryPostgreSQLAgent:
    # 초기화 함수
    def __init__(self, model:str = "openai:gpt-4o-mini") -> None:
        self.logger = logging.getLogger(f"{__name__}.HistoryPostgreSQLAgent")
        self.model = model
        self.checkpointer = None
        self.agent = None
        # 비동기 초기화 여부
        self._initialized = False
        
    # 비동기 초기화 메소드
    async def _initialize(self):
        if self._initialized:
            return
        
        # self.checkpointer 초기화
        self.checkpointer = AsyncPostgresSaver(psycopg_pool) # type: ignore
        
        # 대화 기억을 저장할 테이블 자동 생성(최초 1회)
        await self.checkpointer.setup()
        
        # Agent 객체 생성
        self.agent = create_agent(
            model = self.model,
            checkpointer=self.checkpointer
        )
        
        # 비동기 초기화 완료 설정
        self._initialized = True
        
    # 에이전트 실행 메소드
    async def run(self, message:str, conversation_id:str) -> str:
        # 비동기 초기화 메소드 호출
        await self._initialize()
        
        # LLM 요청하고 응답받기
        result = await self.agent.ainvoke( # type: ignore
            {"messages": [{"role": "user", "content": message}]},
            {"configurable": {"thread_id": conversation_id},
             "callbacks":[LoggingCallbackHandler()]}
        )
        
        # AI 메시지 추출 반환
        return result["messages"][-1].content
    
    # 대화 히스토리 조회하기
    async def get_history(self, conversation_id:str) -> dict:
        # 비동기 초기화 메소드 호출
        await self._initialize()
        
        # 현재 Agent의 상태(저장정보) 가져오기
        state = await self.agent.aget_state( # type: ignore
            {"configurable": {"thread_id": conversation_id}}
        )
        
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
        # 비동기 초기화 메소드 호출
        await self._initialize()
        
        # 해당 대화 ID를 완전 삭제
        await self.checkpointer.adelete_thread(conversation_id) # type: ignore
        
        return {
            "conversation_id": conversation_id,
            "message": "대화 기록이 삭제되었습니다."
        }
    
HistoryPostgreSQLAgentDep = Annotated[HistoryPostgreSQLAgent, Depends(HistoryPostgreSQLAgent)]