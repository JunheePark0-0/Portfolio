# tool로 정의할 필요 없는 일반 함수들
# schemas : EmailItem, ParsedQuery, EmailFetchInput, EmailFetchOutput, EmailFetchOutputs, UserChoice
from py_files.schemas import EmailItem, ParsedQuery, EmailFetchInput, EmailFetchOutput, UserChoice, ParsedPrompt, EmailReply
from py_files.states import EmailAgentState, EmailAgentState2
from typing import TypedDict, List


# 프롬프트 로드 함수
# prompts
def load_prompts(name : str):
    import yaml
    from datetime import datetime

    with open("prompts/prompts.yaml", "r") as f:
        prompts = yaml.safe_load(f)
        
    prompt = prompts[name]

    if name == "fetching_email_prompt" or name == "fetching_email_with_feedback_prompt":
        today_date = datetime.now().strftime("%Y-%m-%d")
        prompt["instructions"] = prompt["instructions"].format(today_date = today_date)
        
    return prompt


# 쿼리 파싱 함수
def parse_query(query : str) -> ParsedQuery:
    """쿼리를 파싱하여 주어진 형식에 맞는 파싱 결과를 반환"""
    from langchain_core.prompts import ChatPromptTemplate
    from langchain.chat_models import init_chat_model

    query_parser_prompt = load_prompts("query_parser_prompt")
    
    llm_structured = init_chat_model("openai:gpt-4o-mini", temperature=0.0).with_structured_output(ParsedQuery)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", query_parser_prompt['role'] + "\n" + query_parser_prompt['instructions']),
            ("user", query_parser_prompt["inputs"].format(query = query))
        ]
    )
    messages = prompt.format_messages(query = query)
    response = llm_structured.invoke(messages)

    return response


# 이메일 검색 함수
def fetch_email(parsed_query: ParsedQuery, email_dicts: List[dict]) -> EmailFetchOutput:
    """파싱된 쿼리를 사용하여 관련 이메일 찾아서 반환 + 수동 메시지 생성"""
    from typing import List, Dict, Optional, Literal
    from langchain.chat_models import init_chat_model
    from langchain_core.messages import SystemMessage, HumanMessage

    fetching_email_prompt = load_prompts("fetching_email_prompt")
    
    # 이메일 포맷팅
    formatted_emails = []
    for email in email_dicts:
        formatted_email = {
            "id": email["id"],
            "subject": email["subject"], 
            "sender": email["sender"],
            "date": email["date"],
            "content": email["content"][:200] + "..." if len(email["content"]) > 200 else email["content"]
        }
        formatted_emails.append(formatted_email)
    
    # 메시지 수동 생성
    system_content = fetching_email_prompt['role'] + "\n" + fetching_email_prompt['instructions']
    user_content = fetching_email_prompt["inputs"].format(
        parsed_query = parsed_query.model_dump(), 
        emails = formatted_emails
    )
    
    messages = [
        SystemMessage(content = system_content),
        HumanMessage(content = user_content)
    ]
    
    # LLM 호출
    llm_structured = init_chat_model("openai:gpt-4o-mini", temperature=0.0).with_structured_output(EmailFetchOutput)
    response = llm_structured.invoke(messages)

    return response, formatted_emails

def categorize_user_response(user_response : str) -> UserChoice:
    """사용자 피드백을 카테고리로 분류"""
    from langchain.chat_models import init_chat_model
    from langchain_core.messages import SystemMessage, HumanMessage

    categorize_prompt = load_prompts("categorize_prompt")
    
    system_content = categorize_prompt['role'] + "\n" + categorize_prompt['instructions']
    user_content = categorize_prompt["inputs"].format(user_response = user_response)
    
    messages = [
        SystemMessage(content = system_content),
        HumanMessage(content = user_content)
    ]
    
    llm_structured = init_chat_model("openai:gpt-4o-mini", temperature=0.0).with_structured_output(UserChoice)
    response = llm_structured.invoke(messages)

    return response

