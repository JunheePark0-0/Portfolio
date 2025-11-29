"""
Email Responder Agent
"""

from langgraph.graph import StateGraph, END, START
from langchain_core.prompts import ChatPromptTemplate
from langchain.chat_models import init_chat_model

import os 
# 프로젝트 루트 설정
project_root = os.path.dirname(os.path.abspath(__file__)) # Multi-Agent-System

from dotenv import load_dotenv
load_dotenv(".env")

# tools
from tools.tools import send_email_tool
# schemas
from py_files.schemas import EmailFetchOutput, ParsedPrompt, ParsedEditRequest, EmailReply, UserChoice
# states
from py_files.states import EmailAgentState, EmailAgentState2
# functions 
from py_files.functions import parse_prompt, parse_edit_request, generate_email_reply, should_edit, categorize_user_response

# 노드들
def get_email_prompt_node(state : EmailAgentState2) -> EmailAgentState2:
    """서치한 이메일 + 프롬프트 저장"""
    try:
        fetched_email = state["fetched_email"]
    except Exception as e:
        print(f"❌ 이메일 가져오기 오류: {str(e)}")
    
    message = f"""어떤 내용의 답장을 작성하고 싶으신가요?"""
    prompt = input(message).strip()
    return {
        "fetched_email" : fetched_email,
        "prompt" : prompt,
        "parsed_prompt" : None,
        "reply_draft" : None,
        "status" : "RECEIVED_PROMPT"
    }

def parse_prompt_node(state : EmailAgentState2) -> EmailAgentState2:
    """프롬프트 파싱 노드드 (이미 프롬프트를 받았다고 생각)"""
    try:
        parsed_prompt = parse_prompt(state["prompt"])
        return {**state, "parsed_prompt" : parsed_prompt, "status" : "PARSED_PROMPT"}
    except Exception as e:
        print(f"❌ 프롬프트 파싱 오류: {str(e)}")
        return {**state, "status" : "ERROR", "error" : str(e)}
    
def generate_email_reply_node(state : EmailAgentState2) -> EmailAgentState2:
    """첫 번째 답장 생성 노드"""
    previous_reply = 'None'
    try:
        reply_draft = generate_email_reply(state["fetched_email"], previous_reply, state["parsed_prompt"])
        return {**state, "reply_draft" : reply_draft, "status" : "FIRST_DRAFT_GENERATED"}
    except Exception as e:
        print(f"❌ 첫 번째 답장 생성 오류: {str(e)}")
        return {**state, "status" : "ERROR", "error" : str(e)}

def edit_with_feedback_node(state : EmailAgentState2) -> EmailAgentState2:
    """사용자 피드백을 반영해서 수정하는 노드"""
    try:
        # 프롬프트 업데이트, 파싱
        parsed_edit_request = parse_edit_request(state["parsed_prompt"], state["edit_request"])
        # 수정해서 답장 생성
        reply_draft = generate_email_reply(state["fetched_email"], state["reply_draft"], parsed_edit_request)
        return {**state, "parsed_edit_request" : parsed_edit_request, "reply_draft" : reply_draft, "status" : "EDIT_REQUEST_PARSED"}
    except Exception as e:
        print(f"❌ 답장 수정 중 오류: {str(e)}")
        return {**state, "status" : "ERROR", "error" : str(e)}

def generate_email_feedback_node(state : EmailAgentState2) -> EmailAgentState2:
    """답장 생성 결과 피드백 노드"""
    # 답장 생성 결과가 없다면..
    if "reply_draft" not in state:
        print("답장 생성 결과가 없습니다..")
        return {**state, "status" : "ERROR", "error" : "No email reply generated"}
    
    reply_draft = state["reply_draft"]
    print("\n" + "="*50)
    print("📧 [사용자 확인 단계]")
    print("="*50)

    message = f"""
작성한 초안:
--------------------------------
제목 : {reply_draft.subject}
받는 사람 : {reply_draft.to}
내용 : {reply_draft.content}
--------------------------------

초안이 마음에 드시나요? 
- '예' 또는 '확인': 답장 초안이 마음에 듭니다
- 그 외: 답장의 구체적인 수정사항을 말씀해주세요
  (예: "더 친절한 말투로", "제목을 바꿔줘" 등)

입력: """

    user_response = input(message).strip()
    
    print(f"\n사용자 입력: '{user_response}'")
    print("사용자 응답 분석 중...")
    try:
        user_choice = categorize_user_response(user_response)

        if user_choice.kind == "CONFIRM":
            print("확인 - 답장 초안대로 진행하겠습니다!")
            return {**state, "user_feedback" : user_choice, "status" : "RECEIVED_FEEDBACK"}
        else:
            print("수정 요구 - 답장을 수정하겠습니다..")
            return {**state, "user_feedback" : user_choice, "edit_request" : user_response, "status" : "RECEIVED_FEEDBACK"}
    
    except Exception as e:
        print(f"오류 발생: {str(e)}")
        print("기본값 - 답장 초안대로 진행하겠습니다..")
        user_choice = UserChoice(kind = "CONFIRM", goto = "email_responder")

        return {**state, "user_feedback" : user_choice, "status" : "RECEIVED_FEEDBACK"}

