"""OSM rail layers for Saudi Arabia (skill `osm-ksa-rail-network`).

Reads the Geofabrik GCC extract (ODbL; manifest row `osm-gcc-2026-10-14`) with osmium-tool, keeps
the features inside Saudi Arabia (OSM relation 307584) and writes:

- `data/ksa/osm/ksa-rail.osm.pbf` + `.opl`  rail objects (gitignored, regenerable)
- `data/ksa/osm/routes.json`  route relations with ordered stops (input to line YAMLs)
- `cities/ksa/lines/geojson/osm_raw.geojson` every rail way inside KSA with its OSM tags of interest
- `cities/ksa/lines/geojson/existing_osm.geojson`  in-service track (railway=rail/subway/
  light_rail/monorail/narrow_gauge), `layer: existing` (OSM evidence only; the line YAML
  carries the operator)
- `cities/ksa/lines/geojson/historical_osm.geojson` railway=abandoned/disused, `layer: historical`
- `cities/ksa/lines/geojson/osm_construction_proposed.geojson` railway=construction/proposed:
  `layer: unassigned` (OSM is not an announcement; rule 5), never used by a scenario
- `cities/ksa/lines/geojson/osm_stations.geojson`   railway=station/halt nodes and station areas

Every output is a derived database of OpenStreetMap: (c) OpenStreetMap contributors, ODbL 1.0.

CLI:
  uv run python -m rail.osm extract [--pbf data/osm/gcc-states-latest.osm.pbf]
  uv run python -m rail.osm summary
"""

from __future__ import annotations

import json
import math
import re
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any

import typer
from shapely.geometry import LineString, Point, mapping, shape
from shapely.ops import unary_union
from shapely.prepared import prep

from common import REPO_ROOT

OSM_CREDIT = "(c) OpenStreetMap contributors, ODbL 1.0 (https://www.openstreetmap.org/copyright)"
KSA_RELATION = 307584  # OSM relation "Saudi Arabia", admin_level=2, ISO3166-1=SA
SOURCE_OSM = "osm-gcc-2026-10-14"  # manifest id of the GCC extract

DEFAULT_PBF = Path("data/osm/gcc-states-latest.osm.pbf")
OSM_DIR = Path("data/ksa/osm")
GEOJSON_DIR = Path("cities/ksa/lines/geojson")
KSA_BOUNDARY = Path("cities/ksa/zones/ksa.geojson")

RAIL_FILTER = [
    "r/route=train,railway,subway,light_rail,monorail",
    "w/railway",
    "nw/railway=station,halt,stop",
    "nw/public_transport=station",
]
IN_SERVICE = {"rail", "subway", "light_rail", "monorail", "narrow_gauge"}
HISTORICAL = {"abandoned", "disused"}
PLANNED = {"construction", "proposed"}
KEEP_TAGS = [
    "railway",
    "service",
    "usage",
    "name",
    "name:en",
    "name:ar",
    "operator",
    "electrified",
    "gauge",
    "maxspeed",
    "tracks",
    "construction",
    "proposed",
    "disused",
    "abandoned",
    "start_date",
    "historic",
    "ref",
]

app = typer.Typer(add_completion=False, help="OSM rail layers for Saudi Arabia (ODbL).")

_ESC = re.compile(r"%([0-9a-fA-F]+)%")


def opl_unescape(s: str) -> str:
    """OPL escapes non-ASCII and separators as %<hex>%."""
    return _ESC.sub(lambda m: chr(int(m.group(1), 16)), s)


def parse_tags(field: str) -> dict[str, str]:
    if not field:
        return {}
    out = {}
    for kv in field.split(","):
        if "=" in kv:
            k, v = kv.split("=", 1)
            out[opl_unescape(k)] = opl_unescape(v)
    return out


def parse_opl(path: Path) -> tuple[dict, dict, dict]:
    """Return nodes {id: (lon, lat, tags)}, ways {id: (node_ids, tags)},
    relations {id: (members [(type, id, role)], tags)}."""
    nodes: dict[int, tuple[float, float, dict]] = {}
    ways: dict[int, tuple[list[int], dict]] = {}
    rels: dict[int, tuple[list[tuple[str, int, str]], dict]] = {}
    with path.open(encoding="utf-8") as f:
        for line in f:
            parts = line.rstrip("\n").split(" ")
            kind, oid = parts[0][0], int(parts[0][1:])
            fields = {p[0]: p[1:] for p in parts[1:] if p}
            tags = parse_tags(fields.get("T", ""))
            if kind == "n":
                if fields.get("x") and fields.get("y"):
                    nodes[oid] = (float(fields["x"]), float(fields["y"]), tags)
            elif kind == "w":
                nds = [int(n[1:]) for n in fields.get("N", "").split(",") if n]
                ways[oid] = (nds, tags)
            elif kind == "r":
                members = []
                for m in fields.get("M", "").split(","):
                    if not m:
                        continue
                    ref, _, role = m.partition("@")
                    members.append((ref[0], int(ref[1:]), opl_unescape(role)))
                rels[oid] = (members, tags)
    return nodes, ways, rels


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0088  # mean Earth radius (IUGG), km
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def line_km(coords: list[tuple[float, float]]) -> float:
    return sum(
        haversine_km(a[1], a[0], b[1], b[0]) for a, b in zip(coords, coords[1:], strict=False)
    )


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def osmium_version() -> str:
    out = subprocess.run(["osmium", "--version"], capture_output=True, text=True, check=True)
    return out.stdout.splitlines()[0].strip()


