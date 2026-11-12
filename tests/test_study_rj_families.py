"""STUDY_RJ_FAMILIES (Tariq, 6 Nov 2026): the all-families comparison layout and the Riyadh-Jeddah
corridor study. A research study: no judge, no top5/SWITCHER/R7/R8 change, S1 and HHR untouched.
"""

from __future__ import annotations

import json
import subprocess

import numpy as np
import pandas as pd
import pytest
import yaml

from common import REPO_ROOT
from common.labels import ALIGNMENT_LIMITATION, LABEL
from common.schemas import Scenario
from study import families as fam
from study import rj
from tests.localdata import needs_local

START_HEAD = "8dafdfe"  # HEAD at the start of STUDY_RJ_FAMILIES
# R9 (7 Nov 2026): the run-scoped guard is pinned to the last commit before R9 (release
# preparation edits the licence register and the executive-summary banners by approval).
END_HEAD = "4da3bcf"
NOTE = REPO_ROOT / "docs/rj-routes-study.md"
ROUTES = ("RJ-LB", "RJ-A", "RJ-B", "RJ-C1", "RJ-C2")
# Areas this run must not change (prompt "Do not change" and the handoff list)
UNTOUCHED = [
    "cities/ksa/lines",
    "scenarios/S1.yaml",
    "network/graph_params.yaml",
    "cities/ksa/assumptions/access_network.yaml",
    "cities/ksa/assumptions/align_weights.yaml",
    "cities/ksa/alignments",
    "cities/ksa/corridors",
    "runs/r6/top5",
    "judge",
    "film",
    "docs/licences.md",
    "docs/licences.csv",
    "docs/report",
    "web",
    "api",
    "prompts/STUDY_RJ_FAMILIES.md",
]


