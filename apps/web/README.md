# Zanbo Quant Vue Frontend

## Run dev

```bash
cd /home/zanbo/zanbotest/apps/web
npm install
npm run dev
```

Dev server: `http://127.0.0.1:5173`

## Build

```bash
cd /home/zanbo/zanbotest/apps/web
npm run build
```

Build output: `apps/web/dist`

## Preview build

```bash
cd /home/zanbo/zanbotest/apps/web
npm run preview
```

Preview server: `http://127.0.0.1:4173`

## Admin Token

Protected API actions now require `BACKEND_ADMIN_TOKEN` on the backend.

For browser use, set one of:

```js
localStorage.setItem('zanbo_admin_token', '<BACKEND_ADMIN_TOKEN>')
sessionStorage.setItem('zanbo_admin_token', '<BACKEND_ADMIN_TOKEN>')
```

Or provide `VITE_ADMIN_API_TOKEN` during local development.

## Dev API fallback (quant-factors)

默认前端只走 `VITE_API_BASE_URL`（或同源 `/api`）。  
如需本机多端口调试量化接口，可在前端环境变量中显式开启：

```bash
VITE_QUANT_API_DEV_FALLBACK=1
```

## Current modules

- Dashboard
- Stocks List
- Stock Scores
- Stock Detail
- Global News
- CN News
- Stock News
- Daily Summaries
- Signals Overview
- Themes
- Signal Timeline
- Research Reports
- Multi-role Research
- Chatrooms Overview
- Candidate Pool
- Source Monitor
- Database Audit

## Architecture

- Vue 3 + TypeScript + Vite
- Vue Router
- Pinia
- TanStack Query
- Tailwind CSS v4
- Axios
- Markdown rendering
- WebSocket realtime bus
