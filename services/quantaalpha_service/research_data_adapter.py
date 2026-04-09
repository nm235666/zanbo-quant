from __future__ import annotations

import math
import os
import time
from dataclasses import dataclass
from typing import Any

DATA_ADAPTER_VERSION = "self_qlib_equiv_v1"
FACTOR_EXPR_VERSION = "alpha158_20_equiv_v1"
DEFAULT_UNIVERSE_MAX_SYMBOLS = max(300, int(os.getenv("FACTOR_RESEARCH_UNIVERSE_MAX_SYMBOLS", "1800") or "1800"))
DEFAULT_PIPELINE_TIMEOUT_SECONDS = max(30, int(os.getenv("FACTOR_RESEARCH_PIPELINE_TIMEOUT_SECONDS", "180") or "180"))


@dataclass
class FactorSpec:
    name: str
    expression: str
    required_window: int


def _safe_div(num: float, den: float) -> float:
    if abs(den) <= 1e-12:
        return 0.0
    return num / den


def _pearson_corr(x: list[float], y: list[float]) -> float:
    if len(x) < 3 or len(x) != len(y):
        return 0.0
    mx = sum(x) / len(x)
    my = sum(y) / len(y)
    num = sum((a - mx) * (b - my) for a, b in zip(x, y))
    den_x = math.sqrt(sum((a - mx) ** 2 for a in x))
    den_y = math.sqrt(sum((b - my) ** 2 for b in y))
    den = den_x * den_y
    return _safe_div(num, den) if den > 0 else 0.0


def _rank(values: list[float]) -> list[float]:
    indexed = sorted(enumerate(values), key=lambda item: item[1])
    out = [0.0] * len(values)
    i = 0
    while i < len(indexed):
        j = i + 1
        while j < len(indexed) and indexed[j][1] == indexed[i][1]:
            j += 1
        avg = (i + j - 1) / 2.0 + 1.0
        for k in range(i, j):
            out[indexed[k][0]] = avg
        i = j
    return out


def _spearman_corr(x: list[float], y: list[float]) -> float:
    return _pearson_corr(_rank(x), _rank(y))


def _window(series: list[float | None], end_idx: int, n: int) -> list[float]:
    start = max(0, end_idx - n + 1)
    out = [v for v in series[start : end_idx + 1] if v is not None]
    return out


def _val(series: list[float | None], idx: int) -> float | None:
    if idx < 0 or idx >= len(series):
        return None
    return series[idx]


def _ts_mean(series: list[float | None], end_idx: int, n: int) -> float | None:
    values = _window(series, end_idx, n)
    if len(values) < max(3, int(n * 0.6)):
        return None
    return sum(values) / len(values)


def _ts_std(series: list[float | None], end_idx: int, n: int) -> float | None:
    values = _window(series, end_idx, n)
    if len(values) < max(3, int(n * 0.6)):
        return None
    m = sum(values) / len(values)
    v = sum((x - m) ** 2 for x in values) / len(values)
    return math.sqrt(max(0.0, v))


def _ts_min(series: list[float | None], end_idx: int, n: int) -> float | None:
    values = _window(series, end_idx, n)
    if len(values) < max(3, int(n * 0.6)):
        return None
    return min(values)


def _ts_max(series: list[float | None], end_idx: int, n: int) -> float | None:
    values = _window(series, end_idx, n)
    if len(values) < max(3, int(n * 0.6)):
        return None
    return max(values)


def _ts_delta(series: list[float | None], end_idx: int, n: int) -> float | None:
    now = _val(series, end_idx)
    prev = _val(series, end_idx - n)
    if now is None or prev is None:
        return None
    return now - prev


def _ts_rank(series: list[float | None], end_idx: int, n: int) -> float | None:
    values = _window(series, end_idx, n)
    last = _val(series, end_idx)
    if len(values) < max(3, int(n * 0.6)) or last is None:
        return None
    sorted_vals = sorted(values)
    pos = 0
    for idx, val in enumerate(sorted_vals):
        if val <= last:
            pos = idx + 1
    return _safe_div(float(pos), float(len(sorted_vals)))


