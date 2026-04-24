<template>
  <AppShell title="候选漏斗" subtitle="候选股票从进入到执行的完整状态机管理，支持按阶段过滤与流转操作。">
    <div class="space-y-4">
      <div class="rounded-[18px] border border-[var(--line)] bg-white/80 px-4 py-3 text-sm">
        <div class="flex flex-wrap items-center gap-2">
          <span class="text-xs font-semibold uppercase tracking-[0.14em] text-[var(--muted)]">可用性分级</span>
          <span class="rounded-full px-2.5 py-1 text-xs font-semibold" :class="availabilityBadgeClass">{{ availabilityLabel }}</span>
          <span class="text-xs text-[var(--muted)]">{{ availabilityReason }}</span>
        </div>
        <div class="mt-2 flex flex-wrap gap-2 text-xs">
          <span v-if="upstreamScoreDate" class="metric-chip">上游评分日期 {{ upstreamScoreDate }}</span>
          <span class="metric-chip">上游评分样本 {{ upstreamScoreCount }}</span>
          <span class="metric-chip">漏斗总量 {{ funnelTotal }}</span>
          <span v-for="item in availabilityMissingInputs" :key="item" class="metric-chip text-amber-700">{{ item }}</span>
        </div>
        <p class="mt-3 text-xs leading-relaxed text-[var(--muted)]">
          定时任务：<code class="rounded bg-[var(--panel-soft)] px-1">funnel_ingested_score_align</code>（评分对齐：已进入→已增强）、
          <code class="rounded bg-[var(--panel-soft)] px-1">funnel_review_refresh</code>（复盘快照）。可通过
          <code class="rounded bg-[var(--panel-soft)] px-1">/api/jobs/trigger?job_key=…</code> 或 <code class="rounded bg-[var(--panel-soft)] px-1">jobs/run_funnel_job.py</code> 触发；说明见仓库
          <code class="rounded bg-[var(--panel-soft)] px-1">docs/funnel_operating_model_cn.md</code>。
        </p>
      </div>

      <PageSection title="新建候选" subtitle="将标的加入漏斗，初始为「已进入」。代码自动转大写；名称若留空则使用代码作为名称（与后端必填一致）。">
        <div class="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <label class="text-sm font-semibold text-[var(--ink)]">
            证券代码
            <input
              v-model.trim="createForm.ts_code"
              data-testid="funnel-create-ts-code"
              class="mt-1 w-full rounded-2xl border border-[var(--line)] bg-white px-4 py-3 text-sm uppercase"
              placeholder="如 000001.SZ"
            />
          </label>
          <label class="text-sm font-semibold text-[var(--ink)]">
            名称
            <input
              v-model.trim="createForm.name"
              data-testid="funnel-create-name"
              class="mt-1 w-full rounded-2xl border border-[var(--line)] bg-white px-4 py-3 text-sm"
              placeholder="与代码一致或公司简称"
            />
          </label>
          <label class="text-sm font-semibold text-[var(--ink)] sm:col-span-2">
            入池说明（可选）
            <input
              v-model.trim="createForm.reason"
              class="mt-1 w-full rounded-2xl border border-[var(--line)] bg-white px-4 py-3 text-sm"
              placeholder="为何纳入漏斗"
            />
          </label>
        </div>
        <div v-if="createError" class="mt-3 rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
          {{ createError }}
        </div>
        <div v-if="createSuccess" class="mt-3 rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">
          已加入漏斗。
        </div>
        <div class="mt-3 flex flex-wrap gap-2">
          <button
            type="button"
            data-testid="funnel-create-submit"
            class="rounded-2xl bg-[var(--brand)] px-5 py-2.5 text-sm font-semibold text-white disabled:opacity-60"
            :disabled="createPending || !createForm.ts_code.trim()"
            @click="submitCreateCandidate"
          >
            {{ createPending ? '提交中…' : '加入漏斗' }}
          </button>
        </div>
      </PageSection>

      <!-- 漏斗概览 stat cards -->
      <PageSection title="漏斗概览" subtitle="各阶段候选数量统计。">
        <div class="grid gap-3 grid-cols-2 sm:grid-cols-4 xl:grid-cols-5">
          <button
            v-for="s in STATE_LIST"
            :key="s.key"
            class="rounded-[var(--radius-md)] border p-3 text-left transition hover:shadow-[var(--shadow-card)]"
            :class="[
              activeFilter === s.key
                ? 'border-[var(--brand)] bg-[var(--brand)]/5 shadow-[var(--shadow-card)]'
                : 'border-[var(--line)] bg-white shadow-[var(--shadow-soft)]',
            ]"
            @click="toggleFilter(s.key)"
          >
            <div class="text-xs font-semibold uppercase tracking-[0.12em] text-[var(--muted)]">{{ s.label }}</div>
            <div class="mt-1.5 text-2xl font-extrabold" :class="s.colorClass">
              {{ stateCountMap[s.key] ?? 0 }}
            </div>
          </button>
        </div>
      </PageSection>

      <!-- 漏斗指标 -->
      <PageSection title="漏斗指标" subtitle="整体转化效率指标。">
        <div v-if="metricsLoading" class="text-sm text-[var(--muted)]">加载中...</div>
        <MetricGrid
          v-else
          :items="metricsItems"
          columns-class="grid-cols-3"
        />
      </PageSection>

      <!-- 候选列表 -->
      <PageSection title="候选列表" :subtitle="listSubtitle">
        <template #action>
          <div class="flex flex-wrap gap-2">
            <button
              class="rounded-full border px-3 py-1 text-xs font-semibold transition"
              :class="activeFilter === '' ? 'border-[var(--brand)] bg-[var(--brand)] text-white' : 'border-[var(--line)] bg-white text-[var(--ink)] hover:border-[var(--brand)] hover:text-[var(--brand)]'"
              @click="setListFilter('')"
            >
              全部
            </button>
            <button
              v-for="s in STATE_LIST"
              :key="s.key"
              class="rounded-full border px-3 py-1 text-xs font-semibold transition"
              :class="activeFilter === s.key ? 'border-[var(--brand)] bg-[var(--brand)] text-white' : 'border-[var(--line)] bg-white text-[var(--ink)] hover:border-[var(--brand)] hover:text-[var(--brand)]'"
              @click="toggleFilter(s.key)"
            >
              {{ s.label }}
            </button>
          </div>
        </template>

        <div class="mb-4 flex flex-wrap items-end gap-2">
          <label class="text-sm font-semibold text-[var(--ink)]">
            搜索代码/名称
            <input
              v-model.trim="listSearchInput"
              data-testid="funnel-list-search"
              class="mt-1 w-48 rounded-2xl border border-[var(--line)] bg-white px-3 py-2 text-sm"
              placeholder="如 000001"
              @keyup.enter="applyListSearch"
            />
          </label>
          <button
            type="button"
            class="rounded-2xl border border-[var(--line)] bg-white px-4 py-2 text-xs font-semibold text-[var(--ink)] hover:border-[var(--brand)]"
            @click="applyListSearch"
          >
            搜索
          </button>
          <span class="pb-1 text-xs text-[var(--muted)]">每页 {{ pageSize }} 条，服务端筛选。</span>
        </div>

        <div
          v-if="!candidatesLoading && !candidatesError && listTotal > 0"
          class="mb-3 flex flex-wrap items-center justify-between gap-2 text-xs text-[var(--muted)]"
        >
          <span>第 {{ listPage }} / {{ totalPages }} 页，共 {{ listTotal }} 条</span>
          <div class="flex gap-2">
            <button
              type="button"
              class="rounded-full border border-[var(--line)] bg-white px-3 py-1 font-semibold disabled:opacity-40"
              :disabled="listPage <= 1"
              @click="listPage = Math.max(1, listPage - 1)"
            >
              上一页
            </button>
            <button
              type="button"
              class="rounded-full border border-[var(--line)] bg-white px-3 py-1 font-semibold disabled:opacity-40"
              :disabled="listPage >= totalPages"
              @click="listPage = Math.min(totalPages, listPage + 1)"
            >
              下一页
            </button>
          </div>
        </div>

        <div v-if="candidatesLoading" class="py-8 text-center text-sm text-[var(--muted)]">加载中...</div>
        <div v-else-if="candidatesError" class="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-4 text-sm text-rose-700">
          加载候选列表失败，请刷新重试。
        </div>
        <div v-else-if="listTotal === 0 && activeFilter" class="rounded-2xl border border-dashed border-[var(--line)] px-4 py-10 text-center text-sm text-[var(--muted)]">
          {{ `当前阶段（${stateLabel(activeFilter)}）暂无候选` }}
        </div>
        <div v-else-if="listTotal === 0 && listSearchApplied" class="rounded-2xl border border-dashed border-[var(--line)] px-4 py-10 text-center text-sm text-[var(--muted)]">
          无匹配「{{ listSearchApplied }}」的标的，请调整关键词。
        </div>
        <div v-else-if="listTotal === 0" class="rounded-2xl border border-dashed border-[var(--line)] bg-gray-50 px-6 py-8 text-center">
          <div class="text-sm font-semibold text-[var(--ink)]">候选池暂无标的</div>
          <div class="mt-2 text-xs text-[var(--muted)]">候选标的尚未进入漏斗，或当前筛选条件无结果。</div>
          <div class="mt-4 flex flex-wrap justify-center gap-2">
            <RouterLink to="/app/desk/market" class="rounded-full border border-[var(--brand)] bg-white px-4 py-2 text-xs font-semibold text-[var(--brand)]">
              查看市场结论获取方向
            </RouterLink>
            <RouterLink to="/app/data/signals/overview" class="rounded-full border border-[var(--line)] bg-white px-4 py-2 text-xs font-semibold text-[var(--ink)]">
              从信号中发现候选
            </RouterLink>
            <RouterLink to="/app/data/chatrooms/investment" class="rounded-full border border-[var(--line)] bg-white px-4 py-2 text-xs font-semibold text-[var(--ink)]">
              从群聊候选池导入
            </RouterLink>
          </div>
        </div>
        <div v-else-if="allCandidates.length === 0" class="rounded-2xl border border-dashed border-[var(--line)] px-4 py-8 text-center text-sm text-[var(--muted)]">
          本页无数据，请翻页或清空筛选。
        </div>
        <div v-else class="divide-y divide-[var(--line)]">
          <div
            v-for="candidate in allCandidates"
            :key="candidate.id"
            class="cursor-pointer py-3 transition hover:bg-[var(--panel-soft)]"
            :class="{ 'bg-[var(--brand)]/5': selectedId === candidate.id }"
            @click="selectCandidate(candidate)"
          >
            <div class="flex flex-wrap items-start justify-between gap-2">
              <div class="min-w-0">
                <div class="text-sm font-semibold text-[var(--ink)]">
                  {{ candidate.ts_code }}
                  <span v-if="candidate.name" class="ml-1 font-normal text-[var(--muted)]">{{ candidate.name }}</span>
                  <span
                    v-if="isStaleIngested(candidate)"
                    class="ml-2 rounded-full border border-amber-300 bg-amber-50 px-2 py-0.5 text-[10px] font-semibold text-amber-800"
                  >
                    已进入 ≥{{ staleIngestedDays }} 天
                  </span>
                  <span
                    v-if="candidate.evidence_summary"
                    class="ml-2 rounded-full border px-2 py-0.5 text-[10px] font-semibold"
                    :class="evidenceBadgeClass(candidate.evidence_summary)"
                  >
                    {{ evidenceStatusLabel(candidate.evidence_summary) }}
                  </span>
                </div>
                <div v-if="candidate.last_transition_reason" class="mt-0.5 text-xs text-[var(--muted)] truncate max-w-sm">
                  {{ candidate.last_transition_reason }}
                </div>
                <div v-if="candidate.evidence_summary" class="mt-1 flex flex-wrap gap-1.5 text-[10px] text-[var(--muted)]">
                  <span class="metric-chip">评分 {{ formatMaybeNumber(candidate.evidence_summary.total_score, 1) }}</span>
                  <span class="metric-chip">新闻 {{ candidate.evidence_summary.news_count || 0 }}</span>
                  <span class="metric-chip">信号 {{ candidate.evidence_summary.signal_count || 0 }}</span>
                  <span class="metric-chip">群聊 {{ candidate.evidence_summary.candidate_pool_count || 0 }}</span>
                </div>
              </div>
              <div class="flex items-center gap-2">
                <span :class="stateBadgeClass(candidate.current_state)">
                  {{ stateLabel(candidate.current_state) }}
                </span>
                <span v-if="candidate.state_version != null" class="text-[10px] font-mono text-[var(--muted)]">v{{ candidate.state_version }}</span>
                <div v-if="candidate.last_updated" class="text-xs text-[var(--muted)]">
                  {{ formatDate(candidate.last_updated) }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </PageSection>

      <!-- 流转操作面板 -->
      <PageSection v-if="selectedCandidate" title="流转操作" subtitle="仅展示与后端一致的可选目标状态；提交时携带版本号与幂等键以防重复提交。">
        <div class="space-y-4">
          <div class="flex flex-wrap items-center gap-3">
            <div class="text-sm font-semibold text-[var(--ink)]">
              {{ selectedCandidate.ts_code }}
              <span v-if="selectedCandidate.name" class="font-normal text-[var(--muted)]">{{ selectedCandidate.name }}</span>
            </div>
            <span :class="stateBadgeClass(selectedCandidate.current_state)">
              当前：{{ stateLabel(selectedCandidate.current_state) }}
            </span>
            <span class="text-xs text-[var(--muted)]">状态版本 {{ selectedCandidate.state_version ?? '—' }}</span>
          </div>

          <div class="rounded-2xl border px-4 py-3" :class="evidenceChainComplete ? 'border-emerald-200 bg-emerald-50' : 'border-amber-200 bg-amber-50'">
            <div class="flex flex-wrap items-center justify-between gap-2">
              <div>
                <div class="text-xs font-semibold" :class="evidenceChainComplete ? 'text-emerald-700' : 'text-amber-700'">候选证据包</div>
                <div class="mt-1 text-sm font-bold text-[var(--ink)]">{{ evidencePanelTitle }}</div>
              </div>
              <span class="rounded-full border bg-white px-2.5 py-1 text-xs font-semibold" :class="evidenceChainComplete ? 'border-emerald-200 text-emerald-700' : 'border-amber-200 text-amber-700'">
                {{ evidenceStatusLabel(selectedCandidate.evidence_summary || evidenceSummaryFromPacket) }}
              </span>
            </div>
            <div v-if="candidateDetailLoading" class="mt-3 rounded-xl border border-dashed border-[var(--line)] bg-white px-3 py-4 text-sm text-[var(--muted)]">
              正在加载证据包…
            </div>
            <div v-else-if="!hasEvidencePacket" class="mt-3 rounded-xl border border-dashed border-amber-200 bg-white px-3 py-4 text-sm text-amber-800">
              后端未返回证据包，请刷新页面或确认 API 已重启到最新版本。
            </div>
            <div v-if="evidenceWarnings.length" class="mt-2 space-y-1 text-xs text-amber-800">
              <div v-for="warning in evidenceWarnings" :key="warning">{{ warning }}</div>
            </div>
            <div v-if="hasEvidencePacket" class="mt-3 grid gap-2 md:grid-cols-2">
              <div class="rounded-xl border border-[var(--line)] bg-white px-3 py-2 text-xs text-[var(--muted)]">
                <div class="font-semibold text-[var(--ink)]">评分</div>
                <div class="mt-1">总分 {{ formatMaybeNumber(evidencePacket.score?.total_score, 1) }} · {{ evidencePacket.score?.position_label || '-' }}</div>
                <div class="mt-1 truncate">{{ evidencePacket.score?.decision_reason || '暂无评分理由' }}</div>
              </div>
              <div class="rounded-xl border border-[var(--line)] bg-white px-3 py-2 text-xs text-[var(--muted)]">
                <div class="font-semibold text-[var(--ink)]">新闻</div>
                <div class="mt-1">总数 {{ evidencePacket.news?.count || 0 }} · 高重要 {{ evidencePacket.news?.high_importance_count || 0 }}</div>
                <div class="mt-1 truncate">{{ evidencePacket.news?.items?.[0]?.title || '暂无个股新闻' }}</div>
              </div>
              <div class="rounded-xl border border-[var(--line)] bg-white px-3 py-2 text-xs text-[var(--muted)]">
                <div class="font-semibold text-[var(--ink)]">信号</div>
                <div class="mt-1">命中 {{ evidencePacket.signals?.count || 0 }} · 最近 {{ evidencePacket.signals?.latest_signal_date || '-' }}</div>
                <div class="mt-1 truncate">{{ (evidencePacket.signals?.directions || []).join(' / ') || '暂无方向' }}</div>
              </div>
              <div class="rounded-xl border border-[var(--line)] bg-white px-3 py-2 text-xs text-[var(--muted)]">
                <div class="font-semibold text-[var(--ink)]">群聊候选池</div>
                <div class="mt-1">匹配 {{ evidencePacket.candidate_pool?.matched_count || 0 }} · 偏向 {{ evidencePacket.candidate_pool?.dominant_bias || '-' }}</div>
                <div class="mt-1">提及 {{ evidencePacket.candidate_pool?.mention_count || 0 }} · 群数 {{ evidencePacket.candidate_pool?.room_count || 0 }}</div>
              </div>
            </div>
          </div>

          <div class="rounded-2xl border border-[var(--line)] bg-[var(--panel-soft)] px-4 py-3 text-xs text-[var(--muted)]">
            触发来源取值与后端优先级表一致（见
            <code class="rounded bg-white/80 px-1">TRIGGER_SOURCE_PRIORITY</code>
            ）。手动操作请选「手动 / 研究员」。
          </div>

          <div class="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            <label class="text-sm font-semibold text-[var(--ink)]">
              目标状态
              <select v-model="transitionForm.to_state" class="mt-1 w-full rounded-2xl border border-[var(--line)] bg-white px-4 py-3 text-sm">
                <option value="">请选择...</option>
                <option v-for="s in nextStates" :key="s.key" :value="s.key">{{ s.label }}</option>
              </select>
            </label>
            <label class="text-sm font-semibold text-[var(--ink)]">
              触发来源
              <select v-model="transitionForm.trigger_source" class="mt-1 w-full rounded-2xl border border-[var(--line)] bg-white px-4 py-3 text-sm">
                <option v-for="opt in TRIGGER_SOURCE_OPTIONS" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
              </select>
            </label>
            <label class="text-sm font-semibold text-[var(--ink)]">
              流转原因
              <input
                v-model="transitionForm.reason"
                class="mt-1 w-full rounded-2xl border border-[var(--line)] bg-white px-4 py-3 text-sm"
                placeholder="简要说明（可选）"
              />
            </label>
            <label class="text-sm font-semibold text-[var(--ink)]">
              证据引用（可选）
              <input
                v-model="transitionForm.evidence_ref"
                class="mt-1 w-full rounded-2xl border border-[var(--line)] bg-white px-4 py-3 text-sm"
                placeholder="链接、快照 ID 等"
              />
            </label>
          </div>

          <div>
            <div class="text-xs font-semibold uppercase tracking-[0.12em] text-[var(--muted)]">流转历史</div>
            <div v-if="candidateDetailLoading" class="mt-2 text-sm text-[var(--muted)]">加载中…</div>
            <ul v-else-if="transitionsList.length" class="mt-2 max-h-48 space-y-2 overflow-y-auto text-sm">
              <li
                v-for="(t, idx) in transitionsList"
                :key="String(t.id || idx)"
                class="rounded-xl border border-[var(--line)] bg-white px-3 py-2"
              >
                <span class="font-mono text-xs text-[var(--muted)]">{{ formatDate(String(t.created_at || '')) }}</span>
                <span class="ml-2">{{ stateLabel(String(t.from_state || '')) }} → {{ stateLabel(String(t.to_state || '')) }}</span>
                <span v-if="t.trigger_source" class="ml-2 text-xs text-[var(--muted)]">{{ triggerSourceLabel(String(t.trigger_source)) }}</span>
                <div v-if="t.reason" class="mt-1 text-xs text-[var(--muted)]">{{ t.reason }}</div>
              </li>
            </ul>
            <div v-else class="mt-2 text-sm text-[var(--muted)]">暂无历史记录。</div>
          </div>

          <div class="mt-4">
            <div class="text-xs font-semibold uppercase tracking-[0.12em] text-[var(--muted)]">复盘快照（T+N 收盘收益）</div>
            <div v-if="reviewSnapLoading" class="mt-2 text-sm text-[var(--muted)]">加载中…</div>
            <ul v-else-if="reviewRows.length" class="mt-2 max-h-40 space-y-1 overflow-y-auto text-xs text-[var(--muted)]">
              <li v-for="(rv, idx) in reviewRows" :key="String(rv.id || idx)">
                {{ rv.ref_date }} · {{ rv.horizon_days }} 日 {{ rv.return_pct }}% · {{ rv.basis }}
              </li>
            </ul>
            <div v-else class="mt-2 text-xs text-[var(--muted)]">暂无快照。任务 <code class="rounded bg-[var(--panel-soft)] px-1">funnel_review_refresh</code> 写入 <code class="rounded bg-[var(--panel-soft)] px-1">funnel_review_snapshots</code>。</div>
          </div>

          <div v-if="transitionError" class="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
            流转失败：{{ transitionError }}
          </div>
          <div v-if="transitionSuccess" class="rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">
            流转成功！
          </div>

          <div class="flex gap-2">
            <button
              class="rounded-2xl bg-[var(--brand)] px-5 py-2.5 text-sm font-semibold text-white disabled:opacity-60"
              :disabled="!transitionForm.to_state || transitionPending"
              @click="doTransition"
            >
              {{ transitionPending ? '处理中...' : '确认流转' }}
            </button>
            <button
              class="rounded-2xl border border-[var(--line)] bg-white px-5 py-2.5 text-sm font-semibold text-[var(--ink)]"
              @click="clearSelection"
            >
              取消
            </button>
          </div>
        </div>
      </PageSection>
    </div>
  </AppShell>
</template>

<script setup lang="ts">
import { ref, computed, reactive, watch, onMounted } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { useQuery, useQueryClient } from '@tanstack/vue-query'
import AppShell from '../../shared/ui/AppShell.vue'
import PageSection from '../../shared/ui/PageSection.vue'
import MetricGrid from '../../shared/ui/MetricGrid.vue'
import type { MetricGridItem } from '../../shared/ui/MetricGrid.vue'
import { useAuthStore } from '../../stores/auth'
import {
  createFunnelCandidate,
  fetchFunnelCandidate,
  fetchFunnelCandidates,
  fetchFunnelMetrics,
  fetchFunnelReviewSnapshots,
  transitionFunnelCandidate,
  type FunnelCandidate,
  type FunnelEvidencePacket,
  type FunnelEvidenceSummary,
  type FunnelMetrics,
} from '../../services/api/funnel'

interface StateConfig {
  key: string
  label: string
  colorClass: string
  badgeClass: string
}

const STATE_LIST: StateConfig[] = [
  { key: 'ingested', label: '已进入', colorClass: 'text-gray-600', badgeClass: 'inline-flex items-center rounded-full border border-gray-200 bg-gray-100 px-2.5 py-1 text-xs font-semibold text-gray-700' },
  { key: 'amplified', label: '已增强', colorClass: 'text-blue-600', badgeClass: 'inline-flex items-center rounded-full border border-blue-200 bg-blue-100 px-2.5 py-1 text-xs font-semibold text-blue-700' },
  { key: 'ai_screen_passed', label: 'AI初筛', colorClass: 'text-purple-600', badgeClass: 'inline-flex items-center rounded-full border border-purple-200 bg-purple-100 px-2.5 py-1 text-xs font-semibold text-purple-700' },
  { key: 'shortlisted', label: '短名单', colorClass: 'text-cyan-600', badgeClass: 'inline-flex items-center rounded-full border border-cyan-200 bg-cyan-100 px-2.5 py-1 text-xs font-semibold text-cyan-700' },
  { key: 'decision_ready', label: '待决策', colorClass: 'text-amber-600', badgeClass: 'inline-flex items-center rounded-full border border-amber-200 bg-amber-100 px-2.5 py-1 text-xs font-semibold text-amber-700' },
  { key: 'confirmed', label: '已确认', colorClass: 'text-emerald-600', badgeClass: 'inline-flex items-center rounded-full border border-emerald-200 bg-emerald-100 px-2.5 py-1 text-xs font-semibold text-emerald-700' },
  { key: 'rejected', label: '已淘汰', colorClass: 'text-rose-600', badgeClass: 'inline-flex items-center rounded-full border border-rose-200 bg-rose-100 px-2.5 py-1 text-xs font-semibold text-rose-700' },
  { key: 'deferred', label: '已暂缓', colorClass: 'text-orange-600', badgeClass: 'inline-flex items-center rounded-full border border-orange-200 bg-orange-100 px-2.5 py-1 text-xs font-semibold text-orange-700' },
  { key: 'executed', label: '已执行', colorClass: 'text-emerald-700', badgeClass: 'inline-flex items-center rounded-full border border-emerald-300 bg-emerald-200 px-2.5 py-1 text-xs font-semibold text-emerald-800' },
  { key: 'reviewed', label: '已复盘', colorClass: 'text-teal-600', badgeClass: 'inline-flex items-center rounded-full border border-teal-200 bg-teal-100 px-2.5 py-1 text-xs font-semibold text-teal-700' },
]

/** Must match `VALID_TRANSITIONS` in services/funnel_service/service.py */
const STATE_TRANSITIONS: Record<string, string[]> = {
  ingested: ['amplified', 'rejected'],
  amplified: ['ai_screen_passed', 'rejected'],
  ai_screen_passed: ['shortlisted', 'rejected'],
  shortlisted: ['decision_ready', 'deferred', 'rejected'],
  decision_ready: ['confirmed', 'rejected', 'deferred'],
  confirmed: ['executed'],
  deferred: ['executed', 'rejected', 'shortlisted'],
  executed: ['reviewed'],
  rejected: [],
  reviewed: [],
}

const TRIGGER_SOURCE_OPTIONS = [
  { value: 'researcher', label: '手动 / 研究员' },
  { value: 'decision_action', label: '决策看板' },
  { value: 'ai_screen', label: 'AI 筛选' },
  { value: 'system_rule', label: '系统规则' },
  { value: 'signal', label: '信号' },
  { value: 'execution_feedback', label: '执行反馈' },
] as const

const route = useRoute()
const staleIngestedDays = 14
const listPage = ref(1)
const pageSize = 50
const listSearchInput = ref('')
const listSearchApplied = ref('')

const activeFilter = ref('')
const selectedCandidate = ref<FunnelCandidate | null>(null)
const selectedId = ref<string>('')
const transitionForm = reactive({ to_state: '', trigger_source: 'researcher', reason: '', evidence_ref: '' })
const transitionError = ref('')
const transitionSuccess = ref(false)
const transitionPending = ref(false)

const createForm = reactive({ ts_code: '', name: '', reason: '', source: 'desk_manual' })
const createError = ref('')
const createSuccess = ref(false)
const createPending = ref(false)

const authStore = useAuthStore()
const queryClient = useQueryClient()

const {
  data: candidatesData,
  isPending: candidatesLoading,
  isError: candidatesError,
} = useQuery({
  queryKey: computed(() => ['funnel-candidates', listPage.value, activeFilter.value, listSearchApplied.value]),
  queryFn: () =>
    fetchFunnelCandidates({
      state: activeFilter.value || undefined,
      q: listSearchApplied.value || undefined,
      limit: pageSize,
      offset: (listPage.value - 1) * pageSize,
      include_evidence: 1,
    }),
})

const {
  data: metricsData,
  isPending: metricsLoading,
} = useQuery({
  queryKey: ['funnel-metrics'],
  queryFn: fetchFunnelMetrics,
})

const {
  data: candidateDetailRaw,
  isPending: candidateDetailLoading,
} = useQuery({
  queryKey: computed(() => ['funnel-candidate', selectedId.value]),
  queryFn: () => fetchFunnelCandidate(selectedId.value),
  enabled: computed(() => Boolean(selectedId.value)),
})

const {
  data: reviewSnapData,
  isPending: reviewSnapLoading,
} = useQuery({
  queryKey: computed(() => ['funnel-review-shots', selectedId.value]),
  queryFn: () => fetchFunnelReviewSnapshots(selectedId.value),
  enabled: computed(() => Boolean(selectedId.value)),
})

const reviewRows = computed(() => {
  const d = reviewSnapData.value as Record<string, unknown> | null | undefined
  if (!d || !Array.isArray(d.items)) return []
  return d.items as Record<string, unknown>[]
})

const transitionsList = computed(() => {
  const d = candidateDetailRaw.value as Record<string, unknown> | null | undefined
  if (!d || !Array.isArray(d.transitions)) return []
  return d.transitions as Record<string, unknown>[]
})

const candidateDetail = computed<Record<string, any>>(() => (candidateDetailRaw.value || {}) as Record<string, any>)
const evidencePacket = computed<FunnelEvidencePacket>(() => (candidateDetail.value.evidence_packet || {}) as FunnelEvidencePacket)
const hasEvidencePacket = computed(() => Object.keys(evidencePacket.value || {}).length > 0)
const evidenceWarnings = computed<string[]>(() => {
  const warnings = candidateDetail.value.warning_messages
  if (Array.isArray(warnings)) return warnings.map((item) => String(item)).filter(Boolean)
  const packetWarnings = evidencePacket.value.warning_messages
  return Array.isArray(packetWarnings) ? packetWarnings.map((item) => String(item)).filter(Boolean) : []
})
const evidenceChainComplete = computed(() => Boolean(candidateDetail.value.evidence_chain_complete ?? evidencePacket.value.evidence_chain_complete))
const evidencePanelTitle = computed(() => {
  if (candidateDetailLoading.value) return '正在加载候选证据包'
  if (!hasEvidencePacket.value) return '证据包未返回'
  return evidenceChainComplete.value ? '证据链完整' : '证据链不完整，动作可继续但建议补证据'
})
const evidenceSummaryFromPacket = computed<FunnelEvidenceSummary>(() => ({
  evidence_status: String(evidencePacket.value.evidence_status || ''),
  evidence_chain_complete: Boolean(evidencePacket.value.evidence_chain_complete),
  missing_evidence: Array.isArray(evidencePacket.value.missing_evidence) ? evidencePacket.value.missing_evidence : [],
  warning_messages: Array.isArray(evidencePacket.value.warning_messages) ? evidencePacket.value.warning_messages : [],
  total_score: evidencePacket.value.score?.total_score,
  news_count: Number(evidencePacket.value.news?.count || 0),
  signal_count: Number(evidencePacket.value.signals?.count || 0),
  candidate_pool_count: Number(evidencePacket.value.candidate_pool?.matched_count || 0),
}))

const allCandidates = computed<FunnelCandidate[]>(() => {
  const raw = candidatesData.value
  if (!raw) return []
  const rows = Array.isArray(raw) ? raw : Array.isArray(raw.items) ? raw.items : Array.isArray(raw.candidates) ? raw.candidates : []
  return rows.map((item: any) => ({
    id: String(item?.id || ''),
    ts_code: String(item?.ts_code || '').toUpperCase(),
    name: String(item?.name || ''),
    current_state: String(item?.current_state || item?.state || ''),
    state_version: item?.state_version != null ? Number(item.state_version) : undefined,
    last_transition_reason: String(item?.last_transition_reason || item?.reason || ''),
    last_updated: String(item?.last_updated || item?.updated_at || ''),
    created_at: String(item?.created_at || ''),
    evidence_summary: item?.evidence_summary || undefined,
  }))
})

const metricsPayload = computed<Record<string, any>>(() => (metricsData.value || {}) as Record<string, any>)
const candidatesPayload = computed<Record<string, any>>(() => (candidatesData.value || {}) as Record<string, any>)
const listTotal = computed(() => Number(candidatesPayload.value.total ?? 0))
const totalPages = computed(() => Math.max(1, Math.ceil(listTotal.value / pageSize)))

const stateCountMap = computed(() => {
  const apiCounts = metricsPayload.value?.state_counts
  if (apiCounts && typeof apiCounts === 'object') {
    return Object.fromEntries(Object.entries(apiCounts).map(([k, v]) => [k, Number(v || 0)]))
  }
  const map: Record<string, number> = {}
  for (const c of allCandidates.value) {
    map[c.current_state] = (map[c.current_state] || 0) + 1
  }
  return map
})

const listSubtitle = computed(() => {
  const f = activeFilter.value ? `阶段：${stateLabel(activeFilter.value)} · ` : ''
  const q = listSearchApplied.value ? `关键词「${listSearchApplied.value}」· ` : ''
  return `${f}${q}本页 ${allCandidates.value.length} 条，符合条件 ${listTotal.value} 条`
})

function applyPrefillFromRoute() {
  const pre = String(route.query.prefill_ts || route.query.ts_code || '').trim().toUpperCase()
  if (pre) createForm.ts_code = pre
}

onMounted(() => {
  applyPrefillFromRoute()
})

watch(
  () => route.query.prefill_ts,
  () => applyPrefillFromRoute(),
)

function applyListSearch() {
  listSearchApplied.value = listSearchInput.value.trim()
  listPage.value = 1
}

function setListFilter(key: string) {
  activeFilter.value = key
  listPage.value = 1
}

function daysSinceUpdate(iso: string): number {
  if (!iso) return 0
  const t = new Date(iso).getTime()
  if (Number.isNaN(t)) return 0
  return Math.floor((Date.now() - t) / 86400000)
}

function isStaleIngested(c: FunnelCandidate): boolean {
  if (c.current_state !== 'ingested') return false
  const ref = c.last_updated || c.created_at || ''
  return daysSinceUpdate(ref) >= staleIngestedDays
}

function formatMaybeNumber(value: unknown, digits = 1): string {
  const n = Number(value)
  return Number.isFinite(n) ? n.toFixed(digits) : '-'
}

function evidenceStatusLabel(summary?: FunnelEvidenceSummary): string {
  if (!summary) return '无证据'
  if (summary.evidence_chain_complete || summary.evidence_status === 'complete') return '证据完整'
  const missing = Array.isArray(summary.missing_evidence) ? summary.missing_evidence : []
  if (missing.includes('score')) return '缺评分'
  if (missing.length) return `缺${missing.length}项证据`
  return '证据不足'
}

function evidenceBadgeClass(summary?: FunnelEvidenceSummary): string {
  if (summary?.evidence_chain_complete || summary?.evidence_status === 'complete') return 'border-emerald-200 bg-emerald-50 text-emerald-700'
  return 'border-amber-200 bg-amber-50 text-amber-700'
}

const metricsItems = computed<MetricGridItem[]>(() => {
  const m = metricsPayload.value as FunnelMetrics & Record<string, unknown>
  const total = Number((m.total ?? m.candidate_count ?? allCandidates.value.length) || 0)
  const decisionReady = Number(stateCountMap.value.decision_ready || 0)
  const executed = Number(stateCountMap.value.executed || 0)
  const reviewed = Number(stateCountMap.value.reviewed || 0)
  const apiConv = m.conversion_rate
  const conversionDisplay =
    apiConv != null && Number.isFinite(Number(apiConv))
      ? `${(Number(apiConv) * 100).toFixed(1)}%`
      : total > 0
        ? `${(((executed + reviewed) / total) * 100).toFixed(1)}%`
        : '-'
  const apiAvg = m.avg_days_to_decision
  const avgDisplay =
    apiAvg != null && Number.isFinite(Number(apiAvg)) ? `${Number(apiAvg).toFixed(1)} 天` : '-'
  return [
    { label: '候选总数', value: total || '-' },
    { label: '平均决策天数', value: avgDisplay },
    { label: '待决策', value: decisionReady },
    { label: '转化率', value: conversionDisplay },
  ]
})

const availabilityStatus = computed(() => {
  const fromMetrics = String(metricsPayload.value.status || '').trim()
  if (fromMetrics) return fromMetrics
  return String(candidatesPayload.value.status || '').trim() || 'unknown'
})
const availabilityReason = computed(() => {
  const reason = String(metricsPayload.value.status_reason || candidatesPayload.value.status_reason || '').trim()
  if (reason) return reason
  if (availabilityStatus.value === 'ready') return '漏斗链路可用于筛选与流转。'
  if (availabilityStatus.value === 'degraded') return '部分上游已就绪，但漏斗候选仍需补齐。'
  if (availabilityStatus.value === 'not_initialized') return '漏斗表尚未初始化。'
  return '当前缺少稳定漏斗输入。'
})
const availabilityLabel = computed(() => {
  if (availabilityStatus.value === 'ready') return 'ready'
  if (availabilityStatus.value === 'degraded') return 'degraded'
  if (availabilityStatus.value === 'not_initialized') return 'not_initialized'
  if (availabilityStatus.value === 'empty') return 'empty'
  return 'unknown'
})
const availabilityBadgeClass = computed(() => {
  if (availabilityStatus.value === 'ready') return 'border border-emerald-200 bg-emerald-100 text-emerald-800'
  if (availabilityStatus.value === 'degraded') return 'border border-amber-200 bg-amber-100 text-amber-800'
  if (availabilityStatus.value === 'not_initialized') return 'border border-rose-200 bg-rose-100 text-rose-700'
  return 'border border-[var(--line)] bg-[var(--panel-soft)] text-[var(--muted)]'
})
const availabilityMissingInputs = computed<string[]>(() => {
  const v = metricsPayload.value.missing_inputs || candidatesPayload.value.missing_inputs
  return Array.isArray(v) ? v.slice(0, 5).map((item) => String(item)) : []
})
const upstreamScoreDate = computed(() => String(metricsPayload.value?.upstream_scores?.latest_score_date || candidatesPayload.value?.upstream_scores?.latest_score_date || '').trim())
const upstreamScoreCount = computed(() => Number(metricsPayload.value?.upstream_scores?.latest_count ?? candidatesPayload.value?.upstream_scores?.latest_count ?? 0))
const funnelTotal = computed(() => Number(metricsPayload.value.total ?? candidatesPayload.value.total ?? allCandidates.value.length))

const nextStates = computed(() => {
  if (!selectedCandidate.value) return []
  const valid = STATE_TRANSITIONS[selectedCandidate.value.current_state] || []
  return STATE_LIST.filter((s) => valid.includes(s.key))
})

function stateLabel(key: string): string {
  if (!key) return '—'
  return STATE_LIST.find((s) => s.key === key)?.label ?? key
}

function triggerSourceLabel(src: string): string {
  const hit = TRIGGER_SOURCE_OPTIONS.find((o) => o.value === src)
  return hit ? hit.label : src
}

function stateBadgeClass(key: string): string {
  return STATE_LIST.find((s) => s.key === key)?.badgeClass
    ?? 'inline-flex items-center rounded-full border border-gray-200 bg-gray-100 px-2.5 py-1 text-xs font-semibold text-gray-700'
}

function toggleFilter(key: string) {
  activeFilter.value = activeFilter.value === key ? '' : key
  listPage.value = 1
}

function selectCandidate(c: FunnelCandidate) {
  selectedCandidate.value = c
  selectedId.value = c.id
  transitionForm.to_state = ''
  transitionForm.reason = ''
  transitionForm.evidence_ref = ''
  transitionForm.trigger_source = 'researcher'
  transitionError.value = ''
  transitionSuccess.value = false
}

function clearSelection() {
  selectedCandidate.value = null
  selectedId.value = ''
}

function formatDate(s: string): string {
  try {
    return new Date(s).toLocaleDateString('zh-CN')
  } catch {
    return s
  }
}

async function doTransition() {
  if (!selectedCandidate.value || !transitionForm.to_state) return
  transitionPending.value = true
  transitionError.value = ''
  transitionSuccess.value = false
  try {
    const operator =
      String(authStore.user?.username || authStore.user?.display_name || 'web_user').trim() || 'web_user'
    const stateVersion = Number(selectedCandidate.value.state_version ?? 0)
    await transitionFunnelCandidate(selectedCandidate.value.id, {
      to_state: transitionForm.to_state,
      reason: transitionForm.reason.trim() || undefined,
      trigger_source: transitionForm.trigger_source,
      evidence_ref: transitionForm.evidence_ref.trim() || undefined,
      state_version: stateVersion,
      idempotency_key: crypto.randomUUID(),
      operator,
    })
    transitionSuccess.value = true
    await queryClient.invalidateQueries({ queryKey: ['funnel-candidates'] })
    await queryClient.invalidateQueries({ queryKey: ['funnel-metrics'] })
    await queryClient.invalidateQueries({ queryKey: ['funnel-candidate'] })
    await queryClient.invalidateQueries({ queryKey: ['funnel-review-shots'] })
    clearSelection()
  } catch (e: any) {
    const base = e?.message || '未知错误'
    const extra = e?.status === 409 ? ' 若提示版本冲突，请重新点击列表中的该标的后再试。' : ''
    transitionError.value = `${base}${extra}`
  } finally {
    transitionPending.value = false
  }
}

async function submitCreateCandidate() {
  const code = createForm.ts_code.trim().toUpperCase()
  if (!code) return
  createPending.value = true
  createError.value = ''
  createSuccess.value = false
  try {
    const name = createForm.name.trim() || code
    await createFunnelCandidate({
      ts_code: code,
      name,
      source: createForm.source.trim() || 'desk_manual',
      trigger_source: 'researcher',
      reason: createForm.reason.trim() || undefined,
    })
    createSuccess.value = true
    createForm.ts_code = ''
    createForm.name = ''
    createForm.reason = ''
    await queryClient.invalidateQueries({ queryKey: ['funnel-candidates'] })
    await queryClient.invalidateQueries({ queryKey: ['funnel-metrics'] })
    await queryClient.invalidateQueries({ queryKey: ['funnel-review-shots'] })
  } catch (e: any) {
    createError.value = e?.message || '创建失败'
  } finally {
    createPending.value = false
  }
}
</script>
