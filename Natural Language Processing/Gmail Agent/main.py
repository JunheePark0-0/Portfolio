from email_fetcher import email_fetcher_main
from email_responder import email_responder_main

def connect_agents():
    """email_fetcher와 email_responder 에이전트 연결"""
    # email_fetcher 에이전트 실행
    email_fetcher_result = email_fetcher_main()
    # email_responder 에이전트 실행
    fetched_email = email_fetcher_result['fetched_email']
    email_responder_result = email_responder_main(fetched_email)
    return email_responder_result

def main():
    connect_agents()

if __name__ == "__main__":
    main()

