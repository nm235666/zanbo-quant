<template>
  <AppShell title="投研决策板" subtitle="宏观-行业-个股评分、短名单、交易计划与验证结果统一闭环。">
    <div class="space-y-4">
      <PageSection title="决策输入" subtitle="输入单票聚焦代码，或直接刷新全局决策板。">
        <div class="grid gap-3 xl:grid-cols-[1fr_180px_180px_180px] md:grid-cols-2">
          <input v-model.trim="focusTsCode" class="rounded-2xl border border-[var(--line)] bg-white px-4 py-3" placeholder="聚焦股票，如 000001.SZ" @keydown.enter="applyFilters" />
          <select v-model.number="pageSize" class="rounded-2xl border border-[var(--line)] bg-white px-4 py-3">
            <option :value="8">8 / 页</option>
            <option :value="12">12 / 页</option>
            <option :value="20">20 / 页</option>
          </select>
          <input v-model.trim="killReasonDraft" class="rounded-2xl border border-[var(--line)] bg-white px-4 py-3" placeholder="Kill Switch 备注" />
          <div class="flex flex-wrap gap-2">
            <button class="rounded-2xl bg-[var(--brand)] px-4 py-3 font-semibold text-white disabled:opacity-60" :disabled="isBoardFetching" @click="applyFilters">
              {{ isBoardFetching ? '刷新中...' : '刷新决策板' }}
            </button>
            <button class="rounded-2xl border border-[var(--line)] bg-white px-4 py-3 font-semibold text-[var(--ink)] disabled:opacity-60" :disabled="isSnapshotPending" @click="runSnapshot">
              {{ isSnapshotPending ? '生成中...' : '生成快照' }}
            </button>
            <RouterLink to="/research/trade-plan" class="rounded-2xl border border-[var(--line)] bg-white px-4 py-3 font-semibold text-[var(--ink)]">
              打开交易计划书
            </RouterLink>
          </div>
        </div>
        <div class="mt-3 flex flex-wrap gap-2">
          <StatusBadge :value="killSwitchTone" :label="killSwitchLabel" />
          <StatusBadge :value="marketRegime.mode || 'muted'" :label="marketRegime.label || '数据不足'" />
          <StatusBadge value="info" :label="`短名单 ${shortlist.length}`" />
          <StatusBadge value="muted" :label="`行业 ${industries.length}`" />
        </div>
        <div v-if="message" class="mt-3 rounded-[18px] border border-[var(--line)] bg-[rgba(255,255,255,0.72)] px-4 py-3 text-sm text-[var(--muted)]">
          {{ message }}
        </div>
        <div v-if="boardErrorText" class="mt-3 rounded-[18px] border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {{ boardErrorText }}
        </div>
      </PageSection>

      <div class="grid gap-4 lg:grid-cols-4 md:grid-cols-2">
        <StatCard title="市场模式" :value="marketRegime.label || '数据不足'" :hint="`评分 ${formatNumber(marketRegime.score, 1)}`" />
        <StatCard title="短名单" :value="String(shortlist.length || 0)" :hint="`最新评分日期 ${snapshotDate || '-'}`" />
        <StatCard title="行业数" :value="String(industries.length || 0)" :hint="`Top 行业 ${topIndustryName || '-'}`" />
        <StatCard title="验证层" :value="validation.status || 'idle'" :hint="`done ${validation.done ?? 0} · error ${validation.error ?? 0}`" />
      </div>

      <div class="grid gap-4 xl:grid-cols-[1.2fr_0.8fr]">
        <PageSection title="市场模式与交易计划" subtitle="把宏观评分直接转成仓位语言与执行提醒。">
          <div class="grid gap-3 md:grid-cols-2">
            <InfoCard :title="marketRegime.label || '数据不足'" :meta="`分数 ${formatNumber(marketRegime.score, 1)} · 模式 ${marketRegime.mode || '-'}`" :description="marketRegime.summary || '暂无市场模式摘要。'">
              <div class="mt-3 flex flex-wrap gap-2 text-xs">
                <span v-for="item in marketRegime.factors || []" :key="item" class="metric-chip">{{ item }}</span>
              </div>
            </InfoCard>
            <InfoCard :title="tradePlan.headline || '交易计划'" :meta="`底仓 ${tradePlan.base_position ?? 0}% · 浮动仓 ${tradePlan.floating_position ?? 0}% · 预备仓 ${tradePlan.reserve_position ?? 0}%`" :description="tradePlan.mode || '-'">
              <div class="mt-3 space-y-2 text-sm text-[var(--muted)]">
                <div v-for="item in tradePlan.actions || []" :key="item">{{ item }}</div>
              </div>
            </InfoCard>
          </div>
          <div v-if="focusStock" class="mt-3">
            <InfoCard :title="focusStock.name || focusStock.ts_code || '聚焦股票'" :meta="focusStock.ts_code || '-'" :description="focusStock.reason || focusStock.trade_plan?.suggestion || ''">
              <template #badge>
                <StatusBadge :value="focusStock.score?.position_label || 'muted'" :label="focusStock.score?.position_label || '-'"/>
              </template>
              <div class="mt-3 flex flex-wrap gap-2">
                <StatusBadge value="brand" :label="`总分 ${formatNumber(focusStock.score?.total_score, 1)}`" />
                <StatusBadge value="info" :label="`行业分 ${formatNumber(focusStock.score?.industry_total_score, 1)}`" />
                <StatusBadge value="muted" :label="focusStock.risk || '暂无风险提示'" />
              </div>
              <div class="mt-3 flex flex-wrap gap-2">
                <RouterLink
                  v-if="focusStock.ts_code"
                  :to="`/stocks/detail/${focusStock.ts_code}`"
                  class="rounded-full border border-[var(--line)] bg-white px-3 py-2 text-xs font-semibold text-[var(--ink)] transition hover:border-[var(--brand)] hover:text-[var(--brand)]"
                >
                  打开股票详情
                </RouterLink>
              </div>
            </InfoCard>
          </div>
        </PageSection>

        <PageSection title="Kill Switch 与验证层" subtitle="人工确认、快照和验证结果放在一起，便于收口。">
          <InfoCard :title="killSwitchLabel" :meta="killSwitch.updated_at || '-'" :description="killSwitch.reason || '暂无备注'">
            <template #badge>
              <StatusBadge :value="killSwitchTone" :label="killSwitchLabel" />
            </template>
            <div class="mt-3 flex flex-wrap gap-2">
              <button class="rounded-full bg-red-700 px-3 py-2 text-xs font-semibold text-white disabled:opacity-60" :disabled="isTogglePending" @click="pauseTrading">
                {{ isTogglePending ? '切换中...' : '暂停交易' }}
              </button>
              <button class="rounded-full bg-emerald-700 px-3 py-2 text-xs font-semibold text-white disabled:opacity-60" :disabled="isTogglePending" @click="resumeTrading">
                {{ isTogglePending ? '切换中...' : '恢复交易' }}
              </button>
            </div>
          </InfoCard>

          <InfoCard class="mt-3" title="验证层概览" :meta="validation.source || '-'" :description="validation.summary || '暂无验证数据'">
            <template #badge>
              <StatusBadge :value="validation.status || 'muted'" :label="validation.status || '-'" />
            </template>
            <div class="mt-3 flex flex-wrap gap-2 text-xs">
              <span class="metric-chip">done <strong>{{ validation.done ?? 0 }}</strong></span>
              <span class="metric-chip">error <strong>{{ validation.error ?? 0 }}</strong></span>
            </div>
            <div v-if="validation.latest" class="mt-3 rounded-[18px] border border-[var(--line)] bg-white/80 px-3 py-3 text-sm text-[var(--muted)]">
              <div class="font-semibold text-[var(--ink)]">{{ validation.latest.task_id || '-' }}</div>
              <div class="mt-1">{{ validation.latest.task_type || '-' }} · {{ validation.latest.status || '-' }}</div>
              <div class="mt-1">{{ validation.latest.error_message || validation.latest.error_code || '暂无错误' }}</div>
            </div>
          </InfoCard>
        </PageSection>
      </div>

      <div class="grid gap-4 xl:grid-cols-[0.95fr_1.05fr]">
        <PageSection title="行业排序" subtitle="按最新行业评分从高到低排列。">
          <DataTable :columns="industryColumns" :rows="industries" row-key="industry" empty-text="暂无行业评分数据" caption="行业排序">
            <template #cell-score="{ row }">{{ formatNumber(row.score, 2) }}</template>
            <template #cell-top_stocks="{ row }">
              <div class="space-y-1">
                <div v-for="stock in row.top_stocks || []" :key="stock.ts_code" class="text-xs text-[var(--muted)]">
                  {{ stock.name || stock.ts_code || '-' }} · {{ formatNumber(stock.score, 1) }}
                </div>
              </div>
            </template>
          </DataTable>
        </PageSection>

        <PageSection title="股票短名单" subtitle="先看高分样本，再决定要不要下钻股票详情。">
          <DataTable :columns="stockColumns" :rows="shortlist" row-key="ts_code" empty-text="暂无短名单股票" caption="股票短名单">
            <template #cell-ts_code="{ row }">
              <RouterLink :to="`/stocks/detail/${row.ts_code}`" class="font-semibold text-[var(--brand)] hover:underline">
                {{ row.name || row.ts_code || '-' }}
              </RouterLink>
              <div class="mt-1 text-xs text-[var(--muted)]">{{ row.ts_code || '-' }}</div>
            </template>
            <template #cell-total_score="{ row }">{{ formatNumber(row.total_score, 2) }}</template>
            <template #cell-industry_total_score="{ row }">{{ formatNumber(row.industry_total_score, 2) }}</template>
            <template #cell-position_label="{ row }"><StatusBadge :value="row.position_label || 'muted'" :label="row.position_label || '-'"/></template>
            <template #cell_actions="{ row }">
              <div class="flex flex-wrap gap-2">
                <RouterLink :to="`/stocks/detail/${row.ts_code}`" class="rounded-full border border-[var(--line)] bg-white px-3 py-2 text-xs font-semibold text-[var(--ink)] transition hover:border-[var(--brand)] hover:text-[var(--brand)]">
                  股票详情
                </RouterLink>
                <button class="rounded-full border border-[var(--line)] bg-white px-3 py-2 text-xs font-semibold text-[var(--ink)] transition hover:border-[var(--brand)] hover:text-[var(--brand)] disabled:opacity-60" :disabled="isActionPending" @click="submitManualAction('confirm', row.ts_code, `短名单确认：${row.name || row.ts_code || '-'}`, row.name || row.ts_code || '')">
                  确认
                </button>
                <button class="rounded-full border border-[var(--line)] bg-white px-3 py-2 text-xs font-semibold text-[var(--ink)] transition hover:border-[var(--brand)] hover:text-[var(--brand)] disabled:opacity-60" :disabled="isActionPending" @click="submitManualAction('defer', row.ts_code, `短名单暂缓：${row.name || row.ts_code || '-'}`, row.name || row.ts_code || '')">
                  暂缓
                </button>
                <button class="rounded-full border border-[var(--line)] bg-white px-3 py-2 text-xs font-semibold text-[var(--ink)] transition hover:border-[var(--brand)] hover:text-[var(--brand)] disabled:opacity-60" :disabled="isActionPending" @click="submitManualAction('reject', row.ts_code, `短名单拒绝：${row.name || row.ts_code || '-'}`, row.name || row.ts_code || '')">
                  拒绝
                </button>
              </div>
            </template>
          </DataTable>
        </PageSection>
      </div>

      <PageSection title="决策快照历史" subtitle="每日快照沉淀，方便回看决策板状态。">
        <DataTable :columns="historyColumns" :rows="historyItems" row-key="id" empty-text="暂无快照历史" caption="决策快照历史">
          <template #cell-snapshot_date="{ row }">{{ row.snapshot_date || '-' }}</template>
          <template #cell-snapshot_type="{ row }">{{ row.snapshot_type || '-' }}</template>
          <template #cell-created_at="{ row }">{{ row.created_at || '-' }}</template>
          <template #cell-summary="{ row }">{{ row.payload?.summary ? `行业 ${row.payload.summary.industry_count || 0} / 短名单 ${row.payload.summary.shortlist_size || 0}` : '-' }}</template>
        </DataTable>
      </PageSection>

      <PageSection title="人工确认记录" subtitle="对短名单标的做确认、暂缓、拒绝和观察留痕，方便回看。">
        <div class="grid gap-3 xl:grid-cols-[1fr_1fr_160px] md:grid-cols-2">
          <input v-model.trim="actionTsCodeDraft" class="rounded-2xl border border-[var(--line)] bg-white px-4 py-3" placeholder="动作股票代码，如 000001.SZ" />
          <input v-model.trim="actionNoteDraft" class="rounded-2xl border border-[var(--line)] bg-white px-4 py-3" placeholder="动作备注" />
          <button class="rounded-2xl bg-[var(--brand)] px-4 py-3 font-semibold text-white disabled:opacity-60" :disabled="isActionPending || !actionTsCodeDraft.trim()" @click="submitManualAction('review', actionTsCodeDraft, actionNoteDraft, actionTsCodeDraft)">
            {{ isActionPending ? '记录中...' : '记录确认' }}
          </button>
        </div>
        <div class="mt-3 flex flex-wrap gap-2 text-xs">
          <button class="rounded-full border border-[var(--line)] bg-white px-3 py-2 font-semibold text-[var(--ink)] disabled:opacity-60" :disabled="isActionPending || !actionTsCodeDraft.trim()" @click="submitManualAction('confirm', actionTsCodeDraft, actionNoteDraft, actionTsCodeDraft)">
            确认
          </button>
          <button class="rounded-full border border-[var(--line)] bg-white px-3 py-2 font-semibold text-[var(--ink)] disabled:opacity-60" :disabled="isActionPending || !actionTsCodeDraft.trim()" @click="submitManualAction('defer', actionTsCodeDraft, actionNoteDraft, actionTsCodeDraft)">
            暂缓
          </button>
          <button class="rounded-full border border-[var(--line)] bg-white px-3 py-2 font-semibold text-[var(--ink)] disabled:opacity-60" :disabled="isActionPending || !actionTsCodeDraft.trim()" @click="submitManualAction('reject', actionTsCodeDraft, actionNoteDraft, actionTsCodeDraft)">
            拒绝
          </button>
          <button class="rounded-full border border-[var(--line)] bg-white px-3 py-2 font-semibold text-[var(--ink)] disabled:opacity-60" :disabled="isActionPending || !actionTsCodeDraft.trim()" @click="submitManualAction('watch', actionTsCodeDraft, actionNoteDraft, actionTsCodeDraft)">
            观察
          </button>
        </div>
        <div v-if="recentActions.length" class="mt-4 space-y-2">
          <InfoCard
            v-for="item in recentActions"
            :key="item.id"
            :title="joinActionTitle(item)"
            :meta="joinActionMeta(item)"
            :description="item.note || item.payload?.context?.reason || '暂无备注'"
          >
            <template #badge>
              <StatusBadge :value="item.action_type || 'muted'" :label="item.action_type || '-'" />
            </template>
          </InfoCard>
        </div>
        <div v-else class="rounded-[18px] border border-[var(--line)] bg-white/80 px-4 py-3 text-sm text-[var(--muted)]">
          暂无人工确认记录。
        </div>
      </PageSection>
    </div>
  </AppShell>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useMutation, useQuery } from '@tanstack/vue-query'
