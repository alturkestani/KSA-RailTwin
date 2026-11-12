"""FIX_HHR_REROUTE: the corridor-bonus band uses every part of a MultiLineString (HHR main + KAIA
branch) and never the old city-to-airport chord; the materiality thresholds A-align-120..123."""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pytest

from network import align

# A two-part fixture: a main line running east along 24.20 N, a branch leaving it at the
# junction J and ending at an "airport" P to the south-west (coordinates off the cell edges).
# The old stitch drew a straight chord from P back to the city end C of the main line; that
# chord must not be in the band.
C = (24.2013, 45.1013)  # city end of the main line (lat, lon)
J = (24.2013, 45.3013)  # junction
E = (24.2013, 45.6013)  # far end of the main line
P = (24.0513, 45.2013)  # branch end (airport)


def _write_line(root: Path, geometry: dict) -> None:
    base = root / align.LINES / "geojson"
    base.mkdir(parents=True, exist_ok=True)
    fc = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"line_id": "fixture-hhr", "layer": "existing"},
                "geometry": geometry,
            }
        ],
    }
    (base / "fixture-hhr.geojson").write_text(json.dumps(fc), encoding="utf-8")
    (base / "existing.geojson").write_text(json.dumps(fc), encoding="utf-8")


def _grid() -> align.Grid:
    step = 10
    res = step * align.ad.RES
    w, s, e, n = 45.0, 23.95, 45.7, 24.3
    r0, r1 = int(math.floor((90.0 - n) / res)), int(math.ceil((90.0 - s) / res))
    c0, c1 = int(math.floor(w / res)), int(math.ceil(e / res))
    shape = (r1 - r0, c1 - c0)
    return align.Grid(step, r0, c0, np.zeros(shape, np.float32), np.zeros(shape, np.uint16))


def _cell(g: align.Grid, lat: float, lon: float) -> tuple[int, int]:
    r, c = g.rc(lat, lon)
    return int(np.rint(r)), int(np.rint(c))


def _interp(a: tuple[float, float], b: tuple[float, float], t: float) -> tuple[float, float]:
    return (a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1]))


@pytest.fixture()
def two_part_root(tmp_path: Path):
    root = tmp_path / "repo"
    _write_line(
        root,
        {
            "type": "MultiLineString",
            "coordinates": [
                [[C[1], C[0]], [J[1], J[0]], [E[1], E[0]]],
                [[J[1], J[0]], [P[1], P[0]]],
            ],
        },
    )
    align._rail_geoms.cache_clear()
    yield root
    align._rail_geoms.cache_clear()


def test_band_includes_every_part_and_not_the_chord(two_part_root: Path) -> None:
    g = _grid()
    m = align.rail_mask(g, [], two_part_root)
    # branch vertices and points along the branch are in the band
    for t in (0.0, 0.25, 0.5, 0.75, 1.0):
        assert m[_cell(g, *_interp(J, P, t))], f"branch point t={t} missing from the band"
    # main-line points are in the band
    for t in (0.0, 0.5, 1.0):
        assert m[_cell(g, *_interp(C, E, t))]
    # the old chord P -> C (away from both parts) is not
    for t in (0.3, 0.5, 0.7):
        r, c = _cell(g, *_interp(P, C, t))
        assert not m[r - 1 : r + 2, c - 1 : c + 2].any(), f"chord point t={t} is in the band"


def test_band_stitched_linestring_would_include_the_chord(tmp_path: Path) -> None:
    """Control: the old stitched LineString (main, branch, chord back) bands the chord."""
    root = tmp_path / "repo"
    _write_line(
        root,
        {
            "type": "LineString",
            "coordinates": [[x[1], x[0]] for x in (C, J, E, J, P, C)],
        },
    )
    align._rail_geoms.cache_clear()
    try:
        g = _grid()
        m = align.rail_mask(g, [], root)
        assert m[_cell(g, *_interp(P, C, 0.5))]
    finally:
        align._rail_geoms.cache_clear()


def test_rail_parts_and_layer_hashes(two_part_root: Path) -> None:
    geoms = align._rail_geoms(str(two_part_root))
    assert len(align.rail_parts(geoms["fixture-hhr"])) == 2
    h = align.rail_layer_hashes(two_part_root)
    assert set(h) == {"fixture-hhr.geojson", "existing.geojson"}
    assert all(len(v) == 64 for v in h.values())


