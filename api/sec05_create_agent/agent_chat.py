import logging
from typing import Annotated
from fastapi import Depends
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage

class ChatAgent:
    # 초기화 메소드
    def __init__(self, model: str = "openai:gpt-4o-mini") -> None:
        # 로거 생성
        self.logger = logging.getLogger(f"{__name__}.ChatAgent")
        # Agent 생성
        self.agent = create_agent(model)

    # 에이전트 실행 메소드
    async def run(self, question: str) -> str:
        # LLM으로 요청하고 응답받기
        # LangChain 메시지 이름 <-> OpenAI 메시지 이름
        #   SystemMessage           SystemMessage(system)
        #   HumanMessage            UserMessage(user)
        #   AiMessage               AssistantMessage(assistant)
        result = await self.agent.ainvoke({
            "messages": [HumanMessage(question)]
            # "messages": [{"role": "user", "content": question}]
        })
        
        # 응답에서 AiMessage 얻기
        # result 타입: <class 'dict'>
        # result 내용: {'messages’: [
        #                 HumanMessage(...),
        #                 AIMessage(...)
        #              ]}
        # AIMessage는 result["messages"] 리스트의 마지막 요소
        ai_message = result["messages"][-1]
        
        # AiMessage에서 텍스트 얻기
        response = ai_message.content
        self.logger.info(type(response))
        return response
    
# 의존성 주입을 위해서 타입 힌트 정의
ChatAgentDep = Annotated[ChatAgent, Depends(ChatAgent)]