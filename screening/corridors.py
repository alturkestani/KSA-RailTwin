"""Corridor families from the screening short list (W2.4; `corridor-generator` skill).

Four families, each a set of hypothetical-layer line YAMLs under `cities/ksa/corridors/<family>/`
and a scenario `scenarios/S2..S5.yaml`; every rule distance is an assumption in
`cities/ksa/assumptions/corridor_rules.yaml` (A-corr-001..014). Nothing is hard-coded: the families
come from the short list (`runs/r2/score/scores.parquet`), the register, the CP1 metro list
(A-screen-013) and the W1 station and line layers, so the verifier can re-run and diff.

- trunk gaps (S2): metros and short-list towns >= A-corr-002, pairs on a Gabriel graph inside the
  A-corr-003 band; a pair whose rail path (existing + committed, transfers A-corr-001) is missing
  or longer than A-corr-005 x the straight line is a gap; tier-1 metro pairs joined only by
  non-HSR lines are speed gaps (A-corr-006; e.g. Jeddah-Riyadh HSR vs the S1 mixed Landbridge);
  connected pairs are recorded as dominated by S0/S1;
- branches and spurs (S3): short-list towns with a scored role between A-corr-007 and A-corr-008 km
  from the nearest station; spur from that station; towns within A-corr-009 km sharing a root form
  one branch;
- commuter belts (S4): per metro, short-list towns 40-120 km away (A-screen-005), one radial per
  A-corr-010 sector;
- station additions (S5): short-list towns more than 10 km from a station (A-screen-004) and within
  A-corr-011 km of an existing or committed alignment: a new station between the two host stations.

Alignments are great-circle sketches through the stations (A-corr-012), terrain shares from the
nearest classified register row along the sketch (A-corr-013, DEM pending), structure shares from
A-corr-014. Every corridor is `uncosted` until the W3 cost register prices it (skill rule).

R4_ALIGN (additive): `--alignments cities/ksa/alignments` replaces the sketch fields of every
corridor whose routed sidecar (`network.align apply`) was routed through the same stations: km-posts
become chainage along the routed alignment (route factor 1, the measured detour is recorded),
terrain shares are the along-line classes and structure shares the measured tunnel/viaduct km
(A-align-080). The trunk-gap detour tests (A-corr-005) then divide the rail path by the routed
length where one exists (else the straight line, recorded in the decision). `--alternatives-out`
writes the trunk pairs that were not generated (dominated or not a speed gap) as corridor YAMLs so
they can be routed too.

R5 (additive, CP5 H4a): `exclude_corridors` in corridor_rules.yaml drops a named corridor by rule
(recorded as a decision row; `validate` rejects it), e.g. the Farasan sea-crossing belt.

FIX_HHR_REROUTE (additive): station-siting rule A-station-001 (adopted by Tariq, 6 Nov 2026;
`docs/stations-siting.md`). Every station the generator adds (anything not taken from
`stations.geojson`) that is not of class `airport` and lies within 1.5 km of an airport point
(`rail.station_inventory.ON_AIRPORT_KM`; airport points = aerodrome centroids of
`economic_nodes.parquet`) is checked: a station addition (S5) is refused, and a station of any other
family is flagged (`siting_flags`) for a site search. Nothing is moved. Each case is a decision row.

uv run python -m screening.corridors generate --seed 1
Label: screening input, not a forecast.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import math
import re
import shutil
import unicodedata
from pathlib import Path
from typing import Any

import networkx as nx
import numpy as np
import pandas as pd
import typer
import yaml
from pydantic import ConfigDict

from common.runmeta import write_meta
from common.schemas import LABEL_TEXT, LineSpec
from screening.funnel import load_config, metro_table, scored_roles, val

app = typer.Typer(add_completion=False, help=__doc__, no_args_is_help=True)

RULES = Path("cities/ksa/assumptions/corridor_rules.yaml")
WEIGHTS = Path("cities/ksa/assumptions/screening_weights.yaml")
LINES = Path("cities/ksa/lines")
FAMILIES = {
    "trunk_gap": ("S2", "family_trunk_gaps", "Trunk gaps between metros and regional centres"),
    "branch_spur": ("S3", "family_branches_spurs", "Branches and spurs to economic nodes"),
    "commuter_belt": ("S4", "family_commuter_belts", "Commuter belts per metro (40-120 km)"),
    "station_addition": (
        "S5",
        "family_station_additions",
        "Station additions on existing and committed lines",
    ),
}
LABEL = "screening input, not a forecast; indicative sketch alignment, uncosted"
R_KM = 6371.0088


class CorridorSpec(LineSpec):
    """`line-yaml` plus the corridor-generator fields."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    family: str
    rule_id: str
    generated_from_ids: list[str]
    alignment_sketch: list[list[float]]
    route_factor: dict[str, Any]
    terrain_shares: dict[str, float]
    terrain_method: str
    structures_share: dict[str, float]
    structures_method: str
    technology_options: list[str]
    connects_to: list[dict[str, Any]] = []
    assumptions_used: list[str]
    cost_status: str
    label: str
    alignment_routed: dict[str, Any] | None = None  # R4_ALIGN (additive)
    siting_flags: list[dict[str, Any]] | None = None  # A-station-001 (FIX_HHR_REROUTE, additive)


# ----------------------------------------------------------------------------- geometry
def gc_km(lat1: Any, lon1: Any, lat2: Any, lon2: Any) -> Any:
    p1, p2 = np.radians(lat1), np.radians(lat2)
    a = (
        np.sin((p2 - p1) / 2) ** 2
        + np.cos(p1) * np.cos(p2) * np.sin((np.radians(lon2) - np.radians(lon1)) / 2) ** 2
    )
    return 2 * R_KM * np.arcsin(np.sqrt(a))