import { RouterLink } from 'vue-router'
import AppShell from '../../shared/ui/AppShell.vue'
import PageSection from '../../shared/ui/PageSection.vue'
import DataTable from '../../shared/ui/DataTable.vue'
import InfoCard from '../../shared/ui/InfoCard.vue'
import StatCard from '../../shared/ui/StatCard.vue'
import StatusBadge from '../../shared/ui/StatusBadge.vue'
import { fetchDecisionActions, fetchDecisionBoard, fetchDecisionHistory, recordDecisionAction, runDecisionSnapshot, setDecisionKillSwitch } from '../../services/api/decision'
import { formatNumber } from '../../shared/utils/format'

const focusTsCode = ref('')
const pageSize = ref(12)
const killReasonDraft = ref('手动切换')
const actionTsCodeDraft = ref('000001.SZ')
const actionNoteDraft = ref('已确认')
const message = ref('')

const boardQuery = useQuery({
  queryKey: computed(() => ['decision-board', focusTsCode.value, pageSize.value]),
  queryFn: () => fetchDecisionBoard({ ts_code: focusTsCode.value, page: 1, page_size: pageSize.value }),
  refetchInterval: 30_000,
})

const historyQuery = useQuery({
  queryKey: ['decision-history'],
  queryFn: () => fetchDecisionHistory({ page: 1, page_size: 10 }),
  refetchInterval: 60_000,
})

