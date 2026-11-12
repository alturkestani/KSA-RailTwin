"""CLI for `access` (R0 skeleton: `version` and `--seed` only; no modelling code yet)."""

from common.cli import make_app

app = make_app("access", "Running-time model, commute-shed isochrones and the 30-minute test.")

if __name__ == "__main__":
    app()
