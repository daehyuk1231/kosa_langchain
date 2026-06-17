import json
import logging

from api.sec09_multi_agent.langgraph.agents.knowledge_agent import KnowledgeAgent
from api.sec09_multi_agent.langgraph.state import ShareState

# 로거 생성
logger = logging.getLogger(__name__)

# 모듈 싱글톤 에이전트 생성
agent = KnowledgeAgent()

# 지식 베이스 검색 노드 정의
async def knowledge_node(state: ShareState) -> dict:
    logger.info("지식 베이스 검색 노드 실행")      
    
    # 고객 문의 분석 내용 가져오기
    inquiry_analysis = json.loads(state.get("inquiry_analysis", "{}"))
    
    # 키워드 얻기
    keywords = inquiry_analysis["keywords"]
    
    # 문의 유형
    inquiry_type = inquiry_analysis["inquiry_type"]
    keywords = keywords + "\n" + inquiry_type
    
    # Agent 실행하여 지식 베이스 검색 결과 얻기
    knowledge = await agent.run(keywords)
    logger.info(f"knowledge: {knowledge}")
    
    # 상태 업데이트: 검색 결과 저장
    return { "knowledge_base": knowledge }