def _ts_corr(a: list[float | None], b: list[float | None], end_idx: int, n: int) -> float | None:
    start = max(0, end_idx - n + 1)
    x: list[float] = []
    y: list[float] = []
    for i in range(start, end_idx + 1):
        av = _val(a, i)
        bv = _val(b, i)
        if av is None or bv is None:
            continue
        x.append(av)
        y.append(bv)
    if len(x) < max(3, int(n * 0.6)):
        return None
    return _pearson_corr(x, y)


def alpha158_20_equivalent_specs() -> list[FactorSpec]:
    return [
        FactorSpec("alpha158_20_01", "ts_mean(returns,5)", 6),
        FactorSpec("alpha158_20_02", "ts_std(returns,10)", 12),
        FactorSpec("alpha158_20_03", "ts_rank(close,20)", 22),
        FactorSpec("alpha158_20_04", "(close-delay(close,5))/delay(close,5)", 8),
        FactorSpec("alpha158_20_05", "ts_corr(returns,vol_delta,10)", 14),
        FactorSpec("alpha158_20_06", "ts_mean((high-low)/close,10)", 12),
        FactorSpec("alpha158_20_07", "ts_delta(vol,5)/ts_mean(vol,20)", 24),
        FactorSpec("alpha158_20_08", "(close-open)/open", 3),
        FactorSpec("alpha158_20_09", "ts_mean(amount,5)/ts_mean(amount,20)-1", 24),
        FactorSpec("alpha158_20_10", "ts_std((high-low)/close,20)", 24),
        FactorSpec("alpha158_20_11", "ts_rank(amount,20)", 24),
        FactorSpec("alpha158_20_12", "ts_corr(close,vol,20)", 24),
        FactorSpec("alpha158_20_13", "ts_mean(returns,20)", 24),
        FactorSpec("alpha158_20_14", "ts_rank(returns,10)", 14),
        FactorSpec("alpha158_20_15", "ts_delta(close,1)", 4),
        FactorSpec("alpha158_20_16", "ts_mean((close-low)/(high-low),10)", 12),
        FactorSpec("alpha158_20_17", "ts_max(high,20)/close-1", 24),
        FactorSpec("alpha158_20_18", "close/ts_min(low,20)-1", 24),
        FactorSpec("alpha158_20_19", "ts_corr(returns,amount,20)", 24),
        FactorSpec("alpha158_20_20", "ts_std(returns,5)/ts_std(returns,20)", 24),
    ]


