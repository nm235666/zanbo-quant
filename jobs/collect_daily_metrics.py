#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import db_compat as sqlite3

WEB_DIR = ROOT_DIR / "apps" / "web"
METRICS_DAILY_DIR = ROOT_DIR / "docs" / "metrics" / "daily"
DEFAULT_DB_PATH = ROOT_DIR / "stock_codes.db"
CN_TZ = timezone(timedelta(hours=8))
CLOSURE_ACTIONS = {"confirm", "reject", "defer", "review"}

# Metric gate thresholds — falling below these triggers a non-zero exit (blocking gate)
GATE_PIPELINE_SUCCESS_RATE_MIN = 0.85   # E2E smoke must pass >= 85%
GATE_TRACEABILITY_RATE_MIN = 0.70       # >= 70% decision records must have evidence trace
GATE_CLOSURE_RATE_MIN = 0.50            # >= 50% decisions must reach a closure state


def _cn_today_str() -> str:
    return datetime.now(timezone.utc).astimezone(CN_TZ).date().isoformat()


def _parse_target_date(value: str) -> date:
    text = str(value or "").strip()
    if not text:
        return date.fromisoformat(_cn_today_str())
    return date.fromisoformat(text)


def _utc_iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _cn_day_utc_window(target_date: date) -> tuple[str, str]:
    start_cn = datetime.combine(target_date, time.min, tzinfo=CN_TZ)
    end_cn = start_cn + timedelta(days=1)
    return _utc_iso(start_cn), _utc_iso(end_cn)


def _extract_json_from_stdout(stdout_text: str) -> dict[str, Any] | None:
    text = str(stdout_text or "").strip()
    if not text:
        return None
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return parsed
    except Exception:
        pass
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        try:
            parsed = json.loads(text[start : end + 1])
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            return None
    return None


def _parse_playwright_report(report: dict[str, Any]) -> tuple[int, int]:
    stats = report.get("stats") if isinstance(report, dict) else None
    if isinstance(stats, dict):
        passed = int(stats.get("expected") or 0) + int(stats.get("flaky") or 0)
        failed = int(stats.get("unexpected") or 0)
        if passed + failed > 0:
            return passed, failed

    passed = 0
    failed = 0

    def walk(node: Any) -> None:
        nonlocal passed, failed
        if isinstance(node, dict):
            tests = node.get("tests")
            if isinstance(tests, list):
                for test_item in tests:
                    if not isinstance(test_item, dict):
                        continue
                    outcome = str(test_item.get("outcome") or "").strip().lower()
                    if outcome in {"expected", "flaky"}:
                        passed += 1
                    elif outcome in {"unexpected", "timedout", "interrupted"}:
                        failed += 1
            for child in node.values():
                walk(child)
        elif isinstance(node, list):
            for child in node:
                walk(child)

    walk(report)
    return passed, failed


def _run_smoke_once() -> tuple[dict[str, Any] | None, str | None, str | None]:
    if not WEB_DIR.exists():
        return None, None, "apps/web 目录不存在，无法运行 smoke"

    cmd = [
        "npx",
        "playwright",
        "test",
        "--config",
        "./playwright.smoke.config.ts",
        "--reporter=json",
    ]
    try:
        completed = subprocess.run(
            cmd,
            cwd=str(WEB_DIR),
            capture_output=True,
            text=True,
            timeout=1800,
            check=False,
        )
    except FileNotFoundError:
        return None, None, "npx 不可用，无法运行 smoke"
    except subprocess.TimeoutExpired:
        return None, None, "smoke 执行超时（1800s）"
    except Exception as exc:
        return None, None, f"smoke 执行异常: {exc}"

    payload = _extract_json_from_stdout(completed.stdout)
    if payload is None:
        stderr = str(completed.stderr or "").strip()
        return None, None, f"smoke 输出无法解析为 JSON，exit_code={completed.returncode}, stderr={stderr[:300]}"

    out_path = METRICS_DAILY_DIR / "_latest_smoke_report.json"
    try:
        out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass

    if completed.returncode != 0:
        return payload, str(out_path), f"smoke exit_code={completed.returncode}，已使用报告继续计算"
    return payload, str(out_path), None


