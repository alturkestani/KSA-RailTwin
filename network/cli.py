"""CLI for `network` (R0 skeleton: `version` and `--seed` only; no modelling code yet)."""

from common.cli import make_app

app = make_app(
    "network", "National graphs, road skims, distance fields, terrain classes and alignments."
)

if __name__ == "__main__":
    app()
