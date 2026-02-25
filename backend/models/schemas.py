from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class CompileRequest(BaseModel):
    strategy_text: str = Field(min_length=5)


class CompileResponse(BaseModel):
    strategy_json: dict[str, Any]


class BacktestRequest(BaseModel):
    allowed_pairs: list[str]
    time_range: tuple[datetime, datetime]
    strategy_json: dict[str, Any]


class BacktestMetrics(BaseModel):
    roi: float
    sharpe: float
    max_drawdown: float
    win_rate: float
    trade_count: int
    pair_graph_score: float = 0.0


class BacktestResponse(BaseModel):
    result_id: str
    metrics: BacktestMetrics


class OptimizeRequest(BaseModel):
    allowed_pairs: list[str]
    time_range: tuple[datetime, datetime]
    strategy_json: dict[str, Any]
    iterations: int = Field(default=5, ge=1, le=20)
    objective: Literal["roi", "sharpe"] = "sharpe"


class OptimizeCandidate(BaseModel):
    strategy_json: dict[str, Any]
    metrics: BacktestMetrics


class OptimizeResponse(BaseModel):
    result_id: str
    best_candidate: OptimizeCandidate
    candidates: list[OptimizeCandidate]


class ResultResponse(BaseModel):
    result_id: str
    kind: Literal["backtest", "optimize"]
    payload: dict[str, Any]
