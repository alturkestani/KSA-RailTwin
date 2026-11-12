// Pareto explorer: robust NPV vs reach (or capex), each point with its low/medium/high population band.
// S6-L4 and S6-L5 appear here only, captioned "trade-off illustration only: no recommendation".
// S6-L6 appears here only too, captioned "comparison layout, not the recommended programme": a
// connectivity comparison from the connecting-set search (runs/r6/l6/score), not a search result.
import { useEffect, useState } from "react";
import { api } from "../api";
import { compact, num, range } from "../format";
import type { Meta, ParetoLayout, ParetoPoint, ParetoResponse } from "../types";
import { niceTicks } from "../components/RangeChart";

type XKey = "access_gain_120" | "capex_p50";
const X_LABEL: Record<XKey, string> = {
  access_gain_120: "reach: 2025 population newly within 120 min of a metro by rail vs S1 (persons)",
  capex_p50: "capex P50, SAR million (uplifted, undiscounted)",
};
const COLOR: Record<string, string> = { "S6-L2": "#1f4e79", "S6-L1": "#7c3aed", "S6-L3": "#0f766e", "S6-L4": "#94a3b8", "S6-L5": "#94a3b8", "S6-L6": "#1a7f64" };

function xOf(p: ParetoPoint | ParetoLayout, k: XKey): number | null {
  if (k === "access_gain_120") return p.access_gain_120;
  return "capex_p50" in p ? p.capex_p50 : p.capex.p50;
}