def _diff(*paths: str) -> list[str]:
    r = subprocess.run(
        ["git", "cat-file", "-e", START_HEAD], cwd=REPO_ROOT, capture_output=True, check=False
    )
    if r.returncode:
        pytest.skip("start HEAD not in this clone")
    return subprocess.run(
        ["git", "diff", "--name-only", START_HEAD, END_HEAD, "--", *paths],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.split()


# --------------------------------------------------------------------------- item 1
@needs_local("runs/r6/v3/library/library.json")
def test_all_families_is_a_comparison_layout() -> None:
    d = yaml.safe_load((REPO_ROOT / fam.SCENARIO).read_text(encoding="utf-8"))
    Scenario.model_validate(d)
    assert d["kind"] == "comparison_layout"
    assert d["label"] == "comparison layout, not the recommended programme"
    assert not d["id"].startswith("S6")
    assert LABEL in d["labels"]
    assert d["baseline"] == "S1"
    s1 = yaml.safe_load((REPO_ROOT / "scenarios/S1.yaml").read_text(encoding="utf-8"))
    assert d["lines"]["include"] == s1["lines"]["include"]  # S1 as it stands, Landbridge included
    lib = fam.library_ids()
    assert len(lib) == 73 and len(d["candidates"]) == 72
    drawn = {p.rsplit("/", 1)[1].removesuffix(".yaml") for p in d["candidates"]}
    assert drawn == set(lib) - set(fam.COMBINED)
    assert all((REPO_ROOT / p).exists() for p in d["candidates"])
    assert not any("alignments-study" in p for p in d["candidates"])  # RJ sketches not in it


def test_all_families_not_in_top5_switcher_or_r8() -> None:
    for p in (
        "runs/r6/top5/top5.csv",
        "web/src/config.ts",
        "web/src/App.tsx",
        "docs/report/figures/figures-index.csv",
    ):
        f = REPO_ROOT / p
        if f.exists():
            t = f.read_text(encoding="utf-8")
            for token in ("all-families", "S1-S5-all-families", "rj-routes", "study-rj"):
                assert token not in t, (p, token)
    assert not list((REPO_ROOT / "runs/r6/top5").glob("*all-families*"))


def test_untouched_areas() -> None:
    assert _diff(*UNTOUCHED) == []


# --------------------------------------------------------------------------- item 3
@pytest.mark.parametrize("rid", ROUTES)
def test_rj_sketch_is_routed_not_straight(rid: str) -> None:
    summ = json.loads((REPO_ROOT / rj.STUDY / f"{rid}.json").read_text(encoding="utf-8"))
    assert summ["weights_hash"] == rj.FROZEN_HASH
    assert summ["profile_feasible"] and summ["formation_cap_ok"]
    assert summ["length_km"] > summ["straight_km_legs"] * 1.01
    fc = json.loads((REPO_ROOT / rj.STUDY / f"{rid}.geojson").read_text(encoding="utf-8"))
    routed = [f for f in fc["features"] if f["properties"]["kind"] == "routed"]
    assert len(routed) == 1
    coords = routed[0]["geometry"]["coordinates"]
    c = rj.load_corridor(rid)
    assert len(coords) > 20 * len(c["stations"])  # a path, not a station-to-station polyline
    from rail.hhr_check import stitch_jumps

    assert stitch_jumps(coords) == []


def _densify(coords: list[list[float]], step_km: float = 0.25) -> pd.DataFrame:
    pts = []
    for (x0, y0), (x1, y1) in zip(coords, coords[1:], strict=False):
        n = max(1, int(float(rj.haversine_km(y0, x0, y1, x1)) / step_km))
        t = np.linspace(0, 1, n, endpoint=False)
        pts += list(zip(y0 + t * (y1 - y0), x0 + t * (x1 - x0), strict=True))
    pts.append((coords[-1][1], coords[-1][0]))
    return pd.DataFrame(pts, columns=["lat", "lon"])


@pytest.mark.parametrize("rid", ROUTES)
def test_through_track_and_stops_outside_sourced_markers(rid: str) -> None:
    p = rj.params()
    mk = rj.load_markers()
    fc = json.loads((REPO_ROOT / rj.STUDY / f"{rid}.geojson").read_text(encoding="utf-8"))
    coords = next(f for f in fc["features"] if f["properties"]["kind"] == "routed")["geometry"][
        "coordinates"
    ]
    res = rj.siting_check(_densify(coords), mk, p)
    assert res["outside"] and res["points_not_verifiable"] == 0
    assert res["min_distance_to_marker_km"] > float(rj._v(p["siting"]["clearance_km"]))
    for s in rj.load_corridor(rid)["stations"]:
        r = rj.siting_check(pd.DataFrame({"lat": [s["lat"]], "lon": [s["lon"]]}), mk, p)
        assert r["outside"], s["id"]


def test_markers_are_sourced_points_not_a_polygon() -> None:
    fc = json.loads((REPO_ROOT / rj.MARKERS).read_text(encoding="utf-8"))
    assert "OpenStreetMap" in fc["attribution"] and "ODbL" in fc["attribution"]
    assert len(fc["features"]) == 49
    assert {f["geometry"]["type"] for f in fc["features"]} == {"Point"}
    assert all(
        f["properties"]["source"] == "S-rj-001" and f["properties"]["osm_id"].startswith("node/")
        for f in fc["features"]
    )


def test_gateways_on_hhr_and_s1_landbridge_not_rewritten() -> None:
    p = rj.params()
    for g in ("gateway-sw", "gateway-nw"):
        assert rj.place(g, p)["snap_km"] < 0.5
    lb = yaml.safe_load(
        (REPO_ROOT / "cities/ksa/lines/landbridge.yaml").read_text(encoding="utf-8")
    )
    assert [s["km_post"] for s in lb["stations"]] == [0.0, 236.4, 588.3, 819.5, 874.3]


# --------------------------------------------------------------------------- item 7
def test_study_note_labels_bounds_and_wording() -> None:
    t = NOTE.read_text(encoding="utf-8")
    assert LABEL in t
    assert ALIGNMENT_LIMITATION in t
    assert "hypothetical (ours), user-proposed" in t
    assert "comparison layout, not the recommended programme" in t
    for s in (
        "2 hours",
        "9 hours",
        "1:50",
        "450 km/h",
        "100 km/h",
        "door-to-door",
        "C-002",
        "S-rj-030",
    ):
        assert s in t, s
    assert "Haram boundary" in t and "No polygon is drawn" in t
    low = t.lower()
    for bad in (
        "will reduce",
        "will transform",
        "vignette",
        "pilgrim",
        "muslim",
        "nationality",
        "case study of",
    ):
        assert bad not in low, bad
    assert " will " not in low


def test_study_figures_exist_and_are_not_indexed() -> None:
    idx = (REPO_ROOT / "docs/report/figures/figures-index.csv").read_text(encoding="utf-8")
    for f in (
        "all-families-map.png",
        "rj-routes-map.png",
        "rj-haram-siting.png",
        "rj-travel-times.png",
    ):
        assert (REPO_ROOT / "docs/study-rj" / f).exists()
        assert f not in idx
