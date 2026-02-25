export function StrategyInputPanel({
  value,
  onChange,
}: {
  value: string;
  onChange: (next: string) => void;
}) {
  return (
    <section className="pixel-panel">
      <h2>Strategy Input</h2>
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        rows={5}
        className="pixel-input"
        placeholder='When BTC EMA20 crosses EMA50 and ETH momentum > 0, go long BTC.'
      />
    </section>
  );
}
