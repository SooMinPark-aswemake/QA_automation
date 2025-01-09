import { test, expect } from '@playwright/test';

test('test', async ({ page }) => {
  await page.goto('https://partners.qmarket.me/login');
  await page.locator('div').filter({ : /^닫기$/ }).getByRole('button').click();
  await page.pause
  await page.getByPlaceholder('아이디를 입력해주세요').click();
  await page.getByPlaceholder('아이디를 입력해주세요').fill('qmarket');
  await page.getByPlaceholder('비밀번호를 입력해주세요').click();
  await page.getByPlaceholder('비밀번호를 입력해주세요').fill('qmarket!@#');
  await page.getByRole('button', { name: '로그인' }).click();
});