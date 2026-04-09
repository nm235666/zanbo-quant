from __future__ import annotations

from collections import defaultdict
from typing import Any


def _table_exists(conn, table_name: str) -> bool:
    row = conn.execute(
        "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name=?",
        (table_name,),
    ).fetchone()
    return bool(row and int(row[0] or 0) > 0)


def _as_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except Exception:
        return default


def _clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def _parse_json(raw: Any) -> dict[str, Any]:
    if raw is None:
        return {}
    if isinstance(raw, dict):
        return raw
    try:
        import json

        parsed = json.loads(str(raw or ""))
        return parsed if isinstance(parsed, dict) else {}
    except Exception:
        return {}


def _normalize_center_type(center_type: str) -> str:
    raw = str(center_type or "").strip().lower()
    if raw in {"industry", "sector"}:
        return "industry"
    return "theme"


def _latest_score_date(conn) -> str:
    if not _table_exists(conn, "stock_scores_daily"):
        return ""
    row = conn.execute("SELECT MAX(score_date) FROM stock_scores_daily").fetchone()
    return str(row[0] or "").strip() if row else ""


def _latest_theme_row(conn, center_key: str) -> dict[str, Any] | None:
    if not _table_exists(conn, "theme_hotspot_tracker"):
        return None
    key = str(center_key or "").strip()
    like = f"%{key}%"
    if key:
        row = conn.execute(
            """
            SELECT t.theme_name, t.theme_group, t.direction, t.theme_strength, t.confidence, t.evidence_count,
                   t.intl_news_count, t.domestic_news_count, t.stock_news_count, t.chatroom_count, t.stock_link_count,
                   t.latest_evidence_time, t.heat_level, t.top_terms_json, t.top_stocks_json, t.source_summary_json,
                   t.evidence_json, s.current_state, s.prev_state, s.driver_type, s.driver_title
            FROM theme_hotspot_tracker t
            LEFT JOIN signal_state_tracker s
              ON s.signal_scope = 'theme' AND s.signal_key = ('theme:' || t.theme_name)
            WHERE t.theme_name = ? OR t.theme_name LIKE ? OR t.theme_group LIKE ? OR COALESCE(t.top_terms_json, '') LIKE ?
            ORDER BY CASE WHEN t.theme_name = ? THEN 0 ELSE 1 END, t.theme_strength DESC, t.confidence DESC, t.theme_name
            LIMIT 1
            """,
            (key, like, like, like, key),
        ).fetchone()
        if row:
            return dict(row)
    row = conn.execute(
        """
        SELECT t.theme_name, t.theme_group, t.direction, t.theme_strength, t.confidence, t.evidence_count,
               t.intl_news_count, t.domestic_news_count, t.stock_news_count, t.chatroom_count, t.stock_link_count,
               t.latest_evidence_time, t.heat_level, t.top_terms_json, t.top_stocks_json, t.source_summary_json,
               t.evidence_json, s.current_state, s.prev_state, s.driver_type, s.driver_title
        FROM theme_hotspot_tracker t
        LEFT JOIN signal_state_tracker s
          ON s.signal_scope = 'theme' AND s.signal_key = ('theme:' || t.theme_name)
        ORDER BY t.theme_strength DESC, t.confidence DESC, t.theme_name
        LIMIT 1
        """
    ).fetchone()
    return dict(row) if row else None


def _latest_industry_row(conn, center_key: str) -> dict[str, Any] | None:
    if not _table_exists(conn, "stock_scores_daily"):
        return None
    latest_score_date = _latest_score_date(conn)
    if not latest_score_date:
        return None
    key = str(center_key or "").strip()
    like = f"%{key}%"
    if key:
        row = conn.execute(
            """
            SELECT
                industry,
                COUNT(*) AS stock_count,
                AVG(COALESCE(industry_total_score, total_score, 0)) AS avg_score,
                AVG(COALESCE(total_score, 0)) AS avg_total_score,
                MAX(COALESCE(industry_total_score, total_score, 0)) AS top_score,
                MAX(name) AS any_name,
                MAX(ts_code) AS any_ts_code
            FROM stock_scores_daily
            WHERE score_date = ? AND (industry = ? OR industry LIKE ? OR name LIKE ? OR ts_code LIKE ?)
            GROUP BY industry
            ORDER BY CASE WHEN industry = ? THEN 0 ELSE 1 END, avg_score DESC, stock_count DESC, industry
            LIMIT 1
            """,
            (latest_score_date, key, like, like, like, key),
        ).fetchone()
        if row:
            return dict(row)
    row = conn.execute(
        """
        SELECT
            industry,
            COUNT(*) AS stock_count,
            AVG(COALESCE(industry_total_score, total_score, 0)) AS avg_score,
            AVG(COALESCE(total_score, 0)) AS avg_total_score,
            MAX(COALESCE(industry_total_score, total_score, 0)) AS top_score,
            MAX(name) AS any_name,
            MAX(ts_code) AS any_ts_code
        FROM stock_scores_daily
        WHERE score_date = ? AND COALESCE(industry, '') <> ''
        GROUP BY industry
        ORDER BY avg_score DESC, stock_count DESC, industry
        LIMIT 1
        """,
        (latest_score_date,),
    ).fetchone()
    return dict(row) if row else None


