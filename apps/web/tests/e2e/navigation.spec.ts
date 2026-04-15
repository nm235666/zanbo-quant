import { test, expect } from '@playwright/test'

async function loginAsAdmin(page) {
  await page.goto('/login')
  await page.waitForTimeout(2000)
  await page.fill('input[type="text"]', 'nm235666')
  await page.fill('input[type="password"]', 'nm235689')
  const btns = page.locator('button')
  await btns.nth(await btns.count() - 1).click()
  await page.waitForTimeout(5000)
}

test.describe('导航与菜单', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page)
  })

  test('首页加载正常', async ({ page }) => {
    await page.goto('/dashboard')
    await page.waitForTimeout(3000)
    await expect(page.locator('body')).toBeVisible()
    const hasStatCards = await page.locator('[class*="rounded-\[var(--radius-md)\]"]').count() > 0
    expect(hasStatCards).toBeTruthy()
  })

  test('页面跳转正常', async ({ page }) => {
    await page.goto('/signals/overview')
    await page.waitForTimeout(3000)
    await expect(page.locator('body')).toBeVisible()
    
    await page.goto('/intelligence/global-news')
    await page.waitForTimeout(3000)
    await expect(page.locator('body')).toBeVisible()
  })
})
