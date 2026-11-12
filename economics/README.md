> **Document version:** economics/README.md v1.0 | 30 Oct 2026 | Author: R0 builder | Status: draft

# `economics/` (W4, R5)

Will own the long-term benefits and cost-benefit analysis (W4): a named appraisal standard (Green Book, DfT TAG incl. A2.4, EU CBA Guide 2014, World Bank) with departures stated, 30/40/60-year horizons with residual value, social, commercial and declining discount rates, the benefit streams without double counting, and NPV, BCR with and without wider impacts, EIRR, FIRR, payback, fiscal cost, Monte Carlo P10/P50/P90, tornado charts and switching values (`cba-appraisal` skill). Owner: `economist`.

Status at R0: skeleton only (`uv run python -m economics.cli version`). No methods are implemented or chosen here yet; the owning milestone decides them under the rules in `CLAUDE.md`, and every real-world constant it introduces lives in YAML with `source:` or `assumption:` and a row in `docs/assumptions.md`. Modelled outputs carry the label "synthetic demand, uncalibrated: scenario comparison, not a forecast".
