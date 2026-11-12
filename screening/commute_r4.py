# ruff: noqa: E501
"""R4 register updates for the screening funnel (CP4-5a and CP4 requirement 3).

1. `minutes`: the commute criterion on time instead of straight-line km (CP4-5a). For every register
   row and every metro anchor: free-flow road minutes (OSRM, national MLD files) and, where an
   existing line serves both ends (a station within A-screen-043's station radius of the town and of
   the metro anchor), the rail in-vehicle minutes between those stations from `access.railgraph`
   (S0 network, timetable factor applied). The commute measure is min(road, rail).
   The band in minutes (A-screen-042) is the straight-line band A-screen-005 (40-120 km) converted
   with the register's own median road minutes per straight-line km for rows near each band edge
   (computed here, never typed), so the CP1-approved intent is kept.
2. `roles`: explicit economic roles for the 24 created rows (`screening/created_roles_r4.yaml`,
   S-r4-roles-*). Only roles with confidence medium or high enter the register (A-screen-044);
   low-confidence (oasis-level) roles are recorded in the YAML, not scored.
3. `weights`: writes `cities/ksa/assumptions/screening_weights_r4.yaml` (the CP1 weights with the
   commute block switched to minutes); the funnel reads it with `--weights`.

  uv run python -m screening.commute_r4 minutes --seed 1
  uv run python -m screening.commute_r4 roles --seed 1
  uv run python -m screening.commute_r4 weights

Label: screening input, not a forecast.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import typer
import yaml

from common import REPO_ROOT
from common.labels import LABEL
from common.runmeta import seed_option, write_meta

REGISTER = Path("cities/ksa/candidates.parquet")
WEIGHTS = Path("cities/ksa/assumptions/screening_weights.yaml")
WEIGHTS_R4 = Path("cities/ksa/assumptions/screening_weights_r4.yaml")
MINUTES = Path("cities/ksa/zones/commute_minutes_r4.parquet")
ROLES = Path("screening/created_roles_r4.yaml")
OSRM_DIR = Path("data/ksa/osrm/gcc-states-latest")
STATION_RADIUS_KM = {"value": 10.0, "range": [5.0, 20.0], "assumption": "A-screen-043"}

app = typer.Typer(add_completion=False, help=__doc__, no_args_is_help=True)


@app.callback()
def _group() -> None:
    """R4 screening register updates."""


def _metros(root: Path) -> list[dict[str, Any]]:
    from screening.funnel import metro_table

    cfg = yaml.safe_load((root / WEIGHTS).read_text(encoding="utf-8"))
    return metro_table(pd.read_parquet(root / REGISTER), cfg)


def _rail_minutes(reg: pd.DataFrame, metros: list[dict[str, Any]], root: Path) -> np.ndarray:
    """(rows, metros) rail in-vehicle minutes on the S0 network where both ends have a station."""
    from access import railgraph
    from modechoice.coefficients import load_r3

    cfg = railgraph.load_cfg(root)
    sup = yaml.safe_load((root / railgraph.SUPPLY).read_text(encoding="utf-8"))
    fac = railgraph.factors(root)
    lines = railgraph.scenario_lines("S0", cfg, root)
    ontime = {k: float(v["value"]) for k, v in load_r3()["on_time"]["rail_by_line"].items()}
    svcs = [railgraph.build_service(ld, cfg, sup, fac, ontime, root) for ld in lines]
    g = railgraph.build_graph(svcs, lines, cfg)
    lat, lon = g.nodes.lat.to_numpy(), g.nodes.lon.to_numpy()
    rad = float(STATION_RADIUS_KM["value"])

    def near(la: float, lo: float) -> list[int]:
        d = railgraph.km_between(np.full(len(lat), lo), np.full(len(lat), la), lon, lat)
        return [int(i) for i in np.where(d <= rad)[0]]

    out = np.full((len(reg), len(metros)), np.nan)
    m_near = [
        sorted({i for a, b in zip(m["lat"], m["lon"], strict=True) for i in near(a, b)})
        for m in metros
    ]
    for r, (la, lo) in enumerate(
        zip(reg.lat.to_numpy(float), reg.lon.to_numpy(float), strict=True)
    ):
        t_near = near(la, lo)
        if not t_near:
            continue
        for j, mn in enumerate(m_near):
            best = np.inf
            for a in t_near:
                for b in mn:
                    if a != b:
                        tr = railgraph.trace(g, a, b)
                        if tr:
                            best = min(best, tr["ivt"] + tr["xfer_eq"])
            if np.isfinite(best):
                out[r, j] = best
    return out


@app.command("minutes")
def minutes_cmd(
    seed: int = seed_option(),
    osrm_dir: Path = typer.Option(OSRM_DIR),
    run_dir: Path = typer.Option(Path("runs/r4/screening/commute-minutes")),
    root: Path = typer.Option(REPO_ROOT, hidden=True),
) -> None:
    """Road (OSRM) and rail in-vehicle minutes from every register row to every metro anchor."""
    from network import osrm as osrm_mod
    from screening.funnel import haversine_km

    reg = pd.read_parquet(root / REGISTER)
    metros = _metros(root)
    anchors = [
        (j, a, b) for j, m in enumerate(metros) for a, b in zip(m["lat"], m["lon"], strict=True)
    ]
    src = reg[["lon", "lat"]].to_numpy(float)
    dst = np.array([[b, a] for _, a, b in anchors])
    with osrm_mod.server(root / osrm_dir, max_table=2000) as url:
        t = osrm_mod.table(url, src, dst, batch=200)
    road = np.full((len(reg), len(metros)), np.inf)
    road_km = np.full((len(reg), len(metros)), np.nan)
    for k, (j, _, _) in enumerate(anchors):
        dmin = t["duration_s"][:, k] / 60.0
        better = dmin < road[:, j]
        road[:, j] = np.where(better, dmin, road[:, j])
        road_km[:, j] = np.where(better, t["distance_m"][:, k] / 1000.0, road_km[:, j])
    rail = _rail_minutes(reg, metros, root)
    line_km = np.full((len(reg), len(metros)), np.inf)
    for j, m in enumerate(metros):
        line_km[:, j] = np.min(
            [
                haversine_km(reg.lat.to_numpy(float), reg.lon.to_numpy(float), a, b)
                for a, b in zip(m["lat"], m["lon"], strict=True)
            ],
            0,
        )
    rows = []
    for j, m in enumerate(metros):
        rows.append(
            pd.DataFrame(
                {
                    "row_key": reg.row_key,
                    "metro": m["name"],
                    "tier": m["tier"],
                    "line_km": line_km[:, j].round(2),
                    "road_min": road[:, j].round(2),
                    "road_km": road_km[:, j].round(2),
                    "rail_ivt_min": rail[:, j].round(2),
                    "commute_min": np.fmin(
                        road[:, j], np.where(np.isnan(rail[:, j]), np.inf, rail[:, j])
                    ).round(2),
                }
            )
        )
    df = pd.concat(rows, ignore_index=True)
    df.loc[df.road_min.isin([np.inf]), "road_min"] = np.nan
    (root / MINUTES).parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(root / MINUTES, index=False)
    band = minute_band(df, root)
    run = root / run_dir
    run.mkdir(parents=True, exist_ok=True)
    (run / "band.json").write_text(json.dumps(band, indent=1) + "\n")
    write_meta(
        run,
        seed,
        {"register": str(REGISTER), "station_radius": STATION_RADIUS_KM},
        extra={
            "band": band,
            "label": LABEL,
            "method": "OSRM table (free flow) + access.railgraph S0",
        },
    )
    typer.echo(json.dumps(band, indent=1))


def minute_band(df: pd.DataFrame, root: Path = REPO_ROOT) -> dict[str, Any]:
    """Convert A-screen-005 (km) to minutes: median road minutes per straight-line km of the row-
    metro pairs within +/-10 km of each band edge (road minutes from the OSRM table)."""
    cfg = yaml.safe_load((root / WEIGHTS).read_text(encoding="utf-8"))
    lo, hi = cfg["criteria"]["commute"]["band_km"]["value"]
    out: dict[str, Any] = {"band_km": [lo, hi], "assumption": "A-screen-042"}
    edges = []
    for e in (lo, hi):
        near = df[(df.line_km - e).abs() <= 10.0].dropna(subset=["road_min"])
        rate = float((near.road_min / near.line_km).median())
        edges.append(round(e * rate, 1))
        out[f"edge_{e}km"] = {
            "pairs": int(len(near)),
            "median_min_per_km": round(rate, 3),
            "minutes": round(e * rate, 1),
        }
    out["band_min"] = edges
    return out


@app.command("roles")
def roles_cmd(
    seed: int = seed_option(),
    run_dir: Path = typer.Option(Path("runs/r4/screening/roles")),
    root: Path = typer.Option(REPO_ROOT, hidden=True),
) -> None:
    """Apply the medium/high-confidence roles of created_roles_r4.yaml to the register."""
    doc = yaml.safe_load((root / ROLES).read_text(encoding="utf-8"))
    reg = pd.read_parquet(root / REGISTER)
    applied, recorded = 0, 0
    keys = set(reg.row_key)
    for r in doc["rows"]:
        if r["row_key"] not in keys:
            raise KeyError(f"{r['row_key']} not in the register")
        i = reg.index[reg.row_key == r["row_key"]][0]
        roles = [
            {"role": x["role"], "source": ";".join(x["sources"])}
            for x in r.get("roles", [])
            if x["confidence"] in doc["scored_confidence"]["value"]
        ]
        recorded += sum(
            1
            for x in r.get("roles", [])
            if x["confidence"] not in doc["scored_confidence"]["value"]
        )
        existing = [
            e for e in reg.at[i, "economic_roles"] if e["role"] not in {x["role"] for x in roles}
        ]
        reg.at[i, "economic_roles"] = list(existing) + roles
        applied += len(roles)
    reg.to_parquet(root / REGISTER, index=False)
    run = root / run_dir
    run.mkdir(parents=True, exist_ok=True)
    summary = {
        "rows": len(doc["rows"]),
        "roles_applied": applied,
        "roles_recorded_not_scored": recorded,
    }
    write_meta(run, seed, {"roles": doc}, extra={"summary": summary, "label": LABEL})
    typer.echo(json.dumps(summary))


@app.command("weights")
def weights_cmd(
    band_json: Path = typer.Option(Path("runs/r4/screening/commute-minutes/band.json")),
    root: Path = typer.Option(REPO_ROOT, hidden=True),
) -> None:
    """Write screening_weights_r4.yaml: CP1 weights, commute measured in minutes (A-screen-042/043)."""
    text = (root / WEIGHTS).read_text(encoding="utf-8")
    cfg = yaml.safe_load(text)
    band = json.loads((root / band_json).read_text(encoding="utf-8"))
    c = cfg["criteria"]["commute"]
    c["measure_kind"] = {"value": "minutes", "assumption_id": "A-screen-043"}
    c["measure"] = (
        "max over metros with min(road minutes, rail in-vehicle minutes where an existing line serves "
        "both ends) in the minute band of tier_factor * log10(metro pop) / log10(largest metro pop)"
    )
    c["band_min"] = {
        "value": band["band_min"],
        "unit": "min",
        "assumption_id": "A-screen-042",
        "derived_from": "A-screen-005 band (km) x the register's median road min per straight-line km at each edge",
    }
    c["minutes_file"] = {"value": str(MINUTES), "assumption_id": "A-screen-043"}
    head = (
        "# > **Document version:** cities/ksa/assumptions/screening_weights_r4.yaml v1.0 | 1 Nov 2026 | Author: R4 builder | Status: draft\n"
        "# Generated by `uv run python -m screening.commute_r4 weights` from screening_weights.yaml (CP1 weights unchanged)\n"
        "# with the commute criterion re-measured in minutes (CP4-5a). Do not edit by hand.\n"
    )
    (root / WEIGHTS_R4).write_text(
        head + yaml.safe_dump(cfg, sort_keys=False, allow_unicode=True, width=120), encoding="utf-8"
    )
    typer.echo(json.dumps(c["band_min"]))


if __name__ == "__main__":
    app()
