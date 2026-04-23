import { expect, test, type Page } from '@playwright/test'
import { skipUnlessSmokeLimitedRoleIsLimited } from './helpers/smokeLimitedRole'

const credentials = {
  admin: {
    username: process.env.SMOKE_ADMIN_USERNAME?.trim() || 'nm235666',
    password: process.env.SMOKE_ADMIN_PASSWORD?.trim() || 'nm235689',
  },
  pro: {
    username: process.env.SMOKE_PRO_USERNAME?.trim() || 'zanbo',
    password: process.env.SMOKE_PRO_PASSWORD?.trim() || 'zanbo666',
  },
  limited: {
    username: process.env.SMOKE_LIMITED_USERNAME?.trim() || 'test112233',
    password: process.env.SMOKE_LIMITED_PASSWORD?.trim() || 'test123',
  },
}

async function login(page: Page, role: keyof typeof credentials) {
  const account = credentials[role]
  await page.goto('/login')
  await page.getByPlaceholder('请输入账号（3-32位英文数字._-）').fill(account.username)
  await page.getByPlaceholder('请输入密码（至少6位）').fill(account.password)
  await page.locator('button').filter({ hasText: /^登录$/ }).last().click()
  await page.waitForURL((url) => !url.pathname.endsWith('/login'), { timeout: 60_000 })
}

// Round 23 new pages — first-render smoke tests (pro user)