def bearing_deg(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    p1, p2, dl = math.radians(lat1), math.radians(lat2), math.radians(lon2 - lon1)
    y = math.sin(dl) * math.cos(p2)
    x = math.cos(p1) * math.sin(p2) - math.sin(p1) * math.cos(p2) * math.cos(dl)
    return (math.degrees(math.atan2(y, x)) + 360) % 360


def _xy(lat: Any, lon: Any, lat0: float, lon0: float) -> tuple[Any, Any]:
    """Local equirectangular km around (lat0, lon0); fine for the <= 50 km checks it serves."""
    x = np.radians(np.asarray(lon) - lon0) * R_KM * math.cos(math.radians(lat0))
    y = np.radians(np.asarray(lat) - lat0) * R_KM
    return x, y


def point_line_km(lat: float, lon: float, coords: list[list[float]]) -> float:
    """Distance (km) from a point to a [lon, lat] polyline."""
    c = np.asarray(coords, dtype=float)
    x, y = _xy(c[:, 1], c[:, 0], lat, lon)
    best = np.inf
    for i in range(len(c) - 1):
        ax, ay, bx, by = x[i], y[i], x[i + 1], y[i + 1]
        dx, dy = bx - ax, by - ay
        L = dx * dx + dy * dy
        t = 0.0 if L == 0 else max(0.0, min(1.0, -(ax * dx + ay * dy) / L))
        best = min(best, math.hypot(ax + t * dx, ay + t * dy))
    return float(best)


def point_segment_km(p: tuple[float, float], a: tuple[float, float], b: tuple[float, float]):
    """Distance (km) of point p from the straight segment a-b, and the position t along it."""
    lat0, lon0 = p
    (ax, bx), (ay, by) = _xy([a[0], b[0]], [a[1], b[1]], lat0, lon0)
    dx, dy = bx - ax, by - ay
    L = dx * dx + dy * dy
    t = 0.0 if L == 0 else max(0.0, min(1.0, -(ax * dx + ay * dy) / L))
    return math.hypot(ax + t * dx, ay + t * dy), t


def slug(s: str) -> str:
    s = unicodedata.normalize("NFKD", str(s))
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:28] or "x"


def sha12(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:12]


# ----------------------------------------------------------------------------- inputs
def load_stations(rules: dict) -> pd.DataFrame:
    keep = set(val(rules["network"]["lines_existing"])) | set(
        val(rules["network"]["lines_committed"])
    )
    gj = json.loads((LINES / "stations.geojson").read_text(encoding="utf-8"))["features"]
    rows = []
    for f in gj:
        q = f["properties"]
        if q["line_id"] not in keep:
            continue
        lon, lat = f["geometry"]["coordinates"]
        rows.append(
            {
                "uid": q["station_uid"],
                "line_id": q["line_id"],
                "layer": q["layer"],
                "name_en": q["name_en"],
                "name_ar": q.get("name_ar") or q["name_en"],
                "km_post": float(q.get("km_post") or 0.0),
                "lat": lat,
                "lon": lon,
                "located": bool(q.get("located", True)),
            }
        )
    return pd.DataFrame(rows).sort_values(["line_id", "km_post"]).reset_index(drop=True)


def line_types(ids: list[str]) -> dict[str, str]:
    out = {}
    for i in ids:
        out[i] = yaml.safe_load((LINES / f"{i}.yaml").read_text(encoding="utf-8"))["line_type"]
    return out


def line_coords(line_id: str) -> list[list[list[float]]]:
    gj = json.loads((LINES / "geojson" / f"{line_id}.geojson").read_text(encoding="utf-8"))
    parts = []
    for f in gj["features"]:
        g = f["geometry"]
        parts += [g["coordinates"]] if g["type"] == "LineString" else g["coordinates"]
    return parts


def rail_graph(st: pd.DataFrame, transfer_km: float) -> nx.Graph:
    g = nx.Graph()
    for uid, line in zip(st.uid, st.line_id, strict=True):
        g.add_node(uid, line=line)
    for _, grp in st.groupby("line_id"):
        grp = grp.sort_values("km_post")
        for a, b in zip(grp.itertuples(), list(grp.itertuples())[1:], strict=False):
            w = abs(b.km_post - a.km_post) or float(gc_km(a.lat, a.lon, b.lat, b.lon))
            g.add_edge(a.uid, b.uid, km=w, line=a.line_id)
    lat, lon = st.lat.to_numpy(), st.lon.to_numpy()
    for i in range(len(st)):
        d = gc_km(lat[i], lon[i], lat, lon)
        for j in np.flatnonzero((d <= transfer_km) & (np.arange(len(st)) > i)):
            if st.line_id[i] != st.line_id[j]:
                g.add_edge(st.uid[i], st.uid[j], km=float(d[j]), line="transfer")
    return g


def nearest_station(st: pd.DataFrame, lat: float, lon: float) -> tuple[str, float]:
    d = gc_km(lat, lon, st.lat.to_numpy(), st.lon.to_numpy())
    i = int(np.argmin(d))
    return str(st.uid[i]), float(d[i])


