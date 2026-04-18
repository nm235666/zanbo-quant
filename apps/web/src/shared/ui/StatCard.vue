<template>
  <div class="relative overflow-hidden rounded-[var(--radius-md)] border border-[var(--line)] bg-white p-4 shadow-[var(--shadow-soft)] transition hover:shadow-[var(--shadow-card)]">
    <div class="text-xs font-semibold uppercase tracking-[0.14em] text-[var(--muted)]">{{ title }}</div>
    <div :class="['mt-1.5 text-[32px] font-extrabold tracking-tight', valueClass]">{{ value }}</div>
    <div v-if="hint" class="mt-2 text-[13px] leading-5 text-[var(--muted)] line-clamp-2">{{ hint }}</div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  title: string
  value: string | number
  hint?: string
  tone?: 'success' | 'warning' | 'danger' | 'info' | 'muted'
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
</script>
