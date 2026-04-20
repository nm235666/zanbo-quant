<template>
  <AppShell title="长线配置动作" subtitle="基于宏观三周期状态的组合级动作建议：现金比例、风险敞口、防守/进攻切换。">
    <div class="space-y-4">
      <StatePanel
        v-if="pageStatus !== 'ready'"
        :tone="pageStatus === 'not_initialized' ? 'warning' : 'default'"
        :title="pageStatusTitle"
        :description="pageStatusDescription"
      >
        <template #action>
          <RouterLink
            to="/app/macro-regime"
            class="rounded-2xl border border-[var(--line)] bg-white px-4 py-2 text-sm font-semibold text-[var(--ink)] transition hover:border-[var(--brand)] hover:text-[var(--brand)]"
          >
            去看宏观状态
          </RouterLink>
        </template>
      </StatePanel>

      <!-- 当前配置摘要 -->
      <div v-if="allocation" class="kpi-grid">
        <StatCard
          title="现金比例目标"
          :value="`${allocation.cash_ratio_pct?.toFixed(0) ?? '-'}%`"
          hint="建议持有的现金占账户总值"
        />
        <StatCard
          title="单票上限"
          :value="`${allocation.max_single_position_pct?.toFixed(0) ?? '-'}%`"
          hint="单只标的最大仓位占账户总值"
        />
        <StatCard
          title="主题集中度上限"
          :value="`${allocation.max_theme_concentration_pct?.toFixed(0) ?? '-'}%`"
          hint="同一主题总暴露不超过该比例"
        />
        <StatCard
          title="配置基调"
          :value="stanceLabel(allocation.stance)"
          :hint="stanceHint(allocation.stance)"
        />
      </div>
      <div v-else-if="!allocationLoading" class="rounded-2xl border border-dashed border-[var(--line)] px-4 py-8 text-center text-sm text-[var(--muted)]">
        {{ pageStatusDescription }}
      </div>

      <!-- 冲突裁决 -->
      <div v-if="allocation?.conflict_ruling" class="rounded-2xl border border-amber-200 bg-amber-50 px-4 py-4">
        <div class="mb-1 text-xs font-semibold text-amber-700">短长线冲突裁决</div>
        <div class="text-sm text-amber-800 leading-6">{{ allocation.conflict_ruling }}</div>
      </div>

      <!-- 风险压缩 -->
      <div v-if="allocation && allocation.risk_budget_compression < 1.0" class="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-4">
        <div class="mb-1 text-xs font-semibold text-rose-700">风险预算压缩中</div>
        <div class="text-sm text-rose-800">当前风险预算压缩至 {{ ((allocation.risk_budget_compression ?? 1) * 100).toFixed(0) }}%，限制高风险操作。</div>
      </div>

      <!-- 关联宏观状态 -->
      <PageSection title="三层股池统计" subtitle="系统机会池 → 用户关注池（候选漏斗）→ 持仓池。">
        <div class="grid gap-3 sm:grid-cols-3">
          <RouterLink to="/app/signals/overview" class="group rounded-2xl border border-[var(--line)] bg-[var(--panel-soft)] px-4 py-4 transition hover:border-[var(--brand)]">
            <div class="text-xs font-semibold text-[var(--muted)] mb-1">系统机会池</div>
            <div class="text-lg font-bold text-[var(--ink)]">信号 + 评分</div>
            <div class="mt-1 text-xs text-[var(--muted)]">进入 → 查看信号与综合评分</div>
          </RouterLink>
          <RouterLink to="/app/funnel" class="group rounded-2xl border border-[var(--line)] bg-[var(--panel-soft)] px-4 py-4 transition hover:border-[var(--brand)]">
            <div class="text-xs font-semibold text-[var(--muted)] mb-1">用户关注池</div>
            <div class="text-lg font-bold text-[var(--ink)]">候选漏斗</div>
            <div class="mt-1 text-xs text-[var(--muted)]">进入 → 管理研究候选池</div>
          </RouterLink>
          <RouterLink to="/app/positions" class="group rounded-2xl border border-[var(--line)] bg-[var(--panel-soft)] px-4 py-4 transition hover:border-[var(--brand)]">
            <div class="text-xs font-semibold text-[var(--muted)] mb-1">持仓池</div>
            <div class="text-lg font-bold text-[var(--ink)]">当前持仓</div>
            <div class="mt-1 text-xs text-[var(--muted)]">进入 → 查看持仓与仓位结构</div>
          </RouterLink>
        </div>
      </PageSection>

      <!-- 手动设置配置 -->
      <PageSection title="手动设置配置目标" subtitle="记录当前配置策略决策。">
        <div class="space-y-4">
          <div class="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
            <label class="text-sm font-semibold text-[var(--ink)]">
              配置基调
              <select v-model="form.stance" class="mt-1 w-full rounded-2xl border border-[var(--line)] bg-white px-4 py-3 text-sm">
                <option value="offensive">进攻</option>
                <option value="neutral">中性</option>
                <option value="defensive">防守</option>
              </select>
            </label>
            <label class="text-sm font-semibold text-[var(--ink)]">
              现金比例目标（%）
              <input v-model.number="form.cash_ratio_pct" type="number" min="0" max="100" step="1"
                class="mt-1 w-full rounded-2xl border border-[var(--line)] bg-white px-4 py-3 text-sm" placeholder="如 10" />
            </label>
            <label class="text-sm font-semibold text-[var(--ink)]">
              单票仓位上限（%）
              <input v-model.number="form.max_single_position_pct" type="number" min="0" max="100" step="1"
                class="mt-1 w-full rounded-2xl border border-[var(--line)] bg-white px-4 py-3 text-sm" placeholder="如 8" />
            </label>
            <label class="text-sm font-semibold text-[var(--ink)]">
              主题集中度上限（%）
              <input v-model.number="form.max_theme_concentration_pct" type="number" min="0" max="100" step="1"
                class="mt-1 w-full rounded-2xl border border-[var(--line)] bg-white px-4 py-3 text-sm" placeholder="如 20" />
            </label>
          </div>
          <label class="text-sm font-semibold text-[var(--ink)]">
            风险预算压缩比例（0.0-1.0）
            <input v-model.number="form.risk_budget_compression" type="number" min="0" max="1" step="0.1"
              class="mt-1 w-full max-w-xs rounded-2xl border border-[var(--line)] bg-white px-4 py-3 text-sm" placeholder="如 1.0（不压缩）" />
          </label>
          <label class="text-sm font-semibold text-[var(--ink)]">
            决策备注
            <textarea v-model="form.action_notes" rows="2"
              class="mt-1 w-full rounded-2xl border border-[var(--line)] bg-white px-4 py-3 text-sm"
              placeholder="记录本次配置调整的原因与依据..." />
          </label>
          <div v-if="submitError" class="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{{ submitError }}</div>
          <div v-if="submitSuccess" class="rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">配置决策已记录。</div>
          <button
            class="rounded-2xl bg-[var(--brand)] px-5 py-2.5 text-sm font-semibold text-white disabled:opacity-60"
            :disabled="submitPending"
            @click="submitAllocation"
          >
            {{ submitPending ? '提交中...' : '记录配置决策' }}
          </button>
        </div>
      </PageSection>

      <!-- 历史记录 -->
      <PageSection :title="`配置历史 (${historyTotal})`" subtitle="历次配置目标变更记录。">
        <div v-if="historyLoading" class="py-6 text-center text-sm text-[var(--muted)]">加载中...</div>
        <div v-else-if="!historyItems.length" class="py-6 text-center text-sm text-[var(--muted)]">{{ historyEmptyText }}</div>
        <div v-else class="divide-y divide-[var(--line)]">
          <div v-for="item in historyItems" :key="item.id" class="py-4">
            <div class="flex flex-wrap items-start justify-between gap-2">
              <div class="flex flex-wrap items-center gap-2">
                <span :class="stanceBadgeClass(item.stance)">{{ stanceLabel(item.stance) }}</span>
                <span class="text-xs text-[var(--muted)]">现金 {{ item.cash_ratio_pct?.toFixed(0) }}% · 单票 {{ item.max_single_position_pct?.toFixed(0) }}% · 主题 {{ item.max_theme_concentration_pct?.toFixed(0) }}%</span>
              </div>
              <div class="text-xs text-[var(--muted)]">{{ formatDate(item.created_at) }}</div>
            </div>
            <div v-if="item.action_notes" class="mt-1 text-xs text-[var(--muted)]">{{ item.action_notes }}</div>
            <div v-if="item.conflict_ruling" class="mt-1 text-xs text-amber-600">裁决: {{ item.conflict_ruling }}</div>
          </div>
        </div>
      </PageSection>
    </div>
  </AppShell>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { useQuery, useQueryClient } from '@tanstack/vue-query'
