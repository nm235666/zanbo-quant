<template>
  <AppShell title="产业链图谱" subtitle="主题 + 行业双中心关系浏览，点击节点即可下钻到详情页或切换中心。">
    <div class="space-y-4">
      <PageSection title="图谱筛选" subtitle="先选择中心类型，再用关键词、层级和节点数量控制图谱粒度。">
        <div class="grid gap-3 xl:grid-cols-[1.2fr_0.8fr]">
          <div class="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
            <label class="text-sm font-semibold text-[var(--ink)]">
              中心类型
              <select v-model="filters.center_type" class="mt-1 w-full rounded-2xl border border-[var(--line)] bg-white px-4 py-3">
                <option value="theme">主题中心</option>
                <option value="industry">行业中心</option>
              </select>
            </label>
            <label class="text-sm font-semibold text-[var(--ink)]">
              关键词 / 中心
              <input v-model="filters.keyword" class="mt-1 w-full rounded-2xl border border-[var(--line)] bg-white px-4 py-3" placeholder="如 AI、黄金、银行、半导体" />
            </label>
            <label class="text-sm font-semibold text-[var(--ink)]">
              深度
              <select v-model="filters.depth" class="mt-1 w-full rounded-2xl border border-[var(--line)] bg-white px-4 py-3">
                <option :value="1">1 层</option>
                <option :value="2">2 层</option>
                <option :value="3">3 层</option>
              </select>
            </label>
            <label class="text-sm font-semibold text-[var(--ink)]">
              节点上限
              <select v-model="filters.limit" class="mt-1 w-full rounded-2xl border border-[var(--line)] bg-white px-4 py-3">
                <option :value="8">8</option>
                <option :value="12">12</option>
                <option :value="16">16</option>
                <option :value="24">24</option>
              </select>
            </label>
          </div>

          <div class="rounded-[24px] border border-[var(--line)] bg-white/80 p-4">
            <div class="flex flex-wrap items-center justify-between gap-3">
              <div>
                <div class="text-sm font-bold text-[var(--ink)]">关系筛选</div>
                <div class="mt-1 text-xs text-[var(--muted)]">只过滤边，不破坏节点浏览和下钻。</div>
              </div>
              <div class="flex flex-wrap gap-2">
                <button class="rounded-2xl border border-[var(--line)] bg-white px-3 py-2 text-sm font-semibold text-[var(--ink)]" @click="resetFilters">重置</button>
                <button class="rounded-2xl bg-[var(--brand)] px-4 py-2 text-sm font-semibold text-white" @click="applyFilters">
                  {{ isFetching ? '加载中...' : '刷新图谱' }}
                </button>
              </div>
            </div>
            <div v-if="relationOptions.length" class="mt-3 flex flex-wrap gap-2">
              <button
                class="rounded-full border px-3 py-2 text-xs font-semibold transition"
                :class="relationFilter === '' ? 'border-[var(--brand)] bg-[var(--brand)] text-white' : 'border-[var(--line)] bg-white text-[var(--ink)]'"
                @click="relationFilter = ''"
              >
                全部关系
              </button>
              <button
                v-for="item in relationOptions"
                :key="item.key"
                class="rounded-full border px-3 py-2 text-xs font-semibold transition"
                :class="relationFilter === item.key ? 'border-[var(--brand)] bg-[var(--brand)] text-white' : 'border-[var(--line)] bg-white text-[var(--ink)]'"
                @click="relationFilter = item.key"
              >
                {{ item.label }} · {{ item.count }}
              </button>
            </div>
            <div v-else class="mt-3 text-sm text-[var(--muted)]">当前图谱暂无可筛选关系。</div>
          </div>
        </div>
      </PageSection>

      <div class="grid gap-4 lg:grid-cols-4 md:grid-cols-2">
        <StatCard title="节点数" :value="summary.node_count ?? 0" hint="当前图谱节点总数" />
        <StatCard title="边数" :value="summary.edge_count ?? 0" hint="当前图谱关系连线" />
        <StatCard title="主题数" :value="summary.theme_count ?? 0" hint="主题节点数量" />
        <StatCard title="行业数" :value="summary.industry_count ?? 0" hint="行业节点数量" />
      </div>

      <div class="grid gap-4 xl:grid-cols-[minmax(0,1.35fr)_minmax(360px,0.72fr)]">
        <PageSection title="关系图" subtitle="主题、行业、股票三层关系图，节点可点击，中心可切换。">
          <template #action>
            <div class="flex flex-wrap gap-2 text-xs">
              <span class="metric-chip">中心：{{ centerLabel || '-' }}</span>
              <span class="metric-chip">最新评分：{{ summary.latest_score_date || '-' }}</span>
              <span class="metric-chip">中心类型：{{ centerTypeLabel(filters.center_type) }}</span>
            </div>
          </template>

          <StatePanel
            v-if="graphEmpty"
            class="mb-4"
            tone="warning"
            title="当前图谱暂无可展示数据"
            :description="graphSummaryMessage"
          >
            <template #action>
              <button class="rounded-2xl bg-[var(--brand)] px-4 py-2 font-semibold text-white" @click="applyFilters">重新加载</button>
            </template>
          </StatePanel>

          <div v-else class="overflow-hidden rounded-[28px] border border-[var(--line)] bg-[linear-gradient(180deg,rgba(255,255,255,0.9)_0%,rgba(245,248,250,0.84)_100%)]">
            <div class="border-b border-[var(--line)] px-4 py-3 text-xs text-[var(--muted)]">
              选中节点：<span class="font-semibold text-[var(--ink)]">{{ selectedNode?.label || centerLabel || '-' }}</span>
              <span class="mx-2">·</span>
              点击节点可查看详情，再从右侧切换中心或跳转原页面。
            </div>
            <div class="relative overflow-hidden" :style="{ height: `${graphHeight}px` }">
              <svg class="pointer-events-none absolute inset-0 h-full w-full" viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true">
                <defs>
                  <marker id="graph-arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto" markerUnits="strokeWidth">
                    <path d="M0,0 L0,6 L6,3 z" fill="rgba(13,97,122,0.35)" />
                  </marker>
                </defs>
                <line
                  v-for="edge in visibleEdges"
                  :key="edge.id"
                  :x1="edgeLayout(edge).x1"
                  :y1="edgeLayout(edge).y1"
                  :x2="edgeLayout(edge).x2"
                  :y2="edgeLayout(edge).y2"
                  :stroke="edgeStroke(edge)"
                  :stroke-width="edgeWidth(edge)"
                  :opacity="edgeOpacity(edge)"
                  marker-end="url(#graph-arrow)"
                />
              </svg>

              <button
                v-for="node in layoutNodes"
                :key="node.id"
                type="button"
                class="absolute -translate-x-1/2 -translate-y-1/2 rounded-[24px] border px-4 py-3 text-left shadow-[0_14px_36px_rgba(10,32,44,0.08)] transition hover:-translate-y-[54%] hover:shadow-[0_18px_42px_rgba(10,32,44,0.14)]"
                :class="nodeClass(node)"
                :style="{ left: `${node.left}%`, top: `${node.top}%`, width: nodeWidth(node), maxWidth: '280px' }"
                @click="selectNode(node.id)"
              >
                <div class="flex items-start justify-between gap-2">
                  <div class="min-w-0">
                    <div class="truncate text-[13px] font-extrabold leading-5 text-[var(--ink)]">{{ node.label }}</div>
                    <div class="mt-1 text-[11px] uppercase tracking-[0.14em] text-[var(--muted)]">{{ nodeTypeLabel(node.type) }} · L{{ node.layer }}</div>
                  </div>
                  <StatusBadge :value="node.status || 'info'" :label="node.status || '-'" />
                </div>
                <div class="mt-2 max-h-[40px] overflow-hidden text-xs leading-5 text-[var(--muted)]">{{ node.summary || '-' }}</div>
                <div class="mt-2 flex flex-wrap gap-2 text-[11px] text-[var(--muted)]">
                  <span v-if="node.score !== undefined" class="rounded-full bg-white/82 px-2 py-1">分数 {{ formatValue(node.score) }}</span>
                  <span v-if="node.strength !== undefined" class="rounded-full bg-white/82 px-2 py-1">强度 {{ formatValue(node.strength) }}</span>
                </div>
              </button>
            </div>
          </div>
        </PageSection>

        <PageSection title="节点详情" subtitle="右侧固定展示当前选中节点的解释、关联节点和跳转入口。">
          <div v-if="selectedNode" class="space-y-4">
            <div class="rounded-[24px] border border-[var(--line)] bg-white/82 p-4">
              <div class="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <div class="text-xs uppercase tracking-[0.16em] text-[var(--muted)]">{{ nodeTypeLabel(selectedNode.type) }}</div>
                  <div class="mt-1 text-2xl font-extrabold text-[var(--ink)]">{{ selectedNode.label }}</div>
                  <div class="mt-2 text-sm text-[var(--muted)]">{{ selectedNode.subtitle || selectedNode.summary || '-' }}</div>
                </div>
                <StatusBadge :value="selectedNode.status || 'info'" :label="selectedNode.status || '-'" />
              </div>

              <div class="mt-4 grid gap-2 md:grid-cols-2">
                <div class="metric-chip">权重 <strong>{{ formatValue(selectedNode.weight) }}</strong></div>
                <div class="metric-chip">分数 <strong>{{ formatValue(selectedNode.score) }}</strong></div>
                <div class="metric-chip">强度 <strong>{{ formatValue(selectedNode.strength) }}</strong></div>
                <div class="metric-chip">层级 <strong>L{{ selectedNode.layer ?? '-' }}</strong></div>
              </div>
            </div>

            <div v-if="detailWhy" class="rounded-[24px] border border-[var(--line)] bg-[var(--panel-soft)] p-4">
              <div class="text-sm font-bold text-[var(--ink)]">为什么是这个节点</div>
              <div class="mt-2 text-sm leading-6 text-[var(--muted)]">{{ detailWhy }}</div>
            </div>

            <div v-if="selectedNode.highlights?.length" class="rounded-[24px] border border-[var(--line)] bg-white/82 p-4">
              <div class="text-sm font-bold text-[var(--ink)]">关键要点</div>
              <div class="mt-3 flex flex-wrap gap-2">
                <span v-for="item in selectedNode.highlights" :key="item" class="metric-chip">{{ item }}</span>
              </div>
            </div>

            <div v-if="detailMetrics.length" class="rounded-[24px] border border-[var(--line)] bg-white/82 p-4">
              <div class="text-sm font-bold text-[var(--ink)]">关键指标</div>
              <div class="mt-3 grid gap-2 md:grid-cols-2">
                <div v-for="item in detailMetrics" :key="item.label" class="rounded-2xl border border-[var(--line)] bg-white px-3 py-2 text-sm">
                  <div class="text-xs text-[var(--muted)]">{{ item.label }}</div>
                  <div class="mt-1 font-semibold text-[var(--ink)]">{{ item.value }}</div>
                </div>
              </div>
            </div>

            <div v-if="relatedNodes.length" class="rounded-[24px] border border-[var(--line)] bg-white/82 p-4">
              <div class="text-sm font-bold text-[var(--ink)]">它和谁有关</div>
              <div class="mt-3 flex flex-wrap gap-2">
                <button
                  v-for="item in relatedNodes"
                  :key="item.id"
                  type="button"
                  class="rounded-full border border-[var(--line)] bg-white px-3 py-2 text-xs font-semibold text-[var(--ink)] transition hover:border-[var(--brand)] hover:text-[var(--brand)]"
                  @click="selectNode(item.id)"
                >
                  {{ item.label }} · {{ nodeTypeLabel(item.type) }}
                </button>
              </div>
            </div>

            <div v-if="selectedEdgeRows.length" class="rounded-[24px] border border-[var(--line)] bg-white/82 p-4">
              <div class="text-sm font-bold text-[var(--ink)]">关联关系</div>
              <div class="mt-3 space-y-2">
                <InfoCard
                  v-for="edge in selectedEdgeRows"
                  :key="edge.id"
                  :title="edge.relation_label || edge.relation_key || '-'"
                  :meta="edgeSummary(edge)"
                  :description="edge.summary || ''"
                />
              </div>
            </div>

            <div v-if="selectedActions.length" class="rounded-[24px] border border-[var(--line)] bg-white/82 p-4">
              <div class="text-sm font-bold text-[var(--ink)]">跳转入口</div>
              <div class="mt-3 flex flex-wrap gap-2">
                <button
                  v-for="item in selectedActions"
                  :key="`${item.label}-${item.to}`"
                  type="button"
                  class="rounded-2xl bg-[var(--brand)] px-4 py-2 text-sm font-semibold text-white"
                  @click="goTo(item.to)"
                >
                  {{ item.label }}
                </button>
                <button
                  v-if="canSwitchCenter"
                  type="button"
                  class="rounded-2xl border border-[var(--line)] bg-white px-4 py-2 text-sm font-semibold text-[var(--ink)]"
                  @click="switchCenterToSelected"
                >
                  以此为中心
                </button>
              </div>
            </div>

            <div v-if="selectedNode.id === centerId && centerDetailSummary" class="rounded-[24px] border border-[var(--line)] bg-[linear-gradient(180deg,rgba(255,255,255,0.94)_0%,rgba(238,244,247,0.82)_100%)] p-4">
              <div class="text-sm font-bold text-[var(--ink)]">中心解释</div>
              <div class="mt-2 text-sm leading-6 text-[var(--muted)]">{{ centerDetailSummary }}</div>
              <div v-if="centerDetailNextSteps.length" class="mt-3 flex flex-wrap gap-2">
                <button
                  v-for="item in centerDetailNextSteps"
                  :key="`${item.label}-${item.to}`"
                  type="button"
                  class="rounded-2xl border border-[var(--line)] bg-white px-4 py-2 text-sm font-semibold text-[var(--ink)]"
                  @click="goTo(item.to)"
                >
                  {{ item.label }}
                </button>
              </div>
            </div>
          </div>
          <div v-else class="rounded-[24px] border border-[var(--line)] bg-white/82 p-5 text-sm text-[var(--muted)]">
            请先在左侧选择一个节点。
          </div>
        </PageSection>
      </div>
    </div>
  </AppShell>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { keepPreviousData, useQuery } from '@tanstack/vue-query'
