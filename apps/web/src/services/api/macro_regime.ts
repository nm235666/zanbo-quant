import { http } from '../http'

export interface MacroRegime {
  id: string
  status?: 'ready' | 'insufficient_evidence' | 'not_initialized' | 'empty' | 'error'
  status_reason?: string
  missing_inputs?: string[]
  generated_from?: string[]
  conflict_ruling?: string
  short_term_state: string
  short_term_confidence: number
  short_term_change_reason: string
  short_term_changed: number
  medium_term_state: string
  medium_term_confidence: number
  medium_term_change_reason: string
  medium_term_changed: number
  long_term_state: string
  long_term_confidence: number
  long_term_change_reason: string
  long_term_changed: number
  portfolio_action_json: Array<{ type: string; description: string }>
  created_at: string
  created_by: string
  outcome_notes?: string
  outcome_rating?: 'effective' | 'partial' | 'ineffective'
  correction_suggestion?: string
}

export interface RegimeRecord {
  short_term_state: string
  medium_term_state: string
  long_term_state: string
  short_term_confidence?: number
  medium_term_confidence?: number
  long_term_confidence?: number
  short_term_change_reason?: string
  medium_term_change_reason?: string
  long_term_change_reason?: string
  short_term_changed?: boolean
  medium_term_changed?: boolean
  long_term_changed?: boolean
}

export const REGIME_STATE_LABELS: Record<string, string> = {
  expansion: '扩张',
  slowdown: '放缓',
  risk_rising: '风险抬升',
  volatile: '震荡',
  contraction: '收缩',
  recovery: '复苏',
}

export const REGIME_STATE_COLORS: Record<string, string> = {
  expansion: 'emerald',
  recovery: 'teal',
  slowdown: 'amber',
  volatile: 'yellow',
  risk_rising: 'orange',
  contraction: 'red',
}

export async function fetchLatestRegime() {
  const { data } = await http.get('/api/macro/regime')
  return data
}

export async function fetchRegimeHistory(params?: { page?: number; page_size?: number }) {
  const { data } = await http.get('/api/macro/regime', { params: { ...params, history: 1 } })
  return data
}

export async function recordRegime(payload: RegimeRecord) {
  const { data } = await http.post('/api/macro/regime', payload)
  return data
}

export interface RegimeSuggestion {
  short_term_state: string
  short_term_confidence: number
  medium_term_state: string
  medium_term_confidence: number
  long_term_state: string
  long_term_confidence: number
  basis: string
  data_points: number
}

export async function fetchRegimeSuggestion(): Promise<{ ok: boolean; suggestion: RegimeSuggestion | null }> {
  const resp = await fetch('/api/macro/regime?suggest=1', { credentials: 'include' })
  if (!resp.ok) throw new Error(await resp.text())
  return resp.json()
}

export async function updateRegimeOutcome(id: string, outcome_notes: string, outcome_rating: string, correction_suggestion: string = "") {
  const resp = await fetch(`/api/macro/regime?id=${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ outcome_notes, outcome_rating, correction_suggestion }),
    credentials: 'include',
  })
  if (!resp.ok) throw new Error(await resp.text())
  return resp.json()
}
