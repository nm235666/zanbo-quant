<template>
  <div class="relative overflow-hidden rounded-[var(--radius-md)] border border-[var(--line)] bg-white p-4 shadow-[var(--shadow-soft)] transition hover:shadow-[var(--shadow-card)]">
    <div class="text-xs font-semibold uppercase tracking-[0.14em] text-[var(--muted)]">{{ title }}</div>
    <div :class="['mt-1.5 text-[32px] font-extrabold tracking-tight', valueClass]">{{ value }}</div>
    <div v-if="hint" class="mt-2 text-[13px] leading-5 text-[var(--muted)] line-clamp-2">{{ hint }}</div>
    <div v-if="props.updatedAt" class="mt-1.5 flex items-center gap-1 text-[11px]">
      <span :class="freshnessClass" class="inline-block size-1.5 rounded-full" />
      <span class="text-[var(--muted)]">{{ freshnessLabel }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  title: string
  value: string | number
  hint?: string
  tone?: 'success' | 'warning' | 'danger' | 'info' | 'muted'
  updatedAt?: string
  freshnessThresholdHours?: number
}

const props = defineProps<Props>()

const valueClass = computed(() => {
  if (!props.tone) return 'text-[var(--ink)]'
  return {
    success: 'text-emerald-600',
    warning: 'text-amber-600',
    danger: 'text-rose-600',
    info: 'text-sky-600',
    muted: 'text-[var(--muted)]',
  }[props.tone]
})

const freshnessStatus = computed(() => {
  if (!props.updatedAt) return 'unknown'
  const diffHours = (Date.now() - new Date(props.updatedAt).getTime()) / 3600000
  const threshold = props.freshnessThresholdHours ?? 24
  if (diffHours < threshold * 0.5) return 'fresh'
  if (diffHours < threshold) return 'normal'
  if (diffHours < threshold * 2) return 'stale'
  return 'expired'
})

const freshnessClass = computed(() => ({
  'bg-emerald-500': freshnessStatus.value === 'fresh',
  'bg-sky-400': freshnessStatus.value === 'normal',
  'bg-amber-400': freshnessStatus.value === 'stale',
  'bg-rose-500': freshnessStatus.value === 'expired',
  'bg-gray-300': freshnessStatus.value === 'unknown',
}))

const freshnessLabel = computed(() => {
  if (!props.updatedAt) return ''
  const diffHours = (Date.now() - new Date(props.updatedAt).getTime()) / 3600000
  if (diffHours < 1) return `${Math.round(diffHours * 60)} 分钟前`
  if (diffHours < 24) return `${Math.round(diffHours)} 小时前`
  return `${Math.round(diffHours / 24)} 天前`
})
</script>