const actionsQuery = useQuery({
  queryKey: computed(() => ['decision-actions', focusTsCode.value]),
  queryFn: () => fetchDecisionActions({ page: 1, page_size: 10, ts_code: focusTsCode.value }),
  refetchInterval: 60_000,
})

const toggleKillSwitchMutation = useMutation({
  mutationFn: (allowTrading: boolean) => setDecisionKillSwitch({ allow_trading: allowTrading, reason: killReasonDraft.value }),
  onSuccess: async () => {
    message.value = 'Kill Switch 状态已更新。'
    await refreshAll()
  },
  onError: (error: Error) => {
    message.value = `Kill Switch 切换失败：${error.message}`
  },
})

const runSnapshotMutation = useMutation({
  mutationFn: () => runDecisionSnapshot(),
  onSuccess: async () => {
    message.value = '决策快照已生成。'
    await refreshAll()
  },
  onError: (error: Error) => {
    message.value = `快照生成失败：${error.message}`
  },
})

const actionMutation = useMutation({
  mutationFn: (payload: { action_type: 'confirm' | 'reject' | 'defer' | 'watch' | 'review'; ts_code: string; stock_name?: string; note?: string }) =>
    recordDecisionAction({
      action_type: payload.action_type,
      ts_code: payload.ts_code,
      stock_name: payload.stock_name || '',
      note: payload.note || '',
      snapshot_date: snapshotDate.value,
      context: {
        source: 'decision_board',
        market_mode: marketRegime.value.mode || '',
        trade_plan: tradePlan.value.mode || '',
      },
    }),
  onSuccess: async () => {
    message.value = '人工确认记录已保存。'
    await refreshAll()
  },
  onError: (error: Error) => {
    message.value = `人工确认记录失败：${error.message}`
  },
})

