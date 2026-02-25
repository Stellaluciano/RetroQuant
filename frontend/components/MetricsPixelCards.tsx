export function MetricsPixelCards({ metrics }: { metrics?: Record<string, number> }) {
  if (!metrics) return null;
  return (
    <section className="pixel-grid">
      {Object.entries(metrics).map(([k, v]) => (
        <article key={k} className="metric-card">
          <p>{k.toUpperCase()}</p>
          <h3>{typeof v === "number" ? v.toFixed(4) : String(v)}</h3>
        </article>
      ))}
    </section>
  );
}
