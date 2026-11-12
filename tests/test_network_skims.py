"""Road graph, skims and OSRM helpers on the invented fixtures (no Jeddah or GCC PBF needed)."""

import json
import shutil

import numpy as np
import pandas as pd
import pytest
from pyproj import Geod
from scipy.sparse import csr_matrix

from network import osrm
from network.roadgraph import (
    build_from_opl_lines,
    build_graph,
    load_speed_config,
    parse_maxspeed,
    parse_opl_way,
    way_directions,
)
from network.skims import long_skims, path_km, run_skims

CFG = load_speed_config()
GEOD = Geod(ellps="WGS84")


def _m(lon1, lat1, lon2, lat2) -> float:
    return GEOD.inv(lon1, lat1, lon2, lat2)[2]


def test_parse_opl_way_tags_and_locations() -> None:
    line = (
        "w9 Thighway=primary,name=Fixture%20%Road,oneway=yes Nn1x40.05y22.05,n2x40.15y22.05,n3x y"
    )
    wid, tags, nodes = parse_opl_way(line)
    assert wid == 9 and tags["name"] == "Fixture Road" and tags["oneway"] == "yes"
    assert nodes == [(1, 40.05, 22.05), (2, 40.15, 22.05)]  # n3 has no location -> skipped
    assert parse_opl_way("n1 x40 y22") is None


def test_maxspeed_and_oneway_rules() -> None:
    assert parse_maxspeed("80") == 80 and parse_maxspeed("50 mph") == pytest.approx(80.4672)
    assert parse_maxspeed("none") is None and parse_maxspeed(None) is None
    assert way_directions({"highway": "primary", "oneway": "-1"}, CFG) == (False, True)
    assert way_directions({"highway": "motorway"}, CFG) == (True, False)  # implied
    assert way_directions({"highway": "motorway", "oneway": "no"}, CFG) == (True, True)
    assert way_directions({"highway": "tertiary", "junction": "roundabout"}, CFG) == (True, False)


def test_build_from_opl_speeds_and_lengths() -> None:
    lines = [
        "w1 Thighway=primary Nn1x40.05y22.05,n2x40.15y22.05",
        "w2 Thighway=primary,maxspeed=100,oneway=yes Nn2x40.15y22.05,n3x40.25y22.05",
        "w3 Thighway=service,service=parking_aisle Nn3x40.25y22.05,n4x40.3y22.05",
    ]
    g = build_from_opl_lines(lines, CFG)
    assert g.n_nodes == 3 and g.n_edges == 3  # w1 both ways, w2 forward only, w3 excluded
    seg = _m(40.05, 22.05, 40.15, 22.05)
    i = int(np.flatnonzero(g.way_id == 1)[0])
    assert g.length_m[i] == pytest.approx(seg)
    assert g.time_s[i] == pytest.approx(seg / (CFG["default_speed_kmh"]["primary"]["value"] / 3.6))
    j = int(np.flatnonzero(g.way_id == 2)[0])
    f = CFG["maxspeed_factor"]["value"]
    assert g.time_s[j] == pytest.approx(g.length_m[j] / (100 * f / 3.6))
    nxg = g.to_networkx()
    assert nxg.number_of_edges() == 3 and nxg.graph["path"] == "osmium+networkx"


def test_path_km_and_unreachable() -> None:
    m = csr_matrix(([100.0, 200.0], ([0, 1], [1, 2])), shape=(4, 4))
    pred = np.array([-9999, 0, 1, -9999])

    def look(r, c):
        return np.asarray(m[r, c]).ravel()

    out = path_km(pred, 0, np.array([0, 1, 2, 3]), look)
    assert out[:3].tolist() == [0.0, 100.0, 300.0] and np.isnan(out[3])


