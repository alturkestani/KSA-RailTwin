"""GEO_VERIFY CLI (`.claude/skills/geo-verify/SKILL.md`).

Run with rasterio available:
  uv run --with rasterio python -m screening.geo_verify.cli backtest --seed 1
  uv run --with rasterio python -m screening.geo_verify.cli estimate --seed 1 --which no-pop
  uv run --with rasterio python -m screening.geo_verify.cli stations --seed 1
  uv run python -m screening.geo_verify.cli seat --seed 1 --name Al-Qarā ...
  uv run python -m screening.geo_verify.cli validate-geocodes --seed 1
  uv run python -m screening.geo_verify.cli served-rerun --seed 1
Outputs go to runs/geo_verify/<command>/ with meta.json and method_log.jsonl.
Labels: synthetic demand, uncalibrated: scenario comparison, not a forecast (population
estimates are derived evidence, never an official figure).
"""

from __future__ import annotations

import glob
import json
import subprocess
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import typer
import yaml

from common import REPO_ROOT
from common.runmeta import rng, seed_option, write_meta
from screening.geo_verify import estimators, footprints, geom, imagery, method_log

app = typer.Typer(add_completion=False, help="Geospatial verification and estimation.")
PARAMS = Path(__file__).with_name("params.yaml")
SITES = Path(__file__).with_name("station_sites.yaml")
REGISTERS = "cities/ksa/regions/archive/pilot/pilot-*.parquet"
RUNS = REPO_ROOT / "runs" / "geo_verify"


def _cfg(path: Path = PARAMS) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _v(node: Any) -> Any:
    return node["value"] if isinstance(node, dict) and "value" in node else node


def params(cfg: dict) -> estimators.Params:
    e, o = cfg["extent"], cfg["occupancy"]
    return estimators.Params(
        eps_m=_v(e["eps_m"]),
        min_samples=_v(e["min_samples"]),
        snap_m=_v(e["snap_m"]),
        close_kernel=_v(e["close_kernel"]),
        min_area_m2=_v(e["min_area_m2"]),
        window_km=_v(e["window_km"]),
        hh_size=_v(o["hh_size"]),
        dwellings_per_building=_v(o["dwellings_per_building"]),
        residential_share=_v(o["residential_share"]),
    )


def register(root: Path = REPO_ROOT, pattern: str = REGISTERS) -> pd.DataFrame:
    """Register rows of every file matching `pattern` (default: the pilot registers; R2 passes
    e.g. cities/ksa/regions/northern_borders.parquet)."""
    parts = []
    for f in sorted(glob.glob(str(root / pattern))):
        d = pd.read_parquet(f)
        d["register_file"] = str(Path(f).relative_to(root))
        d["row_in_file"] = range(len(d))
        parts.append(d)
    return pd.concat(parts, ignore_index=True)


def bbox_km(lat: float, lon: float, km: float) -> tuple[float, float, float, float]:
    dlat = km / 110.574
    dlon = km / (111.320 * np.cos(np.radians(lat)))
    return lon - dlon, lat - dlat, lon + dlon, lat + dlat


def estimate_one(
    lat: float, lon: float, cfg: dict, p: estimators.Params, index: pd.DataFrame, dl_log: list
) -> dict[str, Any]:
    """Extent + both estimators for one settlement point."""
    g = cfg["gates"]
    bb = bbox_km(lat, lon, p.window_km)
    tiles = []
    for qk in footprints.quadkeys_bbox(bb):
        df, rec = footprints.tile(
            qk, index, imagery.GEO_CACHE / "msbuildings", g["max_cache_gib"], g["min_free_gib"]
        )
        if rec:
            dl_log.append(rec)
        tiles.append(df)
    b = pd.concat(tiles, ignore_index=True)
    w, s, e, n = bb
    b = b[(b.lon >= w) & (b.lon <= e) & (b.lat >= s) & (b.lat <= n)]
    cl = estimators.extent_buildings(b, lat, lon, p)
    out: dict[str, Any] = {"quadkeys": footprints.quadkeys_bbox(bb), "n_buildings": len(cl)}
    if cl.empty:
        out.update(grid=0.0, buildings=0.0, extent_km2=0.0, extent_bbox=None)
        return out
    pad = 2.0 / 110.574  # bbox + 2 km (skill section 5)
    ebox = (cl.lon.min() - pad, cl.lat.min() - pad, cl.lon.max() + pad, cl.lat.max() + pad)
    arr, tr, _ = imagery.read_window(str(REPO_ROOT / cfg["inputs"]["worldpop"]), ebox)
    mask = estimators.extent_mask(cl, tr, arr.shape, p.close_kernel)
    cell_km2 = abs(tr.a * tr.e) * 110.574 * 111.320 * np.cos(np.radians(lat))
    out.update(
        grid=estimators.grid_sum(arr, mask),
        buildings=estimators.buildings_estimate(len(cl), p),
        extent_km2=round(float(mask.sum() * cell_km2), 3),
        extent_bbox=[round(x, 5) for x in ebox],
    )
    return out


