import { http } from '../http'

export interface FunnelCandidate {
  id: string
  ts_code: string
  name?: string
  current_state: string
  last_transition_reason?: string
  last_updated?: string
  created_at?: string
}

export interface FunnelMetrics {
  candidate_count?: number
  avg_days_to_decision?: number
  conversion_rate?: number
}

export interface FunnelTransitionPayload {
  to_state: string
  reason?: string
  trigger_source?: string
}

export async function fetchFunnelCandidates(params?: { state?: string; limit?: number; offset?: number }) {
  const { data } = await http.get('/api/funnel/candidates', { params })
  return data
}

export async function fetchFunnelCandidate(id: string) {
  const { data } = await http.get(`/api/funnel/candidates/${id}`)
  return data
}

export async function createFunnelCandidate(payload: {
  ts_code: string
  name?: string
  initial_state?: string
  trigger_source?: string
  reason?: string
}) {
  const { data } = await http.post('/api/funnel/candidates', payload)
  return data
}

export async function transitionFunnelCandidate(id: string, payload: FunnelTransitionPayload) {
  const { data } = await http.post(`/api/funnel/candidates/${id}/transition`, payload)
  return data
}

export async function fetchFunnelMetrics() {
  const { data } = await http.get('/api/funnel/metrics')
  return data
}
