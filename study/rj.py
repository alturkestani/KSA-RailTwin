# ruff: noqa: E501
"""Riyadh-Jeddah corridor study (STUDY_RJ_FAMILIES items 3-6): user-proposed hypothetical routes.

  uv run python -m study.rj corridors              # cities/ksa/alignments-study/corridors/<id>.yaml
  uv run python -m study.rj route --seed 1         # runs/study/rj/align-s1/<id> (frozen v1 weights)
  uv run python -m study.rj sidecars --seed 1      # cities/ksa/alignments-study/<id>.geojson/.json
  uv run python -m study.rj markers                # Haram boundary markers from the OSM extract
  uv run python -m study.rj siting --seed 1        # through track vs the sourced markers
  uv run python -m study.rj times --seed 1         # R4 running-time model x timetable factor
  uv run python -m study.rj costs --seed 1         # cost register via costs.estimate
  uv run python -m study.rj maps --seed 1          # study figures (docs/study-rj/)

Routing is `network.align.route_corridor` under the frozen v1 weights (hash checked); running times
are `access.running_time` with the generic timetable factor as `network.evaluate` applies it; costs
are `costs.estimate` on `network.evaluate.costing_input`. No new formula, no judge, no change to S1,
HHR, the interchange rules or the access model.

Hypothetical alignments (ours), user-proposed (Tariq, 6 Nov 2026): indicative engineering sketches,
not designs. Label: synthetic demand, uncalibrated: scenario comparison, not a forecast.
"""

from __future__ import annotations

import json
import math
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import typer
import yaml

from common import REPO_ROOT
from common.labels import ALIGNMENT_LIMITATION, LABEL
from common.runmeta import seed_option, write_meta
from network.geo import haversine_km

PARAMS = Path("cities/ksa/assumptions/rj_study.yaml")
STUDY = Path("cities/ksa/alignments-study")
CORR = STUDY / "corridors"
RUNS = Path("runs/study/rj")
FROZEN_HASH = "2b718ecbe6caead86e8424e621f90420815a6ada10ad6c4e1b7ffa00bca792d4"
OSM_PBF = Path("data/osm/gcc-states-latest.osm.pbf")
MARKERS = STUDY / "haram_markers.geojson"
STUDY_LABEL = (
    "hypothetical alignment (ours), user-proposed: indicative engineering sketch, not a design"
)

app = typer.Typer(add_completion=False, help=__doc__, no_args_is_help=True)


def _v(node: Any) -> Any:
    return node["value"] if isinstance(node, dict) and "value" in node else node


def params(root: Path = REPO_ROOT) -> dict[str, Any]:
    return yaml.safe_load((root / PARAMS).read_text(encoding="utf-8"))


# --------------------------------------------------------------------------- places
def hhr_points(root: Path = REPO_ROOT) -> np.ndarray:
    """(lat, lon) vertices of every part of the corrected hhr.geojson."""
    fc = json.loads((root / "cities/ksa/lines/geojson/hhr.geojson").read_text(encoding="utf-8"))
    pts = []
    for f in fc["features"]:
        g = f["geometry"]
        parts = [g["coordinates"]] if g["type"] == "LineString" else g["coordinates"]
        for part in parts:
            pts += [(c[1], c[0]) for c in part]
    return np.asarray(pts)


def place(pid: str, p: dict[str, Any], root: Path = REPO_ROOT) -> dict[str, Any]:
    d = dict(p["places"][pid])
    if d.get("snap") == "hhr":
        pts = hhr_points(root)
        dist = haversine_km(pts[:, 0], pts[:, 1], d["target_lat"], d["target_lon"])
        i = int(np.argmin(dist))
        d["lat"], d["lon"] = round(float(pts[i, 0]), 6), round(float(pts[i, 1]), 6)
        d["snap_km"] = round(float(dist[i]), 3)
    return d


def corridor(rid: str, p: dict[str, Any], root: Path = REPO_ROOT) -> dict[str, Any]:
    """Corridor YAML dict (line-yaml fields the router and the estimators read)."""
    r = p["routes"][rid]
    stations, km = [], 0.0
    prev = None
    for pid in r["points"]:
        d = place(pid, p, root)
        if prev is not None:
            km += float(haversine_km(prev["lat"], prev["lon"], d["lat"], d["lon"]))
        is_stop = pid in r["stops"]
        cls = "terminal" if pid in (r["points"][0], r["points"][-1]) else "intermediate"
        stations.append(
            {
                "id": pid,
                "name_en": d["name_en"],
                "name_ar": d["name_ar"],
                "km_post": round(km, 3),
                "lat": float(d["lat"]),
                "lon": float(d["lon"]),
                "class": cls if is_stop else "waypoint",
                "source": d.get("source") or d.get("assumption_id"),
            }
        )
        prev = d
    return {
        "id": rid,
        "name_en": f"Riyadh - Jeddah study {rid}: {r['title']} (hypothetical, user-proposed)",
        "name_ar": f"دراسة الرياض - جدة {rid} (افتراضي)",
        "family": "study_rj",
        "layer": "hypothetical",
        "operator": None,
        "status": "user-proposed",
        "source": "Tariq, 6 Nov 2026 (prompts/STUDY_RJ_FAMILIES.md item 3; CP7-6 user-proposed corridors)",
        "source_date": "2026-11-06",
        "accessed": "2026-11-06",
        "rule_id": "user-proposed (CP7-6)",
        "generated_from_ids": ["Tariq 2026-11-06 STUDY_RJ_FAMILIES"],
        "line_type": r["line_type"],
        "length_km": round(km, 3),
        "stations": stations,
        "stops": list(r["stops"]),
        "label": LABEL,
        "note": STUDY_LABEL,
    }


@app.command("corridors")
def corridors_cmd(root: Path = typer.Option(REPO_ROOT, hidden=True)) -> None:
    """Write one corridor YAML per study route (inputs to the router)."""
    p = params(root)
    (root / CORR).mkdir(parents=True, exist_ok=True)
    for rid in p["routes"]:
        c = corridor(rid, p, root)
        head = (
            f"# Version: {rid}.yaml v1.0 | 6 Nov 2026 | Author: STUDY_RJ_FAMILIES | Status: draft\n"
            f"# Generated by `study.rj corridors` from {PARAMS}; do not edit by hand.\n"
            f"# {STUDY_LABEL}. Label: {LABEL}.\n"
        )
        (root / CORR / f"{rid}.yaml").write_text(
            head + yaml.safe_dump(c, sort_keys=False, allow_unicode=True), encoding="utf-8"
        )
        typer.echo(f"{rid}: {len(c['stations'])} points, chain {c['length_km']} km")


# --------------------------------------------------------------------------- routing
def load_corridor(rid: str, root: Path = REPO_ROOT) -> dict[str, Any]:
    return yaml.safe_load((root / CORR / f"{rid}.yaml").read_text(encoding="utf-8"))


@app.command("route")
def route_cmd(
    route: list[str] = typer.Option(None, "--route", help="route id(s); default all"),
    seed: int = seed_option(),
    root: Path = typer.Option(REPO_ROOT, hidden=True),
) -> None:
    """Route every study corridor with network.align under the frozen v1 weights."""
    from network import align

    w = align.load_weights(None, root)
    h = align.weights_hash(w)
    if h != FROZEN_HASH:
        raise SystemExit(f"weights hash {h} is not the frozen v1 hash {FROZEN_HASH}")
    for rid in route or list(params(root)["routes"]):
        c = load_corridor(rid, root)
        out = root / RUNS / f"align-s{seed}" / rid
        s = align.write_outputs(c, align.route_corridor(c, w, root), w, out, seed, root)
        typer.echo(
            f"{rid}: {s['length_km']:.1f} km, tunnel {s['tunnel_km']} km, viaduct {s['viaduct_km']} km, "
            f"feasible {s['profile_feasible']}"
        )
    if align.weights_hash(align.load_weights(None, root)) != FROZEN_HASH:
        raise SystemExit("weights changed during the run")


# --------------------------------------------------------------------------- Haram markers
MARKER_NAMES = ("حد الحرم", "حدود الحرم")


def extract_markers(root: Path = REPO_ROOT) -> dict[str, Any]:
    """OSM nodes tagged boundary=marker whose name contains a Haram-boundary phrase (S-rj-001).
    Reads the local Geofabrik GCC extract with osmium; writes nothing under data/."""
    p = params(root)
    w, s, e, n = p["siting"]["osm_bbox_wsen"]
    tmp = root / RUNS / "osm"
    tmp.mkdir(parents=True, exist_ok=True)
    pbf = tmp / "makkah-area.osm.pbf"
    sub = tmp / "markers.osm.pbf"
    seq = tmp / "markers.geojsonseq"
    run = lambda *a: subprocess.run(a, check=True, capture_output=True)  # noqa: E731
    run(
        "osmium",
        "extract",
        "-b",
        f"{w},{s},{e},{n}",
        str(root / OSM_PBF),
        "-o",
        str(pbf),
        "--overwrite",
    )
    run("osmium", "tags-filter", str(pbf), "n/boundary=marker", "-o", str(sub), "--overwrite")
    run(
        "osmium",
        "export",
        str(sub),
        "-f",
        "geojsonseq",
        "-o",
        str(seq),
        "--overwrite",
        "--attributes",
        "type,id,version,timestamp",
    )
    feats = []
    for line in seq.read_text(encoding="utf-8").split("\n"):
        line = line.strip("\x1e").strip()
        if not line:
            continue
        f = json.loads(line)
        pr = f["properties"]
        name = pr.get("name", "") + " " + pr.get("alt_name", "")
        if not any(k in name for k in MARKER_NAMES):
            continue
        lon, lat = f["geometry"]["coordinates"]
        feats.append(
            {
                "type": "Feature",
                "properties": {
                    "osm_id": f"node/{pr['@id']}",
                    "osm_version": pr.get("@version"),
                    "osm_timestamp": pr.get("@timestamp"),
                    "name": pr.get("name"),
                    "name_en": pr.get("name:en"),
                    "historic": pr.get("historic"),
                    "source": "S-rj-001",
                },
                "geometry": {"type": "Point", "coordinates": [round(lon, 7), round(lat, 7)]},
            }
        )
    feats.sort(key=lambda f: f["properties"]["osm_id"])
    return {
        "type": "FeatureCollection",
        "name": "haram_boundary_markers_osm",
        "attribution": "(c) OpenStreetMap contributors, ODbL 1.0 (https://www.openstreetmap.org/copyright)",
        "note": "Haram boundary marker boards as mapped in OSM (boundary=marker, name contains "
        "'حد الحرم' / 'حدود الحرم'). Points, not a boundary: no complete official GIS boundary "
        "was found (S-rj-002) and no polygon is drawn. Precision: OSM point positions of roadside "
        "boards, typically metres to tens of metres; a board marks where a road crosses the "
        "boundary, not the line between boards (A-rj-004).",
        "features": feats,
    }


