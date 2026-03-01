import { test, expect } from '@playwright/test';

test.describe('랜딩 페이지', () => {
  test('페이지가 정상적으로 로드된다', async ({ page }) => {
    await page.goto('/');

    // 타이틀 확인
    await expect(page).toHaveTitle(/노무닥터/);
  });

  test('메인 heading이 표시된다', async ({ page }) => {
    await page.goto('/');

    // 메인 heading 확인
    await expect(page.locator('h1')).toBeVisible();
  });
});
