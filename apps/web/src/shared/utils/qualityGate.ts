/**
 * QualityGate — 决策动作硬门禁
 *
 * 统一阻断等级：blocker（必须修复）/ warning（需二次确认）/ info（提示）
 * blocker 漏拦截率要求为 0。
 * 每次 gate 结果可通过 evaluateGate() 返回结构审计。
 */

export type GateSeverity = 'blocker' | 'warning' | 'info'

export interface GateRule {
  rule_id: string
  source_bug?: string   // BUG->CHECK 溯源编号
  scope: string[]       // 适用的 action_type 列表，[] 表示所有
  severity: GateSeverity
  message: string       // 用户可读阻断原因
  fix_hint: string      // 修复建议（可行动）
  owner: string
}

export interface GateContext {
  action_type: string
  ts_code: string
  note: string
  evidence_sources: string  // 用户填写的证据字段（raw string）
  position_pct_range?: string
  position_recommendation?: string
  decision_context_from: string  // 跨页来源模块
  snapshot_date: string
}

export interface GateViolation {
  rule: GateRule
  field?: string  // 触发的字段名（可选）
}

export interface GateResult {
  passed: boolean         // 无 blocker = 可提交
  blockers: GateViolation[]
  warnings: GateViolation[]
  infos: GateViolation[]
  gate_version: string    // 规则版本，用于审计记录
  evaluated_at: string    // ISO 时间戳
  action_type: string
}

const GATE_VERSION = '1.0.0'

// TS 代码格式验证
const TS_CODE_RE = /^[0-9]{6}\.(SZ|SH|BJ)$/i

function scopeMatches(rule: GateRule, actionType: string): boolean {
  if (!rule.scope || rule.scope.length === 0) return true
  return rule.scope.includes(actionType.toLowerCase())
}

/**
 * 内置规则（BUG->CHECK 转化规则库）
 * rule_id 命名：B=blocker W=warning I=info + 3位序号
 */
const BUILTIN_RULES: Array<GateRule & { check: (ctx: GateContext) => boolean }> = [
  {
    rule_id: 'B001',
    source_bug: 'P0-decision-no-tscode',
    scope: ['confirm', 'reject', 'defer'],
    severity: 'blocker',
    message: '确认/拒绝/暂缓动作必须指定有效股票代码（6位数字 + .SZ/.SH/.BJ）',
    fix_hint: '在"股票代码"输入框填入完整代码，如 000001.SZ',
    owner: 'decision-board',
    check: (ctx) => !TS_CODE_RE.test(ctx.ts_code.trim()),
  },
  {
    rule_id: 'B002',
    source_bug: 'P0-decision-no-note',
    scope: ['confirm', 'reject'],
    severity: 'blocker',
    message: '确认/拒绝动作必须填写决策备注，空备注无法支撑审计追溯',
    fix_hint: '在"备注"字段填写至少一句话说明理由，如"强势突破+量价配合"',
    owner: 'decision-board',
    check: (ctx) => ctx.note.trim().length < 3,
  },
  {
    rule_id: 'B003',
    source_bug: 'P0-decision-no-position-range',
    scope: ['confirm'],
    severity: 'blocker',
    message: '确认动作必须填写账户仓位区间或仓位建议，否则无法形成可执行动作',
    fix_hint: '填写“建议仓位（如 5-8%）”或“建议仓位（可选）”字段后再提交',
    owner: 'decision-board',
    check: (ctx) =>
      String(ctx.position_pct_range || '').trim().length === 0 &&
      String(ctx.position_recommendation || '').trim().length === 0,
  },
  {
    rule_id: 'W001',
    source_bug: 'P1-decision-short-note',
    scope: ['confirm', 'reject'],
    severity: 'warning',
    message: '备注过短（< 10 字），建议补充更多决策依据以便复盘',
    fix_hint: '扩充备注内容，建议包含：来源信号、风险点、执行时间窗口',
    owner: 'decision-board',
    check: (ctx) => ctx.note.trim().length > 0 && ctx.note.trim().length < 10,
  },
  {
    rule_id: 'W002',
    source_bug: 'P1-decision-no-evidence',
    scope: ['confirm', 'reject'],
    severity: 'warning',
    message: '未填写证据来源，结论可追溯性较低',
    fix_hint: '在"证据来源"字段填写分析依据，如"多角色分析 run_id=xxx"或"新闻信号"',
    owner: 'decision-board',
    check: (ctx) => ctx.evidence_sources.trim().length === 0,
  },
  {
    rule_id: 'W003',
    source_bug: 'P1-decision-dark-origin',
    scope: ['confirm', 'reject'],
    severity: 'warning',
    message: '动作来自手工直接输入（无关联上游模块），来源可追溯性为零',
    fix_hint: '尽量从信号图谱、新闻分析或多角色分析跳转到决策板，以自动带入上下文来源',
    owner: 'decision-board',
    check: (ctx) => ctx.decision_context_from.trim().length === 0,
  },
  {
    rule_id: 'I001',
    source_bug: undefined,
    scope: ['confirm', 'reject', 'defer', 'watch'],
    severity: 'info',
    message: '当前无快照日期，决策日期将以提交时间为准',
    fix_hint: '如需绑定特定快照，先点击"生成快照"再提交动作',
    owner: 'decision-board',
    check: (ctx) => ctx.snapshot_date.trim().length === 0,
  },
  {
    rule_id: 'I002',
    source_bug: undefined,
    scope: ['confirm', 'reject'],
    severity: 'info',
    message: '当前动作来源为手动输入而非系统跨页跳转，建议核查上下文是否完整',
    fix_hint: '从分析结果页点击"→决策板"按钮进入，可自动携带来源上下文',
    owner: 'decision-board',
    check: (ctx) =>
      ctx.decision_context_from.trim().length === 0 ||
      ctx.decision_context_from === 'decision_board',
  },
]

/**
 * 评估 gate，返回结构化结果。
 * 调用方应在 passed=false 时阻止提交；warnings 需二次确认。
 */
export function evaluateGate(ctx: GateContext): GateResult {
  const blockers: GateViolation[] = []
  const warnings: GateViolation[] = []
  const infos: GateViolation[] = []

  for (const rule of BUILTIN_RULES) {
    if (!scopeMatches(rule, ctx.action_type)) continue
    if (!rule.check(ctx)) continue  // rule does not fire
    const violation: GateViolation = { rule }
    if (rule.severity === 'blocker') blockers.push(violation)
    else if (rule.severity === 'warning') warnings.push(violation)
    else infos.push(violation)
  }

  return {
    passed: blockers.length === 0,
    blockers,
    warnings,
    infos,
    gate_version: GATE_VERSION,
    evaluated_at: new Date().toISOString(),
    action_type: ctx.action_type,
  }
}

/**
 * 将 GateResult 序列化为可审计的摘要字符串（用于存入 action payload）
 */
export function serializeGateAudit(result: GateResult): string {
  const parts: string[] = [
    `gate_version=${result.gate_version}`,
    `passed=${result.passed}`,
    `blockers=${result.blockers.map((v) => v.rule.rule_id).join(',')||'none'}`,
    `warnings=${result.warnings.map((v) => v.rule.rule_id).join(',')||'none'}`,
    `evaluated_at=${result.evaluated_at}`,
  ]
  return parts.join(' | ')
}
