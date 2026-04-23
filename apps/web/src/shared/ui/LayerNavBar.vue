<template>
  <div class="layer-nav-bar" data-shell-layer-bar>
    <nav class="layer-nav-bar__tabs" aria-label="四层架构导航">
      <RouterLink
        v-for="layer in tabs"
        :key="layer.id"
        :to="layer.targetPath"
        class="layer-nav-bar__tab"
        :class="layer.active ? 'layer-nav-bar__tab--active' : ''"
        :data-layer-id="layer.id"
        :data-layer-active="layer.active ? 'true' : 'false'"
      >
        <span class="layer-nav-bar__tab-index">L{{ layer.index }}</span>
        <span class="layer-nav-bar__tab-label">{{ layer.shortLabel }}</span>
      </RouterLink>
    </nav>
    <div class="layer-nav-bar__crumbs" data-shell-layer-crumbs>
      <span class="layer-nav-bar__crumb-layer">{{ activeLayerLabel }}</span>
      <template v-if="activeGroupTitle">
        <span class="layer-nav-bar__crumb-divider">›</span>
        <span class="layer-nav-bar__crumb-group">{{ activeGroupTitle }}</span>
      </template>
      <template v-if="activeItemLabel">
        <span class="layer-nav-bar__crumb-divider">›</span>
        <span class="layer-nav-bar__crumb-page">{{ activeItemLabel }}</span>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { LAYER_DEFS, resolveLayerByPath } from '../../app/layers'
import { hasPermissionByEffective } from '../../app/permissions'
import { useAuthStore } from '../../stores/auth'
import { NAV_GROUPS, type NavGroupConfig, type NavItemConfig } from '../../app/navigation'

const props = defineProps<{
  groups?: NavGroupConfig[]
}>()

const route = useRoute()
const auth = useAuthStore()

const allGroups = computed<NavGroupConfig[]>(() => (props.groups && props.groups.length ? props.groups : NAV_GROUPS))

function pickItemForLayer(layerPrefix: string): NavItemConfig | null {
  for (const group of allGroups.value) {
    for (const item of group.items) {
      if (item.to === layerPrefix || item.to.startsWith(layerPrefix + '/')) return item
    }
  }
  return null
}

const tabs = computed(() => {
  const activeLayer = resolveLayerByPath(route.path)
  return LAYER_DEFS.map((def, index) => {
    const allowed = hasPermissionByEffective(auth.effectivePermissions, auth.role, def.permission)
    const navItem = pickItemForLayer(def.prefix)
    const targetPath = navItem?.to || def.defaultPath
    return {
      id: def.id,
      index: index + 1,
      shortLabel: def.shortLabel,
      label: def.label,
      targetPath: allowed ? targetPath : '/upgrade',
      active: !!activeLayer && activeLayer.id === def.id,
      allowed,
    }
  })
})

const activeLayerDef = computed(() => resolveLayerByPath(route.path))

const activeLayerLabel = computed(() => activeLayerDef.value?.label || '其它')

const activeGroupAndItem = computed<{ group: NavGroupConfig | null; item: NavItemConfig | null }>(() => {
  const path = route.path
  for (const group of allGroups.value) {
    for (const item of group.items) {
      if (item.to === path) return { group, item }
    }
  }
  for (const group of allGroups.value) {
    for (const item of group.items) {
      if (item.to !== '/' && path.startsWith(item.to + '/')) return { group, item }
    }
  }
  return { group: null, item: null }
})

const activeGroupTitle = computed(() => activeGroupAndItem.value.group?.title || '')
const activeItemLabel = computed(() => activeGroupAndItem.value.item?.label || '')
</script>

<style scoped>
.layer-nav-bar {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  padding: 0.65rem 0.85rem;
  border-radius: var(--radius-md);
  border: 1px solid var(--line);
  background: rgba(255, 255, 255, 0.92);
  box-shadow: var(--shadow-soft);
}
.layer-nav-bar__tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}
.layer-nav-bar__tab {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.4rem 0.85rem;
  border-radius: 999px;
  border: 1px solid var(--line);
  background: rgba(255, 255, 255, 0.7);
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--ink);
  text-decoration: none;
  transition: all 160ms ease;
}
.layer-nav-bar__tab:hover {
  border-color: var(--brand);
  color: var(--brand);
}
.layer-nav-bar__tab--active {
  background: var(--brand);
  color: #fff;
  border-color: var(--brand);
  box-shadow: 0 6px 16px rgba(13, 148, 136, 0.18);
}
.layer-nav-bar__tab-index {
  font-family: var(--font-mono, ui-monospace, monospace);
  font-size: 0.72rem;
  letter-spacing: 0.06em;
  opacity: 0.78;
}
.layer-nav-bar__tab-label {
  font-size: 0.84rem;
}
.layer-nav-bar__crumbs {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.75rem;
  color: var(--muted);
}
.layer-nav-bar__crumb-layer {
  font-weight: 600;
  color: var(--brand);
}
.layer-nav-bar__crumb-divider {
  opacity: 0.55;
}
.layer-nav-bar__crumb-page {
  font-weight: 600;
  color: var(--ink);
}
</style>
