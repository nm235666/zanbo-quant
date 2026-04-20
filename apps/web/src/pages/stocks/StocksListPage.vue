<template>
  <AppShell title="股票列表" subtitle="统一股票入口，先搜代码、简称、市场、地区，再进入详情与研究工作流。">
    <div class="space-y-4">
      <div class="page-hero-grid">
        <div class="page-hero-card">
          <div class="page-insight-label">Research Entry</div>
          <div class="page-hero-title">先缩小范围，再进入单票研究。</div>
          <div class="page-hero-copy">
            这页更适合做第一步收敛：用市场、地区和上市状态把候选池缩到可读范围，再进入个股详情、评分和价格链路。
          </div>
          <div class="page-action-cluster">
            <button class="rounded-2xl bg-[var(--brand)] px-4 py-3 font-semibold text-white" @click="applyFilters">
              {{ isFetching ? '查询中...' : '刷新候选池' }}
            </button>
            <RouterLink class="rounded-2xl border border-[var(--line)] bg-white px-4 py-3 text-sm font-semibold text-[var(--ink)]" to="/app/stocks/scores">
              打开综合评分
            </RouterLink>
          </div>
        </div>
        <div class="page-insight-list">
          <div class="page-insight-item">
            <div class="page-insight-label">当前检索焦点</div>
            <div class="page-insight-value">{{ filters.keyword || '全市场扫描' }}</div>
            <div class="page-insight-note">关键词为空时按市场/地区/状态做广域浏览。</div>
          </div>
          <div class="page-insight-item">
            <div class="page-insight-label">建议动作</div>
            <div class="page-insight-value">{{ stocks?.total ? '进入高相关标的' : '先放宽筛选' }}</div>
            <div class="page-insight-note">命中 {{ stocks?.total ?? 0 }} 条结果；优先点击名称进入详情做下一步判断。</div>
          </div>
        </div>
      </div>

      <div class="kpi-grid">
        <StatCard title="结果总量" :value="stocks?.total ?? 0" hint="当前筛选命中股票" />
        <StatCard title="当前页" :value="`${queryFilters.page}`" :hint="`共 ${stocks?.total_pages || 1} 页`" />
        <StatCard title="市场维度" :value="filters.market || '全部'" hint="筛选中的市场范围" />
        <StatCard title="地区维度" :value="filters.area || '全部'" hint="筛选中的地区范围" />
      </div>

      <PageSection title="筛选检索" subtitle="这是整个股票研究链路的入口页。">
        <div class="grid gap-3 xl:grid-cols-6 md:grid-cols-3">
          <label class="text-sm font-semibold text-[var(--ink)]">
            关键词
            <input v-model="filters.keyword" class="mt-1 w-full rounded-2xl border border-[var(--line)] bg-white px-4 py-3" placeholder="输入股票代码或简称" />
          </label>
          <label class="text-sm font-semibold text-[var(--ink)]">
            上市状态
            <select v-model="filters.status" class="mt-1 w-full rounded-2xl border border-[var(--line)] bg-white px-4 py-3">
              <option value="">全部状态</option>
              <option value="L">上市</option>
              <option value="D">退市</option>
              <option value="P">暂停</option>
            </select>
          </label>
          <label class="text-sm font-semibold text-[var(--ink)]">
            市场
            <select v-model="filters.market" class="mt-1 w-full rounded-2xl border border-[var(--line)] bg-white px-4 py-3">
              <option value="">全部市场</option>
              <option v-for="item in stockFilters?.markets || []" :key="item" :value="item">{{ item }}</option>
            </select>
          </label>
          <label class="text-sm font-semibold text-[var(--ink)]">
            地区
            <select v-model="filters.area" class="mt-1 w-full rounded-2xl border border-[var(--line)] bg-white px-4 py-3">
              <option value="">全部地区</option>
              <option v-for="item in stockFilters?.areas || []" :key="item" :value="item">{{ item }}</option>
            </select>
          </label>
          <label class="text-sm font-semibold text-[var(--ink)]">
            每页条数
            <select v-model.number="filters.page_size" class="mt-1 w-full rounded-2xl border border-[var(--line)] bg-white px-4 py-3">
              <option :value="20">20 / 页</option>
              <option :value="50">50 / 页</option>
              <option :value="100">100 / 页</option>
            </select>
          </label>
          <button class="rounded-2xl bg-[var(--brand)] px-4 py-3 font-semibold text-white" @click="applyFilters">
            {{ isFetching ? '查询中...' : '应用筛选' }}
          </button>
        </div>
      </PageSection>

      <PageSection :title="`股票结果 (${stocks?.total || 0})`" subtitle="点击代码或名称进入统一股票详情页。">
        <div
          v-if="paginationNotice"
          class="mb-3 rounded-2xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800"
        >
          {{ paginationNotice }}
        </div>
        <div class="table-lead">
          <div class="table-lead-copy">
            当前结果优先服务“选股收敛”而不是最终结论。先看市场、行业和上市状态，再进入股票详情页做更深入判断。
          </div>
          <div class="flex flex-wrap gap-2 text-xs">
            <span class="metric-chip">市场 {{ filters.market || '全部' }}</span>
            <span class="metric-chip">地区 {{ filters.area || '全部' }}</span>
            <span class="metric-chip">状态 {{ filters.status ? listStatusLabel(filters.status) : '全部' }}</span>
          </div>
        </div>
        <div class="grid gap-3 lg:hidden">
          <InfoCard
            v-for="row in stocks?.items || []"
            :key="row.ts_code"
            :title="row.name || row.ts_code || '-'"
            :meta="`${row.ts_code || '-'} · ${row.industry || '-'} · ${row.market || '-'}`"
            :description="`地区 ${row.area || '-'} · 上市 ${row.list_date || '-'} · 状态 ${listStatusLabel(row.list_status)}`"
          >
            <template #badge>
              <StatusBadge :value="row.list_status" :label="listStatusLabel(row.list_status)" />
            </template>
            <div class="mt-3">
              <RouterLink class="rounded-full border border-[var(--line)] bg-white px-3 py-2 text-xs font-semibold text-[var(--brand)]" :to="`/app/stocks/detail/${row.ts_code}`">查看详情</RouterLink>
            </div>
          </InfoCard>
        </div>

        <DataTable class="hidden lg:block" :columns="columns" :rows="stocks?.items || []" row-key="ts_code" empty-text="暂无股票结果">
          <template #cell-ts_code="{ row }">
            <RouterLink class="font-bold text-[var(--brand)]" :to="`/app/stocks/detail/${row.ts_code}`">{{ row.ts_code }}</RouterLink>
          </template>
          <template #cell-name="{ row }">
            <RouterLink class="font-semibold" :to="`/app/stocks/detail/${row.ts_code}`">{{ row.name }}</RouterLink>
          </template>
          <template #cell-list_status="{ row }">
            <StatusBadge :value="row.list_status" :label="listStatusLabel(row.list_status)" />
          </template>
        </DataTable>
        <div class="table-pager mt-3 flex items-center justify-between text-sm text-[var(--muted)]">
          <div>第 {{ pageDisplay }} / {{ totalPagesDisplay }} 页</div>
          <div class="flex gap-2">
            <button class="rounded-2xl bg-stone-800 px-4 py-2 text-white disabled:opacity-40" :disabled="queryFilters.page <= 1" @click="goPrevPage">上一页</button>
            <button class="rounded-2xl bg-stone-800 px-4 py-2 text-white disabled:opacity-40" :disabled="queryFilters.page >= totalPagesDisplay" @click="goNextPage">下一页</button>
          </div>
        </div>
      </PageSection>
    </div>
  </AppShell>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { keepPreviousData, useQuery } from '@tanstack/vue-query'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import AppShell from '../../shared/ui/AppShell.vue'
