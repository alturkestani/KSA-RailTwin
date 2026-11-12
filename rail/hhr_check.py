"""FIX_HHR_JEDDAH: before/after check of the HHR alignment fix and of what read the old geometry.

Before = `cities/ksa/lines/geojson/hhr.geojson` at a git revision (the stitched LineString);
after = the working-tree file (main line + KAIA branch, MultiLineString). Nothing published is
re-run: the R4_ALIGN routed profiles in `runs/align/*/hhr/profile.parquet` are compared again with
`network.align.compare` against both geometries, and the settlement and station-addition
distances are recomputed with both.

CLI:
  uv run python -m rail.hhr_check --before-rev 0cc369e --out runs/fix-hhr/check.json
"""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import typer
import yaml
from shapely.geometry import shape

from common import REPO_ROOT
from rail.osm import haversine_km

HHR = Path("cities/ksa/lines/geojson/hhr.geojson")
GEOJSON = Path("cities/ksa/lines/geojson")
JUMP_KM = 2.0

app = typer.Typer(add_completion=False, help="HHR geometry fix: before/after check.")


def _km(c: list) -> float:
    return sum(haversine_km(a[1], a[0], b[1], b[0]) for a, b in zip(c, c[1:], strict=False))


def parts_of(geom: dict) -> list[list]:
    return [geom["coordinates"]] if geom["type"] == "LineString" else list(geom["coordinates"])


def geometry_table(fc: dict) -> dict[str, Any]:
    f = fc["features"][0]
    parts = parts_of(f["geometry"])
    names = f["properties"].get("parts") or ["main"]
    out: dict[str, Any] = {"type": f["geometry"]["type"], "parts": []}
    for name, c in zip(names, parts, strict=True):
        segs = [haversine_km(a[1], a[0], b[1], b[0]) for a, b in zip(c, c[1:], strict=False)]
        seen: dict[tuple, int] = {}
        dups = []
        for i, p in enumerate(c):
            if tuple(p) in seen:
                dups.append((seen[tuple(p)], i))
            seen.setdefault(tuple(p), i)
        out["parts"].append(
            {
                "part": name,
                "vertices": len(c),
                "km": round(_km(c), 2),
                "first": c[0],
                "last": c[-1],
                "segments_over_2km": sum(s > JUMP_KM for s in segs),
                "max_segment": max(
                    (
                        {"index": i, "km": round(s, 2), "from": c[i], "to": c[i + 1]}
                        for i, s in enumerate(segs)
                    ),
                    key=lambda d: d["km"],
                ),
                "repeated_vertices": len(dups),
                "first_repeat": dups[0] if dups else None,
            }
        )
    out["total_km"] = round(sum(p["km"] for p in out["parts"]), 2)
    return out


def stitch_jumps(c: list, min_km: float = 5.0) -> list[dict]:
    """Segments longer than min_km whose end vertex re-enters an already drawn stretch (a stitch,
    as opposed to a long straight OSM way)."""
    seen = {tuple(p): i for i, p in reversed(list(enumerate(c)))}
    out = []
    for i, (a, b) in enumerate(zip(c, c[1:], strict=False)):
        km = haversine_km(a[1], a[0], b[1], b[0])
        later_repeat = any(
            seen.get(tuple(p), j) < j for j, p in enumerate(c[i + 1 : i + 60], i + 1)
        )
        if km > min_km and later_repeat:
            out.append({"index": i, "km": round(km, 2), "from": a, "to": b})
    return out


def _main_geom(fc: dict):
    g = shape(fc["features"][0]["geometry"])
    return g if g.geom_type == "LineString" else g.geoms[0]


