import { test, type APIRequestContext } from '@playwright/test'

export function getSmokeLimitedCredentials() {
  return {
    username: process.env.SMOKE_LIMITED_USERNAME?.trim() || 'test112233',
    password: process.env.SMOKE_LIMITED_PASSWORD?.trim() || 'test123',
  }
}

/** Skip current test when SMOKE_LIMITED_* 账号在服务端不是 limited（例如被写用例临时改过角色）。 */
export async function skipUnlessSmokeLimitedRoleIsLimited(request: APIRequestContext) {
  const { username, password } = getSmokeLimitedCredentials()
  const res = await request.post('/api/auth/login', {
    data: { username, password },
  })
  if (!res.ok()) {
    test.skip(true, `SMOKE_LIMITED 登录 API 失败: HTTP ${res.status()}`)
  }
  const json = (await res.json()) as { user?: { role?: string } } | null
  const role = String(json?.user?.role || '').toLowerCase()
  test.skip(
    role !== 'limited',
    `SMOKE_LIMITED 账号(${username})当前 role=${role}，本用例需要 limited；请将账号改回 limited 或更换 SMOKE_LIMITED_USERNAME`,
  )
}
