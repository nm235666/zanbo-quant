const { chromium } = require('@playwright/test')
const fs = require('fs')
const path = require('path')

const baseURL = 'http://127.0.0.1:8002'
const outDir = '/home/zanbo/zanbotest/tmp/ui-fullshot-20260413/desktop'
const routes = [
  '/dashboard','/stocks/list','/stocks/scores','/stocks/detail/000001.SZ','/stocks/prices','/macro',
  '/intelligence/global-news','/intelligence/cn-news','/intelligence/stock-news','/intelligence/daily-summaries',
  '/signals/overview','/signals/themes','/signals/graph','/signals/timeline','/signals/audit','/signals/quality-config','/signals/state-timeline',
  '/research/reports','/research/scoreboard','/research/decision','/research/quant-factors','/research/multi-role','/research/trend',
  '/chatrooms/overview','/chatrooms/candidates','/chatrooms/chatlog','/chatrooms/investment',
  '/system/source-monitor','/system/jobs-ops','/system/llm-providers','/system/permissions','/system/database-audit','/system/invites','/system/users','/upgrade'
]

function safeName(route) {
  return route.replace(/^\//, '').replace(/[^a-zA-Z0-9._-]+/g, '_') || 'root'
}

;(async () => {
  fs.mkdirSync(outDir, { recursive: true })
  const browser = await chromium.launch({ headless: true })
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } })
  const page = await context.newPage()
  const rows = []

  await page.goto(baseURL + '/login', { waitUntil: 'domcontentloaded', timeout: 30000 })
  await page.waitForTimeout(1000)
  await page.fill('input[type="text"]', 'nm235666')
  await page.fill('input[type="password"]', 'nm235689')
  const btns = page.locator('button')
  await btns.nth(Math.max(0, (await btns.count()) - 1)).click()
  await page.waitForTimeout(2500)

  for (const route of routes) {
    const row = { route, ok: true }
    try {
      await page.goto(baseURL + route, { waitUntil: 'domcontentloaded', timeout: 30000 })
      await page.waitForTimeout(1800)
      await page.evaluate(() => window.scrollTo(0, 0))
      await page.waitForTimeout(120)
      const metrics = await page.evaluate(() => {
        const doc = document.scrollingElement || document.documentElement
        return {
          title: document.title,
          h1: document.querySelector('h1')?.textContent?.trim() || '',
          innerWidth: window.innerWidth,
          scrollWidth: doc?.scrollWidth || 0,
          overflowX: (doc?.scrollWidth || 0) - window.innerWidth,
          bodyHeight: doc?.scrollHeight || 0,
        }
      })
      row.metrics = metrics
      await page.screenshot({ path: path.join(outDir, safeName(route) + '.png'), fullPage: false })
    } catch (e) {
      row.ok = false
      row.error = String(e && e.message ? e.message : e)
      try {
        await page.screenshot({ path: path.join(outDir, safeName(route) + '__error.png'), fullPage: false })
      } catch {}
    }
    rows.push(row)
  }

  fs.writeFileSync('/home/zanbo/zanbotest/tmp/ui-fullshot-20260413/summary.json', JSON.stringify({ generatedAt: new Date().toISOString(), baseURL, rows }, null, 2))
  await browser.close()
  console.log('saved /home/zanbo/zanbotest/tmp/ui-fullshot-20260413/summary.json')
})()
