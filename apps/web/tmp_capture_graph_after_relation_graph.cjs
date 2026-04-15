const { chromium } = require('@playwright/test')

async function login(page) {
  await page.goto('http://127.0.0.1:8002/login', { waitUntil: 'domcontentloaded' })
  await page.fill('input[type="text"]', 'nm235666')
  await page.fill('input[type="password"]', 'nm235689')
  const btns = page.locator('button')
  await btns.nth((await btns.count()) - 1).click()
  await page.waitForTimeout(2200)
}

;(async () => {
  const browser = await chromium.launch({ headless: true })
  const context = await browser.newContext({ viewport: { width: 1500, height: 980 } })
  const page = await context.newPage()
  await login(page)

  await page.goto('http://127.0.0.1:8002/signals/graph?center_type=theme&keyword=%E8%BD%AF%E9%A5%AE%E6%96%99&depth=2&limit=12', { waitUntil: 'domcontentloaded' })
  await page.waitForTimeout(2800)
  await page.screenshot({ path: '/home/zanbo/zanbotest/tmp/ui-fullshot-20260413/desktop/signals_graph_theme_relation_graph.png', fullPage: false })

  await page.goto('http://127.0.0.1:8002/signals/graph?center_type=industry&keyword=%E8%BD%AF%E9%A5%AE%E6%96%99&depth=2&limit=12', { waitUntil: 'domcontentloaded' })
  await page.waitForTimeout(2800)
  await page.screenshot({ path: '/home/zanbo/zanbotest/tmp/ui-fullshot-20260413/desktop/signals_graph_industry_relation_graph.png', fullPage: false })

  await browser.close()
})()