def fetch_email_with_feedback(parsed_query: ParsedQuery, formatted_emails: List[dict], user_feedback: str = None, previous_email: EmailItem = None) -> EmailFetchOutput:
    """사용자 피드백을 반영하여 이메일을 재검색하는 함수"""
    from typing import List, Dict, Optional, Literal
    from langchain.chat_models import init_chat_model
    from langchain_core.messages import SystemMessage, HumanMessage

    fetching_email_feedback_prompt = load_prompts("fetching_email_with_feedback_prompt")
    
    # 기본 시스템 메시지
    system_content = fetching_email_feedback_prompt['role'] + "\n" + fetching_email_feedback_prompt['instructions']
    
    # 사용자 콘텐츠 생성
    user_content = fetching_email_feedback_prompt["inputs"].format(
        parsed_query = parsed_query.model_dump(), 
        emails = formatted_emails,
        user_feedback = user_feedback,
        previous_email = previous_email
    )
    
    messages = [
        SystemMessage(content = system_content),
        HumanMessage(content = user_content)
    ]
    
    # LLM 호출
    llm_structured = init_chat_model("openai:gpt-4o-mini", temperature=0.0).with_structured_output(EmailFetchOutput)
    response = llm_structured.invoke(messages)

    return response

def should_retry(state : EmailAgentState) -> str:
    """사용자 피드백에 따라 다음 단계 결정"""
    if not state.get("user_feedback"):
        return "error"

    feedback = state["user_feedback"]
    if hasattr(feedback, "kind"):
        if feedback.kind == "CONFIRM":
            return "completed"
        else:
            return "email_fetcher"
    else:
        return "error"


def parse_prompt(prompt : str) -> ParsedPrompt:
    """요구사항을 파싱하여 주어진 형식에 맞는 파싱 결과를 반환"""
    from langchain_core.prompts import ChatPromptTemplate
    from langchain.chat_models import init_chat_model

    prompt_parser_prompt = load_prompts("prompt_parser_prompt")
    
    llm_structured = init_chat_model("openai:gpt-4o-mini", temperature=0.0).with_structured_output(ParsedPrompt)
    
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", prompt_parser_prompt['role'] + "\n" + prompt_parser_prompt['instructions']),
            ("user", prompt_parser_prompt["inputs"].format(prompt = prompt))
        ]
    )

    messages = prompt.format_messages(prompt = prompt)
    response = llm_structured.invoke(messages)

    return response 

def parse_edit_request(parsed_prompt : ParsedPrompt, edit_request : str) -> ParsedPrompt:
    """수정 요구사항을 파싱하여 주어진 형식에 맞는 파싱 결과를 반환"""
    from langchain_core.prompts import ChatPromptTemplate
    from langchain.chat_models import init_chat_model

    edit_request_parser_prompt = load_prompts("edit_request_parser_prompt")
    
    llm_structured = init_chat_model("openai:gpt-4o-mini", temperature=0.0).with_structured_output(ParsedPrompt)
    
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", edit_request_parser_prompt['role'] + "\n" + edit_request_parser_prompt['instructions']),
            ("user", edit_request_parser_prompt["inputs"].format(parsed_prompt = parsed_prompt, edit_request = edit_request))
        ]
    )
    
    messages = prompt.format_messages(parsed_prompt = parsed_prompt, edit_request = edit_request)
    response = llm_structured.invoke(messages)

    return response

def generate_email_reply(fetched_email : EmailFetchOutput, previous_reply : EmailReply, prompt : ParsedPrompt) -> EmailReply:
    """이메일 답변을 생성하는 함수(초안, 수정 둘 다 사용)"""
    from langchain_core.prompts import ChatPromptTemplate
    from langchain.chat_models import init_chat_model

    email_reply_prompt = load_prompts("email_reply_prompt")

    llm_structured = init_chat_model("openai:gpt-4o-mini", temperature=0.0).with_structured_output(EmailReply)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", email_reply_prompt['role'] + "\n" + email_reply_prompt['instructions']),
            ("user", email_reply_prompt["inputs"].format(fetched_email = fetched_email, previous_reply = previous_reply, prompt = prompt))
        ]
    )
    
    messages = prompt.format_messages(fetched_email = fetched_email, previous_reply = previous_reply, prompt = prompt) # 초안이면 previous_reply는 None
    response = llm_structured.invoke(messages)

    return response

def should_edit(state : EmailAgentState2) -> str:
    """사용자 피드백에 따라 다음 단계 결정"""
    if not state.get("user_feedback"):
        return "error"
    
    feedback = state["user_feedback"]
    if hasattr(feedback, "kind"):
        if feedback.kind == "CONFIRM":
            return "completed"
        else:
            return "feedback_edit"
    else:
        return "error"