import { http } from '../http'

export interface PortfolioPosition {
  id: string
  ts_code: string
  name?: string
  size?: number
  avg_price?: number
  current_price?: number
  unrealized_pnl?: number
  created_at?: string
}

export interface PortfolioOrder {
  id: string
  ts_code: string
  name?: string
  action_type?: string
  planned_price?: number
  executed_price?: number
  size?: number
  status?: string
  created_at?: string
  executed_at?: string
  decision_action_id?: string
  note?: string
}

export interface PortfolioReview {
  id: string
  order_id?: string
  review_tag?: string
  slippage?: number
  review_note?: string
  created_at?: string
}

export async function fetchPortfolioPositions() {
  const { data } = await http.get('/api/portfolio/positions')
  return data
}

export async function fetchPortfolioOrders(params?: { status?: string; limit?: number; decision_action_id?: string }) {
  const { data } = await http.get('/api/portfolio/orders', { params })
  return data
}

export async function createPortfolioOrder(payload: {
  ts_code: string
  action_type: string
  planned_price?: number
  size?: number
  note?: string
}) {
  const { data } = await http.post('/api/portfolio/orders', payload)
  return data
}

export async function updatePortfolioOrder(id: string, payload: Record<string, any>) {
  const { data } = await http.patch(`/api/portfolio/orders/${id}`, payload)
  return data
}

export async function fetchPortfolioReviews(params?: { order_id?: string; limit?: number }) {
  const { data } = await http.get('/api/portfolio/review', { params })
  return data
}

export async function createPortfolioReview(payload: {
  order_id?: string
  review_tag: string
  slippage?: number
  review_note?: string
}) {
  const { data } = await http.post('/api/portfolio/review', payload)
  return data
}
