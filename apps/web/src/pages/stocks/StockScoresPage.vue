<template>
  <AppShell title="股票综合评分" subtitle="统一看行业内评分、核心分项与估值/趋势维度，不再散落在旧页面里。">
    <div class="space-y-4">
      <div class="page-hero-grid">
        <div class="page-hero-card">
          <div class="page-insight-label">Scoreboard</div>
          <div class="page-hero-title">先看谁值得研究，不要一上来就进详情页。</div>
          <div class="page-hero-copy">
            综合评分页负责做优先级排序。建议先按行业和评分日期收敛，再把高分样本送到详情页、价格中心和投研决策板。
          </div>
          <div class="page-action-cluster">
            <button class="rounded-2xl bg-[var(--brand)] px-4 py-3 font-semibold text-white" @click="applyFilters">
              {{ isFetching ? '查询中...' : '更新评分看板' }}
            </button>
            <RouterLink id="scores-workbench-cta" class="rounded-2xl border border-[var(--line)] bg-white px-4 py-3 text-sm font-semibold text-[var(--ink)]" :to="workbenchEntryTo">
              进入决策工作台
            </RouterLink>
          </div>
        </div>
        <div class="page-insight-list">
          <div class="page-insight-item">
            <div class="page-insight-label">当前主视角</div>
            <div class="page-insight-value">{{ filters.industry || '全行业排序' }}</div>
            <div class="page-insight-note">按行业筛选时更适合做板块内部比较，不筛选时适合看全市场分布。</div>
          </div>
          <div class="page-insight-item">
            <div class="page-insight-label">行动建议</div>
            <div class="page-insight-value">{{ scores?.items?.length ? '查看高分样本' : '检查筛选条件' }}</div>
            <div class="page-insight-note">优先关注总分、行业内总分和趋势分同时高的标的。</div>
          </div>
        </div>
      </div>

      <div class="kpi-grid">
        <StatCard title="评分总量" :value="scores?.total ?? 0" hint="当前筛选命中评分条数" />
        <StatCard title="行业筛选" :value="filters.industry || '全部'" hint="当前行业维度" />
        <StatCard title="市场筛选" :value="filters.market || '全部'" hint="当前市场维度" />
        <StatCard title="评分日期" :value="filters.score_date || '最新'" hint="为空则按最新快照" />
      </div>

      <!-- Sticky decision entry CTA — always visible regardless of scroll/data state -->
      <div class="sticky top-0 z-10 flex items-center justify-between gap-3 rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-2.5 shadow-sm">
        <span class="text-sm font-semibold text-emerald-800">评分筛选完成后，进入决策工作台做判断</span>
        <RouterLink id="scores-workbench-cta-sticky" :to="workbenchEntryTo" class="shrink-0 rounded-xl bg-emerald-700 px-3 py-1.5 text-xs font-semibold text-white transition hover:bg-emerald-800">
          进入决策工作台 →
        </RouterLink>
      </div>

      <PageSection title="筛选器" subtitle="按行业、市场、关键词与日期筛选评分结果。">
        <div class="grid gap-3 xl:grid-cols-5 md:grid-cols-2">
          <input v-model="filters.keyword" class="rounded-2xl border border-[var(--line)] bg-white px-4 py-3" placeholder="代码或简称" />
          <select v-model="filters.industry" class="rounded-2xl border border-[var(--line)] bg-white px-4 py-3">
            <option value="">全部行业</option>
            <option v-for="item in scoreFilters?.industries || []" :key="item" :value="item">{{ item }}</option>
          </select>
          <select v-model="filters.market" class="rounded-2xl border border-[var(--line)] bg-white px-4 py-3">
            <option value="">全部市场</option>
            <option v-for="item in scoreFilters?.markets || []" :key="item" :value="item">{{ item }}</option>
          </select>
          <input v-model="filters.score_date" class="rounded-2xl border border-[var(--line)] bg-white px-4 py-3" placeholder="评分日期 YYYYMMDD，可空" />
          <button class="rounded-2xl bg-[var(--brand)] px-4 py-3 font-semibold text-white" @click="applyFilters">
            {{ isFetching ? '查询中...' : '应用筛选' }}
          </button>
        </div>
      </PageSection>

      <PageSection :title="`评分结果 (${scores?.total || 0})`" subtitle="点击股票名进入详情页做进一步研究。">
        <div class="table-lead">
          <div class="table-lead-copy">
            这张表是“研究优先级排序”，不是最终买卖结论。优先看 `总分 + 行业内总分 + 趋势分` 的组合，再进入详情页做定性判断。
          </div>
          <div class="flex flex-wrap gap-2 text-xs">
            <span class="metric-chip">行业 {{ filters.industry || '全部' }}</span>
            <span class="metric-chip">市场 {{ filters.market || '全部' }}</span>
            <span class="metric-chip">评分日期 {{ filters.score_date || '最新' }}</span>
          </div>
        </div>
        <div class="grid gap-3 lg:hidden">
          <InfoCard
            v-for="row in scores?.items || []"
            :key="row.ts_code"
            :title="row.name || row.ts_code || '-'"
            :meta="`${row.ts_code || '-'} · ${row.industry || '-'} · ${row.market || '-'}`"
            :description="`总分 ${formatNumber(row.total_score, 2)} · 行业内 ${formatNumber(row.industry_total_score, 2)} · 等级 ${row.score_grade || '-'}`"
          >
            <template #badge>
              <StatusBadge value="brand" :label="row.score_grade || '-'" />
            </template>
            <div class="mt-3 flex flex-wrap gap-2">
              <RouterLink class="rounded-full border border-[var(--line)] bg-white px-3 py-2 text-xs font-semibold text-[var(--brand)]" :to="`/app/stocks/detail/${row.ts_code}`">查看详情</RouterLink>
              <RouterLink class="rounded-full border border-[var(--line)] bg-white px-3 py-2 text-xs font-semibold text-[var(--ink)]" :to="`/app/workbench?ts_code=${encodeURIComponent(row.ts_code)}&from=stock_scores`">→工作台</RouterLink>
            </div>
          </InfoCard>
        </div>

        <DataTable class="hidden lg:block" :columns="columns" :rows="scores?.items || []" row-key="ts_code" empty-text="暂无评分数据">
          <template #cell-name="{ row }">
            <RouterLink class="font-semibold text-[var(--brand)]" :to="`/app/stocks/detail/${row.ts_code}`">{{ row.name || row.ts_code }}</RouterLink>
          </template>
          <template #cell-total_score="{ row }">{{ formatNumber(row.total_score, 2) }}</template>
          <template #cell-industry_total_score="{ row }">{{ formatNumber(row.industry_total_score, 2) }}</template>
          <template #cell-news_score="{ row }">{{ formatNumber(row.news_score, 2) }}</template>
          <template #cell-trend_score="{ row }">{{ formatNumber(row.trend_score, 2) }}</template>
          <template #cell-score_grade="{ row }"><StatusBadge value="brand" :label="row.score_grade || '-'" /></template>
        </DataTable>
      </PageSection>
    </div>
  </AppShell>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, watch } from 'vue'
