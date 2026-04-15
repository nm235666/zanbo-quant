<template>
  <div class="grid gap-3" :class="columnsClass">
    <div
      v-for="item in items"
      :key="`${item.label}-${item.value}`"
      class="rounded-[var(--radius-md)] border border-[var(--line)] bg-white p-4 shadow-[var(--shadow-soft)] transition hover:shadow-[var(--shadow-card)]"
    >
      <div class="text-xs font-semibold uppercase tracking-[0.14em] text-[var(--muted)]">{{ item.label }}</div>
      <div class="mt-2 text-lg font-bold text-[var(--ink)]">{{ item.value || '-' }}</div>
      <div v-if="item.hint" class="mt-2 text-sm leading-6 text-[var(--muted)] line-clamp-2">{{ item.hint }}</div>
    </div>
    <div
      v-if="!items.length"
      class="rounded-[var(--radius-md)] border border-dashed border-[var(--line)] bg-gray-50/50 px-4 py-8 text-center text-sm text-[var(--muted)]"
    >
      {{ emptyText }}
    </div>
  </div>
</template>

<script setup lang="ts">
export interface MetricGridItem {
  label: string
  value?: string | number | null
  hint?: string
}

interface Props {
  items: MetricGridItem[]
  emptyText?: string
  columnsClass?: string
}

withDefaults(defineProps<Props>(), {
  emptyText: '暂无数据',
  columnsClass: 'xl:grid-cols-4 md:grid-cols-2',
})
</script>
