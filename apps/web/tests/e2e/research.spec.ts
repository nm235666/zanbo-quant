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

test.describe('投研模块', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page)
  })

  test('评分总览页面加载', async ({ page }) => {
    await page.goto('/research/scoreboard')
    await page.waitForTimeout(4000)
    await expect(page.locator('body')).toBeVisible()
    const hasStatCards = await page.locator('[class*="rounded-\[var(--radius-md)\]"]').count() > 0
    expect(hasStatCards).toBeTruthy()
  })

  test('决策板页面加载', async ({ page }) => {
    await page.goto('/research/decision')
    await page.waitForTimeout(4000)
    await expect(page.locator('body')).toBeVisible()
  })

  test('研究报告页面加载', async ({ page }) => {
    await page.goto('/research/reports')
    await page.waitForTimeout(4000)
    await expect(page.locator('body')).toBeVisible()
  })

  test('多角色研究页面加载', async ({ page }) => {
    await page.goto('/research/multi-role')
    await page.waitForTimeout(4000)
    await expect(page.locator('body')).toBeVisible()
  })

  test('趋势分析页面加载', async ({ page }) => {
    await page.goto('/research/trend')
    await page.waitForTimeout(4000)
    await expect(page.locator('body')).toBeVisible()
  })

  test('决策快照按钮具备 pending 状态与结果反馈', async ({ page }) => {
    await page.route('**/api/decision/snapshot/run', async (route) => {
      await page.waitForTimeout(900)
      await route.continue()
    })

    await page.goto('/research/decision')
    await page.waitForTimeout(3000)
    const snapshotButton = page.getByRole('button', { name: /生成快照|生成中/ }).first()
    await snapshotButton.click()
    await expect(snapshotButton).toBeDisabled()
    await expect(snapshotButton).toHaveText(/生成中/)
    await page.waitForTimeout(2500)
    const hasSuccess = await page.locator('text=快照已生成').first().isVisible().catch(() => false)
    const hasFailure = await page.locator('text=快照生成失败').first().isVisible().catch(() => false)
    expect(hasSuccess || hasFailure).toBeTruthy()
    if (hasSuccess) {
      const hasId = await page.locator('text=结果标识').first().isVisible().catch(() => false)
      expect(hasId).toBeTruthy()
    }
  })
})