def test_live_hhr_band_has_branch_not_chord() -> None:
    """On the live corrected hhr.geojson: the KAIA branch is in the band; the middle of the old
    stitch chord (KAIA -> Al-Sulaimaniyah, 17.32 km) is not."""
    from shapely.geometry import shape

    p = align.REPO_ROOT / align.LINES / "geojson" / "hhr.geojson"
    d = json.loads(p.read_text(encoding="utf-8"))
    geom = shape(d["features"][0]["geometry"])
    assert geom.geom_type == "MultiLineString" and len(geom.geoms) == 2
    branch = geom.geoms[1]
    kaia = branch.coords[-1]  # branch end at KAIA (lon, lat)
    # Al-Sulaimaniyah station: the vertex the old stitch jumped to
    import yaml

    hhr = yaml.safe_load((align.REPO_ROOT / align.LINES / "hhr.yaml").read_text(encoding="utf-8"))
    sul = next(s for s in hhr["stations"] if s["id"] == "jeddah")  # HHR Jeddah (Al-Sulaimaniyah)
    lon0, lat0 = min(kaia[0], sul["lon"]) - 0.1, min(kaia[1], sul["lat"]) - 0.1
    lon1, lat1 = max(kaia[0], sul["lon"]) + 0.1, max(kaia[1], sul["lat"]) + 0.1
    step = 10
    res = step * align.ad.RES
    r0, r1 = int(math.floor((90.0 - lat1) / res)), int(math.ceil((90.0 - lat0) / res))
    c0, c1 = int(math.floor(lon0 / res)), int(math.ceil(lon1 / res))
    shape_ = (r1 - r0, c1 - c0)
    g = align.Grid(step, r0, c0, np.zeros(shape_, np.float32), np.zeros(shape_, np.uint16))
    align._rail_geoms.cache_clear()
    try:
        m = align.rail_mask(g, [], align.REPO_ROOT)
    finally:
        align._rail_geoms.cache_clear()
    for lon, lat in branch.coords:
        assert m[_cell(g, lat, lon)]
    mid = ((kaia[1] + sul["lat"]) / 2, (kaia[0] + sul["lon"]) / 2)
    assert not m[_cell(g, *mid)], "the old KAIA -> Al-Sulaimaniyah chord is in the band"


# --------------------------------------------------------------------------- materiality thresholds
def _cfg() -> dict:
    from network import reroute

    return reroute.load_config(align.REPO_ROOT)


def _base() -> dict:
    return {
        "length_km": 100.0,
        "tunnel_km": 2.0,
        "viaduct_km": 0.0,
        "earthworks_km": 10.0,
        "run_min": 40.0,
    }


def test_thresholds_registered_values() -> None:
    m = _cfg()["material"]
    assert m["length_rel"] == {"value": 0.01, "assumption_id": "A-align-120"}
    assert m["structure_rel"] == {"value": 0.01, "assumption_id": "A-align-121"}
    assert m["run_min_abs"] == {"value": 0.5, "assumption_id": "A-align-122"}
    assert m["max_offset_km"] == {"value": 1.0, "assumption_id": "A-align-123"}
    assert _cfg()["corridors"] == [
        "S4-commuter_belt-jeddah-000",
        "S4-commuter_belt-jeddah-045",
        "S4-commuter_belt-jeddah-315",
        "S2-trunk_gap-riyadh-jeddah",
    ]


@pytest.mark.parametrize(
    ("change", "expected", "trigger"),
    [
        ({}, False, ""),
        ({"length_km": 100.9}, False, ""),  # 0.9 %
        ({"length_km": 101.1}, True, "length"),  # 1.1 %
        ({"tunnel_km": 2.019}, False, ""),  # 0.95 %
        ({"tunnel_km": 2.03}, True, "tunnel_km"),  # 1.5 %
        ({"viaduct_km": 0.001}, True, "viaduct_km"),  # old value 0: any change >= 0.001 km
        ({"viaduct_km": 0.0005}, False, ""),
        ({"earthworks_km": 9.8}, True, "earthworks_km"),
        ({"run_min": 40.5}, False, ""),  # exactly 0.5 min: not over
        ({"run_min": 40.51}, True, "run_min"),
        ({"offset_max_km": 1.0}, False, ""),
        ({"offset_max_km": 1.01}, True, "max_offset"),
    ],
)
def test_material_rule(change: dict, expected: bool, trigger: str) -> None:
    from network import reroute

    b = _base()
    a = _base() | {"offset_max_km": 0.0} | change
    v = reroute.material(b, a, _cfg())
    assert v["moved_materially"] is expected
    assert v["triggers"] == trigger


def test_path_offsets_identical_and_shifted() -> None:
    from shapely.geometry import LineString

    from network import reroute

    old = LineString([(39.0, 21.5), (39.2, 21.7)])
    same = reroute.path_offsets(old, old, 50.0, 500.0)
    assert same == {"offset_mean_km": 0.0, "offset_max_km": 0.0, "moved_km_over_500m": 0.0}
    # shift ~1.1 km north (0.01 deg latitude): every point moves by about 0.8-1.1 km laterally
    new = LineString([(39.0, 21.51), (39.2, 21.71)])
    s = reroute.path_offsets(old, new, 50.0, 500.0)
    assert 0.6 < s["offset_mean_km"] < 1.2
    assert s["moved_km_over_500m"] > 25.0


# --------------------------------------------------------------------------- A-station-001 check
def _airports():
    import pandas as pd

    return pd.DataFrame({"label": ["TST"], "lat": [24.10], "lon": [45.20]})


def _load(path: str) -> dict:
    import yaml

    return yaml.safe_load((align.REPO_ROOT / path).read_text(encoding="utf-8"))


