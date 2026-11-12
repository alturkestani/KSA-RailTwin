"""Population scenarios to 2050/2060 and their downscaling to demand zones (W8, R3 task 2).

Every output is "synthetic demand, uncalibrated: scenario comparison, not a forecast".

Inputs (every real-world number lives in YAML or a committed table with a source or assumption id):
- `cities/ksa/population/inputs.yaml`: census and GASTAT estimate totals, policy targets,
  downscaling and giga-project parameters;
- `cities/ksa/population/base_2022_governorates.csv`: GASTAT Census 2022 TA1 by governorate (150),
  mapped to the 149 OSM governorate zones G001-G149 (Al Amoah into G031, A-pop-007);
- `cities/ksa/population/wpp2024_sau_total_population.csv`: UN WPP 2024 Saudi rows (all variants);
- `cities/ksa/population/wup2025_sau_urban_share.csv`: UN WUP 2025 Saudi urban share;
- `cities/ksa/population/scenarios/*.yaml`: the scenario files (`build` writes all but
  `gigaprojects.yaml`, which is hand-written).

Library:
    project(base_by_zone, scenario, year) -> pd.Series   # zone populations, sum == scenario total
    giga_increments(giga, year, quantile, base_by_zone) -> pd.Series
    apply_giga(pop, increments, mode) -> pd.Series

CLI:
    uv run python -m demand.population build --seed 1          # tables + generated YAMLs
    uv run python -m demand.population show --scenario un_wpp_medium --year 2040
    uv run python -m demand.population validate
"""

from __future__ import annotations

import csv
import datetime as dt
import gzip
import json
import math
import re
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import typer
import yaml

from common import REPO_ROOT
from common.labels import LABEL
from common.runmeta import write_meta

app = typer.Typer(add_completion=False, help="Population scenarios to 2060 (W8).")

POP_DIR = REPO_ROOT / "cities" / "ksa" / "population"
SCEN_DIR = POP_DIR / "scenarios"
INPUTS = POP_DIR / "inputs.yaml"
BASE_CSV = POP_DIR / "base_2022_governorates.csv"
WPP_CSV = POP_DIR / "wpp2024_sau_total_population.csv"
WUP_CSV = POP_DIR / "wup2025_sau_urban_share.csv"
DOWNSCALING_YAML = POP_DIR / "downscaling.yaml"
WPP_RAW = REPO_ROOT / "data/ksa/population/wpp2024/WPP2024_TotalPopulationBySex.csv.gz"
WUP_NAT_RAW = (
    REPO_ROOT / "data/ksa/population/wup2025/WUP2025-DB-National-Definitions-Population-Data.csv.gz"
)
WUP_DEG_RAW = (
    REPO_ROOT
    / "data/ksa/population/wup2025/WUP2025-DB-DEGURBA-Level1-Population-Surface-Data.csv.gz"
)
SOURCE_INDEXES = [
    REPO_ROOT / "docs/sources/index.csv",
    *sorted((REPO_ROOT / "docs/sources").glob("r3-*.csv")),
]
ASSUMPTION_FILES = [REPO_ROOT / "docs/assumptions.md"]

# Source / assumption ids (docs/sources/r3-pop.csv, docs/assumptions.md); ids, not figures.
S_WPP = "S-r3-pop-001"
S_WUP_NAT, S_WUP_DEG = "S-r3-pop-008", "S-r3-pop-010"
S_CENSUS_GOV = "S-cp2-gastat-007"
S_TA9 = "S-cp2-gastat-003"
S_EST = "S-cp2-gastat-006"
ISO3 = "SAU"
FIRST_YEAR, LAST_YEAR = 2022, 2060
YEARS = list(range(FIRST_YEAR, LAST_YEAR + 1))
WPP_KEEP_FROM = 2010
# scenario id -> WPP 2024 variant name (as printed in the file)
WPP_SCENARIOS = {
    "un_wpp_low": "Low",
    "un_wpp_medium": "Medium",
    "un_wpp_high": "High",
    "un_wpp_constant_fertility": "Constant fertility",
    "un_wpp_zero_migration": "Zero migration",
}
PI_VARIANTS = {
    "lower_95": "Lower 95 PI",
    "lower_80": "Lower 80 PI",
    "median": "Median PI",
    "upper_80": "Upper 80 PI",
    "upper_95": "Upper 95 PI",
}
PI_YEARS = [2025, 2030, 2035, 2040, 2045, 2050, 2055, 2060]
COVER_KEYS = {"source", "sources", "assumption", "assumptions", "derived_from"}
ID_S = re.compile(r"\bS-[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*\b")
ID_A = re.compile(r"\bA-[a-z0-9_]+-[0-9]+[a-z]?\b")
HEADER = (
    "# > **Document version:** {name} v0.1 | {date} | Author: demand-modeler (R3) | Status: draft"
)
DOC_DATE = "31 Oct 2026"