@app.command("markers")
def markers_cmd(root: Path = typer.Option(REPO_ROOT, hidden=True)) -> None:
    """Write the sourced Haram boundary markers (small ODbL table, credited)."""
    fc = extract_markers(root)
    (root / MARKERS).write_text(
        json.dumps(fc, ensure_ascii=False, indent=0) + "\n", encoding="utf-8"
    )
    typer.echo(f"{len(fc['features'])} markers -> {MARKERS}")


def load_markers(root: Path = REPO_ROOT) -> pd.DataFrame:
    fc = json.loads((root / MARKERS).read_text(encoding="utf-8"))
    return pd.DataFrame(
        [
            {
                **f["properties"],
                "lon": f["geometry"]["coordinates"][0],
                "lat": f["geometry"]["coordinates"][1],
            }
            for f in fc["features"]
        ]
    )


def bearing_deg(lat0: float, lon0: float, lat: Any, lon: Any) -> np.ndarray:
    p1, p2 = math.radians(lat0), np.radians(lat)
    dl = np.radians(np.asarray(lon) - lon0)
    y = np.sin(dl) * np.cos(p2)
    x = math.cos(p1) * np.sin(p2) - math.sin(p1) * np.cos(p2) * np.cos(dl)
    return (np.degrees(np.arctan2(y, x)) + 360.0) % 360.0


def siting_check(prof: pd.DataFrame, mk: pd.DataFrame, p: dict[str, Any]) -> dict[str, Any]:
    """Through-track points vs the sourced markers (A-rj-004): within check_radius of the centre,
    a point is outside when its distance from the centre exceeds the largest marker distance in
    its +/- sector (plus the clearance); no marker in the sector = not verifiable."""
    S = p["siting"]
    c = S["centre"]
    sec, clr, rad = (
        float(_v(S["sector_deg"])),
        float(_v(S["clearance_km"])),
        float(_v(S["check_radius_km"])),
    )
    mr = haversine_km(c["lat"], c["lon"], mk.lat.to_numpy(), mk.lon.to_numpy())
    mb = bearing_deg(c["lat"], c["lon"], mk.lat.to_numpy(), mk.lon.to_numpy())
    lat, lon = prof.lat.to_numpy(), prof.lon.to_numpy()
    r = haversine_km(c["lat"], c["lon"], lat, lon)
    b = bearing_deg(c["lat"], c["lon"], lat, lon)
    near = r <= rad
    inside, unverifiable, bracketed, margins = 0, 0, 0, []
    for ri, bi in zip(r[near], b[near], strict=True):
        d = np.abs((mb - bi + 180.0) % 360.0 - 180.0)
        m = mr[d <= sec]
        if not len(m):
            # fallback: the nearest marker by bearing on each side (still markers only, no polygon)
            sd = (mb - bi + 360.0) % 360.0
            cw, ccw = int(np.argmin(sd)), int(np.argmax(sd))
            if min(sd[cw], 360.0 - sd[ccw]) > 90.0:
                unverifiable += 1
                continue
            m = mr[[cw, ccw]]
            bracketed += 1
        margin = float(ri - m.max())
        margins.append(margin)
        if margin < clr:
            inside += 1
    dmin = haversine_km(
        lat[:, None], lon[:, None], mk.lat.to_numpy()[None, :], mk.lon.to_numpy()[None, :]
    ).min(axis=1)
    return {
        "points_within_check_radius": int(near.sum()),
        "points_inside_or_within_clearance": inside,
        "points_not_verifiable": unverifiable,
        "points_bracket_checked": bracketed,
        "min_sector_margin_km": round(min(margins), 3) if margins else None,
        "min_distance_to_marker_km": round(float(dmin.min()), 3),
        "min_distance_to_centre_km": round(float(r.min()), 3),
        "outside": bool(inside == 0 and unverifiable == 0),
        "clearance_km": clr,
        "sector_deg": sec,
    }


def hhr_chainage(p: dict[str, Any], mk: pd.DataFrame, root: Path = REPO_ROOT) -> dict[str, float]:
    """Km along the HHR main line from hhr:makkah to each gateway and to the HHR boundary marker."""
    from pyproj import Transformer
    from shapely import transform as stransform
    from shapely.geometry import Point, shape

    fc = json.loads((root / "cities/ksa/lines/geojson/hhr.geojson").read_text(encoding="utf-8"))
    g = shape(fc["features"][0]["geometry"])
    main = g.geoms[0] if g.geom_type == "MultiLineString" else g
    tr = Transformer.from_crs(4326, 32637, always_xy=True)
    f = lambda geom: stransform(geom, lambda xy: np.column_stack(tr.transform(xy[:, 0], xy[:, 1])))  # noqa: E731
    m = f(main)
    hy = yaml.safe_load((root / "cities/ksa/lines/hhr.yaml").read_text(encoding="utf-8"))
    mak = next(s for s in hy["stations"] if s["id"] == "makkah")
    k0 = m.project(f(Point(mak["lon"], mak["lat"])))
    out = {}
    for gid in ("gateway-sw", "gateway-nw"):
        d = place(gid, p, root)
        out[gid] = round(abs(m.project(f(Point(d["lon"], d["lat"]))) - k0) / 1000, 1)
    hm = mk[mk["name"].astype(str).str.contains("قطار")]
    for r in hm.itertuples():
        out[f"marker {r.osm_id} (HHR crossing board)"] = round(
            abs(m.project(f(Point(r.lon, r.lat))) - k0) / 1000, 1
        )
    return out


