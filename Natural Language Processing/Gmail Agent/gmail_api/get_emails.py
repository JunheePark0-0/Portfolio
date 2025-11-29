from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os, sys
import base64
from typing import List, Dict

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def get_emails(label_name):
    # project_root = os.path.dirname("Multi-Agent-System")
    # script_dir = os.path.join(project_root, "gmail_api")
    # token_path = os.path.join(script_dir, "token.json")
    token_path = "token.json"

    creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    service = build("gmail", "v1", credentials = creds)

    # 특정 라벨에 대한 이메일 10개 
    results = service.users().messages().list(
        userId = "me",
        labelIds = [f"{label_name}"],
        maxResults = 5
    ).execute()
    payloads = []
    ids = []

    messages = results.get("messages", [])
    if not messages:
        print("No messages found")
    else:
        print("Chat messages : ")

        for message in messages:
            ids.append(message["id"])
            message_data = service.users().messages().get(userId = "me", id = message["id"], format = "full").execute()
            payload = message_data.get("payload", {})
            payloads.append(payload)
            headers = payload.get("headers", [])
            subject = next(h["value"] for h in headers if h["name"] == "Subject")
            sender = next(h["value"] for h in headers if h["name"] == "From")
            print(f"- subject: {subject} | sender: {sender}")
            print(f"| id: {message['id']} | Snippet: {message_data.get('snippet')}")
    
    return payloads, ids

def parse_emails(label_name) -> List[Dict]:
    f"""
    label_name : 라벨 이름
    return : 라벨에 해당하는 메일들의 정보를 담은 리스트
    [{"id", "subject", "sender", "date", "content"}...]
    """
    input_payloads, input_ids = get_emails(label_name)
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
    
if __name__ == "__main__":
    label_name = sys.argv[1]
    get_emails(label_name)