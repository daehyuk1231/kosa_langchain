import logging
from pathlib import Path
from typing import Annotated
from fastapi import Depends
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

# 로거 생성
logger = logging.getLogger(__name__)

# 메모리에 대화 기억을 저장시키는 체크포인트 생성
in_memory_saver = InMemorySaver()

# 루트 디렉토리 설정(Windows 사용자 문서 폴더 내)
ROOT_DIR = Path.home() / "Document" / "langchain-root-dir"
# parents=True: 상위 폴더들을 모두 생성
# exist_ok=True: 존재하면 예외 발생하지 않고 조용히 건너뜀
ROOT_DIR.mkdir(parents=True, exist_ok=True)

# 루트 디렉토리 내부 경로 검증 함수
def validate_path(path: str) -> Path:
    """경로가 루트 디렉토리 내에 있는지 검증합니다.
    Args:
        path: 검증할 경로 (상대 경로 또는 절대 경로)
    Returns:
        Path: 검증된 절대 경로
    Raises:
        ValueError: 경로가 루트 디렉토리 밖을 가리키는 경우
    """
    # 상대 경로를 절대 경로로 변환
    if not Path(path).is_absolute():
        # resolve(): 경로를 절대 경로로 변환하고, 심볼릭 링크를 해석하여 실제 경로를 반환
        # <ROOT_DIR>/../ => C:<User>/Documents
        full_path = (ROOT_DIR / path).resolve()
    else:
        full_path = Path(path).resolve()
    
    # 루트 디렉토리 내에 있는지 확인
    try:
        # relative_to(): full_path가 ROOT_DIR의 하위 경로인지 확인하고 상대경로 반환, 
        # 그렇지 않으면 ValueError 예외 발생
        full_path.relative_to(ROOT_DIR)
    except ValueError:
        raise ValueError(f"경로는 반드시 {ROOT_DIR} 내에 있어야 합니다.")
    # 검증된 절대 경로 반환
    return full_path

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

    async def run(self, question: str, conversation_id:str="user1") -> str:
        result = await self.agent.ainvoke(
            {"messages": [{"role":"user", "content": question}]},
            {"configurable": {"thread_id": conversation_id}}
        )
        
        return result["messages"][-1].content
    
# 의존성 주입을 위한 타입 힌트 정의
FileSystemAgentDep = Annotated[FileSystemAgent, Depends(FileSystemAgent)]