import pytest
from playwright.sync_api import Page, Browser, BrowserContext, sync_playwright
from typing import Generator
import requests
from datetime import datetime

def pytest_configure(config):
    """Slack 웹훅 URL 등록"""
    config.slack_webhook_url = "https://hooks.slack.com/services/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"

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    
    if report.when == "call":
        test_status = "성공" if report.passed else "실패"
        message = (
            f"*Playwright 테스트 결과*\n"
            f"*테스트 이름*\n{item.name}\n"
            f"*상태*\n{test_status}\n"
            f"*실행 시간*\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        if hasattr(item.config, "slack_webhook_url"):
            try:
                requests.post(
                    item.config.slack_webhook_url,
                    json={"text": message, "mrkdwn": True}
                )
            except Exception as e:
                print(f"Slack 전송 실패: {str(e)}")



@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """브라우저 컨텍스트 설정"""
    return {
        **browser_context_args,
        "viewport": {
            "width": 1920,
            "height": 1080,
        },
        "ignore_https_errors": True,
    }

@pytest.fixture(scope="session")
def browser() -> Generator[Browser, None, None]:
    """브라우저 설정"""
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=False)
    yield browser
    browser.close()
    playwright.stop()

@pytest.fixture
def context(browser: Browser) -> Generator[BrowserContext, None, None]:
    """브라우저 컨텍스트 생성"""
    context = browser.new_context()
    yield context
    context.close()

@pytest.fixture
def page(context: BrowserContext) -> Generator[Page, None, None]:
    """새로운 페이지 생성"""
    page = context.new_page()
    yield page
    page.close()

@pytest.fixture
def login_page(page: Page) -> Page:
    """로그인 페이지 초기화"""
    page.goto("https://dev-partners.qmarket.me/login")
    return page

@pytest.fixture
def logged_in_page(page: Page) -> Page:
    """로그인 상태의 페이지 제공"""
    # 로그인 페이지로 이동
    page.goto("https://dev-partners.qmarket.me/login")
    
    # 로그인 실행
    page.get_by_placeholder("아이디를 입력해주세요").fill("qmarket")
    page.get_by_placeholder("비밀번호를 입력해주세요").fill("qmarket!@#")
    page.get_by_role("button", name="로그인").click()
    
    # 로그인 성공 확인
    page.get_by_text("화면을 아무 곳이나 클릭해 주세요").click()
    
    return page

@pytest.fixture(scope="session")
def base_url() -> str:
    """기본 URL 제공"""
    return "https://dev-partners.qmarket.me"