# ----------------------------------------------------------------------------- building blocks
class Ctx:
    def __init__(self, cand: Path, scores: Path, rules_p: Path, weights_p: Path, seed: int):
        self.rules = yaml.safe_load(rules_p.read_text(encoding="utf-8"))
        self.cfg = load_config(weights_p)
        self.reg = pd.read_parquet(cand)
        sc = pd.read_parquet(scores)
        short = sc[sc.short_list][["row_key", "rank", "score"]]
        self.short = short.merge(self.reg, on="row_key", how="left").sort_values("rank")
        self.st = load_stations(self.rules)
        self.types = line_types(sorted(set(self.st.line_id)))
        self.g = rail_graph(self.st, float(val(self.rules["network"]["transfer_km"])))
        self.metros = metro_table(self.reg, self.cfg)
        self.seed = seed
        self.src = (
            f"generated by screening.corridors from {cand.name} {sha12(cand)}, {scores.name} "
            f"{sha12(scores)} and {rules_p.name} {sha12(rules_p)}, seed {seed}"
        )
        self.rules_hash = sha12(rules_p)
        terr = self.reg[self.reg.terrain_class.notna()]
        self.terr = (terr.lat.to_numpy(), terr.lon.to_numpy(), terr.terrain_class.to_numpy())
        self.decisions: list[dict[str, Any]] = []
        self.alignments: Path | None = None
        self.alternatives: list[dict[str, Any]] = []

    def station(
        self,
        sid: str,
        name_en: str,
        name_ar: str,
        lat: float,
        lon: float,
        km: float,
        cls: str,
        source: str,
    ) -> dict[str, Any]:
        return {
            "id": sid,
            "name_en": name_en,
            "name_ar": name_ar,
            "km_post": round(km, 1),
            "lat": round(lat, 6),
            "lon": round(lon, 6),
            "class": cls,
            "source": source,
        }

    def terrain(self, pts: list[tuple[float, float]]) -> tuple[dict[str, float], dict[str, float]]:
        geo = self.rules["geometry"]
        step = float(val(geo["terrain_sample_km"]))
        search = float(val(geo["terrain_search_km"]))
        samples = []
        for (la1, lo1), (la2, lo2) in zip(pts, pts[1:], strict=False):
            n = max(1, int(math.ceil(float(gc_km(la1, lo1, la2, lo2)) / step)))
            for k in range(n):
                samples.append((la1 + (la2 - la1) * k / n, lo1 + (lo2 - lo1) * k / n))
        samples.append(pts[-1])
        lat, lon, cls = self.terr
        counts: dict[str, int] = {}
        for la, lo in samples:
            d = gc_km(la, lo, lat, lon)
            i = int(np.argmin(d)) if len(d) else -1
            c = str(cls[i]) if i >= 0 and d[i] <= search else "unknown"
            counts[c] = counts.get(c, 0) + 1
        n = sum(counts.values())
        shares = {k: round(v / n, 3) for k, v in sorted(counts.items())}
        sb = geo["structures_by_terrain"]
        struct = {
            s: round(sum(shares[k] * sb[k][s] for k in shares), 4) for s in ("tunnel", "viaduct")
        }
        return shares, struct

    def corridor(
        self,
        family: str,
        cid: str,
        name_en: str,
        name_ar: str,
        rule: str,
        stations: list[dict],
        ids: list[str],
        line_type: str,
        tech: list[str],
        assumptions: list[str],
        connects: list[dict],
        notes: str,
    ) -> dict[str, Any]:
        pts = [(s["lat"], s["lon"]) for s in stations]
        shares, struct = self.terrain(pts)
        geo = self.rules["geometry"]
        today = dt.date(2026, 10, 31).isoformat()
        out = {
            "id": cid,
            "name_en": name_en,
            "name_ar": name_ar,
            "family": family,
            "layer": "hypothetical",
            "operator": None,
            "status": "generated",
            "source": self.src,
            "source_date": today,
            "accessed": today,
            "line_type": line_type,
            "length_km": round(stations[-1]["km_post"], 1),
            "alignment": None,
            "alignment_sketch": [[round(a, 5), round(b, 5)] for a, b in pts],
            "route_factor": {
                "value": val(geo["route_factor"]),
                "range": geo["route_factor"]["range"],
                "assumption_id": "A-corr-012",
            },
            "stations": stations,
            "generated_from": f"rule {rule}; short list {', '.join(ids)}",
            "generated_from_ids": ids,
            "rule_id": rule,
            "rules_hash": self.rules_hash,
            "terrain_shares": shares,
            "terrain_method": "share of 5 km samples along the sketch by the terrain class of the "
            "nearest classified register row within 30 km, else unknown (A-corr-013; DEM pending)",
            "structures_share": struct,
            "structures_method": "terrain shares x assumed tunnel/viaduct shares per class "
            "(A-corr-014)",
            "technology_options": tech,
            "connects_to": connects,
            "assumptions_used": sorted(
                set(assumptions) | {"A-corr-012", "A-corr-013", "A-corr-014"}
            ),
            "cost_status": "uncosted: no cost range yet (W3); excluded from CBA until priced",
            "label": LABEL,
            "notes": notes,
        }
        if self.alignments is not None and family != "station_addition":
            # station additions sit on existing or committed track: nothing to route
            out = apply_alignment(out, self.alignments)
        CorridorSpec.model_validate(out)
        return out

    def routed_km(self, cid: str) -> float | None:
        """Routed length of a trunk candidate (generated or alternative) if a sidecar exists."""
        if self.alignments is None:
            return None
        for p in (
            self.alignments / f"{cid}.json",
            self.alignments / "alternatives" / f"{cid}.json",
        ):
            if p.exists():
                return float(json.loads(p.read_text(encoding="utf-8"))["length_km"])
        return None


def stations_key(stations: list[dict[str, Any]]) -> str:
    """Hash of the station ids and coordinates in km order (a sidecar applies only if equal)."""
    st = sorted(stations, key=lambda s: float(s["km_post"]))
    key = [[s["id"], round(float(s["lat"]), 5), round(float(s["lon"]), 5)] for s in st]
    return hashlib.sha256(json.dumps(key).encode("utf-8")).hexdigest()[:16]


def apply_alignment(c: dict[str, Any], folder: Path) -> dict[str, Any]:
    """Replace the sketch fields with the routed ones (R4_ALIGN, A-align-080) when the sidecar was
    routed through the same stations; otherwise mark the corridor as awaiting routing."""
    p = folder / f"{c['id']}.json"
    if not p.exists():
        p = folder / "alternatives" / f"{c['id']}.json"
    if not p.exists():
        return c | {"alignment_routed": {"status": "not routed (no sidecar)"}}
    sc = json.loads(p.read_text(encoding="utf-8"))
    if sc["stations_key"] != stations_key(c["stations"]):
        return c | {"alignment_routed": {"status": "stale sidecar (stations changed); re-route"}}
    km = sc["station_km"]
    stations = [s | {"km_post": round(float(km[s["id"]]), 3)} for s in c["stations"]]
    keep = (
        "status",
        "weights_hash",
        "length_km",
        "straight_km_legs",
        "detour_ratio",
        "design_kmh",
        "max_grade_cap",
        "r_min_m",
        "tunnel_km",
        "viaduct_km",
        "earthworks_km",
        "fill_m3",
        "cut_m3",
        "restricted_km",
        "min_curve_kmh",
        "speed_restrictions",
        "elev_min_m",
        "elev_max_m",
        "area_km",
        "wadi_crossings_osm",
        "run",
        "formation_cap_ok",
        "profile_feasible",
        "infeasible_legs",
    )
    routed = {k: sc[k] for k in keep if k in sc}
    L = float(sc["length_km"])
    return c | {
        "length_km": round(L, 3),
        "alignment": sc["geojson"],
        "stations": stations,
        "route_factor": {
            "value": 1.0,
            "range": [1.0, 1.0],
            "assumption_id": "A-align-080",
            "note": f"km-posts along the routed alignment; measured detour ratio "
            f"{sc['detour_ratio']} over the straight legs (replaces A-corr-012)",
        },
        "terrain_shares": dict(sorted(sc["terrain_shares"].items())),
        "terrain_method": "along-line class per 100 m of the routed alignment from Copernicus "
        "GLO-30 relief, OSM sand/sabkha and the OSM coastline (A-align-060; R4_ALIGN)",
        "structures_share": {
            "tunnel": round(float(sc["tunnel_km"]) / L, 4),
            "viaduct": round(float(sc["viaduct_km"]) / L, 4),
        },
        "structures_method": "measured tunnel/viaduct km of the routed formation profile "
        "(A-align-041..043; R4_ALIGN)",
        "assumptions_used": sorted(
            (set(c["assumptions_used"]) - {"A-corr-012", "A-corr-013", "A-corr-014"})
            | {"A-align-001", "A-align-060", "A-align-080"}
        ),
        "label": "screening input, not a forecast; routed hypothetical alignment (R4_ALIGN), "
        "uncosted",
        "alignment_routed": routed,
    }


def _town_station(ctx: Ctx, r: Any, km: float, cls: str) -> dict[str, Any]:
    return ctx.station(
        slug(r.name_en), r.name_en, r.name_ar, r.lat, r.lon, km, cls, f"register {r.row_key}"
    )


