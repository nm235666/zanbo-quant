<template>
  <AppShell title="研究工作台" subtitle="研究用户主入口：先完成今日判断，再进入决策、执行与跟踪。">
    <div class="space-y-4">
      <!-- Hero header with CTA -->
      <div class="flex flex-wrap items-center justify-between gap-3">
        <div class="text-sm text-[var(--muted)]">
          {{ todayDateLabel }}
        </div>
        <RouterLink
          :to="primaryCta.to"
          class="rounded-2xl bg-[var(--brand)] px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:opacity-90"
          data-testid="workbench-primary-cta"
        >
          {{ primaryCta.label }} →
        </RouterLink>
      </div>

      <div
        class="rounded-2xl border border-[var(--line)] bg-white px-5 py-4 shadow-[var(--shadow-soft)]"
        data-testid="workbench-first-action-card"
      >
        <div class="flex flex-wrap items-center justify-between gap-2">
          <div>
            <div class="text-xs font-semibold text-[var(--muted)]">今日首个动作</div>
            <div class="mt-0.5 text-sm font-bold text-[var(--ink)]">{{ firstActionCard.title }}</div>
          </div>
          <span
            class="rounded-full border px-2.5 py-0.5 text-[11px] font-semibold"
            :class="firstActionCard.statusTone"
          >
            {{ firstActionCard.statusLabel }}
          </span>
        </div>
        <div class="mt-2 text-sm leading-6 text-[var(--muted)]">{{ firstActionCard.description }}</div>
        <div class="mt-3">
          <RouterLink
            :to="firstActionCard.to"
            class="inline-flex items-center rounded-full border border-[var(--brand)] bg-white px-4 py-1.5 text-xs font-semibold text-[var(--brand)] transition hover:bg-[var(--brand)] hover:text-white"
            data-testid="workbench-first-action-link"
          >
            {{ firstActionCard.actionLabel }} →
          </RouterLink>
        </div>
      </div>

      <!-- 今日6问 -->
      <div class="rounded-2xl border border-[var(--line)] bg-[var(--panel-soft)] px-5 py-4">
        <div class="mb-3 flex items-center justify-between">
          <div class="text-sm font-bold text-[var(--ink)]">今日6问（3分钟判断清单）</div>
          <span class="rounded-full border border-[var(--line)] px-2.5 py-0.5 text-xs text-[var(--muted)]">每日必答</span>
        </div>
        <div class="grid gap-2 sm:grid-cols-2">
          <RouterLink v-for="q in dailyQuestionCards" :key="q.to" :to="q.to"
            class="group flex items-start gap-2.5 rounded-xl border border-transparent px-3 py-2.5 transition hover:border-[var(--line)] hover:bg-white">
            <span class="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full border border-[var(--line)] text-xs font-bold text-[var(--muted)]">{{ q.n }}</span>
            <span class="min-w-0">
              <span class="text-[13px] leading-5 text-[var(--ink)]">{{ q.question }}</span>
              <span class="mt-0.5 block text-xs leading-5 text-[var(--muted)] truncate">{{ q.answer }}</span>
              <span
                class="mt-1 inline-flex rounded-full border px-2 py-0.5 text-[10px] font-semibold"
                :class="q.status === 'answered' ? 'border-emerald-200 bg-emerald-100 text-emerald-700' : q.status === 'not_initialized' ? 'border-amber-200 bg-amber-100 text-amber-700' : 'border-sky-200 bg-sky-100 text-sky-700'"
              >
                {{ q.statusLabel }}
              </span>
            </span>
          </RouterLink>
        </div>
      </div>

      <!-- 宏观三周期状态 -->
      <PageSection title="宏观三周期" subtitle="基调判断：长期状态决定防守/进攻取向。">
        <div class="mb-3 grid gap-2 sm:grid-cols-3">
          <div class="rounded-xl border px-3 py-2" :class="macroFlowStatus.calc.done ? 'border-emerald-200 bg-emerald-50' : 'border-amber-200 bg-amber-50'">
            <div class="text-[11px] font-semibold text-[var(--muted)]">系统计算</div>
            <div class="mt-0.5 text-xs font-semibold" :class="macroFlowStatus.calc.done ? 'text-emerald-700' : 'text-amber-700'">{{ macroFlowStatus.calc.text }}</div>
          </div>
          <div class="rounded-xl border px-3 py-2" :class="macroFlowStatus.review.done ? 'border-emerald-200 bg-emerald-50' : 'border-amber-200 bg-amber-50'">
            <div class="text-[11px] font-semibold text-[var(--muted)]">人工复核确认</div>
            <div class="mt-0.5 text-xs font-semibold" :class="macroFlowStatus.review.done ? 'text-emerald-700' : 'text-amber-700'">{{ macroFlowStatus.review.text }}</div>
          </div>
          <div class="rounded-xl border px-3 py-2" :class="macroFlowStatus.sink.done ? 'border-emerald-200 bg-emerald-50' : 'border-amber-200 bg-amber-50'">
            <div class="text-[11px] font-semibold text-[var(--muted)]">沉淀复盘</div>
            <div class="mt-0.5 text-xs font-semibold" :class="macroFlowStatus.sink.done ? 'text-emerald-700' : 'text-amber-700'">{{ macroFlowStatus.sink.text }}</div>
          </div>
        </div>
        <div v-if="regime" class="grid gap-3 md:grid-cols-3">
          <div class="rounded-2xl border border-[var(--line)] bg-[var(--panel-soft)] px-4 py-3">
            <div class="mb-1 text-xs text-[var(--muted)]">短期 1-4周</div>
            <div class="text-base font-bold" :class="regimeStateClass(regime.short_term_state)">
              {{ regimeStateLabel(regime.short_term_state) }}
            </div>
            <div class="mt-0.5 text-xs text-[var(--muted)]">{{ ((regime.short_term_confidence ?? 0) * 100).toFixed(0) }}% 可信度</div>
          </div>
          <div class="rounded-2xl border border-[var(--line)] bg-[var(--panel-soft)] px-4 py-3">
            <div class="mb-1 text-xs text-[var(--muted)]">中期 1-6月</div>
            <div class="text-base font-bold" :class="regimeStateClass(regime.medium_term_state)">
              {{ regimeStateLabel(regime.medium_term_state) }}
            </div>
            <div class="mt-0.5 text-xs text-[var(--muted)]">{{ ((regime.medium_term_confidence ?? 0) * 100).toFixed(0) }}% 可信度</div>
          </div>
          <div class="rounded-2xl border border-[var(--line)] bg-[var(--panel-soft)] px-4 py-3">
            <div class="mb-1 text-xs text-[var(--muted)]">长期 6-24月</div>
            <div class="text-base font-bold" :class="regimeStateClass(regime.long_term_state)">
              {{ regimeStateLabel(regime.long_term_state) }}
            </div>
            <div class="mt-0.5 text-xs text-[var(--muted)]">{{ ((regime.long_term_confidence ?? 0) * 100).toFixed(0) }}% 可信度</div>
          </div>
        </div>
        <div v-if="allocation?.conflict_ruling" class="mt-3 rounded-2xl border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-800">
          裁决: {{ allocation.conflict_ruling }}
        </div>
        <div v-if="!regime" class="py-4 text-sm text-[var(--muted)]">
          {{ macroWorkbenchEmptyText }}
          <RouterLink to="/app/desk/macro-regime" class="ml-1 text-[var(--brand)] underline">前往处理</RouterLink>
        </div>
        <div class="mt-3 flex gap-2">
          <RouterLink to="/app/desk/macro-regime" class="rounded-xl border border-[var(--line)] px-3 py-1.5 text-xs font-semibold text-[var(--ink)] hover:border-[var(--brand)]">
            三周期详情 →
          </RouterLink>
          <RouterLink to="/app/desk/allocation" class="rounded-xl border border-[var(--line)] px-3 py-1.5 text-xs font-semibold text-[var(--ink)] hover:border-[var(--brand)]">
            配置动作 →
          </RouterLink>
        </div>
      </PageSection>

      <!-- 三层股池 -->
      <PageSection title="三层股池" subtitle="系统机会池 → 用户关注池（漏斗）→ 持仓池 流转状态。">
        <div class="grid gap-3 sm:grid-cols-3">
          <div v-if="signalsAccessBlocked" class="rounded-2xl border border-amber-200 bg-amber-50 px-4 py-4 text-center">
            <div class="text-xs font-semibold text-amber-700 mb-1">系统机会池</div>
            <div class="text-lg font-bold text-amber-900">当前账号暂无信号研究权限</div>
            <div class="mt-1 text-xs text-amber-800">可先用市场结论与候选漏斗完成今日判断。</div>
            <div class="mt-3 flex flex-wrap justify-center gap-2">
              <RouterLink v-for="item in signalsQuickHint" :key="`signals-pool-${item.to}`" :to="item.to" class="rounded-full border border-amber-300 bg-white px-3 py-1 text-xs font-semibold text-amber-900">
                {{ item.label }}
              </RouterLink>
            </div>
          </div>
          <RouterLink v-else to="/app/data/signals/overview" class="group rounded-2xl border border-[var(--line)] bg-[var(--panel-soft)] px-4 py-4 transition hover:border-[var(--brand)] text-center">
            <div class="text-xs font-semibold text-[var(--muted)] mb-1">系统机会池</div>
            <div class="text-lg font-bold text-[var(--ink)]">{{ signalsTotal != null ? `${signalsTotal} 信号` : '信号 + 评分' }}</div>
            <div class="mt-1 text-xs text-[var(--muted)]">全市场机会发现层</div>
          </RouterLink>
          <RouterLink to="/app/desk/funnel" class="group rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-4 transition hover:border-emerald-400 text-center">
            <div class="text-xs font-semibold text-emerald-700 mb-1">用户关注池</div>
            <div class="text-lg font-bold text-emerald-800">{{ funnelTotal }} 候选</div>
            <div class="mt-1 text-xs text-emerald-700">候选漏斗研究承接层</div>
          </RouterLink>
          <RouterLink to="/app/desk/positions" class="group rounded-2xl border border-[var(--line)] bg-[var(--panel-soft)] px-4 py-4 transition hover:border-[var(--brand)] text-center">
            <div class="text-xs font-semibold text-[var(--muted)] mb-1">持仓池</div>
            <div class="text-lg font-bold text-[var(--ink)]">{{ positionsTotal }} 持仓</div>
            <div class="mt-1 text-xs text-[var(--muted)]">实际仓位管理层</div>
          </RouterLink>
        </div>
        <div class="mt-3 grid gap-2 sm:grid-cols-3">
          <div class="rounded-xl border border-[var(--line)] bg-white px-3 py-2 text-xs text-[var(--muted)]">
            关注池总数：<span class="font-semibold text-[var(--ink)]">{{ funnelMetrics.candidateCount }}</span>
            <span class="ml-2">转化率：<span class="font-semibold text-[var(--ink)]">{{ funnelMetrics.conversionRate }}</span></span>
          </div>
          <div class="rounded-xl border border-[var(--line)] bg-white px-3 py-2 text-xs text-[var(--muted)]">
            平均决策周期：<span class="font-semibold text-[var(--ink)]">{{ funnelMetrics.avgDays }}</span>
          </div>
          <div class="rounded-xl border border-[var(--line)] bg-white px-3 py-2 text-xs text-[var(--muted)]">
            关键状态：<span class="font-semibold text-[var(--ink)]">{{ funnelStateSummary }}</span>
          </div>
        </div>
      </PageSection>

      <!-- 今日短线主题 Top N -->
      <PageSection title="今日短线主题" :subtitle="`Top ${topN}，排序：时效性 > 信号强度 > 资金确认度 > 冲突风险`">
        <template #action>
          <select v-model.number="topN" class="rounded-full border border-[var(--line)] bg-white px-3 py-1 text-xs font-semibold" :disabled="signalsAccessBlocked">
            <option :value="3">Top 3</option>
            <option :value="5">Top 5</option>
            <option :value="10">Top 10</option>
          </select>
          <RouterLink v-if="!signalsAccessBlocked" to="/app/data/signals/themes" class="rounded-2xl border border-[var(--line)] bg-white px-3 py-2 text-xs font-semibold text-[var(--ink)] transition hover:border-[var(--brand)] hover:text-[var(--brand)]">
            查看全部主题
          </RouterLink>
          <RouterLink v-else to="/app/desk/market" class="rounded-2xl border border-amber-300 bg-white px-3 py-2 text-xs font-semibold text-amber-900 transition hover:border-amber-400">
            先看市场结论
          </RouterLink>
        </template>
        <div v-if="signalsAccessBlocked" class="rounded-2xl border border-amber-200 bg-amber-50 px-4 py-5 text-sm text-amber-900">
          <div class="text-xs font-semibold text-amber-700">主题热点暂未开放</div>
          <div class="mt-1 font-semibold">{{ signalsAccessHint?.title }}</div>
          <div class="mt-2 leading-6">{{ signalsAccessHint?.message }}</div>
          <div class="mt-3 flex flex-wrap gap-2">
            <RouterLink v-for="item in signalsQuickHint" :key="`signals-theme-${item.to}`" :to="item.to" class="rounded-full border border-amber-300 bg-white px-3 py-1.5 text-xs font-semibold text-amber-900">
              {{ item.label }}
            </RouterLink>
          </div>
        </div>
        <div v-else-if="topThemes.length" class="grid gap-3 sm:grid-cols-3">
          <div v-for="(theme, idx) in topThemes" :key="theme.id || idx"
            class="rounded-2xl border border-[var(--line)] bg-[var(--panel-soft)] px-4 py-3">
            <div class="flex items-center justify-between mb-1">
              <span class="text-xs font-bold text-[var(--muted)]">Top {{ (idx as number) + 1 }}</span>
              <span :class="themeDirectionClass(theme.direction)" class="rounded-full px-2 py-0.5 text-xs font-semibold">
                {{ themeDirectionLabel(theme.direction) }}
              </span>
            </div>
            <div class="text-sm font-bold text-[var(--ink)] truncate">{{ theme.theme_name || theme.name || theme.keyword || '-' }}</div>
            <div v-if="theme.heat_level || theme.strength" class="mt-1 text-xs text-[var(--muted)]">
              热度: {{ theme.heat_level || theme.strength || '-' }}
            </div>
          </div>
        </div>
        <div v-else class="rounded-2xl border border-dashed border-[var(--line)] px-4 py-6 text-center text-sm text-[var(--muted)]">
          暂无主题数据，<RouterLink to="/app/data/signals/themes" class="text-[var(--brand)] underline">前往信号中心</RouterLink>
        </div>
        <div class="mt-3 rounded-2xl border px-4 py-3" :class="signalsAccessBlocked ? 'border-amber-200 bg-amber-50' : 'border-sky-200 bg-sky-50'">
          <div class="text-xs font-semibold" :class="signalsAccessBlocked ? 'text-amber-700' : 'text-sky-700'">今日短线核心结论</div>
          <div class="mt-1 text-sm leading-6" :class="signalsAccessBlocked ? 'text-amber-900' : 'text-sky-900'">{{ coreThemeConclusion }}</div>
          <div v-if="coreThemeConflict" class="mt-1 text-xs text-amber-700">冲突裁决：{{ coreThemeConflict }}</div>
        </div>
      </PageSection>

      <!-- 今日重点 -->
      <PageSection title="今日重点结论" subtitle="不是流程描述，而是今天可直接执行的重点。">
        <div class="grid gap-3 sm:grid-cols-3">
          <InfoCard
            title="核心主线"
            meta="今日应优先关注"
            :description="todayFocus.mainline"
          >
            <RouterLink
              to="/app/desk/market"
              class="mt-2 inline-flex items-center rounded-full border border-[var(--line)] bg-white px-3 py-1 text-xs font-semibold text-[var(--ink)] transition hover:border-[var(--brand)] hover:text-[var(--brand)]"
            >
              查看市场结论 →
            </RouterLink>
          </InfoCard>
          <InfoCard
            title="关键风险"
            meta="今天最不能忽略"
            :description="todayFocus.risk"
          >
            <RouterLink
              to="/app/data/signals/overview"
              class="mt-2 inline-flex items-center rounded-full border border-[var(--line)] bg-white px-3 py-1 text-xs font-semibold text-[var(--ink)] transition hover:border-[var(--brand)] hover:text-[var(--brand)]"
            >
              查看风险信号 →
            </RouterLink>
          </InfoCard>
          <InfoCard
            title="优先动作"
            meta="今天第一步做什么"
            :description="todayFocus.action"
          >
            <RouterLink
              :to="todayFocus.actionTo"
              class="mt-2 inline-flex items-center rounded-full border border-[var(--line)] bg-white px-3 py-1 text-xs font-semibold text-[var(--ink)] transition hover:border-[var(--brand)] hover:text-[var(--brand)]"
            >
              立即执行 →
            </RouterLink>
          </InfoCard>
        </div>
      </PageSection>

      <!-- 待处理动作 -->
      <PageSection title="待处理动作" subtitle="需要你审批或跟进的任务。">
        <template #action>
          <RouterLink
            to="/app/lab/task-inbox"
            class="rounded-2xl border border-[var(--line)] bg-white px-3 py-2 text-xs font-semibold text-[var(--ink)] transition hover:border-[var(--brand)] hover:text-[var(--brand)]"
          >
            任务收件箱
          </RouterLink>
        </template>

        <div v-if="actionsLoading" class="py-6 text-center text-sm text-[var(--muted)]">加载中...</div>
        <div v-else-if="actionsError" class="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
          加载待处理动作失败，请刷新页面重试。
        </div>
        <div v-else-if="pendingActions.length === 0" class="rounded-2xl border border-dashed border-[var(--line)] bg-gray-50 px-4 py-6 text-center">
          <div class="text-sm font-semibold text-[var(--ink)]">当前没有积压动作，给你 3 个可执行建议</div>
          <div class="mt-2 space-y-2 text-left">
            <div v-for="(item, idx) in suggestedActions" :key="item.to + idx" class="rounded-xl border border-[var(--line)] bg-white px-3 py-2">
              <div class="text-xs font-semibold text-[var(--muted)]">建议 {{ idx + 1 }}</div>
              <div class="mt-0.5 text-sm text-[var(--ink)]">{{ item.text }}</div>
              <RouterLink :to="item.to" class="mt-1 inline-flex text-xs font-semibold text-[var(--brand)] hover:underline">
                去执行 →
              </RouterLink>
            </div>
          </div>
          <div class="mt-3 flex justify-center gap-2">
            <RouterLink to="/app/desk/board" class="rounded-full border border-[var(--brand)] bg-white px-4 py-2 text-xs font-semibold text-[var(--brand)]">
              录入第一条动作
            </RouterLink>
            <RouterLink to="/app/desk/funnel" class="rounded-full border border-[var(--line)] bg-white px-4 py-2 text-xs font-semibold text-[var(--ink)]">
              从候选池挑 1 个
            </RouterLink>
          </div>
        </div>
        <div v-else class="divide-y divide-[var(--line)]">
          <div
            v-for="action in pendingActions"
            :key="action.id"
            class="flex flex-wrap items-center justify-between gap-2 py-3"
          >
            <div class="min-w-0">
              <div class="text-sm font-semibold text-[var(--ink)]">{{ action.ts_code }} <span v-if="action.stock_name" class="font-normal text-[var(--muted)]">{{ action.stock_name }}</span></div>
              <div v-if="action.note" class="mt-0.5 text-xs text-[var(--muted)] truncate max-w-xs">{{ action.note }}</div>
            </div>
            <div class="flex items-center gap-2">
              <StatusBadge :value="action.action_type" />
              <RouterLink
                :to="actionHandleLink(action)"
                class="rounded-full border border-[var(--line)] bg-white px-3 py-1 text-xs font-semibold text-[var(--ink)] transition hover:border-[var(--brand)] hover:text-[var(--brand)]"
              >
                {{ actionHandleLabel(action) }}
              </RouterLink>
            </div>
          </div>
        </div>
      </PageSection>

      <!-- 风险预警 -->
      <PageSection title="风险预警" subtitle="先处理研究侧可见风险；治理排障信息只保留为摘要，不作为主链入口。">
        <template #action>
          <RouterLink
            :to="signalsAccessBlocked ? '/app/desk/market' : '/app/data/signals/overview'"
            class="rounded-2xl border border-[var(--line)] bg-white px-3 py-2 text-xs font-semibold text-[var(--ink)] transition hover:border-[var(--brand)] hover:text-[var(--brand)]"
          >
            {{ signalsAccessBlocked ? '查看市场结论' : '查看信号图谱' }}
          </RouterLink>
        </template>
        <div v-if="signalsAccessBlocked" class="rounded-2xl border border-amber-200 bg-amber-50 px-4 py-6 text-center">
          <div class="text-sm font-semibold text-amber-800">信号图谱未向当前账号开放</div>
          <div class="mt-1 text-xs text-amber-700">当前首页已保留可执行主链：市场结论、候选漏斗、待处理动作与决策板。更深的 signals 研究可在升级后解锁。</div>
          <div class="mt-3 flex flex-wrap justify-center gap-2">
            <RouterLink v-for="item in signalsQuickHint" :key="`signals-risk-${item.to}`" :to="item.to" class="rounded-full border border-amber-300 bg-white px-4 py-2 text-xs font-semibold text-amber-900">
              {{ item.label }}
            </RouterLink>
          </div>
        </div>
        <div v-else class="rounded-2xl border border-dashed border-[var(--line)] bg-gray-50 px-4 py-6 text-center">
          <div class="text-sm font-semibold text-emerald-700">研究侧当前无异常风险信号</div>
          <div class="mt-1 text-xs text-[var(--muted)]">信号与市场结论未发现明显冲突；更深的链路治理已下沉到后台管理模式。</div>
          <div class="mt-3 flex justify-center gap-2">
            <RouterLink to="/app/data/signals/overview" class="rounded-full border border-[var(--line)] bg-white px-4 py-2 text-xs font-semibold text-[var(--ink)]">
              查看信号总览
            </RouterLink>
            <RouterLink to="/app/desk/market" class="rounded-full border border-[var(--line)] bg-white px-4 py-2 text-xs font-semibold text-[var(--ink)]">
              查看市场结论
            </RouterLink>
          </div>
        </div>
      </PageSection>

      <!-- 最近决策 -->
      <PageSection title="最近决策" subtitle="最近录入的决策动作记录。">
        <template #action>
          <RouterLink
            to="/app/desk/board"
            class="rounded-2xl border border-[var(--line)] bg-white px-3 py-2 text-xs font-semibold text-[var(--ink)] transition hover:border-[var(--brand)] hover:text-[var(--brand)]"
          >
            查看完整决策历史
          </RouterLink>
        </template>
        <div v-if="actionsLoading" class="py-4 text-center text-sm text-[var(--muted)]">加载中...</div>
        <div v-else-if="recentDecisions.length === 0" class="rounded-2xl border border-dashed border-[var(--line)] px-4 py-6 text-center text-sm text-[var(--muted)]">
          暂无决策记录
        </div>
        <div v-else class="divide-y divide-[var(--line)]">
          <div
            v-for="d in recentDecisions"
            :key="d.id"
            class="flex flex-wrap items-center justify-between gap-2 py-3"
          >
            <div class="min-w-0">
              <div class="text-sm font-semibold text-[var(--ink)]">
                {{ d.ts_code }}
                <span v-if="d.stock_name" class="font-normal text-[var(--muted)]">{{ d.stock_name }}</span>
              </div>
              <div v-if="d.note" class="mt-0.5 text-xs text-[var(--muted)] truncate max-w-xs">{{ d.note }}</div>
            </div>
            <StatusBadge :value="d.action_type" />
          </div>
        </div>
      </PageSection>

      <!-- 快速导航 -->
      <PageSection title="快速导航" subtitle="跳转到研究体系的各个核心模块。">
        <div class="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          <RouterLink
            v-for="nav in quickNavItems"
            :key="nav.to"
            :to="nav.to"
            class="group flex flex-col gap-2 rounded-[var(--radius-card)] border border-[var(--line)] bg-white p-4 shadow-[var(--shadow-soft)] transition hover:-translate-y-0.5 hover:border-[var(--brand)] hover:shadow-[var(--shadow-card)]"
          >
            <div class="text-[15px] font-bold text-[var(--ink)] group-hover:text-[var(--brand)]">{{ nav.label }}</div>
            <div class="text-[13px] text-[var(--muted)]">{{ nav.description }}</div>
          </RouterLink>
        </div>
      </PageSection>
    </div>
  </AppShell>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { RouterLink } from 'vue-router'
