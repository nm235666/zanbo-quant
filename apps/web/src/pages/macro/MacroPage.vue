<template>
  <AppShell title="宏观数据看板" subtitle="统一查询宏观指标、频率、区间和历史序列。">
    <div class="space-y-4">
      <div class="page-hero-grid">
        <div class="page-hero-card">
          <div class="page-insight-label">Macro Lens</div>
          <div class="page-hero-title">先确认宏观方向，再决定是否要下钻行业和个股。</div>
          <div class="page-hero-copy">
            这里更适合快速判断趋势和周期，而不是做逐条数据核对。优先选择一个核心指标，再看曲线方向、频率和当前时间窗是否支持你的判断。
          </div>
          <div class="page-action-cluster">
            <button class="rounded-2xl bg-[var(--brand)] px-4 py-3 font-semibold text-white" @click="applyFilters">更新趋势</button>
          </div>
        </div>
        <div class="page-insight-list">
          <div class="page-insight-item">
            <div class="page-insight-label">当前指标</div>
            <div class="page-insight-value">{{ result?.items?.[0]?.indicator_name || filters.indicator_code || '未指定' }}</div>
            <div class="page-insight-note">为空时按结果列表浏览；指定指标后更适合看趋势变化。</div>
          </div>
          <div class="page-insight-item">
            <div class="page-insight-label">周期视角</div>
            <div class="page-insight-value">{{ periodRangeLabel }}</div>
            <div class="page-insight-note">频率 {{ filters.freq || '全部' }}，结果 {{ result?.total || 0 }} 条。</div>
          </div>
        </div>
      </div>

      <div class="kpi-grid">
        <StatCard title="指标池" :value="indicatorOptions.length" hint="可选宏观指标总数" />
        <StatCard title="查询结果" :value="result?.total ?? 0" hint="当前筛选命中条数" />
        <StatCard title="频率筛选" :value="filters.freq || '全部'" hint="D/W/M/Q/Y" />
        <StatCard title="周期区间" :value="periodRangeLabel" hint="起止为空时按默认范围" />
      </div>

      <PageSection title="宏观查询" subtitle="选择指标、频率与周期区间，快速查看时间序列。">
        <div class="grid gap-3 xl:grid-cols-[minmax(0,1.2fr)_130px_150px_150px_130px_130px] md:grid-cols-2">
          <select v-model="filters.indicator_code" class="w-full min-w-0 rounded-2xl border border-[var(--line)] bg-white px-4 py-3">
            <option value="">选择指标（可选）</option>
            <option v-for="item in indicatorOptions" :key="item.indicator_code" :value="item.indicator_code">
              {{ item.indicator_name || item.indicator_code }} [{{ item.indicator_code }}]
            </option>
          </select>
          <select v-model="filters.freq" class="w-full min-w-0 rounded-2xl border border-[var(--line)] bg-white px-4 py-3">
            <option value="">全部频率</option>
            <option value="D">日频</option>
            <option value="W">周频</option>
            <option value="M">月频</option>
            <option value="Q">季频</option>
            <option value="Y">年频</option>
          </select>
          <input v-model="filters.period_start" class="w-full min-w-0 rounded-2xl border border-[var(--line)] bg-white px-4 py-3" placeholder="起始周期，如 202001" />
          <input v-model="filters.period_end" class="w-full min-w-0 rounded-2xl border border-[var(--line)] bg-white px-4 py-3" placeholder="结束周期，如 202512" />
          <select v-model.number="filters.page_size" class="w-full min-w-0 rounded-2xl border border-[var(--line)] bg-white px-4 py-3">
            <option :value="50">50 / 页</option>
            <option :value="100">100 / 页</option>
            <option :value="200">200 / 页</option>
          </select>
          <button class="w-full min-w-0 rounded-2xl bg-[var(--brand)] px-4 py-3 font-semibold text-white" @click="applyFilters">查询</button>
        </div>
      </PageSection>

      <PageSection title="指标趋势" subtitle="按统计周期查看指标走势。">
        <TrendAreaChart :labels="chart.labels" :series="chart.series" :height="360" empty-text="暂无宏观序列数据" />
      </PageSection>

      <PageSection :title="`宏观结果 (${result?.total || 0})`" subtitle="查询结果与源字段保持一致，便于校验和导出。">
        <div class="table-lead">
          <div class="table-lead-copy">结果表用于核对源字段和周期值，曲线用于判断方向。两者结合看，避免只看一条时间序列就下结论。</div>
          <div class="flex flex-wrap gap-2 text-xs">
            <span class="metric-chip">频率 {{ filters.freq || '全部' }}</span>
            <span class="metric-chip">区间 {{ periodRangeLabel }}</span>
          </div>
        </div>
        <div class="grid gap-3 lg:hidden">
          <InfoCard
            v-for="row in result?.items || []"
            :key="`${row.indicator_code}-${row.period}`"
            :title="row.indicator_name || row.indicator_code || '-'"
            :meta="`${row.indicator_code || '-'} · ${row.freq || '-'} · ${row.period || '-'}`"
            :description="`指标值 ${row.value ?? '-'} · 来源 ${row.source || '-'}`"
          />
        </div>
        <DataTable class="hidden lg:block" :columns="columns" :rows="result?.items || []" row-key="period" empty-text="暂无宏观结果" />
        <div class="table-pager mt-3 flex items-center justify-between text-sm text-[var(--muted)]">
          <div>第 {{ filters.page }} / {{ result?.total_pages || 1 }} 页</div>
          <div class="flex gap-2">
            <button class="rounded-2xl bg-stone-800 px-4 py-2 text-white disabled:opacity-40" :disabled="filters.page <= 1" @click="goPrevPage">上一页</button>
            <button class="rounded-2xl bg-stone-800 px-4 py-2 text-white disabled:opacity-40" :disabled="filters.page >= (result?.total_pages || 1)" @click="goNextPage">下一页</button>
          </div>
        </div>
      </PageSection>
    </div>
  </AppShell>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, watch } from 'vue'