import { useRoute, useRouter } from 'vue-router'
import AppShell from '../../shared/ui/AppShell.vue'
import PageSection from '../../shared/ui/PageSection.vue'
import StatCard from '../../shared/ui/StatCard.vue'
import InfoCard from '../../shared/ui/InfoCard.vue'
import StatusBadge from '../../shared/ui/StatusBadge.vue'
import StatePanel from '../../shared/ui/StatePanel.vue'
import { fetchSignalChainGraph } from '../../services/api/signals'
import { buildCleanQuery, readQueryNumber, readQueryString } from '../../shared/utils/urlState'

type GraphNode = Record<string, any>
type GraphEdge = Record<string, any>
type LayoutNode = GraphNode & { left: number; top: number }

const route = useRoute()
const router = useRouter()

const filters = reactive({
  center_type: 'theme',
  keyword: '',
  depth: 2,
  limit: 12,
})
const queryFilters = reactive({
  center_type: 'theme',
  center_key: '',
  depth: 2,
  limit: 12,
})
const relationFilter = ref('')
const selectedNodeId = ref('')

const { data: result, isFetching } = useQuery({
  queryKey: computed(() => ['signal-chain-graph', { ...queryFilters }]),
  queryFn: () => fetchSignalChainGraph({ ...queryFilters }),
  placeholderData: keepPreviousData,
})

