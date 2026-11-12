"""rail.osm (OPL parsing, layer tagging) and rail.lines (build, km-posts, validate) on the
invented fixture tests/fixtures/rail_fixture.opl (no real data, runs in well under a second)."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest
import yaml
from shapely.geometry import box

from rail import lines as rl
from rail.osm import build_layers, haversine_km, opl_unescape, parse_opl

FIX = Path(__file__).parent / "fixtures" / "rail_fixture.opl"


def test_opl_unescape_arabic_and_space():
    assert opl_unescape("Fixture%20%Alpha") == "Fixture Alpha"
    assert opl_unescape("%0623%%0644%%0641%") == "ألف"


def test_parse_opl_counts_and_tags():
    nodes, ways, rels = parse_opl(FIX)
    assert len(nodes) == 8 and len(ways) == 4 and len(rels) == 1
    assert nodes[10][2]["name:ar"] == "ألف"
    assert ways[100][0] == [1, 2, 3]
    assert rels[200][0][0] == ("n", 10, "stop")


def test_layers_keep_three_osm_classes_apart():
    nodes, ways, rels = parse_opl(FIX)
    out = build_layers(nodes, ways, rels, box(39, 21, 41, 23))
    assert {f["properties"]["layer"] for f in out["existing"]} == {"existing"}
    assert [f["properties"]["osm_id"] for f in out["historical"]] == [102]
    # OSM construction/proposed is never a committed line by itself (rule 5)
    assert [f["properties"]["layer"] for f in out["planned"]] == ["unassigned"]
    assert {f["properties"]["osm_id"] for f in out["stations"]} == {10, 11}
    (route,) = out["routes"]
    assert [s["osm_id"] for s in route["stops"]] == [10, 11]


def _fixture_root(tmp_path: Path, spec: dict) -> Path:
    (tmp_path / "data/ksa/osm").mkdir(parents=True)
    shutil.copy(FIX, tmp_path / "data/ksa/osm/ksa-rail.opl")
    (tmp_path / "rail/specs").mkdir(parents=True)
    (tmp_path / "cities/ksa/lines").mkdir(parents=True)
    (tmp_path / "rail/specs/fx.yaml").write_text(yaml.safe_dump(spec), encoding="utf-8")
    return tmp_path


SPEC = {
    "id": "fixture-line",
    "line": {
        "name_en": "Fixture Line",
        "name_ar": "خط اختبار",
        "layer": "existing",
        "operator": "Fixture Operator",
        "status": "in_service",
        "source": "S-fixture",
        "line_type": "conventional_passenger",
        "fixture": True,
    },
    "stations": [
        {
            "id": "a",
            "name_en": "Fixture Alpha",
            "name_ar": "ألف",
            "class": "terminal",
            "source": "S-fixture",
            "osm": "node/10",
        },
        {
            "id": "c",
            "name_en": "Fixture Gamma",
            "name_ar": "جيم",
            "class": "terminal",
            "source": "S-fixture",
            "osm": "node/11",
        },
    ],
}


def test_build_km_post_is_track_distance(tmp_path):
    root = _fixture_root(tmp_path, SPEC)
    rl.build(only="", root=root)
    line = yaml.safe_load((root / "cities/ksa/lines/fixture-line.yaml").read_text("utf-8"))
    expected = haversine_km(22.0, 40.0, 22.0, 40.2) + haversine_km(22.0, 40.2, 22.1, 40.2)
    assert line["stations"][1]["km_post"] == pytest.approx(expected, abs=0.01)
    assert rl.check_line(root / "cities/ksa/lines/fixture-line.yaml", root) == []
    st = (root / "cities/ksa/lines/stations.geojson").read_text("utf-8")
    assert '"location_method": "osm:node/10"' in st


def test_committed_great_circle_and_unlocated_flag(tmp_path):
    spec = yaml.safe_load(yaml.safe_dump(SPEC))
    spec["km_method"] = "great_circle"
    spec["line"].update(
        layer="committed", status="announced", source_date="2026-10-31", uncertainty_km=20
    )
    spec["line"].pop("operator")
    spec["stations"][1] = {
        "id": "c",
        "name_en": "Fixture Gamma",
        "name_ar": "جيم",
        "class": "planned",
        "source": "S-fixture",
        "proxy_osm": "node/11",
    }
    root = _fixture_root(tmp_path, spec)
    rl.build(only="", root=root)
    st = (root / "cities/ksa/lines/stations.geojson").read_text("utf-8")
    assert "unlocated:town_centroid_proxy" in st and '"located": false' in st
    assert rl.check_line(root / "cities/ksa/lines/fixture-line.yaml", root) == []


def test_validate_rejects_committed_without_uncertainty(tmp_path):
    spec = yaml.safe_load(yaml.safe_dump(SPEC))
    spec["km_method"] = "great_circle"
    spec["line"].update(layer="committed", status="announced", source_date="2026-10-31")
    root = _fixture_root(tmp_path, spec)
    rl.build(only="", root=root)
    errs = rl.check_line(root / "cities/ksa/lines/fixture-line.yaml", root)
    assert any("uncertainty_km" in e for e in errs)


def test_existing_cannot_be_planned_status():
    from common.schemas import LineSpec

    data = {**SPEC["line"], "id": "x", "status": "announced"}
    data["stations"] = [
        {**s, "km_post": i, "lat": 22.0, "lon": 40.0 + i / 10}
        for i, s in enumerate({k: v for k, v in s.items() if k != "osm"} for s in SPEC["stations"])
    ]
    with pytest.raises(ValueError):
        LineSpec.model_validate(data)


def test_real_line_files_validate_when_present():
    """The committed cities/ksa/lines/*.yaml validate (skips in a clone without them)."""
    from common import REPO_ROOT

    files = sorted((REPO_ROOT / "cities/ksa/lines").glob("*.yaml"))
    if not files:
        pytest.skip("no line files")
    errs = [e for f in files for e in rl.check_line(f, REPO_ROOT)]
    assert errs == []
    layers = {f.stem: yaml.safe_load(f.read_text("utf-8"))["layer"] for f in files}
    assert layers["hejaz-railway"] == "historical"
    assert all(layers[i] == "committed" for i in ("landbridge", "riyadh-rail-link"))