def _load_theme_signal_profile(conn, theme_name: str) -> dict[str, Any]:
    if not theme_name:
        return {}
    tables = ["investment_signal_tracker", "investment_signal_tracker_7d", "investment_signal_tracker_1d"]
    rows: list[dict[str, Any]] = []
    for table_name in tables:
        if not _table_exists(conn, table_name):
            continue
        matched = conn.execute(
            f"""
            SELECT signal_key, signal_type, subject_name, ts_code, direction, signal_strength, confidence,
                   evidence_count, news_count, stock_news_count, chatroom_count, signal_status,
                   latest_signal_date, source_summary_json, evidence_json
            FROM {table_name}
            WHERE subject_name LIKE ? OR signal_key LIKE ? OR ts_code LIKE ?
            ORDER BY signal_strength DESC, confidence DESC, latest_signal_date DESC
            LIMIT 3
            """,
            (f"%{theme_name}%", f"%{theme_name}%", f"%{theme_name}%"),
        ).fetchall()
        rows.extend(dict(row) for row in matched)
    best = None
    best_score = -1.0
    for item in rows:
        score = _as_float(item.get("signal_strength")) * 100 + _as_float(item.get("confidence"))
        if score > best_score:
            best_score = score
            best = item
    if not best:
        return {}
    best["source_count"] = len(rows)
    best["source_summary"] = _parse_json(best.get("source_summary_json"))
    best["evidence"] = _parse_json(best.get("evidence_json"))
    return best


def _load_stock_signal_profile(conn, ts_code: str) -> dict[str, Any]:
    code = str(ts_code or "").strip().upper()
    if not code:
        return {}
    tables = ["investment_signal_tracker", "investment_signal_tracker_7d", "investment_signal_tracker_1d"]
    rows: list[dict[str, Any]] = []
    for table_name in tables:
        if not _table_exists(conn, table_name):
            continue
        matched = conn.execute(
            f"""
            SELECT signal_key, signal_type, subject_name, ts_code, direction, signal_strength, confidence,
                   evidence_count, news_count, stock_news_count, chatroom_count, signal_status,
                   latest_signal_date, source_summary_json, evidence_json
            FROM {table_name}
            WHERE ts_code = ? OR signal_key LIKE ? OR subject_name LIKE ?
            ORDER BY signal_strength DESC, confidence DESC, latest_signal_date DESC
            LIMIT 3
            """,
            (code, f"%{code}%", f"%{code}%"),
        ).fetchall()
        rows.extend(dict(row) for row in matched)
    best = None
    best_score = -1.0
    for item in rows:
        score = _as_float(item.get("signal_strength")) * 100 + _as_float(item.get("confidence"))
        if score > best_score:
            best_score = score
            best = item
    if not best:
        return {}
    best["source_count"] = len(rows)
    best["source_summary"] = _parse_json(best.get("source_summary_json"))
    best["evidence"] = _parse_json(best.get("evidence_json"))
    return best


def _top_market_expectations_for_theme(conn, theme_name: str, limit: int = 5):
    if not theme_name or not _table_exists(conn, "market_expectation_items"):
        return []
    rows = conn.execute(
        """
        SELECT question, volume, liquidity, end_date, source_url, related_theme_names_json, outcome_prices_json
        FROM market_expectation_items
        WHERE related_theme_names_json LIKE ?
        ORDER BY COALESCE(volume, 0) DESC, COALESCE(liquidity, 0) DESC, id DESC
        LIMIT ?
        """,
        (f'%"{theme_name}"%', limit),
    ).fetchall()
    return [dict(r) for r in rows]


def _build_node(
    *,
    node_id: str,
    node_type: str,
    label: str,
    layer: int,
    summary: str,
    subtitle: str = "",
    status: str = "",
    weight: float = 0.0,
    score: float = 0.0,
    strength: float = 0.0,
    target: str = "",
    actions: list[dict[str, str]] | None = None,
    highlights: list[str] | None = None,
    metrics: dict[str, Any] | None = None,
    source: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "id": node_id,
        "type": node_type,
        "label": label,
        "layer": layer,
        "summary": summary,
        "subtitle": subtitle,
        "status": status,
        "weight": round(_clamp(weight, 0.0, 9999.0), 2),
        "score": round(_clamp(score, 0.0, 9999.0), 2),
        "strength": round(_clamp(strength, 0.0, 9999.0), 2),
        "target": target,
        "actions": actions or [],
        "highlights": highlights or [],
        "metrics": metrics or {},
        "source": source or {},
    }