import { useQuery } from '@tanstack/vue-query'
import AppShell from '../../shared/ui/AppShell.vue'
import PageSection from '../../shared/ui/PageSection.vue'
import InfoCard from '../../shared/ui/InfoCard.vue'
import StatusBadge from '../../shared/ui/StatusBadge.vue'
import { hasPermissionByEffective } from '../../app/permissions'
import { fetchDecisionActions } from '../../services/api/decision'
import { fetchLatestRegime, fetchRegimeHistory, REGIME_STATE_LABELS } from '../../services/api/macro_regime'
import { fetchLatestAllocation } from '../../services/api/portfolio_allocation'
import { fetchFunnelCandidates, fetchFunnelMetrics } from '../../services/api/funnel'
import { fetchPortfolioPositions } from '../../services/api/portfolio'
import { fetchThemeHotspots, fetchInvestmentSignals } from '../../services/api/signals'
import { fetchMarketConclusion } from '../../services/api/market'
import { useAuthStore } from '../../stores/auth'

const todayDateLabel = computed(() => {
  return new Date().toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' })
})

const TOPN_KEY = 'workbench_theme_topn'
const topN = ref<3 | 5 | 10>(
  (() => { const v = localStorage.getItem(TOPN_KEY); return v === '5' ? 5 : v === '10' ? 10 : 3 })()
)
watch(topN, (v) => localStorage.setItem(TOPN_KEY, String(v)))