@app.command("siting")
def siting_cmd(
    seed: int = seed_option(), root: Path = typer.Option(REPO_ROOT, hidden=True)
) -> None:
    """Siting check of every routed path and stop against the sourced markers."""
    from rail.hhr_check import stitch_jumps

    p = params(root)
    mk = load_markers(root)
    out: dict[str, Any] = {"label": LABEL, "markers": len(mk), "routes": {}}
    for rid in p["routes"]:
        run = root / RUNS / f"align-s{seed}" / rid
        prof = pd.read_parquet(run / "profile.parquet")
        res = siting_check(prof, mk, p)
        c = load_corridor(rid, root)
        st = pd.DataFrame(c["stations"])
        res["stations"] = {
            s.id: {
                "class": s["class"],
                **{
                    k: v
                    for k, v in siting_check(
                        pd.DataFrame({"lat": [s.lat], "lon": [s.lon]}), mk, p
                    ).items()
                    if k
                    in (
                        "outside",
                        "min_distance_to_marker_km",
                        "min_distance_to_centre_km",
                        "points_not_verifiable",
                        "points_bracket_checked",
                        "min_sector_margin_km",
                    )
                },
            }
            for _, s in st.iterrows()
        }
        fc = json.loads((run / "alignment.geojson").read_text(encoding="utf-8"))
        coords = fc["features"][0]["geometry"]["coordinates"]
        res["stitch_jumps"] = stitch_jumps(coords)
        res["routed_vertices"] = len(coords)
        out["routes"][rid] = res
        typer.echo(
            f"{rid}: outside={res['outside']} min margin {res['min_sector_margin_km']} km, "
            f"min to marker {res['min_distance_to_marker_km']} km, unverifiable {res['points_not_verifiable']}, bracketed {res['points_bracket_checked']}, "
            f"stitches {len(res['stitch_jumps'])}"
        )
    out["hhr_km_from_makkah"] = hhr_chainage(p, mk, root)
    d = root / RUNS / f"siting-s{seed}"
    d.mkdir(parents=True, exist_ok=True)
    (d / "siting.json").write_text(
        json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    write_meta(
        d, seed, {"params": p["siting"]}, extra={"label": LABEL, "markers_file": str(MARKERS)}
    )


# --------------------------------------------------------------------------- sidecars
@app.command("sidecars")
def sidecars_cmd(
    seed: int = seed_option(), root: Path = typer.Option(REPO_ROOT, hidden=True)
) -> None:
    """Copy the routed alignment and summary of every study route next to its corridor YAML."""
    for rid in params(root)["routes"]:
        run = root / RUNS / f"align-s{seed}" / rid
        meta = json.loads((run / "meta.json").read_text(encoding="utf-8"))
        if meta.get("weights_hash") != FROZEN_HASH:
            raise SystemExit(
                f"{rid}: routed with weights {meta.get('weights_hash')}, not frozen v1"
            )
        shutil.copyfile(run / "alignment.geojson", root / STUDY / f"{rid}.geojson")
        summ = json.loads((run / "summary.json").read_text(encoding="utf-8"))
        summ |= {
            "study_label": STUDY_LABEL,
            "weights_hash": meta["weights_hash"],
            "code_version": meta.get("code_version"),
            "run": str(RUNS / f"align-s{seed}" / rid),
        }
        (root / STUDY / f"{rid}.json").write_text(
            json.dumps(summ, indent=1, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        typer.echo(f"{rid}: {summ['length_km']} km")


def routed(rid: str, seed: int = 1, root: Path = REPO_ROOT) -> tuple[dict[str, Any], pd.DataFrame]:
    run = root / RUNS / f"align-s{seed}" / rid
    return json.loads((run / "summary.json").read_text(encoding="utf-8")), pd.read_parquet(
        run / "profile.parquet"
    )


# --------------------------------------------------------------------------- running time
def curve_limits(
    prof: pd.DataFrame, line_speed: float, root: Path = REPO_ROOT
) -> list[tuple[float, float, float]]:
    """Curve speed limits on the joined path: radius recomputed over the whole path (so waypoint
    joins count), v = sqrt(R (E + I) / 11.8) (align.py, A-align-012), restrictions by align.restrictions."""
    from network import align

    w = align.load_weights(None, root)
    kl = align.line_class("hsr", w, root)
    lat0, lon0 = float(prof.lat.mean()), float(prof.lon.mean())
    t = align.to_xy(prof.lat.to_numpy(), prof.lon.to_numpy(), lat0, lon0)
    x, y = t.transform(prof.lon.to_numpy(), prof.lat.to_numpy())
    step = float(_v(w["profile"]["step_m"]))
    chord = int(round(float(_v(w["smoothing"]["chord_m"])) / step))
    R = align.radius_m(np.column_stack([x, y]), chord)
    v = np.minimum(line_speed, np.sqrt(np.maximum(R, 0) * kl.e_plus_i_mm / 11.8))
    df = pd.DataFrame({"s_km": prof.s_km.to_numpy(), "vmax_kmh": v})
    k = align.Klass("study", kl.cap, float(line_speed), kl.r_min_m, kl.e_plus_i_mm, kl.sf)
    return [(r["from_km"], r["to_km"], r["kmh"]) for r in align.restrictions(df, k, w)]


def line_run(
    c: dict[str, Any],
    summ: dict[str, Any],
    prof: pd.DataFrame,
    sc: dict[str, Any],
    root: Path = REPO_ROOT,
):
    from dataclasses import replace

    from access import running_time as rt

    classes = rt.load_yaml(rt.CLASSES, root)
    stock = rt.Stock.from_yaml(sc["stock"], classes["classes"][sc["stock"]])
    if sc.get("vmax_override_kmh"):
        stock = replace(stock, vmax_kmh=float(sc["vmax_override_kmh"]))
    st = (
        pd.DataFrame(
            [
                {
                    "id": s["id"],
                    "km_post": float(summ["station_km"][s["id"]]),
                    "class": s["class"],
                    "lat": s["lat"],
                    "lon": s["lon"],
                    "name_en": s["name_en"],
                }
                for s in c["stations"]
            ]
        )
        .sort_values("km_post")
        .reset_index(drop=True)
    )
    speed = float(sc["line_speed_kmh"])
    return rt.LineRun(
        c["id"], st, stock, speed, curve_limits(prof, min(speed, stock.vmax_kmh), root), 1.0
    )


def factor(root: Path = REPO_ROOT) -> dict[str, Any]:
    return json.loads((root / "runs/access/running_time/factors-s1/factors.json").read_text())[
        "generic"
    ]


def door_to_door(
    ivt: float, line_type: str, p: dict[str, Any], root: Path = REPO_ROOT
) -> dict[str, float]:
    acc = yaml.safe_load(
        (root / "cities/ksa/assumptions/access_network.yaml").read_text(encoding="utf-8")
    )
    hw = acc["hypothetical_service"]["headway_min"]
    headway = float(_v(hw.get(line_type, hw["default"])))
    D = p["door_to_door"]
    wait = min(headway / 2.0, float(_v(D["rail_wait"]["wait_cap_min"])))
    a, e = float(_v(D["rail_access_min"])), float(_v(D["rail_egress_min"]))
    return {
        "access_min": a,
        "wait_min": wait,
        "ivt_min": ivt,
        "egress_min": e,
        "total_min": a + wait + ivt + e,
        "headway_min": headway,
    }


def air_times(p: dict[str, Any]) -> dict[str, Any]:
    D = p["door_to_door"]
    B = D["air_block_model"]
    nodes = pd.read_parquet(REPO_ROOT / "cities/ksa/zones/economic_nodes.parquet").set_index(
        "node_id"
    )
    ruh, jed = nodes.loc["airport-ruh-king-khalid"], nodes.loc["airport-jed-king-abdulaziz"]
    km = float(haversine_km(ruh.lat, ruh.lon, jed.lat, jed.lon))
    block = float(B["fixed_min"]) + km / float(B["km_per_min"])
    bound = float(_v(D["air_airborne_bound_min"]))
    a, e = float(_v(D["air_access_min"])), float(_v(D["air_egress_min"]))
    lo_a, hi_a = D["air_access_min"]["range"]
    lo_e, hi_e = D["air_egress_min"]["range"]
    return {
        "airport_gc_km": round(km, 1),
        "block_model_min": round(block, 1),
        "airborne_bound_min": bound,
        "door_to_door_model_min": round(a + block + e, 1),
        "door_to_door_bound_min": round(a + bound + e, 1),
        "door_to_door_range_min": [round(lo_a + block + lo_e, 1), round(hi_a + bound + hi_e, 1)],
        "access_min": a,
        "egress_min": e,
    }


@app.command("times")
def times_cmd(seed: int = seed_option(), root: Path = typer.Option(REPO_ROOT, hidden=True)) -> None:
    """End-to-end and per-stop minutes for every route x speed class x stop pattern."""
    from access import running_time as rt

    p = params(root)
    f = factor(root)
    rows, stops_rows = [], []
    for rid, r in p["routes"].items():
        c = load_corridor(rid, root)
        summ, prof = routed(rid, seed, root)
        for sc in p["speed_classes"]:
            if r["line_type"] == "mixed" and float(sc["line_speed_kmh"]) > 250:
                continue  # the mixed (Landbridge-class) sketch is shown at its own 220/250 classes only
            run = line_run(c, summ, prof, sc, root)
            for pat, stops in (
                ("all-stop", r["stops"]),
                ("express", [r["stops"][0], r["stops"][-1]]),
            ):
                if pat == "express" and len(stops) == len(r["stops"]):
                    continue
                tab = rt.pair_table(run, stops)
                ivt = float(
                    tab.loc[(tab["from"] == stops[0]) & (tab.to == stops[-1]), "ivt_min"].iloc[0]
                )
                row = {
                    "route": rid,
                    "line_type": r["line_type"],
                    "speed_class": sc["id"],
                    "pattern": pat,
                    "stops": "|".join(stops),
                    "routed_km": summ["length_km"],
                    "kinematic_min": round(ivt, 2),
                    "p10_min": round(ivt * f["range"][0], 1),
                    "p50_min": round(ivt * f["value"], 1),
                    "p90_min": round(ivt * f["range"][1], 1),
                    "avg_kmh_p50": round(summ["length_km"] / (ivt * f["value"] / 60.0), 1),
                    "restricted_km": round(sum(b - a for a, b, _ in run.restrictions), 1),
                }
                d2d = door_to_door(ivt * f["value"], r["line_type"], p, root)
                row |= {"d2d_p50_min": round(d2d["total_min"], 1), "d2d_wait_min": d2d["wait_min"]}
                rows.append(row)
                if pat == "all-stop" and len(stops) > 2:
                    for s in rt.stop_costs(run, stops).itertuples():
                        stops_rows.append(
                            {
                                "route": rid,
                                "speed_class": sc["id"],
                                "station": s.station,
                                "stop_cost_kinematic_min": round(s.stop_cost_min, 2),
                                "stop_cost_p50_min": round(s.stop_cost_min * f["value"], 2),
                            }
                        )
    # the S1 Landbridge as it stands in R4 (landbridge.yaml chain x 1.029, 250 km/h, express)
    lb = rt.load_yaml(Path("cities/ksa/lines/landbridge.yaml"), root)
    run = rt.build_run(lb, root)
    for pat, stops in (("express", ["riyadh", "jeddah"]), ("all-stop", run.stations.id.tolist())):
        tab = rt.pair_table(run, stops)
        ivt = float(tab.loc[(tab["from"] == stops[0]) & (tab.to == stops[-1]), "ivt_min"].iloc[0])
        km = float(tab.loc[(tab["from"] == stops[0]) & (tab.to == stops[-1]), "km"].iloc[0])
        d2d = door_to_door(ivt * f["value"], "mixed", p, root)
        rows.append(
            {
                "route": "S1-landbridge (R4 as-is)",
                "line_type": "mixed",
                "speed_class": "250",
                "pattern": pat,
                "stops": "|".join(stops),
                "routed_km": round(km, 1),
                "kinematic_min": round(ivt, 2),
                "p10_min": round(ivt * f["range"][0], 1),
                "p50_min": round(ivt * f["value"], 1),
                "p90_min": round(ivt * f["range"][1], 1),
                "avg_kmh_p50": round(km / (ivt * f["value"] / 60.0), 1),
                "restricted_km": 0.0,
                "d2d_p50_min": round(d2d["total_min"], 1),
                "d2d_wait_min": d2d["wait_min"],
            }
        )
    df = pd.DataFrame(rows)
    E = p["envelope"]
    lo, hi = float(_v(E["lower_h"])) * 60, float(_v(E["upper_h"])) * 60
    df["within_2h_9h_p50"] = (df.p50_min >= lo) & (df.p50_min <= hi)
    df["below_2h_p10"] = df.p10_min < lo
    air = air_times(p)
    df["vs_air_d2d_model_min"] = (df.d2d_p50_min - air["door_to_door_model_min"]).round(1)
    d = root / RUNS / f"times-s{seed}"
    d.mkdir(parents=True, exist_ok=True)
    df.to_csv(d / "times.csv", index=False)
    pd.DataFrame(stops_rows).to_csv(d / "stop_costs.csv", index=False)
    # arithmetic reference only: average speeds the 2 h / 9 h bounds imply on the announced 900 km
    ref = {"km": 900, "source": "S-054", "avg_kmh_for_2h": 450.0, "avg_kmh_for_9h": 100.0}
    (d / "air.json").write_text(
        json.dumps({"air": air, "bounds_reference": ref, "factor": f}, indent=1) + "\n"
    )
    write_meta(
        d,
        seed,
        {"params": p, "factor": f},
        extra={"label": LABEL, "method": "access.running_time x generic factor (A-r4-rt-011)"},
    )
    typer.echo(
        df[
            [
                "route",
                "speed_class",
                "pattern",
                "routed_km",
                "kinematic_min",
                "p10_min",
                "p50_min",
                "p90_min",
                "d2d_p50_min",
            ]
        ].to_string()
    )
    typer.echo(json.dumps(air))


# --------------------------------------------------------------------------- costs
def costing_corridor(rid: str, seed: int = 1, root: Path = REPO_ROOT) -> dict[str, Any]:
    """Corridor dict in the shape network.evaluate.costing_input reads: stops only (waypoints are
    not stations), routed length, measured terrain and structure shares."""
    c = load_corridor(rid, root)
    summ, _ = routed(rid, seed, root)
    L = float(summ["length_km"])
    stations = [
        {**s, "km_post": float(summ["station_km"][s["id"]])}
        for s in c["stations"]
        if s["class"] != "waypoint"
    ]
    return {
        **c,
        "length_km": L,
        "stations": stations,
        "alignment": str(STUDY / f"{rid}.geojson"),
        "generated_from": "user-proposed (Tariq, 6 Nov 2026)",
        "rules_hash": "n/a (user-proposed)",
        "terrain_shares": summ["terrain_shares"],
        "structures_share": {
            "tunnel": round(summ["tunnel_km"] / L, 5),
            "viaduct": round(summ["viaduct_km"] / L, 5),
        },
        "alignment_routed": {"status": "routed", "profile_feasible": summ["profile_feasible"]},
    }


@app.command("costs")
def costs_cmd(
    seed: int = seed_option(),
    draws: int = typer.Option(10_000),
    root: Path = typer.Option(REPO_ROOT, hidden=True),
) -> None:
    """costs.estimate (cost register, reference-class uplifts) for every study route."""
    from network import evaluate as nev

    rows = []
    for rid in params(root)["routes"]:
        c = costing_corridor(rid, seed, root)
        spec, costing = nev.costing_input(c, root)
        spec["id"] = f"study-{rid.lower()}"  # LineSpec ids are lower-case
        d = root / RUNS / f"costs-s{seed}" / rid
        d.mkdir(parents=True, exist_ok=True)
        (d / "spec.yaml").write_text(
            yaml.safe_dump(spec, sort_keys=False, allow_unicode=True), encoding="utf-8"
        )
        (d / "costing.yaml").write_text(yaml.safe_dump(costing, sort_keys=False), encoding="utf-8")
        out = RUNS / f"costs-s{seed}" / rid / "estimate"
        subprocess.run(
            [
                "uv",
                "run",
                "python",
                "-m",
                "costs.estimate",
                "--corridor",
                str(d / "spec.yaml"),
                "--costing",
                str(d / "costing.yaml"),
                "--seed",
                str(seed),
                "--draws",
                str(draws),
                "--out",
                str(out),
            ],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        )
        rcf = yaml.safe_load((root / out / "rcf" / "summary.yaml").read_text(encoding="utf-8"))
        cap = rcf["capex"]
        summ, _ = routed(rid, seed, root)
        rows.append(
            {
                "route": rid,
                "line_type": c["line_type"],
                "routed_km": summ["length_km"],
                "tunnel_km": summ["tunnel_km"],
                "viaduct_km": summ["viaduct_km"],
                "earthworks_km": summ["earthworks_km"],
                "stations": len(spec["stations"]),
                **{f"base_{k.lower()}_sar_m": round(v, 0) for k, v in cap["base_estimate"].items()},
                **{f"uplifted_{k.lower()}_sar_m": round(v, 0) for k, v in cap["uplifted"].items()},
                "uplift_id": rcf["uplifts_used"]["capex"]["id"],
            }
        )
        typer.echo(
            f"{rid}: base P50 {cap['base_estimate']['P50']:.0f}, uplifted P50 {cap['uplifted']['P50']:.0f} SAR m"
        )
    df = pd.DataFrame(rows)
    d = root / RUNS / f"costs-s{seed}"
    df.to_csv(d / "capex.csv", index=False)
    write_meta(
        d,
        seed,
        {"draws": draws},
        extra={"label": LABEL, "method": "network.evaluate.costing_input + costs.estimate"},
    )


# --------------------------------------------------------------------------- scenarios, legs
@app.command("scenarios")
def scenarios_cmd(root: Path = typer.Option(REPO_ROOT, hidden=True)) -> None:
    """One study scenario per route: S1 plus that one user-proposed corridor (never combined)."""
    p = params(root)
    s1 = yaml.safe_load((root / "scenarios/S1.yaml").read_text(encoding="utf-8"))
    d = root / "scenarios/study"
    d.mkdir(parents=True, exist_ok=True)
    for rid, r in p["routes"].items():
        sc = {
            "id": f"S1-study-{rid.lower()}",
            "kind": "study_sketch",
            "label": "study sketch, not the recommended programme; not scored",
            "title": f"S1 + {rid}: {r['title']} (hypothetical, user-proposed)",
            "layer": "hypothetical (ours)",
            "layers": ["existing", "committed", "hypothetical"],
            "baseline": "S1",
            "lines": {"include": list(s1["lines"]["include"])},
            "candidates": [str(CORR / f"{rid}.yaml")],
            "alignment": str(STUDY / f"{rid}.geojson"),
            "notes": [
                STUDY_LABEL,
                "S1 (with the committed Landbridge) is unchanged; this sketch is drawn beside it, not instead of it.",
                "Not scored: the judge was not run. Not in the all-families layout.",
            ],
            "seed": 1,
            "labels": [LABEL],
            "source": "prompts/STUDY_RJ_FAMILIES.md item 3 (Tariq, 6 Nov 2026; CP7-6 user-proposed)",
        }
        head = (
            f"# Version: {rid.lower()}.yaml v1.0 | 6 Nov 2026 | Author: STUDY_RJ_FAMILIES | Status: draft\n"
            f"# Generated by `study.rj scenarios`; do not edit by hand. Label: {LABEL}.\n"
        )
        (d / f"{rid.lower()}.yaml").write_text(
            head + yaml.safe_dump(sc, sort_keys=False, allow_unicode=True), encoding="utf-8"
        )
        typer.echo(sc["id"])


@app.command("legs")
def legs_cmd(seed: int = seed_option(), root: Path = typer.Option(REPO_ROOT, hidden=True)) -> None:
    """Per-leg routed km, straight km, structures and ground levels of every route."""
    rows = []
    for rid in params(root)["routes"]:
        summ, prof = routed(rid, seed, root)
        km = prof.s_km.diff().fillna(0.0).to_numpy()
        for lg in summ["legs"]:
            m = (prof.leg == lg["leg"]).to_numpy()
            sub = prof[m]
            st = sub.structure.to_numpy()
            rows.append(
                {
                    "route": rid,
                    "from": lg["from"],
                    "to": lg["to"],
                    "straight_km": lg["straight_km"],
                    "routed_km": lg["routed_km"],
                    "detour_ratio": round(lg["routed_km"] / lg["straight_km"], 3),
                    "tunnel_km": round(float(km[m][st == "tunnel"].sum()), 2),
                    "viaduct_km": round(float(km[m][st == "viaduct"].sum()), 2),
                    "z_ground_start_m": round(float(sub.z_ground_m.iloc[0])),
                    "z_ground_end_m": round(float(sub.z_ground_m.iloc[-1])),
                    "z_ground_max_m": round(float(sub.z_ground_m.max())),
                }
            )
    d = root / RUNS / f"legs-s{seed}"
    d.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(rows)
    df.to_csv(d / "legs.csv", index=False)
    write_meta(d, seed, {}, extra={"label": LABEL})
    typer.echo(df.to_string())


# --------------------------------------------------------------------------- maps
FIG = Path("docs/study-rj")
ROUTE_COL = {
    "RJ-LB": "#7f7f7f",
    "RJ-A": "#1f77b4",
    "RJ-B": "#2ca02c",
    "RJ-C1": "#e07b00",
    "RJ-C2": "#8e44ad",
}


def _routed_geom(rid: str, root: Path):
    import geopandas as gpd

    g = gpd.read_file(root / STUDY / f"{rid}.geojson")
    return g[g["kind"] == "routed"]


def _footer(fig, text: str) -> None:
    fig.text(0.01, 0.01, text, fontsize=6.3, va="bottom", wrap=True)


def map_routes(root: Path, seed: int) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    from common import figures as cf

    p = params(root)
    cf.register_fonts()
    fig, ax = plt.subplots(figsize=(11, 7.6), dpi=110)
    handles = cf._base_layers(ax)
    for rid, _r in p["routes"].items():
        g = _routed_geom(rid, root)
        summ = json.loads((root / STUDY / f"{rid}.json").read_text())
        g.plot(ax=ax, color=ROUTE_COL[rid], lw=2.2, zorder=6, alpha=0.9)
        handles.append(
            Line2D(
                [],
                [],
                color=ROUTE_COL[rid],
                lw=2.2,
                label=f"hypothetical (ours): {rid} {summ['length_km']:.0f} km routed",
            )
        )
        for s in load_corridor(rid, root)["stations"]:
            if s["class"] == "waypoint":
                ax.scatter(s["lon"], s["lat"], marker="x", s=18, color="#555555", zorder=7)
            else:
                ax.scatter(
                    s["lon"],
                    s["lat"],
                    s=22,
                    color=ROUTE_COL[rid],
                    edgecolor="black",
                    lw=0.4,
                    zorder=8,
                )
    for pid, off in (
        ("riyadh", (4, 4)),
        ("jeddah", (-4, -10)),
        ("taif", (5, -8)),
        ("dawadmi", (0, 6)),
        ("muwai", (0, 6)),
        ("al-jumum", (-5, 6)),
        ("gateway-sw", (-6, -10)),
        ("gateway-nw", (-6, 5)),
    ):
        d = place(pid, p, root)
        ax.annotate(
            d["name_en"].split(" (")[0].split(",")[0],
            (d["lon"], d["lat"]),
            xytext=off,
            textcoords="offset points",
            fontsize=6.6,
            ha="right" if off[0] < 0 else "left",
            zorder=10,
            bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.7, "pad": 0.5},
        )
    handles.append(
        Line2D([], [], color="#555555", marker="x", ls="", label="routing waypoint (not a station)")
    )
    ax.set_xlim(38.7, 47.3)
    ax.set_ylim(20.7, 25.4)
    cf._aspect(ax, 23.0)
    ax.set_axis_off()
    cf._osm(ax)
    ax.legend(
        handles=handles,
        loc="lower right",
        bbox_to_anchor=(1.0, 0.05),
        fontsize=6.8,
        title="rail layers (never mixed)",
        title_fontsize=7.2,
        framealpha=0.9,
    )
    ax.set_title(
        "Riyadh-Jeddah study: user-proposed hypothetical routes, terrain-routed (frozen v1 weights)",
        fontsize=10,
    )
    _footer(
        fig,
        f"{LABEL}. Study sketches, not the recommended programme; not scored. The committed Landbridge (dashed) is S1 as it stands: "
        "a great-circle sketch through town-centroid proxies (terminals unpublished; C-002 open). RJ-LB is our terrain routing of the same proxies.\n"
        f"Alignment limitation: {ALIGNMENT_LIMITATION}.",
    )
    dest = root / FIG / "rj-routes-map.png"
    fig.savefig(dest, dpi=110, metadata={"Software": None})
    plt.close(fig)
    return dest


def map_siting(root: Path, seed: int) -> Path:
    import geopandas as gpd
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    from common import figures as cf

    p = params(root)
    mk = load_markers(root)
    cf.register_fonts()
    fig, ax = plt.subplots(figsize=(10.5, 7.8), dpi=110)
    hhr = gpd.read_file(root / "cities/ksa/lines/geojson/hhr.geojson")
    hhr.plot(ax=ax, color="black", lw=1.8, zorder=4)
    handles = [Line2D([], [], color="black", lw=1.8, label="existing: HHR (corrected geometry)")]
    hy = yaml.safe_load((root / "cities/ksa/lines/hhr.yaml").read_text(encoding="utf-8"))
    for s in hy["stations"]:
        if 21.1 < s["lat"] < 21.8:
            ax.scatter(s["lon"], s["lat"], s=30, marker="s", color="black", zorder=8)
            ax.annotate(
                f"hhr:{s['id']}",
                (s["lon"], s["lat"]),
                xytext=(4, -9),
                textcoords="offset points",
                fontsize=6.6,
                zorder=10,
            )
    ax.scatter(mk.lon, mk.lat, s=14, marker="^", color="#b00020", zorder=7)
    handles.append(
        Line2D(
            [],
            [],
            color="#b00020",
            marker="^",
            ls="",
            label=f"Haram boundary marker boards (OSM, {len(mk)}; points only, no official polygon)",
        )
    )
    for rid in p["routes"]:
        if rid == "RJ-LB":
            continue
        _routed_geom(rid, root).plot(ax=ax, color=ROUTE_COL[rid], lw=2.0, zorder=6)
        handles.append(
            Line2D(
                [],
                [],
                color=ROUTE_COL[rid],
                lw=2.0,
                label=f"hypothetical (ours): {rid} through alignment",
            )
        )
    _routed_geom("RJ-LB", root).plot(ax=ax, color=ROUTE_COL["RJ-LB"], lw=1.6, ls="--", zorder=5)
    handles.append(
        Line2D(
            [],
            [],
            color=ROUTE_COL["RJ-LB"],
            lw=1.6,
            ls="--",
            label="RJ-LB: announced proxies, terrain-routed by us",
        )
    )
    for pid, lab in (
        ("gateway-sw", "gateway SW (on HHR, outside)"),
        ("gateway-nw", "gateway NW (on HHR, outside)"),
        ("al-jumum", "Al-Jumum (announced stop, proxy)"),
        ("taif", "Taif"),
        ("jeddah", "Jeddah placeholder"),
    ):
        d = place(pid, p, root)
        ax.scatter(
            d["lon"],
            d["lat"],
            s=60,
            marker="o",
            facecolor="white",
            edgecolor="black",
            lw=1.2,
            zorder=9,
        )
        ax.annotate(
            lab,
            (d["lon"], d["lat"]),
            xytext=(5, 5),
            textcoords="offset points",
            fontsize=7,
            zorder=10,
            bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.75, "pad": 0.5},
        )
    handles.append(
        Line2D(
            [],
            [],
            color="black",
            marker="o",
            markerfacecolor="white",
            ls="",
            label="station site (study)",
        )
    )
    ax.set_xlim(39.1, 40.55)
    ax.set_ylim(21.1, 21.78)
    cf._aspect(ax, 21.4)
    ax.set_axis_off()
    cf._osm(ax)
    ax.legend(
        handles=handles,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.01),
        ncol=2,
        fontsize=6.8,
        framealpha=0.9,
    )
    ax.set_title(
        "Through Riyadh-Jeddah alignments relative to the Haram boundary (siting constraint)",
        fontsize=10,
    )
    _footer(
        fig,
        f"{LABEL}. Markers: OSM boundary=marker boards named as Haram-boundary boards in Arabic (S-rj-001); about 1,104 markers are reported in total (S-rj-002), "
        "no open official GIS boundary was found, and no polygon is drawn. RJ-B and RJ-C2 share the Taif leg. Check: every through-track point is farther out than the markers in its bearing sector, plus 2 km (A-rj-004).\n"
        f"Alignment limitation: {ALIGNMENT_LIMITATION}.",
    )
    dest = root / FIG / "rj-haram-siting.png"
    fig.savefig(dest, dpi=110, metadata={"Software": None})
    plt.close(fig)
    return dest


