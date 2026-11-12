// Number formatting. Ranges are always written P10 / P50 / P90 (rule 3); minus is U+2212.
import type { Range } from "./types";

const MINUS = "−";

export function num(v: number | null | undefined, digits = 0): string {
  if (v === null || v === undefined || !Number.isFinite(v)) return "n/a";
  const s = Math.abs(v).toLocaleString("en-US", {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  });
  return v < 0 ? `${MINUS}${s}` : s;
}

export function signed(v: number | null | undefined, digits = 0): string {
  if (v === null || v === undefined || !Number.isFinite(v)) return "n/a";
  return v > 0 ? `+${num(v, digits)}` : num(v, digits);
}

export function range(r: Range | null | undefined, digits = 0): string {
  if (!r) return "n/a";
  return `P10 ${num(r.p10, digits)} / P50 ${num(r.p50, digits)} / P90 ${num(r.p90, digits)}`;
}

export function compact(v: number | null | undefined): string {
  if (v === null || v === undefined || !Number.isFinite(v)) return "n/a";
  const a = Math.abs(v);
  if (a >= 1e6) return `${num(v / 1e6, 1)}M`;
  if (a >= 1e3) return `${num(v / 1e3, 1)}k`;
  return num(v, 0);
}

export function prettyId(id: string): string {
  return id
    .replace(/^CBA-/, "")
    .replace(/^S\d-(trunk_gap|branch_spur|commuter_belt|station_addition)-/, (_m, fam: string) => `${fam.replace("_", " ")}: `)
    .replace(/-/g, " ");
}
