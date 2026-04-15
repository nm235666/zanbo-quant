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

test.describe('群聊模块', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page)
  })

  test('群聊总览页面加载', async ({ page }) => {
    await page.goto('/chatrooms/overview')
    await page.waitForTimeout(4000)
    await expect(page.locator('body')).toBeVisible()
    expect(await page.locator('input, select').count()).toBeGreaterThan(0)
  })

  test('候选池页面加载', async ({ page }) => {
    await page.goto('/chatrooms/candidates')
    await page.waitForTimeout(4000)
    await expect(page.locator('body')).toBeVisible()
  })

  test('聊天记录页面加载', async ({ page }) => {
    await page.goto('/chatrooms/chatlog')
    await page.waitForTimeout(4000)
    await expect(page.locator('body')).toBeVisible()
  })

  test('投研结论页面加载', async ({ page }) => {
    await page.goto('/chatrooms/investment')
    await page.waitForTimeout(4000)
    await expect(page.locator('body')).toBeVisible()
  })
})
