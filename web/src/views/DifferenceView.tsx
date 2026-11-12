// Difference mode: scenario minus the baseline S1 on the same metrics (api /api/difference).
import { useEffect, useMemo, useState } from "react";
import { api } from "../api";
import { FAMILY_OF, POP_LABEL } from "../config";
import { num, prettyId, signed } from "../format";
import type { DifferenceResponse, Meta, Population, Range, Scenario } from "../types";
import { RangeChart } from "../components/RangeChart";

export function DifferenceView({
  scenario,
  pop,
  meta,
  onCorridors,
  onReady,
}: {
  scenario: Scenario | null;
  scenarios: Scenario[];
  pop: Population;
  meta: Meta | null;
  onCorridors: (ids: string[] | null) => void;
  onReady: () => void;
}) {
  const id = scenario?.id ?? "S6-L2";
  const fam = FAMILY_OF[id];
  const options = useMemo(() => (fam && scenario ? scenario.candidates : []), [fam, scenario]);
  const [pick, setPick] = useState<string>("");
  const [diff, setDiff] = useState<DifferenceResponse | null>(null);
  const [err, setErr] = useState<string>("");

  const target = id.startsWith("S6") ? id : fam ? pick || options[0] || "" : "S6-L2";
  useEffect(() => {
    if (!target) return;
    setErr("");
    api
      .difference(target, pop)
      .then((d) => {
        setDiff(d);
        onCorridors(d.added_corridors);
        onReady();
      })
      .catch((e: unknown) => {
        setErr(String(e));
        onReady();
      });
  }, [target, pop]);
  useEffect(() => () => onCorridors(null), [onCorridors]);

  const inc = diff?.increments;
  const incRows = inc
    ? (["npv", "pvb", "pvc", "capex"] as const)
        .map((k) => ({ k, r: inc[k] as Range | null | undefined }))
        .filter((x): x is { k: "npv" | "pvb" | "pvc" | "capex"; r: Range } => !!x.r && typeof x.r === "object")
    : [];

  return (
    <div>
      <h2>Difference mode: {diff?.scenario ?? target} minus S1</h2>
      {id === "S0" || id === "S1" ? <p className="muted">S1 is the baseline, so the programme shown is S6-L2 (central case). Pick a programme or a family.</p> : null}
      {fam ? (
        <label>
          Corridor of {id}{" "}
          <select value={pick || options[0] || ""} onChange={(e) => setPick(e.target.value)}>
            {options.map((o) => (
              <option key={o} value={o}>
                {prettyId(o)}
              </option>
            ))}
          </select>
        </label>
      ) : null}
      {err ? <div className="error">{err}</div> : null}
      {diff ? (
        <>
          <p className="muted">
            {meta?.label}. {POP_LABEL[pop]}. {diff.role ? `${diff.scenario}: ${diff.role}. ` : ""}
            {typeof inc?.basis === "string" ? `Appraisal: ${inc.basis}.` : ""}
          </p>
          {diff.rows.length ? (
            <table className="grid">
              <thead>
                <tr>
                  <th>metric (in the model)</th>
                  <th>{diff.scenario}</th>
                  <th>S1</th>
                  <th>difference</th>
                  <th>unit</th>
                </tr>
              </thead>
              <tbody>
                {diff.rows.map((r) => (
                  <tr key={r.metric}>
                    <td>{r.metric}</td>
                    <td className="num">{num(r.scenario)}</td>
                    <td className="num">{num(r.S1)}</td>
                    <td className="num delta">{signed(r.delta)}</td>
                    <td>{r.unit}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : null}
          {diff.lines_2050.length ? (
            <>
              <h3>Passengers per line, 2050 (UN WPP medium)</h3>
              {diff.lines_2050_coverage ? (
                <p className="coverage">
                  S1 per-line values are in the run files for {diff.lines_2050_coverage.s1_lines_covered.map(prettyId).join(", ")} only; not covered:{" "}
                  {diff.lines_2050_coverage.s1_lines_not_covered.map(prettyId).join(", ")}. Why: {diff.lines_2050_coverage.why}.
                </p>
              ) : null}
              <table className="grid">
                <thead>
                  <tr>
                    <th>line</th>
                    <th>{diff.scenario}</th>
                    <th>S1</th>
                    <th>difference</th>
                  </tr>
                </thead>
                <tbody>
                  {diff.lines_2050.map((l) => (
                    <tr key={l.line_id}>
                      <td>{prettyId(l.line_id)}</td>
                      <td className="num">{num(l.scenario)}</td>
                      <td className="num">{l.S1 === null ? "not in run files" : num(l.S1)}</td>
                      <td className="num delta">{l.delta === null ? "not computed" : signed(l.delta)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </>
          ) : null}
          <RangeChart
            title={`Increment over S1 (appraisal, ${POP_LABEL[pop]}, 60 years): SAR million`}
            unit="SAR million (NPV, PVB, PVC: PV at 2026; capex: uplifted, undiscounted)"
            rows={incRows.map(({ k, r }) => ({ key: k, label: k.toUpperCase(), range: r, tone: "central" }))}
            width={620}
          />
          {diff.p90_cost_note ? <p className="note-l1">Al-Kharj spur P90 cost risk: {diff.p90_cost_note}.</p> : null}
          <p className="muted small">
            Added corridors (highlighted on the map): {diff.added_corridors.map(prettyId).join("; ")}. Sources: {Array.isArray(diff.source) ? diff.source.join(", ") : diff.source}. Alignment
            limitation: {meta?.alignment_limitation}.
          </p>
        </>
      ) : null}
    </div>
  );
}
