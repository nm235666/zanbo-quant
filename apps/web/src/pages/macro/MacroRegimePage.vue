<template>
  <AppShell title="宏观三周期状态" subtitle="短期（1-4周）、中期（1-6月）、长期（6-24月）状态评估与组合动作建议。">
    <div class="space-y-4">
      <StatePanel
        v-if="pageStatus !== 'ready'"
        :tone="pageStatus === 'not_initialized' ? 'warning' : 'default'"
        :title="pageStatusTitle"
        :description="pageStatusDescription"
      >
        <template #action>
          <RouterLink
            to="/app/allocation"
            class="rounded-2xl border border-[var(--line)] bg-white px-4 py-2 text-sm font-semibold text-[var(--ink)] transition hover:border-[var(--brand)] hover:text-[var(--brand)]"
          >
            查看配置动作
          </RouterLink>
        </template>
      </StatePanel>

      <!-- 当前状态总览 -->
      <div class="page-hero-grid">
        <div class="page-hero-card">
          <div class="page-insight-label">Macro Regime</div>
          <div class="page-hero-title">三周期状态决定组合基本盘取向。</div>
          <div class="page-hero-copy">
            先看长期状态确定防守/进攻基调，再看短中期是否与长期一致；若冲突，系统会自动给出裁决动作。
          </div>
          <div class="page-action-cluster">
            <RouterLink to="/app/allocation" class="rounded-2xl bg-[var(--brand)] px-4 py-3 font-semibold text-white">
              查看配置动作
            </RouterLink>
          </div>
        </div>
        <div class="page-insight-list">
          <div class="page-insight-item">
            <div class="page-insight-label">最新评估</div>
            <div class="page-insight-value">{{ latestDate || '暂无记录' }}</div>
            <div class="page-insight-note">最近一次三周期状态录入时间</div>
          </div>
          <div class="page-insight-item">
            <div class="page-insight-label">当前基调</div>
            <div class="page-insight-value">{{ currentStanceLabel }}</div>
            <div class="page-insight-note">由长期状态驱动</div>
          </div>
        </div>
      </div>

      <!-- 三周期状态卡 -->
      <div v-if="regime" class="grid gap-4 md:grid-cols-3">
        <!-- 短期 -->
        <div class="rounded-2xl border p-5 space-y-3"
          :class="stateCardClass(regime.short_term_state)">
          <div class="flex items-center justify-between">
            <div class="text-xs font-semibold uppercase tracking-wide opacity-70">短期 1-4周</div>
            <span v-if="regime.short_term_changed" class="rounded-full bg-amber-100 px-2 py-0.5 text-xs text-amber-700 font-semibold">已变化</span>
          </div>
          <div class="text-2xl font-bold">{{ stateLabel(regime.short_term_state) }}</div>
          <div class="flex items-center gap-2">
            <div class="h-1.5 flex-1 rounded-full bg-black/10">
              <div class="h-1.5 rounded-full bg-current opacity-60" :style="`width:${(regime.short_term_confidence||0)*100}%`"></div>
            </div>
            <span class="text-xs font-semibold opacity-60">{{ ((regime.short_term_confidence||0)*100).toFixed(0) }}%</span>
          </div>
          <div v-if="regime.short_term_change_reason" class="text-xs opacity-70 leading-5">{{ regime.short_term_change_reason }}</div>
        </div>

        <!-- 中期 -->
        <div class="rounded-2xl border p-5 space-y-3"
          :class="stateCardClass(regime.medium_term_state)">
          <div class="flex items-center justify-between">
            <div class="text-xs font-semibold uppercase tracking-wide opacity-70">中期 1-6月</div>
            <span v-if="regime.medium_term_changed" class="rounded-full bg-amber-100 px-2 py-0.5 text-xs text-amber-700 font-semibold">已变化</span>
          </div>
          <div class="text-2xl font-bold">{{ stateLabel(regime.medium_term_state) }}</div>
          <div class="flex items-center gap-2">
            <div class="h-1.5 flex-1 rounded-full bg-black/10">
              <div class="h-1.5 rounded-full bg-current opacity-60" :style="`width:${(regime.medium_term_confidence||0)*100}%`"></div>
            </div>
            <span class="text-xs font-semibold opacity-60">{{ ((regime.medium_term_confidence||0)*100).toFixed(0) }}%</span>
          </div>
          <div v-if="regime.medium_term_change_reason" class="text-xs opacity-70 leading-5">{{ regime.medium_term_change_reason }}</div>
        </div>

        <!-- 长期 -->
        <div class="rounded-2xl border p-5 space-y-3"
          :class="stateCardClass(regime.long_term_state)">
          <div class="flex items-center justify-between">
            <div class="text-xs font-semibold uppercase tracking-wide opacity-70">长期 6-24月</div>
            <span v-if="regime.long_term_changed" class="rounded-full bg-amber-100 px-2 py-0.5 text-xs text-amber-700 font-semibold">已变化</span>
          </div>
          <div class="text-2xl font-bold">{{ stateLabel(regime.long_term_state) }}</div>
          <div class="flex items-center gap-2">
            <div class="h-1.5 flex-1 rounded-full bg-black/10">
              <div class="h-1.5 rounded-full bg-current opacity-60" :style="`width:${(regime.long_term_confidence||0)*100}%`"></div>
            </div>
            <span class="text-xs font-semibold opacity-60">{{ ((regime.long_term_confidence||0)*100).toFixed(0) }}%</span>
          </div>
          <div v-if="regime.long_term_change_reason" class="text-xs opacity-70 leading-5">{{ regime.long_term_change_reason }}</div>
        </div>
      </div>

      <!-- 无数据占位 -->
      <div v-else-if="!regimeLoading" class="rounded-2xl border border-dashed border-[var(--line)] px-4 py-10 text-center text-sm text-[var(--muted)]">
        {{ pageStatus === 'not_initialized' ? '当前还没有任何有效三周期记录。你可以先用系统建议填表，再由人工复核确认首条状态。' : pageStatusDescription }}
      </div>

      <!-- 冲突裁决 -->
      <div v-if="conflictRuling" class="rounded-2xl border border-amber-200 bg-amber-50 px-4 py-4">
        <div class="mb-1 text-xs font-semibold text-amber-700">短长线冲突裁决</div>
        <div class="text-sm text-amber-800 leading-6">{{ conflictRuling }}</div>
      </div>

      <div v-if="statusFootnote" class="rounded-2xl border border-[var(--line)] bg-[var(--panel-soft)] px-4 py-3 text-xs text-[var(--muted)]">
        {{ statusFootnote }}
      </div>

      <!-- 组合动作建议 -->
      <PageSection v-if="portfolioActions.length" title="组合动作建议" subtitle="由当前三周期状态自动推导。">
        <div class="grid gap-3 sm:grid-cols-2">
          <div
            v-for="action in portfolioActions"
            :key="action.type"
            class="rounded-2xl border border-[var(--line)] bg-[var(--panel-soft)] px-4 py-3"
          >
            <div class="mb-1 text-xs font-semibold uppercase text-[var(--muted)]">{{ actionTypeLabel(action.type) }}</div>
            <div class="text-sm leading-6 text-[var(--ink)]">{{ action.description }}</div>
          </div>
        </div>
      </PageSection>

      <!-- 系统建议 -->
      <div v-if="suggestion" class="mb-4 rounded-2xl border border-sky-200 bg-sky-50 px-4 py-3">
        <div class="flex items-center justify-between mb-2">
          <div class="text-sm font-bold text-sky-800">系统建议状态</div>
          <button @click="applySuggestion" class="rounded-full bg-sky-600 px-3 py-1 text-xs font-semibold text-white hover:bg-sky-700">
            一键填入表单
          </button>
        </div>
        <div class="grid gap-2 sm:grid-cols-3 text-xs">
          <div class="rounded-xl bg-white px-3 py-2">
            <div class="text-[var(--muted)] mb-0.5">短期建议</div>
            <div class="font-semibold">{{ REGIME_STATE_LABELS[suggestion.short_term_state] ?? suggestion.short_term_state }}</div>
            <div class="text-[var(--muted)]">{{ (suggestion.short_term_confidence * 100).toFixed(0) }}% 置信</div>
          </div>
          <div class="rounded-xl bg-white px-3 py-2">
            <div class="text-[var(--muted)] mb-0.5">中期建议</div>
            <div class="font-semibold">{{ REGIME_STATE_LABELS[suggestion.medium_term_state] ?? suggestion.medium_term_state }}</div>
            <div class="text-[var(--muted)]">{{ (suggestion.medium_term_confidence * 100).toFixed(0) }}% 置信</div>
          </div>
          <div class="rounded-xl bg-white px-3 py-2">
            <div class="text-[var(--muted)] mb-0.5">长期建议</div>
            <div class="font-semibold">{{ REGIME_STATE_LABELS[suggestion.long_term_state] ?? suggestion.long_term_state }}</div>
            <div class="text-[var(--muted)]">{{ (suggestion.long_term_confidence * 100).toFixed(0) }}% 置信</div>
          </div>
        </div>
        <div class="mt-2 text-xs text-sky-700">依据：{{ suggestion.basis }}</div>
        <div class="mt-1 text-xs text-sky-600">说明：建议仅供参考，请人工复核后确认录入。</div>
      </div>

      <!-- 录入新状态 -->
      <PageSection title="录入三周期评估" subtitle="记录当前宏观三周期状态与关键变化原因。">
        <div class="space-y-4">
          <div class="grid gap-3 md:grid-cols-3">
            <label class="text-sm font-semibold text-[var(--ink)]">
              短期状态（1-4周）
              <select v-model="form.short_term_state" class="mt-1 w-full rounded-2xl border border-[var(--line)] bg-white px-4 py-3 text-sm">
                <option v-for="(label, val) in STATE_LABELS" :key="val" :value="val">{{ label }}</option>
              </select>
            </label>
            <label class="text-sm font-semibold text-[var(--ink)]">
              中期状态（1-6月）
              <select v-model="form.medium_term_state" class="mt-1 w-full rounded-2xl border border-[var(--line)] bg-white px-4 py-3 text-sm">
                <option v-for="(label, val) in STATE_LABELS" :key="val" :value="val">{{ label }}</option>
              </select>
            </label>
            <label class="text-sm font-semibold text-[var(--ink)]">
              长期状态（6-24月）
              <select v-model="form.long_term_state" class="mt-1 w-full rounded-2xl border border-[var(--line)] bg-white px-4 py-3 text-sm">
                <option v-for="(label, val) in STATE_LABELS" :key="val" :value="val">{{ label }}</option>
              </select>
            </label>
          </div>
          <div class="grid gap-3 md:grid-cols-3">
            <label class="text-sm font-semibold text-[var(--ink)]">
              短期变化原因
              <input v-model="form.short_term_change_reason" class="mt-1 w-full rounded-2xl border border-[var(--line)] bg-white px-4 py-3 text-sm" placeholder="可选，简述原因" />
            </label>
            <label class="text-sm font-semibold text-[var(--ink)]">
              中期变化原因
              <input v-model="form.medium_term_change_reason" class="mt-1 w-full rounded-2xl border border-[var(--line)] bg-white px-4 py-3 text-sm" placeholder="可选，简述原因" />
            </label>
            <label class="text-sm font-semibold text-[var(--ink)]">
              长期变化原因
              <input v-model="form.long_term_change_reason" class="mt-1 w-full rounded-2xl border border-[var(--line)] bg-white px-4 py-3 text-sm" placeholder="可选，简述原因" />
            </label>
          </div>
          <div class="flex flex-wrap gap-4 text-sm">
            <label class="flex items-center gap-2 font-medium text-[var(--ink)]">
              <input type="checkbox" v-model="form.short_term_changed" class="rounded" /> 短期状态已变化
            </label>
            <label class="flex items-center gap-2 font-medium text-[var(--ink)]">
              <input type="checkbox" v-model="form.medium_term_changed" class="rounded" /> 中期状态已变化
            </label>
            <label class="flex items-center gap-2 font-medium text-[var(--ink)]">
              <input type="checkbox" v-model="form.long_term_changed" class="rounded" /> 长期状态已变化
            </label>
          </div>
          <div v-if="submitError" class="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{{ submitError }}</div>
          <div v-if="submitSuccess" class="rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">评估已记录，组合建议已自动更新。</div>
          <button
            class="rounded-2xl bg-[var(--brand)] px-5 py-2.5 text-sm font-semibold text-white disabled:opacity-60"
            :disabled="submitPending"
            @click="submitRegime"
          >
            {{ submitPending ? '提交中...' : '记录当前评估' }}
          </button>
        </div>
      </PageSection>

      <!-- 历史记录 -->
      <PageSection :title="`历史记录 (${historyTotal})`" subtitle="宏观三周期状态变更记录。">
        <div v-if="historyLoading" class="py-6 text-center text-sm text-[var(--muted)]">加载中...</div>
        <div v-else-if="!historyItems.length" class="py-6 text-center text-sm text-[var(--muted)]">
          {{ historyEmptyText }}
        </div>
        <div v-else class="divide-y divide-[var(--line)]">
          <div v-for="item in historyItems" :key="item.id" class="py-4 space-y-2">
            <div class="flex flex-wrap items-start justify-between gap-2">
              <div class="flex flex-wrap gap-2">
                <span :class="stateBadgeClass(item.short_term_state)">短 {{ stateLabel(item.short_term_state) }}</span>
                <span :class="stateBadgeClass(item.medium_term_state)">中 {{ stateLabel(item.medium_term_state) }}</span>
                <span :class="stateBadgeClass(item.long_term_state)">长 {{ stateLabel(item.long_term_state) }}</span>
              </div>
              <div class="flex items-center gap-2">
                <div class="text-xs text-[var(--muted)]">{{ formatDate(item.created_at) }}{{ item.created_by ? ' · ' + item.created_by : '' }}</div>
                <button
                  class="rounded-lg border border-[var(--line)] px-2 py-0.5 text-xs text-[var(--muted)] hover:bg-[var(--panel-soft)]"
                  @click="toggleOutcomeEdit(item.id)"
                >记录复盘</button>
              </div>
            </div>
            <!-- Existing outcome display -->
            <div v-if="item.outcome_rating || item.outcome_notes" class="flex flex-wrap items-center gap-2">
              <span :class="outcomeBadgeClass(item.outcome_rating)">{{ OUTCOME_LABELS[item.outcome_rating ?? ''] ?? item.outcome_rating }}</span>
              <span v-if="item.outcome_notes" class="text-xs text-[var(--muted)]">{{ item.outcome_notes }}</span>
            </div>
            <div v-if="item.correction_suggestion" class="mt-1 text-xs text-blue-700 italic">
              规则修正：{{ item.correction_suggestion }}
            </div>
            <!-- Inline outcome form -->
            <div v-if="editingOutcomeId === item.id" class="rounded-2xl border border-[var(--line)] bg-[var(--panel-soft)] p-3 space-y-2">
              <textarea
                v-model="outcomeDraft.notes"
                rows="2"
                placeholder="复盘备注（可选）"
                class="w-full rounded-xl border border-[var(--line)] bg-white px-3 py-2 text-sm resize-none"
              />
              <div class="flex items-center gap-2">
                <select v-model="outcomeDraft.rating" class="rounded-xl border border-[var(--line)] bg-white px-3 py-2 text-sm">
                  <option value="">请选择评级</option>
                  <option value="effective">有效</option>
                  <option value="partial">部分有效</option>
                  <option value="ineffective">无效</option>
                </select>
                <button
                  class="rounded-xl bg-[var(--brand)] px-3 py-2 text-sm font-semibold text-white disabled:opacity-60"
                  :disabled="outcomeSaving"
                  @click="submitOutcome(item.id)"
                >{{ outcomeSaving ? '保存中...' : '保存' }}</button>
                <button
                  class="rounded-xl border border-[var(--line)] px-3 py-2 text-sm text-[var(--muted)]"
                  @click="editingOutcomeId = null"
                >取消</button>
              </div>
              <textarea v-model="outcomeDraft.correction"
                class="mt-2 w-full rounded-xl border border-[var(--line)] bg-white px-3 py-2 text-xs"
                rows="2"
                placeholder="规则修正建议（可选）：如「下次宏观放缓信号出现时，提前减少进攻仓位比例至15%以下」" />
              <div v-if="outcomeError" class="text-xs text-rose-600">{{ outcomeError }}</div>
            </div>
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
import StatePanel from '../../shared/ui/StatePanel.vue'
import {
  fetchLatestRegime,
  fetchRegimeHistory,
  fetchRegimeSuggestion,
  recordRegime,
  updateRegimeOutcome,
  REGIME_STATE_LABELS,
  type MacroRegime,
} from '../../services/api/macro_regime'