def _load_market_panel(conn, lookback: int, universe_limit: int) -> tuple[dict[str, Any] | None, str]:
    window = max(40, min(int(lookback or 120) + 40, 360))
    rows = conn.execute(
        """
        SELECT trade_date
        FROM stock_daily_prices
        GROUP BY trade_date
        ORDER BY trade_date DESC
        LIMIT ?
        """,
        (window,),
    ).fetchall()
    trade_dates_desc = [str(item[0]) for item in rows if item and item[0]]
    if len(trade_dates_desc) < 25:
        return None, "insufficient_trade_dates"
    trade_dates = list(reversed(trade_dates_desc))
    min_date = trade_dates[0]
    as_of_date = trade_dates[-1]
    date_index = {d: i for i, d in enumerate(trade_dates)}
    raw_rows = conn.execute(
        """
        SELECT ts_code, trade_date, open, high, low, close, vol, amount, pct_chg
        FROM stock_daily_prices
        WHERE trade_date >= ?
        ORDER BY ts_code ASC, trade_date ASC
        """,
        (min_date,),
    ).fetchall()
    if not raw_rows:
        return None, "price_rows_empty"

    symbols: dict[str, dict[str, list[float | None]]] = {}
    for row in raw_rows:
        ts_code = str(row[0] or "").strip()
        trade_date = str(row[1] or "").strip()
        idx = date_index.get(trade_date)
        if not ts_code or idx is None:
            continue
        node = symbols.setdefault(
            ts_code,
            {
                "open": [None] * len(trade_dates),
                "high": [None] * len(trade_dates),
                "low": [None] * len(trade_dates),
                "close": [None] * len(trade_dates),
                "vol": [None] * len(trade_dates),
                "amount": [None] * len(trade_dates),
                "returns": [None] * len(trade_dates),
            },
        )
        node["open"][idx] = float(row[2]) if row[2] is not None else None
        node["high"][idx] = float(row[3]) if row[3] is not None else None
        node["low"][idx] = float(row[4]) if row[4] is not None else None
        node["close"][idx] = float(row[5]) if row[5] is not None else None
        node["vol"][idx] = float(row[6]) if row[6] is not None else None
        node["amount"][idx] = float(row[7]) if row[7] is not None else None
        if row[8] is not None:
            node["returns"][idx] = float(row[8]) / 100.0

    filtered: dict[str, dict[str, list[float | None]]] = {}
    for symbol, panel in symbols.items():
        close = panel["close"]
        for i in range(1, len(trade_dates)):
            if panel["returns"][i] is None:
                c = close[i]
                p = close[i - 1]
                if c is not None and p is not None and abs(p) > 1e-12:
                    panel["returns"][i] = c / p - 1.0
        if panel["close"][-1] is None or panel["returns"][-1] is None:
            continue
        points = sum(1 for v in panel["close"] if v is not None)
        if points < max(25, int(lookback * 0.5)):
            continue
        filtered[symbol] = panel

    if len(filtered) < 200:
        return None, "insufficient_symbol_coverage"

    if universe_limit > 0 and len(filtered) > universe_limit:
        ranking: list[tuple[str, float]] = []
        for symbol, panel in filtered.items():
            amount = panel["amount"]
            close = panel["close"]
            valid_amount = [v for v in amount[-20:] if v is not None]
            valid_close = [v for v in close[-20:] if v is not None]
            if not valid_amount or not valid_close:
                continue
            liquidity_score = (sum(valid_amount) / len(valid_amount)) * (sum(valid_close) / len(valid_close))
            ranking.append((symbol, float(liquidity_score)))
        ranking.sort(key=lambda item: item[1], reverse=True)
        chosen = set(sym for sym, _ in ranking[:universe_limit])
        filtered = {k: v for k, v in filtered.items() if k in chosen}

    validation = {
        "trade_days": len(trade_dates),
        "symbol_count": len(filtered),
        "universe_limit": universe_limit,
        "as_of_date": as_of_date,
        "missing_close_ratio": round(
            _safe_div(
                sum(sum(1 for v in panel["close"] if v is None) for panel in filtered.values()),
                len(filtered) * len(trade_dates),
            ),
            6,
        ),
    }
    return {
        "trade_dates": trade_dates,
        "as_of_idx": len(trade_dates) - 1,
        "as_of_date": as_of_date,
        "symbols": filtered,
        "validation": validation,
    }, "ok"


