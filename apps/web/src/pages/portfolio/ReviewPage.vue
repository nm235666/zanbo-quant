<template>
  <AppShell title="交易复盘" subtitle="执行后复盘分析：滑点统计、交易评级与经验沉淀。">
    <div class="space-y-4">
      <!-- 复盘列表 -->
      <PageSection title="复盘闭环" :subtitle="`共 ${reviews.length} 条`">
        <div v-if="reviewsLoading" class="py-8 text-center text-sm text-[var(--muted)]">加载中...</div>
        <div v-else-if="reviewsError" class="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-4 text-sm text-rose-700">
          加载复盘记录失败，请刷新重试。
        </div>
        <div v-else-if="reviews.length === 0" class="rounded-2xl border border-dashed border-[var(--line)] px-4 py-10 text-center text-sm text-[var(--muted)]">
          暂无复盘记录，完成交易后添加复盘。
        </div>
        <div v-else class="space-y-4">
          <div
            v-for="review in reviews"
            :key="review.id"
            class="rounded-2xl border border-[var(--line)] bg-white px-4 py-4"
          >
            <div class="flex flex-wrap items-start justify-between gap-2">
              <div>
                <div class="text-sm font-semibold text-[var(--ink)]">
                  订单 #{{ review.order_id || review.id }}{{ review.ts_code ? ` · ${review.ts_code}` : '' }}
                </div>
                <div class="mt-0.5 text-xs text-[var(--muted)]">{{ formatDate(review.created_at) }}</div>
              </div>
              <div class="flex items-center gap-2">
                <span :class="reviewTagClass(review.review_tag)">{{ reviewTagLabel(review.review_tag) }}</span>
                <span v-if="review.slippage != null" class="text-xs text-[var(--muted)]">
                  滑点 {{ review.slippage > 0 ? '+' : '' }}{{ review.slippage.toFixed(2) }}%
                </span>
              </div>
            </div>

            <div class="mt-3 grid gap-3 sm:grid-cols-2 xl:grid-cols-5">
              <div class="rounded-2xl border border-[var(--line)] bg-[var(--panel-soft)] px-3 py-3">
                <div class="mb-1 text-xs font-semibold uppercase text-[var(--muted)]">原始判断</div>
                <div class="text-sm font-semibold text-[var(--ink)]">{{ review.snapshot_id || review.decision_action_id || '-' }}</div>
                <div class="mt-1 text-xs leading-5 text-[var(--muted)]">{{ review.decision_payload?.trigger_reason || review.decision_note || '当前没有关联的判断说明。' }}</div>
              </div>
              <div class="rounded-2xl border border-[var(--line)] bg-[var(--panel-soft)] px-3 py-3">
                <div class="mb-1 text-xs font-semibold uppercase text-[var(--muted)]">动作建议</div>
                <div class="text-sm font-semibold text-[var(--ink)]">{{ reviewActionLabel(review.action_type) }}</div>
                <div class="mt-1 text-xs leading-5 text-[var(--muted)]">{{ review.decision_payload?.position_pct_range || review.order_note || '当前没有动作仓位说明。' }}</div>
              </div>
              <div class="rounded-2xl border border-[var(--line)] bg-[var(--panel-soft)] px-3 py-3">
                <div class="mb-1 text-xs font-semibold uppercase text-[var(--muted)]">执行结果</div>
                <div class="text-sm font-semibold text-[var(--ink)]">{{ reviewExecutionLabel(review.order_status, review.decision_payload?.execution_status) }}</div>
                <div class="mt-1 text-xs leading-5 text-[var(--muted)]">{{ review.executed_at ? `执行于 ${formatDate(review.executed_at)}` : '当前未记录执行时间。' }}</div>
              </div>
              <div class="rounded-2xl border border-[var(--line)] bg-[var(--panel-soft)] px-3 py-3">
                <div class="mb-1 text-xs font-semibold uppercase text-[var(--muted)]">结果归因</div>
                <div class="text-sm font-semibold text-[var(--ink)]">{{ reviewTagLabel(review.review_tag) }}</div>
                <div class="mt-1 text-xs leading-5 text-[var(--muted)]">{{ review.review_note || review.decision_payload?.review_conclusion || '当前还没有结果归因说明。' }}</div>
              </div>
              <div class="rounded-2xl border border-[var(--line)] bg-[var(--panel-soft)] px-3 py-3">
                <div class="mb-1 text-xs font-semibold uppercase text-[var(--muted)]">规则修正建议</div>
                <div class="text-sm font-semibold text-[var(--ink)]">{{ review.rule_correction_hint ? '已形成' : '待补充' }}</div>
                <div class="mt-1 text-xs leading-5 text-[var(--muted)]">{{ review.rule_correction_hint || '当前还没有沉淀规则修正建议。' }}</div>
              </div>
            </div>
          </div>
        </div>
      </PageSection>

      <!-- 添加复盘 -->
      <PageSection title="添加复盘" subtitle="为已执行订单录入复盘分析。">
        <div class="space-y-4">
          <div class="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
            <label class="text-sm font-semibold text-[var(--ink)]">
              订单 ID
              <input
                v-model="form.order_id"
                class="mt-1 w-full rounded-2xl border border-[var(--line)] bg-white px-4 py-3 text-sm"
                placeholder="关联订单编号（可选）"
              />
            </label>
            <label class="text-sm font-semibold text-[var(--ink)]">
              交易评级
              <select v-model="form.review_tag" class="mt-1 w-full rounded-2xl border border-[var(--line)] bg-white px-4 py-3 text-sm">
                <option value="">请选择...</option>
                <option value="win">盈利（win）</option>
                <option value="loss">亏损（loss）</option>
                <option value="neutral">中性（neutral）</option>
                <option value="pending">待评（pending）</option>
              </select>
            </label>
            <label class="text-sm font-semibold text-[var(--ink)]">
              滑点（%）
              <input
                v-model.number="form.slippage"
                type="number"
                step="0.01"
                class="mt-1 w-full rounded-2xl border border-[var(--line)] bg-white px-4 py-3 text-sm"
                placeholder="如 -0.15"
              />
            </label>
          </div>
          <label class="text-sm font-semibold text-[var(--ink)]">
            复盘笔记
            <textarea
              v-model="form.review_note"
              rows="3"
              class="mt-1 w-full rounded-2xl border border-[var(--line)] bg-white px-4 py-3 text-sm"
              placeholder="交易回顾与经验总结..."
            />
          </label>

          <div v-if="submitError" class="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
            {{ submitError }}
          </div>
          <div v-if="submitSuccess" class="rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">
            复盘记录已保存。
          </div>

          <button
            class="rounded-2xl bg-[var(--brand)] px-5 py-2.5 text-sm font-semibold text-white disabled:opacity-60"
            :disabled="!form.review_tag || submitPending"
            @click="submitReview"
          >
            {{ submitPending ? '提交中...' : '提交复盘' }}
          </button>
        </div>
      </PageSection>
    </div>
  </AppShell>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useQuery, useQueryClient } from '@tanstack/vue-query'