def _index(cfg: dict) -> pd.DataFrame:
    return footprints.load_index(REPO_ROOT / cfg["inputs"]["footprint_index"])


@app.command()
def backtest(
    seed: int = seed_option(),
    run_dir: Path = RUNS / "backtest",
    params_file: Path = typer.Option(PARAMS, help="alternate params YAML (sensitivity runs)"),
) -> None:
    """Back-test both estimators on 10 stratified settlements with Census 2022 figures."""
    cfg, gen = _cfg(params_file), rng(seed)
    p, idx = params(cfg), _index(cfg)
    reg = register()
    known = reg[(reg.pop_type == "official") & (reg.pop_year == 2022) & reg.population.notna()]
    known = known[known.population < _v(cfg["backtest"]["max_city_pop"])]
    picks = []
    for st in cfg["backtest"]["strata"]:
        pool = known[(known.population >= st["min"]) & (known.population < st["max"])]
        pool = pool.sort_values(["register_file", "row_in_file"])
        sel = gen.choice(len(pool), size=st["n"], replace=False)
        picks.append(pool.iloc[sorted(sel)].assign(stratum=st["name"]))
    sample = pd.concat(picks)
    rows, dl = [], []
    log = run_dir / "method_log.jsonl"
    log.unlink(missing_ok=True)
    for r in sample.itertuples():
        est = estimate_one(r.lat, r.lon, cfg, p, idx, dl)
        row = {
            "stratum": r.stratum,
            "name_en": r.name_en,
            "region": r.region,
            "census_2022": r.population,
            "pop_source": r.pop_source,
            "lat": r.lat,
            "lon": r.lon,
            **{k: est[k] for k in ("n_buildings", "grid", "buildings", "extent_km2")},
        }
        row["ape_grid"] = estimators.abs_pct_error(est["grid"], r.population)
        row["ape_buildings"] = estimators.abs_pct_error(est["buildings"], r.population)
        rows.append(row)
        method_log.append(
            log,
            {
                "id": method_log.entry_id("bt", f"{r.register_file}:{r.row_in_file}"),
                "method": "backtest grid + buildings over DBSCAN extent",
                "inputs": [
                    "worldpop-sau-2020-100m-unadj-constrained",
                    "msbuildings-ksa-2026-02-03",
                    r.pop_source,
                ],
                "parameters": [f"A-geo-00{i}" for i in range(1, 10)],
                "value": {"grid": est["grid"], "buildings": est["buildings"]},
                "band": None,
                "run_id": str(run_dir.relative_to(REPO_ROOT)),
                "target": r.name_en,
                "extent_bbox": est["extent_bbox"],
                "extent_km2": est["extent_km2"],
                "n_buildings": est["n_buildings"],
            },
        )
    df = pd.DataFrame(rows)
    mape = {"grid": float(df.ape_grid.median()), "buildings": float(df.ape_buildings.median())}
    gate = _v(cfg["backtest"]["rank_gate_mape"])
    summary = {
        "median_ape": mape,
        "may_rank": {k: v <= gate for k, v in mape.items()},
        "n": len(df),
        "downloads": dl,
    }
    run_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(run_dir / "backtest.csv", index=False)
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    write_meta(run_dir, seed, cfg, {"assumptions": [f"A-geo-0{i:02d}" for i in range(1, 11)]})
    typer.echo(df.to_string())
    typer.echo(json.dumps({k: summary[k] for k in ("median_ape", "may_rank")}))


