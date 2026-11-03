export function calculateMeasuredSpeedKmh(speedometerValue) {
  if (speedometerValue === null || speedometerValue === undefined) return "";

  const normalized = String(speedometerValue).trim().replace(/\s/g, "").replace(",", ".");
  if (!normalized || normalized === "-") return "";

  const speedometerSpeed = Number(normalized);
  if (!Number.isFinite(speedometerSpeed)) return "";

  return (Math.round(speedometerSpeed * 0.95 * 100) / 100).toFixed(2);
}