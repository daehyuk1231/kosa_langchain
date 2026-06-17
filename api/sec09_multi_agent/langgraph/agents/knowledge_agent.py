import logging
from langchain.agents import create_agent
from langchain.tools import tool

#################################################################################
# Tool 정의
#################################################################################
@tool
def search_knowledge_base(keywords: str) -> str:
    """지식 베이스에서 관련 문서를 검색합니다.    
    Args:
        keywords: 검색 키워드        
    Returns:
        str: 관련 정책 및 FAQ
    """    
    # Mock 지식 베이스
    knowledge = {
        "환불": """
            📚 환불 정책:
            - 구매 후 7일 이내 환불 가능
            - 미개봉 제품에 한함
            - 환불 금액은 영업일 기준 3-5일 소요
            - 배송비는 고객 부담 (제품 하자 시 무료)
            """,
        "배송": """
            📚 배송 정책:
            - 평일 오후 2시 이전 주문 시 당일 출고
            - 배송 기간: 1-3일 (도서산간 2-4일)
            - 배송 추적은 마이페이지에서 확인 가능
            - 배송비: 3만원 이상 무료, 미만 3,000원
            """,
        "기술": """
            📚 기술 지원 FAQ:
            - 제품 초기화: 설정 > 시스템 > 공장 초기화
            - 로그 전송: 앱 오류 시 로그 자동 전송
            - 업데이트: 앱 > 설정 > 버전 확인
            - 고객센터: 1588-1234 (평일 9-18시)
            """,
        "계정": """
            📚 계정 관리 가이드:
            - 비밀번호 재설정: 로그인 > 비밀번호 찾기
            - 회원 탈퇴: 마이페이지 > 설정 > 회원 탈퇴
            - 개인정보 수정: 마이페이지 > 정보 수정
            - 이메일/문자 알림 설정 가능
            """
    }
    
    # 키워드에 해당하는 문서 찾기
    result = "📚 관련 문서:\n"
    found = False
    
    for key, doc in knowledge.items():
        if key in keywords.lower():
            result += doc
            found = True
            break
    
    if not found:
        result += """
            일반 고객센터 안내:
            - 전화: 1588-1234
            - 이메일: support@company.com
            - 운영시간: 평일 9-18시
            """
    return result


#################################################################################
# Agent 클래스
#################################################################################
class KnowledgeAgent:
    # 초기화 메소드
    def __init__(self, model: str = "openai:gpt-4o-mini"):
        self.logger = logging.getLogger(f"{__name__}.KnowledgeAgent")      
        self.agent = create_agent(
            model=model,
            tools=[search_knowledge_base],
            system_prompt="""당신은 지식 베이스 관리 전문가입니다.
                search_knowledge_base 도구를 사용하여 관련 정보를 검색하세요."""
        )

    # 에이전트 실행 메소드
    async def run(self, keywords: str) -> str:
        self.logger.info("지식 베이스 검색 에이전트 실행")
        
        # 검색 요청
        result = await self.agent.ainvoke(
            {"messages": [{
                "role": "user", 
                "content": f"다음 키워드로 지식 베이스를 검색해주세요: {keywords}"
            }]}
        )

        # 검색 결과 반환
        return result["messages"][-1].content
