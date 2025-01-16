# 전체 주문관리 화면 검증

import re
import pytest
from playwright.sync_api import Page, expect

def test_orderlist(logged_in_page: Page, stop_mart_holiday) -> None:
    """주문관리 화면 테스트"""
    page = logged_in_page

    elements = page.locator("span").all()

    # 주문관리 페이지가 로드되었는지 확인
    try:
        page.get_by_role("heading", name="주문관리").wait_for(state="visible", timeout=5000)
    except:
        assert False, "주문관리 페이지 로드 실패"

    # 대시보드 노출 확인
    page.locator("span.css-jye6wx-OrderTabText-OrderTabText:text('주문대기')").wait_for(state="visible", timeout=5000)
    page.locator("span.css-jye6wx-OrderTabText-OrderTabText:text('배달대기')").wait_for(state="visible", timeout=5000)
    page.locator("span.css-jye6wx-OrderTabText-OrderTabText:text('배달중')").wait_for(state="visible", timeout=5000)
    page.locator("span.css-jye6wx-OrderTabText-OrderTabText:text('배달완료')").wait_for(state="visible", timeout=5000)
    page.locator("span.css-jye6wx-OrderTabText-OrderTabText:text('환불대기')").wait_for(state="visible", timeout=5000)
