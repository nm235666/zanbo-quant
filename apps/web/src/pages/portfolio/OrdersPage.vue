<template>
  <AppShell title="订单记录" subtitle="模拟交易订单跟踪，支持按状态筛选。">
    <div class="space-y-4">
      <PageSection title="订单列表" :subtitle="`共 ${orders.length} 条`">
        <template #action>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="tab in STATUS_TABS"
              :key="tab.key"
              class="rounded-full border px-3 py-1 text-xs font-semibold transition"
              :class="
                activeStatus === tab.key
                  ? 'border-[var(--brand)] bg-[var(--brand)] text-white'
                  : 'border-[var(--line)] bg-white text-[var(--ink)] hover:border-[var(--brand)] hover:text-[var(--brand)]'
              "
              @click="activeStatus = tab.key"
            >
              {{ tab.label }}
            </button>
          </div>
        </template>

        <div v-if="filterDecisionActionId" class="mb-3 flex items-center gap-2 rounded-2xl border border-blue-200 bg-blue-50 px-3 py-2 text-xs text-blue-700">
          <span class="font-semibold">当前过滤：决策动作 {{ filterDecisionActionId }}</span>
          <RouterLink to="/portfolio/orders" class="ml-auto text-blue-500 underline">清除过滤</RouterLink>
        </div>
        <div v-if="isPending" class="py-8 text-center text-sm text-[var(--muted)]">加载中...</div>
        <div v-else-if="isError" class="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-4 text-sm text-rose-700">
          加载订单失败：{{ String(error) }}
          <button class="ml-2 underline" @click="() => refetch()">重试</button>
        </div>
        <div v-else-if="orders.length === 0" class="rounded-2xl border border-dashed border-[var(--line)] px-4 py-10 text-center text-sm text-[var(--muted)]">
          暂无{{ activeTab?.label || '' }}订单
        </div>
        <div v-else class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead>
              <tr class="border-b border-[var(--line)] text-left">
                <th class="pb-2 pr-4 text-xs font-semibold uppercase tracking-[0.12em] text-[var(--muted)]">代码</th>
                <th class="pb-2 pr-4 text-xs font-semibold uppercase tracking-[0.12em] text-[var(--muted)]">操作</th>
                <th class="pb-2 pr-4 text-right text-xs font-semibold uppercase tracking-[0.12em] text-[var(--muted)]">计划价</th>
                <th class="pb-2 pr-4 text-right text-xs font-semibold uppercase tracking-[0.12em] text-[var(--muted)]">成交价</th>
                <th class="pb-2 pr-4 text-right text-xs font-semibold uppercase tracking-[0.12em] text-[var(--muted)]">数量</th>
                <th class="pb-2 pr-4 text-xs font-semibold uppercase tracking-[0.12em] text-[var(--muted)]">状态</th>
                <th class="pb-2 text-xs font-semibold uppercase tracking-[0.12em] text-[var(--muted)]">创建时间</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-[var(--line)]">
              <tr
                v-for="order in orders"
                :key="order.id"
                class="transition hover:bg-[var(--panel-soft)]"
              >
                <td class="py-3 pr-4 font-semibold text-[var(--ink)]">
                  <RouterLink
                    :to="`/stocks/detail/${order.ts_code}`"
                    class="transition hover:text-[var(--brand)]"
                  >
                    {{ order.ts_code }}
                  </RouterLink>
                  <div v-if="order.name" class="text-xs font-normal text-[var(--muted)]">{{ order.name }}</div>
                </td>
                <td class="py-3 pr-4">
                  <span :class="actionTypeClass(order.action_type)">
                    {{ actionTypeLabel(order.action_type) }}
                  </span>
                </td>
                <td class="py-3 pr-4 text-right tabular-nums">{{ formatPrice(order.planned_price) }}</td>
                <td class="py-3 pr-4 text-right tabular-nums">{{ formatPrice(order.executed_price) }}</td>
                <td class="py-3 pr-4 text-right tabular-nums">{{ order.size ?? '-' }}</td>
                <td class="py-3 pr-4">
                  <span :class="statusBadgeClass(order.status)">{{ statusLabel(order.status) }}</span>
                </td>
                <td class="py-3 text-xs text-[var(--muted)]">{{ formatDate(order.created_at) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </PageSection>
    </div>
  </AppShell>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { useQuery } from '@tanstack/vue-query'
import AppShell from '../../shared/ui/AppShell.vue'
import PageSection from '../../shared/ui/PageSection.vue'
import { fetchPortfolioOrders, type PortfolioOrder } from '../../services/api/portfolio'

interface StatusTab {
  key: string
  label: string
}

const STATUS_TABS: StatusTab[] = [
  { key: '', label: '全部' },
  { key: 'planned', label: '计划中' },
  { key: 'executed', label: '已执行' },
  { key: 'cancelled', label: '已取消' },
]

const route = useRoute()

const filterDecisionActionId = computed(() => String(route.query.decision_action_id || '').trim())

const activeStatus = ref('')

const activeTab = computed(() => STATUS_TABS.find((t) => t.key === activeStatus.value))

const {
  data,
  isPending,
  isError,
  error,
  refetch,
} = useQuery({
  queryKey: computed(() => ['portfolio-orders', activeStatus.value, filterDecisionActionId.value]),
  queryFn: () => fetchPortfolioOrders({
    status: activeStatus.value || undefined,
    limit: 100,
    decision_action_id: filterDecisionActionId.value || undefined,
  }),
})

const orders = computed<PortfolioOrder[]>(() => {
  const raw = data.value
  if (!raw) return []
  if (Array.isArray(raw)) return raw
  if (Array.isArray(raw.orders)) return raw.orders
  return []
})

function formatPrice(v?: number | null): string {
  if (v == null) return '-'
  return v.toFixed(2)
}

function formatDate(s?: string): string {
  if (!s) return '-'
  try {
    return new Date(s).toLocaleDateString('zh-CN')
  } catch {
    return s
  }
}

function actionTypeLabel(t?: string): string {
  const map: Record<string, string> = { buy: '买入', sell: '卖出', hold: '持有', confirm: '确认' }
  return t ? (map[t] ?? t) : '-'
}

function actionTypeClass(t?: string): string {
  if (t === 'buy') return 'inline-flex items-center rounded-full border border-emerald-200 bg-emerald-100 px-2 py-0.5 text-xs font-semibold text-emerald-700'
  if (t === 'sell') return 'inline-flex items-center rounded-full border border-rose-200 bg-rose-100 px-2 py-0.5 text-xs font-semibold text-rose-700'
  return 'inline-flex items-center rounded-full border border-gray-200 bg-gray-100 px-2 py-0.5 text-xs font-semibold text-gray-700'
}

function statusLabel(s?: string): string {
  const map: Record<string, string> = { planned: '计划中', executed: '已执行', cancelled: '已取消', pending: '待处理' }
  return s ? (map[s] ?? s) : '-'
}

function statusBadgeClass(s?: string): string {
  const base = 'inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-semibold'
  if (s === 'executed') return `${base} border-emerald-200 bg-emerald-100 text-emerald-700`
  if (s === 'cancelled') return `${base} border-gray-200 bg-gray-100 text-gray-600`
  if (s === 'planned') return `${base} border-amber-200 bg-amber-100 text-amber-700`
  return `${base} border-[var(--line)] bg-[var(--panel-soft)] text-[var(--muted)]`
}
</script>
