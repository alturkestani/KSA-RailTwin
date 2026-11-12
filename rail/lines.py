"""Line YAML build and validation (skill `line-yaml`).

`build` turns the hand-written specs in `rail/specs/<id>.yaml` (published facts with source ids,
station lists referencing OSM elements or sourced coordinates) into:
- `cities/ksa/lines/<id>.yaml`               LineSpec (common/schemas.py)
- `cities/ksa/lines/geojson/<id>.geojson`    the line's alignment (OSM route ways for existing and
                                            historical lines; an indicative polyline through the
                                            station sites for committed lines, with uncertainty_km)
- `cities/ksa/lines/stations.geojson`        every station of every line with `location_method`
- `cities/ksa/lines/geojson/{existing,committed,historical}.geojson`  alignments by layer

km-posts: shortest path along the OSM track between consecutive stations (route ways when the spec
names an OSM route relation, else every in-service track), or `published` km-posts from the spec,
or for committed lines the great-circle chain between station sites (flagged in the station's
`km_method`).

CLI:
  uv run python -m rail.lines build [--only hhr]   (merges: located stations are preserved)
  uv run python -m rail.lines apply-sites [--sites rail/station_research.yaml]
  uv run python -m rail.lines validate cities/ksa/lines/
"""

from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path
from typing import Any

import networkx as nx
import numpy as np
import typer
import yaml
from pydantic import ValidationError
from scipy.spatial import cKDTree
from shapely.geometry import LineString, MultiLineString, Point, mapping, shape

from common import REPO_ROOT
from common.schemas import LineSpec
from rail.osm import OSM_CREDIT, haversine_km, parse_opl

SPECS = Path("rail/specs")
LINES = Path("cities/ksa/lines")
GEOJSON = LINES / "geojson"
RAIL_OPL = Path("data/ksa/osm/ksa-rail.opl")
PLACES_SEQ = Path("data/ksa/osm/gcc-places.geojsonseq")
BRIDGE_KM = 0.3  # A-r1a-005: join OSM track gaps up to 300 m (mapping gaps)
STATION_OFF_LINE_KM = 2.0  # line-yaml skill: report stations > 2 km off the alignment
TRACK_TAGS = {"rail", "subway", "light_rail", "monorail", "narrow_gauge", "abandoned", "disused"}
LINE_FIELDS = set(LineSpec.model_fields) | {"from", "class"}

app = typer.Typer(add_completion=False, help="Line YAML: build from specs, validate.")


# ----------------------------------------------------------------------------- OSM helpers
class OsmIndex:
    """Nodes, ways and relations of the KSA rail extract, plus place nodes for proxies."""

    def __init__(self, root: Path):
        self.nodes, self.ways, self.rels = parse_opl(root / RAIL_OPL)
        self.places: dict[int, tuple[float, float, dict]] = {}
        seq = root / PLACES_SEQ
        if seq.exists():
            for line in seq.open(encoding="utf-8"):
                line = line.strip().lstrip("\x1e")
                if line:
                    f = json.loads(line)
                    if f["properties"].get("@type") == "node":
                        lon, lat = f["geometry"]["coordinates"]
                        self.places[int(f["properties"]["@id"])] = (lon, lat, f["properties"])

    def element_point(self, ref: str) -> tuple[float, float]:
        """'node/123' or 'way/456' (centroid) -> (lat, lon)."""
        kind, _, oid = ref.partition("/")
        i = int(oid)
        if kind == "node":
            if i in self.nodes:
                lon, lat, _ = self.nodes[i]
            elif i in self.places:
                lon, lat, _ = self.places[i]
            else:
                raise KeyError(f"OSM {ref} not in the rail extract or the place nodes")
            return lat, lon
        if kind == "way":
            nds = self.ways[i][0]
            pts = [self.nodes[n] for n in nds if n in self.nodes]
            return float(np.mean([p[1] for p in pts])), float(np.mean([p[0] for p in pts]))
        raise ValueError(f"unsupported OSM ref {ref}")

    def route_ways(self, rel_ids: list[int]) -> list[int]:
        out: list[int] = []
        for r in rel_ids:
            members, _ = self.rels[r]
            out += [m[1] for m in members if m[0] == "w" and m[1] in self.ways]
        return list(dict.fromkeys(out))

    def track_ways(self, kinds: set[str]) -> list[int]:
        return [w for w, (_, t) in self.ways.items() if t.get("railway") in kinds]

    def graph(self, way_ids: list[int], bridge_km: float = BRIDGE_KM) -> nx.Graph:
        """Track graph; dangling ends within `bridge_km` of another component are joined
        (mapping gaps in OSM; edges flagged `bridge=True`, counted in g.graph['bridges'])."""
        g = nx.Graph()
        for w in way_ids:
            nds = [n for n in self.ways[w][0] if n in self.nodes]
            for a, b in zip(nds, nds[1:], strict=False):
                la, lb = self.nodes[a], self.nodes[b]
                g.add_edge(a, b, km=haversine_km(la[1], la[0], lb[1], lb[0]))
        comp = {n: i for i, c in enumerate(nx.connected_components(g)) for n in c}
        ids = list(g.nodes)
        tree = cKDTree(_xyz([self.nodes[n][1] for n in ids], [self.nodes[n][0] for n in ids]))
        bridges = 0
        for n in [n for n in ids if g.degree(n) == 1]:
            lon, lat, _ = self.nodes[n]
            for j in tree.query_ball_point(_xyz([lat], [lon])[0], bridge_km / 6371.0088):
                m = ids[j]
                if comp[m] != comp[n] and not g.has_edge(n, m):
                    lm = self.nodes[m]
                    g.add_edge(n, m, km=haversine_km(lat, lon, lm[1], lm[0]), bridge=True)
                    bridges += 1
                    break
        g.graph["bridges"] = bridges
        return g


