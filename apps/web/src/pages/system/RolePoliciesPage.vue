<template>
  <AppShell title="角色权限策略" subtitle="配置 admin / pro / limited 的可访问权限与每日配额，保存后立即生效。">
    <div class="space-y-4">
      <PageSection title="全局操作" subtitle="可刷新当前策略，或一键恢复默认基线。">
        <div class="flex flex-wrap gap-2">
          <button class="rounded-2xl border border-[var(--line)] bg-[var(--panel-soft)] px-4 py-3 text-sm font-semibold" @click="refreshPolicies">
            刷新策略
          </button>
          <button class="rounded-2xl bg-stone-800 px-4 py-3 text-sm font-semibold text-white" @click="resetDefaults">
            恢复默认策略
          </button>
        </div>
        <div v-if="message" class="mt-3 text-sm text-[var(--muted)]">{{ message }}</div>
      </PageSection>

      <PageSection title="角色配置" subtitle="每个角色独立配置权限集合与日配额（留空表示不限）。">
        <div class="mb-4 rounded-[18px] border border-[rgba(15,97,122,0.16)] bg-[rgba(15,97,122,0.06)] px-4 py-3 text-sm text-[var(--muted)]">
          admin 独占管理员权限与全量访问能力；pro、limited 只允许配置研究与阅读类权限，保存时会自动剔除越权项。
        </div>
        <div v-if="policyWarnings.length" class="mb-4 rounded-[18px] border border-[rgba(214,134,72,0.28)] bg-[rgba(214,134,72,0.08)] px-4 py-3 text-sm text-[var(--muted)]">
          <div class="font-semibold text-[var(--ink)]">发现越权权限</div>
          <div class="mt-1">当前策略含越权权限，已在编辑视图中隔离展示，不会随保存再次写回。</div>
          <div class="mt-2 space-y-1">
            <div v-for="warning in policyWarnings" :key="warning">{{ warning }}</div>
          </div>
        </div>
        <div class="space-y-4">
          <div
            v-for="role in roleOrder"
            :key="role"
            class="rounded-[20px] border border-[var(--line)] bg-white p-4 shadow-[var(--shadow-soft)]"
          >
            <div class="flex items-center justify-between gap-2">
              <div class="text-lg font-bold">{{ role }}</div>
              <button class="rounded-2xl bg-[var(--brand)] px-3 py-2 text-sm font-semibold text-white" @click="saveRole(role)">
                保存 {{ role }}
              </button>
            </div>
            <div class="mt-3 grid gap-3 md:grid-cols-2">
              <label class="text-sm text-[var(--muted)]">
                走势日配额（trend）
                <input
                  v-model.trim="drafts[role].trend_daily_limit_text"
                  class="mt-1 w-full rounded-2xl border border-[var(--line)] bg-white px-3 py-2"
                  placeholder="留空表示不限"
                />
              </label>
              <label class="text-sm text-[var(--muted)]">
                多角色日配额（multi-role）
                <input
                  v-model.trim="drafts[role].multi_role_daily_limit_text"
                  class="mt-1 w-full rounded-2xl border border-[var(--line)] bg-white px-3 py-2"
                  placeholder="留空表示不限"
                />
              </label>
            </div>
            <div class="mt-3 text-sm font-semibold">权限项</div>
            <div class="mt-2 grid gap-2 md:grid-cols-2 xl:grid-cols-3">
              <label v-for="perm in permissionsForRole(role)" :key="`${role}-${perm}`" class="flex items-center gap-2 rounded-xl border border-[var(--line)] px-3 py-2 text-sm">
                <input
                  type="checkbox"
                  :checked="drafts[role].permissions.has(perm)"
                  :disabled="role === 'admin' && perm !== '*'"
                  @change="togglePermission(role, perm)"
                />
                <span>{{ perm }}</span>
              </label>
            </div>
            <div v-if="invalidPermissionsByRole[role]?.length" class="mt-3 rounded-[16px] border border-[rgba(214,134,72,0.28)] bg-[rgba(214,134,72,0.06)] px-3 py-3 text-sm text-[var(--muted)]">
              已隔离的越权权限：{{ invalidPermissionsByRole[role].join('、') }}
            </div>
          </div>
        </div>
      </PageSection>
    </div>
  </AppShell>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import AppShell from '../../shared/ui/AppShell.vue'
import PageSection from '../../shared/ui/PageSection.vue'
import { fetchAuthRolePolicies, resetAuthRolePoliciesToDefault, updateAuthRolePolicy, type AuthRolePolicy } from '../../services/api/system'

