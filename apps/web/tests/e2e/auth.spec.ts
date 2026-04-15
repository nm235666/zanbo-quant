import { test, expect } from '@playwright/test'

test.describe('认证模块', () => {
  test('登录页面展示正常', async ({ page }) => {
    await page.goto('/login')
    await page.waitForTimeout(2000)
    
    await expect(page).toHaveTitle(/web/)
    await expect(page.locator('input[type="text"]').first()).toBeVisible()
    await expect(page.locator('input[type="password"]').first()).toBeVisible()
    
    // 获取最后一个button（提交按钮）
    const buttons = page.locator('button')
    const count = await buttons.count()
    await expect(buttons.nth(count - 1)).toBeVisible()
  })

  test('管理员账号登录成功', async ({ page }) => {
    await page.goto('/login')
    await page.waitForTimeout(2000)
    
    await page.fill('input[type="text"]', 'nm235666')
    await page.fill('input[type="password"]', 'nm235689')
    
    const buttons = page.locator('button')
    const count = await buttons.count()
    await buttons.nth(count - 1).click()
    
    await page.waitForTimeout(5000)
    expect(page.url()).not.toContain('/login')
  })

  test('Pro账号登录成功', async ({ page }) => {
    await page.goto('/login')
    await page.waitForTimeout(2000)
    
    await page.fill('input[type="text"]', 'zanbo')
    await page.fill('input[type="password"]', 'zanbo666')
    
    const buttons = page.locator('button')
    const count = await buttons.count()
    await buttons.nth(count - 1).click()
    
    await page.waitForTimeout(5000)
    expect(page.url()).not.toContain('/login')
  })

  test('错误密码登录失败', async ({ page }) => {
    await page.goto('/login')
    await page.waitForTimeout(2000)
    
    await page.fill('input[type="text"]', 'nm235666')
    await page.fill('input[type="password"]', 'wrongpassword')
    
    const buttons = page.locator('button')
    const count = await buttons.count()
    await buttons.nth(count - 1).click()
    
    await page.waitForTimeout(3000)
    const stillOnLogin = page.url().includes('/login')
    expect(stillOnLogin).toBeTruthy()
  })

  test('空密码验证', async ({ page }) => {
    await page.goto('/login')
    await page.waitForTimeout(2000)
    
    await page.fill('input[type="text"]', 'nm235666')
    
    const buttons = page.locator('button')
    const count = await buttons.count()
    await buttons.nth(count - 1).click()
    
    await page.waitForTimeout(2000)
    expect(page.url()).toContain('/login')
  })
})