def validation_rows(root: Path, before: dict, after: dict) -> list[dict]:
    from network import align as al

    line = yaml.safe_load((root / "cities/ksa/lines/hhr.yaml").read_text(encoding="utf-8"))
    kp = [float(s["km_post"]) for s in line["stations"]]
    ref = round(max(kp) - min(kp), 3)
    rows = []
    for pp in sorted((root / "runs/align").glob("validation*/**/hhr/profile.parquet")):
        run = pp.parent.parent
        prof = pd.read_parquet(pp)
        pub = pd.read_csv(run / "validation.csv").set_index("line").loc["hhr"].to_dict()
        for tag, fc in (("before", before), ("after", after)):
            props = fc["features"][0]["properties"]
            m = al.compare(prof, _main_geom(fc), props.get("alignment_km"), ref)
            rows.append({"run": str(run.relative_to(root / "runs/align")), "geometry": tag, **m})
        rows.append(
            {
                "run": str(run.relative_to(root / "runs/align")),
                "geometry": "after_with_branch",
                **compare_multi(prof, after),
            }
        )
        rows.append(
            {
                "run": str(run.relative_to(root / "runs/align")),
                "geometry": "published",
                **{k: pub.get(k) for k in m},
            }
        )
    return rows


def compare_multi(routed: pd.DataFrame, fc: dict, n: int = 2000) -> dict[str, float]:
    """`network.align.compare` offsets against main line + branch: the main part is clipped between
    the projections of the routed end points as in `compare`; the branch is added whole (the routed
    validation line visits KAIA, so its OSM counterpart includes the branch)."""
    from shapely.geometry import LineString, MultiLineString, Point
    from shapely.ops import substring

    from network import align as al

    g = shape(fc["features"][0]["geometry"])
    lat0, lon0 = float(routed.lat.mean()), float(routed.lon.mean())
    t = al.to_xy(np.zeros(1), np.zeros(1), lat0, lon0)
    rl = LineString(np.column_stack(t.transform(routed.lon.to_numpy(), routed.lat.to_numpy())))
    main, *branches = [al._proj(t, p) for p in g.geoms]
    a, b = main.project(Point(rl.coords[0])), main.project(Point(rl.coords[-1]))
    main = substring(main, min(a, b), max(a, b))
    ol = MultiLineString([main, *branches])
    pr = [rl.interpolate(d) for d in np.linspace(0, rl.length, n)]
    po = [
        part.interpolate(d)
        for part in ol.geoms
        for d in np.linspace(0, part.length, max(2, int(n * part.length / ol.length)))
    ]
    d_ro = np.array([ol.distance(p) for p in pr]) / 1000
    d_or = np.array([rl.distance(p) for p in po]) / 1000
    return {
        "osm_km_clipped": round(ol.length / 1000, 3),
        "hausdorff_km": round(float(max(d_ro.max(), d_or.max())), 3),
        "mean_offset_km": round(float(0.5 * (d_ro.mean() + d_or.mean())), 3),
        "mean_offset_routed_to_osm_km": round(float(d_ro.mean()), 3),
        "p90_offset_km": round(float(np.percentile(np.concatenate([d_ro, d_or]), 90)), 3),
    }


def structures(root: Path, before: dict, after: dict) -> dict[str, dict]:
    """OSM bridge/tunnel km within 50 m (`network.align.osm_structures`): the published run used
    the whole stitched LineString; after = main part only and main + branch."""
    from network import align as al

    return {
        "before": al.osm_structures("hhr", shape(before["features"][0]["geometry"]), root),
        "after_main": al.osm_structures("hhr", _main_geom(after), root),
        "after_with_branch": al.osm_structures(
            "hhr", shape(after["features"][0]["geometry"]), root
        ),
    }


def _root_with(root: Path, fc: dict, tmp: Path) -> Path:
    (tmp / GEOJSON).mkdir(parents=True)
    for p in (root / GEOJSON).glob("*.geojson"):
        shutil.copy(p, tmp / GEOJSON / p.name)
    (tmp / HHR).write_text(json.dumps(fc), encoding="utf-8")
    return tmp