const STATE_LABELS = REGIME_STATE_LABELS
const queryClient = useQueryClient()

const { data: latestData, isPending: regimeLoading } = useQuery({
  queryKey: ['macro-regime-latest'],
  queryFn: fetchLatestRegime,
})

const { data: historyData, isPending: historyLoading } = useQuery({
  queryKey: ['macro-regime-history'],
  queryFn: () => fetchRegimeHistory({ page: 1, page_size: 20 }),
})

const regime = computed<MacroRegime | null>(() => latestData.value?.regime ?? null)
const portfolioActions = computed(() => regime.value?.portfolio_action_json ?? [])
const historyItems = computed(() => historyData.value?.items ?? [])
const historyTotal = computed(() => historyData.value?.total ?? 0)
const regimeStatus = computed(() => String((latestData.value as any)?.status || '').trim() || 'empty')
const regimeStatusReason = computed(() => String((latestData.value as any)?.status_reason || '').trim())
const regimeMissingInputs = computed<string[]>(() => {
  const raw = (latestData.value as any)?.missing_inputs
  return Array.isArray(raw) ? raw : []
})
const pageStatus = computed(() => regimeStatus.value)
const pageStatusTitle = computed(() => {
  if (pageStatus.value === 'not_initialized') return '宏观三周期尚未初始化'
  if (pageStatus.value === 'insufficient_evidence') return '宏观三周期为降级状态'
  if (pageStatus.value === 'error') return '宏观三周期生成失败'
  return '宏观三周期暂未就绪'
})
const pageStatusDescription = computed(() => {
  if (regimeStatusReason.value) return regimeStatusReason.value
  if (pageStatus.value === 'not_initialized') return '系统尚未形成首条三周期状态。当前页面不该只是空白录入页，而应通过系统建议 + 人工复核沉淀第一条记录。'
  if (pageStatus.value === 'insufficient_evidence') return '当前已有部分输入，但还不足以形成稳定的三周期状态，请先补足宏观、市场与历史复盘证据。'
  return '当前没有可展示的三周期结果。'
})
const historyEmptyText = computed(() => {
  if (pageStatus.value === 'not_initialized') return '暂无历史记录，因为系统还没有生成或确认过任何三周期状态。'
  if (pageStatus.value === 'insufficient_evidence') return '暂无历史记录，当前存在输入但尚未形成可确认的状态沉淀。'
  return '暂无历史记录。'
})

