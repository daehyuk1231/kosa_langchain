import json
import logging
from langchain.agents import create_agent
from langchain.tools import tool

#################################################################################
# Tool 정의
#################################################################################
@tool
def get_user_info(user_id: str = "guest") -> str:
    """사용자 정보를 조회합니다.    
    Args:
        user_id: 사용자 ID (기본값: guest)        
    Returns:
        str: 사용자 정보 (이름, 등급, 누적주문, 보유포인트 등)
    """
    # Mock 사용자 데이터
    user_db = {
        "guest": {
            "이름": "게스트",
            "등급": "일반",
            "누적주문": 0,
            "보유포인트": 0
        },
        "user1": {
            "이름": "김철수",
            "등급": "골드",
            "누적주문": 15,
            "보유포인트": 12500
        },
        "user2": {
            "이름": "채정원",
            "등급": "VIP",
            "누적주문": 50,
            "보유포인트": 85000
        }
    }
    
    # 사용자 정보 조회
    user = user_db.get(user_id, user_db["guest"])
    
    # 사용자 정보를 JSON 문자열로 반환
    user_json = json.dumps(user, ensure_ascii=False)
    return user_json


#################################################################################
# Agent 클래스
#################################################################################
class UserInfoAgent:
    # 초기화 메소드
    def __init__(self, model: str = "openai:gpt-4o-mini"):
        self.logger = logging.getLogger(f"{__name__}.UserInfoAgent")
        self.agent = create_agent(
            model=model,
            tools=[get_user_info],
            system_prompt="""당신은 사용자 정보 관리 전문가입니다.
                get_user_info 도구를 사용하여 사용자 정보를 조회하세요."""
        )

    # 에이전트 실행 메소드
    async def run(self, user_id: str = "guest") -> str:
        self.logger.info("사용자 정보 조회 에이전트 실행")
        
        # 사용자 정보 조회 요청
        result = await self.agent.ainvoke(
            {"messages": [
                {"role": "user", 
                 "content": f"사용자 ID '{user_id}'의 정보를 조회해주세요."}
            ]}
        )
        
        # 조회 결과 반환
        return result["messages"][-1].content
