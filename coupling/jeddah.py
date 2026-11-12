# ruff: noqa: E501
"""Jeddah decongestion coupling with TrafficTwin (R4 task 4; W8).

TrafficTwin (read-only checkout) simulates Jeddah residents' internal trips (synthetic population, no
external or through demand; TrafficTwin docs/fidelity.md). What it can represent of a rail scenario
is the car shift between rail-station catchments inside the city. This module:
1. computes the modelled shift share from the R4 demand runs: the rail share of the Jeddah <-> Jeddah
   zone pairs whose rail path uses the in-city stations (A-r4-cpl-001);
2. writes TrafficTwin policy YAML (`pt_line`, TrafficTwin's docs/policies.md style) for every
   Jeddah-related rail family and validates it with TrafficTwin's own pydantic `Policy` model
   (imported read-only, no bytecode written);
3. marks the families TrafficTwin cannot represent (fewer than two stations inside its network:
   commuter belts, trunk lines whose only in-city station is the terminal) as not runnable;
4. prints / runs the exact matched-control command from the TrafficTwin checkout with
   `--runs-dir` in this repo, and parses `policy_report.json` (VHT, delay, teleports).

  uv run python -m coupling.jeddah policies --seed 1
  uv run python -m coupling.jeddah command --policy r4_hhr_jeddah_kaia
  uv run python -m coupling.jeddah report --seed 1

Label: synthetic demand, uncalibrated: scenario comparison, not a forecast.
"""

from __future__ import annotations

import glob
import json
import os
import sys
from pathlib import Path
from typing import Any

import pandas as pd
import typer
import yaml

from common import REPO_ROOT
from common.labels import LABEL
from common.runmeta import seed_option, write_meta

# The read-only TrafficTwin checkout; TRAFFICTWIN overrides it (as in scripts/link_data.sh). The
# public repository runs without it: the coupling test skips and `make demo` never needs it.
TRAFFICTWIN = Path(
    os.path.expanduser(os.environ.get("TRAFFICTWIN", "~/Documents/Projects/TrafficTwin"))
)
POLICY_DIR = Path("coupling/policies")
RUNS = Path("runs/coupling")
CFG = Path("cities/ksa/assumptions/access_coupling.yaml")

app = typer.Typer(add_completion=False, help=__doc__, no_args_is_help=True)


@app.callback()
def _group() -> None:
    """TrafficTwin coupling."""


def _v(node: Any) -> Any:
    return node["value"] if isinstance(node, dict) and "value" in node else node


def load_cfg(root: Path = REPO_ROOT) -> dict[str, Any]:
    return yaml.safe_load((root / CFG).read_text(encoding="utf-8"))


def traffictwin_policy_model() -> Any:
    """TrafficTwin's `sim.schemas.Policy`, imported read-only (no .pyc written)."""
    sys.dont_write_bytecode = True
    if str(TRAFFICTWIN) not in sys.path:
        sys.path.insert(0, str(TRAFFICTWIN))
    from sim.schemas import Policy  # type: ignore[import-not-found]

    return Policy


def shift_share(run_dir: Path, stations: list[str], root: Path = REPO_ROOT) -> dict[str, float]:
    """Rail share of Jeddah <-> Jeddah zone pairs whose rail path boards and alights at the given
    in-city stations (R4 demand run, all purposes)."""
    z = pd.read_parquet(root / "runs/zones/zones.parquet")[["zone_id", "metro"]]
    jz = set(z[z.metro == "Jeddah"].zone_id)
    d = pd.concat([pd.read_parquet(f) for f in glob.glob(str(root / run_dir / "od_*.parquet"))])
    j = d[d.o.isin(jz) & d.d.isin(jz)]
    k = j[j.rail_station_o.isin(stations) & j.rail_station_d.isin(stations)]
    return {
        "pairs_trips": float(k.trips.sum()),
        "rail_trips": float(k.trips_rail.sum()),
        "rail_share": float(k.trips_rail.sum() / k.trips.sum()) if len(k) else 0.0,
        "jeddah_jeddah_trips": float(j.trips.sum()),
    }


