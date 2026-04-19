import { expect, test, type Page } from '@playwright/test'

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
  await page.waitForURL((url) => !url.pathname.endsWith('/login'))
}

// Round 23 new pages — first-render smoke tests (pro user)

test('workbench 首屏渲染', async ({ page }) => {
  await login(page, 'pro')
  await page.goto('/research/workbench')
  await expect(page).toHaveURL(/\/research\/workbench$/)
  await expect(page.locator('#main-content')).toBeVisible()
  await expect(page.locator('body')).not.toContainText('Cannot read properties of undefined')
})

test('市场结论页首屏渲染', async ({ page }) => {
  await login(page, 'pro')
  await page.goto('/market/conclusion')
  await expect(page).toHaveURL(/\/market\/conclusion$/)
  await expect(page.locator('#main-content')).toBeVisible()
  await expect(page.locator('body')).not.toContainText('Cannot read properties of undefined')
})

test('候选漏斗页首屏渲染', async ({ page }) => {
  await login(page, 'pro')
  await page.goto('/research/funnel')
  await expect(page).toHaveURL(/\/research\/funnel$/)
  await expect(page.locator('#main-content')).toBeVisible()
  await expect(page.locator('body')).not.toContainText('Cannot read properties of undefined')
})

test('组合持仓页首屏渲染', async ({ page }) => {
  await login(page, 'pro')
  await page.goto('/portfolio/positions')
  await expect(page).toHaveURL(/\/portfolio\/positions$/)
  await expect(page.locator('#main-content')).toBeVisible()
  await expect(page.locator('body')).not.toContainText('Cannot read properties of undefined')
})

test('组合订单页首屏渲染', async ({ page }) => {
  await login(page, 'pro')
  await page.goto('/portfolio/orders')
  await expect(page).toHaveURL(/\/portfolio\/orders$/)
  await expect(page.locator('#main-content')).toBeVisible()
})

test('组合复盘页首屏渲染', async ({ page }) => {
  await login(page, 'pro')
  await page.goto('/portfolio/review')
  await expect(page).toHaveURL(/\/portfolio\/review$/)
  await expect(page.locator('#main-content')).toBeVisible()
})

test('任务收件箱首屏渲染', async ({ page }) => {
  await login(page, 'pro')
  await page.goto('/research/task-inbox')
  await expect(page).toHaveURL(/\/research\/task-inbox$/)
  await expect(page.locator('#main-content')).toBeVisible()
  await expect(page.locator('body')).not.toContainText('Cannot read properties of undefined')
})
