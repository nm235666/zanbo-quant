import type { LocationQueryRaw } from 'vue-router'
import type { NavSurface } from './navigation'

export const CROSS_MODE_ALLOWED_KEYS = [
  'ts_code',
  'tsCode',
  'code',
  'theme',
  'theme_id',
  'theme_code',
  'signal',
  'signal_id',
  'signal_code',
  'industry',
  'industry_code',
  'q',
  'query',
  'keyword',
  'date_from',
  'date_to',
  'start_date',
  'end_date',
  'range',
  'window',
  'time_range',
  'from',
] as const

export const CROSS_MODE_DROPPED_KEYS = [
  'job_id',
  'job_run_id',
  'run_id',
  'provider_id',
  'node_id',
  'cursor',
  'dry_run',
  'audit_id',
  'audit_filter',
  'admin_token',
  'bypass_cache',
  'trace_id',
  'internal_id',
]

export type CrossModeContext = {
  preservedQuery: LocationQueryRaw
  droppedKeys: string[]
  stockCode: string | null
  themeId: string | null
  signalId: string | null
  industry: string | null
  targetPath: string
}

const ALLOWED_SET = new Set<string>(CROSS_MODE_ALLOWED_KEYS)
const DROPPED_SET = new Set<string>(CROSS_MODE_DROPPED_KEYS)

function pickString(value: unknown): string {
  if (Array.isArray(value)) {
    for (const item of value) {
      const s = pickString(item)
      if (s) return s
    }
    return ''
  }
  if (value == null) return ''
  const s = String(value).trim()
  return s
}

function hasStockDetailPageIn(surface: NavSurface): boolean {
  return surface === 'app'
}

function hasSignalTimelineIn(surface: NavSurface): boolean {
  return surface === 'app'
}

function hasThemesPageIn(surface: NavSurface): boolean {
  return surface === 'app'
}

export function extractCrossModeContext(
  rawQuery: Record<string, unknown> | null | undefined,
  targetSurface: NavSurface,
): CrossModeContext {
  const preservedQuery: Record<string, string | string[]> = {}
  const droppedKeys: string[] = []
  const query = rawQuery && typeof rawQuery === 'object' ? rawQuery : {}

  for (const rawKey of Object.keys(query)) {
    const key = String(rawKey || '').trim()
    if (!key) continue
    if (DROPPED_SET.has(key)) {
      droppedKeys.push(key)
      continue
    }
    if (!ALLOWED_SET.has(key)) {
      droppedKeys.push(key)
      continue
    }
    const value = query[rawKey]
    if (Array.isArray(value)) {
      const arr = value.map((v) => (v == null ? '' : String(v).trim())).filter(Boolean)
      if (arr.length) preservedQuery[key] = arr
    } else {
      const s = value == null ? '' : String(value).trim()
      if (s) preservedQuery[key] = s
    }
  }

  const stockCode = pickString(query.ts_code) || pickString(query.tsCode) || pickString(query.code) || ''
  const themeId = pickString(query.theme_id) || pickString(query.theme) || pickString(query.theme_code) || ''
  const signalId = pickString(query.signal_id) || pickString(query.signal) || pickString(query.signal_code) || ''
  const industry = pickString(query.industry) || pickString(query.industry_code) || ''

  let targetPath = targetSurface === 'app' ? '/app/desk/workbench' : '/admin/dashboard'
  if (stockCode && hasStockDetailPageIn(targetSurface)) {
    targetPath = `/app/data/stocks/detail/${encodeURIComponent(stockCode)}`
  } else if (signalId && hasSignalTimelineIn(targetSurface)) {
    targetPath = `/app/data/signals/timeline`
  } else if (themeId && hasThemesPageIn(targetSurface)) {
    targetPath = `/app/data/signals/themes`
  } else if (industry && targetSurface === 'app') {
    targetPath = `/app/data/signals/graph`
  } else if (targetSurface === 'admin' && stockCode) {
    targetPath = `/admin/dashboard`
  }

  return {
    preservedQuery,
    droppedKeys,
    stockCode: stockCode || null,
    themeId: themeId || null,
    signalId: signalId || null,
    industry: industry || null,
    targetPath,
  }
}

export function describeCrossModeContext(ctx: CrossModeContext, targetSurface: NavSurface): string {
  const pieces: string[] = []
  if (ctx.stockCode) pieces.push(`股票 ${ctx.stockCode}`)
  if (ctx.signalId) pieces.push(`信号 ${ctx.signalId}`)
  if (ctx.themeId) pieces.push(`主题 ${ctx.themeId}`)
  if (ctx.industry) pieces.push(`行业 ${ctx.industry}`)
  const preservedKeys = Object.keys(ctx.preservedQuery).filter(
    (k) => !['ts_code', 'tsCode', 'code', 'theme', 'theme_id', 'signal', 'signal_id', 'industry', 'industry_code', 'theme_code', 'signal_code'].includes(k),
  )
  if (preservedKeys.length) pieces.push(`筛选 ${preservedKeys.join('/')}`)
  const modeLabel = targetSurface === 'app' ? '研究工作台' : '后台管理台'
  const head = `已切换到${modeLabel}`
  if (!pieces.length && !ctx.droppedKeys.length) return `${head}。`
  const preserved = pieces.length ? `保留 ${pieces.join('、')}` : '无可保留上下文'
  const dropped = ctx.droppedKeys.length ? `丢弃 ${ctx.droppedKeys.join('/')}（当前模式不兼容）` : ''
  return `${head}，${preserved}${dropped ? '；' + dropped : ''}。`
}
