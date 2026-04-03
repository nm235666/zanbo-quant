import { http } from '../http'
import { readAdminToken } from '../authToken'

export async function fetchStockFilters() {
  const { data } = await http.get('/api/stocks/filters')
  return data
}

export async function fetchStocks(params: Record<string, any>) {
  const { data } = await http.get('/api/stocks', { params })
  return data
}

export async function fetchStockDetail(params: Record<string, any>) {
  const { data } = await http.get('/api/stock-detail', { params })
  return data
}

export async function fetchStockPrices(params: Record<string, any>) {
  const { data } = await http.get('/api/prices', { params })
  return data
}

export async function fetchStockMinline(params: Record<string, any>) {
  const { data } = await http.get('/api/minline', { params })
  return data
}

export async function fetchStockScores(params: Record<string, any>) {
  const { data } = await http.get('/api/stock-scores', { params })
  return data
}

export async function fetchStockScoreFilters() {
  const { data } = await http.get('/api/stock-scores/filters')
  return data
}

export async function triggerStockNewsFetch(params: Record<string, any>) {
  const { data } = await http.get('/api/stock-news/fetch', { params })
  return data
}

export async function triggerTrendAnalysis(params: Record<string, any>) {
  const { data } = await http.get('/api/llm/trend', {
    params,
    timeout: 180_000,
  })
  return data
}

export async function triggerMultiRoleTask(params: Record<string, any>) {
  const { data } = await http.get('/api/llm/multi-role/start', { params })
  return data
}

export async function fetchMultiRoleTask(params: Record<string, any>) {
  const { data } = await http.get('/api/llm/multi-role/task', { params })
  return data
}

export async function triggerMultiRoleTaskV2(payload: Record<string, any>) {
  const { data } = await http.post('/api/llm/multi-role/v2/start', payload)
  return data
}

export async function fetchMultiRoleTaskV2(params: Record<string, any>) {
  const { data } = await http.get('/api/llm/multi-role/v2/task', { params })
  return data
}

export async function decideMultiRoleTaskV2(payload: Record<string, any>) {
  const { data } = await http.post('/api/llm/multi-role/v2/decision', payload)
  return data
}

export async function retryMultiRoleAggregateV2(payload: Record<string, any>) {
  const { data } = await http.post('/api/llm/multi-role/v2/retry-aggregate', payload, { timeout: 120_000 })
  return data
}

export async function streamMultiRoleTaskV2(
  params: { job_id: string; interval_ms?: number; timeout_seconds?: number },
  options: {
    signal?: AbortSignal
    onMessage?: (packet: any) => void
  } = {},
) {
  const query = new URLSearchParams()
  query.set('job_id', String(params.job_id || ''))
  if (params.interval_ms != null) query.set('interval_ms', String(params.interval_ms))
  if (params.timeout_seconds != null) query.set('timeout_seconds', String(params.timeout_seconds))

  const base = (import.meta.env.VITE_API_BASE_URL?.trim() || '').replace(/\/$/, '')
  const url = `${base}/api/llm/multi-role/v2/stream?${query.toString()}`
  const token = readAdminToken() || (import.meta.env.VITE_ADMIN_API_TOKEN?.trim() || '')
  const headers: Record<string, string> = {}
  if (token) headers['X-Admin-Token'] = token

  const response = await fetch(url, {
    method: 'GET',
    headers,
    signal: options.signal,
    credentials: 'same-origin',
  })
  if (!response.ok) {
    let message = `stream request failed: HTTP ${response.status}`
    try {
      const data = await response.json()
      if (data?.error) message = String(data.error)
    } catch {
      // ignore json parse error
    }
    throw new Error(message)
  }
  if (!response.body) return

  const reader = response.body.getReader()
  const decoder = new TextDecoder('utf-8')
  let buffer = ''
  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    let newlineIndex = buffer.indexOf('\n')
    while (newlineIndex >= 0) {
      const line = buffer.slice(0, newlineIndex).trim()
      buffer = buffer.slice(newlineIndex + 1)
      if (line) {
        try {
          const packet = JSON.parse(line)
          options.onMessage?.(packet)
        } catch {
          // ignore malformed stream line
        }
      }
      newlineIndex = buffer.indexOf('\n')
    }
  }
}
