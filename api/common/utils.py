from langchain_core.callbacks import BaseCallbackHandler
import json

###############################################################
# 커스텀 콜백 핸들러 - LLM 호출 상세 정보 출력
###############################################################     
class LoggingCallbackHandler(BaseCallbackHandler):
    def on_llm_start(self, serialized, prompts, **kwargs):
        print("\n*******************************\n")
        print("===== 요청 프롬프트 =====")
        print(prompts)
        print("\n===== 요청 추가 파라미터 =====")
        print(json.dumps(kwargs, indent=2, ensure_ascii=False, default=str))

    def on_llm_end(self, response, **kwargs):
        print("\n===== 응답 메시지 =====")
        print(response)        
        print("\n===== 응답 추가 파라미터 =====")
        print(json.dumps(kwargs, indent=2, ensure_ascii=False, default=str))
        print("\n*******************************\n")