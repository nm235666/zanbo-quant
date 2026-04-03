import axios from 'axios'
import { readAdminToken } from './authToken'

const resolvedBaseUrl = import.meta.env.VITE_API_BASE_URL?.trim() || ''
const bundledAdminToken = import.meta.env.VITE_ADMIN_API_TOKEN?.trim() || ''

export const http = axios.create({
  baseURL: resolvedBaseUrl,
  timeout: 20_000,
})

http.interceptors.request.use((config) => {
  const token = readAdminToken() || bundledAdminToken
  if (token) {
    config.headers = config.headers || {}
    config.headers['X-Admin-Token'] = token
  }
  return config
})

http.interceptors.response.use(
  (response) => response,
  (error) => {
    const data = error?.response?.data || {}
    const status = error?.response?.status
    const reqBase = String(error?.config?.baseURL || resolvedBaseUrl || '').trim()
    const reqUrl = String(error?.config?.url || '').trim()
    const endpoint = `${reqBase}${reqUrl}` || reqUrl || reqBase
    const code = data?.code ? ` [${data.code}]` : ''
    const hint = data?.hint ? `（${data.hint}）` : ''
    const networkHint = !error?.response && endpoint ? `（endpoint: ${endpoint}）` : ''
    const message = `${data?.error || error?.message || '请求失败'}${code}${hint}${networkHint}`
    const wrapped: Error & { status?: number; response?: any; data?: any } = new Error(message)
    wrapped.status = status
    wrapped.response = error?.response
    wrapped.data = data
    return Promise.reject(wrapped)
  },
)
