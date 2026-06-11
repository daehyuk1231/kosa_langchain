from datetime import datetime
import logging
import os
from pathlib import Path
import shutil
from typing import Annotated
from fastapi import Depends
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from langchain.tools import tool

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
@tool
def list_directory(path: str = ".") -> str:
    """디렉토리의 파일 및 하위 디렉토리 목록을 조회합니다.
    Args:
        path: 조회할 디렉토리 경로 (기본값: 루트 디렉토리)
    Returns:
        str: 디렉토리 내용 목록 (파일과 디렉토리)
    """
    try:
        # 경로 검증 및 절대 경로 변환
        dir_path = validate_path(path)        
        if not dir_path.exists():
            return f"오류: 디렉토리 '{path}'가 존재하지 않습니다."        
        if not dir_path.is_dir():
            return f"오류: '{path}'는 디렉토리가 아닙니다."
        # 디렉토리 내용 목록 생성        
        items = []
        for item in sorted(dir_path.iterdir()):
            item_type = "DIR" if item.is_dir() else "FILE"
            relative_path = item.relative_to(ROOT_DIR)
            items.append(f"[{item_type}] {relative_path}")
        # 목록이 비어있으면 "(빈 디렉토리)" 표시, 그렇지 않으면 항목들을 줄바꿈으로 구분하여 반환
        result = "\n".join(items) if items else "(빈 디렉토리)"
        logger.info(f"디렉토리 목록 조회: {path}")
        return result
    except Exception as e:
        logger.error(f"디렉토리 목록 조회 실패: {e}")
        return f"오류: {str(e)}"


@tool
def create_directory(path: str) -> str:
    """새로운 디렉토리를 생성합니다.
    Args:
        path: 생성할 디렉토리 경로
    Returns:
        str: 생성 결과 메시지
    """
    try:
        # 경로 검증 및 절대 경로 변환
        dir_path = validate_path(path)
        if dir_path.exists():
            return f"오류: '{path}'가 이미 존재합니다."
        # 상위 디렉토리가 없으면 생성하면서 새로운 디렉토리를 생성
        dir_path.mkdir(parents=True, exist_ok=False)
        logger.info(f"디렉토리 생성: {path}")
        return f"디렉토리 '{path}'를 생성했습니다."
    except Exception as e:
        logger.error(f"디렉토리 생성 실패: {e}")
        return f"오류: {str(e)}"


@tool
def create_file(path: str, content: str = "") -> str:
    """새로운 파일을 생성하고 내용을 작성합니다.
    Args:
        path: 생성할 파일 경로
        content: 파일에 작성할 내용 (기본값: 빈 문자열)
    Returns:
        str: 생성 결과 메시지
    """
    try:
        # 경로 검증 및 절대 경로 변환
        file_path = validate_path(path)
        if file_path.exists():
            return f"오류: '{path}'가 이미 존재합니다."
        
        # 상위 디렉토리가 없으면 생성
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 파일 생성 및 내용 작성
        file_path.write_text(content, encoding="utf-8")
        logger.info(f"파일 생성: {path}")
        return f"파일 '{path}'를 생성했습니다. (크기: {len(content)} 바이트)"
    except Exception as e:
        logger.error(f"파일 생성 실패: {e}")
        return f"오류: {str(e)}"


@tool
def read_file(path: str) -> str:
    """파일의 내용을 읽습니다.
    Args:
        path: 읽을 파일 경로
    Returns:
        str: 파일 내용
    """
    try:
        # 경로 검증 및 절대 경로 변환
        file_path = validate_path(path)   
        if not file_path.exists():
            return f"오류: 파일 '{path}'가 존재하지 않습니다."
        if not file_path.is_file():
            return f"오류: '{path}'는 파일이 아닙니다."
        # 파일 내용 읽기
        content = file_path.read_text(encoding="utf-8")
        logger.info(f"파일 읽기: {path}")
        return content
    except Exception as e:
        logger.error(f"파일 읽기 실패: {e}")
        return f"오류: {str(e)}"


