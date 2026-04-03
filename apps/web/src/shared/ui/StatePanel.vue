<template>
  <div class="rounded-[20px] border px-4 py-4 text-sm shadow-[var(--shadow-soft)]" :class="toneClass">
    <div class="font-semibold text-[var(--ink)]">{{ title }}</div>
    <div class="mt-1 leading-6 text-[var(--muted)]">{{ description }}</div>
    <div v-if="$slots.action" class="mt-3 flex flex-wrap gap-2">
      <slot name="action" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(defineProps<{
  title: string
  description: string
  tone?: 'default' | 'warning' | 'danger'
}>(), {
  tone: 'default',
})

const toneClass = computed(() => {
  if (props.tone === 'danger') return 'border-[rgba(178,77,84,0.18)] bg-[rgba(178,77,84,0.06)]'
  if (props.tone === 'warning') return 'border-[rgba(214,134,72,0.22)] bg-[rgba(214,134,72,0.09)]'
  return 'border-[var(--line)] bg-[rgba(255,255,255,0.72)]'
})
</script>