import { keepPreviousData, useQuery } from '@tanstack/vue-query'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import AppShell from '../../shared/ui/AppShell.vue'
import PageSection from '../../shared/ui/PageSection.vue'
import DataTable from '../../shared/ui/DataTable.vue'
import StatusBadge from '../../shared/ui/StatusBadge.vue'
import InfoCard from '../../shared/ui/InfoCard.vue'
import StatCard from '../../shared/ui/StatCard.vue'
import { fetchStockScoreFilters, fetchStockScores } from '../../services/api/stocks'
import { formatNumber } from '../../shared/utils/format'
import { buildCleanQuery, readQueryNumber, readQueryString } from '../../shared/utils/urlState'

const route = useRoute()
const router = useRouter()

const filters = reactive({ keyword: '', industry: '', market: '', score_date: '', page_size: 20 })
const queryFilters = reactive({ keyword: '', industry: '', market: '', score_date: '', page: 1, page_size: 20 })
const columns = [
  { key: 'name', label: '股票' },
  { key: 'industry', label: '行业' },
  { key: 'market', label: '市场' },
  { key: 'total_score', label: '总分' },
  { key: 'industry_total_score', label: '行业内总分' },
  { key: 'trend_score', label: '趋势分' },
  { key: 'news_score', label: '新闻分' },
  { key: 'score_grade', label: '评分等级' },
]

const workbenchEntryTo = computed(() => {
  const q: Record<string, string> = { from: 'stock_scores' }
  if (queryFilters.industry) q.industry = queryFilters.industry
  if (queryFilters.keyword) q.keyword = queryFilters.keyword
  if (queryFilters.score_date) q.score_date = queryFilters.score_date
  const qs = new URLSearchParams(q).toString()
  return `/app/workbench${qs ? '?' + qs : ''}`
})

const { data: scoreFilters } = useQuery({ queryKey: ['stock-score-filters'], queryFn: fetchStockScoreFilters })
const { data: scores, isFetching } = useQuery({
  queryKey: computed(() => ['stock-scores', { ...queryFilters }]),
  queryFn: () => fetchStockScores({ ...queryFilters }),
  placeholderData: keepPreviousData,
})

function applyFilters() {
  queryFilters.keyword = (filters.keyword || '').trim()
  queryFilters.industry = filters.industry
  queryFilters.market = filters.market
  queryFilters.score_date = (filters.score_date || '').trim()
  queryFilters.page_size = Number(filters.page_size) || 20
  queryFilters.page = 1
  syncRouteFromQuery()
}

function syncRouteFromQuery() {
  router.replace({
    query: buildCleanQuery({
      keyword: queryFilters.keyword,
      industry: queryFilters.industry,
      market: queryFilters.market,
      score_date: queryFilters.score_date,
      page_size: queryFilters.page_size,
    }),
  })
}

function applyRouteQuery() {
  const q = route.query as Record<string, unknown>
  const next = {
    keyword: readQueryString(q, 'keyword', ''),
    industry: readQueryString(q, 'industry', ''),
    market: readQueryString(q, 'market', ''),
    score_date: readQueryString(q, 'score_date', ''),
    page_size: Math.max(20, readQueryNumber(q, 'page_size', 20)),
  }
  Object.assign(filters, next)
  Object.assign(queryFilters, {
    ...next,
    page: 1,
  })
}

onMounted(() => {
  applyRouteQuery()
})

watch(
  () => route.query,
  () => {
    applyRouteQuery()
  },
)
</script>
