<template>
  <div class="overflow-auto rounded-[var(--radius-lg)] border border-[var(--line)] bg-[linear-gradient(180deg,rgba(255,255,255,0.98)_0%,rgba(247,251,252,0.94)_100%)] shadow-[var(--shadow-soft)]">
    <table class="min-w-full border-collapse text-sm" :aria-label="ariaLabel || caption || undefined">
      <caption v-if="caption" class="sr-only">{{ caption }}</caption>
      <thead>
        <tr class="bg-[linear-gradient(180deg,rgba(241,247,250,0.96)_0%,rgba(233,241,246,0.96)_100%)] text-left text-xs uppercase tracking-[0.16em] text-[var(--muted)]">
          <th v-for="column in columns" :key="column.key" scope="col" class="px-4 py-3 font-semibold">{{ column.label }}</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(row, index) in rows" :key="rowKey ? row[rowKey] ?? index : index" class="border-t border-[var(--line)]/55 align-top transition hover:bg-[rgba(15,97,122,0.04)]">
          <td v-for="column in columns" :key="column.key" class="px-4 py-3 text-[var(--ink)]">
            <slot :name="`cell-${column.key}`" :row="row">
              {{ row[column.key] ?? '-' }}
            </slot>
          </td>
        </tr>
        <tr v-if="!rows.length">
          <td :colspan="columns.length" class="px-4 py-8 text-center text-sm text-[var(--muted)]">{{ emptyText }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
export interface TableColumn {
  key: string
  label: string
}

defineProps<{
  columns: TableColumn[]
  rows: Array<Record<string, any>>
  rowKey?: string
  emptyText?: string
  caption?: string
  ariaLabel?: string
}>()
</script>
