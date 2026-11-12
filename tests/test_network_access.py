"""Nearest-target distance fields on invented points (no PBF beyond the road fixture)."""

import json
import math

import numpy as np
import pandas as pd
import pytest

from network.access import METHOD_GC, nearest_targets
from network.geo import KNearest, haversine_km
from network.roadgraph import build_graph

# Hand computation (haversine, R = 6371.0088 km) of (22.0 N, 40.0 E) -> (22.4 N, 40.3 E):
# dphi = 0.4 deg, dlambda = 0.3 deg, a = sin^2(dphi/2) + cos(22.0) cos(22.4) sin^2(dlambda/2)
# = 1.2183e-5 + 0.92718 * 0.92452 * 6.8538e-6 = 1.8058e-5 -> d = 2 R asin(sqrt(a)) = 54.150 km
HAND_KM = 54.150


def test_haversine_matches_hand_value() -> None:
    assert float(haversine_km(22.0, 40.0, 22.4, 40.3)) == pytest.approx(HAND_KM, abs=0.001)


def test_kdtree_equals_brute_force() -> None:
    rng = np.random.default_rng(1)
    tl, tn = rng.uniform(16, 33, 200), rng.uniform(34, 56, 200)
    pl, pn = rng.uniform(16, 33, 50), rng.uniform(34, 56, 50)
    km, idx = KNearest(tl, tn).query(pl, pn, k=1)
    brute = haversine_km(pl[:, None], pn[:, None], tl[None, :], tn[None, :])
    assert (idx[:, 0] == brute.argmin(axis=1)).all()
    assert np.allclose(km[:, 0], brute.min(axis=1), atol=1e-6)


def _targets() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "id": ["fx-a", "fx-b", "fx-c"],
            "lat": [22.0, 22.4, 22.9],
            "lon": [40.0, 40.3, 40.7],
            "layer": ["hypothetical"] * 3,
        }
    )


def test_great_circle_nearest() -> None:
    pts = pd.DataFrame({"id": ["p1", "p2"], "lat": [22.4, 22.85], "lon": [40.3, 40.7]})
    res = nearest_targets(pts, _targets(), backend="great_circle", k=2)
    assert res["target_id"].tolist() == ["fx-b", "fx-c"]
    assert res.loc[0, "gc_km"] == pytest.approx(0.0, abs=1e-9)
    assert res.loc[1, "gc_km"] == pytest.approx(float(haversine_km(22.85, 40.7, 22.9, 40.7)))
    assert (res["method"] == METHOD_GC).all() and res["road_min"].isna().all()
    assert not res["road_reachable"].any()


def test_k_is_capped_by_target_count() -> None:
    pts = pd.DataFrame({"id": ["p"], "lat": [22.0], "lon": [40.0]})
    res = nearest_targets(pts, _targets(), backend="great_circle", k=10)
    assert res.loc[0, "k"] == 3


def test_graph_backend_road_time_wins(fixtures) -> None:
    g = build_graph(fixtures / "roads_fixture.osm")
    # point at node 4 (22.15, 40.05). Great-circle nearest target is node 1 (11 km south), but
    # 1 can only be reached by going round (oneway 1->4); node 5 (10.3 km east) is faster.
    pts = pd.DataFrame({"id": ["p4"], "lat": [22.15], "lon": [40.05]})
    tg = pd.DataFrame(
        {
            "id": ["t1", "t5"],
            "lat": [22.05, 22.15],
            "lon": [40.05, 40.15],
            "layer": ["existing"] * 2,
        }
    )
    res = nearest_targets(pts, tg, backend="graph", graph=g, k=2)
    row = res.iloc[0]
    assert row["gc_target_id"] == "t5"  # 10.3 km < 11.1 km at this latitude
    assert row["target_id"] == "t5" and row["road_reachable"]
    assert row["method"] == "nx_dijkstra_roads_fixture"
    f = 0.8  # maxspeed_factor in road_speeds.yaml (A-r1a-025); w2 has maxspeed=100
    assert row["road_min"] == pytest.approx(row["road_km"] / (100 * f) * 60, rel=1e-6)
    res1 = nearest_targets(pts, tg.iloc[:1], backend="graph", graph=g, k=1)
    assert res1.loc[0, "road_km"] > 3 * res1.loc[0, "gc_km"]  # the long way round
    assert not math.isnan(res1.loc[0, "road_min"])


def test_cli_writes_meta(fixtures, tmp_path) -> None:
    from typer.testing import CliRunner

    from network.access import app

    pts = tmp_path / "p.parquet"
    tg = tmp_path / "t.parquet"
    pd.DataFrame({"id": ["p1"], "lat": [22.4], "lon": [40.3]}).to_parquet(pts)
    _targets().to_parquet(tg)
    out = tmp_path / "o" / "near.parquet"
    r = CliRunner().invoke(app, ["--points", str(pts), "--targets", str(tg), "--out", str(out)])
    assert r.exit_code == 0, r.output
    meta = json.loads((tmp_path / "o" / "near.meta" / "meta.json").read_text())
    assert meta["method"] == METHOD_GC and meta["n_points"] == 1