const authStore = useAuthStore()
const effectivePermissions = computed(() => authStore.effectivePermissions)
const role = computed(() => authStore.role)
const canUseSignalsAdvanced = computed(() =>
  hasPermissionByEffective(effectivePermissions.value, role.value, 'signals_advanced'),
)

function extractHttpStatus(error: unknown): number {
  return Number((error as any)?.status || (error as any)?.response?.status || 0)
}

const signalsAccessHint = computed(() => {
  if (canUseSignalsAdvanced.value) return null
  return {
    title: '当前账号暂无信号研究权限',
    message: '主题热点、系统机会池与信号图谱需要更高权限。你仍可先用市场结论、候选漏斗和决策板完成今日判断与首个动作。',
    alternatives: [
      { to: '/app/desk/market', label: '查看市场结论' },
      { to: '/app/desk/funnel', label: '查看候选漏斗' },
      { to: '/app/desk/board', label: '去决策板' },
    ],
  }
})

const {
  data: actionsData,
  isPending: actionsLoading,
  isError: actionsError,
} = useQuery({
  queryKey: ['decision-actions-workbench'],
  queryFn: () => fetchDecisionActions({ limit: 5 }),
})

const allActions = computed<any[]>(() => {
  const raw = actionsData.value
  if (!raw) return []
  if (Array.isArray(raw)) return raw
  if (Array.isArray(raw.actions)) return raw.actions
  return []
})

