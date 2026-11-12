"""Main-cut choreography for the moving-map renderer (BUILD_MOVIE): the 58 `cut: main` shots.

film/sim.py holds the engine and the 11 trailer scenes (unchanged, byte-reproducible); this module
adds one Scene per main shot (sh-01-01 ... sh-08-14) in the same style: every frame drawn over the
Copernicus relief, the twin's own GeoJSON, a moving camera, trains as comets, pulses and range bars.
sim.scene_for() looks a shot up in the trailer scenes first, then here (lazy import, no cycle).

Rules kept here (BUILD_MOVIE, CLAUDE.md):
- every scene has a legend and the OSM + Copernicus credit bar (`credits_bar=True`), titles too;
- chart quantities are drawn as geometry read from the shot's data_source files at build time
  (run outputs under RAILTWIN_RUNS_ROOT, the cost register, the source registers); chart labels
  carry words, not numbers; the caption carries the figures;
- moving trains, seats and particles are illustrative (A-film-015), never timetables;
- the closing notice appears only on sh-08-14, inside the credits roll (sim.roll_html);
- determinism: no randomness except the seeded generator in ctx;
- FIX_FILM_STORY (Tariq, 10 Nov 2026): money is shown as a benefit-to-cost bar (riyals back per
  riyal spent, P10-P90 with the middle marked) beside a bold line at 1 ("pays back its cost"),
  never as a net-present-value range; sh-08-15..20 show the north and south on the S6-L6
  connected comparison layout along its DEM least-cost alignments (never straight lines).

CLI (still frames through the same per-frame code path as film.render):
  uv run python -m film.sim_main frame sh-02-05 --lang ar --f 0.7 --out /tmp/bm/frames/x.png
  uv run python -m film.sim_main frames --lang ar --f 0.7 --outdir /tmp/bm/frames
"""

from __future__ import annotations

import csv
import json
import math
import re
from pathlib import Path

import numpy as np
import pandas as pd
import typer
import yaml
from PIL import Image

from common import REPO_ROOT
from film import render as R
from film import sim
from film.sim import (
    DASH_PX,
    PAL,
    Cam,
    Canvas,
    Data,
    Inset,
    Scene,
    arc,
    at,
    base_network,
    chain,
    comet,
    ease,
    fr,
    load_layer,
    load_lines,
    partial,
    pulse,
    runs_file,
    town,
    world,
    world_px,
)

EC = ("existing", "committed")
ECH = ("existing", "committed", "hypothetical")
EH = ("existing", "hypothetical")
PANEL = (7, 11, 20)
GREY = (150, 156, 168)
ROAD = (176, 170, 160)
TUNNEL = (14, 12, 22)  # tunnels: dark core inside the hypothetical line (sh-06-03)
BAR = (214, 186, 132)
GATE = (184, 130, 51)  # a muted warm bar (the glow pass blooms bright fills)
NAT = Cam(44.6, 23.6, 72)  # chart backdrop (as the trailer charts)
NAT_SIDE = Cam(45.1, 24.2, 60)  # the whole Kingdom beside a side caption
NAT_LOW = Cam(45.0, 23.4, 56)  # the whole Kingdom above a bottom caption


# ---------------------------------------------------------------- data helpers


def reg_value(sid: str) -> str:
    """The `value` column of a source-register row (docs/sources/*.csv)."""
    for p in sorted((REPO_ROOT / "docs/sources").glob("*.csv")):
        with p.open(encoding="utf-8", newline="") as fh:
            for r in csv.DictReader(fh):
                if r.get("id") == sid:
                    return str(r.get("value", ""))
    raise KeyError(sid)


def numbers(text: str) -> list[float]:
    """Numbers in a register value, in order ('32,175,224' -> 32175224; '35.3 million')."""
    out = []
    for m in re.finditer(r"([+-]?\d[\d,]*(?:\.\d+)?)\s*(million|billion)?", text):
        v = float(m.group(1).replace(",", ""))
        v *= {"million": 1e6, "billion": 1e9}.get(m.group(2) or "", 1.0)
        out.append(v)
    return out


def geo_points(path: Path) -> list[tuple[dict, tuple[float, float]]]:
    d = json.loads(path.read_text(encoding="utf-8"))
    return [
        (f["properties"], tuple(f["geometry"]["coordinates"][:2]))
        for f in d["features"]
        if (f.get("geometry") or {}).get("type") == "Point"
    ]


def stations(prefix: str = "", layers: tuple[str, ...] = ()) -> list[tuple[dict, np.ndarray]]:
    out = []
    for props, xy in geo_points(REPO_ROOT / "cities/ksa/lines/stations.geojson"):
        if prefix and not str(props.get("line_id", "")).startswith(prefix):
            continue
        if layers and props.get("layer") not in layers:
            continue
        out.append((props, world(np.array(xy))[0]))
    return out


def polygons(path: Path) -> list[np.ndarray]:
    """Outer rings of a (Multi)Polygon GeoJSON, in world coordinates."""
    out = []
    for _, g in R._geoms(path):
        polys = g["coordinates"] if g.get("type") == "MultiPolygon" else [g.get("coordinates")]
        for poly in polys:
            if poly:
                out.append(world(np.array([p[:2] for p in poly[0]])))
    return out


def routed_lines(path: Path) -> list[np.ndarray]:
    """The routed (DEM least-cost) path of an alignment file at full vertex detail; the 2-point
    `straight_sketch` feature that sits beside it is never drawn (FIX_FILM_STORY: no straight
    lines across mountains)."""
    out = []
    for props, geom in R._geoms(path):
        if props.get("kind") == "straight_sketch":
            continue
        for part in R._parts(geom):
            pts = [q[:2] for q in part if len(q) >= 2]
            if len(pts) >= 2:
                out.append(world(np.array(pts)))
    return out


def corridor_geom(cid: str) -> tuple[list[np.ndarray], list[np.ndarray]]:
    """Lines (routed alignment, v2 first) and new-station points of one corridor id."""
    for run in ("align/corridors-v2-s1", "align/corridors-s1"):
        p = runs_file(f"{run}/{cid}/alignment.geojson")
        if p.exists():
            return [x for x in routed_lines(p) if len(x) >= 2], []
    pts = []
    fam = cid.split("-")[1] if "-" in cid else ""
    y = REPO_ROOT / f"cities/ksa/corridors/{fam}/{cid}.yaml"
    if y.exists():
        d = yaml.safe_load(y.read_text(encoding="utf-8"))
        sid = cid.split(f"{fam}-", 1)[-1]
        for st in d.get("stations") or []:
            if str(st.get("id", "")).replace("_", "-") == sid:
                pts.append(world(np.array([st["lon"], st["lat"]]))[0])
        if not pts and d.get("stations"):
            st = d["stations"][-1]
            pts.append(world(np.array([st["lon"], st["lat"]]))[0])
    return [], pts


def layout_geom(name: str) -> tuple[list[np.ndarray], list[np.ndarray]]:
    d = yaml.safe_load(runs_file(f"r6/top5/{name}.layout.yaml").read_text(encoding="utf-8"))
    lines, pts = [], []
    for c in d.get("corridors") or []:
        a, b = corridor_geom(c["id"])
        lines += a
        pts += b
    return lines, pts


def top5() -> dict[str, dict[str, str]]:
    with runs_file("r6/top5/top5.csv").open(encoding="utf-8", newline="") as fh:
        return {r["layout"]: r for r in csv.DictReader(fh)}


def cba_central() -> dict:
    """Committed programme vs today, medium population, 60 years, Green Book 2026 central."""
    d = json.loads(
        runs_file("cba/CBA-S1-committed-programme/results.json").read_text(encoding="utf-8")
    )
    for r in d["results"]:
        if (
            r["population"] == "un_wpp_medium"
            and r["horizon"] == 60
            and r["rate_case"] == d["central_rate_case"]
        ):
            return r
    raise KeyError("central CBA row")


