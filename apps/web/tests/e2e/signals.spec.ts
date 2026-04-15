import { test, expect } from '@playwright/test'

async function loginAsAdmin(page) {
  for (let attempt = 0; attempt < 3; attempt += 1) {
    await page.goto('/login')
    await page.waitForTimeout(900)
    await page.fill('input[type="text"]', 'nm235666')
    await page.fill('input[type="password"]', 'nm235689')
    for (const pick of ['last', 'first'] as const) {
      try {
        await page.getByRole('button', { name: '登录' })[pick]().click({ timeout: 4000 })
        await page.waitForURL((url) => !url.pathname.includes('/login'), { timeout: 12000 })
        return
      } catch {
        // continue to next strategy
      }
    }
  }
  throw new Error('admin login failed after retries')
}

test.describe('信号模块', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page)
  })

  test('信号总览页面加载', async ({ page }) => {
    await page.goto('/signals/overview')
    await page.waitForTimeout(4000)
    await expect(page.locator('body')).toBeVisible()
    expect(await page.locator("input, select").count()).toBeGreaterThan(0)
  })

  test('信号列表数据加载', async ({ page }) => {
    await page.goto('/signals/overview')
    await page.waitForTimeout(5000)
    const hasTable = await page.locator('table, .data-table, [class*="DataTable"]').count() > 0
    const hasCards = await page.locator('.info-card, [class*="InfoCard"]').count() > 0
    expect(hasTable || hasCards).toBeTruthy()
  })

  test('主题热点页面加载', async ({ page }) => {
    await page.goto('/signals/themes')
    await page.waitForTimeout(4000)
    await expect(page.locator('body')).toBeVisible()
  })

  test('信号筛选功能', async ({ page }) => {
    await page.goto('/signals/overview')
    await page.waitForTimeout(3000)
    const selects = page.locator('select')
    if (await selects.count() > 0) {
      await selects.first().selectOption({ index: 1 })
      await page.waitForTimeout(3000)
    }
    await expect(page.locator('body')).toBeVisible()
  })

  test('信号时间线页面', async ({ page }) => {
    await page.goto('/signals/timeline')
    await page.waitForTimeout(4000)
    await expect(page.locator('body')).toBeVisible()
  })

  test('产业链图谱交互可用', async ({ page }) => {
    await page.goto('/signals/graph?center_type=industry&center_key=%E8%BD%AF%E9%A5%AE%E6%96%99&depth=2&limit=12')
    await page.waitForTimeout(5000)

    await expect(page.getByRole('heading', { name: '关系图' }).first()).toBeVisible()
    await expect(page.locator('.graph-node').first()).toBeVisible()

    const relationChip = page.getByRole('button', { name: /行业→股票/ }).first()
    if (await relationChip.count()) {
      await relationChip.click()
      await page.waitForTimeout(500)
    }

    const graphNode = page.locator('.graph-node').nth(1)
    if (await graphNode.count()) {
      const title = (await graphNode.locator('.graph-node-title').innerText()).trim()
      await graphNode.click()
      await page.waitForTimeout(500)
      await expect(page.locator('text=节点详情').first()).toBeVisible()
      await expect(page.locator('div.text-2xl.font-extrabold').filter({ hasText: title }).first()).toBeVisible()
    }

    await page.getByRole('button', { name: '回到中心' }).click()
    await page.waitForTimeout(400)
    await expect(page.locator('#main-content')).toBeVisible()
  })

  test('图谱主干模式切换会改变节点与折叠统计', async ({ page }) => {
    await page.goto('/signals/graph?center_type=theme&center_key=AI&depth=2&limit=16')
    await page.waitForTimeout(5000)

    const beforeCount = await page.locator('.graph-node').count()
    await page.getByRole('button', { name: '只看主干' }).click()
    await page.waitForTimeout(1200)
    const afterCount = await page.locator('.graph-node').count()

    expect(beforeCount).toBeGreaterThan(0)
    expect(afterCount).toBeLessThanOrEqual(beforeCount)
    await expect(page.locator('text=仅显示主干').first()).toBeVisible()
    await expect(page).toHaveURL(/view=trunk/)

    await page.reload()
    await page.waitForTimeout(2200)
    const afterReloadCount = await page.locator('.graph-node').count()
    await expect(page).toHaveURL(/view=trunk/)
    const trunkLabelVisible = await page.locator('text=仅显示主干').first().isVisible().catch(() => false)
    const noSecondaryHintVisible = await page.locator('text=当前中心无可折叠二级节点').first().isVisible().catch(() => false)
    expect(trunkLabelVisible || noSecondaryHintVisible).toBeTruthy()
    if (trunkLabelVisible) {
      expect(afterReloadCount).toBe(afterCount)
    }
  })

  test('无二级节点时主干按钮禁用并给出提示', async ({ page }) => {
    await page.goto('/signals/graph?center_type=industry&center_key=%E8%BD%AF%E9%A5%AE%E6%96%99&depth=2&limit=12')
    await page.waitForTimeout(4200)
    const trunkBtn = page.getByRole('button', { name: '只看主干' }).first()
    const hasHint = await page.locator('text=当前中心无可折叠二级节点').first().isVisible().catch(() => false)
    if (hasHint) {
      await expect(trunkBtn).toBeDisabled()
    }
  })
})
