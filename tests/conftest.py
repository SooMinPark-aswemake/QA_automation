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
        
        # 실행 시간을 초 단위로 가져와서 소수점 2자리까지 표시
        duration = f"{call.duration:.2f}"

        # 에러 메세지 추가
        error_message = ""
        if report.failed:
            if hasattr(call, 'excinfo'):
                error_message = f"\n*에러 메시지*\n```{str(call.excinfo.value)}```"
                
                # 스크린샷 저장
                try:
                    page = item.funcargs.get('page')
                    if page:
                        screenshot_path = f"screenshots/failed_{item.name}_{int(time.time())}.png"
                        page.screenshot(path=screenshot_path)
                        error_message += f"\n*스크린샷*\n{screenshot_path}"
                except Exception as e:
                    print(f"스크린샷 저장 실패: {str(e)}")
        
        message = (
            f"*Playwright 테스트 결과*\n"
            f"*테스트 이름*\n{item.name}\n"
            f"*상태*\n{test_status}\n"
            f"*실행 시간*\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"*소요 시간*\n{duration}초"  # 실행 시간 추가
            f"{error_message}"
        )
        
        if hasattr(item.config, "slack_webhook_url"):
            try:
                # 기본 메세지 전송
                response = requests.post(
                    item.config.slack_webhook_url,
                    json={"text": message, "mrkdwn": True},
                    timeout=10
                )
                response.raise_for_status()

                # 실패 시 스크린샷 파일 전송
                if report.failed and os.path.exists(screenshot_path):
                    with open(screenshot_path, 'rb') as file:
                        response = requests.post(
                            item.config.slack_webhook_url,
                            files={'file': file},
                            data={'initial_comment': f'{item.name} 실패 스크린샷'},
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
    browser = playwright.chromium.launch(
        headless=False,
        slow_mo=1000)
    yield browser
    browser.close()
    playwright.stop()

@pytest.fixture(scope="session")
def context(browser: Browser) -> Generator[BrowserContext, None, None]:
    """브라우저 컨텍스트 생성"""
    context = browser.new_context()
    yield context
    context.close()

@pytest.fixture(scope="session")
def page(context: BrowserContext) -> Generator[Page, None, None]:
    """새로운 페이지 생성"""
    page = context.new_page()
    yield page
    page.close()

# 파트너스 로그인 페이지 진입 및 로그인 설정
@pytest.fixture(scope="session")
def login_page(page: Page) -> Page:
    """로그인 페이지 초기화"""
    page.goto("https://dev-partners.qmarket.me/login")
    return page

@pytest.fixture(scope="session")
def logged_in_page(login_page: Page) -> Page:
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

@pytest.fixture(scope="session")
def stop_mart_holiday(page: Page) -> Page:
    """마트 휴무일 모달 노출 예외처리"""
    try:
        # 페이지 로드 대기
        page.wait_for_load_state("networkidle")
        
        # 모달 내의 모든 p 태그 텍스트 출력하여 확인
        modal = page.locator("div.ReactModalPortal p")
        print("Found text:", modal.all_text_contents())
        
        # 부분 텍스트 매칭으로 시도
        modal_text = page.get_by_text("배달중단", exact=False)
        modal_text.wait_for(state="visible", timeout=5000)
        
        if modal_text.is_visible():
            page.get_by_role("button", name="오늘 하루 다시 보지 않기").click()
            print("휴무일 모달 처리 완료")
            
    except Exception as e:
        print(f"휴무일 모달 처리 중 예외 발생: {str(e)}")
        print("페이지 현재 URL:", page.url)
        print("현재 페이지 내용:", page.content())
        pass
    
    return page

@pytest.fixture(scope="function", autouse=True)
def trace_test(request, page: Page):
    # 테스트 시작 시 tracing 시작
    page.context.tracing.start(
        screenshots=True,
        snapshots=True,
        sources=True
    )
    
    yield
    
    # 테스트 실패 시에만 trace 저장
    test_failed = request.node.rep_call.failed if hasattr(request.node, "rep_call") else False
    if test_failed:
        test_name = request.node.name
        page.context.tracing.stop(path=f"./traces/failed_{test_name}.zip")
    else:
        page.context.tracing.stop()


@pytest.fixture(scope="session")
def wakeup_alram(page: Page) -> Page:
    """화면 클락 알람 예외처리"""
    try:
        # 페이지 로드 대기
        page.wait_for_load_state("networkidle", timeout=5000)
        
        # 알람 텍스트 locator 정의
        alert_text = page.locator("p.css-1upqwjo-NewOrderAlertPopup")
        
        try:
            # 요소가 있는지 먼저 확인 (짧은 타임아웃)
            if alert_text.count() > 0:
                # 요소가 보이는지 확인
                if alert_text.is_visible():
                    print("알림 팝업 발견")
                    # 클릭 수행
                    alert_text.click()
                    print("알림 팝업 클릭 완료")
                    
                    # 클릭 후 요소가 사라졌는지 확인
                    try:
                        alert_text.wait_for(state="hidden", timeout=5000)
                        print("알림 팝업이 정상적으로 사라짐")
                    except TimeoutError:
                        print("경고: 알림 팝업이 클릭 후에도 사라지지 않음")
                        page.screenshot(path="error-popup-not-hidden.png")
            else:
                print("알림 팝업이 없음 - 정상 진행")
                
        except Exception as e:
            print(f"알림 팝업 처리 중 예외 발생: {str(e)}")
            page.screenshot(path="error-popup-processing.png")
            
    except Exception as e:
        print(f"페이지 로드 중 예외 발생: {str(e)}")
        print("현재 URL:", page.url)
        page.screenshot(path="error-page-load.png")
    
    return page