import { http } from '../http'
import { readAdminToken } from '../authToken'
import axios from 'axios'

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
  const { data } = await requestWithBaseFallback({
    method: 'post',
    url: '/api/llm/multi-role/v2/start',
    data: payload,
  })
  return data as any
}

export async function triggerMultiRoleTaskV3(payload: Record<string, any>) {
  const { data } = await requestWithBaseFallback({
    method: 'post',
    url: '/api/llm/multi-role/v3/jobs',
    data: payload,
  })
  return data as any
}

export async function fetchMultiRoleTaskV3(jobId: string) {
  const { data } = await requestWithBaseFallback({
    method: 'get',
    url: `/api/llm/multi-role/v3/jobs/${encodeURIComponent(String(jobId || '').trim())}`,
  })
  return data as any
}

export async function decideMultiRoleTaskV3(jobId: string, action: 'retry' | 'degrade' | 'abort' | 'resume') {
  const { data } = await requestWithBaseFallback({
    method: 'post',
    url: `/api/llm/multi-role/v3/jobs/${encodeURIComponent(String(jobId || '').trim())}/decisions`,
    data: { action },
  })
  return data as any
}

export async function actMultiRoleTaskV3(
  jobId: string,
  action: 'retry_stage' | 're_aggregate' | 'abort' | 'resume',
  stage = '',
) {
  const { data } = await requestWithBaseFallback({
    method: 'post',
    url: `/api/llm/multi-role/v3/jobs/${encodeURIComponent(String(jobId || '').trim())}/actions`,
    data: { action, stage },
    timeout: 120_000,
  })
  return data as any
}

export async function fetchMultiRoleTaskV2(params: Record<string, any>) {
  const { data } = await requestWithBaseFallback({
    method: 'get',
    url: '/api/llm/multi-role/v2/task',
    params,
  })
  return data as any
}

export async function decideMultiRoleTaskV2(payload: Record<string, any>) {
  const { data } = await requestWithBaseFallback({
    method: 'post',
    url: '/api/llm/multi-role/v2/decision',
    data: payload,
  })
  return data as any
}

export async function retryMultiRoleAggregateV2(payload: Record<string, any>) {
  const { data } = await requestWithBaseFallback({
    method: 'post',
    url: '/api/llm/multi-role/v2/retry-aggregate',
    data: payload,
    timeout: 120_000,
  })
  return data as any
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

  const configuredBase = (import.meta.env.VITE_API_BASE_URL?.trim() || '').replace(/\/$/, '')
  const baseCandidates = configuredBase ? [configuredBase, ''] : ['']
  const token = readAdminToken() || (import.meta.env.VITE_ADMIN_API_TOKEN?.trim() || '')
  const headers: Record<string, string> = {}
  if (token) headers['X-Admin-Token'] = token

  let response: Response | null = null
  let lastError: unknown = null
  for (const base of baseCandidates) {
    const url = `${base}/api/llm/multi-role/v2/stream?${query.toString()}`
    try {
      response = await fetch(url, {
        method: 'GET',
        headers,
        signal: options.signal,
        credentials: 'same-origin',
      })
      break
    } catch (error) {
      lastError = error
      continue
    }
  }
  if (!response) throw (lastError || new Error('stream request failed'))
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

export async function streamMultiRoleTaskV3(
  params: { job_id: string; interval_ms?: number; timeout_seconds?: number },
  options: {
    signal?: AbortSignal
    onMessage?: (packet: any) => void
  } = {},
) {
  const query = new URLSearchParams()
  query.set('interval_ms', String(params.interval_ms ?? 1000))
  query.set('timeout_seconds', String(params.timeout_seconds ?? 180))

  const configuredBase = (import.meta.env.VITE_API_BASE_URL?.trim() || '').replace(/\/$/, '')
  const baseCandidates = configuredBase ? [configuredBase, ''] : ['']
  const token = readAdminToken() || (import.meta.env.VITE_ADMIN_API_TOKEN?.trim() || '')
  const headers: Record<string, string> = {}
  if (token) headers['X-Admin-Token'] = token

  let response: Response | null = null
  let lastError: unknown = null
  for (const base of baseCandidates) {
    const url = `${base}/api/llm/multi-role/v3/jobs/${encodeURIComponent(String(params.job_id || '').trim())}/stream?${query.toString()}`
    try {
      response = await fetch(url, {
        method: 'GET',
        headers,
        signal: options.signal,
        credentials: 'same-origin',
      })
      break
    } catch (error) {
      lastError = error
      continue
    }
  }
  if (!response) throw (lastError || new Error('stream request failed'))
  if (!response.ok) {
    let message = `stream request failed: HTTP ${response.status}`
    try {
      const data = await response.json()
      if (data?.error) message = String(data.error)
    } catch {
      // ignore
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

async function requestWithBaseFallback(config: {
  method: 'get' | 'post'
  url: string
  params?: Record<string, any>
  data?: Record<string, any>
  timeout?: number
}) {
  try {
    return await http.request({
      method: config.method,
      url: config.url,
      params: config.params,
      data: config.data,
      timeout: config.timeout,
    })
  } catch (error: any) {
    // 配置了不可达 baseURL 时，优先回落同源地址，避免前端直接 Network Error
    if (error?.response || !import.meta.env.VITE_API_BASE_URL?.trim()) throw error
    const token = readAdminToken() || (import.meta.env.VITE_ADMIN_API_TOKEN?.trim() || '')
    const headers: Record<string, string> = {}
    if (token) headers['X-Admin-Token'] = token
    return axios.request({
      method: config.method,
      url: config.url,
      params: config.params,
      data: config.data,
      timeout: config.timeout ?? 20_000,
      headers,
      withCredentials: true,
    })
  }
}