def ksa_polygon(root: Path = REPO_ROOT):
    data = json.loads((root / KSA_BOUNDARY).read_text(encoding="utf-8"))
    return shape(data["features"][0]["geometry"])


def _fc(features: list[dict], name: str, extra: dict | None = None) -> dict:
    fc = {
        "type": "FeatureCollection",
        "name": name,
        "attribution": OSM_CREDIT,
        "licence": "ODbL-1.0 (derived database of OpenStreetMap)",
        "source": SOURCE_OSM,
        "features": features,
    }
    if extra:
        fc.update(extra)
    return fc


def write_geojson(path: Path, fc: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(fc, ensure_ascii=False, separators=(",", ":")) + "\n", "utf-8")


def _station_like(tags: dict) -> bool:
    if tags.get("railway") in ("station", "halt"):
        return True
    return tags.get("public_transport") == "station" and any(
        tags.get(k) == "yes" for k in ("train", "subway", "light_rail", "monorail")
    )


def build_layers(nodes: dict, ways: dict, rels: dict, ksa) -> dict[str, Any]:
    """Classify rail ways and stations inside KSA into layer files; collect route relations."""
    pk = prep(ksa)
    raw, existing, historical, planned, stations = [], [], [], [], []
    way_geom: dict[int, LineString] = {}
    for wid, (nds, tags) in ways.items():
        rw = tags.get("railway")
        coords = [(nodes[n][0], nodes[n][1]) for n in nds if n in nodes]
        if not rw or len(coords) < 2:
            continue
        geom = LineString(coords)
        if not pk.intersects(geom):
            continue
        way_geom[wid] = geom
        closed = nds[0] == nds[-1] and len(nds) > 3
        if rw in ("station", "platform") or (closed and rw not in IN_SERVICE | HISTORICAL):
            if rw == "station":
                c = geom.centroid
                stations.append(
                    {
                        "type": "Feature",
                        "geometry": mapping(c),
                        "properties": {
                            "osm_type": "way",
                            "osm_id": wid,
                            **{k: tags.get(k) for k in ("name", "name:en", "name:ar")},
                            "railway": "station",
                            "kind": "station_area_centroid",
                        },
                    }
                )
            continue
        props = {"osm_type": "way", "osm_id": wid, "km": round(line_km(coords), 3)}
        props.update({k: tags[k] for k in KEEP_TAGS if k in tags})
        if rw in IN_SERVICE:
            props["layer"] = "existing"
            existing.append({"type": "Feature", "geometry": mapping(geom), "properties": props})
        elif rw in HISTORICAL:
            props["layer"] = "historical"
            historical.append({"type": "Feature", "geometry": mapping(geom), "properties": props})
        elif rw in PLANNED:
            props["layer"] = "unassigned"
            props["note"] = "OSM construction/proposed tag; not an announcement (rule 5)"
            planned.append({"type": "Feature", "geometry": mapping(geom), "properties": props})
        else:
            props["layer"] = "unassigned"
        raw.append({"type": "Feature", "geometry": mapping(geom), "properties": dict(props)})
    for nid, (lon, lat, tags) in nodes.items():
        if not _station_like(tags) or not pk.contains(Point(lon, lat)):
            continue
        stations.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
                "properties": {
                    "osm_type": "node",
                    "osm_id": nid,
                    **{
                        k: tags.get(k)
                        for k in (
                            "name",
                            "name:en",
                            "name:ar",
                            "operator",
                            "network",
                            "station",
                            "railway",
                            "public_transport",
                            "subway",
                            "train",
                            "light_rail",
                            "disused",
                            "historic",
                            "abandoned",
                            "start_date",
                        )
                    },
                    "kind": "station_node",
                },
            }
        )
    routes = []
    for rid, (members, tags) in rels.items():
        if tags.get("type") != "route":
            continue
        rways = [m[1] for m in members if m[0] == "w" and m[1] in way_geom]
        if not rways:
            continue
        stops = []
        for mtype, mid, role in members:
            if mtype != "n" or mid not in nodes or not (role.startswith("stop") or role == ""):
                continue
            lon, lat, ntags = nodes[mid]
            if not pk.contains(Point(lon, lat)):
                continue
            stops.append(
                {
                    "osm_id": mid,
                    "role": role,
                    "name": ntags.get("name"),
                    "name:en": ntags.get("name:en"),
                    "name:ar": ntags.get("name:ar"),
                    "railway": ntags.get("railway"),
                    "public_transport": ntags.get("public_transport"),
                    "lat": lat,
                    "lon": lon,
                }
            )
        merged = unary_union([way_geom[w] for w in rways])
        routes.append(
            {
                "osm_relation": rid,
                "tags": tags,
                "n_ways": len(rways),
                "track_km_in_ksa": round(sum(line_km(list(way_geom[w].coords)) for w in rways), 3),
                "ways": rways,
                "stops": stops,
                "bounds": list(merged.bounds),
            }
        )
    return {
        "raw": raw,
        "existing": existing,
        "historical": historical,
        "planned": planned,
        "stations": stations,
        "routes": sorted(routes, key=lambda r: r["osm_relation"]),
        "way_geom": way_geom,
    }


