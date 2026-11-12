# ruff: noqa: E501
"""Commute-shed isochrones per metro and scenario (R4 task 2; skill isochrone-commute).

For every metro of the CP1 list (A-screen-013) and every scenario (S0, S1, each S2-S5 candidate on
top of S1), on the R3 demand zones:
- boarding stations = every scenario station within the local catchment of the metro anchor zone
  (A-r4-acc-006) plus each line's nearest station within the access cap (A-demand-045); times are
  the best over them, so a new line never reduces reach; a metro without a station has no rail isochrone
  (reported, not dropped);
- in-vehicle isochrone: zones whose nearest station by road lies within the local station
  catchment (A-r4-acc-006) and is reached from the main station within 30/45/60 in-vehicle
  minutes (`access.railgraph`, mode ivt);
- door-to-door: road access to the main station + terminal minutes, the expected wait
  (headway/2 capped, A-access-010), rides, transfer walks and waits (mode minutes), egress by road
  + terminal; road access and egress carry the summer first/last-mile factor (A-access-011);
- car reference: free-flow road minutes x the peak factor (A-access-012).
Population (WPP medium, GASTAT-2024 anchored, 2025: the R3 calibration point) and jobs (R3 jobs
proxy, A-demand-003) reached per band.

  uv run python -m access.isochrones --metro jeddah --scenario S1 --minutes 30,45,60 \
      --mode door_to_door --seed 1 --out runs/access/S1/
  uv run python -m access.isochrones all --seed 1        (every metro x S0, S1 and candidates)

GeoJSON (dissolved zone polygons per band) under runs/access/<scenario>/<metro>/. Routing: NetworkX-
free scipy Dijkstra on the rail graph (no r5py/OTP installed). Label: synthetic demand,
uncalibrated: scenario comparison, not a forecast.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import typer
import yaml

from access import railgraph
from common import REPO_ROOT
from common.labels import LABEL
from common.runmeta import seed_option, write_meta

WEIGHTS = Path("cities/ksa/assumptions/screening_weights.yaml")
ZONES_GEOJSON = Path("cities/ksa/zones/zones.geojson")
POP = ("un_wpp_medium_gastat2024", 2025)
BANDS = (30, 45, 60, 90, 120)  # 90/120 door-to-door bands added in R5 (CP5 decision H9a)
SKILL_BANDS = (30, 45, 60)
SLUG = {
    "Riyadh": "riyadh",
    "Jeddah": "jeddah",
    "Makkah": "makkah",
    "Madinah": "madinah",
    "Dammam–Khobar–Dhahran": "dammam",
    "Taif": "taif",
    "Buraidah": "buraidah",
    "Tabuk": "tabuk",
    "Abha–Khamis Mushait": "abha_khamis",
    "Jazan": "jazan",
    "Najran": "najran",
}

app = typer.Typer(add_completion=False, help=__doc__)


def _v(node: Any) -> Any:
    return node["value"] if isinstance(node, dict) and "value" in node else node


def summer_factor(root: Path = REPO_ROOT) -> float:
    from modechoice.coefficients import load_r3

    sp = load_r3()["summer_penalty"]
    return 1.0 + float(sp["outdoor_share"]["rail"]) * (float(sp["multiplier"]["value"]) - 1.0)


def scenario_id(scenario: str, candidate: Path | None) -> str:
    return scenario if candidate is None else Path(candidate).stem


def candidate_list(root: Path = REPO_ROOT) -> list[tuple[str, Path]]:
    """(S2..S5, corridor path) for every candidate listed in scenarios/S2..S5.yaml."""
    out = []
    for s in ("S2", "S3", "S4", "S5"):
        d = yaml.safe_load((root / f"scenarios/{s}.yaml").read_text(encoding="utf-8"))
        out += [(s, Path(c)) for c in d.get("candidates", [])]
    return out


@dataclass
class Context:
    """One scenario's rail graphs and road skims, reused for every metro."""

    sid: str
    services: list[railgraph.Service]
    g_min: railgraph.Graph
    g_ivt: railgraph.Graph
    zst: pd.DataFrame  # zone_id, uid, to_min, from_min
    term: float
    cap: float
    summer: float
    zones: pd.DataFrame
    road: pd.DataFrame