import { RouterLink } from 'vue-router'
import AppShell from '../../shared/ui/AppShell.vue'
import PageSection from '../../shared/ui/PageSection.vue'
import StatCard from '../../shared/ui/StatCard.vue'
import StatePanel from '../../shared/ui/StatePanel.vue'
import {
  fetchLatestAllocation,
  fetchAllocationHistory,
  recordAllocation,
  STANCE_LABELS,
  type PortfolioAllocation,
} from '../../services/api/portfolio_allocation'

const queryClient = useQueryClient()

const { data: latestData, isPending: allocationLoading } = useQuery({
  queryKey: ['portfolio-allocation-latest'],
  queryFn: fetchLatestAllocation,
})

const { data: historyData, isPending: historyLoading } = useQuery({
  queryKey: ['portfolio-allocation-history'],
  queryFn: () => fetchAllocationHistory({ page: 1, page_size: 20 }),
})

const allocation = computed<PortfolioAllocation | null>(() => latestData.value?.allocation ?? null)
const historyItems = computed(() => historyData.value?.items ?? [])
const historyTotal = computed(() => historyData.value?.total ?? 0)
const pageStatus = computed(() => String((latestData.value as any)?.status || '').trim() || 'empty')
const statusReason = computed(() => String((latestData.value as any)?.status_reason || '').trim())
const missingInputs = computed<string[]>(() => {
  const raw = (latestData.value as any)?.missing_inputs
  return Array.isArray(raw) ? raw : []
})
const pageStatusTitle = computed(() => {
  if (pageStatus.value === 'not_initialized') return '长线配置动作尚未初始化'
  if (pageStatus.value === 'insufficient_evidence') return '长线配置动作证据不足'
  if (pageStatus.value === 'error') return '长线配置动作生成失败'
  return '长线配置动作暂未就绪'
})
const pageStatusDescription = computed(() => {
  if (statusReason.value) return statusReason.value
  if (pageStatus.value === 'not_initialized') return '当前没有可用的宏观状态或历史配置基础，因此系统无法自动生成现金比例、单票上限和主题集中度建议。你仍可以先手动记录当前配置口径。'
  if (pageStatus.value === 'insufficient_evidence') {
    const missing = missingInputs.value.length ? `缺失输入：${missingInputs.value.join('、')}。` : ''
    return `${missing}系统已拿到部分输入，但还不足以形成稳定的组合动作，建议先确认宏观三周期状态。`
  }
  return '当前没有可展示的配置结果。'
})
const historyEmptyText = computed(() => {
  if (pageStatus.value === 'not_initialized') return '暂无配置历史，因为系统还没有生成或确认过可追踪的组合动作。'
  if (pageStatus.value === 'insufficient_evidence') return '暂无配置历史，当前仍缺少形成配置动作的关键输入。'
  return '暂无记录'
})

