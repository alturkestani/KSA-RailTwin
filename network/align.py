# ruff: noqa: E501
"""Terrain-aware alignments (R4_ALIGN): least-cost path routing on Copernicus GLO-30 at 3 arc-seconds.

Method (prompts/R4_ALIGN.md; parameters in cities/ksa/assumptions/align_weights.yaml, A-align-0xx):

1. **Cost surface.** Per leg (consecutive stations), a window bounded by an ellipse with the two
   stations as foci (A-align-005). Each cell carries the DEM, the OSM/WorldCover flags of
   network/align_data.py, a D8 flow accumulation (wadis, A-align-030) and the distance to a highway or
   existing rail line (A-align-029). Edge cost (16-connected) = length x (1 + w_grade (g/cap)^2) at
   grade, or length x structure factor (tunnel/viaduct cost over the at-grade base, derived from the
   cost register, A-align-021) where the grade g on the smoothed DEM (A-align-006) exceeds the line
   class cap (a hard mask on at-grade running); x (1 + area penalties: urban, protected, military,
   sand, sabkha, wadi, inland water); x (1 - corridor bonus) next to an existing corridor. Sea cells
   are impassable.
2. **Two passes.** Dijkstra (scipy.sparse.csgraph) on a coarse grid over the whole window
   (A-align-003), then at 3" inside a band around the coarse path, piece by piece (A-align-004).
3. **Curvature.** The path is resampled every 50 m and Gaussian-smoothed with the smallest sigma
   that gives every point a radius >= R_min(design speed) (A-align-012), within a maximum offset from
   the least-cost path (A-align-052). Remaining tighter curves become speed restrictions
   v = sqrt(R (E + I) / 11.8).
4. **Vertical profile.** A formation profile with |grade| <= cap is fitted to the ground by a linear
   programme (L1 distance plus a penalty beyond the structure thresholds, A-align-041..043). Formation
   more than 15 m above ground = viaduct, more than 25 m below = tunnel, the rest earthworks (cut/fill
   volumes), water = bridge (viaduct). The cap is re-checked on the result.
5. **Terrain class** per 100 m sample (A-align-060) for the cost register's terrain shares.

CLI:
  uv run python -m network.align route --corridor cities/ksa/corridors/trunk_gap/<id>.yaml --seed 1
  uv run python -m network.align route-all --seed 1 [--workers 3]
  uv run python -m network.align validate --seed 1 [--weights <yaml>] --out runs/align/validation-s1
  uv run python -m network.align tune --seed 1
  uv run python -m network.align freeze
  uv run python -m network.align apply          # sidecars under cities/ksa/corridors/alignments/
  uv run python -m network.align maps --seed 1

Label: hypothetical alignments (ours), indicative engineering sketch, not a design. Produced using
Copernicus WorldDEM-30 (c) DLR e.V. 2010-2014 and (c) Airbus Defence and Space GmbH 2014-2018
provided under COPERNICUS by the European Union and ESA; all rights reserved. ESA WorldCover 2021
v200 (CC BY 4.0). Map data (c) OpenStreetMap contributors (ODbL).
"""

from __future__ import annotations

import functools
import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import typer
import yaml
from scipy import ndimage, sparse
from scipy.sparse import csgraph

from common import REPO_ROOT
from common.runmeta import canonical_json, seed_option, write_meta
from network import align_data as ad

WEIGHTS = Path("cities/ksa/assumptions/align_weights.yaml")
CORRIDORS = Path("cities/ksa/corridors")
SIDECARS = Path("cities/ksa/alignments")
LINES = Path("cities/ksa/lines")
RUNS = Path("runs/align")
COAST = Path("data/ksa/dem/coast/coastline.geojsonseq")
REGISTER = Path("cities/ksa/costs/cost_register.yaml")
COST_MAP = Path("costs/config/estimate_map.yaml")
COST_INDEX = Path("cities/ksa/costs/index.yaml")
LABEL = "hypothetical alignment (ours): indicative engineering sketch, not a design"
M_PER_DEG_LAT = 110_574.0
M_PER_DEG_LON = 111_320.0
OFFSETS16 = [(0, 1), (1, 0), (1, 1), (1, -1), (1, 2), (2, 1), (1, -2), (2, -1)]
OFFSETS8 = OFFSETS16[:4]
# validation: lines excluded from the "existing rail" corridor layer when routing each line
VALIDATION_EXCLUDE = {
    "hhr": ["hhr"],
    "sar-north-passenger": ["sar-north-passenger", "sar-north-freight"],
    "sar-east-passenger": ["sar-east-passenger", "sar-east-freight-legacy"],
}

app = typer.Typer(add_completion=False, help=__doc__, no_args_is_help=True)


@app.callback()
def _group() -> None:
    """Terrain-aware alignments (R4_ALIGN)."""


def _v(x: Any) -> Any:
    return x["value"] if isinstance(x, dict) and "value" in x else x


def load_weights(path: Path | None = None, root: Path = REPO_ROOT) -> dict[str, Any]:
    return yaml.safe_load(((root / WEIGHTS) if path is None else path).read_text("utf-8"))


def weights_hash(w: dict[str, Any]) -> str:
    """SHA-256 of the canonical JSON of the weights (recorded in every meta.json)."""
    return hashlib.sha256(canonical_json(w).encode("utf-8")).hexdigest()


def structure_factor(line_type: str, root: Path = REPO_ROOT) -> float:
    """Mean of the tunnel and viaduct central over the at-grade base central, all normalised to the
    index base (2025 SAR) as costs.estimate prices them (A-align-021)."""
    from costs.register import normalised_lookup

    items = normalised_lookup(root / REGISTER, root / COST_INDEX)
    cmap = yaml.safe_load((root / COST_MAP).read_text(encoding="utf-8"))
    base = float(items[cmap["line_base"][line_type]]["central"])
    st = [float(items[cmap["structure"][s]]["central"]) for s in ("tunnel", "viaduct")]
    return float(np.mean(st) / base)


@dataclass
class Klass:
    name: str
    cap: float
    design_kmh: float
    r_min_m: float
    e_plus_i_mm: float
    sf: float


def line_class(line_type: str, w: dict[str, Any], root: Path = REPO_ROOT) -> Klass:
    c = w["classes"]
    k = c[line_type]
    anc = c["radius_anchor"]
    ei = 11.8 * float(anc["v_kmh"]) ** 2 / float(anc["r_m"])
    v = float(k["design_kmh"])
    sf = _v(w["weights"]["structure_factor"])
    sf = structure_factor(line_type, root) if sf == "derived" else float(sf)
    return Klass(line_type, float(_v(k["max_grade"])), v, 11.8 * v * v / ei, ei, sf)


# --------------------------------------------------------------------------- raster access
@functools.lru_cache(maxsize=48)
def _tile(t: str, step: int, root_s: str) -> tuple[np.ndarray, np.ndarray, np.ndarray] | None:
    """(dem, flags, wc) of one tile at `step` x 3"; None for a sea tile. Coarse steps reduce by
    block: DEM mean, line flags (waterway, highway) any, area flags and WorldCover majority."""
    import rasterio

    root = Path(root_s)
    p = root / ad.TILES / "dem" / f"{t}.tif"
    if not p.exists():
        return None
    with rasterio.open(p) as s:
        dem = s.read(1).astype(np.float32)
    fp, wp = root / ad.TILES / "flags" / f"{t}.tif", root / ad.TILES / "wc" / f"{t}.tif"
    flags = np.zeros_like(dem, np.uint16)
    if fp.exists():
        with rasterio.open(fp) as s:
            flags = s.read(1)
    wc = np.zeros_like(dem, np.uint8)
    if wp.exists():
        with rasterio.open(wp) as s:
            wc = s.read(1)
    # WorldCover: built-up -> builtup flag, water (80) -> water flag, herbaceous wetland (90) on
    # low ground -> sabkha signature is NOT inferred here (OSM only); mangroves -> water
    flags = flags | np.where(wc == 50, ad.FLAGS["builtup"], 0).astype(np.uint16)
    flags = flags | np.where((wc == 80) | (wc == 95), ad.FLAGS["water"], 0).astype(np.uint16)
    if step == 1:
        return dem, flags, wc
    n = ad.PX // step
    d = dem.reshape(n, step, n, step).mean(axis=(1, 3))
    out = np.zeros((n, n), np.uint16)
    for k, b in ad.FLAGS.items():
        m = ((flags & b) > 0).reshape(n, step, n, step)
        hit = m.any(axis=(1, 3)) if k in ("waterway", "highway") else m.mean(axis=(1, 3)) >= 0.5
        out |= (hit * b).astype(np.uint16)
    return d.astype(np.float32), out, np.zeros((n, n), np.uint8)


@dataclass
class Grid:
    """A lat/lon raster window on the global 3"-multiple grid: row 0 = north edge."""

    step: int
    r0: int  # global row of the first row (rows counted from 90 N in cells of step x 3")
    c0: int  # global column (from 0 E)
    dem: np.ndarray
    flags: np.ndarray

    @property
    def res(self) -> float:
        return self.step * ad.RES

    def lat(self, r: Any) -> Any:
        return 90.0 - (self.r0 + np.asarray(r) + 0.5) * self.res

    def lon(self, c: Any) -> Any:
        return (self.c0 + np.asarray(c) + 0.5) * self.res

    def rc(self, lat: Any, lon: Any) -> tuple[Any, Any]:
        r = (90.0 - np.asarray(lat)) / self.res - self.r0 - 0.5
        c = np.asarray(lon) / self.res - self.c0 - 0.5
        return r, c


def read_grid(bounds: tuple[float, float, float, float], step: int, root: Path) -> Grid:
    """Mosaic of the tiles covering (west, south, east, north) at step x 3"; sea = NaN."""
    w, s, e, n = bounds
    res = step * ad.RES
    r0, r1 = int(math.floor((90.0 - n) / res)), int(math.ceil((90.0 - s) / res))
    c0, c1 = int(math.floor(w / res)), int(math.ceil(e / res))
    H, W = r1 - r0, c1 - c0
    dem = np.full((H, W), np.nan, np.float32)
    flags = np.zeros((H, W), np.uint16)
    per = ad.PX // step
    tiles = set(ad.tile_list(root))
    for la in range(int(math.floor(s)), int(math.ceil(n))):
        for lo in range(int(math.floor(w)), int(math.ceil(e))):
            t = ad.tile_id(la, lo)
            if t not in tiles:
                continue
            got = _tile(t, step, str(root))
            if got is None:
                continue
            td, tf, _ = got
            tr0 = int(round((90.0 - (la + 1)) / res))
            tc0 = int(round(lo / res))
            a0, a1 = max(r0, tr0), min(r1, tr0 + per)
            b0, b1 = max(c0, tc0), min(c1, tc0 + per)
            if a1 <= a0 or b1 <= b0:
                continue
            dem[a0 - r0 : a1 - r0, b0 - c0 : b1 - c0] = td[a0 - tr0 : a1 - tr0, b0 - tc0 : b1 - tc0]
            flags[a0 - r0 : a1 - r0, b0 - c0 : b1 - c0] = tf[
                a0 - tr0 : a1 - tr0, b0 - tc0 : b1 - tc0
            ]
    return Grid(step, r0, c0, dem, flags)