def _chain(ctx: Ctx, start: dict, towns: list[Any], start_cls: str = "terminal") -> list[dict]:
    """Stations from `start` through `towns` in the given order, km by great circle."""
    out = [start | {"class": start_cls}]
    km, la, lo = 0.0, start["lat"], start["lon"]
    for i, r in enumerate(towns):
        km += float(gc_km(la, lo, r.lat, r.lon))
        out.append(_town_station(ctx, r, km, "terminal" if i == len(towns) - 1 else "intermediate"))
        la, lo = r.lat, r.lon
    return out


def _ensure_unique_ids(stations: list[dict]) -> list[dict]:
    seen: dict[str, int] = {}
    for s in stations:
        n = seen.get(s["id"], 0)
        seen[s["id"]] = n + 1
        if n:
            s["id"] = f"{s['id']}-{n + 1}"
    return stations


# ----------------------------------------------------------------------------- families
def _gabriel(nodes: list[dict], lo: float, hi: float) -> list[tuple[int, int, float]]:
    """Pairs inside the [lo, hi] km band with no third node in the circle whose diameter is the
    pair (Gabriel graph, A-corr-004)."""
    P = np.array([[n["lat"], n["lon"]] for n in nodes])
    out = []
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            a, b = nodes[i], nodes[j]
            d = float(gc_km(a["lat"], a["lon"], b["lat"], b["lon"]))
            if not lo <= d <= hi:
                continue
            mid = ((a["lat"] + b["lat"]) / 2, (a["lon"] + b["lon"]) / 2)
            dm = gc_km(mid[0], mid[1], P[:, 0], P[:, 1])
            if any(dm[k] < d / 2 for k in range(len(nodes)) if k not in (i, j)):
                continue
            out.append((i, j, d))
    return out


def _rail_link(ctx: Ctx, a: dict, b: dict) -> tuple[float | None, set[str], str, str]:
    """Shortest attachment + rail + attachment km between two nodes over every pair of stations
    within each node's attachment radius (metros A-corr-015, towns A-screen-004)."""
    st = ctx.st
    best: tuple[float | None, set[str], str, str] = (None, set(), "", "")
    opts = []
    for n in (a, b):
        r = n["attach_km"]
        d = gc_km(n["lat"], n["lon"], st.lat.to_numpy(), st.lon.to_numpy())
        opts.append([(str(st.uid[k]), float(d[k])) for k in np.flatnonzero(d <= r)])
    for sa, da in opts[0]:
        for sb, db in opts[1]:
            if not nx.has_path(ctx.g, sa, sb):
                continue
            path = nx.shortest_path(ctx.g, sa, sb, weight="km")
            km = da + db + sum(ctx.g[u][v]["km"] for u, v in zip(path, path[1:], strict=False))
            if best[0] is None or km < best[0]:
                lines = {ctx.g[u][v]["line"] for u, v in zip(path, path[1:], strict=False)}
                best = (km, lines - {"transfer"}, sa, sb)
    return best


def _trunk_corridor(
    ctx: Ctx,
    a: dict,
    b: dict,
    rule: str,
    lt: str,
    tech: list[str],
    why: str,
    link: tuple,
    extra_ids: list[str] | None = None,
) -> dict:
    near_max = float(val(ctx.rules["station_additions"]["max_line_km"]))
    mids = []
    for r in ctx.short.itertuples():
        if r.row_key in (a["row_key"], b["row_key"]):
            continue
        if min(gc_km(r.lat, r.lon, n["lat"], n["lon"]) for n in (a, b)) <= 30:
            continue
        dist, t = point_segment_km((r.lat, r.lon), (a["lat"], a["lon"]), (b["lat"], b["lon"]))
        if dist <= near_max and 0 < t < 1:
            mids.append((t, r))
    mids.sort(key=lambda x: x[0])
    start = ctx.station(
        slug(a["name_en"]),
        a["name_en"],
        a["name_ar"],
        a["lat"],
        a["lon"],
        0.0,
        "terminal",
        a["source"],
    )
    end = pd.Series(
        {
            "name_en": b["name_en"],
            "name_ar": b["name_ar"],
            "lat": b["lat"],
            "lon": b["lon"],
            "row_key": b["source"].removeprefix("register "),
        }
    )
    sts = _chain(ctx, start, [r for _, r in mids] + [end])
    sts[-1]["source"] = b["source"]
    sts = _ensure_unique_ids(sts)
    ids = [a["key"], b["key"]] + (extra_ids or []) + [r.row_key for _, r in mids]
    cid = f"S2-trunk_gap-{slug(a['name_en'])}-{slug(b['name_en'])}"
    connects = [{"station": x} for x in link[2:] if x]
    return ctx.corridor(
        "trunk_gap",
        cid,
        f"{a['name_en']} - {b['name_en']} (hypothetical)",
        f"{a['name_ar']} - {b['name_ar']} (افتراضي)",
        rule,
        sts,
        ids,
        lt,
        tech,
        [
            "A-corr-001",
            "A-corr-002",
            "A-corr-003",
            "A-corr-004",
            "A-corr-005",
            "A-corr-006",
            "A-corr-015",
            "A-screen-013",
        ],
        connects,
        why,
    )