@tool
def write_file(path: str, content: str) -> str:
    """기존 파일에 내용을 덮어씁니다.
    Args:
        path: 작성할 파일 경로
        content: 파일에 작성할 내용
    Returns:
        str: 작성 결과 메시지
    """
    try:
        # 경로 검증 및 절대 경로 변환
        file_path = validate_path(path)
        if not file_path.exists():
            return f"오류: 파일 '{path}'가 존재하지 않습니다. create_file을 사용하세요."
        if not file_path.is_file():
            return f"오류: '{path}'는 파일이 아닙니다."
        # 파일 내용 덮어쓰기
        file_path.write_text(content, encoding="utf-8")
        logger.info(f"파일 작성: {path}")
        return f"파일 '{path}'에 내용을 작성했습니다. (크기: {len(content)} 바이트)"
    except Exception as e:
        logger.error(f"파일 작성 실패: {e}")
        return f"오류: {str(e)}"

@tool
def delete_path(path: str) -> str:
    """파일 또는 디렉토리를 삭제합니다.
    Args:
        path: 삭제할 파일 또는 디렉토리 경로
    Returns:
        str: 삭제 결과 메시지
    """
    try:
        # 경로 검증 및 절대 경로 변환
        target_path = validate_path(path)
        
        # 루트 디렉토리 자체 삭제 방지
        if target_path == ROOT_DIR:
            return "오류: 루트 디렉토리는 삭제할 수 없습니다."
        
        if not target_path.exists():
            return f"오류: '{path}'가 존재하지 않습니다."
        
        # 파일 또는 디렉토리 삭제
        if target_path.is_dir():
            # shutil.rmtree(): 디렉토리와 그 안의 모든 내용을 삭제하는 함수
            shutil.rmtree(target_path)
            logger.info(f"디렉토리 삭제: {path}")
            return f"디렉토리 '{path}'를 삭제했습니다."
        else:
            # Path.unlink(): 파일을 삭제하는 메소드, 디렉토리에는 사용할 수 없음
            target_path.unlink()
            logger.info(f"파일 삭제: {path}")
            return f"파일 '{path}'를 삭제했습니다."
    except Exception as e:
        logger.error(f"삭제 실패: {e}")
        return f"오류: {str(e)}"


@tool
def move_path(source: str, destination: str) -> str:
    """파일 또는 디렉토리를 이동하거나 이름을 변경합니다.
    Args:
        source: 원본 경로
        destination: 대상 경로
    Returns:
        str: 이동/이름 변경 결과 메시지
    """
    try:
        # 경로 검증 및 절대 경로 변환
        src_path = validate_path(source)
        dst_path = validate_path(destination)
        
        if not src_path.exists():
            return f"오류: '{source}'가 존재하지 않습니다."
        
        # 루트 디렉토리 자체 이동 방지
        if src_path == ROOT_DIR:
            return "오류: 루트 디렉토리는 이동할 수 없습니다."
        
        if dst_path.exists():
            return f"오류: '{destination}'가 이미 존재합니다."
        
        # 대상 디렉토리가 없으면 생성
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        
        # shutil.move(): 파일 또는 디렉토리를 이동하거나 이름을 변경하는 함수, 
        # 대상이 이미 존재하면 덮어쓰므로 사전에 존재 여부 확인 필요
        shutil.move(str(src_path), str(dst_path))
        logger.info(f"이동/이름 변경: {source} -> {destination}")
        return f"'{source}'를 '{destination}'로 이동했습니다."
    except Exception as e:
        logger.error(f"이동/이름 변경 실패: {e}")
        return f"오류: {str(e)}"


