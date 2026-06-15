import logging

from langgraph.graph import END, START, StateGraph

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
        # 그래프에 엣지 추가
        graph.add_edge(START, END)
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