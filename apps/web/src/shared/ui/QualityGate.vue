<template>
  <div v-if="hasIssues" class="rounded-[20px] border px-4 py-3 text-sm" :class="containerClass">
    <div class="flex flex-wrap items-center justify-between gap-2">
      <div class="font-semibold" :class="titleClass">
        {{ titleText }}
      </div>
      <div class="flex flex-wrap gap-1.5 text-xs">
        <span v-if="result.blockers.length" class="rounded-full bg-red-700 px-2.5 py-0.5 font-bold text-white">
          {{ result.blockers.length }} 项阻断
        </span>
        <span v-if="result.warnings.length" class="rounded-full bg-amber-600 px-2.5 py-0.5 font-semibold text-white">
          {{ result.warnings.length }} 项警告
        </span>
        <span v-if="result.infos.length" class="rounded-full border border-sky-400 px-2.5 py-0.5 font-semibold text-sky-700">
          {{ result.infos.length }} 项提示
        </span>
      </div>
    </div>

    <ul class="mt-2 space-y-2">
      <li
        v-for="violation in allViolations"
        :key="violation.rule.rule_id"
        class="rounded-[14px] px-3 py-2"
        :class="violationClass(violation.rule.severity)"
      >
        <div class="flex items-start gap-2">
          <span class="mt-0.5 shrink-0 rounded-full px-1.5 py-0.5 text-[10px] font-bold uppercase tracking-wide" :class="badgeClass(violation.rule.severity)">
            {{ violation.rule.severity === 'blocker' ? '阻断' : violation.rule.severity === 'warning' ? '警告' : '提示' }}
          </span>
          <div class="min-w-0 flex-1">
            <div class="font-semibold" :class="messageClass(violation.rule.severity)">
              {{ violation.rule.message }}
            </div>
            <div class="mt-0.5 text-xs text-[var(--muted)]">
              修复建议：{{ violation.rule.fix_hint }}
            </div>
            <div v-if="violation.rule.source_bug" class="mt-0.5 text-[10px] text-[var(--muted)] opacity-60">
              规则 {{ violation.rule.rule_id }} · 溯源 {{ violation.rule.source_bug }}
            </div>
          </div>
        </div>
      </li>
    </ul>

    <div v-if="result.blockers.length" class="mt-3 text-xs font-semibold text-red-700">
      存在阻断项，提交已禁止。请修复上述问题后重试。
    </div>
    <div v-else-if="result.warnings.length && !warningAcknowledged" class="mt-3 flex items-center gap-2 text-xs">
      <span class="text-amber-700">存在警告项。确认继续提交？</span>
      <button
        class="rounded-full border border-amber-400 bg-amber-50 px-3 py-1 font-semibold text-amber-800 transition hover:bg-amber-100"
        type="button"
        @click="emit('acknowledge-warnings')"
      >
        确认并继续
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { GateResult, GateSeverity, GateViolation } from '../utils/qualityGate'

interface Props {
  result: GateResult
  warningAcknowledged?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  warningAcknowledged: false,
})

const emit = defineEmits<{
  (e: 'acknowledge-warnings'): void
}>()

const hasIssues = computed(
  () =>
    props.result.blockers.length > 0 ||
    props.result.warnings.length > 0 ||
    props.result.infos.length > 0,
)

const allViolations = computed<GateViolation[]>(() => [
  ...props.result.blockers,
  ...props.result.warnings,
  ...props.result.infos,
])

const containerClass = computed(() => {
  if (props.result.blockers.length) return 'border-red-300 bg-red-50'
  if (props.result.warnings.length) return 'border-amber-300 bg-amber-50'
  return 'border-sky-200 bg-sky-50'
})

const titleClass = computed(() => {
  if (props.result.blockers.length) return 'text-red-800'
  if (props.result.warnings.length) return 'text-amber-800'
  return 'text-sky-700'
})

const titleText = computed(() => {
  if (props.result.blockers.length) return '提交被阻断 — 请修复以下问题'
  if (props.result.warnings.length) return '存在潜在风险 — 请确认后再提交'
  return '质量提示'
})

function violationClass(severity: GateSeverity) {
  if (severity === 'blocker') return 'bg-red-100/70 border border-red-200'
  if (severity === 'warning') return 'bg-amber-100/70 border border-amber-200'
  return 'bg-sky-100/70 border border-sky-200'
}

function badgeClass(severity: GateSeverity) {
  if (severity === 'blocker') return 'bg-red-700 text-white'
  if (severity === 'warning') return 'bg-amber-600 text-white'
  return 'bg-sky-600 text-white'
}

function messageClass(severity: GateSeverity) {
  if (severity === 'blocker') return 'text-red-800'
  if (severity === 'warning') return 'text-amber-800'
  return 'text-sky-800'
}
</script>
