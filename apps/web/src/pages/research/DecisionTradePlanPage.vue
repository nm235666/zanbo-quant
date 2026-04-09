<template>
  <AppShell title="每日交易计划书" subtitle="把市场模式、仓位建议、执行清单和重点候选压成一页可执行计划。">
    <div class="space-y-4">
      <PageSection title="计划输入" subtitle="输入聚焦股票或直接刷新今日计划。">
        <div class="grid gap-3 xl:grid-cols-[1fr_180px_180px_180px] md:grid-cols-2">
          <input v-model.trim="focusTsCode" class="rounded-2xl border border-[var(--line)] bg-white px-4 py-3" placeholder="聚焦股票，如 000001.SZ" @keydown.enter="refreshPlan" />
          <select v-model.number="pageSize" class="rounded-2xl border border-[var(--line)] bg-white px-4 py-3">
            <option :value="8">8 / 页</option>
            <option :value="12">12 / 页</option>
            <option :value="20">20 / 页</option>
          </select>
          <input v-model.trim="noteDraft" class="rounded-2xl border border-[var(--line)] bg-white px-4 py-3" placeholder="计划备注" />
          <div class="flex flex-wrap gap-2">
            <button class="rounded-2xl bg-[var(--brand)] px-4 py-3 font-semibold text-white disabled:opacity-60" :disabled="isFetching" @click="refreshPlan">
              {{ isFetching ? '刷新中...' : '刷新计划书' }}
            </button>
            <RouterLink to="/research/decision" class="rounded-2xl border border-[var(--line)] bg-white px-4 py-3 font-semibold text-[var(--ink)]">
              返回决策板
            </RouterLink>
          </div>
        </div>
        <div class="mt-3 flex flex-wrap gap-2">
          <StatusBadge :value="planModeTone" :label="planModeLabel" />
          <StatusBadge value="info" :label="`候选 ${priorityStocks.length}`" />
          <StatusBadge value="muted" :label="`行业 ${priorityIndustries.length}`" />
          <StatusBadge value="brand" :label="`快照 ${snapshotDate || '-'}`" />
        </div>
        <div v-if="message" class="mt-3 rounded-[18px] border border-[var(--line)] bg-[rgba(255,255,255,0.72)] px-4 py-3 text-sm text-[var(--muted)]">
          {{ message }}
        </div>
        <div v-if="planErrorText" class="mt-3 rounded-[18px] border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {{ planErrorText }}
        </div>
      </PageSection>

      <div class="grid gap-4 lg:grid-cols-4 md:grid-cols-2">
        <StatCard title="计划模式" :value="planModeLabel" :hint="`标题 ${plan.title || '-'}`" />
        <StatCard title="底仓" :value="`${positionPlan.base_position ?? 0}%`" :hint="`浮动仓 ${positionPlan.floating_position ?? 0}%`" />
        <StatCard title="预备仓" :value="`${positionPlan.reserve_position ?? 0}%`" :hint="`验证 ${validation.status || 'idle'}`" />
        <StatCard title="杀开关" :value="killSwitchLabel" :hint="killSwitch.updated_at || '-'" />
      </div>

      <div class="grid gap-4 xl:grid-cols-[1.1fr_0.9fr]">
        <PageSection title="今日计划" subtitle="以市场模式为中心，把交易计划压缩成可读语言。">
          <div class="grid gap-3 md:grid-cols-2">
            <InfoCard :title="plan.title || '每日交易计划书'" :meta="plan.summary || '暂无摘要'" :description="planDescription">
              <template #badge>
                <StatusBadge :value="planModeTone" :label="planModeLabel" />
              </template>
              <div class="mt-3 flex flex-wrap gap-2 text-xs">
                <span class="metric-chip">底仓 <strong>{{ positionPlan.base_position ?? 0 }}%</strong></span>
                <span class="metric-chip">浮动仓 <strong>{{ positionPlan.floating_position ?? 0 }}%</strong></span>
                <span class="metric-chip">预备仓 <strong>{{ positionPlan.reserve_position ?? 0 }}%</strong></span>
              </div>
              <div class="mt-3 flex flex-wrap gap-2">
                <RouterLink to="/research/decision" class="rounded-full border border-[var(--line)] bg-white px-3 py-2 text-xs font-semibold text-[var(--ink)] transition hover:border-[var(--brand)] hover:text-[var(--brand)]">
                  打开决策板
                </RouterLink>
              </div>
            </InfoCard>
            <InfoCard :title="focusTitle" :meta="focusMeta" :description="plan.focus_reason || '暂未指定聚焦标的'">
              <template #badge>
                <StatusBadge value="info" :label="focusTitle" />
              </template>
              <div class="mt-3 flex flex-wrap gap-2 text-xs">
                <span class="metric-chip">关键词 <strong>{{ focusKeyword || '-' }}</strong></span>
                <span class="metric-chip">来源 <strong>{{ plan.focus_stock?.keyword ? '单票聚焦' : '全局计划' }}</strong></span>
              </div>
            </InfoCard>
          </div>
        </PageSection>

        <PageSection title="执行清单" subtitle="把今天该做什么、不要做什么、先核对什么清晰列出来。">
          <InfoCard title="先做什么" :description="joinLines(plan.do_now)">
            <template #badge><StatusBadge value="success" label="Do Now" /></template>
          </InfoCard>
          <InfoCard class="mt-3" title="不要做什么" :description="joinLines(plan.do_not)">
            <template #badge><StatusBadge value="danger" label="Do Not" /></template>
          </InfoCard>
          <InfoCard class="mt-3" title="核对清单" :description="joinLines(plan.checklist)">
            <template #badge><StatusBadge value="muted" label="Checklist" /></template>
          </InfoCard>
          <InfoCard class="mt-3" title="审批流" :meta="approvalFlow.state_label || '-'" :description="approvalFlow.summary || '暂无审批信息'">
            <template #badge>
              <StatusBadge :value="approvalTone" :label="approvalFlow.state_label || '-'" />
            </template>
            <div class="mt-3 flex flex-wrap gap-2 text-xs">
              <span class="metric-chip">范围 <strong>{{ approvalFlow.scope === 'single' ? '单票' : '全局' }}</strong></span>
              <span class="metric-chip">近期动作 <strong>{{ approvalRecentActions.length }}</strong></span>
            </div>
            <div class="mt-3 flex flex-wrap gap-2">
              <button class="rounded-full bg-emerald-700 px-3 py-2 text-xs font-semibold text-white disabled:opacity-60" :disabled="isActionPending || !approvalTargetTsCode" @click="submitManualAction('confirm', approvalTargetTsCode, approvalTargetNote, approvalTargetName)">
                确认
              </button>
              <button class="rounded-full bg-amber-600 px-3 py-2 text-xs font-semibold text-white disabled:opacity-60" :disabled="isActionPending || !approvalTargetTsCode" @click="submitManualAction('defer', approvalTargetTsCode, approvalTargetNote, approvalTargetName)">
                暂缓
              </button>
              <button class="rounded-full bg-red-700 px-3 py-2 text-xs font-semibold text-white disabled:opacity-60" :disabled="isActionPending || !approvalTargetTsCode" @click="submitManualAction('reject', approvalTargetTsCode, approvalTargetNote, approvalTargetName)">
                驳回
              </button>
              <button class="rounded-full border border-[var(--line)] bg-white px-3 py-2 text-xs font-semibold text-[var(--ink)] disabled:opacity-60" :disabled="isActionPending || !approvalTargetTsCode" @click="submitManualAction('review', approvalTargetTsCode, approvalTargetNote, approvalTargetName)">
                复核
              </button>
            </div>
          </InfoCard>
        </PageSection>
      </div>

      <div class="grid gap-4 xl:grid-cols-[0.95fr_1.05fr]">
        <PageSection title="重点行业" subtitle="优先看排序靠前的行业，再决定是否下钻到单票。">
          <DataTable :columns="industryColumns" :rows="priorityIndustries" row-key="industry" empty-text="暂无重点行业" caption="重点行业">
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

        <PageSection title="重点个股" subtitle="先看计划里的优先候选，再点进详情页。">
          <DataTable :columns="stockColumns" :rows="priorityStocks" row-key="ts_code" empty-text="暂无重点个股" caption="重点个股">
            <template #cell-ts_code="{ row }">
              <RouterLink :to="`/stocks/detail/${row.ts_code}`" class="font-semibold text-[var(--brand)] hover:underline">
                {{ row.name || row.ts_code || '-' }}
              </RouterLink>
              <div class="mt-1 text-xs text-[var(--muted)]">{{ row.ts_code || '-' }}</div>
            </template>
            <template #cell-total_score="{ row }">{{ formatNumber(row.total_score, 2) }}</template>
            <template #cell-industry_total_score="{ row }">{{ formatNumber(row.industry_total_score, 2) }}</template>
            <template #cell-position_label="{ row }"><StatusBadge :value="row.position_label || 'muted'" :label="row.position_label || '-'"/></template>
          </DataTable>
        </PageSection>
      </div>

      <PageSection title="风险与复盘" subtitle="把验证层、回看点和执行状态放到一起，方便第二天复盘。">
        <div class="grid gap-3 xl:grid-cols-3 md:grid-cols-1">
          <InfoCard :title="validation.status || '验证层'" :meta="validation.source || '-'" :description="validation.summary || '暂无验证数据'">
            <template #badge>
              <StatusBadge :value="validation.status || 'muted'" :label="validation.status || '-'" />
            </template>
          </InfoCard>
          <InfoCard :title="killSwitchLabel" :meta="killSwitch.updated_at || '-'" :description="killSwitch.reason || '暂无备注'">
            <template #badge>
              <StatusBadge :value="killSwitchTone" :label="killSwitchLabel" />
            </template>
          </InfoCard>
          <InfoCard :title="plan.note_title || '计划说明'" :meta="plan.generated_at || '-'" :description="joinLines(plan.notes)">
            <template #badge>
              <StatusBadge value="info" label="说明" />
            </template>
          </InfoCard>
        </div>
        <div v-if="approvalRecentActions.length" class="mt-4 space-y-2">
          <InfoCard
            v-for="item in approvalRecentActions"
            :key="item.id"
            :title="joinActionTitle(item)"
            :meta="joinActionMeta(item)"
            :description="item.note || item.payload?.context?.reason || '暂无备注'"
          >
            <template #badge>
              <StatusBadge :value="item.approval_state || 'muted'" :label="item.approval_state_label || item.approval_state || '-'" />
            </template>
          </InfoCard>
        </div>
      </PageSection>

      <div class="grid gap-4 xl:grid-cols-[1.1fr_0.9fr]">
        <PageSection title="日内执行计划" subtitle="按时间段拆成更适合盘中跟踪的动作。">
          <div class="space-y-3">
            <InfoCard
              v-for="item in intradayPlan"
              :key="item.stage"
              :title="item.stage"
              :meta="item.time_window"
              :description="joinLines(item.actions)"
            >
              <template #badge>
                <StatusBadge value="brand" :label="item.time_window" />
              </template>
            </InfoCard>
          </div>
        </PageSection>

        <PageSection title="产业链联动" subtitle="把行业、信号和主题映射关系一并摆出来。">
          <div v-if="themeLinks.length" class="space-y-3">
            <InfoCard
              v-for="item in themeLinks"
              :key="item.term"
              :title="item.term"
              :meta="`联动信号 ${item.signals.length}`"
              :description="joinSignalLines(item.signals)"
            >
              <template #badge>
                <StatusBadge value="info" :label="item.term" />
              </template>
            </InfoCard>
          </div>
          <div v-else class="rounded-[18px] border border-[var(--line)] bg-white/80 px-4 py-3 text-sm text-[var(--muted)]">
            当前没有足够的行业联动信号，后续会随着主题映射和信号表继续增强。
          </div>
        </PageSection>
      </div>

      <PageSection :title="strategyTitle" subtitle="把策略候选做成可反复运行、可切版本、可回放的实验台。">
        <div class="flex flex-wrap items-center gap-3">
          <button class="rounded-2xl bg-[var(--brand)] px-4 py-3 font-semibold text-white disabled:opacity-60" :disabled="isStrategyRunning" @click="generateStrategyBatch">
            {{ isStrategyRunning ? '生成中...' : '生成策略批次' }}
          </button>
          <select v-model="selectedStrategyRunId" class="min-w-[220px] rounded-2xl border border-[var(--line)] bg-white px-4 py-3" @change="strategySelectionTouched = true">
            <option value="">当前最新 / 预览</option>
            <option v-for="item in strategyHistoryItems" :key="item.id || item.run_id" :value="String(item.id || item.run_id || '')">
              版本 {{ item.run_version || '-' }} · {{ item.created_at || '-' }}
            </option>
          </select>
          <StatusBadge :value="strategyRunSummary.llm_enabled ? 'success' : 'muted'" :label="strategyRunSummary.llm_enabled ? 'LLM 辅助已启用' : 'LLM 辅助未启用'" />
          <StatusBadge value="info" :label="strategyRunLabel" />
        </div>
        <div class="mt-3 grid gap-3 xl:grid-cols-4 md:grid-cols-2">
          <StatCard title="候选数" :value="String(strategySummary.strategy_count ?? strategyItems.length ?? 0)" :hint="`最优策略 ${strategySummary.best_strategy || '-'}`" />
          <StatCard title="最优得分" :value="formatNumber(strategySummary.best_fit_score, 1)" :hint="`LLM 平均 ${formatNumber(strategySummary.llm_average_score, 1)}`" />
          <StatCard title="版本摘要" :value="strategyRunLabel" :hint="strategyRunSummary.run_key || '-'" />
          <StatCard title="聚焦标的" :value="strategyLab.focus_name || focusTitle" :hint="strategyLab.focus_stock?.ts_code || approvalTargetTsCode || '-'" />
        </div>
        <div class="mt-4 grid gap-3 xl:grid-cols-[1.05fr_0.95fr]">
          <InfoCard title="运行摘要" :meta="strategyRunSummary.created_at || strategyLab.generated_at || '-'" :description="strategyRunDescription">
            <template #badge>
              <StatusBadge :value="strategyRunSummary.source_mode === 'generated' ? 'success' : 'info'" :label="strategyRunSummary.source_mode === 'generated' ? '已生成' : '预览'" />
            </template>
            <div class="mt-3 grid gap-2 text-xs md:grid-cols-2">
              <span class="metric-chip">市场模式 <strong>{{ strategySummary.market_mode || '-' }}</strong></span>
              <span class="metric-chip">LLM 平均 <strong>{{ formatNumber(strategySummary.llm_average_score, 1) }}</strong></span>
              <span class="metric-chip">策略版本 <strong>{{ strategyRunSummary.run_key || '-' }}</strong></span>
              <span class="metric-chip">对比上版 <strong>{{ strategyRunComparison.best_fit_delta ?? 0 }}</strong></span>
            </div>
          </InfoCard>
          <InfoCard title="历史版本" :meta="`共 ${strategyHistoryItems.length} 个版本`" description="点击选择任意历史批次，查看对应策略候选。">
            <template #badge>
              <StatusBadge value="muted" label="History" />
            </template>
            <div v-if="strategyHistoryItems.length" class="mt-3 space-y-2">
              <button
                v-for="item in strategyHistoryItems.slice(0, 5)"
                :key="item.id || item.run_id"
                class="w-full rounded-2xl border border-[var(--line)] bg-white px-4 py-3 text-left text-sm transition hover:border-[var(--brand)]"
                @click="strategySelectionTouched = true; selectedStrategyRunId = String(item.id || item.run_id || '')"
              >
                <div class="flex items-center justify-between gap-2">
                  <span class="font-semibold text-[var(--ink)]">版本 {{ item.run_version || '-' }}</span>
                  <StatusBadge :value="item.source_mode === 'generated' ? 'success' : 'info'" :label="item.source_mode === 'generated' ? '已生成' : '预览'" />
                </div>
                <div class="mt-1 text-xs text-[var(--muted)]">{{ item.created_at || '-' }}</div>
                <div class="mt-1 text-xs text-[var(--muted)]">
                  {{ item.summary?.best_strategy || '-' }} · {{ formatNumber(item.summary?.best_fit_score, 1) }} · LLM {{ formatNumber(item.summary?.llm_average_score, 1) }}
                </div>
              </button>
            </div>
            <div v-else class="mt-3 rounded-[18px] border border-[var(--line)] bg-white/80 px-4 py-3 text-sm text-[var(--muted)]">
              还没有生成过策略批次，点击“生成策略批次”即可创建第一个版本。
            </div>
          </InfoCard>
        </div>
        <div class="mt-4 grid gap-3 xl:grid-cols-2">
          <InfoCard
            v-for="item in strategyItems"
            :key="`${item.name}-${item.rank}`"
            :title="`${item.rank}. ${item.name}`"
            :meta="`${item.mode || '-'} · 适配 ${formatNumber(item.fit_score, 1)} · LLM ${formatNumber(item.llm_feasibility_score, 1)}`"
            :description="item.summary || '暂无摘要'"
          >
            <template #badge>
              <StatusBadge :value="item.status === 'halted' ? 'danger' : item.mode === 'aggressive' ? 'success' : item.mode === 'balanced' ? 'info' : item.mode === 'defensive' ? 'warning' : 'muted'" :label="item.llm_feasibility_label || item.approval_hint || item.status || '-'" />
            </template>
            <div class="mt-3 grid gap-2 text-xs md:grid-cols-2">
              <span class="metric-chip">入场 <strong>{{ item.entry_rule || '-' }}</strong></span>
              <span class="metric-chip">退出 <strong>{{ item.exit_rule || '-' }}</strong></span>
              <span class="metric-chip">仓位 <strong>{{ item.position_bias || '-' }}</strong></span>
              <span class="metric-chip">范围 <strong>{{ item.universe || '-' }}</strong></span>
            </div>
            <div class="mt-3 flex flex-wrap gap-2 text-xs">
              <span v-for="industry in item.linked_industries || []" :key="`${item.name}-${industry}`" class="metric-chip">
                行业 <strong>{{ industry }}</strong>
              </span>
              <span v-for="stock in item.linked_stocks || []" :key="`${item.name}-${stock}`" class="metric-chip">
                股票 <strong>{{ stock }}</strong>
              </span>
            </div>
            <div class="mt-3 rounded-[18px] border border-[var(--line)] bg-white/80 px-4 py-3 text-sm text-[var(--muted)]">
              <div class="font-semibold text-[var(--ink)]">LLM 辅助说明</div>
              <div class="mt-1">可行性 {{ formatNumber(item.llm_feasibility_score, 1) }} · {{ item.llm_feasibility_label || '-' }}</div>
              <div class="mt-1">{{ item.llm_explanation || '暂无辅助解释' }}</div>
              <div class="mt-2 text-xs">{{ item.llm_risk_note || item.risk_control || '暂无风险控制说明' }}</div>
            </div>
          </InfoCard>
        </div>
        <div v-if="strategyLab.generator_rules?.length" class="mt-4 rounded-[18px] border border-[var(--line)] bg-white/80 px-4 py-3 text-sm text-[var(--muted)]">
          <div class="font-semibold text-[var(--ink)]">生成规则</div>
          <div class="mt-2 space-y-1">
            <div v-for="rule in strategyLab.generator_rules" :key="rule">{{ rule }}</div>
          </div>
        </div>
      </PageSection>
    </div>
  </AppShell>
