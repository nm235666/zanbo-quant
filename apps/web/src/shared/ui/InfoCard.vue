<template>
  <component
    :is="isInteractive ? 'button' : 'div'"
    v-bind="boundAttrs"
    class="relative w-full overflow-hidden rounded-[var(--radius-card)] border border-[var(--line)] bg-white/96 p-4 text-left shadow-[var(--shadow-soft)] transition-all duration-200 hover:shadow-[var(--shadow-card)] active:scale-[0.99]"
    :class="{ 'cursor-pointer': isInteractive, 'hover:-translate-y-0.5': isInteractive }"
  >
    <div class="flex items-start justify-between gap-3">
      <div class="min-w-0 flex-1">
        <div class="text-[15px] font-bold text-[var(--ink)] truncate">
          <slot name="title">{{ title }}</slot>
        </div>
        <div v-if="meta" class="mt-1 text-[12px] text-[var(--muted)] truncate">{{ meta }}</div>
      </div>
      <slot name="badge" />
    </div>
    <div v-if="description" class="mt-2.5 text-[13px] leading-6 text-[var(--muted)] line-clamp-3">{{ description }}</div>
    <div v-if="$slots.default" class="mt-3"><slot /></div>
  </component>
</template>

<script setup lang="ts">
import { computed, useAttrs } from 'vue'

defineOptions({
  inheritAttrs: false,
})

interface Props {
  title: string
  meta?: string
  description?: string
}

defineProps<Props>()

const attrs = useAttrs()
const isInteractive = computed(() => Boolean(attrs.onClick))

const boundAttrs = computed(() => {
  if (!isInteractive.value) return attrs
  return {
    ...attrs,
    type: 'button',
  }
})
</script>
