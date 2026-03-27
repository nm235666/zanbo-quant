#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import re
import db_compat as sqlite3
from pathlib import Path


JSON_COLUMNS = [
    "holder_structure_json",
    "board_structure_json",
    "mgmt_change_json",
    "incentive_plan_json",
]
BAD_TOKEN_RE = re.compile(r'(?<![A-Za-z0-9_"])(-?Infinity|NaN)(?![A-Za-z0-9_"])')


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="清洗 company_governance 中包含 NaN/Infinity 的 JSON 字段")
    parser.add_argument(
        "--db-path",
        default=str(Path(__file__).resolve().parent / "stock_codes.db"),
        help="PostgreSQL 主库兼容参数（默认走 PostgreSQL；仅兼容保留旧 db-path 传参）",
    )
    parser.add_argument("--dry-run", action="store_true", help="仅扫描，不落库")
    return parser.parse_args()


def sanitize_json_value(value):
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return None
        return value
    if isinstance(value, dict):
        return {str(k): sanitize_json_value(v) for k, v in value.items()}
    if isinstance(value, list):
        return [sanitize_json_value(v) for v in value]
    if isinstance(value, tuple):
        return [sanitize_json_value(v) for v in value]
    return value


def clean_json_text(raw: str):
    if raw is None:
        return None, False
    text = str(raw)
    if not BAD_TOKEN_RE.search(text):
        return text, False
    obj = json.loads(text)
    clean_obj = sanitize_json_value(obj)
    clean_text = json.dumps(clean_obj, ensure_ascii=False, allow_nan=False, separators=(",", ":"))
    return clean_text, clean_text != text


def main() -> int:
    args = parse_args()
    db_path = Path(args.db_path).resolve()
    if (not sqlite3.using_postgres()) and not db_path.exists():
        print(f"数据库不存在: {db_path}")
        return 1

    conn = sqlite3.connect(db_path)
    try:
        cols = {r[1] for r in conn.execute("PRAGMA table_info(company_governance)").fetchall()}
        missing = [c for c in JSON_COLUMNS if c not in cols]
        if missing:
            print(f"缺少列: {', '.join(missing)}")
            return 2

        rows = conn.execute(
            """
            SELECT ts_code, asof_date, holder_structure_json, board_structure_json, mgmt_change_json, incentive_plan_json
            FROM company_governance
            """
        ).fetchall()

        changed_rows = 0
        changed_fields = 0
        scanned_fields = 0

        for row in rows:
            ts_code = row[0]
            asof_date = row[1]
            updates = {}
            for idx, col in enumerate(JSON_COLUMNS, start=2):
                scanned_fields += 1
                clean_text, changed = clean_json_text(row[idx])
                if changed:
                    updates[col] = clean_text
                    changed_fields += 1
            if not updates:
                continue
            changed_rows += 1
            if args.dry_run:
                print(f"[DRY-RUN] {ts_code} {asof_date} -> {', '.join(updates.keys())}")
                continue
            set_sql = ", ".join([f"{col} = ?" for col in updates.keys()])
            params = list(updates.values()) + [ts_code, asof_date]
            conn.execute(
                f"""
                UPDATE company_governance
                SET {set_sql}
                WHERE ts_code = ? AND asof_date = ?
                """,
                params,
            )

        if not args.dry_run:
            conn.commit()

        print(f"扫描字段数: {scanned_fields}")
        print(f"变更行数: {changed_rows}")
        print(f"变更字段数: {changed_fields}")
        print("非法 token 规则: NaN / Infinity / -Infinity（排除普通文本误伤）")
        print(f"模式: {'DRY-RUN' if args.dry_run else 'WRITE'}")
    finally:
        conn.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