def bilinear(
    g: Grid, lat: np.ndarray, lon: np.ndarray, arr: np.ndarray | None = None
) -> np.ndarray:
    a = g.dem if arr is None else arr
    r, c = g.rc(lat, lon)
    return ndimage.map_coordinates(
        np.where(np.isnan(a), 0.0, a).astype(np.float64), [r, c], order=1, mode="nearest"
    )


def nearest_flags(g: Grid, lat: np.ndarray, lon: np.ndarray, arr: np.ndarray) -> np.ndarray:
    r, c = g.rc(lat, lon)
    r = np.clip(np.rint(r).astype(int), 0, arr.shape[0] - 1)
    c = np.clip(np.rint(c).astype(int), 0, arr.shape[1] - 1)
    return arr[r, c]


# --------------------------------------------------------------------------- rail lines layer
@functools.lru_cache(maxsize=1)
def _rail_geoms(root_s: str) -> dict[str, Any]:
    from shapely.geometry import shape

    out = {}
    for p in sorted((Path(root_s) / LINES / "geojson").glob("*.geojson")):
        d = json.loads(p.read_text(encoding="utf-8"))
        feats = [f for f in d.get("features", []) if f.get("properties", {}).get("layer")]
        if len(feats) != 1 or feats[0]["properties"].get("layer") != "existing":
            continue
        lid = feats[0]["properties"].get("line_id") or p.stem
        if lid.startswith("riyadh-metro"):
            continue
        out[lid] = shape(feats[0]["geometry"])
    return out


@functools.lru_cache(maxsize=1)
def _ksa(root_s: str):
    return ad.ksa_shape(Path(root_s))


def ksa_mask(g: Grid, root: Path) -> np.ndarray:
    """Cells inside the OSM Saudi Arabia boundary (relation 307584): routes stay in the Kingdom
    (A-align-090)."""
    from rasterio.features import rasterize
    from rasterio.transform import from_origin

    tr = from_origin(g.c0 * g.res, 90.0 - g.r0 * g.res, g.res, g.res)
    return rasterize(
        [(_ksa(str(root)), 1)], out_shape=g.dem.shape, transform=tr, dtype="uint8"
    ).astype(bool)


def rail_parts(geom: Any) -> list[Any]:
    """The LineString parts of a rail geometry (a MultiLineString yields every part)."""
    return list(getattr(geom, "geoms", [geom]))


def rail_layer_hashes(root: Path) -> dict[str, str]:
    """SHA-256 of the rail files the corridor bonus reads (per-line GeoJSON) and of existing.geojson."""
    base = root / LINES / "geojson"
    names = sorted(f"{k}.geojson" for k in _rail_geoms(str(root))) + ["existing.geojson"]
    return {n: ad.sha256(base / n) for n in names if (base / n).exists()}


def rail_mask(g: Grid, exclude: list[str], root: Path) -> np.ndarray:
    from rasterio.features import rasterize
    from rasterio.transform import from_origin

    # FIX_HHR_REROUTE: every part of a MultiLineString (HHR main line + KAIA branch) is burnt into the
    # corridor-bonus band; no part is dropped and nothing joins the parts (no chord between them).
    geoms = [
        part
        for k, v in _rail_geoms(str(root)).items()
        if k not in set(exclude)
        for part in rail_parts(v)
    ]
    if not geoms:
        return np.zeros(g.dem.shape, bool)
    tr = from_origin(g.c0 * g.res, 90.0 - g.r0 * g.res, g.res, g.res)
    return rasterize(
        [(x, 1) for x in geoms],
        out_shape=g.dem.shape,
        transform=tr,
        all_touched=True,
        dtype="uint8",
    ).astype(bool)


# --------------------------------------------------------------------------- cost surface
def cell_m(g: Grid) -> tuple[float, np.ndarray]:
    """(dy metres, dx metres per row)."""
    dy = g.res * M_PER_DEG_LAT
    dx = g.res * M_PER_DEG_LON * np.cos(np.radians(g.lat(np.arange(g.dem.shape[0]))))
    return dy, dx


def flow_accumulation_km2(g: Grid) -> np.ndarray:
    """D8 flow accumulation (km2 upstream) on the window; pits and flats stop flow (no filling;
    a proxy for wadi channels, A-align-030); sea cells drain nothing."""
    z = np.where(np.isnan(g.dem), -1e4, g.dem).astype(np.float64)
    H, W = z.shape
    dy, dxr = cell_m(g)
    area = (dy * dxr[:, None] * np.ones((1, W))) / 1e6
    best = np.zeros((H, W))
    recv = np.full((H, W), -1, np.int64)
    idx = np.arange(H * W).reshape(H, W)
    zp = np.pad(z, 1, constant_values=np.inf)
    ip = np.pad(idx, 1, constant_values=-1)
    for di in (-1, 0, 1):
        for dj in (-1, 0, 1):
            if di == dj == 0:
                continue
            dist = math.hypot(di * dy, dj * float(np.mean(dxr)))
            nz = zp[1 + di : 1 + di + H, 1 + dj : 1 + dj + W]
            drop = (z - nz) / dist
            take = drop > best
            best = np.where(take, drop, best)
            recv = np.where(take, ip[1 + di : 1 + di + H, 1 + dj : 1 + dj + W], recv)
    acc = area.ravel().copy()
    rv = recv.ravel()
    order = np.argsort(-z.ravel(), kind="stable")
    for i in order:
        j = rv[i]
        if j >= 0:
            acc[j] += acc[i]
    acc = acc.reshape(H, W)
    acc[np.isnan(g.dem)] = 0.0
    return acc


def penalty_surface(
    g: Grid, w: dict[str, Any], facc: np.ndarray | None, rail: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """(area penalty per cell, corridor flag per cell)."""
    W = w["weights"]
    f = g.flags
    F = ad.FLAGS

    def on(k: str) -> np.ndarray:
        return (f & F[k]) > 0

    pen = np.zeros(f.shape)
    pen += float(_v(W["urban"])) * (on("urban") | on("builtup"))
    pen += float(_v(W["protected"])) * on("protected")
    pen += float(_v(W["military"])) * on("military")
    pen += float(_v(W["sand"])) * on("sand")
    pen += float(_v(W["sabkha"])) * on("sabkha")
    wadi = on("waterway")
    if facc is not None:
        wadi = wadi | (facc >= float(_v(w["wadi"]["flow_accumulation_km2"])))
    pen += float(_v(W["wadi"])) * wadi
    pen += float(_v(W["water"])) * on("water")
    corr = on("highway") | rail
    km = float(_v(W["corridor_km"]))
    dy, dxr = cell_m(g)
    cells = max(1, int(round(km * 1000 / min(dy, float(np.min(dxr))))))
    if corr.any():
        corr = ndimage.binary_dilation(corr, iterations=cells)
    return pen, corr


def build_graph(
    g: Grid,
    mask: np.ndarray,
    kl: Klass,
    w: dict[str, Any],
    pen: np.ndarray,
    corr: np.ndarray,
    connectivity: int = 16,
) -> tuple[sparse.csr_matrix, np.ndarray]:
    """Undirected weighted graph over the masked, non-sea cells; returns (matrix, node id grid)."""
    H, W = g.dem.shape
    valid = mask & ~np.isnan(g.dem)
    nid = np.full((H, W), -1, np.int64)
    nid[valid] = np.arange(int(valid.sum()))
    dy, dxr = cell_m(g)
    sig_m = float(_v(w["router"]["grade_smoothing_m"]))
    zf = np.where(np.isnan(g.dem), np.nanmean(g.dem) if np.isfinite(g.dem).any() else 0, g.dem)
    zs = ndimage.gaussian_filter(zf.astype(np.float64), sigma=max(sig_m / dy, 0.5), mode="nearest")
    wg = float(_v(w["weights"]["grade"]))
    bonus = float(_v(w["weights"]["corridor_bonus"]))
    kx = float(_v(w["weights"].get("structure_grade_exponent", 0.0)))
    db = float(_v(w["weights"].get("grade_deadband", {"value": 0.0})))
    rows, cols, vals = [], [], []
    for di, dj in OFFSETS16 if connectivity == 16 else OFFSETS8:
        a0, a1 = 0, H - di
        b0, b1 = max(0, -dj), W - max(0, dj)
        va = valid[a0:a1, b0:b1]
        vb = valid[a0 + di : a1 + di, b0 + dj : b1 + dj]
        both = va & vb
        if not both.any():
            continue
        dxm = 0.5 * (dxr[a0:a1] + dxr[a0 + di : a1 + di])[:, None]
        L = np.sqrt((di * dy) ** 2 + (dj * dxm) ** 2) * np.ones_like(va, float)
        dz = np.abs(zs[a0:a1, b0:b1] - zs[a0 + di : a1 + di, b0 + dj : b1 + dj])
        gr = dz / L
        over = np.maximum(gr / kl.cap, 1.0) ** kx  # steeper ground = longer structures
        if db > 0:  # v2 (A-align-101): grades below db x cap cost nothing (earthworks absorb them)
            gn = np.maximum(0.0, gr / kl.cap - db) / (1.0 - db)
            base = np.where(gr <= kl.cap, 1.0 + wg * gn**2, kl.sf * over)
        else:
            base = np.where(gr <= kl.cap, 1.0 + wg * (gr / kl.cap) ** 2, kl.sf * over)
        p = 0.5 * (pen[a0:a1, b0:b1] + pen[a0 + di : a1 + di, b0 + dj : b1 + dj])
        cf = np.where(
            corr[a0:a1, b0:b1] & corr[a0 + di : a1 + di, b0 + dj : b1 + dj], 1.0 - bonus, 1.0
        )
        cost = L * base * (1.0 + p) * cf
        rows.append(nid[a0:a1, b0:b1][both])
        cols.append(nid[a0 + di : a1 + di, b0 + dj : b1 + dj][both])
        vals.append(cost[both])
    n = int(valid.sum())
    m = sparse.coo_matrix(
        (np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))), shape=(n, n)
    ).tocsr()
    return m, nid


def snap(g: Grid, nid: np.ndarray, lat: float, lon: float) -> int:
    r, c = g.rc(lat, lon)
    r, c = (
        int(np.clip(round(float(r)), 0, nid.shape[0] - 1)),
        int(np.clip(round(float(c)), 0, nid.shape[1] - 1)),
    )
    if nid[r, c] >= 0:
        return int(nid[r, c])
    rr, cc = np.nonzero(nid >= 0)
    k = int(np.argmin((rr - r) ** 2 + (cc - c) ** 2))
    return int(nid[rr[k], cc[k]])


def shortest(m: sparse.csr_matrix, nid: np.ndarray, src: int, dst: int) -> np.ndarray:
    """(k, 2) array of (row, col) along the least-cost path from src to dst."""
    dist, pred = csgraph.dijkstra(m, directed=False, indices=src, return_predecessors=True)
    if not np.isfinite(dist[dst]):
        raise RuntimeError("no path inside the window")
    path = [dst]
    while path[-1] != src:
        path.append(int(pred[path[-1]]))
    path.reverse()
    rr, cc = np.nonzero(nid >= 0)
    inv = np.empty(len(rr), np.int64)
    inv[nid[rr, cc]] = np.arange(len(rr))
    k = inv[np.array(path)]
    return np.column_stack([rr[k], cc[k]])


def gc_km(lat1: Any, lon1: Any, lat2: Any, lon2: Any) -> Any:
    from network.geo import haversine_km

    return haversine_km(lat1, lon1, lat2, lon2)