def completed_node(state : EmailAgentState2) -> EmailAgentState2:
    """완료 노드"""
    print("\n🎉 이메일 답장 작성이 성공적으로 완료되었습니다!")
    return {**state, "status" : "COMPLETED"}

def error_node(state : EmailAgentState2) -> EmailAgentState2:
    """오류 노드"""
    print("\n❌ 이메일 답장 작성 중 오류가 발생했습니다.")
    print(f"오류 메시지: {state['error']}")

def email_sender_node(state : EmailAgentState2) -> EmailAgentState2:
    """이메일 보내기 노드"""
    try:
        to = state["reply_draft"].to
        subject = state["reply_draft"].subject
        text = state["reply_draft"].content
        send_email_tool.invoke({"to": to, "subject": subject, "text": text})
    except Exception as e:
        print(f"❌ 이메일 보내기 중 오류: {str(e)}")
        return {**state, "status" : "ERROR", "error" : str(e)}
    print("\n🎉 이메일 보내기 완료!")
    return {**state, "status" : "EMAIL_SENT"}

def email_responder_agent():
    """이메일 답장 생성 에이전트"""
    workflow = StateGraph(EmailAgentState2)

    # 노드 추가
    workflow.add_node("get_email_prompt", get_email_prompt_node)
    workflow.add_node("parse_prompt", parse_prompt_node)
    workflow.add_node("generate_email_reply", generate_email_reply_node)
    workflow.add_node("edit_with_feedback", generate_email_feedback_node) # 피드백 받는 노드
    workflow.add_node("feedback_edit", edit_with_feedback_node) # 피드백 기반 수정 노드
    workflow.add_node("completed", completed_node)
    workflow.add_node("error", error_node)
    workflow.add_node("email_sender", email_sender_node)

    # 엣지 추가 
    workflow.add_edge("get_email_prompt", "parse_prompt")
    workflow.add_edge("parse_prompt", "generate_email_reply")
    workflow.add_edge("generate_email_reply", "edit_with_feedback")

    workflow.add_conditional_edges(
        "edit_with_feedback",
        should_edit,
        {
            "completed" : "completed",
            "feedback_edit" : "feedback_edit",
            "error" : "error"
        }
    )
    workflow.add_edge("feedback_edit", "edit_with_feedback")
    workflow.add_edge("completed", "email_sender")
    workflow.add_edge("email_sender", END)
    workflow.add_edge("error", END)

    workflow.set_entry_point("get_email_prompt")

    return workflow.compile()

def email_responder_main(fetched_email : EmailFetchOutput = None, query : str = None):
    """이메일 답장 생성 에이전트 실행"""
    print("=" * 60)
    print("📧 이메일 답장 생성 에이전트 실행")
    print("=" * 60)

    print("\n🔄 에이전트 시작...")

    try:
        agent = email_responder_agent()
        result = agent.invoke({"fetched_email": fetched_email, "prompt": query})
        print("\n" + "="*60)
        print("📊 이메일 답장 생성 결과")
        print("="*60)
        print(f"상태: {result.get('status', 'UNKNOWN')}")

        if result.get('reply_draft'):
            reply_draft = result['reply_draft']
            print(f"생성된 답장:")
            print(f"  - 제목: {reply_draft.subject}")
            print(f"  - 내용: {reply_draft.content}")
        
        return result
    except Exception as e:
        print(f"\n❌ 에이전트 실행 중 오류: {str(e)}")
        return None

if __name__ == "__main__":
    email_responder_main()