def chart_times(root: Path, seed: int) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    from common import figures as cf

    df = pd.read_csv(root / RUNS / f"times-s{seed}" / "times.csv")
    air = json.loads((root / RUNS / f"times-s{seed}" / "air.json").read_text())["air"]
    df = df[
        (df.pattern == "express")
        | ~df.route.isin(df[df.pattern == "express"].route.unique())
        | df.route.str.startswith("S1")
    ]
    df = df[~((df.route.str.startswith("S1")) & (df.pattern == "all-stop"))]
    cf.register_fonts()
    fig, ax = plt.subplots(figsize=(10, 7.4), dpi=110)
    labels = []
    for i, r in enumerate(df.itertuples()):
        col = ROUTE_COL.get(r.route, "#444444")
        ax.plot([r.p10_min / 60, r.p90_min / 60], [i, i], color=col, lw=1.2, alpha=0.6)
        ax.scatter(r.p50_min / 60, i, color=col, s=30, zorder=5)
        ax.scatter(
            r.d2d_p50_min / 60, i, marker="D", facecolor="white", edgecolor=col, s=26, zorder=5
        )
        ax.scatter(r.kinematic_min / 60, i, marker="|", color="black", s=40, zorder=5)
        labels.append(f"{r.route} @ {r.speed_class} km/h (non-stop, {r.routed_km:.0f} km)")
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=6.8)
    ax.invert_yaxis()
    for x, lab, ls in (
        (2, "2 h bound", ":"),
        (9, "9 h bound", ":"),
        (air["airborne_bound_min"] / 60, "air 1:50 airborne bound", "--"),
        (air["door_to_door_model_min"] / 60, "air door-to-door (model)", "-."),
    ):
        ax.axvline(x, color="#b00020" if "air" in lab else "black", ls=ls, lw=1)
        ax.text(
            x,
            0.01,
            lab,
            rotation=90,
            fontsize=6.5,
            va="bottom",
            ha="right",
            transform=ax.get_xaxis_transform(),
            bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.8, "pad": 0.5},
        )
    ax.set_xlim(1.5, 11.5)
    ax.set_xlabel("hours, Riyadh to Jeddah")
    ax.set_title(
        "Riyadh-Jeddah non-stop rail times: in-vehicle P50 (dot), P10-P90 (line), kinematic floor (|), door-to-door P50 (diamond)",
        fontsize=8.5,
    )
    _footer(
        fig,
        f"{LABEL}. Running times: R4 model (access.running_time) on the routed alignments x the generic timetable factor "
        "(A-r4-rt-011: 1.164 / 1.281 / 2.134). Door-to-door: access 20 + wait + egress 20 min (A-mode-028, A-access-010); air 60 + block + 30 min. "
        "Maglev and test records are reference only, not drawn as Saudi design cases.",
    )
    dest = root / FIG / "rj-travel-times.png"
    fig.subplots_adjust(left=0.33, bottom=0.12)
    fig.savefig(dest, dpi=110, metadata={"Software": None})
    plt.close(fig)
    return dest


