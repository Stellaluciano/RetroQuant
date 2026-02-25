export function OptimizationPanel({
  onClick,
  loading,
  bestSharpe,
}: {
  onClick: () => void;
  loading: boolean;
  bestSharpe?: number;
}) {
  return (
    <section className="pixel-panel">
      <h2>Optimization Panel</h2>
      <button type="button" className="pixel-btn" onClick={onClick} disabled={loading}>
        {loading ? "Optimizing..." : "Optimize Strategy"}
      </button>
      {bestSharpe !== undefined && <p>Best Sharpe: {bestSharpe.toFixed(4)}</p>}
    </section>
  );
}
