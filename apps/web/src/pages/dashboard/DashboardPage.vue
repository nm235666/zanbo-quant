<template>
  <AppShell title="总控台" subtitle="把系统健康、研究优先级、任务编排与重点情报压进一个统一研究入口。">
    <div class="space-y-4">
      <PageSection title="核心状态" subtitle="先看系统是否足够稳，再看今天最值得优先研究的对象。">
        <StatePanel
          v-if="dashboardError"
          tone="danger"
          title="总控台加载失败"
          :description="dashboardError"
        >
          <template #action>
            <button class="rounded-2xl bg-stone-900 px-4 py-2 font-semibold text-white" @click="reload">重新加载</button>
          </template>
        </StatePanel>
        <StatePanel
          v-else-if="!dashboard && isFetching"
          title="总控台正在加载"
          description="正在拉取系统健康、任务回放和研究优先队列。"
        />
        <StatePanel
          v-else-if="!dashboard"
          tone="warning"
          title="总控台暂时没有数据"
          description="当前没有拿到总控数据，可以先重新加载，或直接进入数据源监控与数据库审计页。"
        >
          <template #action>
            <RouterLink to="/system/source-monitor" class="rounded-2xl bg-[var(--brand)] px-4 py-2 font-semibold text-white">数据源监控</RouterLink>
            <RouterLink to="/system/database-audit" class="rounded-2xl border border-[var(--line)] bg-white px-4 py-2 font-semibold text-[var(--ink)]">数据库审计</RouterLink>
          </template>
        </StatePanel>
        <div v-if="dashboard" class="grid gap-4 2xl:grid-cols-[1.05fr_0.95fr]">
          <div>
            <div class="mb-3 text-sm font-bold text-[var(--ink)]">系统核心状态</div>
            <div class="grid gap-3 xl:grid-cols-3 md:grid-cols-2">
              <StatCard title="上市股票" :value="dashboard.overview?.listed_total ?? 0" :hint="`总股票 ${dashboard.overview?.stock_total ?? 0}`" />
              <StatCard title="国际/国内新闻" :value="dashboard.overview?.news_total ?? 0" :hint="`个股新闻 ${dashboard.overview?.stock_news_total ?? 0}`" />
              <StatCard title="群聊记录" :value="dashboard.overview?.chatlog_total ?? 0" :hint="`群聊 ${dashboard.overview?.chatroom_total ?? 0}`" />
              <StatCard title="监控群聊" :value="dashboard.overview?.monitored_chatroom_total ?? 0" hint="纳入实时拉取与跨天补抓" />
              <StatCard title="候选池标的" :value="dashboard.overview?.candidate_total ?? 0" hint="来自群聊与信号聚合" />
              <StatCard title="日报总结" :value="dashboard.overview?.daily_summary_total ?? 0" :hint="`刷新于 ${formatDateTime(dashboard.generated_at)}`" />
            </div>
          </div>
          <div class="rounded-[24px] border border-[var(--line)] bg-[linear-gradient(180deg,rgba(15,97,122,0.08)_0%,rgba(255,255,255,0.82)_100%)] p-4 shadow-[var(--shadow-soft)]">
            <div class="text-sm font-bold text-[var(--ink)]">今日优先研究对象</div>
            <div class="mt-1 text-sm text-[var(--muted)]">优先判断评分领先标的、候选池和高重要新闻，减少在首页先看运维信息的成本。</div>
            <div class="mt-3 grid gap-3 md:grid-cols-3">
              <InfoCard
                v-for="item in priorityCards"
                :key="item.title"
                :title="item.title"
                :meta="item.meta"
                :description="item.description"
                class="cursor-pointer"
                @click="item.onClick?.()"
              >
                <template #badge>
                  <StatusBadge :value="item.badgeTone" :label="item.badgeLabel" />
                </template>
              </InfoCard>
            </div>
          </div>
        </div>
      </PageSection>

      <div class="grid gap-4 2xl:grid-cols-[1.3fr_0.7fr]">
        <PageSection title="研究优先队列" subtitle="今天最值得先看的股票、候选池和高重要新闻。">
          <div class="grid gap-4 xl:grid-cols-3">
            <div>
              <div class="mb-2 text-sm font-bold">评分领先股票</div>
              <div class="space-y-2">
                <InfoCard v-for="item in dashboard?.top_scores || []" :key="item.ts_code" :title="item.name || item.ts_code" :meta="`${item.ts_code || '-'} · ${item.industry || '-'} · ${item.market || '-'}`" class="cursor-pointer" @click="goStockDetail(item.ts_code)">
                  <template #badge>
                    <StatusBadge value="brand" :label="`总分 ${Number(item.industry_total_score ?? item.total_score ?? 0).toFixed(1)}`" />
                  </template>
                </InfoCard>
              </div>
            </div>
            <div>
              <div class="mb-2 text-sm font-bold">群聊候选池</div>
              <div class="space-y-2">
                <InfoCard v-for="item in dashboard?.candidate_pool_top || []" :key="item.candidate_name" :title="item.candidate_name || '-'" :meta="`${item.candidate_type || '-'} · 净分 ${item.net_score ?? 0} · 群数 ${item.room_count ?? 0}`" class="cursor-pointer" @click="goCandidate(item)">
                  <template #badge>
                    <StatusBadge :value="item.dominant_bias" :label="item.dominant_bias || '-'" />
                  </template>
                </InfoCard>
              </div>
            </div>
            <div>
              <div class="mb-2 text-sm font-bold">高重要新闻</div>
              <div class="space-y-2">
                <InfoCard v-for="item in dashboard?.important_news || []" :key="item.id" :title="item.title || '-'" :meta="`${item.source || '-'} · ${formatDateTime(item.pub_date)}`">
                  <template #badge>
                    <StatusBadge :value="item.llm_finance_importance || 'muted'" :label="item.llm_finance_importance || '未评级'" />
                  </template>
                </InfoCard>
              </div>
            </div>
          </div>
        </PageSection>

        <PageSection title="任务编排回放" subtitle="直接看最近任务状态，而不是只看抽象计数。">
          <div v-if="(dashboard?.orchestrator_alerts || []).length" class="mb-3 space-y-2">
            <InfoCard
              v-for="item in dashboard?.orchestrator_alerts || []"
              :key="`alert-${item.id}`"
              :title="item.message || item.job_key || '-'"
              :meta="`任务 ${item.job_key || '-'} · run_id ${item.run_id ?? '-'} · ${formatDateTime(item.created_at)}`"
            >
              <template #badge>
                <StatusBadge :value="item.severity || 'error'" :label="item.severity || 'error'" />
              </template>
            </InfoCard>
          </div>
          <div class="space-y-2">
            <InfoCard
              v-for="item in dashboard?.orchestrator_jobs || []"
              :key="item.id"
              :title="item.job_key || '-'"
              :meta="`开始 ${formatDateTime(item.started_at)} · 耗时 ${item.duration_seconds ?? '-'} 秒 · 退出码 ${item.exit_code ?? '-'}`"
            >
              <template #badge>
                <StatusBadge :value="item.status" :label="item.status || '-'" />
              </template>
            </InfoCard>
          </div>
        </PageSection>
      </div>

      <div class="grid gap-4 xl:grid-cols-2">
        <PageSection title="系统状态板" subtitle="数据库新鲜度、缺口、未评分与重复风险。">
          <div v-if="dashboard?.database_health" class="grid gap-3 xl:grid-cols-3 md:grid-cols-2">
            <StatCard title="日线最新" :value="formatDate(dashboard.database_health.daily_latest)" :hint="`分钟线 ${formatDate(dashboard.database_health.minline_latest)} · 评分 ${formatDate(dashboard.database_health.scores_latest)}`" />
            <StatCard title="事件/治理缺口" :value="`${dashboard.database_health.miss_events ?? '-'} / ${dashboard.database_health.miss_governance ?? '-'}`" :hint="`资金流 ${dashboard.database_health.miss_flow ?? '-'} · 分钟线 ${dashboard.database_health.miss_minline ?? '-'}`" />
            <StatCard title="新闻未评分" :value="dashboard.database_health.news_unscored ?? 0" :hint="`个股新闻 ${dashboard.database_health.stock_news_unscored ?? 0}`" />
            <StatCard title="新闻重复组" :value="dashboard.database_health.news_dup_link ?? 0" :hint="`个股新闻 ${dashboard.database_health.stock_news_dup_link ?? 0}`" />
            <StatCard title="宏观发布日期缺失" :value="dashboard.database_health.macro_publish_empty ?? 0" hint="越接近 0 越健康" />
            <InfoCard title="群聊去重风险" :meta="dupRiskMeta" :description="dupRiskDescription">
              <template #badge>
                <StatusBadge :value="dupRiskTone" :label="dupRiskLabel" />
              </template>
            </InfoCard>
          </div>
        </PageSection>

        <PageSection title="实时链路与数据源" subtitle="看关键数据源、实时链路、评分与日报系统是否在线。">
          <div class="mb-3 rounded-[18px] border border-[var(--line)] bg-white px-3 py-3">
            <div class="mb-2 flex items-center justify-between">
              <div class="text-sm font-bold text-[var(--ink)]">API 端口 build_id 一致性</div>
              <StatusBadge
                :value="dashboard?.api_stack_consistency?.all_ports_online && dashboard?.api_stack_consistency?.build_consistent ? 'success' : 'warning'"
                :label="dashboard?.api_stack_consistency?.all_ports_online && dashboard?.api_stack_consistency?.build_consistent ? '一致' : '存在偏差'"
              />
            </div>
            <div class="text-xs text-[var(--muted)]">
              期望 build_id：{{ dashboard?.api_stack_consistency?.expected_build_id || '-' }} · 实际集合：{{ (dashboard?.api_stack_consistency?.unique_build_ids || []).join(', ') || '-' }}
            </div>
            <div class="mt-2 grid gap-2 md:grid-cols-2">
              <div
                v-for="item in dashboard?.api_stack_consistency?.items || []"
                :key="`api-stack-${item.port}`"
                class="rounded-[14px] border border-[var(--line)] bg-[var(--panel-soft)] px-3 py-2 text-xs"
              >
                <div class="font-semibold">:{{ item.port }} · {{ item.ok ? '在线' : '离线' }}</div>
                <div class="mt-1 text-[var(--muted)]">build_id: {{ item.build_id || '-' }}</div>
                <div class="text-[var(--muted)]" v-if="item.error">错误: {{ item.error }}</div>
              </div>
            </div>
          </div>
          <div class="space-y-2">
            <InfoCard
              v-for="item in dashboard?.source_monitor?.sources || []"
              :key="item.key"
              :title="item.name || item.key"
              :meta="`${item.detail || '-'} · 最近更新 ${formatDateTime(item.last_update)}`"
            >
              <template #badge>
                <StatusBadge :value="item.status" :label="item.status_text || item.status || '-'" />
              </template>
            </InfoCard>
          </div>
        </PageSection>
      </div>

      <div class="grid gap-4 xl:grid-cols-[0.9fr_1.1fr]">
        <PageSection title="调度编排专区" subtitle="从首页直接看到最近任务和调度入口。">
          <div class="grid gap-3 md:grid-cols-2">
            <RouterLink to="/system/source-monitor" class="rounded-[20px] border border-[var(--line)] bg-white px-4 py-4 shadow-[var(--shadow-soft)]">
              <div class="font-semibold text-[var(--ink)]">数据源 / Worker / WS</div>
              <div class="mt-1 text-sm text-[var(--muted)]">排查实时链路、日志尾部和进程状态。</div>
            </RouterLink>
            <RouterLink to="/system/database-audit" class="rounded-[20px] border border-[var(--line)] bg-white px-4 py-4 shadow-[var(--shadow-soft)]">
              <div class="font-semibold text-[var(--ink)]">数据库审计</div>
              <div class="mt-1 text-sm text-[var(--muted)]">查看缺口、重复、未评分与陈旧数据。</div>
            </RouterLink>
            <RouterLink to="/intelligence/stock-news" class="rounded-[20px] border border-[var(--line)] bg-white px-4 py-4 shadow-[var(--shadow-soft)]">
              <div class="font-semibold text-[var(--ink)]">个股新闻积压</div>
              <div class="mt-1 text-sm text-[var(--muted)]">直接处理未评分个股新闻与采集动作。</div>
            </RouterLink>
            <RouterLink to="/intelligence/daily-summaries" class="rounded-[20px] border border-[var(--line)] bg-white px-4 py-4 shadow-[var(--shadow-soft)]">
              <div class="font-semibold text-[var(--ink)]">日报总结工作台</div>
              <div class="mt-1 text-sm text-[var(--muted)]">主动生成日报、查看模型链路与导出。</div>
            </RouterLink>
          </div>
        </PageSection>

        <PageSection title="页面新鲜度与直达入口" subtitle="优先打开最可能有问题、最需要人工介入的页面。">
          <div class="grid gap-3 md:grid-cols-2">
            <InfoCard title="新闻未评分" :meta="`国际/国内 ${dashboard?.database_health?.news_unscored ?? 0} · 个股 ${dashboard?.database_health?.stock_news_unscored ?? 0}`" description="如果这里持续偏大，优先去新闻页和个股新闻页处理。">
              <template #badge><StatusBadge :value="Number(dashboard?.database_health?.stock_news_unscored || 0) > 0 ? 'warning' : 'success'" :label="Number(dashboard?.database_health?.stock_news_unscored || 0) > 0 ? '待处理' : '健康'" /></template>
            </InfoCard>
            <InfoCard title="事件 / 治理 / 资金 / 分钟线缺口" :meta="`事件 ${dashboard?.database_health?.miss_events ?? '-'} · 治理 ${dashboard?.database_health?.miss_governance ?? '-'} · 资金 ${dashboard?.database_health?.miss_flow ?? '-'} · 分钟线 ${dashboard?.database_health?.miss_minline ?? '-'}`" description="缺口显著时先去数据库审计或数据源监控页。">
              <template #badge><StatusBadge value="info" label="数据补齐" /></template>
            </InfoCard>
          </div>
        </PageSection>
      </div>
    </div>
  </AppShell>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import { RouterLink, useRouter } from 'vue-router'