const graphNodes = computed(() => (Array.isArray(result.value?.nodes) ? result.value.nodes : []) as GraphNode[])
const graphEdges = computed(() => (Array.isArray(result.value?.edges) ? result.value.edges : []) as GraphEdge[])
const summary = computed(() => result.value?.summary || {})
const centerNode = computed(() => result.value?.center || null)
const centerId = computed(() => String(centerNode.value?.id || ''))
const centerLabel = computed(() => String(result.value?.center_label || centerNode.value?.label || ''))
const graphDetail = computed(() => result.value?.detail || {})
const graphEmpty = computed(() => Boolean(summary.value?.empty) || graphNodes.value.length === 0)
const graphSummaryMessage = computed(() => String(summary.value?.message || '当前没有可展示的图谱数据。'))
const canSwitchCenter = computed(() => ['theme', 'industry'].includes(String(selectedNode.value?.type || '')))

const relationOptions = computed(() => {
  const counts = new Map<string, number>()
  for (const edge of graphEdges.value) {
    const key = String(edge.relation_key || '').trim()
    if (!key) continue
    counts.set(key, (counts.get(key) || 0) + 1)
  }
  return Array.from(counts.entries())
    .map(([key, count]) => ({ key, count, label: relationLabel(key) }))
    .sort((a, b) => a.label.localeCompare(b.label, 'zh-Hans-CN'))
})

