import logging
from typing import Annotated, AsyncGenerator
from fastapi import Depends
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage

##################################
# ChatService 클래스 정의
##################################
class ChatService:
    def __init__(self) -> None:
        self.logger = logging.getLogger(f"{__name__}.ChatService")
        
        self.chat_model = init_chat_model(
            "gpt-4o-mini",
            model_provider="openai",
            temperature=0.7
        )
        
        self.chat_model_stream = init_chat_model(
            "gpt-4o-mini",
            model_provider="openai",
            temperature=0.7,
            streaming=True
        )
        
    async def chat(self, question: str) -> str:
        # 사용자 메시지 생성
        messages = [
            SystemMessage((
                "당신은 친절하지 않은 해적의 말투로 답변하는 Python 전문가입니다."
                "항상 코드 예제를 포함하여 설명하세요"
            )),
            HumanMessage(question)
        ]
        # LLM으로 메시지를 보내고(요청) 응답 메시지(AiMessage) 받기
        ai_message = await self.chat_model.ainvoke(messages)
        self.logger.info(type(ai_message))
        # AiMessage로부터 내용(응답 텍스트)를 얻어 반환
        return str(ai_message.content)
    
    async def chat_stream(self, question: str) -> AsyncGenerator[str, None]:
        # 사용자 메시지 생성
        messages = [
            SystemMessage((
                "당신은 친절하지 않은 해적의 말투로 답변하는 Python 전문가입니다."
                "항상 코드 예제를 포함하여 설명하세요"
            )),
            HumanMessage(question)
        ]
        # 비동기 스트리밍 응답을 위한 요청
        iterator = self.chat_model_stream.astream(messages)
        async for ai_message_chunk in iterator:
            if ai_message_chunk:
                yield str(ai_message_chunk.content)

##################################
# 의존성 타입 별칭 정의
##################################
ChatServiceDep = Annotated[ChatService, Depends(ChatService)]