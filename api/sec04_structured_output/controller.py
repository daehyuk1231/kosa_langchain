import logging
from typing import Annotated
from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse
from api.sec04_structured_output.model import Movie, Person, PizzaOrder
from api.sec04_structured_output.service import StructuredOutputServiceDep

# 로거 생성
logger = logging.getLogger(__name__)

# 라우터 생성
router = APIRouter(prefix="/sec04", tags=["sec04"])

# 엔드포인트 정의--------------------------------------------------------------
@router.post("/structured-output-person", 
             response_class=JSONResponse,
             response_model=Person)
async def structured_output_person(
    content: Annotated[str, Form()],
    service: StructuredOutputServiceDep
):
    response = await service.structured_output_person(content)
    return response
# -------------------------------------------------------------------------
@router.post("/structured-output-movie", 
             response_class=JSONResponse,
             response_model=Movie)
async def structured_output_movie(
    content: Annotated[str, Form()],
    service: StructuredOutputServiceDep
):
    response = await service.structured_output_movie(content)
    return response
# -------------------------------------------------------------------------
@router.post("/structured-output-pizza", 
             response_class=JSONResponse,
             response_model=PizzaOrder)
async def structured_output_pizza(
    order: Annotated[str, Form()],
    service: StructuredOutputServiceDep
):
    response = await service.structured_output_pizza(order)
    return response