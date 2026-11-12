"""CLI for `demand` (R0 skeleton: `version` and `--seed` only; no modelling code yet)."""

from common.cli import make_app

app = make_app(
    "demand",
    "Zones, population scenarios to 2060, giga-project add-ons, gravity demand, calibration.",
)

if __name__ == "__main__":
    app()
