"""S6_L6_CONNECTED item 7: `network.align.osm_line` returns every part of a MultiLineString and
`compare` measures against main + branch (the published convention, docs/alignments.md §4d);
a LineString is compared exactly as before. Dry run on the existing routed HHR validation path:
no routing, no re-tune."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from shapely.geometry import LineString, MultiLineString, Point

from network import align

# two-part fixture: a main line east along 24.20 N, a branch from junction J south-west to P;
# the routed path visits the main line from C to J, then follows the branch to P
C = (24.2013, 45.1013)
J = (24.2013, 45.3013)
E = (24.2013, 45.6013)
P = (24.0513, 45.2013)


def _routed() -> pd.DataFrame:
    a = np.linspace(0, 1, 120)
    lat = np.r_[np.full(120, C[0]), J[0] + a * (P[0] - J[0])]
    lon = np.r_[C[1] + a * (J[1] - C[1]), J[1] + a * (P[1] - J[1])]
    return pd.DataFrame({"lat": lat, "lon": lon})


def _write(root: Path, geometry: dict) -> None:
    base = root / align.LINES / "geojson"
    base.mkdir(parents=True, exist_ok=True)
    fc = {
        "type": "FeatureCollection",
        "features": [
            {"type": "Feature", "properties": {"alignment_km": 1.0}, "geometry": geometry}
        ],
    }
    (base / "two-part.geojson").write_text(json.dumps(fc), encoding="utf-8")


@pytest.fixture()
def two_part(tmp_path: Path) -> Path:
    _write(
        tmp_path,
        {
            "type": "MultiLineString",
            "coordinates": [
                [[C[1], C[0]], [J[1], J[0]], [E[1], E[0]]],
                [[J[1], J[0]], [P[1], P[0]]],
            ],
        },
    )
    return tmp_path


def test_osm_line_returns_every_part(two_part: Path) -> None:
    g, props = align.osm_line("two-part", two_part)
    assert g.geom_type == "MultiLineString" and len(g.geoms) == 2
    assert props["alignment_km"] == 1.0
    m, _ = align.osm_line("two-part", two_part, main_only=True)
    assert m.geom_type == "LineString" and m.equals(g.geoms[0])


def test_compare_uses_the_branch(two_part: Path) -> None:
    g, _ = align.osm_line("two-part", two_part)
    both = align.compare(_routed(), g, None, None)
    main = align.compare(_routed(), g.geoms[0], None, None)
    # the routed path runs along the branch: every part cuts the offsets by an order of
    # magnitude (main is clipped between the projections of the routed ends, as before)
    assert both["mean_offset_km"] < main["mean_offset_km"] / 5
    assert both["hausdorff_km"] < main["hausdorff_km"] / 3
    # compared length = main clipped to the routed ends + the whole branch
    assert both["osm_km_clipped"] > main["osm_km_clipped"]


def test_compare_linestring_unchanged() -> None:
    """A single LineString takes the old code path (identity case of test_network_align)."""
    lat = np.linspace(24.0, 25.0, 200)
    lon = np.linspace(46.0, 46.5, 200)
    df = pd.DataFrame({"lat": lat, "lon": lon})
    m = align.compare(df, LineString(np.column_stack([lon, lat])), None, None)
    assert abs(m["length_error"]) < 1e-3 and m["mean_offset_km"] < 0.01
    # a one-part MultiLineString gives the same figures as its LineString
    m2 = align.compare(df, MultiLineString([np.column_stack([lon, lat])]), None, None)
    assert m2 == m


def test_live_hhr_compare_geometry_has_branch_not_chord() -> None:
    """Live hhr.geojson: the KAIA branch vertices lie on the compared geometry; the middle of the
    old KAIA -> Al-Sulaimaniyah stitch chord does not."""
    import yaml

    g, _ = align.osm_line("hhr", align.REPO_ROOT)
    assert g.geom_type == "MultiLineString" and len(g.geoms) == 2
    for x, y in g.geoms[1].coords:
        assert g.distance(Point(x, y)) < 1e-9
    kaia = g.geoms[1].coords[-1]
    hhr = yaml.safe_load((align.REPO_ROOT / align.LINES / "hhr.yaml").read_text(encoding="utf-8"))
    sul = next(s for s in hhr["stations"] if s["id"] == "jeddah")
    mid = Point((kaia[0] + sul["lon"]) / 2, (kaia[1] + sul["lat"]) / 2)
    assert g.distance(mid) > 0.01  # degrees, about 1 km: the chord is not in the geometry


RUN = align.REPO_ROOT / align.RUNS / "validation-s1"


@pytest.mark.skipif(not (RUN / "hhr/profile.parquet").exists(), reason="no routed validation run")
def test_live_hhr_dry_recompare_main_plus_branch() -> None:
    """The existing routed HHR path (runs/align/validation-s1) against every part prints the
    published main + branch figures (3.399 / 7.757 / objective about 7.473), not the main-only
    ones (3.432 / 7.774 / 7.484). No routing."""
    w = align.load_weights(None, align.REPO_ROOT)
    df, obj = align.recompare(RUN, w, align.REPO_ROOT)
    h = df.set_index("line").loc["hhr"]
    assert h["osm_parts"] == 2
    assert h["mean_offset_km"] == pytest.approx(3.399, abs=5e-4)
    assert h["p90_offset_km"] == pytest.approx(7.757, abs=5e-4)
    assert h["hausdorff_km"] == pytest.approx(14.330, abs=5e-4)
    assert obj == pytest.approx(7.473, abs=1e-3)
    # the SAR lines (one part) reproduce the published validation.csv
    pub = pd.read_csv(RUN / "validation.csv").set_index("line")
    for lid in ("sar-north-passenger", "sar-east-passenger"):
        assert df.set_index("line").loc[lid, "mean_offset_km"] == pub.loc[lid, "mean_offset_km"]
