import logging
from typing import Annotated
from fastapi import Depends
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from pydantic import BaseModel
from api.sec04_structured_output.model import Movie, Person, PizzaOrder

####################################################
# StructuredOutputService 클래스 정의
####################################################
class StructuredOutputService:
    def __init__(self) -> None:
        self.logger = logging.getLogger(f"{__name__}.StructuredOutputService")
        self.chat_model = init_chat_model(
            model="gpt-4o-mini",
            model_provider="openai",
            temperature=0.0
        )
    
    # 회원 정보 문장 -> LLM -> JSON -> Person 반환
    async def structured_output_person(self, content:str) -> Person:
        messages = [HumanMessage(content)]
        structured_chat_model = self.chat_model.with_structured_output(Person)
        result = await structured_chat_model.ainvoke(messages)
        if isinstance(result, Person):
            return result
        # if isinstance(result, dict):
        #     return Person.model_validate(result)
        # if isinstance(result, BaseModel):
        #     return Person.model_validate(result.model_dump())
        raise TypeError(f"Unexpected structured output type: {type(result)}")
    
    # 영화 이름 -> LLM 영화 정보 -> JSON -> Movie 반환
    async def structured_output_movie(self, content: str) -> Movie:
        messages = [HumanMessage(content)]
        structured_chat_model = self.chat_model.with_structured_output(Movie)
        result = await structured_chat_model.ainvoke(messages)
        if isinstance(result, Movie):
            return result
        raise TypeError(f"Unexpected structured output type: {type(result)}")
    
    # 피자 주문(음성) -> 텍스트 변환 -> LLM -> JSON -> PizzaOrder 반환
    async def structured_output_pizza(self, order: str) -> PizzaOrder:
        messages = [HumanMessage(order)]
        structured_chat_model = self.chat_model.with_structured_output(PizzaOrder)
        result = await structured_chat_model.ainvoke(messages)
        if isinstance(result, PizzaOrder):
            return result
        raise TypeError(f"Unexpected structured output type: {type(result)}")
    
# 의존성 주입을 위한 타입 힌트 정의
StructuredOutputServiceDep = Annotated[StructuredOutputService, Depends(StructuredOutputService)]