const visibleEdges = computed(() => {
  if (!relationFilter.value) return graphEdges.value
  return graphEdges.value.filter((edge) => String(edge.relation_key || '') === relationFilter.value)
})

const layoutNodes = computed<LayoutNode[]>(() => {
  const nodes = graphNodes.value.map((node) => ({
    ...node,
    layer: Number(node.layer ?? 0),
  }))
  const grouped = new Map<number, GraphNode[]>()
  for (const node of nodes) {
    const layer = Number(node.layer || 0)
    const list = grouped.get(layer) || []
    list.push(node)
    grouped.set(layer, list)
  }
  const layerOrder = [0, 1, 2]
  const xMap: Record<number, number> = { 0: 14, 1: 50, 2: 86 }
  const out: LayoutNode[] = []
  for (const layer of layerOrder) {
    const list = (grouped.get(layer) || []).sort((a, b) => {
      const scoreA = Number(a.score || 0)
      const scoreB = Number(b.score || 0)
      if (scoreA !== scoreB) return scoreB - scoreA
      return String(a.label || '').localeCompare(String(b.label || ''), 'zh-Hans-CN')
    })
    const count = list.length
    list.forEach((node, index) => {
      const top = count <= 1 ? 50 : ((index + 1) / (count + 1)) * 100
      out.push({
        ...node,
        left: xMap[layer] ?? 50,
        top,
      })
    })
  }
  return out
})

