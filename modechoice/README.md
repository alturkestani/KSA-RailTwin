> **Document version:** modechoice/README.md v0.1 | 31 Oct 2026 | Author: mode-choice-modeler (R3) | Status: draft

# modechoice

Multinomial logit mode choice over car, rail, air and bus (W8). Coefficients from `cities/ksa/assumptions/mode_choice_priors.yaml` (read-only, "coefficients literature-based until survey results exist"); R3 parameters in `cities/ksa/assumptions/mode_choice_r3.yaml` (A-mode-021…041). Every output: "synthetic demand, uncalibrated: scenario comparison, not a forecast". Method, coefficients, sweep results and the API: `docs/mode-choice.md`.

```
uv run python -m modechoice.cli version
uv run python -m modechoice.cli pairs  --seed 1 --out runs/r3/modechoice/pairs-s1/
uv run python -m modechoice.cli shares --od runs/r3/modechoice/pairs-s1/pairs.parquet --seed 1 --out runs/r3/modechoice/shares-pairs-s1/
uv run python -m modechoice.cli sweep  --seed 1 --out runs/r3/modechoice/sweep/
uv run pytest tests/test_modechoice_mnl.py
```

Modules: `coefficients.py` (priors loader, sweep corners, `apply_overrides` calibration hook), `mnl.py` (utilities, shares, logsum, consumer-surplus change), `pairs.py` (attribute builder from skims, line data and the R3 YAML; representative pairs), `sweep.py` (one-at-a-time, joint, settings and input variants; monotonicity; rank stability; band; scenario vs matched baseline), `cli.py`.
