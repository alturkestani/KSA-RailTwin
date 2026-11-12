// Side panel for the national map: what the selected scenario/programme contains, in model language.
import { useEffect, useState } from "react";
import { api } from "../api";
import { POP_LABEL } from "../config";
import { prettyId, range } from "../format";
import type { CbaCase, Meta, Population, Programme, Scenario } from "../types";

export function ScenarioPanel({ scenario, meta, pop }: { scenario: Scenario | null; meta: Meta | null; pop: Population }) {
  const [prog, setProg] = useState<Programme | null>(null);
  const [s1, setS1] = useState<CbaCase | null>(null);
  const id = scenario?.id ?? "";

  useEffect(() => {
    setProg(null);
    if (id.startsWith("S6")) api.programmes(pop).then((r) => setProg(r.programmes.find((p) => p.id === id) ?? null)).catch(() => setProg(null));
    if (id === "S1") api.cba(pop).then((r) => setS1(r.cases.find((c) => c.case === "CBA-S1-committed-programme") ?? null)).catch(() => setS1(null));
  }, [id, pop]);

  if (!scenario || !meta) return <div className="muted">loading…</div>;
  return (
    <div>
      <h2>
        {scenario.id}
        {scenario.role ? <span className="role"> · {scenario.role}</span> : null}
      </h2>
      <p className="scenario-title">{scenario.title}</p>
      <p className="muted">
        Baseline: {scenario.baseline ?? "none (S0 is the reference for S1)"} · layers: {scenario.layers.join(", ")} · source {scenario.source}
      </p>
      {id.startsWith("S6") && prog ? (
        <>
          <h3>Corridors and phases (hypothetical, ours)</h3>
          <ul>
            {Object.entries(prog.phases).map(([year, ids]) => (
              <li key={year}>
                {year}: {ids.map(prettyId).join("; ")}
              </li>
            ))}
          </ul>
          <h3>In the model, against S1 ({POP_LABEL[pop]}, 60 years, Green Book 2026)</h3>
          <table className="kv">
            <tbody>
              <tr>
                <th>NPV, SAR m PV</th>
                <td>{range(prog.metrics.npv)}</td>
              </tr>
              <tr>
                <th>BCR</th>
                <td>{range(prog.metrics.bcr, 2)}</td>
              </tr>
              <tr>
                <th>Capex, SAR m (uplifted, undiscounted)</th>
                <td>{range(prog.metrics.capex)}</td>
              </tr>
            </tbody>
          </table>
          {prog.p90_cost_note ? <p className="note-l1">Al-Kharj spur P90 cost risk: {prog.p90_cost_note}</p> : null}
          {prog.flags ? <p className="muted">Flags: {prog.flags}</p> : null}
        </>
      ) : null}
      {id === "S1" && s1 ? (
        <>
          <h3>Committed programme in the model, S1 vs S0 ({POP_LABEL[pop]}, 60 years)</h3>
          <table className="kv">
            <tbody>
              <tr>
                <th>NPV, SAR m PV</th>
                <td>{range(s1.metrics.npv)}</td>
              </tr>
              <tr>
                <th>BCR</th>
                <td>{range(s1.metrics.bcr, 2)}</td>
              </tr>
            </tbody>
          </table>
          <p className="muted">Source {s1.source}. Committed lines are announced/planned, never existing (rule 5).</p>
        </>
      ) : null}
      {/^S[2-5]$/.test(id) ? (
        <p>
          {scenario.candidates.length} generated corridors of this family are drawn as hypothetical (ours). Each is appraised against S1 in the Cost/benefit ranges view.
        </p>
      ) : null}
      {id === "S0" ? <p>Existing lines only, including the Riyadh Metro. Historical lines are shown for context.</p> : null}
      <p className="muted small">Alignments: {meta.alignment_limitation}.</p>
    </div>
  );
}
