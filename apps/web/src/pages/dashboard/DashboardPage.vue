<template>
  <AppShell title="总控台" subtitle="后台治理首页：先看系统健康、积压与告警，再进入监控、任务和审计。">
    <div class="space-y-4">
      <PageSection title="核心状态" subtitle="优先确认系统是否健康、数据是否可用，再决定要下钻哪个治理页。">
        <StatePanel
          v-if="dashboardError"
          tone="danger"
          title="总控台加载失败"
          :description="dashboardError"
        >
          <template #action>
            <button class="rounded-2xl bg-stone-900 px-4 py-2 font-semibold text-white hover:bg-stone-800 transition" @click="reload">重新加载</button>
          </template>
        </StatePanel>
        <div v-else-if="!dashboard && isFetching" class="space-y-3">
          <div class="loading-skeleton h-8 w-1/3 rounded-lg" />
          <div class="grid gap-3 md:grid-cols-3">
            <div v-for="idx in 3" :key="`dashboard-skeleton-${idx}`" class="loading-skeleton h-24 rounded-xl border border-[var(--line)]" />
          </div>
          <div class="loading-skeleton h-40 rounded-xl border border-[var(--line)]" />
        </div>
        <StatePanel
          v-else-if="!dashboard"
          tone="warning"
          title="总控台暂时没有数据"
          description="当前没有拿到首页摘要，可以先刷新，或直接进入数据库审计和任务调度中心。"
        >
          <template #action>
            <RouterLink to="/admin/system/database-audit" class="rounded-2xl bg-[var(--brand)] px-4 py-2 font-semibold text-white hover:bg-[var(--brand-ink)] transition">数据库审计</RouterLink>
            <RouterLink to="/admin/system/jobs-ops" class="rounded-2xl border border-[var(--line)] bg-white px-4 py-2 font-semibold text-[var(--ink)] hover:bg-gray-50 transition">任务调度中心</RouterLink>
          </template>
        </StatePanel>
        <div v-if="dashboard" class="grid gap-4 2xl:grid-cols-[1.05fr_0.95fr]">
          <!-- 系统速览 -->
          <div class="rounded-xl border border-[var(--line)] bg-white p-4 shadow-sm">
            <div class="mb-3 text-sm font-bold text-[var(--ink)]">系统速览</div>
            <div class="grid grid-cols-2 sm:flex sm:flex-wrap gap-2 text-xs">
              <span class="metric-chip">上市股票 <strong>{{ dashboard.overview?.listed_total ?? 0 }}</strong></span>
              <span class="metric-chip">新闻 <strong>{{ dashboard.overview?.news_total ?? 0 }}</strong></span>
              <span class="metric-chip">个股新闻 <strong>{{ dashboard.overview?.stock_news_total ?? 0 }}</strong></span>
              <span class="metric-chip">候选池 <strong>{{ dashboard.overview?.candidate_total ?? 0 }}</strong></span>
              <span class="metric-chip hidden sm:inline">日报 <strong>{{ dashboard.overview?.daily_summary_total ?? 0 }}</strong></span>
              <span class="metric-chip text-[var(--muted)]">{{ formatDateTime(dashboard.generated_at).slice(5) }}</span>
            </div>
          </div>
          <!-- 业务波动摘要 -->
          <div class="rounded-xl border border-[var(--line)] bg-gradient-to-b from-[rgba(15,97,122,0.06)] to-white p-4 shadow-sm">
            <div class="text-sm font-bold text-[var(--ink)]">业务波动摘要</div>
            <div class="mt-1 text-sm text-[var(--muted)]">总控台只摘要业务热点与异常线索，不承担研究主入口职责。</div>
            <div class="mt-3 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              <InfoCard
                v-for="item in priorityCards"
                :key="item.title"
                :title="item.title"
                :meta="item.meta"
                :description="item.description"
              >
                <template #badge>
                  <StatusBadge :value="item.badgeTone" :label="item.badgeLabel" />
                </template>
              </InfoCard>
            </div>
          </div>
        </div>
      </PageSection>

      <!-- 决策链路摘要 -->
      <PageSection title="决策链路摘要" subtitle="这里只做监控摘要，不直接承接研究决策动作。">
        <div class="grid gap-3 sm:grid-cols-3">
          <div class="rounded-xl border border-[var(--line)] bg-white px-4 py-4 shadow-sm">
            <div class="flex items-center justify-between">
              <div class="text-xs font-bold text-[var(--muted)] uppercase tracking-wide">风险指示</div>
              <StatusBadge :value="killSwitchTone" :label="killSwitchLabel" />
            </div>
            <div class="mt-2 text-sm font-semibold text-[var(--ink)]">{{ killSwitch.reason || '当前无风险备注' }}</div>
            <div class="mt-1 text-xs text-[var(--muted)]">若风险持续异常，应进入任务或审计页核查规则、数据和任务状态。</div>
          </div>
          <div class="rounded-xl border border-amber-200 bg-amber-50/60 px-4 py-4 shadow-sm">
            <div class="flex items-center justify-between">
              <div class="text-xs font-bold text-amber-700 uppercase tracking-wide">待处理动作摘要</div>
              <StatusBadge value="warning" :label="`${pendingActions.length} 项`" />
            </div>
            <div v-if="pendingActions.length" class="mt-2 space-y-1">
              <div v-for="action in pendingActions" :key="action.id" class="flex items-center gap-2 text-xs">
                <StatusBadge :value="decisionActionTone(action.action_type)" :label="decisionActionLabel(action.action_type)" />
                <span class="truncate font-semibold text-[var(--ink)]">{{ action.stock_name || action.ts_code || '-' }}</span>
                <span class="text-[var(--muted)] shrink-0">{{ String(action.created_at || '').slice(5, 16) }}</span>
              </div>
            </div>
            <div v-else class="mt-2 text-sm text-amber-700">暂无待处理观察/复核动作。</div>
          </div>
          <div class="rounded-xl border border-[var(--line)] bg-white px-4 py-4 shadow-sm">
            <div class="flex items-center justify-between">
              <div class="text-xs font-bold text-[var(--muted)] uppercase tracking-wide">最新动作留痕</div>
              <StatusBadge value="brand" :label="`${recentVerdicts.length} 条`" />
            </div>
            <div v-if="recentVerdicts.length" class="mt-2 space-y-1">
              <div v-for="action in recentVerdicts" :key="action.id" class="flex items-center gap-2 text-xs">
                <StatusBadge :value="decisionActionTone(action.action_type)" :label="decisionActionLabel(action.action_type)" />
                <span class="truncate font-semibold text-[var(--ink)]">{{ action.stock_name || action.ts_code || '-' }}</span>
              </div>
            </div>
            <div v-else class="mt-2 text-sm text-[var(--muted)]">暂无裁决动作记录。</div>
          </div>
        </div>
        <div class="mt-3 flex flex-wrap gap-2">
          <RouterLink to="/admin/system/jobs-ops" class="rounded-2xl bg-[var(--brand)] px-4 py-2 text-sm font-semibold text-white transition hover:bg-[var(--brand-ink)]">
            查看任务治理
          </RouterLink>
          <RouterLink to="/admin/system/database-audit" class="rounded-2xl border border-[var(--line)] bg-white px-4 py-2 text-sm font-semibold text-[var(--ink)] transition hover:border-[var(--brand)] hover:text-[var(--brand)]">
            查看数据审计
          </RouterLink>
        </div>
      </PageSection>

      <div class="grid gap-4 2xl:grid-cols-[1.35fr_0.65fr]">
        <PageSection title="业务热点摘要" subtitle="用于感知业务侧波动来源，不作为研究用户的工作台入口。">
          <div class="mb-3 flex flex-wrap gap-2">
            <button 
              class="rounded-full border px-3 py-2 text-xs font-semibold transition-all duration-200" 
              :class="queueTab==='scores' ? 'border-[var(--brand)] bg-[rgba(15,97,122,0.1)] text-[var(--brand)]' : 'border-[var(--line)] bg-white text-[var(--muted)] hover:border-[var(--brand)]/50'" 
              @click="queueTab='scores'"
            >
              评分领先
            </button>
            <button 
              class="rounded-full border px-3 py-2 text-xs font-semibold transition-all duration-200" 
              :class="queueTab==='candidates' ? 'border-[var(--brand)] bg-[rgba(15,97,122,0.1)] text-[var(--brand)]' : 'border-[var(--line)] bg-white text-[var(--muted)] hover:border-[var(--brand)]/50'" 
              @click="queueTab='candidates'"
            >
              候选池
            </button>
            <button 
              class="rounded-full border px-3 py-2 text-xs font-semibold transition-all duration-200" 
              :class="queueTab==='news' ? 'border-[var(--brand)] bg-[rgba(15,97,122,0.1)] text-[var(--brand)]' : 'border-[var(--line)] bg-white text-[var(--muted)] hover:border-[var(--brand)]/50'" 
              @click="queueTab='news'"
            >
              高重要新闻
            </button>
          </div>
          <TransitionGroup name="list" tag="div" class="space-y-2">
            <InfoCard
              v-for="item in activeQueueItems"
              :key="item.key"
              :title="item.title"
              :meta="item.meta"
              :description="item.description"
            >
              <template #badge>
                <StatusBadge :value="item.badgeValue" :label="item.badgeLabel" />
              </template>
            </InfoCard>
          </TransitionGroup>
        </PageSection>

        <PageSection title="治理快捷入口" subtitle="所有下一步动作都落在后台治理页，不再从这里借道研究页面。">
          <div class="grid gap-3">
            <RouterLink 
              v-for="item in quickLinks" 
              :key="item.to"
              :to="item.to" 
              class="group rounded-xl border border-[var(--line)] bg-white px-4 py-4 shadow-sm transition-all duration-200 hover:shadow-md hover:border-[var(--brand)]/30"
            >
              <div class="font-semibold text-[var(--ink)] group-hover:text-[var(--brand)] transition-colors">{{ item.title }}</div>
              <div class="mt-1 text-sm text-[var(--muted)] line-clamp-2">{{ item.desc }}</div>
            </RouterLink>
          </div>
        </PageSection>
      </div>

      <div class="grid gap-4 xl:grid-cols-[0.95fr_1.05fr]">
        <PageSection title="关键健康摘要" subtitle="首页只保留最值得立即处理的健康指标。">
          <div v-if="dashboard?.database_health" class="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
            <StatCard title="日线最新" :value="formatDate(dashboard.database_health.daily_latest)" :hint="`分钟线 ${formatDate(dashboard.database_health.minline_latest)}`" />
            <StatCard title="事件缺口" :value="dashboard.database_health.miss_events ?? 0" :hint="`治理: ${dashboard.database_health.miss_governance ?? 0}`" />
            <StatCard title="新闻未评分" :value="dashboard.database_health.news_unscored ?? 0" :hint="`个股: ${dashboard.database_health.stock_news_unscored ?? 0}`" />
            <StatCard title="新闻重复" :value="dashboard.database_health.news_dup_link ?? 0" :hint="`个股: ${dashboard.database_health.stock_news_dup_link ?? 0}`" />
            <StatCard title="宏观缺失" :value="dashboard.database_health.macro_publish_empty ?? 0" hint="越接近0越健康" />
            <InfoCard title="群聊去重" :meta="dupRiskMeta" :description="dupRiskDescription">
              <template #badge>
                <StatusBadge :value="dupRiskTone" :label="dupRiskLabel" />
              </template>
            </InfoCard>
          </div>
        </PageSection>

        <PageSection title="近期输出与治理提示" subtitle="保留业务沉淀摘要，用来辅助治理判断，而不是承接研究流转。">
          <div class="grid gap-3">
            <InfoCard 
              title="新闻未评分" 
              :meta="`国际/国内 ${dashboard?.database_health?.news_unscored ?? 0} · 个股 ${dashboard?.database_health?.stock_news_unscored ?? 0}`" 
              description="如果这里持续偏大，优先去新闻页和个股新闻页处理。"
            >
              <template #badge>
                <StatusBadge :value="Number(dashboard?.database_health?.stock_news_unscored || 0) > 0 ? 'warning' : 'success'" :label="Number(dashboard?.database_health?.stock_news_unscored || 0) > 0 ? '待处理' : '健康'" />
              </template>
            </InfoCard>
            <InfoCard 
              title="数据缺口监控" 
              :meta="`事件 ${dashboard?.database_health?.miss_events ?? '-'} · 治理 ${dashboard?.database_health?.miss_governance ?? '-'} · 资金 ${dashboard?.database_health?.miss_flow ?? '-'}`" 
              description="缺口显著时优先进入数据库审计或数据源监控页。"
            >
              <template #badge>
                <StatusBadge value="info" label="数据补齐" />
              </template>
            </InfoCard>
            <InfoCard
              v-for="item in recentSummaryCards"
              :key="item.key"
              :title="item.title"
              :meta="item.meta"
              :description="item.description"
            >
              <template #badge>
                <StatusBadge value="brand" label="日报沉淀" />
              </template>
            </InfoCard>
          </div>
        </PageSection>
      </div>
    </div>
  </AppShell>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import { RouterLink } from 'vue-router'
