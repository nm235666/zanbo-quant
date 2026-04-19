<template>
  <div v-if="error">
    <!-- Default: red-tinted box -->
    <div
      v-if="!compact"
      class="bg-red-50 border border-red-200 rounded-lg px-4 py-3 space-y-1"
    >
      <p class="text-sm text-red-700 font-medium">{{ error }}</p>
      <p v-if="code" class="text-xs text-red-400 font-mono">{{ code }}</p>
      <p v-if="actionLabel" class="text-xs text-red-600">建议：{{ actionLabel }}</p>
      <button
        v-if="retryFn"
        class="mt-1 text-xs text-red-600 underline hover:text-red-800"
        @click="retryFn"
      >
        重试
      </button>
    </div>

    <!-- Compact: inline text only -->
    <span v-else class="space-x-2">
      <span class="text-sm text-red-700 font-medium">{{ error }}</span>
      <span v-if="code" class="text-xs text-red-400 font-mono">{{ code }}</span>
      <span v-if="actionLabel" class="text-xs text-red-600">建议：{{ actionLabel }}</span>
      <button
        v-if="retryFn"
        class="text-xs text-red-600 underline hover:text-red-800"
        @click="retryFn"
      >
        重试
      </button>
    </span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  error?: string | null
  code?: string | null
  action?: string | null
  retryFn?: (() => void) | null
  compact?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  error: null,
  code: null,
  action: null,
  retryFn: null,
  compact: false,
})

const ACTION_LABELS: Record<string, string> = {
  redirect_to_login: '请重新登录',
  contact_admin_or_upgrade: '请联系管理员或升级权限',
  check_request_fields: '请检查填写内容',
  verify_id_and_retry: '请刷新后重试',
  reload_and_retry: '请刷新页面后重试',
  reload_resource_and_retry: '请刷新状态后重试',
  no_action_needed: '无需操作（重复提交已忽略）',
  check_current_state_and_allowed_transitions: '请查看当前状态允许的操作',
  use_higher_priority_trigger_source: '请使用更高权限的触发源',
  retry_or_use_deep_workflow: '请重试或启动深度分析工作流',
  run_deep_workflow_for_full_analysis: '请启动深度分析以获得完整结论',
  retry_later_or_check_provider_config: '请稍后重试或检查 AI 服务配置',
  contact_admin_with_request_id: '请联系管理员并提供请求信息',
  check_request: '请检查请求参数',
}

const actionLabel = computed(() =>
  props.action ? (ACTION_LABELS[props.action] ?? null) : null,
)
</script>