def _xyz(lat, lon):
    la, lo = np.radians(lat), np.radians(lon)
    return np.c_[np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)]


def snap(g: nx.Graph, osm: OsmIndex, pts: list[tuple[float, float]]) -> list[tuple[int, float]]:
    ids = list(g.nodes)
    tree = cKDTree(_xyz([osm.nodes[n][1] for n in ids], [osm.nodes[n][0] for n in ids]))
    out = []
    for lat, lon in pts:
        d, j = tree.query(_xyz([lat], [lon])[0])
        out.append((ids[j], float(d * 6371.0088)))
    return out


def path_km_and_coords(g: nx.Graph, osm: OsmIndex, a: int, b: int):
    try:
        path = nx.shortest_path(g, a, b, weight="km")
    except nx.NetworkXNoPath:
        return None, []
    km = sum(g.edges[u, v]["km"] for u, v in zip(path, path[1:], strict=False))
    return km, [(osm.nodes[n][0], osm.nodes[n][1]) for n in path]


# ----------------------------------------------------------------------------- build
def load_spec(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def slug(text: str) -> str:
    out = "".join(c.lower() if c.isalnum() else "-" for c in text)
    while "--" in out:
        out = out.replace("--", "-")
    return out.strip("-") or "station"


def stations_from_route(spec: dict, osm: OsmIndex) -> list[dict]:
    """Ordered named stop nodes of an OSM route relation (`stations_from_route: <rel id>`)."""
    rid = spec["stations_from_route"]
    members, _ = osm.rels[rid]
    out, seen = [], set()
    skip = set(spec.get("skip_osm_nodes", []))
    for mtype, mid, role in members:
        if mtype != "n" or mid not in osm.nodes or mid in skip:
            continue
        if not (role.startswith("stop") or role == ""):
            continue
        tags = osm.nodes[mid][2]
        en = spec.get("names_en", {}).get(mid) or tags.get("name:en") or tags.get("name")
        ar = tags.get("name:ar") or tags.get("name")
        if not en:
            continue
        sid = slug(en)
        if sid in seen:
            continue
        seen.add(sid)
        out.append(
            {
                "id": sid,
                "name_en": en,
                "name_ar": ar,
                "class": "intermediate",
                "source": spec["station_source"],
                "osm": f"node/{mid}",
            }
        )
    out += list(spec.get("extra_stations", []))
    if spec.get("order_by") == "lat_desc":  # relation member order is not running order
        for s in out:
            s["_lat"] = osm.element_point(s["osm"])[0]
        out.sort(key=lambda s: -s.pop("_lat"))
    for s in out:
        s["class"] = "intermediate" if s["class"] == "terminal" else s["class"]
    out[0]["class"] = out[-1]["class"] = "terminal"
    return out


def station_points(spec: dict, osm: OsmIndex) -> list[dict]:
    out = []
    listed = spec.get("stations") or stations_from_route(spec, osm)
    for s in listed:
        s = dict(s)
        if "osm" in s:
            lat, lon = osm.element_point(s["osm"])
            s["lat"], s["lon"] = round(lat, 6), round(lon, 6)
            s.setdefault("location_method", f"osm:{s['osm']}")
        elif "proxy_osm" in s:  # unlocated planned site: town centroid used as a flagged proxy
            lat, lon = osm.element_point(s["proxy_osm"])
            s["lat"], s["lon"] = round(lat, 6), round(lon, 6)
            s.setdefault("location_method", f"unlocated:town_centroid_proxy:osm:{s['proxy_osm']}")
        elif "lat" not in s:
            raise ValueError(f"{spec['id']}:{s['id']} has no osm ref, proxy or lat/lon")
        out.append(s)
    return out


def compute_km_posts(spec: dict, stations: list[dict], osm: OsmIndex) -> tuple[list, Any, str]:
    """Return (km_posts, alignment parts [(name, coords)], method); part 0 is the main line."""
    method = spec.get("km_method", "osm_track")
    pts = [(s["lat"], s["lon"]) for s in stations]
    if method == "published":
        kms = [float(s["km_post"]) for s in stations]
        return kms, [("main", [(p[1], p[0]) for p in pts])], "published km-posts (spec source ids)"
    if method == "great_circle":
        kms, acc = [0.0], 0.0
        for a, b in zip(pts, pts[1:], strict=False):
            acc += haversine_km(a[0], a[1], b[0], b[1])
            kms.append(round(acc, 1))
        return (
            kms,
            [("main", [(p[1], p[0]) for p in pts])],
            "great-circle chain between station sites",
        )
    rel = spec.get("osm_route") if spec.get("km_source") == "route" else None
    rels = rel if isinstance(rel, list) else ([rel] if rel else [])
    kinds = set(spec.get("osm_track", ["rail"]))
    ways = osm.route_ways(rels) if rels else osm.track_ways(kinds)
    g = osm.graph(ways)
    snaps = snap(g, osm, pts)
    kms, coords = [0.0], []
    branch_segs: list[tuple[str, list]] = []  # (branch station id, path from its main station)
    fallbacks = 0
    last_main = 0  # index of the last main-line station (branch stations hang off it)
    acc_main = 0.0
    for i in range(1, len(stations)):
        a, b = snaps[last_main][0], snaps[i][0]
        km, seg = path_km_and_coords(g, osm, a, b)
        if km is None and spec.get("km_fallback") == "great_circle":
            pa, pb = osm.nodes[a], osm.nodes[b]
            km, seg = haversine_km(pa[1], pa[0], pb[1], pb[0]), [pa[:2], pb[:2]]
            fallbacks += 1
        if km is None:
            raise ValueError(f"{spec['id']}:{stations[i]['id']}: no OSM track path")
        kms.append(round(acc_main + km, 2))
        if stations[i].get("branch"):
            # FIX_HHR_JEDDAH: a branch is its own part. Appending it to the main path stitched a
            # straight chord from the branch end back to the last main station.
            branch_segs.append((stations[i]["id"], seg))
        else:
            coords += seg if not coords else seg[1:]
            last_main, acc_main = i, acc_main + km
    for s, (n, d) in zip(stations, snaps, strict=True):
        s["snap_km"] = round(d, 3)
        if "proxy_osm" in s:  # put the inferred site on the track, nearest to the proxy place
            s["lat"], s["lon"] = round(osm.nodes[n][1], 6), round(osm.nodes[n][0], 6)
            s["location_method"] = (
                f"unlocated:track_node_nearest_to_osm:{s['proxy_osm']} (snap {d:.1f} km)"
            )
    src = f"relation(s) {rels}" if rels else f"OSM track {sorted(kinds)}"
    src += f"; {g.graph['bridges']} gaps <= {BRIDGE_KM} km bridged"
    if fallbacks:
        src += f"; {fallbacks} segments without a track path use the great-circle distance"
    parts = [("main", coords)] + branch_parts(coords, branch_segs)
    return kms, parts, f"cumulative shortest path along {src} between consecutive stations"


def branch_parts(main: list, branch_segs: list[tuple[str, list]]) -> list[tuple[str, list]]:
    """Cut each branch path at the junction: its last vertex on the main part (the shared stretch
    from the main station to the junction is already drawn by the main part)."""
    on_main = {tuple(p) for p in main}
    out = []
    for sid, seg in branch_segs:
        k = max((j for j, p in enumerate(seg) if tuple(p) in on_main), default=0)
        out.append((f"branch:{sid}", seg[k:]))
    return out


def parts_geometry(parts: list[tuple[str, list]]) -> dict:
    """One part -> LineString (unchanged for lines without a branch); several -> MultiLineString."""
    if len(parts) == 1:
        return mapping(LineString(parts[0][1]))
    return mapping(MultiLineString([p[1] for p in parts]))


def path_km(coords: list) -> float:
    return sum(
        haversine_km(a[1], a[0], b[1], b[0]) for a, b in zip(coords, coords[1:], strict=False)
    )


def to_line_yaml(spec: dict, stations: list[dict], kms: list[float]) -> dict:
    line = {"id": spec["id"], **spec["line"]}
    line["stations"] = [
        {
            "id": s["id"],
            "name_en": s["name_en"],
            "name_ar": s["name_ar"],
            "km_post": km,
            "lat": s["lat"],
            "lon": s["lon"],
            "class": s["class"],
            "source": s["source"],
        }
        for s, km in zip(stations, kms, strict=True)
    ]
    if spec.get("alignment", True):
        line["alignment"] = f"cities/ksa/lines/geojson/{spec['id']}.geojson"
    return line


def _dump(obj: Any) -> str:
    return yaml.safe_dump(obj, sort_keys=False, allow_unicode=True, width=100)


@app.command()
def build(
    only: str = typer.Option("", help="comma-separated spec ids (default: all)"),
    root: Path = typer.Option(REPO_ROOT, hidden=True),
) -> None:
    """Build line YAMLs, per-line alignments, stations.geojson and layer files from rail/specs."""
    osm = OsmIndex(root)
    wanted = {x for x in only.split(",") if x}
    specs = sorted((root / SPECS).glob("*.yaml"))
    by_layer: dict[str, list] = {"existing": [], "committed": [], "historical": []}
    station_feats: list[dict] = []
    for path in specs:
        spec = load_spec(path)
        if wanted and spec["id"] not in wanted:
            continue
        stations = station_points(spec, osm)
        kms, parts, method = compute_km_posts(spec, stations, osm)
        line = to_line_yaml(spec, stations, kms)
        LineSpec.model_validate(line)
        header = (
            f"# {spec['id']}: generated by `uv run python -m rail.lines build` from "
            f"rail/specs/{path.name}; do not edit by hand.\n"
            f"# Geometry and station coordinates: {OSM_CREDIT} where location_method is osm:*.\n"
            f"# km-post method: {method}.\n"
        )
        (root / LINES / f"{spec['id']}.yaml").write_text(header + _dump(line), encoding="utf-8")
        layer = line["layer"]
        props = {
            "line_id": spec["id"],
            "name_en": line["name_en"],
            "name_ar": line["name_ar"],
            "layer": layer,
            "status": line["status"],
            "operator": line.get("operator"),
            "source": line["source"],
            "source_date": str(line.get("source_date") or ""),
            "accessed": str(line.get("accessed") or ""),
            "km_method": method,
            "alignment_km": round(sum(path_km(c) for _, c in parts), 2),
            "uncertainty_km": line.get("uncertainty_km"),
        }
        if len(parts) > 1:  # main line + branch stubs (FIX_HHR_JEDDAH)
            props["parts"] = [n.split(":")[0] for n, _ in parts]
            props["part_to"] = [n.split(":")[1] if ":" in n else None for n, _ in parts]
            props["part_km"] = [round(path_km(c), 2) for _, c in parts]
        feat = {"type": "Feature", "properties": props, "geometry": parts_geometry(parts)}
        fc = {
            "type": "FeatureCollection",
            "name": spec["id"],
            "attribution": OSM_CREDIT,
            "licence": "ODbL-1.0 (derived database of OpenStreetMap) where km_method is OSM",
            "features": [feat],
        }
        (root / GEOJSON).mkdir(parents=True, exist_ok=True)
        (root / GEOJSON / f"{spec['id']}.geojson").write_text(
            json.dumps(fc, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8"
        )
        by_layer.setdefault(layer, []).append(feat)
        for s, km in zip(stations, kms, strict=True):
            station_feats.append(
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [s["lon"], s["lat"]]},
                    "properties": {
                        "station_uid": f"{spec['id']}:{s['id']}",
                        "line_id": spec["id"],
                        "station_id": s["id"],
                        "name_en": s["name_en"],
                        "name_ar": s["name_ar"],
                        "class": s["class"],
                        "layer": layer,
                        "status": line["status"],
                        "operator": line.get("operator"),
                        "opened": str(s.get("opened", spec.get("opened")) or "") or None,
                        "km_post": km,
                        "source": s["source"],
                        "location_method": s.get("location_method", "published_coordinates"),
                        "located": not str(s.get("location_method", "")).startswith("unlocated"),
                        "uncertainty_km": s.get("uncertainty_km", line.get("uncertainty_km")),
                        "snap_km": s.get("snap_km"),
                        "site_status": s.get("site_status"),
                        "notes": s.get("notes"),
                        "confidence": s.get("confidence"),
                    },
                }
            )
        typer.echo(f"{spec['id']}: {len(stations)} stations, last km {kms[-1]} ({method})")
    if wanted:
        return
    for layer, feats in by_layer.items():
        fc = {
            "type": "FeatureCollection",
            "name": layer,
            "attribution": OSM_CREDIT,
            "layer": layer,
            "features": feats,
        }
        (root / GEOJSON / f"{layer}.geojson").write_text(
            json.dumps(fc, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8"
        )
    kept = preserve_located(station_feats, root / LINES / "stations.geojson")
    typer.echo(f"stations.geojson: {kept} located stations preserved from the previous file")
    fc = {
        "type": "FeatureCollection",
        "name": "stations",
        "attribution": OSM_CREDIT,
        "generated": dt.date.today().isoformat(),
        "features": station_feats,
    }
    (root / LINES / "stations.geojson").write_text(
        json.dumps(fc, ensure_ascii=False, indent=0) + "\n", encoding="utf-8"
    )


# CP2_PREP item 6: a rebuild merges, it never overwrites a geo- or research-located station.
LOCATION_KEYS = (
    "location_method",
    "located",
    "uncertainty_km",
    "snap_km",
    "site_status",
    "confidence",
    "notes",
)


def preserve_located(new_feats: list[dict], old_path: Path) -> int:
    """Keep the previous site of every station the build would put back to `unlocated:*`.

    A station located by GEO_VERIFY (`screening.geo_verify stations --apply`) or by research
    (`rail.lines apply-sites`) has a location_method that is not `unlocated:*`; a rebuild from the
    specs can only produce `osm:*` or `unlocated:*`. If the rebuild yields `unlocated:*` for a
    station whose previous record was located, geometry and LOCATION_KEYS are copied over. A
    station that OSM now places (`osm:*`) takes the new OSM position; a station that stays
    unlocated keeps its previous notes (the research trail). Returns the count kept.
    """
    if not old_path.exists():
        return 0
    old = {
        f["properties"]["station_uid"]: f
        for f in json.loads(old_path.read_text(encoding="utf-8"))["features"]
    }
    kept = 0
    for f in new_feats:
        prev = old.get(f["properties"]["station_uid"])
        if prev is None:
            continue
        was = str(prev["properties"].get("location_method") or "")
        now = str(f["properties"].get("location_method") or "")
        if now.startswith("unlocated") and was and not was.startswith("unlocated"):
            f["geometry"] = prev["geometry"]
            for k in LOCATION_KEYS:
                f["properties"][k] = prev["properties"].get(k)
            kept += 1
        elif now.startswith("unlocated") and not f["properties"].get("notes"):
            # still unlocated: keep the research record of what was searched
            f["properties"]["notes"] = prev["properties"].get("notes")
    return kept


@app.command("apply-sites")
def apply_sites(
    sites: Path = typer.Option(Path("rail/station_research.yaml"), help="research outcomes"),
    root: Path = typer.Option(REPO_ROOT, hidden=True),
) -> None:
    """Write researched station sites (outcome resolved | low_confidence) into stations.geojson.

    `unlocated` outcomes keep their point and only record the method and what was searched.
    """
    path = root / LINES / "stations.geojson"
    gj = json.loads(path.read_text(encoding="utf-8"))
    entries = yaml.safe_load((sites if sites.is_absolute() else root / sites).read_text("utf-8"))
    by = {e["station_uid"]: e for e in entries["stations"]}
    counts: dict[str, int] = {}
    for f in gj["features"]:
        e = by.pop(f["properties"]["station_uid"], None)
        if e is None:
            continue
        pr = f["properties"]
        counts[e["outcome"]] = counts.get(e["outcome"], 0) + 1
        refs = ", ".join(e.get("sources") or [])
        if e["outcome"] == "unlocated":
            pr["notes"] = f"{e.get('notes') or ''} [CP2_PREP research: {refs}]".strip()
            continue
        f["geometry"] = {"type": "Point", "coordinates": [e["lon"], e["lat"]]}
        pr.update(
            location_method=e["location_method"],
            located=e["outcome"] == "resolved",
            uncertainty_km=e.get("uncertainty_km"),
            confidence=e.get("confidence"),
            notes=f"{e.get('notes') or ''} [CP2_PREP research: {refs}]".strip(),
        )
    if by:
        raise typer.BadParameter(f"unknown station_uid(s): {sorted(by)}")
    path.write_text(json.dumps(gj, ensure_ascii=False, indent=0) + "\n", encoding="utf-8")
    typer.echo(f"apply-sites: {counts}")


# ----------------------------------------------------------------------------- validate
def check_line(path: Path, root: Path) -> list[str]:
    errs: list[str] = []
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        line = LineSpec.model_validate(data)
    except (ValidationError, yaml.YAMLError) as e:
        return [f"{path.name}: schema: {e}"]
    if line.layer == "committed" and line.uncertainty_km is None:
        errs.append(f"{path.name}: committed line needs uncertainty_km")
    if line.layer in ("existing", "committed") and not line.source.startswith("S-"):
        errs.append(f"{path.name}: source must be an S- id")
    for s in line.stations:
        if not s.source.startswith("S-") and not line.fixture:
            errs.append(f"{path.name}:{s.id}: station source must be an S- id")
    if line.alignment:
        apath = root / line.alignment
        if not apath.exists():
            errs.append(f"{path.name}: alignment file {line.alignment} missing")
        else:
            fc = json.loads(apath.read_text(encoding="utf-8"))
            geom = shape(fc["features"][0]["geometry"])
            if line.layer != "committed":  # committed polylines pass through stations by design
                for s in line.stations:
                    d_deg = geom.distance(Point(s.lon, s.lat))
                    if d_deg * 111.32 > STATION_OFF_LINE_KM:
                        errs.append(
                            f"{path.name}:{s.id}: station ~{d_deg * 111.32:.1f} km off alignment"
                        )
    return errs


@app.command()
def validate(
    target: Path = typer.Argument(LINES),
    root: Path = typer.Option(REPO_ROOT, hidden=True),
) -> None:
    """Validate one line YAML or every *.yaml in a directory; exit 1 on any error."""
    t = target if target.is_absolute() else root / target
    files = sorted(t.glob("*.yaml")) if t.is_dir() else [t]
    errs: list[str] = []
    for f in files:
        errs += check_line(f, root)
    for e in errs:
        typer.echo(f"FAIL {e}")
    typer.echo(f"{len(files)} line files, {len(errs)} errors")
    if errs:
        sys.exit(1)


if __name__ == "__main__":
    app()
