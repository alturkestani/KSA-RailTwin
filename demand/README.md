> **Document version:** demand/README.md v1.0 | 30 Oct 2026 | Author: R0 builder | Status: draft

# `demand/` (W8, R3)

Will own national demand (W8): zones at governorate level and finer around metros, population scenarios to 2050/2060 (GASTAT projections if published, UN WPP low/medium/high, Vision 2030 targets), giga-projects as explicit add-on scenarios (announced versus delivered), doubly-constrained gravity models by purpose, freight OD where data allows, and calibration to observed rail, air and bus totals (`gravity-calibration` skill). Owner: `demand-modeler`.

Status at R0: skeleton only (`uv run python -m demand.cli version`). No methods are implemented or chosen here yet; the owning milestone decides them under the rules in `CLAUDE.md`, and every real-world constant it introduces lives in YAML with `source:` or `assumption:` and a row in `docs/assumptions.md`. Modelled outputs carry the label "synthetic demand, uncalibrated: scenario comparison, not a forecast".
