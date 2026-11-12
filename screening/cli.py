"""CLI for `screening` (R0 skeleton: `version` and `--seed` only; no modelling code yet)."""

from common.cli import make_app

app = make_app(
    "screening",
    "National screening: region sweeps, candidate register, funnel, corridors, coverage.",
)

if __name__ == "__main__":
    app()
