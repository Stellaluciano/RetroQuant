"use client";

import { useMemo, useState } from "react";

import { MetricsPixelCards } from "../components/MetricsPixelCards";
import { OptimizationPanel } from "../components/OptimizationPanel";
import { PairSelector } from "../components/PairSelector";
import { RunBacktestButton } from "../components/RunBacktestButton";
import { StrategyInputPanel } from "../components/StrategyInputPanel";
import { TimeRangeSlider } from "../components/TimeRangeSlider";
import { postJSON } from "../lib/api";

type CompileResponse = { strategy_json: Record<string, unknown> };
type BacktestResponse = { result_id: string; metrics: Record<string, number> };
type OptimizeResponse = {
  result_id: string;
  best_candidate: { strategy_json: Record<string, unknown>; metrics: { sharpe: number } };
};

export default function HomePage() {
  const [strategyText, setStrategyText] = useState(
    "When BTC EMA20 crosses EMA50 and ETH momentum > 0, go long BTC."
  );
  const [pair, setPair] = useState("BTCUSDT");
  const [days, setDays] = useState(90);
  const [strategyJson, setStrategyJson] = useState<Record<string, unknown>>({});
  const [metrics, setMetrics] = useState<Record<string, number>>();
  const [bestSharpe, setBestSharpe] = useState<number>();
  const [loadingBacktest, setLoadingBacktest] = useState(false);
  const [loadingOptimize, setLoadingOptimize] = useState(false);

  const timeRange = useMemo(() => {
    const end = new Date();
    const start = new Date(end.getTime() - days * 24 * 60 * 60 * 1000);
    return [start.toISOString(), end.toISOString()];
  }, [days]);

  async function compileStrategy() {
    const compiled = await postJSON<CompileResponse>("/compile-strategy", { strategy_text: strategyText });
    const json = { ...compiled.strategy_json, pair };
    setStrategyJson(json);
    return json;
  }

  async function runBacktest() {
    setLoadingBacktest(true);
    try {
      const json = Object.keys(strategyJson).length ? strategyJson : await compileStrategy();
      const response = await postJSON<BacktestResponse>("/run-backtest", {
        allowed_pairs: ["BTCUSDT", "ETHUSDT", "SOLUSDT"],
        time_range: timeRange,
        strategy_json: json,
      });
      setMetrics(response.metrics);
    } finally {
      setLoadingBacktest(false);
    }
  }

  async function optimize() {
    setLoadingOptimize(true);
    try {
      const json = Object.keys(strategyJson).length ? strategyJson : await compileStrategy();
      const response = await postJSON<OptimizeResponse>("/optimize", {
        allowed_pairs: ["BTCUSDT", "ETHUSDT", "SOLUSDT"],
        time_range: timeRange,
        strategy_json: json,
        iterations: 6,
        objective: "sharpe",
      });
      setBestSharpe(response.best_candidate.metrics.sharpe);
    } finally {
      setLoadingOptimize(false);
    }
  }

  return (
    <main className="terminal">
      <h1>RetroQuant // LLM Crypto Strategy Lab</h1>
      <StrategyInputPanel value={strategyText} onChange={setStrategyText} />
      <PairSelector value={pair} onChange={setPair} />
      <TimeRangeSlider days={days} onChange={setDays} />
      <RunBacktestButton loading={loadingBacktest} onClick={runBacktest} />
      <OptimizationPanel loading={loadingOptimize} onClick={optimize} bestSharpe={bestSharpe} />
      <section className="pixel-panel">
        <h2>Compiled JSON DSL</h2>
        <pre>{JSON.stringify(strategyJson, null, 2)}</pre>
      </section>
      <MetricsPixelCards metrics={metrics} />
    </main>
  );
}
