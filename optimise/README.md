> **Document version:** optimise/README.md v1.0 | 30 Oct 2026 | Author: R0 builder | Status: draft

# `optimise/` (W9, R6)

Will own optimisation and phasing (W9): the Pareto front over NPV/BCR, coverage and equity, emissions, fiscal exposure and risk; decision variables for corridors, alignments, station siting (p-median or coverage with a through-passenger time penalty), technology, stopping patterns, frequencies and fares; real-options sequencing with stage-gates; and robustness across Monte Carlo draws (`pareto-optimizer` skill). Owner: `optimizer`.

Status at R0: skeleton only (`uv run python -m optimise.cli version`). No methods are implemented or chosen here yet; the owning milestone decides them under the rules in `CLAUDE.md`, and every real-world constant it introduces lives in YAML with `source:` or `assumption:` and a row in `docs/assumptions.md`. Modelled outputs carry the label "synthetic demand, uncalibrated: scenario comparison, not a forecast".