def _build_edge(
    *,
    source: str,
    target: str,
    relation_key: str,
    relation_label: str,
    weight: float = 0.0,
    summary: str = "",
    evidence_count: int = 0,
) -> dict[str, Any]:
    return {
        "id": f"{source}__{relation_key}__{target}",
        "source": source,
        "target": target,
        "relation_key": relation_key,
        "relation_label": relation_label,
        "weight": round(_clamp(weight, 0.0, 9999.0), 2),
        "summary": summary,
        "evidence_count": int(evidence_count or 0),
    }


def _stock_target(ts_code: str) -> str:
    code = str(ts_code or "").strip().upper()
    return f"/stocks/detail/{code}" if code else "/stocks/list"


def _theme_target(theme_name: str) -> str:
    theme = str(theme_name or "").strip()
    return f"/signals/themes?keyword={theme}" if theme else "/signals/themes"


def _industry_target(industry: str) -> str:
    name = str(industry or "").strip()
    return f"/stocks/scores?industry={name}" if name else "/stocks/scores"


def _build_theme_graph(conn, *, center_key: str, depth: int, limit: int) -> dict[str, Any]:
    latest_score_date = _latest_score_date(conn)
    center_row = _latest_theme_row(conn, center_key)
    if not center_row:
        center_name = str(center_key or "主题图谱").strip() or "主题图谱"
        center_node = _build_node(
            node_id=f"theme:{center_name}",
            node_type="theme",
            label=center_name,
            layer=0,
            summary="当前没有可用的主题热点数据，显示空图骨架。",
            subtitle="主题中心 · 数据不足",
            status="empty",
            target=_theme_target(center_name),
            actions=[{"label": "打开主题热点页", "to": _theme_target(center_name)}],
            highlights=["先补齐主题热点引擎与主题股票映射数据"],
            metrics={"theme_count": 0, "industry_count": 0, "stock_count": 0},
        )
        return {
            "center_type": "theme",
            "center_key": center_name,
            "center_label": center_name,
            "center": center_node,
            "nodes": [center_node],
            "edges": [],
            "summary": {
                "node_count": 1,
                "edge_count": 0,
                "theme_count": 1,
                "industry_count": 0,
                "stock_count": 0,
                "depth": depth,
                "latest_score_date": latest_score_date,
                "empty": True,
                "message": "当前没有足够的主题热点或映射数据。",
            },
            "legend": [
                {"type": "theme", "label": "主题"},
                {"type": "industry", "label": "行业"},
                {"type": "stock", "label": "股票"},
            ],
        }

    theme_name = str(center_row.get("theme_name") or center_key or "").strip()
    theme_signal = _load_theme_signal_profile(conn, theme_name)
    market_expectations = _top_market_expectations_for_theme(conn, theme_name, limit=5)
    top_stocks_rows = []
    if _table_exists(conn, "theme_stock_mapping"):
        top_stocks_rows = [
            dict(row)
            for row in conn.execute(
                """
                SELECT
                    m.theme_name, m.ts_code, COALESCE(m.stock_name, c.name, s.name, m.ts_code) AS stock_name,
                    COALESCE(c.industry, s.industry, '未知行业') AS industry,
                    COALESCE(s.total_score, 0) AS total_score,
                    COALESCE(s.industry_total_score, 0) AS industry_total_score,
                    COALESCE(s.score_grade, '') AS score_grade,
                    COALESCE(s.industry_score_grade, '') AS industry_score_grade,
                    COALESCE(s.trend_score, 0) AS trend_score,
                    COALESCE(s.news_score, 0) AS news_score,
                    COALESCE(s.risk_score, 0) AS risk_score,
                    COALESCE(m.weight, 1.0) AS relation_weight,
                    COALESCE(m.relation_type, '主题映射') AS relation_type,
                    COALESCE(m.notes, '') AS notes
                FROM theme_stock_mapping m
                LEFT JOIN stock_codes c ON c.ts_code = m.ts_code
                LEFT JOIN stock_scores_daily s
                  ON s.ts_code = m.ts_code AND s.score_date = ?
                WHERE m.theme_name = ?
                ORDER BY COALESCE(s.industry_total_score, s.total_score, 0) DESC, relation_weight DESC, stock_name
                LIMIT ?
                """,
                (latest_score_date, theme_name, max(limit * 2, limit)),
            ).fetchall()
        ]

    stock_nodes_by_code: dict[str, dict[str, Any]] = {}
    industry_buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in top_stocks_rows:
        ts_code = str(row.get("ts_code") or "").strip().upper()
        stock_name = str(row.get("stock_name") or ts_code or "").strip() or ts_code
        industry = str(row.get("industry") or "未知行业").strip() or "未知行业"
        stock_signal = _load_stock_signal_profile(conn, ts_code)
        score = _as_float(row.get("total_score"))
        industry_score = _as_float(row.get("industry_total_score"))
        node = _build_node(
            node_id=f"stock:{ts_code}",
            node_type="stock",
            label=stock_name,
            layer=2,
            summary=f"{industry} · 综合分 {score:.1f} · 行业分 {industry_score:.1f}",
            subtitle=str(row.get("score_grade") or row.get("industry_score_grade") or "股票"),
            status=str(stock_signal.get("signal_status") or row.get("relation_type") or "观察"),
            weight=_as_float(row.get("relation_weight"), 1.0),
            score=score,
            strength=_as_float(stock_signal.get("signal_strength"), 0.0),
            target=_stock_target(ts_code),
            actions=[
                {"label": "打开股票详情", "to": _stock_target(ts_code)},
                {"label": "打开决策板", "to": f"/research/decision?ts_code={ts_code}"},
            ],
            highlights=[
                f"行业 {industry}",
                f"信号状态 {stock_signal.get('signal_status') or '未命中'}",
                f"最新信号 {stock_signal.get('latest_signal_date') or '-'}",
            ],
            metrics={
                "relation_weight": _as_float(row.get("relation_weight"), 1.0),
                "theme_weight": _as_float(row.get("relation_weight"), 1.0),
                "signal_strength": round(_as_float(stock_signal.get("signal_strength")), 2),
                "confidence": round(_as_float(stock_signal.get("confidence")), 2),
                "score_grade": row.get("score_grade"),
                "industry_score_grade": row.get("industry_score_grade"),
            },
            source={
                "theme_name": theme_name,
                "relation_type": row.get("relation_type"),
                "notes": row.get("notes"),
                "signal": stock_signal,
            },
        )
        stock_nodes_by_code[ts_code] = node
        industry_buckets[industry].append({"row": row, "stock_node": node, "stock_signal": stock_signal})

    industry_nodes: list[dict[str, Any]] = []
    for industry, items in industry_buckets.items():
        scores = [_as_float(item["row"].get("industry_total_score") or item["row"].get("total_score")) for item in items]
        best_item = sorted(items, key=lambda item: _as_float(item["row"].get("industry_total_score") or item["row"].get("total_score")), reverse=True)[0]
        top_stock_names = [str(item["stock_node"]["label"]) for item in items[:3]]
        avg_score = sum(scores) / len(scores) if scores else 0.0
        node = _build_node(
            node_id=f"industry:{industry}",
            node_type="industry",
            label=industry,
            layer=1,
            summary=f"关联 {len(items)} 只股票，平均分 {avg_score:.1f}",
            subtitle=f"主题中心 · {len(top_stock_names)} 代表股",
            status=str(best_item["stock_node"].get("status") or "行业"),
            weight=max(_as_float(best_item["row"].get("relation_weight"), 1.0), len(items)),
            score=avg_score,
            strength=_as_float(best_item["stock_signal"].get("signal_strength"), 0.0),
            target=_industry_target(industry),
            actions=[
                {"label": "打开股票评分", "to": _industry_target(industry)},
                {"label": "打开股票列表", "to": f"/stocks/list?keyword={industry}"},
            ],
            highlights=[
                f"代表股 {', '.join(top_stock_names) if top_stock_names else '-'}",
                f"中心主题 {theme_name}",
            ],
            metrics={
                "stock_count": len(items),
                "avg_score": round(avg_score, 2),
                "best_stock": best_item["stock_node"]["label"],
            },
            source={
                "theme_name": theme_name,
                "stocks": [item["stock_node"]["id"] for item in items],
            },
        )
        industry_nodes.append(node)

    industry_nodes.sort(key=lambda item: (-_as_float(item.get("score")), str(item.get("label") or "")))
    if depth <= 1:
        visible_industry_nodes = industry_nodes[:limit]
        visible_stock_nodes: list[dict[str, Any]] = []
    else:
        visible_industry_nodes = industry_nodes[:limit]
        visible_stock_nodes = sorted(stock_nodes_by_code.values(), key=lambda item: (-_as_float(item.get("score")), str(item.get("label") or "")))[:limit]

    center_node = _build_node(
        node_id=f"theme:{theme_name}",
        node_type="theme",
        label=theme_name,
        layer=0,
        summary=f"{center_row.get('theme_group') or '主题'} · 热度 {center_row.get('heat_level') or '-'} · 状态 {center_row.get('current_state') or '-'}",
        subtitle=f"{center_row.get('direction') or '-'} · 强度 { _as_float(center_row.get('theme_strength')):.1f}",
        status=str(center_row.get("current_state") or center_row.get("heat_level") or "主题"),
        weight=_as_float(center_row.get("theme_strength"), 0.0),
        score=_as_float(center_row.get("confidence"), 0.0),
        strength=_as_float(theme_signal.get("signal_strength"), 0.0),
        target=_theme_target(theme_name),
        actions=[
            {"label": "打开主题热点页", "to": _theme_target(theme_name)},
            {"label": "看信号时间线", "to": f"/signals/timeline?signal_key=theme:{theme_name}"},
            {"label": "看状态时间线", "to": f"/signals/state-timeline?signal_scope=theme&signal_key=theme:{theme_name}"},
        ],
        highlights=[
            f"股票映射 {center_row.get('stock_link_count') or 0} 只",
            f"证据数 {center_row.get('evidence_count') or 0}",
            f"最新证据 {center_row.get('latest_evidence_time') or '-'}",
        ],
        metrics={
            "theme_strength": round(_as_float(center_row.get("theme_strength")), 2),
            "confidence": round(_as_float(center_row.get("confidence")), 2),
            "evidence_count": int(center_row.get("evidence_count") or 0),
            "stock_link_count": int(center_row.get("stock_link_count") or 0),
            "signal_strength": round(_as_float(theme_signal.get("signal_strength")), 2),
            "signal_confidence": round(_as_float(theme_signal.get("confidence")), 2),
            "market_expectations": len(market_expectations),
        },
        source={
            "theme_row": center_row,
            "signal_profile": theme_signal,
            "market_expectations": market_expectations,
        },
    )

    nodes = [center_node, *visible_industry_nodes, *visible_stock_nodes]
    edges: list[dict[str, Any]] = []
    for industry_node in visible_industry_nodes:
        edges.append(
            _build_edge(
                source=center_node["id"],
                target=industry_node["id"],
                relation_key="theme_industry",
                relation_label="主题→行业",
                weight=_as_float(industry_node.get("score")),
                summary=f"{theme_name} 关联行业 {industry_node['label']}",
                evidence_count=int(center_row.get("evidence_count") or 0),
            )
        )
    for industry_node in visible_industry_nodes:
        industry_label = str(industry_node.get("label") or "").strip()
        for stock_node in visible_stock_nodes:
            if str(stock_node.get("source", {}).get("theme_name") or "") != theme_name:
                continue
            if str(stock_node.get("metrics", {}).get("relation_weight") or "") == "":
                continue
            if str(stock_node.get("source", {}).get("signal", {}).get("ts_code") or "").strip().upper() != str(stock_node.get("label") or "").strip().upper():
                pass
            if str(stock_node.get("summary") or "").find(industry_label) == -1:
                continue
            edges.append(
                _build_edge(
                    source=industry_node["id"],
                    target=stock_node["id"],
                    relation_key="industry_stock",
                    relation_label="行业→股票",
                    weight=_as_float(stock_node.get("score")),
                    summary=f"{industry_label} 包含 {stock_node['label']}",
                    evidence_count=int(center_row.get("evidence_count") or 0),
                )
            )

    detail = {
        "why": f"当前主题 {theme_name} 具有 {center_row.get('stock_link_count') or 0} 条股票映射与 {center_row.get('evidence_count') or 0} 条证据",
        "next_steps": [
            {"label": "打开主题热点页", "to": _theme_target(theme_name)},
            {"label": "看信号时间线", "to": f"/signals/timeline?signal_key=theme:{theme_name}"},
            {"label": "看状态时间线", "to": f"/signals/state-timeline?signal_scope=theme&signal_key=theme:{theme_name}"},
        ],
        "market_expectations": market_expectations[:5],
    }
    summary = {
        "node_count": len(nodes),
        "edge_count": len(edges),
        "theme_count": 1,
        "industry_count": len(visible_industry_nodes),
        "stock_count": len(visible_stock_nodes),
        "depth": depth,
        "latest_score_date": latest_score_date,
        "center_type": "theme",
        "center_label": theme_name,
    }
    return {
        "center_type": "theme",
        "center_key": theme_name,
        "center_label": theme_name,
        "center": center_node,
        "detail": detail,
        "nodes": nodes,
        "edges": edges,
        "summary": summary,
        "legend": [
            {"type": "theme", "label": "主题"},
            {"type": "industry", "label": "行业"},
            {"type": "stock", "label": "股票"},
            {"relation_key": "theme_industry", "label": "主题→行业"},
            {"relation_key": "industry_stock", "label": "行业→股票"},
        ],
    }


