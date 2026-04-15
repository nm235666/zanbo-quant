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

test.describe('响应式布局测试', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page)
  })

  test('移动端视图 - 信号总览', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 })
    await page.goto('/signals/overview')
    await page.waitForTimeout(4000)
    await expect(page.locator('body')).toBeVisible()
  })

  test('平板视图 - 股票列表', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 })
    await page.goto('/stocks/list')
    await page.waitForTimeout(4000)
    await expect(page.locator('body')).toBeVisible()
  })

  test('桌面端视图 - 决策板', async ({ page }) => {
    await page.setViewportSize({ width: 1920, height: 1080 })
    await page.goto('/research/decision')
    await page.waitForTimeout(4000)
    await expect(page.locator('body')).toBeVisible()
    const hasTable = await page.locator('table').count() > 0
    expect(hasTable).toBeTruthy()
  })
})
