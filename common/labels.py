"""The label every modelled output carries (rule 3) and the P10/P50/P90 range formatter.

CLI: `uv run python -m common.labels` prints the label; `... range 1.2 3.4 5.6 --unit "SAR bn"`.
"""

from __future__ import annotations

import typer

LABEL = "synthetic demand, uncalibrated: scenario comparison, not a forecast"
# FIX_R7 item 4d (additive): printed beside LABEL by every report module that shows a routed
# alignment, a cost or a running time built on one. Holds for the frozen weights v1 that every
# R4-R7 figure uses (docs/alignments.md §0, §4); terrain: Copernicus GLO-30, routed at 3" (~90 m).
ALIGNMENT_LIMITATION = (
    "alignments are indicative least-cost sketches on 30 m terrain whose mean lateral offset from "
    "real lines was 3–10 km on three reference lines; lengths within ±5 %; costs and running times "
    "inherit that uncertainty"
)

app = typer.Typer(add_completion=False, help="Labels and range formatting.")


def format_range(p10: float, p50: float, p90: float, unit: str = "", digits: int = 1) -> str:
    """'P10 1.2 / P50 3.4 / P90 5.6 SAR bn'. Costs and benefits are always ranges, never points."""
    if not p10 <= p50 <= p90:
        raise ValueError(f"expected P10 <= P50 <= P90, got {p10}, {p50}, {p90}")
    body = f"P10 {p10:,.{digits}f} / P50 {p50:,.{digits}f} / P90 {p90:,.{digits}f}"
    return f"{body} {unit}".rstrip()


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    if ctx.invoked_subcommand is None:
        typer.echo(LABEL)


@app.command("alignment")
def alignment_cmd() -> None:
    """Print the alignment-offset limitation (FIX_R7)."""
    typer.echo(ALIGNMENT_LIMITATION)


@app.command("range")
def range_cmd(
    p10: float,
    p50: float,
    p90: float,
    unit: str = typer.Option("", "--unit"),
    digits: int = typer.Option(1, "--digits"),
) -> None:
    """Format a P10/P50/P90 range."""
    typer.echo(format_range(p10, p50, p90, unit, digits))


if __name__ == "__main__":
    app()