def _build_industry_graph(conn, *, center_key: str, depth: int, limit: int) -> dict[str, Any]:
    latest_score_date = _latest_score_date(conn)
    center_row = _latest_industry_row(conn, center_key)
    if not center_row:
        industry_name = str(center_key or "行业图谱").strip() or "行业图谱"
        center_node = _build_node(
            node_id=f"industry:{industry_name}",
            node_type="industry",
            label=industry_name,
            layer=0,
            summary="当前没有可用的行业评分数据，显示空图骨架。",
            subtitle="行业中心 · 数据不足",
            status="empty",
            target=_industry_target(industry_name),
            actions=[{"label": "打开股票评分", "to": _industry_target(industry_name)}],
            highlights=["先补齐股票评分和行业维度数据"],
            metrics={"theme_count": 0, "industry_count": 1, "stock_count": 0},
        )
        return {
            "center_type": "industry",
            "center_key": industry_name,
            "center_label": industry_name,
            "center": center_node,
            "nodes": [center_node],
            "edges": [],
            "summary": {
                "node_count": 1,
                "edge_count": 0,
                "theme_count": 0,
                "industry_count": 1,
                "stock_count": 0,
                "depth": depth,
                "latest_score_date": latest_score_date,
                "empty": True,
                "message": "当前没有足够的行业评分或映射数据。",
            },
            "legend": [
                {"type": "industry", "label": "行业"},
                {"type": "theme", "label": "主题"},
                {"type": "stock", "label": "股票"},
            ],
        }

    industry_name = str(center_row.get("industry") or center_key or "").strip()
    latest_stock_rows = []
    if _table_exists(conn, "stock_scores_daily"):
        if latest_score_date:
            latest_stock_rows = [
                dict(row)
                for row in conn.execute(
                    """
                    SELECT s.ts_code, s.name, s.industry, s.total_score, s.industry_total_score, s.score_grade,
                           s.industry_score_grade, s.trend_score, s.news_score, s.risk_score
                    FROM stock_scores_daily s
                    WHERE s.score_date = ? AND COALESCE(s.industry, '') = ?
                    ORDER BY COALESCE(s.industry_total_score, s.total_score, 0) DESC, s.ts_code
                    LIMIT ?
                    """,
                    (latest_score_date, industry_name, max(limit * 2, limit)),
                ).fetchall()
            ]
        if not latest_stock_rows:
            latest_stock_rows = [
                {
                    "ts_code": str(row[0] or "").strip().upper(),
                    "name": str(row[1] or row[0] or "").strip(),
                    "industry": str(row[2] or industry_name or "").strip(),
                    "total_score": 0,
                    "industry_total_score": 0,
                    "score_grade": "",
                    "industry_score_grade": "",
                    "trend_score": 0,
                    "news_score": 0,
                    "risk_score": 0,
                    "list_status": "",
                }
                for row in conn.execute(
                    """
                    SELECT ts_code, name, industry
                    FROM stock_codes
                    WHERE COALESCE(industry, '') = ?
                    ORDER BY ts_code
                    LIMIT ?
                    """,
                    (industry_name, max(limit * 2, limit)),
                ).fetchall()
            ]

    theme_rows = []
    if _table_exists(conn, "theme_stock_mapping"):
        theme_rows = [
            dict(row)
            for row in conn.execute(
                """
                SELECT
                    m.theme_name,
                    COUNT(DISTINCT m.ts_code) AS stock_count,
                    SUM(COALESCE(m.weight, 1.0)) AS total_weight,
                    MAX(COALESCE(t.theme_strength, 0)) AS theme_strength,
                    MAX(COALESCE(t.confidence, 0)) AS confidence,
                    MAX(COALESCE(t.heat_level, '')) AS heat_level,
                    MAX(COALESCE(t.direction, '')) AS direction,
                    MAX(COALESCE(s.current_state, '')) AS current_state
                FROM theme_stock_mapping m
                JOIN stock_codes c ON c.ts_code = m.ts_code
                LEFT JOIN theme_hotspot_tracker t ON t.theme_name = m.theme_name
                LEFT JOIN signal_state_tracker s
                  ON s.signal_scope = 'theme' AND s.signal_key = ('theme:' || m.theme_name)
                WHERE COALESCE(c.industry, '') = ?
                GROUP BY m.theme_name
                ORDER BY total_weight DESC, stock_count DESC, m.theme_name
                LIMIT ?
                """,
                (industry_name, max(limit * 2, limit)),
            ).fetchall()
        ]

    theme_nodes_by_name: dict[str, dict[str, Any]] = {}
    stock_nodes: list[dict[str, Any]] = []
    for row in latest_stock_rows[:limit]:
        ts_code = str(row.get("ts_code") or "").strip().upper()
        stock_name = str(row.get("name") or ts_code).strip() or ts_code
        stock_signal = _load_stock_signal_profile(conn, ts_code)
        score = _as_float(row.get("total_score"))
        industry_score = _as_float(row.get("industry_total_score"))
        node = _build_node(
            node_id=f"stock:{ts_code}",
            node_type="stock",
            label=stock_name,
            layer=2,
            summary=f"{industry_name} · 综合分 {score:.1f} · 行业分 {industry_score:.1f}",
            subtitle=str(row.get("score_grade") or row.get("industry_score_grade") or "股票"),
            status=str(stock_signal.get("signal_status") or row.get("list_status") or "观察"),
            weight=max(score, industry_score, 1.0),
            score=score,
            strength=_as_float(stock_signal.get("signal_strength"), 0.0),
            target=_stock_target(ts_code),
            actions=[
                {"label": "打开股票详情", "to": _stock_target(ts_code)},
                {"label": "打开决策板", "to": f"/research/decision?ts_code={ts_code}"},
            ],
            highlights=[
                f"行业 {industry_name}",
                f"信号状态 {stock_signal.get('signal_status') or '未命中'}",
                f"最新信号 {stock_signal.get('latest_signal_date') or '-'}",
            ],
            metrics={
                "signal_strength": round(_as_float(stock_signal.get("signal_strength")), 2),
                "confidence": round(_as_float(stock_signal.get("confidence")), 2),
                "score_grade": row.get("score_grade"),
                "industry_score_grade": row.get("industry_score_grade"),
            },
            source={
                "industry": industry_name,
                "signal": stock_signal,
            },
        )
        stock_nodes.append(node)

    for row in theme_rows[:limit]:
        theme_name = str(row.get("theme_name") or "").strip()
        if not theme_name:
            continue
        theme_row = _latest_theme_row(conn, theme_name) or {}
        theme_signal = _load_theme_signal_profile(conn, theme_name)
        connected_stock_count = int(row.get("stock_count") or 0)
        node = _build_node(
            node_id=f"theme:{theme_name}",
            node_type="theme",
            label=theme_name,
            layer=1,
            summary=f"{industry_name} 关联主题 · 样本 {connected_stock_count} 只",
            subtitle=f"{row.get('direction') or '-'} · 强度 { _as_float(row.get('theme_strength')):.1f}",
            status=str(theme_signal.get("signal_status") or row.get("current_state") or row.get("heat_level") or "主题"),
            weight=max(_as_float(row.get("total_weight"), 0.0), _as_float(row.get("theme_strength"), 0.0), 1.0),
            score=_as_float(row.get("confidence"), 0.0),
            strength=_as_float(theme_signal.get("signal_strength"), 0.0),
            target=_theme_target(theme_name),
            actions=[
                {"label": "打开主题热点页", "to": _theme_target(theme_name)},
                {"label": "看信号时间线", "to": f"/signals/timeline?signal_key=theme:{theme_name}"},
            ],
            highlights=[
                f"当前状态 {row.get('current_state') or '-'}",
                f"主题强度 {row.get('theme_strength') or '-'}",
                f"关联股票 {connected_stock_count} 只",
            ],
            metrics={
                "stock_count": connected_stock_count,
                "theme_strength": round(_as_float(row.get("theme_strength")), 2),
                "confidence": round(_as_float(row.get("confidence")), 2),
            },
            source={
                "industry": industry_name,
                "theme_row": theme_row,
                "signal": theme_signal,
            },
        )
        theme_nodes_by_name[theme_name] = node

    if depth <= 1:
        visible_theme_nodes = list(theme_nodes_by_name.values())[:limit]
        visible_stock_nodes = []
    else:
        visible_theme_nodes = list(theme_nodes_by_name.values())[:limit]
        visible_stock_nodes = stock_nodes[:limit]

    center_node = _build_node(
        node_id=f"industry:{industry_name}",
        node_type="industry",
        label=industry_name,
        layer=0,
        summary=f"最新行业均分 { _as_float(center_row.get('avg_score')):.1f} · 样本 {center_row.get('stock_count') or 0} 只",
        subtitle=f"最新评分日 {latest_score_date or '-'}",
        status="行业中心",
        weight=max(_as_float(center_row.get("avg_score"), 0.0), _as_float(center_row.get("top_score"), 0.0), 1.0),
        score=_as_float(center_row.get("avg_score"), 0.0),
        strength=_as_float(center_row.get("top_score"), 0.0),
        target=_industry_target(industry_name),
        actions=[
            {"label": "打开股票评分", "to": _industry_target(industry_name)},
            {"label": "打开股票列表", "to": f"/stocks/list?keyword={industry_name}"},
        ],
        highlights=[
            f"样本 {center_row.get('stock_count') or 0} 只",
            f"均分 { _as_float(center_row.get('avg_score')):.1f}",
            f"顶部样本 {center_row.get('any_name') or center_row.get('any_ts_code') or '-'}",
        ],
        metrics={
            "stock_count": int(center_row.get("stock_count") or 0),
            "avg_score": round(_as_float(center_row.get("avg_score")), 2),
            "top_score": round(_as_float(center_row.get("top_score")), 2),
        },
        source={
            "industry_row": center_row,
            "stocks": [item["id"] for item in visible_stock_nodes],
            "themes": [item["id"] for item in visible_theme_nodes],
        },
    )

    nodes = [center_node, *visible_theme_nodes, *visible_stock_nodes]
    edges: list[dict[str, Any]] = []
    for theme_node in visible_theme_nodes:
        theme_name = str(theme_node.get("label") or "").strip()
        relation_weight = max(_as_float(theme_node.get("weight"), 0.0), 1.0)
        edges.append(
            _build_edge(
                source=center_node["id"],
                target=theme_node["id"],
                relation_key="industry_theme",
                relation_label="行业→主题",
                weight=relation_weight,
                summary=f"{industry_name} 关联主题 {theme_name}",
                evidence_count=int(theme_node.get("metrics", {}).get("stock_count") or 0),
            )
        )
    for stock_node in visible_stock_nodes:
        edges.append(
            _build_edge(
                source=center_node["id"],
                target=stock_node["id"],
                relation_key="industry_stock",
                relation_label="行业→股票",
                weight=_as_float(stock_node.get("score"), 0.0),
                summary=f"{industry_name} 包含 {stock_node['label']}",
                evidence_count=1,
            )
        )
        for theme_node in visible_theme_nodes:
            if str(theme_node.get("source", {}).get("industry") or "").strip() != industry_name:
                continue
            edges.append(
                _build_edge(
                    source=theme_node["id"],
                    target=stock_node["id"],
                    relation_key="theme_stock",
                    relation_label="主题→股票",
                    weight=_as_float(stock_node.get("score"), 0.0),
                    summary=f"{theme_node['label']} 影响 {stock_node['label']}",
                    evidence_count=int(theme_node.get("metrics", {}).get("stock_count") or 0),
                )
            )

    detail = {
        "why": f"当前行业 {industry_name} 在最新评分日的平均分为 {_as_float(center_row.get('avg_score')):.1f}，样本 {center_row.get('stock_count') or 0} 只",
        "next_steps": [
            {"label": "打开股票评分", "to": _industry_target(industry_name)},
            {"label": "打开股票列表", "to": f"/stocks/list?keyword={industry_name}"},
        ],
        "themes": [item["label"] for item in visible_theme_nodes[:5]],
    }
    summary = {
        "node_count": len(nodes),
        "edge_count": len(edges),
        "theme_count": len(visible_theme_nodes),
        "industry_count": 1,
        "stock_count": len(visible_stock_nodes),
        "depth": depth,
        "latest_score_date": latest_score_date,
        "center_type": "industry",
        "center_label": industry_name,
    }
    return {
        "center_type": "industry",
        "center_key": industry_name,
        "center_label": industry_name,
        "center": center_node,
        "detail": detail,
        "nodes": nodes,
        "edges": edges,
        "summary": summary,
        "legend": [
            {"type": "industry", "label": "行业"},
            {"type": "theme", "label": "主题"},
            {"type": "stock", "label": "股票"},
            {"relation_key": "industry_theme", "label": "行业→主题"},
            {"relation_key": "industry_stock", "label": "行业→股票"},
            {"relation_key": "theme_stock", "label": "主题→股票"},
        ],
    }


def query_signal_chain_graph(
    *,
    sqlite3_module,
    db_path,
    center_type: str = "theme",
    center_key: str = "",
    depth: int = 2,
    limit: int = 12,
) -> dict[str, Any]:
    normalized_center_type = _normalize_center_type(center_type)
    normalized_center_key = str(center_key or "").strip()
    depth = max(1, min(int(depth or 2), 3))
    limit = max(3, min(int(limit or 12), 30))
    conn = sqlite3_module.connect(db_path)
    conn.row_factory = sqlite3_module.Row
    try:
        if normalized_center_type == "industry":
            payload = _build_industry_graph(conn, center_key=normalized_center_key, depth=depth, limit=limit)
        else:
            payload = _build_theme_graph(conn, center_key=normalized_center_key, depth=depth, limit=limit)
        payload["requested_center_type"] = normalized_center_type
        payload["requested_center_key"] = normalized_center_key
        payload["requested_depth"] = depth
        payload["requested_limit"] = limit
        return payload
    finally:
        conn.close()