const latestDate = computed(() => {
  if (!regime.value?.created_at) return null
  try { return new Date(regime.value.created_at).toLocaleDateString('zh-CN') } catch { return regime.value.created_at }
})

const conflictRuling = computed(() => {
  // Look for conflict ruling in latest allocation
  return latestData.value?.conflict_ruling ?? ''
})

const currentStanceLabel = computed(() => {
  const state = regime.value?.long_term_state
  if (!state) return '未知'
  if (['contraction', 'risk_rising'].includes(state)) return '防守'
  if (['expansion', 'recovery'].includes(state)) return '进攻'
  return '中性'
})

function stateLabel(state?: string): string {
  return state ? (REGIME_STATE_LABELS[state] ?? state) : '-'
}

const statusFootnote = computed(() => {
  if (!regimeMissingInputs.value.length) return ''
  return `缺失输入：${regimeMissingInputs.value.join('、')}`
})

function stateCardClass(state?: string): string {
  if (!state) return 'bg-[var(--panel-soft)]'
  const map: Record<string, string> = {
    expansion: 'bg-emerald-50 border-emerald-200 text-emerald-800',
    recovery: 'bg-teal-50 border-teal-200 text-teal-800',
    slowdown: 'bg-amber-50 border-amber-200 text-amber-800',
    volatile: 'bg-yellow-50 border-yellow-200 text-yellow-800',
    risk_rising: 'bg-orange-50 border-orange-200 text-orange-800',
    contraction: 'bg-red-50 border-red-200 text-red-800',
  }
  return map[state] ?? 'bg-[var(--panel-soft)] border-[var(--line)]'
}

