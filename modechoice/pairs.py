"""Build MNL input OD tables (attributes per mode) from the road skims, the line YAMLs and
mode_choice_r3.yaml.

`build_attributes(od, r3, skims, points, scenario)` fills the per-mode columns for any OD table with
`o`, `d`, `purpose` (this is the function `demand/gravity.py` can call for zone pairs);
`representative_pairs(...)` builds the sweep's small table of named pairs. Every number comes
from the skims (runs/skims/national-governorates), the line YAMLs (read-only) or the R3 YAML
(source or assumption id); the `prov_*` columns name them.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml
from pyproj import Geod

from common import REPO_ROOT
from modechoice.coefficients import Corner, r3_value
from modechoice.mnl import PURPOSES

SKIMS_PATH = REPO_ROOT / "runs" / "skims" / "national-governorates" / "skims.parquet"
POINTS_PATH = REPO_ROOT / "cities" / "ksa" / "zones" / "governorate_points.geojson"
LINES_DIR = REPO_ROOT / "cities" / "ksa" / "lines"
SCENARIO_LINES = {
    # scenarios/S0.yaml and S1.yaml `lines.include` (existing; existing + committed)
    "S0": ("hhr", "sar-north-passenger", "sar-east-passenger"),
    "S1": ("hhr", "sar-north-passenger", "sar-east-passenger", "landbridge"),
}
_GEOD = Geod(ellps="WGS84")


def load_skims(path: Path = SKIMS_PATH) -> pd.DataFrame:
    s = pd.read_parquet(path, columns=["o", "d", "km", "min"])
    return s.rename(columns={"km": "road_km", "min": "road_min"})


def load_points(path: Path = POINTS_PATH) -> dict[str, tuple[float, float]]:
    g = json.loads(Path(path).read_text(encoding="utf-8"))
    out = {}
    for f in g["features"]:
        p = f["properties"]
        zid = p.get("zone_id") or p.get("gov_id")
        lon, lat = f["geometry"]["coordinates"][:2]
        out[str(zid)] = (float(lon), float(lat))
    return out


def gc_km(a: tuple[float, float], b: tuple[float, float]) -> float:
    _, _, m = _GEOD.inv(a[0], a[1], b[0], b[1])
    return float(m) / 1000.0


def scenario_lines(scenario: str) -> tuple[str, ...]:
    path = REPO_ROOT / "scenarios" / f"{scenario}.yaml"
    if path.exists():
        inc = yaml.safe_load(path.read_text(encoding="utf-8"))["lines"]["include"]
        return tuple(str(x) for x in inc)
    return SCENARIO_LINES[scenario]


def _road(skims: pd.DataFrame, o: str, d: str) -> tuple[float, float]:
    r = skims[(skims["o"] == o) & (skims["d"] == d)]
    if r.empty:
        return float("nan"), float("nan")
    return float(r["road_km"].iloc[0]), float(r["road_min"].iloc[0])


def _air_route(r3: dict[str, Any], a: str, b: str) -> dict[str, Any] | None:
    for r in r3["air"]["routes"]:
        if set(r["pair"]) == {a, b}:
            return r
    return None


def _rail_spec(
    pair: dict[str, Any], scenario: str, lines: tuple[str, ...]
) -> dict[str, Any] | None:
    """The pair's rail entry for the scenario (S0's entry when the scenario includes its line)."""
    rail = pair.get("rail", {}) or {}
    spec = rail.get(scenario) or rail.get("S0")
    if spec is None or spec["line"] not in lines:
        return None
    return spec


def _end(spec_value: float, rng: list[float] | None, which: Corner) -> float:
    if which == "base" or rng is None:
        return float(spec_value)
    lo, hi = sorted(float(x) for x in rng)
    return lo if which == "low" else hi


def rail_attributes(
    spec: dict[str, Any], r3: dict[str, Any], inputs: dict[str, Corner] | None = None
) -> dict[str, float]:
    """IVT, fare, headway and on-time for a pair's rail spec (published or hypothetical service)."""
    inputs = inputs or {}
    if spec.get("hypothetical_service"):
        ratio = r3_value(
            r3, "rail", "hypothetical_speed_ratio", which=inputs.get("rail_speed", "base")
        )
        dwell = r3_value(r3, "dwell_min_hypothetical")
        ivt = spec["track_km"] / (spec["design_speed_kmh"] * ratio) * 60.0
        ivt += spec["intermediate_stops"] * dwell
        fare = spec["track_km"] * r3_value(
            r3, "rail", "fare_per_km_hypothetical", which=inputs.get("rail_fare", "base")
        )
    else:
        ivt = _end(spec["ivt_min"], spec.get("ivt_range"), inputs.get("rail_ivt", "base"))
        fare = _end(spec["fare_sar"], spec.get("fare_range"), inputs.get("rail_fare", "base"))
    headway = _end(
        spec["headway_min"], spec.get("headway_range"), inputs.get("rail_headway", "base")
    )
    ontime = float(r3["on_time"]["rail_by_line"][spec["line"]]["value"])
    return {"ivt": ivt, "fare": fare, "headway": headway, "ontime": ontime}


