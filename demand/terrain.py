"""Terrain class per register row from an open DEM (R3; Tariq's CP3 decision 8).

DEM: Copernicus DEM GLO-30 Public, Cloud-Optimised GeoTIFFs on AWS Open Data
(https://copernicus-dem-30m.s3.amazonaws.com/, anonymous HTTP, no account). Only a window around
each settlement is read (GDAL /vsicurl/ range requests); every window is cached as a small GeoTIFF
under data/ksa/dem/windows/ with an index (data/ksa/dem/windows/index.csv) that the manifest hashes.

Per row:
1. extent = a disc of radius r = clip(k * sqrt(population), r_min, r_max) km around the register
   point (A-geo-011, A-geo-012); rows without a population use r_missing;
2. the window is resampled (bilinear) to the local UTM zone at 30 m and median-filtered
   (A-geo-013) to suppress buildings and palms (Copernicus is a surface model, not bare earth);
3. metrics inside the disc: slope mean and P90 (degrees, np.gradient on the metric grid), relief
   (P95 - P5 elevation), mean elevation, roughness (std of the residual from a ~1 km box mean,
   A-geo-014), and the great-circle km to the nearest OSM natural=coastline vertex;
4. an ordered rule (cities/ksa/assumptions/demand_terrain.yaml) gives the class: escarpment_mountain
   -> sabkha -> coastal -> dunes -> mixed -> flat_desert. Dunes and sabkha are only DEM signatures
   (roughness at low slope; very low, very flat ground near the coast); they are flagged as such.

The output is a sidecar (cities/ksa/zones/terrain_dem.parquet); the coordinator applies it.
Produced using Copernicus WorldDEM-30 (c) DLR e.V. 2010-2014 and (c) Airbus Defence and Space GmbH
2014-2018 provided under COPERNICUS by the European Union and ESA; all rights reserved. The
organisations in charge of the Copernicus programme by law or by delegation do not incur any
liability for any use of the Copernicus WorldDEM-30.
Coastline (c) OpenStreetMap contributors (ODbL).

CLI:
  uv run python -m demand.terrain classify --register cities/ksa/candidates.parquet \
      --rows all|longlist-missing --seed 1 --out runs/r3/terrain/
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import typer
import yaml
from scipy import ndimage

from common import REPO_ROOT
from common.labels import LABEL
from common.runmeta import config_hash, seed_option, write_meta
from network.geo import KNearest

RULES = Path("cities/ksa/assumptions/demand_terrain.yaml")
CACHE = Path("data/ksa/dem/windows")
COAST = Path("data/ksa/dem/coast/coastline.geojsonseq")
LONGLIST = Path("runs/r2/long-list/longlist.parquet")
SIDECAR = Path("cities/ksa/zones/terrain_dem.parquet")
CLASSES = ("flat_desert", "dunes", "sabkha", "escarpment_mountain", "coastal", "mixed")
METHOD = (
    "Copernicus GLO-30 DSM window, UTM 30 m bilinear, median filter; disc radius from population; "
    "ordered threshold rule cities/ksa/assumptions/demand_terrain.yaml (A-geo-011..022); "
    "coast = OSM natural=coastline"
)
GDAL_ENV = {
    "GDAL_DISABLE_READDIR_ON_OPEN": "EMPTY_DIR",
    "CPL_VSIL_CURL_ALLOWED_EXTENSIONS": ".tif",
    "GDAL_HTTP_MAX_RETRY": "4",
    "GDAL_HTTP_RETRY_DELAY": "1",
    "VSI_CACHE": "TRUE",
}
app = typer.Typer(
    add_completion=False, help="Terrain class per register row from Copernicus GLO-30."
)


@app.callback()
def main() -> None:
    """Terrain class per register row from Copernicus GLO-30 (R3)."""


def val(x: Any) -> Any:
    return x["value"] if isinstance(x, dict) and "value" in x else x


def load_rules(root: Path = REPO_ROOT) -> dict:
    return yaml.safe_load((root / RULES).read_text(encoding="utf-8"))


# --------------------------------------------------------------------------- pure functions


def radius_km(population: float | None, ext: dict) -> float:
    """Disc radius (km): k * sqrt(population) clipped to [r_min, r_max] (A-geo-011/012)."""
    if population is None or not np.isfinite(population) or population <= 0:
        return float(val(ext["radius_missing_pop_km"]))
    r = float(val(ext["radius_k_km_per_sqrt_person"])) * math.sqrt(float(population))
    return float(np.clip(r, float(val(ext["radius_min_km"])), float(val(ext["radius_max_km"]))))


def disc_mask(shape: tuple[int, int], res_m: float, centre_rc: tuple[float, float], r_m: float):
    rr, cc = np.mgrid[0 : shape[0], 0 : shape[1]]
    d = np.hypot((rr - centre_rc[0]) * res_m, (cc - centre_rc[1]) * res_m)
    return d <= r_m


def terrain_metrics(elev: np.ndarray, res_m: float, mask: np.ndarray, cfg: dict) -> dict:
    """Slope, relief, elevation and roughness inside `mask` on a metric grid (res_m metres)."""
    z = np.asarray(elev, float)
    if np.isnan(z).any():
        fill = np.nanmedian(z) if np.isfinite(z).any() else 0.0
        z = np.where(np.isnan(z), fill, z)
    k = int(val(cfg["smoothing"]["median_filter_px"]))
    if k > 1:
        z = ndimage.median_filter(z, size=k, mode="nearest")
    gy, gx = np.gradient(z, res_m)
    slope = np.degrees(np.arctan(np.hypot(gx, gy)))
    w = int(val(cfg["smoothing"]["roughness_window_px"]))
    resid = z - ndimage.uniform_filter(z, size=w, mode="nearest")
    m = mask.astype(bool)
    zin, sin, rin = z[m], slope[m], resid[m]
    p5, p95 = np.percentile(zin, [5, 95])
    return {
        "slope_mean_deg": round(float(sin.mean()), 3),
        "slope_p50_deg": round(float(np.percentile(sin, 50)), 3),
        "slope_p90_deg": round(float(np.percentile(sin, 90)), 3),
        "relief_m": round(float(p95 - p5), 2),
        "elev_mean_m": round(float(zin.mean()), 2),
        "rough_m": round(float(rin.std()), 3),
        "n_px": int(m.sum()),
    }


def signatures(metrics: dict, rule: dict) -> dict[str, bool]:
    """Which class conditions hold (several may; the rule order picks one)."""
    s_mean, s50, s90 = metrics["slope_mean_deg"], metrics["slope_p50_deg"], metrics["slope_p90_deg"]
    relief, elev, rough = metrics["relief_m"], metrics["elev_mean_m"], metrics["rough_m"]
    coast = metrics.get("coast_km")
    coast = np.inf if coast is None or not np.isfinite(coast) else coast
    esc, sab, cst, dun, mix = (
        rule[k] for k in ("escarpment_mountain", "sabkha", "coastal", "dunes", "mixed")
    )
    return {
        "escarpment_mountain": bool(
            s90 >= val(esc["slope_p90_deg_min"]) or relief >= val(esc["relief_m_min"])
        ),
        "sabkha": bool(
            coast <= val(sab["coast_km_max"])
            and elev <= val(sab["elev_mean_m_max"])
            and relief <= val(sab["relief_m_max"])
            and s_mean <= val(sab["slope_mean_deg_max"])
        ),
        "coastal": bool(coast <= val(cst["coast_km_max"])),
        "dunes": bool(
            s50 >= val(dun["slope_p50_deg_min"])
            and s90 < val(dun["slope_p90_deg_max"])
            and relief <= val(dun["relief_m_max"])
            and rough >= val(dun["rough_m_min"])
            and s90 <= val(dun["slope_p90_over_p50_max"]) * s50
            and elev <= val(dun["elev_mean_m_max"])
        ),
        "mixed": bool(s90 >= val(mix["slope_p90_deg_min"]) or relief >= val(mix["relief_m_min"])),
        "flat_desert": True,
    }


def classify(metrics: dict, rule: dict) -> tuple[str, str, list[str]]:
    """(class, rule that fired, flags) from the ordered threshold rule (A-geo-021)."""
    sig = signatures(metrics, rule)
    order = rule.get("order") or [
        "escarpment_mountain",
        "sabkha",
        "coastal",
        "dunes",
        "mixed",
        "flat_desert",
    ]
    cls = next(c for c in order if sig[c])
    flags = []
    if sig["sabkha"]:
        flags.append("sabkha_signature_dem_only")
    if sig["dunes"]:
        flags.append("dune_signature_dem_only")
    if sig["coastal"] and cls != "coastal":
        flags.append("within_coastal_distance")
    return cls, cls, flags


# --------------------------------------------------------------------------- DEM access


def tile_name(lat_i: int, lon_i: int) -> str:
    ns, ew = ("N" if lat_i >= 0 else "S"), ("E" if lon_i >= 0 else "W")
    return f"Copernicus_DSM_COG_10_{ns}{abs(lat_i):02d}_00_{ew}{abs(lon_i):03d}_00_DEM"


def tile_url(lat_i: int, lon_i: int, cfg: dict) -> str:
    ns, ew = ("N" if lat_i >= 0 else "S"), ("E" if lon_i >= 0 else "W")
    return cfg["dem"]["url_template"].format(ns=ns, ew=ew, lat=abs(lat_i), lon=abs(lon_i))


def window_bounds(lat: float, lon: float, r_km: float, margin_km: float = 1.5):
    dlat = (r_km + margin_km) / 110.574
    dlon = (r_km + margin_km) / (111.320 * math.cos(math.radians(lat)))
    return lon - dlon, lat - dlat, lon + dlon, lat + dlat


def tiles_for(bounds) -> list[tuple[int, int]]:
    w, s, e, n = bounds
    return [
        (la, lo)
        for la in range(math.floor(s), math.floor(n) + 1)
        for lo in range(math.floor(w), math.floor(e) + 1)
    ]


_TILE_EXISTS: dict[str, bool] = {}
_LOCK = threading.Lock()


def tile_exists(url: str) -> bool:
    """HEAD the COG once; 404/403 = no tile (ocean). Other errors raise (never silently 'sea')."""
    with _LOCK:
        if url in _TILE_EXISTS:
            return _TILE_EXISTS[url]
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, method="HEAD")
            with urllib.request.urlopen(req, timeout=30):
                ok = True
            break
        except urllib.error.HTTPError as e:
            if e.code in (403, 404):
                ok = False
                break
            if attempt == 3:
                raise
        except OSError:
            if attempt == 3:
                raise
        time.sleep(1 + attempt)
    with _LOCK:
        _TILE_EXISTS[url] = ok
    return ok


def cache_file(root: Path, row_key: str) -> Path:
    return root / CACHE / (hashlib.sha1(row_key.encode("utf-8")).hexdigest()[:16] + ".tif")


def fetch_window(root: Path, row_key: str, lat: float, lon: float, r_km: float, cfg: dict) -> dict:
    """Read the window from the remote COGs (or the cache) and write it as a GeoTIFF."""
    import rasterio
    from rasterio.merge import merge

    path = cache_file(root, row_key)
    bounds = window_bounds(lat, lon, r_km)
    tiles = tiles_for(bounds)
    names = [tile_name(*t) for t in tiles]
    present = [t for t in tiles if tile_exists(tile_url(*t, cfg))]
    info = {
        "row_key": row_key,
        "file": path.relative_to(root).as_posix(),
        "west": round(bounds[0], 6),
        "south": round(bounds[1], 6),
        "east": round(bounds[2], 6),
        "north": round(bounds[3], 6),
        "tiles": ";".join(names),
        "tiles_missing": ";".join(tile_name(*t) for t in tiles if t not in present),
    }
    if not path.exists():
        fill = float(val(cfg["dem"]["missing_tile_fill_m"]))
        with rasterio.Env(**GDAL_ENV):
            if present:
                srcs = [rasterio.open("/vsicurl/" + tile_url(*t, cfg)) for t in present]
                try:
                    arr, tr = merge(srcs, bounds=bounds, nodata=np.nan)
                    crs = srcs[0].crs
                finally:
                    for s in srcs:
                        s.close()
                arr = np.where(np.isnan(arr), fill, arr).astype("float32")
            else:
                from rasterio.crs import CRS
                from rasterio.transform import from_bounds

                res = 1 / 3600
                wpx = int(round((bounds[2] - bounds[0]) / res))
                hpx = int(round((bounds[3] - bounds[1]) / res))
                arr = np.full((1, hpx, wpx), fill, "float32")
                tr, crs = from_bounds(*bounds, wpx, hpx), CRS.from_epsg(4326)
            path.parent.mkdir(parents=True, exist_ok=True)
            tmp = path.with_suffix(".tmp.tif")
            with rasterio.open(
                tmp,
                "w",
                driver="GTiff",
                width=arr.shape[2],
                height=arr.shape[1],
                count=1,
                dtype="float32",
                crs=crs,
                transform=tr,
                compress="deflate",
                predictor=3,
                tiled=True,
                blockxsize=256,
                blockysize=256,
            ) as dst:
                dst.write(arr)
            tmp.rename(path)
    info["bytes"] = path.stat().st_size
    info["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    return info


def utm_grid(path: Path, lat: float, lon: float, r_km: float, res_m: float):
    """Window resampled (bilinear) to the local UTM zone, centred on the point; (array, centre)."""
    import rasterio
    from rasterio.crs import CRS
    from rasterio.transform import from_origin
    from rasterio.warp import Resampling, reproject, transform

    zone = int((lon + 180) // 6) + 1
    utm = CRS.from_epsg((32600 if lat >= 0 else 32700) + zone)
    xs, ys = transform(CRS.from_epsg(4326), utm, [lon], [lat])
    half = r_km * 1000 + 500
    n = int(math.ceil(2 * half / res_m))
    tr = from_origin(xs[0] - half, ys[0] + half, res_m, res_m)
    dst = np.full((n, n), np.nan, "float32")
    with rasterio.open(path) as src:
        reproject(
            source=rasterio.band(src, 1),
            destination=dst,
            dst_transform=tr,
            dst_crs=utm,
            resampling=Resampling.bilinear,
            dst_nodata=np.nan,
        )
    return dst, ((half / res_m) - 0.5, (half / res_m) - 0.5), utm.to_epsg()


def load_coast(root: Path, step_km: float) -> KNearest:
    lat, lon = [], []
    with (root / COAST).open(encoding="utf-8") as f:
        for line in f:
            line = line.strip().lstrip("\x1e")
            if not line:
                continue
            coords = json.loads(line)["geometry"]["coordinates"]
            for (x0, y0), (x1, y1) in zip(coords, coords[1:], strict=False):
                d = math.hypot((y1 - y0) * 110.574, (x1 - x0) * 111.32 * math.cos(math.radians(y0)))
                k = max(1, int(math.ceil(d / step_km)))
                for t in np.arange(k) / k:
                    lon.append(x0 + t * (x1 - x0))
                    lat.append(y0 + t * (y1 - y0))
            lon.append(coords[-1][0])
            lat.append(coords[-1][1])
    return KNearest(np.array(lat), np.array(lon))


# --------------------------------------------------------------------------- pipeline


def select_rows(root: Path, register: Path, rows: str) -> pd.DataFrame:
    reg = pd.read_parquet(root / register)
    reg = reg[reg.lat.notna() & reg.lon.notna()]
    if rows == "all":
        return reg
    if rows == "longlist-missing":
        ll = pd.read_parquet(root / LONGLIST)
        keys = set(ll.loc[ll.funnel_stage == "long", "row_key"])
        return reg[reg.row_key.isin(keys) & reg.terrain_class.isna()]
    raise typer.BadParameter("--rows must be all or longlist-missing")


def process_row(root: Path, r: pd.Series, cfg: dict) -> dict:
    rk = str(r.row_key)
    rad = radius_km(r.population, cfg["extent"])
    info = fetch_window(root, rk, float(r.lat), float(r.lon), rad, cfg)
    res = float(cfg["dem"]["target_res_m"])
    grid, centre, epsg = utm_grid(root / info["file"], float(r.lat), float(r.lon), rad, res)
    mask = disc_mask(grid.shape, res, centre, rad * 1000)
    met = terrain_metrics(grid, res, mask, cfg)
    # sensitivity: the same metrics on the minimum disc (A-geo-012), inside the same window
    rmin = float(val(cfg["extent"]["radius_min_km"]))
    met_min = met
    if rad > rmin:
        met_min = terrain_metrics(grid, res, disc_mask(grid.shape, res, centre, rmin * 1000), cfg)
    return {"info": info, "metrics": met, "metrics_rmin": met_min, "radius_km": rad, "epsg": epsg}


def crosstab(prior: pd.Series, dem: pd.Series) -> dict:
    t = pd.crosstab(prior.fillna("NaN"), dem, dropna=False)
    return {str(i): {str(c): int(v) for c, v in row.items() if v} for i, row in t.iterrows()}


@app.command("classify")
def classify_cmd(
    register: Path = typer.Option(Path("cities/ksa/candidates.parquet"), "--register"),
    rows: str = typer.Option("all", "--rows", help="all | longlist-missing"),
    out: Path = typer.Option(Path("runs/r3/terrain"), "--out"),
    sidecar: Path = typer.Option(SIDECAR, "--sidecar", help="sidecar Parquet (rows=all only)"),
    workers: int = typer.Option(8, "--workers", help="parallel window reads"),
    seed: int = seed_option(),
    root: Path = typer.Option(REPO_ROOT, hidden=True),
) -> None:
    """Fetch/cache DEM windows, compute metrics, classify; write the sidecar and meta.json."""
    t0 = time.time()
    cfg = load_rules(root)
    sel = select_rows(root, register, rows).reset_index(drop=True)
    coast = load_coast(root, float(cfg["coast"]["densify_km"]))
    ckm, _ = coast.query(sel.lat.to_numpy(float), sel.lon.to_numpy(float), k=1)
    with ThreadPoolExecutor(max_workers=workers) as ex:
        results = list(ex.map(lambda i: process_row(root, sel.iloc[i], cfg), range(len(sel))))
    recs, index = [], []
    for i, res in enumerate(results):
        r = sel.iloc[i]
        met = dict(res["metrics"], coast_km=round(float(ckm[i, 0]), 2))
        cls, fired, flags = classify(met, cfg["rule"])
        cls_min = classify(dict(res["metrics_rmin"], coast_km=met["coast_km"]), cfg["rule"])[0]
        if cls_min != cls:
            flags.append("class_differs_at_min_radius")
        if res["info"]["tiles_missing"]:
            flags.append("ocean_tiles_filled_0m")
        recs.append(
            {
                "row_key": r.row_key,
                "terrain_class_dem": cls,
                "slope_mean_deg": met["slope_mean_deg"],
                "slope_p50_deg": met["slope_p50_deg"],
                "slope_p90_deg": met["slope_p90_deg"],
                "relief_m": met["relief_m"],
                "elev_mean_m": met["elev_mean_m"],
                "rough_m": met["rough_m"],
                "coast_km": met["coast_km"],
                "radius_km": round(res["radius_km"], 2),
                "terrain_class_dem_rmin": cls_min,
                "dem_tile": res["info"]["tiles"],
                "utm_epsg": res["epsg"],
                "rule_fired": fired,
                "flags": ";".join(flags),
                "method": METHOD,
                "terrain_class_prior": r.terrain_class
                if isinstance(r.terrain_class, str)
                else None,
            }
        )
        index.append(res["info"])
    df = pd.DataFrame(recs).sort_values("row_key").reset_index(drop=True)
    out_dir = root / out
    out_dir.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out_dir / f"terrain_dem_{rows}.parquet", index=False)
    if rows == "all":
        df.to_parquet(root / sidecar, index=False)
    # window index (manifest-hashed): merge with any earlier index so both selections are listed
    idx_path = root / CACHE / "index.csv"
    old = {}
    if idx_path.exists():
        with idx_path.open(encoding="utf-8") as f:
            old = {row["row_key"]: row for row in csv.DictReader(f)}
    for row in index:
        old[row["row_key"]] = {k: str(v) for k, v in row.items()}
    fields = [
        "row_key",
        "file",
        "west",
        "south",
        "east",
        "north",
        "tiles",
        "tiles_missing",
        "bytes",
        "sha256",
    ]
    with idx_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        for k in sorted(old):
            w.writerow({c: old[k][c] for c in fields})
    cache_bytes = sum(int(v["bytes"]) for v in old.values())
    prior = df.terrain_class_prior
    summary = {
        "rows": len(df),
        "class_counts": {k: int(v) for k, v in df.terrain_class_dem.value_counts().items()},
        "prior_nan_filled": int(prior.isna().sum()),
        "changed_vs_prior": int((prior.notna() & (prior != df.terrain_class_dem)).sum()),
        "same_as_prior": int((prior == df.terrain_class_dem).sum()),
        "crosstab_prior_x_dem": crosstab(prior, df.terrain_class_dem),
        "flags": {
            f: int(df["flags"].str.contains(f).sum())
            for f in (
                "sabkha_signature_dem_only",
                "dune_signature_dem_only",
                "within_coastal_distance",
                "ocean_tiles_filled_0m",
                "class_differs_at_min_radius",
            )
        },
        "window_cache_files": len(old),
        "window_cache_bytes": cache_bytes,
        "remote_tiles_seen": len(_TILE_EXISTS),
        "remote_tiles_missing": sorted(
            u.split("/")[-1] for u, ok in _TILE_EXISTS.items() if not ok
        ),
        "seconds": round(time.time() - t0, 1),
    }
    (out_dir / f"summary_{rows}.json").write_text(json.dumps(summary, indent=1) + "\n")
    write_meta(
        out_dir,
        seed,
        {"rules": cfg, "rules_hash": config_hash(cfg), "register": str(register), "rows": rows},
        extra={
            "assumptions": [f"A-geo-0{i}" for i in range(11, 23)],
            "label_note": "terrain is an input class, not a modelled output; " + LABEL,
            "summary_file": f"summary_{rows}.json",
            "dem": "Copernicus DEM GLO-30 Public (AWS Open Data COG), manifest cop-dem-glo30-aws",
            "attribution": (
                "produced using Copernicus WorldDEM-30 (c) DLR e.V. 2010-2014 and (c) Airbus "
                "Defence and Space GmbH 2014-2018 provided under COPERNICUS by the European Union "
                "and ESA; all rights reserved"
            ),
        },
    )
    (out_dir / f"meta_{rows}.json").write_text((out_dir / "meta.json").read_text())
    typer.echo(
        json.dumps(
            {
                k: summary[k]
                for k in ("rows", "class_counts", "changed_vs_prior", "prior_nan_filled", "seconds")
            },
            indent=1,
        )
    )


if __name__ == "__main__":
    app()