const board = computed<Record<string, any>>(() => (boardQuery.data.value || {}) as Record<string, any>)
const isBoardFetching = computed(() => Boolean(boardQuery.isFetching.value))
const boardErrorText = computed(() => {
  const value = boardQuery.error.value
  if (!value) return ''
  return value instanceof Error ? value.message : String(value)
})
const marketRegime = computed<Record<string, any>>(() => (board.value.market_regime || {}) as Record<string, any>)
const industries = computed<Array<Record<string, any>>>(() => (board.value.industries || []) as Array<Record<string, any>>)
const shortlist = computed<Array<Record<string, any>>>(() => (board.value.shortlist || []) as Array<Record<string, any>>)
const tradePlan = computed<Record<string, any>>(() => (board.value.trade_plan || {}) as Record<string, any>)
const validation = computed<Record<string, any>>(() => (board.value.validation || {}) as Record<string, any>)
const focusStock = computed<Record<string, any> | null>(() => (board.value.focus_stock || null) as Record<string, any> | null)
const killSwitch = computed<Record<string, any>>(() => (board.value.kill_switch || {}) as Record<string, any>)
const historyItems = computed<Array<Record<string, any>>>(() => (historyQuery.data.value?.items || []) as Array<Record<string, any>>)
const recentActions = computed<Array<Record<string, any>>>(() => (actionsQuery.data.value?.items || []) as Array<Record<string, any>>)
const snapshotDate = computed(() => String(board.value.snapshot_date || '').trim())
const topIndustryName = computed(() => String(industries.value[0]?.industry || '').trim())
const killSwitchLabel = computed(() => (Number(killSwitch.value.allow_trading ?? 1) === 1 ? '交易允许' : '交易暂停'))
const killSwitchTone = computed(() => (Number(killSwitch.value.allow_trading ?? 1) === 1 ? 'success' : 'danger'))
const isTogglePending = computed(() => Boolean(toggleKillSwitchMutation.isPending.value))
const isSnapshotPending = computed(() => Boolean(runSnapshotMutation.isPending.value))
const isActionPending = computed(() => Boolean(actionMutation.isPending.value))