import AppShell from '../../shared/ui/AppShell.vue'
import PageSection from '../../shared/ui/PageSection.vue'
import StatCard from '../../shared/ui/StatCard.vue'
import StatusBadge from '../../shared/ui/StatusBadge.vue'
import InfoCard from '../../shared/ui/InfoCard.vue'
import StatePanel from '../../shared/ui/StatePanel.vue'
import { fetchDashboard } from '../../services/api/dashboard'
import { formatDate, formatDateTime } from '../../shared/utils/format'

const router = useRouter()
const { data, error, isFetching, refetch } = useQuery({
  queryKey: ['dashboard'],
  queryFn: fetchDashboard,
  refetchInterval: () => (document.visibilityState === 'visible' ? 60_000 : 180_000),
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
  if (dupRiskValue.value > 0) return '当前存在少量去重记录，先作为审计指标观察，不默认判定为首页异常故障。'
  return '当前没有明显的群聊去重风险。'
})
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
      onClick: topScore?.ts_code ? () => goStockDetail(topScore.ts_code) : undefined,
    },
    {
      title: topCandidate?.candidate_name || '暂无候选池热点',
      meta: topCandidate ? `${topCandidate.candidate_type || '-'} · 群数 ${topCandidate.room_count ?? 0}` : '候选池热点',
      description: topCandidate ? `净分 ${topCandidate.net_score ?? 0}` : '等待候选池数据',
      badgeTone: topCandidate?.dominant_bias || 'info',
      badgeLabel: topCandidate?.dominant_bias || '候选池',
      onClick: topCandidate ? () => goCandidate(topCandidate) : undefined,
    },
    {
      title: topNews?.title || '暂无高重要新闻',
      meta: topNews ? `${topNews.source || '-'} · ${formatDateTime(topNews.pub_date)}` : '资讯优先级',
      description: topNews ? '优先阅读这条高重要度新闻，判断是否影响今日研究路径。' : '等待新闻数据',
      badgeTone: topNews?.llm_finance_importance || 'muted',
      badgeLabel: topNews?.llm_finance_importance || '资讯',
      onClick: topNews ? () => router.push('/intelligence/stock-news') : undefined,
    },
  ]
})

function reload() {
  refetch()
}

function goStockDetail(tsCode: unknown) {
  const code = String(tsCode || '').trim()
  if (!code) return
  router.push({ path: `/stocks/detail/${encodeURIComponent(code)}` })
}

function goCandidate(item: Record<string, any>) {
  const name = String(item.candidate_name || '').trim()
  if (String(item.candidate_type || '').trim() === '主题') {
    router.push({ path: '/signals/themes', query: { keyword: name } })
    return
  }
  router.push({ path: '/chatrooms/candidates', query: { keyword: name } })
}
</script>
