<template>
  <div class="relative overflow-hidden rounded-[var(--radius-md)] border border-[var(--line)] bg-white p-4 shadow-[var(--shadow-soft)] transition hover:shadow-[var(--shadow-card)]">
    <div class="text-xs font-semibold uppercase tracking-[0.14em] text-[var(--muted)]">{{ title }}</div>
    <div class="mt-1.5 text-[32px] font-extrabold tracking-tight text-[var(--ink)]">{{ value }}</div>
    <div v-if="hint" class="mt-2 text-[13px] leading-5 text-[var(--muted)] line-clamp-2">{{ hint }}</div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  title: string
  value: string | number
  hint?: string
}

defineProps<Props>()
</script>
