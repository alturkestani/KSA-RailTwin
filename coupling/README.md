> **Document version:** coupling/README.md v1.0 | 30 Oct 2026 | Author: R0 builder | Status: draft

# `coupling/` (W8, R4)

Will own the coupling to TrafficTwin Jeddah (W8): Jeddah decongestion measured with TrafficTwin's own matched-control SUMO runs (VHT, delay, teleport share, seed band), reading the TrafficTwin checkout through the `data/traffictwin` symlink without ever writing to it. National scale uses the graph/skim model, not SUMO. Owner: `sim-engineer`.

Status at R0: skeleton only (`uv run python -m coupling.cli version`). No methods are implemented or chosen here yet; the owning milestone decides them under the rules in `CLAUDE.md`, and every real-world constant it introduces lives in YAML with `source:` or `assumption:` and a row in `docs/assumptions.md`. Modelled outputs carry the label "synthetic demand, uncalibrated: scenario comparison, not a forecast".
