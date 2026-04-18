import { http } from '../http'

export interface DailyMetrics {
  date: string
  pipeline_success_rate: number | null
  traceability_rate: number | null
  closure_rate: number | null
  sample_insufficient: boolean
}

export interface MetricsSummary {
  latest: DailyMetrics | null
  trend_7d: DailyMetrics[]
}

export async function fetchMetricsSummary(): Promise<MetricsSummary> {
  const { data } = await http.get('/api/metrics/summary')
  return data
}
