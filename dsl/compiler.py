from __future__ import annotations

import re


def compile_nl_strategy(strategy_text: str) -> dict:
    text = strategy_text.lower()
    pair = "BTCUSDT" if "btc" in text else "ETHUSDT"
    execution = "short" if "short" in text else "long"

    ema_match = re.search(r"ema\s*(\d+)\s*(?:crosses|cross|>)\s*ema\s*(\d+)", text)
    if ema_match:
        fast, slow = sorted((int(ema_match.group(1)), int(ema_match.group(2))))
        result = {
            "signal": "ema_cross",
            "pair": pair,
            "fast": fast,
            "slow": slow,
            "execution": execution,
        }
        if "eth momentum" in text:
            op = ">0" if "> 0" in text or ">0" in text else "<0"
            result["filter"] = {"eth_momentum": op}
        return result

    rsi_match = re.search(r"rsi\s*(?:below|<)\s*(\d+)", text)
    if rsi_match:
        return {
            "signal": "rsi_reversion",
            "pair": pair,
            "threshold": int(rsi_match.group(1)),
            "lookback": 14,
            "execution": execution,
        }

    return {
        "signal": "breakout",
        "pair": pair,
        "lookback": 20,
        "execution": execution,
    }
