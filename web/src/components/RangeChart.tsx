// P10/P50/P90 range bars on a shared axis (never a single point; rule 3).
import type { Range } from "../types";
import { compact, num } from "../format";

export interface RangeRow {
  key: string;
  label: string;
  sub?: string;
  range: Range | null;
  tone?: "central" | "upside" | "reach" | "baseline" | "plain";
}

const TONE: Record<NonNullable<RangeRow["tone"]>, string> = {
  central: "#1f4e79",
  upside: "#7c3aed",
  reach: "#0f766e",
  baseline: "#d97706",
  plain: "#475569",
};

export function RangeChart({ rows, unit, digits = 0, width = 760, title }: { rows: RangeRow[]; unit: string; digits?: number; width?: number; title?: string }) {
  const vals = rows.flatMap((r) => (r.range ? [r.range.p10, r.range.p90] : [])).filter((v): v is number => v !== null && Number.isFinite(v));
  if (vals.length === 0) return <div className="muted">No ranges stored for this selection.</div>;
  let lo = Math.min(0, ...vals);
  let hi = Math.max(0, ...vals);
  if (hi === lo) hi = lo + 1;
  const pad = (hi - lo) * 0.04;
  lo -= pad;
  hi += pad;
  const labelW = Math.min(250, Math.round(width * 0.3));
  const textW = Math.min(230, Math.max(215, Math.round(width * 0.3)));
  const plotW = width - labelW - textW;
  const rowH = 30;
  const h = rows.length * rowH + 34;
  const x = (v: number) => labelW + ((v - lo) / (hi - lo)) * plotW;
  const ticks = niceTicks(lo, hi, 5);
  return (
    <figure className="range-chart">
      {title ? <figcaption>{title}</figcaption> : null}
      <svg width={width} height={h} role="img" aria-label={title ?? "P10/P50/P90 ranges"}>
        {ticks.map((t) => (
          <g key={t}>
            <line x1={x(t)} x2={x(t)} y1={6} y2={h - 22} stroke="#e2e8f0" />
            <text x={x(t)} y={h - 8} fontSize="10" textAnchor="middle" fill="#64748b">
              {compact(t)}
            </text>
          </g>
        ))}
        <line x1={x(0)} x2={x(0)} y1={4} y2={h - 22} stroke="#334155" strokeDasharray="3 3" />
        {rows.map((r, i) => {
          const y = 14 + i * rowH;
          const c = TONE[r.tone ?? "plain"];
          const ok = r.range && r.range.p10 !== null && r.range.p90 !== null && r.range.p50 !== null;
          return (
            <g key={r.key}>
              <text x={4} y={y + 4} fontSize="12" fill="#0f172a">
                {r.label}
              </text>
              {r.sub ? (
                <text x={4} y={y + 16} fontSize="9.5" fill="#64748b">
                  {r.sub}
                </text>
              ) : null}
              {ok && r.range ? (
                <>
                  <line x1={x(r.range.p10 as number)} x2={x(r.range.p90 as number)} y1={y} y2={y} stroke={c} strokeOpacity={0.35} strokeWidth={10} strokeLinecap="butt" />
                  <line x1={x(r.range.p10 as number)} x2={x(r.range.p10 as number)} y1={y - 6} y2={y + 6} stroke={c} strokeWidth={1.5} />
                  <line x1={x(r.range.p90 as number)} x2={x(r.range.p90 as number)} y1={y - 6} y2={y + 6} stroke={c} strokeWidth={1.5} />
                  <line x1={x(r.range.p50 as number)} x2={x(r.range.p50 as number)} y1={y - 7} y2={y + 7} stroke={c} strokeWidth={3} />
                </>
              ) : (
                <text x={labelW} y={y + 4} fontSize="11" fill="#64748b">
                  range not stored
                </text>
              )}
              <text x={labelW + plotW + 10} y={y + 4} fontSize="10.5" fill="#334155">
                {r.range ? `P10 ${num(r.range.p10, digits)} / P50 ${num(r.range.p50, digits)} / P90 ${num(r.range.p90, digits)}` : ""}
              </text>
            </g>
          );
        })}
      </svg>
      <div className="axis-unit">{unit}; bar = P10 to P90, thick tick = P50; dashed line = 0</div>
    </figure>
  );
}

export function niceTicks(lo: number, hi: number, n: number): number[] {
  const span = hi - lo;
  const step0 = span / Math.max(1, n);
  const mag = Math.pow(10, Math.floor(Math.log10(step0)));
  const step = [1, 2, 2.5, 5, 10].map((m) => m * mag).find((s) => span / s <= n + 1) ?? mag * 10;
  const out: number[] = [];
  for (let t = Math.ceil(lo / step) * step; t <= hi; t += step) out.push(Math.round(t / step) * step);
  return out;
}