</template>

<script setup lang="ts">
import { computed, ref, watch, watchEffect } from 'vue'
import { useMutation, useQuery } from '@tanstack/vue-query'
import { RouterLink } from 'vue-router'
import AppShell from '../../shared/ui/AppShell.vue'
import PageSection from '../../shared/ui/PageSection.vue'
import InfoCard from '../../shared/ui/InfoCard.vue'
import StatCard from '../../shared/ui/StatCard.vue'
import StatusBadge from '../../shared/ui/StatusBadge.vue'
import DataTable from '../../shared/ui/DataTable.vue'
import {
  fetchDecisionActions,
  fetchDecisionKillSwitch,
  fetchDecisionPlan,
  fetchDecisionStrategyRun,
  fetchDecisionStrategyRuns,
  recordDecisionAction,
  runDecisionStrategyLab,
} from '../../services/api/decision'
import { formatNumber } from '../../shared/utils/format'

const focusTsCode = ref('')
const pageSize = ref(12)
const noteDraft = ref('')
const approvalNoteDraft = ref('计划确认')
const message = ref('')
const selectedStrategyRunId = ref('')
const strategySelectionTouched = ref(false)

watch(focusTsCode, () => {
  selectedStrategyRunId.value = ''
  strategySelectionTouched.value = false
})

