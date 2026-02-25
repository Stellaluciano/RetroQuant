STRATEGY_DSL_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "RetroQuant Strategy DSL",
    "type": "object",
    "required": ["signal", "pair", "execution"],
    "properties": {
        "signal": {
            "type": "string",
            "enum": ["ema_cross", "rsi_reversion", "breakout"],
        },
        "pair": {"type": "string"},
        "fast": {"type": "integer", "minimum": 1},
        "slow": {"type": "integer", "minimum": 2},
        "threshold": {"type": "number"},
        "lookback": {"type": "integer", "minimum": 2},
        "filter": {
            "type": "object",
            "additionalProperties": {"type": ["string", "number", "boolean"]},
        },
        "execution": {"type": "string", "enum": ["long", "short"]},
    },
}
