<template>
  <AppShell title="市场结论" subtitle="今日交易主线、主要风险、行业影响与候选方向综合汇总。">
    <div class="space-y-4">
      <!-- Header CTA -->
      <div class="flex flex-wrap items-center justify-between gap-3">
        <div v-if="data" class="text-xs text-[var(--muted)]">
          数据更新：{{ freshnessLabel }}
        </div>
        <RouterLink
          to="/research/decision"
          class="rounded-2xl bg-[var(--brand)] px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:opacity-90"
        >
          进入决策工作台 →
        </RouterLink>
      </div>

      <!-- Loading state -->
      <div v-if="isPending" class="py-16 text-center text-sm text-[var(--muted)]">
        <div class="text-base font-semibold text-[var(--ink)]">加载市场结论中...</div>
        <div class="mt-1">正在聚合新闻、宏观与信号数据</div>
      </div>

      <!-- Error state -->
      <div v-else-if="isError" class="rounded-[var(--radius-lg)] border border-rose-200 bg-rose-50 px-6 py-8 text-center">
        <div class="text-base font-semibold text-rose-700">加载失败</div>
        <div class="mt-1 text-sm text-rose-600">{{ String(error) }}</div>
        <button
          class="mt-4 rounded-2xl border border-rose-300 bg-white px-4 py-2 text-sm font-semibold text-rose-700 transition hover:bg-rose-50"
          @click="() => refetch()"
        >
          重试
        </button>
      </div>

      <template v-else-if="data">
        <!-- 今日交易主线 -->
        <PageSection title="今日交易主线" subtitle="综合宏观、新闻与信号的核心交易逻辑。">
          <div class="rounded-2xl border border-[var(--line)] bg-[linear-gradient(180deg,rgba(255,255,255,0.9)_0%,rgba(238,244,247,0.78)_100%)] px-5 py-4 shadow-[var(--shadow-soft)]">
            <div v-if="apiData.trading_theme" class="text-[15px] leading-7 text-[var(--ink)]">
              {{ apiData.trading_theme }}
            </div>
            <div v-else class="text-sm text-[var(--muted)]">暂无交易主线数据</div>
          </div>
        </PageSection>

        <!-- 主要风险 -->
        <PageSection title="主要风险" subtitle="当前需要关注的核心风险因子。">
          <div v-if="mainRisks.length === 0" class="text-sm text-[var(--muted)]">暂无风险数据</div>
          <ul v-else class="space-y-2">
            <li
              v-for="(risk, idx) in mainRisks"
              :key="idx"
              class="flex items-start gap-3 rounded-2xl border border-rose-100 bg-rose-50 px-4 py-3"
            >
              <span class="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-rose-200 text-[11px] font-bold text-rose-700">{{ idx + 1 }}</span>
              <span class="text-sm text-rose-800">{{ risk }}</span>
            </li>
          </ul>
        </PageSection>

        <!-- 行业影响 -->
        <PageSection title="行业影响" subtitle="受益行业与受压行业分析。">
          <div class="grid gap-4 sm:grid-cols-2">
            <div>
              <div class="mb-2 text-xs font-semibold uppercase tracking-[0.14em] text-emerald-600">受益行业</div>
              <div v-if="benefitingSectors.length === 0" class="text-sm text-[var(--muted)]">暂无数据</div>
              <ul v-else class="space-y-1.5">
                <li
                  v-for="(sector, idx) in benefitingSectors"
                  :key="idx"
                  class="flex items-center gap-2 rounded-2xl border border-emerald-100 bg-emerald-50 px-3 py-2 text-sm text-emerald-800"
                >
                  <span class="h-1.5 w-1.5 shrink-0 rounded-full bg-emerald-500" />
                  {{ sector }}
                </li>
              </ul>
            </div>
            <div>
              <div class="mb-2 text-xs font-semibold uppercase tracking-[0.14em] text-rose-600">受压行业</div>
              <div v-if="pressuredSectors.length === 0" class="text-sm text-[var(--muted)]">暂无数据</div>
              <ul v-else class="space-y-1.5">
                <li
                  v-for="(sector, idx) in pressuredSectors"
                  :key="idx"
                  class="flex items-center gap-2 rounded-2xl border border-rose-100 bg-rose-50 px-3 py-2 text-sm text-rose-800"
                >
                  <span class="h-1.5 w-1.5 shrink-0 rounded-full bg-rose-500" />
                  {{ sector }}
                </li>
              </ul>
            </div>
          </div>
        </PageSection>

        <!-- 候选方向 -->
        <PageSection title="候选方向" subtitle="当前具备交易逻辑的重点候选标的。">
          <div v-if="candidateDirections.length === 0" class="rounded-2xl border border-dashed border-[var(--line)] px-4 py-8 text-center text-sm text-[var(--muted)]">
            暂无候选方向数据
          </div>
          <div v-else class="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
            <div
              v-for="candidate in candidateDirections"
              :key="candidate.ts_code"
              class="rounded-[var(--radius-card)] border border-[var(--line)] bg-white p-4 shadow-[var(--shadow-soft)] transition hover:shadow-[var(--shadow-card)]"
            >
              <div class="flex items-start justify-between gap-2">
                <div>
                  <div class="text-[15px] font-bold text-[var(--ink)]">{{ candidate.name || candidate.ts_code }}</div>
                  <div class="mt-0.5 text-xs text-[var(--muted)]">{{ candidate.ts_code }}</div>
                </div>
              </div>
              <div v-if="candidate.reason" class="mt-2 text-[13px] leading-6 text-[var(--muted)] line-clamp-3">
                {{ candidate.reason }}
              </div>
              <div class="mt-3 flex flex-wrap gap-2">
                <RouterLink
                  :to="`/stocks/detail/${candidate.ts_code}`"
                  class="rounded-full border border-[var(--line)] bg-white px-3 py-1 text-xs font-semibold text-[var(--ink)] transition hover:border-[var(--brand)] hover:text-[var(--brand)]"
                >
                  查看详情
                </RouterLink>
                <RouterLink
                  :to="`/research/workbench?ts_code=${candidate.ts_code}`"
                  class="rounded-full bg-[var(--brand)] px-3 py-1 text-xs font-semibold text-white transition hover:opacity-90"
                >
                  进入研究
                </RouterLink>
              </div>
            </div>
          </div>
        </PageSection>

        <!-- 冲突说明 -->
        <PageSection
          v-if="apiData.conflict_note"
          title="冲突说明"
          subtitle="信号或逻辑存在分歧时的处理说明。"
        >
          <div class="rounded-2xl border border-amber-200 bg-amber-50 px-4 py-4">
            <div class="text-sm font-semibold text-amber-800">冲突说明</div>
            <div class="mt-1 text-[13px] leading-6 text-amber-700">{{ apiData.conflict_note }}</div>
            <div v-if="apiData.resolution_basis" class="mt-3">
              <div class="text-xs font-semibold uppercase tracking-[0.14em] text-amber-700">解决依据</div>
              <div class="mt-1 text-[13px] leading-6 text-amber-700">{{ apiData.resolution_basis }}</div>
            </div>
          </div>
        </PageSection>

        <!-- 数据来源 -->
        <PageSection title="数据来源" subtitle="本次结论依赖的数据源统计。">
          <div v-if="sourcesCount === 0" class="text-sm text-[var(--muted)]">暂无来源信息</div>
          <div v-else class="flex flex-wrap gap-3">
            <div class="rounded-2xl border border-[var(--line)] bg-white px-4 py-3 text-sm">
              <span class="font-semibold text-[var(--ink)]">{{ sourcesCount }}</span>
              <span class="ml-1 text-[var(--muted)]">个数据来源</span>
            </div>
            <div
              v-for="(src, idx) in sourcesList"
              :key="idx"
              class="rounded-2xl border border-[var(--line)] bg-white px-3 py-2 text-xs text-[var(--muted)]"
            >
              {{ src }}
            </div>
          </div>
        </PageSection>
      </template>
    </div>
  </AppShell>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import { useQuery } from '@tanstack/vue-query'
