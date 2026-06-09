import logging
from typing import Annotated
from fastapi import Depends
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent

from api.sec04_structured_output.model import Movie

class StructuredOutputAgent:
    # 초기화 메소드
    def __init__(self, model:str="openai:gpt-4o-mini") -> None:
        self.logger = logging.getLogger(f"{__name__}.StructuredOutputAgent")
        # Agent 생성
        chat_model = init_chat_model(model, temperature=0.0)
        self.agent = create_agent(
            chat_model,
            system_prompt="당신은 영화 전문가입니다. 한국어로 답변해 주세요.",
            response_format=Movie
        )
    
    # 에이전트 실행 메소드
    async def run(self, content:str) -> Movie:
        result = await self.agent.ainvoke(
            {"messages": [{"role":"user", "content":content}]}
        )
        
        # result = {
        #   "messages": [
        #       {HumanMessage(content="...")}, 
        #       {AIMessage(content="...")}
        #   ],
        #   "structured_response": Movie(...)
        # }
        
        movie = result["structured_response"]
        return movie
    
# 의존성 주입을 위한 타입 힌트 정의
StructuredOutputAgentDep = Annotated[StructuredOutputAgent, Depends(StructuredOutputAgent)]