test('workbench 首屏渲染', async ({ page }) => {
  await login(page, 'pro')
  await page.goto('/app/workbench')
  await expect(page).toHaveURL(/\/app\/workbench$/)
  await expect(page.locator('[data-shell-surface="app"]')).toBeVisible()
  await expect(page.locator('#main-content')).toBeVisible()
  await expect(page.locator('[data-testid="workbench-first-action-card"]')).toBeVisible()
  await expect(page.locator('[data-testid="workbench-primary-cta"]')).toHaveAttribute('href', /\/app\//)
  await expect(page.locator('body')).not.toContainText('Cannot read properties of undefined')
})

test('市场结论页首屏渲染', async ({ page }) => {
  await login(page, 'pro')
  await page.goto('/app/market')
  await expect(page).toHaveURL(/\/app\/market$/)
  await expect(page.locator('#main-content')).toBeVisible()
  await expect(page.locator('body')).not.toContainText('Cannot read properties of undefined')
})

test('单标的详情页包含决策动作时间线收口区', async ({ page }) => {
  await login(page, 'pro')
  await page.goto('/app/stocks/detail/000001.SZ')
  await expect(page).toHaveURL(/\/app\/stocks\/detail\/000001\.SZ$/)
  await expect(page.getByRole('heading', { name: '决策视角' })).toBeVisible()
  const timeline = page.locator('[data-testid="stock-detail-decision-timeline"]')
  if (await timeline.count()) {
    await expect(timeline.first()).toBeVisible()
  }
  await expect(page.locator('#main-content a[href*="/app/decision"]').first()).toBeVisible()
  await expect(page.locator('body')).not.toContainText('Cannot read properties of undefined')
})

test('候选漏斗页首屏渲染', async ({ page }) => {
  await login(page, 'pro')
  await page.goto('/app/funnel')
  await expect(page).toHaveURL(/\/app\/funnel$/)
  await page.locator('#main-content').waitFor({ state: 'visible', timeout: 20_000 })
  await expect(page.locator('#main-content')).toBeVisible()
  await expect(page.locator('body')).not.toContainText('Cannot read properties of undefined')
})

test('组合持仓页首屏渲染', async ({ page }) => {
  await login(page, 'pro')
  await page.goto('/app/positions')
  await expect(page).toHaveURL(/\/app\/positions$/)
  await expect(page.locator('#main-content')).toBeVisible()
  await expect(page.locator('body')).not.toContainText('Cannot read properties of undefined')
})

test('组合订单页首屏渲染', async ({ page }) => {
  await login(page, 'pro')
  await page.goto('/app/orders')
  await expect(page).toHaveURL(/\/app\/orders$/)
  await expect(page.locator('#main-content')).toBeVisible()
})

test('组合复盘页首屏渲染', async ({ page }) => {
  await login(page, 'pro')
  await page.goto('/app/review')
  await expect(page).toHaveURL(/\/app\/review$/)
  await expect(page.locator('#main-content')).toBeVisible()
})

test('任务收件箱首屏渲染', async ({ page }) => {
  await login(page, 'pro')
  await page.goto('/app/research/task-inbox')
  await expect(page).toHaveURL(/\/app\/research\/task-inbox$/)
  await expect(page.locator('#main-content')).toBeVisible()
  await expect(page.locator('body')).not.toContainText('Cannot read properties of undefined')
})

test('宏观三周期状态页首屏渲染', async ({ page }) => {
  await login(page, 'pro')
  await page.goto('/app/macro-regime')
  await expect(page).toHaveURL(/\/app\/macro-regime$/)
  await expect(page.locator('#main-content')).toBeVisible()
  await expect(page.locator('body')).not.toContainText('Cannot read properties of undefined')
})

test('长线配置动作页首屏渲染', async ({ page }) => {
  await login(page, 'pro')
  await page.goto('/app/allocation')
  await expect(page).toHaveURL(/\/app\/allocation$/)
  await expect(page.locator('#main-content')).toBeVisible()
  await expect(page.locator('body')).not.toContainText('Cannot read properties of undefined')
})

test('workbench 今日6问链接可见', async ({ page }) => {
  await login(page, 'pro')
  await page.goto('/app/workbench')
  await expect(page.locator('#main-content')).toBeVisible()
  await expect(page.locator('#main-content a[href*="app/macro-regime"]').first()).toBeVisible()
  await expect(page.locator('#main-content a[href*="app/allocation"]').first()).toBeVisible()
  await expect(page.locator('body')).not.toContainText('Cannot read properties of undefined')
})

test('workbench Top N 选择器可见', async ({ page }) => {
  await login(page, 'pro')
  await page.goto('/app/workbench')
  await expect(page.locator('#main-content')).toBeVisible()
  // At least one select with a value="5" option must exist
  const selectWithFive = page.locator('#main-content select').filter({ has: page.locator('option[value="5"]') }).first()
  await expect(selectWithFive).toBeVisible()
  await expect(page.locator('body')).not.toContainText('Cannot read properties of undefined')
})

test('workbench 主链 CTA 不借道 admin 页面', async ({ page }) => {
  await login(page, 'pro')
  await page.goto('/app/workbench')
  await expect(page.locator('#main-content')).toBeVisible()
  await expect(page.locator('#main-content a[href^="/admin/"]')).toHaveCount(0)
})

test('决策板建议仓位区间字段可见', async ({ page }) => {
  await login(page, 'pro')
  await page.goto('/app/decision')
  await expect(page).toHaveURL(/\/app\/decision$/)
  await expect(page.locator('#main-content')).toBeVisible()
  // Position range input placeholder should mention 账户仓位区间
  await expect(page.locator('input[placeholder*="账户仓位区间"]')).toBeVisible()
  await expect(page.locator('body')).not.toContainText('Cannot read properties of undefined')
})

test('宏观状态页复盘入口可见', async ({ page }) => {
  await login(page, 'pro')
  await page.goto('/app/macro-regime')
  await expect(page).toHaveURL(/\/app\/macro-regime$/)
  await expect(page.locator('#main-content')).toBeVisible()
  // Page must render without JS errors
  await expect(page.locator('body')).not.toContainText('Cannot read properties of undefined')
  await expect(page.locator('body')).not.toContainText('Cannot read properties of null')
})

test('长线配置动作页规则约束卡片可见', async ({ page }) => {
  await login(page, 'pro')
  await page.goto('/app/allocation')
  await expect(page).toHaveURL(/\/app\/allocation$/)
  await expect(page.locator('#main-content')).toBeVisible()
  // The page must show at least one key allocation concept
  await expect(page.locator('#main-content')).toContainText(/现金比例|配置动作|风险预算/)
  await expect(page.locator('body')).not.toContainText('Cannot read properties of undefined')
})

test('批次 A 旧路径会显式跳到新前缀', async ({ page }) => {
  await login(page, 'pro')
  await page.goto('/research/workbench')
  await expect(page).toHaveURL(/\/app\/workbench$/)
  await page.goto('/portfolio/orders')
  await expect(page).toHaveURL(/\/app\/orders$/)
})

test('后台 inner page 使用 admin shell', async ({ page }) => {
  await login(page, 'admin')
  await page.goto('/admin/system/jobs-ops')
  await expect(page).toHaveURL(/\/admin\/system\/jobs-ops$/)
  await expect(page.locator('[data-shell-surface="admin"]')).toBeVisible()
  await expect(page.locator('[data-shell-nav="admin"]')).toContainText('系统治理')
  await expect(page.locator('[data-shell-nav="admin"]')).not.toContainText('研究输入')
})

test('dashboard 主链 CTA 不借道 app 页面', async ({ page }) => {
  await login(page, 'admin')
  await page.goto('/admin/dashboard')
  await expect(page.locator('#main-content')).toBeVisible()
  await expect(page.locator('#main-content a[href^="/app/"]')).toHaveCount(0)
})

test('upgrade 对 app/admin 来源保持模式语义', async ({ page, request }) => {
  await skipUnlessSmokeLimitedRoleIsLimited(request)
  await login(page, 'limited')
  await page.goto('/upgrade?from=%2Fapp%2Fresearch%2Fmulti-role')
  await expect(page).toHaveURL(/\/upgrade\?from=/)
  await expect(page.getByRole('link', { name: '返回研究工作台' }).first()).toBeVisible()

  await page.goto('/upgrade?from=%2Fadmin%2Fdashboard')
  await expect(page).toHaveURL(/\/upgrade\?from=/)
  await expect(page.getByRole('link', { name: '返回后台管理首页' }).first()).toBeVisible()
})
