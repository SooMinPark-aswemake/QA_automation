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
    tabs = ["주문대기", "배달대기", "배달중", "배달완료", "환불대기"]

    for tab in tabs:
        try:
            tab_selector = f"span.css-jye6wx-OrderTabText-OrderTabText:text('{tab}')"
            expect(page.locator(tab_selector)).to_be_visible(timeout=5000)
        except:
            assert False, f"{tab} 탭이 보이지 않습니다"

    # 대시보드 노출 확인
    #page.locator("span.css-jye6wx-OrderTabText-OrderTabText:text('주문대기')").wait_for(state="visible", timeout=5000)
    #page.locator("span.css-jye6wx-OrderTabText-OrderTabText:text('배달대기')").wait_for(state="visible", timeout=5000)
    #page.locator("span.css-jye6wx-OrderTabText-OrderTabText:text('배달중')").wait_for(state="visible", timeout=5000)
    #page.locator("span.css-jye6wx-OrderTabText-OrderTabText:text('배달완료')").wait_for(state="visible", timeout=5000)
    #page.locator("span.css-jye6wx-OrderTabText-OrderTabText:text('환불대기')").wait_for(state="visible", timeout=5000)

    # 주문상세 진입
    try:
        # 정확한 클래스명으로 상세보기 링크 찾기
        order_detail = page.locator("a.css-164qccr-OrderList").first
        expect(order_detail).to_be_visible(timeout=5000)
        order_detail.click()

        expect(page.get_by_text("주문 상세").first).to_be_visible(timeout=5000)

    except:
        assert False, "주문없음"