const graphHeight = computed(() => {
  const counts = [0, 1, 2].map((layer) => layoutNodes.value.filter((node) => Number(node.layer || 0) === layer).length)
  const maxCount = Math.max(1, ...counts)
  return Math.max(560, 180 + maxCount * 120)
})

const selectedNode = computed<GraphNode | null>(() => {
  const id = String(selectedNodeId.value || centerId.value || '')
  return graphNodes.value.find((node) => String(node.id || '') === id) || graphNodes.value[0] || null
})

const selectedEdgeRows = computed(() => {
  const selectedId = String(selectedNode.value?.id || '')
  if (!selectedId) return []
  return visibleEdges.value.filter((edge) => String(edge.source || '') === selectedId || String(edge.target || '') === selectedId)
})

const relatedNodes = computed(() => {
  const selectedId = String(selectedNode.value?.id || '')
  if (!selectedId) return []
  const ids = new Set<string>()
  for (const edge of selectedEdgeRows.value) {
    if (String(edge.source || '') !== selectedId) ids.add(String(edge.source || ''))
    if (String(edge.target || '') !== selectedId) ids.add(String(edge.target || ''))
  }
  return graphNodes.value.filter((node) => ids.has(String(node.id || '')))
})

const selectedActions = computed(() => {
  const actions = Array.isArray(selectedNode.value?.actions) ? selectedNode.value.actions : []
  return actions.filter((item) => item && String(item.to || '').trim())
})