import PageSection from '../../shared/ui/PageSection.vue'
import DataTable from '../../shared/ui/DataTable.vue'
import StatusBadge from '../../shared/ui/StatusBadge.vue'
import InfoCard from '../../shared/ui/InfoCard.vue'
import StatCard from '../../shared/ui/StatCard.vue'
import { fetchStockFilters, fetchStocks } from '../../services/api/stocks'
import { listStatusLabel } from '../../shared/utils/format'
import { buildCleanQuery, readQueryNumber, readQueryString } from '../../shared/utils/urlState'

const route = useRoute()
const router = useRouter()

const filters = reactive({
  keyword: '',
  status: '',
  market: '',
  area: '',
  page_size: 20,
})
const queryFilters = reactive({
  keyword: '',
  status: '',
  market: '',
  area: '',
  page: 1,
  page_size: 20,
})
const paginationNotice = ref('')
const lastNoticeKey = ref('')

const columns = [
  { key: 'ts_code', label: '股票代码' },
  { key: 'symbol', label: '交易代码' },
  { key: 'name', label: '简称' },
  { key: 'area', label: '地区' },
  { key: 'industry', label: '行业' },
  { key: 'market', label: '市场' },
  { key: 'list_date', label: '上市日期' },
  { key: 'list_status', label: '上市状态' },
]

