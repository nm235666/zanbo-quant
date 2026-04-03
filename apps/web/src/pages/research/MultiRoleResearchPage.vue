<template>
  <AppShell title="多角色公司分析" subtitle="支持股票简称搜索、异步任务轮询、按角色查看和分角色下载。">
    <div class="space-y-4">
      <PageSection title="分析发起" subtitle="可以直接输 ts_code，也可以输股票简称，由前端自动解析第一条匹配结果。">
        <div class="grid gap-3 xl:grid-cols-[1fr_140px_180px] md:grid-cols-2">
          <input v-model="form.keyword" class="rounded-2xl border border-[var(--line)] bg-white px-4 py-3" placeholder="输入 ts_code 或简称，如 000001.SZ / 平安银行" />
          <select v-model.number="form.lookback" class="rounded-2xl border border-[var(--line)] bg-white px-4 py-3">
            <option :value="60">60 日</option>
            <option :value="120">120 日</option>
            <option :value="240">240 日</option>
          </select>
          <button class="rounded-2xl bg-[var(--brand)] px-4 py-3 font-semibold text-white" :disabled="isPending" @click="runAnalysis">
            {{ isPending ? '任务创建中...' : '发起分析' }}
          </button>
        </div>
        <label class="mt-3 flex items-center gap-2 text-sm text-[var(--muted)]">
          <input v-model="acceptAutoDegrade" type="checkbox" />
          允许自动降级完成（失败角色不阻塞全局汇总）
        </label>
        <div class="mt-3 rounded-[20px] border border-[var(--line)] bg-[linear-gradient(180deg,rgba(255,255,255,0.9)_0%,rgba(238,244,247,0.78)_100%)] px-4 py-3 text-sm text-[var(--muted)] shadow-[var(--shadow-soft)]">
          {{ actionMessage }}
        </div>
        <div class="mt-2 text-sm text-[var(--muted)]">实际模型：{{ usedModel }}</div>
        <div v-if="attemptChain" class="mt-1 text-sm text-[var(--muted)]">尝试链路：{{ attemptChain }}</div>
        <div v-if="quotaHint" class="mt-1 text-sm text-[var(--muted)]">今日额度：{{ quotaHint }}</div>
        <div v-if="pendingDecision" class="mt-3 rounded-2xl border border-amber-300 bg-amber-50 px-4 py-3 text-sm text-amber-900">
          <div>有角色任务失败，等待你的决策：重试 / 降级 / 终止。</div>
          <div class="mt-2 flex flex-wrap gap-2">
            <button class="rounded-xl bg-[var(--brand)] px-3 py-2 text-white" :disabled="decisionPending" @click="submitDecision('retry')">重试失败角色</button>
            <button class="rounded-xl bg-stone-700 px-3 py-2 text-white" :disabled="decisionPending" @click="submitDecision('degrade')">降级并继续汇总</button>
            <button class="rounded-xl bg-red-700 px-3 py-2 text-white" :disabled="decisionPending" @click="submitDecision('abort')">终止任务</button>
          </div>
        </div>
      </PageSection>

      <PageSection title="子任务进度" subtitle="每个角色独立执行，状态可单独追踪。">
        <div v-if="roleRuns.length" class="space-y-2">
          <div v-for="item in roleRuns" :key="item.role" class="rounded-xl border border-[var(--line)] bg-white px-3 py-2 text-sm">
            <div class="flex items-center justify-between gap-2">
              <div class="font-semibold">{{ item.role }}</div>
              <div class="text-[var(--muted)]">{{ item.status || '-' }}</div>
            </div>
            <div class="mt-1 text-[var(--muted)]">
              模型：{{ item.used_model || item.requested_model || '-' }} · 重试 {{ item.retry_count || 0 }} 次 · 耗时 {{ item.duration_ms || 0 }}ms
            </div>
            <div v-if="item.error" class="mt-1 text-red-600">错误：{{ item.error }}</div>
          </div>
        </div>
        <div v-else class="text-sm text-[var(--muted)]">尚未启动角色子任务。</div>
      </PageSection>

      <PageSection title="角色视图" subtitle="优先展示按角色切分后的结论，也保留完整原文。">
        <template #action>
          <div class="flex flex-wrap gap-2">
            <button
              class="rounded-2xl bg-emerald-700 px-4 py-2 text-white"
              :disabled="!canRetryAggregate || aggregateRetryPending"
              @click="retryAggregate"
            >
              {{ aggregateRetryPending ? '重试汇总中...' : '重试汇总' }}
            </button>
            <button class="rounded-2xl bg-stone-800 px-4 py-2 text-white" :disabled="!selectedRoleSection" @click="downloadRoleMarkdown">下载当前角色 Markdown</button>
            <button class="rounded-2xl bg-blue-700 px-4 py-2 text-white" :disabled="!fullMarkdown" @click="downloadFullMarkdown">下载完整 Markdown</button>
          </div>
        </template>
        <div v-if="roleSections.length" class="mb-4 flex flex-wrap gap-2">
          <button
            v-for="item in roleSections"
            :key="item.role"
            class="rounded-2xl px-4 py-2 text-sm font-semibold text-white"
            :class="activeRole === item.role ? 'bg-[var(--brand)]' : 'bg-stone-800'"
            @click="activeRole = item.role"
          >
            {{ item.role }}
          </button>
        </div>
        <MarkdownBlock :content="selectedRoleContent" />
      </PageSection>

      <PageSection title="公共结论" subtitle="统一展示置信度、风险复核和行动视图。">
        <div class="grid gap-3 xl:grid-cols-3 md:grid-cols-1">
          <InfoCard title="决策置信度" :description="decisionConfidenceSummary" :meta="decisionConfidenceMeta" />
          <InfoCard title="风险复核" :meta="riskReviewMeta">
            <div class="markdown-compact" v-html="riskReviewHtml" />
          </InfoCard>
          <InfoCard title="行动视图" :meta="portfolioViewMeta">
            <div class="markdown-compact" v-html="portfolioViewHtml" />
          </InfoCard>
        </div>
        <div v-if="usedContextDims.length" class="mt-3 flex flex-wrap gap-2">
          <span v-for="item in usedContextDims" :key="item" class="metric-chip">{{ item }}</span>
        </div>
      </PageSection>

      <PageSection title="风控与通知" subtitle="展示 pre-trade 风控校验结果和通知发送状态。">
        <div class="grid gap-3 xl:grid-cols-2 md:grid-cols-1">
          <InfoCard
            title="Pre-trade 风控"
            :description="riskCheckDescription"
            :meta="riskCheckMeta"
          />
          <InfoCard
            title="通知发送"
            :description="notificationDescription"
            :meta="notificationMeta"
          />
        </div>
      </PageSection>

      <PageSection title="公共结论 / 完整原文" subtitle="如果角色切分不够完整，仍然可以回到完整 Markdown 原文。">
        <MarkdownBlock :content="fullMarkdown" />
      </PageSection>
    </div>
  </AppShell>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, reactive, ref } from 'vue'
