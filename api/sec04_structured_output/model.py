from typing import Annotated
from pydantic import BaseModel, EmailStr, Field

#------------------------------------------------------
# Pydantic 모델 정의 - Person
#------------------------------------------------------
class Person(BaseModel):
    """개인 정보 스키마"""
    name: Annotated[str, Field(description="이름")]
    age: Annotated[int, Field(description="나이")]
    email: Annotated[EmailStr, Field(description="이메일")]

#------------------------------------------------------
# Pydantic 모델 정의 - Movie
#------------------------------------------------------
class Movie(BaseModel):
    """영화 정보 스키마"""
    title: Annotated[str, Field(description="영화 제목")]
    year: Annotated[int, Field(description="개봉 연도")]
    director: Annotated[str, Field(description="감독 이름")]
    plot: Annotated[str, Field(description="줄거리")]

#------------------------------------------------------
# Pydantic 모델 정의 - PizzaOrder
#------------------------------------------------------
class PizzaOrder(BaseModel):
    """피자 주문 정보 스키마"""
    size: Annotated[str, Field(description="피자 크기 (small, medium, large)")]
    type: Annotated[str, Field(description="피자 종류 (normal, thin crust, stuffed crust)")]
    ingredients: Annotated[list[str], Field(description="재료 목록")]