import AppShell from '../../shared/ui/AppShell.vue'
import PageSection from '../../shared/ui/PageSection.vue'
import { fetchPortfolioReviews, createPortfolioReview, type PortfolioReview } from '../../services/api/portfolio'

const {
  data: reviewsData,
  isPending: reviewsLoading,
  isError: reviewsError,
} = useQuery({
  queryKey: ['portfolio-reviews'],
  queryFn: () => fetchPortfolioReviews({ limit: 50 }),
})

const reviews = computed<PortfolioReview[]>(() => {
  const raw = reviewsData.value
  if (!raw) return []
  if (Array.isArray(raw)) return raw
  if (Array.isArray(raw.reviews)) return raw.reviews
  return []
})

const form = reactive({
  order_id: '',
  review_tag: '',
  slippage: null as number | null,
  review_note: '',
})

const submitPending = ref(false)
const submitError = ref('')
const submitSuccess = ref(false)
const queryClient = useQueryClient()

function formatDate(s?: string): string {
  if (!s) return '-'
  try {
    return new Date(s).toLocaleDateString('zh-CN')
  } catch {
    return s
  }
}

function reviewTagLabel(t?: string): string {
  const map: Record<string, string> = { win: '盈利', loss: '亏损', neutral: '中性', pending: '待评' }
  return t ? (map[t] ?? t) : '-'
}

function reviewActionLabel(action?: string): string {
  const map: Record<string, string> = {
    buy: '新买',
    add: '加仓',
    reduce: '减仓',
    sell: '卖出',
    close: '清仓',
    watch: '观察',
    defer: '暂缓',
  }
  return action ? (map[action] ?? action) : '未关联动作'
}

function reviewExecutionLabel(orderStatus?: string, decisionExecutionStatus?: string): string {
  const status = orderStatus || decisionExecutionStatus || ''
  const map: Record<string, string> = {
    planned: '待执行',
    partial: '部分执行',
    executed: '已执行',
    cancelled: '已取消',
    executing: '执行中',
    done: '已完成',
  }
  return status ? (map[status] ?? status) : '未关联执行状态'
}

function reviewTagClass(t?: string): string {
  const base = 'inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-semibold'
  if (t === 'win') return `${base} border-emerald-200 bg-emerald-100 text-emerald-700`
  if (t === 'loss') return `${base} border-rose-200 bg-rose-100 text-rose-700`
  if (t === 'neutral') return `${base} border-sky-200 bg-sky-100 text-sky-700`
  return `${base} border-[var(--line)] bg-[var(--panel-soft)] text-[var(--muted)]`
}

async function submitReview() {
  if (!form.review_tag) return
  submitPending.value = true
  submitError.value = ''
  submitSuccess.value = false
  try {
    await createPortfolioReview({
      order_id: form.order_id || undefined,
      review_tag: form.review_tag,
      slippage: form.slippage ?? undefined,
      review_note: form.review_note || undefined,
    })
    submitSuccess.value = true
    form.order_id = ''
    form.review_tag = ''
    form.slippage = null
    form.review_note = ''
    await queryClient.invalidateQueries({ queryKey: ['portfolio-reviews'] })
  } catch (e: any) {
    submitError.value = e?.message || '提交失败'
  } finally {
    submitPending.value = false
  }
}
</script>
