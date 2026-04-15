const { chromium, devices } = require('@playwright/test');
const fs = require('fs/promises');
const path = require('path');

const baseURL = (process.env.PLAYWRIGHT_BASE_URL || 'http://192.168.5.52:8077').trim();
const outDir = '/home/zanbo/zanbotest/tmp/layout-scan';
const routes = [
  '/dashboard','/stocks/list','/stocks/scores','/stocks/detail/000001.SZ','/stocks/prices','/macro',
  '/intelligence/global-news','/intelligence/cn-news','/intelligence/stock-news','/intelligence/daily-summaries',
  '/signals/overview','/signals/themes','/signals/graph','/signals/timeline','/signals/audit','/signals/quality-config','/signals/state-timeline',
  '/research/reports','/research/scoreboard','/research/decision','/research/quant-factors','/research/multi-role','/research/trend',
  '/chatrooms/overview','/chatrooms/candidates','/chatrooms/chatlog','/chatrooms/investment',
  '/system/source-monitor','/system/jobs-ops','/system/llm-providers','/system/permissions','/system/database-audit','/system/invites','/system/users',
  '/upgrade'
];

function safeName(route) {
  return route.replace(/^\//, '').replace(/[^a-zA-Z0-9._-]+/g, '_') || 'root';
}

async function login(page) {
  await page.goto(baseURL + '/login', { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForTimeout(1500);
  await page.fill('input[type="text"]', 'nm235666');
  await page.fill('input[type="password"]', 'nm235689');
  const btns = page.locator('button');
  const count = await btns.count();
  await btns.nth(Math.max(0, count - 1)).click();
  await page.waitForTimeout(3500);
}

async function inspectLayout(page) {
  return page.evaluate(() => {
    const doc = document.scrollingElement || document.documentElement;
    const overflowX = (doc?.scrollWidth || 0) - window.innerWidth;
    const all = Array.from(document.querySelectorAll('*'));
    const offenders = [];
    for (const el of all) {
      const style = window.getComputedStyle(el);
      if (style.display === 'none' || style.visibility === 'hidden') continue;
      const r = el.getBoundingClientRect();
      if (r.width <= 0 || r.height <= 0) continue;
      const overRight = r.right - window.innerWidth;
      const overLeft = 0 - r.left;
      if (overRight > 8 || overLeft > 8) {
        offenders.push({
          tag: el.tagName.toLowerCase(),
          className: String(el.className || '').slice(0, 120),
          id: el.id || '',
          overRight: Math.round(overRight),
          overLeft: Math.round(overLeft),
          width: Math.round(r.width)
        });
        if (offenders.length >= 8) break;
      }
    }
    const fixedCount = all.filter((el) => window.getComputedStyle(el).position === 'fixed').length;
    return {
      title: document.title,
      innerWidth: window.innerWidth,
      scrollWidth: doc?.scrollWidth || 0,
      overflowX,
      fixedCount,
      offenders,
      textSnippet: (document.body?.innerText || '').slice(0, 180).replace(/\s+/g, ' ').trim(),
    };
  });
}

async function runViewport(name, contextOptions) {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext(contextOptions);
  const page = await context.newPage();
  const errors = [];
  page.on('console', (msg) => { if (msg.type() === 'error') errors.push(msg.text()); });
  page.on('pageerror', (err) => errors.push(String(err)));

  await login(page);

  const results = [];
  for (const route of routes) {
    const url = baseURL + route;
    const started = Date.now();
    let status = 'ok';
    let note = '';
    let metrics = null;
    try {
      await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
      await page.waitForTimeout(3500);
      metrics = await inspectLayout(page);
      const file = path.join(outDir, name, safeName(route) + '.png');
      await page.screenshot({ path: file, fullPage: true });
    } catch (e) {
      status = 'error';
      note = String(e && e.message ? e.message : e);
      const file = path.join(outDir, name, safeName(route) + '__error.png');
      try { await page.screenshot({ path: file, fullPage: true }); } catch (_) {}
    }
    results.push({ route, url, status, note, elapsedMs: Date.now() - started, metrics, consoleErrors: errors.slice(-5) });
  }

  await context.close();
  await browser.close();
  return results;
}

(async () => {
  await fs.mkdir(path.join(outDir, 'desktop'), { recursive: true });
  await fs.mkdir(path.join(outDir, 'mobile'), { recursive: true });
  const desktop = await runViewport('desktop', { viewport: { width: 1440, height: 900 } });
  const mobile = await runViewport('mobile', { ...devices['iPhone 13'] });
  const summary = { baseURL, generatedAt: new Date().toISOString(), desktop, mobile };
  await fs.writeFile(path.join(outDir, 'summary.json'), JSON.stringify(summary, null, 2), 'utf8');
  console.log('saved:', path.join(outDir, 'summary.json'));
})();
