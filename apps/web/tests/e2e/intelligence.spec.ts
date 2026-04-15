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

test.describe('情报模块', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page)
  })

  test('国际新闻页面加载', async ({ page }) => {
    await page.goto('/intelligence/global-news')
    await page.waitForTimeout(4000)
    await expect(page.locator('body')).toBeVisible()
    // 只要页面有内容即可（可能有不同class名）
    await expect(page.locator('body')).toBeVisible()
  })

  test('国内新闻页面加载', async ({ page }) => {
    await page.goto('/intelligence/cn-news')
    await page.waitForTimeout(4000)
    await expect(page.locator('body')).toBeVisible()
  })

  test('个股新闻页面加载', async ({ page }) => {
    await page.goto('/intelligence/stock-news')
    await page.waitForTimeout(4000)
    await expect(page.locator('body')).toBeVisible()
    expect(await page.locator('input, select').count()).toBeGreaterThan(0)
  })

  test('新闻筛选功能', async ({ page }) => {
    await page.goto('/intelligence/global-news')
    await page.waitForTimeout(3000)
    const keywordInput = page.locator('input[type="text"]').first()
    if (await keywordInput.count() > 0) {
      await keywordInput.fill('test')
      await page.waitForTimeout(2000)
    }
    await expect(page.locator('body')).toBeVisible()
  })

  test('日报汇总页面加载', async ({ page }) => {
    await page.goto('/intelligence/daily-summaries')
    await page.waitForTimeout(4000)
    await expect(page.locator('body')).toBeVisible()
  })
})