@tool
def copy_path(source: str, destination: str) -> str:
    """파일 또는 디렉토리를 복사합니다.
    Args:
        source: 원본 경로
        destination: 대상 경로
    Returns:
        str: 복사 결과 메시지
    """
    try:
        # 경로 검증 및 절대 경로 변환
        src_path = validate_path(source)
        dst_path = validate_path(destination)
        
        if not src_path.exists():
            return f"오류: '{source}'가 존재하지 않습니다."
        
        if dst_path.exists():
            return f"오류: '{destination}'가 이미 존재합니다."
        
        # 대상 디렉토리가 없으면 생성
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 파일 및 디렉토리 복사
        if src_path.is_dir():
            # shutil.copytree(): 디렉토리와 그 안의 모든 내용을 복사하는 함수, 
            # 대상이 이미 존재하면 오류 발생
            shutil.copytree(src_path, dst_path)
            logger.info(f"디렉토리 복사: {source} -> {destination}")
            return f"디렉토리 '{source}'를 '{destination}'로 복사했습니다."
        else:
            # shutil.copy2(): 파일을 복사하는 함수, 
            # 메타데이터(생성 시간, 수정 시간 등)도 함께 복사 
            # 대상이 이미 존재하면 덮어쓰므로 사전에 존재 여부 확인 필요
            shutil.copy2(src_path, dst_path)
            logger.info(f"파일 복사: {source} -> {destination}")
            return f"파일 '{source}'를 '{destination}'로 복사했습니다."
    except Exception as e:
        logger.error(f"복사 실패: {e}")
        return f"오류: {str(e)}"


@tool
def get_file_info(path: str) -> str:
    """파일 또는 디렉토리의 정보를 조회합니다.
    Args:
        path: 정보를 조회할 경로
    Returns:
        str: 파일/디렉토리 정보
    """
    try:
        # 경로 검증 및 절대 경로 변환
        target_path = validate_path(path)
        
        if not target_path.exists():
            return f"오류: '{path}'가 존재하지 않습니다."
        # Path.stat(): 파일 또는 디렉토리의 상태 정보를 반환하는 메소드
        stat = target_path.stat()
        item_type = "디렉토리" if target_path.is_dir() else "파일"
        
        # 생성 시간 (Windows에서는 birthtime, 없으면 ctime 사용)
        if hasattr(stat, 'st_birthtime'):
            creation_time = datetime.fromtimestamp(stat.st_birthtime).strftime('%Y-%m-%d %H:%M:%S')
        else:
            creation_time = datetime.fromtimestamp(os.path.getctime(target_path)).strftime('%Y-%m-%d %H:%M:%S')
        
        # 수정 시간
        modification_time = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        
        # 정보 문자열 생성
        info = f"""경로: {path}
            타입: {item_type}
            크기: {stat.st_size} 바이트
            생성 시간: {creation_time}
            수정 시간: {modification_time}"""
        
        logger.info(f"정보 조회: {path}")
        return info
    except Exception as e:
        logger.error(f"정보 조회 실패: {e}")
        return f"오류: {str(e)}"
    
###############################################################
# Agent 클래스 정의
###############################################################
class FileSystemAgent:
    def __init__(self, model:str="openai:gpt-4o-mini") -> None:
        self.logger = logging.getLogger(f"{__name__}.FileSystemAgent")
        self.checkpointer = in_memory_saver
        self.root_dir = ROOT_DIR
        self.agent = create_agent(
            model=model,
            tools=[
                list_directory,
                create_directory,
                create_file,
                read_file,
                write_file,
                delete_path,
                move_path,
                copy_path,
                get_file_info
            ],
            checkpointer=self.checkpointer
        )

    async def run(self, question: str, conversation_id:str="user1") -> str:
        system_message = {"role":"system", "content": f"""
            당신은 파일 시스템 관리 도우미입니다.
            - 작업 가능한 루트 디렉토리: {self.root_dir}
            - 모든 경로는 이 루트 디렉토리를 기준으로 상대 경로로 지정하거나, 루트 디렉토리 내부의 절대 경로로 지정해야 합니다.
                예: "test.txt", "folder/test.txt", "{self.root_dir}/test.txt"
            - 사용자의 요청을 정확히 이해하고 적절한 도구를 사용하여 작업을 수행하세요.
        """}
        user_message = {"role":"user", "content": question}
        
        result = await self.agent.ainvoke(
            {"messages": [system_message, user_message]},
            {"configurable": {"thread_id": conversation_id}}
        )
        
        return result["messages"][-1].content
    
# 의존성 주입을 위한 타입 힌트 정의
FileSystemAgentDep = Annotated[FileSystemAgent, Depends(FileSystemAgent)]