def zones_table(root: Path = REPO_ROOT) -> pd.DataFrame:
    from demand.gravity import zone_population

    z = zone_population(POP[1], POP[0], root)
    base = pd.read_parquet(root / "runs/zones/zones.parquet")[["zone_id", "jobs_proxy", "metro"]]
    return z[["zone_id", "population", "parent_gov", "region"]].merge(base, on="zone_id")


def context(
    scenario: str,
    candidate: Path | None = None,
    root: Path = REPO_ROOT,
    factor_case: str = "value",
    zones: pd.DataFrame | None = None,
    road: pd.DataFrame | None = None,
) -> Context:
    from modechoice.coefficients import load_r3

    cfg = railgraph.load_cfg(root)
    sup = yaml.safe_load((root / railgraph.SUPPLY).read_text(encoding="utf-8"))
    fac = railgraph.factors(root)
    ontime = {k: float(v["value"]) for k, v in load_r3()["on_time"]["rail_by_line"].items()}
    base = "S0" if scenario == "S0" else "S1"
    lines = railgraph.scenario_lines(base, cfg, root, candidate)
    svcs = [
        railgraph.build_service(ld, cfg, sup, fac, ontime, root, factor_case=factor_case)
        for ld in lines
    ]
    conn = set(_v(cfg.get("connector_lines", {"value": []})))
    g_min = railgraph.build_graph(svcs, lines, cfg, "minutes")
    g_ivt = railgraph.build_graph(svcs, lines, cfg, "ivt")
    zst = railgraph.zone_station_times(svcs, root)
    zst = zst[~zst.line_id.isin(conn)]  # connector stations are not boarding points
    if road is None:
        road = pd.read_parquet(root / "runs/skims/r3-zones/road.parquet")
    return Context(
        scenario_id(scenario, candidate),
        svcs,
        g_min,
        g_ivt,
        zst,
        float(_v(sup["rail"]["terminal_min"])),
        float(_v(sup["rail"]["station_access"]["max_road_min"])),
        summer_factor(root),
        zones if zones is not None else zones_table(root),
        road,
    )


def metros(root: Path = REPO_ROOT) -> list[dict[str, Any]]:
    from screening.funnel import metro_table

    cfg = yaml.safe_load((root / WEIGHTS).read_text(encoding="utf-8"))
    return metro_table(pd.read_parquet(root / "cities/ksa/candidates.parquet"), cfg)


def anchor_zone(m: dict[str, Any], root: Path = REPO_ROOT) -> str:
    """Zone containing the metro's first anchor point."""
    import geopandas as gpd

    zg = gpd.read_file(root / ZONES_GEOJSON)[["zone_id", "geometry"]]
    pt = gpd.GeoDataFrame(geometry=gpd.points_from_xy([m["lon"][0]], [m["lat"][0]]), crs=4326)
    j = gpd.sjoin(pt, zg, predicate="within")
    return str(j.zone_id.iloc[0])


def origin_stations(ctx: Context, az: str, local: float) -> pd.DataFrame:
    """Boarding stations of a metro: every station within the local catchment of the anchor zone
    (A-r4-acc-006) plus each line's nearest station within the access cap (A-demand-045), so a
    new line never removes a boarding station."""
    acc = ctx.zst[(ctx.zst.zone_id == az) & (ctx.zst.to_min <= ctx.cap)].sort_values("to_min")
    loc = acc[acc.to_min <= local]
    per_line = acc.groupby("line_id").head(1)  # each line's nearest station within the cap
    return pd.concat([loc, per_line]).drop_duplicates("uid").sort_values("to_min")


