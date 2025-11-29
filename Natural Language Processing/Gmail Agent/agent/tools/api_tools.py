from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import os
import base64
from typing import List, Dict, Tuple
from langchain_core.tools import tool


def get_token_path() -> str:
    """token.json 파일 경로 반환"""
    project_root = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(os.path.dirname(project_root), "gmail_api", "token.json")


def get_emails():
    """Fetch raw Gmail payloads for the most recent messages in the inbox."""
    token_path = get_token_path()

    creds = Credentials.from_authorized_user_file(token_path, ["https://www.googleapis.com/auth/gmail.readonly"])
    service = build("gmail", "v1", credentials=creds)

    results = service.users().messages().list(
        userId = "me",
        labelIds = ["INBOX"],
        maxResults = 20 ##### 수정 #####
    ).execute()
    
    payloads = []
    ids = []

    messages = results.get("messages", [])
    if not messages:
        print("No messages found")

    for message in messages:
        ids.append(message["id"])
        message_data = service.users().messages().get(userId = "me", id = message["id"], format = "full").execute()
        payload = message_data.get("payload", {})
        payloads.append(payload)
    
    return payloads, ids

def parse_emails() -> List[Dict]:
    """
    return : INBOX에 있는 메일들의 정보를 담은 리스트
    [{"id", "subject", "sender", "date", "content"}...]
    """
    input_payloads, input_ids = get_emails()
    email_dicts = []
    for payload, id in zip(input_payloads, input_ids):
        headers = payload.get("headers", [])
        subject = next(h["value"] for h in headers if h["name"] == "Subject")
        sender = next(h["value"] for h in headers if h["name"] == "From")
        date = next(h["value"] for h in headers if h["name"] == "Date")
        
        text = ""
        if "parts" in payload:
            for part in payload["parts"]:
                if part.get("mimeType") == "text/plain":
                    data = part.get("body", {}).get("data", "")
                    if data:
                        text = base64.urlsafe_b64decode(data).decode('utf-8')
        else:
            data = payload.get("body", {}).get("data", "")
            if data:
                text = base64.urlsafe_b64decode(data).decode('utf-8')

        email_dicts.append({"id": id, "subject": subject, "sender": sender, "date": date, "content": text})
        
    return email_dicts


from email.message import EmailMessage


def send_emails(to, subject, text):
    """
    to : 받는 사람
    subject : 제목
    text : 내용
    """
    token_path = get_token_path()
    SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
    creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    service = build("gmail", "v1", credentials = creds)
    
    try:
        message = EmailMessage()
        message.set_content(text)

        message["to"] = to
        message["subject"] = subject

        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        send_message = {"raw" : encoded_message}

        sent = (
            service.users()
            .messages()
            .send(userId = "me", body = send_message)
            .execute()
        )

        print(f'Message Id: {sent["id"]}')
        return sent

    except Exception as e:
        print("Error occurred :", e)
        return None    

if __name__ == "__main__":
    get_emails()

