from __future__ import annotations

import pandas as pd


def build_pair_graph(prices: pd.DataFrame, lookback: int = 48) -> dict[str, dict[str, float]]:
    """Builds a simple pair relationship graph using rolling return correlations."""
    if prices.empty:
        return {}

    pivot = prices.pivot_table(index="timestamp", columns="pair", values="close", aggfunc="last").sort_index()
    returns = pivot.pct_change().dropna()
    if returns.empty:
        return {}

    window = returns.tail(max(lookback, 10))
    corr = window.corr().fillna(0.0)

    graph: dict[str, dict[str, float]] = {}
    for base in corr.columns:
        graph[base] = {}
        for target in corr.columns:
            if base == target:
                continue
            graph[base][target] = round(float(corr.loc[base, target]), 4)
    return graph
