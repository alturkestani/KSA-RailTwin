"""CLI for `optimise` (R0 skeleton: `version` and `--seed` only; no modelling code yet)."""

from common.cli import make_app

app = make_app("optimise", "Multi-objective optimisation, station siting and real-options phasing.")

if __name__ == "__main__":
    app()
