# ruff: noqa: E501
"""Build cities/ksa/assumptions/access_air_routes.yaml and access_bus.yaml from the R4 scout tables
(runs/r4/scout/air_routes.csv, bus_cities.csv; sources docs/sources/r4-net.csv) and the register
coordinates of the bus nodes. Values are copied by script, not by hand.
  uv run python scripts/r4_network_tables.py
"""

from __future__ import annotations

import csv
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
HDR = "# > **Document version:** cities/ksa/assumptions/{n} v1.0 | 1 Nov 2026 | Author: R4 builder (gis-network-engineer) | Status: draft\n"

# region capitals not named by the bus source (A-r4-bus-001): register names
CAPITALS = {
    "Madinah": "Medina",
    "Buraidah": "Buraydah",
    "Tabuk": "Tabuk",
    "Hail": "Ha'il",
    "Arar": "Arar",
    "Sakaka": "Sakaka",
}


def main() -> None:
    air = list(csv.DictReader((ROOT / "runs/r4/scout/air_routes.csv").open(encoding="utf-8")))
    routes = [
        {
            "pair": [r["a"], r["b"]],
            "airlines": r["airlines"].split(";"),
            "sources": r["source_ids"].split(";"),
            "status": "secondary",
            "note": r["notes"],
        }
        for r in air
    ]
    doc = {
        "version": "1.0",
        "label": "synthetic demand, uncalibrated: scenario comparison, not a forecast",
        "rule": {
            "value": "a domestic air route exists between two airports when the pair is listed below (scheduled "
            "passenger service on the airport pages read 1 Nov 2026); this replaces R3's hub rule A-demand-051",
            "assumption": "A-r4-air-001",
        },
        "headway_unlisted_min": {
            "value": 480,
            "range": [240, 1440],
            "assumption": "A-demand-052",
            "note": "routes without a headway in mode_choice_r3.yaml air.routes; no frequency found (S-r4-net)",
        },
        "routes": routes,
    }
    p = ROOT / "cities/ksa/assumptions/access_air_routes.yaml"
    p.write_text(
        HDR.format(n=p.name)
        + "# Spoke-to-spoke domestic air network (CP4 R4 requirement 2). Every pair: Wikipedia airport pages\n"
        "# (secondary), docs/sources/r4-net.csv.\n"
        + yaml.safe_dump(doc, sort_keys=False, allow_unicode=True, width=120),
        encoding="utf-8",
    )
    bus = list(csv.DictReader((ROOT / "runs/r4/scout/bus_cities.csv").open(encoding="utf-8")))
    c = pd.read_parquet(ROOT / "cities/ksa/candidates.parquet")
    names = {
        "Al-Ahsa": "Al-Hofuf",
        "Al-Baha": "Al Bahah",
        "Al-Namaas": "An-Nimas",
        "Jazan": "Jizan",
        "Makkah": "Mecca",
        "Taif": "At Ta'if",
        "Riyadh": "Riyadh",
        "Jeddah": "Jeddah",
        "Dammam": "Dammam",
        "Abha": "Abha",
        "Khamis Mushait": "Khamis Mushait",
        "Najran": "Najran",
    }

    def locate(n: str) -> dict:
        hits = c[c.name_en.str.lower() == n.lower()]
        if hits.empty:
            hits = c[c.name_en.str.lower().str.contains(n.lower().split()[-1], regex=False)]
        h = hits.sort_values("population", ascending=False).iloc[0]
        return {
            "register_row": h.row_key,
            "register_name": h.name_en,
            "lat": round(float(h.lat), 6),
            "lon": round(float(h.lon), 6),
        }

    nodes = []
    for r in bus:
        nodes.append(
            {
                "city": r["city_en"],
                "tier": "named",
                "operator": r["operator"],
                "sources": r["source_ids"].split(";"),
                **locate(names.get(r["city_en"], r["city_en"])),
            }
        )
    for city, reg in CAPITALS.items():
        nodes.append(
            {
                "city": city,
                "tier": "region_capital",
                "operator": "not named",
                "assumption": "A-r4-bus-001",
                **locate(reg),
            }
        )
    doc = {
        "version": "1.0",
        "label": "synthetic demand, uncalibrated: scenario comparison, not a forecast",
        "rule": {
            "value": "bus is available between two zones when each zone point is within node_access_max_road_min of a "
            "different bus node; access adds the road minutes to the node",
            "assumption": "A-r4-bus-002",
            "variants": {
                "named_and_capitals": "default",
                "named_only": "sensitivity (sourced nodes only)",
                "r3_all_pairs": "sensitivity (R3 rule A-mode-040: every pair >= 50 road km)",
            },
        },
        "node_access_max_road_min": {"value": 30, "range": [15, 60], "assumption": "A-r4-bus-002"},
        "min_road_km": {"value": 50, "range": [30, 100], "assumption": "A-mode-040"},
        "nodes": nodes,
    }
    p = ROOT / "cities/ksa/assumptions/access_bus.yaml"
    p.write_text(
        HDR.format(n=p.name)
        + "# Intercity bus nodes (CP4 R4 requirement 2). Named cities: one press source (S-r4-net-033);\n"
        "# region capitals not named there are added by assumption A-r4-bus-001 (flagged).\n"
        + yaml.safe_dump(doc, sort_keys=False, allow_unicode=True, width=120),
        encoding="utf-8",
    )
    for n in nodes:
        print(n["city"], "->", n["register_name"], n["lat"], n["lon"])


if __name__ == "__main__":
    main()