function stanceLabel(stance?: string): string {
  return stance ? (STANCE_LABELS[stance] ?? stance) : '-'
}

function stanceHint(stance?: string): string {
  const map: Record<string, string> = {
    offensive: '积极增加风险敞口',
    defensive: '降低风险暴露，提高现金',
    neutral: '维持当前组合结构',
  }
  return stance ? (map[stance] ?? '') : ''
}

function stanceBadgeClass(stance?: string): string {
  const base = 'inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-semibold'
  const map: Record<string, string> = {
    offensive: 'border-emerald-200 bg-emerald-100 text-emerald-700',
    defensive: 'border-rose-200 bg-rose-100 text-rose-700',
    neutral: 'border-sky-200 bg-sky-100 text-sky-700',
  }
  return `${base} ${map[stance ?? ''] ?? 'border-[var(--line)] bg-stone-100 text-stone-600'}`
}

function formatDate(s?: string): string {
  if (!s) return '-'
  try { return new Date(s).toLocaleDateString('zh-CN') } catch { return s }
}

const form = reactive({
  stance: 'neutral',
  cash_ratio_pct: 10,
  max_single_position_pct: 8,
  max_theme_concentration_pct: 20,
  risk_budget_compression: 1.0,
  action_notes: '',
})

const submitPending = ref(false)
const submitError = ref('')
const submitSuccess = ref(false)

async function submitAllocation() {
  submitPending.value = true
  submitError.value = ''
  submitSuccess.value = false
  try {
    const result = await recordAllocation({ ...form })
    if (!result.ok) throw new Error(result.error || '提交失败')
    submitSuccess.value = true
    await queryClient.invalidateQueries({ queryKey: ['portfolio-allocation-latest'] })
    await queryClient.invalidateQueries({ queryKey: ['portfolio-allocation-history'] })
  } catch (e: any) {
    submitError.value = e?.message || '提交失败'
  } finally {
    submitPending.value = false
  }
}
</script>
