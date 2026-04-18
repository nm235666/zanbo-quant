#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import db_compat as sqlite3


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="导入 external/strategy 内容到 research_reports 作为研报数据源")
    parser.add_argument("--repo-dir", default="external/strategy", help="策略仓库目录")
    parser.add_argument("--db-path", default="stock_codes.db", help="数据库路径（db_compat 兼容）")
    parser.add_argument("--report-type", default="strategy_repo", help="写入 report_type")
    parser.add_argument("--model", default="strategy_repo_sync_v1", help="写入 model 字段")
    parser.add_argument("--max-files", type=int, default=5000, help="最多导入文件数")
    parser.add_argument(
        "--include-prefixes",
        default="港A美/机构日报,港A美/私人精选",
        help="仅导入这些相对路径前缀（逗号分隔）；留空表示全仓库扫描",
    )
    parser.add_argument("--error-sample-limit", type=int, default=20, help="输出失败样例数量")
    parser.add_argument("--dry-run", action="store_true", help="仅扫描不写入")
    return parser.parse_args()


def iso_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def detect_report_date(path: Path, content: str) -> str:
    # 1) filename / path contains date
    m = re.search(r"(20\d{2})[-_]?([01]?\d)[-_]?([0-3]?\d)", str(path))
    if m:
        mm = m.group(2).zfill(2)
        dd = m.group(3).zfill(2)
        return f"{m.group(1)}-{mm}-{dd}"
    # 2) first lines contain date
    head = "\n".join(content.splitlines()[:30])
    m = re.search(r"(20\d{2})[-/\.]([01]?\d)[-/\.]([0-3]?\d)", head)
    if m:
        mm = m.group(2).zfill(2)
        dd = m.group(3).zfill(2)
        return f"{m.group(1)}-{mm}-{dd}"
    # 3) fallback: file mtime date
    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).strftime("%Y-%m-%d")


def extract_title(path: Path, content: str) -> str:
    for line in content.splitlines()[:40]:
        s = line.strip()
        if s.startswith("#"):
            return s.lstrip("#").strip()[:120] or path.stem
    return path.stem


def _parse_prefixes(raw: str) -> list[str]:
    return [x.strip().strip("/") for x in str(raw or "").split(",") if x.strip().strip("/")]


def iter_report_files(repo_dir: Path, max_files: int, include_prefixes: list[str]):
    exts = {".md", ".markdown", ".txt", ".rst"}
    count = 0
    for p in repo_dir.rglob("*"):
        if not p.is_file():
            continue
        if ".git" in p.parts:
            continue
        if p.suffix.lower() not in exts:
            continue
        rel = p.relative_to(repo_dir).as_posix()
        if include_prefixes and not any(rel.startswith(prefix + "/") or rel == prefix for prefix in include_prefixes):
            continue
        count += 1
        if count > max_files:
            break
        yield p


def ensure_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS research_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            report_date TEXT,
            report_type TEXT,
            subject_key TEXT,
            subject_name TEXT,
            model TEXT,
            markdown_content TEXT,
            context_json TEXT,
            created_at TEXT,
            update_time TEXT
        )
        """
    )


def upsert_report(
    conn: sqlite3.Connection,
    *,
    report_date: str,
    report_type: str,
    subject_key: str,
    subject_name: str,
    model: str,
    markdown_content: str,
    context_json: str,
    now: str,
) -> str:
    row = conn.execute(
        """
        SELECT id, markdown_content
        FROM research_reports
        WHERE report_type = ? AND subject_key = ? AND report_date = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (report_type, subject_key, report_date),
    ).fetchone()
    if row:
        old = str(row[1] or "")
        if old == markdown_content:
            return "unchanged"
        conn.execute(
            """
            UPDATE research_reports
            SET subject_name = ?, model = ?, markdown_content = ?, context_json = ?, update_time = ?
            WHERE id = ?
            """,
            (subject_name, model, markdown_content, context_json, now, int(row[0])),
        )
        return "updated"

    conn.execute(
        """
        INSERT INTO research_reports (
            report_date, report_type, subject_key, subject_name, model, markdown_content, context_json, created_at, update_time
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (report_date, report_type, subject_key, subject_name, model, markdown_content, context_json, now, now),
    )
    return "inserted"


def main() -> int:
    args = parse_args()
    repo_dir = Path(args.repo_dir).resolve()
    if not repo_dir.exists() or not (repo_dir / ".git").exists():
        print(f"[strategy-import] repo not found or not git repo: {repo_dir}")
        print("[strategy-import] 请先执行: bash scripts/sync_strategy_repo.sh")
        return 2

    conn = sqlite3.connect(str(Path(args.db_path).resolve()))
    now = iso_now()
    inserted = 0
    updated = 0
    unchanged = 0
    failed = 0
    scanned = 0
    skipped_short = 0
    errors: list[dict[str, str]] = []
    include_prefixes = _parse_prefixes(args.include_prefixes)

    try:
        ensure_table(conn)
        for path in iter_report_files(repo_dir, args.max_files, include_prefixes):
            scanned += 1
            try:
                content = path.read_text(encoding="utf-8", errors="ignore").strip()
                if len(content) < 60:
                    skipped_short += 1
                    continue
                rel = path.relative_to(repo_dir).as_posix()
                title = extract_title(path, content)
                report_date = detect_report_date(path, content)
                digest = hashlib.sha1(content.encode("utf-8", errors="ignore")).hexdigest()
                subject_key = f"strategy_repo:{rel}"
                context = {
                    "repo": "WealthCodePro/Strategy",
                    "repo_rel_path": rel,
                    "content_sha1": digest,
                    "source": "strategy_repo_sync",
                }
                if args.dry_run:
                    continue
                status = upsert_report(
                    conn,
                    report_date=report_date,
                    report_type=args.report_type,
                    subject_key=subject_key,
                    subject_name=title,
                    model=args.model,
                    markdown_content=content,
                    context_json=json.dumps(context, ensure_ascii=False),
                    now=now,
                )
                if status == "inserted":
                    inserted += 1
                elif status == "updated":
                    updated += 1
                else:
                    unchanged += 1
            except Exception as exc:
                failed += 1
                if len(errors) < args.error_sample_limit:
                    errors.append(
                        {
                            "file": str(path.relative_to(repo_dir).as_posix()),
                            "error": f"{type(exc).__name__}: {exc}",
                        }
                    )

        if not args.dry_run:
            conn.commit()
    finally:
        conn.close()

    print(
        f"[strategy-import] scanned={scanned} inserted={inserted} updated={updated} "
        f"unchanged={unchanged} skipped_short={skipped_short} failed={failed} "
        f"prefixes={','.join(include_prefixes) if include_prefixes else '<all>'} dry_run={args.dry_run}"
    )
    if errors:
        print("[strategy-import] error_samples:")
        for item in errors:
            print(f"  - {item['file']} :: {item['error']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