function stateBadgeClass(state?: string): string {
  const base = 'inline-flex items-center rounded-full px-2.5 py-1 text-xs font-semibold border'
  const map: Record<string, string> = {
    expansion: 'bg-emerald-100 border-emerald-200 text-emerald-700',
    recovery: 'bg-teal-100 border-teal-200 text-teal-700',
    slowdown: 'bg-amber-100 border-amber-200 text-amber-700',
    volatile: 'bg-yellow-100 border-yellow-200 text-yellow-700',
    risk_rising: 'bg-orange-100 border-orange-200 text-orange-700',
    contraction: 'bg-red-100 border-red-200 text-red-700',
  }
  return `${base} ${map[state ?? ''] ?? 'bg-stone-100 border-stone-200 text-stone-600'}`
}

function actionTypeLabel(type: string): string {
  const map: Record<string, string> = {
    cash: '现金比例',
    risk_budget: '风险预算',
    theme: '主题集中度',
    defence: '防守动作',
  }
  return map[type] ?? type
}

function formatDate(s?: string): string {
  if (!s) return '-'
  try { return new Date(s).toLocaleDateString('zh-CN') } catch { return s }
}

const { data: suggestionData } = useQuery({
  queryKey: ['macro-regime-suggestion'],
  queryFn: fetchRegimeSuggestion,
  refetchInterval: 600_000,
})
const suggestion = computed(() => (suggestionData.value as any)?.suggestion ?? null)

