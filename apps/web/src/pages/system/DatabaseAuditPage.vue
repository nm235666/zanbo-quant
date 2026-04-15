<template>
  <AppShell title="数据库审计" subtitle="缺口、重复、未评分、Markdown 报告和健康指标放到统一工作面板。">
    <div class="space-y-4">
      <div class="page-hero-grid">
        <div class="page-hero-card">
          <div class="page-insight-label">Data Audit</div>
          <div class="page-hero-title">先处理影响主链展示的问题，再回头做细节清理。</div>
          <div class="page-hero-copy">
            数据审计页的价值在于快速排序风险。优先看缺口、重复、未评分和发布日期缺失，这些问题最容易直接影响前端页面的完整性和可信度。
          </div>
        </div>
        <div class="page-insight-list">
          <div class="page-insight-item">
            <div class="page-insight-label">当前风险级别</div>
            <div class="page-insight-value">{{ riskItems.length ? `${riskItems.length} 项待处理` : '总体稳定' }}</div>
            <div class="page-insight-note">建议优先清零缺口和重复，再处理长期尾项。</div>
          </div>
          <div class="page-insight-item">
            <div class="page-insight-label">最影响前端展示</div>
            <div class="page-insight-value">{{ riskItems[0]?.label || '暂无突出问题' }}</div>
            <div class="page-insight-note">前端最怕“空字段 + 弱数据 + 时间不齐”，这些都会直接拉低页面质量。</div>
          </div>
        </div>
      </div>

      <StatePanel
        v-if="riskItems.length"
        tone="warning"
        title="发现待处理数据问题"
        :description="`当前共 ${riskItems.length} 项健康风险，建议优先处理缺口和重复问题。`"
      />

      <PageSection title="数据库健康快照" subtitle="结构化健康数据适合快速巡检。">
        <div class="kpi-grid">
          <StatCard title="日线最新" :value="formatDate(health?.daily_latest)" :hint="`分钟线 ${formatDate(health?.minline_latest)} · 评分 ${formatDate(health?.scores_latest)}`" />
          <StatCard title="事件/治理缺口" :value="`${health?.miss_events ?? '-'} / ${health?.miss_governance ?? '-'}`" :hint="`资金流 ${health?.miss_flow ?? '-'} · 分钟线 ${health?.miss_minline ?? '-'}`" />
          <StatCard title="新闻未评分" :value="health?.news_unscored ?? 0" :hint="`个股新闻 ${health?.stock_news_unscored ?? 0}`" />
          <StatCard title="重复组" :value="`${health?.news_dup_link ?? 0} / ${health?.stock_news_dup_link ?? 0}`" hint="国际/个股新闻重复组" />
          <StatCard title="宏观发布日期缺失" :value="health?.macro_publish_empty ?? 0" hint="应继续补齐" />
          <StatCard title="群聊去重异常" :value="health?.chatlog_dup_key ?? 0" hint="理论上应尽量接近 0" />
        </div>
      </PageSection>

      <PageSection title="问题清单" subtitle="按问题类型聚合，便于快速制定修复顺序。">
        <div class="table-lead">
          <div class="table-lead-copy">问题清单不是平均处理的。优先级建议按“影响主展示链路程度”排序，而不是单纯看数字大小。</div>
        </div>
        <div class="grid gap-3 md:grid-cols-2">
          <div
            v-for="item in riskItems"
            :key="item.label"
            class="rounded-[18px] border border-[var(--line)] bg-white/82 px-4 py-3 text-sm"
          >
            <div class="font-semibold text-[var(--ink)]">{{ item.label }}</div>
            <div class="mt-1 text-[var(--muted)]">当前值 {{ item.value }}</div>
          </div>
        </div>
      </PageSection>

      <PageSection title="审计报告" subtitle="Markdown 报告直接在新前端里解析，不再裸文本展示。">
        <div class="max-h-[720px] overflow-auto pr-1">
          <MarkdownBlock :content="audit?.markdown || '暂无审计报告'" />
        </div>
      </PageSection>
    </div>
  </AppShell>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import AppShell from '../../shared/ui/AppShell.vue'
import PageSection from '../../shared/ui/PageSection.vue'
import StatCard from '../../shared/ui/StatCard.vue'
import StatePanel from '../../shared/ui/StatePanel.vue'
import MarkdownBlock from '../../shared/markdown/MarkdownBlock.vue'
import { fetchDatabaseAudit, fetchDbHealth } from '../../services/api/dashboard'
import { formatDate } from '../../shared/utils/format'

const { data: audit } = useQuery({ queryKey: ['database-audit'], queryFn: fetchDatabaseAudit })
const { data: health } = useQuery({ queryKey: ['db-health'], queryFn: fetchDbHealth })

const riskItems = computed(() => {
  const rows = [
    { label: '事件缺口', value: Number(health.value?.miss_events || 0) },
    { label: '治理缺口', value: Number(health.value?.miss_governance || 0) },
    { label: '资金流缺口', value: Number(health.value?.miss_flow || 0) },
    { label: '分钟线缺口', value: Number(health.value?.miss_minline || 0) },
    { label: '国际新闻未评分', value: Number(health.value?.news_unscored || 0) },
    { label: '个股新闻未评分', value: Number(health.value?.stock_news_unscored || 0) },
    { label: '国际新闻重复组', value: Number(health.value?.news_dup_link || 0) },
    { label: '个股新闻重复组', value: Number(health.value?.stock_news_dup_link || 0) },
    { label: '宏观发布日期缺失', value: Number(health.value?.macro_publish_empty || 0) },
    { label: '群聊去重异常', value: Number(health.value?.chatlog_dup_key || 0) },
  ]
  return rows.filter((item) => item.value > 0)
})
</script>