const detailMetrics = computed(() => {
  const node = selectedNode.value
  if (!node || !node.metrics || typeof node.metrics !== 'object') return []
  return Object.entries(node.metrics)
    .filter(([, value]) => value !== null && value !== undefined && value !== '')
    .slice(0, 8)
    .map(([label, value]) => ({ label: metricLabel(label), value: formatValue(value) }))
})

const detailWhy = computed(() => {
  if (!selectedNode.value) return ''
  if (selectedNode.value.id === centerId.value) {
    return String(graphDetail.value?.why || selectedNode.value.summary || '')
  }
  return String(selectedNode.value.summary || selectedNode.value.subtitle || '')
})

const centerDetailSummary = computed(() => String(graphDetail.value?.why || ''))
const centerDetailNextSteps = computed(() => (Array.isArray(graphDetail.value?.next_steps) ? graphDetail.value.next_steps : []))

watch(
  () => [centerId.value, graphNodes.value.length] as const,
  () => {
    if (centerId.value) {
      selectedNodeId.value = centerId.value
      return
    }
    if (!selectedNodeId.value && graphNodes.value.length) {
      selectedNodeId.value = String(graphNodes.value[0]?.id || '')
    }
  },
  { immediate: true },
)

watch(
  () => route.query,
  () => {
    applyRouteQuery()
  },
)

function relationLabel(key: string) {
  return (
    ({
      theme_industry: '主题→行业',
      industry_theme: '行业→主题',
      industry_stock: '行业→股票',
      theme_stock: '主题→股票',
    } as Record<string, string>)[key] || key || '-'
  )
}

function metricLabel(key: string) {
  return (
    ({
      avg_score: '平均分',
      top_score: '顶部得分',
      stock_count: '股票数',
      confidence: '置信度',
      signal_strength: '信号强度',
      theme_strength: '主题强度',
      evidence_count: '证据数',
      relation_weight: '关系权重',
    } as Record<string, string>)[key] || key
  )
}

function formatValue(value: unknown) {
  const num = Number(value)
  if (Number.isFinite(num)) return num.toFixed(num >= 100 ? 0 : 2)
  return String(value ?? '-')
}

function centerTypeLabel(value: string) {
  return value === 'industry' ? '行业中心' : '主题中心'
}

function nodeTypeLabel(value: string) {
  return (
    ({
      theme: '主题',
      industry: '行业',
      stock: '股票',
    } as Record<string, string>)[String(value || '')] || String(value || '-')
  )
}

function nodeClass(node: LayoutNode) {
  const selected = String(node.id || '') === String(selectedNode.value?.id || '')
  const palette: Record<string, string> = {
    theme: 'border-amber-200 bg-[rgba(255,247,205,0.96)] text-amber-950',
    industry: 'border-sky-200 bg-[rgba(224,242,254,0.96)] text-sky-950',
    stock: 'border-emerald-200 bg-[rgba(236,253,245,0.96)] text-emerald-950',
  }
  return [
    palette[String(node.type || '')] || 'border-[var(--line)] bg-white text-[var(--ink)]',
    selected ? 'ring-2 ring-[var(--brand)] ring-offset-2 ring-offset-white' : '',
  ].join(' ')
}

