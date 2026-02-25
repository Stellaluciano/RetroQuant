from __future__ import annotations

import copy
import random

from engine.backtest import run_backtest


class LLMStyleOptimizer:
    """Heuristic optimizer that mimics LLM-guided parameter mutations."""

    def __init__(self, seed: int = 42) -> None:
        random.seed(seed)

    def _mutate(self, strategy: dict, metrics: dict | None = None) -> dict:
        candidate = copy.deepcopy(strategy)
        signal = candidate.get("signal")

        if signal == "ema_cross":
            fast = int(candidate.get("fast", 20))
            slow = int(candidate.get("slow", 50))
            if metrics and metrics.get("sharpe", 0) < 0.8:
                fast = max(5, fast - random.randint(1, 3))
                slow = min(120, slow + random.randint(2, 8))
            else:
                fast = max(5, fast + random.choice([-2, -1, 1, 2]))
                slow = max(fast + 1, slow + random.choice([-5, -3, 3, 5]))
            candidate["fast"] = fast
            candidate["slow"] = slow
        elif signal == "rsi_reversion":
            threshold = int(candidate.get("threshold", 30))
            lookback = int(candidate.get("lookback", 14))
            candidate["threshold"] = max(10, min(45, threshold + random.choice([-3, -2, 2, 3])))
            candidate["lookback"] = max(5, min(30, lookback + random.choice([-2, -1, 1, 2])))
        else:
            lookback = int(candidate.get("lookback", 20))
            candidate["lookback"] = max(5, min(80, lookback + random.choice([-5, -3, 3, 5])))

        if random.random() < 0.25:
            candidate["execution"] = "short" if candidate.get("execution") == "long" else "long"

        return candidate

    def optimize(
        self,
        allowed_pairs: list[str],
        time_range: tuple,
        base_strategy: dict,
        iterations: int,
        objective: str,
    ) -> tuple[dict, list[dict]]:
        candidates = []
        current = base_strategy
        current_metrics = run_backtest(allowed_pairs, time_range, current)
        best = {"strategy_json": current, "metrics": current_metrics}
        candidates.append(best)

        for _ in range(iterations):
            mutated = self._mutate(current, current_metrics)
            metrics = run_backtest(allowed_pairs, time_range, mutated)
            candidate = {"strategy_json": mutated, "metrics": metrics}
            candidates.append(candidate)

            better = metrics[objective] > best["metrics"][objective]
            if better:
                best = candidate
                current = mutated
                current_metrics = metrics

        return best, candidates
