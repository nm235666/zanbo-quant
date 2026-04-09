import { http } from '../http'

export async function fetchDecisionBoard(params: Record<string, any> = {}) {
  const { data } = await http.get('/api/decision/board', { params })
  return data
}

export async function fetchDecisionStock(params: Record<string, any>) {
  const { data } = await http.get('/api/decision/stock', { params })
  return data
}

export async function fetchDecisionPlan(params: Record<string, any> = {}) {
  const { data } = await http.get('/api/decision/plan', { params })
  return data
}

export async function fetchDecisionStrategies(params: Record<string, any> = {}) {
  const { data } = await http.get('/api/decision/strategies', { params })
  return data
}

export async function fetchDecisionStrategyRuns(params: Record<string, any> = {}) {
  const { data } = await http.get('/api/decision/strategy-runs', { params })
  return data
}

export async function fetchDecisionStrategyRun(params: Record<string, any> = {}) {
  const { data } = await http.get('/api/decision/strategy-runs', { params })
  return data
}

export async function runDecisionStrategyLab(payload: Record<string, any> = {}) {
  const { data } = await http.post('/api/decision/strategy-runs/run', payload)
  return data
}

export async function fetchDecisionHistory(params: Record<string, any> = {}) {
  const { data } = await http.get('/api/decision/history', { params })
  return data
}

export async function fetchDecisionActions(params: Record<string, any> = {}) {
  const { data } = await http.get('/api/decision/actions', { params })
  return data
}

export async function fetchDecisionKillSwitch() {
  const { data } = await http.get('/api/decision/kill-switch')
  return data
}

export async function setDecisionKillSwitch(payload: { allow_trading: boolean; reason?: string }) {
  const { data } = await http.post('/api/decision/kill-switch', payload)
  return data
}

export async function runDecisionSnapshot() {
  const { data } = await http.post('/api/decision/snapshot/run', {})
  return data
}

export async function recordDecisionAction(payload: {
  action_type: 'confirm' | 'reject' | 'defer' | 'watch' | 'review'
  ts_code: string
  stock_name?: string
  note?: string
  snapshot_date?: string
  context?: Record<string, any>
}) {
  const { data } = await http.post('/api/decision/actions', payload)
  return data
}