def build_policies(root: Path = REPO_ROOT) -> list[dict[str, Any]]:
    cfg = load_cfg(root)
    out = []
    for fam in cfg["families"]:
        rec: dict[str, Any] = {
            "id": fam["id"],
            "family": fam["family"],
            "scenario": fam["scenario"],
            "runnable": bool(fam["runnable"]),
        }
        if not fam["runnable"]:
            rec["reason"] = fam["reason"]
            out.append(rec)
            continue
        sh = shift_share(Path(fam["share_from_run"]), fam["share_stations"], root)
        share = round(sh["rail_share"], 4)
        pol = {
            "id": fam["id"],
            "kind": "policy",
            "title": fam["title"],
            "daytype": "weekday",
            "transforms": [
                {
                    "type": "pt_line",
                    "line_id": fam["line_id"],
                    "both_directions": True,
                    "headway_s": float(_v(fam["headway_s"])),
                    "hours": list(_v(fam["hours"])),
                    "catchment_m": float(_v(cfg["catchment_m"])),
                    "shift_share": share,
                    "shift_modes": ["car", "chauffeured", "ridehail"],
                    "stop_duration_s": float(_v(fam["stop_duration_s"])),
                    "stops": fam["stops"],
                    "assumption": (
                        f"A-r4-cpl-001: shift_share {share} = modelled rail share of Jeddah <-> Jeddah "
                        f"zone pairs using {', '.join(fam['share_stations'])} in {fam['share_from_run']} "
                        "(synthetic demand, uncalibrated). A-r4-cpl-002: catchment. A-r4-cpl-003: TrafficTwin "
                        "represents the line as buses at the rail headway (a conservative road-load proxy; "
                        "a train adds no road vehicles)."
                    ),
                }
            ],
            "notes": f"{LABEL}. Generated by coupling.jeddah from {fam['share_from_run']}.",
        }
        rec.update({"shift": sh, "policy": pol, "path": str(POLICY_DIR / f"{fam['id']}.yaml")})
        out.append(rec)
    return out


@app.command("policies")
def policies_cmd(
    seed: int = seed_option(),
    root: Path = typer.Option(REPO_ROOT, hidden=True),
) -> None:
    """Write and validate the TrafficTwin policy YAMLs (coupling/policies/)."""
    model = traffictwin_policy_model()
    recs = build_policies(root)
    (root / POLICY_DIR).mkdir(parents=True, exist_ok=True)
    for r in recs:
        if not r["runnable"]:
            continue
        model.model_validate(r["policy"])
        head = (
            f"# > **Document version:** {r['path']} v1.0 | 1 Nov 2026 | Author: R4 builder (sim-engineer) | "
            "Status: draft\n# TrafficTwin policy (policy-yaml style), generated by `uv run python -m coupling.jeddah "
            f"policies`; validated with TrafficTwin sim.schemas.Policy. {LABEL}.\n"
        )
        (root / r["path"]).write_text(
            head + yaml.safe_dump(r["policy"], sort_keys=False, width=110), encoding="utf-8"
        )
    summary = [{k: v for k, v in r.items() if k != "policy"} for r in recs]
    run = root / RUNS / f"policies-s{seed}"
    run.mkdir(parents=True, exist_ok=True)
    (run / "policies.json").write_text(json.dumps(summary, indent=1) + "\n")
    write_meta(run, seed, {"coupling": load_cfg(root)}, extra={"label": LABEL, "policies": summary})
    typer.echo(json.dumps(summary, indent=1))


def command(policy: str, seed: int = 1, root: Path = REPO_ROOT) -> str:
    p = (root / POLICY_DIR / f"{policy}.yaml").resolve()
    runs = (root / RUNS).resolve()
    return (
        f"cd {TRAFFICTWIN} && PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m sim.runner "
        f"--policy {p} --daytype weekday --sample 0.10 --seed {seed} --runs-dir {runs}"
    )


@app.command("command")
def command_cmd(policy: str = typer.Option(...), seed: int = seed_option()) -> None:
    """Print the exact TrafficTwin command (outputs under runs/coupling/)."""
    typer.echo(command(policy, seed))


def kpis(run: Path) -> dict[str, Any]:
    rep = json.loads((run / "policy_report.json").read_text(encoding="utf-8"))
    return rep


@app.command("report")
def report_cmd(
    seed: int = seed_option(),
    root: Path = typer.Option(REPO_ROOT, hidden=True),
) -> None:
    """Collect the policy reports under runs/coupling/ into runs/coupling/summary-s<seed>.json."""
    out = {}
    for rep in sorted((root / RUNS).glob("*/policy_report.json")):
        out[rep.parent.name] = json.loads(rep.read_text(encoding="utf-8"))
    p = root / RUNS / f"summary-s{seed}.json"
    p.write_text(json.dumps(out, indent=1, default=str) + "\n")
    typer.echo(json.dumps({k: list(v)[:12] for k, v in out.items()}, indent=1))


if __name__ == "__main__":
    app()
