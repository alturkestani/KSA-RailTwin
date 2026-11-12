> **Document version:** access/README.md v1.0 | 30 Oct 2026 | Author: R0 builder | Status: draft

# `access/` (W8, R4)

Will own network evaluation (W8): the rail running-time model (acceleration–cruise–brake plus dwell, an explicit minute cost per stop) from line YAML, 30/45/60-minute commute-shed isochrones for every metro, and the 30-minute test for towns 40–120 km from each major city, checked against observed Haramain performance (`isochrone-commute` skill). Owner: `sim-engineer`.

Status at R0: skeleton only (`uv run python -m access.cli version`). No methods are implemented or chosen here yet; the owning milestone decides them under the rules in `CLAUDE.md`, and every real-world constant it introduces lives in YAML with `source:` or `assumption:` and a row in `docs/assumptions.md`. Modelled outputs carry the label "synthetic demand, uncalibrated: scenario comparison, not a forecast".
