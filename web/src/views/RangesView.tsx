// Cost/benefit ranges: every figure is a P10/P50/P90 bar (rule 3), all programmes against S1.
import { useEffect, useState } from "react";
import { api } from "../api";
import { FAMILY_OF, POP_LABEL } from "../config";
import { num, prettyId, range } from "../format";
import type { CbaCase, FiscalResponse, Meta, Population, Programme, Scenario, VfmResponse } from "../types";
import { RangeChart, type RangeRow } from "../components/RangeChart";

const ORDER = ["S6-L2", "S6-L1", "S6-L3"];
const TONE: Record<string, RangeRow["tone"]> = { "S6-L2": "central", "S6-L1": "upside", "S6-L3": "reach" };

export function RangesView({ scenario, pop, meta, onReady }: { scenario: Scenario | null; scenarios: Scenario[]; pop: Population; meta: Meta | null; onReady: () => void }) {
  const [progs, setProgs] = useState<Programme[]>([]);
  const [cases, setCases] = useState<CbaCase[]>([]);
  const [fiscal, setFiscal] = useState<FiscalResponse | null>(null);
  const [vfm, setVfm] = useState<VfmResponse | null>(null);

  useEffect(() => {
    Promise.all([api.programmes(pop), api.cba(pop), api.fiscal(), api.vfm()]).then(([p, c, f, v]) => {
      setProgs(p.programmes);
      setCases(c.cases);
      setFiscal(f);
      setVfm(v);
      onReady();
    });
  }, [pop]);

  const id = scenario?.id ?? "";
  const shown = ORDER.map((k) => progs.find((p) => p.id === k)).filter((p): p is Programme => !!p);
  const l1 = progs.find((p) => p.id === "S6-L1");
  const sub = (p: Programme) => (p.id === "S6-L1" ? "upside case; carries the Al-Kharj spur P90 cost risk" : p.role);
  const s1 = cases.find((c) => c.case === "CBA-S1-committed-programme");
  const fam = FAMILY_OF[id];
  const famCases = fam ? cases.filter((c) => c.family === fam).sort((a, b) => (b.metrics.npv?.p50 ?? 0) - (a.metrics.npv?.p50 ?? 0)) : [];
  const fiscalEntity = fiscal?.programmes.find((e) => e.entity === (id.startsWith("S6") ? id : "S6-L2"));
  const vfmRows = vfm?.programmes ?? [];

  return (
    <div className="ranges">
      <h2>Cost/benefit ranges in the model (P10 / P50 / P90)</h2>
      <p className="muted">
        {meta?.label}. {POP_LABEL[pop]}, 60-year appraisal, Green Book 2026 declining rate; SAR million, 2025 prices, PV at 2026. Alignment limitation: {meta?.alignment_limitation}.
      </p>
      <div className="two-col">
        <RangeChart
          title="Programmes against S1: NPV (SAR m PV)"
          unit="SAR million PV"
          rows={shown.map((p) => ({ key: p.id, label: `${p.id} · ${p.role.split(" that")[0]}`, sub: sub(p), range: p.metrics.npv, tone: TONE[p.id] }))}
          width={720}
        />
        <RangeChart
          title="Programmes against S1: capex (SAR m, uplifted, undiscounted)"
          unit="SAR million"
          rows={shown.map((p) => ({ key: p.id, label: p.id, sub: sub(p), range: p.metrics.capex, tone: TONE[p.id] }))}
          width={720}
        />
      </div>
      <RangeChart title="Programmes against S1: BCR" unit="benefit-cost ratio" digits={2} rows={shown.map((p) => ({ key: p.id, label: p.id, sub: sub(p), range: p.metrics.bcr, tone: TONE[p.id] }))} width={720} />
      {l1?.p90_cost_note ? <p className="note-l1">S6-L1, Al-Kharj spur P90 cost risk: {l1.p90_cost_note}.</p> : null}

      {id === "S1" && s1 ? (
        <RangeChart
          title="S1 committed programme against S0 (SAR m PV)"
          unit="SAR million PV"
          rows={(["pvb", "pvc", "npv", "fiscal_cost"] as const).map((m) => ({ key: m, label: m.toUpperCase().replace("_", " "), range: s1.metrics[m], tone: "baseline" }))}
          width={720}
        />
      ) : null}
      {fam ? (
        <RangeChart
          title={`${id} family: each corridor against S1, NPV (SAR m PV), sorted by P50`}
          unit="SAR million PV"
          rows={famCases.map((c) => ({ key: c.case, label: prettyId(c.case).slice(0, 38), sub: `BCR ${range(c.metrics.bcr, 2)}`, range: c.metrics.npv }))}
          width={980}
        />
      ) : null}
      {id === "S0" ? <p>S0 is the reference for S1 only; select S1 or a programme.</p> : null}

      {fiscalEntity ? (
        <RangeChart
          title={`${fiscalEntity.entity}: net fiscal cost by delivery model, 60 years (${fiscal?.population_case}; SAR m PV)`}
          unit="SAR million PV"
          rows={fiscalEntity.models.map((m) => ({ key: m.model, label: m.model.replace(/_/g, " ").replace(/ sar$/, " (SAR)").replace(/ppp dbfom/, "PPP DBFOM").replace(/lvc/, "LVC"), range: m.net_fiscal_cost_60y }))}
          width={720}
        />
      ) : null}
      {vfmRows.length ? (
        <div>
          <h3>Value for money (PSC minus availability PPP)</h3>
          <p className="muted">{vfm?.definition}. {vfm?.range_note}.</p>
          <table className="grid">
            <thead>
              <tr>
                <th>programme</th>
                <th>low</th>
                <th>central</th>
                <th>high</th>
                <th>in the model</th>
              </tr>
            </thead>
            <tbody>
              {vfmRows.map((v) => (
                <tr key={v.entity}>
                  <td>{v.entity}</td>
                  <td className="num">{num(v.vfm.low)}</td>
                  <td className="num">{num(v.vfm.central)}</td>
                  <td className="num">{num(v.vfm.high)}</td>
                  <td>{v.sign_central}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}
      <p className="muted small">Sources: runs/r6/top5/top5.csv, runs/r6/top5/L*/score.json, runs/cba/*/results.json, runs/r7/fiscal/fiscal.json, runs/r7/vfm/vfm.json.</p>
    </div>
  );
}
