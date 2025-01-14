import re
import pytest
from playwright.sync_api import Page, expect

# test_1depth.py
def test_order_menu(logged_in_page: Page) -> None:
    """주문관리 메뉴 테스트"""
    page = logged_in_page

    # 주문관리 페이지가 로드되었는지 확인
    try:
        page.get_by_role("heading", name="주문관리").wait_for(state="visible", timeout=5000)
    except:
        assert False, "주문관리 페이지 로드 실패"

def test_product_menu(logged_in_page: Page) -> None:
    """상품관리 메뉴 테스트"""
    page = logged_in_page
    
    # 상품관리 메뉴로 이동
    page.get_by_role("link", name="상품관리").click()

    try:
        page.get_by_role("heading", name="상품관리").wait_for(state="visible", timeout=5000)
    except:
        assert False, "상품관리 페이지 로드 실패"

def test_event_menu(logged_in_page: Page) -> None:
    """이벤트관리 메뉴 테스트"""
    page = logged_in_page
    
    # 이벤트관리 메뉴로 이동
    page.get_by_role("link", name="이벤트관리").click()
    
    try:
        page.get_by_role("heading", name="마트할인").wait_for(state="visible", timeout=5000)
    except:
        assert False, "이벤트관리 페이지 로드 실패"

def test_매출정산_menu(logged_in_page: Page) -> None:
    """매출정산 메뉴 테스트"""
    page = logged_in_page
    
    # 매출정산 메뉴로 이동
    page.get_by_role("link", name="매출/정산").click()
    
    try:
        page.get_by_role("heading", name="매출/정산").wait_for(state="visible", timeout=5000)
    except:
        assert False, "매출/정산 페이지 로드 실패"

def test_공지사항관리_menu(logged_in_page: Page) -> None:
    """공지사항관리 메뉴 테스트"""
    page = logged_in_page
    
    # 공지사항관리 메뉴로 이동
    page.get_by_role("link", name="공지사항관리").click()
    
    try:
        page.get_by_role("heading", name="마트 공지사항").wait_for(state="visible", timeout=5000)
    except:
        assert False, "공지사항관리 페이지 로드 실패"