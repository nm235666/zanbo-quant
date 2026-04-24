import { http } from '../http'

export interface FunnelCandidate {
  id: string
  ts_code: string
  name?: string
  current_state: string
  state_version?: number
  last_transition_reason?: string
  last_updated?: string
  created_at?: string
  evidence_summary?: FunnelEvidenceSummary
}

export interface FunnelMetrics {
  candidate_count?: number
  avg_days_to_decision?: number | null
  conversion_rate?: number | null
}

export interface FunnelEvidenceSummary {
  evidence_status?: string
  evidence_chain_complete?: boolean
  missing_evidence?: string[]
  warning_messages?: string[]
  score_status?: string
  total_score?: number | null
  news_count?: number
  signal_count?: number
  candidate_pool_count?: number
  latest_evidence_time?: string
}

export interface FunnelEvidencePacket {
  ts_code?: string
  name?: string
  industry?: string
  score?: Record<string, any>
  news?: Record<string, any>
  signals?: Record<string, any>
  candidate_pool?: Record<string, any>
  degraded_sources?: string[]
  status?: string
  evidence_status?: string
  missing_evidence?: string[]
  warning_messages?: string[]
  evidence_chain_complete?: boolean
}

export interface FunnelTransitionPayload {
  to_state: string
  reason?: string
  trigger_source?: string
  evidence_ref?: string
  idempotency_key?: string
  state_version?: number
  operator?: string
}

export async function fetchFunnelCandidates(params?: {
  state?: string
  q?: string
  limit?: number
  offset?: number
  include_evidence?: 1 | boolean
}) {
  const { data } = await http.get('/api/funnel/candidates', { params })
  return data
}

export async function fetchFunnelReviewSnapshots(candidateId: string, params?: { limit?: number }) {
  const { data } = await http.get('/api/funnel/review-snapshots', {
    params: { candidate_id: candidateId, ...params },
  })
  return data
}

export async function fetchFunnelCandidate(id: string) {
  const { data } = await http.get(`/api/funnel/candidates/${id}`)
  return data
}

export async function createFunnelCandidate(payload: {
  ts_code: string
  name: string
  source?: string
  trigger_source?: string
  reason?: string
  evidence_ref?: string
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
