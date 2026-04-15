<template>
  <!-- 桌面端：表格视图 -->
  <div class="hidden overflow-auto rounded-[var(--radius-lg)] border border-[var(--line)] bg-white shadow-[var(--shadow-soft)] md:block">
    <table class="min-w-full border-collapse text-[13px]" :aria-label="ariaLabel || caption || undefined">
      <caption v-if="caption" class="sr-only">{{ caption }}</caption>
      <thead class="sticky top-0 z-10">
        <tr class="text-left text-[11px] uppercase tracking-[0.14em] text-[var(--muted)]" style="background: var(--table-head-bg);">
          <th v-for="column in columns" :key="column.key" scope="col" class="px-4 py-3 font-semibold">{{ column.label }}</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="(row, index) in rows"
          :key="rowKey ? row[rowKey] ?? index : index"
          class="border-t border-[var(--line)]/55 align-top transition hover:bg-[var(--table-row-hover)]"
          :style="{ background: index % 2 ? 'rgba(255,255,255,0.96)' : 'rgba(248,252,253,0.72)' }"
        >
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

  <!-- 移动端：卡片视图 -->
  <div class="space-y-3 md:hidden">
    <div 
      v-for="(row, index) in rows" 
      :key="rowKey ? row[rowKey] ?? index : index"
      class="rounded-xl border border-[var(--line)] bg-white p-4 shadow-sm transition hover:shadow-md"
    >
      <div 
        v-for="(column, colIndex) in columns" 
        :key="column.key" 
        class="flex justify-between py-2"
        :class="{ 'border-b border-gray-100': colIndex < columns.length - 1 }"
      >
        <span class="text-xs text-[var(--muted)]">{{ column.label }}</span>
        <span class="text-sm font-medium text-[var(--ink)] text-right max-w-[60%]">
          <slot :name="`cell-${column.key}`" :row="row">
            {{ row[column.key] ?? '-' }}
          </slot>
        </span>
      </div>
    </div>
    <div v-if="!rows.length" class="rounded-xl border border-dashed border-[var(--line)] bg-gray-50/50 px-4 py-8 text-center text-sm text-[var(--muted)]">
      {{ emptyText }}
    </div>
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
