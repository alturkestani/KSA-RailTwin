# ruff: noqa: E501
"""Data preparation for terrain-aware alignments (R4_ALIGN): per 1-degree tile rasters at 3 arc-seconds.

Every tile is on the Copernicus GLO-30 tile grid (lat/lon of its south-west corner), resampled to
3 arc-seconds (1,200 x 1,200 px, about 90 m; A-align-001). Three rasters per tile, cached under
data/ksa/align/tiles/ (gitignored; index.csv hashed in the manifest):

- dem/<tile>.tif: Copernicus DEM GLO-30 Public (DSM), average-resampled from the COG overview by
  GDAL (remote /vsicurl/ range reads, no account). Tiles absent from the bucket are sea (A-geo-022
  convention: the router treats them as impassable, not as zero height).
- wc/<tile>.tif: ESA WorldCover 10 m 2021 v200 class, mode-resampled to the same grid (CC BY 4.0).
- flags/<tile>.tif: uint16 bit flags rasterised from the OpenStreetMap layers extracted by
  network/align_osm.sh (ODbL), see FLAGS.

Tiles: every GLO-30 tile that intersects the OSM Saudi Arabia boundary (relation 307584) buffered by
`tile_buffer_deg` (A-align-002).

  uv run python -m network.align_data tiles
  uv run python -m network.align_data dem --workers 8
  uv run python -m network.align_data worldcover --workers 4
  uv run python -m network.align_data flags
  uv run python -m network.align_data index    # index.csv + index-{dem,wc,flags}.csv (manifest)

Produced using Copernicus WorldDEM-30 (c) DLR e.V. 2010-2014 and (c) Airbus Defence and Space GmbH
2014-2018 provided under COPERNICUS by the European Union and ESA; all rights reserved.
ESA WorldCover 2021 v200 (c) ESA WorldCover project / contains modified Copernicus Sentinel data
(2021) processed by ESA WorldCover consortium, CC BY 4.0. Map data (c) OpenStreetMap contributors.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

import numpy as np
import typer
import yaml

from common import REPO_ROOT

CFG = Path("cities/ksa/assumptions/align_weights.yaml")
TILES = Path("data/ksa/align/tiles")
OSM = Path("data/ksa/align/osm")
ADMIN = Path("data/ksa/osm/gcc-admin-areas.geojsonseq")
KSA_RELATION = 307584
PX = 1200  # 3 arc-seconds per 1-degree tile
RES = 1.0 / PX
GDAL_ENV = {
    "GDAL_DISABLE_READDIR_ON_OPEN": "EMPTY_DIR",
    "CPL_VSIL_CURL_ALLOWED_EXTENSIONS": ".tif",
    "GDAL_HTTP_MAX_RETRY": "5",
    "GDAL_HTTP_RETRY_DELAY": "2",
    "VSI_CACHE": "TRUE",
}
DEM_URL = (
    "https://copernicus-dem-30m.s3.amazonaws.com/Copernicus_DSM_COG_10_{t}_DEM/"
    "Copernicus_DSM_COG_10_{t}_DEM.tif"
)
WC_URL = (
    "https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/"
    "ESA_WorldCover_10m_2021_v200_{t}_Map.tif"
)
# bit flags in flags/<tile>.tif
FLAGS = {
    "urban": 1,  # OSM landuse=residential|commercial|retail|industrial
    "builtup": 2,  # WorldCover class 50 (set from wc/ at read time, not stored here)
    "protected": 4,  # OSM boundary=protected_area|national_park, leisure=nature_reserve
    "military": 8,  # OSM landuse=military or military=*
    "sand": 16,  # OSM natural=sand|dune
    "sabkha": 32,  # OSM natural=wetland with wetland in sabkha|saltmarsh|tidalflat|mud|salt_pond|None
    "water": 64,  # OSM natural=water (inland); WorldCover 80 is added at read time
    "waterway": 128,  # OSM waterway=river|stream|wadi|canal|drain|ditch (lines, all touched)
    "highway": 256,  # OSM highway=motorway|trunk|primary (+ links) (lines, all touched)
}
SABKHA_WETLAND = {"sabkha", "saltmarsh", "tidalflat", "mud", "salt_pond", None}

app = typer.Typer(add_completion=False, help=__doc__, no_args_is_help=True)


@app.callback()
def _group() -> None:
    """Alignment data preparation (R4_ALIGN)."""


def load_cfg(root: Path = REPO_ROOT) -> dict[str, Any]:
    return yaml.safe_load((root / CFG).read_text(encoding="utf-8"))


def _v(x: Any) -> Any:
    return x["value"] if isinstance(x, dict) and "value" in x else x


def tile_id(lat_i: int, lon_i: int) -> str:
    ns, ew = ("N" if lat_i >= 0 else "S"), ("E" if lon_i >= 0 else "W")
    return f"{ns}{abs(lat_i):02d}_00_{ew}{abs(lon_i):03d}_00"


def tile_ll(t: str) -> tuple[int, int]:
    a, _, b, _ = t.split("_")
    lat = int(a[1:]) * (1 if a[0] == "N" else -1)
    lon = int(b[1:]) * (1 if b[0] == "E" else -1)
    return lat, lon


def _features(path: Path):
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip().strip("\x1e")
            if line:
                yield json.loads(line)


def ksa_shape(root: Path = REPO_ROOT):
    from shapely.geometry import shape

    for f in _features(root / ADMIN):
        if f["properties"].get("@id") == KSA_RELATION or (
            f["properties"].get("ISO3166-1") == "SA"
            and str(f["properties"].get("admin_level")) == "2"
        ):
            return shape(f["geometry"])
    raise RuntimeError("Saudi Arabia boundary not found in the admin extract")


def tile_list(root: Path = REPO_ROOT) -> list[str]:
    path = root / TILES / "tiles.txt"
    if path.exists():
        return path.read_text().split()
    raise FileNotFoundError("run `network.align_data tiles` first")


@app.command("tiles")
def tiles_cmd(root: Path = typer.Option(REPO_ROOT, hidden=True)) -> None:
    """The tile list (tiles.txt): GLO-30 tiles touching the buffered KSA boundary."""
    from shapely.geometry import box

    buf = float(_v(load_cfg(root)["data"]["tile_buffer_deg"]))
    ksa = ksa_shape(root).buffer(buf)
    w, s, e, n = ksa.bounds
    out = [
        tile_id(la, lo)
        for la in range(math.floor(s), math.ceil(n))
        for lo in range(math.floor(w), math.ceil(e))
        if ksa.intersects(box(lo, la, lo + 1, la + 1))
    ]
    (root / TILES).mkdir(parents=True, exist_ok=True)
    (root / TILES / "tiles.txt").write_text("\n".join(out) + "\n")
    typer.echo(f"{len(out)} tiles")


def _write(path: Path, arr: np.ndarray, lat_i: int, lon_i: int, dtype: str, nodata=None) -> None:
    import rasterio
    from rasterio.crs import CRS
    from rasterio.transform import from_origin

    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp.tif")
    prof = {
        "driver": "GTiff",
        "width": PX,
        "height": PX,
        "count": 1,
        "dtype": dtype,
        "crs": CRS.from_epsg(4326),
        "transform": from_origin(lon_i, lat_i + 1, RES, RES),
        "compress": "deflate",
        "tiled": True,
        "blockxsize": 256,
        "blockysize": 256,
    }
    if dtype == "float32":
        prof["predictor"] = 3
    if nodata is not None:
        prof["nodata"] = nodata
    with rasterio.open(tmp, "w", **prof) as dst:
        dst.write(arr.astype(dtype), 1)
    tmp.rename(path)


def _exists(url: str) -> bool:
    import urllib.error
    import urllib.request

    for attempt in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, method="HEAD"), timeout=30):
                return True
        except urllib.error.HTTPError as e:
            if e.code in (403, 404):
                return False
            if attempt == 3:
                raise
        except OSError:
            if attempt == 3:
                raise
    return False


def fetch_dem(t: str, root: Path) -> str:
    import rasterio
    from rasterio.enums import Resampling
    from rasterio.windows import from_bounds

    path = root / TILES / "dem" / f"{t}.tif"
    sea = root / TILES / "dem" / f"{t}.sea"
    if path.exists() or sea.exists():
        return "cached"
    url = DEM_URL.format(t=t)
    if not _exists(url):
        sea.parent.mkdir(parents=True, exist_ok=True)
        sea.write_text("no GLO-30 tile in the bucket (sea)\n")
        return "sea"
    lat_i, lon_i = tile_ll(t)
    with rasterio.Env(**GDAL_ENV), rasterio.open("/vsicurl/" + url) as src:
        # GLO-30 pixel centres sit on whole arc-seconds; read the exact 1-degree box
        win = from_bounds(lon_i, lat_i, lon_i + 1, lat_i + 1, src.transform)
        arr = src.read(
            1, window=win, out_shape=(PX, PX), resampling=Resampling.average, boundless=True
        )
    _write(path, arr, lat_i, lon_i, "float32")
    return "fetched"


@app.command("dem")
def dem_cmd(
    workers: int = typer.Option(8), root: Path = typer.Option(REPO_ROOT, hidden=True)
) -> None:
    """Fetch every DEM tile at 3 arc-seconds (cached)."""
    ts = tile_list(root)
    with ThreadPoolExecutor(workers) as ex:
        for t, r in zip(ts, ex.map(lambda t: fetch_dem(t, root), ts), strict=True):
            typer.echo(f"{t} {r}")


def fetch_wc(t3: str, root: Path) -> str:
    """One 3-degree WorldCover tile, mode-resampled to 3 arc-seconds and split into 1-degree tiles."""
    import rasterio
    from rasterio.enums import Resampling
    from rasterio.windows import from_bounds

    lat3, lon3 = tile_ll(t3)
    want = [
        tile_id(lat3 + i, lon3 + j)
        for i in range(3)
        for j in range(3)
        if tile_id(lat3 + i, lon3 + j) in set(tile_list(root))
    ]
    todo = [w for w in want if not (root / TILES / "wc" / f"{w}.tif").exists()]
    if not todo:
        return "cached"
    ns, ew = ("N" if lat3 >= 0 else "S"), ("E" if lon3 >= 0 else "W")
    url = WC_URL.format(t=f"{ns}{abs(lat3):02d}{ew}{abs(lon3):03d}")
    if not _exists(url):
        for w in todo:
            _write(root / TILES / "wc" / f"{w}.tif", np.zeros((PX, PX)), *tile_ll(w), "uint8", 0)
        return "absent (no WorldCover tile: written as class 0)"
    with rasterio.Env(**GDAL_ENV), rasterio.open("/vsicurl/" + url) as src:
        for w in todo:
            la, lo = tile_ll(w)
            win = from_bounds(lo, la, lo + 1, la + 1, src.transform)
            arr = src.read(
                1, window=win, out_shape=(PX, PX), resampling=Resampling.mode, boundless=True
            )
            _write(root / TILES / "wc" / f"{w}.tif", arr, la, lo, "uint8", 0)
    return f"fetched {len(todo)}"


@app.command("worldcover")
def wc_cmd(
    workers: int = typer.Option(4), root: Path = typer.Option(REPO_ROOT, hidden=True)
) -> None:
    """Fetch WorldCover at 3 arc-seconds for every tile (cached)."""
    t3 = sorted(
        {
            tile_id(3 * math.floor(la / 3), 3 * math.floor(lo / 3))
            for la, lo in map(tile_ll, tile_list(root))
        }
    )
    with ThreadPoolExecutor(workers) as ex:
        for t, r in zip(t3, ex.map(lambda t: fetch_wc(t, root), t3), strict=True):
            typer.echo(f"{t} {r}")


def _osm_layers(root: Path) -> dict[str, list]:
    """Shapely geometries per flag from the OSM extracts (tag tests repeated: osmium's relation
    filter also passes member ways with other tags)."""
    from shapely.geometry import shape

    out: dict[str, list] = {k: [] for k in FLAGS}

    def add(k: str, f: dict) -> None:
        try:
            g = shape(f["geometry"])
        except (ValueError, TypeError, KeyError):
            return
        if not g.is_empty:
            out[k].append(g if g.is_valid else g.buffer(0))

    for f in _features(root / OSM / "landuse-urban.geojsonseq"):
        if f["properties"].get("landuse") in ("residential", "commercial", "retail", "industrial"):
            add("urban", f)
    for f in _features(root / OSM / "protected.geojsonseq"):
        p = f["properties"]
        if p.get("boundary") in ("protected_area", "national_park") or (
            p.get("leisure") == "nature_reserve"
        ):
            add("protected", f)
    for f in _features(root / OSM / "military.geojsonseq"):
        p = f["properties"]
        if (p.get("landuse") == "military" or p.get("military")) and f["geometry"]["type"] in (
            "Polygon",
            "MultiPolygon",
        ):
            add("military", f)
    for f in _features(root / OSM / "natural.geojsonseq"):
        p = f["properties"]
        if f["geometry"]["type"] not in ("Polygon", "MultiPolygon"):
            continue
        if p.get("natural") in ("sand", "dune"):
            add("sand", f)
        elif p.get("natural") == "wetland" and p.get("wetland") in SABKHA_WETLAND:
            add("sabkha", f)
        elif p.get("natural") == "water":
            add("water", f)
    for f in _features(root / OSM / "waterways.geojsonseq"):
        if f["geometry"]["type"] in ("LineString", "MultiLineString"):
            add("waterway", f)
    for f in _features(root / OSM / "highways.geojsonseq"):
        if f["geometry"]["type"] in ("LineString", "MultiLineString"):
            add("highway", f)
    return out


@app.command("flags")
def flags_cmd(root: Path = typer.Option(REPO_ROOT, hidden=True)) -> None:
    """Rasterise the OSM layers into flags/<tile>.tif (uint16 bit flags)."""
    from rasterio.features import rasterize
    from rasterio.transform import from_origin
    from shapely.geometry import box
    from shapely.strtree import STRtree

    layers = _osm_layers(root)
    trees = {k: (STRtree(v), v) for k, v in layers.items() if v}
    typer.echo({k: len(v) for k, v in layers.items()})
    for t in tile_list(root):
        path = root / TILES / "flags" / f"{t}.tif"
        if path.exists():
            continue
        la, lo = tile_ll(t)
        tr = from_origin(lo, la + 1, RES, RES)
        bb = box(lo, la, lo + 1, la + 1)
        arr = np.zeros((PX, PX), np.uint16)
        for k, (tree, geoms) in trees.items():
            idx = tree.query(bb)
            if len(idx) == 0:
                continue
            gs = [geoms[i].intersection(bb) for i in idx]
            gs = [g for g in gs if not g.is_empty]
            if not gs:
                continue
            m = rasterize(
                [(g, 1) for g in gs],
                out_shape=(PX, PX),
                transform=tr,
                all_touched=k in ("waterway", "highway"),
                dtype="uint8",
            )
            arr |= (m.astype(np.uint16) * FLAGS[k]).astype(np.uint16)
        _write(path, arr, la, lo, "uint16")
        typer.echo(f"{t} flags")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


@app.command("index")
def index_cmd(root: Path = typer.Option(REPO_ROOT, hidden=True)) -> None:
    """index.csv: one row per cached tile raster with its SHA-256 (the manifest hashes this file)."""
    rows = []
    for kind in ("dem", "wc", "flags"):
        for p in sorted((root / TILES / kind).glob("*")):
            if p.suffix in (".tif", ".sea"):
                rows.append(
                    {
                        "kind": kind,
                        "tile": p.stem,
                        "file": p.relative_to(root).as_posix(),
                        "bytes": p.stat().st_size,
                        "sha256": sha256(p),
                    }
                )
    for name, sel in (("index.csv", rows),) + tuple(
        (f"index-{k}.csv", [r for r in rows if r["kind"] == k]) for k in ("dem", "wc", "flags")
    ):
        with (root / TILES / name).open("w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(sel)
    total = sum(r["bytes"] for r in rows)
    typer.echo(f"{len(rows)} files, {total / 1e6:.1f} MB")


if __name__ == "__main__":
    app()
