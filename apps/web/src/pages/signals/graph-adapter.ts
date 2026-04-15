import type { JsonLine, JsonNode } from 'relation-graph-vue3/types/types/relation-graph-models/types'

export type GraphNode = Record<string, any>
export type GraphEdge = Record<string, any>

export type GraphRenderNode = JsonNode & {
  data: {
    raw: GraphNode
    role: 'center' | 'primary' | 'secondary'
    score: number
    meta: string
  }
}

export type GraphRenderEdge = JsonLine & {
  data: {
    raw: GraphEdge
    role: 'primary' | 'secondary'
  }
}

export type GraphLayoutConfig = {
  canvasWidth: number
  canvasHeight: number
  centerX: number
  primaryX: number
  secondaryX: number
  maxPrimary: number
  maxSecondary: number
  nodeWidthCenter: number
  nodeWidthPrimary: number
  nodeWidthSecondary: number
  nodeHeight: number
}

export type GraphRenderPayload = {
  jsonData: { rootId: string; nodes: GraphRenderNode[]; lines: GraphRenderEdge[] }
  hiddenNodeCount: number
  secondaryCandidateCount: number
  primaryCandidateCount: number
}

const COLOR_NEUTRAL = '#a7b6c2'
const COLOR_PRIMARY_LINE = '#3f7189'
const COLOR_SECONDARY_LINE = '#8aa6b9'
const COLOR_ACTIVE_LINE = '#0f617a'

function toNumber(value: unknown, fallback = 0) {
  const n = Number(value)
  return Number.isFinite(n) ? n : fallback
}

function clamp(value: number, min: number, max: number) {
  return Math.min(max, Math.max(min, value))
}

function labelOf(node: GraphNode) {
  return String(node?.label || node?.name || node?.id || '-')
}

function scoreOf(node: GraphNode) {
  return toNumber(node?.score, 0)
}

function sortByScore(nodes: GraphNode[]) {
  return [...nodes].sort((a, b) => {
    const d = scoreOf(b) - scoreOf(a)
    if (d !== 0) return d
    return labelOf(a).localeCompare(labelOf(b), 'zh-Hans-CN')
  })
}

function makeLayoutConfig(centerType: 'theme' | 'industry', limit: number, viewportWidth: number): GraphLayoutConfig {
  const wide = viewportWidth >= 1480
  const compact = viewportWidth < 1200
  const maxPrimary = clamp(Math.round(limit), 6, 14)
  const maxSecondary = clamp(Math.round(limit), 8, 18)
  if (centerType === 'industry') {
    return {
      canvasWidth: wide ? 1280 : 1160,
      canvasHeight: 640,
      centerX: compact ? 560 : 620,
      primaryX: compact ? 250 : 280,
      secondaryX: compact ? 870 : 960,
      maxPrimary,
      maxSecondary,
      nodeWidthCenter: 220,
      nodeWidthPrimary: 190,
      nodeWidthSecondary: 176,
      nodeHeight: 72,
    }
  }
  return {
    canvasWidth: wide ? 1360 : 1220,
    canvasHeight: 640,
    centerX: compact ? 190 : 220,
    primaryX: compact ? 540 : 620,
    secondaryX: compact ? 930 : 1020,
    maxPrimary,
    maxSecondary,
    nodeWidthCenter: 220,
    nodeWidthPrimary: 194,
    nodeWidthSecondary: 184,
    nodeHeight: 72,
  }
}

function stackY(index: number, count: number, centerY: number) {
  if (count <= 1) return centerY
  const gap = clamp(520 / Math.max(1, count - 1), 64, 112)
  const start = centerY - ((count - 1) * gap) / 2
  return clamp(start + index * gap, 58, centerY * 2 - 58)
}

function relationMatches(edge: GraphEdge, relationKey: string) {
  if (!relationKey) return true
  return String(edge?.relation_key || '') === relationKey
}

function lineRole(edge: GraphEdge, centerId: string): 'primary' | 'secondary' {
  const from = String(edge?.source || '')
  const to = String(edge?.target || '')
  if (from === centerId || to === centerId) return 'primary'
  return 'secondary'
}