def trunk_gaps(ctx: Ctx) -> list[dict]:
    R = ctx.rules["trunk_gaps"]
    lo, hi = val(R["pair_km"])
    on_km = float(val(ctx.rules["network"]["on_network_km"]))
    m_km = float(val(R["metro_attach_km"]))
    nodes = []
    for m in ctx.metros:
        anchor = next(x for x in ctx.cfg["metros"] if x["name"] == m["name"])
        hit = ctx.reg[ctx.reg.row_key.isin(anchor["anchors"])]
        nodes.append(
            {
                "key": f"metro:{m['name']}",
                "name_en": m["name"],
                "name_ar": str(hit.name_ar.iloc[0]) if len(hit) else m["name"],
                "lat": float(m["lat"][0]),
                "lon": float(m["lon"][0]),
                "pop": m["pop"],
                "tier": m["tier"],
                "row_key": None,
                "attach_km": m_km,
                "source": "A-screen-013 metro anchor",
            }
        )
    for r in ctx.short.itertuples():
        if pd.isna(r.population) or r.population < val(R["min_population"]):
            continue
        if any(gc_km(r.lat, r.lon, n["lat"], n["lon"]) <= 30 for n in nodes):
            continue  # part of a metro already on the node list
        nodes.append(
            {
                "key": r.row_key,
                "name_en": r.name_en,
                "name_ar": r.name_ar,
                "lat": r.lat,
                "lon": r.lon,
                "pop": r.population,
                "tier": None,
                "row_key": r.row_key,
                "attach_km": on_km,
                "source": f"register {r.row_key}",
            }
        )
    out, done = [], set()
    # T1: missing links on the Gabriel graph of metros and large short-list towns
    for i, j, d_gc in _gabriel(nodes, lo, hi):
        a, b = nodes[i], nodes[j]
        link = _rail_link(ctx, a, b)
        pair = f"{a['name_en']}-{b['name_en']}"
        rk = ctx.routed_km(f"S2-trunk_gap-{slug(a['name_en'])}-{slug(b['name_en'])}")
        d = rk if rk is not None else d_gc
        basis = "routed" if rk is not None else "straight"
        if link[0] is not None and link[0] / d <= val(R["detour_max"]):
            if ctx.alignments is None or rk is None:
                ctx.alternatives.append(
                    _trunk_corridor(
                        ctx,
                        a,
                        b,
                        "T1-missing-link",
                        "mixed",
                        ["hsr", "conventional_passenger", "mixed"],
                        "alternative",
                        link,
                    )
                )
            ctx.decisions.append(
                {
                    "family": "trunk_gap",
                    "candidate": pair,
                    "decision": "dominated by S0/S1",
                    "reason": f"rail path via {', '.join(sorted(link[1]))}, "
                    f"network/{basis} {link[0] / d:.2f} <= {val(R['detour_max'])} "
                    "(A-corr-005)",
                }
            )
            continue
        why = (
            "no rail path in S0/S1 between stations within the attachment radii"
            if link[0] is None
            else f"rail path {link[0]:.0f} km = {link[0] / d:.2f} x {basis} line "
            f"(> {val(R['detour_max'])}, A-corr-005)"
        )
        out.append(
            _trunk_corridor(
                ctx,
                a,
                b,
                "T1-missing-link",
                "mixed",
                ["hsr", "conventional_passenger", "mixed"],
                why,
                link,
            )
        )
        done.add(frozenset((a["key"], b["key"])))
    # T2: speed gaps between tier-1 metro clusters (A-corr-006)
    tier = int(val(R["speed_gap_tier"]))
    ck = float(val(R["cluster_km"]))
    t1 = sorted([n for n in nodes if n["tier"] == tier], key=lambda n: -n["pop"])
    clusters: list[dict] = []
    for n in t1:
        host = next(
            (c for c in clusters if gc_km(n["lat"], n["lon"], c["lat"], c["lon"]) <= ck), None
        )
        if host is None:
            clusters.append(n | {"members": [n["key"]]})
        else:
            host["members"].append(n["key"])
            ctx.decisions.append(
                {
                    "family": "trunk_gap",
                    "candidate": n["name_en"],
                    "decision": f"merged into the {host['name_en']} cluster",
                    "reason": f"tier-{tier} metros within {ck:.0f} km (A-corr-006)",
                }
            )
    if val(R["speed_gap_pruning"]) == "gabriel":
        pairs = _gabriel(clusters, lo, hi)
    else:
        pairs = [
            (
                i,
                j,
                float(
                    gc_km(
                        clusters[i]["lat"],
                        clusters[i]["lon"],
                        clusters[j]["lat"],
                        clusters[j]["lon"],
                    )
                ),
            )
            for i in range(len(clusters))
            for j in range(i + 1, len(clusters))
        ]
        pairs = [p for p in pairs if lo <= p[2] <= hi]
    for i, j, d_gc in pairs:
        a, b = clusters[i], clusters[j]
        if frozenset((a["key"], b["key"])) in done:
            continue
        link = _rail_link(ctx, a, b)
        pair = f"{a['name_en']}-{b['name_en']}"
        rk = ctx.routed_km(f"S2-trunk_gap-{slug(a['name_en'])}-{slug(b['name_en'])}")
        d = rk if rk is not None else d_gc
        basis = "routed" if rk is not None else "straight"
        if link[0] is None or link[0] / d > val(R["detour_max"]):
            if link[0] is not None and (ctx.alignments is None or rk is None):
                extra = [k for k in a["members"] + b["members"] if k not in (a["key"], b["key"])]
                ctx.alternatives.append(
                    _trunk_corridor(
                        ctx, a, b, "T2-speed-gap", "hsr", ["hsr"], "alternative", link, extra
                    )
                )
            ctx.decisions.append(
                {
                    "family": "trunk_gap",
                    "candidate": pair,
                    "decision": "not a speed gap (no direct rail path)"
                    if link[0] is None
                    else "not a speed gap (rail path beyond the detour limit)",
                    "reason": "no S0/S1 path within the detour limit; a missing "
                    "link is generated by T1 only where the Gabriel graph keeps the "
                    "pair"
                    + (
                        ""
                        if link[0] is None
                        else f" (network/{basis} {link[0] / d:.2f} > {val(R['detour_max'])})"
                    ),
                }
            )
            continue
        if all(ctx.types.get(x) == "hsr" for x in link[1]):
            ctx.decisions.append(
                {
                    "family": "trunk_gap",
                    "candidate": pair,
                    "decision": "dominated by S0 (HSR in service)",
                    "reason": f"rail path via {', '.join(sorted(link[1]))}",
                }
            )
            continue
        why = (
            f"connected in S0/S1 via {', '.join(sorted(link[1]))} (network/{basis} "
            f"{link[0] / d:.2f}) but not by HSR: tier-{tier} metro clusters (A-corr-006); "
            "the S1 line is the comparator"
        )
        extra = [k for k in a["members"] + b["members"] if k not in (a["key"], b["key"])]
        out.append(_trunk_corridor(ctx, a, b, "T2-speed-gap", "hsr", ["hsr"], why, link, extra))
    return out


