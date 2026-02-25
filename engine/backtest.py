from __future__ import annotations

import math

import numpy as np
import pandas as pd

from data.store import load_pair_data
from engine.pair_graph import build_pair_graph


def _max_drawdown(equity_curve: pd.Series) -> float:
    peak = equity_curve.cummax()
    dd = (equity_curve - peak) / peak
    return float(dd.min())


def run_backtest(allowed_pairs: list[str], time_range: tuple, strategy_json: dict) -> dict:
    start, end = time_range
    pair = strategy_json.get("pair", allowed_pairs[0])
    if pair not in allowed_pairs:
        pair = allowed_pairs[0]

    pair_data = load_pair_data(allowed_pairs, start, end)
    df = pair_data[pair_data["pair"] == pair].reset_index(drop=True)
    if df.empty or len(df) < 30:
        return {"roi": 0.0, "sharpe": 0.0, "max_drawdown": 0.0, "win_rate": 0.0, "trade_count": 0, "pair_graph_score": 0.0}

    close = df["close"].astype(float)
    signal = pd.Series(0, index=df.index, dtype=float)

    if strategy_json.get("signal") == "ema_cross":
        fast = int(strategy_json.get("fast", 20))
        slow = int(strategy_json.get("slow", 50))
        ema_fast = close.ewm(span=fast, adjust=False).mean()
        ema_slow = close.ewm(span=slow, adjust=False).mean()
        signal = (ema_fast > ema_slow).astype(float)
    elif strategy_json.get("signal") == "rsi_reversion":
        n = int(strategy_json.get("lookback", 14))
        threshold = float(strategy_json.get("threshold", 30))
        delta = close.diff()
        gain = delta.clip(lower=0).rolling(n).mean()
        loss = -delta.clip(upper=0).rolling(n).mean()
        rs = gain / loss.replace(0, np.nan)
        rsi = 100 - (100 / (1 + rs))
        signal = (rsi < threshold).fillna(0).astype(float)
    else:
        lookback = int(strategy_json.get("lookback", 20))
        high_roll = close.rolling(lookback).max()
        signal = (close >= high_roll).fillna(0).astype(float)

    filter_rule = strategy_json.get("filter", {})
    if isinstance(filter_rule, dict) and "eth_momentum" in filter_rule:
        eth = pair_data[pair_data["pair"] == "ETHUSDT"].copy()
        if not eth.empty:
            eth = eth.sort_values("timestamp")
            eth["eth_momentum"] = eth["close"].pct_change().rolling(8).mean().fillna(0)
            df = df.sort_values("timestamp")
            merged = df[["timestamp"]].merge(eth[["timestamp", "eth_momentum"]], on="timestamp", how="left")
            op = str(filter_rule["eth_momentum"]).strip()
            if op == ">0":
                signal = signal.where(merged["eth_momentum"].fillna(0) > 0, 0)
            elif op == "<0":
                signal = signal.where(merged["eth_momentum"].fillna(0) < 0, 0)

    if strategy_json.get("execution") == "short":
        signal = -signal

    returns = close.pct_change().fillna(0)
    strat_returns = returns * signal.shift(1).fillna(0)
    equity = (1 + strat_returns).cumprod()

    trade_changes = signal.diff().fillna(0).abs()
    trade_count = int((trade_changes > 0).sum())
    trade_pnl = strat_returns[strat_returns != 0]
    win_rate = float((trade_pnl > 0).mean()) if len(trade_pnl) else 0.0
    roi = float(equity.iloc[-1] - 1)

    volatility = strat_returns.std()
    sharpe = float(math.sqrt(24 * 365) * strat_returns.mean() / volatility) if volatility and not math.isnan(volatility) else 0.0

    pair_graph = build_pair_graph(pair_data)

    return {
        "roi": round(roi, 4),
        "sharpe": round(sharpe, 4),
        "max_drawdown": round(_max_drawdown(equity), 4),
        "win_rate": round(win_rate, 4),
        "trade_count": trade_count,
        "pair_graph_score": pair_graph.get(pair, {}).get("ETHUSDT", 0.0),
    }
