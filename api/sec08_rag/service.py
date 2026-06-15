import asyncio
import logging
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_postgres import PGVector
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.embeddings import init_embeddings

class EmbeddingService:
    # 초기화 메소드
    def __init__(self) -> None:
        self.logger = logging.getLogger(f"{__name__}.EmbeddingService")

    # PDF 파일 로드 메소드
    async def load_pdf(self, file_path: str) -> list[Document]:
        # 파일 존재 여부 확인
        if not Path(file_path).exists():
            raise FileNotFoundError("파일을 찾을 수 없습니다.")
        # 파일 로더 생성
        loader = PyPDFLoader(file_path)
        # 파일을 읽고 Document 리스트 얻기
        documents = await loader.aload()
        return documents
    
    # 메타데이터를 추가하는 메소드
    def add_metadata(self, documents: list[Document], **metadata: str):
        if metadata:
            for doc in documents:
                for key, value in metadata.items():
                    doc.metadata[key] = value
        return documents
    
    # Document를 작게 분할하는 메소드(분할된 Document = 청크 도큐먼트)
    # 로딩된 list[Document] -> 분할된 청크 list[Document]
    def split_documents(self, documents: list[Document]):
        # 분할기를 생성
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,     # 분할된 Document가 가질 최대 문자수
            chunk_overlap=50,  # 분할된 Document간 겹치는 문자수
            length_function=len # 문자수를 계산하는 함수
        )
        
        # 분할하기
        chunk_documents = text_splitter.split_documents(documents)
        return chunk_documents
    
    # PGVector에 임베딩 저장(SQLAlchemy 비동기 엔진 이용)
    async def save_to_vectorestore_with_sqlalchemy(self, 
                                                   collection_name: str, 
                                                   chunk_documents: list[Document]):
        
        from api.common.sqlalchemy_conf import engine
        
        # PGVector 객체 생성(DB 연결을 이용해서 벡터를 저장하고 유사도 검색을 수행하는 역할)
        vectorestore = PGVector(
            embeddings=init_embeddings(model="openai:text-embedding-3-large"),
            collection_name=collection_name,
            connection=engine,
            async_mode=True
        )
        
        # 벡터 저장소에 벡터를 저장하기
        await vectorestore.aadd_documents(chunk_documents)
        print("임베딩 저장 완료")
        
    
if __name__ == "__main__":
    import sys
    import selectors
    
    # C:\kosa-course\projects\langchain\api\sec08_rag\service.py
    sys.path.append(str(Path(__file__).parents[2]))
    
    service = EmbeddingService()
    
    # 비동기 함수 또는 메소드를 최상위 레벨로 실행할 경우
    documents = asyncio.run(service.load_pdf("대한민국헌법(19880225).pdf"))
    # print(f"총 도큐먼트 수: {len(documents)}", "\n")
    # print(f"첫 도큐먼트 내용: {documents[0].page_content}", "\n")
    # print(f"첫 도큐먼트의 메타데이터: {documents[0].metadata}")
    
    documents = service.add_metadata(documents, title="헌법", author="법제처")
    # print(f"첫 도큐먼트의 메타데이터: {documents[0].metadata}")
    
    chunk_documents = service.split_documents(documents)
    # print(f"총 도큐먼트 수: {len(chunk_documents)}", "\n")
    # print(f"도큐먼트0 내용: {chunk_documents[0].page_content}", "\n")
    # print("-"*100)
    # print(f"도큐먼트1 내용: {chunk_documents[1].page_content}", "\n")
    
    asyncio.run(
        service.save_to_vectorestore_with_sqlalchemy(
            collection_name="헌법",
            chunk_documents=chunk_documents
        ),
        # Windows는 기본적으로 ProactorEventLoop를 사용
        # - psycopg 비동기 드라이버가 이를 지원하지 않아 오류가 발생
        # - loop_factory로 SelectorEventLoop를 지정해서 호환성 문제를 해결.
        loop_factory=lambda: asyncio.SelectorEventLoop(selectors.SelectSelector())
    )        