def branches_spurs(ctx: Ctx) -> list[dict]:
    R = ctx.rules["branches_spurs"]
    lo, hi, grp_km = val(R["min_rail_km"]), val(R["max_spur_km"]), val(R["group_km"])
    towns = []
    for r in ctx.short.itertuples():
        if val(R["requires_role"]) and not scored_roles(r.economic_roles, ctx.cfg):
            continue
        sid, d = nearest_station(ctx.st, r.lat, r.lon)
        if d < lo:
            continue
        if d > hi:
            ctx.decisions.append(
                {
                    "family": "branch_spur",
                    "candidate": r.name_en,
                    "decision": "left to the trunk family",
                    "reason": f"{d:.0f} km from the nearest station {sid} (> {hi} km, A-corr-008)",
                }
            )
            continue
        towns.append((sid, d, r))
    # group: same root station, within group_km of another member (single linkage)
    groups: list[list[tuple]] = []
    for item in sorted(towns, key=lambda x: (x[0], x[1])):
        for gr in groups:
            if gr[0][0] == item[0] and any(
                gc_km(item[2].lat, item[2].lon, o[2].lat, o[2].lon) <= grp_km for o in gr
            ):
                gr.append(item)
                break
        else:
            groups.append([item])
    out = []
    for gr in groups:
        root = ctx.st[ctx.st.uid == gr[0][0]].iloc[0]
        # order: nearest first, then nearest-neighbour from the last town
        rest = sorted(gr, key=lambda x: x[1])
        order = [rest.pop(0)]
        while rest:
            last = order[-1][2]
            rest.sort(key=lambda x: float(gc_km(last.lat, last.lon, x[2].lat, x[2].lon)))
            order.append(rest.pop(0))
        start = ctx.station(
            slug(root.uid.split(":")[-1]),
            root.name_en,
            root.name_ar,
            root.lat,
            root.lon,
            0.0,
            "terminal",
            f"stations.geojson {root.uid}",
        )
        sts = _ensure_unique_ids(_chain(ctx, start, [x[2] for x in order]))
        ids = [x[2].row_key for x in order]
        names = " + ".join(x[2].name_en for x in order)
        cid = f"S3-branch_spur-{slug(order[0][2].name_en)}"
        if len(order) > 1:
            ctx.decisions.append(
                {
                    "family": "branch_spur",
                    "candidate": names,
                    "decision": "merged into one branch",
                    "reason": f"same root {root.uid}, members within {grp_km} km (A-corr-009)",
                }
            )
        out.append(
            ctx.corridor(
                "branch_spur",
                cid,
                f"{root.name_en} - {names} spur (hypothetical)",
                f"{root.name_ar} - {' + '.join(x[2].name_ar for x in order)} (افتراضي)",
                "B1-role-spur",
                sts,
                ids,
                "conventional_passenger",
                ["conventional_passenger", "mixed"],
                ["A-corr-007", "A-corr-008", "A-corr-009", "A-screen-009", "A-screen-011"],
                [{"station": root.uid, "line": root.line_id, "layer": root.layer}],
                f"short-list towns with a scored economic role {gr[0][1]:.0f}-"
                f"{max(x[1] for x in gr):.0f} km "
                f"from {root.uid} ({root.layer}{'' if root.located else ', unlocated proxy stop'})",
            )
        )
    return out


