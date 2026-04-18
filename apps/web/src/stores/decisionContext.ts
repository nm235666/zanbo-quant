import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface DecisionContext {
  ts_code?: string
  name?: string
  from?: string
  industry?: string
  keyword?: string
  score_date?: string
  signal_run_id?: string
  multi_role_job_id?: string
  snapshot_id?: string
  trace_id?: string
  set_at?: string  // ISO timestamp
}

export const useDecisionContextStore = defineStore('decisionContext', () => {
  const context = ref<DecisionContext>({})

  function setContext(update: Partial<DecisionContext>) {
    context.value = {
      ...context.value,
      ...update,
      set_at: new Date().toISOString(),
    }
  }

  function clearContext() {
    context.value = {}
  }

  function mergeFromQuery(query: Record<string, string | string[] | undefined>) {
    const update: Partial<DecisionContext> = {}
    if (query.ts_code) update.ts_code = String(query.ts_code)
    if (query.from) update.from = String(query.from)
    if (query.keyword) update.keyword = String(query.keyword)
    if (query.industry) update.industry = String(query.industry)
    if (query.score_date) update.score_date = String(query.score_date)
    if (query.signal_run_id) update.signal_run_id = String(query.signal_run_id)
    if (query.multi_role_job_id) update.multi_role_job_id = String(query.multi_role_job_id)
    if (Object.keys(update).length) setContext(update)
  }

  const hasContext = computed(() =>
    Object.keys(context.value)
      .filter((k) => k !== 'set_at')
      .some((k) => context.value[k as keyof DecisionContext]),
  )

  const contextAge = computed(() => {
    if (!context.value.set_at) return null
    return Date.now() - new Date(context.value.set_at).getTime()
  })

  // Context is fresh if set within last 30 minutes
  const isContextFresh = computed(() => {
    const age = contextAge.value
    return age !== null && age < 30 * 60 * 1000
  })

  return { context, hasContext, contextAge, isContextFresh, setContext, clearContext, mergeFromQuery }
})