const pendingActions = computed(() =>
  allActions.value
    .filter((a: any) => {
      const type = String(a.action_type || '').toLowerCase()
      const status = String(a.payload?.execution_status || a.execution_status || '').toLowerCase()
      // Show: confirmed actions pending execution, watch-type actions
      return (type === 'confirm' && (!status || status === 'planned')) ||
             type === 'watch' ||
             status === 'planned'
    })
    .slice(0, 5)
)

const recentDecisions = computed(() => allActions.value.slice(0, 5))

function actionExecutionStatus(action: Record<string, any>): string {
  return String(action?.payload?.execution_status || action?.execution_status || '').trim().toLowerCase()
}

function actionHandleLink(action: Record<string, any>): string {
  const actionId = String(action?.id || '').trim()
  const status = actionExecutionStatus(action)
  if (actionId && status) {
    return `/app/desk/orders?decision_action_id=${encodeURIComponent(actionId)}`
  }
  return '/app/desk/board'
}

function actionHandleLabel(action: Record<string, any>): string {
  const status = actionExecutionStatus(action)
  if (status) return '查看执行'
  return '处理动作'
}

const { data: regimeData } = useQuery({
  queryKey: ['macro-regime-workbench'],
  queryFn: fetchLatestRegime,
})

const { data: regimeHistoryData } = useQuery({
  queryKey: ['macro-regime-history-workbench'],
  queryFn: () => fetchRegimeHistory({ page: 1, page_size: 50 }),
})

