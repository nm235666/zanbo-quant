<template>
  <AppShell title="Agent 运营台" subtitle="查看 Agent 运行、工具步骤、审批状态与 MCP 审计追踪。">
    <div class="space-y-4">
      <PageSection title="运行入口" subtitle="手动创建闭环 Agent run，worker 会处理 queued 状态。">
        <div class="grid gap-3 md:grid-cols-[1fr_1fr_auto]">
          <label class="text-sm font-semibold text-[var(--ink)]">
            Agent
            <select v-model="selectedAgentKey" class="mt-1 w-full rounded-2xl border border-[var(--line)] bg-white px-4 py-3">
              <option value="funnel_progress_agent">funnel_progress_agent</option>
              <option value="portfolio_reconcile_agent">portfolio_reconcile_agent</option>
              <option value="portfolio_review_agent">portfolio_review_agent</option>
            </select>
          </label>
          <label class="text-sm font-semibold text-[var(--ink)]">
            运行筛选
            <select v-model="filters.agent_key" class="mt-1 w-full rounded-2xl border border-[var(--line)] bg-white px-4 py-3">
              <option value="">全部 Agent</option>
              <option value="funnel_progress_agent">funnel_progress_agent</option>
              <option value="portfolio_reconcile_agent">portfolio_reconcile_agent</option>
              <option value="portfolio_review_agent">portfolio_review_agent</option>
            </select>
          </label>
          <button class="self-end rounded-2xl bg-[var(--brand)] px-4 py-3 font-semibold text-white disabled:opacity-50" :disabled="startMutation.isPending.value" @click="startRun">
            {{ startMutation.isPending.value ? '创建中...' : '创建 run' }}
          </button>
        </div>
      </PageSection>

      <div class="grid gap-4 xl:grid-cols-[minmax(0,0.95fr)_minmax(0,1.05fr)]">
        <PageSection :title="`Agent Runs (${runs.length})`" subtitle="点击一条运行查看 steps 和审批动作。">
          <div class="mb-3 flex flex-wrap items-center gap-2">
            <select v-model="filters.status" class="rounded-2xl border border-[var(--line)] bg-white px-3 py-2 text-sm">
              <option value="">全部状态</option>
              <option value="queued">queued</option>
              <option value="running">running</option>
              <option value="waiting_approval">waiting_approval</option>
              <option value="succeeded">succeeded</option>
              <option value="failed">failed</option>
              <option value="cancelled">cancelled</option>
            </select>
            <button class="rounded-2xl border border-[var(--line)] bg-white px-3 py-2 text-sm font-semibold" @click="refreshRuns">刷新</button>
          </div>
          <div class="max-h-[680px] space-y-2 overflow-auto pr-1">
            <InfoCard
              v-for="run in runs"
              :key="run.id"
              :title="run.agent_key"
              :meta="`${run.status} · ${run.trigger_source || '-'} · ${formatDateTime(run.created_at)}`"
              :description="runSummary(run)"
              @click="selectRun(run.id)"
            >
              <template #badge>
                <StatusBadge :value="badgeValue(run.status)" :label="run.status || '-'" />
              </template>
              <div class="mt-2 flex flex-wrap gap-2 text-xs">
                <span class="metric-chip">changed {{ Number(run.result?.changed_count || 0) }}</span>
                <span v-if="run.approval_required" class="metric-chip">approval</span>
                <span class="metric-chip">{{ run.id.slice(0, 18) }}</span>
              </div>
            </InfoCard>
            <div v-if="!runs.length && !runsQuery.isPending.value" class="surface-note">暂无 Agent 运行记录。</div>
          </div>
        </PageSection>

        <PageSection title="运行详情" subtitle="查看工具步骤、审计 id、待批准动作和错误。">
          <div v-if="!activeRun" class="surface-note">从左侧选择一个 run。</div>
          <div v-else class="space-y-4">
            <div class="rounded-[18px] border border-[var(--line)] bg-white/80 px-4 py-3">
              <div class="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <div class="text-sm font-bold text-[var(--ink)]">{{ activeRun.agent_key }}</div>
                  <div class="mt-1 text-xs text-[var(--muted)]">{{ activeRun.id }}</div>
                </div>
                <StatusBadge :value="badgeValue(activeRun.status)" :label="activeRun.status" />
              </div>
              <div class="mt-3 grid gap-2 text-sm md:grid-cols-3">
                <div class="metric-chip">trigger {{ activeRun.trigger_source || '-' }}</div>
                <div class="metric-chip">changed {{ Number(activeRun.result?.changed_count || 0) }}</div>
                <div class="metric-chip">steps {{ activeRun.steps?.length || 0 }}</div>
              </div>
            </div>

            <div v-if="activeRun.status === 'waiting_approval'" class="rounded-[18px] border border-amber-200 bg-amber-50 px-4 py-3">
              <div class="text-sm font-bold text-amber-900">审批动作</div>
              <textarea v-model="approvalReason" class="mt-2 min-h-[88px] w-full rounded-2xl border border-amber-200 bg-white px-3 py-2 text-sm" placeholder="填写批准或拒绝原因" />
              <div class="mt-2 flex flex-wrap gap-2">
                <button class="rounded-2xl bg-emerald-700 px-4 py-2 text-sm font-semibold text-white disabled:opacity-50" :disabled="approvalBusy || !approvalReason.trim()" @click="approveRun">
                  批准并执行
                </button>
                <button class="rounded-2xl bg-rose-700 px-4 py-2 text-sm font-semibold text-white disabled:opacity-50" :disabled="approvalBusy || !approvalReason.trim()" @click="rejectRun">
                  拒绝
                </button>
              </div>
            </div>

            <div class="space-y-2">
              <InfoCard
                v-for="step in activeRun.steps || []"
                :key="step.id"
                :title="`${step.step_index}. ${step.tool_name}`"
                :meta="`${step.status} · ${step.dry_run ? 'dry-run' : 'write'} · audit=${step.audit_id || '-'}`"
                :description="step.error_text || stepDescription(step)"
              >
                <template #badge>
                  <StatusBadge :value="badgeValue(step.status)" :label="step.status || '-'" />
                </template>
              </InfoCard>
            </div>

            <div class="rounded-[18px] border border-[var(--line)] bg-white/80 px-4 py-3">
              <div class="text-sm font-bold text-[var(--ink)]">结果摘要</div>
              <pre class="mt-2 max-h-[260px] overflow-auto whitespace-pre-wrap text-xs text-[var(--muted)]">{{ pretty(activeRun.result) }}</pre>
            </div>
          </div>
        </PageSection>
      </div>
    </div>
  </AppShell>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import AppShell from '../../shared/ui/AppShell.vue'