@app.command()
def estimate(
    seed: int = seed_option(),
    which: str = typer.Option("no-pop", help="no-pop | secondary | all"),
    limit: int = typer.Option(0, help="0 = every selected row"),
    region: str = typer.Option("", help="register region slug, e.g. al_baha (default: all)"),
    registers: str = typer.Option(REGISTERS, help="glob of register files (repo-relative)"),
    backtest_dir: Path = RUNS / "backtest",
    run_dir: Path = RUNS / "estimate",
    params_file: Path = typer.Option(PARAMS, help="params YAML"),
) -> None:
    """Estimate population for register rows (never overwrites an official figure)."""
    cfg = _cfg(params_file)
    rng(seed)
    p, idx = params(cfg), _index(cfg)
    bt = json.loads((backtest_dir / "summary.json").read_text())
    err, may = bt["median_ape"], bt["may_rank"]
    reg = register(pattern=registers)
    sel = reg[reg.population.isna()] if which == "no-pop" else reg
    if which == "secondary":
        sel = reg[reg.population.notna()]
    if region:
        sel = sel[sel.region == region]
    if limit:
        sel = sel.head(limit)
    run_dir = run_dir / which
    run_dir.mkdir(parents=True, exist_ok=True)
    log = run_dir / f"method_log-{which}.jsonl"
    log.unlink(missing_ok=True)
    rows, dl = [], []
    for r in sel.itertuples():
        if pd.isna(r.lat) or pd.isna(r.lon):
            continue
        est = estimate_one(r.lat, r.lon, cfg, p, idx, dl)
        lo, mid, hi = estimators.band(
            [est["grid"], est["buildings"]], [err["grid"], err["buildings"]]
        )
        mid_id = method_log.entry_id("est", f"{r.register_file}:{r.row_in_file}")
        method_log.append(
            log,
            {
                "id": mid_id,
                "method": "grid (WorldPop) + buildings x occupancy over DBSCAN extent",
                "inputs": [
                    "worldpop-sau-2020-100m-unadj-constrained",
                    "msbuildings-ksa-2026-02-03",
                ],
                "parameters": [f"A-geo-00{i}" for i in range(1, 10)],
                "value": {"grid": est["grid"], "buildings": est["buildings"], "central": mid},
                "band": [lo, hi],
                "backtest_median_ape": err,
                "may_rank": may,
                "run_id": str(run_dir.relative_to(REPO_ROOT)),
                "target": r.name_en,
                "extent_bbox": est["extent_bbox"],
                "extent_km2": est["extent_km2"],
                "n_buildings": est["n_buildings"],
            },
        )
        div = None
        if pd.notna(r.population) and r.population > 0 and mid == mid:
            div = (mid - r.population) / r.population
        rows.append(
            {
                "register_file": r.register_file,
                "row_in_file": r.row_in_file,
                "name_en": r.name_en,
                "region": r.region,
                "population": r.population,
                "pop_type": r.pop_type,
                "grid": est["grid"],
                "buildings": est["buildings"],
                "est_low": lo,
                "est_central": mid,
                "est_high": hi,
                "n_buildings": est["n_buildings"],
                "extent_km2": est["extent_km2"],
                "divergence": div,
                "method_log_id": mid_id,
            }
        )
    df = pd.DataFrame(rows)
    df.to_csv(run_dir / f"estimates-{which}.csv", index=False)
    (run_dir / f"downloads-{which}.json").write_text(json.dumps(dl, indent=2) + "\n")
    write_meta(run_dir, seed, cfg, {"which": which, "backtest": bt["median_ape"]})
    typer.echo(df.drop(columns=["register_file"]).to_string())


@app.command("seat")
def seat_cmd(
    seed: int = seed_option(),
    lat: float = typer.Option(...),
    lon: float = typer.Option(...),
    governorate_ar: str = typer.Option(..., help="name_ar of the polygon in governorates.geojson"),
    label: str = typer.Option("point"),
    run_dir: Path = RUNS / "seat",
) -> None:
    """Point-in-polygon and km to the boundary against an OSM governorate polygon."""
    from shapely.geometry import shape

    rng(seed)
    gj = json.loads((REPO_ROOT / "cities/ksa/zones/governorates.geojson").read_text())
    feats = [
        f
        for f in gj["features"]
        if governorate_ar in json.dumps(f["properties"], ensure_ascii=False)
    ]
    if not feats:
        raise typer.BadParameter(f"no governorate matching {governorate_ar}")
    f = feats[0]
    inside, km = geom.point_polygon_km(lat, lon, shape(f["geometry"]))
    res = {
        "label": label,
        "lat": lat,
        "lon": lon,
        "polygon": f["properties"],
        "inside": inside,
        "km_to_boundary": round(km, 2),
        "epsg": geom.utm_epsg(lon),
    }
    run_dir.mkdir(parents=True, exist_ok=True)
    method_log.append(
        run_dir / "method_log.jsonl",
        {
            "id": method_log.entry_id("seat", f"{label}:{lat}:{lon}"),
            "method": "point-in-polygon, UTM by longitude",
            "inputs": ["osm-gcc-admin-extract-2026-10-14"],
            "parameters": [],
            "value": res,
            "band": None,
            "run_id": str(run_dir.relative_to(REPO_ROOT)),
        },
    )
    write_meta(run_dir, seed, {"lat": lat, "lon": lon, "gov": governorate_ar})
    typer.echo(json.dumps(res, ensure_ascii=False))


