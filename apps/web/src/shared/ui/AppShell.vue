<template>
  <component :is="shellComponent" v-if="shellComponent" :title="title" :subtitle="subtitle">
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
}>()

const route = useRoute()

const resolvedSurface = computed<'app' | 'admin' | 'shared'>(() => {
  const metaSurface = String((route.meta as { surface?: string } | undefined)?.surface || '').trim()
  if (metaSurface === 'app' || metaSurface === 'admin' || metaSurface === 'shared') return metaSurface
  if (route.path.startsWith('/admin/')) return 'admin'
  if (route.path.startsWith('/app/')) return 'app'
  return 'shared'
})

const shellComponent = computed(() => {
  if (resolvedSurface.value === 'app') return UserShell
  if (resolvedSurface.value === 'admin') return AdminShell
  return null
})

const title = computed(() => props.title)
const subtitle = computed(() => props.subtitle)
</script>