def test_long_skims_nan_never_zero() -> None:
    dur = np.array([[0.0, 600.0], [np.nan, 0.0]])
    dist = np.array([[0.0, 10_000.0], [np.nan, 0.0]])
    sk = long_skims(["A", "B"], dur, dist, np.array([0.1, 3.0]), 2.0)
    ba = sk[(sk.o == "B") & (sk.d == "A")].iloc[0]
    assert np.isnan(ba["min"]) and not ba["reachable"]
    ab = sk[(sk.o == "A") & (sk.d == "B")].iloc[0]
    assert ab["min"] == 10.0 and ab["km"] == 10.0 and ab["d_snap_flag"] and not ab["o_snap_flag"]


def test_skims_on_fixture_roads(fixtures, tmp_path) -> None:
    out = tmp_path / "sk"
    extra = run_skims("osmnx", fixtures / "roads_fixture.osm", fixtures / "zones.geojson", out, 1)
    sk = pd.read_parquet(out / "skims.parquet")
    zs = pd.read_parquet(out / "zones_snapped.parquet")
    meta = json.loads((out / "meta.json").read_text())
    assert len(sk) == 36 and extra["n_unreachable"] == 0
    assert meta["seed"] == 1 and meta["backend"] == "osmnx" and meta["path"] == "osmium+networkx"
    assert meta["n_nodes"] == 8 and meta["n_nodes_largest_scc"] == 6
    assert (zs["snap_km"] < 0.1).all() and not zs["snap_flag"].any()  # island nodes never used
    # FZ1 -> FZ4 uses the oneway secondary; FZ4 -> FZ1 must go round (trunk 2-5 is private)
    sec = CFG["default_speed_kmh"]["secondary"]["value"]
    d14 = _m(40.05, 22.05, 40.05, 22.15)
    r14 = sk[(sk.o == "FZ1") & (sk.d == "FZ4")].iloc[0]
    assert r14["km"] == pytest.approx(d14 / 1000, rel=1e-6)
    assert r14["min"] == pytest.approx(d14 / (sec / 3.6) / 60, rel=1e-6)
    r41 = sk[(sk.o == "FZ4") & (sk.d == "FZ1")].iloc[0]
    assert r41["km"] > 3 * r14["km"]


def test_far_zones_are_flagged(fixtures, tmp_path) -> None:
    extra = run_skims(
        "osmnx",
        fixtures / "roads_fixture.osm",
        fixtures / "zones_jeddah_fixture.geojson",
        tmp_path / "far",
        1,
    )
    assert extra["n_snap_flagged"] == 6 and extra["max_snap_km"] > 50


def test_osrm_estimate_affine() -> None:
    sc = {
        "points": [
            {"pbf_mb": 1, "wall_s": 3, "peak_rss_mb": 110, "output_mb": 20},
            {"pbf_mb": 3, "wall_s": 7, "peak_rss_mb": 130, "output_mb": 60},
        ],
        "slope_margin": {"value": 1.0},
    }
    est = osrm.estimate(int(10e6), sc)  # a + b*10 with a=1, b=2 for time
    assert est["minutes"] == pytest.approx(21 / 60, abs=0.01)
    assert est["disk_gib"] == pytest.approx(200 / 1073.741824, abs=0.01)
    assert osrm.pbf_stem(osrm.Path("x/gcc-states-latest.osm.pbf")) == "gcc-states-latest"


@pytest.mark.skipif(shutil.which("osrm-extract") is None, reason="osrm-backend not installed")
def test_osrm_backend_on_fixture(fixtures, tmp_path) -> None:
    root = tmp_path / "osrm"
    out = tmp_path / "so"
    run_skims(
        "osrm", fixtures / "roads_fixture.osm", fixtures / "zones.geojson", out, 1, osrm_root=root
    )
    sk = pd.read_parquet(out / "skims.parquet")
    r14 = sk[(sk.o == "FZ1") & (sk.d == "FZ4")].iloc[0]
    assert r14["km"] == pytest.approx(_m(40.05, 22.05, 40.05, 22.15) / 1000, rel=0.02)
    assert (
        json.loads((root / "roads_fixture" / "prep_stats.json").read_text())["algorithm"] == "mld"
    )


def test_build_graph_reads_xml(fixtures) -> None:
    g = build_graph(fixtures / "roads_fixture.osm")
    assert g.stats["ways_read"] == 6 and g.stats["ways_kept"] == 5
