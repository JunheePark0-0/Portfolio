# tool로 정의할 함수들

from langchain_core.tools import tool
from typing import List, Dict

@tool
def get_email_tool() -> List[Dict]:
    """사용자 이메일 가져오는 함수"""
    from .api_tools import parse_emails
    return parse_emails()

@tool
def send_email_tool(to : str, subject : str, text : str) -> str:
    """사용자 이메일 보내는 함수"""
    from .api_tools import send_emails
    return send_emails(to, subject, text)

