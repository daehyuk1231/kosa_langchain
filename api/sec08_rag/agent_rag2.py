import logging
from typing import Annotated
from fastapi import Depends
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_postgres import PGVector
from api.common.sqlalchemy_conf import engine
from langchain.embeddings import init_embeddings

# 로거 생성
logger = logging.getLogger(__name__)

###############################################################
# 도구 정의
###############################################################
@tool
async def search_documents(query: str, k: int = 3) -> str:
    """
    삼성화재 자동차보험 약관과 관련된 질문에 대해 유사한 문서를 검색하는 도구입니다.
    Args:
        query: 검색할 질문이나 키워드 (예: "보험 기간", "대인배상 보상 범위")
        k: 검색할 문서 개수 (기본값: 3)
    Returns:
        str: 검색된 삼성화재 자동차보험 약관 문서 내용과 메타데이터
    """

    # PGVector 객체 생성
    vectorstore = PGVector(
        embeddings=init_embeddings(model="openai:text-embedding-3-large"),
        collection_name="삼성화재자동차보험약관",
        connection=engine,
        async_mode=True
    )
    
    # 유사도 검색
    # results: List[Tuple[도큐먼트(Document), 거리(float)]] = 
    # [(Document(page_content="...", metadata={"source": "..."}, ...), 0.95), ...]
    # 거리는 0~2 사이의 거리값으로, 0에 가까울수록 유사도가 높음
    results = await vectorstore.asimilarity_search_with_score(query, k)
    # 거리 임계값을 주고, 임계값 이하인 Document만 추려내기
    documents = [(doc, distance) for (doc, distance) in results if distance < 0.5]

    # LLM으로 보낼 내용을 리스트 항목으로 만들기
    output_lines = [f"검색 결과: '{query}' (삼성화재자동차보험약관)\n"]
    if not documents:
        output_lines.append("관련된 삼성화재 자동차보험 약관 문서를 찾을 수 없습니다.")
        return "".join(output_lines)

    for idx, (doc, distance) in enumerate(documents, 1):
        output_lines.append(f"\n[문서 {idx}] (거리: {distance: .4f})")
        # 메타 데이터 추가하기
        if doc.metadata:
            if "title" in doc.metadata:
                output_lines.append(f"\n제목: {doc.metadata['title']}")
            if "author" in doc.metadata:
                output_lines.append(f"\n작성자: {doc.metadata['author']}")
            if "page" in doc.metadata:
                output_lines.append(f"\n페이지: {doc.metadata['page']}")
            if "source" in doc.metadata:
                output_lines.append(f"\n출처: {doc.metadata['source']}")
        # 문서 원본 텍스트 추가하기
        output_lines.append(f"\n내용:\n{doc.page_content}\n")
        output_lines.append("-"*100)
    # 리스트 항목을 하나의 문자열로 결합
    result_text ="".join(output_lines)
    return result_text
    
###############################################################
# Agent 클래스 정의
###############################################################
class RAGAgent2:
    def __init__(self, model:str="openai:gpt-4o-mini") -> None:
        self.logger = logging.getLogger(f"{__name__}.RAGAgent2")
        self.agent = create_agent(
            model=model,
            tools=[search_documents],
            system_prompt="""
                당신은 삼성화재자동차보험약관 전문가입니다.
                
                사용 가능한 도구:
                **search_documents**: 삼성화재자동차보험약관 문서 검색
                
                답변 생성 지침:
                - 사용자의 질문을 받으면 search_documents 도구를 사용하여 관련 삼성화재 자동차보험 약관을 검색합니다.
                - 검색된 삼성화재 자동차보험 약관 문서 내용을 바탕으로 정확하고 상세한 답변을 제공하세요.
                - 답변 시 조항 번호, 페이지 등 출처를 반드시 명시하여 신뢰성을 높이세요.
                - 약관 문서에 없는 내용은 추측하지 말고 "삼성화재 자동차보험 약관 문서에서 해당 정보를 찾을 수 없습니다"라고 답하세요.
            """
        )

    async def run(self, question: str) -> str:
        result = await self.agent.ainvoke(
            {"messages": [{"role":"user", "content": question}]}
        )
        
        return result["messages"][-1].content
    
# 의존성 주입을 위한 타입 힌트 정의
RAGAgent2Dep = Annotated[RAGAgent2, Depends(RAGAgent2)]
