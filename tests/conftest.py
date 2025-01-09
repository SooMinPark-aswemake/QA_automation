import pytest
import datetime
import requests
import re  # re.compile을 위해 필요
from playwright.sync_api import sync_playwright, Page

@pytest.fixture(scope="function")
def page() -> Page:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        context.tracing.start(screenshots=True, snapshots=True, sources=True)  # 트레이싱 시작
        page = context.new_page()
        page.goto("https://partners.qmarket.me/login")
        
        # 로그인 절차
        try:
            page.locator("div").filter(has_text=re.compile(r"^닫기$")).get_by_role("button").click(timeout=5000)
        except:
            pass
        
        page.get_by_placeholder("아이디를 입력해주세요").click()
        page.get_by_placeholder("아이디를 입력해주세요").fill("qmarket")
        page.get_by_placeholder("비밀번호를 입력해주세요").click()
        page.get_by_placeholder("비밀번호를 입력해주세요").fill("qmarket!@#")
        page.get_by_role("button", name="로그인").click()
        
        yield page
        
        context.tracing.stop(path="trace.zip")  # 트레이싱 종료 및 파일 저장

def send_slack_message(webhook_url, status, test_name, error_message=None):
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # datetime 모듈 수정
    color = "#36a64f" if status == "성공" else "#ff0000"
    
    message = {
        "attachments": [
            {
                "color": color,
                "title": "Playwright 테스트 결과",
                "fields": [
                    {"title": "테스트 이름", "value": test_name, "short": True},
                    {"title": "상태", "value": status, "short": True},
                    {"title": "실행 시간", "value": current_time, "short": True}
                ]
            }
        ]
    }
    
    if error_message:
        message["attachments"][0]["fields"].append({
            "title": "에러 메시지",
            "value": error_message,
            "short": False
        })
    
    try:
        response = requests.post(webhook_url, json=message)
        print(f"Slack 전송 상태: {response.status_code}")  # 디버깅용
    except Exception as e:
        print(f"Slack 전송 에러: {str(e)}")  # 디버깅용

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    webhook_url = "https://hooks.slack.com/services/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"  # 실제 webhook URL 필요
    
    outcome = yield
    result = outcome.get_result()
    
    if result.when == "call":
        if result.passed:
            send_slack_message(webhook_url, "성공", item.name)
        elif result.failed:
            send_slack_message(webhook_url, "실패", item.name, str(result.longrepr))