import AppShell from '../../shared/ui/AppShell.vue'
import PageSection from '../../shared/ui/PageSection.vue'
import { fetchMarketConclusion } from '../../services/api/market'

const {
  data,
  isPending,
  isError,
  error,
  refetch,
} = useQuery({
  queryKey: ['market-conclusion'],
  queryFn: fetchMarketConclusion,
  refetchInterval: 300_000,
})

const apiData = computed(() => (data.value as any) || {})

const freshnessLabel = computed(() => {
  if (!apiData.value?.generated_at) return '未知'
  try {
    return new Date(apiData.value.generated_at).toLocaleString('zh-CN')
  } catch {
    return apiData.value.generated_at
  }
})

const mainRisks = computed<string[]>(() => {
  const r = apiData.value?.main_risks
  if (!r) return []
  if (Array.isArray(r)) return r
  return []
})

const benefitingSectors = computed<string[]>(() => {
  const s = apiData.value?.benefiting_sectors ?? apiData.value?.sector_impact?.benefiting_sectors
  if (!s) return []
  if (Array.isArray(s)) return s
  return []
})

const pressuredSectors = computed<string[]>(() => {
  const s = apiData.value?.pressured_sectors ?? apiData.value?.sector_impact?.pressured_sectors
  if (!s) return []
  if (Array.isArray(s)) return s
  return []
})

const candidateDirections = computed<any[]>(() => {
  const c = apiData.value?.candidate_directions
  if (!c) return []
  if (Array.isArray(c)) return c
  return []
})

const sourcesCount = computed<number>(() => {
  const s = apiData.value?.sources
  if (!s) return 0
  if (Array.isArray(s)) return s.length
  if (typeof s === 'number') return s
  return 0
})

const sourcesList = computed<string[]>(() => {
  const s = apiData.value?.sources
  if (!s) return []
  if (Array.isArray(s)) return s.slice(0, 10)
  return []
})
</script>
