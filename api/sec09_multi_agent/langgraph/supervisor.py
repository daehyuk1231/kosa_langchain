import logging
from typing import Annotated

from fastapi import Depends
from langgraph.graph import END, START, StateGraph

from api.sec09_multi_agent.langgraph.nodes.account_node import account_node
from api.sec09_multi_agent.langgraph.nodes.analysis_node import analysis_node
from api.sec09_multi_agent.langgraph.nodes.gather_node import gather_node
from api.sec09_multi_agent.langgraph.nodes.general_node import general_node
from api.sec09_multi_agent.langgraph.nodes.knowledge_node import knowledge_node
from api.sec09_multi_agent.langgraph.nodes.order_node import order_node
from api.sec09_multi_agent.langgraph.nodes.refund_node import refund_node
from api.sec09_multi_agent.langgraph.nodes.route_node_fun import route_node_fun
from api.sec09_multi_agent.langgraph.nodes.tech_support_node import tech_support_node
from api.sec09_multi_agent.langgraph.nodes.user_info_node import user_info_node
from api.sec09_multi_agent.langgraph.state import ShareState


class CustomerSupportSupervisor:
    # 초기화 메소드
    def __init__(self) -> None:
        self.logger = logging.getLogger(f"{__name__}.CustomerSupportSupervisor")
        # 그래프(작업 흐름) 구성
        self.build_workflow()
        
    # 그래프(작업 흐름) 구성 메소드
    def build_workflow(self):
        # 그래프 생성
        graph = StateGraph(ShareState)
        
        # 그래프에 노드 추가
        graph.add_node("analysis", analysis_node)
        graph.add_node("user_info", user_info_node)
        graph.add_node("knowledge", knowledge_node)
        graph.add_node("gather", gather_node)
        graph.add_node("tech_support", tech_support_node)
        graph.add_node("order", order_node)
        graph.add_node("refund", refund_node)
        graph.add_node("account", account_node)
        graph.add_node("general", general_node)
        
        # START 노드에서 분석 노드로 연결
        graph.add_edge(START, "analysis")
        # 병렬 처리 노드 연결
        graph.add_edge("analysis", "user_info")
        graph.add_edge("analysis", "knowledge")
        # 병렬 취합 노드 연결
        graph.add_edge("user_info", "gather")
        graph.add_edge("knowledge", "gather")
        # 분기하기
        graph.add_conditional_edges(
            "gather",
            # 취합된 정보를 가지고 어디로 분기할지 반환하는 함수
            route_node_fun,
            # { "리턴값": "다음노드" }
            {
                "tech_support":"tech_support",
                "order":"order",
                "refund":"refund",
                "account":"account",
                "general":"general"
            }
        )
        # END 노드로 연결
        graph.add_edge("tech_support", END)
        graph.add_edge("order", END)
        graph.add_edge("refund", END)
        graph.add_edge("account", END)
        graph.add_edge("general", END)
        
        # 그래프 컴파일
        self.work_flow = graph.compile()
        
    async def run(self, inquiry:str, user_id:str="user1") -> str:
        # 초기 상태 생성
        initial_state = ShareState(
            messages=[],
            user_inquiry=inquiry,
            user_id=user_id,
            inquiry_analysis="",
            user_info="",
            knowledge_base="",
            final_response=""
        )
        # 그래프 실행
        final_state = await self.work_flow.ainvoke(initial_state)
        return final_state["final_response"]
    
    # 그래프 시각화 메소드 (디버깅용)
    def get_graph_image(self):
        return self.work_flow.get_graph().draw_mermaid_png()
    
# 의존성 주입을 위한 타입 힌트 정의
CustomerSupportSupervisorDep = Annotated[CustomerSupportSupervisor, Depends(CustomerSupportSupervisor)]