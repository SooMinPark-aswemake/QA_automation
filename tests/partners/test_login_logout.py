import re
import pytest
from playwright.sync_api import Page, expect

def test_login_view(login_page: Page):
    """"로그인 화면 검증"""
    page = login_page

    try:
        # 잘못된 계정으로 로그인 시도
        page.get_by_placeholder("아이디를 입력해주세요.").fill("qmarkett")
        page.get_by_placeholder("비밀번호를 입력해주세요.").fill("qmarkett!@#")
        page.get_by_role("button", name="로그인").click()

        # 오류 메세지 확인
        page.get_by_text("아이디 또는 비밀번호가 맞지 않습니다. 다시 확인해주세요").wait_for(state="visible", timeout=5000)


    except:
        assert False, "로그인 성공 또는 오류 메세지 미노출"

    try:
        page.get_by_text("아이디 또는 비밀번호를 잊으셨다면 채널톡으로 문의해 주세요.").wait_for(state="visible", timeout=5000)

    except:
        assert False, "안내문구 미노출"

    try:
        # 큐마켓 입점 문의하기 검증
        with page.expect_popup() as popup_info:
            page.get_by_role("button", name="큐마켓 입점 문의하기").click()
        
        popup = popup_info.value
        popup.wait_for_load_state("domcontentloaded")
        expect(popup).to_have_url(re.compile("https://www.qmarket.online/contactus"))
        popup.close()

    except Exception as e:
        page.screenshot(path="contact_qmarket_error.png")
        raise e
    
    try:
        # 매뉴얼 바로가기 검증
        with page.expect_popup() as popup_info:
            page.get_by_role("button", name="매뉴얼 바로가기").click()
        
        popup = popup_info.value
        popup.wait_for_load_state("domcontentloaded")
        expect(popup).to_have_url(re.compile("https://docs.channel.io/partners/ko"))
        popup.close()

    except Exception as e:
        page.screenshot(path="menual_qmarket_error.png")
        raise e