const form = reactive({
  short_term_state: 'volatile',
  short_term_confidence: 0.7,
  medium_term_state: 'volatile',
  medium_term_confidence: 0.7,
  long_term_state: 'volatile',
  long_term_confidence: 0.7,
  short_term_change_reason: '',
  medium_term_change_reason: '',
  long_term_change_reason: '',
  short_term_changed: false,
  medium_term_changed: false,
  long_term_changed: false,
})

function applySuggestion() {
  if (!suggestion.value) return
  form.short_term_state = suggestion.value.short_term_state
  form.short_term_confidence = suggestion.value.short_term_confidence
  form.medium_term_state = suggestion.value.medium_term_state
  form.medium_term_confidence = suggestion.value.medium_term_confidence
  form.long_term_state = suggestion.value.long_term_state
  form.long_term_confidence = suggestion.value.long_term_confidence
  form.short_term_change_reason = `系统建议：${suggestion.value.basis}`
}

const submitPending = ref(false)
const submitError = ref('')
const submitSuccess = ref(false)

async function submitRegime() {
  submitPending.value = true
  submitError.value = ''
  submitSuccess.value = false
  try {
    const result = await recordRegime({ ...form })
    if (!result.ok) throw new Error(result.error || '提交失败')
    submitSuccess.value = true
    await queryClient.invalidateQueries({ queryKey: ['macro-regime-latest'] })
    await queryClient.invalidateQueries({ queryKey: ['macro-regime-history'] })
    await queryClient.invalidateQueries({ queryKey: ['macro-regime-workbench'] })
  } catch (e: any) {
    submitError.value = e?.message || '提交失败'
  } finally {
    submitPending.value = false
  }
}