def commuter_belts(ctx: Ctx) -> list[dict]:
    R = ctx.rules["commuter_belts"]
    lo, hi = val(R["band_km"])
    sector = float(val(R["sector_deg"]))
    tiers = set(val(R["metro_tiers"]))
    out = []
    for m in ctx.metros:
        if m["tier"] not in tiers:
            continue
        la, lo_ = float(m["lat"][0]), float(m["lon"][0])
        d = np.min(
            [
                gc_km(ctx.short.lat, ctx.short.lon, a, b)
                for a, b in zip(m["lat"], m["lon"], strict=True)
            ],
            0,
        )
        sel = ctx.short[(d >= lo) & (d <= hi)].assign(d=d[(d >= lo) & (d <= hi)])
        if sel.empty:
            ctx.decisions.append(
                {
                    "family": "commuter_belt",
                    "candidate": m["name"],
                    "decision": "no belt",
                    "reason": f"no short-list town {lo}-{hi} km from the metro (A-screen-005)",
                }
            )
            continue
        sel = sel.assign(
            sec=[int(bearing_deg(la, lo_, r.lat, r.lon) // sector) for r in sel.itertuples()]
        )
        anchor = next(x for x in ctx.cfg["metros"] if x["name"] == m["name"])
        a_row = ctx.reg[ctx.reg.row_key.isin(anchor["anchors"])]
        name_ar = str(a_row.name_ar.iloc[0]) if len(a_row) else m["name"]
        for sec, grp in sel.groupby("sec"):
            grp = grp.sort_values("d")
            start = ctx.station(
                slug(m["name"]),
                m["name"],
                name_ar,
                la,
                lo_,
                0.0,
                "terminal",
                "A-screen-013 metro anchor",
            )
            sts = _ensure_unique_ids(_chain(ctx, start, list(grp.itertuples())))
            lo_deg, hi_deg = int(sec * sector), int((sec + 1) * sector)
            cid = f"S4-commuter_belt-{slug(m['name'])}-{lo_deg:03d}"
            names = " + ".join(grp.name_en)
            out.append(
                ctx.corridor(
                    "commuter_belt",
                    cid,
                    f"{m['name']} commuter belt {lo_deg}-{hi_deg} deg: {names} (hypothetical)",
                    f"حزام {name_ar} للتنقل اليومي ({lo_deg}-{hi_deg}°) (افتراضي)",
                    "C1-metro-sector",
                    sts,
                    list(grp.row_key),
                    "commuter",
                    ["commuter", "conventional_passenger"],
                    ["A-screen-005", "A-screen-013", "A-corr-010"],
                    [],
                    f"short-list towns {lo}-{hi} km (straight line) from {m['name']} "
                    f"(tier {m['tier']}) "
                    f"in the {lo_deg}-{hi_deg} deg sector",
                )
            )
    return out


def station_additions(ctx: Ctx) -> list[dict]:
    R = ctx.rules["station_additions"]
    max_line, min_st = float(val(R["max_line_km"])), float(val(R["min_station_km"]))
    geoms = {lid: line_coords(lid) for lid in sorted(set(ctx.st.line_id))}
    out = []
    for r in ctx.short.itertuples():
        sid, dst = nearest_station(ctx.st, r.lat, r.lon)
        if dst <= min_st:
            continue
        best = min(
            (
                (min(point_line_km(r.lat, r.lon, part) for part in parts), lid)
                for lid, parts in geoms.items()
            ),
            key=lambda x: x[0],
        )
        if best[0] > max_line:
            continue
        lid = best[1]
        hs = ctx.st[ctx.st.line_id == lid].sort_values("km_post").reset_index(drop=True)
        # host pair bracketing the town: smallest detour through it
        k = min(
            range(len(hs) - 1),
            key=lambda i: float(
                gc_km(hs.lat[i], hs.lon[i], r.lat, r.lon)
                + gc_km(r.lat, r.lon, hs.lat[i + 1], hs.lon[i + 1])
                - gc_km(hs.lat[i], hs.lon[i], hs.lat[i + 1], hs.lon[i + 1])
            ),
        )
        A, B = hs.iloc[k], hs.iloc[k + 1]
        d1 = float(gc_km(A.lat, A.lon, r.lat, r.lon))
        d2 = d1 + float(gc_km(r.lat, r.lon, B.lat, B.lon))
        mk = lambda s, km, cls: ctx.station(  # noqa: E731
            slug(s.uid.split(":")[-1]),
            s.name_en,
            s.name_ar,
            s.lat,
            s.lon,
            km,
            cls,
            f"stations.geojson {s.uid}",
        )
        sts = _ensure_unique_ids(
            [
                mk(A, 0.0, "intermediate"),
                _town_station(ctx, r, d1, "planned"),
                mk(B, d2, "intermediate"),
            ]
        )
        layer = str(A.layer)
        out.append(
            ctx.corridor(
                "station_addition",
                f"S5-station_addition-{slug(r.name_en)}",
                f"New station {r.name_en} on {lid} (hypothetical)",
                f"محطة جديدة {r.name_ar} (افتراضي)",
                "A1-near-alignment",
                sts,
                [r.row_key],
                ctx.types[lid],
                [ctx.types[lid]],
                ["A-corr-011", "A-screen-004"],
                [{"line": lid, "layer": layer, "between": [A.uid, B.uid]}],
                f"{best[0]:.1f} km from the {lid} alignment ({layer}), {dst:.1f} km from the "
                "nearest "
                f"station {sid}; through-passenger time penalty to be set by pareto-optimizer (R6)",
            )
        )
    return out


# ----------------------------------------------------------------------------- outputs
def exclusions(rules: dict) -> list[dict[str, Any]]:
    """Explicit corridor exclusions (R5, CP5 H4a): `exclude_corridors` in corridor_rules.yaml.

    Each entry needs `id`, `reason` and `decision`; an optional `members` list guards the premise:
    if the generator produces that id from other short-list rows, the exclusion no longer clearly
    applies and generation stops for a human review (never a silent drop or a silent keep)."""
    out = rules.get("exclude_corridors") or []
    for e in out:
        missing = {"id", "reason", "decision"} - set(e)
        if missing:
            raise ValueError(f"exclude_corridors entry {e!r} lacks {sorted(missing)}")
    return out


def apply_exclusions(
    fams: dict[str, list[dict]], rules: dict, decisions: list[dict[str, Any]]
) -> dict[str, list[dict]]:
    """Drop the corridors named in `exclude_corridors`, each recorded as a decision row of its
    family (so it shows in the scenario's `dominated_or_merged`); an entry that matches nothing is
    recorded too, so the rule stays visible while it cannot fire."""
    ex = {e["id"]: e for e in exclusions(rules)}
    hit: set[str] = set()
    out: dict[str, list[dict]] = {}
    for fam, items in fams.items():
        keep = []
        for c in items:
            e = ex.get(c["id"])
            if e is None:
                keep.append(c)
                continue
            if e.get("members") is not None and sorted(e["members"]) != sorted(
                c["generated_from_ids"]
            ):
                raise ValueError(
                    f"exclusion {c['id']}: generated from {c['generated_from_ids']}, the rule was "
                    f"written for {e['members']}; review the exclusion ({e['decision']})"
                )
            hit.add(c["id"])
            decisions.append(
                {
                    "family": fam,
                    "candidate": c["id"],
                    "decision": "excluded by rule (exclude_corridors)",
                    "reason": f"{e['reason']} ({e['decision']})",
                }
            )
        out[fam] = keep
    for cid, e in ex.items():
        if cid not in hit:
            decisions.append(
                {
                    "family": next((f for f in FAMILIES if cid.startswith(FAMILIES[f][0])), ""),
                    "candidate": cid,
                    "decision": "exclusion rule not triggered (corridor not generated)",
                    "reason": f"{e['reason']} ({e['decision']})",
                }
            )
    return out


AIRPORT_NODES = Path("cities/ksa/zones/economic_nodes.parquet")


def airport_points(path: Path = AIRPORT_NODES) -> pd.DataFrame | None:
    """Airport points (aerodrome centroids, a proxy for the terminal) for A-station-001."""
    if not path.exists():
        return None
    nodes = pd.read_parquet(path)
    air = nodes[nodes.role == "airport"].reset_index(drop=True)
    label = air.subtype.str.extract(r"IATA (\w+)")[0].fillna(air.name_en)
    return pd.DataFrame({"label": label, "lat": air.lat, "lon": air.lon})


def siting_check(
    fams: dict[str, list[dict]], airports: pd.DataFrame, decisions: list[dict[str, Any]]
) -> dict[str, list[dict]]:
    """A-station-001 (adopted 6 Nov 2026): main stations are not colocated on airport land.

    Checks every station the generator adds (source not `stations.geojson`, class not `airport`)
    against the airport points: within ON_AIRPORT_KM a station addition is refused (the new
    station is the whole candidate) and a station of any other family is flagged in
    `siting_flags` for a site search. Nothing is moved; each case is a decision row. A corridor
    with no such station is returned unchanged (byte-identical output)."""
    from rail.station_inventory import ON_AIRPORT_KM

    out: dict[str, list[dict]] = {}
    for fam, items in fams.items():
        keep = []
        for c in items:
            hits = []
            for st in c["stations"]:
                if str(st.get("source", "")).startswith("stations.geojson"):
                    continue  # existing or committed station: kept as recorded (P3, P4)
                if st.get("class") == "airport":
                    continue  # an airport halt is allowed as an extra stop
                d = gc_km(st["lat"], st["lon"], airports.lat.to_numpy(), airports.lon.to_numpy())
                i = int(np.argmin(d))
                if float(d[i]) <= ON_AIRPORT_KM:
                    hits.append((st, str(airports.label.iloc[i]), float(d[i])))
            if not hits:
                keep.append(c)
                continue
            where = "; ".join(f"{st['id']} {km:.2f} km from {a}" for st, a, km in hits)
            if fam == "station_addition":
                decisions.append(
                    {
                        "family": fam,
                        "candidate": c["id"],
                        "decision": "refused by siting rule A-station-001 (on airport land)",
                        "reason": f"{where}; a city station must serve the urban catchment",
                    }
                )
                continue
            c = c | {
                "siting_flags": [
                    {
                        "station": st["id"],
                        "airport": a,
                        "distance_km": round(km, 2),
                        "flag": "on airport land (A-station-001): site search needed",
                    }
                    for st, a, km in hits
                ]
            }
            decisions.append(
                {
                    "family": fam,
                    "candidate": c["id"],
                    "decision": "flagged by siting rule A-station-001 (on airport land)",
                    "reason": f"{where}; not moved: a site search should apply the rule",
                }
            )
            keep.append(c)
        out[fam] = keep
    return out


def scenario(fid: str, fam: str, files: list[str], decisions: list[dict], src: str) -> dict:
    sid, kind, title = FAMILIES[fam]
    s1 = yaml.safe_load(Path("scenarios/S1.yaml").read_text(encoding="utf-8"))
    return {
        "id": sid,
        "kind": kind,
        "title": f"{sid} {title} (generated)",
        "layers": ["existing", "committed", "hypothetical"],
        "baseline": "S1",
        "lines": {"include": s1["lines"]["include"]},
        "candidates": files,
        "candidates_uncosted": files,
        "dominated_or_merged": [d for d in decisions if d["family"] == fam],
        "population_scenario": "base-2022",
        "gigaproject_addon": "none",
        "demand_params": "cities/ksa/assumptions/demand.yaml",
        "mode_choice_params": "cities/ksa/assumptions/modechoice.yaml",
        "costs": "cities/ksa/costs/cost_register.yaml",
        "appraisal": "cities/ksa/assumptions/appraisal.yaml",
        "seed": 1,
        "sensitivity": {"band": "P10/P50/P90", "draws": 1000},
        "labels": [LABEL_TEXT, "screening input, not a forecast"],
        "source": f"prompts/R2.md task 4; {src}",
    }


def _py(o: Any) -> Any:
    if isinstance(o, dict):
        return {k: _py(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_py(v) for v in o]
    if isinstance(o, np.generic):
        return o.item()
    return o


def _dump(obj: Any, header: str) -> str:
    return header + yaml.safe_dump(_py(obj), allow_unicode=True, sort_keys=False, width=100)


@app.command()
def generate(
    candidates: Path = typer.Option(Path("cities/ksa/candidates.parquet"), "--candidates"),
    scores: Path = typer.Option(Path("runs/r2/score/scores.parquet"), "--scores"),
    rules: Path = typer.Option(RULES, "--rules"),
    weights: Path = typer.Option(WEIGHTS, "--weights"),
    out: Path = typer.Option(Path("cities/ksa/corridors"), "--out"),
    scenarios_dir: Path = typer.Option(Path("scenarios"), "--scenarios"),
    run_dir: Path = typer.Option(Path("runs/r2/corridors"), "--run-dir"),
    seed: int = typer.Option(1, "--seed", min=0, help="recorded (generation is deterministic)"),
    alignments: Path = typer.Option(None, "--alignments", help="R4_ALIGN routed sidecars"),
    alternatives_out: Path = typer.Option(None, "--alternatives-out"),
) -> None:
    """Generate the four families and S2..S5."""
    ctx = Ctx(candidates, scores, rules, weights, seed)
    ctx.alignments = alignments
    fams = {
        "trunk_gap": trunk_gaps(ctx),
        "branch_spur": branches_spurs(ctx),
        "commuter_belt": commuter_belts(ctx),
        "station_addition": station_additions(ctx),
    }
    fams = apply_exclusions(fams, ctx.rules, ctx.decisions)  # R5 H4a (additive)
    air = airport_points()
    if air is not None:  # A-station-001 (FIX_HHR_REROUTE, additive)
        fams = siting_check(fams, air, ctx.decisions)
    if out.exists():
        shutil.rmtree(out)
    hdr = sketch_hdr = (
        "# Generated by screening.corridors (R2); do not edit by hand. Hypothetical layer, "
        "indicative sketch alignment, uncosted.\n# Label: screening input, not a forecast.\n"
    )
    if alignments is not None:
        hdr = (
            "# Generated by screening.corridors (R2 rules, R4_ALIGN routed alignments: "
            f"--alignments {alignments.as_posix()}); do not edit by hand. Hypothetical layer, "
            "routed alignment (indicative, not a design), uncosted.\n"
            "# Label: screening input, not a forecast.\n"
        )
    counts = {}
    for fam, items in fams.items():
        files = []
        ids = [c["id"] for c in items]
        if len(ids) != len(set(ids)):
            raise ValueError(f"duplicate corridor ids in {fam}")
        for c in items:
            p = out / fam / f"{c['id']}.yaml"
            p.parent.mkdir(parents=True, exist_ok=True)
            routed = (c.get("alignment_routed") or {}).get("status") == "routed"
            p.write_text(_dump(c, hdr if routed else sketch_hdr), encoding="utf-8")
            files.append(str(p))
        sc = scenario(FAMILIES[fam][0], fam, files, ctx.decisions, ctx.src)
        sp = scenarios_dir / f"{FAMILIES[fam][0]}.yaml"
        sp.write_text(
            _dump(
                sc,
                f"# Scenario {sc['id']}: generated by screening.corridors "
                "(R2). Schema: .claude/skills/scenario-yaml/SKILL.md.\n",
            ),
            encoding="utf-8",
        )
        counts[fam] = len(items)
    run_dir.mkdir(parents=True, exist_ok=True)
    if alternatives_out is not None:
        for c in ctx.alternatives:
            p = alternatives_out / f"{c['id']}.yaml"
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(_dump(c, hdr), encoding="utf-8")
    pd.DataFrame(ctx.decisions).to_csv(run_dir / "decisions.csv", index=False)
    rows = [
        {
            "family": f,
            "id": c["id"],
            "rule": c["rule_id"],
            "line_type": c["line_type"],
            "length_km": c["length_km"],
            "stations": len(c["stations"]),
            "generated_from": ";".join(c["generated_from_ids"]),
            "terrain": json.dumps(c["terrain_shares"]),
            "tunnel": c["structures_share"]["tunnel"],
            "viaduct": c["structures_share"]["viaduct"],
        }
        for f, items in fams.items()
        for c in items
    ]
    pd.DataFrame(rows).to_csv(run_dir / "corridors.csv", index=False)
    summary = {"label": LABEL, "counts": counts, "decisions": len(ctx.decisions)}
    write_meta(
        run_dir,
        seed,
        {"candidates": sha12(candidates), "scores": sha12(scores), "rules": sha12(rules)},
        {"step": "screening.corridors", **summary},
    )
    typer.echo(json.dumps(summary))


@app.command()
def validate(
    path: Path = typer.Argument(Path("cities/ksa/corridors")),
    rules: Path = typer.Option(RULES, "--rules", help="exclude_corridors are rejected (R5 H4a)"),
) -> None:
    """Validate every corridor YAML against CorridorSpec (line-yaml + corridor fields)."""
    files = sorted(path.rglob("*.yaml")) if path.is_dir() else [path]
    excluded = {e["id"] for e in exclusions(yaml.safe_load(rules.read_text(encoding="utf-8")))}
    for f in files:
        c = yaml.safe_load(f.read_text(encoding="utf-8"))
        CorridorSpec.model_validate(c)
        if c["layer"] != "hypothetical" or not c.get("rule_id") or not c.get("generated_from_ids"):
            raise typer.BadParameter(f"{f}: needs layer hypothetical, rule_id, generated_from_ids")
        if c["id"] in excluded:
            raise typer.BadParameter(f"{f}: {c['id']} is excluded by exclude_corridors ({rules})")
    typer.echo(f"ok {len(files)} corridor files")


if __name__ == "__main__":
    app()
