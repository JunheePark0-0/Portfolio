# Schema - State의 형식을 정돈하는 역할

from typing import List, Dict, Optional, Literal
from pydantic import BaseModel, Field

class EmailItem(BaseModel):
    """이메일 하나"""
    id : str
    subject : str 
    sender : str
    date : str 
    content : str 

class ParsedQuery(BaseModel):
    """쿼리 파싱 결과"""
    content : List[str] = Field(..., description = "The content extracted from the query")
    when : Optional[str] = Field(description = "The period hints extracted from the query")
    sender : Optional[str] = Field(description = "The sender extracted from the query")

class EmailFetchInput(BaseModel):
    """이메일 검색 입력"""
    # description 앞에 ...는 필수 항목을 의미함
    query : str = Field(..., description = "The query to fetch emails")
    emails : List[EmailItem] = Field(..., description = "The list of emails")
    top_k : int = Field(..., description = "The max number of emails to fetch")

class EmailFetchOutput(BaseModel):
    """이메일 검색 결과"""
    id : str
    subject : str
    sender : str
    date : str
    content : str
    reasoning : str = Field(..., description = "The reasoning behind the relevance")

class UserChoice(BaseModel):
    """이메일 검색 후 사용자의 피드백"""
    kind : Literal["CONFIRM", "RETRY"]

class ParsedPrompt(BaseModel):
    """요구사항 파싱 결과"""
    instructions : List[str] = Field(..., description = "The instructions extracted from the prompt")
    tone : Optional[str] = Field(description = "The tone extracted from the prompt")
    constraints : Optional[str] = Field(description = "The constraints extracted from the prompt")

class ParsedEditRequest(BaseModel):
    """요청한 수정사항들(하나만 만들어두고 업데이트하기)"""
    instructions : str = Field(..., description = "The instructions for the email reply")
    tone : str = Field(..., description = "The tone of the email reply")
    constraints : str = Field(..., description = "The constraints for the email reply")
    
class EmailReply(BaseModel):
    """생성된 이메일 답변"""
    version : str = Field(..., description = "The version of the email reply")
    to : str = Field(..., description = "The recipient of the email reply")
    subject : str = Field(..., description = "The subject of the email reply")
    content : str = Field(..., description = "The content of the email reply")