// --- 长线复盘 outcome state ---
const OUTCOME_LABELS: Record<string, string> = {
  effective: '有效',
  partial: '部分有效',
  ineffective: '无效',
}

const editingOutcomeId = ref<string | null>(null)
const outcomeDraft = reactive({ notes: '', rating: '', correction: '' })
const outcomeSaving = ref(false)
const outcomeError = ref('')

function toggleOutcomeEdit(id: string) {
  if (editingOutcomeId.value === id) {
    editingOutcomeId.value = null
  } else {
    editingOutcomeId.value = id
    outcomeDraft.notes = ''
    outcomeDraft.rating = ''
    outcomeDraft.correction = ''
    outcomeError.value = ''
  }
}

function outcomeBadgeClass(rating?: string): string {
  const base = 'inline-flex items-center rounded-full px-2.5 py-1 text-xs font-semibold border'
  if (rating === 'effective') return `${base} bg-emerald-100 border-emerald-200 text-emerald-700`
  if (rating === 'partial') return `${base} bg-amber-100 border-amber-200 text-amber-700`
  if (rating === 'ineffective') return `${base} bg-red-100 border-red-200 text-red-700`
  return `${base} bg-stone-100 border-stone-200 text-stone-600`
}

async function submitOutcome(itemId: string) {
  outcomeSaving.value = true
  outcomeError.value = ''
  try {
    const result = await updateRegimeOutcome(
      itemId,
      outcomeDraft.notes,
      outcomeDraft.rating,
      outcomeDraft.correction,
    )
    if (!result.ok) throw new Error(result.error || '保存失败')
    editingOutcomeId.value = null
    await queryClient.invalidateQueries({ queryKey: ['macro-regime-history'] })
  } catch (e: any) {
    outcomeError.value = e?.message || '保存失败'
  } finally {
    outcomeSaving.value = false
  }
}
</script>
