import { http } from '../http'

export type QuantFactorsStartPayload = {
  direction: string
  market_scope?: string
  lookback?: number
  config_profile?: string
  llm_profile?: string
  engine_profile?: 'auto' | 'business' | 'research'
  extra_args?: string[]
}

export async function startQuantMine(payload: QuantFactorsStartPayload) {
  return callQuantFactorsApi('post', '/mine/start', payload)
}

export async function startQuantAutoResearch(payload: QuantFactorsStartPayload) {
  return callQuantFactorsApi('post', '/auto-research/start', payload)
}

export async function startQuantBacktest(payload: QuantFactorsStartPayload) {
  return callQuantFactorsApi('post', '/backtest/start', payload)
}

export async function fetchQuantTask(task_id: string) {
  return callQuantFactorsApi('get', '/task', undefined, { task_id })
}

export async function fetchQuantResults(params: Record<string, any>) {
  return callQuantFactorsApi('get', '/results', undefined, params)
}

export async function fetchQuantHealth() {
  return callQuantFactorsApi('get', '/health')
}

type QuantApiMethod = 'get' | 'post'

const devFallbackEnabled = String(import.meta.env.VITE_QUANT_API_DEV_FALLBACK || '').trim().toLowerCase()
const enableDevFallback = devFallbackEnabled === '1' || devFallbackEnabled === 'true' || devFallbackEnabled === 'yes' || devFallbackEnabled === 'on'

function quantApiCandidates(suffix: string): string[] {
  const list = [`/api/quant-factors${suffix}`]
  if (typeof window !== 'undefined' && enableDevFallback) {
    const protocol = window.location.protocol || 'http:'
    const host = window.location.hostname || '127.0.0.1'
    list.push(`${protocol}//${host}:8077/api/quant-factors${suffix}`)
    list.push(`${protocol}//${host}:8002/api/quant-factors${suffix}`)
  }
  return Array.from(new Set(list))
}

async function callQuantFactorsApi(method: QuantApiMethod, suffix: string, payload?: any, params?: Record<string, any>) {
  const urls = quantApiCandidates(suffix)
  let lastError: any = null
  const statusTrace: Array<{ url: string; status: number }> = []
  for (const url of urls) {
    try {
      if (method === 'get') {
        const { data } = await http.get(url, { params })
        return data
      }
      const { data } = await http.post(url, payload || {})
      return data
    } catch (error: any) {
      lastError = error
      const status = Number(error?.status || error?.response?.status || 0)
      statusTrace.push({ url, status })
      if (status === 401 || status === 403) throw error
      if (status && status !== 404) throw error
      continue
    }
  }
  const authFailed = statusTrace.some((row) => row.status === 401 || row.status === 403)
  if (authFailed) {
    throw new Error('鉴权失败：请重新登录后再试（quant-factors）')
  }
  if (statusTrace.length && statusTrace.every((row) => row.status === 404)) {
    const used = statusTrace.map((row) => row.url).join(' | ')
    throw new Error(`接口未找到：${suffix}（已尝试 ${used}）`)
  }
  throw lastError || new Error('quant-factors API unavailable')
}
