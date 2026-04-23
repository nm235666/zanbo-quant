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
  await page.waitForURL((url) => !url.pathname.endsWith('/login'))
}

test('admin 登录后落到 admin dashboard', async ({ page }) => {
  await login(page, 'admin')
  await expect(page).toHaveURL(/\/admin\/dashboard$/)
  await expect(page.locator('[data-shell-surface="admin"]')).toBeVisible()
  await expect(page.locator('[data-shell-switch="admin"]')).toBeVisible()
  await expect(page.getByText('业务热点摘要')).toBeVisible()
})

test('pro 默认落点正确且可打开评分总览', async ({ page }) => {
  await login(page, 'pro')
  await expect(page).toHaveURL(/\/app\/workbench$/)
  await expect(page.locator('[data-shell-surface="app"]')).toBeVisible()
  await expect(page.locator('[data-shell-switch="app"]')).toHaveCount(0)
  await page.goto('/app/research/scoreboard')
  await expect(page).toHaveURL(/\/app\/research\/scoreboard$/)
  await expect(page.locator('[data-shell-surface="app"]')).toBeVisible()
  await expect(page.locator('header').getByText('评分总览')).toBeVisible()
  await expect(page.getByRole('heading', { name: '自动短名单' })).toBeVisible()
  await expect(page.getByRole('heading', { name: '入选理由' })).toBeVisible()
})

test('limited 默认落点正确且无权限页跳 upgrade', async ({ page, request }) => {
  await skipUnlessSmokeLimitedRoleIsLimited(request)
  await login(page, 'limited')
  const landedPath = new URL(page.url()).pathname
  expect(landedPath.length > 1).toBeTruthy()
  await page.goto('/system/users')
  await expect(page).toHaveURL(/\/upgrade/)
  await expect(page.getByRole('heading', { name: '功能升级提示' })).toBeVisible()
  await expect(page.getByText('当前受限任务')).toBeVisible()
  await expect(page.getByText('需要权限')).toBeVisible()
})

test('三个主研究页首屏可渲染', async ({ page }) => {
  await login(page, 'pro')
  for (const path of ['/app/research/scoreboard', '/app/stocks/scores', '/app/decision']) {
    await page.goto(path)
    await expect(page).toHaveURL(new RegExp(path.replace(/\//g, '\\/')))
    await expect(page.locator('#main-content')).toBeVisible()
    await expect(page.locator('[data-shell-surface="app"]')).toBeVisible()
    await expect(page.locator('body')).not.toContainText('Cannot read properties of undefined')
  }
})

test('旧路径访问会显式跳到新语义地址', async ({ page }) => {
  await login(page, 'pro')
  await page.goto('/research/workbench')
  await expect(page).toHaveURL(/\/app\/workbench$/)
  await page.goto('/portfolio/orders')
  await expect(page).toHaveURL(/\/app\/orders$/)
})
