<template>
  <AppShell title="任务收件箱" subtitle="待审批的多角色分析、失败重试任务与待复盘订单汇总。">
    <div class="space-y-4">
      <!-- 待审批 -->
      <PageSection
        title="待审批"
        :subtitle="`${pendingApproval.length} 项多角色分析任务等待决策`"
        eyebrow="需要操作"
      >
        <div v-if="approvalLoading" class="py-6 text-center text-sm text-[var(--muted)]">加载中...</div>
        <div v-else-if="approvalError" class="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
          加载失败，请刷新重试。
        </div>
        <div v-else-if="pendingApproval.length === 0" class="rounded-2xl border border-dashed border-[var(--line)] px-4 py-8 text-center text-sm text-[var(--muted)]">
          暂无待审批任务
        </div>
        <div v-else class="divide-y divide-[var(--line)]">
          <div
            v-for="job in pendingApproval"
            :key="job.job_id || job.id"
            class="flex flex-wrap items-center justify-between gap-3 py-3"
          >
            <div class="min-w-0">
              <div class="text-sm font-semibold text-[var(--ink)]">
                {{ job.ts_code || job.title || job.job_id || '-' }}
                <span v-if="job.stock_name" class="ml-1 font-normal text-[var(--muted)]">{{ job.stock_name }}</span>
              </div>
              <div class="mt-0.5 flex flex-wrap items-center gap-2 text-xs text-[var(--muted)]">
                <span>多角色分析</span>
                <span v-if="job.created_at">· {{ ageLabel(job.created_at) }}</span>
              </div>
            </div>
            <RouterLink
              :to="`/app/lab/multi-role?job_id=${job.job_id || job.id}`"
              class="rounded-2xl bg-[var(--brand)] px-4 py-2 text-xs font-semibold text-white transition hover:opacity-90"
            >
              审批
            </RouterLink>
          </div>
        </div>
      </PageSection>

      <!-- 待重试 -->
      <PageSection
        title="待重试"
        :subtitle="`${failedJobs.length} 个任务执行失败`"
        eyebrow="需要操作"
      >
        <div v-if="approvalLoading" class="py-4 text-center text-sm text-[var(--muted)]">加载中...</div>
        <div v-else-if="failedJobs.length === 0" class="rounded-2xl border border-dashed border-[var(--line)] px-4 py-8 text-center text-sm text-[var(--muted)]">
          暂无失败任务
        </div>
        <div v-else class="divide-y divide-[var(--line)]">
          <div
            v-for="job in failedJobs"
            :key="job.job_id || job.id"
            class="flex flex-wrap items-center justify-between gap-3 py-3"
          >
            <div class="min-w-0">
              <div class="text-sm font-semibold text-[var(--ink)]">
                {{ job.ts_code || job.title || job.job_id || '-' }}
                <span v-if="job.stock_name" class="ml-1 font-normal text-[var(--muted)]">{{ job.stock_name }}</span>
              </div>
              <div class="mt-0.5 flex flex-wrap items-center gap-2 text-xs">
                <span class="text-rose-600">执行失败</span>
                <span v-if="job.error_message" class="text-[var(--muted)] truncate max-w-xs">{{ job.error_message }}</span>
                <span v-if="job.created_at" class="text-[var(--muted)]">· {{ ageLabel(job.created_at) }}</span>
              </div>
            </div>
            <RouterLink
              :to="`/app/lab/multi-role?job_id=${job.job_id || job.id}&retry=1`"
              class="rounded-2xl border border-amber-300 bg-amber-50 px-4 py-2 text-xs font-semibold text-amber-700 transition hover:bg-amber-100"
            >
              重试
            </RouterLink>
          </div>
        </div>
      </PageSection>

      <!-- 待复盘 -->
      <PageSection
        title="待复盘"
        :subtitle="`${pendingReview.length} 个已执行订单待复盘`"
        eyebrow="需要操作"
      >
        <div v-if="ordersLoading" class="py-4 text-center text-sm text-[var(--muted)]">加载中...</div>
        <div v-else-if="ordersError" class="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
          加载失败，请刷新重试。
        </div>
        <div v-else-if="pendingReview.length === 0" class="rounded-2xl border border-dashed border-[var(--line)] px-4 py-8 text-center text-sm text-[var(--muted)]">
          暂无待复盘订单
        </div>
        <div v-else class="divide-y divide-[var(--line)]">
          <div
            v-for="order in pendingReview"
            :key="order.id"
            class="flex flex-wrap items-center justify-between gap-3 py-3"
          >
            <div class="min-w-0">
              <div class="text-sm font-semibold text-[var(--ink)]">
                {{ order.ts_code }}
                <span v-if="order.name" class="ml-1 font-normal text-[var(--muted)]">{{ order.name }}</span>
              </div>
              <div class="mt-0.5 flex flex-wrap items-center gap-2 text-xs text-[var(--muted)]">
                <span>{{ actionTypeLabel(order.action_type) }}</span>
                <span v-if="order.executed_price">· 成交价 {{ order.executed_price.toFixed(2) }}</span>
                <span v-if="order.created_at">· {{ ageLabel(order.created_at) }}</span>
              </div>
            </div>
            <RouterLink
              to="/app/desk/review"
              class="rounded-2xl border border-teal-300 bg-teal-50 px-4 py-2 text-xs font-semibold text-teal-700 transition hover:bg-teal-100"
            >
              复盘
            </RouterLink>
          </div>
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
import { http } from '../../services/http'
import { fetchPortfolioOrders, type PortfolioOrder } from '../../services/api/portfolio'

