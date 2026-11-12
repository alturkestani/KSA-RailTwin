"""Microsoft Global ML Building Footprints (CDLA-Permissive-2.0) by level-9 quadkey.

The country index `dataset-links.csv` maps quadkeys to gzipped GeoJSON-lines files. Each tile is
downloaded once (after the disk and cache gates) and kept raw under `data/ksa/geo/msbuildings/raw/`
(registered in the manifest with its SHA-256); a centroid lon/lat + area (m2) parquet is cached
beside it.
"""

from __future__ import annotations

import gzip
import hashlib
import io
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

from screening.geo_verify import imagery

INDEX_URL = "https://minedbuildings.z5.web.core.windows.net/global-buildings/dataset-links.csv"
LOCATION = "KingdomofSaudiArabia"


def quadkey(lat: float, lon: float, level: int = 9) -> str:
    """Bing Maps tile quadkey for a point."""
    lat = max(min(lat, 85.05112878), -85.05112878)
    n = 2**level
    x = int((lon + 180.0) / 360.0 * n)
    s = math.sin(math.radians(lat))
    y = int((0.5 - math.log((1 + s) / (1 - s)) / (4 * math.pi)) * n)
    x, y = min(max(x, 0), n - 1), min(max(y, 0), n - 1)
    digits = []
    for i in range(level, 0, -1):
        mask = 1 << (i - 1)
        digits.append(str((1 if x & mask else 0) + (2 if y & mask else 0)))
    return "".join(digits)


def quadkeys_bbox(bbox, level: int = 9) -> list[str]:
    w, s, e, n = bbox
    out = set()
    for lat in np.linspace(s, n, 6):
        for lon in np.linspace(w, e, 6):
            out.add(quadkey(float(lat), float(lon), level))
    return sorted(out)


def load_index(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, dtype={"QuadKey": str})
    return df[df.Location == LOCATION].set_index("QuadKey")


def _parse(raw: bytes) -> pd.DataFrame:
    lons, lats, areas = [], [], []
    for line in io.TextIOWrapper(gzip.GzipFile(fileobj=io.BytesIO(raw)), encoding="utf-8"):
        if not line.strip():
            continue
        g = json.loads(line)
        ring = np.asarray(g["geometry"]["coordinates"][0], dtype=float)
        lon0, lat0 = ring[:, 0].mean(), ring[:, 1].mean()
        kx = 111_320.0 * math.cos(math.radians(lat0))
        x, y = (ring[:, 0] - lon0) * kx, (ring[:, 1] - lat0) * 110_574.0
        areas.append(0.5 * abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1))))
        lons.append(lon0)
        lats.append(lat0)
    return pd.DataFrame({"lon": lons, "lat": lats, "area_m2": areas})


def tile(qk: str, index: pd.DataFrame, cache: Path, max_cache_gib: float, min_free_gib: float):
    """Centroid table for a quadkey (empty if the tile has no Saudi file) and a log record."""
    out = cache / f"qk={qk}.parquet"
    if out.exists():
        return pd.read_parquet(out), None
    if qk not in index.index:
        return pd.DataFrame({"lon": [], "lat": [], "area_m2": []}), None
    imagery.ensure_disk(min_free_gib)
    imagery.ensure_cache(max_cache_gib)
    import httpx

    urls = index.loc[[qk], "Url"].tolist()
    parts, recs = [], []
    rawdir = cache / "raw"
    rawdir.mkdir(parents=True, exist_ok=True)
    for i, url in enumerate(urls):
        raw = httpx.get(url, timeout=300, follow_redirects=True).content
        rp = rawdir / f"qk={qk}-{i}.csv.gz"
        rp.write_bytes(raw)
        recs.append(
            {
                "url": url,
                "bytes": len(raw),
                "sha256": hashlib.sha256(raw).hexdigest(),
                "path": str(rp),
            }
        )
        parts.append(_parse(raw))
    rec = {"quadkey": qk, "files": recs}
    df = pd.concat(parts, ignore_index=True)
    cache.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out, index=False)
    return df, rec