const { data: allocationData } = useQuery({
  queryKey: ['portfolio-allocation-workbench'],
  queryFn: fetchLatestAllocation,
})

const { data: funnelData } = useQuery({
  queryKey: ['funnel-workbench'],
  queryFn: () => fetchFunnelCandidates({ limit: 200 }),
})

const { data: funnelMetricsData } = useQuery({
  queryKey: ['funnel-metrics-workbench'],
  queryFn: fetchFunnelMetrics,
})

const { data: positionsData } = useQuery({
  queryKey: ['positions-workbench'],
  queryFn: fetchPortfolioPositions,
})

const { data: marketConclusionData } = useQuery({
  queryKey: ['market-conclusion-workbench'],
  queryFn: fetchMarketConclusion,
  refetchInterval: 300_000,
})

const {
  data: signalsData,
  error: signalsError,
} = useQuery({
  queryKey: ['signals-count-workbench'],
  queryFn: () => fetchInvestmentSignals({ limit: 1 }),
  refetchInterval: canUseSignalsAdvanced.value ? 300_000 : false,
  retry: false,
})

const signalsStatus = computed(() => extractHttpStatus(signalsError.value))
const themesStatus = computed(() => extractHttpStatus(themesError.value))
const signalsAccessBlocked = computed(() =>
  !canUseSignalsAdvanced.value && (signalsStatus.value === 401 || signalsStatus.value === 403 || themesStatus.value === 401 || themesStatus.value === 403),
)

