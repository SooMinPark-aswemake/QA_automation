import pytest
from playwright.sync_api import Page, Browser, BrowserContext, sync_playwright
from typing import Generator
import requests
from datetime import datetime
import time
import os
from dotenv import load_dotenv

# 슬랙 메세지 전송
def pytest_configure(config):
    load_dotenv()
    """Slack 웹훅 URL 등록"""
    config.slack_webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    config.last_request_time = 0  # 마지막 요청 시간 추적

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    
    if report.when == "call":
        # Rate limiting (최소 1초 간격)
        current_time = time.time()
        if hasattr(item.config, "last_request_time"):
            time_diff = current_time - item.config.last_request_time
            if time_diff < 1:
                time.sleep(1 - time_diff)
        
        print(f"테스트 실행: {item.name}")
        test_status = "성공" if report.passed else "실패"
        message = (
            f"*Playwright 테스트 결과*\n"
            f"*테스트 이름*\n{item.name}\n"
            f"*상태*\n{test_status}\n"
            f"*실행 시간*\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        if hasattr(item.config, "slack_webhook_url"):
            try:
                response = requests.post(
                    item.config.slack_webhook_url,
                    json={"text": message, "mrkdwn": True},
                    timeout=10
                )
                response.raise_for_status()
                print(f"테스트 결과 전송 완료: {item.name}")
                item.config.last_request_time = time.time()
            except Exception as e:
                print(f"Slack 전송 실패 ({item.name}): {str(e)}")


# Playwright 관련 설정
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

# 파트너스 로그인 페이지 진입 및 로그인 설정
@pytest.fixture
def login_page(page: Page) -> Page:
    """로그인 페이지 초기화"""
    page.goto("https://dev-partners.qmarket.me/login")
    return page

@pytest.fixture
def logged_in_page(page: Page) -> Page:
    """로그인 상태의 페이지 제공"""
    # 환경변수 로드
    load_dotenv()
    
    # 환경변수 확인
    id = os.getenv('qmarket_id')
    pw = os.getenv('qmarket_pw')
    
    # 로그인 페이지로 이동
    page.goto("https://dev-partners.qmarket.me/login")
    
    # 로그인 실행
    page.get_by_placeholder("아이디를 입력해주세요").fill(id)
    page.get_by_placeholder("비밀번호를 입력해주세요").fill(pw)

    # 로그인 버튼 클릭
    page.get_by_role("button", name="로그인").click()
    
    return page

@pytest.fixture(scope="session")
def base_url() -> str:
    """기본 URL 제공"""
    return "https://dev-partners.qmarket.me"