def zone_times(ctx: Context, az: str) -> pd.DataFrame | None:
    """Per zone: rail door-to-door minutes and in-vehicle minutes from the metro anchor zone (best
    over the metro's boarding stations), and car peak minutes. NaN rail columns when the metro has
    no station within the access cap."""
    cfg = railgraph.load_cfg(REPO_ROOT)
    peak = float(_v(cfg["car_peak_factor"]))
    local = float(_v(cfg["station_catchment_road_min"]))
    z = ctx.zones[["zone_id"]].copy()
    r = ctx.road[ctx.road.o == az].set_index("d")["min"]
    z["car_peak_min"] = z.zone_id.map(r).to_numpy(float) * peak
    acc = origin_stations(ctx, az, local)
    if acc.empty:
        z["d2d_min"] = np.nan
        z["ivt_min"] = np.nan
        z["main_station"] = None
        return z
    uid_ix = {u: k for k, u in enumerate(ctx.g_min.nodes.uid)}
    origins = [(uid_ix[o.uid], (float(o.to_min) + ctx.term) * ctx.summer) for o in acc.itertuples()]
    eg = ctx.zst[ctx.zst.from_min <= ctx.cap].copy()
    eg["ix"] = eg.uid.map(uid_ix)
    ix = eg.ix.to_numpy()
    egress = ((eg.from_min + ctx.term) * ctx.summer).to_numpy()
    d2d = np.min([t_acc + ctx.g_min.gen[a][ix] + egress for a, t_acc in origins], axis=0)
    eg["d2d"] = d2d
    best = eg.groupby("zone_id").d2d.min()
    # in-vehicle: best over every station within the zone's local catchment and every boarding
    # station of the metro (0 for zones in a boarding station's own catchment)
    loc = eg[eg.from_min <= local].copy()
    lix = loc.ix.to_numpy()
    v = np.min([ctx.g_ivt.gen[a][lix] for a, _ in origins], axis=0)
    v[np.isin(lix, [a for a, _ in origins])] = 0.0
    loc["ivt"] = v
    ivt = loc.groupby("zone_id").ivt.min()
    z["d2d_min"] = z.zone_id.map(best).to_numpy(float)
    z["ivt_min"] = z.zone_id.map(ivt).to_numpy(float)
    z.loc[~np.isfinite(z.d2d_min), "d2d_min"] = np.nan
    z.loc[~np.isfinite(z.ivt_min), "ivt_min"] = np.nan
    z["main_station"] = "|".join(acc.uid)
    return z