import AppShell from '../../shared/ui/AppShell.vue'
import PageSection from '../../shared/ui/PageSection.vue'
import StatCard from '../../shared/ui/StatCard.vue'
import StatusBadge from '../../shared/ui/StatusBadge.vue'
import InfoCard from '../../shared/ui/InfoCard.vue'
import StatePanel from '../../shared/ui/StatePanel.vue'
import { fetchDashboard } from '../../services/api/dashboard'
import { fetchDecisionActions, fetchDecisionKillSwitch } from '../../services/api/decision'
import { formatDate, formatDateTime } from '../../shared/utils/format'
import { useUiStore } from '../../stores/ui'

const ui = useUiStore()
const queueTab = ref<'scores' | 'candidates' | 'news'>('scores')

const { data, error, isFetching, refetch } = useQuery({
  queryKey: ['dashboard'],
  queryFn: fetchDashboard,
  refetchInterval: () => (document.visibilityState === 'visible' ? 60_000 : 180_000),
})

const { data: actionsData } = useQuery({
  queryKey: ['dashboard-actions'],
  queryFn: () => fetchDecisionActions({ limit: 10 }),
  staleTime: 120_000,
  refetchInterval: () => (document.visibilityState === 'visible' ? 120_000 : 600_000),
})

const { data: killSwitchData } = useQuery({
  queryKey: ['dashboard-killswitch'],
  queryFn: fetchDecisionKillSwitch,
  staleTime: 120_000,
  refetchInterval: () => (document.visibilityState === 'visible' ? 120_000 : 600_000),
})

