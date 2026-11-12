"""R7 inputs: the judge v3 scores that the fiscal exposure and the value-for-money logic read.

Programmes (CP7 layouts) use the R6_V3 full-judge scores `runs/r6/top5/<L>/score.json` as they
are. Corridors use a single-corridor judge v3 run at the phase the CP7 layouts give them: the
library already holds the 2030 runs (`runs/r6/v3/library/<id>/score.json`); the corridors phased
in 2050 are scored here, with the same frozen judge, into `runs/r7/corridors/<id>@<phase>/`.
Standalone corridor values do not add up to a layout (corridors compete for the same trips,
docs/r6-topology.md §0); the layout scores are the programme figures.

    uv run python -m funding.inputs score-corridors [--workers 4]
    uv run python -m funding.inputs list
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import typer
import yaml

from common import REPO_ROOT
from common.labels import LABEL

LAYOUTS = {"L2": "S6-L2", "L1": "S6-L1", "L3": "S6-L3"}  # CP7-1 order: cost-robust first
TOP5 = Path("runs/r6/top5")
LIBRARY = Path("runs/r6/v3/library")
OUT = Path("runs/r7/corridors")
S1_CBA = Path("runs/cba/CBA-S1-committed-programme")


def scenario(layout: str, root: Path = REPO_ROOT) -> dict[str, Any]:
    return yaml.safe_load((root / "scenarios" / f"{LAYOUTS[layout]}.yaml").read_text())


def corridor_phases(root: Path = REPO_ROOT) -> dict[str, int]:
    """Every distinct corridor of the CP7 layouts and its phase (identical in every layout)."""
    out: dict[str, int] = {}
    for lay in LAYOUTS:
        for c in scenario(lay, root)["layout"]["corridors"]:
            if out.setdefault(c["id"], int(c["phase"])) != int(c["phase"]):
                raise ValueError(f"{c['id']} has different phases across the CP7 layouts")
    return dict(sorted(out.items()))


# FIX_R7 (additive): score files that replace the default ones for a sensitivity build (alignment
# weights v2, `funding.r7v2`); empty for every R7 base figure.
OVERRIDES: dict[str, Path] = {}


def corridor_score_path(cid: str, phase: int, root: Path = REPO_ROOT) -> Path:
    if cid in OVERRIDES:
        return OVERRIDES[cid]
    lib = root / LIBRARY / cid / "score.json"
    if lib.exists() and phase in {int(p) for p in json.loads(lib.read_text())["phases"]}:
        return lib
    return root / OUT / f"{cid}@{phase}" / "score.json"


def layout_score_path(layout: str, root: Path = REPO_ROOT) -> Path:
    if layout in OVERRIDES:
        return OVERRIDES[layout]
    return root / TOP5 / layout / "score.json"


def load(path: Path) -> dict[str, Any]:
    d = json.loads(Path(path).read_text())
    if d.get("label") != LABEL:
        raise ValueError(f"{path}: missing the synthetic-demand label")
    return d


def judge_hash(path: Path) -> str:
    """The judge SHA-256 recorded in the run meta next to a score.json."""
    m = json.loads((Path(path).parent / "meta.json").read_text())
    return str(m.get("judge_sha256") or m.get("code_version", ""))


app = typer.Typer(add_completion=False, help=__doc__, no_args_is_help=True)


@app.command("list")
def list_cmd() -> None:
    """Print every CP7 corridor, its phase and the score file used."""
    for cid, ph in corridor_phases().items():
        p = corridor_score_path(cid, ph)
        typer.echo(f"{cid}\t{ph}\t{p.relative_to(REPO_ROOT)}\t{'ok' if p.exists() else 'MISSING'}")


@app.command("score-corridors")
def score_corridors(workers: int = typer.Option(4, "--workers")) -> None:
    """Score with the frozen judge v3 each CP7 corridor whose phase is not in the library."""
    from optimise import search

    for cid, ph in corridor_phases().items():
        p = corridor_score_path(cid, ph)
        if p.exists():
            typer.echo(f"have {p.relative_to(REPO_ROOT)}")
            continue
        out = p.parent
        out.mkdir(parents=True, exist_ok=True)
        lay = out / "layout.yaml"
        lay.write_text(
            yaml.safe_dump(
                {
                    "id": f"R7-{cid}@{ph}",
                    "layer": "hypothetical",
                    "base": "S1",
                    "source": "funding.inputs (R7 single-corridor score at its CP7 phase)",
                    "corridors": [{"id": cid, "phase": ph}],
                },
                sort_keys=False,
            )
        )
        s = search.run_judge(lay, out, workers=workers)
        typer.echo(f"scored {cid}@{ph}: robust NPV {s['robust_npv']:.0f} SAR m ({LABEL})")


if __name__ == "__main__":
    app()