def _load_smoke_report(allow_smoke_run: bool) -> tuple[int | None, int | None, str | None, list[str]]:
    notes: list[str] = []
    candidates = [
        WEB_DIR / "playwright-report" / "report.json",
        WEB_DIR / "playwright-report.json",
        ROOT_DIR / "playwright-report" / "report.json",
        ROOT_DIR / "playwright-report.json",
        METRICS_DAILY_DIR / "_latest_smoke_report.json",
    ]

    for path in candidates:
        if not path.exists() or not path.is_file():
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            passed, failed = _parse_playwright_report(payload)
            return passed, failed, str(path), notes
        except Exception as exc:
            notes.append(f"读取 smoke 报告失败({path}): {exc}")

    if not allow_smoke_run:
        notes.append("未找到 smoke JSON 报告，且已关闭临时 smoke 执行")
        return None, None, None, notes

    payload, report_path, err = _run_smoke_once()
    if err:
        notes.append(err)
    if isinstance(payload, dict):
        passed, failed = _parse_playwright_report(payload)
        return passed, failed, report_path, notes
    notes.append("未能获取 smoke JSON 报告，pipeline_success_rate 置为 null")
    return None, None, report_path, notes


def _safe_rate(numerator: int, denominator: int) -> float | None:
    if denominator <= 0:
        return None
    return round((float(numerator) / float(denominator)) * 100.0, 4)


