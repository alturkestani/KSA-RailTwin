"""FIX_HHR_REROUTE: re-route the four corridors that had vertices in the old stitched-chord band.

FIX_HHR_JEDDAH rebuilt `hhr.geojson` as a MultiLineString (main line + KAIA branch) and found that
the old stitched LineString drew a 17.32 km city-to-airport chord that the corridor bonus
(A-align-029, `network.align.rail_mask`) treated as existing rail. This module re-routes only the
four corridors in that band, under the frozen v1 weights (hash checked before and after), and
reports what moved.

  uv run python -m network.reroute route   --seed 1   # runs/fix-hhr-reroute/align-s1/<id>
  uv run python -m network.reroute control --seed 1   # same, on the old stitched hhr.geojson
  uv run python -m network.reroute deltas  --seed 1   # deltas.csv/json + materiality verdicts
  uv run python -m network.reroute apply   --seed 1   # live sidecars (cities/ksa/alignments)

Outputs are hypothetical alignments (ours): indicative engineering sketches, not designs.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import typer
import yaml

from common import REPO_ROOT
from common.runmeta import seed_option, write_meta
from network import align

CONFIG = Path("cities/ksa/assumptions/reroute_thresholds.yaml")
OUT = Path("runs/fix-hhr-reroute")
STITCHED_REV = "0cc369e"  # hhr.geojson before FIX_HHR_JEDDAH (stitched LineString)
# S4-commuter_belt-jeddah-045 left the corridor set at R5 H4a (6318367); its live sidecar is the
# R4_ALIGN routing. Its corridor YAML is read from the commit before H4a.
REMOVED = {"S4-commuter_belt-jeddah-045": "6318367^"}
app = typer.Typer(
    add_completion=False, help="FIX_HHR_REROUTE: re-route the four chord-band corridors."
)


@app.callback()
def _group() -> None:
    """Re-route, control, deltas, apply."""


def _v(x: Any) -> Any:
    return x["value"] if isinstance(x, dict) and "value" in x else x


def load_config(root: Path = REPO_ROOT) -> dict[str, Any]:
    return yaml.safe_load((root / CONFIG).read_text(encoding="utf-8"))


def corridor_path(cid: str, root: Path) -> Path | None:
    hits = sorted((root / align.CORRIDORS).rglob(f"{cid}.yaml"))
    return hits[0] if hits else None


def load_corridor(cid: str, root: Path) -> tuple[dict[str, Any], str]:
    """The corridor YAML (live, or from git for a corridor that left the set) and its origin."""
    p = corridor_path(cid, root)
    if p is not None:
        return yaml.safe_load(p.read_text(encoding="utf-8")), p.relative_to(root).as_posix()
    rev = REMOVED[cid]
    fam = cid.split("-")[1]
    rel = f"{align.CORRIDORS.as_posix()}/{fam}/{cid}.yaml"
    text = subprocess.run(
        ["git", "show", f"{rev}:{rel}"], cwd=root, capture_output=True, text=True, check=True
    ).stdout
    dest = root / OUT / "corridors" / f"{cid}.yaml"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(text, encoding="utf-8")
    return yaml.safe_load(text), f"git {rev}:{rel}"


def frozen_hash(root: Path) -> str:
    return (root / align.WEIGHTS).with_suffix(".sha256").read_text().split()[0]


def check_weights(root: Path) -> str:
    w = align.load_weights(None, root)
    h = align.weights_hash(w)
    if not w.get("frozen") or h != frozen_hash(root):
        raise typer.BadParameter(f"weights not the frozen v1 set: {h}")
    return h


def _route(ids: list[str], out: Path, seed: int, root: Path) -> list[dict[str, Any]]:
    w = align.load_weights(None, root)
    rows = []
    for cid in ids:
        c, src = load_corridor(cid, root)
        s = align.write_outputs(c, align.route_corridor(c, w, root), w, out / cid, seed, root)
        rows.append({"id": cid, "corridor_yaml": src, "length_km": s["length_km"]})
        typer.echo(f"{cid}: {s['length_km']:.3f} km ({src})")
    return rows


@app.command("route")
def route_cmd(
    seed: int = seed_option(),
    only: str = typer.Option("", help="comma-separated subset of the four ids"),
    root: Path = typer.Option(REPO_ROOT, hidden=True),
) -> None:
    """Route the four under the frozen v1 weights on the corrected hhr.geojson; keep old ones."""
    cfg = load_config(root)
    ids = [x for x in cfg["corridors"] if not only or x in only.split(",")]
    h0 = check_weights(root)
    before = root / OUT / "before"
    before.mkdir(parents=True, exist_ok=True)
    for cid in ids:
        for ext in ("json", "geojson"):
            src = root / align.SIDECARS / f"{cid}.{ext}"
            dst = before / f"{cid}.{ext}"
            if not dst.exists():  # the first copy is the before state; never overwritten
                shutil.copyfile(src, dst)
    align._rail_geoms.cache_clear()
    out = root / OUT / f"align-s{seed}"
    rows = _route(ids, out, seed, root)
    h1 = check_weights(root)
    write_meta(
        out,
        seed,
        {"corridors": ids, "weights_hash": h0},
        extra={
            "label": align.LABEL,
            "weights_hash_before": h0,
            "weights_hash_after": h1,
            "weights_frozen_sha256": frozen_hash(root),
            "rail_layer_sha256": align.rail_layer_hashes(root),
            "routed": rows,
        },
    )


@app.command("control")
def control_cmd(
    seed: int = seed_option(),
    only: str = typer.Option("", help="comma-separated subset of the four ids"),
    root: Path = typer.Option(REPO_ROOT, hidden=True),
) -> None:
    """Control: route the four on the OLD stitched hhr.geojson (git 0cc369e) and byte-compare the
    result with the live (before) sidecars: the re-route delta comes from the HHR geometry alone."""
    from shapely.geometry import shape

    cfg = load_config(root)
    ids = [x for x in cfg["corridors"] if not only or x in only.split(",")]
    check_weights(root)
    rel = f"{align.LINES.as_posix()}/geojson/hhr.geojson"
    old = json.loads(
        subprocess.run(
            ["git", "show", f"{STITCHED_REV}:{rel}"],
            cwd=root,
            capture_output=True,
            text=True,
            check=True,
        ).stdout
    )
    live = align._rail_geoms(str(root))
    patched = dict(live) | {"hhr": shape(old["features"][0]["geometry"])}
    orig = align._rail_geoms
    align._rail_geoms = lambda root_s: patched  # type: ignore[assignment]
    try:
        out = root / OUT / f"control-stitched-s{seed}"
        _route(ids, out, seed, root)
    finally:
        align._rail_geoms = orig
    rows = []
    for cid in ids:
        sc = json.loads((root / OUT / "before" / f"{cid}.json").read_text(encoding="utf-8"))
        ref = root / sc["run"]
        same = {
            f: (out / cid / f).read_bytes() == (ref / f).read_bytes()
            for f in ("alignment.geojson", "summary.json", "profile.parquet")
        }
        ok = all(same.values())
        rows.append({"id": cid, "reference_run": sc["run"], **same, "identical": ok})
        typer.echo(f"{cid}: {'identical' if all(same.values()) else same} vs {sc['run']}")
    pd.DataFrame(rows).to_csv(out / "control.csv", index=False)
    write_meta(
        out,
        seed,
        {"corridors": ids, "stitched_rev": STITCHED_REV},
        extra={"label": align.LABEL, "control": rows},
    )


def _stitched_geoms(root: Path) -> dict[str, Any]:
    from shapely.geometry import shape

    rel = f"{align.LINES.as_posix()}/geojson/hhr.geojson"
    old = json.loads(
        subprocess.run(
            ["git", "show", f"{STITCHED_REV}:{rel}"],
            cwd=root,
            capture_output=True,
            text=True,
            check=True,
        ).stdout
    )
    return dict(align._rail_geoms(str(root))) | {"hhr": shape(old["features"][0]["geometry"])}


@app.command("band")
def band_cmd(
    seed: int = seed_option(),
    root: Path = typer.Option(REPO_ROOT, hidden=True),
) -> None:
    """Where the corridor flag (A-align-029: highway or rail, dilated by corridor_km) differs
    between the stitched and the corrected hhr.geojson, at the coarse and fine routing step, in a
    window around Jeddah; and how many cells of each routed path (before, after) fall in it."""
    w = align.load_weights(None, root)
    cfg = load_config(root)
    align._rail_geoms.cache_clear()
    new = align._rail_geoms(str(root))
    old = _stitched_geoms(root)
    bounds = (38.9, 21.2, 39.5, 22.0)  # Jeddah: covers the chord, the branch and the four exits
    orig = align._rail_geoms
    res: dict[str, Any] = {"bounds_wsen": bounds, "steps": {}}
    for name, arcsec in (("coarse", align._v(w["router"]["coarse_arcsec"])), ("fine", 3)):
        step = int(round(float(arcsec) / float(align._v(w["data"]["resolution_arcsec"]))))
        g = align.read_grid(bounds, step, root)
        flags = {}
        for tag, geoms in (("stitched", old), ("corrected", new)):
            align._rail_geoms = lambda root_s, _g=geoms: _g  # type: ignore[assignment]
            try:
                _, corr = align.penalty_surface(g, w, None, align.rail_mask(g, [], root))
                rail_only = align.rail_mask(g, [], root)
            finally:
                align._rail_geoms = orig
            flags[tag] = (corr, rail_only)
        diff = flags["stitched"][0] != flags["corrected"][0]
        rdiff = flags["stitched"][1] != flags["corrected"][1]
        row: dict[str, Any] = {
            "step_arcsec": float(arcsec),
            "rail_cells_changed": int(rdiff.sum()),
            "corridor_cells_changed": int(diff.sum()),
            "corridor_lost": int((flags["stitched"][0] & ~flags["corrected"][0]).sum()),
            "corridor_gained": int((~flags["stitched"][0] & flags["corrected"][0]).sum()),
            "paths": {},
        }
        for cid in cfg["corridors"]:
            for tag, run in (
                (
                    "before",
                    root / json.loads((root / OUT / "before" / f"{cid}.json").read_text())["run"],
                ),
                ("after", root / OUT / f"align-s{seed}" / cid),
            ):
                if not (run / "profile.parquet").exists():
                    continue
                df = pd.read_parquet(run / "profile.parquet")
                r, c = g.rc(df.lat.to_numpy(), df.lon.to_numpy())
                r, c = np.rint(r).astype(int), np.rint(c).astype(int)
                ok = (r >= 0) & (r < g.dem.shape[0]) & (c >= 0) & (c < g.dem.shape[1])
                cells = {(int(a), int(b)) for a, b in zip(r[ok], c[ok], strict=True)}
                row["paths"][f"{cid}:{tag}"] = {
                    "cells_in_window": len(cells),
                    "in_rail_change": sum(1 for a, b in cells if rdiff[a, b]),
                    "in_corridor_change": sum(1 for a, b in cells if diff[a, b]),
                }
        res["steps"][name] = row
        typer.echo(
            f"{name}: rail cells changed {row['rail_cells_changed']}, corridor-flag cells changed "
            f"{row['corridor_cells_changed']} (lost {row['corridor_lost']}, gained "
            f"{row['corridor_gained']})"
        )
        for k, v in row["paths"].items():
            typer.echo(f"  {k}: {v}")
    (root / OUT / "band-diff.json").write_text(json.dumps(res, indent=1) + "\n", encoding="utf-8")


# --------------------------------------------------------------------------- deltas
def _aeqd(lat0: float, lon0: float):
    from pyproj import Transformer

    return Transformer.from_crs(
        "EPSG:4326", f"+proj=aeqd +lat_0={lat0} +lon_0={lon0} +units=m +ellps=WGS84", always_xy=True
    )


def path_offsets(old: Any, new: Any, sample_m: float, moved_m: float) -> dict[str, float]:
    """Lateral offset of the new path from the old path (both lon/lat LineStrings), sampled along
    the new path every `sample_m` metres in a local azimuthal-equidistant projection."""
    c = new.centroid
    t = _aeqd(c.y, c.x)
    o = align._proj(t, old)
    n = align._proj(t, new)
    k = max(2, int(np.ceil(n.length / sample_m)) + 1)
    pts = [n.interpolate(d) for d in np.linspace(0.0, n.length, k)]
    d = np.array([o.distance(p) for p in pts])
    step_km = n.length / (k - 1) / 1000.0
    # reverse direction too (the old path's farthest point from the new one)
    k2 = max(2, int(np.ceil(o.length / sample_m)) + 1)
    d2 = np.array([n.distance(o.interpolate(x)) for x in np.linspace(0.0, o.length, k2)])
    return {
        "offset_mean_km": round(float(d.mean()) / 1000.0, 3),
        "offset_max_km": round(float(max(d.max(), d2.max())) / 1000.0, 3),
        "moved_km_over_500m": round(float((d > moved_m).sum() * step_km), 3),
    }


def routed_line(run: Path):
    from shapely.geometry import LineString

    df = pd.read_parquet(run / "profile.parquet")
    return LineString(np.column_stack([df.lon, df.lat]))


def run_minutes(c: dict[str, Any], root: Path) -> dict[str, float]:
    """End-to-end all-stop minutes, R4 running-time model (as network.evaluate summary)."""
    from access import running_time as rt

    res = {}
    for case in ("value", "low", "high"):
        run = rt.build_run(c, root, case)
        tab = rt.pair_table(run, run.stations.id.tolist())
        res[case] = float(tab.ivt_min.iloc[len(run.stations) - 2])
    return res


def material(b: dict[str, Any], a: dict[str, Any], cfg: dict[str, Any]) -> dict[str, Any]:
    m = cfg["material"]
    lr, sr = float(_v(m["length_rel"])), float(_v(m["structure_rel"]))
    out: dict[str, Any] = {}
    out["length"] = abs(a["length_km"] - b["length_km"]) / b["length_km"] > lr
    for k in ("tunnel_km", "viaduct_km", "earthworks_km"):
        d = abs(a[k] - b[k])
        out[k] = d / b[k] > sr if b[k] > 0 else d >= 0.001
    out["run_min"] = abs(a["run_min"] - b["run_min"]) > float(_v(m["run_min_abs"]))
    out["max_offset"] = a["offset_max_km"] > float(_v(m["max_offset_km"]))
    out["moved_materially"] = any(out.values())
    out["triggers"] = ",".join(k for k, v in out.items() if v is True and k != "moved_materially")
    return out


@app.command("deltas")
def deltas_cmd(
    seed: int = seed_option(),
    root: Path = typer.Option(REPO_ROOT, hidden=True),
) -> None:
    """Deltas old vs new per corridor + materiality verdicts (A-align-120..124)."""
    from screening.corridors import apply_alignment

    cfg = load_config(root)
    rep = cfg["reporting"]
    out = root / OUT
    rows = []
    for cid in cfg["corridors"]:
        b = json.loads((out / "before" / f"{cid}.json").read_text(encoding="utf-8"))
        a_run = out / f"align-s{seed}" / cid
        a = json.loads((a_run / "summary.json").read_text(encoding="utf-8"))
        c, src = load_corridor(cid, root)
        # the corridor YAML as the generator would write it from each sidecar
        tmp = out / "deltas-sidecars" / cid
        for tag, run in (("before", root / b["run"]), ("after", a_run)):
            d = tmp / tag
            d.mkdir(parents=True, exist_ok=True)
            sc = align.write_sidecar(c, run, d, root)
            sc["geojson"] = (
                b["geojson"] if tag == "before" else f"{align.SIDECARS.as_posix()}/{cid}.geojson"
            )
            (d / f"{cid}.json").write_text(json.dumps(sc, indent=1) + "\n", encoding="utf-8")
        cb = apply_alignment(c, tmp / "before")
        ca = apply_alignment(c, tmp / "after")
        rb, ra = run_minutes(cb, root), run_minutes(ca, root)
        off = path_offsets(
            routed_line(root / b["run"]),
            routed_line(a_run),
            float(_v(rep["sample_m"])),
            float(_v(rep["moved_m"])),
        )
        live = corridor_path(cid, root) is not None
        row: dict[str, Any] = {"id": cid, "corridor_yaml": src, "live_set": live}
        for k in ("length_km", "tunnel_km", "viaduct_km", "earthworks_km", "formation_max_grade"):
            row[f"{k}_before"] = b[k]
            row[f"{k}_after"] = a[k]
            row[f"{k}_delta"] = round(a[k] - b[k], 5)
        row["run_min_before"] = round(rb["value"], 3)
        row["run_min_after"] = round(ra["value"], 3)
        row["run_min_delta"] = round(ra["value"] - rb["value"], 3)
        row["run_min_range_after"] = f"{ra['low']:.2f}-{ra['high']:.2f}"
        row |= off
        v = material(
            {k: b[k] for k in ("length_km", "tunnel_km", "viaduct_km", "earthworks_km")}
            | {"run_min": rb["value"]},
            {k: a[k] for k in ("length_km", "tunnel_km", "viaduct_km", "earthworks_km")}
            | {"run_min": ra["value"], "offset_max_km": off["offset_max_km"]},
            cfg,
        )
        row["moved_materially"] = v["moved_materially"]
        row["triggers"] = v["triggers"]
        row["stations_km_before"] = json.dumps(b["station_km"])
        row["stations_km_after"] = json.dumps(a["station_km"])
        rows.append(row)
        typer.echo(
            f"{cid}: {row['length_km_before']:.3f} -> {row['length_km_after']:.3f} km, "
            f"run {row['run_min_delta']:+.3f} min, max offset {off['offset_max_km']} km, "
            f"material={v['moved_materially']} [{v['triggers']}]"
        )
    df = pd.DataFrame(rows)
    df.to_csv(out / "deltas.csv", index=False)
    (out / "deltas.json").write_text(json.dumps(rows, indent=1) + "\n", encoding="utf-8")
    write_meta(
        out / "deltas-meta",
        seed,
        cfg,
        extra={"label": align.LABEL, "weights_hash": check_weights(root), "n": len(rows)},
    )


FIGURES = Path("docs/report/figures")
CHORD_BOX = (39.10, 21.45, 39.30, 21.70)  # w, s, e, n around the old KAIA -> Al-Sulaimaniyah chord
MAP_MAX_E = 39.90  # Riyadh-Jeddah: show the Jeddah end only (where the chord was)


def map_extent(geojson: Path) -> tuple[float, float, float, float]:
    """Window: the routed corridor's bounding box (cut at MAP_MAX_E) joined with the chord box,
    padded by 0.05 degrees."""
    d = json.loads(geojson.read_text(encoding="utf-8"))
    rc = next(f for f in d["features"] if f["properties"].get("kind") == "routed")
    xs = [p[0] for p in rc["geometry"]["coordinates"] if p[0] <= MAP_MAX_E]
    ys = [p[1] for p in rc["geometry"]["coordinates"] if p[0] <= MAP_MAX_E]
    w, s, e, n = CHORD_BOX
    pad = 0.05
    return (
        round(min(w, *xs) - pad, 3),
        round(min(s, *ys) - pad, 3),
        round(min(MAP_MAX_E, max(e, *xs) + pad), 3),
        round(max(n, *ys) + pad, 3),
    )


@app.command("maps")
def maps_cmd(root: Path = typer.Option(REPO_ROOT, hidden=True)) -> None:
    """docs/report/figures/reroute-<id>-before.png / -after.png: the old stitched HHR with the
    previous sidecar, and the corrected HHR with the live sidecar (map code: common.figures
    jeddah_hhr_map, as hhr-jeddah-before/-after)."""
    from common.figures import jeddah_hhr_map

    cfg = load_config(root)
    stitched = root / OUT / f"hhr-stitched-{STITCHED_REV}.geojson"
    rel = f"{align.LINES.as_posix()}/geojson/hhr.geojson"
    stitched.write_text(
        subprocess.run(
            ["git", "show", f"{STITCHED_REV}:{rel}"],
            cwd=root,
            capture_output=True,
            text=True,
            check=True,
        ).stdout,
        encoding="utf-8",
    )
    rows = []
    for cid in cfg["corridors"]:
        before = (OUT / "before" / f"{cid}.geojson").as_posix()
        after = (align.SIDECARS / f"{cid}.geojson").as_posix()
        ext = map_extent(root / after)
        for tag, hhr, cor in (
            ("before", (OUT / stitched.name).as_posix(), before),
            ("after", rel, after),
        ):
            hhr_name = "old stitched HHR (0cc369e)" if tag == "before" else "corrected HHR"
            title = f"{cid}: {tag} the re-route ({hhr_name}; frozen v1 weights)"
            png = FIGURES / f"reroute-{cid}-{tag}.png"
            r = jeddah_hhr_map(Path(hhr), png, title, Path(cor), ext)
            rows.append({"id": cid, "map": tag, "png": png.as_posix(), "extent": ext, **r})
            typer.echo(f"{png}: {(root / png).stat().st_size / 1e3:.0f} KB")
    (root / OUT / "maps.json").write_text(json.dumps(rows, indent=1) + "\n", encoding="utf-8")


@app.command("apply")
def apply_cmd(
    seed: int = seed_option(),
    root: Path = typer.Option(REPO_ROOT, hidden=True),
) -> None:
    """Write the live sidecars cities/ksa/alignments/<id>.{json,geojson} for the four (only those)
    from runs/fix-hhr-reroute/align-s<seed>, and refresh the four rows of summary.csv."""
    cfg = load_config(root)
    check_weights(root)
    dest = root / align.SIDECARS
    runs = root / OUT / f"align-s{seed}"
    summ = pd.read_csv(dest / "summary.csv")
    for cid in cfg["corridors"]:
        c, _ = load_corridor(cid, root)
        sm = align.write_sidecar(c, runs / cid, dest, root)
        if cid in set(summ.id):
            i = summ.index[summ.id == cid][0]
            for k in summ.columns:
                if k in sm:
                    summ.at[i, k] = sm[k]
        typer.echo(f"{cid}: sidecar {sm['length_km']:.3f} km")
    summ.to_csv(dest / "summary.csv", index=False)


if __name__ == "__main__":
    app()
