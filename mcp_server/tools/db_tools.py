from __future__ import annotations

import re
from typing import Any

import db_compat as db
from mcp_server import schemas

from .common import READONLY_ALLOWED_TABLES, SENSITIVE_COLUMNS, db_counts, row_to_dict, rows_to_dicts, table_safe


def table_counts(args: schemas.TableCountsArgs) -> dict[str, Any]:
    tables = args.tables or sorted(READONLY_ALLOWED_TABLES)
    return {"ok": True, "tables": db_counts(tables)}


def _extract_tables(sql: str) -> set[str]:
    return {
        match.group(2)
        for match in re.finditer(r"(?is)\b(from|join)\s+([A-Za-z_][A-Za-z0-9_]*)\b", sql)
    }


def _validate_readonly_sql(sql: str, limit: int) -> str:
    text = str(sql or "").strip()
    if not text:
        raise ValueError("sql_required")
    if ";" in text.rstrip(";"):
        raise ValueError("multi_statement_blocked")
    text = text.rstrip(";").strip()
    if not re.match(r"(?is)^select\b", text):
        raise ValueError("only_select_allowed")
    lowered = re.sub(r"\s+", " ", text.lower())
    blocked = (" insert ", " update ", " delete ", " drop ", " alter ", " create ", " truncate ", " grant ", " revoke ")
    padded = f" {lowered} "
    if any(token in padded for token in blocked):
        raise ValueError("mutating_sql_blocked")
    for column in SENSITIVE_COLUMNS:
        if re.search(rf"(?is)\b{re.escape(column)}\b", text):
            raise ValueError(f"sensitive_column_blocked:{column}")
    tables = _extract_tables(text)
    if not tables:
        raise ValueError("table_reference_required")
    for table in tables:
        table_safe(table)
        if table not in READONLY_ALLOWED_TABLES:
            raise ValueError(f"table_not_allowlisted:{table}")
    if not re.search(r"(?is)\blimit\s+\d+\b", text):
        text = f"{text} LIMIT {limit}"
    else:
        text = re.sub(r"(?is)\blimit\s+\d+\b", f"LIMIT {limit}", text)
    return text


def readonly_query(args: schemas.ReadonlyQueryArgs) -> dict[str, Any]:
    limit = max(1, min(int(args.limit or 100), 500))
    sql = _validate_readonly_sql(args.sql, limit)
    conn = db.connect()
    db.apply_row_factory(conn)
    try:
        cur = conn.execute(sql, tuple(args.params or ()))
        rows = cur.fetchall()
        columns = [col[0] for col in (cur.description or [])]
        return {
            "ok": True,
            "sql": sql,
            "columns": columns,
            "items": rows_to_dicts(rows) if columns else [row_to_dict(r) for r in rows],
            "total": len(rows),
            "limit": limit,
        }
    finally:
        conn.close()

