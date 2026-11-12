> **Document version:** screening/README.md v1.0 | 30 Oct 2026 | Author: R0 builder | Status: draft

# `screening/` (W2, R2)

Will own the Kingdom-wide screening (W2): the per-region sweeps of all 13 regions (`region-sweep` skill), the candidate town register `cities/ksa/candidates.parquet`, the funnel from all settlements to a long list (transparent filters) and a short list (weighted multi-criteria score with a ±25 % weight sweep and rank stability), corridor-family generation from the short list (never a hard-coded town list), and the coverage audit reconciled to GASTAT's governorate count. Owners: `region-scout` × 13, `screening-analyst`.

Status at R0: skeleton only (`uv run python -m screening.cli version`). No methods are implemented or chosen here yet; the owning milestone decides them under the rules in `CLAUDE.md`, and every real-world constant it introduces lives in YAML with `source:` or `assumption:` and a row in `docs/assumptions.md`. Modelled outputs carry the label "synthetic demand, uncalibrated: scenario comparison, not a forecast".
