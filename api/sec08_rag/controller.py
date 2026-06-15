import logging
from typing import Annotated
from fastapi import APIRouter, Form, HTTPException, UploadFile
from fastapi.responses import PlainTextResponse
from langchain_core.document_loaders import Blob
from langchain_community.document_loaders.parsers.pdf import PyPDFParser

from api.sec08_rag.service import EmbeddingServiceDep

# 로거 생성
logger = logging.getLogger(__name__)

# 라우터 생성
router = APIRouter(prefix="/sec08", tags=["sec08"])

############################################################
# Agent를 사용하는 대화 엔드포인트
############################################################
@router.post("/pdf-embedding", response_class=PlainTextResponse)
async def pdf_embedding(
    title: Annotated[str, Form()],
    author: Annotated[str, Form()],
    attach: Annotated[UploadFile, Form()],
    service: EmbeddingServiceDep
):
    # 파일 검증
    if attach.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="PDF 파일만 업로드 가능함")

    # PDF 로드
    content = await attach.read()
    blob = Blob.from_data(content, mime_type="application/pdf")
    parser = PyPDFParser()
    documents = list(parser.lazy_parse(blob))
    
    # 메타데이터 추가
    documents = service.add_metadata(documents, title=title, author=author)
    
    # 분할하기
    chunk_documents = service.split_documents(documents)
    
    # 벡터 저장소에 청크 도큐먼트들을 저장
    await service.save_to_vectorestore_with_sqlalchemy(
        collection_name=title,
        chunk_documents=chunk_documents
    )
    
    # 결과 반환
    result = (
        f"✅ PDF 임베딩 완료!\n\n"
        f"- 컬렉션명: {title}\n"        
        f"- 제목: {title}\n"
        f"- 작성자: {author}\n"        
        f"- 총 페이지 수: {len(documents)}\n"
        f"- 총 청크 수: {len(chunk_documents)}"
    )
    return result

# -----------------------------------------------------------
@router.post("/similarity-search", response_class=PlainTextResponse)
async def similarity_search(
    query: Annotated[str, Form()],
    k: Annotated[int, Form()],
    service: EmbeddingServiceDep,
    collection_name: str = "헌법"
):
    result = await service.similarity_search(
        collection_name=collection_name,
        query=query, 
        k=k
    )
    return result