def write_ksa_boundary(admin_seq: Path, out: Path) -> None:
    """KSA country polygon from the GCC admin export (relation 307584), simplified ~100 m."""
    for line in admin_seq.open(encoding="utf-8"):
        line = line.strip().lstrip("\x1e")
        if not line:
            continue
        f = json.loads(line)
        p = f["properties"]
        if p.get("@type") == "relation" and p.get("@id") == KSA_RELATION:
            geom = shape(f["geometry"]).simplify(0.001, preserve_topology=True)
            props = {
                "osm_type": "relation",
                "osm_id": KSA_RELATION,
                "name": p.get("name"),
                "name:en": p.get("name:en"),
                "simplify_deg": 0.001,
            }
            fc = _fc([{"type": "Feature", "geometry": mapping(geom), "properties": props}], "ksa")
            write_geojson(out, fc)
            return
    raise RuntimeError(f"relation {KSA_RELATION} not found in {admin_seq}")


@app.command()
def extract(
    pbf: Path = typer.Option(DEFAULT_PBF, help="GCC PBF (read-only symlink)"),
    root: Path = typer.Option(REPO_ROOT, hidden=True),
) -> None:
    """Filter rail and admin objects with osmium and write the layer GeoJSONs and routes.json."""
    osm = root / OSM_DIR
    osm.mkdir(parents=True, exist_ok=True)
    rail_pbf, rail_opl = osm / "ksa-rail.osm.pbf", osm / "ksa-rail.opl"
    admin_pbf, admin_seq = osm / "gcc-admin.osm.pbf", osm / "gcc-admin-areas.geojsonseq"
    src = pbf if pbf.is_absolute() else root / pbf
    run(["osmium", "tags-filter", str(src), *RAIL_FILTER, "-o", str(rail_pbf), "--overwrite"])
    run(["osmium", "cat", str(rail_pbf), "-f", "opl", "-o", str(rail_opl), "--overwrite"])
    run(
        [
            "osmium",
            "tags-filter",
            str(src),
            "r/boundary=administrative",
            "-o",
            str(admin_pbf),
            "--overwrite",
        ]
    )
    run(
        [
            "osmium",
            "export",
            str(admin_pbf),
            "-f",
            "geojsonseq",
            "--geometry-types=polygon",
            "-a",
            "type,id",
            "-o",
            str(admin_seq),
            "--overwrite",
        ]
    )
    write_ksa_boundary(admin_seq, root / KSA_BOUNDARY)
    nodes, ways, rels = parse_opl(rail_opl)
    out = build_layers(nodes, ways, rels, ksa_polygon(root))
    gj = root / GEOJSON_DIR
    meta = {"osmium": osmium_version(), "pbf": str(pbf)}
    write_geojson(gj / "osm_raw.geojson", _fc(out["raw"], "osm_raw", meta))
    write_geojson(gj / "existing_osm.geojson", _fc(out["existing"], "existing_osm", meta))
    write_geojson(gj / "historical_osm.geojson", _fc(out["historical"], "historical_osm", meta))
    write_geojson(
        gj / "osm_construction_proposed.geojson",
        _fc(out["planned"], "osm_construction_proposed", meta),
    )
    write_geojson(gj / "osm_stations.geojson", _fc(out["stations"], "osm_stations", meta))
    (osm / "routes.json").write_text(
        json.dumps(out["routes"], ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    typer.echo(summary_text(out))


def summary_text(out: dict) -> str:
    km = Counter()
    for f in out["raw"]:
        km[f["properties"]["railway"]] += f["properties"]["km"]
    lines = [f"{k}: {v:,.1f} km" for k, v in sorted(km.items())]
    lines.append(f"stations: {len(out['stations'])}; routes: {len(out['routes'])}")
    return "\n".join(lines)


@app.command()
def summary(root: Path = typer.Option(REPO_ROOT, hidden=True)) -> None:
    """Print km by railway tag and counts from the written GeoJSONs."""
    gj = root / GEOJSON_DIR
    for name in (
        "existing_osm",
        "historical_osm",
        "osm_construction_proposed",
        "osm_stations",
    ):
        fc = json.loads((gj / f"{name}.geojson").read_text(encoding="utf-8"))
        km = sum(f["properties"].get("km", 0) for f in fc["features"])
        typer.echo(f"{name}: {len(fc['features'])} features, {km:,.1f} km")


if __name__ == "__main__":
    app()
