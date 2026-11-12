// Footer on every view: the synthetic-demand label, the alignment limitation, judge v3 and seed.
// The texts come from the API (/api/meta -> common.labels); they are never retyped here.
import type { Meta } from "../types";

export function Footer({ meta }: { meta: Meta | null }) {
  if (!meta) return <footer className="footer">loading labels…</footer>;
  return (
    <footer className="footer" data-testid="footer">
      <div className="footer-label">
        <b>{meta.label}</b>
      </div>
      <div className="footer-limit">Alignment limitation: {meta.alignment_limitation}.</div>
      <div className="footer-meta">
        Judge {meta.judge.version} (sha256 {meta.judge.sha256.slice(0, 16)}…, {meta.judge.source}) · seed {meta.seed} · baseline {meta.baseline} (
        {meta.baseline_run}) · central appraisal row {meta.central_row.population}, {meta.central_row.horizon} years, {meta.central_row.rate_case} · contract v
        {meta.contract_version} · map data {meta.osm_credit} (ODbL) · in the model, results compare scenarios; none is a forecast
      </div>
    </footer>
  );
}
