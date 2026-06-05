from contextlib import asynccontextmanager
import logging

import colorlog
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
from api.common.sqlalchemy_conf import engine
from api.common.entity_base import Base

# ============================================
# 애플리케이션 시작과 종료시 실행해야할 코드
# ============================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 테이블 자동 생성
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.create_all)
    logger.info("애플리케이션 시작")
    yield
    logger.info("애플리케이션 종료, 커넥션 풀 안전 종료")
    await engine.dispose()

# ============================================
# FastAPI 애플리케이션 인스턴스 생성
# ============================================
app = FastAPI(
    title="FastAPI 백엔드",
    description="FastAPI를 학습하기 위한 프로젝트",
    version="1.0.0",
    lifespan=lifespan
)

# ============================================
# 정적 파일 디렉토리 설정
# ============================================
# 정적 파일을 요청할때 사용할 URL 경로 설정
# 정적 파일을 저장하는 디렉토리를 설정
app.mount("/static", StaticFiles(directory="static"), name="static")

# ============================================
# 템플릿 디렉토리 설정
# ============================================
# 템플릿 엔진으로 Jinja2를 사용
# View(HTML)을 생성하는 동적 파일을 저장할 디렉토리 설정
templates = Jinja2Templates(directory="templates")

# ============================================
# 로그 설정
# ============================================
# 루트 로거 얻기
logger = logging.getLogger()
# reload=True로 인해 두번 실행되므로서 두개의 핸들러가 추가될 수 있음
# 이전 핸들러를 삭제해야만 하나의 핸들러만 추가됨
logger.handlers.clear()
# 칼라를 출력하도록 핸들러 생성
handler = colorlog.StreamHandler()
# 로그 문자열 형식 설정
handler.setFormatter(colorlog.ColoredFormatter(
    '%(log_color)s%(levelname)s%(reset)s:     '
    '%(cyan)s%(name)s%(reset)s.%(yellow)s%(funcName)s()%(reset)s: '
    '%(green)s%(message)s%(reset)s',
    log_colors={
        'DEBUG': 'white',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red',
    }
))
# 루트 로거에 핸들러 추가
logger.addHandler(handler)
# 루트 로거에 로그 레벨 설정
logger.setLevel(logging.INFO)

# ============================================
# CORS 설정
# ============================================
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],    # 모든 출처 허용 (운영 환경에서는 특정 도메인만 허용 권장)
    allow_credentials=True, # 쿠키, 인증 헤더 등을 포함한 요청 허용
    allow_methods=["*"],    # 모든 HTTP 메서드 허용 (GET, POST, PUT, DELETE 등)
    allow_headers=["*"],    # 모든 헤더 허용)
)

# ============================================
# 홈(/) 라우트(엔드포인트) 설정
# ============================================
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    logger.info("실행")
    # TemplateResponse() 메소드는 HTMLResponse 객체를 반환
    return templates.TemplateResponse("index.html", {"request":request})

# ============================================
# 외부 라우터 추가
# ============================================
from api.httpmethod import controller as httpmethod_controller
app.include_router(httpmethod_controller.router)

from api.receivedata import controller as receivedata_controller
app.include_router(receivedata_controller.router)

from api.validation import controller as validation_controller
app.include_router(validation_controller.router)

from api.returntype import controller as returntype_controller
app.include_router(returntype_controller.router)

from api.di import controller as di_controller
app.include_router(di_controller.router)

from api.exception import controller as exception_controller
app.include_router(exception_controller.router)

from api.database.member import controller as member_controller
app.include_router(member_controller.router)

from api.database.board import controller as board_controller
app.include_router(board_controller.router)

# ============================================
# 전역 예외 처리기 등록
# ============================================
from api.common.exception_handler import register_exception_handler
register_exception_handler(app)

# ============================================
# 애플리케이션 시작
# ============================================
if __name__ == "__main__":
    logger.info("유비콘 서버를 구동해서 FastAPI 애플리케이션을 실행")
    uvicorn.run(
        # 유비콘(비동기 서버)가 실행할 애플리케이션
        # reload=False일 경우: app을 제공할 수 있음
        # reload=True 일 경우: "main:app"과 같이 문자열로 제공해야 함
        # main 모듈을 찾아 app을 재시작해야 하므로 모듈 이름이 필요
        "main:app",         
        host="localhost",   # 0.0.0.0은 모든 네트워크 인터페이스에서 접근 가능
        port=8000,            # 서버가 실행될 포트 번호     
        reload=True,        # 코드 변경 시 자동으로 서버를 재시작
        access_log=True,    # HTTP 요청/응답 접근 로그 활성화
    )