const dashboard = computed(() => data.value)
const dashboardError = computed(() => error.value?.message || '')
const dupRiskValue = computed(() => Number(dashboard.value?.database_health?.chatlog_dup_key ?? 0))
const dupRiskTone = computed(() => {
  if (dupRiskValue.value >= 10) return 'warning'
  if (dupRiskValue.value > 0) return 'info'
  return 'success'
})
const dupRiskLabel = computed(() => {
  if (dupRiskValue.value >= 10) return '需排查'
  if (dupRiskValue.value > 0) return '轻微波动'
  return '健康'
})
const dupRiskMeta = computed(() => `当前值 ${dupRiskValue.value} · 仅超过阈值时视为显性风险`)
const dupRiskDescription = computed(() => {
  if (dupRiskValue.value >= 10) return '群聊去重指标已超过阈值，建议进入数据库审计页或群聊链路继续排查。'
  if (dupRiskValue.value > 0) return '当前存在少量去重记录，先作为审计指标观察。'
  return '当前没有明显的群聊去重风险。'
})

// Decision workbench computed
const recentActions = computed<Array<Record<string, any>>>(() => {
  const raw = actionsData.value
  if (!raw) return []
  if (Array.isArray(raw)) return raw
  return Array.isArray(raw.items) ? raw.items : []
})

