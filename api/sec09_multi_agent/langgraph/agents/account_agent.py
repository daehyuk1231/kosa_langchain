import logging
from langchain.agents import create_agent

#################################################################################
# Agent 클래스
#################################################################################
class AccountAgent:
    """
    계정 관리 Agent
    계정 관련 문의(로그인, 비밀번호, 회원정보 등)에 대한 답변을 제공합니다.
    """    
    # 초기화 메소드
    def __init__(self, model: str = "openai:gpt-4o-mini"):
        self.logger = logging.getLogger(f"{__name__}.AccountAgent")
        self.agent = create_agent(
            model=model,
            system_prompt="""당신은 계정 관리팀 전문가입니다.
                계정, 로그인, 비밀번호, 회원정보 수정 등에 대해 답변합니다.
                사용자 정보와 지식 베이스 정보를 참고하여 친절하고 안전한 답변을 제공하세요.
                답변 형식은 다음과 같습니다.
                
                👤 계정 관리팀 답변:
                안녕하세요, 계정 관리팀입니다.
                
                [사용자 정보]
                
                [지식 베이스 정보]
                
                계정 보안 팁:
                - 비밀번호는 주기적으로 변경
                - 2단계 인증 설정 권장
                - 개인정보는 타인 공유 금지
                
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
        self.logger.info("계정 관리 에이전트 실행")
        
        # 최종 답변 생성 요청
        prompt = f"""
            다음 고객 문의에 대해 계정 관리팀 답변을 작성해주세요.
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