def settlement_distances(root: Path, before: dict, after: dict) -> dict[str, Any]:
    from network import distances as nd

    params = yaml.safe_load((root / nd.PARAMS).read_text(encoding="utf-8"))
    step = float(params["densify_km"]["value"])
    df = pd.read_parquet(root / nd.SETTLEMENTS)
    pts = df[["lat", "lon"]].astype(float)
    out: dict[str, Any] = {"rows": len(df)}
    with tempfile.TemporaryDirectory() as td:
        for prefix, key in (
            ("existing_line", "intercity_lines"),
            ("existing_any_line", "existing_all_lines"),
        ):
            ids = params[key]["value"]
            res = {}
            for tag, fc in (("before", before), ("after", after)):
                r = _root_with(root, fc, Path(td) / f"{prefix}-{tag}")
                km, nid = nd.gc_nearest(pts, nd.line_vertices(r, ids, step))
                res[tag] = (np.round(km, 2), nid)
            pub = df[f"dist_{prefix}_km"].to_numpy(float)
            changed = np.flatnonzero(np.abs(res["before"][0] - res["after"][0]) > 0.005)
            out[prefix] = {
                "published_equals_before": int(np.sum(np.abs(pub - res["before"][0]) <= 0.005)),
                "published_equals_after": int(np.sum(np.abs(pub - res["after"][0]) <= 0.005)),
                "rows_changed": len(changed),
                "changed": [
                    {
                        "osm_id": int(df.osm_id.iloc[i]),
                        "name": str(df.get("name_en", df.get("name")).iloc[i]),
                        "before_km": float(res["before"][0][i]),
                        "after_km": float(res["after"][0][i]),
                        "nearest_before": str(res["before"][1][i]),
                        "nearest_after": str(res["after"][1][i]),
                    }
                    for i in changed
                ],
            }
    return out


def station_addition_distances(root: Path, before: dict, after: dict) -> dict[str, Any]:
    """S5 station-addition test (A-corr-011): town-to-alignment distance for every register row
    within 25 km of HHR, before and after."""
    from screening.corridors import point_line_km

    rules = yaml.safe_load(
        (root / "cities/ksa/assumptions/corridor_rules.yaml").read_text(encoding="utf-8")
    )
    max_line = float(rules["station_additions"]["max_line_km"]["value"])
    reg = pd.read_parquet(root / "cities/ksa/candidates.parquet")
    pb = parts_of(before["features"][0]["geometry"])
    pa = parts_of(after["features"][0]["geometry"])
    rows = []
    for r in reg.itertuples():
        b = min(point_line_km(r.lat, r.lon, p) for p in pb)
        a = min(point_line_km(r.lat, r.lon, p) for p in pa)
        if min(a, b) <= 25 and abs(a - b) > 0.005:
            rows.append(
                {
                    "row_key": r.row_key,
                    "name": r.name_en,
                    "before_km": round(b, 2),
                    "after_km": round(a, 2),
                    "crosses_max_line": (b <= max_line) != (a <= max_line),
                }
            )
    return {"max_line_km": max_line, "register_rows": len(reg), "changed_within_25km": rows}


@app.command()
def main(
    before_rev: str = typer.Option("0cc369e", help="git revision holding the stitched file"),
    out: Path = typer.Option(Path("runs/fix-hhr/check.json")),
    with_structures: bool = typer.Option(True),
    root: Path = typer.Option(REPO_ROOT, hidden=True),
) -> None:
    txt = subprocess.run(
        ["git", "show", f"{before_rev}:{HHR}"], cwd=root, capture_output=True, text=True, check=True
    ).stdout
    before = json.loads(txt)
    after = json.loads((root / HHR).read_text(encoding="utf-8"))
    res: dict[str, Any] = {
        "before_rev": before_rev,
        "geometry": {"before": geometry_table(before), "after": geometry_table(after)},
        "stitches": {
            "before": stitch_jumps(parts_of(before["features"][0]["geometry"])[0]),
            "after": [
                j for p in parts_of(after["features"][0]["geometry"]) for j in stitch_jumps(p)
            ],
        },
        "validation": validation_rows(root, before, after),
        "settlements": settlement_distances(root, before, after),
        "station_additions": station_addition_distances(root, before, after),
    }
    if with_structures:
        res["structures"] = structures(root, before, after)
    o = out if out.is_absolute() else root / out
    o.parent.mkdir(parents=True, exist_ok=True)
    o.write_text(
        json.dumps(res, indent=1, ensure_ascii=False, default=str) + "\n", encoding="utf-8"
    )
    typer.echo(json.dumps(res, indent=1, ensure_ascii=False, default=str)[:6000])


if __name__ == "__main__":
    app()
