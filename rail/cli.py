"""CLI for `rail` (R0 skeleton: `version` and `--seed` only; no modelling code yet)."""

from common.cli import make_app

app = make_app(
    "rail",
    "Rail layers: line and timetable YAML for the existing, committed and hypothetical layers.",
)

if __name__ == "__main__":
    app()