function lineStyle(edge: GraphEdge, role: 'primary' | 'secondary', selectedNodeId: string) {
  const connected = selectedNodeId && (String(edge?.source || '') === selectedNodeId || String(edge?.target || '') === selectedNodeId)
  const major = role === 'primary'
  const color = connected ? COLOR_ACTIVE_LINE : (major ? COLOR_PRIMARY_LINE : COLOR_SECONDARY_LINE)
  const opacity = connected ? 0.86 : (major ? 0.68 : 0.28)
  const lineWidth = connected ? (major ? 2.8 : 2.2) : (major ? 2.0 : 1.2)
  return { color, opacity, lineWidth }
}

function nodeMeta(node: GraphNode, centerId: string) {
  const id = String(node?.id || '')
  if (id === centerId) {
    const stockCount = toNumber(node?.metrics?.stock_count ?? node?.metrics?.company_count, 0)
    return stockCount > 0 ? `企业 ${stockCount} 家` : '中心节点'
  }
  const score = scoreOf(node)
  return Number.isFinite(score) ? `评分 ${score.toFixed(score >= 100 ? 0 : 1)}` : '评分 -'
}

export function buildGraphRenderPayload(params: {
  nodes: GraphNode[]
  edges: GraphEdge[]
  centerType: 'theme' | 'industry'
  centerId: string
  relationKey: string
  selectedNodeId: string
  limit: number
  viewportWidth: number
  hideSecondary?: boolean
}): GraphRenderPayload {
  const {
    nodes,
    edges,
    centerType,
    centerId,
    relationKey,
    selectedNodeId,
    limit,
    viewportWidth,
    hideSecondary = false,
  } = params

  const layout = makeLayoutConfig(centerType, limit, viewportWidth)
  const center = nodes.find((node) => String(node?.id || '') === centerId) || nodes[0]
  if (!center) {
    return {
      jsonData: { rootId: 'empty', nodes: [], lines: [] },
      hiddenNodeCount: 0,
      secondaryCandidateCount: 0,
      primaryCandidateCount: 0,
    }
  }

  const centerNodeId = String(center.id || '')
  const centerY = Math.round(layout.canvasHeight / 2)
  const filteredEdges = edges.filter((edge) => relationMatches(edge, relationKey))
  const adjacentToCenter = new Set<string>()
  const adjacentToPrimary = new Set<string>()
  const primarySeed = new Set<string>()

  for (const edge of filteredEdges) {
    const from = String(edge?.source || '')
    const to = String(edge?.target || '')
    if (!from || !to) continue
    if (from === centerNodeId && to !== centerNodeId) {
      adjacentToCenter.add(to)
      primarySeed.add(to)
      continue
    }
    if (to === centerNodeId && from !== centerNodeId) {
      adjacentToCenter.add(from)
      primarySeed.add(from)
      continue
    }
  }

  for (const edge of filteredEdges) {
    const from = String(edge?.source || '')
    const to = String(edge?.target || '')
    if (!from || !to) continue
    if (primarySeed.has(from) && to !== centerNodeId && !primarySeed.has(to)) adjacentToPrimary.add(to)
    if (primarySeed.has(to) && from !== centerNodeId && !primarySeed.has(from)) adjacentToPrimary.add(from)
  }

  let primaryCandidates: GraphNode[] = []
  let secondaryCandidates: GraphNode[] = []

  if (adjacentToCenter.size > 0) {
    primaryCandidates = nodes.filter((node) => {
      const id = String(node?.id || '')
      return id !== centerNodeId && adjacentToCenter.has(id)
    })
  } else if (centerType === 'industry') {
    primaryCandidates = nodes.filter((node) => String(node?.id || '') !== centerNodeId && String(node?.type || '') === 'theme')
  } else {
    primaryCandidates = nodes.filter((node) => String(node?.id || '') !== centerNodeId && Number(node?.layer ?? 0) === 1)
  }

  if (adjacentToPrimary.size > 0) {
    secondaryCandidates = nodes.filter((node) => {
      const id = String(node?.id || '')
      return id !== centerNodeId && !adjacentToCenter.has(id) && adjacentToPrimary.has(id)
    })
  } else if (centerType === 'industry') {
    secondaryCandidates = nodes.filter((node) => String(node?.id || '') !== centerNodeId && String(node?.type || '') === 'stock')
  } else {
    secondaryCandidates = nodes.filter((node) => String(node?.id || '') !== centerNodeId && Number(node?.layer ?? 0) >= 2)
  }

  const sortedPrimary = sortByScore(primaryCandidates).slice(0, layout.maxPrimary)
  const sortedSecondary = hideSecondary ? [] : sortByScore(secondaryCandidates).slice(0, layout.maxSecondary)
  const visible = [center, ...sortedPrimary, ...sortedSecondary]
  const visibleIdSet = new Set(visible.map((item) => String(item?.id || '')))
  const hiddenNodeCount = Math.max(0, nodes.length - visible.length)

  const renderNodes: GraphRenderNode[] = [
    {
      id: centerNodeId,
      text: labelOf(center),
      x: layout.centerX,
      y: centerY,
      width: layout.nodeWidthCenter,
      height: layout.nodeHeight + 10,
      color: '#f5fbfe',
      borderColor: '#0f617a',
      borderWidth: 2,
      fontColor: '#102131',
      data: {
        raw: center,
        role: 'center',
        score: scoreOf(center),
        meta: nodeMeta(center, centerNodeId),
      },
    },
  ]

  sortedPrimary.forEach((node, index) => {
    renderNodes.push({
      id: String(node.id || ''),
      text: labelOf(node),
      x: layout.primaryX,
      y: stackY(index, sortedPrimary.length, centerY),
      width: layout.nodeWidthPrimary,
      height: layout.nodeHeight,
      color: '#f8fbfc',
      borderColor: '#7f9aad',
      borderWidth: 1.4,
      fontColor: '#1d3345',
      data: {
        raw: node,
        role: 'primary',
        score: scoreOf(node),
        meta: nodeMeta(node, centerNodeId),
      },
    })
  })

  sortedSecondary.forEach((node, index) => {
    renderNodes.push({
      id: String(node.id || ''),
      text: labelOf(node),
      x: layout.secondaryX,
      y: stackY(index, sortedSecondary.length, centerY),
      width: layout.nodeWidthSecondary,
      height: layout.nodeHeight - 6,
      color: '#fcfdfe',
      borderColor: '#c2cfd9',
      borderWidth: 1,
      fontColor: '#334a5d',
      data: {
        raw: node,
        role: 'secondary',
        score: scoreOf(node),
        meta: nodeMeta(node, centerNodeId),
      },
    })
  })

  const renderLines: GraphRenderEdge[] = []
  for (const edge of filteredEdges) {
    const from = String(edge?.source || '')
    const to = String(edge?.target || '')
    if (!visibleIdSet.has(from) || !visibleIdSet.has(to)) continue
    const role = lineRole(edge, centerNodeId)
    const style = lineStyle(edge, role, selectedNodeId)
    renderLines.push({
      from,
      to,
      color: style.color,
      opacity: style.opacity,
      lineWidth: style.lineWidth,
      lineShape: 4,
      showStartArrow: false,
      showEndArrow: false,
      lineDirection: 'h',
      forDisplayOnly: true,
      disableDefaultClickEffect: true,
      data: {
        raw: edge,
        role,
      },
    })
  }

  if (!renderLines.length && visibleIdSet.size > 1) {
    for (const node of sortedPrimary.slice(0, 6)) {
      renderLines.push({
        from: centerNodeId,
        to: String(node.id || ''),
        color: COLOR_NEUTRAL,
        opacity: 0.32,
        lineWidth: 1.1,
        lineShape: 4,
        showStartArrow: false,
        showEndArrow: false,
        forDisplayOnly: true,
        disableDefaultClickEffect: true,
        data: {
          raw: { source: centerNodeId, target: node.id, relation_key: 'fallback' },
          role: 'secondary',
        },
      })
    }
  }

  return {
    jsonData: {
      rootId: centerNodeId,
      nodes: renderNodes,
      lines: renderLines,
    },
    hiddenNodeCount,
    secondaryCandidateCount: secondaryCandidates.length,
    primaryCandidateCount: primaryCandidates.length,
  }
}