export function ParetoView({ meta, onReady }: { meta: Meta | null; onReady: () => void }) {
  const [data, setData] = useState<ParetoResponse | null>(null);
  const [xk, setXk] = useState<XKey>("access_gain_120");
  const [full, setFull] = useState(false);
  useEffect(() => {
    api.pareto().then((d) => {
      setData(d);
      onReady();
    });
  }, []);
  if (!data) return <div className="muted">loading…</div>;

  const W = 980;
  const H = 520;
  const m = { l: 80, r: 30, t: 40, b: 50 };
  const pts = [...data.front, ...data.layouts];
  const xs = pts.map((p) => xOf(p, xk)).filter((v): v is number => v !== null);
  // Default y range: the five search layouts' population bands; front points and S6-L6 below it are
  // marked at the bottom edge (count shown), "full range" shows them all.
  const yPts = full ? pts : data.layouts.filter((p) => !p.comparison_only);
  const ys = yPts.flatMap((p) => [p.npv_band.low, p.npv_band.high, p.robust_npv]).filter((v): v is number => v !== null);
  const [x0, x1] = [Math.min(0, ...xs), Math.max(...xs) * 1.12 || 1];
  const [y0, y1] = [Math.min(0, ...ys) * 1.08, Math.max(0, ...ys) * 1.25 || 1];
  const l6 = data.layouts.find((p) => p.comparison_only);
  const below = data.front.filter((p) => p.robust_npv !== null && p.robust_npv < y0);
  const clampY = (v: number) => Math.max(y0, Math.min(y1, v));
  const DY: Record<string, number> = { "S6-L2": 24, "S6-L1": -12, "S6-L3": -12, "S6-L4": -12, "S6-L5": 20, "S6-L6": -12 };
  const sx = (v: number) => m.l + ((v - x0) / (x1 - x0)) * (W - m.l - m.r);
  const sy = (v: number) => H - m.b - ((v - y0) / (y1 - y0)) * (H - m.t - m.b);

  return (
    <div>
      <h2>Pareto explorer: robust NPV against reach (trade-off view)</h2>
      <p className="muted">
        {meta?.label}. Judge {meta?.judge.version} ({meta?.judge.sha256.slice(0, 16)}…), seed {meta?.seed}. Each point: robust NPV (minimum over UN WPP low/medium/high of NPV at P50 cost, SAR m PV) with
        a vertical bar from the low to the high population case. In the model, all layouts are compared against S1.
      </p>
      <label>
        x axis{" "}
        <select value={xk} onChange={(e) => setXk(e.target.value as XKey)}>
          <option value="access_gain_120">reach (population within 120 min)</option>
          <option value="capex_p50">capex P50</option>
        </select>
      </label>{" "}
      <label className="check">
        <input type="checkbox" checked={full} onChange={() => setFull(!full)} /> full y range (all {data.front.length} front points)
      </label>
      <div>
      <svg width={W} height={H} role="img" aria-label="Pareto front" style={{ display: "block" }}>
        {niceTicks(y0, y1, 6).map((t) => (
          <g key={`y${t}`}>
            <line x1={m.l} x2={W - m.r} y1={sy(t)} y2={sy(t)} stroke="#e2e8f0" />
            <text x={m.l - 6} y={sy(t) + 3} fontSize="10" textAnchor="end" fill="#64748b">
              {compact(t)}
            </text>
          </g>
        ))}
        {niceTicks(x0, x1, 6).map((t) => (
          <g key={`x${t}`}>
            <line x1={sx(t)} x2={sx(t)} y1={m.t} y2={H - m.b} stroke="#f1f5f9" />
            <text x={sx(t)} y={H - m.b + 14} fontSize="10" textAnchor="middle" fill="#64748b">
              {compact(t)}
            </text>
          </g>
        ))}
        <line x1={m.l} x2={W - m.r} y1={sy(0)} y2={sy(0)} stroke="#334155" strokeDasharray="3 3" />
        <text x={(W + m.l) / 2} y={H - 10} fontSize="11" textAnchor="middle" fill="#0f172a">
          {X_LABEL[xk]}
        </text>
        <text transform={`translate(16 ${(H - m.b + m.t) / 2}) rotate(-90)`} fontSize="11" textAnchor="middle" fill="#0f172a">
          robust NPV, SAR million PV (bar: low–high population case)
        </text>
        {data.front.map((p) => {
          const x = xOf(p, xk);
          if (x === null || p.robust_npv === null) return null;
          return (
            <g key={p.layout_hash + p.engine}>
              {p.npv_band.low !== null && p.npv_band.high !== null ? <line x1={sx(x)} x2={sx(x)} y1={sy(clampY(p.npv_band.low))} y2={sy(clampY(p.npv_band.high))} stroke="#94a3b8" strokeWidth={1.2} /> : null}
              {p.robust_npv < y0 ? (
                <path d={`M ${sx(x) - 4} ${sy(y0) - 6} L ${sx(x) + 4} ${sy(y0) - 6} L ${sx(x)} ${sy(y0)} Z`} fill="#94a3b8" />
              ) : (
                <circle cx={sx(x)} cy={sy(p.robust_npv)} r={3.5} fill={p.on_full_front ? "#475569" : "#fff"} stroke="#475569" />
              )}
            </g>
          );
        })}
        {data.layouts.map((p) => {
          const x = xOf(p, xk);
          if (x === null || p.robust_npv === null) return null;
          const c = COLOR[p.id] ?? "#334155";
          const label = p.comparison_only
            ? `${p.id}: ${p.caption ?? data.caption_comparison}`
            : p.trade_off_only
              ? `${p.id}: trade-off illustration only`
              : `${p.id}: ${p.role.split(" that")[0]}`;
          const right = sx(x) > W - 260;
          if (p.robust_npv < y0) {
            // off-scale (S6-L6 in the default view): a labelled marker at the bottom edge
            return (
              <g key={p.id}>
                <path d={`M ${sx(x) - 7} ${sy(y0) - 10} L ${sx(x) + 7} ${sy(y0) - 10} L ${sx(x)} ${sy(y0)} Z`} fill="#fff" stroke={c} strokeWidth={2} />
                <text x={right ? sx(x) - 10 : sx(x) + 10} y={sy(y0) - 14} textAnchor={right ? "end" : "start"} fontSize="11.5" fill={c} fontStyle="italic">
                  {p.id} (comparison layout): robust NPV {num(p.robust_npv)}, below this range
                </text>
              </g>
            );
          }
          return (
            <g key={p.id}>
              {p.npv_band.low !== null && p.npv_band.high !== null ? <line x1={sx(x)} x2={sx(x)} y1={sy(clampY(p.npv_band.low))} y2={sy(clampY(p.npv_band.high))} stroke={c} strokeWidth={3} strokeOpacity={0.6} /> : null}
              <rect x={sx(x) - 6} y={sy(p.robust_npv) - 6} width={12} height={12} fill={p.trade_off_only ? "#fff" : c} stroke={c} strokeWidth={2} />
              <text x={right ? sx(x) - 10 : sx(x) + 10} y={sy(p.robust_npv) + (DY[p.id] ?? -10)} textAnchor={right ? "end" : "start"} fontSize="11.5" fill={p.trade_off_only ? "#64748b" : c} fontStyle={p.trade_off_only ? "italic" : "normal"}>
                {label}
              </text>
            </g>
          );
        })}
        <text x={m.l + 4} y={13} fontSize="11" fill="#475569" fontStyle="italic">
          S6-L4, S6-L5: {data.caption_trade_off}
        </text>
        <text x={m.l + 4} y={28} fontSize="11" fill="#1a7f64" fontStyle="italic">
          S6-L6: {data.caption_comparison} (connectivity comparison, not a search-front point)
        </text>
        {below.length ? (
          <text x={W - m.r} y={13} fontSize="10" textAnchor="end" fill="#64748b">
            {below.length} front points below this range (triangles); tick "full y range" to show them
          </text>
        ) : null}
      </svg>
      </div>
      <p className="caption-warn">
        S6-L4 and S6-L5: {data.caption_trade_off}; they are reach trade-off illustrations from the search. S6-L6: {data.caption_comparison}; it is a connectivity comparison (the smallest-capex connecting set), not a search-front point and
        not a reach trade-off. None of the three carries a delivery model or a stage-gate. {l6 ? <>In the model, S6-L6&apos;s national reach gain (reported only, not plotted) is {num(l6.national_reach_gain_120)} persons.</> : null}
      </p>
      <table className="grid">
        <thead>
          <tr>
            <th>layout</th>
            <th>framing</th>
            <th>NPV draws, UN WPP medium (SAR m PV)</th>
            <th>NPV at P50 cost low / medium / high</th>
            <th>capex (SAR m)</th>
            <th>reach gain 120 min</th>
          </tr>
        </thead>
        <tbody>
          {data.layouts.map((p) => (
            <tr key={p.id} className={p.trade_off_only ? "muted" : ""}>
              <td>{p.id}</td>
              <td>{p.caption ?? p.role}</td>
              <td>{range(p.npv_draws_medium)}</td>
              <td>
                {num(p.npv_band.low)} / {num(p.npv_band.medium)} / {num(p.npv_band.high)}
              </td>
              <td>{range(p.capex)}</td>
              <td className="num">{num(p.access_gain_120)}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <p className="muted small">
        Sources: runs/r6/pareto_front.csv ({data.front.length} rows), runs/r6/top5/top5.csv (S6-L1 to S6-L5), runs/r6/l6/score/S6-L6.csv (S6-L6, not a front point). Filled circles: on the full front. Alignment limitation: {meta?.alignment_limitation}.
      </p>
    </div>
  );
}