# --------------------------------------------------------------------------- io helpers
def read_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


def inputs() -> dict[str, Any]:
    return read_yaml(INPUTS)


def scenario_path(sid_or_path: str | Path) -> Path:
    p = Path(sid_or_path)
    if p.suffix in (".yaml", ".yml") and p.exists():
        return p
    return SCEN_DIR / f"{sid_or_path}.yaml"


def load_scenario(sid_or_path: str | Path) -> dict[str, Any]:
    return read_yaml(scenario_path(sid_or_path))


def load_base(path: Path = BASE_CSV) -> pd.DataFrame:
    return pd.read_csv(path, dtype={"zone_id": str})


def base_by_zone(base: pd.DataFrame | None = None) -> pd.Series:
    """Census 2022 population by zone (149 OSM governorate zones), int64, sorted by zone id."""
    b = load_base() if base is None else base
    s = b.groupby("zone_id")["pop_2022"].sum().astype("int64").sort_index()
    s.name = "population"
    return s


def region_of_zone(base: pd.DataFrame | None = None) -> pd.Series:
    b = load_base() if base is None else base
    r = b.groupby("zone_id")["region"].agg(lambda x: sorted(set(x)))
    if (r.map(len) != 1).any():
        raise ValueError(f"zones spanning regions: {r[r.map(len) != 1].to_dict()}")
    return r.map(lambda x: x[0]).sort_index()


# --------------------------------------------------------------------------- core maths
def largest_remainder(weights: pd.Series, total: int) -> pd.Series:
    """Integers proportional to `weights` that sum exactly to `total` (ties by index order)."""
    if total < 0:
        raise ValueError("total must be non-negative")
    w = weights.astype("float64").clip(lower=0.0)
    if w.sum() <= 0:
        raise ValueError("weights sum to zero")
    raw = w / w.sum() * total
    floor = np.floor(raw).astype("int64")
    short = int(total - floor.sum())
    frac = (raw - floor).to_numpy()
    order = np.lexsort((np.arange(len(frac)), -frac))  # largest fraction first, then index order
    add = np.zeros(len(frac), dtype="int64")
    add[order[:short]] = 1
    return pd.Series(floor.to_numpy() + add, index=weights.index, name=weights.name)


def national_total(scenario: dict[str, Any], year: int) -> int:
    nt = scenario["national_totals"]
    vals = {int(k): v for k, v in nt["values"].items()}
    if year in vals:
        return int(vals[year])
    if nt.get("no_growth"):
        return int(vals[min(vals)])
    raise KeyError(
        f"{scenario.get('id')}: no national total for {year} (years {min(vals)}-{max(vals)})"
    )


def downscaling_params() -> dict[str, Any]:
    return read_yaml(DOWNSCALING_YAML)


def zone_shares(
    base: pd.Series,
    year: int,
    method: str = "constant_shares",
    regions: pd.Series | None = None,
    params: dict[str, Any] | None = None,
    weight: float | None = None,
) -> pd.Series:
    """Zone shares (sum 1) for a year. `constant_shares` (A-pop-005): Census 2022 shares held.
    `regional_trend` (A-pop-006): region shares drift by exp(w * d_r * (year - 2022)), where
    d_r = ln(g_r / g_KSA) / span from GASTAT TA9 2010->2022; governorate shares within a region
    held."""
    s = base.astype("float64") / float(base.sum())
    if method == "constant_shares":
        return s
    if method != "regional_trend":
        raise ValueError(f"unknown downscaling method {method!r}")
    p = downscaling_params() if params is None else params
    rt = p["regional_trend"]
    w = float(rt["weight"]["value"] if weight is None else weight)
    span = int(rt["end_year"]) - int(rt["base_year"])
    g = {k: v["end"] / v["start"] for k, v in rt["region_population"].items()}
    tot = sum(v["end"] for v in rt["region_population"].values()) / sum(
        v["start"] for v in rt["region_population"].values()
    )
    d = {k: math.log(v / tot) / span for k, v in g.items()}
    reg = region_of_zone() if regions is None else regions
    reg = reg.reindex(s.index)
    if reg.isna().any():
        raise ValueError(f"zones without a region: {reg[reg.isna()].index.tolist()}")
    factor = reg.map(lambda r: math.exp(w * d[r] * (year - FIRST_YEAR)))
    out = s * factor
    return out / out.sum()


