from typing import List, Dict, Literal, TypedDict, Optional
from .schemas import EmailItem, ParsedQuery, EmailFetchOutput, UserChoice, EmailReply, ParsedEditRequest, ParsedPrompt

class EmailAgentState(TypedDict, total = False):
    """Email Fetcher Agent State"""
    query : str
    all_emails : List[Dict]
    formatted_emails : List[Dict]

    parsed_query : ParsedQuery
    fetched_email : EmailFetchOutput

    # 피드백 
    user_feedback : Optional[UserChoice]
    user_message : Optional[str]
    previous_email : Optional[EmailFetchOutput]  # 이전에 찾은 이메일 저장
    feedback_history : Optional[List[str]]  # 피드백 히스토리

    # state 관리
    status : Literal["INITIAL", "QUERY_PARSED", "EMAIL_COLLECTED", "FETCHED_EMAIL", "RECEIVED_FEEDBACK", "RETRY_SEARCH", "CONFIRMED", "ERROR"]

    error : Optional[str]

class EmailAgentState2(TypedDict, total = False):
    """Email Responder Agent State"""
    fetched_email : EmailFetchOutput

    prompt : str
    parsed_prompt : ParsedPrompt

    # 피드백
    edit_request : Optional[str]
    user_feedback : Optional[UserChoice]
    parsed_edit_request : Optional[ParsedEditRequest]
    feedback_history : Optional[List[str]]

    reply_draft : EmailReply

    # state 관리
    status : Literal["INITIAL", "RECEIVED_PROMPT", "PARSED_PROMPT", "FIRST_DRAFT_GENERATED", "EDIT_REQUEST_PARSED", "CONFIRMED", "ERROR", "EMAIL_SENT"]

    error : Optional[str]
