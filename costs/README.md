> **Document version:** costs/README.md v1.1 | 31 Oct 2026 | Author: cost-estimator (R1c) | Status: draft

# `costs/` (W3, R1c)

Cost register, price/FX index, corridor estimator and reference-class uplifts. Method, tables and sources: `docs/costs.md`. Every real-world value lives in YAML with a source id or an assumption id (`docs/assumptions.md`); nothing numeric about the world is in the code. Outputs are cost ranges at 2025 prices, not a budget, and every modelled output carries the label "synthetic demand, uncalibrated: scenario comparison, not a forecast".

| module | does |
|---|---|
| `register.py` | `validate` (schema, rules, every S- and A- id resolves, every money row has an index factor), `normalise --to SAR --price-year 2025` (writes `cost_register.normalised.yaml`, never edits the register), `list` |
| `index_build.py` | builds `cities/ksa/costs/index.yaml` from the manifest-registered World Bank and Eurostat series (A-cost-001, -002, -009) |
| `rcf.py` | draws capex, schedule and ridership multipliers from `cities/ksa/costs/uplifts.yaml`; `apply` writes P10/P50/P80/P90 and the full distribution; `show` |
| `estimate.py` | P10/P50/P90 capex, opex and renewals for one line YAML, every component traced to register ids (`trace.csv`), plus the uplifted P50/P80 and schedule overrun; `meta.json` via `common.runmeta` |
| `reconcile.py` | bottom-up vs top-down per line type on hypothetical reference shapes (A-cost-018); flags gaps > 30 % |
| `config/` | `estimate_map.yaml` (component → register id), `profiles.yaml` (default costing profile per line type), `reconcile.yaml` |

README command (fixture corridor; deterministic for a given seed):

```
uv run python -m costs.estimate --corridor tests/fixtures/corridor.yaml --register cities/ksa/costs/cost_register.yaml --uplifts cities/ksa/costs/uplifts.yaml --seed 1 --out runs/costs/fixture/
```

Other commands: `uv run python -m costs.register validate`, `uv run python -m costs.rcf show`, `uv run python -m costs.reconcile --seed 1 --out runs/costs/reconcile/`, `uv run python -m costs.index_build`, and `uv run python -m costs.cli version`.