def project(
    base_by_zone: pd.Series,
    scenario: dict[str, Any],
    year: int,
    method: str | None = None,
    regions: pd.Series | None = None,
    params: dict[str, Any] | None = None,
    weight: float | None = None,
) -> pd.Series:
    """Zone populations for `year` under `scenario` (int64; the sum equals the scenario's national
    total exactly). Zone overrides (policy scenario) are fixed first; the rest is spread by the
    downscaling shares over the other zones."""
    total = national_total(scenario, year)
    m = method or (scenario.get("downscaling") or {}).get("default", "constant_shares")
    shares = zone_shares(base_by_zone, year, m, regions, params, weight)
    fixed: dict[str, int] = {}
    for zone, ov in (scenario.get("zone_overrides") or {}).items():
        vals = {int(k): v for k, v in ov["values"].items()}
        if year in vals:
            if zone not in shares.index:
                raise KeyError(f"override zone {zone} not in base")
            fixed[zone] = int(vals[year])
    rest_total = total - sum(fixed.values())
    if rest_total < 0:
        raise ValueError(f"overrides exceed the national total in {year}")
    rest = shares.drop(list(fixed))
    out = largest_remainder(rest, rest_total)
    for zone, v in fixed.items():
        out[zone] = v
    out = out.reindex(base_by_zone.index).astype("int64")
    out.name = f"{scenario.get('id')}_{year}"
    assert int(out.sum()) == total
    return out


# --------------------------------------------------------------------------- giga add-ons
def _ramp(year: int, start: int, target: int) -> float:
    if year >= target:
        return 1.0
    if year <= start or target <= start:
        return 0.0 if year < target else 1.0
    return (year - start) / (target - start)


def giga_increments(
    giga: dict[str, Any],
    year: int,
    quantile: str = "p50",
    base_by_zone: pd.Series | None = None,
    field: str = "residents",
    inp: dict[str, Any] | None = None,
) -> pd.Series:
    """Per-zone add-on (float) for `field` (`residents` or `jobs`) in `year`: announced quantity x
    delivered share (A-demand-030) x linear ramp from the ramp start year to the target year
    (A-pop-014); undated targets take the undated target year (A-pop-015); `total_area` residents
    are net of the zone's Census 2022 base (A-pop-016); observed capacities apply from their
    status year. Entries with `supersedes_when_larger` take the larger of the pair."""
    inp = inputs() if inp is None else inp
    gp = inp["gigaprojects"]
    ramp_start = int(gp["ramp_start_year"]["value"])
    undated = int(gp["undated_target_year"]["value"])
    base = base_by_zone if base_by_zone is not None else base_by_zone_default()
    per: dict[str, tuple[str, float]] = {}
    for p in giga["projects"]:
        zone = p.get("zone")
        qty = p.get(f"{field}_announced")
        if zone is None:
            continue
        share = 1.0 if quantile == "announced" else float(p["delivered_share"][quantile])
        val = 0.0
        if qty is not None:
            if field == "residents" and p.get("residents_basis") == "total_area":
                qty = max(0.0, float(qty) - float(base.get(zone, 0)))
            target = p.get(f"{field}_target_year") or p.get("target_year") or undated
            val = float(qty) * share * _ramp(year, ramp_start, int(target))
        elif p.get(f"{field}_observed_capacity") is not None:
            since = int(str(p.get("status_date", ramp_start))[:4])
            val = float(p[f"{field}_observed_capacity"]) if year >= since else 0.0
        per[p["id"]] = (zone, val)
    for p in giga["projects"]:
        other = p.get("supersedes_when_larger")
        if other and other in per and p["id"] in per:
            a, b = per[p["id"]][1], per[other][1]
            per[p["id"]] = (per[p["id"]][0], max(a, b))
            per[other] = (per[other][0], 0.0)
    inc = pd.Series(0.0, index=base.index, name=f"giga_{field}_{quantile}_{year}")
    for zone, v in per.values():
        if zone not in inc.index:
            raise KeyError(f"giga zone {zone} not in base")
        inc[zone] += v
    return inc


def base_by_zone_default() -> pd.Series:
    return base_by_zone()


