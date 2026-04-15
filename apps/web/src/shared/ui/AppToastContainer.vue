<template>
  <Teleport to="body">
    <div class="pointer-events-none fixed top-4 left-1/2 -translate-x-1/2 z-[1700] flex w-[min(92vw,400px)] flex-col gap-2">
      <TransitionGroup name="toast">
        <div
          v-for="item in ui.toasts"
          :key="item.id"
          class="pointer-events-auto rounded-[12px] border px-4 py-3 shadow-lg backdrop-blur-sm"
          :class="toneClass(item.tone)"
          role="status"
          aria-live="polite"
        >
          <div class="flex items-start justify-between gap-3">
            <div class="flex items-center gap-2">
              <span v-if="item.tone === 'success'" class="text-emerald-600">
                <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>
              </span>
              <span v-else-if="item.tone === 'error'" class="text-red-600">
                <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
              </span>
              <span v-else class="text-sky-600">
                <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
              </span>
              <div class="text-sm font-semibold">{{ item.message }}</div>
            </div>
            <button class="rounded-full p-1 text-current/60 hover:text-current hover:bg-black/5 transition" @click="ui.removeToast(item.id)" aria-label="关闭通知">
              <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
            </button>
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
  if (tone === 'success') return 'border-emerald-200 bg-emerald-50/95 text-emerald-800'
  if (tone === 'error') return 'border-red-200 bg-red-50/95 text-red-800'
  return 'border-sky-200 bg-sky-50/95 text-sky-800'
}
</script>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.toast-enter-from {
  opacity: 0;
  transform: translateY(-20px) scale(0.95);
}
.toast-leave-to {
  opacity: 0;
  transform: translateY(-10px) scale(0.95);
}
</style>