def _norm_ar(name: object) -> str:
    """Governorate-name key: no 'محافظة', unified alef/taa marbuta/alef maqsura spellings."""
    t = str(name or "").replace("محافظة", "").strip()
    for a, b in (("أ", "ا"), ("إ", "ا"), ("آ", "ا"), ("ة", "ه"), ("ى", "ي")):
        t = t.replace(a, b)
    return t


@app.command("validate-geocodes")
def validate_geocodes(
    seed: int = seed_option(),
    register_file: Path = Path("cities/ksa/regions/archive/pilot/pilot-qassim.parquet"),
    geocode_dir: Path = Path("data/ksa/pilot-qassim/raw/geocode"),
    run_dir: Path = RUNS / "validate-geocodes",
) -> None:
    """Every row's point inside its governorate polygon (matched on governorate_ar)."""
    from shapely.geometry import shape

    rng(seed)
    gj = json.loads((REPO_ROOT / "cities/ksa/zones/governorates.geojson").read_text())
    polys = {_norm_ar(f["properties"].get("name_ar")): shape(f["geometry"]) for f in gj["features"]}
    df = pd.read_parquet(REPO_ROOT / register_file)
    out = []
    for r in df.itertuples():
        key = _norm_ar(r.governorate_ar)
        poly = polys.get(key)
        if poly is None:
            cand = [k for k in polys if k and (key in k or k in key)]
            poly = polys[cand[0]] if cand else None
        if poly is None or pd.isna(r.lat):
            out.append(
                {
                    "name_en": r.name_en,
                    "governorate_ar": r.governorate_ar,
                    "inside": None,
                    "km_to_boundary": None,
                    "flag": "no_polygon_or_point",
                }
            )
            continue
        inside, km = geom.point_polygon_km(r.lat, r.lon, poly)
        out.append(
            {
                "name_en": r.name_en,
                "governorate_ar": r.governorate_ar,
                "inside": inside,
                "km_to_boundary": round(km, 2),
                "flag": None if inside else "outside",
            }
        )
    res = pd.DataFrame(out)
    run_dir.mkdir(parents=True, exist_ok=True)
    res.to_csv(run_dir / "geocodes.csv", index=False)
    # raw Nominatim files: which governorate polygon holds each top result
    from shapely.geometry import Point

    gx = [(f["properties"], shape(f["geometry"])) for f in gj["features"]]
    raw = []
    for fp in sorted((REPO_ROOT / geocode_dir).glob("*.json")):
        if fp.name.startswith("overpass_"):
            continue  # an Overpass rail extract, not a geocode
        data = json.loads(fp.read_text(encoding="utf-8"))
        top = data[0] if isinstance(data, list) and data else None
        if not top:
            raw.append({"file": fp.name, "flag": "empty_result"})
            continue
        lat, lon = float(top["lat"]), float(top["lon"])
        hit = next((pr for pr, poly in gx if poly.contains(Point(lon, lat))), None)
        region = hit["region"] if hit else None
        raw.append(
            {
                "file": fp.name,
                "osm": f"{top.get('osm_type')}/{top.get('osm_id')}",
                "lat": lat,
                "lon": lon,
                "display_name": top.get("display_name"),
                "polygon_gov": hit["name_ar"] if hit else None,
                "polygon_region": region,
                "flag": None if region == "qassim" else "outside_qassim",
            }
        )
    rw = pd.DataFrame(raw)
    rw.to_csv(run_dir / "raw_geocodes.csv", index=False)
    typer.echo(rw[["file", "polygon_gov", "flag"]].to_string())
    write_meta(run_dir, seed, {"register": str(register_file)})
    typer.echo(res.to_string())
    typer.echo(res.flag.value_counts(dropna=False).to_string())


def _stn_id(s: dict) -> str:
    return method_log.entry_id("stn", site_key(s))


def site_key(s: dict) -> str:
    return s["station_uid"] + (f":{s['variant']}" if s.get("variant") else "")