def apply_giga(pop: pd.Series, increments: pd.Series, mode: str = "reallocate") -> pd.Series:
    """Add giga increments to zone populations. `reallocate` (A-pop-013): the national total is
    kept; the add-on is taken pro rata from the non-host zones. `additive`: the total grows."""
    inc = increments.reindex(pop.index).fillna(0.0)
    add = largest_remainder(inc, int(round(inc.sum()))) if inc.sum() > 0 else inc.astype("int64")
    if mode == "additive":
        return (pop + add).astype("int64")
    if mode != "reallocate":
        raise ValueError(f"unknown add-on mode {mode!r}")
    host = add > 0
    take = largest_remainder(pop[~host].astype("float64"), int(add.sum()))
    out = pop.copy()
    out[host] = pop[host] + add[host]
    out[~host] = pop[~host] - take
    if (out < 0).any():
        raise ValueError("reallocation drives a zone negative")
    assert int(out.sum()) == int(pop.sum())
    return out.astype("int64")


# --------------------------------------------------------------------------- build: tables
def build_base_table() -> pd.DataFrame:
    """150 GASTAT governorates (primary TA1 export) with region, Arabic name and zone id."""
    from screening import gastat

    prim, _ = gastat.primary_vs_relayed()
    if prim.relayed_name.isna().any():
        raise ValueError("primary governorates without a relayed match")
    gov = gastat.governorates_2022()
    m = prim.merge(gov, left_on="relayed_name", right_on="code", how="left", validate="1:1")
    if (m.total != m.pop_2022).any():
        raise ValueError("primary and relayed governorate totals differ")
    zone = m.gov_id.copy()
    note = pd.Series("", index=m.index)
    for i in m.index[zone.isna()]:
        if m.at[i, "code"] == "Al Amoah":
            zone[i] = "G031"  # Tathlith polygon contains the Al Amoah seat node (A-asir-002)
            note[i] = "no OSM polygon (C-r1a-20): merged into G031 Tathlith (A-pop-007)"
        else:
            raise ValueError(f"no zone for {m.at[i, 'code']}")
    out = pd.DataFrame(
        {
            "gastat_name": m.primary_name,
            "relayed_code": m.code,
            "name_ar": m.name_ar,
            "region": m.region,
            "zone_id": zone,
            "pop_2022": m.total.astype("int64"),
            "saudi_2022": m.saudi.astype("int64"),
            "non_saudi_2022": m.non_saudi.astype("int64"),
            "source": S_CENSUS_GOV,
            "zone_note": note,
        }
    ).sort_values(["zone_id", "gastat_name"])
    return out.reset_index(drop=True)


def extract_wpp(raw: Path = WPP_RAW) -> pd.DataFrame:
    """Saudi rows of WPP 2024 TotalPopulationBySex (thousands, as printed), 2010-2060."""
    rows = []
    with gzip.open(raw, "rt", encoding="utf-8-sig") as fh:
        for d in csv.DictReader(fh):
            if d["ISO3_code"] != ISO3:
                continue
            y = int(d["Time"])
            if WPP_KEEP_FROM <= y <= LAST_YEAR:
                rows.append(
                    {
                        "loc_id": d["LocID"],
                        "variant": d["Variant"],
                        "var_id": d["VarID"],
                        "year": y,
                        "pop_total_thousands": d["PopTotal"],
                    }
                )
    return pd.DataFrame(rows).sort_values(["var_id", "year"], key=_numkey).reset_index(drop=True)