def _factor_value(spec: FactorSpec, panel: dict[str, list[float | None]], end_idx: int) -> float | None:
    open_s = panel["open"]
    high_s = panel["high"]
    low_s = panel["low"]
    close_s = panel["close"]
    vol_s = panel["vol"]
    amount_s = panel["amount"]
    ret_s = panel["returns"]
    close_now = _val(close_s, end_idx)
    if close_now is None:
        return None
    vol_delta = [None] * len(vol_s)
    for i in range(len(vol_s)):
        v = _val(vol_s, i)
        p = _val(vol_s, i - 1)
        if v is not None and p is not None and abs(p) > 1e-12:
            vol_delta[i] = v / p - 1.0
    if spec.name == "alpha158_20_01":
        return _ts_mean(ret_s, end_idx, 5)
    if spec.name == "alpha158_20_02":
        return _ts_std(ret_s, end_idx, 10)
    if spec.name == "alpha158_20_03":
        return _ts_rank(close_s, end_idx, 20)
    if spec.name == "alpha158_20_04":
        prev = _val(close_s, end_idx - 5)
        return None if prev is None else _safe_div(close_now - prev, abs(prev))
    if spec.name == "alpha158_20_05":
        return _ts_corr(ret_s, vol_delta, end_idx, 10)
    if spec.name == "alpha158_20_06":
        x = [None] * len(close_s)
        for i in range(len(close_s)):
            c = _val(close_s, i)
            h = _val(high_s, i)
            l = _val(low_s, i)
            if c is not None and h is not None and l is not None:
                x[i] = _safe_div(h - l, abs(c))
        return _ts_mean(x, end_idx, 10)
    if spec.name == "alpha158_20_07":
        delta = _ts_delta(vol_s, end_idx, 5)
        avg = _ts_mean(vol_s, end_idx, 20)
        return None if delta is None or avg is None else _safe_div(delta, avg)
    if spec.name == "alpha158_20_08":
        o = _val(open_s, end_idx)
        return None if o is None else _safe_div(close_now - o, abs(o))
    if spec.name == "alpha158_20_09":
        fast = _ts_mean(amount_s, end_idx, 5)
        slow = _ts_mean(amount_s, end_idx, 20)
        return None if fast is None or slow is None else _safe_div(fast, slow) - 1.0
    if spec.name == "alpha158_20_10":
        x = [None] * len(close_s)
        for i in range(len(close_s)):
            c = _val(close_s, i)
            h = _val(high_s, i)
            l = _val(low_s, i)
            if c is not None and h is not None and l is not None:
                x[i] = _safe_div(h - l, abs(c))
        return _ts_std(x, end_idx, 20)
    if spec.name == "alpha158_20_11":
        return _ts_rank(amount_s, end_idx, 20)
    if spec.name == "alpha158_20_12":
        return _ts_corr(close_s, vol_s, end_idx, 20)
    if spec.name == "alpha158_20_13":
        return _ts_mean(ret_s, end_idx, 20)
    if spec.name == "alpha158_20_14":
        return _ts_rank(ret_s, end_idx, 10)
    if spec.name == "alpha158_20_15":
        return _ts_delta(close_s, end_idx, 1)
    if spec.name == "alpha158_20_16":
        x = [None] * len(close_s)
        for i in range(len(close_s)):
            c = _val(close_s, i)
            h = _val(high_s, i)
            l = _val(low_s, i)
            if c is not None and h is not None and l is not None:
                x[i] = _safe_div(c - l, h - l + 1e-9)
        return _ts_mean(x, end_idx, 10)
    if spec.name == "alpha158_20_17":
        high_max = _ts_max(high_s, end_idx, 20)
        return None if high_max is None else _safe_div(high_max, close_now) - 1.0
    if spec.name == "alpha158_20_18":
        low_min = _ts_min(low_s, end_idx, 20)
        return None if low_min is None else _safe_div(close_now, low_min) - 1.0
    if spec.name == "alpha158_20_19":
        return _ts_corr(ret_s, amount_s, end_idx, 20)
    if spec.name == "alpha158_20_20":
        fast = _ts_std(ret_s, end_idx, 5)
        slow = _ts_std(ret_s, end_idx, 20)
        return None if fast is None or slow is None else _safe_div(fast, slow + 1e-9)
    return None


def _zscore_map(values: dict[str, float]) -> dict[str, float]:
    if not values:
        return {}
    arr = list(values.values())
    mean = sum(arr) / len(arr)
    var = sum((x - mean) ** 2 for x in arr) / max(1, len(arr))
    std = math.sqrt(max(var, 1e-12))
    return {k: (v - mean) / std for k, v in values.items()}


def _perf_metrics(returns: list[float]) -> dict[str, float]:
    if not returns:
        return {"arr": 0.0, "mdd": 0.0, "calmar": 0.0}
    cumulative = 1.0
    peak = 1.0
    max_dd = 0.0
    for r in returns:
        cumulative *= (1.0 + r)
        if cumulative > peak:
            peak = cumulative
        dd = 1.0 - _safe_div(cumulative, peak)
        max_dd = max(max_dd, dd)
    days = max(1, len(returns))
    annual = cumulative ** _safe_div(252.0, float(days)) - 1.0
    calmar = _safe_div(annual, max_dd + 1e-9)
    return {"arr": round(annual, 6), "mdd": round(max_dd, 6), "calmar": round(calmar, 6)}


