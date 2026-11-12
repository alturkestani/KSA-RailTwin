# ruff: noqa: E501
"""R4_ALIGN router on a synthetic fixture: one 1-degree tile with a 10 km corridor across a ridge."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

from common import REPO_ROOT
from network import align
from network import align_data as ad

LAT0, LON0 = 24, 45
A = (24.5, 45.45)  # stations about 10 km apart, east-west, a ridge between them
B = (24.5, 45.55)


def _tile(root: Path, ridge_m: float) -> None:
    """Flat plain at 600 m with a north-south ridge (Gaussian, sigma 1.2 km) at lon 45.5."""
    lon = LON0 + (np.arange(ad.PX) + 0.5) / ad.PX
    lat = LAT0 + 1 - (np.arange(ad.PX) + 0.5) / ad.PX
    dx_km = (lon - 45.5) * 111.32 * np.cos(np.radians(24.5))
    z = 600.0 + ridge_m * np.exp(-0.5 * (dx_km / 1.2) ** 2)
    dem = np.repeat(z[None, :], ad.PX, axis=0)
    # a small built-up block south of the line (urban penalty must be finite, not a wall)
    flags = np.zeros((ad.PX, ad.PX), np.uint16)
    rr = (lat > 24.47) & (lat < 24.48)
    cc = (lon > 45.47) & (lon < 45.49)
    flags[np.ix_(rr, cc)] = ad.FLAGS["urban"]
    t = ad.tile_id(LAT0, LON0)
    ad._write(root / ad.TILES / "dem" / f"{t}.tif", dem, LAT0, LON0, "float32")
    ad._write(root / ad.TILES / "flags" / f"{t}.tif", flags, LAT0, LON0, "uint16")
    (root / ad.TILES / "tiles.txt").write_text(t + "\n")


@pytest.fixture()
def fixture_root(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    (root / "cities/ksa/assumptions").mkdir(parents=True)
    (root / align.LINES / "geojson").mkdir(parents=True)
    (root / align.COAST).parent.mkdir(parents=True)
    w = yaml.safe_load((REPO_ROOT / align.WEIGHTS).read_text(encoding="utf-8"))
    w["weights"]["structure_factor"] = {"value": 6.0, "assumption_id": "test"}
    w["router"]["window_min_halfwidth_km"] = {"value": 8, "assumption_id": "test"}
    (root / align.WEIGHTS).write_text(yaml.safe_dump(w), encoding="utf-8")
    coast = {
        "type": "Feature",
        "properties": {},
        "geometry": {"type": "LineString", "coordinates": [[50.0, 26.0], [50.1, 26.1]]},
    }
    (root / align.COAST).write_text("\x1e" + json.dumps(coast) + "\n", encoding="utf-8")
    # the Kingdom boundary mask (A-align-090): the fixture tile south of 24.52 N, just north of the stations
    (root / ad.ADMIN).parent.mkdir(parents=True, exist_ok=True)
    ksa = {
        "type": "Feature",
        "properties": {"@id": ad.KSA_RELATION, "ISO3166-1": "SA", "admin_level": "2"},
        "geometry": {
            "type": "Polygon",
            "coordinates": [[[45, 24], [46, 24], [46, 24.52], [45, 24.52], [45, 24]]],
        },
    }
    (root / ad.ADMIN).write_text("\x1e" + json.dumps(ksa) + "\n", encoding="utf-8")
    _tile(root, ridge_m=180.0)
    align._tile.cache_clear()
    align._rail_geoms.cache_clear()
    align._coast_tree.cache_clear()
    align._ksa.cache_clear()
    yield root
    align._tile.cache_clear()
    align._coast_tree.cache_clear()
    align._ksa.cache_clear()
    shutil.rmtree(tmp_path, ignore_errors=True)


def _corridor(line_type: str = "hsr") -> dict:
    st = [
        {
            "id": "a",
            "name_en": "A",
            "name_ar": "A",
            "km_post": 0.0,
            "lat": A[0],
            "lon": A[1],
            "class": "terminal",
            "source": "test",
        },
        {
            "id": "b",
            "name_en": "B",
            "name_ar": "B",
            "km_post": 10.1,
            "lat": B[0],
            "lon": B[1],
            "class": "terminal",
            "source": "test",
        },
    ]
    return {"id": "fixture-ridge", "line_type": line_type, "stations": st}


def test_route_fixture_corridor(fixture_root: Path) -> None:
    w = align.load_weights(None, fixture_root)
    res = align.route_corridor(_corridor(), w, fixture_root)
    df = res["profile"]
    s = align.summarise(_corridor(), res, w)
    straight = float(align.gc_km(*A, *B))
    assert s["length_km"] >= straight * 0.999
    assert s["detour_ratio"] >= 0.999
    # endpoints pinned at the stations
    assert abs(df.lat.iloc[0] - A[0]) < 1e-5 and abs(df.lon.iloc[-1] - B[1]) < 1e-5
    # the formation never exceeds the class cap (2.5 % for HSR)
    assert s["formation_cap_ok"] and s["formation_max_grade"] <= 0.025 + 5e-5
    # a 180 m ridge over ~1.2 km sigma cannot be crossed at 2.5 % without a structure or deep cut
    assert s["tunnel_km"] + s["viaduct_km"] + s["earthworks_km"] > 0
    assert set(df.structure) <= {"tunnel", "viaduct", "earthworks", "at_grade"}
    assert abs(sum(s["terrain_shares"].values()) - 1) < 1e-3


def test_route_stays_in_the_kingdom(fixture_root: Path) -> None:
    w = align.load_weights(None, fixture_root)
    df = align.route_corridor(_corridor(), w, fixture_root)["profile"]
    assert (df.lat < 24.52).all()


def test_route_is_deterministic(fixture_root: Path, tmp_path: Path) -> None:
    w = align.load_weights(None, fixture_root)
    outs = []
    for k in range(2):
        o = tmp_path / f"run{k}"
        align.write_outputs(
            _corridor(), align.route_corridor(_corridor(), w, fixture_root), w, o, 1, fixture_root
        )
        outs.append(
            (
                (o / "alignment.geojson").read_bytes(),
                (o / "summary.json").read_bytes(),
                pd.read_parquet(o / "profile.parquet"),
            )
        )
    assert outs[0][0] == outs[1][0]
    assert outs[0][1] == outs[1][1]
    pd.testing.assert_frame_equal(outs[0][2], outs[1][2])
    meta = json.loads((tmp_path / "run0" / "meta.json").read_text())
    assert meta["weights_hash"] == align.weights_hash(w)


def test_mixed_cap_is_stricter(fixture_root: Path) -> None:
    w = align.load_weights(None, fixture_root)
    s_h = align.summarise(
        _corridor("hsr"), align.route_corridor(_corridor("hsr"), w, fixture_root), w
    )
    s_m = align.summarise(
        _corridor("mixed"), align.route_corridor(_corridor("mixed"), w, fixture_root), w
    )
    assert s_m["formation_cap_ok"] and s_m["formation_max_grade"] <= 0.0125 + 5e-5
    heavy_h = s_h["tunnel_km"] + s_h["viaduct_km"]
    heavy_m = s_m["tunnel_km"] + s_m["viaduct_km"]
    assert heavy_m >= heavy_h


def test_fit_profile_respects_cap() -> None:
    w = yaml.safe_load((REPO_ROOT / align.WEIGHTS).read_text(encoding="utf-8"))
    z = np.concatenate([np.zeros(60), np.linspace(0, 100, 10), np.full(60, 100.0)])
    f, relaxed = align.fit_profile(z, 100.0, 0.0125, w)
    assert not relaxed
    assert np.max(np.abs(np.diff(f))) <= 1.25 + 1e-3
    assert f[0] == pytest.approx(0.0) and f[-1] == pytest.approx(100.0)
    # 100 m in 4.9 km cannot be met at 1.25 %: the ends are freed and the result flagged
    short = np.concatenate([np.zeros(20), np.linspace(0, 100, 10), np.full(20, 100.0)])
    f2, relaxed2 = align.fit_profile(short, 100.0, 0.0125, w)
    assert relaxed2 and np.max(np.abs(np.diff(f2))) <= 1.25 + 1e-3


def test_smoothing_and_radius() -> None:
    # a quarter circle of radius 3 km: three-point radius recovers it
    t = np.linspace(0, np.pi / 2, 400)
    xy = np.column_stack([3000 * np.cos(t), 3000 * np.sin(t)])
    xy = align.resample(xy, 50.0)
    R = align.radius_m(xy, 6)
    assert np.nanmedian(R[np.isfinite(R)]) == pytest.approx(3000, rel=0.01)
    # pinned smoothing keeps both ends
    zig = np.column_stack([np.arange(100) * 50.0, np.where(np.arange(100) % 2, 30.0, 0.0)])
    sm = align.gauss_pinned(zig, 5.0)
    assert np.allclose(sm[0], zig[0]) and np.allclose(sm[-1], zig[-1])
    assert np.ptp(sm[20:80, 1]) < np.ptp(zig[20:80, 1])


def test_curve_speed_restriction() -> None:
    w = yaml.safe_load((REPO_ROOT / align.WEIGHTS).read_text(encoding="utf-8"))
    kl = align.Klass("hsr", 0.025, 300.0, 7000.0, 11.8 * 300**2 / 7000, 6.0)
    df = pd.DataFrame(
        {
            "s_km": np.arange(0, 20, 0.1),
            "vmax_kmh": np.where((np.arange(200) > 50) & (np.arange(200) < 80), 212.0, 300.0),
        }
    )
    rs = align.restrictions(df, kl, w)
    assert len(rs) == 1 and rs[0]["kmh"] == 210.0
    assert rs[0]["from_km"] < 5.1 < 7.9 < rs[0]["to_km"]


def test_validation_metrics_identity() -> None:
    from shapely.geometry import LineString

    lat = np.linspace(24.0, 25.0, 200)
    lon = np.linspace(46.0, 46.5, 200)
    df = pd.DataFrame({"lat": lat, "lon": lon})
    m = align.compare(df, LineString(np.column_stack([lon, lat])), None, None)
    assert abs(m["length_error"]) < 1e-3
    assert m["mean_offset_km"] < 0.01 and m["hausdorff_km"] < 0.01


def test_generator_applies_routed_sidecar(tmp_path: Path) -> None:
    from screening.corridors import apply_alignment, stations_key

    c = yaml.safe_load(
        next((REPO_ROOT / "cities/ksa/corridors/trunk_gap").glob("*.yaml")).read_text()
    )
    c.pop("alignment_routed", None)
    st = sorted(c["stations"], key=lambda s: float(s["km_post"]))
    sc = {
        "id": c["id"],
        "status": "routed",
        "stations_key": stations_key(c["stations"]),
        "station_km": {s["id"]: round(float(s["km_post"]) * 1.1, 3) for s in st},
        "length_km": round(float(st[-1]["km_post"]) * 1.1, 3),
        "detour_ratio": 1.1,
        "terrain_shares": {"flat_desert": 0.7, "mixed": 0.3},
        "tunnel_km": 1.0,
        "viaduct_km": 2.0,
        "geojson": f"cities/ksa/alignments/{c['id']}.geojson",
        "speed_restrictions": [],
    }
    (tmp_path / f"{c['id']}.json").write_text(json.dumps(sc))
    out = apply_alignment(c, tmp_path)
    assert out["length_km"] == sc["length_km"] and out["route_factor"]["value"] == 1.0
    assert out["alignment_routed"]["status"] == "routed"
    assert out["structures_share"]["tunnel"] == round(1.0 / sc["length_km"], 4)
    assert "A-corr-012" not in out["assumptions_used"] and "A-align-080" in out["assumptions_used"]
    moved = c | {"stations": [s | {"lat": s["lat"] + 0.01} for s in c["stations"]]}
    assert apply_alignment(moved, tmp_path)["alignment_routed"]["status"].startswith("stale")


def test_costing_terrain_shares_sum_to_one() -> None:
    from network.evaluate import _shares

    sh = _shares({"dunes": 0.0448958, "flat_desert": 0.6549354, "mixed": 0.3001700}, 1.0)
    assert abs(sum(sh.values()) - 1.0) <= 1e-9
    assert all(v > 0 for v in sh.values())


def test_infeasible_leg_is_flagged_and_not_costed() -> None:
    from network.evaluate import infeasible_reason

    w = yaml.safe_load((REPO_ROOT / align.WEIGHTS).read_text(encoding="utf-8"))
    kl = align.Klass("commuter", 0.025, 160.0, 1991.0, 151.7, 10.0)
    n = 300  # two legs of 15 km; leg 1 drops 1,000 m (needs 40 km at 2.5 %)
    s_km = np.linspace(0, 29.9, n)
    leg = (np.arange(n) >= 150).astype(int)
    z = np.concatenate([np.full(150, 500.0), np.linspace(2000.0, 1000.0, n - 150)])
    df = pd.DataFrame(
        {
            "leg": leg,
            "s_km": s_km,
            "lat": 24 + s_km / 111,
            "lon": np.full(n, 46.0),
            "z_ground_m": z,
            "z_formation_m": z,
            "height_m": 0.0,
            "structure": "at_grade",
            "terrain": "flat_desert",
            "flag_bits": 0,
            "vmax_kmh": 160.0,
        }
    )
    df.loc[leg == 0, ["z_ground_m", "z_formation_m"]] = 500.0
    legs = pd.DataFrame(
        [
            {
                "leg": 0,
                "from": "a",
                "to": "b",
                "straight_km": 14.9,
                "routed_km": 14.9,
                "ends_relaxed": False,
            },
            {
                "leg": 1,
                "from": "b",
                "to": "c",
                "straight_km": 15.0,
                "routed_km": 15.0,
                "ends_relaxed": True,
            },
        ]
    )
    s = align.summarise({"id": "x"}, {"profile": df, "legs": legs, "klass": kl}, w)
    assert s["profile_feasible"] is False
    assert (
        s["infeasible_legs"][0]["from"] == "b" and s["infeasible_legs"][0]["min_km_at_cap"] == 40.0
    )
    c = {
        "alignment_routed": {
            "status": "routed",
            "profile_feasible": False,
            "max_grade_cap": 0.025,
            "infeasible_legs": s["infeasible_legs"],
        }
    }
    assert infeasible_reason(c).startswith("grade-infeasible")
    assert (
        infeasible_reason({"alignment_routed": {"status": "routed", "profile_feasible": True}})
        is None
    )
