"""CP2_PREP item 3 (P3a): the UTM zone follows the EPSG definition floor((lon + 180) / 6) + 1."""

from __future__ import annotations

import pytest
from pyproj.aoi import AreaOfInterest
from pyproj.database import query_utm_crs_info
from shapely.geometry import Point

from screening.geo_verify import geom

BOUNDARIES = [
    (35.999, 32636),
    (36.0, 32637),
    (36.001, 32637),
    (41.999, 32637),
    (42.0, 32638),
    (42.001, 32638),
    (47.999, 32638),
    (48.0, 32639),
    (48.001, 32639),
]

# One point per zone 36-40 (lon, lat): Haql area, Jeddah, Riyadh, Dammam, Rub' al Khali east.
ZONE_POINTS = [
    (35.5, 28.0, 32636),
    (39.2, 21.5, 32637),
    (46.7, 24.7, 32638),
    (50.1, 26.4, 32639),
    (55.0, 22.5, 32640),
]


@pytest.mark.parametrize(("lon", "epsg"), BOUNDARIES)
def test_zone_boundaries(lon: float, epsg: int) -> None:
    assert geom.utm_epsg(lon) == epsg


@pytest.mark.parametrize(("lon", "lat", "epsg"), ZONE_POINTS)
def test_one_point_per_zone(lon: float, lat: float, epsg: int) -> None:
    assert geom.utm_epsg(lon) == epsg
    assert geom.to_metric(Point(lon, lat))[1] == epsg


@pytest.mark.parametrize(("lon", "lat", "epsg"), ZONE_POINTS[1:4])
def test_matches_pyproj_query_utm_crs_info(lon: float, lat: float, epsg: int) -> None:
    hits = query_utm_crs_info(
        datum_name="WGS 84", area_of_interest=AreaOfInterest(lon, lat, lon, lat)
    )
    codes = {int(h.code) for h in hits if h.auth_name == "EPSG"}
    assert codes == {epsg}


def test_zone_formula_range() -> None:
    assert geom.utm_zone(-180.0) == 1
    assert geom.utm_zone(179.999) == 60
    assert geom.utm_zone(180.0) == 60
    with pytest.raises(ValueError):
        geom.utm_zone(181.0)