const planQuery = useQuery({
  queryKey: computed(() => ['decision-plan', focusTsCode.value, pageSize.value]),
  queryFn: () => fetchDecisionPlan({ ts_code: focusTsCode.value, page: 1, page_size: pageSize.value }),
  refetchInterval: 60_000,
})

const killSwitchQuery = useQuery({
  queryKey: ['decision-plan-kill-switch'],
  queryFn: () => fetchDecisionKillSwitch(),
  refetchInterval: 60_000,
})

const actionsQuery = useQuery({
  queryKey: computed(() => ['decision-plan-actions', focusTsCode.value]),
  queryFn: () => fetchDecisionActions({ page: 1, page_size: 8, ts_code: focusTsCode.value }),
  refetchInterval: 60_000,
})

const strategyRunsQuery = useQuery({
  queryKey: computed(() => ['decision-strategy-runs', focusTsCode.value]),
  queryFn: () => fetchDecisionStrategyRuns({ ts_code: focusTsCode.value, page: 1, page_size: 8 }),
  refetchInterval: 60_000,
})

const strategyQuery = useQuery({
  queryKey: computed(() => ['decision-strategy-lab', focusTsCode.value, pageSize.value, selectedStrategyRunId.value]),
  queryFn: () => {
    const params: Record<string, any> = {
      ts_code: focusTsCode.value,
      page: 1,
      page_size: pageSize.value,
    }
    if (selectedStrategyRunId.value) {
      params.run_id = Number(selectedStrategyRunId.value)
    }
    return fetchDecisionStrategyRun(params)
  },
  refetchInterval: 60_000,
})

