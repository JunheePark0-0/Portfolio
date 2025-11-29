from typing import Dict, List, Callable, Any, Optional
from langchain_core.tools import BaseTool

def get_tools(tool_names : Optional[List[str]] = None) -> List[BaseTool]:
    """이름으로 tool call, 이름이 비어있다면 모든 tool 불러오기"""
    # defaul tools
    from tools.api_tools import get_emails, parse_emails, send_emails

    # Base tools dictionary
    tools_dict = {
        "get_emails": get_emails,
        "parse_emails": parse_emails,
        "send_emails": send_emails
    }

    # 이름으로 tool call, 이름이 비어있다면 모든 tool 불러오기
    if tool_names is None:
        return list(tools_dict.values())

    return [tools_dict[name] for name in tool_names if name in tools_dict]

def get_tools_by_name(tools : Optional[List[BaseTool]] = None) -> Dict[str, BaseTool]:
    """tool 이름으로 tool call, 이름이 비어있다면 모든 tool 불러오기"""
    if tools is None:
        return get_tools()
        
    return {tool.name: tool for tool in tools}