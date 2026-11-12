"""Two independent population estimators over a built-up settlement extent (skill section 2c).

1. `grid`: WorldPop 2020 100 m constrained UN-adjusted counts summed over the extent mask.
2. `buildings`: building-footprint count in the extent x persons per building, where persons per
   building = household size (Census 2022, relayed) x dwellings per building x residential share
   (A-geo assumptions).
The extent is the DBSCAN cluster(s) of footprint centroids touching the settlement point,
rasterised on the WorldPop grid and morphologically closed.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from screening.geo_verify import extents, geom


@dataclass(frozen=True)
class Params:
    eps_m: float  # A-geo-001
    min_samples: int  # A-geo-002
    snap_m: float  # A-geo-003
    close_kernel: int  # A-geo-004
    min_area_m2: float  # A-geo-005
    hh_size: float  # A-geo-006
    dwellings_per_building: float  # A-geo-007
    residential_share: float  # A-geo-008
    window_km: float  # A-geo-009 (search window half-width around the point)

    @property
    def persons_per_building(self) -> float:
        return self.hh_size * self.dwellings_per_building * self.residential_share


def extent_buildings(b: pd.DataFrame, lat: float, lon: float, p: Params) -> pd.DataFrame:
    """Footprints of the settlement cluster(s) touching the point (may be empty)."""
    b = b[b.area_m2 >= p.min_area_m2]
    if b.empty:
        return b
    epsg = geom.utm_epsg(lon)
    x, y = geom.lonlat_to_metric(b.lon.to_numpy(), b.lat.to_numpy(), epsg)
    xy = np.column_stack([x, y])
    px, py = geom.lonlat_to_metric([lon], [lat], epsg)
    labels = extents.dbscan(xy, p.eps_m, p.min_samples)
    idx = extents.clusters_near(xy, labels, (px[0], py[0]), p.snap_m)
    return b.iloc[idx]


def extent_mask(cluster: pd.DataFrame, transform, shape, kernel: int) -> np.ndarray:
    """Grid cells holding at least one cluster footprint centroid, closed with `kernel`."""
    inv = ~transform
    cols, rows = inv * (cluster.lon.to_numpy(), cluster.lat.to_numpy())
    cols, rows = np.floor(cols).astype(int), np.floor(rows).astype(int)
    ok = (rows >= 0) & (rows < shape[0]) & (cols >= 0) & (cols < shape[1])
    m = np.zeros(shape, dtype=bool)
    m[rows[ok], cols[ok]] = True
    return extents.morph_close(m, kernel)


def grid_sum(arr: np.ndarray, mask: np.ndarray) -> float:
    return float(np.nansum(np.where(mask, arr, 0.0)))


def buildings_estimate(n_buildings: int, p: Params) -> float:
    return float(n_buildings * p.persons_per_building)


def band(values: list[float], errors: list[float | None]) -> tuple[float, float, float]:
    """Central = geometric mean of the methods; range = min-max widened by each method's
    back-test median absolute % error (skill section 2c)."""
    vals = [v for v in values if v and v > 0]
    if not vals:
        return (float("nan"),) * 3
    lows = [v * (1 - (e or 0.0)) for v, e in zip(values, errors, strict=True) if v and v > 0]
    highs = [v * (1 + (e or 0.0)) for v, e in zip(values, errors, strict=True) if v and v > 0]
    central = float(np.exp(np.mean(np.log(vals))))
    return max(min(lows), 0.0), central, max(highs)


def abs_pct_error(est: float, ref: float) -> float:
    return abs(est - ref) / ref