@app.command()
def stations(
    seed: int = seed_option(),
    apply: bool = typer.Option(False, help="write accepted sites into stations.geojson"),
    imagery_check: bool = typer.Option(True, help="fetch a Sentinel-2 window per site"),
    run_dir: Path = RUNS / "stations",
) -> None:
    """Sites from station_sites.yaml (OSM evidence) + a Sentinel-2 confirmation window each."""
    rng(seed)
    sites = yaml.safe_load(SITES.read_text(encoding="utf-8"))["sites"]
    log = run_dir / "method_log.jsonl"
    if not apply:
        log.unlink(missing_ok=True)
    run_dir.mkdir(parents=True, exist_ok=True)
    for s in sites:
        key = site_key(s)
        entry = {
            "id": method_log.entry_id("stn", key),
            "method": s["method"],
            "inputs": s["inputs"],
            "parameters": [],
            "value": [s["lon"], s["lat"]],
            "band": s.get("uncertainty_km"),
            "run_id": str(run_dir.relative_to(REPO_ROOT)),
            "target": key,
        }
        if imagery_check and not apply:
            w = bbox_km(s["lat"], s["lon"], 1.5)
            scenes = imagery.stac_sentinel2(w, "2026-06-01", "2026-10-30")
            if scenes:
                sc = scenes[0]
                png = imagery.GEO_CACHE / "s2" / f"{key.replace(':', '_')}.png"
                win = imagery.s2_window_png(sc["visual"], s["lat"], s["lon"], 1500, png)
                entry["imagery"] = {
                    "scene": sc["id"],
                    "datetime": sc["datetime"],
                    "cloud": sc["cloud"],
                    "bbox": [round(x, 5) for x in w],
                    **win,
                    "seen": s.get("seen"),
                }
        if not apply:
            method_log.append(log, entry)
    if apply:
        path = REPO_ROOT / "cities/ksa/lines/stations.geojson"
        gj = json.loads(path.read_text(encoding="utf-8"))
        by = {s["station_uid"]: s for s in sites if s.get("accept")}
        n = 0
        for f in gj["features"]:
            s = by.get(f["properties"]["station_uid"])
            if not s:
                continue
            f["geometry"] = {"type": "Point", "coordinates": [s["lon"], s["lat"]]}
            pr = f["properties"]
            pr.update(
                location_method=s["location_method"],
                located=s.get("located", True),
                uncertainty_km=s.get("uncertainty_km"),
                site_status=s.get("site_status"),
                confidence=s.get("confidence"),
                notes=f"{s.get('notes') or ''} [method log {_stn_id(s)}]",
            )
            n += 1
        for f in gj["features"]:
            f["properties"].setdefault("confidence", None)
        path.write_text(json.dumps(gj, ensure_ascii=False, indent=0) + "\n", encoding="utf-8")
        typer.echo(f"applied {n} sites")
    write_meta(run_dir, seed, sites)


@app.command("served-rerun")
def served_rerun(seed: int = seed_option(), run_dir: Path = RUNS / "served-rerun") -> None:
    """Refresh register distances from stations.geojson and rerun the funnel long list."""
    cmds = [
        ["uv", "run", "python", "-m", "network.distances", "register", "--seed", str(seed)],
        [
            "uv",
            "run",
            "python",
            "-m",
            "screening.funnel",
            "long-list",
            "--in",
            "cities/ksa/zones/candidates-pilot-r1a.parquet",
            "--threshold",
            "10000",
            "--sensitivity",
            "5000",
            "--seed",
            str(seed),
            "--run-dir",
            str(run_dir / "long-list"),
        ],
    ]
    for c in cmds:
        typer.echo(" ".join(c))
        subprocess.run(c, check=True, cwd=REPO_ROOT)
    write_meta(run_dir, seed, cmds)


GEO_TAG = "GEO_VERIFY 31 Oct 2026"


def _note(r: pd.Series, may: dict) -> str:
    """Record-only note for a register row (never a population value)."""
    if pd.isna(r.est_central):  # no cluster
        return (
            f"{GEO_TAG}: no estimate, no building-footprint cluster within the snap radius "
            f"(A-geo-003; footprint coverage gap or point offset) [{r.method_log_id}]"
        )
    single = " (one method only: the other gave 0)" if min(r.grid, r.buildings) <= 0 else ""
    use = "may rank" if all(may.values()) else "record-only: back-test above the 30 % gate"
    return (
        f"{GEO_TAG}: derived estimate central {r.est_central:,.0f} (band {r.est_low:,.0f}–"
        f"{r.est_high:,.0f}; WorldPop grid {r.grid:,.0f}, buildings x occupancy "
        f"{r.buildings:,.0f}){single}; {use}; primary_to_find: GASTAT locality table "
        f"[{r.method_log_id}]"
    )


