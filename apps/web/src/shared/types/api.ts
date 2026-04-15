export interface DashboardPayload {
  generated_at: string
  overview: Record<string, number>
  database_health?: Record<string, any>
  top_scores?: Array<Record<string, any>>
  candidate_pool_top?: Array<Record<string, any>>
  recent_daily_summaries?: Array<Record<string, any>>
  important_news?: Array<Record<string, any>>
}

export interface MacroRegimeCard {
  label?: string
  score?: number
  mode?: string
  summary?: string
  factors?: string[]
}

export interface IndustryScoreItem {
  industry: string
  score: number
  count?: number
  top_stocks?: Array<Record<string, any>>
}

export interface ShortlistItem {
  ts_code: string
  name?: string
  industry?: string
  market?: string
  area?: string
  total_score?: number
  industry_total_score?: number
  score_grade?: string
  industry_score_grade?: string
  industry_rank?: number | null
  industry_count?: number | null
  position_label?: string
  decision_reason?: string
  decision_risk?: string
  source_date?: string
  score_summary?: Record<string, any>
}

export interface ReasonPacket {
  ts_code: string
  name?: string
  industry?: string
  score?: Record<string, any>
  news?: Record<string, any>
  signals?: Record<string, any>
  candidate_pool?: Record<string, any>
  degraded_sources?: string[]
  status?: string
}

export interface DecisionScoreboardPayload {
  ok?: boolean
  generated_at: string
  snapshot_date?: string
  macro_regime: MacroRegimeCard
  industry_scores: IndustryScoreItem[]
  stock_shortlist: ShortlistItem[]
  reason_packets: Record<string, ReasonPacket>
  source_health?: Record<string, string>
}

export interface PaginatedResponse<T = Record<string, any>> {
  items: T[]
  total: number
  page?: number
  page_size?: number
  total_pages?: number
}