def _lim(a, b, w, e: float) -> float:
    L = float(gc_km(a[0], a[1], b[0], b[1]))
    hw = float(_v(w["router"]["window_min_halfwidth_km"]))
    return max(e * L, math.sqrt(L * L + 4 * hw * hw))


def ellipse_steps(w: dict[str, Any]) -> list[float]:
    """Window ellipse factors tried in order (A-align-005): widened while the path touches the edge."""
    steps = w["router"].get("window_ellipse_steps")
    return [float(x) for x in _v(steps)] if steps else [float(_v(w["router"]["window_ellipse"]))]


def ellipse_mask(
    g: Grid, a: tuple[float, float], b: tuple[float, float], w: dict, e: float | None = None
) -> np.ndarray:
    H, W = g.dem.shape
    lat = g.lat(np.arange(H))[:, None] * np.ones((1, W))
    lon = g.lon(np.arange(W))[None, :] * np.ones((H, 1))
    d = gc_km(lat, lon, a[0], a[1]) + gc_km(lat, lon, b[0], b[1])
    return d <= _lim(a, b, w, ellipse_steps(w)[0] if e is None else e)


def window_bounds(a, b, w, e: float | None = None) -> tuple[float, float, float, float]:
    semi = _lim(a, b, w, ellipse_steps(w)[0] if e is None else e) / 2.0
    mlat = 0.5 * (a[0] + b[0])
    dlat = semi / 110.574 + 0.05
    dlon = semi / (111.320 * math.cos(math.radians(mlat))) + 0.05
    return (
        min(a[1], b[1]) - dlon + abs(a[1] - b[1]) / 2 * 0,
        min(a[0], b[0]) - dlat,
        max(a[1], b[1]) + dlon,
        max(a[0], b[0]) + dlat,
    )


def straightness_penalty(
    g: Grid, a: tuple[float, float], b: tuple[float, float], w: dict[str, Any]
) -> np.ndarray | None:
    """v2 (A-align-102): extra area penalty s x (distance to the station-to-station chord / 10 km)
    on flat cells (relief < flat_relief_m within a relief_box_km box, A-align-103); None when s = 0
    (weights v1 have no such key, so v1 routing is unchanged)."""
    W = w["weights"]
    s = float(_v(W.get("straightness", {"value": 0.0})))
    if s <= 0:
        return None
    H, Wd = g.dem.shape
    lat0 = 0.5 * (a[0] + b[0])
    kx = M_PER_DEG_LON * math.cos(math.radians(lat0)) / 1000.0
    ky = M_PER_DEG_LAT / 1000.0
    y = (g.lat(np.arange(H))[:, None] - a[0]) * ky * np.ones((1, Wd))
    x = (g.lon(np.arange(Wd))[None, :] - a[1]) * kx * np.ones((H, 1))
    bx, by = (b[1] - a[1]) * kx, (b[0] - a[0]) * ky
    L2 = max(bx * bx + by * by, 1e-9)
    u = np.clip((x * bx + y * by) / L2, 0.0, 1.0)
    d = np.hypot(x - u * bx, y - u * by)
    rel_m = float(_v(W.get("straightness_flat_relief_m", {"value": 40.0})))
    box_km = float(_v(w["terrain_class"]["relief_box_km"]))
    dy, dxr = cell_m(g)
    k = max(1, int(round(box_km * 1000 / min(dy, float(np.min(dxr))))))
    zf = np.where(np.isnan(g.dem), np.nanmean(g.dem) if np.isfinite(g.dem).any() else 0, g.dem)
    relief = ndimage.maximum_filter(zf, size=k) - ndimage.minimum_filter(zf, size=k)
    return s * (d / 10.0) * (relief < rel_m)


def route_leg(
    a: tuple[float, float],
    b: tuple[float, float],
    kl: Klass,
    w: dict[str, Any],
    exclude: list[str],
    root: Path,
) -> tuple[np.ndarray, dict[str, Any]]:
    """Least-cost path between two stations: (n, 2) lat/lon at 3" and diagnostics."""
    R = w["router"]
    step_c = int(round(float(_v(R["coarse_arcsec"])) / float(_v(w["data"]["resolution_arcsec"]))))
    conn = int(R["connectivity"])
    touch = float(_v(w["router"].get("window_touch", 0.97)))
    for e in ellipse_steps(w):
        bounds = window_bounds(a, b, w, e)
        gc = read_grid(bounds, step_c, root)
        mask = ellipse_mask(gc, a, b, w, e) & ksa_mask(gc, root)
        facc = flow_accumulation_km2(gc)
        pen, corr = penalty_surface(gc, w, facc, rail_mask(gc, exclude, root))
        sp = straightness_penalty(gc, a, b, w)
        if sp is not None:
            pen = pen + sp
        m, nid = build_graph(gc, mask, kl, w, pen, corr, conn)
        path_c = shortest(m, nid, snap(gc, nid, *a), snap(gc, nid, *b))
        plat, plon = gc.lat(path_c[:, 0]), gc.lon(path_c[:, 1])
        reach = float(
            np.max(gc_km(plat, plon, a[0], a[1]) + gc_km(plat, plon, b[0], b[1])) / _lim(a, b, w, e)
        )
        if reach < touch:
            break
    plat[0], plon[0], plat[-1], plon[-1] = a[0], a[1], b[0], b[1]
    diag = {
        "coarse_nodes": int(m.shape[0]),
        "coarse_cells": int(len(path_c)),
        "window_ellipse": e,
        "window_reach": round(reach, 4),
        "window_bound": bool(reach >= touch),
    }
    # fine pass, piece by piece inside the band around the coarse path
    seg = gc_km(plat[:-1], plon[:-1], plat[1:], plon[1:])
    cum = np.concatenate([[0.0], np.cumsum(seg)])
    piece = float(_v(R["fine_piece_km"]))
    n_p = max(1, int(math.ceil(cum[-1] / piece)))
    cuts = [int(np.searchsorted(cum, cum[-1] * k / n_p)) for k in range(n_p)] + [len(cum) - 1]
    cuts = sorted(set(cuts))
    band = float(_v(R["fine_band_km"]))
    out: list[np.ndarray] = []
    fine_nodes = 0
    for i0, i1 in zip(cuts[:-1], cuts[1:], strict=False):
        la, lo = plat[i0 : i1 + 1], plon[i0 : i1 + 1]
        pad_lat = band / 110.574 + 0.02
        pad_lon = band / (111.320 * math.cos(math.radians(float(la.mean())))) + 0.02
        bb = (lo.min() - pad_lon, la.min() - pad_lat, lo.max() + pad_lon, la.max() + pad_lat)
        gf = read_grid(bb, 1, root)
        H, W = gf.dem.shape
        # band mask: distance to the coarse polyline (rasterised buffer in degrees, local scale)
        from rasterio.features import rasterize
        from rasterio.transform import from_origin
        from shapely.affinity import scale
        from shapely.geometry import LineString

        ky = 1.0 / 110.574
        kx = 1.0 / (111.320 * math.cos(math.radians(float(la.mean()))))
        line = LineString(np.column_stack([lo, la])) if len(la) > 1 else None
        if line is None:
            continue
        # buffer in km space, back to degrees
        lk = scale(line, xfact=1 / kx, yfact=1 / ky, origin=(0, 0))
        buf = scale(lk.buffer(band), xfact=kx, yfact=ky, origin=(0, 0))
        tr = from_origin(gf.c0 * gf.res, 90.0 - gf.r0 * gf.res, gf.res, gf.res)
        bmask = rasterize([(buf, 1)], out_shape=(H, W), transform=tr, dtype="uint8").astype(bool)
        # wadi flags: OSM waterways at 3" plus the coarse flow accumulation looked up per cell
        rr = np.arange(H)[:, None] * np.ones((1, W))
        cc = np.arange(W)[None, :] * np.ones((H, 1))
        fa = nearest_flags(gc, gf.lat(rr).ravel(), gf.lon(cc).ravel(), facc).reshape(H, W)
        penf, corrf = penalty_surface(gf, w, fa, rail_mask(gf, exclude, root))
        spf = straightness_penalty(gf, a, b, w)
        if spf is not None:
            penf = penf + spf
        mf, nidf = build_graph(gf, bmask & ksa_mask(gf, root), kl, w, penf, corrf, conn)
        fine_nodes += int(mf.shape[0])
        pf = shortest(
            mf,
            nidf,
            snap(gf, nidf, float(la[0]), float(lo[0])),
            snap(gf, nidf, float(la[-1]), float(lo[-1])),
        )
        pts = np.column_stack([gf.lat(pf[:, 0]), gf.lon(pf[:, 1])])
        out.append(pts if not out else pts[1:])
    path = np.vstack(out)
    path[0], path[-1] = a, b
    diag["fine_nodes"] = fine_nodes
    return path, diag


# --------------------------------------------------------------------------- geometry
def to_xy(lat: np.ndarray, lon: np.ndarray, lat0: float, lon0: float):
    from pyproj import Transformer

    t = Transformer.from_crs(
        "EPSG:4326", f"+proj=aeqd +lat_0={lat0} +lon_0={lon0} +datum=WGS84 +units=m", always_xy=True
    )
    return t


def resample(xy: np.ndarray, step: float) -> np.ndarray:
    d = np.concatenate([[0.0], np.cumsum(np.hypot(*np.diff(xy, axis=0).T))])
    n = max(2, int(math.ceil(d[-1] / step)) + 1)
    s = np.linspace(0.0, d[-1], n)
    return np.column_stack([np.interp(s, d, xy[:, 0]), np.interp(s, d, xy[:, 1])])


def gauss_pinned(xy: np.ndarray, sigma_pts: float) -> np.ndarray:
    """Gaussian smoothing with both ends pinned (odd reflection about each end point)."""
    if sigma_pts <= 0 or len(xy) < 5:
        return xy.copy()
    k = int(min(len(xy) - 2, math.ceil(4 * sigma_pts)))
    head = 2 * xy[0] - xy[1 : k + 1][::-1]
    tail = 2 * xy[-1] - xy[-k - 1 : -1][::-1]
    ext = np.vstack([head, xy, tail])
    sm = ndimage.gaussian_filter1d(ext, sigma_pts, axis=0, mode="nearest")[k : k + len(xy)]
    sm[0], sm[-1] = xy[0], xy[-1]
    return sm


def radius_m(xy: np.ndarray, chord_pts: int) -> np.ndarray:
    """Three-point circumradius over +/- chord_pts samples (inf on straight track)."""
    n = len(xy)
    R = np.full(n, np.inf)
    k = max(1, chord_pts)
    if n <= 2 * k:
        return R
    p0, p1, p2 = xy[: n - 2 * k], xy[k : n - k], xy[2 * k :]
    a = np.hypot(*(p1 - p0).T)
    b = np.hypot(*(p2 - p1).T)
    c = np.hypot(*(p2 - p0).T)
    cross = np.abs((p1 - p0)[:, 0] * (p2 - p0)[:, 1] - (p1 - p0)[:, 1] * (p2 - p0)[:, 0])
    with np.errstate(divide="ignore", invalid="ignore"):
        r = np.where(cross > 1e-9, a * b * c / (2 * cross), np.inf)
    R[k : n - k] = r
    return R


