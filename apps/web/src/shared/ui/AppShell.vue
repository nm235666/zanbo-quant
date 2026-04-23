<template>
  <component :is="shellComponent" v-if="shellComponent && !embed" :title="title" :subtitle="subtitle">
    <slot />
  </component>
  <div v-else class="page-main-stack">
    <slot />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import AdminShell from './AdminShell.vue'
import UserShell from './UserShell.vue'

const props = defineProps<{
  title: string
  subtitle?: string
  /** 仅渲染主内容槽，不套 UserShell/AdminShell（用于父级已提供壳层时，如资讯 Hub 子路由） */
  embed?: boolean
}>()

const route = useRoute()

const resolvedSurface = computed<'app' | 'admin' | 'shared'>(() => {
  const metaSurface = String((route.meta as { surface?: string } | undefined)?.surface || '').trim()
  if (metaSurface === 'app' || metaSurface === 'admin' || metaSurface === 'shared') return metaSurface
  if (route.path.startsWith('/admin/')) return 'admin'
  if (route.path.startsWith('/app/')) return 'app'
  return 'shared'
})

const embed = computed(() => Boolean(props.embed))

const shellComponent = computed(() => {
  if (embed.value) return null
  if (resolvedSurface.value === 'app') return UserShell
  if (resolvedSurface.value === 'admin') return AdminShell
  return null
})

const title = computed(() => props.title)
const subtitle = computed(() => props.subtitle)
</script>
