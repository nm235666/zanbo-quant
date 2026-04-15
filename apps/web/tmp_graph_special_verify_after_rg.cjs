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
  const report = []

  await login(page)

  await page.goto('http://127.0.0.1:8002/signals/graph?center_type=industry&keyword=%E8%BD%AF%E9%A5%AE%E6%96%99&depth=2&limit=12', { waitUntil: 'domcontentloaded' })
  await page.waitForTimeout(2600)

  const nodes = page.locator('.graph-node')
  const nodeCount = await nodes.count()
  report.push({ check: 'industry nodes render', ok: nodeCount >= 6, value: nodeCount })

  if (nodeCount > 1) {
    const target = nodes.nth(1)
    const title = (await target.locator('.graph-node-title').innerText()).trim()
    await target.click()
    await page.waitForTimeout(400)
    const detailTitle = (await page.locator('text=节点详情').locator('xpath=..').locator('div.text-2xl.font-extrabold').first().innerText().catch(() => '')).trim()
    report.push({ check: 'click sync detail', ok: !title || !detailTitle ? false : detailTitle.includes(title) || title.includes(detailTitle), value: { title, detailTitle } })
  }

  const relationChips = page.locator('button', { hasText: '行业→股票' })
  if (await relationChips.count()) {
    await relationChips.first().click()
    await page.waitForTimeout(500)
    report.push({ check: 'relation chip clickable', ok: true })
  }

  const overflowX = await page.evaluate(() => {
    const root = document.documentElement
    return Math.max(0, root.scrollWidth - root.clientWidth)
  })
  report.push({ check: 'overflowX=0', ok: overflowX === 0, value: overflowX })

  await page.screenshot({ path: '/home/zanbo/zanbotest/tmp/ui-fullshot-20260413/desktop/signals_graph_industry_verify_after_rg.png', fullPage: false })

  await page.goto('http://127.0.0.1:8002/signals/graph?center_type=theme&depth=2&limit=12', { waitUntil: 'domcontentloaded' })
  await page.waitForTimeout(2800)
  await page.screenshot({ path: '/home/zanbo/zanbotest/tmp/ui-fullshot-20260413/desktop/signals_graph_theme_verify_after_rg.png', fullPage: false })

  // Try double click on a theme/industry node to switch center.
  const graphNodes = page.locator('.graph-node')
  const gcount = await graphNodes.count()
  let switched = false
  for (let i = 0; i < Math.min(gcount, 6); i++) {
    const n = graphNodes.nth(i)
    const text = await n.innerText()
    if (text.includes('企业') || text.includes('评分')) {
      await n.dblclick()
      await page.waitForTimeout(900)
      switched = true
      break
    }
  }
  report.push({ check: 'double-click center switch attempted', ok: switched })

  console.log(JSON.stringify(report, null, 2))
  await browser.close()
})().catch((e) => {
  console.error(e)
  process.exit(1)
})
