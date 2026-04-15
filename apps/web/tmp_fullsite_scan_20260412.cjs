const { chromium, devices } = require('@playwright/test')
const fs = require('fs')
const path = require('path')

const baseURL = (process.env.PLAYWRIGHT_BASE_URL || 'http://192.168.5.52:8077').trim()
const outRoot = '/home/zanbo/zanbotest/tmp/layout-scan-20260412'
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

async function login(page) {
  await page.goto(baseURL + '/login', { waitUntil: 'domcontentloaded', timeout: 60000 })
  await page.waitForTimeout(1500)
  await page.fill('input[type="text"]', 'nm235666')
  await page.fill('input[type="password"]', 'nm235689')
  const btns = page.locator('button')
  const n = await btns.count()
  await btns.nth(Math.max(0, n - 1)).click()
  await page.waitForTimeout(3500)
}

async function probe(page) {
  return page.evaluate(() => {
    const doc = document.scrollingElement || document.documentElement
    const overflowX = (doc?.scrollWidth || 0) - window.innerWidth
    const bad = []
    for (const el of Array.from(document.querySelectorAll('*'))) {
      const st = getComputedStyle(el)
      if (st.display === 'none' || st.visibility === 'hidden') continue
      const r = el.getBoundingClientRect()
      if (r.width <= 0 || r.height <= 0) continue
      const over = Math.round(r.right - window.innerWidth)
      if (over > 8) {
        bad.push({ tag: el.tagName.toLowerCase(), cls: String(el.className || '').slice(0, 90), over, w: Math.round(r.width) })
        if (bad.length >= 8) break
      }
    }
    const txt = String(document.body?.innerText || '').replace(/\s+/g, ' ').trim()
    return {
      title: document.title,
      h1: document.querySelector('h1')?.textContent?.trim() || '',
      innerWidth: window.innerWidth,
      scrollWidth: doc?.scrollWidth || 0,
      overflowX: Math.round(overflowX),
      bad,
      textLen: txt.length,
    }
  })
}

async function runViewport(name, contextOptions) {
  const browser = await chromium.launch({ headless: true })
  const context = await browser.newContext(contextOptions)
  const page = await context.newPage()

  const consoleErrors = []
  page.on('console', (msg) => {
    if (msg.type() === 'error') consoleErrors.push(msg.text())
  })
  page.on('pageerror', (err) => consoleErrors.push(String(err)))

  await login(page)

  const rows = []
  for (const route of routes) {
    const item = { route, ok: true, url: baseURL + route }
    try {
      await page.goto(baseURL + route, { waitUntil: 'domcontentloaded', timeout: 60000 })
      await page.waitForTimeout(3200)
      const m = await probe(page)
      item.metrics = m
      item.consoleErrors = consoleErrors.slice(-6)
      const file = path.join(outRoot, name, safeName(route) + '.png')
      await page.screenshot({ path: file, fullPage: true })
    } catch (e) {
      item.ok = false
      item.error = String(e && e.message ? e.message : e)
      try {
        const file = path.join(outRoot, name, safeName(route) + '__error.png')
        await page.screenshot({ path: file, fullPage: false })
      } catch {}
    }
    rows.push(item)
  }

  await context.close()
  await browser.close()
  return rows
}

;(async () => {
  fs.mkdirSync(path.join(outRoot, 'desktop'), { recursive: true })
  fs.mkdirSync(path.join(outRoot, 'mobile'), { recursive: true })
  const desktop = await runViewport('desktop', { viewport: { width: 1440, height: 900 } })
  const mobile = await runViewport('mobile', { ...devices['iPhone 13'] })
  const summary = { generatedAt: new Date().toISOString(), baseURL, routeCount: routes.length, desktop, mobile }
  fs.writeFileSync(path.join(outRoot, 'summary.json'), JSON.stringify(summary, null, 2))
  console.log('saved', path.join(outRoot, 'summary.json'))
})()