def offset_m(a: np.ndarray, b: np.ndarray) -> float:
    """Max distance from points of a to the polyline b (metres)."""
    from shapely.geometry import LineString, MultiPoint

    lb = LineString(b)
    return float(max(lb.distance(p) for p in MultiPoint(a[:: max(1, len(a) // 400)]).geoms))


def smooth_leg(xy: np.ndarray, kl: Klass, w: dict[str, Any]) -> tuple[np.ndarray, dict[str, Any]]:
    S = w["smoothing"]
    step = 50.0
    raw = resample(xy, step)
    chord = int(round(float(_v(S["chord_m"])) / step))
    maxoff = float(_v(S["max_offset_km"])) * 1000
    best, info = raw, {"sigma_m": 0.0}
    for sig in _v(S["sigma_steps_m"]):
        sm = gauss_pinned(raw, float(sig) / step)
        sm = resample(sm, step)
        off = offset_m(sm, raw)
        if off > maxoff:
            break
        R = radius_m(sm, chord)
        inner = R[chord:-chord] if len(R) > 2 * chord else R
        best, info = sm, {"sigma_m": float(sig), "max_offset_m": round(off, 1)}
        if len(inner) == 0 or np.min(inner) >= kl.r_min_m:
            break
    return best, info


# --------------------------------------------------------------------------- vertical profile
def fit_profile(
    z: np.ndarray, ds: Any, cap: float, w: dict[str, Any], forced: np.ndarray | None = None
) -> tuple[np.ndarray, bool]:
    """Formation level f: min sum |f - z| + lam * excess beyond the structure thresholds, subject to
    |f_{i+1} - f_i| <= cap * ds and f = z at both ends (HiGHS LP)."""
    from scipy.optimize import linprog

    P = w["profile"]
    hv, ht = float(_v(P["viaduct_fill_m"])), float(_v(P["tunnel_cut_m"]))
    lam = float(_v(P["structure_penalty"]))
    n = len(z)
    if n < 3:
        return z.copy(), False
    # variables: f (n), u (n) = |f - z|, v (n) = excess fill, t (n) = excess cut
    c = np.concatenate([np.zeros(n), np.ones(n), np.full(n, lam), np.full(n, lam)])
    if forced is not None:  # water: no penalty for being high above it (bridge)
        c[n : 2 * n][forced] = 0.0
        c[2 * n : 3 * n][forced] = 0.0
    eye = sparse.identity(n, format="csr")
    Z = sparse.csr_matrix((n, n))
    D = sparse.diags([-np.ones(n - 1), np.ones(n - 1)], [0, 1], shape=(n - 1, n), format="csr")
    Zd = sparse.csr_matrix((n - 1, n))
    A = sparse.vstack(
        [
            sparse.hstack([eye, -eye, Z, Z]),  # f - u <= z
            sparse.hstack([-eye, -eye, Z, Z]),  # -f - u <= -z
            sparse.hstack([eye, Z, -eye, Z]),  # f - v <= z + hv
            sparse.hstack([-eye, Z, Z, -eye]),  # -f - t <= -z + ht
            sparse.hstack([D, Zd, Zd, Zd]),  # f_{i+1} - f_i <= cap ds
            sparse.hstack([-D, Zd, Zd, Zd]),
        ],
        format="csr",
    )
    gmax = cap * np.broadcast_to(np.asarray(ds, float), (n - 1,)) * (1 - 1e-6)
    b = np.concatenate([z, -z, z + hv, -z + ht, gmax, gmax])
    bounds = [(None, None)] * n + [(0, None)] * (3 * n)
    bounds[0] = (z[0], z[0])
    bounds[n - 1] = (z[-1], z[-1])
    res = linprog(c, A_ub=A, b_ub=b, bounds=bounds, method="highs")
    relaxed = False
    if not res.success:
        # the stations' ground levels cannot be joined within the cap over this distance: free the
        # ends (a station on a structure or in a cutting), reported as ends_relaxed
        bounds[0] = bounds[n - 1] = (None, None)
        res = linprog(c, A_ub=A, b_ub=b, bounds=bounds, method="highs")
        relaxed = True
    return np.round(res.x[:n], 3), relaxed


# --------------------------------------------------------------------------- one corridor
@functools.lru_cache(maxsize=1)
def _coast_tree(root_s: str):
    from network.geo import KNearest

    pts = []
    for f in ad._features(Path(root_s) / COAST):
        g = f["geometry"]
        lines = [g["coordinates"]] if g["type"] == "LineString" else g.get("coordinates", [])
        for ln in lines:
            arr = np.asarray(ln, float)
            if arr.ndim != 2 or len(arr) < 2:
                continue
            for p, q in zip(arr[:-1], arr[1:], strict=False):
                d = float(gc_km(p[1], p[0], q[1], q[0]))
                k = max(1, int(math.ceil(d / 0.5)))
                t = np.linspace(0, 1, k, endpoint=False)[:, None]
                pts.append(p + t * (q - p))
    P = np.vstack(pts)
    return KNearest(P[:, 1], P[:, 0])


def corridor_legs(c: dict[str, Any]) -> list[tuple[dict, dict]]:
    st = sorted(c["stations"], key=lambda s: float(s["km_post"]))
    return list(zip(st[:-1], st[1:], strict=False))


def route_corridor(
    c: dict[str, Any],
    w: dict[str, Any],
    root: Path,
    exclude: list[str] | None = None,
    line_type: str | None = None,
) -> dict[str, Any]:
    """Route, smooth and profile every leg of a corridor; returns the result tables."""
    lt = line_type or c["line_type"]
    kl = line_class(lt, w, root)
    P = w["profile"]
    step = float(_v(P["step_m"]))
    samples, legs = [], []
    km0 = 0.0
    for li, (sa, sb) in enumerate(corridor_legs(c)):
        a, b = (float(sa["lat"]), float(sa["lon"])), (float(sb["lat"]), float(sb["lon"]))
        path, diag = route_leg(a, b, kl, w, exclude or [], root)
        lat0, lon0 = float(path[:, 0].mean()), float(path[:, 1].mean())
        t = to_xy(path[:, 0], path[:, 1], lat0, lon0)
        x, y = t.transform(path[:, 1], path[:, 0])
        raw_xy = np.column_stack([x, y])
        sm, sinfo = smooth_leg(raw_xy, kl, w)
        prof = resample(sm, step)
        lon_s, lat_s = t.transform(prof[:, 0], prof[:, 1], direction="INVERSE")
        lat_s, lon_s = np.asarray(lat_s), np.asarray(lon_s)
        # ground and flags at 3" (bounding grid of the leg)
        bb = (lon_s.min() - 0.03, lat_s.min() - 0.03, lon_s.max() + 0.03, lat_s.max() + 0.03)
        gf = read_grid(bb, 1, root)
        zraw = bilinear(gf, lat_s, lon_s)
        sea = np.isnan(nearest_flags(gf, lat_s, lon_s, gf.dem))
        zraw = np.where(sea, 0.0, zraw)
        z = ndimage.median_filter(zraw, size=3, mode="nearest")
        fl = nearest_flags(gf, lat_s, lon_s, gf.flags)
        water = sea | ((fl & ad.FLAGS["water"]) > 0)
        dsv = np.hypot(*np.diff(prof, axis=0).T)
        f, relaxed = fit_profile(z, dsv, kl.cap, w, forced=water)
        # radius and speed on the smoothed line
        chord = int(round(float(_v(w["smoothing"]["chord_m"])) / step))
        R = radius_m(prof, chord)
        v = np.minimum(kl.design_kmh, np.sqrt(np.maximum(R, 0) * kl.e_plus_i_mm / 11.8))
        # relief for the terrain class: 5 offset lines x +/- half box along
        rb = float(_v(w["terrain_class"]["relief_box_km"])) * 1000
        tang = np.gradient(prof, axis=0)
        tang /= np.maximum(np.hypot(*tang.T)[:, None], 1e-9)
        nrm = np.column_stack([-tang[:, 1], tang[:, 0]])
        zs = []
        for o in np.linspace(-rb / 2, rb / 2, 5):
            q = prof + o * nrm
            ql, qa = t.transform(q[:, 0], q[:, 1], direction="INVERSE")
            zs.append(bilinear(gf, np.asarray(qa), np.asarray(ql)))
        zz = np.vstack(zs)
        half = max(1, int(round(rb / 2 / step)))
        zmax = ndimage.maximum_filter1d(zz.max(axis=0), 2 * half + 1, mode="nearest")
        zmin = ndimage.minimum_filter1d(zz.min(axis=0), 2 * half + 1, mode="nearest")
        coast_km, _ = _coast_tree(str(root)).query(lat_s, lon_s)
        s_km = km0 + np.concatenate([[0.0], np.cumsum(np.hypot(*np.diff(prof, axis=0).T))]) / 1000
        df = pd.DataFrame(
            {
                "leg": li,
                "s_km": np.round(s_km, 4),
                "lat": np.round(lat_s, 6),
                "lon": np.round(lon_s, 6),
                "z_ground_m": np.round(z, 2),
                "z_formation_m": f,
                "radius_m": np.round(np.minimum(R, 1e6), 1),
                "vmax_kmh": np.round(v, 1),
                "relief_m": np.round(zmax - zmin, 1),
                "coast_km": np.round(coast_km[:, 0], 2),
                "flag_bits": fl.astype(int),
                "water": water,
            }
        )
        samples.append(df if not samples else df.iloc[1:])
        km0 = float(s_km[-1])
        legs.append(
            {
                "leg": li,
                "from": sa["id"],
                "to": sb["id"],
                "straight_km": round(float(gc_km(a[0], a[1], b[0], b[1])), 3),
                "routed_km": round(float(s_km[-1] - s_km[0]), 3),
                "ends_relaxed": relaxed,
                **diag,
                **sinfo,
            }
        )
    prof = pd.concat(samples, ignore_index=True)
    prof = classify(prof, w, kl)
    return {"profile": prof, "legs": pd.DataFrame(legs), "klass": kl}


def classify(df: pd.DataFrame, w: dict[str, Any], kl: Klass) -> pd.DataFrame:
    P, T = w["profile"], w["terrain_class"]
    h = df.z_formation_m - df.z_ground_m
    hv, ht = float(_v(P["viaduct_fill_m"])), float(_v(P["tunnel_cut_m"]))
    emin = float(_v(P["earthworks_min_m"]))
    st = np.where(
        df.water,
        "viaduct",
        np.where(
            h > hv,
            "viaduct",
            np.where(h < -ht, "tunnel", np.where(h.abs() > emin, "earthworks", "at_grade")),
        ),
    )
    df = df.assign(height_m=np.round(h, 2), structure=st)
    F = ad.FLAGS
    fl = df["flag_bits"].to_numpy()
    sab = (fl & F["sabkha"]) > 0
    sand = (fl & F["sand"]) > 0
    rel = df.relief_m.to_numpy()
    coast = df.coast_km.to_numpy() <= float(_v(T["coastal_km"]))
    conds = {
        "escarpment_mountain": rel >= float(_v(T["escarpment_relief_m"])),
        "sabkha": sab,
        "coastal": coast,
        "dunes": sand,
        "mixed": rel >= float(_v(T["mixed_relief_m"])),
        "flat_desert": np.ones(len(df), bool),
    }
    cls = np.full(len(df), "flat_desert", dtype=object)
    done = np.zeros(len(df), bool)
    for k in T["order"]:
        m = conds[k] & ~done
        cls[m] = k
        done |= m
    return df.assign(terrain=cls)


def seg_km(df: pd.DataFrame) -> np.ndarray:
    """Length each sample stands for (half the gap on each side), km."""
    s = df.s_km.to_numpy()
    d = np.diff(s)
    out = np.zeros(len(s))
    out[:-1] += d / 2
    out[1:] += d / 2
    return out


def restrictions(df: pd.DataFrame, kl: Klass, w: dict[str, Any]) -> list[dict[str, float]]:
    """Speed restrictions (from_km, to_km, kmh) where curvature limits speed below design."""
    S = w["smoothing"]
    stp = float(_v(S["speed_step_kmh"]))
    mn = float(_v(S["min_restriction_km"]))
    v = np.floor(df.vmax_kmh.to_numpy() / stp) * stp
    s = df.s_km.to_numpy()
    out = []
    i = 0
    n = len(v)
    while i < n:
        if v[i] >= kl.design_kmh:
            i += 1
            continue
        j = i
        while j + 1 < n and v[j + 1] < kl.design_kmh:
            j += 1
        lo, hi = max(0.0, s[i] - mn / 2), min(s[-1], s[j] + mn / 2)
        out.append(
            {
                "from_km": round(float(lo), 3),
                "to_km": round(float(hi), 3),
                "kmh": float(v[i : j + 1].min()),
            }
        )
        i = j + 1
    return out


def summarise(c: dict[str, Any], res: dict[str, Any], w: dict[str, Any]) -> dict[str, Any]:
    df, legs, kl = res["profile"], res["legs"], res["klass"]
    km = seg_km(df)
    L = float(df.s_km.iloc[-1])
    straight = float(legs.straight_km.sum())
    end_to_end = float(gc_km(df.lat.iloc[0], df.lon.iloc[0], df.lat.iloc[-1], df.lon.iloc[-1]))
    P = w["profile"]
    h = df.height_m.to_numpy()
    b, sl = float(_v(P["formation_width_m"])), float(_v(P["side_slope_h_per_v"]))
    ew = df.structure.to_numpy() == "earthworks"
    vol = km * 1000 * (b * np.abs(h) + sl * h * h)
    fill = float(vol[ew & (h > 0)].sum())
    cut = float(vol[ew & (h < 0)].sum())
    by = {
        k: round(float(km[df.structure.to_numpy() == k].sum()), 3)
        for k in ("tunnel", "viaduct", "earthworks", "at_grade")
    }
    terr = {
        k: round(float(km[df.terrain.to_numpy() == k].sum()) / L, 4)
        for k in sorted(set(df.terrain))
    }
    F = ad.FLAGS
    fl = df["flag_bits"].to_numpy()
    area_km = {
        k: round(float(km[(fl & F[k]) > 0].sum()), 3)
        for k in (
            "urban",
            "builtup",
            "protected",
            "military",
            "sand",
            "sabkha",
            "waterway",
            "highway",
        )
    }
    ww = (fl & F["waterway"]) > 0
    crossings = int(np.sum(ww[1:] & ~ww[:-1]) + (1 if ww[0] else 0))
    gr = np.abs(np.diff(df.z_formation_m.to_numpy())) / np.maximum(
        np.diff(df.s_km.to_numpy()) * 1000, 1e-6
    )
    gg = np.abs(np.diff(df.z_ground_m.to_numpy())) / np.maximum(
        np.diff(df.s_km.to_numpy()) * 1000, 1e-6
    )
    rs = restrictions(df, kl, w)
    # feasibility: a leg whose station ground levels differ by more than cap x routed length cannot
    # be built at the class cap however many structures it has (A-align-091)
    infeasible = []
    for _, lg in legs.iterrows():
        sub = df[df.leg == lg["leg"]]
        dz = float(abs(sub.z_ground_m.iloc[-1] - sub.z_ground_m.iloc[0]))
        if bool(lg.get("ends_relaxed", False)) or dz > kl.cap * float(lg["routed_km"]) * 1000:
            infeasible.append(
                {
                    "from": lg["from"],
                    "to": lg["to"],
                    "height_difference_m": round(dz, 1),
                    "routed_km": float(lg["routed_km"]),
                    "min_km_at_cap": round(dz / kl.cap / 1000, 1),
                }
            )
    cap_ok = bool((float(gr.max()) if len(gr) else 0.0) <= kl.cap + 5e-5)
    return {
        "id": c["id"],
        "line_type": kl.name,
        "label": LABEL,
        "length_km": round(L, 3),
        "straight_km_legs": round(straight, 3),
        "straight_km_end_to_end": round(end_to_end, 3),
        "detour_ratio": round(L / straight, 4) if straight else None,
        "max_grade_cap": kl.cap,
        "design_kmh": kl.design_kmh,
        "r_min_m": round(kl.r_min_m, 1),
        "structure_factor": round(kl.sf, 4),
        "tunnel_km": by["tunnel"],
        "viaduct_km": by["viaduct"],
        "earthworks_km": by["earthworks"],
        "at_grade_km": by["at_grade"],
        "tunnel_share": round(by["tunnel"] / L, 5),
        "viaduct_share": round(by["viaduct"] / L, 5),
        "fill_m3": round(fill, -2),
        "cut_m3": round(cut, -2),
        "formation_max_grade": round(float(gr.max()) if len(gr) else 0.0, 5),
        # re-check of the cap on the stored profile (mm levels, 0.1 m chainage: 5e-5 rounding)
        "formation_cap_ok": cap_ok,
        "profile_feasible": bool(cap_ok and not infeasible),
        "infeasible_legs": infeasible,
        "ground_share_over_cap": round(float(km[1:][gg > kl.cap].sum()) / L, 4) if len(gg) else 0.0,
        "elev_min_m": round(float(df.z_ground_m.min()), 1),
        "elev_max_m": round(float(df.z_ground_m.max()), 1),
        "terrain_shares": terr,
        "area_km": area_km,
        "wadi_crossings_osm": crossings,
        "speed_restrictions": rs,
        "restricted_km": round(sum(r["to_km"] - r["from_km"] for r in rs), 3),
        "min_curve_kmh": float(min([r["kmh"] for r in rs], default=kl.design_kmh)),
        "window_bound_legs": int(legs["window_bound"].sum()) if "window_bound" in legs else 0,
        "legs": legs.to_dict(orient="records"),
    }


def station_chainage(c: dict[str, Any], res: dict[str, Any]) -> dict[str, float]:
    df = res["profile"]
    out = {}
    legs = res["legs"]
    for _, lg in legs.iterrows():
        sub = df[df.leg == lg.leg]
        out.setdefault(
            lg["from"],
            round(float(sub.s_km.iloc[0]) if lg.leg == 0 else out.get(lg["from"], 0.0), 3),
        )
        out[lg["to"]] = round(float(sub.s_km.iloc[-1]), 3)
    if legs.shape[0]:
        out[legs.iloc[0]["from"]] = 0.0
    return out


def write_outputs(c: dict, res: dict, w: dict, out: Path, seed: int, root: Path) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    summ = summarise(c, res, w)
    summ["station_km"] = station_chainage(c, res)
    df = res["profile"]
    df.to_parquet(out / "profile.parquet", index=False)
    from shapely.geometry import LineString, mapping

    line = LineString(np.column_stack([df.lon, df.lat]))
    simp = line.simplify(0.0002, preserve_topology=False)
    sketch = [
        [s["lon"], s["lat"]] for s in sorted(c["stations"], key=lambda s: float(s["km_post"]))
    ]
    fc = {
        "type": "FeatureCollection",
        "name": c["id"],
        "attribution": "alignment derived from Copernicus GLO-30 (c) DLR/Airbus, ESA WorldCover 2021 "
        "(CC BY 4.0) and (c) OpenStreetMap contributors (ODbL)",
        "label": LABEL,
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "kind": "routed",
                    "id": c["id"],
                    "layer": "hypothetical",
                    "length_km": summ["length_km"],
                    "detour_ratio": summ["detour_ratio"],
                    "tunnel_km": summ["tunnel_km"],
                    "viaduct_km": summ["viaduct_km"],
                },
                "geometry": json.loads(json.dumps(mapping(simp))),
            },
            {
                "type": "Feature",
                "properties": {"kind": "straight_sketch", "id": c["id"], "layer": "hypothetical"},
                "geometry": {"type": "LineString", "coordinates": sketch},
            },
        ],
    }
    for f in fc["features"]:
        f["geometry"]["coordinates"] = [
            [round(x, 6), round(y, 6)] for x, y in f["geometry"]["coordinates"]
        ]
    (out / "alignment.geojson").write_text(
        json.dumps(fc, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (out / "summary.json").write_text(
        json.dumps(summ, indent=1, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    write_meta(
        out,
        seed,
        {"weights": w},
        extra={
            "label": LABEL,
            "corridor": c["id"],
            "weights_hash": weights_hash(w),
            "weights_frozen": bool(w.get("frozen")),
            "rail_layer_sha256": rail_layer_hashes(root),
            "tiles_index_sha256": ad.sha256(root / ad.TILES / "index.csv")
            if (root / ad.TILES / "index.csv").exists()
            else None,
        },
    )
    return summ


def _corridor_files(root: Path, folder: Path | None = None) -> list[Path]:
    base = root / CORRIDORS if folder is None else folder
    return sorted(p for p in base.rglob("*.yaml") if "station_addition" not in p.parts)


@app.command("route")
def route_cmd(
    corridor: Path = typer.Option(..., help="corridor YAML"),
    weights: Path = typer.Option(None, help="weights YAML (default align_weights.yaml)"),
    seed: int = seed_option(),
    out: Path = typer.Option(None),
    root: Path = typer.Option(REPO_ROOT, hidden=True),
) -> None:
    """Route one corridor (deterministic; the seed is recorded, no draw is used)."""
    w = load_weights(weights, root)
    c = yaml.safe_load((root / corridor).read_text(encoding="utf-8"))
    o = out or (root / RUNS / f"corridors-s{seed}" / c["id"])
    s = write_outputs(c, route_corridor(c, w, root), w, o, seed, root)
    typer.echo(
        f"{c['id']}: {s['length_km']:.1f} km, detour {s['detour_ratio']}, tunnel {s['tunnel_km']} km, viaduct {s['viaduct_km']} km"
    )


def _route_one(args: tuple[str, str, int, str, str, bool]) -> dict[str, Any]:
    path, wpath, seed, outdir, root_s, force = args
    root = Path(root_s)
    w = load_weights(Path(wpath), root)
    c = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    o = Path(outdir) / c["id"]
    if not force and (o / "summary.json").exists() and (o / "meta.json").exists():
        meta = json.loads((o / "meta.json").read_text())
        if meta.get("weights_hash") == weights_hash(w):
            return json.loads((o / "summary.json").read_text())
    try:
        return write_outputs(c, route_corridor(c, w, root), w, o, seed, root)
    except Exception as e:  # recorded, never silent
        return {"id": c["id"], "error": f"{type(e).__name__}: {e}"}


@app.command("route-all")
def route_all_cmd(
    weights: Path = typer.Option(None),
    seed: int = seed_option(),
    workers: int = typer.Option(3),
    only: str = typer.Option("", help="comma-separated corridor ids"),
    corridors_dir: Path = typer.Option(None, help="corridor YAML folder (default S2-S4)"),
    tag: str = typer.Option("corridors", help="run folder tag"),
    force: bool = typer.Option(False, help="re-route even if a run with the same weights exists"),
    root: Path = typer.Option(REPO_ROOT, hidden=True),
) -> None:
    """Route every S2-S4 corridor (station additions sit on existing track and are not routed)."""
    from concurrent.futures import ProcessPoolExecutor

    wpath = str(weights or (root / WEIGHTS))
    outdir = root / RUNS / f"{tag}-s{seed}"
    files = _corridor_files(root, corridors_dir)
    if only:
        keep = set(only.split(","))
        files = [p for p in files if p.stem in keep]
    jobs = [(str(p), wpath, seed, str(outdir), str(root), force) for p in files]
    res = []
    with ProcessPoolExecutor(workers) as ex:
        for r in ex.map(_route_one, jobs):
            res.append(r)
            typer.echo(
                f"{r['id']}: " + (r.get("error") or f"{r['length_km']:.1f} km x{r['detour_ratio']}")
            )
    outdir.mkdir(parents=True, exist_ok=True)
    rows = [
        {
            k: r.get(k)
            for k in (
                "id",
                "line_type",
                "length_km",
                "straight_km_legs",
                "detour_ratio",
                "tunnel_km",
                "viaduct_km",
                "earthworks_km",
                "restricted_km",
                "min_curve_kmh",
                "profile_feasible",
                "error",
            )
        }
        for r in res
    ]
    pd.DataFrame(rows).to_csv(outdir / "routed.csv", index=False)
    w = load_weights(Path(wpath), root)
    write_meta(
        outdir,
        seed,
        {"weights": w},
        extra={
            "label": LABEL,
            "weights_hash": weights_hash(w),
            "n": len(res),
            "errors": [r["id"] for r in res if "error" in r],
        },
    )


# --------------------------------------------------------------------------- validation
def line_as_corridor(lid: str, root: Path) -> dict[str, Any]:
    ld = yaml.safe_load((root / LINES / f"{lid}.yaml").read_text(encoding="utf-8"))
    st = [s for s in ld["stations"] if s.get("lat") is not None and s.get("lon") is not None]
    return {"id": f"validation-{lid}", "line_type": ld.get("line_type"), "stations": st}


def osm_line(lid: str, root: Path, main_only: bool = False):
    """The OSM line geometry with EVERY part (S6_L6_CONNECTED item 7, 6 Nov 2026): a
    MultiLineString (FIX_HHR_JEDDAH: part 0 = main line, then the branches) is returned whole, so
    `compare` measures against main + branch, the published convention (docs/alignments.md §4d).
    `main_only=True` returns part 0 (the diagnostics in network.align_diag clip one line)."""
    from shapely.geometry import shape

    d = json.loads((root / LINES / "geojson" / f"{lid}.geojson").read_text(encoding="utf-8"))
    g = shape(d["features"][0]["geometry"])
    if main_only and g.geom_type == "MultiLineString":
        g = g.geoms[0]
    return g, d["features"][0]["properties"]


def _proj(t: Any, geom: Any) -> Any:
    """Geometry through a pyproj Transformer (shapely 2 coordinate-array transform)."""
    import shapely

    return shapely.transform(geom, lambda xy: np.column_stack(t.transform(xy[:, 0], xy[:, 1])))


def osm_structures(lid: str, line, root: Path) -> dict[str, float]:
    """km of OSM rail ways tagged bridge=* / tunnel=* within 50 m of the line (ksa-rail extract)."""
    import subprocess
    import tempfile

    from shapely.geometry import shape

    pbf = root / "data/ksa/osm/ksa-rail.osm.pbf"
    out = {"bridge_km": 0.0, "tunnel_km": 0.0}
    if not pbf.exists():
        return out | {"note": "ksa-rail.osm.pbf missing"}
    with tempfile.TemporaryDirectory() as td:
        gj = Path(td) / "r.geojsonseq"
        subprocess.run(
            [
                "osmium",
                "export",
                "-f",
                "geojsonseq",
                "--geometry-types=linestring",
                "-o",
                str(gj),
                str(pbf),
            ],
            check=True,
            capture_output=True,
        )
        lat0, lon0 = line.centroid.y, line.centroid.x
        t = to_xy(np.zeros(1), np.zeros(1), lat0, lon0)

        lp = _proj(t, line).buffer(50)
        for f in ad._features(gj):
            p = f["properties"]
            if p.get("railway") not in ("rail", "construction") or not (
                p.get("bridge") or p.get("tunnel")
            ):
                continue
            g = _proj(t, shape(f["geometry"]))
            if not g.intersects(lp):
                continue
            km = g.intersection(lp).length / 1000
            if p.get("tunnel") and p.get("tunnel") != "no":
                out["tunnel_km"] += km
            elif p.get("bridge") and p.get("bridge") != "no":
                out["bridge_km"] += km
    return {k: round(v, 3) for k, v in out.items()}


def compare(
    routed: pd.DataFrame, osm, km_osm: float, ref_km: float | None = None
) -> dict[str, float]:
    """Routed vs OSM. Length reference = the line YAML's station km-post span (cumulative path along
    the OSM track between the first and last station, rail-data-scout method); offsets against the
    OSM geometry clipped between the projections of the end stations.

    Every part of a MultiLineString counts (S6_L6_CONNECTED item 7; the convention of
    `rail.hhr_check.compare_multi`): part 0 (the main line) is clipped as above, the other parts
    (branches) are added whole, the 2,000 OSM sample points are spread over the parts in proportion
    to their length, and every offset is to the nearest part. A LineString is compared as before."""
    from shapely.geometry import LineString, MultiLineString, Point

    lat0, lon0 = float(routed.lat.mean()), float(routed.lon.mean())
    t = to_xy(np.zeros(1), np.zeros(1), lat0, lon0)
    rl = LineString(np.column_stack(t.transform(routed.lon.to_numpy(), routed.lat.to_numpy())))
    parts = list(osm.geoms) if osm.geom_type == "MultiLineString" else [osm]
    ol, *branches = [_proj(t, p) for p in parts]
    # clip the OSM line to the stretch between the first and last routed points
    a = ol.project(Point(rl.coords[0]))
    b = ol.project(Point(rl.coords[-1]))
    from shapely.ops import substring

    ol = substring(ol, min(a, b), max(a, b))
    pr = (
        [Point(p) for p in rl.interpolate(np.linspace(0, rl.length, 2000)).geoms]
        if False
        else [rl.interpolate(d) for d in np.linspace(0, rl.length, 2000)]
    )
    if branches:
        ol = MultiLineString([ol, *branches])
        po = [
            part.interpolate(d)
            for part in ol.geoms
            for d in np.linspace(0, part.length, max(2, int(2000 * part.length / ol.length)))
        ]
    else:
        po = [ol.interpolate(d) for d in np.linspace(0, ol.length, 2000)]
    d_ro = np.array([ol.distance(p) for p in pr]) / 1000
    d_or = np.array([rl.distance(p) for p in po]) / 1000
    return {
        "routed_km": round(rl.length / 1000, 3),
        "osm_km_clipped": round(ol.length / 1000, 3),
        "osm_alignment_km": km_osm,
        "ref_km_station_span": ref_km,
        "length_error": round(rl.length / ((ref_km or ol.length / 1000) * 1000) - 1, 4),
        "hausdorff_km": round(float(max(d_ro.max(), d_or.max())), 3),
        "mean_offset_km": round(float(0.5 * (d_ro.mean() + d_or.mean())), 3),
        "mean_offset_routed_to_osm_km": round(float(d_ro.mean()), 3),
        "p90_offset_km": round(float(np.percentile(np.concatenate([d_ro, d_or]), 90)), 3),
    }


def validate_lines(
    w: dict[str, Any], root: Path, out: Path | None, seed: int, structures: bool = True
) -> pd.DataFrame:
    rows = []
    V = w["validation"]
    for lid, spec in V["lines"].items():
        c = line_as_corridor(lid, root)
        res = route_corridor(
            c, w, root, exclude=VALIDATION_EXCLUDE.get(lid, [lid]), line_type=spec["class"]
        )
        osm, props = osm_line(lid, root)
        kp = [float(s["km_post"]) for s in c["stations"]]
        m = compare(res["profile"], osm, props.get("alignment_km"), round(max(kp) - min(kp), 3))
        s = summarise(c, res, w)
        row = {
            "line": lid,
            "class": spec["class"],
            **m,
            "tunnel_share": s["tunnel_share"],
            "viaduct_share": s["viaduct_share"],
            "tunnel_km": s["tunnel_km"],
            "viaduct_km": s["viaduct_km"],
        }
        if structures:
            o = osm_structures(lid, osm, root)
            L = m["osm_km_clipped"]
            row |= {
                "osm_tunnel_km": o.get("tunnel_km"),
                "osm_bridge_km": o.get("bridge_km"),
                "osm_tunnel_share": round(o.get("tunnel_km", 0) / L, 5),
                "osm_bridge_share": round(o.get("bridge_km", 0) / L, 5),
            }
        row["length_ok"] = abs(m["length_error"]) <= float(_v(V["length_tolerance"]))
        row["offset_ok"] = m["mean_offset_km"] < float(_v(V["mean_offset_km"]))
        rows.append(row)
        if out is not None:
            write_outputs(c, res, w, out / lid, seed, root)
    df = pd.DataFrame(rows)
    if out is not None:
        out.mkdir(parents=True, exist_ok=True)
        df.to_csv(out / "validation.csv", index=False)
        write_meta(
            out, seed, {"weights": w}, extra={"label": LABEL, "weights_hash": weights_hash(w)}
        )
    return df


@app.command("validate")
def validate_cmd(
    weights: Path = typer.Option(None),
    seed: int = seed_option(),
    out: Path = typer.Option(None),
    root: Path = typer.Option(REPO_ROOT, hidden=True),
) -> None:
    """Route HHR, SAR North and SAR East with the same algorithm and compare with OSM."""
    w = load_weights(weights, root)
    df = validate_lines(w, root, out or (root / RUNS / f"validation-s{seed}"), seed)
    typer.echo(df.to_string(index=False))


def recompare(run: Path, w: dict[str, Any], root: Path) -> tuple[pd.DataFrame, float]:
    """Offsets of an EXISTING routed validation run against the current OSM geometry (every part):
    no routing, no structures; the A-align-070 objective with the other lines' rows recomputed the
    same way. A dry check (S6_L6_CONNECTED item 7)."""
    rows = []
    for lid, spec in w["validation"]["lines"].items():
        prof = pd.read_parquet(run / lid / "profile.parquet")
        c = line_as_corridor(lid, root)
        osm, props = osm_line(lid, root)
        kp = [float(s["km_post"]) for s in c["stations"]]
        m = compare(prof, osm, props.get("alignment_km"), round(max(kp) - min(kp), 3))
        rows.append(
            {
                "line": lid,
                "class": spec["class"],
                "osm_parts": len(getattr(osm, "geoms", [osm])),
                **m,
            }
        )
    df = pd.DataFrame(rows)
    return df, objective(df, w)


@app.command("recompare")
def recompare_cmd(
    run: Path = typer.Option(RUNS / "validation-s1"),
    weights: Path = typer.Option(None),
    root: Path = typer.Option(REPO_ROOT, hidden=True),
) -> None:
    """Print the offset statistics of an existing routed validation run (no routing, no output)."""
    df, obj = recompare(root / run, load_weights(weights, root), root)
    cols = [
        "line",
        "osm_parts",
        "osm_km_clipped",
        "mean_offset_km",
        "p90_offset_km",
        "hausdorff_km",
    ]
    typer.echo(df[cols].to_string(index=False))
    typer.echo(f"objective (A-align-070) {obj}")


def set_dotted(w: dict[str, Any], key: str, value: Any) -> dict[str, Any]:
    import copy

    out = copy.deepcopy(w)
    node = out
    *head, last = key.split(".")
    for k in head:
        node = node[k]
    if isinstance(node[last], dict):
        node[last] = {**node[last], "value": value}
    else:
        node[last] = value
    return out


def objective(df: pd.DataFrame, w: dict[str, Any]) -> float:
    tol = float(_v(w["validation"]["length_tolerance"]))
    pen = 20.0 * np.maximum(0.0, df.length_error.abs() - tol)
    return round(float(df.mean_offset_km.mean() + pen.sum()), 4)


def _eval(args: tuple[str, int, str]) -> dict[str, Any]:
    wjson, seed, root_s = args
    w = json.loads(wjson)
    df = validate_lines(w, Path(root_s), None, seed, structures=False)
    return {"objective": objective(df, w), "rows": df.to_dict(orient="records")}


@app.command("tune")
def tune_cmd(
    seed: int = seed_option(),
    workers: int = typer.Option(3),
    out: Path = typer.Option(None),
    root: Path = typer.Option(REPO_ROOT, hidden=True),
) -> None:
    """Coordinate descent over the tune grid on the three validation lines (A-align-070)."""
    from concurrent.futures import ProcessPoolExecutor

    w = load_weights(None, root)
    if w.get("frozen"):
        raise typer.BadParameter("weights are frozen; unfreeze explicitly before re-tuning")
    T = w["tune"]
    o = out or (root / RUNS / f"tune-s{seed}")
    o.mkdir(parents=True, exist_ok=True)
    log = []
    cur = w
    best = None
    keys: list[str] = []
    with ProcessPoolExecutor(workers) as ex:
        for pi, ps in enumerate(T["passes"]):
            for sweep in range(int(ps["sweeps"])):
                for key, values in ps["grid"].items():
                    keys.append(key)
                    cands = [set_dotted(cur, key, v) for v in values]
                    res = list(ex.map(_eval, [(json.dumps(c), seed, str(root)) for c in cands]))
                    for v, r in zip(values, res, strict=True):
                        log.append(
                            {
                                "pass": pi + 1,
                                "sweep": sweep,
                                "param": key,
                                "value": v,
                                "objective": r["objective"],
                                **{
                                    f"{x['line']}:{m}": x[m]
                                    for x in r["rows"]
                                    for m in ("length_error", "mean_offset_km", "hausdorff_km")
                                },
                            }
                        )
                        typer.echo(f"pass {pi + 1} sweep {sweep} {key}={v}: {r['objective']}")
                    k = int(np.argmin([r["objective"] for r in res]))
                    cur = cands[k]
                    best = (res[k]["objective"], key, values[k])
                    pd.DataFrame(log).to_csv(o / "tune.csv", index=False)
    chosen = {key: _v(eval_path(cur, key)) for key in dict.fromkeys(keys)}
    (o / "chosen.json").write_text(
        json.dumps({"objective": best[0] if best else None, "chosen": chosen}, indent=1) + "\n"
    )
    write_meta(o, seed, {"weights": w}, extra={"label": LABEL, "chosen": chosen})
    typer.echo(json.dumps(chosen))


def eval_path(w: dict[str, Any], key: str) -> Any:
    node = w
    for k in key.split("."):
        node = node[k]
    return node


def hillshade(
    z: np.ndarray, dy: float, dx: float, az: float = 315.0, alt: float = 45.0
) -> np.ndarray:
    gy, gx = np.gradient(np.where(np.isnan(z), 0.0, z), dy, dx)
    slope = np.arctan(np.hypot(gx, gy))
    aspect = np.arctan2(-gx, gy)
    a, b = np.radians(az), np.radians(alt)
    hs = np.sin(b) * np.cos(slope) + np.cos(b) * np.sin(slope) * np.cos(a - aspect)
    return np.where(np.isnan(z), np.nan, np.clip(hs, 0, 1))


def _draw_base(ax, bounds, step, root):
    g = read_grid(bounds, step, root)
    dy, dxr = cell_m(g)
    hs = hillshade(g.dem, dy, float(np.mean(dxr)))
    ext = (
        g.c0 * g.res,
        (g.c0 + g.dem.shape[1]) * g.res,
        90 - (g.r0 + g.dem.shape[0]) * g.res,
        90 - g.r0 * g.res,
    )
    # no data (sea, or beyond the tile set around the Kingdom) stays white
    ax.imshow(
        np.ma.masked_invalid(hs),
        cmap="Greys_r",
        extent=ext,
        vmin=-0.2,
        vmax=1.1,
        interpolation="bilinear",
    )
    k = _ksa(str(root))
    for part in getattr(k, "geoms", [k]):
        x, y = part.exterior.xy
        ax.plot(x, y, color="#555555", lw=0.6, ls=":", zorder=2)
    for geom in _rail_geoms(str(root)).values():
        for part in getattr(geom, "geoms", [geom]):
            x, y = part.xy
            ax.plot(x, y, color="black", lw=1.2, zorder=3)
    ax.set_xlim(bounds[0], bounds[2])
    ax.set_ylim(bounds[1], bounds[3])
    ax.set_aspect(1 / math.cos(math.radians(0.5 * (bounds[1] + bounds[3]))))


CREDIT = (
    "Hillshade: Copernicus GLO-30 (c) DLR e.V. 2010-2014, (c) Airbus DS 2014-2018, provided under COPERNICUS by "
    "the EU and ESA. Rail and layers (c) OpenStreetMap contributors (ODbL); ESA WorldCover 2021 (CC BY 4.0).\n"
    "Black = existing rail (OSM). Hypothetical alignments (ours): indicative engineering sketch, not a design. "
    "Synthetic demand, uncalibrated: scenario comparison, not a forecast."
)
FAM_COLOURS = {
    "trunk_gap": "#c0392b",
    "branch_spur": "#1f77b4",
    "commuter_belt": "#2ca02c",
    "alternative": "#9467bd",
}


@app.command("maps")
def maps_cmd(
    seed: int = seed_option(),
    root: Path = typer.Option(REPO_ROOT, hidden=True),
) -> None:
    """Routed alignments over a hillshade, straight sketches faint; validation lines vs OSM."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    out = root / RUNS / "maps"
    out.mkdir(parents=True, exist_ok=True)
    runs = root / RUNS / f"corridors-s{seed}"
    items = []
    for p in _corridor_files(root):
        c = yaml.safe_load(p.read_text(encoding="utf-8"))
        a = runs / c["id"] / "alignment.geojson"
        if a.exists():
            items.append((c["family"], json.loads(a.read_text(encoding="utf-8"))))
    alt = root / RUNS / f"alternatives-s{seed}"
    for a in sorted(alt.glob("*/alignment.geojson")) if alt.exists() else []:
        items.append(("alternative", json.loads(a.read_text(encoding="utf-8"))))
    nat = (34.4, 16.2, 55.8, 32.3)
    for name, fams in (
        ("national", None),
        ("S2-trunk", {"trunk_gap", "alternative"}),
        ("S3-spurs", {"branch_spur"}),
        ("S4-belts", {"commuter_belt"}),
    ):
        fig, ax = plt.subplots(figsize=(14, 12))
        _draw_base(ax, nat, 24, root)
        for fam, fc in items:
            if fams and fam not in fams:
                continue
            for f in fc["features"]:
                xy = np.asarray(f["geometry"]["coordinates"])
                if f["properties"]["kind"] == "straight_sketch":
                    ax.plot(
                        xy[:, 0],
                        xy[:, 1],
                        ls="--",
                        lw=0.7,
                        color=FAM_COLOURS[fam],
                        alpha=0.35,
                        zorder=4,
                    )
                else:
                    ax.plot(xy[:, 0], xy[:, 1], lw=1.6, color=FAM_COLOURS[fam], zorder=5)
        hand = (
            [
                Line2D([], [], color="black", lw=1.2, label="existing rail (OSM)"),
                Line2D(
                    [], [], color="#555555", lw=0.6, ls=":", label="Saudi Arabia boundary (OSM)"
                ),
            ]
            + [
                Line2D(
                    [],
                    [],
                    color=FAM_COLOURS[k],
                    lw=1.6,
                    label=f"hypothetical (ours): {k.replace('_', ' ')} routed",
                )
                for k in FAM_COLOURS
                if (not fams or k in fams)
            ]
            + [
                Line2D(
                    [],
                    [],
                    color="grey",
                    lw=0.7,
                    ls="--",
                    label="hypothetical (ours): straight sketch (before)",
                )
            ]
        )
        ax.legend(handles=hand, loc="upper right", fontsize=9)
        ax.set_title(f"Terrain-aware alignments, {name} (R4_ALIGN)")
        fig.text(0.01, 0.005, CREDIT, fontsize=7, va="bottom")
        fig.savefig(out / f"{name}.png", dpi=110, bbox_inches="tight")
        plt.close(fig)
        typer.echo(f"maps/{name}.png")
    val = root / RUNS / f"validation-s{seed}"
    for lid in load_weights(None, root)["validation"]["lines"]:
        pp = val / lid / "profile.parquet"
        if not pp.exists():
            continue
        df = pd.read_parquet(pp)
        osm, _ = osm_line(lid, root)
        w_, s_, e_, n_ = osm.bounds
        pad = 0.15
        fig, ax = plt.subplots(figsize=(11, 11))
        _draw_base(
            ax,
            (
                min(w_, df.lon.min()) - pad,
                min(s_, df.lat.min()) - pad,
                max(e_, df.lon.max()) + pad,
                max(n_, df.lat.max()) + pad,
            ),
            4,
            root,
        )
        ax.plot(
            df.lon,
            df.lat,
            color="#c0392b",
            lw=1.6,
            zorder=6,
            label="routed (same algorithm, frozen weights)",
        )
        for k, col in (("tunnel", "#8e44ad"), ("viaduct", "#2980b9")):
            t = df[df.structure == k]
            ax.plot(t.lon, t.lat, ".", ms=3, color=col, zorder=7, label=k)
        ax.legend(loc="upper right")
        ax.set_title(f"Validation: {lid} routed vs OSM (black)")
        fig.text(0.01, 0.005, CREDIT, fontsize=6, va="bottom")
        fig.savefig(out / f"validation-{lid}.png", dpi=110, bbox_inches="tight")
        plt.close(fig)
        typer.echo(f"maps/validation-{lid}.png")


BEFORE = Path("runs/r4a/before")


def _summaries(base: Path) -> pd.DataFrame:
    fr = [pd.read_parquet(p) for p in sorted(base.glob("S[2-5]/summary.parquet"))]
    return pd.concat(fr, ignore_index=True) if fr else pd.DataFrame()


@app.command("compare")
def compare_cmd(
    seed: int = seed_option(),
    out: Path = typer.Option(None),
    root: Path = typer.Option(REPO_ROOT, hidden=True),
) -> None:
    """Before (straight sketches, runs/r4a/before) vs after (routed) tables: per corridor km, minutes,
    capex/opex P10/P50/P90, reach, 30-minute towns and ranks; funnel town rank changes; the
    30-minute test pairs. Ranks: uplifted P50 capex (ascending) and uplifted P50 capex per person
    newly reached within 60 in-vehicle minutes (ascending; corridors reaching nobody rank last)."""
    o = out or (root / "runs/r4a" / f"compare-s{seed}")
    o.mkdir(parents=True, exist_ok=True)
    b = _summaries(root / BEFORE / "network-eval")
    a = _summaries(root / "runs/network-eval")
    keep = [
        "candidate",
        "family",
        "line_type",
        "km",
        "run_min_p10",
        "run_min_p50",
        "run_min_p90",
        "capex_p10",
        "capex_p50",
        "capex_p90",
        "capex_uplifted_p50",
        "capex_uplifted_p80",
        "opex_p50",
        "pop_in_vehicle_60_delta_vs_s1",
        "towns_within_30_ivt",
        "towns_within_30_new_vs_s1",
    ]
    for d in (a, b):
        costed = d.capex_uplifted_p50.notna()  # grade-infeasible corridors are not costed
        reach = d.pop_in_vehicle_60_delta_vs_s1.where(d.pop_in_vehicle_60_delta_vs_s1 > 0)
        d["sar_per_person_reached"] = d.capex_uplifted_p50 / reach
        d["rank_capex"] = d.capex_uplifted_p50.rank(method="min", na_option="keep").astype("Int64")
        spp = d.sar_per_person_reached.where(~(costed & reach.isna()), np.inf).where(costed)
        d["rank_cost_per_reach"] = spp.rank(method="min", na_option="keep").astype("Int64")
    keep += ["sar_per_person_reached", "rank_capex", "rank_cost_per_reach"]
    m = b[keep].merge(
        a[keep],
        on=["candidate", "family", "line_type"],
        how="outer",
        suffixes=("_before", "_after"),
        indicator=True,
    )
    m["status"] = (
        m["_merge"]
        .astype(str)
        .map(
            {
                "both": "in both",
                "left_only": "dropped after routing",
                "right_only": "new after routing",
            }
        )
    )
    m = m.drop(columns="_merge")
    m.loc[m.status.eq("in both") & m.capex_p50_after.isna(), "status"] = (
        "in both; not costed after routing (grade-infeasible, A-align-091)"
    )
    for k in ("rank_capex", "rank_cost_per_reach"):
        m[f"{k}_change"] = m[f"{k}_after"] - m[f"{k}_before"]
    for k in ("km", "run_min_p50", "capex_p50", "capex_uplifted_p50", "opex_p50"):
        m[f"{k}_change_pct"] = (m[f"{k}_after"] / m[f"{k}_before"] - 1) * 100
    routed = {}
    for p in sorted((root / SIDECARS).glob("*.json")):
        sc = json.loads(p.read_text(encoding="utf-8"))
        routed[sc["id"]] = {
            k: sc.get(k)
            for k in (
                "detour_ratio",
                "tunnel_km",
                "viaduct_km",
                "earthworks_km",
                "restricted_km",
                "min_curve_kmh",
                "straight_km_legs",
                "profile_feasible",
            )
        }
    m = m.merge(
        pd.DataFrame.from_dict(routed, orient="index").rename_axis("candidate").reset_index(),
        on="candidate",
        how="left",
    )
    m.to_csv(o / "corridors.csv", index=False)
    big = m[(m.rank_capex_change.abs() > 5) | (m.rank_cost_per_reach_change.abs() > 5)]
    big.to_csv(o / "corridor_rank_changes.csv", index=False)
    # funnel (towns)
    fb = pd.read_parquet(root / BEFORE / "funnel-minutes/score/scores.parquet")[
        ["row_key", "name_en", "region", "rank", "short_list"]
    ]
    fa = pd.read_parquet(root / "runs/r4/funnel-minutes/score/scores.parquet")[
        ["row_key", "name_en", "region", "rank", "short_list"]
    ]
    f = fb.merge(
        fa, on=["row_key", "name_en", "region"], how="outer", suffixes=("_before", "_after")
    )
    f["rank_change"] = f.rank_after - f.rank_before
    f.to_csv(o / "towns.csv", index=False)
    towns_big = f[f.rank_change.abs() > 5]
    towns_big.to_csv(o / "town_rank_changes.csv", index=False)
    # 30-minute test
    cb = pd.read_parquet(root / BEFORE / "commute-test-s1/commute_test.parquet")
    ca = pd.read_parquet(root / f"runs/access/commute-test-s{seed}/commute_test.parquet")
    k3 = ["scenario", "metro", "row_key", "town"]
    c = cb[k3 + ["ivt_min", "within_30_ivt"]].merge(
        ca[k3 + ["ivt_min", "within_30_ivt"]], on=k3, how="outer", suffixes=("_before", "_after")
    )
    c["flip"] = np.where(
        c.within_30_ivt_before.fillna(False).astype(bool)
        == c.within_30_ivt_after.fillna(False).astype(bool),
        "",
        np.where(c.within_30_ivt_after.fillna(False).astype(bool), "gained", "lost"),
    )
    c.to_csv(o / "commute30.csv", index=False)
    cand = c[~c.scenario.isin(["S0", "S1"])]
    totals = {
        "label": "synthetic demand, uncalibrated: scenario comparison, not a forecast",
        "corridors_before": int(len(b)),
        "corridors_after": int(len(a)),
        "dropped": m.loc[m.status == "dropped after routing", "candidate"].tolist(),
        "new": m.loc[m.status == "new after routing", "candidate"].tolist(),
        "not_costed_after": m.loc[m.capex_p50_after.isna(), "candidate"].tolist(),
        "capex_p50_sum_before_sar_bn": round(float(b.capex_p50.sum()) / 1e3, 1)
        if "capex_p50" in b
        else None,
        "capex_p50_sum_after_sar_bn": round(float(a.capex_p50.sum()) / 1e3, 1)
        if "capex_p50" in a
        else None,
        "pairs_within_30_ivt_before": int(
            cand.within_30_ivt_before.fillna(False).astype(bool).sum()
        ),
        "pairs_within_30_ivt_after": int(cand.within_30_ivt_after.fillna(False).astype(bool).sum()),
        "pairs_gained": int((cand.flip == "gained").sum()),
        "pairs_lost": int((cand.flip == "lost").sum()),
        "corridor_rank_changes_gt5": big.candidate.tolist(),
        "town_rank_changes_gt5": towns_big.name_en.tolist(),
    }
    (o / "totals.json").write_text(
        json.dumps(totals, indent=1, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    write_meta(o, seed, {"before": BEFORE.as_posix()}, extra=totals)
    typer.echo(json.dumps(totals, indent=1, ensure_ascii=False))


@app.command("reproduce")
def reproduce_cmd(
    n: int = typer.Option(10),
    seed: int = seed_option(),
    out: Path = typer.Option(Path("runs/verify-r4a/reproduce")),
    root: Path = typer.Option(REPO_ROOT, hidden=True),
) -> None:
    """Re-route n corridors drawn at random (rng seeded) from the frozen weights into `out` and
    byte-compare alignment.geojson, summary.json and profile.parquet with runs/align/corridors-s<seed>."""
    w = load_weights(None, root)
    if not w.get("frozen"):
        raise typer.BadParameter("weights are not frozen")
    files = _corridor_files(root)
    rng = np.random.default_rng(seed)
    pick = sorted(rng.choice(len(files), size=min(n, len(files)), replace=False).tolist())
    ref = root / RUNS / f"corridors-s{seed}"
    rows = []
    for i in pick:
        c = yaml.safe_load(files[i].read_text(encoding="utf-8"))
        o = (root / out) / c["id"]
        write_outputs(c, route_corridor(c, w, root), w, o, seed, root)
        same = {
            f: (o / f).read_bytes() == (ref / c["id"] / f).read_bytes()
            for f in ("alignment.geojson", "summary.json", "profile.parquet")
        }
        rows.append({"id": c["id"], **same, "identical": all(same.values())})
        typer.echo(f"{c['id']}: {'identical' if all(same.values()) else same}")
    df = pd.DataFrame(rows)
    df.to_csv((root / out) / "reproduce.csv", index=False)
    typer.echo(
        f"{int(df.identical.sum())}/{len(df)} byte-identical; weights {weights_hash(w)[:12]}"
    )
    if not df.identical.all():
        raise typer.Exit(1)


@app.command("freeze")
def freeze_cmd(root: Path = typer.Option(REPO_ROOT, hidden=True)) -> None:
    """Set `frozen: true` in align_weights.yaml and write its hash (align_weights.sha256)."""
    p = root / WEIGHTS
    text = p.read_text(encoding="utf-8")
    if "\nfrozen: false\n" in text:
        text = text.replace("\nfrozen: false\n", "\nfrozen: true\n")
        p.write_text(text, encoding="utf-8")
    w = load_weights(None, root)
    if not w.get("frozen"):
        raise typer.BadParameter("could not set frozen: true")
    h = weights_hash(w)
    p.with_suffix(".sha256").write_text(
        f"{h}  {WEIGHTS.as_posix()} (canonical JSON of the parsed YAML)\n"
    )
    typer.echo(h)


def write_sidecar(c: dict[str, Any], r: Path, dest: Path, root: Path) -> dict[str, Any]:
    """Write cities/ksa/alignments/[sub/]<id>.json + .geojson from one route run folder `r`."""
    from screening.corridors import stations_key

    sm = json.loads((r / "summary.json").read_text(encoding="utf-8"))
    meta = json.loads((r / "meta.json").read_text(encoding="utf-8"))
    gj = (dest / f"{c['id']}.geojson").relative_to(root).as_posix()
    sm |= {
        "status": "routed",
        "stations_key": stations_key(c["stations"]),
        "geojson": gj,
        "run": r.relative_to(root).as_posix(),
        "weights_hash": meta["weights_hash"],
        "weights_frozen": meta.get("weights_frozen"),
    }
    sm.pop("legs", None)
    (dest / f"{c['id']}.json").write_text(
        json.dumps(sm, indent=1, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (dest / f"{c['id']}.geojson").write_bytes((r / "alignment.geojson").read_bytes())
    return sm


@app.command("apply")
def apply_cmd(
    seed: int = seed_option(),
    corridors_dir: Path = typer.Option(None),
    tag: str = typer.Option("corridors"),
    sub: str = typer.Option("", help="subfolder under cities/ksa/alignments (alternatives)"),
    root: Path = typer.Option(REPO_ROOT, hidden=True),
) -> None:
    """Sidecars for the corridor generator: cities/ksa/alignments/[sub/]<id>.json + .geojson."""
    runs = root / RUNS / f"{tag}-s{seed}"
    dest = root / SIDECARS / sub if sub else root / SIDECARS
    dest.mkdir(parents=True, exist_ok=True)
    rows = []
    for p in _corridor_files(root, corridors_dir):
        c = yaml.safe_load(p.read_text(encoding="utf-8"))
        r = runs / c["id"]
        if not (r / "summary.json").exists():
            typer.echo(f"{c['id']}: no run")
            continue
        sm = write_sidecar(c, r, dest, root)
        rows.append(
            {
                k: sm.get(k)
                for k in (
                    "id",
                    "line_type",
                    "length_km",
                    "straight_km_legs",
                    "detour_ratio",
                    "tunnel_km",
                    "viaduct_km",
                    "earthworks_km",
                    "restricted_km",
                    "min_curve_kmh",
                    "profile_feasible",
                )
            }
        )
    pd.DataFrame(rows).to_csv(dest / "summary.csv", index=False)
    typer.echo(f"{len(rows)} sidecars in {dest.relative_to(root)}")


if __name__ == "__main__":
    app()
