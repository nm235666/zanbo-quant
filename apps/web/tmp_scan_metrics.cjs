const { chromium, devices } = require('@playwright/test')
const fs = require('fs')

const baseURL = (process.env.PLAYWRIGHT_BASE_URL || 'http://192.168.5.52:8077').trim()
const routes = [
  '/dashboard','/stocks/list','/stocks/scores','/stocks/detail/000001.SZ','/stocks/prices','/macro',
  '/intelligence/global-news','/intelligence/cn-news','/intelligence/stock-news','/intelligence/daily-summaries',
  '/signals/overview','/signals/themes','/signals/graph','/signals/timeline','/signals/audit','/signals/quality-config','/signals/state-timeline',
  '/research/reports','/research/scoreboard','/research/decision','/research/quant-factors','/research/multi-role','/research/trend',
  '/chatrooms/overview','/chatrooms/candidates','/chatrooms/chatlog','/chatrooms/investment',
  '/system/source-monitor','/system/jobs-ops','/system/llm-providers','/system/permissions','/system/database-audit','/system/invites','/system/users','/upgrade'
]

async function login(page) {
  await page.goto(baseURL + '/login', { waitUntil: 'domcontentloaded', timeout: 60000 })
  await page.waitForTimeout(1200)
  await page.fill('input[type="text"]', 'nm235666')
  await page.fill('input[type="password"]', 'nm235689')
  const btns = page.locator('button')
  await btns.nth(Math.max(0, (await btns.count()) - 1)).click()
  await page.waitForTimeout(3000)
}

async function run(name, contextOptions) {
  const browser = await chromium.launch({ headless: true })
  const context = await browser.newContext(contextOptions)
  const page = await context.newPage()
  await login(page)
  const rows = []
  for (const route of routes) {
    let row = { route, ok: true }
    try {
      await page.goto(baseURL + route, { waitUntil: 'domcontentloaded', timeout: 60000 })
      await page.waitForTimeout(2800)
      const m = await page.evaluate(() => {
        const doc = document.scrollingElement || document.documentElement
        const overflowX = (doc?.scrollWidth || 0) - window.innerWidth
        const bad = []
        for (const el of Array.from(document.querySelectorAll('*'))) {
          const st = getComputedStyle(el)
          if (st.display === 'none' || st.visibility === 'hidden') continue
          const r = el.getBoundingClientRect()
          if (r.width <= 0 || r.height <= 0) continue
          const over = r.right - window.innerWidth
          if (over > 8) {
            bad.push({ tag: el.tagName.toLowerCase(), cls: String(el.className || '').slice(0, 80), w: Math.round(r.width), over: Math.round(over) })
            if (bad.length >= 5) break
          }
        }
        return { title: document.title, innerWidth: window.innerWidth, scrollWidth: doc?.scrollWidth || 0, overflowX: Math.round(overflowX), bad }
      })
      row = { ...row, ...m }
    } catch (e) {
      row = { ...row, ok: false, error: String(e && e.message ? e.message : e) }
    }
    rows.push(row)
  }
  await context.close()
  await browser.close()
  return { viewport: name, rows }
}

;(async () => {
  const desktop = await run('desktop', { viewport: { width: 1440, height: 900 } })
  const mobile = await run('mobile', { ...devices['iPhone 13'] })
  const data = { generatedAt: new Date().toISOString(), baseURL, desktop, mobile }
  fs.writeFileSync('/home/zanbo/zanbotest/tmp/layout-scan-metrics.json', JSON.stringify(data, null, 2))
  console.log('saved /home/zanbo/zanbotest/tmp/layout-scan-metrics.json')
})()
