<template>
  <section class="relative overflow-hidden rounded-[var(--radius-lg)] border border-[var(--line)] bg-white p-4 shadow-[var(--shadow-card)] md:p-5">
    <div class="pointer-events-none absolute inset-x-0 top-0 h-16 bg-[linear-gradient(180deg,rgba(15,97,122,0.03)_0%,rgba(15,97,122,0)_100%)]" />
    <div v-if="title || subtitle || $slots.action" class="relative mb-4 flex flex-wrap items-end justify-between gap-3 border-b border-[var(--line)]/60 pb-3">
      <div class="min-w-0">
        <div v-if="eyebrow" class="text-xs font-semibold uppercase tracking-[0.14em] text-[var(--muted)]">{{ eyebrow }}</div>
        <h2 v-if="title" class="mt-1 text-[21px] font-extrabold tracking-tight text-[var(--ink)] md:text-[23px]" style="font-family: var(--font-display)">{{ title }}</h2>
        <p v-if="subtitle" class="mt-1 text-[13px] text-[var(--muted)] md:text-sm">{{ subtitle }}</p>
      </div>
      <div v-if="$slots.action" class="ml-auto flex max-w-full flex-wrap items-center justify-end gap-2"><slot name="action" /></div>
    </div>
    <div class="relative">
      <slot />
    </div>
  </section>
</template>

<script setup lang="ts">
interface Props {
  title?: string
  subtitle?: string
  eyebrow?: string
}

defineProps<Props>()
</script>