// Fetch multi-role jobs (pending_user_decision + error in one batch if possible, else two calls)
async function fetchMultiRoleJobs(status: string) {
  const { data } = await http.get('/api/llm/multi-role/v3/jobs', { params: { status, limit: 50 } })
  return data
}

const {
  data: approvalData,
  isPending: approvalLoading,
  isError: approvalError,
} = useQuery({
  queryKey: ['multi-role-jobs-inbox'],
  queryFn: async () => {
    const [pendingRes, errorRes] = await Promise.allSettled([
      fetchMultiRoleJobs('pending_user_decision'),
      fetchMultiRoleJobs('error'),
    ])
    return {
      pending: pendingRes.status === 'fulfilled' ? pendingRes.value : { jobs: [] },
      error: errorRes.status === 'fulfilled' ? errorRes.value : { jobs: [] },
    }
  },
  refetchInterval: 30_000,
})

const {
  data: ordersData,
  isPending: ordersLoading,
  isError: ordersError,
} = useQuery({
  queryKey: ['portfolio-orders-executed'],
  queryFn: () => fetchPortfolioOrders({ status: 'executed', limit: 50 }),
  refetchInterval: 60_000,
})

function extractJobs(raw: any): any[] {
  if (!raw) return []
  if (Array.isArray(raw)) return raw
  if (Array.isArray(raw.jobs)) return raw.jobs
  return []
}

const pendingApproval = computed(() => extractJobs(approvalData.value?.pending))
const failedJobs = computed(() => extractJobs(approvalData.value?.error))

const pendingReview = computed<PortfolioOrder[]>(() => {
  const raw = ordersData.value
  if (!raw) return []
  if (Array.isArray(raw)) return raw
  if (Array.isArray(raw.orders)) return raw.orders
  return []
})

function ageLabel(s: string): string {
  try {
    const ms = Date.now() - new Date(s).getTime()
    const hours = Math.floor(ms / 3_600_000)
    if (hours < 1) {
      const mins = Math.floor(ms / 60_000)
      return `${mins} 分钟前`
    }
    if (hours < 24) return `${hours} 小时前`
    const days = Math.floor(hours / 24)
    return `${days} 天前`
  } catch {
    return s
  }
}

function actionTypeLabel(t?: string): string {
  const map: Record<string, string> = { buy: '买入', sell: '卖出', hold: '持有', confirm: '确认' }
  return t ? (map[t] ?? t) : '-'
}
</script>