import { useMutation, useQuery } from '@tanstack/vue-query'
import MarkdownIt from 'markdown-it'
import AppShell from '../../shared/ui/AppShell.vue'
import PageSection from '../../shared/ui/PageSection.vue'
import MarkdownBlock from '../../shared/markdown/MarkdownBlock.vue'
import InfoCard from '../../shared/ui/InfoCard.vue'
import { decideMultiRoleTaskV2, fetchMultiRoleTaskV2, fetchStocks, retryMultiRoleAggregateV2, streamMultiRoleTaskV2, triggerMultiRoleTaskV2 } from '../../services/api/stocks'
import { fetchAuthStatus } from '../../services/api/auth'

function looksLikeTsCode(value: string) {
  return /^[0-9A-Z]{6}\.(SZ|SH|BJ)$/i.test(value.trim())
}

function downloadText(content: string, filename: string) {
  const blob = new Blob([content], { type: 'text/markdown;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  link.remove()
  setTimeout(() => URL.revokeObjectURL(url), 1000)
}

const form = reactive({ keyword: '000001.SZ', lookback: 120 })
const fullMarkdown = ref('等待发起分析...')
const actionMessage = ref('准备就绪')
const roleSections = ref<Array<Record<string, any>>>([])
const activeRole = ref('')
const usedModel = ref('')
const attempts = ref<Array<Record<string, any>>>([])
const resolvedStock = ref<{ ts_code: string; name: string }>({ ts_code: '', name: '' })
const decisionConfidence = ref<Record<string, any>>({})
const riskReview = ref<Record<string, any>>({})
const portfolioView = ref<Record<string, any>>({})
const usedContextDims = ref<string[]>([])
const preTradeCheck = ref<Record<string, any>>({})
const notification = ref<Record<string, any>>({})
const roleRuns = ref<Array<Record<string, any>>>([])
const aggregatorRun = ref<Record<string, any>>({})
const acceptAutoDegrade = ref(true)
const currentJobId = ref('')
const taskStatus = ref('')
const decisionPending = ref(false)
const aggregateRetryPending = ref(false)
let timer = 0
let streamController: AbortController | null = null

const selectedRoleSection = computed(() => roleSections.value.find((item) => item.role === activeRole.value) || null)
const selectedRoleContent = computed(() => selectedRoleSection.value?.content || fullMarkdown.value)
const attemptChain = computed(() => attempts.value.map((item) => `${item.model || '-'}${item.error ? '×' : '√'}`).join(' -> '))
const riskCheckDescription = computed(() => {
  if (!Object.keys(preTradeCheck.value).length) return '未启用或暂无风控校验结果。'
  const reasons = Array.isArray(preTradeCheck.value.reasons) ? preTradeCheck.value.reasons : []
  if (reasons.length) return reasons.join('；')
  return preTradeCheck.value.allowed ? '通过校验，可进入后续模拟执行。' : '未通过校验，请先检查约束。'
})
const riskCheckMeta = computed(() => {
  if (!Object.keys(preTradeCheck.value).length) return '-'
  const checks = Array.isArray(preTradeCheck.value.checks) ? preTradeCheck.value.checks.length : 0
  return `${preTradeCheck.value.allowed ? 'allowed' : 'blocked'} · checks ${checks}`
})
const notificationDescription = computed(() => {
  if (!Object.keys(notification.value).length) return '未启用通知或本次未触发。'
  if (notification.value.ok) return '通知已发送。'
  if (notification.value.skipped) return `通知未发送：${notification.value.reason || 'skipped'}`
  return `通知失败：${notification.value.error || 'unknown error'}`
})
const notificationMeta = computed(() => {
  if (!Object.keys(notification.value).length) return '-'
  if (notification.value.ok) return 'ok'
  if (notification.value.skipped) return 'skipped'
  return 'error'
})
const pendingDecision = computed(() => taskStatus.value === 'pending_user_decision')
const markdown = new MarkdownIt({ html: false, linkify: true, breaks: true })
function normalizeSummary(value: unknown, fallback: string) {
  const text = String(value || '').trim()
  return text || fallback
}
const decisionConfidenceSummary = computed(() => normalizeSummary(decisionConfidence.value.summary, '原始分析未稳定提供数值化置信度。'))
const decisionConfidenceMeta = computed(() => {
  const label = String(decisionConfidence.value.label || '').trim()
  if (!label || label === '无' || label.toLowerCase() === 'none' || label.toLowerCase() === 'markdown') return '未显式给出'
  return label
})
const riskReviewText = computed(() => normalizeSummary(riskReview.value.summary, '暂无结构化风险复核'))
const riskReviewMeta = computed(() => {
  const source = String(riskReview.value.source || '').trim()
  if (!source || source.toLowerCase() === 'markdown') return '结构化摘要'
  return source
})
const riskReviewHtml = computed(() => markdown.render(riskReviewText.value))
const portfolioViewText = computed(() => normalizeSummary(portfolioView.value.summary, '暂无结构化行动视图'))
const portfolioViewMeta = computed(() => {
  const source = String(portfolioView.value.source || '').trim()
  if (!source || source.toLowerCase() === 'markdown') return '结构化摘要'
  return source
})
const portfolioViewHtml = computed(() => markdown.render(portfolioViewText.value))
const canRetryAggregate = computed(() => {
  const status = taskStatus.value
  const aggStatus = String(aggregatorRun.value?.status || '')
  return Boolean(currentJobId.value) && (status === 'done' || status === 'done_with_warnings') && aggStatus === 'error'
})
const { data: authStatus, refetch: refetchAuthStatus } = useQuery({
  queryKey: ['auth-status-multi-role-page'],
  queryFn: () => fetchAuthStatus(true),
  staleTime: 10_000,
})
const quotaHint = computed(() => {
  const q = authStatus.value?.multi_role_quota as any
  if (!q) return ''
  if (q.limit == null) return '不限'
  return `${q.used ?? 0} / ${q.limit}，剩余 ${q.remaining ?? 0}`
})

function clearTimer() {
  window.clearTimeout(timer)
  timer = 0
}

function stopLiveStream() {
  if (streamController) {
    streamController.abort()
    streamController = null
  }
}

function resetResultViews() {
  roleSections.value = []
  activeRole.value = ''
  usedModel.value = ''
  attempts.value = []
  decisionConfidence.value = {}
  riskReview.value = {}
  portfolioView.value = {}
  usedContextDims.value = []
  preTradeCheck.value = {}
  notification.value = {}
}

function applyTaskSnapshot(task: Record<string, any>, resolved?: { ts_code: string; name: string }) {
  taskStatus.value = String(task.status || '')
  roleRuns.value = Array.isArray(task.role_runs) ? task.role_runs : []
  aggregatorRun.value = (task.aggregator_run || {}) as Record<string, any>
  attempts.value = Array.isArray(task.attempts) ? task.attempts : attempts.value

  if (task.status === 'done' || task.status === 'done_with_warnings') {
    usedModel.value = String(task.used_model || task.model || usedModel.value || '')
    fullMarkdown.value = task.analysis_markdown || task.analysis || task.result || fullMarkdown.value || '分析完成，但未返回正文。'
    roleSections.value = Array.isArray(task.role_outputs) ? task.role_outputs : (Array.isArray(task.role_sections) ? task.role_sections : roleSections.value)
    activeRole.value = roleSections.value[0]?.role || activeRole.value
    decisionConfidence.value = (task.decision_confidence || {}) as Record<string, any>
    riskReview.value = (task.risk_review || {}) as Record<string, any>
    portfolioView.value = (task.portfolio_view || {}) as Record<string, any>
    usedContextDims.value = Array.isArray(task.used_context_dims) ? task.used_context_dims : []
    preTradeCheck.value = (task.pre_trade_check || {}) as Record<string, any>
    notification.value = (task.notification || {}) as Record<string, any>
    actionMessage.value = `分析完成：${task.name || resolved?.name || resolved?.ts_code || resolvedStock.value.name || resolvedStock.value.ts_code}${task.status === 'done_with_warnings' ? '（含降级告警）' : ''}${usedModel.value ? ` · 实际模型 ${usedModel.value}` : ''}`
    return true
  }
  if (task.status === 'pending_user_decision') {
    actionMessage.value = '有角色任务失败，等待你的决策（重试/降级/终止）。'
    return true
  }
  if (task.status === 'error') {
    actionMessage.value = `分析失败：${task.error || task.message || '未知错误'}`
    fullMarkdown.value = `分析失败：${task.error || task.message || '未知错误'}`
    resetResultViews()
    return true
  }
  actionMessage.value = `任务运行中：${task.progress || 0}% · ${task.message || task.status || '运行中'}`
  return false
}

function startPolling(jobId: string, resolved?: { ts_code: string; name: string }) {
  clearTimer()
  const poll = async (): Promise<void> => {
    try {
      const task = await fetchMultiRoleTaskV2({ job_id: jobId })
      const terminal = applyTaskSnapshot(task as Record<string, any>, resolved)
      if (!terminal) timer = window.setTimeout(poll, 3000)
    } catch (error: any) {
      actionMessage.value = `轮询失败：${error?.message || String(error)}`
    }
  }
  poll()
}

function startLiveStream(jobId: string, resolved?: { ts_code: string; name: string }) {
  clearTimer()
  stopLiveStream()
  const controller = new AbortController()
  streamController = controller
  streamMultiRoleTaskV2(
    { job_id: jobId, interval_ms: 1000, timeout_seconds: 180 },
    {
      signal: controller.signal,
      onMessage: (packet: Record<string, any>) => {
        const event = String(packet?.event || '')
        if (event === 'update' && packet?.job) {
          const terminal = applyTaskSnapshot(packet.job as Record<string, any>, resolved)
          if (terminal) controller.abort()
          return
        }
        if (event === 'timeout') {
          actionMessage.value = '流式连接超时，切换轮询继续跟踪...'
          controller.abort()
          startPolling(jobId, resolved)
          return
        }
        if (event === 'error') {
          actionMessage.value = `流式更新失败：${packet?.error || 'unknown error'}，切换轮询继续跟踪...`
          controller.abort()
          startPolling(jobId, resolved)
        }
      },
    },
  ).catch((error: any) => {
    if (controller.signal.aborted) return
    actionMessage.value = `流式更新中断：${error?.message || String(error)}，切换轮询继续跟踪...`
    startPolling(jobId, resolved)
  }).finally(() => {
    if (streamController === controller) streamController = null
  })
}

const mutation = useMutation({
  mutationFn: async () => {
    const raw = form.keyword.trim()
    if (!raw) throw new Error('请输入股票代码或简称')
    if (looksLikeTsCode(raw)) {
      return { ts_code: raw.toUpperCase(), name: '' }
    }
    const searchResult = await fetchStocks({ keyword: raw, status: 'L', page: 1, page_size: 5 })
    const first = searchResult.items?.[0]
    if (!first?.ts_code) throw new Error(`未找到匹配股票：${raw}`)
    return { ts_code: String(first.ts_code), name: String(first.name || '') }
  },
  onSuccess: async (resolved) => {
    stopLiveStream()
    clearTimer()
    resolvedStock.value = resolved
    resetResultViews()
    roleRuns.value = []
    aggregatorRun.value = {}
    taskStatus.value = ''
    currentJobId.value = ''
    actionMessage.value = `已解析股票：${resolved.name || resolved.ts_code}，正在创建分析任务...`
    const payload = await triggerMultiRoleTaskV2({
      ts_code: resolved.ts_code,
      lookback: form.lookback,
      accept_auto_degrade: acceptAutoDegrade.value,
    })
    const jobId = String(payload.job_id || '')
    currentJobId.value = jobId
    fullMarkdown.value = '任务已创建，正在后台生成分析...'
    const terminal = applyTaskSnapshot(payload as Record<string, any>, resolved)
    if (!terminal && jobId) startLiveStream(jobId, resolved)
    refetchAuthStatus()
  },
  onError: (error: Error) => {
    stopLiveStream()
    clearTimer()
    actionMessage.value = `分析失败：${error.message}`
    fullMarkdown.value = `分析失败：${error.message}`
    resetResultViews()
    roleRuns.value = []
    aggregatorRun.value = {}
    taskStatus.value = ''
    currentJobId.value = ''
  },
})

const isPending = computed(() => mutation.isPending.value)

function runAnalysis() {
  mutation.mutate()
}

async function submitDecision(action: 'retry' | 'degrade' | 'abort') {
  if (!currentJobId.value || decisionPending.value) return
  decisionPending.value = true
  try {
    const res = await decideMultiRoleTaskV2({ job_id: currentJobId.value, action })
    const terminal = applyTaskSnapshot(res as Record<string, any>, resolvedStock.value)
    if (action === 'abort' || res.status === 'error') {
      actionMessage.value = `任务已终止：${res.error || '用户终止'}`
      fullMarkdown.value = `任务已终止：${res.error || '用户终止'}`
      return
    }
    actionMessage.value = action === 'degrade' ? '正在按降级策略收口汇总...' : '正在执行补重试，请稍候...'
    if (!terminal && currentJobId.value) startLiveStream(currentJobId.value, resolvedStock.value)
  } catch (error: any) {
    actionMessage.value = `决策提交失败：${error?.message || String(error)}`
  } finally {
    decisionPending.value = false
  }
}

async function retryAggregate() {
  if (!currentJobId.value || aggregateRetryPending.value || !canRetryAggregate.value) return
  aggregateRetryPending.value = true
  actionMessage.value = '正在重试聚合汇总，请稍候...'
  try {
    const res = await retryMultiRoleAggregateV2({ job_id: currentJobId.value })
    const terminal = applyTaskSnapshot(res as Record<string, any>, resolvedStock.value)
    const aggStatus = String((res.aggregator_run || {}).status || '')
    actionMessage.value = aggStatus === 'done' ? '汇总重试成功。' : '汇总重试失败，已保留角色原文。'
    if (!terminal && currentJobId.value) startLiveStream(currentJobId.value, resolvedStock.value)
  } catch (error: any) {
    actionMessage.value = `重试汇总失败：${error?.message || String(error)}`
  } finally {
    aggregateRetryPending.value = false
  }
}

function downloadRoleMarkdown() {
  if (!selectedRoleSection.value) return
  const stock = resolvedStock.value.ts_code || 'UNKNOWN'
  downloadText(selectedRoleSection.value.content || '', `${stock}_${selectedRoleSection.value.role}_多角色分析.md`)
}

function downloadFullMarkdown() {
  const stock = resolvedStock.value.ts_code || 'UNKNOWN'
  downloadText(fullMarkdown.value || '', `${stock}_LLM多角色公司分析.md`)
}

onBeforeUnmount(() => {
  stopLiveStream()
  clearTimer()
})
</script>

<style scoped>
.markdown-compact :deep(p),
.markdown-compact :deep(ul),
.markdown-compact :deep(ol) {
  margin: 0;
}

.markdown-compact :deep(p + p),
.markdown-compact :deep(ul + p),
.markdown-compact :deep(p + ul),
.markdown-compact :deep(ol + p),
.markdown-compact :deep(p + ol) {
  margin-top: 0.5rem;
}

.markdown-compact :deep(ul),
.markdown-compact :deep(ol) {
  padding-left: 1rem;
}

.markdown-compact :deep(li + li) {
  margin-top: 0.25rem;
}
</style>
