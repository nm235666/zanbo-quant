const { chromium, devices } = require('@playwright/test')
const fs = require('fs')
const path = require('path')

const baseURL = 'http://192.168.5.52:8077'
const outRoot = '/home/zanbo/zanbotest/tmp/layout-quickscan-20260412'
const routes = [
  '/dashboard','/stocks/list','/stocks/scores','/stocks/detail/000001.SZ','/stocks/prices','/macro',
  '/intelligence/global-news','/intelligence/cn-news','/intelligence/stock-news','/intelligence/daily-summaries',
  '/signals/overview','/signals/themes','/signals/graph','/signals/timeline','/signals/audit','/signals/quality-config','/signals/state-timeline',
  '/research/reports','/research/scoreboard','/research/decision','/research/quant-factors','/research/multi-role','/research/trend',
  '/chatrooms/overview','/chatrooms/candidates','/chatrooms/chatlog','/chatrooms/investment',
  '/system/source-monitor','/system/jobs-ops','/system/llm-providers','/system/permissions','/system/database-audit','/system/invites','/system/users','/upgrade'
]

function safeName(route) { return route.replace(/^\//, '').replace(/[^a-zA-Z0-9._-]+/g, '_') || 'root' }

async function login(page) {
  await page.goto(baseURL + '/login', { waitUntil: 'domcontentloaded', timeout: 60000 })
  await page.waitForTimeout(1200)
  await page.fill('input[type="text"]', 'nm235666')
  await page.fill('input[type="password"]', 'nm235689')
  const btns = page.locator('button')
  await btns.nth(Math.max(0, (await btns.count()) - 1)).click()
  await page.waitForTimeout(3000)
}

async function inspect(page) {
  return page.evaluate(() => {
    const doc = document.scrollingElement || document.documentElement
    const bad = []
    for (const el of Array.from(document.querySelectorAll('*'))) {
      const st = getComputedStyle(el)
      if (st.display === 'none' || st.visibility === 'hidden') continue
      const r = el.getBoundingClientRect()
      if (r.width <= 0 || r.height <= 0) continue
      const over = Math.round(r.right - window.innerWidth)
      if (over > 8) {
        bad.push({ tag: el.tagName.toLowerCase(), cls: String(el.className || '').slice(0, 100), over, w: Math.round(r.width) })
        if (bad.length >= 5) break
      }
    }
    return {
      title: document.title,
      heading: document.querySelector('h1')?.textContent?.trim() || '',
      innerWidth: window.innerWidth,
      scrollWidth: doc?.scrollWidth || 0,
      overflowX: Math.round((doc?.scrollWidth || 0) - window.innerWidth),
      bad,
    }
  })
}

async function run(name, contextOptions) {
  const browser = await chromium.launch({ headless: true })
  const context = await browser.newContext(contextOptions)
  const page = await context.newPage()
  const errs = []
  page.on('console', (m) => { if (m.type() === 'error') errs.push(m.text()) })
  page.on('pageerror', (e) => errs.push(String(e)))
  await login(page)

  const rows = []
  for (const route of routes) {
    const row = { route, ok: true }
    try {
      await page.goto(baseURL + route, { waitUntil: 'domcontentloaded', timeout: 60000 })
      await page.waitForTimeout(2200)
      const m = await inspect(page)
      row.metrics = m
      row.consoleErrors = errs.slice(-5)
      await page.screenshot({ path: path.join(outRoot, name, safeName(route) + '.png'), fullPage: false })
    } catch (e) {
      row.ok = false
      row.error = String(e && e.message ? e.message : e)
    }
    rows.push(row)
  }

  await browser.close()
  return rows
}

;(async () => {
  fs.mkdirSync(path.join(outRoot, 'desktop'), { recursive: true })
  fs.mkdirSync(path.join(outRoot, 'mobile'), { recursive: true })
  const desktop = await run('desktop', { viewport: { width: 1440, height: 900 } })
  const mobile = await run('mobile', { ...devices['iPhone 13'] })
  fs.writeFileSync(path.join(outRoot, 'summary.json'), JSON.stringify({ generatedAt: new Date().toISOString(), baseURL, desktop, mobile }, null, 2))
  console.log('saved quickscan summary')
})()