const { data: stockFilters } = useQuery({ queryKey: ['stock-filters'], queryFn: fetchStockFilters })
const { data: stocks, isFetching } = useQuery({
  queryKey: computed(() => ['stocks', { ...queryFilters }]),
  queryFn: () => fetchStocks({ ...queryFilters }),
  placeholderData: keepPreviousData,
})
const totalPagesDisplay = computed(() => {
  const total = Number(stocks.value?.total || 0)
  if (total <= 0) return 1
  return Math.max(1, Number(stocks.value?.total_pages || 1))
})
const pageDisplay = computed(() => {
  if (Number(stocks.value?.total || 0) <= 0) return 1
  return Math.min(Math.max(1, Number(queryFilters.page || 1)), totalPagesDisplay.value)
})

function applyFilters() {
  paginationNotice.value = ''
  queryFilters.keyword = (filters.keyword || '').trim()
  queryFilters.status = filters.status
  queryFilters.market = filters.market
  queryFilters.area = filters.area
  queryFilters.page_size = Number(filters.page_size) || 20
  queryFilters.page = 1
  syncRouteFromQuery()
}

function goPrevPage() {
  if (queryFilters.page <= 1) return
  paginationNotice.value = ''
  queryFilters.page -= 1
  syncRouteFromQuery()
}

function goNextPage() {
  const totalPages = Number(stocks.value?.total_pages || 1)
  if (queryFilters.page >= totalPages) return
  paginationNotice.value = ''
  queryFilters.page += 1
  syncRouteFromQuery()
}

function syncRouteFromQuery() {
  router.replace({
    query: buildCleanQuery({
      keyword: queryFilters.keyword,
      status: queryFilters.status,
      market: queryFilters.market,
      area: queryFilters.area,
      page: queryFilters.page,
      page_size: queryFilters.page_size,
    }),
  })
}

function enforcePageCoherence(nextPage: number, reason: 'empty' | 'overflow') {
  queryFilters.page = nextPage
  const noticeKey = `${queryFilters.keyword}|${queryFilters.market}|${queryFilters.area}|${reason}|${nextPage}`
  if (lastNoticeKey.value !== noticeKey) {
    paginationNotice.value = reason === 'empty'
      ? '当前筛选结果为空，系统已自动回到第 1 页。'
      : `当前页超出结果范围，系统已自动跳转到第 ${nextPage} 页。`
    lastNoticeKey.value = noticeKey
  }
  syncRouteFromQuery()
}

function applyRouteQuery() {
  const q = route.query as Record<string, unknown>
  const next = {
    keyword: readQueryString(q, 'keyword', ''),
    status: readQueryString(q, 'status', ''),
    market: readQueryString(q, 'market', ''),
    area: readQueryString(q, 'area', ''),
    page: Math.max(1, readQueryNumber(q, 'page', 1)),
    page_size: Math.max(20, readQueryNumber(q, 'page_size', 20)),
  }
  Object.assign(filters, {
    keyword: next.keyword,
    status: next.status,
    market: next.market,
    area: next.area,
    page_size: next.page_size,
  })
  Object.assign(queryFilters, next)
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

watch(
  () => [stocks.value?.total, stocks.value?.total_pages, queryFilters.page] as const,
  () => {
    if (!stocks.value) return
    const total = Number(stocks.value?.total || 0)
    const itemsCount = Array.isArray(stocks.value?.items) ? stocks.value.items.length : 0
    const totalPages = Math.max(1, Number(stocks.value?.total_pages || 1))
    const expectedPage = (total <= 0 || itemsCount <= 0) ? 1 : Math.min(Math.max(1, Number(queryFilters.page || 1)), totalPages)
    if (expectedPage === queryFilters.page) return

    enforcePageCoherence(expectedPage, total <= 0 || itemsCount <= 0 ? 'empty' : 'overflow')
  },
)

watch(
  () => isFetching.value,
  (fetching) => {
    if (fetching) return
    if (Number(queryFilters.page || 1) <= 1) return
    // 请求失败或未返回可用分页信息时，也要避免“高页码 + 空画面”的矛盾态。
    if (!stocks.value) {
      enforcePageCoherence(1, 'empty')
    }
  },
)
</script>