const signalsTotal = computed(() => {
  if (signalsAccessBlocked.value) return null
  const raw = signalsData.value as any
  if (!raw) return null
  return raw.total ?? raw.count ?? (Array.isArray(raw.signals) ? raw.signals.length : null) ?? (Array.isArray(raw.items) ? raw.items.length : null)
})

const regime = computed(() => regimeData.value?.regime ?? null)
const allocation = computed(() => allocationData.value?.allocation ?? null)
const funnelTotal = computed(() => (funnelData.value as any)?.total ?? 0)
const positionsTotal = computed(() => (positionsData.value as any)?.total ?? 0)
const marketConclusion = computed(() => (marketConclusionData.value as any) || {})
const marketConclusionStatus = computed(() => String(marketConclusion.value?.status || '').trim() || 'empty')
const regimeStatus = computed(() => String((regimeData.value as any)?.status || '').trim() || 'empty')
const allocationStatus = computed(() => String((allocationData.value as any)?.status || '').trim() || 'empty')

function regimeStateLabel(state?: string): string {
  return state ? (REGIME_STATE_LABELS[state] ?? state) : '未知'
}

function regimeStateClass(state?: string): string {
  if (!state) return 'text-[var(--muted)]'
  const map: Record<string, string> = {
    expansion: 'text-emerald-700', recovery: 'text-teal-700',
    slowdown: 'text-amber-700', volatile: 'text-yellow-700',
    risk_rising: 'text-orange-700', contraction: 'text-red-700',
  }
  return map[state] ?? 'text-[var(--muted)]'
}


const dailyQuestions = [
  { n: 1, question: '今天最该关注的短线主题是什么', to: '/app/data/signals/themes' },
  { n: 2, question: '关注池里哪些标的应新开仓', to: '/app/desk/funnel' },
  { n: 3, question: '每只新开仓标的建议仓位是多少', to: '/app/desk/allocation' },
  { n: 4, question: '持仓池里哪些标的应减仓/清仓', to: '/app/desk/positions' },
  { n: 5, question: '卖出原因：止盈/止损/失效/风险切换', to: '/app/desk/board' },
  { n: 6, question: '宏观状态是否变化，组合层该怎么应对', to: '/app/desk/macro-regime' },
]

const {
  data: themesData,
  error: themesError,
} = useQuery({
  queryKey: ['theme-hotspots-workbench', topN],
  queryFn: () => fetchThemeHotspots({ page: 1, page_size: topN.value, direction: 'bullish' }),
  retry: false,
})

const topThemes = computed(() => {
  if (signalsAccessBlocked.value) return []
  const raw = themesData.value
  if (!raw) return []
  if (Array.isArray(raw)) return raw.slice(0, topN.value)
  if (Array.isArray((raw as any).items)) return (raw as any).items.slice(0, topN.value)
  return []
})

function themeDirectionLabel(direction?: string): string {
  const map: Record<string, string> = { bullish: '多', bearish: '空', neutral: '中性', mixed: '混合' }
  return direction ? (map[direction] ?? direction) : '-'
}

function themeDirectionClass(direction?: string): string {
  if (direction === 'bullish') return 'bg-emerald-100 text-emerald-700'
  if (direction === 'bearish') return 'bg-red-100 text-red-700'
  return 'bg-stone-100 text-stone-600'
}

const signalsQuickHint = computed(() => {
  if (!signalsAccessHint.value) return [] as Array<{ to: string; label: string }>
  return signalsAccessHint.value.alternatives
})

function shortText(text: string, max = 40): string {
  const normalized = String(text || '').trim()
  if (!normalized) return ''
  return normalized.length > max ? `${normalized.slice(0, max)}...` : normalized
}

const funnelCandidates = computed<any[]>(() => {
  const raw = funnelData.value as any
  if (!raw) return []
  if (Array.isArray(raw.items)) return raw.items.slice(0, 3)
  if (Array.isArray(raw.candidates)) return raw.candidates.slice(0, 3)
  if (Array.isArray(raw)) return raw.slice(0, 3)
  return []
})

const funnelMetrics = computed(() => {
  const m = (funnelMetricsData.value as any) || {}
  const candidateCount = m?.candidate_count ?? funnelTotal.value
  const conversionRate = m?.conversion_rate != null ? `${(Number(m.conversion_rate) * 100).toFixed(1)}%` : '-'
  const avgDays = m?.avg_days_to_decision != null ? `${Number(m.avg_days_to_decision).toFixed(1)} 天` : '-'
  return { candidateCount, conversionRate, avgDays }
})

const funnelStateSummary = computed(() => {
  const list = funnelCandidates.value
  if (!list.length) return '暂无候选'
  const stateCount: Record<string, number> = {}
  for (const item of list) {
    const key = String(item?.current_state || 'unknown')
    stateCount[key] = (stateCount[key] || 0) + 1
  }
  const entries = Object.entries(stateCount)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 3)
    .map(([k, v]) => `${k}:${v}`)
  return entries.join(' / ')
})

const coreThemeConclusion = computed(() => {
  const tradingTheme = String(marketConclusion.value?.trading_theme || '').trim()
  if (tradingTheme) return tradingTheme
  if (signalsAccessBlocked.value) return '当前账号暂无主题热点权限，今日主线已降级为市场结论与候选漏斗联合判断。'
  if (marketConclusionStatus.value === 'not_initialized') return '市场结论链路尚未初始化，当前无法稳定给出今日主线。'
  if (marketConclusionStatus.value === 'insufficient_evidence') return '市场证据不足，已用主题热点做降级判断。'
  if (topThemes.value.length > 0) {
    const first = topThemes.value[0] as any
    const firstName = String(first?.theme_name || first?.name || first?.keyword || '').trim()
    const heat = first?.heat_level || first?.strength
    const heatText = heat ? `（热度 ${heat}）` : ''
    const restNames = topThemes.value.slice(1, 3)
      .map((t: any) => String(t?.theme_name || t?.name || t?.keyword || '').trim())
      .filter(Boolean)
    const rest = restNames.length ? `，次选：${restNames.join(' / ')}` : ''
    return `主线：${firstName}${heatText}${rest}`
  }
  return '暂无主题数据，建议先检查主题信号与市场结论输入。'
})