const industryColumns = [
  { key: 'industry', label: '行业' },
  { key: 'score', label: '评分' },
  { key: 'count', label: '样本' },
  { key: 'top_stocks', label: '代表股' },
]

const stockColumns = [
  { key: 'ts_code', label: '股票' },
  { key: 'total_score', label: '总分' },
  { key: 'industry_total_score', label: '行业分' },
  { key: 'position_label', label: '位置' },
  { key: 'decision_risk', label: '风险' },
  { key: 'actions', label: '动作' },
]

const historyColumns = [
  { key: 'snapshot_date', label: '快照日期' },
  { key: 'snapshot_type', label: '类型' },
  { key: 'summary', label: '摘要' },
  { key: 'created_at', label: '创建时间' },
]

async function refreshAll() {
  await Promise.all([boardQuery.refetch(), historyQuery.refetch(), actionsQuery.refetch()])
}

function applyFilters() {
  refreshAll()
}

function runSnapshot() {
  runSnapshotMutation.mutate()
}

function submitManualAction(actionType: 'confirm' | 'reject' | 'defer' | 'watch' | 'review', tsCode: string, note: string, stockName = '') {
  const normalizedTsCode = String(tsCode || '').trim().toUpperCase()
  if (!normalizedTsCode) return
  actionTsCodeDraft.value = normalizedTsCode
  if (String(note || '').trim()) actionNoteDraft.value = String(note || '').trim()
  actionMutation.mutate({
    action_type: actionType,
    ts_code: normalizedTsCode,
    note: String(note || actionNoteDraft.value || '').trim(),
    stock_name: String(stockName || normalizedTsCode).trim(),
  })
}

function pauseTrading() {
  toggleKillSwitchMutation.mutate(false)
}

function resumeTrading() {
  toggleKillSwitchMutation.mutate(true)
}

function joinActionTitle(item: Record<string, any>) {
  return `${item.stock_name || item.ts_code || '-'} · ${String(item.action_type || '-').toUpperCase()}`
}

function joinActionMeta(item: Record<string, any>) {
  return [item.ts_code || '-', item.actor || '-', item.created_at || '-'].filter(Boolean).join(' · ')
}
</script>