@app.command("maps")
def maps_cmd(seed: int = seed_option(), root: Path = typer.Option(REPO_ROOT, hidden=True)) -> None:
    """Study figures under docs/study-rj/ (not in the R8 figure index)."""
    (root / FIG).mkdir(parents=True, exist_ok=True)
    for f in (map_routes, map_siting, chart_times):
        d = f(root, seed)
        typer.echo(f"{d.relative_to(root)} {d.stat().st_size / 1024:.0f} KB")


# --------------------------------------------------------------------------- summary
@app.command("summary")
def summary_cmd(
    seed: int = seed_option(), root: Path = typer.Option(REPO_ROOT, hidden=True)
) -> None:
    """Differences against RJ-A (speed-oriented) and RJ-LB: km, structures, capex, non-stop minutes."""
    cap = pd.read_csv(root / RUNS / f"costs-s{seed}" / "capex.csv").set_index("route")
    t = pd.read_csv(root / RUNS / f"times-s{seed}" / "times.csv", dtype={"speed_class": str})
    t = t[(t.pattern == "express") | ((t.pattern == "all-stop") & (t.stops.str.count("[|]") == 1))]
    out: dict[str, Any] = {"label": LABEL, "reference": "RJ-A", "routes": {}}
    for rid in cap.index:
        row = {}
        for ref in ("RJ-A", "RJ-LB"):
            d = {
                k: round(float(cap.at[rid, k] - cap.at[ref, k]), 1)
                for k in (
                    "routed_km",
                    "tunnel_km",
                    "viaduct_km",
                    "base_p50_sar_m",
                    "uplifted_p50_sar_m",
                )
            }
            d["base_p50_pct"] = round(
                100 * (cap.at[rid, "base_p50_sar_m"] / cap.at[ref, "base_p50_sar_m"] - 1), 1
            )
            row[f"vs_{ref}"] = d
        mins = {}
        for sc in t[t.route == rid].speed_class.unique():
            a = t[(t.route == "RJ-A") & (t.speed_class == sc)]
            b = t[(t.route == rid) & (t.speed_class == sc)]
            if len(a) and len(b):
                mins[sc] = round(float(b.p50_min.iloc[0] - a.p50_min.iloc[0]), 1)
        row["nonstop_p50_min_vs_RJ-A_by_speed"] = mins
        out["routes"][rid] = row
    # offset of each routed path from the towns it serves or passes (km, nearest path point)
    p = params(root)
    hy = yaml.safe_load((root / "cities/ksa/lines/hhr.yaml").read_text(encoding="utf-8"))
    mak = next(x for x in hy["stations"] if x["id"] == "makkah")
    towns = {
        k: (place(k, p, root)["lat"], place(k, p, root)["lon"])
        for k in ("riyadh", "dawadmi", "muwai", "taif", "al-jumum", "jeddah")
    }
    towns["hhr:makkah"] = (mak["lat"], mak["lon"])
    out["offsets_km"] = {}
    for rid in cap.index:
        _, prof = routed(rid, seed, root)
        out["offsets_km"][rid] = {
            k: round(float(haversine_km(prof.lat.to_numpy(), prof.lon.to_numpy(), la, lo).min()), 1)
            for k, (la, lo) in towns.items()
        }
    d = root / RUNS / f"summary-s{seed}"
    d.mkdir(parents=True, exist_ok=True)
    (d / "summary.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    write_meta(d, seed, {}, extra={"label": LABEL})
    typer.echo(json.dumps(out, indent=1))


# --------------------------------------------------------------------------- full-judge score
# STUDY_RJ_SCORE (Tariq, 6 Nov 2026): each package is S1* + one sketch, where S1* = S1 without the
# committed Landbridge. The omission lives only in study/rj_judge.py and only when its study
# replacement marker is present; optimise.layout's default "S1 + items" (R6, L1-L6) is untouched.
PACKAGES = {
    "replace-rj-a": "RJ-A",
    "replace-rj-b": "RJ-B",
    "replace-rj-c1": "RJ-C1",
    "replace-rj-c2": "RJ-C2",
    "replace-rj-lb": "RJ-LB",
}
SCORE = RUNS / "score"
S1_STAR = SCORE / "_s1-star"
SKIMS = SCORE / "_skims"
JUDGE = "v3-variants"
PHASE = 2030  # the first R6 investment phase (the announced Landbridge target is 2034, secondary)
OMIT = ("landbridge",)
MARKER_KEY = "study_rj_replace"
SCORE_LABEL = "study sketch, not the recommended programme"
S1_STAR_DEF = (
    "S1*: S1 without the committed Landbridge = existing lines (HHR, SAR North, SAR East) + "
    "Riyadh Rail Link + the Saudi GCC section"
)
SKIM_CHECK = (
    "21.27028,40.41583",
    "21.62117,39.69898",
    "21.51764,39.24536",
)  # Taif, Al-Jumum, Jeddah


def _key(lat: float, lon: float) -> str:
    return f"{round(float(lat), 5)},{round(float(lon), 5)}"


def score_corridor(rid: str, seed: int = 1, root: Path = REPO_ROOT) -> dict[str, Any]:
    """The corridor the judge scores for one sketch: stops only at their routed chainage (the
    sidecar's station_km; length = routed km, not the straight end-to-end distance), the curve
    speed limits recomputed on the joined path at the class line speed (the STUDY_RJ_FAMILIES §5
    method, `curve_limits`), and the terminals at the Landbridge's A-r4-acc-004 placements, which
    the access model applies to the same Riyadh/Jeddah centroid placeholders (the corridor files
    keep the placeholders; nothing is moved there)."""
    from access import running_time as rt

    c = costing_corridor(rid, seed, root)
    summ, prof = routed(rid, seed, root)
    cls = rt.load_yaml(rt.CLASSES, root)
    vmax = float(_v(cls["classes"][cls["by_line_type"][c["line_type"]]]["vmax_kmh"]))
    restr = curve_limits(prof, vmax, root)
    acc = yaml.safe_load((root / "cities/ksa/assumptions/access_network.yaml").read_text())
    sites = acc["station_sites"]["landbridge"]
    stations = []
    for s in c["stations"]:
        s = dict(s)
        o = sites.get(s["id"]) if s["class"] == "terminal" else None
        if o:
            s["placeholder_lat"], s["placeholder_lon"] = s["lat"], s["lon"]
            s["lat"], s["lon"] = float(o["lat"]), float(o["lon"])
            s["site_override"] = (
                "A-r4-acc-004: the Landbridge placement of the same placeholder "
                "(access_network.yaml station_sites.landbridge; access model unchanged)"
            )
        stations.append(s)
    return {
        **c,
        "stations": stations,
        "phase": PHASE,
        "alignment_routed": {
            "status": "routed",
            "profile_feasible": summ["profile_feasible"],
            "line_speed_kmh": vmax,
            "speed_restrictions": [
                {"from_km": round(a, 3), "to_km": round(b, 3), "kmh": round(v, 1)}
                for a, b, v in restr
            ],
            "source": f"{RUNS}/align-s{seed}/{rid} profile (STUDY_RJ_FAMILIES §5 curve_limits)",
        },
        "study_marker": MARKER_KEY,
        "label": LABEL,
        "study_label": SCORE_LABEL,
    }


def judge_python(root: Path = REPO_ROOT) -> str:
    return str(root / ".venv/bin/python")


def judge_env(root: Path, marker: Path | None = None) -> dict[str, str]:
    from optimise import judge as jd

    env = dict(os.environ, R6_JUDGE_ROOT=str(jd.judge_root(JUDGE, root)))
    env.pop("PYTHONPATH", None)
    env.pop("STUDY_RJ_MARKER", None)
    if marker is not None:
        env["STUDY_RJ_MARKER"] = str(marker.resolve())
    return env


def ivt_check(c: dict[str, Any], seed: int, root: Path = REPO_ROOT) -> dict[str, Any]:
    """End-to-end in-vehicle minutes of the scoring corridor through the R4 model (the judge's
    build_run path: routed chainage + curve limits, generic factor) vs the §5 times.csv row."""
    from access import running_time as rt

    run = rt.build_run(c, root)
    stops = run.stations.id.tolist()
    tab = rt.pair_table(run, stops)
    raw = float(tab.loc[(tab["from"] == stops[0]) & (tab.to == stops[-1]), "ivt_min"].iloc[0])
    f = float(factor(root)["value"])
    t = pd.read_csv(root / RUNS / f"times-s{seed}" / "times.csv", dtype={"speed_class": str})
    row = t[
        (t.route == c["id"])
        & (t.speed_class == str(int(c["alignment_routed"]["line_speed_kmh"])))
        & (t.pattern == "all-stop")
    ].iloc[0]
    return {
        "ivt_end_to_end_min": round(raw * f, 1),
        "generic_factor": f,
        "times_csv_p50_all_stop_min": float(row.p50_min),
        "speed_class": int(c["alignment_routed"]["line_speed_kmh"]),
        "stops": stops,
        "km": float(run.stations.km_post.iloc[-1]),
    }


@app.command("score-inputs")
def score_inputs_cmd(
    seed: int = seed_option(), root: Path = typer.Option(REPO_ROOT, hidden=True)
) -> None:
    """Scoring corridor, cost run (the judge's own costs.estimate on the study spec), layout and
    study replacement marker for every package; the station keys for the skim step."""
    from optimise import judge as jd

    jr = jd.judge_root(JUDGE, root)
    pts: dict[str, dict[str, float]] = {}
    for pid, rid in PACKAGES.items():
        d = root / SCORE / pid
        inp = d / "inputs"
        inp.mkdir(parents=True, exist_ok=True)
        c = score_corridor(rid, seed, root)
        (inp / f"{rid}.corridor.yaml").write_text(
            yaml.safe_dump(c, sort_keys=False, allow_unicode=True), encoding="utf-8"
        )
        for s in c["stations"]:
            pts[_key(s["lat"], s["lon"])] = {"lat": float(s["lat"]), "lon": float(s["lon"])}
        src = root / RUNS / f"costs-s{seed}" / rid
        for f in ("spec.yaml", "costing.yaml"):
            shutil.copyfile(src / f, inp / f)
        cost = (d / "cost").resolve()
        if not (cost / "rcf" / "distribution.parquet").exists():
            subprocess.run(
                [
                    judge_python(root),
                    "-m",
                    "costs.estimate",
                    "--corridor",
                    str((inp / "spec.yaml").resolve()),
                    "--costing",
                    str((inp / "costing.yaml").resolve()),
                    "--seed",
                    str(seed),
                    "--draws",
                    "10000",
                    "--out",
                    str(cost),
                ],
                cwd=jr,
                env=dict(judge_env(root), PYTHONPATH=str(jr)),
                check=True,
                capture_output=True,
                text=True,
            )
        a = pd.read_parquet(cost / "rcf" / "distribution.parquet")
        b = pd.read_parquet(
            root / RUNS / f"costs-s{seed}" / rid / "estimate" / "rcf" / "distribution.parquet"
        )
        same = a.shape == b.shape and bool((a.to_numpy() == b.to_numpy()).all())
        if not same:
            raise RuntimeError(f"{rid}: judge cost run differs from the study cost run")
        layout = {
            "id": pid,
            "layer": "hypothetical",
            "base": "S1-star",
            "label": LABEL,
            "corridors": [{"id": rid, "phase": PHASE}],
        }
        (inp / "layout.yaml").write_text(yaml.safe_dump(layout, sort_keys=False), encoding="utf-8")
        marker = {
            MARKER_KEY: {
                "package": pid,
                "sketch_id": rid,
                "omit_lines": list(OMIT),
                "corridor": str((inp / f"{rid}.corridor.yaml").resolve()),
                "skims": str((root / SKIMS).resolve()),
                "cost": {
                    "cost_run": str(cost),
                    "cost_spec": str((inp / "spec.yaml").resolve()),
                    "cost_costing": str((inp / "costing.yaml").resolve()),
                },
            },
            "label": LABEL,
        }
        (inp / "marker.yaml").write_text(yaml.safe_dump(marker, sort_keys=False), encoding="utf-8")
        chk = ivt_check(c, seed, root) | {"cost_run_identical_to_study": same}
        (inp / "check.json").write_text(json.dumps(chk, indent=1) + "\n", encoding="utf-8")
        typer.echo(f"{pid}: {json.dumps(chk)}")
    (root / SKIMS).mkdir(parents=True, exist_ok=True)
    (root / SKIMS / "stations.json").write_text(json.dumps(pts, indent=1) + "\n")


@app.command("score-skims")
def score_skims_cmd(root: Path = typer.Option(REPO_ROOT, hidden=True)) -> None:
    """Station skims for the study stops without one (judge's skim method; OSRM started and
    stopped by this command only)."""
    from optimise import judge as jd

    jr = jd.judge_root(JUDGE, root)
    r = subprocess.run(
        [
            judge_python(root),
            str(root / "study/rj_judge.py"),
            "skims",
            "--stations",
            str((root / SKIMS / "stations.json").resolve()),
            "--out",
            str((root / SKIMS).resolve()),
            "--check-keys",
            ";".join(SKIM_CHECK),
        ],
        cwd=jr,
        env=judge_env(root),
        capture_output=True,
        text=True,
    )
    (root / SKIMS / "skims.log").write_text(r.stdout + "\n" + r.stderr[-20000:])
    if r.returncode:
        raise RuntimeError(r.stderr[-1500:])
    write_meta(root / SKIMS, 1, {"check_keys": list(SKIM_CHECK)}, extra={"label": LABEL})
    typer.echo(r.stdout)


def _entry(cmd: list[str], marker: Path, root: Path, log: Path) -> None:
    from optimise import judge as jd

    r = subprocess.run(
        [judge_python(root), str(root / "study/rj_judge.py"), *cmd],
        cwd=jd.judge_root(JUDGE, root),
        env=judge_env(root, marker),
        capture_output=True,
        text=True,
    )
    log.write_text(r.stdout + "\n" + r.stderr[-20000:])
    if r.returncode:
        raise RuntimeError(f"{cmd[0]} failed: {r.stderr[-1500:]}")


def score_record(s: dict[str, Any], rid: str, nr: dict[str, Any]) -> dict[str, Any]:
    """Headline figures of one package, all incremental versus S1* (the judge's S1 column in these
    runs is S1*), in the shape of the scenario `score:` block."""
    ar = pd.DataFrame(s["appraisal_rows"])
    med = ar[(ar.population == "un_wpp_medium") & (ar.horizon == 60)]
    med = med[med.rate_case == "greenbook_2026"]
    by = s.get("by_line_2050_medium") or {}
    loads1 = s.get("loads_2050_medium_S1") or {}
    loads = s.get("loads_2050_medium") or {}
    pops = ("un_wpp_low", "un_wpp_medium", "un_wpp_high")
    r = lambda x: None if x is None else round(float(x), 1)  # noqa: E731
    return {
        "label": SCORE_LABEL,
        "labels": [LABEL],
        "baseline": "S1-star",
        "increment_vs": "S1* (S1 without the committed Landbridge), not published S1",
        "judge": f"{JUDGE} sha256 {s.get('_judge_sha256', '')}".strip(),
        "seed": s["seed"],
        "draws": s["draws"],
        "phase": PHASE,
        "robust_npv": r(s["robust_npv"]),
        "robust_case": s["robust_case"],
        "npv_at_p50_cost": {p: r(s["npv_at_p50_cost"][p]) for p in pops},
        "npv_at_p90_cost": {p: r(s["npv_at_p90_cost"][p]) for p in pops},
        "bcr_medium": {
            k: round(float(s[f"bcr_{k}"]["un_wpp_medium"]), 3) for k in ("p10", "p50", "p90")
        },
        "capex_sar_m": {k: r(v) for k, v in s["capex_sar_m"].items()},
        "rail_trips_2050_medium": r(s["rail_trips_2050_medium"]),
        "added_rail_trips_2050_medium": r(
            s["rail_trips_2050_medium"] - s["rail_trips_2050_medium_S1"]
        ),
        "rail_pkm_m_2050_medium": r(s["rail_pkm_m_2050_medium"]),
        "added_rail_pkm_m_2050_medium": r(
            s["rail_pkm_m_2050_medium"] - s["rail_pkm_m_2050_medium_S1"]
        ),
        "sketch_pax_2050_medium": r((by.get(rid) or {}).get("passengers")),
        "hhr_pax_2050_medium": r((loads.get("hhr") or {}).get("passengers")),
        "hhr_pax_2050_medium_S1_star": r((loads1.get("hhr") or {}).get("passengers")),
        "access_gain_120_five_metros": r(s.get("access_gain_120")),
        "access_gain_60_five_metros": r(s.get("access_gain_60")),
        "national_reach_gain_120_reported_only": r(nr["gain_vs_S1"]["120"]),
        "national_reach_120_reported_only": r(nr["population_2025_within_min"]["120"]),
        "co2_pv_p50_medium": r(med.pv_carbon_p50.iloc[0]),
        "units": "SAR million, 2025 prices, PV 2026; capex undiscounted, uplifted; trips per year",
    }


@app.command("score")
def score_cmd(
    seed: int = seed_option(),
    only: str = typer.Option("", help="comma-separated package ids (default: all five)"),
    root: Path = typer.Option(REPO_ROOT, hidden=True),
) -> None:
    """Full judge v3 (seed 1, 10,000 draws, --all-cases) for each package through the study entry,
    then the national reach (reported only) and the meta/score bookkeeping. Never writes
    runs/r6/."""
    from optimise import judge as jd
    from optimise import search as se

    rec = jd.load_record(JUDGE, root)
    for pid in [p for p in (only.split(",") if only else PACKAGES) if p]:
        rid = PACKAGES[pid]
        d = root / SCORE / pid
        inp = d / "inputs"
        marker = inp / "marker.yaml"
        jd.check_fingerprint(JUDGE, root)
        _entry(
            ["evaluate", "--layout", str((inp / "layout.yaml").resolve()), "--out",
             str(d.resolve()), "--workers", "4", "--seed", str(seed), "--draws", "10000",
             "--all-cases"],
            marker, root, d / "judge.log",
        )  # fmt: skip
        _entry(
            ["reach", "--layout", str((inp / "layout.yaml").resolve()), "--out",
             str((d / "national_reach.json").resolve()), "--reach-script",
             str(root / "optimise/reach.py")],
            marker, root, d / "reach.log",
        )  # fmt: skip
        jd.check_fingerprint(JUDGE, root)
        layout = yaml.safe_load((inp / "layout.yaml").read_text())
        write_meta(
            d,
            seed,
            {"layout": layout, "judge_args": ["--all-cases", "--draws", "10000"]},
            extra={
                "label": LABEL,
                "study_label": SCORE_LABEL,
                "judge": JUDGE,
                "judge_sha256": rec["sha256"],
                "judge_commit": rec["commit"],
                "judge_fingerprint_checked": True,
                "landbridge_omitted": True,
                "omitted_lines": list(OMIT),
                "study_marker": MARKER_KEY,
                "study_marker_file": str(marker.relative_to(root)),
                "baseline": S1_STAR_DEF,
                "layout_hash": se.layout_hash(layout),
                "layout_file": str((inp / "layout.yaml").relative_to(root)),
                "entry": "study/rj_judge.py",
            },
        )
        se.judge_meta_version(d, rec)
        sp, raw = d / "score.json", d / "score.judge.json"
        raw.write_bytes(sp.read_bytes())
        s = json.loads(raw.read_text())
        r = json.loads((d / "national_reach.json").read_text())
        lr = next(iter(r["layouts"].values()))
        s["national_reach_reported_only"] = {
            "note": "reported column only, never in the score (CP7-5, A-r6-104); "
            "added by study.rj score after the judge run; S1 here = S1*",
            "population_2025_within_min": {b: lr["layout"][b] for b in ("60", "120")},
            "S1_star_population_2025_within_min": {b: r["S1"][b] for b in ("60", "120")},
            "gain_vs_S1": lr["gain"],
            "within_120_with_access_cap": lr["layout"]["120_within_access_cap"],
            "population_total_2025": r["population_total_2025"],
        }
        s["study"] = {
            "label": SCORE_LABEL,
            "package": pid,
            "sketch": rid,
            "landbridge_omitted": True,
            "baseline": S1_STAR_DEF,
            "note": "every *_S1 field of this file is S1* (the judge's S1 line set without the "
            "Landbridge, study marker study_rj_replace); landbridge loads are None by construction",
        }
        s["_judge_sha256"] = rec["sha256"]
        s["score_record"] = score_record(s, rid, s["national_reach_reported_only"])
        sp.write_text(json.dumps(s, indent=1, default=float) + "\n")
        typer.echo(
            f"{pid}: robust NPV {s['robust_npv']:,.0f}; capex P50 {s['capex_sar_m']['capex_p50']:,.0f}"
        )


@app.command("score-summary")
def score_summary_cmd(
    seed: int = seed_option(), root: Path = typer.Option(REPO_ROOT, hidden=True)
) -> None:
    """runs/study/rj/score/_s1-star/ (the S1* reference values, identical across the five runs by
    construction: checked), score.csv, the judge capex vs §6 table, and the score: block of each
    replacement scenario file."""
    rows, ref = [], None
    cap6 = pd.read_csv(root / RUNS / f"costs-s{seed}" / "capex.csv").set_index("route")
    for pid, rid in PACKAGES.items():
        s = json.loads((root / SCORE / pid / "score.json").read_text())
        nr = s["national_reach_reported_only"]
        base = {
            "rail_trips_2050_medium": s["rail_trips_2050_medium_S1"],
            "rail_pkm_m_2050_medium": s["rail_pkm_m_2050_medium_S1"],
            "loads_2050_medium": s["loads_2050_medium_S1"],
            "five_metro_population_2025": s["accessibility"]["by_metro"]["S1"],
            "national_reach_2025": nr["S1_star_population_2025_within_min"],
        }
        if ref is None:
            ref = base
        elif json.dumps(base, sort_keys=True) != json.dumps(ref, sort_keys=True):
            raise RuntimeError(f"{pid}: S1* reference differs between runs")
        rec = s["score_record"]
        rows.append(
            {
                "package": pid,
                "sketch": rid,
                "line_type": yaml.safe_load(
                    (root / SCORE / pid / "inputs" / f"{rid}.corridor.yaml").read_text()
                )["line_type"],
                "routed_km": float(cap6.at[rid, "routed_km"]),
                "robust_npv": rec["robust_npv"],
                **{f"npv_p50cost_{p.split('_')[-1]}": v for p, v in rec["npv_at_p50_cost"].items()},
                **{f"npv_p90cost_{p.split('_')[-1]}": v for p, v in rec["npv_at_p90_cost"].items()},
                **{f"bcr_{k}_medium": v for k, v in rec["bcr_medium"].items()},
                **{k: v for k, v in rec["capex_sar_m"].items()},
                "study_s6_uplifted_p10": float(cap6.at[rid, "uplifted_p10_sar_m"]),
                "study_s6_uplifted_p50": float(cap6.at[rid, "uplifted_p50_sar_m"]),
                "study_s6_uplifted_p90": float(cap6.at[rid, "uplifted_p90_sar_m"]),
                "study_s6_base_p50": float(cap6.at[rid, "base_p50_sar_m"]),
                **{
                    k: rec[k]
                    for k in (
                        "added_rail_trips_2050_medium",
                        "added_rail_pkm_m_2050_medium",
                        "sketch_pax_2050_medium",
                        "hhr_pax_2050_medium",
                        "hhr_pax_2050_medium_S1_star",
                        "access_gain_120_five_metros",
                        "national_reach_gain_120_reported_only",
                        "co2_pv_p50_medium",
                    )
                },
            }
        )
    for row in rows:
        pd.DataFrame([row]).to_csv(root / SCORE / row["package"] / "scorecard.csv", index=False)
    out = root / S1_STAR
    out.mkdir(parents=True, exist_ok=True)
    (out / "s1_star.json").write_text(
        json.dumps(
            {
                "label": LABEL,
                "definition": S1_STAR_DEF,
                "how": "the judge's own S1 reference run inside each of the five package runs "
                "(study marker study_rj_replace: line set S1 without the Landbridge); identical "
                "across the five runs (checked by study.rj score-summary). No separate judge run "
                "was needed; no published S1 number is used.",
                "runs": [str(SCORE / p) for p in PACKAGES],
                **ref,
            },
            indent=1,
        )
        + "\n"
    )
    write_meta(out, seed, {"packages": list(PACKAGES)}, extra={"label": LABEL})
    df = pd.DataFrame(rows)
    df.to_csv(root / SCORE / "score.csv", index=False)
    for pid in PACKAGES:
        rec = json.loads((root / SCORE / pid / "score.json").read_text())["score_record"]
        f = root / "scenarios/study" / f"{pid}.yaml"
        txt = f.read_text(encoding="utf-8")
        head = "".join(ln + "\n" for ln in txt.splitlines() if ln.startswith("#"))
        sc = yaml.safe_load(txt)
        sc["score"] = rec | {"run": str(SCORE / pid)}
        f.write_text(
            head + yaml.safe_dump(sc, sort_keys=False, allow_unicode=True), encoding="utf-8"
        )
    typer.echo(df.to_string())


@app.command("score-scenarios")
def score_scenarios_cmd(root: Path = typer.Option(REPO_ROOT, hidden=True)) -> None:
    """One replacement scenario per sketch: S1* + that sketch instead of the committed Landbridge
    (the stacked rj-*.yaml files stay as they are: drawn beside, not instead; not scored)."""
    p = params(root)
    s1 = yaml.safe_load((root / "scenarios/S1.yaml").read_text(encoding="utf-8"))
    d = root / "scenarios/study"
    for pid, rid in PACKAGES.items():
        r = p["routes"][rid]
        f = d / f"{pid}.yaml"
        old = yaml.safe_load(f.read_text(encoding="utf-8")) if f.exists() else {}
        sc = {
            "id": f"S1-star-{pid}",
            "kind": "study_replacement",
            "label": SCORE_LABEL,
            "title": f"S1* + {rid} instead of the committed Landbridge: {r['title']} "
            "(hypothetical, user-proposed)",
            "layer": "hypothetical (ours)",
            "layers": ["existing", "committed", "hypothetical"],
            "baseline": "S1-star",
            "baseline_definition": S1_STAR_DEF,
            "lines": {"include": [x for x in s1["lines"]["include"] if x not in OMIT]},
            "replaces": list(OMIT),
            "study_marker": MARKER_KEY,
            "candidates": [str(CORR / f"{rid}.yaml")],
            "alignment": str(STUDY / f"{rid}.geojson"),
            "alignment_sidecar": str(STUDY / f"{rid}.json"),
            "corridors": [
                {
                    "id": rid,
                    "phase": PHASE,
                    "line_type": "hsr" if rid != "RJ-LB" else "mixed",
                    "track": "double",
                    "electrified": True,
                    "length": "routed km from the sidecar (not the corridor file's straight "
                    "end-to-end length_km)",
                }
            ],
            "notes": [
                STUDY_LABEL,
                "Replacement package: S1* plus this one sketch, opened in 2030 (the first R6 "
                "investment phase; the announced Landbridge target is 2034, secondary).",
                "S1.yaml and the committed Landbridge are unchanged; every published S1, L1-L5, "
                "S6-L6 and R8 figure is unchanged.",
                "Headline figures are increments versus S1*, not versus published S1, and are "
                "not the same kind of increment as L1-L5 (extras on top of S1 with the Landbridge).",
            ],
            "seed": 1,
            "labels": [LABEL],
            "source": "prompts/STUDY_RJ_SCORE.md (Tariq, 6 Nov 2026)",
        }
        if "score" in old:
            sc["score"] = old["score"]
        head = (
            f"# Version: {pid}.yaml v1.0 | 6 Nov 2026 | Author: STUDY_RJ_SCORE | Status: draft\n"
            f"# Generated by `study.rj score-scenarios` / `score-summary`; do not edit by hand. "
            f"Label: {LABEL}.\n"
        )
        f.write_text(
            head + yaml.safe_dump(sc, sort_keys=False, allow_unicode=True), encoding="utf-8"
        )
        typer.echo(sc["id"])


if __name__ == "__main__":
    app()
