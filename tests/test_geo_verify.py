"""GEO_VERIFY package on small fixtures: geometry, extents, estimators, method log."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from shapely.geometry import Polygon, box

from screening.geo_verify import estimators, extents, footprints, geom, imagery, method_log

FIX = Path(__file__).parent / "fixtures" / "geo_verify"


def test_utm_zone_by_longitude():
    assert geom.utm_epsg(35.9) == 32636
    assert geom.utm_epsg(39.2) == 32637
    assert geom.utm_epsg(46.7) == 32638


def test_geodesic_one_degree_latitude():
    assert geom.geodesic_km(21.0, 39.0, 22.0, 39.0) == pytest.approx(110.7, abs=0.3)


def test_point_polygon_inside_and_outside():
    sq = box(39.0, 21.0, 39.2, 21.2)
    inside, km = geom.point_polygon_km(21.1, 39.1, sq)
    assert inside and km == pytest.approx(10.4, abs=0.3)
    outside, km2 = geom.point_polygon_km(21.1, 39.3, sq)
    assert not outside and km2 == pytest.approx(10.4, abs=0.3)


def _synthetic_settlement(seed: int = 1):
    """A 30 x 30 grid of buildings at 40 m spacing plus a far-away hamlet of 10."""
    rng = np.random.default_rng(seed)
    town = np.array([(i * 40.0, j * 40.0) for i in range(30) for j in range(30)])
    hamlet = rng.uniform(0, 50, size=(10, 2)) + 5000.0
    return np.vstack([town, hamlet])


def test_dbscan_separates_town_and_hamlet():
    xy = _synthetic_settlement()
    lab = extents.dbscan(xy, eps=100.0, min_samples=5)
    assert len(set(lab[:900])) == 1 and lab[0] >= 0
    assert lab[900] != lab[0] and lab[900] >= 0
    idx = extents.clusters_near(xy, lab, (600.0, 600.0), snap_m=500.0)
    assert len(idx) == 900


def test_dbscan_noise():
    xy = np.array([[0.0, 0.0], [1000.0, 0.0], [2000.0, 0.0]])
    assert (extents.dbscan(xy, 100.0, 2) == -1).all()


def test_morph_close_fills_gap():
    m = np.zeros((7, 7), dtype=bool)
    m[3, 1:3] = m[3, 4:6] = True
    assert not m[3, 3]
    assert extents.morph_close(m, 3)[3, 3]


def test_persons_per_building():
    p = estimators.Params(100, 5, 1500, 3, 20, 4.8, 1.0, 0.8, 25)
    assert p.persons_per_building == pytest.approx(3.84)
    assert estimators.buildings_estimate(100, p) == pytest.approx(384.0)


def test_extent_mask_and_grid_sum():
    pytest.importorskip("rasterio")
    from rasterio.transform import from_origin

    tr = from_origin(39.0, 21.01, 0.001, 0.001)  # 10 x 10 cells
    arr = np.ones((10, 10), dtype="float32") * 5
    cl = pd.DataFrame({"lon": [39.0025, 39.0045], "lat": [21.0055, 21.0055]})
    mask = estimators.extent_mask(cl, tr, arr.shape, kernel=3)
    assert mask[4, 2] and mask[4, 4] and mask[4, 3]  # the gap between two cells is closed
    assert estimators.grid_sum(arr, mask) == pytest.approx(5.0 * mask.sum())


def test_band_and_backtest_table():
    bt = pd.read_csv(FIX / "backtest_table.csv")
    ape = [estimators.abs_pct_error(g, c) for g, c in zip(bt.grid, bt.census_2022, strict=True)]
    assert np.median(ape) == pytest.approx(0.1)
    lo, mid, hi = estimators.band([900.0, 1200.0], [0.1, 0.5])
    assert mid == pytest.approx(np.sqrt(900 * 1200))
    assert lo == pytest.approx(600.0) and hi == pytest.approx(1800.0)
    lo2, mid2, hi2 = estimators.band([0.0, 0.0], [0.1, 0.1])
    assert np.isnan(mid2)


def test_quadkey_known_tile():
    # Wadi ad-Dawasir lies in level-9 tile 122311131 (dataset-links.csv, 2026-02-03 release)
    assert footprints.quadkey(20.4602516, 44.799553) == "122311131"


def test_method_log_append_and_ids(tmp_path):
    p = tmp_path / "log.jsonl"
    eid = method_log.entry_id("stn", "fixture:jeddah")
    assert eid == method_log.entry_id("stn", "fixture:jeddah") and eid.startswith("geo-stn-")
    st = json.loads((FIX / "station.geojson").read_text())["features"][0]
    method_log.append(
        p,
        {
            "id": eid,
            "method": "fixture",
            "inputs": [],
            "parameters": [],
            "value": st["geometry"]["coordinates"],
            "band": None,
            "run_id": "test",
        },
    )
    assert method_log.read(p)[0]["value"] == [39.245363, 21.517643]
    with pytest.raises(ValueError):
        method_log.append(p, {"id": "x"})


def test_disk_and_cache_gates(tmp_path):
    (tmp_path / "f.bin").write_bytes(b"0" * 1024)
    assert imagery.cache_bytes(tmp_path) == 1024
    with pytest.raises(imagery.DiskGateError):
        imagery.ensure_cache(1e-9, root=tmp_path)
    with pytest.raises(imagery.DiskGateError):
        imagery.ensure_disk(1e9)


def test_to_metric_area():
    poly, epsg = geom.to_metric(Polygon([(39, 21), (39.01, 21), (39.01, 21.01), (39, 21.01)]))
    assert epsg == 32637 and poly.area == pytest.approx(1.16e6, rel=0.02)