def build_attributes(
    od: pd.DataFrame,
    r3: dict[str, Any],
    skims: pd.DataFrame,
    points: dict[str, tuple[float, float]],
    scenario: str,
    rail_specs: dict[tuple[str, str], dict[str, Any]] | None = None,
    inputs: dict[str, Corner] | None = None,
) -> pd.DataFrame:
    """Fill per-mode attribute columns for an OD table (columns o, d, purpose).

    `rail_specs` maps (o, d) to a rail spec (as in representative_pairs); OD pairs without one have
    rail unavailable (R3 has no zone-to-station skims; R4 replaces this with the rail graph)."""
    inputs = inputs or {}
    rail_specs = rail_specs or {}
    lines = scenario_lines(scenario)
    fuel = r3_value(r3, "car", "fuel_price_sar_per_l", which=inputs.get("fuel_price", "base"))
    econ = r3_value(r3, "car", "fuel_economy_km_per_l", which=inputs.get("fuel_economy", "base"))
    parking = r3_value(r3, "car", "parking_toll_sar_per_trip", which=inputs.get("parking", "base"))
    terminal = r3_value(r3, "car", "terminal_min")
    ae = r3["access_egress"]
    bus_factor = r3_value(r3, "bus", "ivt_factor_on_road", which=inputs.get("bus_ivt", "base"))
    bus_fare_km = r3_value(r3, "bus", "fare_per_km_sar", which=inputs.get("bus_fare", "base"))
    bus_headway = r3_value(r3, "bus", "headway_min", which=inputs.get("bus_headway", "base"))
    bus_min_km = r3_value(r3, "bus", "availability_min_road_km")
    blk_fixed = r3_value(
        r3, "air", "block_time", "fixed_min", which=inputs.get("air_block", "base")
    )
    blk_speed = r3_value(
        r3, "air", "block_time", "speed_km_per_min", which=_flip(inputs.get("air_block", "base"))
    )
    air_fixed = r3_value(r3, "air", "fare", "fixed_sar", which=inputs.get("air_fare", "base"))
    air_km = r3_value(r3, "air", "fare", "per_km_sar", which=inputs.get("air_fare", "base"))
    air_ontime = r3_value(r3, "on_time", "air")
    hosts = r3["air"]["airport_host"]

    rows = []
    for rec in od.itertuples(index=False):
        o, d = str(rec.o), str(rec.d)
        km, mins = _road(skims, o, d)
        row: dict[str, Any] = {
            "road_km": km,
            "road_min": mins,
            # car
            "avail_car": bool(np.isfinite(mins)),
            "ivt_min_car": mins + terminal,
            "access_min_car": 0.0,
            "egress_min_car": 0.0,
            "headway_min_car": 0.0,
            "cost_sar_car": km * fuel / econ + parking,  # per vehicle; MNL divides by occupancy
            "ontime_car": np.nan,
        }
        # rail
        spec = rail_specs.get((o, d))
        if spec is not None and spec["line"] in lines:
            ra = rail_attributes(spec, r3, inputs)
            row.update(
                avail_rail=True,
                ivt_min_rail=ra["ivt"],
                access_min_rail=float(ae["rail"]["access_min"]),
                egress_min_rail=float(ae["rail"]["egress_min"]),
                headway_min_rail=ra["headway"],
                cost_sar_rail=ra["fare"],
                ontime_rail=ra["ontime"],
                rail_line=spec["line"],
            )
        else:
            row.update(avail_rail=False, ontime_rail=np.nan, rail_line=None)
        # air
        ho, hd = hosts.get(o), hosts.get(d)
        route = (
            _air_route(r3, ho["iata"], hd["iata"])
            if ho and hd and ho["iata"] != hd["iata"]
            else None
        )
        if route is not None:
            po, pd_ = points[ho["host_zone"]], points[hd["host_zone"]]
            g = gc_km(po, pd_)
            acc_extra = _road(skims, o, ho["host_zone"])[1] if ho["host_zone"] != o else 0.0
            egr_extra = _road(skims, hd["host_zone"], d)[1] if hd["host_zone"] != d else 0.0
            row.update(
                avail_air=True,
                air_gc_km=g,
                ivt_min_air=blk_fixed + g / blk_speed,
                access_min_air=float(ae["air"]["access_min"]) + acc_extra,
                egress_min_air=float(ae["air"]["egress_min"]) + egr_extra,
                headway_min_air=_end(
                    route["headway_min"], route.get("range"), inputs.get("air_headway", "base")
                ),
                cost_sar_air=air_fixed + air_km * g,
                ontime_air=air_ontime,
            )
        else:
            row.update(avail_air=False, ontime_air=np.nan)
        # bus
        if np.isfinite(km) and km >= bus_min_km:
            row.update(
                avail_bus=True,
                ivt_min_bus=mins * bus_factor,
                access_min_bus=float(ae["bus"]["access_min"]),
                egress_min_bus=float(ae["bus"]["egress_min"]),
                headway_min_bus=bus_headway,
                cost_sar_bus=km * bus_fare_km,
                ontime_bus=np.nan,
            )
        else:
            row.update(avail_bus=False, ontime_bus=np.nan)
        rows.append(row)
    attrs = pd.DataFrame(rows, index=od.index)
    out = pd.concat([od.reset_index(drop=True), attrs.reset_index(drop=True)], axis=1)
    out["scenario"] = scenario
    return out


