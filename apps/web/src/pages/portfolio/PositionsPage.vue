<template>
  <AppShell title="当前持仓" subtitle="模拟交易账户持仓概览，含成本、市值与浮动盈亏。">
    <div class="space-y-4">
      <PageSection title="持仓列表" subtitle="当前所有活跃持仓。">
        <template #action>
          <RouterLink
            to="/research/decision"
            class="rounded-2xl border border-[var(--line)] bg-white px-3 py-2 text-xs font-semibold text-[var(--ink)] transition hover:border-[var(--brand)] hover:text-[var(--brand)]"
          >
            前往决策工作台
          </RouterLink>
        </template>

        <div v-if="isPending" class="py-8 text-center text-sm text-[var(--muted)]">加载中...</div>
        <div v-else-if="isError" class="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-4 text-sm text-rose-700">
          加载持仓失败：{{ String(error) }}
          <button class="ml-2 underline" @click="() => refetch()">重试</button>
        </div>
        <div v-else-if="positions.length === 0" class="rounded-2xl border border-dashed border-[var(--line)] px-4 py-12 text-center">
          <div class="text-base font-semibold text-[var(--ink)]">暂无持仓</div>
          <div class="mt-1 text-sm text-[var(--muted)]">在决策工作台确认交易后，持仓将出现在这里。</div>
          <RouterLink
            to="/research/decision"
            class="mt-4 inline-flex items-center rounded-full border border-[var(--line)] bg-white px-4 py-1.5 text-sm font-semibold text-[var(--ink)] transition hover:border-[var(--brand)] hover:text-[var(--brand)]"
          >
            前往决策工作台 →
          </RouterLink>
        </div>
        <div v-else class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead>
              <tr class="border-b border-[var(--line)] text-left">
                <th class="pb-2 pr-4 text-xs font-semibold uppercase tracking-[0.12em] text-[var(--muted)]">代码</th>
                <th class="pb-2 pr-4 text-xs font-semibold uppercase tracking-[0.12em] text-[var(--muted)]">名称</th>
                <th class="pb-2 pr-4 text-right text-xs font-semibold uppercase tracking-[0.12em] text-[var(--muted)]">持仓量</th>
                <th class="pb-2 pr-4 text-right text-xs font-semibold uppercase tracking-[0.12em] text-[var(--muted)]">均价</th>
                <th class="pb-2 pr-4 text-right text-xs font-semibold uppercase tracking-[0.12em] text-[var(--muted)]">现价</th>
                <th class="pb-2 pr-4 text-right text-xs font-semibold uppercase tracking-[0.12em] text-[var(--muted)]">浮盈亏</th>
                <th class="pb-2 text-xs font-semibold uppercase tracking-[0.12em] text-[var(--muted)]">建仓日期</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-[var(--line)]">
              <tr
                v-for="pos in positions"
                :key="pos.id"
                class="transition hover:bg-[var(--panel-soft)]"
              >
                <td class="py-3 pr-4 font-semibold text-[var(--ink)]">
                  <RouterLink
                    :to="`/stocks/detail/${pos.ts_code}`"
                    class="transition hover:text-[var(--brand)]"
                  >
                    {{ pos.ts_code }}
                  </RouterLink>
                </td>
                <td class="py-3 pr-4 text-[var(--muted)]">{{ pos.name || '-' }}</td>
                <td class="py-3 pr-4 text-right tabular-nums">{{ pos.size ?? '-' }}</td>
                <td class="py-3 pr-4 text-right tabular-nums">{{ formatPrice(pos.avg_price) }}</td>
                <td class="py-3 pr-4 text-right tabular-nums text-[var(--muted)]">{{ formatPrice(pos.current_price) }}</td>
                <td class="py-3 pr-4 text-right tabular-nums font-semibold" :class="pnlClass(pos.unrealized_pnl)">
                  {{ formatPnl(pos.unrealized_pnl) }}
                </td>
                <td class="py-3 text-xs text-[var(--muted)]">{{ formatDate(pos.created_at) }}</td>
              </tr>
            </tbody>
          </table>
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
import { fetchPortfolioPositions, type PortfolioPosition } from '../../services/api/portfolio'

const {
  data,
  isPending,
  isError,
  error,
  refetch,
} = useQuery({
  queryKey: ['portfolio-positions'],
  queryFn: fetchPortfolioPositions,
  refetchInterval: 60_000,
})

const positions = computed<PortfolioPosition[]>(() => {
  const raw = data.value as any
  if (!raw) return []
  if (Array.isArray(raw)) return raw
  if (Array.isArray(raw.positions)) return raw.positions
  return []
})

function formatPrice(v?: number | null): string {
  if (v == null) return '-'
  return v.toFixed(2)
}

function formatPnl(v?: number | null): string {
  if (v == null) return '-'
  const prefix = v > 0 ? '+' : ''
  return `${prefix}${v.toFixed(2)}`
}

function pnlClass(v?: number | null): string {
  if (v == null) return 'text-[var(--muted)]'
  if (v > 0) return 'text-emerald-600'
  if (v < 0) return 'text-rose-600'
  return 'text-[var(--muted)]'
}

function formatDate(s?: string): string {
  if (!s) return '-'
  try {
    return new Date(s).toLocaleDateString('zh-CN')
  } catch {
    return s
  }
}
</script>