def run_research_pipeline(
    *,
    conn,
    direction: str,
    lookback: int,
    top_factor_count: int,
    universe_limit: int | None = None,
    timeout_seconds: int | None = None,
) -> dict[str, Any]:
    start_ts = time.time()
    hard_timeout = max(30, int(timeout_seconds or DEFAULT_PIPELINE_TIMEOUT_SECONDS))
    limit = DEFAULT_UNIVERSE_MAX_SYMBOLS if universe_limit is None else max(0, int(universe_limit))
    market, reason = _load_market_panel(conn, lookback=lookback, universe_limit=limit)
    if not market:
        return {"ok": False, "error_code": "DATA_NOT_READY", "error_message": f"研究数据不可用: {reason}"}

    specs = alpha158_20_equivalent_specs()
    as_of_idx = int(market["as_of_idx"])
    symbols = market["symbols"]
    target: dict[str, float] = {}
    factor_values: dict[str, dict[str, float]] = {spec.name: {} for spec in specs}
    errors: dict[str, int] = {spec.name: 0 for spec in specs}
    for idx_sym, (sym, panel) in enumerate(symbols.items(), start=1):
        if idx_sym % 100 == 0 and (time.time() - start_ts) > hard_timeout:
            return {
                "ok": False,
                "error_code": "PROCESS_TIMEOUT",
                "error_message": f"研究执行超时（>{hard_timeout}s），请缩小股票池或降低 lookback",
            }
        tr = _val(panel["returns"], as_of_idx)
        if tr is None:
            continue
        target[sym] = tr
        for spec in specs:
            value = _factor_value(spec, panel, as_of_idx)
            if value is None or math.isnan(value) or math.isinf(value):
                errors[spec.name] += 1
                continue
            factor_values[spec.name][sym] = float(value)

    factors: list[dict[str, Any]] = []
    for idx_spec, spec in enumerate(specs, start=1):
        if idx_spec % 4 == 0 and (time.time() - start_ts) > hard_timeout:
            return {
                "ok": False,
                "error_code": "PROCESS_TIMEOUT",
                "error_message": f"因子评估超时（>{hard_timeout}s），请稍后重试",
            }
        values_map = factor_values.get(spec.name) or {}
        common_symbols = [sym for sym in values_map.keys() if sym in target]
        if len(common_symbols) < 80:
            factors.append(
                {
                    "factor_name": spec.name,
                    "factor_expression": spec.expression,
                    "ic": 0.0,
                    "rank_ic": 0.0,
                    "coverage": round(_safe_div(len(common_symbols), max(1, len(target))), 6),
                    "stability": 0.0,
                    "quality_score": -1.0,
                    "error_reason": "insufficient_samples",
                }
            )
            continue
        x = [values_map[sym] for sym in common_symbols]
        y = [target[sym] for sym in common_symbols]
        ic = _pearson_corr(x, y)
        rank_ic = _spearman_corr(x, y)
        coverage = _safe_div(len(common_symbols), max(1, len(target)))
        stability = max(0.0, 1.0 - abs(ic - rank_ic))
        quality = 0.45 * ic + 0.35 * rank_ic + 0.10 * stability + 0.10 * coverage
        factors.append(
            {
                "factor_name": spec.name,
                "factor_expression": spec.expression,
                "ic": round(ic, 6),
                "rank_ic": round(rank_ic, 6),
                "coverage": round(coverage, 6),
                "stability": round(stability, 6),
                "quality_score": round(quality, 6),
                "error_reason": "",
            }
        )
    factors.sort(key=lambda item: float(item.get("quality_score") or -1e9), reverse=True)
    selected = [row for row in factors if float(row.get("quality_score") or -1.0) > -0.5][: max(1, int(top_factor_count))]
    if not selected:
        return {"ok": False, "error_code": "DATA_NOT_READY", "error_message": "可计算因子不足，无法完成研究回测"}

    selected_maps = [factor_values.get(str(item["factor_name"]), {}) for item in selected]
    selected_scores: dict[str, float] = {}
    if selected_maps:
        z_maps = [_zscore_map(m) for m in selected_maps]
        for sym in target.keys():
            vals = [zm[sym] for zm in z_maps if sym in zm]
            if len(vals) >= max(1, int(len(z_maps) * 0.5)):
                selected_scores[sym] = sum(vals) / len(vals)
    if len(selected_scores) < 50:
        return {"ok": False, "error_code": "DATA_NOT_READY", "error_message": "候选股票覆盖不足，无法回测"}

    baseline_maps = [_zscore_map(m) for m in factor_values.values() if m]
    baseline_scores: dict[str, float] = {}
    for sym in target.keys():
        vals = [m[sym] for m in baseline_maps if sym in m]
        if len(vals) >= 5:
            baseline_scores[sym] = sum(vals) / len(vals)

    selected_rank = sorted(selected_scores.items(), key=lambda kv: kv[1], reverse=True)
    baseline_rank = sorted(baseline_scores.items(), key=lambda kv: kv[1], reverse=True)
    top_n = max(50, int(len(selected_rank) * 0.1))
    selected_symbols = [sym for sym, _ in selected_rank[:top_n]]
    baseline_symbols = [sym for sym, _ in baseline_rank[:top_n]]

    lookback_days = max(20, min(int(lookback), len(market["trade_dates"]) - 1))
    end_idx = as_of_idx
    start_idx = max(1, end_idx - lookback_days + 1)
    candidate_daily: list[float] = []
    baseline_daily: list[float] = []
    for i in range(start_idx, end_idx + 1):
        c = [symbols[s]["returns"][i] for s in selected_symbols if s in symbols and symbols[s]["returns"][i] is not None]
        b = [symbols[s]["returns"][i] for s in baseline_symbols if s in symbols and symbols[s]["returns"][i] is not None]
        if c:
            candidate_daily.append(sum(c) / len(c))
        if b:
            baseline_daily.append(sum(b) / len(b))

    candidate_perf = _perf_metrics(candidate_daily)
    baseline_perf = _perf_metrics(baseline_daily)
    avg_ic = sum(float(item.get("ic") or 0.0) for item in selected) / len(selected)
    avg_rank_ic = sum(float(item.get("rank_ic") or 0.0) for item in selected) / len(selected)
    metrics = {
        "ic": round(avg_ic, 6),
        "rank_ic": round(avg_rank_ic, 6),
        **candidate_perf,
    }
    baseline_ic = round(
        sum(float(item.get("ic") or 0.0) for item in factors[: max(3, min(20, len(factors)))]) / max(1, len(factors[: max(3, min(20, len(factors)))])),
        6,
    )
    baseline_rank_ic = round(
        sum(float(item.get("rank_ic") or 0.0) for item in factors[: max(3, min(20, len(factors)))]) / max(1, len(factors[: max(3, min(20, len(factors)))])),
        6,
    )
    benchmark_delta = {
        "baseline": {
            "name": "alpha158_20",
            "ic": baseline_ic,
            "rank_ic": baseline_rank_ic,
            **baseline_perf,
        },
        "delta_arr": round(float(metrics["arr"]) - float(baseline_perf["arr"]), 6),
        "delta_mdd": round(float(metrics["mdd"]) - float(baseline_perf["mdd"]), 6),
        "delta_calmar": round(float(metrics["calmar"]) - float(baseline_perf["calmar"]), 6),
        "delta_ic": round(float(metrics["ic"]) - float(baseline_ic), 6),
        "delta_rank_ic": round(float(metrics["rank_ic"]) - float(baseline_rank_ic), 6),
    }

    return {
        "ok": True,
        "metrics": metrics,
        "artifacts": {
            "data_adapter_version": DATA_ADAPTER_VERSION,
            "factor_expr_version": FACTOR_EXPR_VERSION,
            "pipeline_timeout_seconds": hard_timeout,
            "selection_reason": "alpha158_20_equivalent_topN",
            "candidate_factors": factors,
            "selected_factors": selected,
            "benchmark_delta": benchmark_delta,
            "as_of_date": market["as_of_date"],
            "validation": market["validation"],
            "universe": {
                "name": "A_share_all",
                "symbol_count": len(symbols),
                "selected_count": len(selected_symbols),
                "baseline_count": len(baseline_symbols),
            },
            "factor_meta": {
                "spec_count": len(specs),
                "error_count_by_factor": errors,
            },
        },
        "stdout": (
            f"[self_research] as_of={market['as_of_date']} symbols={len(symbols)} "
            f"selected_factors={len(selected)} selected_stocks={len(selected_symbols)}"
        ),
    }