def _load_json_object(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    if value is None:
        return {}
    text = str(value).strip()
    if not text:
        return {}
    try:
        parsed = json.loads(text)
        return parsed if isinstance(parsed, dict) else {}
    except Exception:
        return {}


def _collect_decision_metrics(target_date: date) -> tuple[dict[str, Any], list[str]]:
    start_utc_iso, end_utc_iso = _cn_day_utc_window(target_date)
    notes: list[str] = []
    conn = sqlite3.connect(DEFAULT_DB_PATH)
    try:
        rows = conn.execute(
            """
            SELECT id, action_type, ts_code, created_at, action_payload_json
            FROM decision_actions
            WHERE created_at >= ? AND created_at < ?
            ORDER BY created_at DESC, id DESC
            """,
            (start_utc_iso, end_utc_iso),
        ).fetchall()
    except Exception as exc:
        notes.append(f"decision_actions 查询失败: {exc}")
        rows = []
    finally:
        conn.close()

    total = len(rows)
    traceable = 0
    closure = 0

    for row in rows:
        row_id = row[0]
        action_type = str(row[1] or "").strip().lower()
        ts_code = str(row[2] or "").strip().upper()
        created_at = str(row[3] or "").strip()
        payload = _load_json_object(row[4])
        has_context = bool(payload.get("context"))

        if row_id and action_type and ts_code and created_at:
            traceable += 1
        if action_type in CLOSURE_ACTIONS and has_context:
            closure += 1

    sample_insufficient = total < 20
    traceability_rate = _safe_rate(traceable, total)
    closure_rate = _safe_rate(closure, total)

    return {
        "decision_total_records": total,
        "traceable_records": traceable,
        "closure_records": closure,
        "traceability_rate": traceability_rate,
        "closure_rate": closure_rate,
        "sample_insufficient": sample_insufficient,
    }, notes


def _build_markdown(payload: dict[str, Any]) -> str:
    date_text = str(payload.get("date") or "")
    generated_at = str(payload.get("generated_at") or "")
    pipeline_rate = payload.get("pipeline_success_rate")
    traceability_rate = payload.get("traceability_rate")
    closure_rate = payload.get("closure_rate")
    sample_insufficient = bool(payload.get("sample_insufficient"))
    pipeline_passed = payload.get("pipeline_passed")
    pipeline_failed = payload.get("pipeline_failed")
    decision_total = payload.get("decision_total_records")
    traceable = payload.get("traceable_records")
    closure = payload.get("closure_records")

    notes = payload.get("notes") or []
    note_lines = "\n".join([f"- {str(item)}" for item in notes]) if notes else "- 无"

    return (
        f"# Daily Metrics {date_text}\n\n"
        f"- generated_at: `{generated_at}`\n"
        f"- sample_insufficient: `{str(sample_insufficient).lower()}`\n\n"
        "## Summary\n\n"
        "| Metric | Value | Detail |\n"
        "|---|---:|---|\n"
        f"| Pipeline Success Rate | {pipeline_rate if pipeline_rate is not None else 'null'} | passed={pipeline_passed}, failed={pipeline_failed} |\n"
        f"| Traceability Rate | {traceability_rate if traceability_rate is not None else 'null'} | traceable={traceable}, total={decision_total} |\n"
        f"| Closure Rate | {closure_rate if closure_rate is not None else 'null'} | closure={closure}, total={decision_total} |\n\n"
        "## Notes\n\n"
        f"{note_lines}\n"
    )


def collect_daily_metrics(*, target_date: date, allow_smoke_run: bool = True) -> dict[str, Any]:
    METRICS_DAILY_DIR.mkdir(parents=True, exist_ok=True)

    pipeline_passed, pipeline_failed, report_path, smoke_notes = _load_smoke_report(allow_smoke_run=allow_smoke_run)
    decision_metrics, decision_notes = _collect_decision_metrics(target_date)

    pipeline_total: int | None = None
    pipeline_success_rate: float | None = None
    if pipeline_passed is not None and pipeline_failed is not None:
        pipeline_total = pipeline_passed + pipeline_failed
        pipeline_success_rate = _safe_rate(pipeline_passed, pipeline_total)

    payload: dict[str, Any] = {
        "date": target_date.isoformat(),
        "generated_at": _utc_iso(datetime.now(timezone.utc)),
        "pipeline_success_rate": pipeline_success_rate,
        "pipeline_passed": pipeline_passed,
        "pipeline_failed": pipeline_failed,
        "pipeline_total": pipeline_total,
        "pipeline_report_path": report_path,
        "traceability_rate": decision_metrics["traceability_rate"],
        "traceable_records": decision_metrics["traceable_records"],
        "closure_rate": decision_metrics["closure_rate"],
        "closure_records": decision_metrics["closure_records"],
        "decision_total_records": decision_metrics["decision_total_records"],
        "sample_insufficient": bool(decision_metrics["sample_insufficient"]),
        "notes": [*smoke_notes, *decision_notes],
    }

    json_path = METRICS_DAILY_DIR / f"{target_date.isoformat()}.json"
    md_path = METRICS_DAILY_DIR / f"{target_date.isoformat()}.md"

    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(_build_markdown(payload), encoding="utf-8")

    return {
        "ok": True,
        "date": target_date.isoformat(),
        "json_path": str(json_path),
        "md_path": str(md_path),
        "pipeline_success_rate": pipeline_success_rate,
        "traceability_rate": payload["traceability_rate"],
        "closure_rate": payload["closure_rate"],
        "sample_insufficient": payload["sample_insufficient"],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect daily system metrics and write docs/metrics artifacts")
    parser.add_argument("--date", default="", help="Target CN date, format YYYY-MM-DD (default: today CN)")
    parser.add_argument(
        "--skip-smoke-run",
        action="store_true",
        help="Do not trigger temporary smoke run when JSON report is missing",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    target_date = _parse_target_date(args.date)
    result = collect_daily_metrics(target_date=target_date, allow_smoke_run=not bool(args.skip_smoke_run))
    print(json.dumps(result, ensure_ascii=False))

    if not result.get("ok"):
        return 1

    # Gate check — sample_insufficient means we skip threshold enforcement
    if result.get("sample_insufficient"):
        return 0

    gate_failures: list[str] = []
    pipeline_rate = result.get("pipeline_success_rate")
    traceability_rate = result.get("traceability_rate")
    closure_rate = result.get("closure_rate")

    if pipeline_rate is not None and pipeline_rate < GATE_PIPELINE_SUCCESS_RATE_MIN:
        gate_failures.append(
            f"pipeline_success_rate {pipeline_rate:.2%} < threshold {GATE_PIPELINE_SUCCESS_RATE_MIN:.0%}"
        )
    if traceability_rate is not None and traceability_rate < GATE_TRACEABILITY_RATE_MIN:
        gate_failures.append(
            f"traceability_rate {traceability_rate:.2%} < threshold {GATE_TRACEABILITY_RATE_MIN:.0%}"
        )
    if closure_rate is not None and closure_rate < GATE_CLOSURE_RATE_MIN:
        gate_failures.append(
            f"closure_rate {closure_rate:.2%} < threshold {GATE_CLOSURE_RATE_MIN:.0%}"
        )

    if gate_failures:
        print(
            json.dumps(
                {"gate": "FAIL", "failures": gate_failures},
                ensure_ascii=False,
            )
        )
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