def _numkey(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce") if s.name in ("var_id", "year") else s


def extract_wup(nat: Path = WUP_NAT_RAW, deg: Path = WUP_DEG_RAW) -> pd.DataFrame:
    """Saudi urban share (mid-year, %): national definitions and Degree of Urbanisation."""
    out: dict[int, dict[str, str]] = {}
    with gzip.open(nat, "rt", encoding="utf-8-sig") as fh:
        for d in csv.DictReader(fh):
            if d["ISO3_Code"] == ISO3 and d["Category"] == "Urban" and int(d["Year"]) >= 2010:
                out.setdefault(int(d["Year"]), {})["urban_pct_national_definitions"] = d["percPop"]
    with gzip.open(deg, "rt", encoding="utf-8-sig") as fh:
        for d in csv.DictReader(fh):
            if d["ISO3_Code"] != ISO3 or int(d["Year"]) < 2010:
                continue
            if d["Category"] == "Cities and Towns":
                out.setdefault(int(d["Year"]), {})["cities_and_towns_pct_degurba"] = d["percPop"]
            if d["Category"] == "Cities":
                out.setdefault(int(d["Year"]), {})["cities_pct_degurba"] = d["percPop"]
    df = pd.DataFrame([{"year": y, **v} for y, v in sorted(out.items())])
    return df


def wpp_series(wpp: pd.DataFrame, variant: str) -> dict[int, float]:
    """Thousands by year; projection variants take the Medium estimates before 2024 (A-pop-004)."""
    inp = inputs()
    start = int(inp["wpp_projection_start_year"]["value"])
    med = wpp[wpp.variant == "Medium"].set_index("year").pop_total_thousands.astype(float)
    v = wpp[wpp.variant == variant].set_index("year").pop_total_thousands.astype(float)
    out = {}
    for y in YEARS:
        out[y] = float(med[y]) if (y < start or variant == "Medium") else float(v[y])
    return out


def anchor_factor(wpp: pd.DataFrame) -> float:
    inp = inputs()
    med = wpp[(wpp.variant == inp["anchor"]["wpp_variant_for_factor"])]
    w22 = float(med.set_index("year").pop_total_thousands.astype(float)[inp["anchor"]["year"]])
    return inp["census_2022_total"]["value"] / (w22 * 1000.0)


# --------------------------------------------------------------------------- build: yaml
def _dump(path: Path, doc: dict[str, Any], extra_comment: str = "") -> None:
    rel = path.relative_to(REPO_ROOT).as_posix()
    head = HEADER.format(name=rel, date=DOC_DATE)
    gen = "# Generated by `uv run python -m demand.population build`; do not edit by hand."
    lines = [head, gen] + ([f"# {extra_comment}"] if extra_comment else [])
    body = yaml.safe_dump(doc, sort_keys=False, allow_unicode=True, width=100)
    path.write_text("\n".join(lines) + "\n" + body, encoding="utf-8")


def _common(sid: str, kind: str, title: str) -> dict[str, Any]:
    return {
        "id": sid,
        "kind": kind,
        "title": title,
        "label": LABEL,
        "base": "baseline",
        "zones": "cities/ksa/population/base_2022_governorates.csv",
        "downscaling": {
            "default": "constant_shares",
            "alternatives": ["regional_trend"],
            "assumptions": ["A-pop-005", "A-pop-006"],
        },
    }


def build_yamls(wpp: pd.DataFrame, wup: pd.DataFrame, base: pd.DataFrame) -> list[Path]:
    inp = inputs()
    SCEN_DIR.mkdir(parents=True, exist_ok=True)
    census = int(inp["census_2022_total"]["value"])
    if int(base.pop_2022.sum()) != census:
        raise ValueError("base table does not sum to the census total in inputs.yaml")
    f = anchor_factor(wpp)
    med22 = wpp_series(wpp, "Medium")[FIRST_YEAR]
    anchor = {
        "census_2022_total": census,
        "wpp_medium_2022_thousands": med22,
        "factor": f,
        "gap_wpp_minus_census_persons": int(round(med22 * 1000 - census)),
        "source": [S_CENSUS_GOV, S_WPP],
        "assumption": "A-pop-001",
    }
    written: list[Path] = []

    # baseline: Census 2022, no growth
    doc = _common("baseline", "baseline_census", "GASTAT Census 2022 governorate base, no growth")
    doc.pop("base")
    doc["national_totals"] = {
        "unit": "persons",
        "no_growth": True,
        "source": S_CENSUS_GOV,
        "assumptions": ["A-pop-007"],
        "values": {FIRST_YEAR: census},
    }
    doc["zones_source"] = S_CENSUS_GOV
    written.append(SCEN_DIR / "baseline.yaml")
    _dump(written[-1], doc, "S0 baseline population: every year returns the 2022 census zones.")

    # WPP variants
    for sid, variant in WPP_SCENARIOS.items():
        ser = wpp_series(wpp, variant)
        doc = _common(sid, "projection_un_wpp", f"UN WPP 2024 {variant} variant, census-anchored")
        doc["wpp_variant"] = variant
        doc["national_totals"] = {
            "unit": "persons",
            "source": S_WPP,
            "assumptions": ["A-pop-001", "A-pop-002", "A-pop-004"],
            "anchor": anchor,
            "values": {y: int(round(v * 1000 * f)) for y, v in ser.items()},
        }
        if sid == "un_wpp_medium":
            pi: dict[str, Any] = {
                "unit": "persons",
                "source": S_WPP,
                "assumptions": ["A-pop-001"],
                "note": "WPP 2024 probabilistic projections (Median PI and 80/95 % intervals)",
            }
            for key, var in PI_VARIANTS.items():
                s = wpp_series(wpp, var)
                pi[key] = {y: int(round(s[y] * 1000 * f)) for y in PI_YEARS}
            doc["prediction_intervals"] = pi
        written.append(SCEN_DIR / f"{sid}.yaml")
        _dump(written[-1], doc)

    # sensitivity: re-anchor to the GASTAT 2024 estimate (A-pop-003)
    med = wpp_series(wpp, "Medium")
    est23 = int(inp["gastat_estimate_2023"]["value"])
    est24 = int(inp["gastat_estimate_2024"]["value"])
    ratio = est24 / (med[2024] * 1000.0)
    vals = {FIRST_YEAR: census, 2023: est23}
    for y in YEARS:
        if y >= int(inp["gastat2024_reanchor"]["hold_ratio_from_year"]):
            vals[y] = int(round(med[y] * 1000.0 * ratio))
    doc = _common(
        "un_wpp_medium_gastat2024",
        "sensitivity",
        "UN WPP 2024 Medium growth path re-anchored to the GASTAT 2024 estimate",
    )
    doc["matched_to"] = "un_wpp_medium"
    doc["national_totals"] = {
        "unit": "persons",
        "source": [S_WPP, S_EST, S_CENSUS_GOV],
        "assumptions": ["A-pop-003"],
        "reanchor": {
            "gastat_2024": est24,
            "wpp_medium_2024_thousands": med[2024],
            "ratio": ratio,
            "source": [S_EST, S_WPP],
            "assumption": "A-pop-003",
        },
        "values": dict(sorted(vals.items())),
    }
    written.append(SCEN_DIR / "un_wpp_medium_gastat2024.yaml")
    _dump(written[-1], doc)

    # Vision 2030 policy scenario (A-pop-009..012): a policy input, not a forecast
    v = inp["vision2030"]
    tgt = int(v["national_target_2030"]["value"])
    rz = v["riyadh_target_2030"]
    zone = rz["zone"]
    zb = int(base.groupby("zone_id").pop_2022.sum()[zone])
    nat, riy = {}, {}
    for y in YEARS:
        if y <= 2030:
            t = (y - FIRST_YEAR) / (2030 - FIRST_YEAR)
            nat[y] = int(round(census * (tgt / census) ** t))
            riy[y] = int(round(zb * (int(rz["value"]) / zb) ** t))
        else:
            nat[y] = int(round(tgt * med[y] / med[2030]))
            riy[y] = int(round(int(rz["value"]) / tgt * nat[y]))
    doc = _common("vision2030_policy", "policy_vision2030", "Vision 2030 stated targets (policy)")
    doc["policy_note"] = (
        "Labelled POLICY scenario built from stated targets (press reports of official remarks); "
        "it is not a projection and carries no likelihood."
    )
    doc["national_totals"] = {
        "unit": "persons",
        "source": [S_CENSUS_GOV, S_WPP, *v["national_target_2030"]["source"]],
        "assumptions": ["A-pop-009", "A-pop-010"],
        "target_2030": {
            "value": tgt,
            "p10": v["national_target_2030"]["p10"],
            "p90": v["national_target_2030"]["p90"],
            "source": v["national_target_2030"]["source"],
            "assumption": "A-pop-009",
        },
        "values": nat,
    }
    doc["zone_overrides"] = {
        zone: {
            "name": "Ar Riyadh governorate (Riyadh city target applied to the governorate)",
            "unit": "persons",
            "source": [S_CENSUS_GOV, *rz["source"]],
            "assumptions": ["A-pop-011", "A-pop-012"],
            "target_2030": {
                "value": int(rz["value"]),
                "p10": rz["p10"],
                "p90": rz["p90"],
                "assumption": "A-pop-011",
            },
            "values": riy,
        }
    }
    doc["tourism"] = {
        "use": "tourism purpose totals (gravity), never zone population (A-pop-018)",
        "target_2030": {
            k: v["tourism_visits_target_2030"][k]
            for k in ("value", "international", "domestic", "unit")
        }
        | {"source": v["tourism_visits_target_2030"]["source"], "assumption": "A-pop-018"},
        "observed_2025": dict(v["tourism_visits_observed_2025"]),
        "observed_2024": dict(v["tourism_visits_observed_2024"]),
    }
    written.append(SCEN_DIR / "vision2030_policy.yaml")
    _dump(written[-1], doc)

    # urbanisation trend (WUP 2025)
    w = wup.set_index("year")
    yrs = [2010, 2015, 2020, FIRST_YEAR, 2025, 2030, 2035, 2040, 2045, 2050]
    last = int(w.index.max())
    doc = {
        "id": "urbanisation_wup2025",
        "kind": "urbanisation_trend",
        "title": "UN WUP 2025 urban share, Saudi Arabia",
        "label": LABEL,
        "use": (
            "context input for zones and the urban/rural split; "
            "not used to change governorate shares in v0.1"
        ),
        "urban_pct_national_definitions": {
            "unit": "% of population, mid-year",
            "source": S_WUP_NAT,
            "assumptions": ["A-pop-008"],
            "values": {
                y: round(float(w.urban_pct_national_definitions[min(y, last)]), 2)
                for y in yrs + [2055, 2060]
            },
            "held_after": last,
        },
        "cities_and_towns_pct_degurba": {
            "unit": "% of population, mid-year (Degree of Urbanisation: cities + towns)",
            "source": S_WUP_DEG,
            "assumptions": ["A-pop-008"],
            "values": {
                y: round(float(w.cities_and_towns_pct_degurba[min(y, last)]), 2)
                for y in yrs + [2055, 2060]
            },
            "held_after": last,
        },
    }
    written.append(SCEN_DIR / "urbanisation_wup2025.yaml")
    _dump(written[-1], doc)
    return written


def build_downscaling() -> dict[str, Any]:
    """Regional series 2010 and 2022 (GASTAT TA9) for the regional-trend method."""
    from screening import gastat

    inp = inputs()["downscaling"]["regional_trend"]
    t = gastat.read_ta9().pivot(index="region", columns="year", values="population")
    b, e = int(inp["base_year"]), int(inp["end_year"])
    return {
        "label": LABEL,
        "kind": "downscaling_parameters",
        "constant_shares": {
            "assumption": "A-pop-005",
            "note": "Census 2022 governorate shares held for every year",
        },
        "regional_trend": {
            "assumption": "A-pop-006",
            "source": S_TA9,
            "base_year": b,
            "end_year": e,
            "weight": dict(inputs()["downscaling"]["regional_trend"]["weight"]),
            "region_population": {
                r: {"start": int(t.loc[r, b]), "end": int(t.loc[r, e])} for r in sorted(t.index)
            },
        },
    }


# --------------------------------------------------------------------------- validation
def known_ids() -> tuple[set[str], set[str]]:
    s: set[str] = set()
    for p in SOURCE_INDEXES:
        if p.exists():
            with p.open(encoding="utf-8") as fh:
                s |= {r["id"] for r in csv.DictReader(fh)}
    a: set[str] = set()
    for p in ASSUMPTION_FILES:
        if p.exists():
            a |= set(re.findall(r"^\| (A-[A-Za-z0-9_-]+) \|", p.read_text(encoding="utf-8"), re.M))
    return s, a


def uncovered_numbers(
    node: Any, path: str = "", covered: bool = False, depth: int = 0
) -> list[str]:
    """Numeric leaves with no `source`/`assumption` key on their own mapping or an ancestor below
    the top level (a file-wide `sources:` does not count)."""
    out: list[str] = []
    if isinstance(node, dict):
        here = covered or (depth > 0 and bool(COVER_KEYS & set(node)))
        for k, v in node.items():
            out += uncovered_numbers(v, f"{path}.{k}", here, depth + 1)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            out += uncovered_numbers(v, f"{path}[{i}]", covered, depth + 1)
    elif isinstance(node, (int, float)) and not isinstance(node, bool):
        if not covered:
            out.append(path)
    return out


def validate_file(path: Path, known_s: set[str], known_a: set[str]) -> list[str]:
    text = path.read_text(encoding="utf-8")
    errs = []
    first = text.splitlines()[0] if text else ""
    if not first.startswith("# > **Document version:**"):
        errs.append(f"{path.name}: first line is not a version header comment")
    doc = yaml.safe_load(text)
    if doc.get("label") != LABEL:
        errs.append(f"{path.name}: label missing or wrong")
    if not doc.get("kind"):
        errs.append(f"{path.name}: kind missing")
    errs += [
        f"{path.name}: number without source/assumption at {p}" for p in uncovered_numbers(doc)
    ]
    for sid in sorted(set(ID_S.findall(text))):
        if sid not in known_s:
            errs.append(f"{path.name}: source id {sid} not in the source indexes")
    for aid in sorted(set(ID_A.findall(text))):
        if aid not in known_a:
            errs.append(f"{path.name}: assumption id {aid} not in the assumption registers")
    return errs


def validate_all(paths: list[Path] | None = None) -> list[str]:
    known_s, known_a = known_ids()
    files = paths or [*sorted(SCEN_DIR.glob("*.yaml")), INPUTS, DOWNSCALING_YAML]
    errs: list[str] = []
    for f in files:
        errs += validate_file(f, known_s, known_a)
    return errs


# --------------------------------------------------------------------------- CLI
@app.command()
def build(
    seed: int = typer.Option(1, "--seed", min=0, help="recorded in meta.json (no randomness used)"),
    run_dir: Path = typer.Option(REPO_ROOT / "runs/population/build", "--out"),
) -> None:
    """Write the base table, the WPP/WUP extracts, downscaling.yaml and the generated scenarios."""
    base = build_base_table()
    base.to_csv(BASE_CSV, index=False)
    wpp = extract_wpp()
    wpp.to_csv(WPP_CSV, index=False)
    wup = extract_wup()
    wup.to_csv(WUP_CSV, index=False)
    ds = build_downscaling()
    _dump(DOWNSCALING_YAML, ds)
    files = build_yamls(wpp, wup, base)
    errs = validate_all()
    meta = write_meta(
        run_dir,
        seed,
        {"inputs": inputs(), "downscaling": ds},
        extra={
            "assumptions": sorted(known_ids()[1] & _ids_in(files + [INPUTS, DOWNSCALING_YAML])),
            "outputs": [
                p.relative_to(REPO_ROOT).as_posix()
                for p in [BASE_CSV, WPP_CSV, WUP_CSV, DOWNSCALING_YAML, *files]
            ],
            "validation_errors": errs,
        },
    )
    typer.echo(
        f"base zones {base.zone_id.nunique()} from {len(base)} governorates; "
        f"wrote {len(files)} scenarios"
    )
    typer.echo(f"meta {meta.relative_to(REPO_ROOT)}; validation errors: {len(errs)}")
    for e in errs:
        typer.echo(f"  {e}")


def _ids_in(files: list[Path]) -> set[str]:
    out: set[str] = set()
    for f in files:
        out |= set(ID_A.findall(f.read_text(encoding="utf-8")))
    return out


@app.command()
def show(
    scenario: str = typer.Option(..., "--scenario"),
    year: int = typer.Option(..., "--year"),
    method: str = typer.Option("", "--downscaling", help="constant_shares | regional_trend"),
    giga: str = typer.Option(
        "", "--giga", help="announced | p10 | p50 | p90 (adds gigaprojects.yaml)"
    ),
    top: int = typer.Option(10, "--top"),
    seed: int = typer.Option(1, "--seed", min=0),
    out: Path | None = typer.Option(None, "--out", help="write zones.parquet + meta.json here"),
) -> None:
    """Print the national total and the largest zones for a scenario and year."""
    sc = load_scenario(scenario)
    b = base_by_zone()
    pop = project(b, sc, year, method or None)
    note = ""
    if giga:
        inc = giga_increments(load_scenario("gigaprojects"), year, giga, b)
        mode = inputs()["gigaprojects"]["addon_mode"]["value"]
        pop = apply_giga(pop, inc, mode)
        note = f" + giga {giga} ({mode}, add-on {int(round(inc.sum())):,})"
    typer.echo(LABEL)
    typer.echo(f"{sc['id']} {year}{note}: national {int(pop.sum()):,} over {len(pop)} zones")
    names = load_base().groupby("zone_id").gastat_name.agg(" + ".join)
    for z, v in pop.sort_values(ascending=False).head(top).items():
        typer.echo(f"  {z} {names[z]:<28} {v:>12,}  {100 * v / pop.sum():5.2f} %")
    if out:
        out.mkdir(parents=True, exist_ok=True)
        df = pd.DataFrame({"zone_id": pop.index, "population": pop.to_numpy()})
        df["scenario"], df["year"], df["label"] = sc["id"], year, LABEL
        df.to_parquet(out / "zones.parquet", index=False)
        write_meta(
            out,
            seed,
            {"scenario": sc, "year": year, "method": method, "giga": giga},
            extra={
                "assumptions": sorted(set(ID_A.findall(json.dumps(sc)))),
                "scenario_id": sc["id"],
            },
        )
        typer.echo(f"wrote {out}/zones.parquet")


@app.command()
def validate() -> None:
    """Every scenario YAML has a header, the label, a kind, and a source/assumption id (that
    resolves in the registers) for every number; exit 1 otherwise."""
    errs = validate_all()
    for e in errs:
        typer.echo(f"FAIL {e}")
    n = len(list(SCEN_DIR.glob("*.yaml")))
    typer.echo(
        f"{n} scenario files + inputs + downscaling: {len(errs)} problems ({dt.date.today()})"
    )
    if errs:
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
