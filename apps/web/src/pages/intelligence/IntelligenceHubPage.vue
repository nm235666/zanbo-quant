<template>
  <AppShell title="资讯中心" subtitle="国际 / 国内 / 个股新闻与日报总结；按权限显示子 Tab。">
    <nav class="mb-4 flex flex-wrap gap-2 border-b border-[var(--line)] pb-3" aria-label="资讯子导航" data-intelligence-hub-tabs>
      <RouterLink
        v-for="tab in visibleTabs"
        :key="tab.to"
        :to="tab.to"
        class="rounded-full border px-3 py-1.5 text-sm font-semibold transition"
        :class="isTabActive(tab.to) ? 'border-emerald-600 bg-emerald-50 text-emerald-900' : 'border-[var(--line)] bg-white text-[var(--ink)] hover:border-emerald-300'"
      >
        {{ tab.label }}
      </RouterLink>
    </nav>
    <router-view />
  </AppShell>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import AppShell from '../../shared/ui/AppShell.vue'
import { hasPermissionByEffective } from '../../app/permissions'
import type { AppPermission } from '../../app/permissions'
import { useAuthStore } from '../../stores/auth'

type IntelTab = { to: string; label: string; permission: AppPermission }

const tabs: IntelTab[] = [
  { to: '/app/data/intelligence/global-news', label: '国际', permission: 'news_read' },
  { to: '/app/data/intelligence/cn-news', label: '国内', permission: 'news_read' },
  { to: '/app/data/intelligence/stock-news', label: '个股', permission: 'stock_news_read' },
  { to: '/app/data/intelligence/daily-summaries', label: '日报', permission: 'daily_summary_read' },
]

const route = useRoute()
const auth = useAuthStore()

const visibleTabs = computed(() =>
  tabs.filter((t) => hasPermissionByEffective(auth.effectivePermissions, auth.role, t.permission)),
)

function isTabActive(to: string): boolean {
  const p = route.path.replace(/\/$/, '')
  const t = to.replace(/\/$/, '')
  return p === t || p.startsWith(t + '/')
}
</script>