import PageSection from '../../shared/ui/PageSection.vue'
import InfoCard from '../../shared/ui/InfoCard.vue'
import StatusBadge from '../../shared/ui/StatusBadge.vue'
import { approveAgentRun, fetchAgentRun, fetchAgentRuns, rejectAgentRun, startAgentRun, type AgentRun, type AgentStep } from '../../services/api/agents'
import { formatDateTime } from '../../shared/utils/format'
import { useUiStore } from '../../stores/ui'

const queryClient = useQueryClient()
const ui = useUiStore()
const selectedAgentKey = ref('portfolio_reconcile_agent')
const selectedRunId = ref('')
const approvalReason = ref('')
const filters = reactive({ agent_key: '', status: '' })

const runsQuery = useQuery({
  queryKey: ['agent-runs', filters],
  queryFn: () => fetchAgentRuns({ agent_key: filters.agent_key, status: filters.status, limit: 80 }),
  refetchInterval: () => (document.visibilityState === 'visible' ? 30_000 : 120_000),
})

const detailQuery = useQuery({
  queryKey: ['agent-run-detail', selectedRunId],
  queryFn: () => fetchAgentRun(selectedRunId.value),
  enabled: computed(() => Boolean(selectedRunId.value)),
  refetchInterval: () => (document.visibilityState === 'visible' && selectedRunId.value ? 20_000 : false),
})

const runs = computed<AgentRun[]>(() => (Array.isArray(runsQuery.data.value?.items) ? runsQuery.data.value?.items || [] : []))
const activeRun = computed<AgentRun | null>(() => detailQuery.data.value?.run || null)
const approvalBusy = computed(() => approveMutation.isPending.value || rejectMutation.isPending.value)

const startMutation = useMutation({
  mutationFn: () => startAgentRun({ agent_key: selectedAgentKey.value, trigger_source: 'manual', actor: 'agent-ops-page', goal: {}, dedupe: false }),
  onSuccess: async (data) => {
    selectedRunId.value = data.run.id
    ui.showToast(`Agent run 已创建：${data.run.agent_key}`, 'success')
    await refreshRuns()
  },
  onError: (error: any) => ui.showToast(error?.message || '创建 Agent run 失败', 'error'),
})

const approveMutation = useMutation({
  mutationFn: () => approveAgentRun(selectedRunId.value, { reason: approvalReason.value.trim(), actor: 'agent-ops-page' }),
  onSuccess: async () => {
    approvalReason.value = ''
    ui.showToast('审批通过，已执行待写步骤。', 'success')
    await refreshRuns()
  },
  onError: (error: any) => ui.showToast(error?.message || '审批失败', 'error'),
})

const rejectMutation = useMutation({
  mutationFn: () => rejectAgentRun(selectedRunId.value, { reason: approvalReason.value.trim(), actor: 'agent-ops-page' }),
  onSuccess: async () => {
    approvalReason.value = ''
    ui.showToast('已拒绝该 Agent run。', 'success')
    await refreshRuns()
  },
  onError: (error: any) => ui.showToast(error?.message || '拒绝失败', 'error'),
})

watch(activeRun, () => {
  approvalReason.value = ''
})

function startRun() {
  startMutation.mutate()
}

function selectRun(runId: string) {
  selectedRunId.value = runId
}

async function refreshRuns() {
  await queryClient.invalidateQueries({ queryKey: ['agent-runs'] })
  if (selectedRunId.value) await queryClient.invalidateQueries({ queryKey: ['agent-run-detail'] })
}

function approveRun() {
  approveMutation.mutate()
}

function rejectRun() {
  rejectMutation.mutate()
}

function runSummary(run: AgentRun) {
  const result = run.result || {}
  const pending = Array.isArray(result.pending_write_steps) ? result.pending_write_steps.length : 0
  const warnings = Array.isArray(result.warnings) ? result.warnings.length : 0
  return `${result.closure_status || '-'} · pending=${pending} · warnings=${warnings}`
}

function stepDescription(step: AgentStep) {
  const result = step.result || {}
  if (result.error) return String(result.error)
  if (typeof result.changed_count !== 'undefined') return `changed=${result.changed_count} · skipped=${result.skipped_count || 0}`
  return JSON.stringify(step.args || {})
}

function badgeValue(status: string) {
  if (['succeeded', 'success', 'approved'].includes(status)) return 'success'
  if (['failed', 'error', 'cancelled', 'rejected'].includes(status)) return 'error'
  if (['waiting_approval', 'pending_approval', 'running', 'queued'].includes(status)) return 'warn'
  return 'muted'
}

function pretty(value: unknown) {
  try {
    return JSON.stringify(value || {}, null, 2)
  } catch {
    return String(value || '')
  }
}
</script>