const coreThemeConflict = computed(() => {
  const note = String(marketConclusion.value?.conflict_note || '').trim()
  if (note) return shortText(note, 80)
  if (allocation.value?.conflict_ruling) return shortText(String(allocation.value.conflict_ruling), 80)
  return ''
})

const todayFocus = computed(() => {
  const mainline = coreThemeConclusion.value
  const riskList = Array.isArray(marketConclusion.value?.main_risks) ? marketConclusion.value.main_risks : []
  const risk = riskList.length > 0
    ? String(riskList[0])
    : marketConclusionStatus.value === 'ready'
      ? '当前未识别到需要前置披露的高优先级风险。'
      : '风险侧证据不足，建议先去市场结论或信号总览补核。'
  if (pendingActions.value.length > 0) {
    const first = pendingActions.value[0]
    return {
      mainline,
      risk,
      action: `先处理待办动作：${first.ts_code || '-'} ${shortText(String(first.note || ''), 26)}`.trim(),
      actionTo: '/app/desk/board',
    }
  }
  if (funnelTotal.value > 0) {
    return {
      mainline,
      risk,
      action: `关注池有 ${funnelTotal.value} 个候选，先选 1 个进入决策板。`,
      actionTo: '/app/desk/funnel',
    }
  }
  return {
    mainline,
    risk,
    action: '暂无现成动作，先从主题榜挑 1 个标的建立首条决策记录。',
    actionTo: '/app/data/signals/themes',
  }
})

const macroFlowStatus = computed(() => {
  const historyItems = Array.isArray((regimeHistoryData.value as any)?.items) ? (regimeHistoryData.value as any).items : []
  const hasSystemCalcInput = !!String(marketConclusion.value?.trading_theme || '').trim() || topThemes.value.length > 0
  const hasManualReview = !!regime.value
  const sinkCount = historyItems.filter((item: any) => !!item?.outcome_rating).length
  return {
    calc: {
      done: hasSystemCalcInput,
      text: hasSystemCalcInput ? '已生成计算结论' : '待生成计算结论',
    },
    review: {
      done: hasManualReview,
      text: hasManualReview ? '已完成人工复核' : '待人工复核确认',
    },
    sink: {
      done: sinkCount > 0,
      text: sinkCount > 0 ? `已沉淀 ${sinkCount} 条复盘` : '待沉淀复盘结果',
    },
  }
})

const macroWorkbenchEmptyText = computed(() => {
  if (regimeStatus.value === 'not_initialized') return '宏观三周期尚未初始化，系统还没有首条已确认状态。'
  if (regimeStatus.value === 'insufficient_evidence') return '宏观三周期已有部分输入，但还不足以形成稳定状态。'
  return '暂无三周期状态。'
})

const primaryCta = computed(() => {
  if (pendingActions.value.length > 0) {
    return { label: '处理待办动作', to: '/app/desk/board' }
  }
  if (funnelTotal.value > 0) {
    return { label: '处理关注池候选', to: '/app/desk/funnel' }
  }
  if (topThemes.value.length > 0) {
    return { label: '从主题建立动作', to: '/app/data/signals/themes' }
  }
  return { label: '进入决策工作台', to: '/app/desk/board' }
})

const firstActionCard = computed(() => {
  if (pendingActions.value.length > 0) {
    const first = pendingActions.value[0]
    const stock = String(first?.ts_code || '').trim() || '未知标的'
    const actionType = String(first?.action_type || '').trim().toUpperCase() || 'ACTION'
    return {
      title: `${stock} 待处理动作`,
      description: `发现 ${pendingActions.value.length} 条待处理动作，优先处理 ${actionType}，并确认是否进入执行队列。`,
      to: '/app/desk/board',
      actionLabel: '去处理动作',
      statusLabel: '待处理',
      statusTone: 'border-amber-200 bg-amber-50 text-amber-700',
    }
  }
  if (funnelTotal.value > 0) {
    return {
      title: `关注池有 ${funnelTotal.value} 个候选`,
      description: '请先从候选漏斗挑选 1 个标的进入决策板，避免今天无可执行动作。',
      to: '/app/desk/funnel',
      actionLabel: '去候选漏斗',
      statusLabel: '待筛选',
      statusTone: 'border-sky-200 bg-sky-50 text-sky-700',
    }
  }
  if (topThemes.value.length > 0) {
    const firstTheme = String(topThemes.value[0]?.theme_name || topThemes.value[0]?.name || topThemes.value[0]?.keyword || '').trim() || '主题'
    return {
      title: `围绕「${firstTheme}」建立首条动作`,
      description: '当前暂无待处理动作和候选积压，建议从短线主题直接生成一条可追踪决策。',
      to: '/app/data/signals/themes',
      actionLabel: '去主题中心',
      statusLabel: '可执行',
      statusTone: 'border-emerald-200 bg-emerald-50 text-emerald-700',
    }
  }
  return {
    title: '先补齐今日主线证据',
    description: '主题、候选与动作均为空，建议先完成市场结论与信号核对，再生成第一条决策动作。',
    to: '/app/desk/market',
    actionLabel: '去市场结论',
    statusLabel: '待初始化',
    statusTone: 'border-stone-200 bg-stone-50 text-stone-700',
  }
})

const suggestedActions = computed(() => {
  const list: Array<{ text: string; to: string }> = []
  if (topThemes.value.length > 0) {
    const first = topThemes.value[0]
    list.push({
      text: `围绕主题「${String(first?.theme_name || first?.name || first?.keyword || '-') }」建立第一条决策动作。`,
      to: '/app/desk/board',
    })
  }
  if (funnelTotal.value > 0) {
    list.push({
      text: `从关注池 ${funnelTotal.value} 个候选中，先挑 1 个进入待决策状态。`,
      to: '/app/desk/funnel',
    })
  }
  if (allocation.value) {
    list.push({
      text: `按当前配置口径（单票上限 ${allocation.value.max_single_position_pct ?? '-'}%）补齐仓位建议。`,
      to: '/app/desk/allocation',
    })
  } else {
    list.push({
      text: '先完成长线配置录入，避免短线动作没有账户级仓位口径。',
      to: '/app/desk/allocation',
    })
  }
  return list.slice(0, 3)
})

