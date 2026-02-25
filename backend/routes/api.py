from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4

from fastapi import APIRouter, HTTPException

from backend.models.schemas import (
    BacktestRequest,
    BacktestResponse,
    CompileRequest,
    CompileResponse,
    OptimizeRequest,
    OptimizeResponse,
    ResultResponse,
)
from dsl.compiler import compile_nl_strategy
from dsl.schema import STRATEGY_DSL_SCHEMA
from engine.backtest import run_backtest
from optimizer.llm_optimizer import LLMStyleOptimizer

router = APIRouter()
RESULT_STORE: dict[str, dict] = {}


@router.post("/compile-strategy", response_model=CompileResponse)
def compile_strategy(payload: CompileRequest) -> CompileResponse:
    strategy_json = compile_nl_strategy(payload.strategy_text)
    return CompileResponse(strategy_json=strategy_json)


@router.post("/run-backtest", response_model=BacktestResponse)
def run_backtest_endpoint(payload: BacktestRequest) -> BacktestResponse:
    metrics = run_backtest(payload.allowed_pairs, payload.time_range, payload.strategy_json)
    result_id = str(uuid4())
    RESULT_STORE[result_id] = {
        "kind": "backtest",
        "payload": {"metrics": metrics, "strategy_json": payload.strategy_json},
    }
    return BacktestResponse(result_id=result_id, metrics=metrics)


@router.post("/optimize", response_model=OptimizeResponse)
def optimize_endpoint(payload: OptimizeRequest) -> OptimizeResponse:
    optimizer = LLMStyleOptimizer()
    best, candidates = optimizer.optimize(
        payload.allowed_pairs,
        payload.time_range,
        payload.strategy_json,
        payload.iterations,
        payload.objective,
    )
    result_id = str(uuid4())
    RESULT_STORE[result_id] = {
        "kind": "optimize",
        "payload": {"best_candidate": best, "candidates": candidates},
    }
    return OptimizeResponse(result_id=result_id, best_candidate=best, candidates=candidates)


@router.get("/results/{result_id}", response_model=ResultResponse)
def get_result(result_id: str) -> ResultResponse:
    entry = RESULT_STORE.get(result_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Result not found")
    return ResultResponse(result_id=result_id, kind=entry["kind"], payload=entry["payload"])


@router.get("/dsl-schema")
def get_dsl_schema() -> dict:
    return STRATEGY_DSL_SCHEMA


@router.get("/demo-request")
def demo_request() -> dict:
    now = datetime.now(timezone.utc)
    return {
        "allowed_pairs": ["BTCUSDT", "ETHUSDT", "SOLUSDT"],
        "time_range": [(now - timedelta(days=60)).isoformat(), now.isoformat()],
        "strategy_json": {
            "signal": "ema_cross",
            "pair": "BTCUSDT",
            "fast": 20,
            "slow": 50,
            "filter": {"eth_momentum": ">0"},
            "execution": "long",
        },
    }
