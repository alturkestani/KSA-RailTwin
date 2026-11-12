"""FIX_HHR_JEDDAH: branch lines are built as main + branch parts (no stitched chord), the real HHR
file has the expected parts and lengths, no line in existing.geojson carries a stitch, figures
rebuild identically, and the station inventory parses."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest
import yaml

from common import REPO_ROOT
from rail import lines as rl
from rail.osm import haversine_km

# Invented fixture: main line A(1) - 2 - J(3) - 4 - 5 - C(6) and a branch J(3) - 7 - 8 - K(9).
OPL = """\
n1 v1 dV c0 t2020-01-01T00:00:00Z i0 u T x40.0 y22.0
n2 v1 dV c0 t2020-01-01T00:00:00Z i0 u T x40.05 y22.0
n3 v1 dV c0 t2020-01-01T00:00:00Z i0 u T x40.1 y22.0
n4 v1 dV c0 t2020-01-01T00:00:00Z i0 u T x40.15 y22.0
n5 v1 dV c0 t2020-01-01T00:00:00Z i0 u T x40.2 y22.0
n6 v1 dV c0 t2020-01-01T00:00:00Z i0 u T x40.25 y22.0
n7 v1 dV c0 t2020-01-01T00:00:00Z i0 u T x40.1 y22.02
n8 v1 dV c0 t2020-01-01T00:00:00Z i0 u T x40.1 y22.04
n9 v1 dV c0 t2020-01-01T00:00:00Z i0 u T x40.1 y22.06
w100 v1 dV c0 t2020-01-01T00:00:00Z i0 u Trailway=rail Nn1,n2,n3,n4,n5,n6
w101 v1 dV c0 t2020-01-01T00:00:00Z i0 u Trailway=rail Nn3,n7,n8,n9
"""


def _station(sid: str, node: int, cls: str, **kw) -> dict:
    return {
        "id": sid,
        "name_en": sid.upper(),
        "name_ar": "محطة",
        "class": cls,
        "source": "S-fixture",
        "osm": f"node/{node}",
        **kw,
    }


SPEC = {
    "id": "fx-branch",
    "line": {
        "name_en": "Fixture Branch Line",
        "name_ar": "خط اختبار",
        "layer": "existing",
        "operator": "Fixture Operator",
        "status": "in_service",
        "source": "S-fixture",
        "line_type": "hsr",
        "fixture": True,
    },
    "stations": [
        _station("a", 1, "terminal"),
        _station("b", 2, "major"),
        _station("k", 9, "airport", branch=True),
        _station("c", 6, "terminal"),
    ],
}


def _parts(geom: dict) -> list[list]:
    return [geom["coordinates"]] if geom["type"] == "LineString" else geom["coordinates"]


def _stitches(c: list, jump_km: float = 2.0) -> list[int]:
    """Segments over jump_km that end on an already drawn vertex without retracing an already
    drawn segment: a jump back onto the line (the HHR chord), as opposed to a long straight OSM
    segment or an out-and-back over the same track."""
    seen: set[tuple] = set()
    segs: set[frozenset] = set()
    out = []
    for i, (a, b) in enumerate(zip(c, c[1:], strict=False)):
        seen.add(tuple(a))
        seg = frozenset((tuple(a), tuple(b)))
        if haversine_km(a[1], a[0], b[1], b[0]) > jump_km and tuple(b) in seen and seg not in segs:
            out.append(i)
        segs.add(seg)
    return out


@pytest.fixture()
def built(tmp_path: Path) -> Path:
    (tmp_path / "data/ksa/osm").mkdir(parents=True)
    (tmp_path / "data/ksa/osm/ksa-rail.opl").write_text(OPL, encoding="utf-8")
    (tmp_path / "rail/specs").mkdir(parents=True)
    (tmp_path / "cities/ksa/lines").mkdir(parents=True)
    (tmp_path / "rail/specs/fx.yaml").write_text(yaml.safe_dump(SPEC), encoding="utf-8")
    rl.build(only="", root=tmp_path)
    return tmp_path


def test_branch_is_its_own_part_without_chord(built: Path):
    fc = json.loads((built / "cities/ksa/lines/geojson/fx-branch.geojson").read_text("utf-8"))
    f = fc["features"][0]
    assert f["geometry"]["type"] == "MultiLineString"
    main, branch = f["geometry"]["coordinates"]
    assert f["properties"]["parts"] == ["main", "branch"]
    assert f["properties"]["part_to"] == [None, "k"]
    # main runs A..C once; the branch starts at the junction (n3), not at station B (n2)
    assert [p[0] for p in main] == [40.0, 40.05, 40.1, 40.15, 40.2, 40.25]
    assert branch[0] == [40.1, 22.0] and branch[-1] == [40.1, 22.06]
    assert len(branch) == 4
    for c in (main, branch):
        assert len({tuple(p) for p in c}) == len(c)
        assert _stitches(c) == []
    # km-posts unchanged by the fix: the branch station's km-post is the track distance via B
    line = yaml.safe_load((built / "cities/ksa/lines/fx-branch.yaml").read_text("utf-8"))
    km = {s["id"]: s["km_post"] for s in line["stations"]}
    leg = haversine_km(22.0, 40.05, 22.0, 40.1) + haversine_km(22.0, 40.1, 22.06, 40.1)
    assert km["k"] == pytest.approx(km["b"] + leg, abs=0.01)
    assert km["c"] == pytest.approx(haversine_km(22.0, 40.0, 22.0, 40.25), abs=0.05)


def test_multilinestring_validates(built: Path):
    assert rl.check_line(built / "cities/ksa/lines/fx-branch.yaml", built) == []


def test_line_without_branch_stays_linestring(built: Path):
    spec = yaml.safe_load(yaml.safe_dump(SPEC))
    spec["stations"] = [s for s in spec["stations"] if not s.get("branch")]
    (built / "rail/specs/fx.yaml").write_text(yaml.safe_dump(spec), encoding="utf-8")
    rl.build(only="", root=built)
    fc = json.loads((built / "cities/ksa/lines/geojson/fx-branch.geojson").read_text("utf-8"))
    assert fc["features"][0]["geometry"]["type"] == "LineString"
    assert "parts" not in fc["features"][0]["properties"]


def test_rebuild_preserves_located_station(built: Path):
    path = built / "cities/ksa/lines/stations.geojson"
    gj = json.loads(path.read_text("utf-8"))
    for f in gj["features"]:
        f["properties"]["location_method"] = "unlocated:test"
    path.write_text(json.dumps(gj), encoding="utf-8")
    rl.build(only="", root=built)
    gj2 = json.loads(path.read_text("utf-8"))
    assert {f["properties"]["station_uid"] for f in gj2["features"]} == {
        f"fx-branch:{s['id']}" for s in SPEC["stations"]
    }


# ----------------------------------------------------------------------------- real files
LINES = REPO_ROOT / "cities/ksa/lines"


def _real(name: str) -> dict:
    p = LINES / "geojson" / name
    if not p.exists():
        pytest.skip(f"{name} missing")
    return json.loads(p.read_text("utf-8"))


def test_hhr_main_and_branch_lengths():
    f = _real("hhr.geojson")["features"][0]
    assert f["geometry"]["type"] == "MultiLineString"
    assert f["properties"]["parts"] == ["main", "branch"]
    main, branch = (
        sum(haversine_km(a[1], a[0], b[1], b[0]) for a, b in zip(c, c[1:], strict=False))
        for c in f["geometry"]["coordinates"]
    )
    line = yaml.safe_load((LINES / "hhr.yaml").read_text("utf-8"))
    span = max(s["km_post"] for s in line["stations"] if s["id"] != "kaia")
    assert abs(main / line["length_km"] - 1) <= 0.02
    assert abs(main / span - 1) <= 0.02
    # The brief expected ~3.75 km (S-002, secondary); OSM's junction-to-terminal track is 6.69 km
    # (conflict C-fixhhr-001, open). The test pins the OSM figure and that it is a short stub.
    assert branch == pytest.approx(6.69, abs=0.05)
    assert branch < 10


def test_existing_layer_has_no_stitch():
    fc = _real("existing.geojson")
    hhr = [f for f in fc["features"] if f["properties"]["line_id"] == "hhr"]
    assert len(hhr) == 1 and hhr[0]["geometry"]["type"] == "MultiLineString"
    for f in fc["features"]:
        for c in _parts(f["geometry"]):
            assert _stitches(c) == [], f["properties"]["line_id"]
    # no stretch drawn twice on HHR (two SAR freight lines have short out-and-back reversals into
    # stub stations on real track; recorded in docs/status/main.md, out of this run's scope)
    for c in _parts(hhr[0]["geometry"]):
        assert len({tuple(p) for p in c}) == len(c)


def test_long_segments_are_osm_way_segments():
    """Every segment over 2 km in existing.geojson joins consecutive nodes of one OSM way (the
    stitched 17.3 km chord did not)."""
    opl = REPO_ROOT / rl.RAIL_OPL
    if not opl.exists():
        pytest.skip("OSM rail extract not present")
    osm = rl.OsmIndex(REPO_ROOT)
    c2n = {(v[0], v[1]): k for k, v in osm.nodes.items()}
    pairs = set()
    for w in osm.ways.values():
        for a, b in zip(w[0], w[0][1:], strict=False):
            pairs |= {(a, b), (b, a)}
    bad = []
    for f in _real("existing.geojson")["features"]:
        for c in _parts(f["geometry"]):
            for a, b in zip(c, c[1:], strict=False):
                long = haversine_km(a[1], a[0], b[1], b[0]) > 2
                if long and (c2n.get(tuple(a)), c2n.get(tuple(b))) not in pairs:
                    bad.append((f["properties"]["line_id"], a, b))
    assert bad == []


def test_stations_match_line_yaml():
    gj = _real("../stations.geojson")
    line = yaml.safe_load((LINES / "hhr.yaml").read_text("utf-8"))
    pts = {
        f["properties"]["station_id"]: f["geometry"]["coordinates"]
        for f in gj["features"]
        if f["properties"]["line_id"] == "hhr"
    }
    for s in line["stations"]:
        assert pts[s["id"]] == pytest.approx([s["lon"], s["lat"]], abs=1e-6)


def test_jeddah_figure_is_idempotent(tmp_path: Path):
    from common.figures import jeddah_hhr_map

    _real("hhr.geojson")
    a, b = tmp_path / "a.png", tmp_path / "b.png"
    ra = jeddah_hhr_map(Path("cities/ksa/lines/geojson/hhr.geojson"), a, "t")
    jeddah_hhr_map(Path("cities/ksa/lines/geojson/hhr.geojson"), b, "t")
    assert a.read_bytes() == b.read_bytes()
    assert ra["stitches_km"] == [] and ra["parts"] == ["main", "branch"]
    assert a.stat().st_size < 1_000_000


def test_screenshots_present_and_small():
    for name in ("hhr-jeddah-before.png", "hhr-jeddah-after.png"):
        p = REPO_ROOT / "docs/report/figures" / name
        assert p.exists() and p.stat().st_size < 1_000_000


def test_station_inventory_parses(tmp_path: Path):
    from rail import station_inventory as si

    out = tmp_path / "inv.csv"
    si.main(out=out, root=REPO_ROOT)
    rows = list(csv.DictReader(out.open(encoding="utf-8")))
    assert rows and list(rows[0]) == si.FIELDS
    assert {r["flag"] for r in rows} <= {"city", "airport", "on-airport-land", "unplaced"}
    by = {r["station_uid"]: r for r in rows}
    assert by["hhr:kaia"]["flag"] == "airport" and by["hhr:jeddah"]["flag"] == "city"
    assert by["landbridge:jeddah"]["flag"] == "unplaced"
    # no hypothetical (ours) station is an airport halt or on airport land today
    hyp = [r for r in rows if r["layer"] == "hypothetical"]
    assert hyp and all(r["flag"] == "city" for r in hyp)


def test_inventory_flag_rule():
    from rail.station_inventory import flag_of

    assert flag_of("major", "osm:node/1", 0.5) == "on-airport-land"
    assert flag_of("airport", "osm:node/1", 0.5) == "airport"
    assert flag_of("major", "osm:node/1", 1.6) == "city"
    assert flag_of("planned", "town_centroid:osm:node/1", 20.0, located=False) == "unplaced"
    assert flag_of("planned", "unlocated:town_centroid_proxy:osm:way/1", 0.1) == "unplaced"


def test_stitch_helper_flags_chord_not_out_and_back():
    # out along y, branch out and back, then a 17 km jump back onto the drawn line: one stitch
    line = [[40.0, 22.0], [40.0, 22.1], [40.0, 22.2], [40.0, 22.1], [40.0, 22.0], [40.1, 22.15]]
    assert _stitches(line) == []  # retracing the same OSM segments is not a stitch
    chord = [[40.0, 22.0], [40.0, 22.05], [40.0, 22.2], [40.0, 22.05], [40.15, 22.05]]
    chord += [[40.0, 22.0]]
    assert _stitches(chord) == [4]