import { keepPreviousData, useQuery } from '@tanstack/vue-query'
import { useRoute, useRouter } from 'vue-router'
import AppShell from '../../shared/ui/AppShell.vue'
import PageSection from '../../shared/ui/PageSection.vue'
import DataTable from '../../shared/ui/DataTable.vue'
import InfoCard from '../../shared/ui/InfoCard.vue'
import StatCard from '../../shared/ui/StatCard.vue'
import TrendAreaChart from '../../shared/charts/TrendAreaChart.vue'
import { fetchMacroIndicators, fetchMacroSeries } from '../../services/api/macro'
import { buildCleanQuery, readQueryNumber, readQueryString } from '../../shared/utils/urlState'

const route = useRoute()
const router = useRouter()

const filters = reactive({
  indicator_code: '',
  freq: '',
  period_start: '',
  period_end: '',
  keyword: '',
  page: 1,
  page_size: 50,
})

const columns = [
  { key: 'indicator_code', label: '指标代码' },
  { key: 'indicator_name', label: '指标名称' },
  { key: 'freq', label: '频率' },
  { key: 'period', label: '统计周期' },
  { key: 'value', label: '指标值' },
  { key: 'source', label: '数据来源' },
]

const { data: indicators } = useQuery({
  queryKey: ['macro-indicators'],
  queryFn: fetchMacroIndicators,
})

const { data: result } = useQuery({
  queryKey: ['macro-series', filters],
  queryFn: () => fetchMacroSeries(filters),
  placeholderData: keepPreviousData,
})

const indicatorOptions = computed(() => indicators.value?.items || [])
const periodRangeLabel = computed(() => {
  const start = String(filters.period_start || '').trim()
  const end = String(filters.period_end || '').trim()
  if (!start && !end) return '默认'
  return `${start || '-'} ~ ${end || '-'}`
})
const chart = computed(() => {
  const rows = [...(result.value?.items || [])].sort((a: Record<string, any>, b: Record<string, any>) => String(a.period || '').localeCompare(String(b.period || '')))
  const label = rows[0]?.indicator_name || rows[0]?.indicator_code || '指标值'
  return {
    labels: rows.map((item: Record<string, any>) => String(item.period || '')),
    series: [
      {
        name: label,
        data: rows.map((item: Record<string, any>) => Number(item.value)),
        color: '#0f617a',
        area: true,
      },
    ],
  }
})

function applyFilters() {
  filters.page = 1
  syncRouteFromFilters()
}

function goPrevPage() {
  if (filters.page <= 1) return
  filters.page -= 1
  syncRouteFromFilters()
}

function goNextPage() {
  const totalPages = Number(result.value?.total_pages || 1)
  if (filters.page >= totalPages) return
  filters.page += 1
  syncRouteFromFilters()
}

function syncRouteFromFilters() {
  router.replace({
    query: buildCleanQuery({
      indicator_code: filters.indicator_code,
      freq: filters.freq,
      period_start: filters.period_start,
      period_end: filters.period_end,
      page: filters.page,
      page_size: filters.page_size,
    }),
  })
}

function applyRouteQuery() {
  const q = route.query as Record<string, unknown>
  Object.assign(filters, {
    indicator_code: readQueryString(q, 'indicator_code', ''),
    freq: readQueryString(q, 'freq', ''),
    period_start: readQueryString(q, 'period_start', ''),
    period_end: readQueryString(q, 'period_end', ''),
    keyword: '',
    page: Math.max(1, readQueryNumber(q, 'page', 1)),
    page_size: Math.max(20, readQueryNumber(q, 'page_size', 50)),
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