const trimActions = computed<any[]>(() => allActions.value.filter((item: any) =>
  ['confirm', 'reject', 'defer', 'watch', 'review'].includes(String(item?.action_type || '').toLowerCase()),
))

const dailyQuestionCards = computed(() => {
  const topThemeNames = topThemes.value
    .slice(0, 3)
    .map((theme: any) => String(theme?.theme_name || theme?.name || theme?.keyword || '').trim())
    .filter(Boolean)

  const q1Status = signalsAccessBlocked.value
    ? 'answered'
    : topThemeNames.length > 0
      ? 'answered'
      : marketConclusionStatus.value === 'not_initialized'
        ? 'not_initialized'
        : 'insufficient_evidence'
  const q1Answer = signalsAccessBlocked.value
    ? '信号主题未开放，当前已降级为市场结论 + 候选漏斗判断'
    : topThemeNames.length
      ? `Top${topThemeNames.length}：${topThemeNames.join(' / ')}`
      : q1Status === 'not_initialized'
        ? '主题主线链路尚未初始化'
        : '主题证据不足，建议先查看信号主题'

  const funnelNames = funnelCandidates.value
    .map((item: any) => String(item?.name || item?.ts_code || '').trim())
    .filter(Boolean)
  const q2Status = funnelTotal.value > 0 ? 'answered' : 'insufficient_evidence'
  const q2Answer = funnelTotal.value > 0
    ? `关注池 ${funnelTotal.value} 个，优先：${funnelNames.length ? funnelNames.join(' / ') : '请打开候选漏斗查看'}`
    : '关注池当前没有可开仓候选，建议先从市场结论或信号进入'

  const q3Status = allocation.value
    ? 'answered'
    : allocationStatus.value === 'not_initialized'
      ? 'not_initialized'
      : 'insufficient_evidence'
  const q3Answer = allocation.value
    ? `单票上限 ${allocation.value.max_single_position_pct ?? '-'}% · 现金目标 ${allocation.value.cash_ratio_pct ?? '-'}%`
    : q3Status === 'not_initialized'
      ? '仓位口径尚未初始化'
      : '仓位建议证据不足，需先确认长线配置'

  const reduceActions = trimActions.value.filter((item: any) =>
    ['reject', 'defer', 'review'].includes(String(item?.action_type || '').toLowerCase()),
  )
  const q4Status = positionsTotal.value <= 0
    ? 'not_initialized'
    : reduceActions.length > 0 ? 'answered' : 'insufficient_evidence'
  const q4Answer = positionsTotal.value <= 0
    ? '持仓池为空，当前没有减仓/清仓任务'
    : reduceActions.length > 0
      ? `当前持仓 ${positionsTotal.value} 个，最近 ${reduceActions.length} 条调整动作待确认`
      : `当前持仓 ${positionsTotal.value} 个，但尚未形成明确减仓/清仓结论`

  const sellReasonAction = reduceActions[0]
  const q5Status = sellReasonAction ? 'answered' : 'insufficient_evidence'
  const q5Answer = sellReasonAction
    ? `${String(sellReasonAction?.action_type || '').toUpperCase()}：${shortText(String(sellReasonAction?.note || '')) || '已记录动作，建议补充理由'}`
    : '暂无卖出/减仓理由，建议补齐决策动作与复盘说明'

  const q6Status = regime.value
    ? 'answered'
    : regimeStatus.value === 'not_initialized'
      ? 'not_initialized'
      : 'insufficient_evidence'
  const q6Answer = regime.value
    ? `短${regimeStateLabel(regime.value.short_term_state)} / 中${regimeStateLabel(regime.value.medium_term_state)} / 长${regimeStateLabel(regime.value.long_term_state)}${allocation.value?.conflict_ruling ? ' · 已给冲突裁决' : ''}`
    : q6Status === 'not_initialized'
      ? '宏观三周期尚未初始化'
      : '宏观状态证据不足，尚未形成稳定结论'

  return [
    { ...dailyQuestions[0], answer: q1Answer, answered: q1Status === 'answered', status: q1Status, statusLabel: q1Status === 'answered' ? '已回答' : q1Status === 'not_initialized' ? '未初始化' : '证据不足' },
    { ...dailyQuestions[1], answer: q2Answer, answered: q2Status === 'answered', status: q2Status, statusLabel: q2Status === 'answered' ? '已回答' : '证据不足' },
    { ...dailyQuestions[2], answer: q3Answer, answered: q3Status === 'answered', status: q3Status, statusLabel: q3Status === 'answered' ? '已回答' : q3Status === 'not_initialized' ? '未初始化' : '证据不足' },
    { ...dailyQuestions[3], answer: q4Answer, answered: q4Status === 'answered', status: q4Status, statusLabel: q4Status === 'answered' ? '已回答' : q4Status === 'not_initialized' ? '未建持仓' : '证据不足' },
    { ...dailyQuestions[4], answer: q5Answer, answered: q5Status === 'answered', status: q5Status, statusLabel: q5Status === 'answered' ? '已回答' : '待补理由' },
    { ...dailyQuestions[5], answer: q6Answer, answered: q6Status === 'answered', status: q6Status, statusLabel: q6Status === 'answered' ? '已回答' : q6Status === 'not_initialized' ? '未初始化' : '证据不足' },
  ]
})

const quickNavItems = [
  {
    to: '/app/desk/market',
    label: '市场结论',
    description: '今日交易主线、主要风险与候选方向',
  },
  {
    to: '/app/desk/funnel',
    label: '候选漏斗',
    description: '候选股票全生命周期状态管理',
  },
  {
    to: '/app/desk/board',
    label: '决策工作台',
    description: '短名单执行、动作审批与验证结果',
  },
  {
    to: '/app/lab/multi-role',
    label: '多角色分析',
    description: 'AI六角色协同深度公司分析',
  },
]
</script>
