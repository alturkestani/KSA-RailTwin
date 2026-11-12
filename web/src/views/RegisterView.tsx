// Register and funnel: filters by region, stage and population; funnel counts; table.
import { useEffect, useMemo, useState } from "react";
import { api } from "../api";
import { STAGE_ORDER, STAGE_STYLE } from "../config";
import { num } from "../format";
import type { FunnelResponse, RegisterRow, Stage } from "../types";

export function RegisterView({ onRows, onReady }: { onRows: (rows: RegisterRow[] | null) => void; onReady: () => void }) {
  const [rows, setRows] = useState<RegisterRow[]>([]);
  const [funnel, setFunnel] = useState<FunnelResponse | null>(null);
  const [region, setRegion] = useState<string>("");
  const [stages, setStages] = useState<Set<Stage>>(new Set(STAGE_ORDER));
  const [minPop, setMinPop] = useState<number>(0);

  useEffect(() => {
    Promise.all([api.register(), api.funnel()]).then(([r, f]) => {
      setRows(r.rows);
      setFunnel(f);
      onReady();
    });
    return () => onRows(null);
  }, []);

  const filtered = useMemo(
    () => rows.filter((r) => (!region || r.region === region) && stages.has(r.stage) && (r.population ?? 0) >= minPop),
    [rows, region, stages, minPop],
  );
  useEffect(() => onRows(filtered), [filtered, onRows]);

  const regions = useMemo(() => [...new Set(rows.map((r) => r.region))].sort(), [rows]);
  const fr = funnel?.per_region.find((p) => p.region === region);
  const bars = region && fr
    ? [
        { stage: `settlements (${region})`, count: fr.settlements },
        { stage: "long list", count: fr.long_list },
        { stage: "served bucket", count: fr.served },
        { stage: "short list", count: fr.short_list },
      ]
    : (funnel?.stages ?? []);
  const maxCount = Math.max(1, ...bars.map((b) => b.count));
  const table = [...filtered].sort((a, b) => (a.rank ?? 1e9) - (b.rank ?? 1e9) || (b.population ?? 0) - (a.population ?? 0)).slice(0, 150);

  return (
    <div>
      <h2>Settlement register and screening funnel</h2>
      <p className="muted">{funnel?.label ?? "screening input, not a forecast"}. Every region and governorate stays in the register (rule 2); filters only hide rows.</p>
      <div className="filters">
        <label>
          Region{" "}
          <select value={region} onChange={(e) => setRegion(e.target.value)}>
            <option value="">all 13 regions</option>
            {regions.map((r) => (
              <option key={r} value={r}>
                {r}
              </option>
            ))}
          </select>
        </label>
        <label>
          Min. population{" "}
          <select value={minPop} onChange={(e) => setMinPop(Number(e.target.value))}>
            {[0, 5000, 10000, 50000, 100000].map((v) => (
              <option key={v} value={v}>
                {num(v)}
              </option>
            ))}
          </select>
        </label>
        {STAGE_ORDER.map((s) => (
          <label key={s} className="check">
            <input
              type="checkbox"
              checked={stages.has(s)}
              onChange={() => {
                const n = new Set(stages);
                if (n.has(s)) n.delete(s);
                else n.add(s);
                setStages(n);
              }}
            />{" "}
            {STAGE_STYLE[s].name}
          </label>
        ))}
      </div>
      <h3>Funnel{region ? ` (${region})` : " (national)"}</h3>
      <div className="funnel">
        {bars.map((b) => (
          <div key={b.stage} className="funnel-row">
            <span className="funnel-label">{b.stage}</span>
            <span className="funnel-bar" style={{ width: `${(70 * b.count) / maxCount}%` }} />
            <span className="funnel-count">{num(b.count)}</span>
          </div>
        ))}
      </div>
      <h3>
        Register rows: {num(filtered.length)} shown of {num(rows.length)}
      </h3>
      <div className="table-wrap">
        <table className="grid">
          <thead>
            <tr>
              <th>rank</th>
              <th>name</th>
              <th>الاسم</th>
              <th>region</th>
              <th>population</th>
              <th>status</th>
              <th>stage</th>
              <th>roles</th>
            </tr>
          </thead>
          <tbody>
            {table.map((r) => (
              <tr key={r.row_key}>
                <td>{r.rank ?? ""}</td>
                <td>{r.name_en}</td>
                <td dir="rtl" className="ar">
                  {r.name_ar}
                </td>
                <td>{r.region}</td>
                <td className="num">{r.population === null ? "n/a" : num(r.population)}</td>
                <td>{r.pop_source_status}</td>
                <td>{STAGE_STYLE[r.stage].name}</td>
                <td className="small">{r.economic_roles.join(", ")}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
