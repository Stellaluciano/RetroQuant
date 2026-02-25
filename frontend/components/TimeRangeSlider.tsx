export function TimeRangeSlider({
  days,
  onChange,
}: {
  days: number;
  onChange: (days: number) => void;
}) {
  return (
    <section className="pixel-panel">
      <h2>Time Range Slider</h2>
      <input
        className="pixel-range"
        type="range"
        min={7}
        max={180}
        step={1}
        value={days}
        onChange={(e) => onChange(Number(e.target.value))}
      />
      <p>{days} days</p>
    </section>
  );
}
