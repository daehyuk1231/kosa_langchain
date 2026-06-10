import logging
from typing import Annotated
from fastapi import Depends
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

# 로거 생성
logger = logging.getLogger(__name__)

# 메모리에 대화 기억을 저장시키는 체크포인트 생성
in_memory_saver = InMemorySaver()

###############################################################
# 도구 정의
###############################################################

###############################################################
# Agent 클래스 정의
###############################################################
class FileSystemAgent:
    def __init__(self, model:str="openai:gpt-4o-mini") -> None:
        self.logger = logging.getLogger(f"{__name__}.FileSystemAgent")
        self.checkpointer = in_memory_saver
        self.agent = create_agent(
            model=model,
            tools=[],
            checkpointer=self.checkpointer
        )

    async def run(self, question: str, conversation_id:str="default") -> str:
        result = await self.agent.ainvoke(
            {"messages": [{"role":"user", "content": question}]},
            {"configurable": {"thread_id": conversation_id}}
        )
        
        return result["messages"][-1].content
    
# 의존성 주입을 위한 타입 힌트 정의
FileSystemAgentDep = Annotated[FileSystemAgent, Depends(FileSystemAgent)]