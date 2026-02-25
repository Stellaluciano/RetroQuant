export function RunBacktestButton({ loading, onClick }: { loading: boolean; onClick: () => void }) {
  return (
    <button type="button" className="pixel-btn callout" onClick={onClick} disabled={loading}>
      {loading ? "Running..." : "Run Backtest"}
    </button>
  );
}
