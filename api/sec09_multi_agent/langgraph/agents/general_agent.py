import logging
from langchain.agents import create_agent

#################################################################################
# Agent 클래스
#################################################################################
class GeneralAgent:
    """
    일반 문의 Agent
    특정 카테고리에 속하지 않는 일반 문의에 대한 답변을 제공합니다.
    """
    # 초기화 메소드
    def __init__(self, model: str = "openai:gpt-4o-mini"):
        self.logger = logging.getLogger(f"{__name__}.GeneralAgent")
        self.agent = create_agent(
            model=model,
            system_prompt="""당신은 고객 지원팀 전문가입니다.
                일반적인 문의, 기타 문의 등에 대해 답변합니다.
                사용자 정보와 지식 베이스 정보를 참고하여 친절하고 포괄적인 답변을 제공하세요.
                답변 형식은 다음과 같습니다.

                💬 고객 지원팀 답변:
                안녕하세요, 고객 지원팀입니다.

                [사용자 정보]

                [지식 베이스 정보]

                추가 문의사항:
                - 전화: 1588-1234 (평일 9-18시)
                - 이메일: support@company.com
                - 카카오톡: kakaotalk

                친절하게 안내해드리겠습니다.
                감사합니다."""
        )

    # 에이전트 실행 메소드
    async def run(self, inquiry: str, analysis: str, 
                  user_info: str, knowledge: str) -> str:
        self.logger.info("일반 문의 에이전트 실행")
        
        # 최종 답변 생성 요청
        prompt = f"""
            다음 고객 문의에 대해 고객 지원팀 답변을 작성해주세요.
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