def _flip(which: Corner) -> Corner:
    """Block time: 'high' = slow (more fixed minutes AND lower speed)."""
    return {"low": "high", "high": "low", "base": "base"}[which]


def representative_pairs(
    r3: dict[str, Any],
    skims: pd.DataFrame,
    points: dict[str, tuple[float, float]],
    scenarios: tuple[str, ...] = ("S0", "S1"),
    purposes: tuple[str, ...] = PURPOSES,
    inputs: dict[str, Corner] | None = None,
) -> pd.DataFrame:
    """The sweep's representative OD table: every pair x scenario x purpose with attributes."""
    frames = []
    for scn in scenarios:
        lines = scenario_lines(scn)
        for pair in r3["representative_pairs"]:
            spec = _rail_spec(pair, scn, lines)
            od = pd.DataFrame({"o": pair["o"], "d": pair["d"], "purpose": list(purposes)})
            specs = {(pair["o"], pair["d"]): spec} if spec else {}
            t = build_attributes(od, r3, skims, points, scn, specs, inputs)
            t.insert(0, "pair_id", pair["id"])
            t.insert(1, "pair_name", pair["name"])
            t["input_variant"] = bool(pair.get("input_variant", False))
            t["prov_rail"] = _prov(spec)
            frames.append(t)
    return pd.concat(frames, ignore_index=True)


def _prov(spec: dict[str, Any] | None) -> str:
    if not spec:
        return "rail unavailable in scenario"
    keys = ("ivt_source", "fare_source", "headway_source", "assumption", "design_speed_source")
    return "; ".join(f"{k}={spec[k]}" for k in keys if spec.get(k))
