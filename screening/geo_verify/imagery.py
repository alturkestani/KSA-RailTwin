"""Streaming raster access with a disk gate (skill section 5).

- `free_gib` / `ensure_disk`: stop when free space on the home volume drops below the gate.
- `cache_bytes` / `ensure_cache`: the geo cache `data/ksa/geo/` stays under its cap.
- `read_window`: rasterio windowed read of a (local or HTTPS COG) raster over a lon/lat bbox.
- `stac_sentinel2`: newest low-cloud Sentinel-2 L2A scenes over a bbox (Earth Search STAC,
  AWS open data); only the scene id, date and asset URL are returned. No crops are committed:
  confirmation windows are written under the gitignored cache only.
rasterio is imported lazily (run with `uv run --with rasterio ...` until it is in pyproject).
"""

from __future__ import annotations

import shutil
from pathlib import Path

import numpy as np

from common import REPO_ROOT

GEO_CACHE = REPO_ROOT / "data" / "ksa" / "geo"
STAC_URL = "https://earth-search.aws.element84.com/v1/search"


class DiskGateError(RuntimeError):
    pass


def free_gib(path: Path | None = None) -> float:
    return shutil.disk_usage(path or Path.home()).free / 2**30


def ensure_disk(min_free_gib: float, path: Path | None = None) -> float:
    f = free_gib(path)
    if f < min_free_gib:
        raise DiskGateError(f"free disk {f:.1f} GiB below the {min_free_gib} GiB gate")
    return f


def cache_bytes(root: Path = GEO_CACHE) -> int:
    if not root.exists():
        return 0
    return sum(p.stat().st_size for p in root.rglob("*") if p.is_file())


def ensure_cache(max_gib: float, incoming_bytes: int = 0, root: Path = GEO_CACHE) -> int:
    used = cache_bytes(root)
    if used + incoming_bytes > max_gib * 2**30:
        raise DiskGateError(f"geo cache {used / 2**30:.2f} GiB + incoming exceeds {max_gib} GiB")
    return used


def read_window(src_path: str, bbox: tuple[float, float, float, float]):
    """(array float32 with NaN nodata, affine transform, crs) for bbox = (W, S, E, N) lon/lat."""
    import rasterio
    from rasterio.windows import from_bounds

    with rasterio.open(src_path) as src:
        win = from_bounds(*bbox, transform=src.transform).round_offsets().round_lengths()
        arr = src.read(1, window=win, boundless=True, fill_value=0).astype("float32")
        if src.nodata is not None:
            arr[arr == src.nodata] = np.nan
        arr[arr < 0] = np.nan
        return arr, src.window_transform(win), src.crs


def stac_sentinel2(bbox, start: str, end: str, max_cloud: float = 5.0, limit: int = 3):
    """Newest Sentinel-2 L2A scenes over bbox: list of dicts (id, datetime, cloud, visual)."""
    import json

    import httpx

    q = {
        "collections": ["sentinel-2-l2a"],
        "bbox": list(bbox),
        "datetime": f"{start}T00:00:00Z/{end}T23:59:59Z",
        "query": {"eo:cloud_cover": {"lt": max_cloud}},
        "sortby": [{"field": "properties.datetime", "direction": "desc"}],
        "limit": limit,
    }
    r = httpx.post(
        STAC_URL, content=json.dumps(q), timeout=60, headers={"Content-Type": "application/json"}
    )
    r.raise_for_status()
    return [
        {
            "id": f["id"],
            "datetime": f["properties"]["datetime"],
            "cloud": f["properties"].get("eo:cloud_cover"),
            "visual": f["assets"]["visual"]["href"],
        }
        for f in r.json()["features"]
    ]


def s2_window_png(href: str, lat: float, lon: float, half_m: float, out: Path) -> dict:
    """Read the TCI window around a point from the COG and write a PNG under the cache."""
    import rasterio
    from PIL import Image
    from pyproj import Transformer
    from rasterio.windows import from_bounds

    with rasterio.open(href) as src:
        tr = Transformer.from_crs("EPSG:4326", src.crs, always_xy=True)
        x, y = tr.transform(lon, lat)
        win = from_bounds(x - half_m, y - half_m, x + half_m, y + half_m, transform=src.transform)
        arr = src.read([1, 2, 3], window=win.round_offsets().round_lengths(), boundless=True)
    out.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(np.moveaxis(arr, 0, -1).astype("uint8")).resize(
        (arr.shape[2] * 2, arr.shape[1] * 2), Image.NEAREST
    ).save(out)
    return {"png": str(out.relative_to(REPO_ROOT)), "px": list(arr.shape[1:]), "half_m": half_m}