@app.command("apply-notes")
def apply_notes(
    seed: int = seed_option(),
    estimate_dir: Path = RUNS / "estimate",
    backtest_dir: Path = RUNS / "backtest",
    conflicts_md: Path = Path("docs/sources/conflicts.md"),
) -> None:
    """Append record-only notes to the pilot registers (Parquet + CSV notes column only) and
    write the GEO_VERIFY conflict table (> 25 % divergence) into conflicts.md."""
    import csv

    import pyarrow as pa
    import pyarrow.parquet as pq

    rng(seed)
    cfg = _cfg()
    may = json.loads((backtest_dir / "summary.json").read_text())["may_rank"]
    frames = [pd.read_csv(f) for f in sorted(estimate_dir.glob("*/estimates-*.csv"))]
    est = pd.concat(frames, ignore_index=True)
    for fname, grp in est.groupby("register_file"):
        notes = {int(r.row_in_file): _note(r, may) for _, r in grp.iterrows()}
        path = REPO_ROOT / fname
        table = pq.read_table(path)
        col = table.column("notes").to_pylist()
        for i, n in notes.items():
            old = [p for p in (col[i] or "").split(" | ") if p and not p.startswith(GEO_TAG)]
            col[i] = " | ".join([*old, n])
        idx = table.schema.get_field_index("notes")
        field = table.schema.field(idx)
        if pa.types.is_null(field.type):  # an all-null notes column becomes large_string
            field = field.with_type(pa.large_string())
        table = table.set_column(idx, field, pa.array(col, field.type))
        pq.write_table(table, path)
        cpath = path.with_suffix(".csv")
        with cpath.open(encoding="utf-8", newline="") as fh:
            rows = list(csv.reader(fh))
        ni = rows[0].index("notes")
        for i in notes:
            rows[i + 1][ni] = col[i] or ""
        with cpath.open("w", encoding="utf-8", newline="") as fh:
            csv.writer(fh, lineterminator="\n").writerows(rows)
    thr = _v(cfg["conflict_divergence"])
    c = est[est.divergence.notna() & (est.divergence.abs() > thr)].copy()
    c = c.sort_values(["region", "name_en"]).reset_index(drop=True)
    lines = [
        "## GEO_VERIFY conflicts (31 Oct 2026): derived estimate vs relayed Census 2022 figure",
        "",
        f"Rule: geo-verify skill section 3 (> {thr:.0%} divergence logs a row; both figures kept,"
        " nothing overwritten). The derived estimates come from two estimators that FAIL the"
        " 30 % back-test gate (`docs/geo-verify.md`), so these rows are weak evidence: they flag"
        " where a GASTAT locality table is most needed, not that the relayed figure is wrong."
        " Status of every row: open. Method-log ids resolve in"
        " `runs/geo_verify/estimate/secondary/method_log-secondary.jsonl`.",
        "",
        "| id | region | settlement | relayed figure (source) | derived central (band) |"
        " divergence | method log |",
        "|---|---|---|---|---|---|---|",
    ]
    reg = register()
    srcs = {(r.register_file, r.row_in_file): r.pop_source for r in reg.itertuples()}
    for i, r in c.iterrows():
        lines.append(
            f"| C-geo-{i + 1:03d} | {r.region} | {r.name_en} | {r.population:,.0f} "
            f"({srcs.get((r.register_file, r.row_in_file))}) | {r.est_central:,.0f} "
            f"({r.est_low:,.0f}–{r.est_high:,.0f}) | {r.divergence:+.0%} | {r.method_log_id} |"
        )
    block = "\n".join(lines) + "\n"
    text = (REPO_ROOT / conflicts_md).read_text(encoding="utf-8")
    head = "## GEO_VERIFY conflicts"
    if head in text:
        text = text[: text.index(head)].rstrip("\n") + "\n"
    (REPO_ROOT / conflicts_md).write_text(text.rstrip("\n") + "\n\n" + block, encoding="utf-8")
    write_meta(RUNS / "apply-notes", seed, {"rows": len(est), "conflicts": len(c)})
    typer.echo(f"notes on {len(est)} rows; {len(c)} conflict rows")


if __name__ == "__main__":
    app()