const message = ref('')
const roleOrder = ['admin', 'pro', 'limited']
const allPermissions = [
  '*',
  'news_read',
  'stock_news_read',
  'daily_summary_read',
  'trend_analyze',
  'multi_role_analyze',
  'research_advanced',
  'signals_advanced',
  'chatrooms_advanced',
  'stocks_advanced',
  'macro_advanced',
  'admin_users',
  'admin_system',
]
const rolePermissionAllowlist: Record<string, string[]> = {
  admin: ['*'],
  pro: [
    'news_read',
    'stock_news_read',
    'daily_summary_read',
    'trend_analyze',
    'multi_role_analyze',
    'research_advanced',
    'signals_advanced',
    'chatrooms_advanced',
    'stocks_advanced',
    'macro_advanced',
  ],
  limited: [
    'news_read',
    'stock_news_read',
    'daily_summary_read',
    'trend_analyze',
    'multi_role_analyze',
    'research_advanced',
    'signals_advanced',
    'chatrooms_advanced',
    'stocks_advanced',
    'macro_advanced',
  ],
}

type RoleDraft = {
  permissions: Set<string>
  trend_daily_limit_text: string
  multi_role_daily_limit_text: string
}

const drafts = reactive<Record<string, RoleDraft>>({
  admin: { permissions: new Set(['*']), trend_daily_limit_text: '', multi_role_daily_limit_text: '' },
  pro: { permissions: new Set(), trend_daily_limit_text: '', multi_role_daily_limit_text: '' },
  limited: { permissions: new Set(), trend_daily_limit_text: '', multi_role_daily_limit_text: '' },
})
const invalidPermissionsByRole = reactive<Record<string, string[]>>({
  admin: [],
  pro: [],
  limited: [],
})

const policyWarnings = computed(() =>
  roleOrder.flatMap((role) =>
    (invalidPermissionsByRole[role] || []).map((perm) => `${role}：${perm}`),
  ),
)

function permissionsForRole(role: string) {
  return rolePermissionAllowlist[role] || allPermissions
}

function applyRolePolicy(item: AuthRolePolicy) {
  const role = String(item.role || '').toLowerCase()
  if (!role || !drafts[role]) return
  const allowlist = new Set(permissionsForRole(role))
  const incoming = Array.isArray(item.permissions) ? item.permissions.map((x) => String(x || '').trim()).filter(Boolean) : []
  const invalid = role === 'admin' ? [] : incoming.filter((perm) => !allowlist.has(perm))
  invalidPermissionsByRole[role] = invalid
  drafts[role].permissions = new Set(role === 'admin' ? ['*'] : incoming.filter((perm) => allowlist.has(perm)))
  drafts[role].trend_daily_limit_text = item.trend_daily_limit == null ? '' : String(item.trend_daily_limit)
  drafts[role].multi_role_daily_limit_text = item.multi_role_daily_limit == null ? '' : String(item.multi_role_daily_limit)
}

function parseLimit(text: string): number | null {
  const raw = String(text || '').trim()
  if (!raw) return null
  const num = Number(raw)
  if (!Number.isFinite(num) || num < 0) throw new Error(`配额必须是非负整数，当前输入=${raw}`)
  return Math.floor(num)
}

function serializePermissions(role: string): string[] {
  if (role === 'admin') return ['*']
  const allowlist = new Set(permissionsForRole(role))
  const values = Array.from(drafts[role].permissions)
  return values.filter((x) => x !== '*' && allowlist.has(x)).sort()
}

function togglePermission(role: string, perm: string) {
  if (!drafts[role]) return
  if (role === 'admin') {
    drafts[role].permissions = new Set(['*'])
    return
  }
  const allowlist = new Set(permissionsForRole(role))
  if (perm === '*' || !allowlist.has(perm)) return
  const next = new Set(drafts[role].permissions)
  if (next.has(perm)) next.delete(perm)
  else next.add(perm)
  drafts[role].permissions = next
}

const { refetch } = useQuery({
  queryKey: ['auth-role-policies'],
  queryFn: async () => {
    const data = await fetchAuthRolePolicies()
    for (const role of roleOrder) {
      if (!drafts[role]) {
        drafts[role] = { permissions: new Set(), trend_daily_limit_text: '', multi_role_daily_limit_text: '' }
      }
    }
    for (const item of data.roles || []) applyRolePolicy(item)
    message.value = `策略来源：${data.effective_source || 'db'}`
    return data
  },
})

async function saveRole(role: string) {
  try {
    await updateAuthRolePolicy({
      role,
      permissions: serializePermissions(role),
      trend_daily_limit: parseLimit(drafts[role].trend_daily_limit_text),
      multi_role_daily_limit: parseLimit(drafts[role].multi_role_daily_limit_text),
    })
    await refetch()
    message.value = `已保存 ${role} 策略`
  } catch (error: any) {
    message.value = `保存失败：${error?.message || String(error)}`
  }
}

async function refreshPolicies() {
  await refetch()
}

async function resetDefaults() {
  try {
    const data = await resetAuthRolePoliciesToDefault()
    for (const item of data.roles || []) applyRolePolicy(item)
    message.value = '已恢复默认策略'
  } catch (error: any) {
    message.value = `恢复失败：${error?.message || String(error)}`
  }
}
</script>
