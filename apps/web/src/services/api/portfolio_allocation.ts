import { http } from '../http'

export interface PortfolioAllocation {
  id: string
  status?: 'ready' | 'insufficient_evidence' | 'not_initialized' | 'empty' | 'error'
  status_reason?: string
  missing_inputs?: string[]
  generated_from?: string[]
  regime_id: string
  cash_ratio_pct: number
  max_single_position_pct: number
  max_theme_concentration_pct: number
  stance: string
  risk_budget_compression: number
  action_notes: string
  conflict_ruling: string
  macro_actions?: Array<{ type: string; description: string }>
  conflict_constraints?: {
    allowed_actions?: string[]
    required_defence_actions?: string[]
    risk_budget_pct?: number
    effective_condition?: string
  }
  long_term_review?: {
    regime_id?: string
    outcome_rating?: string
    outcome_notes?: string
    correction_suggestion?: string
    regime_created_at?: string
    action_count?: number
  }
  created_at: string
  created_by: string
}

export const STANCE_LABELS: Record<string, string> = {
  offensive: '进攻',
  defensive: '防守',
  neutral: '中性',
}

export const STANCE_COLORS: Record<string, string> = {
  offensive: 'emerald',
  defensive: 'rose',
  neutral: 'sky',
}

export async function fetchLatestAllocation() {
  const { data } = await http.get('/api/portfolio/allocation')
  return data
}

export async function fetchAllocationHistory(params?: { page?: number; page_size?: number }) {
  const { data } = await http.get('/api/portfolio/allocation', { params: { ...params, history: 1 } })
  return data
}

export async function recordAllocation(payload: {
  cash_ratio_pct: number
  max_single_position_pct: number
  max_theme_concentration_pct: number
  stance: string
  risk_budget_compression: number
  action_notes?: string
  regime_id?: string
}) {
  const { data } = await http.post('/api/portfolio/allocation', payload)
  return data
}
