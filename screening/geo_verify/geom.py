"""Metric CRS choice (UTM by longitude, skill section 3) and WGS84 geodesic distances."""

from __future__ import annotations

from pyproj import CRS, Geod, Transformer
from shapely.geometry.base import BaseGeometry
from shapely.ops import transform

GEOD = Geod(ellps="WGS84")


def utm_zone(lon: float) -> int:
    """UTM zone number by longitude, EPSG definition: floor((lon + 180) / 6) + 1 (1..60).

    Zone n spans [6n - 186, 6n - 180) degrees E; a point on a boundary belongs to the zone
    east of it. The Norway/Svalbard exceptions lie far outside Saudi Arabia and are not modelled.
    """
    if not -180.0 <= lon <= 180.0:
        raise ValueError(f"longitude out of range: {lon}")
    return min(int((lon + 180.0) // 6) + 1, 60)


def utm_epsg(lon: float) -> int:
    """WGS84 / UTM north EPSG code 326<zone> (skill section 3): 32636 west of 36 E, 32637 for
    36-42 E, 32638 for 42-48 E, 32639 for 48-54 E, 32640 for 54-60 E. Saudi Arabia lies wholly
    north of the equator, so the north zones apply."""
    return 32600 + utm_zone(lon)


def geodesic_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """WGS84 geodesic distance in km (pyproj Geod.inv)."""
    _, _, d = GEOD.inv(lon1, lat1, lon2, lat2)
    return float(d) / 1000.0


def to_metric(geom: BaseGeometry, lon: float | None = None) -> tuple[BaseGeometry, int]:
    """Project a lon/lat geometry to its UTM zone; returns (geometry, epsg)."""
    epsg = utm_epsg(geom.centroid.x if lon is None else lon)
    tr = Transformer.from_crs(CRS.from_epsg(4326), CRS.from_epsg(epsg), always_xy=True)
    return transform(tr.transform, geom), epsg


def lonlat_to_metric(lons, lats, epsg: int):
    """Vectorised lon/lat -> metric x, y for a given EPSG."""
    tr = Transformer.from_crs(CRS.from_epsg(4326), CRS.from_epsg(epsg), always_xy=True)
    return tr.transform(lons, lats)


def point_polygon_km(lat: float, lon: float, polygon: BaseGeometry) -> tuple[bool, float]:
    """(inside, km to the polygon boundary) in the point's UTM zone."""
    from shapely.geometry import Point

    poly_m, epsg = to_metric(polygon, lon)
    x, y = lonlat_to_metric([lon], [lat], epsg)
    pt = Point(x[0], y[0])
    return bool(poly_m.contains(pt)), float(poly_m.boundary.distance(pt) / 1000.0)
