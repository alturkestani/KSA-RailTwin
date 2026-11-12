"""Station siting inventory: city vs airport (FIX_HHR_JEDDAH item 2; rule A-station-001,
adopted by Tariq 6 Nov 2026).

For every station in `cities/ksa/lines/stations.geojson` (existing, committed, historical) and every
new station of the S2-S5 corridor files (`cities/ksa/corridors/*/*.yaml`; host stations that point
back to stations.geojson are not repeated), with the S6 layouts that include the corridor:
class, coordinates, distance to the served town's point, distance to the nearest airport point,
and a flag:

- `unplaced`        no site chosen: `located` false in stations.geojson, or `location_method`
                    unlocated:* / a town-centroid proxy
- `airport`         station class `airport` (an airport halt)
- `on-airport-land` within ON_AIRPORT_KM of an airport point (A-station-001 inventory threshold)
- `city`            otherwise

Airport points are the 27 GACA airports of `cities/ksa/zones/economic_nodes.parquet` (OSM aerodrome
features: area centroids, not terminal buildings). The served town is the register row for a
corridor station (`register <row_key>`), the metro reference point for `A-screen-013`, and the
nearest OSM city/town of `settlements.parquet` for stations.geojson rows (a proxy).

CLI:
  uv run python -m rail.station_inventory --out runs/fix-hhr/stations-inventory.csv
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import typer
import yaml

from common import REPO_ROOT
from rail.osm import haversine_km

STATIONS = Path("cities/ksa/lines/stations.geojson")
CORRIDORS = Path("cities/ksa/corridors")
SCENARIOS = Path("scenarios")
NODES = Path("cities/ksa/zones/economic_nodes.parquet")
SETTLEMENTS = Path("cities/ksa/zones/settlements.parquet")
CANDIDATES = Path("cities/ksa/candidates.parquet")
METRO_PARAMS = Path("network/distances_params.yaml")
ON_AIRPORT_KM = 1.5  # A-station-001 (adopted): "on airport land" = within 1.5 km of the terminal
NEAR_AIRPORT_KM = 5.0  # listed for review only
FIELDS = [
    "station_uid",
    "set",
    "layer",
    "name_en",
    "class",
    "lat",
    "lon",
    "location_method",
    "located",
    "served_town",
    "served_town_method",
    "dist_town_km",
    "nearest_airport",
    "dist_airport_km",
    "flag",
    "near_airport_5km",
    "in_s6",
]

app = typer.Typer(add_completion=False, help="Station siting inventory (city vs airport).")


def _nearest(lat: float, lon: float, pts: pd.DataFrame, name: str) -> tuple[str, float]:
    d = np.array([haversine_km(lat, lon, a, b) for a, b in zip(pts.lat, pts.lon, strict=True)])
    i = int(d.argmin())
    return str(pts[name].iloc[i]), float(d[i])


def flag_of(cls: str, method: str, dist_airport: float, located: bool = True) -> str:
    if not located or method.startswith("unlocated") or "centroid_proxy" in method:
        return "unplaced"
    if cls == "airport":
        return "airport"
    if dist_airport <= ON_AIRPORT_KM:
        return "on-airport-land"
    return "city"


def s6_membership(root: Path) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for p in sorted((root / SCENARIOS).glob("S6-L*.yaml")):
        sc = yaml.safe_load(p.read_text(encoding="utf-8"))
        for c in (sc.get("layout") or {}).get("corridors", []):
            out.setdefault(c["id"], []).append(sc["id"])
    return out


def build_rows(root: Path) -> list[dict[str, Any]]:
    nodes = pd.read_parquet(root / NODES)
    air = nodes[nodes.role == "airport"].reset_index(drop=True)
    air = air.assign(label=air.subtype.str.extract(r"IATA (\w+)")[0].fillna(air.name_en))
    sett = pd.read_parquet(root / SETTLEMENTS, columns=["name_en", "place", "lat", "lon"])
    towns = sett[sett.place.isin(["city", "town"])].reset_index(drop=True)
    reg = pd.read_parquet(root / CANDIDATES, columns=["row_key", "name_en", "lat", "lon"])
    reg = reg.set_index("row_key")
    s6 = s6_membership(root)
    rows: list[dict[str, Any]] = []

    def add(uid, set_, layer, name, cls, lat, lon, method, town, town_m, d_town, s6ids, loc=True):
        a, da = _nearest(lat, lon, air, "label")
        rows.append(
            {
                "station_uid": uid,
                "set": set_,
                "layer": layer,
                "name_en": name,
                "class": cls,
                "lat": round(lat, 6),
                "lon": round(lon, 6),
                "location_method": method,
                "served_town": town,
                "served_town_method": town_m,
                "dist_town_km": None if d_town is None else round(d_town, 2),
                "nearest_airport": a,
                "dist_airport_km": round(da, 2),
                "located": loc,
                "flag": flag_of(cls, method, da, loc),
                "near_airport_5km": da <= NEAR_AIRPORT_KM,
                "in_s6": ";".join(s6ids),
            }
        )

    gj = json.loads((root / STATIONS).read_text(encoding="utf-8"))
    for f in gj["features"]:
        p = f["properties"]
        lon, lat = f["geometry"]["coordinates"]
        town, dt = _nearest(lat, lon, towns, "name_en")
        add(
            p["station_uid"],
            "stations.geojson",
            p["layer"],
            p["name_en"],
            p["class"],
            lat,
            lon,
            str(p.get("location_method") or ""),
            town,
            "nearest OSM city/town (proxy)",
            dt,
            [],
            p.get("located") is not False,
        )
    metro = yaml.safe_load((root / METRO_PARAMS).read_text(encoding="utf-8"))
    metro_nodes = {name: spec["osm_node"] for name, spec in metro["metro_cities"]["value"].items()}
    for path in sorted((root / CORRIDORS).glob("*/*.yaml")):
        c = yaml.safe_load(path.read_text(encoding="utf-8"))
        for s in c["stations"]:
            src = str(s.get("source", ""))
            if src.startswith("stations.geojson"):
                continue  # host station: listed once from stations.geojson
            lat, lon = float(s["lat"]), float(s["lon"])
            if src.startswith("register "):
                key = src.split(" ", 1)[1]
                r = reg.loc[key]
                town, dt = str(r.name_en), haversine_km(lat, lon, float(r.lat), float(r.lon))
                tm, method = "register row (town point)", f"town point: {src}"
            else:
                town, dt = _nearest(lat, lon, towns, "name_en")
                tm = "nearest OSM city/town (proxy)"
                method = f"metro reference point: {src}" if src else "unknown"
                hit = [n for n in metro_nodes if n.lower() in s["name_en"].lower()]
                if hit:
                    town = hit[0]
                    tm = "metro reference point (A-screen-013)"
            add(
                f"{c['id']}:{s['id']}",
                f"corridor {c['family']}",
                c["layer"],
                s["name_en"],
                s["class"],
                lat,
                lon,
                method,
                town,
                tm,
                dt,
                s6.get(c["id"], []),
            )
    return rows


@app.command()
def main(
    out: Path = typer.Option(Path("runs/fix-hhr/stations-inventory.csv")),
    root: Path = typer.Option(REPO_ROOT, hidden=True),
) -> None:
    rows = build_rows(root)
    o = out if out.is_absolute() else root / out
    o.parent.mkdir(parents=True, exist_ok=True)
    with o.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    df = pd.DataFrame(rows)
    typer.echo(f"{len(df)} rows -> {out}")
    typer.echo(df.groupby(["set", "flag"]).size().to_string())
    typer.echo(f"near an airport point (<= {NEAR_AIRPORT_KM} km): {int(df.near_airport_5km.sum())}")


if __name__ == "__main__":
    app()
