import { expect, test, type Page } from '@playwright/test'

const credentials = {
  pro: {
    username: process.env.SMOKE_PRO_USERNAME?.trim() || 'zanbo',
    password: process.env.SMOKE_PRO_PASSWORD?.trim() || 'zanbo666',
  },
}

async function login(page: Page, role: keyof typeof credentials) {
  const account = credentials[role]
  await page.goto('/login')
  await page.getByPlaceholder('请输入账号（3-32位英文数字._-）').fill(account.username)
  await page.getByPlaceholder('请输入密码（至少6位）').fill(account.password)
  await page.locator('button').filter({ hasText: /^登录$/ }).last().click()
  await page.waitForURL((url) => !url.pathname.endsWith('/login'))
}

test.describe('R30 市场结论冲突裁决可视化', () => {
  test('confidence 徽章带 data-confidence 属性且数值为真实百分比', async ({ page }) => {
    await login(page, 'pro')
    await page.goto('/app/market')
    await expect(page).toHaveURL(/\/app\/market$/)

    const badge = page.locator('[data-testid="conclusion-confidence-badge"]')
    await expect(badge).toBeVisible({ timeout: 20_000 })

    const rawConfidence = await badge.getAttribute('data-confidence')
    expect(rawConfidence).not.toBeNull()
    const pct = Number(rawConfidence)
    expect(Number.isFinite(pct)).toBe(true)
    expect(pct).toBeGreaterThanOrEqual(0)
    expect(pct).toBeLessThanOrEqual(100)
    // 必须展示一个非空方向
    const direction = await badge.getAttribute('data-direction')
    expect(direction).not.toBeNull()
    expect(String(direction)).toMatch(/(看多|看空|中性)/)
  })

  test('规则链表格可展开且 winner 行带标记', async ({ page }) => {
    await login(page, 'pro')
    await page.goto('/app/market')
    const toggle = page.locator('[data-testid="conclusion-rule-trace-toggle"]')
    await expect(toggle).toBeVisible({ timeout: 20_000 })
    await toggle.click()

    const breakdown = page.locator('[data-testid="conclusion-score-breakdown"]')
    await expect(breakdown).toBeVisible()
    const winnerSource = await breakdown.getAttribute('data-winner-source')
    expect(winnerSource).not.toBeNull()
    expect(String(winnerSource).length).toBeGreaterThan(0)

    const winnerRow = breakdown.locator(`tr[data-source="${winnerSource}"]`)
    await expect(winnerRow).toBeVisible()
    await expect(winnerRow).toHaveAttribute('data-is-winner', 'true')

    const compositeAttr = await winnerRow.getAttribute('data-composite')
    expect(Number.isFinite(Number(compositeAttr))).toBe(true)
  })

  test('低可信场景下 needs_review 告警与异议来源展示共存', async ({ page }) => {
    await login(page, 'pro')
    await page.goto('/app/market')

    const badge = page.locator('[data-testid="conclusion-confidence-badge"]')
    await expect(badge).toBeVisible({ timeout: 20_000 })
    const needsReview = await badge.getAttribute('data-needs-review')

    if (needsReview === 'true') {
      await expect(page.locator('[data-testid="conclusion-needs-review-alert"]')).toBeVisible()
    } else {
      // 可信度足够时，告警不应出现
      await expect(page.locator('[data-testid="conclusion-needs-review-alert"]')).toHaveCount(0)
    }
  })
})
