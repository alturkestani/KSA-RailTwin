"""CLI for `coupling` (R0 skeleton: `version` and `--seed` only; no modelling code yet)."""

from common.cli import make_app

app = make_app(
    "coupling",
    "TrafficTwin Jeddah coupling: matched-control decongestion runs on the read-only checkout.",
)

if __name__ == "__main__":
    app()
