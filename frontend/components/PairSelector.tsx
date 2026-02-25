const PAIRS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"];

export function PairSelector({ value, onChange }: { value: string; onChange: (pair: string) => void }) {
  return (
    <section className="pixel-panel">
      <h2>Pair Selector</h2>
      <div className="pair-row">
        {PAIRS.map((pair) => (
          <button
            key={pair}
            type="button"
            className={`pixel-btn ${value === pair ? "active" : ""}`}
            onClick={() => onChange(pair)}
          >
            {pair}
          </button>
        ))}
      </div>
    </section>
  );
}
