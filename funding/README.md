> **Document version:** funding/README.md v1.2 | 4 Nov 2026 | Author: R1d builder; R7 builder (fiscal, vfm, inputs, recommend, report, risk-matrix build) | Status: draft

# `funding/` (W6, R1d and R7)

Funding, ownership and delivery models (W6, `ppp-structuring` skill). An options landscape with evidence, not a recommendation for any entity (rule 9). Owner: `funding-ppp-analyst`. The narrative is `docs/funding.md`.

| module | what it does | command |
|---|---|---|
| `models.py` | schema and validation of the options register `cities/ksa/funding/models.yaml`: the 13 required options plus at least one `hybrid_*` (with `mix:`), the seven risk keys, sourced term ranges, every cited S-id resolving to a row in `docs/sources/*.csv` | `uv run python -m funding.models validate` |
| `risk_matrix.py` | schema of the risk-allocation matrix: the template `cities/ksa/funding/risk_matrix_template.yaml` (empty allocations, the five fiscal-exposure metric definitions) and the filled `risk_matrix_<corridor>.yaml` of R7 (exactly one `x` per row, mechanism and precedents named); Markdown rendering | `uv run python -m funding.risk_matrix validate`, `... render` |
| `inputs.py` | R7 inputs: the CP7 corridors and phases, the judge v3 score per corridor (library at 2030; `runs/r7/corridors/<id>@2050/` scored here with the frozen judge) and per programme (`runs/r6/top5/<L>/`) | `uv run python -m funding.inputs score-corridors` |
| `fiscal.py` | fiscal exposure per corridor and programme by model: upfront public capex, net fiscal cost 30/40/60 y, budget share, contingent liabilities, timing (P10/P50/P90) → `runs/r7/fiscal/fiscal.json` | `uv run python -m funding.fiscal build --seed 1` |
| `vfm.py` | PSC vs availability PPP, one-at-a-time ranges, switching values (Brent), rate sensitivity → `runs/r7/vfm/vfm.json` | `uv run python -m funding.vfm build --seed 1` |
| `risk_matrix.py build` | fills the template per corridor × model from the allocation rules (`funding_r7.yaml`) and the run evidence | `uv run python -m funding.risk_matrix build --corridor <id> --model <id> --out ...`; `... build-all` |
| `recommend.py` | `cities/ksa/funding/recommendations.yaml` (judgement + generated evidence + legal items) | `uv run python -m funding.recommend build` |
| `report.py` | `docs/fiscal-exposure.md`, `docs/delivery-models.md` from the run outputs | `uv run python -m funding.report write` |
| `sources.py` | S-id lookup across `docs/sources/*.csv` | — |
| `cli.py` | `version`, `models-validate`, `risk-validate` | `uv run python -m funding.cli --help` |

Tests: `tests/test_funding_models.py`, `tests/test_funding_risk_matrix.py`, `tests/test_funding_r7_fiscal.py`, `tests/test_funding_r7_vfm.py`, `tests/test_funding_r7_matrix.py` (fictional fixtures inline, plus the real files).

R7 pipeline (the README command for R7; about 3 minutes for the judge runs, seconds for the rest; needs `judge/v3-variants` and the R6_V3 runs):

```
uv run python -m funding.inputs score-corridors && uv run python -m funding.fiscal build --seed 1 && uv run python -m funding.vfm build --seed 1 && uv run python -m funding.risk_matrix build-all && uv run python -m funding.recommend build && uv run python -m funding.report write
```

Label: synthetic demand, uncalibrated: scenario comparison, not a forecast.
