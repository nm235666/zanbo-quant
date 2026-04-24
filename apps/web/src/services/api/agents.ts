import { http } from '../http'

export type AgentRun = {
  id: string
  agent_key: string
  status: string
  mode?: string
  trigger_source?: string
  schedule_key?: string
  actor?: string
  goal?: Record<string, any>
  plan?: Record<string, any>
  result?: Record<string, any>
  error_text?: string
  approval_required?: boolean
  created_at?: string
  updated_at?: string
  finished_at?: string
  steps?: AgentStep[]
}

export type AgentStep = {
  id: string
  run_id: string
  step_index: number
  tool_name: string
  args?: Record<string, any>
  dry_run?: boolean
  status: string
  audit_id?: number
  result?: Record<string, any>
  error_text?: string
  created_at?: string
  updated_at?: string
}

export async function fetchAgentRuns(params: Record<string, any> = {}) {
  const { data } = await http.get('/api/agents/runs', { params })
  return data as { ok: boolean; items: AgentRun[] }
}

export async function fetchAgentRun(runId: string) {
  const { data } = await http.get(`/api/agents/runs/${encodeURIComponent(runId)}`)
  return data as { ok: boolean; run: AgentRun }
}

export async function startAgentRun(payload: {
  agent_key: string
  trigger_source?: string
  actor?: string
  goal?: Record<string, any>
  schedule_key?: string
  dedupe?: boolean
}) {
  const { data } = await http.post('/api/agents/runs', payload)
  return data as { ok: boolean; run: AgentRun }
}

export async function approveAgentRun(runId: string, payload: { reason: string; actor?: string; idempotency_key?: string }) {
  const { data } = await http.post(`/api/agents/runs/${encodeURIComponent(runId)}/approve`, {
    ...payload,
    decision: 'approved',
  })
  return data as { ok: boolean; run: AgentRun }
}

export async function rejectAgentRun(runId: string, payload: { reason: string; actor?: string; idempotency_key?: string }) {
  const { data } = await http.post(`/api/agents/runs/${encodeURIComponent(runId)}/approve`, {
    ...payload,
    decision: 'rejected',
  })
  return data as { ok: boolean; run: AgentRun }
}