const pendingActions = computed(() =>
  recentActions.value.filter((a) => ['watch', 'review'].includes(String(a.action_type || '').toLowerCase())).slice(0, 3),
)

const recentVerdicts = computed(() =>
  recentActions.value.filter((a) => ['confirm', 'reject', 'defer'].includes(String(a.action_type || '').toLowerCase())).slice(0, 3),
)

const killSwitch = computed<Record<string, any>>(() => (killSwitchData.value as any) || {})
const killSwitchAllowTrading = computed(() => Boolean(killSwitch.value.allow_trading ?? killSwitch.value.status === 'ACTIVE'))
const killSwitchTone = computed(() => (killSwitchAllowTrading.value ? 'success' : 'danger'))
const killSwitchLabel = computed(() => (killSwitchAllowTrading.value ? '交易正常' : '交易暂停'))

const ACTION_LABEL_MAP: Record<string, string> = { confirm: '确认', reject: '拒绝', defer: '暂缓', watch: '观察', review: '复核' }
const ACTION_TONE_MAP: Record<string, string> = { confirm: 'success', reject: 'danger', defer: 'warning', watch: 'info', review: 'muted' }
function decisionActionLabel(type: string) { return ACTION_LABEL_MAP[String(type || '').toLowerCase()] || String(type || '-') }
function decisionActionTone(type: string) { return ACTION_TONE_MAP[String(type || '').toLowerCase()] || 'muted' }

const quickLinks = [
  { to: '/admin/system/source-monitor', title: '数据源监控', desc: '排查实时链路、进程状态和 worker 健康度。' },
  { to: '/admin/system/jobs-ops', title: '任务调度中心', desc: '查看任务列表、dry-run、运行记录与告警。' },
  { to: '/admin/system/database-audit', title: '数据库审计', desc: '查看缺口、重复、未评分与陈旧数据。' },
  { to: '/admin/system/llm-providers', title: 'LLM 节点管理', desc: '排查 provider、限流、联通性与默认路由。' },
  { to: '/admin/system/users', title: '用户与权限', desc: '查看用户、配额、会话与角色分配状态。' },
]