def reached(ctx: Context, m: dict[str, Any], az: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    zt = zone_times(ctx, az)
    zz = zt.merge(ctx.zones, on="zone_id")
    own = zz.metro.eq(m["name"])
    rows = []
    for mode, col in (
        ("in_vehicle", "ivt_min"),
        ("door_to_door", "d2d_min"),
        ("car_peak", "car_peak_min"),
    ):
        for b in BANDS:
            hit = zz[col] <= b
            rows.append(
                {
                    "scenario": ctx.sid,
                    "metro": m["name"],
                    "tier": m["tier"],
                    "mode": mode,
                    "band_min": b,
                    "main_station": zt.main_station.iloc[0],
                    "zones": int(hit.sum()),
                    "population": float(zz.loc[hit, "population"].sum()),
                    "jobs": float(zz.loc[hit, "jobs_proxy"].sum()),
                    "population_outside_metro": float(zz.loc[hit & ~own, "population"].sum()),
                    "jobs_outside_metro": float(zz.loc[hit & ~own, "jobs_proxy"].sum()),
                }
            )
    return pd.DataFrame(rows), zz


def write_geojson(
    zz: pd.DataFrame, run: Path, m: dict[str, Any], sid: str, root: Path
) -> list[str]:
    import geopandas as gpd

    zg = gpd.read_file(root / ZONES_GEOJSON)[["zone_id", "geometry"]]
    out = []
    for mode, col in (("in_vehicle", "ivt_min"), ("door_to_door", "d2d_min")):
        feats = []
        for b in BANDS:
            ids = set(zz.loc[zz[col] <= b, "zone_id"])
            if not ids:
                continue
            geom = zg[zg.zone_id.isin(ids)].geometry.union_all().simplify(0.005)
            feats.append(
                {
                    "band_min": b,
                    "mode": mode,
                    "metro": m["name"],
                    "scenario": sid,
                    "population": float(zz.loc[zz.zone_id.isin(ids), "population"].sum()),
                    "label": LABEL,
                    "geometry": geom,
                }
            )
        if feats:
            gdf = gpd.GeoDataFrame(feats, crs=4326)
            p = run / f"isochrone_{mode}.geojson"
            gdf.to_file(p, driver="GeoJSON")
            out.append(str(p.relative_to(root)))
    return out


def run_scenario(
    scenario: str,
    candidate: Path | None,
    ms: list[dict[str, Any]],
    azs: dict[str, str],
    root: Path,
    seed: int,
    out_root: Path,
    geo: str = "changed",
    ref: pd.DataFrame | None = None,
    zones: pd.DataFrame | None = None,
    road: pd.DataFrame | None = None,
) -> pd.DataFrame:
    ctx = context(scenario, candidate, root, zones=zones, road=road)
    run = root / out_root / ctx.sid
    run.mkdir(parents=True, exist_ok=True)
    tabs = []
    geos: dict[str, Any] = {}
    for m in ms:
        tab, zz = reached(ctx, m, azs[m["name"]])
        tabs.append(tab)
        changed = True
        if ref is not None:
            r = ref[ref.metro == m["name"]].sort_values(["mode", "band_min"]).population.to_numpy()
            changed = not np.allclose(
                r, tab.sort_values(["mode", "band_min"]).population.to_numpy()
            )
        if geo == "all" or (geo == "changed" and changed):
            d = run / SLUG[m["name"]]
            d.mkdir(parents=True, exist_ok=True)
            geos[m["name"]] = write_geojson(zz, d, m, ctx.sid, root)
        else:
            geos[m["name"]] = "same as S1 (reached population unchanged)"
    df = pd.concat(tabs, ignore_index=True)
    df["candidate"] = str(candidate) if candidate else None
    df.to_parquet(run / "reached.parquet", index=False)
    write_meta(
        run,
        seed,
        {
            "scenario": scenario,
            "candidate": str(candidate),
            "population": POP,
            "network": railgraph.load_cfg(root),
        },
        extra={
            "label": LABEL,
            "geojson": geos,
            "routing": "scipy dijkstra on the rail graph (minutes / ivt)",
        },
    )
    return df


@app.command("all")
def all_cmd(
    seed: int = seed_option(),
    out: Path = typer.Option(Path("runs/access")),
    root: Path = typer.Option(REPO_ROOT, hidden=True),
) -> None:
    """Every metro x S0, S1 and every S2-S5 candidate; GeoJSON for S0, S1 and changed metros."""
    ms = metros(root)
    azs = {m["name"]: anchor_zone(m, root) for m in ms}
    zones = zones_table(root)
    road = pd.read_parquet(root / "runs/skims/r3-zones/road.parquet")
    frames = [run_scenario("S0", None, ms, azs, root, seed, out, "all", zones=zones, road=road)]
    s1 = run_scenario("S1", None, ms, azs, root, seed, out, "all", zones=zones, road=road)
    frames.append(s1)
    for fam, c in candidate_list(root):
        df = run_scenario(
            fam, c, ms, azs, root, seed, out, "changed", ref=s1, zones=zones, road=road
        )
        df["family"] = fam
        frames.append(df)
    allr = pd.concat(frames, ignore_index=True)
    summ = root / out / f"isochrones-summary-s{seed}"
    summ.mkdir(parents=True, exist_ok=True)
    allr.to_parquet(summ / "reached_all.parquet", index=False)
    write_meta(
        summ, seed, {"scenarios": sorted(allr.scenario.unique().tolist())}, extra={"label": LABEL}
    )
    typer.echo(f"{allr.scenario.nunique()} scenarios x {allr.metro.nunique()} metros -> {summ}")


@app.callback(invoke_without_command=True)
def main(
    ctx_: typer.Context,
    metro: str | None = typer.Option(None, "--metro", help="|".join(SLUG.values())),
    scenario: str = typer.Option("S1", "--scenario"),
    candidate: Path | None = typer.Option(None, "--candidate"),
    minutes: str = typer.Option("30,45,60", "--minutes"),
    mode: str = typer.Option("door_to_door", "--mode", help="door_to_door | in_vehicle"),
    seed: int = seed_option(),
    out: Path = typer.Option(Path("runs/access"), "--out"),
    root: Path = typer.Option(REPO_ROOT, hidden=True),
) -> None:
    """Single metro / scenario (the skill's command form); `all` runs the full set."""
    if ctx_.invoked_subcommand is not None:
        return
    if metro is None:
        raise typer.BadParameter("--metro is required (or use the `all` command)")
    if tuple(int(x) for x in minutes.split(",")) not in (SKILL_BANDS, BANDS):
        raise typer.BadParameter("bands are 30,45,60 (skill isochrone-commute) or 30,...,120 (H9a)")
    ms = [m for m in metros(root) if SLUG[m["name"]] == metro]
    azs = {m["name"]: anchor_zone(m, root) for m in ms}
    out_root = out.parent if re.fullmatch(r"S\d.*", out.name) else out
    df = run_scenario(scenario, candidate, ms, azs, root, seed, out_root, "all")
    typer.echo(df[df["mode"] == mode].to_string(index=False))


if __name__ == "__main__":
    app()
