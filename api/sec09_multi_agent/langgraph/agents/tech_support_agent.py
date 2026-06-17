import logging
from langchain.agents import create_agent

#################################################################################
# Agent 클래스
#################################################################################
class TechSupportAgent:
    """
    기술 지원 Agent
    제품 오류, 작동 문제 등 기술적 문의에 대한 답변을 제공합니다.
    """
    # 초기화 메소드
    def __init__(self, model: str = "openai:gpt-4o-mini"):
        self.logger = logging.getLogger(f"{__name__}.TechSupportAgent")        
        self.agent = create_agent(
            model=model,
            system_prompt="""당신은 기술 지원팀 전문가입니다.
                제품의 기술적 문제, 오류, 작동 불량 등에 대해 답변합니다.
                사용자 정보와 지식 베이스 정보를 참고하여 친절하고 전문적인 답변을 제공하세요.
                답변 형식은 다음과 같습니다.

                🔧 기술 지원팀 답변:
                안녕하세요, 기술 지원팀입니다.

                [사용자 정보]

                [지식 베이스 정보]

                추가 지원이 필요하시면:
                1. 원격 지원 요청: 1588-1234 (내선 2번)
                2. 방문 수리: 예약 후 서비스센터 방문
                3. 이메일 문의: tech@company.com

                친절하게 안내해드리겠습니다.
                감사합니다."""
        )

    # 에이전트 실행 메소드
    async def run(self, inquiry: str, analysis: str, 
                  user_info: str, knowledge: str) -> str:
        self.logger.info("기술 지원 에이전트 실행")
        
        # 최종 답변 생성 요청
        prompt = f"""
            다음 고객 문의에 대해 기술 지원팀 답변을 작성해주세요:
            원본 문의: {inquiry}
            문의 분석: {analysis}
            사용자 정보: {user_info}
            지식 베이스 정보: {knowledge}
            """
        result = await self.agent.ainvoke(
            {"messages": [{"role": "user", "content": prompt}]}
        )
        
        # 최종 답변 반환
        return result["messages"][-1].content