const priorityCards = computed(() => {
  const topScore = dashboard.value?.top_scores?.[0]
  const topCandidate = dashboard.value?.candidate_pool_top?.[0]
  const topNews = dashboard.value?.important_news?.[0]
  return [
    {
      title: topScore?.name || topScore?.ts_code || '暂无评分领先股票',
      meta: topScore ? `${topScore.ts_code || '-'} · ${topScore.industry || '-'}` : '研究优先股票',
      description: topScore ? `行业内总分 ${Number(topScore.industry_total_score ?? topScore.total_score ?? 0).toFixed(1)}` : '等待评分数据',
      badgeTone: 'brand',
      badgeLabel: '评分领先',
    },
    {
      title: topCandidate?.candidate_name || '暂无候选池热点',
      meta: topCandidate ? `${topCandidate.candidate_type || '-'} · 群数 ${topCandidate.room_count ?? 0}` : '候选池热点',
      description: topCandidate ? `净分 ${topCandidate.net_score ?? 0}` : '等待候选池数据',
      badgeTone: topCandidate?.dominant_bias || 'info',
      badgeLabel: topCandidate?.dominant_bias || '候选池',
    },
    {
      title: topNews?.title || '暂无高重要新闻',
      meta: topNews ? `${topNews.source || '-'} · ${formatDateTime(topNews.pub_date)}` : '资讯优先级',
      description: topNews ? '这条资讯值得被后台重点观察，必要时再通知研究侧跟进。' : '等待新闻数据',
      badgeTone: topNews?.llm_finance_importance || 'muted',
      badgeLabel: topNews?.llm_finance_importance || '资讯',
    },
  ]
})

const activeQueueItems = computed(() => {
  if (queueTab.value === 'scores') {
    return (dashboard.value?.top_scores || []).slice(0, 10).map((item: Record<string, any>) => ({
      key: `score-${item.ts_code || item.name}`,
      title: item.name || item.ts_code || '-',
      meta: `${item.ts_code || '-'} · ${item.industry || '-'} · ${item.market || '-'}`,
      description: `行业内总分 ${Number(item.industry_total_score ?? item.total_score ?? 0).toFixed(1)}`,
      badgeValue: 'info',
      badgeLabel: `总分 ${Number(item.industry_total_score ?? item.total_score ?? 0).toFixed(1)}`,
    }))
  }
  if (queueTab.value === 'candidates') {
    return (dashboard.value?.candidate_pool_top || []).slice(0, 10).map((item: Record<string, any>) => ({
      key: `candidate-${item.candidate_name}`,
      title: item.candidate_name || '-',
      meta: `${item.candidate_type || '-'} · 群数 ${item.room_count ?? 0}`,
      description: `净分 ${item.net_score ?? 0}`,
      badgeValue: item.dominant_bias || 'muted',
      badgeLabel: item.dominant_bias || '-',
    }))
  }
  return (dashboard.value?.important_news || []).slice(0, 10).map((item: Record<string, any>) => ({
    key: `news-${item.id}`,
    title: item.title || '-',
    meta: `${item.source || '-'} · ${formatDateTime(item.pub_date)}`,
    description: '优先确认是否需要触发数据补齐、规则核查或人工复核。',
    badgeValue: item.llm_finance_importance || 'muted',
    badgeLabel: item.llm_finance_importance || '未评级',
  }))
})

const recentSummaryCards = computed(() =>
  (dashboard.value?.recent_daily_summaries || []).slice(0, 2).map((item: Record<string, any>) => ({
    key: `summary-${item.id}`,
    title: item.summary_date || '日报总结',
    meta: `${item.model || '-'} · ${item.created_at ? formatDateTime(item.created_at) : '-'}`,
    description: `新闻数 ${item.news_count ?? 0}，可直接进入日报页查看沉淀结果。`,
  })),
)

async function reload() {
  try {
    const result = await refetch()
    if (result.error) {
      ui.showToast('总控台刷新失败，请稍后重试', 'error')
      return
    }
    ui.showToast('总控台已刷新', 'success')
  } catch (err: any) {
    ui.showToast(err?.message || '总控台刷新失败', 'error')
  }
}

</script>

<style scoped>
.list-enter-active,
.list-leave-active {
  transition: all 0.2s ease;
}
.list-enter-from {
  opacity: 0;
  transform: translateX(-10px);
}
.list-leave-to {
  opacity: 0;
  transform: translateX(10px);
}

.metric-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.375rem 0.625rem;
  background-color: rgba(15, 97, 122, 0.06);
  border-radius: 9999px;
  color: var(--muted);
}
.metric-chip strong {
  color: var(--ink);
  font-weight: 600;
}
</style>
