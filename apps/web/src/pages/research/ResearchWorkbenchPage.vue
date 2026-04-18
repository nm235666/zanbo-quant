<template>
  <AppShell title="研究工作台" subtitle="量化投研指挥中心：今日重点、待处理动作、风险预警与最近决策一览。">
    <div class="space-y-4">
      <!-- Hero header with CTA -->
      <div class="flex flex-wrap items-center justify-between gap-3">
        <div class="text-sm text-[var(--muted)]">
          {{ todayDateLabel }}
        </div>
        <RouterLink
          to="/research/decision"
          class="rounded-2xl bg-[var(--brand)] px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:opacity-90"
        >
          进入决策工作台 →
        </RouterLink>
      </div>

      <!-- 今日重点 -->
      <PageSection title="今日重点" subtitle="当前重点研究方向与核心链接。">
        <div class="grid gap-3 sm:grid-cols-3">
          <InfoCard
            title="市场结论"
            meta="今日交易主线"
            description="查看宏观+行业+新闻汇总后的今日交易结论，包含候选方向与风险提示。"
          >
            <RouterLink
              to="/market/conclusion"
              class="mt-2 inline-flex items-center rounded-full border border-[var(--line)] bg-white px-3 py-1 text-xs font-semibold text-[var(--ink)] transition hover:border-[var(--brand)] hover:text-[var(--brand)]"
            >
              查看市场结论 →
            </RouterLink>
          </InfoCard>
          <InfoCard
            title="候选漏斗"
            meta="候选股票全周期管理"
            description="从进入到确认的完整漏斗，查看各阶段候选数量与最新流转记录。"
          >
            <RouterLink
              to="/research/funnel"
              class="mt-2 inline-flex items-center rounded-full border border-[var(--line)] bg-white px-3 py-1 text-xs font-semibold text-[var(--ink)] transition hover:border-[var(--brand)] hover:text-[var(--brand)]"
            >
              查看候选漏斗 →
            </RouterLink>
          </InfoCard>
          <InfoCard
            title="多角色分析"
            meta="AI驱动深度分析"
            description="宏观、股票、行业、汇率、国际、风险六角色协同分析，支持任务异步跟踪。"
          >
            <RouterLink
              to="/research/multi-role"
              class="mt-2 inline-flex items-center rounded-full border border-[var(--line)] bg-white px-3 py-1 text-xs font-semibold text-[var(--ink)] transition hover:border-[var(--brand)] hover:text-[var(--brand)]"
            >
              发起分析 →
            </RouterLink>
          </InfoCard>
        </div>
      </PageSection>

      <!-- 待处理动作 -->
      <PageSection title="待处理动作" subtitle="需要你审批或跟进的任务。">
        <template #action>
          <RouterLink
            to="/research/task-inbox"
            class="rounded-2xl border border-[var(--line)] bg-white px-3 py-2 text-xs font-semibold text-[var(--ink)] transition hover:border-[var(--brand)] hover:text-[var(--brand)]"
          >
            任务收件箱
          </RouterLink>
        </template>

        <div v-if="actionsLoading" class="py-6 text-center text-sm text-[var(--muted)]">加载中...</div>
        <div v-else-if="actionsError" class="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
          加载待处理动作失败，请刷新页面重试。
        </div>
        <div v-else-if="pendingActions.length === 0" class="rounded-2xl border border-dashed border-[var(--line)] bg-gray-50 px-4 py-6 text-center">
          <div class="text-sm font-semibold text-[var(--ink)]">暂无待处理动作</div>
          <div class="mt-1 text-xs text-[var(--muted)]">所有任务已处理，或尚未发起分析任务。</div>
          <div class="mt-3 flex justify-center gap-2">
            <RouterLink to="/research/multi-role" class="rounded-full border border-[var(--brand)] bg-white px-4 py-2 text-xs font-semibold text-[var(--brand)]">
              发起多角色分析
            </RouterLink>
            <RouterLink to="/research/decision" class="rounded-full border border-[var(--line)] bg-white px-4 py-2 text-xs font-semibold text-[var(--ink)]">
              打开决策看板
            </RouterLink>
          </div>
        </div>
        <div v-else class="divide-y divide-[var(--line)]">
          <div
            v-for="action in pendingActions"
            :key="action.id"
            class="flex flex-wrap items-center justify-between gap-2 py-3"
          >
            <div class="min-w-0">
              <div class="text-sm font-semibold text-[var(--ink)]">{{ action.ts_code }} <span v-if="action.stock_name" class="font-normal text-[var(--muted)]">{{ action.stock_name }}</span></div>
              <div v-if="action.note" class="mt-0.5 text-xs text-[var(--muted)] truncate max-w-xs">{{ action.note }}</div>
            </div>
            <div class="flex items-center gap-2">
              <StatusBadge :value="action.action_type" />
              <RouterLink
                to="/research/decision"
                class="rounded-full border border-[var(--line)] bg-white px-3 py-1 text-xs font-semibold text-[var(--ink)] transition hover:border-[var(--brand)] hover:text-[var(--brand)]"
              >
                处理
              </RouterLink>
            </div>
          </div>
        </div>
      </PageSection>

      <!-- 风险预警 -->
      <PageSection title="风险预警" subtitle="当前异常信号与系统风险提示。">
        <template #action>
          <RouterLink
            to="/signals/overview"
            class="rounded-2xl border border-[var(--line)] bg-white px-3 py-2 text-xs font-semibold text-[var(--ink)] transition hover:border-[var(--brand)] hover:text-[var(--brand)]"
          >
            查看信号图谱
          </RouterLink>
        </template>
        <div class="rounded-2xl border border-dashed border-[var(--line)] bg-gray-50 px-4 py-6 text-center">
          <div class="text-sm font-semibold text-emerald-700">系统正常，暂无异常风险信号</div>
          <div class="mt-1 text-xs text-[var(--muted)]">数据源与信号链路均正常运行。</div>
          <div class="mt-3 flex justify-center gap-2">
            <RouterLink to="/system/source-monitor" class="rounded-full border border-[var(--line)] bg-white px-4 py-2 text-xs font-semibold text-[var(--ink)]">
              查看数据源监控
            </RouterLink>
            <RouterLink to="/signals/overview" class="rounded-full border border-[var(--line)] bg-white px-4 py-2 text-xs font-semibold text-[var(--ink)]">
              查看信号总览
            </RouterLink>
          </div>
        </div>
      </PageSection>

      <!-- 最近决策 -->
      <PageSection title="最近决策" subtitle="最近录入的决策动作记录。">
        <template #action>
          <RouterLink
            to="/research/decision"
            class="rounded-2xl border border-[var(--line)] bg-white px-3 py-2 text-xs font-semibold text-[var(--ink)] transition hover:border-[var(--brand)] hover:text-[var(--brand)]"
          >
            查看完整决策历史
          </RouterLink>
        </template>
        <div v-if="actionsLoading" class="py-4 text-center text-sm text-[var(--muted)]">加载中...</div>
        <div v-else-if="recentDecisions.length === 0" class="rounded-2xl border border-dashed border-[var(--line)] px-4 py-6 text-center text-sm text-[var(--muted)]">
          暂无决策记录
        </div>
        <div v-else class="divide-y divide-[var(--line)]">
          <div
            v-for="d in recentDecisions"
            :key="d.id"
            class="flex flex-wrap items-center justify-between gap-2 py-3"
          >
            <div class="min-w-0">
              <div class="text-sm font-semibold text-[var(--ink)]">
                {{ d.ts_code }}
                <span v-if="d.stock_name" class="font-normal text-[var(--muted)]">{{ d.stock_name }}</span>
              </div>
              <div v-if="d.note" class="mt-0.5 text-xs text-[var(--muted)] truncate max-w-xs">{{ d.note }}</div>
            </div>
            <StatusBadge :value="d.action_type" />
          </div>
        </div>
      </PageSection>

      <!-- 快速导航 -->
      <PageSection title="快速导航" subtitle="跳转到研究体系的各个核心模块。">
        <div class="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          <RouterLink
            v-for="nav in quickNavItems"
            :key="nav.to"
            :to="nav.to"
            class="group flex flex-col gap-2 rounded-[var(--radius-card)] border border-[var(--line)] bg-white p-4 shadow-[var(--shadow-soft)] transition hover:-translate-y-0.5 hover:border-[var(--brand)] hover:shadow-[var(--shadow-card)]"
          >
            <div class="text-[15px] font-bold text-[var(--ink)] group-hover:text-[var(--brand)]">{{ nav.label }}</div>
            <div class="text-[13px] text-[var(--muted)]">{{ nav.description }}</div>
          </RouterLink>
        </div>
      </PageSection>
    </div>
  </AppShell>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import { useQuery } from '@tanstack/vue-query'