def test_siting_refuses_station_addition_on_airport_land() -> None:
    from screening.corridors import siting_check

    c = _load("cities/ksa/corridors/station_addition/S5-station_addition-al-jubayl.yaml")
    planned = next(s for s in c["stations"] if s["class"] == "planned")
    on_air = c | {
        "id": "S5-fixture-on-airport",
        "stations": [
            s | {"lat": 24.105, "lon": 45.205} if s is planned else s for s in c["stations"]
        ],
    }
    far = c | {"id": "S5-fixture-far"}
    dec: list[dict] = []
    out = siting_check({"station_addition": [on_air, far]}, _airports(), dec)
    assert [x["id"] for x in out["station_addition"]] == ["S5-fixture-far"]
    assert out["station_addition"][0] is far  # unchanged object: byte-identical output
    assert len(dec) == 1 and dec[0]["candidate"] == "S5-fixture-on-airport"
    assert dec[0]["decision"].startswith("refused by siting rule A-station-001")
    assert "TST" in dec[0]["reason"]


def test_siting_flags_other_families_without_moving() -> None:
    from screening.corridors import CorridorSpec, siting_check

    c = _load("cities/ksa/corridors/commuter_belt/S4-commuter_belt-jeddah-000.yaml")
    town = c["stations"][-1]
    assert not town["source"].startswith("stations.geojson")
    moved = [s | {"lat": 24.10, "lon": 45.21} if s is town else s for s in c["stations"]]
    on_air = c | {"stations": moved}
    dec: list[dict] = []
    out = siting_check({"commuter_belt": [on_air]}, _airports(), dec)
    got = out["commuter_belt"][0]
    assert got["stations"] == moved  # nothing moved
    assert got["siting_flags"][0]["station"] == town["id"]
    assert got["siting_flags"][0]["airport"] == "TST"
    assert got["siting_flags"][0]["distance_km"] <= 1.5
    assert dec[0]["decision"].startswith("flagged by siting rule A-station-001")
    CorridorSpec.model_validate(got)  # the flag is a valid additive field


def test_siting_ignores_existing_and_airport_stations() -> None:
    from screening.corridors import siting_check

    c = _load("cities/ksa/corridors/station_addition/S5-station_addition-al-jubayl.yaml")
    sts = []
    for s in c["stations"]:
        if s["source"].startswith("stations.geojson"):
            s = s | {"lat": 24.10, "lon": 45.20}  # an existing station on airport land: kept
        else:
            s = s | {"lat": 24.10, "lon": 45.20, "class": "airport"}  # an airport halt: allowed
        sts.append(s)
    dec: list[dict] = []
    out = siting_check({"station_addition": [c | {"stations": sts}]}, _airports(), dec)
    assert len(out["station_addition"]) == 1 and dec == []


def test_siting_live_corridors_unaffected() -> None:
    """No current S2-S5 corridor station is on airport land: the check changes nothing."""
    from screening.corridors import airport_points, siting_check

    air = airport_points(align.REPO_ROOT / "cities/ksa/zones/economic_nodes.parquet")
    assert air is not None and len(air) == 27
    fams: dict[str, list[dict]] = {}
    for p in sorted((align.REPO_ROOT / "cities/ksa/corridors").rglob("*.yaml")):
        c = _load(p.relative_to(align.REPO_ROOT).as_posix())
        fams.setdefault(c["family"], []).append(c)
    dec: list[dict] = []
    out = siting_check(fams, air, dec)
    assert dec == []
    assert all(a is b for f in fams for a, b in zip(fams[f], out[f], strict=True))


# --------------------------------------------------------------------------- re-route maps
IDS = [
    "S4-commuter_belt-jeddah-000",
    "S4-commuter_belt-jeddah-045",
    "S4-commuter_belt-jeddah-315",
    "S2-trunk_gap-riyadh-jeddah",
]


def test_reroute_maps_exist_and_small() -> None:
    for cid in IDS:
        for tag in ("before", "after"):
            p = align.REPO_ROOT / f"docs/report/figures/reroute-{cid}-{tag}.png"
            assert p.exists(), p
            assert p.stat().st_size < 1_000_000


def test_reroute_map_idempotent_and_default_unchanged(tmp_path: Path) -> None:
    from common.figures import jeddah_hhr_map
    from network import reroute

    hhr = Path("cities/ksa/lines/geojson/hhr.geojson")
    cor = Path("cities/ksa/alignments/S4-commuter_belt-jeddah-000.geojson")
    ext = reroute.map_extent(align.REPO_ROOT / cor)
    w, s, e, n = ext
    assert w < 39.10 and s < 21.45 and e > 39.30 and n > 22.1  # chord box and the belt
    a, b = tmp_path / "a.png", tmp_path / "b.png"
    ra = jeddah_hhr_map(hhr, a, "t", cor, ext)
    jeddah_hhr_map(hhr, b, "t", cor, ext)
    assert a.read_bytes() == b.read_bytes()
    assert ra["corridor_km"] == 78.14 and ra["stitches_km"] == []
    # without the new arguments the FIX_HHR_JEDDAH map has no corridor key
    assert "corridor_km" not in jeddah_hhr_map(hhr, tmp_path / "c.png", "t")