def attempts_v3() -> np.ndarray:
    """runs/r6/v3/results.tsv: every row of the final search register, normalised
    (capex_p50 across, robust_npv up)."""
    xs, ys = [], []
    with runs_file("r6/v3/results.tsv").open(encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            try:
                xs.append(float(r["capex_p50"]))
                ys.append(float(r["robust_npv"]))
            except (TypeError, ValueError):
                continue
    xa, ya = np.array(xs), np.array(ys)
    lo_x, hi_x = np.percentile(xa, [0.5, 99.5])
    lo_y, hi_y = np.percentile(ya, [0.5, 99.5])
    return np.column_stack(
        [np.clip((xa - lo_x) / (hi_x - lo_x), 0, 1), np.clip((ya - lo_y) / (hi_y - lo_y), 0, 1)]
    )


def checkpoints() -> list[str]:
    """Checkpoint ids named in docs/STATUS.md (CP1 ..., distinct, in order)."""
    txt = (REPO_ROOT / "docs/STATUS.md").read_text(encoding="utf-8")
    seen: list[str] = []
    for m in re.finditer(r"\bCP([1-9])\b", txt):
        k = "CP" + m.group(1)
        if k not in seen:
            seen.append(k)
    # CP9 is this film's own review (pending, PROJECT.md section 10): not a decision yet.
    return sorted((k for k in seen if k != "CP9"), key=lambda k: int(k[2:]))


# ---------------------------------------------------------------- drawing helpers


def sline(c: Canvas, pts, col, width: float, alpha: float = 1.0, dash=None) -> None:
    c.line(world_px(pts, c.cam), col, width, alpha, dash)


def sdot(c: Canvas, x: float, y: float, r: float, col, alpha: float = 1.0) -> None:
    c.dot(world_px([(x, y)], c.cam)[0], col, r, alpha)


def sring(c: Canvas, x: float, y: float, r: float, col, width: float, alpha: float) -> None:
    c.ring(world_px([(x, y)], c.cam)[0], col, r, width, alpha)


def fill(c: Canvas, ring: np.ndarray, col, alpha: float) -> None:
    if len(ring) >= 3 and alpha > 0 and c.visible(ring):
        c.d.polygon(c.xy(ring), fill=(*col, int(255 * min(alpha, 1))))


def panel(c: Canvas, box, alpha: float = 0.74) -> None:
    c.rect(box, PANEL, alpha)


def lerp(v: float, v0: float, v1: float, x0: float, x1: float) -> float:
    return x0 + (v - v0) / (v1 - v0) * (x1 - x0)


def hbar(c: Canvas, xa: float, xb: float, y: float, h: float, col, alpha: float = 0.92) -> None:
    """A chart bar. Fills are toned down (x0.72, alpha capped) because the engine's glow pass
    blooms large bright areas to white."""
    if xb < xa:
        xa, xb = xb, xa
    if xb - xa > 0.5:
        tone = tuple(int(v * 0.72) for v in col)
        c.rect((xa, y - h / 2, xb, y + h / 2), tone, min(alpha, 0.8))


def tick(c: Canvas, x: float, y: float, h: float, col=PAL["white"], alpha: float = 0.95) -> None:
    c.rect((x - 2, y - h / 2, x + 2, y + h / 2), col, alpha)


def bcr_bar(
    c: Canvas, x0: float, x1: float, y: float, lo: float, hi: float, q: tuple, a: float
) -> None:
    """FIX_FILM_STORY: one benefit-to-cost range (q = P10, P50, P90 of riyals back per riyal) on a
    linear axis lo..hi, a bold white line at 1 ("pays back its cost") and a zero line if lo < 0.
    Green when the middle is at or above 1, red below; `a` grows the bar from P10 to P90."""
    one = lerp(1.0, lo, hi, x0, x1)
    sline(c, [(one, y - 46), (one, y + 46)], PAL["white"], 4, 0.95)
    if lo < 0:
        z = lerp(0.0, lo, hi, x0, x1)
        sline(c, [(z, y - 30), (z, y + 30)], PAL["region"], 2, 0.8)
    if a > 0:
        col = PAL["good"] if q[1] >= 1.0 else PAL["warn"]
        xa = lerp(q[0], lo, hi, x0, x1)
        xb = lerp(q[0] + (q[2] - q[0]) * a, lo, hi, x0, x1)
        hbar(c, xa, xb, y, 34, col)
        if a > 0.95:
            tick(c, lerp(q[1], lo, hi, x0, x1), y, 56)


def corridor_station_xy(cid: str, sid: str) -> np.ndarray | None:
    """World point of station `sid` in a corridor YAML (cities/ksa/corridors/<fam>/<cid>.yaml)."""
    fam = cid.split("-")[1] if "-" in cid else ""
    y = REPO_ROOT / f"cities/ksa/corridors/{fam}/{cid}.yaml"
    if not y.exists():
        return None
    for st in yaml.safe_load(y.read_text(encoding="utf-8")).get("stations") or []:
        if st.get("id") == sid:
            return world(np.array([st["lon"], st["lat"]]))[0]
    return None


L6_PLACES = {  # FIX_FILM_STORY: name -> (Arabic, corridor id, station id)
    "Sakaka": ("سكاكا", "S2-trunk_gap-tabuk-sakaka", "sakaka"),
    "Bisha": ("بيشة", "S2-trunk_gap-taif-bisha", "bisha"),
    "Baysh": ("بيش", "S4-commuter_belt-jazan-315", "baysh"),
}


def flow(c: Canvas, path: np.ndarray, t: float, ctx: dict, n: int, col, speed=0.2, r=3.0) -> None:
    """Illustrative particles along a path (both ways when n is even)."""
    for k in range(n):
        ph = (ctx["phase"][k % 64] + t * speed + k * 0.013) % 1.0
        p = path if k % 2 == 0 else path[::-1]
        c.dot(at(p, ph), col, r, 0.95)


def screen_of(cam: Cam, p: np.ndarray) -> tuple[float, float]:
    x, y = cam.screen(np.asarray(p, float).reshape(1, 2))[0]
    return float(x), float(y)


def fit_cam(pts: np.ndarray, sx: float, sy: float, w: float, h: float) -> Cam:
    """A camera that puts the bbox of world points `pts` inside the screen box centred at
    (sx, sy) of size w x h (bottom-caption layout: cam.cx = W/2, cam.cy = H*CY)."""
    u0, v0 = pts.min(axis=0)
    u1, v1 = pts.max(axis=0)
    z = min(w / max(u1 - u0, 1e-6), h / max(v1 - v0, 1e-6))
    uc, vc = (u0 + u1) / 2, (v0 + v1) / 2
    lon = (uc - (sx - sim.W / 2) / z) / sim.K
    lat = vc + (sy - sim.H * sim.CY) / z
    return Cam(lon, lat, z)


# ---------------------------------------------------------------- places


EXTRA = {  # name -> (Arabic, station uid in cities/ksa/lines/stations.geojson)
    "Al-Jouf": ("الجوف", "sar-north-passenger:al-jawf"),
    "Dawadmi": ("الدوادمي", "landbridge:dawadmi"),
    "Muwai": ("المويه", "landbridge:muwai"),
    "Ar Rusayfah": ("الرصيفة", "hhr:makkah"),
    "Kuwait border": ("الحدود الكويتية", "gcc-railway-ksa:kuwait-border"),
    "UAE border": ("الحدود الإماراتية", "gcc-railway-ksa:uae-border"),
    "Majmaah": ("المجمعة", "sar-north-passenger:majmaah"),
}


def add_places(D: Data) -> None:
    """Main-cut place names (new keys only; the trailer names are untouched)."""
    pts = {
        p.get("station_uid"): xy
        for p, xy in geo_points(REPO_ROOT / "cities/ksa/lines/stations.geojson")
    }
    for name, (ar, uid) in EXTRA.items():
        if uid in pts and name not in D.places:
            D.places[name] = world(np.array(pts[uid]))[0]
            sim.AR_NAMES.setdefault(name, ar)


# ---------------------------------------------------------------- scenes

_CACHE: dict[int, dict[str, Scene]] = {}


def scenes(D: Data) -> dict[str, Scene]:
    """Main-cut choreography (shot id -> Scene), built once per Data object."""
    if id(D) not in _CACHE:
        _CACHE[id(D)] = _build(D)
    return _CACHE[id(D)]


# Qurayyat sits under the Arabic legend (top left) in northern views: label it to the right.
SIDE_DEFAULT = {"Qurayyat": "r"}


def mk(**kw) -> Scene:
    kw.setdefault("credits_bar", True)
    kw["label_side"] = SIDE_DEFAULT | kw.get("label_side", {})
    return Scene(**kw)


def _build(D: Data) -> dict[str, Scene]:  # noqa: C901 (one block per shot, in film order)
    add_places(D)
    P = D.places
    S: dict[str, Scene] = {}
    hejaz = load_layer("hejaz-railway.geojson")
    landbridge = chain(load_layer("landbridge.geojson"), P["Riyadh"], gap=0.3)
    gcc = load_layer("gcc-railway-ksa.geojson")
    legacy = chain(load_layer("sar-east-freight-legacy.geojson"), P["Dammam"], gap=0.3)
    metro = [load_layer(f"riyadh-metro-l{i}.geojson") for i in range(1, 7)]
    metro_st = [xy for _, xy in stations("riyadh-metro")]
    rj_ids = ["RJ-A", "RJ-B", "RJ-C1", "RJ-C2", "RJ-LB"]
    rj = {
        k: [x for x in load_lines(REPO_ROOT / f"cities/ksa/alignments-study/{k}.geojson")]
        for k in rj_ids
    }
    rj_all = [x for v in rj.values() for x in v if len(x) > 2]

    # 1 -- four journeys --------------------------------------------------------------------
    four = ["Qurayyat", "Jeddah", "Abha", "Tabuk"]

    def d0101(c: Canvas, t: float, T: float, ctx: dict) -> None:
        base_network(c, D, t, alpha=0.6)
        town(c, D, "Riyadh", r=5.5)
        for i, n in enumerate(four):
            pulse(c, D, n, t, (0.18 + 0.16 * i) * T, PAL["city"])

    S["sh-01-01"] = mk(
        keys=[(0.0, Cam(45.1, 24.6, 52)), (1.0, Cam(45.1, 24.5, 56))],
        draw=d0101,
        side=True,
        labels=[("Riyadh", 0.08)] + [(n, 0.18 + 0.16 * i) for i, n in enumerate(four)],
        label_side={"Qurayyat": "r", "Tabuk": "r", "Jeddah": "l", "Abha": "r"},
        legend=EC,
    )

    def d0102(c: Canvas, t: float, T: float, ctx: dict) -> None:
        base_network(c, D, t, trains=False)
        f = t / T
        comet(c, D.north, 0.01 + 0.97 * ease(fr(f, 0.06, 0.94)), PAL["existing"], 0.07, 4.6)
        for n in ("Riyadh", "Qassim", "Hail", "Al-Jouf", "Qurayyat"):
            town(c, D, n, r=5)
        if f > 0.9:
            pulse(c, D, "Qurayyat", t, 0.9 * T, PAL["existing"])

    S["sh-01-02"] = mk(
        keys=[
            (0.0, Cam(45.0, 26.4, 128)),
            (0.55, Cam(42.7, 28.0, 118)),
            (1.0, Cam(41.0, 29.1, 122)),
        ],
        draw=d0102,
        labels=[
            ("Riyadh", 0.0),
            ("Qassim", 0.25),
            ("Hail", 0.45),
            ("Al-Jouf", 0.65),
            ("Qurayyat", 0.82),
        ],
        legend=EC,
    )

    air_jr = arc(P["Jeddah"], P["Riyadh"], lift=0.22)

    def d0103(c: Canvas, t: float, T: float, ctx: dict) -> None:
        base_network(c, D, t)
        a = ease(fr(t / T, 0.04, 0.3))
        c.line(partial(air_jr, a), PAL["air"], 2.4, 0.6)
        if a >= 1:
            flow(c, air_jr, t, ctx, 30, PAL["air"], speed=0.2, r=3.2)
        for n in ("Riyadh", "Jeddah"):
            town(c, D, n, r=6)

    S["sh-01-03"] = mk(
        keys=[(0.0, Cam(43.1, 23.5, 118)), (1.0, Cam(43.0, 23.2, 140))],
        draw=d0103,
        labels=[("Riyadh", 0.0), ("Jeddah", 0.0)],
        legend=EC,
    )

    air_aj = arc(P["Abha"], P["Jeddah"], lift=0.2)
    south_names = ("Jeddah", "Makkah", "Taif", "Abha", "Khamis Mushait")
    side_ak = {"Abha": "l", "Khamis Mushait": "r", "Makkah": "r", "Jeddah": "l", "Taif": "r"}

    def d0104(c: Canvas, t: float, T: float, ctx: dict) -> None:
        f = t / T
        for g in D.existing:
            c.line(g, PAL["existing"], 3.0, 0.9)
        for path, ph, sp in D.trains()[2:5]:
            comet(c, path, (ph + sp * t) % 1.0, PAL["existing"], 0.03, 3.4)
        a = ease(fr(f, 0.35, 0.85))
        if a > 0:
            c.line(partial(air_aj, a), PAL["air"], 2.4, 0.85, dash=(10, 8))
            c.dot(at(air_aj, min(a, 0.999)), (255, 255, 255), 4.5)
        for n in south_names:
            town(c, D, n, r=5.5)
        pulse(c, D, "Abha", t, 0.15 * T, PAL["city"])

    S["sh-01-04"] = mk(
        keys=[
            (0.0, Cam(40.3, 21.0, 255)),
            (0.45, Cam(41.2, 19.5, 270)),
            (1.0, Cam(41.8, 18.75, 300)),
        ],
        draw=d0104,
        labels=[(n, 0.0 if n in ("Jeddah", "Makkah") else 0.15) for n in south_names],
        label_side=side_ak,
        legend=("existing",),
        zoom_detail=True,
    )

    def d0105(c: Canvas, t: float, T: float, ctx: dict) -> None:
        for g in D.existing:
            c.line(g, PAL["existing"], 3.0, 0.9)
        for n in ("Abha", "Khamis Mushait"):
            town(c, D, n, r=6)
        pulse(c, D, "Abha", t, 0.05 * T, PAL["city"])

    S["sh-01-05"] = mk(
        keys=[(0.0, Cam(42.05, 18.75, 330)), (1.0, Cam(42.25, 18.6, 420))],
        draw=d0105,
        labels=[("Abha", 0.0), ("Khamis Mushait", 0.1)],
        label_side=side_ak,
        legend=("existing",),
        zoom_detail=True,
    )

    air_rt = arc(P["Riyadh"], P["Tabuk"], lift=-0.16)
    km10 = 10 / 111.0

    def d0106(c: Canvas, t: float, T: float, ctx: dict) -> None:
        base_network(c, D, t)
        f = t / T
        a = ease(fr(f, 0.1, 0.6))
        if a > 0:
            c.line(partial(air_rt, a), PAL["air"], 2.4, 0.85, dash=(10, 8))
            c.dot(at(air_rt, min(a, 0.999)), (255, 255, 255), 4.5)
        town(c, D, "Riyadh", r=6)
        if f > 0.55:
            c.ring(P["Tabuk"], PAL["warn"], km10 * c.cam.z, 2.5, 0.95)
            pulse(c, D, "Tabuk", t, 0.55 * T, PAL["warn"])
        else:
            town(c, D, "Tabuk", r=5)

    S["sh-01-06"] = mk(
        keys=[(0.0, Cam(44.0, 26.0, 105)), (1.0, Cam(40.6, 27.4, 128))],
        draw=d0106,
        labels=[("Riyadh", 0.0), ("Tabuk", 0.1)],
        legend=EC,
    )

    air_title = arc(P["Riyadh"], P["Jeddah"], lift=-0.22)

    def d0107(c: Canvas, t: float, T: float, ctx: dict) -> None:
        base_network(c, D, t, alpha=0.6, trains=False)
        comet(c, D.north, (0.1 + 0.05 * t) % 1.0, PAL["existing"], 0.06, 3.6)
        c.line(air_title, PAL["air"], 2.0, 0.5, dash=(10, 8))
        c.dot(at(air_title, (0.08 * t) % 1.0), (255, 255, 255), 4.0)
        for n in ("Abha", "Tabuk"):
            pulse(c, D, n, t, 0.0, PAL["city"])

    S["sh-01-07"] = mk(
        keys=[(0.0, Cam(44.6, 24.0, 66)), (1.0, Cam(44.6, 24.0, 60))],
        draw=d0107,
        title=True,
        closing=False,
        dim=lambda f: 0.5,
        legend=EC,
    )

    # 2 -- history and today's network -------------------------------------------------------
    hz_all = np.vstack(hejaz) if hejaz else np.zeros((1, 2))
    hz = chain(hejaz, hz_all[int(np.argmax(hz_all[:, 1]))], gap=0.4)
    if len(hz) >= 2 and hz[0][1] < hz[-1][1]:
        hz = hz[::-1]  # north to south, towards Madinah
    hz_st = [xy for _, xy in stations("hejaz-railway")]
    arch = Path(R.RENDERS) / "_assets/archival"

    def d0201(c: Canvas, t: float, T: float, ctx: dict) -> None:
        f = t / T
        for g in D.border:
            c.line(g, PAL["region"], 1.6, 0.5)
        for g in D.existing:
            c.line(g, PAL["existing"], 2.0, 0.3)
        a = ease(fr(f, 0.04, 0.8))
        if len(hz) >= 2 and a > 0:
            c.line(partial(hz, a), PAL["historical"], 3.6, 0.95, dash=(3, 7))
            c.dot(at(hz, min(a, 0.999)), (255, 255, 255), 5)
        for i, p in enumerate(hz_st):
            if fr(f, 0.04, 0.8) * len(hz_st) > i:
                c.dot(p, PAL["historical"], 3.0, 0.9)
        if f > 0.8:
            pulse(c, D, "Madinah", t, 0.8 * T, PAL["historical"])

    S["sh-02-01"] = mk(
        keys=[(0.0, Cam(40.6, 27.6, 132)), (1.0, Cam(40.9, 26.9, 150))],
        draw=d0201,
        labels=[("Tabuk", 0.2), ("Madinah", 0.75)],
        legend=("existing", "historical"),
        insets=[
            Inset(arch / "loc-96513602.jpg", (1190, 170, 600, 290), 0.06, (1.0, 1.1)),
            Inset(arch / "loc-2002714726.jpg", (1190, 480, 600, 290), 0.42, (1.0, 1.1)),
        ],
        texts=[
            (
                1190,
                782,
                "Photographs: B. Moritz / Library of Congress (public domain)",
                "صور: B. Moritz / Library of Congress (ملك عام)",
                "s",
                "l",
            ),
        ],
        texts_at=0.42,
    )

    def d0202(c: Canvas, t: float, T: float, ctx: dict) -> None:
        f = t / T
        for g in D.regions:
            c.line(g, PAL["region"], 1.0, 0.2)
        for g in D.border:
            c.line(g, PAL["region"], 1.6, 0.55)
        a = ease(fr(f, 0.05, 0.8))
        if len(legacy) >= 2 and a > 0:
            c.line(partial(legacy, a), PAL["existing"], 3.6, 0.95)
            c.dot(at(legacy, min(a, 0.999)), (255, 255, 255), 5)
        for n in ("Dammam", "Riyadh"):
            town(c, D, n, r=6)

    S["sh-02-02"] = mk(
        keys=[(0.0, Cam(48.6, 25.4, 175)), (1.0, Cam(48.2, 25.3, 190))],
        draw=d0202,
        labels=[("Dammam", 0.0), ("Hofuf", 0.35), ("Al-Kharj", 0.6), ("Riyadh", 0.8)],
        legend=("existing",),
    )

    def d0203(c: Canvas, t: float, T: float, ctx: dict) -> None:
        f = t / T
        for g in D.regions:
            c.line(g, PAL["region"], 1.0, 0.2)
        for g in D.border:
            c.line(g, PAL["region"], 1.6, 0.55)
        for g in D.committed:
            c.line(g, PAL["committed"], 2.4, 0.5, dash=DASH_PX["committed"])
        for g in D.existing:
            c.line(g, PAL["existing"], 2.0, 0.35)
        a1 = ease(fr(f, 0.05, 0.3))
        a2 = ease(fr(f, 0.3, 0.8))
        if a1 > 0:
            c.line(partial(D.east, a1), PAL["existing"], 4.0, 0.95)
        if a2 > 0:
            c.line(partial(D.north, a2), PAL["existing"], 4.0, 0.95)
            c.dot(at(D.north, min(a2, 0.999)), (255, 255, 255), 5)
        if f > 0.8:
            comet(c, D.north, (t * 0.06) % 1.0, PAL["existing"], 0.06, 3.6)
            comet(c, D.east, (t * 0.08) % 1.0, PAL["existing"], 0.06, 3.6)
        for n in ("Riyadh", "Dammam", "Qassim", "Hail", "Al-Jouf", "Qurayyat"):
            town(c, D, n, r=4.5)

    S["sh-02-03"] = mk(
        keys=[(0.0, Cam(46.6, 26.0, 92)), (1.0, Cam(43.6, 27.4, 92))],
        draw=d0203,
        labels=[
            ("Riyadh", 0.0),
            ("Dammam", 0.1),
            ("Qassim", 0.4),
            ("Hail", 0.5),
            ("Al-Jouf", 0.62),
            ("Qurayyat", 0.75),
        ],
        legend=EC,
    )

    def d0204(c: Canvas, t: float, T: float, ctx: dict) -> None:
        f = t / T
        base_network(c, D, t, alpha=0.4, trains=False)
        a = ease(fr(f, 0.15, 0.6))
        if a > 0:
            c.line(partial(D.hhr, a), PAL["existing"], 4.4, 0.95)
        if f > 0.55:
            for k in range(3):
                comet(c, D.hhr, (k / 3 + 0.08 * t) % 1.0, PAL["existing"], 0.05, 3.8)
        for n in ("Makkah", "Jeddah", "Madinah"):
            town(c, D, n, r=6)

    S["sh-02-04"] = mk(
        keys=[(0.0, Cam(43.5, 24.0, 80)), (1.0, Cam(39.75, 22.9, 225))],
        draw=d0204,
        labels=[("Makkah", 0.2), ("Jeddah", 0.3), ("Madinah", 0.45)],
        label_side={"Jeddah": "l", "Makkah": "r"},
        legend=("existing",),
    )

    def d0205(c: Canvas, t: float, T: float, ctx: dict) -> None:
        f = t / T
        for g in D.existing:
            c.line(g, PAL["existing"], 2.2, 0.35)
        for i, lines in enumerate(metro):
            a = ease(fr(f, 0.1 + 0.08 * i, 0.45 + 0.08 * i))
            for g in lines:
                if a > 0:
                    c.line(partial(g, a), PAL["existing"], 4.2, 0.95)
        n = int(len(metro_st) * ease(fr(f, 0.35, 0.9)))
        for p in metro_st[:n]:
            c.dot(p, (0, 0, 0), 5.0, 0.6)
            c.dot(p, PAL["white"], 3.2, 0.95)

    mst = np.array(metro_st) if metro_st else np.array([P["Riyadh"]])
    mc = mst.mean(axis=0)
    S["sh-02-05"] = mk(
        keys=[
            (0.0, Cam(float(mc[0] / sim.K), float(mc[1]) - 0.02, 420)),
            (1.0, Cam(float(mc[0] / sim.K), float(mc[1]) - 0.06, 1500)),
        ],
        draw=d0205,
        legend=("existing",),
        zoom_detail=True,
    )

    gov = [
        world(np.array(xy))[0]
        for _, xy in geo_points(REPO_ROOT / "cities/ksa/zones/governorate_points.geojson")
    ]
    six = ["Taif", "Tabuk", "Khamis Mushait", "Abha", "Najran", "Jazan"]

    def d0206(c: Canvas, t: float, T: float, ctx: dict) -> None:
        f = t / T
        base_network(c, D, t, alpha=0.8)
        n = int(len(gov) * ease(fr(f, 0.03, 0.3)))
        for p in gov[:n]:
            c.dot(p, PAL["city"], 2.4, 0.55)
        for i, nm in enumerate(six):
            t0 = (0.32 + 0.1 * i) * T
            if t >= t0 and nm in P:
                c.ring(P[nm], PAL["warn"], km10 * c.cam.z, 2.5, 0.95)
                pulse(c, D, nm, t, t0, PAL["warn"])

    S["sh-02-06"] = mk(
        keys=[(0.0, NAT_SIDE), (0.3, NAT_SIDE), (1.0, Cam(41.6, 22.4, 78))],
        draw=d0206,
        side=True,
        labels=[(n, 0.32 + 0.1 * i) for i, n in enumerate(six)],
        label_side={"Khamis Mushait": "r", "Abha": "l", "Najran": "r", "Jazan": "l", "Taif": "r"},
        legend=EC,
    )

    def d0207(c: Canvas, t: float, T: float, ctx: dict) -> None:
        f = t / T
        base_network(c, D, t, committed=False)
        for i, g in enumerate(D.committed):
            a = ease(fr(f, 0.08 + 0.12 * i, 0.55 + 0.12 * i))
            if a > 0 and len(g) >= 2:
                c.line(partial(g, a), PAL["committed"], 3.4, 0.95, dash=DASH_PX["committed"])
        for n in ("Riyadh", "Jeddah", "Dammam"):
            town(c, D, n, r=5)

    S["sh-02-07"] = mk(
        keys=[(0.0, Cam(45.2, 24.4, 74)), (1.0, Cam(45.2, 24.3, 82))],
        draw=d0207,
        labels=[("Riyadh", 0.0), ("Jeddah", 0.1), ("Dammam", 0.1)],
        legend=EC,
    )

    reach = json.loads(runs_file("r6/v3/national_reach.json").read_text(encoding="utf-8"))
    share = float(reach["S1"]["120"]) / float(reach["population_total_2025"])
    st_ec = [xy for p, xy in stations(layers=EC) if not str(p["line_id"]).startswith("riyadh-m")]
    rx0, rx1, ry = 340, 1580, 236

    def d0208(c: Canvas, t: float, T: float, ctx: dict) -> None:
        f = t / T
        base_network(c, D, t, alpha=0.8)
        g = ease(fr(f, 0.05, 0.5))
        for p in st_ec:
            c.dot(p, PAL["city"], 3 + 26 * g, 0.12 * g)
            c.dot(p, PAL["white"], 3.0, 0.9)
        panel(c, (rx0 - 30, ry - 56, rx1 + 30, ry + 52), 0.76 * fr(f, 0.2, 0.32))
        a = ease(fr(f, 0.3, 0.75))
        if a > 0:
            hbar(c, rx0, rx1, ry, 30, GREY, 0.45)
            hbar(c, rx0, rx0 + (rx1 - rx0) * share * a, ry, 30, BAR, 0.9)

    S["sh-02-08"] = mk(
        keys=[(0.0, Cam(45.0, 23.0, 56)), (1.0, Cam(45.0, 23.0, 60))],
        draw=d0208,
        legend=EC,
        texts_at=0.3,
        texts=[
            (rx0, ry - 52, "within two hours of a station", "على بعد ساعتين من محطة", "", "l"),
            (rx1, ry + 20, "everyone", "كل السكان", "s", "r"),
        ],
    )

    # 3 -- the growing country ----------------------------------------------------------------
    pmax = D.pop[0, 2]

    def popdots(c: Canvas, k: float, alpha: float = 1.0) -> None:
        n = len(D.pop)
        shown = int(n * k)
        for i in range(shown):
            r = 1.6 + 24 * math.sqrt(D.pop[i, 2] / pmax)
            c.dot(D.pop_xy[i], PAL["city"], r, 0.32 * alpha)
            c.dot(D.pop_xy[i], (255, 250, 235), max(r * 0.28, 1.2), 0.8 * alpha)

    census = numbers(reg_value("S-r10-023"))[0]
    est = [v for v in numbers(reg_value("S-r10-024")) if v > 1e6][0]
    bx0, bx1, by0 = 1380, 1800, 360

    def d0301(c: Canvas, t: float, T: float, ctx: dict) -> None:
        f = t / T
        base_network(c, D, t, alpha=0.5, trains=False)
        popdots(c, ease(fr(f, 0.03, 0.55)))
        panel(c, (bx0 - 30, by0 - 70, bx1 + 30, by0 + 190), 0.76 * fr(f, 0.2, 0.3))
        top = max(census, est)
        a1 = ease(fr(f, 0.3, 0.55))
        a2 = ease(fr(f, 0.55, 0.8))
        hbar(c, bx0, bx0 + (bx1 - bx0) * census / top * a1, by0, 34, BAR, 0.9)
        hbar(c, bx0, bx0 + (bx1 - bx0) * est / top * a2, by0 + 120, 34, PAL["good"], 0.95)

    S["sh-03-01"] = mk(
        keys=[(0.0, Cam(44.0, 23.8, 54)), (1.0, Cam(44.0, 23.6, 58))],
        draw=d0301,
        legend=EC,
        texts_at=0.3,
        texts=[
            (bx0, by0 - 66, "census count", "تعداد", "", "l"),
            (bx0, by0 + 54, "official estimate, later", "تقدير رسمي لاحق", "", "l"),
        ],
    )

    def d0302(c: Canvas, t: float, T: float, ctx: dict) -> None:
        base_network(c, D, t, alpha=0.7)
        popdots(c, 1.0, 0.8)

    S["sh-03-02"] = mk(
        keys=[(0.0, Cam(45.1, 24.4, 58)), (1.0, Cam(45.0, 24.1, 64))],
        draw=d0302,
        side=True,
        labels=[("Riyadh", 0.05), ("Jeddah", 0.1), ("Dammam", 0.15)],
        legend=EC,
    )

    riy_pop = [
        (D.pop_xy[i], D.pop[i, 2])
        for i in range(len(D.pop))
        if np.hypot(*(D.pop_xy[i] - P["Riyadh"])) < 0.6
    ]

    def d0303(c: Canvas, t: float, T: float, ctx: dict) -> None:
        f = t / T
        for g in D.existing:
            c.line(g, PAL["existing"], 2.6, 0.7)
        for lines in metro:
            for g in lines:
                c.line(g, PAL["existing"], 3.4, 0.95)
        for p, v in riy_pop:
            r = 2 + 30 * math.sqrt(v / pmax)
            c.dot(p, PAL["city"], r * (0.7 + 0.3 * ease(f)), 0.25)
        for k in range(4):
            comet(c, D.east, (k / 4 + 0.05 * t) % 1.0, PAL["existing"], 0.02, 3.4)

    S["sh-03-03"] = mk(
        keys=[(0.0, Cam(46.8, 24.62, 520)), (1.0, Cam(46.72, 24.68, 700))],
        draw=d0303,
        labels=[("Riyadh", 0.0)],
        label_side={"Riyadh": "r"},
        legend=("existing",),
        zoom_detail=True,
    )

    def d0304(c: Canvas, t: float, T: float, ctx: dict) -> None:
        f = t / T
        base_network(c, D, t, alpha=0.6, trains=False)
        for k in range(4):
            comet(c, D.hhr, (k / 4 + 0.07 * t) % 1.0, PAL["existing"], 0.04, 3.8)
        pulse(c, D, "Makkah", t, 0.05 * T, PAL["city"])
        pulse(c, D, "Madinah", t, 0.2 * T, PAL["city"])
        if f > 0.55:
            for i, n in enumerate(("Riyadh", "Jeddah", "Dammam")):
                town(c, D, n, r=5, alpha=fr(f, 0.55 + 0.08 * i, 0.65 + 0.08 * i))

    S["sh-03-04"] = mk(
        keys=[(0.0, Cam(39.9, 22.9, 210)), (0.5, Cam(40.6, 23.2, 150)), (1.0, Cam(44.0, 24.0, 76))],
        draw=d0304,
        labels=[("Makkah", 0.0), ("Madinah", 0.15), ("Jeddah", 0.3), ("Riyadh", 0.6)],
        label_side={"Jeddah": "l", "Makkah": "r"},
        legend=EC,
    )

    def d0305(c: Canvas, t: float, T: float, ctx: dict) -> None:
        f = t / T
        base_network(c, D, t, alpha=0.7, committed=False)
        for g in D.committed:
            c.line(g, PAL["committed"], 2.4, 0.45, dash=DASH_PX["committed"])
        a = ease(fr(f, 0.1, 0.6))
        for g in gcc:
            if a > 0:
                c.line(partial(g, a), PAL["committed"], 3.8, 0.95, dash=DASH_PX["committed"])
        for n in ("Kuwait border", "UAE border"):
            if f > 0.6:
                pulse(c, D, n, t, 0.6 * T, PAL["committed"])
        town(c, D, "Dammam", r=5)
        town(c, D, "Riyadh", r=5)

    S["sh-03-05"] = mk(
        keys=[(0.0, Cam(47.6, 25.4, 112)), (1.0, Cam(48.6, 25.8, 98))],
        draw=d0305,
        labels=[("Riyadh", 0.0), ("Dammam", 0.1), ("Kuwait border", 0.6), ("UAE border", 0.62)],
        legend=EC,
    )

    def d0306(c: Canvas, t: float, T: float, ctx: dict) -> None:
        base_network(c, D, t)
        for n in ("Riyadh", "Jeddah", "Makkah", "Madinah", "Dammam", "Tabuk", "Abha"):
            town(c, D, n, r=4.5)

    S["sh-03-06"] = mk(
        keys=[(0.0, Cam(45.0, 24.2, 70)), (1.0, NAT_SIDE)],
        draw=d0306,
        side=True,
        labels=[("Riyadh", 0.0), ("Jeddah", 0.0), ("Tabuk", 0.2), ("Abha", 0.2)],
        legend=EC,
    )

    # 4 -- who would ride ---------------------------------------------------------------------
    trips3 = [
        arc(P["Riyadh"], P["Jeddah"], lift=-0.18),
        arc(P["Jeddah"], P["Abha"], lift=0.22),
        arc(P["Riyadh"], P["Tabuk"], lift=-0.16),
    ]
    cam41 = Cam(43.0, 23.6, 66)
    mids = [screen_of(cam41, at(a, 0.5)) for a in trips3]

    def d0401(c: Canvas, t: float, T: float, ctx: dict) -> None:
        f = t / T
        base_network(c, D, t, alpha=0.6, trains=False)
        for i, a in enumerate(trips3):
            k = ease(fr(f, 0.08 + 0.15 * i, 0.4 + 0.15 * i))
            if k > 0:
                c.line(partial(a, k), PAL["city"], 3.0, 0.75)
            if k >= 1:
                for j in range(6):
                    c.dot(at(a, (j / 6 + 0.12 * t) % 1.0), PAL["city"], 3.4, 0.95)
        for n in ("Riyadh", "Jeddah", "Abha", "Tabuk"):
            town(c, D, n, r=5)

    S["sh-04-01"] = mk(
        keys=[(0.0, cam41), (1.0, cam41)],
        draw=d0401,
        labels=[("Riyadh", 0.0), ("Jeddah", 0.08), ("Abha", 0.23), ("Tabuk", 0.38)],
        legend=EC,
        texts_at=0.5,
        texts=[
            (mids[0][0] + 8, mids[0][1] + 10, "business", "أعمال", "b", "l"),
            (mids[1][0] + 24, mids[1][1] - 4, "families", "عائلات", "b", "l"),
            (mids[2][0] + 10, mids[2][1] - 44, "students and families", "طلاب وعائلات", "b", "l"),
        ],
    )

    rb = json.loads(
        runs_file("study/extra-travel/baseline/rj_baseline.json").read_text(encoding="utf-8")
    )
    tr = rb["runs"]["S1"]["total"]["trips"]
    seg = [("rail", tr["rail"], PAL["committed"]), ("air", tr["air"], PAL["air"])]
    seg.append(("road", tr["car"] + tr["bus"], ROAD))
    tot = sum(v for _, v, _ in seg)
    sx0, sx1, sy = 360, 1560, 250
    edges = np.cumsum([0.0] + [v / tot for _, v, _ in seg])
    air_rj = arc(P["Riyadh"], P["Jeddah"], lift=-0.2)

    def d0402(c: Canvas, t: float, T: float, ctx: dict) -> None:
        f = t / T
        base_network(c, D, t, alpha=0.7, committed=False)
        c.line(landbridge, PAL["committed"], 3.4, 0.95, dash=DASH_PX["committed"])
        c.line(air_rj, PAL["air"], 2.0, 0.6, dash=(10, 8))
        comet(c, landbridge, (0.05 * t) % 1.0, PAL["committed"], 0.05, 3.6)
        for n in ("Riyadh", "Jeddah"):
            town(c, D, n, r=6)
        panel(c, (sx0 - 30, sy - 50, sx1 + 30, sy + 80), 0.78 * fr(f, 0.15, 0.25))
        a = ease(fr(f, 0.25, 0.7))
        for i, (_, _, col) in enumerate(seg):
            xa = sx0 + (sx1 - sx0) * edges[i]
            xb = sx0 + (sx1 - sx0) * min(edges[i + 1], a)
            if xb > xa:
                hbar(c, xa, xb, sy, 44, col, 0.95)

    S["sh-04-02"] = mk(
        keys=[(0.0, Cam(43.1, 22.6, 118)), (1.0, Cam(43.1, 22.5, 128))],
        draw=d0402,
        labels=[("Riyadh", 0.0), ("Jeddah", 0.0)],
        legend=EC,
        texts_at=0.6,
        texts=[
            (
                int(sx0 + (sx1 - sx0) * (edges[i] + edges[i + 1]) / 2),
                sy + 30,
                name,
                {"rail": "قطار", "air": "طيران", "road": "طريق"}[name],
                "b",
                "c",
            )
            for i, (name, _, _) in enumerate(seg)
        ],
    )

    with runs_file("study/rj/times-s1/times.csv").open(encoding="utf-8", newline="") as fh:
        trows = list(csv.DictReader(fh))
    rail_min = sorted(float(r["d2d_p50_min"]) for r in trows)
    air_min = float(trows[0]["d2d_p50_min"]) - float(trows[0]["vs_air_d2d_model_min"])
    tx0, tx1, ty0, ty1 = 170, 900, 250, 730
    tmax = max(rail_min) * 1.3
    lb_st = [P[n] for n in ("Dawadmi", "Muwai", "Al-Jumum", "Taif") if n in P]

    def d0403(c: Canvas, t: float, T: float, ctx: dict) -> None:
        f = t / T
        base_network(c, D, t, alpha=0.5, trains=False)
        for g in rj_all:
            c.line(
                g, PAL["hypothetical"], 2.4, 0.5 + 0.4 * fr(f, 0.7, 0.8), DASH_PX["hypothetical"]
            )
        if f > 0.72:
            for p in lb_st:
                c.dot(p, PAL["hypothetical"], 6 + 3 * math.sin(t * 4), 0.95)
        for n in ("Riyadh", "Jeddah"):
            town(c, D, n, r=6)
        panel(c, (tx0 - 40, ty0 - 70, tx1 + 40, ty1 + 60), 0.8)
        a = ease(fr(f, 0.06, 0.5))
        step = (ty1 - ty0 - 60) / max(len(rail_min), 1)
        hbar(c, tx0, tx0 + (tx1 - tx0) * air_min / tmax * a, ty0, 26, PAL["air"], 0.95)
        for i, v in enumerate(rail_min):
            k = ease(fr(f, 0.1 + 0.01 * i, 0.5 + 0.01 * i))
            y = ty0 + 50 + i * step
            hbar(c, tx0, tx0 + (tx1 - tx0) * v / tmax * k, y, max(step - 3, 3), PAL["hypothetical"])
        xa = tx0 + (tx1 - tx0) * air_min / tmax
        sline(c, [(xa, ty0 - 20), (xa, ty1)], PAL["air"], 1.6, 0.8 * fr(f, 0.45, 0.55), (6, 6))

    S["sh-04-03"] = mk(
        keys=[(0.0, Cam(39.3, 23.0, 96)), (1.0, Cam(39.3, 23.0, 100))],
        draw=d0403,
        labels=[("Riyadh", 0.0), ("Jeddah", 0.0), ("Taif", 0.72), ("Al-Jumum", 0.74)],
        label_side={"Jeddah": "r", "Al-Jumum": "r", "Riyadh": "l", "Taif": "r"},
        legend=EH,
        texts_at=0.08,
        texts=[
            (
                tx0,
                ty0 - 62,
                "door to door, faster ← → slower",
                "من الباب للباب: أسرع ← → أبطأ",
                "",
                "l",
            ),
            (int(tx0 + (tx1 - tx0) * air_min / tmax) + 14, ty0 - 16, "air", "طيران", "b", "l"),
            (tx1, ty0 + 200, "rail cases", "حالات القطار", "b", "r"),
        ],
    )

    iso: list[tuple[str, list[np.ndarray]]] = []
    for m in ("jeddah", "makkah", "dammam", "riyadh", "madinah"):
        p = runs_file(f"access/S1/{m}/isochrone_door_to_door.geojson")
        if p.exists():
            iso.append((m, polygons(p)))
    metros = list(R.METROS)

    def d0404(c: Canvas, t: float, T: float, ctx: dict) -> None:
        f = t / T
        base_network(c, D, t, alpha=0.8)
        for i, (_, rings) in enumerate(iso):
            a = ease(fr(f, 0.3 + 0.12 * i, 0.55 + 0.12 * i))
            for ring in rings:
                fill(c, ring, PAL["city"], 0.30 * a)
                c.line(ring, PAL["city"], 1.6, 0.8 * a)
        for i, n in enumerate(metros):
            pulse(c, D, n, t, (0.04 + 0.04 * i) * T, PAL["city"])

    S["sh-04-04"] = mk(
        keys=[(0.0, Cam(45.0, 23.6, 64)), (1.0, Cam(44.6, 23.6, 74))],
        draw=d0404,
        labels=[(n, 0.04 + 0.04 * i) for i, n in enumerate(metros)],
        label_side={"Jeddah": "l", "Makkah": "r", "Madinah": "l"},
        legend=EC,
    )

    lays = [layout_geom(f"L{i}") for i in range(1, 6)]

    def d0405(c: Canvas, t: float, T: float, ctx: dict) -> None:
        f = t / T
        base_network(c, D, t, alpha=0.8)
        k = min(int(fr(f, 0.1, 0.95) * len(lays)), len(lays) - 1)
        if f >= 0.1:
            lines, pts = lays[k]
            for g in lines:
                c.line(g, PAL["hypothetical"], 3.2, 0.95, DASH_PX["hypothetical"])
            for p in pts:
                c.dot(p, PAL["hypothetical"], 7, 0.95)
        for n in metros:
            town(c, D, n, r=6)

    S["sh-04-05"] = mk(
        keys=[(0.0, Cam(45.0, 23.6, 66)), (1.0, Cam(45.0, 23.6, 70))],
        draw=d0405,
        labels=[(n, 0.0) for n in metros],
        label_side={"Jeddah": "l", "Makkah": "r", "Madinah": "l"},
        legend=ECH,
    )

    with runs_file("study/extra-travel/induced_summary.csv").open(encoding="utf-8") as fh:
        ind = {r["case"]: r for r in csv.DictReader(fh)}
    z0 = ind["zero"]
    moved = float(z0["s1_vs_s0_rail_trips_2050_medium"]) / float(
        z0["national_trips_s1_2050_medium"]
    )
    qx0, qx1, qy = 330, 1590, 330

    def d0406(c: Canvas, t: float, T: float, ctx: dict) -> None:
        f = t / T
        base_network(c, D, t, alpha=0.35)
        panel(c, (qx0 - 40, qy - 90, qx1 + 40, qy + 260), 0.8)
        a = ease(fr(f, 0.08, 0.35))
        hbar(c, qx0, qx0 + (qx1 - qx0) * a, qy, 56, GREY, 0.8)
        hbar(c, qx0, qx0 + (qx1 - qx0) * a, qy + 160, 56, GREY, 0.8)
        m = ease(fr(f, 0.4, 0.8))
        if m > 0:  # the moved trips: drawn at true share of the national total, sliding to rail
            w = max((qx1 - qx0) * moved, 4)
            x = qx0 + (qx1 - qx0 - w) * (1 - m) * 0.5
            hbar(c, x, x + w, qy + 160, 56, PAL["committed"], 0.98)

    S["sh-04-06"] = mk(
        keys=[(0.0, NAT), (1.0, Cam(44.6, 23.6, 76))],
        draw=d0406,
        legend=EC,
        texts=[
            (
                qx0,
                qy - 80,
                "all trips in the country, without the committed lines",
                "كل الرحلات في البلد، بدون الخطوط الملتزم بها",
                "",
                "l",
            ),
            (
                qx0,
                qy + 80,
                "with the committed lines: same total",
                "مع الخطوط الملتزم بها: نفس المجموع",
                "",
                "l",
            ),
            (
                qx1,
                qy + 196,
                "orange: trips that moved to rail",
                "البرتقالي: رحلات انتقلت للقطار",
                "s",
                "r",
            ),
        ],
    )

    cases = [k for k in ("low", "central", "high", "stress") if k in ind]
    extra = [float(ind[k]["extra_trips_2050_medium"]) for k in cases]
    npv0 = abs(float(z0["npv_p50_medium"]))
    dnpv = max(abs(float(ind[k]["npv_p50_medium"]) - float(z0["npv_p50_medium"])) for k in cases)
    ex0, ex1, ey = 330, 1590, 300
    emax = max(extra) * 1.15

    def d0407(c: Canvas, t: float, T: float, ctx: dict) -> None:
        f = t / T
        base_network(c, D, t, alpha=0.35)
        panel(c, (ex0 - 40, ey - 100, ex1 + 40, ey + 340), 0.8)
        sline(c, [(ex0, ey - 40), (ex0, ey + 40)], PAL["white"], 2, 0.85)
        a = ease(fr(f, 0.08, 0.4))
        lo, hi = min(extra), max(extra)
        xa, xb = lerp(lo, 0, emax, ex0, ex1), lerp(lo + (hi - lo) * a, 0, emax, ex0, ex1)
        if a > 0:
            hbar(c, xa, xb, ey, 34, PAL["good"])
            for v in extra:
                if lo + (hi - lo) * a >= v:
                    sdot(c, lerp(v, 0, emax, ex0, ex1), ey, 6, PAL["white"])
        b = ease(fr(f, 0.5, 0.8))
        if b > 0:
            hbar(c, ex0, ex0 + (ex1 - ex0) * b, ey + 220, 40, GREY, 0.8)
            w = (ex1 - ex0) * dnpv / npv0
            hbar(c, ex1 - w * b, ex1, ey + 220, 40, PAL["warn"], 0.98)

    S["sh-04-07"] = mk(
        keys=[(0.0, NAT), (1.0, Cam(44.6, 23.6, 76))],
        draw=d0407,
        legend=EC,
        texts=[
            (
                ex0,
                ey - 90,
                "extra trips a year if travel also creates trips",
                "رحلات إضافية في السنة لو السفر يولّد رحلات",
                "",
                "l",
            ),
            (ex0, ey + 26, "zero", "صفر", "s", "c"),
            (
                ex0,
                ey + 130,
                "overall result (benefits minus costs), middle case: the whole bar",
                "النتيجة العامة (المنافع ناقص التكاليف)، الحالة الوسطى: العمود كامل",
                "",
                "l",
            ),
            (ex1, ey + 250, "red: the largest change", "الأحمر: أكبر تغيّر", "s", "r"),
        ],
        texts_at=0.08,
    )

    # 5 -- air today, Qatar, Landbridge -------------------------------------------------------
    gaca = numbers(reg_value("S-r10-029"))
    dom, total = gaca[0], max(gaca)
    hubs = ("Riyadh", "Jeddah")
    spokes = ("Dammam", "Madinah", "Tabuk", "Abha", "Jazan", "Najran", "Hail", "Qassim")
    air_net = [arc(P[a], P[b], lift=0.15) for a in hubs for b in spokes if b in P and a in P]
    air_net.append(arc(P["Riyadh"], P["Jeddah"], lift=-0.18))
    ax0, ax1, ay = 380, 1340, 236

    def d0501(c: Canvas, t: float, T: float, ctx: dict) -> None:
        f = t / T
        base_network(c, D, t, alpha=0.7)
        for i, a in enumerate(air_net):
            k = ease(fr(f, 0.03 + 0.02 * i, 0.3 + 0.02 * i))
            if k > 0:
                c.line(partial(a, k), PAL["air"], 1.6, 0.45)
            if k >= 1:
                c.dot(at(a, (ctx["phase"][i] + 0.15 * t) % 1.0), PAL["air"], 3.2, 0.95)
        panel(c, (ax0 - 30, ay - 56, ax1 + 30, ay + 56), 0.78 * fr(f, 0.2, 0.3))
        b = ease(fr(f, 0.3, 0.7))
        if b > 0:
            hbar(c, ax0, ax0 + (ax1 - ax0) * b, ay, 30, GREY, 0.6)
            hbar(c, ax0, ax0 + (ax1 - ax0) * dom / total * b, ay, 30, PAL["air"], 0.98)

    S["sh-05-01"] = mk(
        keys=[(0.0, Cam(44.8, 23.0, 58)), (1.0, Cam(44.8, 23.1, 62))],
        draw=d0501,
        legend=EC,
        texts_at=0.3,
        texts=[
            (
                ax0,
                ay - 52,
                "pink: domestic · grey: international",
                "الوردي: داخلي · الرمادي: دولي",
                "",
                "l",
            ),
        ],
    )

    oag = reg_value("S-xt-002")
    growth = [float(x) for x in re.findall(r"\+(\d+(?:\.\d+)?)\s*%", oag)]
    gx0, gx1, gy = 1250, 1760, 330

    def d0502(c: Canvas, t: float, T: float, ctx: dict) -> None:
        f = t / T
        base_network(c, D, t)
        c.line(air_jr, PAL["air"], 2.4, 0.6)
        flow(c, air_jr, t, ctx, 30 + int(24 * ease(fr(f, 0.3, 0.8))), PAL["air"], 0.22, 3.2)
        for n in ("Riyadh", "Jeddah"):
            town(c, D, n, r=6)
        panel(c, (gx0 - 30, gy - 70, gx1 + 30, gy + 190), 0.78)
        gmax = max(growth) if growth else 1.0
        for i, g in enumerate(growth[:2]):
            a = ease(fr(f, 0.2 + 0.2 * i, 0.5 + 0.2 * i))
            hbar(c, gx0, gx0 + (gx1 - gx0) * g / gmax * a, gy + i * 120, 34, PAL["air"])

    S["sh-05-02"] = mk(
        keys=[(0.0, Cam(41.6, 23.0, 128)), (1.0, Cam(41.7, 22.9, 136))],
        draw=d0502,
        labels=[("Riyadh", 0.0), ("Jeddah", 0.0)],
        legend=EC,
        texts_at=0.2,
        texts=[
            (gx0, gy - 66, "growth on 2024", "النمو مقارنة بـ 2024", "", "l"),
            (gx0, gy + 54, "growth on 2019", "النمو مقارنة بـ 2019", "", "l"),
        ],
    )

    def d0503(c: Canvas, t: float, T: float, ctx: dict) -> None:
        base_network(c, D, t)
        c.line(air_jr, PAL["air"], 2.0, 0.5)
        flow(c, air_jr, t, ctx, 22, PAL["air"], 0.2, 3.0)
        for n in ("Riyadh", "Jeddah", "Makkah", "Madinah"):
            town(c, D, n, r=5)

    S["sh-05-03"] = mk(
        keys=[(0.0, Cam(43.6, 23.6, 90)), (1.0, Cam(43.4, 23.4, 100))],
        draw=d0503,
        side=True,
        labels=[("Riyadh", 0.0), ("Jeddah", 0.0)],
        legend=EC,
    )

    cam54 = Cam(49.9, 25.6, 270)
    qx, qy_ = screen_of(cam54, world(np.array([51.2, 25.3]))[0])  # label anchor only (east)

    def d0504(c: Canvas, t: float, T: float, ctx: dict) -> None:
        base_network(c, D, t)
        pulse(c, D, "Hofuf", t, 0.15 * T, PAL["committed"])
        pulse(c, D, "Dammam", t, 0.3 * T, PAL["committed"])

    S["sh-05-04"] = mk(
        keys=[(0.0, Cam(49.3, 25.6, 230)), (1.0, cam54)],
        draw=d0504,
        labels=[("Hofuf", 0.15), ("Dammam", 0.3)],
        legend=EC,
        texts_at=0.45,
        texts=[(int(qx), int(qy_) - 16, "Qatar", "قطر", "b", "c")],
    )

    lb_names = ["Riyadh", "Dawadmi", "Muwai", "Al-Jumum", "Jeddah"]

    def d0505(c: Canvas, t: float, T: float, ctx: dict) -> None:
        f = t / T
        base_network(c, D, t, committed=False)
        a = ease(fr(f, 0.06, 0.8))
        if a > 0:
            c.line(partial(landbridge, a), PAL["committed"], 4.0, 0.95, DASH_PX["committed"])
            c.dot(at(landbridge, min(a, 0.999)), (255, 255, 255), 5)
        for i, n in enumerate(lb_names):
            if f > 0.06 + 0.17 * i:
                town(c, D, n, col=PAL["committed"], r=5)

    S["sh-05-05"] = mk(
        keys=[(0.0, Cam(44.0, 23.6, 120)), (1.0, Cam(42.6, 23.0, 132))],
        draw=d0505,
        labels=[(n, 0.06 + 0.17 * i) for i, n in enumerate(lb_names)],
        label_side={"Jeddah": "l", "Al-Jumum": "r"},
        legend=EC,
    )

    # 6 -- method ------------------------------------------------------------------------------
    v2 = [
        x
        for cid in ("S3-branch_spur-al-kharj", "S4-commuter_belt-riyadh-225")
        for x in load_lines(runs_file(f"align/corridors-v2-s1/{cid}/alignment.geojson"))
    ]
    v2pts = np.vstack(v2) if v2 else np.array([P["Riyadh"]])

    def d0601(c: Canvas, t: float, T: float, ctx: dict) -> None:
        f = t / T
        for g in D.existing:
            c.line(g, PAL["existing"], 3.0, 0.9)
        for i, g in enumerate(v2):
            a = ease(fr(f, 0.06 + 0.3 * i, 0.6 + 0.3 * i))
            if a > 0:
                c.line(partial(g, a), PAL["hypothetical"], 4.0, 0.95, (6, 7))
                c.dot(at(g, min(a, 0.999)), (255, 255, 255), 5)
        for n in ("Riyadh", "Al-Kharj"):
            town(c, D, n, r=6)

    c61 = fit_cam(v2pts, 960, 430, 1300, 620)
    S["sh-06-01"] = mk(
        keys=[(0.0, Cam(c61.lon, c61.lat, c61.z * 0.8)), (1.0, c61)],
        draw=d0601,
        labels=[("Riyadh", 0.0), ("Al-Kharj", 0.2)],
        legend=EH,
        zoom_detail=True,
    )

    val = {
        k: [x for x in load_lines(runs_file(f"align/validation-v2-s1/{k}/alignment.geojson"))]
        for k in ("hhr", "sar-north-passenger", "sar-east-passenger")
        if runs_file(f"align/validation-v2-s1/{k}/alignment.geojson").exists()
    }

    def d0602(c: Canvas, t: float, T: float, ctx: dict) -> None:
        f = t / T
        base_network(c, D, t, alpha=0.6, trains=False)
        for g in D.existing:
            c.line(g, PAL["existing"], 4.0, 0.9)
        for i, lines in enumerate(val.values()):
            a = ease(fr(f, 0.1 + 0.15 * i, 0.5 + 0.15 * i))
            for g in lines:
                if a > 0:
                    c.line(partial(g, a), PAL["hypothetical"], 3.0, 0.95, (5, 7))

    S["sh-06-02"] = mk(
        keys=[(0.0, Cam(44.2, 25.4, 64)), (0.55, Cam(44.2, 25.4, 66)), (1.0, Cam(39.7, 22.7, 260))],
        draw=d0602,
        labels=[("Makkah", 0.6), ("Madinah", 0.6), ("Jeddah", 0.6)],
        label_side={"Jeddah": "l", "Makkah": "r"},
        legend=EH,
    )

    prof = pd.read_parquet(runs_file("study/rj/align-s1/RJ-B/profile.parquet"))
    leg1 = prof[prof["leg"] == 1]
    lp = world(leg1[["lon", "lat"]].to_numpy())
    lstruct = leg1["structure"].to_numpy()
    chord = np.vstack([lp[0], lp[-1]])
    c63 = fit_cam(lp, 960, 440, 1250, 560)

    def runs_of(kind: str) -> list[np.ndarray]:
        out, cur = [], []
        for i, s in enumerate(lstruct):
            if s == kind:
                cur.append(lp[i])
            elif cur:
                out.append(np.array(cur))
                cur = []
        if cur:
            out.append(np.array(cur))
        return [x for x in out if len(x) >= 2]

    tunnels, viaducts = runs_of("tunnel"), runs_of("viaduct")
    cum = sim.cumlen(lp)

    def d0603(c: Canvas, t: float, T: float, ctx: dict) -> None:
        f = t / T
        for g in D.existing:
            c.line(g, PAL["existing"], 3.0, 0.9)
        ca = ease(fr(f, 0.05, 0.25))
        if ca > 0:
            c.line(partial(chord, ca), PAL["white"], 2.0, 0.8 * (1 - 0.5 * fr(f, 0.6, 0.8)), (8, 8))
        a = ease(fr(f, 0.3, 0.8))
        if a > 0:
            c.line(partial(lp, a), PAL["hypothetical"], 4.0, 0.95, (6, 7))
            lim = a * cum[-1]
            for seg_, col in ((tunnels, TUNNEL), (viaducts, PAL["white"])):
                for s_ in seg_:
                    keep = [p for p in s_ if cum[int(np.argmin(np.hypot(*(lp - p).T)))] <= lim]
                    if len(keep) >= 2:
                        if col is TUNNEL:
                            c.line(np.array(keep), PAL["hypothetical"], 10.0, 0.95)
                        c.line(np.array(keep), col, 6.0, 0.95)
            c.dot(at(lp, min(a, 0.999)), (255, 255, 255), 5)
        town(c, D, "Taif", r=6)
        c.rect((147, 207, 189, 225), PAL["hypothetical"], 0.95 * fr(f, 0.3, 0.36))
        c.rect((150, 210, 186, 222), TUNNEL, 0.95 * fr(f, 0.3, 0.36))
        c.rect((150, 250, 186, 262), PAL["white"], 0.95 * fr(f, 0.3, 0.36))

    S["sh-06-03"] = mk(
        keys=[(0.0, Cam(c63.lon, c63.lat, c63.z * 0.85)), (1.0, c63)],
        draw=d0603,
        labels=[("Taif", 0.0)],
        legend=EH,
        zoom_detail=True,
        texts_at=0.3,
        texts=[
            (200, 200, "tunnel", "نفق", "", "l"),
            (200, 240, "viaduct", "جسر", "", "l"),
            (200, 280, "dashed white: straight line", "الأبيض المتقطع: خط مستقيم", "s", "l"),
        ],
    )

    marks = [
        world(np.array(xy))[0]
        for _, xy in geo_points(REPO_ROOT / "cities/ksa/alignments-study/haram_markers.geojson")
    ]
    mk_arr = np.array(marks) if marks else np.array([P["Makkah"]])
    c64 = fit_cam(mk_arr, 960, 430, 1100, 560)

    def d0604(c: Canvas, t: float, T: float, ctx: dict) -> None:
        f = t / T
        for g in D.existing:
            c.line(g, PAL["existing"], 4.0, 0.95)
        for k in range(2):
            comet(c, D.hhr, (k / 2 + 0.03 * t) % 1.0, PAL["existing"], 0.01, 3.6)
        n = int(len(marks) * ease(fr(f, 0.05, 0.35)))
        for p in marks[:n]:
            c.dot(p, PAL["warn"], 3.6, 0.95)
        a = ease(fr(f, 0.35, 0.8))
        for g in rj_all:
            if a > 0:
                c.line(partial(g, 1.0), PAL["hypothetical"], 3.2, 0.9 * a, DASH_PX["hypothetical"])
        if f > 0.7:
            pulse(c, D, "Ar Rusayfah", t, 0.7 * T, PAL["existing"])

    S["sh-06-04"] = mk(
        keys=[(0.0, Cam(c64.lon, c64.lat, c64.z * 0.7)), (1.0, c64)],
        draw=d0604,
        labels=[("Ar Rusayfah", 0.7)],
        legend=EH,
        zoom_detail=True,
        texts_at=0.08,
        texts=[
            (
                150,
                200,
                "red dots: mapped Haram boundary markers",
                "النقاط الحمراء: علامات حدود الحرم على الخريطة",
                "",
                "l",
            ),
        ],
    )

    reg = yaml.safe_load((REPO_ROOT / "cities/ksa/costs/cost_register.yaml").read_text("utf-8"))
    cats = ["line_type", "structure", "signalling", "electrification"]
    crow = []
    for cat in cats:
        items = [
            i
            for i in reg["items"]
            if i.get("category") == cat
            and i.get("unit") == "SAR_m_per_km"
            and all(isinstance(i.get(k), int | float) and i.get(k) > 0 for k in ("low", "high"))
        ]
        items.sort(key=lambda i: float(i.get("central") or i["low"]))
        crow += [
            (cat, float(i["low"]), float(i.get("central") or i["low"]), float(i["high"]))
            for i in items
        ]
    lo_all = math.log10(min(r[1] for r in crow))
    hi_all = math.log10(max(r[3] for r in crow))
    kx0, kx1, ky0, ky1 = 560, 1700, 220, 780

    def d0605(c: Canvas, t: float, T: float, ctx: dict) -> None:
        f = t / T
        base_network(c, D, t, alpha=0.35)
        panel(c, (kx0 - 360, ky0 - 60, kx1 + 40, ky1 + 50), 0.8)
        step = (ky1 - ky0) / max(len(crow) + len(cats), 1)
        y = ky0
        last = None
        for i, (cat, lo, mid, hi) in enumerate(crow):
            if cat != last:
                y += step
                last = cat
            a = ease(fr(f, 0.06 + 0.5 * i / len(crow), 0.2 + 0.5 * i / len(crow)))
            if a > 0:
                xa = lerp(math.log10(lo), lo_all, hi_all, kx0, kx1)
                xb = lerp(math.log10(hi), lo_all, hi_all, kx0, kx1)
                hbar(c, xa, xa + (xb - xa) * a, y, max(step * 0.7, 2), PAL["committed"], 0.85)
                if a > 0.9:
                    tick(c, lerp(math.log10(mid), lo_all, hi_all, kx0, kx1), y, step + 2)
            y += step

    first_y = {}
    yy = ky0
    step0 = (ky1 - ky0) / max(len(crow) + len(cats), 1)
    lastc = None
    for cat, *_ in crow:
        if cat != lastc:
            yy += step0
            first_y[cat] = yy
            lastc = cat
        yy += step0
    cat_lbl = {
        "line_type": ("track and line", "السكة والخط"),
        "structure": ("structures", "المنشآت"),
        "signalling": ("signalling", "الإشارات"),
        "electrification": ("electrification", "الكهربة"),
    }
    S["sh-06-05"] = mk(
        keys=[(0.0, NAT), (1.0, Cam(44.6, 23.6, 76))],
        draw=d0605,
        legend=EC,
        texts=[(kx0 - 30, int(first_y[k]) - 4, *cat_lbl[k], "", "r") for k in cats if k in first_y]
        + [
            (
                kx1,
                ky0 - 52,
                "cost per km, log scale →  bar: low to high · white: middle",
                "التكلفة لكل كيلو (مقياس لوغاريتمي) ←  العمود: من المنخفض للمرتفع · الأبيض: الوسط",
                "s",
                "r",
            ),
        ],
    )

    upl = yaml.safe_load((REPO_ROOT / "cities/ksa/costs/uplifts.yaml").read_text("utf-8"))
    rc = next(u for u in upl["uplifts"] if u["id"] == "U-capex-rail-sobc")
    pc = sorted((float(k), float(v)) for k, v in rc["params"]["percentiles"].items())
    rmax = max(v for _, v in pc) * 1.05
    ux0, ux1, uy0, uy1 = 300, 1180, 230, 740

    def d0606(c: Canvas, t: float, T: float, ctx: dict) -> None:
        f = t / T
        base_network(c, D, t, alpha=0.35)
        panel(c, (ux0 - 60, uy0 - 60, 1700, uy1 + 70), 0.8)
        sline(c, [(ux0, uy1), (ux1, uy1)], PAL["region"], 1.5, 0.8)
        sline(c, [(ux0, uy1), (ux0, uy0)], PAL["region"], 1.5, 0.8)
        x1 = lerp(1.0, 0, rmax, ux0, ux1)
        sline(c, [(x1, uy0), (x1, uy1)], PAL["white"], 1.6, 0.8, (6, 6))
        pts = [(lerp(v, 0, rmax, ux0, ux1), lerp(p, 0, 100, uy1, uy0)) for p, v in pc]
        a = ease(fr(f, 0.08, 0.6))
        if a > 0 and len(pts) >= 2:
            k = max(int(len(pts) * a), 2)
            sline(c, pts[:k], PAL["committed"], 4.0, 0.95)
            for x, y in pts[:k]:
                sdot(c, x, y, 4, PAL["committed"])
        b = fr(f, 0.65, 0.75)
        if b > 0:
            c.rect((1330, 400, 1640, 560), GREY, 0.35 * b)
            sline(
                c,
                [(1330, 400), (1640, 400), (1640, 560), (1330, 560), (1330, 400)],
                PAL["white"],
                2,
                0.8 * b,
            )

    S["sh-06-06"] = mk(
        keys=[(0.0, NAT), (1.0, Cam(44.6, 23.6, 76))],
        draw=d0606,
        legend=EC,
        texts=[
            (ux1, uy1 + 14, "final cost ÷ estimate →", "التكلفة النهائية ÷ التقدير →", "s", "r"),
            (
                ux0 + 10,
                uy0 - 50,
                "↑ share of rail projects at or below",
                "↑ نسبة مشاريع السكك عند هذا الحد أو أقل",
                "s",
                "l",
            ),
            (int(lerp(1.0, 0, rmax, ux0, ux1)) + 8, uy0 + 4, "no overrun", "بدون تجاوز", "s", "l"),
            (1485, 455, "contingency", "الاحتياطي", "b", "c"),
            (1485, 495, "reported separately", "يُذكر بشكل منفصل", "s", "c"),
        ],
        texts_at=0.08,
    )

    # 7 -- the search ---------------------------------------------------------------------------
    fam: dict[str, list[np.ndarray]] = {"S2": [], "S3": [], "S4": []}
    root = runs_file("align/corridors-s1")
    for d_ in sorted(root.glob("S*")) if root.exists() else []:
        k = d_.name[:2]
        if k in fam and (d_ / "alignment.geojson").exists():
            fam[k] += [x for x in load_lines(d_ / "alignment.geojson") if len(x) >= 2]
    s5 = []
    for y_ in sorted((REPO_ROOT / "cities/ksa/corridors/station_addition").glob("*.yaml")):
        _, pts = corridor_geom(y_.stem)
        s5 += pts

    def d0701(c: Canvas, t: float, T: float, ctx: dict) -> None:
        f = t / T
        base_network(c, D, t, alpha=0.8)
        order = [("S5", None), ("S3", fam["S3"]), ("S4", fam["S4"]), ("S2", fam["S2"])]
        for i, (k, lines) in enumerate(order):
            a = ease(fr(f, 0.06 + 0.18 * i, 0.3 + 0.18 * i))
            if a <= 0:
                continue
            if k == "S5":
                for p in s5:
                    c.dot(p, PAL["hypothetical"], 5.5, 0.95 * a)
            else:
                for g in lines or []:
                    c.line(partial(g, a), PAL["hypothetical"], 2.4, 0.85, DASH_PX["hypothetical"])

    S["sh-07-01"] = mk(
        keys=[(0.0, Cam(45.1, 24.2, 62)), (1.0, NAT_SIDE)],
        draw=d0701,
        side=True,
        legend=ECH,
    )

    l2 = top5()["S6-L2"]
    three = [float(l2[f"npv_p50cost_{k}"]) for k in ("low", "medium", "high")]
    jx, jy = 960, 470

    def d0702(c: Canvas, t: float, T: float, ctx: dict) -> None:
        f = t / T
        base_network(c, D, t, alpha=0.35)
        panel(c, (150, 190, 1770, 790), 0.8)
        # the frozen judge
        c.rect((jx - 150, jy - 90, jx + 150, jy + 90), (40, 48, 64), 0.95)
        sline(
            c,
            [
                (jx - 150, jy - 90),
                (jx + 150, jy - 90),
                (jx + 150, jy + 90),
                (jx - 150, jy + 90),
                (jx - 150, jy - 90),
            ],
            PAL["existing"],
            2.5,
            0.95,
        )
        for k, f0 in ((-1, 0.08), (1, 0.75)):  # fingerprint checked before and after
            if f > f0:
                sring(c, jx, jy + k * 150, 22, PAL["good"], 3, 0.95)
        # the fan of draws
        if "fan" not in ctx:
            r_ = ctx["rng"]
            ctx["fan"] = np.column_stack([r_.random(10_000), r_.normal(0, 1, 10_000)])
        n = int(10_000 * ease(fr(f, 0.15, 0.55)))
        fan = ctx["fan"][:n]
        for u, v in fan[::4]:
            sdot(c, 260 + 360 * u, jy + v * 60 * (0.3 + u), 1.2, PAL["existing"], 0.5)
        # three population cases; the score is the worst one
        lo_ = min(three + [0.0])
        hi_ = max(three)
        for i, v in enumerate(three):
            a = ease(fr(f, 0.55 + 0.06 * i, 0.7 + 0.06 * i))
            y = jy - 90 + i * 90
            xa = lerp(0, lo_, hi_ * 1.1, 1240, 1700)
            xb = lerp(v * a, lo_, hi_ * 1.1, 1240, 1700)
            worst = v == min(three)
            col = PAL["warn"] if worst and f > 0.82 else PAL["good"]
            hbar(c, xa, xb, y, 40, col, 0.95)

    S["sh-07-02"] = mk(
        keys=[(0.0, NAT), (1.0, Cam(44.6, 23.6, 76))],
        draw=d0702,
        legend=EC,
        texts=[
            (jx, jy - 18, "the judge (frozen)", "الحَكَم (مجمّد)", "b", "c"),
            (jx, jy - 230, "fingerprint checked before", "البصمة قبل", "s", "c"),
            (jx, jy + 186, "and after", "وبعد", "s", "c"),
            (440, 250, "random draws", "سحوبات عشوائية", "", "c"),
            (1470, 250, "three population cases", "ثلاث حالات للسكان", "", "c"),
            (1470, jy + 170, "score: the worst (red)", "النتيجة: الأسوأ (أحمر)", "s", "c"),
        ],
        texts_at=0.05,
    )

    loop_c = (760, 470)
    nodes = [
        (loop_c[0] + 230 * math.cos(a), loop_c[1] + 200 * math.sin(a))
        for a in (-math.pi / 2, 0, math.pi / 2, math.pi)
    ]
    ring_pts = [
        (loop_c[0] + 230 * math.cos(a), loop_c[1] + 200 * math.sin(a))
        for a in np.linspace(-math.pi / 2, 1.5 * math.pi, 120)
    ]

    def d0703(c: Canvas, t: float, T: float, ctx: dict) -> None:
        f = t / T
        base_network(c, D, t, alpha=0.35)
        panel(c, (190, 190, 1760, 790), 0.8)
        ring_w = world_px(ring_pts, c.cam)
        a = ease(fr(f, 0.05, 0.35))
        c.line(partial(ring_w, a), PAL["hypothetical"], 3.0, 0.9)
        if a >= 1:
            comet(c, ring_w, (0.25 * t) % 1.0, PAL["good"], 0.12, 4.0)
        for i, (x, y) in enumerate(nodes):
            if a * 4 > i:
                sdot(c, x, y, 16, PAL["hypothetical"], 0.95)
        b = fr(f, 0.45, 0.6)
        lane = world_px([(1240, 340), (1680, 340)], c.cam)
        lane2 = world_px([(1240, 600), (1680, 600)], c.cam)
        for ln in (lane, lane2):
            c.line(ln, GREY, 2.0, 0.7 * b)
        if b > 0:
            for k in range(8):
                c.dot(at(lane, (k / 8 + 0.1 * t) % 1.0), PAL["existing"], 4, 0.9 * b)
                c.dot(at(lane2, (k / 8 + 0.13 * t) % 1.0), PAL["existing"], 4, 0.9 * b)

    S["sh-07-03"] = mk(
        keys=[(0.0, NAT), (1.0, Cam(44.6, 23.6, 76))],
        draw=d0703,
        legend=EC,
        texts=[
            (
                int(nodes[0][0]),
                int(nodes[0][1]) - 66,
                "a written hypothesis",
                "فرضية مكتوبة",
                "",
                "c",
            ),
            (int(nodes[1][0]) + 30, int(nodes[1][1]) - 16, "one change", "تغيير واحد", "", "l"),
            (int(nodes[2][0]), int(nodes[2][1]) + 30, "the judge", "الحَكَم", "", "c"),
            (
                int(nodes[3][0]) - 30,
                int(nodes[3][1]) - 16,
                "keep or discard",
                "يبقى أو يُستبعد",
                "",
                "r",
            ),
            (1460, 290, "classical optimisers", "أدوات تحسين تقليدية", "", "c"),
            (1460, 550, "searching in parallel", "تبحث بالتوازي", "", "c"),
        ],
        texts_at=0.05,
    )

    att = attempts_v3()
    order_ = np.random.default_rng(1).permutation(len(att))  # fixed reveal order (seed 1)
    att = att[order_]
    px0, py0, px1, py1 = 300, 200, 1620, 800

    def d0704(c: Canvas, t: float, T: float, ctx: dict) -> None:
        f = t / T
        base_network(c, D, t, alpha=0.35)
        c.rect((px0 - 30, py0 - 40, px1 + 30, py1 + 40), PANEL, 0.75)
        sline(c, [(px0, py1), (px1, py1)], PAL["region"], 1.5, 0.8)
        sline(c, [(px0, py1), (px0, py0)], PAL["region"], 1.5, 0.8)
        n = int(len(att) * ease(fr(f, 0.03, 0.9)))
        for x, y in att[:n:3]:
            sdot(c, px0 + x * (px1 - px0), py1 - y * (py1 - py0), 1.4, PAL["existing"], 0.55)

    S["sh-07-04"] = mk(
        keys=[(0.0, NAT), (1.0, Cam(44.6, 23.6, 76))],
        draw=d0704,
        legend=EC,
        texts=[
            (px0, py1 + 18, "cost (capital, median) →", "التكلفة (رأس المال، الوسيط) →", "", "l"),
            (
                px0 + 10,
                py0 - 34,
                "↑ benefits minus costs (worst population case)",
                "↑ المنافع ناقص التكاليف (أسوأ حالة للسكان)",
                "",
                "l",
            ),
            (
                px1,
                py0 - 34,
                "one dot: one row of the register",
                "كل نقطة: صف واحد من السجل",
                "",
                "r",
            ),
        ],
    )

    cps = checkpoints()
    cx0, cx1, cy_ = 300, 1620, 420

    def d0705(c: Canvas, t: float, T: float, ctx: dict) -> None:
        f = t / T
        base_network(c, D, t, alpha=0.35)
        panel(c, (cx0 - 80, cy_ - 160, cx1 + 80, cy_ + 170), 0.8)
        a = ease(fr(f, 0.05, 0.85))
        sline(c, [(cx0, cy_), (cx0 + (cx1 - cx0) * a, cy_)], PAL["region"], 3, 0.9)
        for i, _ in enumerate(cps):
            x = lerp(i, 0, max(len(cps) - 1, 1), cx0, cx1)
            if (x - cx0) / (cx1 - cx0) <= a + 1e-6:
                sdot(c, x, cy_, 14, PAL["good"], 0.95)
                k = ((t * 0.9) - i * 0.15) % 1.0
                sring(c, x, cy_, 16 + 30 * k, PAL["good"], 2.5, (1 - k) * 0.8)
            else:
                sdot(c, x, cy_, 8, GREY, 0.6)
        if "rows" not in ctx:
            ctx["rows"] = ctx["rng"].random((len(cps), 24))
        for i in range(len(cps)):  # the machine's search between checkpoints (illustrative)
            for k, u in enumerate(ctx["rows"][i]):
                x = lerp(i + (k + 0.5) / 24, 0, max(len(cps) - 1, 1), cx0, cx1)
                if i < len(cps) - 1 and (x - cx0) / (cx1 - cx0) <= a:
                    sdot(c, x, cy_ + 60 + 50 * u, 2.4, PAL["existing"], 0.7)

    S["sh-07-05"] = mk(
        keys=[(0.0, NAT), (1.0, Cam(44.6, 23.6, 76))],
        draw=d0705,
        legend=EC,
        texts=[
            (int(lerp(i, 0, max(len(cps) - 1, 1), cx0, cx1)), cy_ - 66, k, k, "b", "c")
            for i, k in enumerate(cps)
        ]
        + [
            (cx0 - 40, cy_ - 140, "green: a person decided", "الأخضر: شخص قرّر", "", "l"),
            (cx1 + 40, cy_ + 126, "blue: the machine searched", "الأزرق: الآلة بحثت", "", "r"),
        ],
        texts_at=0.05,
    )

    # 8 -- the answers -----------------------------------------------------------------------
    cb = cba_central()
    q01 = (cb["bcr"]["P10"], cb["bcr"]["P50"], cb["bcr"]["P90"])  # S1 vs S0, medium, 60 y
    nx0, nx1, ny = 300, 1620, 330
    blo, bhi = 0.0, max(q01[2], 1.0) * 1.12

    def d0801(c: Canvas, t: float, T: float, ctx: dict) -> None:
        f = t / T
        base_network(c, D, t, alpha=0.5, committed=False)
        for g in D.committed:
            c.line(g, PAL["committed"], 3.4, 0.95, DASH_PX["committed"])
        panel(c, (nx0 - 40, ny - 110, nx1 + 40, ny + 110), 0.8)
        sline(c, [(nx0, ny - 40), (nx0, ny + 40)], PAL["region"], 2, 0.8)
        bcr_bar(c, nx0, nx1, ny, blo, bhi, q01, ease(fr(f, 0.15, 0.6)))

    x_one = int(lerp(1.0, blo, bhi, nx0, nx1))
    S["sh-08-01"] = mk(
        keys=[(0.0, Cam(44.8, 23.6, 70)), (1.0, Cam(44.8, 23.5, 76))],
        draw=d0801,
        legend=EC,
        texts=[
            (x_one, ny + 74, "one: pays back its cost", "واحد: يرجّع تكلفته", "b", "c"),
            (
                nx0,
                ny - 104,
                "riyals back for every riyal spent, committed lines",
                "كم ريال يرجع لكل ريال ينصرف، الخطوط الملتزم بها",
                "",
                "l",
            ),
            (nx0, ny + 74, "zero", "صفر", "s", "c"),
            (
                nx1,
                ny - 104,
                "bar: range · white mark: middle",
                "العمود: النطاق · العلامة البيضاء: الوسط",
                "s",
                "r",
            ),
        ],
        texts_at=0.1,
    )

    T5 = top5()

    def split_scene(lay: str, extra_key: str | None = None) -> Scene:
        row = T5[f"S6-{lay}"]
        lines, pts = layout_geom(lay)
        allp = np.vstack(lines + [np.array(pts)] if pts else lines) if (lines or pts) else None
        cap = [float(row[k]) for k in ("capex_p10", "capex_p50", "capex_p90")]
        qb = tuple(float(row[f"bcr_{k}_medium"]) for k in ("p10", "p50", "p90"))
        reachv = None
        if extra_key:
            reachv = (float(row["access_gain_120"]), float(T5["S6-L2"]["access_gain_120"]))
        px_0, px_1 = 1180, 1740
        lo_, hi_ = 0.0, max(qb[2], 1.0) * 1.08
        cmax = cap[2] * 1.08
        if allp is not None and len(allp) >= 1:
            cam = fit_cam(np.vstack([allp, P["Riyadh"][None, :]]), 540, 470, 820, 560)
            cam.z = min(cam.z, 420)
        else:
            cam = Cam(46.0, 24.6, 160)
        names = [
            n
            for n in (
                "Riyadh",
                "Al-Kharj",
                "Al Jubayl station",
                "Dhahran station",
                "Duruma station",
                "Dammam",
            )
            if n in P
        ]

        def d(c: Canvas, t: float, T: float, ctx: dict) -> None:
            f = t / T
            base_network(c, D, t)
            a = ease(fr(f, 0.05, 0.4))
            for g in lines:
                c.line(partial(g, a), PAL["hypothetical"], 4.0, 0.95, (6, 7))
            for i, p in enumerate(pts):
                if f > 0.05 + 0.08 * i:
                    c.dot(p, PAL["hypothetical"], 8, 0.95)
                    k = ((t - i * 0.3) * 0.9) % 1.0
                    c.ring(p, PAL["hypothetical"], 9 + 30 * k, 2.5, (1 - k) * 0.9)
            panel(c, (px_0 - 50, 200, px_1 + 40, 780), 0.8 * fr(f, 0.15, 0.25))
            b = ease(fr(f, 0.25, 0.5))
            if b > 0:  # cost range, P10-P90, white tick at the median
                xa = px_0 + (px_1 - px_0) * cap[0] / cmax
                xb = px_0 + (px_1 - px_0) * (cap[0] + (cap[2] - cap[0]) * b) / cmax
                hbar(c, xa, xb, 290, 30, PAL["committed"])
                if b > 0.95:
                    tick(c, px_0 + (px_1 - px_0) * cap[1] / cmax, 290, 48)
            if f > 0.4:
                bcr_bar(c, px_0, px_1, 510, lo_, hi_, qb, ease(fr(f, 0.45, 0.75)))
            if reachv:
                g_ = ease(fr(f, 0.55, 0.75))
                rmax_ = max(reachv) * 1.08
                for i, v in enumerate(reachv):
                    hbar(
                        c,
                        px_0,
                        px_0 + (px_1 - px_0) * v / rmax_ * g_,
                        690 + 50 * i,
                        30,
                        PAL["city"] if i == 0 else GREY,
                    )

        texts = [
            (px_0, 222, "cost, range (white: middle)", "التكلفة، نطاق (الأبيض: الوسط)", "", "l"),
            (
                px_0,
                420,
                "riyals back for every riyal spent (white: middle)",
                "كم ريال يرجع لكل ريال ينصرف (الأبيض: الوسط)",
                "",
                "l",
            ),
            (
                int(lerp(1.0, lo_, hi_, px_0, px_1)),
                576,
                "one: pays back",
                "واحد: يرجّع تكلفته",
                "s",
                "c",
            ),
        ]
        if reachv:
            texts += [
                (
                    px_0,
                    650,
                    "within 120 minutes: this option · central case",
                    "في نطاق 120 دقيقة: هذا الخيار · الحالة الوسطى",
                    "s",
                    "l",
                ),
            ]
        return mk(
            keys=[(0.0, Cam(cam.lon, cam.lat, cam.z * 0.85)), (1.0, cam)],
            draw=d,
            labels=[(n, 0.05) for n in names],
            label_side={"Dhahran station": "r", "Al Jubayl station": "r", "Dammam": "l"},
            legend=ECH,
            texts=texts,
            texts_at=0.2,
        )

    S["sh-08-02"] = split_scene("L2")
    S["sh-08-03"] = split_scene("L1")
    S["sh-08-04"] = split_scene("L3", extra_key="reach")

    bars = sim.fiscal_bars()
    fx0, fx1, fy = 560, 1700, 330

    def d0805(c: Canvas, t: float, T: float, ctx: dict) -> None:
        f = t / T
        base_network(c, D, t, alpha=0.35)
        c.rect((fx0 - 440, fy - 120, fx1 + 40, fy + 300), PANEL, 0.78)
        vmax = max(b[2] for b in bars) * 1.05
        sline(c, [(fx0, fy - 60), (fx0, fy + 250)], PAL["white"], 2, 0.8)
        for i, (name, p10, p90, p50) in enumerate(bars):
            a = ease(fr(f, 0.12 + 0.15 * i, 0.5 + 0.15 * i))
            y = fy + i * 150
            xa = fx0 + p10 / vmax * (fx1 - fx0)
            xb = fx0 + (p10 + (p90 - p10) * a) / vmax * (fx1 - fx0)
            hi = name == "fully_public_sar"
            if a > 0:
                hbar(c, xa, xb, y, 46 if hi else 36, PAL["warn"], 0.98 if hi else 0.6)
                if a > 0.95:
                    tick(c, fx0 + p50 / vmax * (fx1 - fx0), y, 64)
            if hi and f > 0.75:
                k = (t * 0.8) % 1.0
                sline(
                    c,
                    [
                        (xa - 8, y - 32),
                        (xb + 8, y - 32),
                        (xb + 8, y + 32),
                        (xa - 8, y + 32),
                        (xa - 8, y - 32),
                    ],
                    PAL["white"],
                    2,
                    0.5 + 0.4 * (1 - k),
                )

    S["sh-08-05"] = mk(
        keys=[(0.0, NAT), (1.0, Cam(44.6, 23.6, 78))],
        draw=d0805,
        legend=EC,
        texts=[
            (fx0 - 20, fy - 18, "Fully public", "تنفيذ حكومي كامل", "b", "r"),
            (fx0 - 20, fy + 132, "PPP, availability", "شراكة، بدفعات إتاحة", "b", "r"),
            (
                fx0 + 6,
                fy - 104,
                "zero: the state pays nothing net",
                "الصفر: الدولة ما تدفع شي",
                "",
                "l",
            ),
            (
                fx1,
                fy + 220,
                "net cost to the state, central case →   bar: range · white mark: median",
                "صافي التكلفة على الدولة، الحالة الوسطى →   "
                "العمود: النطاق · العلامة البيضاء: الوسيط",
                "",
                "r",
            ),
        ],
    )

    ben = [("pv_user_time_cost", PAL["good"]), ("pv_safety", PAL["good"])]
    bvals = [(cb[k]["P10"], cb[k]["P50"], cb[k]["P90"], col) for k, col in ben]
    bmax = max(v[2] for v in bvals) * 1.08
    hx0, hx1, hy = 560, 1700, 330

    def d0806(c: Canvas, t: float, T: float, ctx: dict) -> None:
        f = t / T
        base_network(c, D, t, alpha=0.5, committed=False)
        for g in D.committed:
            c.line(g, PAL["committed"], 3.0, 0.9, DASH_PX["committed"])
        c.rect((hx0 - 440, hy - 120, hx1 + 40, hy + 280), PANEL, 0.78)
        sline(c, [(hx0, hy - 60), (hx0, hy + 220)], PAL["white"], 2, 0.8)
        for i, (p10, p50, p90, col) in enumerate(bvals):
            a = ease(fr(f, 0.12 + 0.25 * i, 0.45 + 0.25 * i))
            y = hy + i * 150
            if a > 0:
                xa = lerp(p10, 0, bmax, hx0, hx1)
                xb = lerp(p10 + (p90 - p10) * a, 0, bmax, hx0, hx1)
                hbar(c, xa, xb, y, 40, col)
                if a > 0.95:
                    tick(c, lerp(p50, 0, bmax, hx0, hx1), y, 60)

    S["sh-08-06"] = mk(
        keys=[(0.0, Cam(44.6, 23.6, 72)), (1.0, Cam(44.6, 23.6, 78))],
        draw=d0806,
        legend=EC,
        texts=[
            (hx0 - 20, hy - 18, "Travel time and cost", "وقت السفر وتكلفته", "b", "r"),
            (hx0 - 20, hy + 132, "Safety", "السلامة", "b", "r"),
            (hx0 + 6, hy - 104, "zero", "صفر", "", "l"),
            (
                hx1,
                hy + 210,
                "in today's money, 60 years →   bar: range · white mark: middle",
                "بقيمة فلوس اليوم، 60 سنة →   العمود: النطاق · العلامة البيضاء: الوسط",
                "",
                "r",
            ),
        ],
    )

    wei = [float(T5[f"S6-L{i}"]["pv_wei_indicative_medium"]) for i in (1, 2, 3)]
    wx0, wx1, wy = 360, 1600, 380
    wmax = max(wei) * 1.1

    def d0807(c: Canvas, t: float, T: float, ctx: dict) -> None:
        f = t / T
        base_network(c, D, t, alpha=0.35)
        panel(c, (wx0 - 60, wy - 140, wx1 + 60, wy + 170), 0.8)
        sline(c, [(wx0, wy - 60), (wx0, wy + 60)], PAL["white"], 2, 0.8)
        a = ease(fr(f, 0.12, 0.6))
        lo, hi = min(wei), max(wei)
        if a > 0:
            xa, xb = lerp(lo, 0, wmax, wx0, wx1), lerp(lo + (hi - lo) * a, 0, wmax, wx0, wx1)
            hbar(c, xa, xb, wy, 50, GREY, 0.55)
            for k in range(int(xa), int(xb), 18):  # hatching: indicative, not in any score
                sline(c, [(k, wy + 25), (min(k + 22, xb), wy - 25)], PAL["white"], 1.4, 0.45)
            for v in wei:
                if lo + (hi - lo) * a >= v:
                    sdot(c, lerp(v, 0, wmax, wx0, wx1), wy, 7, PAL["white"], 0.95)

    S["sh-08-07"] = mk(
        keys=[(0.0, NAT), (1.0, Cam(44.6, 23.6, 76))],
        draw=d0807,
        legend=EC,
        texts=[
            (
                wx0,
                wy - 130,
                "wider boost to the economy, rough estimate: one dot per option",
                "الأثر الأوسع على الاقتصاد، تقدير تقريبي: نقطة لكل خيار",
                "",
                "l",
            ),
            (wx0, wy + 70, "zero", "صفر", "s", "c"),
            (
                wx1,
                wy + 110,
                "hatched grey: outside every ranking",
                "الرمادي المخطط: خارج كل ترتيب",
                "",
                "r",
            ),
        ],
        texts_at=0.1,
    )

    with runs_file("study/rj/score/score.csv").open(encoding="utf-8", newline="") as fh:
        srows = list(csv.DictReader(fh))
    bcr = [float(r["bcr_p50_medium"]) for r in srows]
    bx0_, bx1_, by_ = 200, 820, 260

    def d0808(c: Canvas, t: float, T: float, ctx: dict) -> None:
        f = t / T
        base_network(c, D, t, alpha=0.6, trains=False)
        for i, k in enumerate(rj_ids):
            a = ease(fr(f, 0.05 + 0.08 * i, 0.35 + 0.08 * i))
            for g in rj[k]:
                if len(g) > 2 and a > 0:
                    c.line(partial(g, a), PAL["hypothetical"], 2.8, 0.9, DASH_PX["hypothetical"])
        for n in ("Riyadh", "Jeddah"):
            town(c, D, n, r=6)
        panel(c, (bx0_ - 40, by_ - 70, bx1_ + 40, by_ + 60 + 46 * len(bcr)), 0.8)
        x1 = lerp(1.0, 0, 1.1, bx0_, bx1_)
        sline(c, [(x1, by_ - 30), (x1, by_ + 30 + 46 * len(bcr))], PAL["white"], 2.5, 0.9)
        for i, v in enumerate(bcr):
            b = ease(fr(f, 0.45 + 0.05 * i, 0.7 + 0.05 * i))
            hbar(
                c, bx0_, lerp(v * b, 0, 1.1, bx0_, bx1_), by_ + 30 + 46 * i, 28, PAL["hypothetical"]
            )

    S["sh-08-08"] = mk(
        keys=[(0.0, Cam(38.75, 23.1, 106)), (1.0, Cam(38.8, 23.0, 110))],
        draw=d0808,
        labels=[("Riyadh", 0.0), ("Jeddah", 0.0)],
        legend=EH,
        texts=[
            (
                bx0_,
                by_ - 62,
                "riyals back for every riyal spent, middle case, one bar per sketch",
                "كم ريال يرجع لكل ريال ينصرف، الحالة الوسطى، عمود لكل مخطط",
                "s",
                "l",
            ),
            (
                int(lerp(1.0, 0, 1.1, bx0_, bx1_)),
                by_ - 30 - 26,
                "one: pays back",
                "واحد: يرجّع",
                "s",
                "c",
            ),
        ],
        texts_at=0.4,
    )

    gains = []
    for k in rj_ids:
        p = runs_file(f"study/rj/score/replace-{k.lower()}/national_reach.json")
        g_ = 0.0
        if p.exists():
            d_ = json.loads(p.read_text(encoding="utf-8"))
            for v in (d_.get("layouts") or {}).values():
                g_ = float((v.get("gain") or {}).get("120", 0.0))
        gains.append(g_)
    gmax_ = max(gains + [1.0]) * 1.1
    gx0_, gx1_, gy_ = 200, 820, 250

    def d0809(c: Canvas, t: float, T: float, ctx: dict) -> None:
        f = t / T
        base_network(c, D, t, alpha=0.6, trains=False)
        k = min(int(fr(f, 0.05, 0.95) * len(rj_ids)), len(rj_ids) - 1)
        for i, rid in enumerate(rj_ids):
            on = i == k
            for g in rj[rid]:
                if len(g) > 2:
                    c.line(
                        g,
                        PAL["hypothetical"],
                        4.0 if on else 2.0,
                        0.95 if on else 0.3,
                        DASH_PX["hypothetical"],
                    )
        for n in ("Riyadh", "Jeddah"):
            town(c, D, n, r=6)
        panel(c, (gx0_ - 40, gy_ - 50, gx1_ + 40, gy_ + 40 + 50 * len(gains)), 0.8)
        for i, v in enumerate(gains):
            if i <= k:
                a = ease(fr(f, 0.05 + 0.18 * i, 0.15 + 0.18 * i))
                y = gy_ + 20 + 50 * i
                hbar(c, gx0_, gx0_ + (gx1_ - gx0_) * v / gmax_ * a, y, 30, PAL["city"])
                sdot(c, gx0_ - 14, y, 6, PAL["hypothetical"] if i == k else GREY, 0.95)

    S["sh-08-09"] = mk(
        keys=[(0.0, Cam(38.75, 23.1, 106)), (1.0, Cam(38.8, 23.0, 110))],
        draw=d0809,
        labels=[("Riyadh", 0.0), ("Jeddah", 0.0)],
        legend=EH,
        texts=[
            (
                gx0_,
                gy_ - 44,
                "added to the national two-hour reach, one bar per sketch",
                "الإضافة إلى نطاق الساعتين الوطني، عمود لكل مخطط",
                "s",
                "l",
            ),
        ],
        texts_at=0.05,
    )

    def leg_start(rid: str, leg: int) -> np.ndarray | None:
        p = runs_file(f"study/rj/align-s1/{rid}/profile.parquet")
        if not p.exists():
            return None
        q = pd.read_parquet(p)
        q = q[q["leg"] == leg]
        return world(q[["lon", "lat"]].to_numpy()[:1])[0] if len(q) else None

    gw = leg_start("RJ-C1", 3)  # gateway south-west of Makkah: start of the last leg
    if gw is not None:
        D.places.setdefault("Gateway", gw)
        sim.AR_NAMES.setdefault("Gateway", "البوابة")
    two = [n for n in ("Gateway", "Al-Jumum") if n in P]
    pts10 = np.array([P[n] for n in two] + [P["Jeddah"], P["Makkah"]])
    c810 = fit_cam(pts10, 960, 430, 900, 480)

    def d0810(c: Canvas, t: float, T: float, ctx: dict) -> None:
        f = t / T
        for g in D.existing:
            c.line(g, PAL["existing"], 3.4, 0.9)
        for k_ in ("RJ-C1", "RJ-LB"):
            for g in rj[k_]:
                if len(g) > 2:
                    c.line(g, PAL["hypothetical"], 3.2, 0.9, DASH_PX["hypothetical"])
        for n in ("Jeddah", "Makkah"):
            town(c, D, n, r=6)
        for i, n in enumerate(two):
            pulse(c, D, n, t, (0.2 + 0.25 * i) * T, PAL["hypothetical"])
        del f

    S["sh-08-10"] = mk(
        keys=[(0.0, Cam(c810.lon, c810.lat, c810.z * 0.6)), (1.0, c810)],
        draw=d0810,
        labels=[("Jeddah", 0.0), ("Makkah", 0.0)]
        + [(n, 0.2 + 0.25 * i) for i, n in enumerate(two)],
        label_side={"Jeddah": "l", "Makkah": "r", "Gateway": "l", "Al-Jumum": "r"},
        legend=EH,
        zoom_detail=True,
    )

    st3 = ["Al Jubayl station", "Dhahran station", "Duruma station"]
    gx = [520, 960, 1400]

    def d0811(c: Canvas, t: float, T: float, ctx: dict) -> None:
        f = t / T
        base_network(c, D, t, alpha=0.5)
        for i, n in enumerate(st3):
            pulse(c, D, n, t, 0.1 * i * T, PAL["good"])
        panel(c, (300, 540, 1620, 820), 0.8)
        a = ease(fr(f, 0.05, 0.8))
        sline(c, [(380, 680), (380 + (1540 - 380) * a, 680)], PAL["region"], 3, 0.9)
        for x in gx:
            if (x - 380) / (1540 - 380) <= a:
                c.rect((x - 9, 650, x + 9, 710), GATE, 0.9)

    S["sh-08-11"] = mk(
        keys=[(0.0, Cam(47.0, 23.4, 90)), (1.0, Cam(47.0, 23.4, 96))],
        draw=d0811,
        labels=[(n, 0.1 * i) for i, n in enumerate(st3)],
        legend=EC,
        texts=[
            (gx[0], 580, "gate", "بوابة قرار", "b", "c"),
            (gx[1], 580, "gate", "بوابة قرار", "b", "c"),
            (gx[2], 580, "gate", "بوابة قرار", "b", "c"),
            (
                960,
                730,
                "before each construction start: a field survey and observed demand",
                "قبل كل بدء إنشاء: مسح ميداني وطلب فعلي مرصود",
                "",
                "c",
            ),
        ],
        texts_at=0.1,
    )

    def d0812(c: Canvas, t: float, T: float, ctx: dict) -> None:
        f = t / T
        base_network(c, D, t, trains=False)
        comet(c, D.north, 0.02 + 0.96 * ease(fr(f, 0.0, 0.3)), PAL["existing"], 0.08, 4.0)
        a = ease(fr(f, 0.25, 0.5))
        if a > 0:
            c.line(partial(air_title, a), PAL["air"], 2.6, 0.95, dash=(10, 8))
        if f > 0.5:
            c.ring(P["Abha"], PAL["warn"], km10 * c.cam.z, 2.5, 0.95)
            pulse(c, D, "Abha", t, 0.5 * T, PAL["warn"])
        if f > 0.7:
            c.ring(P["Tabuk"], PAL["warn"], km10 * c.cam.z, 2.5, 0.95)
            pulse(c, D, "Tabuk", t, 0.7 * T, PAL["warn"])
        for n in ("Riyadh", "Jeddah", "Qurayyat"):
            town(c, D, n)

    S["sh-08-12"] = mk(
        keys=[(0.0, Cam(44.4, 24.4, 66)), (1.0, NAT_SIDE)],
        draw=d0812,
        side=True,
        labels=[
            ("Riyadh", 0.0),
            ("Qurayyat", 0.25),
            ("Jeddah", 0.3),
            ("Abha", 0.5),
            ("Tabuk", 0.7),
        ],
        legend=EC,
    )

    S["sh-08-13"] = mk(
        keys=[(0.0, Cam(44.6, 24.0, 64)), (1.0, Cam(44.6, 24.0, 58))],
        draw=lambda c, t, T, ctx: base_network(c, D, t, alpha=0.65),
        title=True,
        closing=False,
        dim=lambda f: 0.5,
        legend=EC,
    )

    def d0814(c: Canvas, t: float, T: float, ctx: dict) -> None:
        base_network(c, D, t, alpha=0.45)
        panel(c, (140, 40, 1780, 790), 0.62 * fr(t / T, 0.0, 0.08))

    S["sh-08-14"] = mk(
        keys=[(0.0, Cam(44.6, 24.0, 58)), (1.0, Cam(44.6, 24.0, 54))],
        draw=d0814,
        title=True,
        closing=False,
        roll=True,
        credits_bar=False,  # the roll carries the OSM and Copernicus credits in full
        dim=lambda f: 0.32,
        legend=EC,
    )
    # FIX_FILM_STORY: the far north and south, today and on the S6-L6 connected comparison
    # layout (docs/r6-l6-connected.md; runs/r6/l6/). Lines are the corridors' DEM least-cost
    # alignments (runs/align/corridors-s1), drawn at full vertex detail: never straight lines.
    for name, (ar, cid, sid) in L6_PLACES.items():
        xy = corridor_station_xy(cid, sid)
        if xy is not None and name not in P:
            D.places[name] = xy
            sim.AR_NAMES.setdefault(name, ar)
    l6 = yaml.safe_load(runs_file("r6/l6/L6.layout.yaml").read_text(encoding="utf-8"))
    l6_ids = [c["id"] for c in l6.get("corridors") or []]
    l6_lines = {cid: corridor_geom(cid)[0] for cid in l6_ids if not cid.startswith("S5-")}
    l6_adds = [p for cid in l6_ids if cid.startswith("S5-") for p in corridor_geom(cid)[1]]
    l6_st: list[np.ndarray] = []
    for cid in l6_ids:
        fam6 = cid.split("-")[1]  # not `fam`: sh-07-01's closure reads that name
        y_ = REPO_ROOT / f"cities/ksa/corridors/{fam6}/{cid}.yaml"
        if y_.exists():
            for st in yaml.safe_load(y_.read_text(encoding="utf-8")).get("stations") or []:
                l6_st.append(world(np.array([st["lon"], st["lat"]]))[0])
    north = ["S2-trunk_gap-tabuk-sakaka", "S3-branch_spur-sakaka"]
    south = [
        "S2-trunk_gap-abha-khamis-mushait-najran",
        "S2-trunk_gap-abha-khamis-mushait-bisha",
        "S2-trunk_gap-taif-bisha",
        "S3-branch_spur-bisha",
        "S4-commuter_belt-abha-khamis-mushait-135",
        "S4-commuter_belt-jazan-315",
    ]
    far5 = ["Tabuk", "Abha", "Khamis Mushait", "Najran", "Jazan"]
    side5 = {"Tabuk": "l", "Abha": "l", "Khamis Mushait": "r", "Najran": "r", "Jazan": "l"}

    def l6_draw(c: Canvas, ids: list[str], a: float, alpha: float = 0.95, w: float = 4.0) -> None:
        for cid in ids:
            for g in l6_lines.get(cid, []):
                if a > 0 and len(g) >= 2:
                    c.line(partial(g, a), PAL["hypothetical"], w, alpha, DASH_PX["hypothetical"])

    t15 = [0.1, 0.55, 0.63, 0.71, 0.79]

    def d0815(c: Canvas, t: float, T: float, ctx: dict) -> None:
        base_network(c, D, t, alpha=0.85)
        for nm, t0 in zip(far5, t15, strict=True):
            if t >= t0 * T and nm in P:
                c.ring(P[nm], PAL["warn"], km10 * c.cam.z, 2.5, 0.95)
                pulse(c, D, nm, t, t0 * T, PAL["warn"])

    S["sh-08-15"] = mk(
        keys=[
            (0.0, Cam(38.2, 28.6, 150)),
            (0.3, Cam(38.3, 28.4, 165)),
            (0.5, Cam(42.6, 18.6, 190)),
            (1.0, Cam(42.9, 18.0, 230)),
        ],
        draw=d0815,
        labels=[(n, t0) for n, t0 in zip(far5, t15, strict=True)] + [("Qurayyat", 0.0)],
        label_side=side5,
        legend=EC,
        zoom_detail=True,
    )

    def d0816(c: Canvas, t: float, T: float, ctx: dict) -> None:
        f = t / T
        base_network(c, D, t, alpha=0.75)
        for i, cid in enumerate(l6_lines):
            l6_draw(c, [cid], ease(fr(f, 0.06 + 0.035 * i, 0.4 + 0.035 * i)), 0.95, 3.4)
        for i, p in enumerate(l6_adds):
            if f > 0.55 + 0.05 * i:
                c.dot(p, PAL["hypothetical"], 8, 0.95)
        g = ease(fr(f, 0.75, 0.95))
        for p in l6_st:
            c.dot(p, PAL["city"], 3 + 14 * g, 0.18 * g)

    S["sh-08-16"] = mk(
        keys=[(0.0, Cam(45.0, 23.0, 56)), (1.0, Cam(45.0, 23.0, 60))],
        draw=d0816,
        labels=[(n, 0.5) for n in far5] + [("Riyadh", 0.0), ("Jeddah", 0.0), ("Dammam", 0.0)],
        label_side=side5,
        legend=ECH,
    )

    def d0817(c: Canvas, t: float, T: float, ctx: dict) -> None:
        f = t / T
        base_network(c, D, t, alpha=0.9)
        l6_draw(c, north, ease(fr(f, 0.04, 0.36)))
        for i, cid in enumerate(south):
            l6_draw(c, [cid], ease(fr(f, 0.5 + 0.06 * i, 0.72 + 0.06 * i)))
        for nm in ("Tabuk", "Sakaka", "Abha", "Najran", "Jazan", "Bisha", "Taif"):
            if nm in P:
                town(c, D, nm, r=6)

    S["sh-08-17"] = mk(
        keys=[
            (0.0, Cam(38.3, 29.3, 260)),
            (0.36, Cam(38.4, 29.2, 290)),
            (0.48, Cam(42.0, 19.6, 132)),
            (1.0, Cam(42.4, 18.9, 150)),
        ],
        draw=d0817,
        labels=[("Tabuk", 0.0), ("Sakaka", 0.2), ("Al-Jouf", 0.3)]
        + [(n, 0.5) for n in ("Abha", "Khamis Mushait", "Najran", "Bisha", "Taif", "Jazan")],
        label_side=side5 | {"Sakaka": "r", "Al-Jouf": "l", "Bisha": "r", "Taif": "l"},
        legend=ECH,
        zoom_detail=True,
    )

    r6l6 = json.loads(runs_file("r6/l6/national_reach.json").read_text(encoding="utf-8"))
    tot6 = float(r6l6["population_total_2025"])
    s1_share = float(r6l6["S1"]["120"]) / tot6
    l6_share = [float(v["layout"]["120"]) / tot6 for v in r6l6["layouts"].values()][0]
    qx0, qx1, qy = 340, 1580, 236

    def d0818(c: Canvas, t: float, T: float, ctx: dict) -> None:
        f = t / T
        base_network(c, D, t, alpha=0.8)
        l6_draw(c, list(l6_lines), 1.0, 0.75, 2.6)
        g = ease(fr(f, 0.05, 0.4))
        for p in st_ec:
            c.dot(p, PAL["city"], 3 + 22 * g, 0.12 * g)
        h = ease(fr(f, 0.35, 0.6))
        for p in l6_st:
            c.dot(p, PAL["hypothetical"], 3 + 22 * h, 0.12 * h)
            c.dot(p, PAL["white"], 2.6, 0.9 * h)
        panel(c, (qx0 - 30, qy - 56, qx1 + 30, qy + 112), 0.76 * fr(f, 0.2, 0.32))
        a = ease(fr(f, 0.3, 0.6))
        b = ease(fr(f, 0.55, 0.85))
        hbar(c, qx0, qx1, qy, 28, GREY, 0.45 * fr(f, 0.3, 0.4))
        hbar(c, qx0, qx1, qy + 60, 28, GREY, 0.45 * fr(f, 0.3, 0.4))
        if a > 0:
            hbar(c, qx0, qx0 + (qx1 - qx0) * s1_share * a, qy, 28, BAR, 0.9)
        if b > 0:
            hbar(c, qx0, qx0 + (qx1 - qx0) * l6_share * b, qy + 60, 28, PAL["hypothetical"], 0.9)

    S["sh-08-18"] = mk(
        keys=[(0.0, Cam(45.0, 23.0, 56)), (1.0, Cam(45.0, 23.0, 60))],
        draw=d0818,
        legend=ECH,
        texts_at=0.3,
        texts=[
            (qx0, qy - 52, "within two hours of a station", "على بعد ساعتين من محطة", "", "l"),
            (qx1, qy + 18, "committed lines alone", "الخطوط الملتزم بها بس", "s", "r"),
            (qx1, qy + 78, "connected network", "الشبكة المترابطة", "s", "r"),
            (qx0, qy + 100, "full bar: everyone", "العمود كامل: كل السكان", "s", "l"),
        ],
    )

    c19 = fit_cam(np.array([P[n] for n in far5 + list(R.METROS) if n in P]), 960, 440, 1300, 640)
    q19 = []
    for nm in far5:
        if nm in P:
            x_, y_ = screen_of(c19, P[nm])
            q19.append(
                (int(x_) + (34 if side5[nm] == "r" else -34), int(y_) - 40, "?", "?", "b", "c")
            )

    def d0819(c: Canvas, t: float, T: float, ctx: dict) -> None:
        base_network(c, D, t, alpha=0.8)
        l6_draw(c, list(l6_lines), 1.0, 0.7, 2.6)
        for i, nm in enumerate(far5):
            if nm in P:
                pulse(c, D, nm, t, (0.05 + 0.08 * i) * T, PAL["warn"])
        for n in R.METROS:
            town(c, D, n, r=6)

    S["sh-08-19"] = mk(
        keys=[(0.0, c19), (1.0, c19)],
        draw=d0819,
        labels=[(n, 0.05 + 0.08 * i) for i, n in enumerate(far5)]
        + [(n, 0.0) for n in R.METROS if n != "Dammam"],
        label_side=side5,
        legend=ECH,
        texts=q19
        + [
            (
                960,
                120,
                "door-to-door times: not routed by the study",
                "أوقات من الباب إلى الباب: ما حسبتها الدراسة",
                "b",
                "c",
            )
        ],
        texts_at=0.2,
    )

    with runs_file("r6/l6/score/S6-L6.csv").open(encoding="utf-8", newline="") as fh:
        l6row = next(csv.DictReader(fh))
    q20 = tuple(float(l6row[f"bcr_{k}_medium"]) for k in ("p10", "p50", "p90"))
    ux0, ux1, uy = 300, 1620, 330
    ulo, uhi = min(q20[0], 0.0) - 0.1, 1.25

    def d0820(c: Canvas, t: float, T: float, ctx: dict) -> None:
        f = t / T
        base_network(c, D, t, alpha=0.4)
        l6_draw(c, list(l6_lines), 1.0, 0.45, 2.4)
        panel(c, (ux0 - 40, uy - 110, ux1 + 40, uy + 110), 0.8)
        bcr_bar(c, ux0, ux1, uy, ulo, uhi, q20, ease(fr(f, 0.15, 0.6)))

    S["sh-08-20"] = mk(
        keys=[(0.0, Cam(44.6, 23.6, 70)), (1.0, Cam(44.6, 23.5, 76))],
        draw=d0820,
        legend=ECH,
        texts=[
            (
                int(lerp(1.0, ulo, uhi, ux0, ux1)),
                uy + 74,
                "one: pays back its cost",
                "واحد: يرجّع تكلفته",
                "b",
                "c",
            ),
            (int(lerp(0.0, ulo, uhi, ux0, ux1)), uy + 74, "zero", "صفر", "s", "c"),
            (
                ux0,
                uy - 104,
                "riyals back for every riyal spent, connected network",
                "كم ريال يرجع لكل ريال ينصرف، الشبكة المترابطة",
                "",
                "l",
            ),
            (
                ux1,
                uy - 104,
                "bar: range · white mark: middle",
                "العمود: النطاق · العلامة البيضاء: الوسط",
                "s",
                "r",
            ),
        ],
        texts_at=0.1,
    )
    return S


# ---------------------------------------------------------------- CLI (still frames)

app = typer.Typer(add_completion=False)


def main_shots() -> list[dict]:
    d = yaml.safe_load((REPO_ROOT / "film/storyboard/shots.yaml").read_text(encoding="utf-8"))
    return [s for s in d["shots"] if s.get("cut") == "main"]


def still(shot: dict, lang: str, f: float, out: Path, dur: float = 0.0) -> Path:
    dur = dur or float(R.shot_durations("main", lang).get(shot["id"]) or shot["duration_s"])
    P_ = sim.prepare(shot, lang, dur, Path("/tmp/bm/sim-work") / shot["id"])
    i = int(round(f * (P_["n"] - 1)))
    out.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(sim.frame_at(P_, i), "RGB").save(out)
    return out


@app.command()
def frame(
    shot_id: str,
    lang: str = typer.Option("ar", "--lang"),
    f: float = typer.Option(0.7, "--f", help="shot fraction 0..1"),
    out: Path = typer.Option(..., "--out"),
    dur: float = typer.Option(0.0, "--dur"),
) -> None:
    """Write one still frame of a main shot (same per-frame code path as the render)."""
    s = {x["id"]: x for x in main_shots()}[shot_id]
    typer.echo(still(s, lang, f, out, dur))


@app.command()
def frames(
    lang: str = typer.Option("ar", "--lang"),
    f: float = typer.Option(0.7, "--f"),
    outdir: Path = typer.Option(Path("/tmp/bm/frames"), "--outdir"),
    only: str = typer.Option("", "--only", help="comma-separated shot ids"),
) -> None:
    """Still frames for every main shot (or --only)."""
    want = {x for x in only.split(",") if x}
    for s in main_shots():
        if want and s["id"] not in want:
            continue
        typer.echo(still(s, lang, f, outdir / f"{s['id']}-{lang}.png"))


if __name__ == "__main__":
    app()