const plan = computed<Record<string, any>>(() => (planQuery.data.value || {}) as Record<string, any>)
const killSwitch = computed<Record<string, any>>(() => ((killSwitchQuery.data.value as Record<string, any>) || {}) as Record<string, any>)
const isFetching = computed(() => Boolean(planQuery.isFetching.value))
const planErrorText = computed(() => {
  const value = planQuery.error.value
  if (!value) return ''
  return value instanceof Error ? value.message : String(value)
})
const priorityIndustries = computed<Array<Record<string, any>>>(() => (plan.value.priority_industries || []) as Array<Record<string, any>>)
const priorityStocks = computed<Array<Record<string, any>>>(() => (plan.value.priority_stocks || []) as Array<Record<string, any>>)
const intradayPlan = computed<Array<Record<string, any>>>(() => (plan.value.intraday_plan || []) as Array<Record<string, any>>)
const themeLinks = computed<Array<Record<string, any>>>(() => (plan.value.theme_links || []) as Array<Record<string, any>>)
const positionPlan = computed<Record<string, any>>(() => (plan.value.position_plan || {}) as Record<string, any>)
const validation = computed<Record<string, any>>(() => (plan.value.validation || {}) as Record<string, any>)
const approvalFlow = computed<Record<string, any>>(() => (plan.value.approval_flow || {}) as Record<string, any>)
const approvalRecentActions = computed<Array<Record<string, any>>>(() => (approvalFlow.value.recent_actions || actionsQuery.data.value?.items || []) as Array<Record<string, any>>)
const strategyLab = computed<Record<string, any>>(() => (strategyQuery.data.value || {}) as Record<string, any>)
const strategyItems = computed<Array<Record<string, any>>>(() => (strategyLab.value.strategies || []) as Array<Record<string, any>>)
const strategyHistoryItems = computed<Array<Record<string, any>>>(() => ((strategyRunsQuery.data.value?.items || []) as Array<Record<string, any>>))
const selectedStrategyRun = computed<Record<string, any> | null>(() => {
  const selected = selectedStrategyRunId.value ? strategyHistoryItems.value.find((item) => String(item.id || '') === selectedStrategyRunId.value || String(item.run_id || '') === selectedStrategyRunId.value) : null
  return (selected || null) as Record<string, any> | null
})
const strategySummary = computed<Record<string, any>>(() => (strategyLab.value.summary || {}) as Record<string, any>)
const approvalTone = computed(() => (approvalFlow.value.state === 'approved' ? 'success' : approvalFlow.value.state === 'rejected' ? 'danger' : approvalFlow.value.state === 'deferred' ? 'warning' : approvalFlow.value.state === 'halted' ? 'danger' : 'info'))
const killSwitchTone = computed(() => (Number(killSwitch.value.allow_trading ?? 1) === 1 ? 'success' : 'danger'))
const killSwitchLabel = computed(() => (Number(killSwitch.value.allow_trading ?? 1) === 1 ? '交易允许' : '交易暂停'))
const planModeTone = computed(() => (plan.value.mode === 'aggressive' ? 'success' : plan.value.mode === 'balanced' ? 'info' : plan.value.mode === 'halted' ? 'danger' : 'muted'))
const planModeLabel = computed(() => String(plan.value.mode || 'neutral'))
const snapshotDate = computed(() => String(plan.value.snapshot_date || '').trim())
const focusKeyword = computed(() => String(plan.value.keyword || '').trim())
const focusTitle = computed(() => plan.value.focus_name || plan.value.focus_stock?.ts_code || '聚焦标的')
const focusMeta = computed(() => [plan.value.focus_stock?.ts_code, plan.value.focus_stock?.score?.position_label].filter(Boolean).join(' · ') || '全局计划')
const planDescription = computed(() => `${plan.value.summary || '暂无摘要'}${noteDraft.value ? ` · 备注：${noteDraft.value}` : ''}`)
const strategyTitle = computed(() => strategyLab.value.title || '策略实验台')
const strategyRunComparison = computed<Record<string, any>>(() => (selectedStrategyRun.value?.comparison_to_previous || strategyLab.value.comparison || {}) as Record<string, any>)
const strategyRunLabel = computed(() => {
  const version = selectedStrategyRun.value?.run_version || strategyLab.value.run?.run_version
  if (version) return `版本 ${version}`
  return strategyLab.value.source_mode === 'generated' ? '最新生成' : '预览'
})
const strategyRunSummary = computed(() => {
  const current = selectedStrategyRun.value || strategyLab.value.run || {}
  return {
    run_key: current.run_key || strategyLab.value.run?.run_key || '-',
    created_at: current.created_at || strategyLab.value.generated_at || '-',
    llm_enabled: Number(current.llm_enabled ?? strategyLab.value.run?.llm_enabled ?? 0),
    source_mode: current.source_mode || strategyLab.value.source_mode || 'preview',
  }
})
const strategyRunDescription = computed(() => {
  const summary = strategyLab.value.summary || {}
  return [
    strategyLab.value.title || '策略实验台',
    summary.best_strategy ? `最优 ${summary.best_strategy}` : '',
    summary.market_mode ? `市场 ${summary.market_mode}` : '',
    summary.llm_average_score !== undefined ? `LLM ${formatNumber(summary.llm_average_score, 1)}` : '',
  ]
    .filter(Boolean)
    .join(' · ') || '暂无运行摘要'
})
const approvalTargetTsCode = computed(() => String(plan.value.ts_code || plan.value.focus_stock?.ts_code || focusTsCode.value || '').trim().toUpperCase())
const approvalTargetName = computed(() => String(plan.value.focus_name || plan.value.focus_stock?.name || plan.value.focus_stock?.ts_code || approvalTargetTsCode.value || '').trim())
const approvalTargetNote = computed(() => String(approvalNoteDraft.value || noteDraft.value || '计划确认').trim())

