---
name: assumptions-register
description: How to record every behavioural, demand, cost, appraisal or data assumption (thresholds, weights, value of time, mode-choice coefficients, cost uplifts, discount rates, population growth, dwell times) in YAML and in docs/assumptions.md with source, range and status. Use whenever introducing a parameter that describes the real world rather than the code.
---
> **Document version:** skills/assumptions-register/SKILL.md v1.0 | 30 Oct 2026 | Author: coordinator | Status: active

# Assumptions register

Copied from TrafficTwin Jeddah with minimal changes; do not weaken it.

Every parameter that describes how Saudi Arabia, its travellers, its costs or its economy behave (not how the code behaves) must appear twice: in the YAML where it is used, and as a row in `docs/assumptions.md` (or `docs/assumptions-<track>.md` in a worktree; integration merges them).

Row format:
```
| id | parameter | value | unit | range | source or assumption | status | used in |
```
- `id`: `A-<area>-<nnn>` (e.g. `A-screen-004`, `A-cost-012`, `A-cba-003`, `A-demand-021`, `A-film-002`). Areas: data, screen, corridor, cost, rcf, cba, fund, social, demand, mode, access, sim, opt, viz, film, misc.
- `value`: the central value used; for ranges give P50 here and the P10/P90 in `range`.
- `status`: `assumed` | `sourced` | `calibrated`. Only calibration (R3 calibration) sets `calibrated`.
- `source`: URL or citation with year and access date (use the `source-citation` skill, cite the `S-xxx` id); for `assumed`, one sentence on the reasoning and the plausible range.
- `used in`: file paths (YAML and the module that reads it).

Rules
- Never bury a real-world constant in code. Load it from YAML under `cities/ksa/assumptions/*.yaml` or the module's `config/`.
- Every YAML parameter with a real-world meaning carries `source:` (citation id) or `assumption:` (free text + range). The pydantic loaders in `common/schemas.py` reject a parameter with neither.
- When replacing an assumption with a sourced value, keep the row and update it; the history lives in git.
- Thresholds and weights the brief says Tariq approves (population threshold 10k and the 5k sensitivity, corridor distance, commute band, economic-role list, weight sweep range, discount rates) are registered as `assumed` and marked `approval: pending CP1` in the notes until the checkpoint; after approval the row gets `approval: CP1 <date>`.
- Every report and every `runs/<id>/meta.json` lists the ids of all assumptions the run depended on, together with the label "synthetic demand, uncalibrated: scenario comparison, not a forecast".
- A number without a row or a source is a verifier FAIL (rule 1).

Check: `uv run python -m common.assumptions check` lists YAML parameters that lack a `source:`/`assumption:` or a register row; it must print nothing before a milestone is handed off.
