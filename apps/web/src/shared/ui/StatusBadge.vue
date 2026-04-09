<template>
  <span :class="badgeClass">{{ label }}</span>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { statusTone } from '../utils/format'

const props = defineProps<{ value?: string; label?: string }>()

const tone = computed(() => statusTone(props.value || ''))
const label = computed(() => props.label || props.value || '-')
const badgeClass = computed(() => {
  const base = 'inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-semibold'
  return {
    success: `${base} border-emerald-200 bg-emerald-100 text-emerald-800`,
    warning: `${base} border-amber-200 bg-amber-100 text-amber-800`,
    danger: `${base} border-rose-200 bg-rose-100 text-rose-800`,
    info: `${base} border-sky-200 bg-sky-100 text-sky-800`,
    muted: `${base} border-[var(--line)] bg-[var(--panel-soft)] text-[var(--muted)]`,
  }[tone.value]
})
</script>