watchEffect(() => {
  if (selectedStrategyRunId.value || strategySelectionTouched.value) return
  const latest = strategyHistoryItems.value[0]
  const latestRunId = latest ? String(latest.id || latest.run_id || '') : ''
  if (latestRunId) {
    selectedStrategyRunId.value = latestRunId
  }
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
        source: 'decision_trade_plan',
        market_mode: plan.value.mode || '',
        approval_state: approvalFlow.value.state || '',
      },
    }),
  onSuccess: async () => {
    message.value = '审批动作已保存。'
    await refreshPlan()
  },
  onError: (error: Error) => {
    message.value = `审批动作失败：${error.message}`
  },
})
const isActionPending = computed(() => Boolean(actionMutation.isPending.value))

const strategyRunMutation = useMutation({
  mutationFn: () =>
    runDecisionStrategyLab({
      ts_code: focusTsCode.value,
      page: 1,
      page_size: pageSize.value,
      keyword: focusKeyword.value,
    }),
  onSuccess: async (result: Record<string, any>) => {
    const runId = result.generated_run?.run_id || result.run?.run_id || result.run_id || ''
    if (runId) {
      strategySelectionTouched.value = true
      selectedStrategyRunId.value = String(runId)
    }
    message.value = '策略批次已生成。'
    await Promise.all([
      strategyRunsQuery.refetch(),
      strategyQuery.refetch(),
      planQuery.refetch(),
    ])
  },
  onError: (error: Error) => {
    message.value = `策略批次生成失败：${error.message}`
  },
})
const isStrategyRunning = computed(() => Boolean(strategyRunMutation.isPending.value))

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
]

