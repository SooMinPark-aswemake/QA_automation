import re
import pytest
from playwright.sync_api import Page, expect, sync_playwright, Playwright, Browser, BrowserContext

def test_header(page: Page) -> None:
    page.goto("https://partners.qmarket.me/login")

    try:
        page.locator("div").filter(has_text=re.compile(r"^닫기$")).get_by_role("button").click(timeout=5000)
    except:
        pass

    try:
        page.get_by_role("heading", name="주문관리").wait_for(state="visible", timeout=5000)

    except:
        assert False

    page.get_by_role("link", name="상품관리").click()

    try:
        page.get_by_role("heading", name="상품관리").wait_for(state="visible", timeout=5000)

    except:
        assert False

    page.get_by_role("link", name="이벤트관리").click()

    try:
        page.get_by_role("heading", name="마트할인").wait_for(state="visible", timeout=5000)

    except:
        assert False

    page.get_by_role("link", name="매출/정산").click()

    try:
        page.get_by_role("heading", name="매출/정산").wait_for(state="visible", timeout=5000)

    except:
        assert False

    page.get_by_role("link", name="공지사항관리").click()

    try:
        page.get_by_role("heading", name="마트 공지사항").wait_for(state="visible", timeout=5000)

    except:
        assert False

def test_order_page(page: Page) -> None:

    try:
        page.get_by_role("heading", name="주문관리").wait_for(state="visible", timeout=5000)

    except:
        assert False

    page.get_by_role("link", name="상품관리").click()

    try:
        page.get_by_role("heading", name="상품관리").wait_for(state="visible", timeout=5000)

    except:
        assert False
 

    page.pause()

def test_product_page(page: Page) -> None:

    try:
        page.get_by_role("heading", name="상품관리").wait_for(state='visible', timeout=5000)
    except:
        page.get_by_role("link", name="상품관리").click()
    page.once("dialog", lambda dialog: dialog.dismiss())
    with page.expect_popup() as page1_info:
        page.get_by_role("button", name="일괄 상품 등록/수정").click()
    page1 = page1_info.value
    page1.close()
    page.get_by_role("button", name="단일 상품 등록").click()
    page.get_by_text("단일 상품 등록").click()
    page.get_by_role("main").get_by_role("link", name="상품관리").click()
    page.get_by_text("페이지에서 벗어나시겠습니까? 수정된 내용은 반영되지 않습니다").click()
    page.get_by_role("button", name="머무르기").click()
    page.get_by_role("main").get_by_role("link", name="상품관리").click()
    page.get_by_role("button", name="나가기").click()
    page.get_by_role("button", name="이미지 일괄등록").click()
    page.get_by_text("이미지 일괄등록", exact=True).click()
    page.get_by_role("main").get_by_role("link", name="상품관리").click()
    page.get_by_role("button", name="추천상품 관리").click()
    page.get_by_text("추천상품 관리").click()
    page.get_by_role("main").get_by_role("link", name="상품관리").click()
    page.get_by_role("button", name="채소").click()
    page.get_by_role("button", name="청과").click()
    page.get_by_role("button", name="정육").click()
    page.get_by_role("button", name="수산").click()
    page.get_by_role("button", name="전체 상품 (공산품 + 신선식품)").click()

    page.pause()