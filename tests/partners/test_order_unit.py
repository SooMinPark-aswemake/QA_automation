import re
import pytest
from playwright.sync_api import Page, expect

def test_orderlist(logged_in_page: Page, stop_mart_holiday) -> None:
    """주문관리 화면 테스트"""
    page = logged_in_page

    # 주문관리 페이지가 로드되었는지 확인
    try:
        page.get_by_role("heading", name="주문관리").wait_for(state="visible", timeout=5000)
    except:
        assert False, "주문관리 페이지 로드 실패"

    