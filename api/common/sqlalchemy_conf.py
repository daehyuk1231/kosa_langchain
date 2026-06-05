from typing import Annotated, AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase



################################
# SQLAlchemy 설정
################################
# DB 커넥션 풀(비동기 데이터베이스 엔진) 생성
engine = create_async_engine(
    "postgresql+psycopg://postgres:postgres@localhost:5432/postgres",
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    echo=True
)

# ORM 작업 세션 팩토리 생성
session_maker = async_sessionmaker(
    bind=engine,
    autoflush=True,
    autocommit=False
)

# ORM 작업 세션을 제공하는 제너레이터 생성 함수 정의
# 트랜잭션 작업 처리를 위해 commit/rollback 처리
async def get_orm_session() -> AsyncGenerator[AsyncSession, None]:
    # 세션 생성
    orm_session = session_maker()
    try:
        # 세션을 필요로하는 곳에 제공
        yield orm_session
        # 예외 없이 모든 작업이 성공되었을 때 모든 작업을 영구 반영
        await orm_session.commit()
    except:
        # 모든 작업을 취소시킴
        await orm_session.rollback()
        # 발생된 예외를 재 발생 시킴
        # 엔드포인트 함수에서 예뢰를 마지막으로 처리시키기 위해
        raise
    finally:
        # 세션을 종료, 커넥션을 엔진으로 반납
        await orm_session.close()
        
# 엔티티 클래스의 부모 클래스 정의
# - AsyncAttrs와 DeclarativeBase를 상속
# - AsyncAttrs: SQLAlchemy의 비동기 ORM 기능을 제공하는 클래스
# - DeclarativeBase: SQLAlchemy의 선언적 매핑 기능을 제공하는 클래스
class Base(AsyncAttrs, DeclarativeBase):
    pass

# 의존성 타입 별칭 정의
OrmSessionDep = Annotated[AsyncSession, Depends(get_orm_session)]