function nodeWidth(node: LayoutNode) {
  if (String(node.type || '') === 'stock') return '240px'
  if (String(node.type || '') === 'industry') return '250px'
  return '260px'
}

function edgeLayout(edge: GraphEdge) {
  const source = layoutNodes.value.find((node) => String(node.id || '') === String(edge.source || ''))
  const target = layoutNodes.value.find((node) => String(node.id || '') === String(edge.target || ''))
  if (!source || !target) {
    return { x1: 50, y1: 50, x2: 50, y2: 50 }
  }
  const direction = Number(source.layer || 0) <= Number(target.layer || 0) ? 1 : -1
  const xShift = direction * 6
  return {
    x1: source.left + xShift,
    y1: source.top,
    x2: target.left - xShift,
    y2: target.top,
  }
}

function edgeStroke(edge: GraphEdge) {
  const key = String(edge.relation_key || '')
  if (key === 'theme_industry' || key === 'industry_theme') return 'rgba(245, 158, 11, 0.44)'
  if (key === 'industry_stock') return 'rgba(14, 165, 233, 0.40)'
  if (key === 'theme_stock') return 'rgba(16, 185, 129, 0.40)'
  return 'rgba(13, 97, 122, 0.32)'
}

function edgeWidth(edge: GraphEdge) {
  const weight = Number(edge.weight || 0)
  if (!Number.isFinite(weight) || weight <= 0) return 1.4
  return Math.max(1.4, Math.min(5.5, 1.4 + weight / 35))
}

function edgeOpacity(edge: GraphEdge) {
  if (!relationFilter.value) return 1
  return String(edge.relation_key || '') === relationFilter.value ? 1 : 0.12
}

function edgeSummary(edge: GraphEdge) {
  return `${String(edge.source || '-')} → ${String(edge.target || '-')} · 证据 ${edge.evidence_count ?? 0}`
}

function selectNode(nodeId: string) {
  selectedNodeId.value = nodeId
}

function goTo(path: string) {
  if (!path) return
  router.push(path)
}

function switchCenterToSelected() {
  const node = selectedNode.value
  if (!node || !['theme', 'industry'].includes(String(node.type || ''))) return
  filters.center_type = String(node.type)
  filters.keyword = String(node.label || '')
  applyFilters()
}

function applyFilters() {
  queryFilters.center_type = filters.center_type || 'theme'
  queryFilters.center_key = (filters.keyword || '').trim()
  queryFilters.depth = Number(filters.depth) || 2
  queryFilters.limit = Number(filters.limit) || 12
  syncRouteFromQuery()
}

function resetFilters() {
  filters.center_type = 'theme'
  filters.keyword = ''
  filters.depth = 2
  filters.limit = 12
  relationFilter.value = ''
  applyFilters()
}

function syncRouteFromQuery() {
  router.replace({
    query: buildCleanQuery({
      center_type: queryFilters.center_type,
      center_key: queryFilters.center_key,
      depth: queryFilters.depth,
      limit: queryFilters.limit,
      relation_key: relationFilter.value,
    }),
  })
}

function applyRouteQuery() {
  const q = route.query as Record<string, unknown>
  const centerKey = readQueryString(q, 'center_key', readQueryString(q, 'keyword', ''))
  const next = {
    center_type: readQueryString(q, 'center_type', 'theme'),
    keyword: centerKey,
    depth: Math.max(1, Math.min(3, readQueryNumber(q, 'depth', 2))),
    limit: Math.max(8, Math.min(24, readQueryNumber(q, 'limit', 12))),
  }
  Object.assign(filters, next)
  Object.assign(queryFilters, {
    center_type: next.center_type,
    center_key: centerKey,
    depth: next.depth,
    limit: next.limit,
  })
  relationFilter.value = readQueryString(q, 'relation_key', '')
}

onMounted(() => {
  applyRouteQuery()
  applyFilters()
})
</script>