import AppShell from '../../shared/ui/AppShell.vue'
import PageSection from '../../shared/ui/PageSection.vue'
import InfoCard from '../../shared/ui/InfoCard.vue'
import StatusBadge from '../../shared/ui/StatusBadge.vue'
import { fetchDecisionActions } from '../../services/api/decision'

const todayDateLabel = computed(() => {
  return new Date().toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' })
})

const {
  data: actionsData,
  isPending: actionsLoading,
  isError: actionsError,
} = useQuery({
  queryKey: ['decision-actions-workbench'],
  queryFn: () => fetchDecisionActions({ limit: 5 }),
})

const allActions = computed<any[]>(() => {
  const raw = actionsData.value
  if (!raw) return []
  if (Array.isArray(raw)) return raw
  if (Array.isArray(raw.actions)) return raw.actions
  return []
})

const pendingActions = computed(() =>
  allActions.value.filter((a: any) => ['watch', 'pending'].includes(a.execution_status || a.action_type || '')).slice(0, 5),
)

const recentDecisions = computed(() => allActions.value.slice(0, 5))

const quickNavItems = [
  {
    to: '/market/conclusion',
    label: '市场结论',
    description: '今日交易主线、主要风险与候选方向',
  },
  {
    to: '/research/funnel',
    label: '候选漏斗',
    description: '候选股票全生命周期状态管理',
  },
  {
    to: '/research/decision',
    label: '决策工作台',
    description: '短名单执行、动作审批与验证结果',
  },
  {
    to: '/research/multi-role',
    label: '多角色分析',
    description: 'AI六角色协同深度公司分析',
  },
]
</script>
