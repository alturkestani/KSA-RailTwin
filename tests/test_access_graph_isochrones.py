"""R4 rail graph, isochrones and the 30-minute test on the fixture corridor and 6 fixture zones."""

from __future__ import annotations

import json
import math

import numpy as np
import pandas as pd
import yaml

from access import commute_test as ct
from access import isochrones as iso
from access import railgraph
from common import REPO_ROOT

FIXTURE = REPO_ROOT / "tests/fixtures/corridor.yaml"
ZONES = REPO_ROOT / "tests/fixtures/zones.geojson"
S5 = (
    REPO_ROOT
    / "cities/ksa/corridors/station_addition"
    / "S5-station_addition-al-jubayl-royal-commission.yaml"
)
FAC = {"per_line": {}, "generic": {"value": 1.0, "range": [1.0, 1.0]}}


def _svc(line: dict, headway: float | None = None) -> railgraph.Service:
    cfg = railgraph.load_cfg(REPO_ROOT)
    sup = yaml.safe_load((REPO_ROOT / railgraph.SUPPLY).read_text(encoding="utf-8"))
    s = railgraph.build_service(line, cfg, sup, FAC, {}, REPO_ROOT)
    if headway is not None:
        s.headway_min = headway
    return s


def _ctx() -> iso.Context:
    line = yaml.safe_load(FIXTURE.read_text(encoding="utf-8"))
    cfg = railgraph.load_cfg(REPO_ROOT)
    svcs = [_svc(line, 30.0)]
    g_min = railgraph.build_graph(svcs, [line], cfg, "minutes")
    g_ivt = railgraph.build_graph(svcs, [line], cfg, "ivt")
    pop = {
        f["properties"]["zone_id"]: f["properties"]["population"]
        for f in json.loads(ZONES.read_text(encoding="utf-8"))["features"]
    }
    zones = pd.DataFrame({"zone_id": list(pop), "population": list(pop.values())})
    zones["jobs_proxy"] = zones.population / 2
    zones["metro"] = np.where(zones.zone_id == "FZ1", "Fixture", None)
    uid = line["id"] + ":"
    # FZ1 at fx-a, FZ2 at fx-b, FZ3 at fx-c (5 road-min); FZ4-FZ6 far from every station
    rows = []
    for z, near in (
        ("FZ1", "fx-a"),
        ("FZ2", "fx-b"),
        ("FZ3", "fx-c"),
        ("FZ4", None),
        ("FZ5", None),
        ("FZ6", None),
    ):
        for st in ("fx-a", "fx-b", "fx-c"):
            t = 5.0 if st == near else 200.0
            rows.append(
                {"zone_id": z, "uid": uid + st, "line_id": line["id"], "to_min": t, "from_min": t}
            )
    zst = pd.DataFrame(rows)
    road = pd.DataFrame([{"o": "FZ1", "d": z, "min": 10.0 * i} for i, z in enumerate(pop)])
    return iso.Context("fixture", svcs, g_min, g_ivt, zst, 10.0, 90.0, 1.0, zones, road)


def test_generalised_path_prefers_frequent_service() -> None:
    line = yaml.safe_load(FIXTURE.read_text(encoding="utf-8"))
    fast = {**line, "id": "fast-rare"}
    slow = {**line, "id": "slow-frequent"}
    cfg = railgraph.load_cfg(REPO_ROOT)
    s_fast, s_slow = _svc(fast, 240.0), _svc(slow, 30.0)
    s_slow.ivt = s_slow.ivt * 1.2  # 20 % slower but every 30 min instead of every 240
    g = railgraph.build_graph([s_fast, s_slow], [fast, slow], cfg, "generalised")
    uid = list(g.nodes.uid)
    a_slow, c_slow = uid.index("slow-frequent:fx-a"), uid.index("slow-frequent:fx-c")
    a_fast, c_fast = uid.index("fast-rare:fx-a"), uid.index("fast-rare:fx-c")
    assert g.gen[a_slow, c_slow] < g.gen[a_fast, c_fast]  # the wait is part of the path choice


def test_paths_must_ride() -> None:
    line = yaml.safe_load(FIXTURE.read_text(encoding="utf-8"))
    cfg = railgraph.load_cfg(REPO_ROOT)
    a, b = {**line, "id": "line-a"}, {**line, "id": "line-b"}  # co-located stations (walk links)
    g = railgraph.build_graph([_svc(a), _svc(b)], [a, b], cfg, "generalised")
    uid = list(g.nodes.uid)
    i, j = uid.index("line-a:fx-a"), uid.index("line-b:fx-a")
    t = railgraph.trace(g, i, j)
    assert not t or t["boardings"] >= 1  # never a walk-only "rail" trip
    assert math.isinf(g.gen[i, i])


def test_isochrone_population_counts() -> None:
    ctx = _ctx()
    m = {"name": "Fixture", "tier": 1}
    tab, zz = iso.reached(ctx, m, "FZ1")
    ivt = zz.set_index("zone_id").ivt_min
    assert ivt["FZ1"] == 0.0 and ivt["FZ2"] < ivt["FZ3"]
    assert math.isnan(ivt["FZ4"])
    for b in iso.BANDS:
        hit = zz[zz.ivt_min <= b]
        row = tab[(tab["mode"] == "in_vehicle") & (tab.band_min == b)].iloc[0]
        assert row.population == hit.population.sum()
        assert row.population_outside_metro == hit[hit.zone_id != "FZ1"].population.sum()
    d = tab[tab["mode"] == "door_to_door"].sort_values("band_min").population.to_numpy()
    assert (np.diff(d) >= 0).all()  # bands are nested


def test_commute_test_shape_and_times() -> None:
    ctx = _ctx()
    ivt, d2d, st = ct.rail_times(ctx, "FZ3", "FZ1", 30.0)
    assert st.endswith("fx-c") and 0 < ivt < d2d
    assert all(math.isnan(x) for x in ct.rail_times(ctx, "FZ4", "FZ1", 30.0)[:2])
    for col in (
        "metro",
        "town",
        "ivt_min",
        "ivt_min_low",
        "ivt_min_high",
        "d2d_min",
        "within_30_ivt",
        "car_trip_change_pct",
        "car_trip_change_pct_lo",
        "car_trip_change_pct_hi",
    ):
        assert col in ct.COLUMNS


def test_station_addition_costing_input_and_insertion() -> None:
    from network.evaluate import costing_input

    c = yaml.safe_load(S5.read_text(encoding="utf-8"))
    spec, costing = costing_input(c, REPO_ROOT)
    classes = [s["class"] for s in spec["stations"]]
    assert classes.count("intermediate") == 1  # only the new station is costed as a station
    assert abs(sum(v["value"] for v in costing["costing"]["terrain_shares"].values()) - 1) < 1e-6
    cfg = railgraph.load_cfg(REPO_ROOT)
    lines = railgraph.scenario_lines(
        "S1",
        cfg,
        REPO_ROOT,
        S5,
    )
    host = next(ld for ld in lines if ld.get("candidate"))
    assert "al-jubayl-royal-commission" in [s["id"] for s in host["stations"]]
