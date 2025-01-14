import re
import pytest
from playwright.sync_api import Page, expect, sync_playwright, Playwright, Browser, BrowserContext

def test_header(logged_in_page: Page) -> None:
    """헤더 네비게이션 테스트"""
    page = logged_in_page  # 이미 로그인된 페이지 사용

    # 팝업 닫기 처리
    try:
        page.locator("div").filter(has_text=re.compile(r"^닫기$")).get_by_role("button").click(timeout=5000)
    except:
        pass

    # 주문관리 페이지 확인
    expect(page.get_by_role("heading", name="주문관리")).to_be_visible(timeout=5000)

    # 상품관리 페이지 이동 및 확인
    page.get_by_role("link", name="상품관리").click()
    expect(page.get_by_role("heading", name="상품관리")).to_be_visible(timeout=5000)

    # 이벤트관리 페이지 이동 및 확인
    page.get_by_role("link", name="이벤트관리").click()
    expect(page.get_by_role("heading", name="마트할인")).to_be_visible(timeout=5000)

    # 매출/정산 페이지 이동 및 확인
    page.get_by_role("link", name="매출/정산").click()
    expect(page.get_by_role("heading", name="매출/정산")).to_be_visible(timeout=5000)

    # 공지사항관리 페이지 이동 및 확인
    page.get_by_role("link", name="공지사항관리").click()
    expect(page.get_by_role("heading", name="마트 공지사항")).to_be_visible(timeout=5000)

def test_order_page(logged_in_page: Page) -> None:
    """주문 페이지 테스트"""
    page = logged_in_page

    # 주문관리 페이지 확인
    expect(page.get_by_role("heading", name="주문관리")).to_be_visible(timeout=5000)

    # 상품관리 페이지 이동 및 확인
    page.get_by_role("link", name="상품관리").click()
    expect(page.get_by_role("heading", name="상품관리")).to_be_visible(timeout=5000)

def test_product_page(logged_in_page: Page) -> None:
    """상품 페이지 테스트"""
    page = logged_in_page

    # 상품관리 페이지로 이동
    try:
        if not page.get_by_role("heading", name="상품관리").is_visible(timeout=2000):
            page.get_by_role("link", name="상품관리").click()
    except:
        page.get_by_role("link", name="상품관리").click()

    # 팝업 처리 설정
    page.once("dialog", lambda dialog: dialog.dismiss())

    # 일괄 상품 등록/수정
    with page.expect_popup() as page1_info:
        page.get_by_role("button", name="일괄 상품 등록/수정").click()
    page1 = page1_info.value
    page1.close()

    # 단일 상품 등록
    page.get_by_role("button", name="단일 상품 등록").click()
    page.get_by_text("단일 상품 등록").click()
    page.get_by_role("main").get_by_role("link", name="상품관리").click()

    # 페이지 이탈 확인 다이얼로그 처리
    try:
        page.get_by_text("페이지에서 벗어나시겠습니까? 수정된 내용은 반영되지 않습니다").wait_for(timeout=2000)
        page.get_by_role("button", name="머무르기").click()
    except:
        pass

    # 상품관리 페이지로 다시 이동
    page.get_by_role("main").get_by_role("link", name="상품관리").click()
    page.get_by_role("button", name="나가기").click()

    # 이미지 일괄등록
    page.get_by_role("button", name="이미지 일괄등록").click()
    page.get_by_text("이미지 일괄등록", exact=True).click()
    page.get_by_role("main").get_by_role("link", name="상품관리").click()

    # 추천상품 관리
    page.get_by_role("button", name="추천상품 관리").click()
    page.get_by_text("추천상품 관리").click()
    page.get_by_role("main").get_by_role("link", name="상품관리").click()

    # 카테고리 버튼 클릭
    categories = ["채소", "청과", "정육", "수산"]
    for category in categories:
        page.get_by_role("button", name=category).click()

    # 전체 상품 보기
    page.get_by_role("button", name="전체 상품 (공산품 + 신선식품)").click()