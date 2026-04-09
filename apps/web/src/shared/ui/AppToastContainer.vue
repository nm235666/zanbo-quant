<template>
  <Teleport to="body">
    <div class="pointer-events-none fixed right-4 top-4 z-[1700] flex w-[min(92vw,360px)] flex-col gap-2">
      <TransitionGroup name="toast">
        <div
          v-for="item in ui.toasts"
          :key="item.id"
          class="pointer-events-auto rounded-[16px] border px-3 py-2 shadow-[var(--shadow-float)] backdrop-blur"
          :class="toneClass(item.tone)"
        >
          <div class="flex items-start justify-between gap-3">
            <div class="text-sm font-semibold">{{ item.message }}</div>
            <button class="rounded-full px-1 text-xs text-current/75 hover:text-current" @click="ui.removeToast(item.id)">关闭</button>
          </div>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { useUiStore, type ToastTone } from '../../stores/ui'

const ui = useUiStore()

function toneClass(tone: ToastTone) {
  if (tone === 'success') return 'border-emerald-200 bg-emerald-50 text-emerald-800'
  if (tone === 'error') return 'border-red-200 bg-red-50 text-red-800'
  return 'border-sky-200 bg-sky-50 text-sky-800'
}
</script>
