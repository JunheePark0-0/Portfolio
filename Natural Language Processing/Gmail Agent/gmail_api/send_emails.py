import base64
from email.mime.text import MIMEText
from email.message import EmailMessage

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import os, sys

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

def send_emails(to, subject, text):
    """
    to : 받는 사람
    subject : 제목
    text : 내용
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    token_path = os.path.join(script_dir, "token.json")
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
    to = sys.argv[1]
    subject = sys.argv[2]
    text = sys.argv[3]
    send_emails(to, subject, text)