function joinLines(items: unknown) {
  if (!Array.isArray(items) || !items.length) return '暂无。'
  return items.map((item) => String(item || '').trim()).filter(Boolean).join('；')
}

function joinSignalLines(items: Array<Record<string, any>>) {
  if (!items.length) return '暂无联动信号。'
  return items
    .map((item) => {
      const direction = String(item.direction || '-').trim()
      const score = Number(item.signal_strength || 0)
      const confidence = Number(item.confidence || 0)
      return `${item.subject_name || item.ts_code || '-'} · ${direction} · 强度 ${score.toFixed(1)} · 置信 ${confidence.toFixed(1)}`
    })
    .join('；')
}

function joinActionTitle(item: Record<string, any>) {
  return `${item.stock_name || item.ts_code || '-'} · ${String(item.action_type || '-').toUpperCase()}`
}

function joinActionMeta(item: Record<string, any>) {
  return [item.ts_code || '-', item.actor || '-', item.created_at || '-'].filter(Boolean).join(' · ')
}

function submitManualAction(actionType: 'confirm' | 'reject' | 'defer' | 'watch' | 'review', tsCode: string, note: string, stockName = '') {
  const normalizedTsCode = String(tsCode || '').trim().toUpperCase()
  if (!normalizedTsCode) return
  actionMutation.mutate({
    action_type: actionType,
    ts_code: normalizedTsCode,
    note: String(note || approvalNoteDraft.value || '').trim(),
    stock_name: String(stockName || normalizedTsCode).trim(),
  })
}

async function refreshPlan() {
  await planQuery.refetch()
  await killSwitchQuery.refetch()
  await strategyRunsQuery.refetch()
  await strategyQuery.refetch()
  message.value = '交易计划书已刷新。'
}

async function generateStrategyBatch() {
  await strategyRunMutation.mutateAsync()
}
</script>
