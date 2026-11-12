"""File readers behind the dashboard API. No computation beyond selection, reshaping and the
difference against S1 (scenario value minus S1 value on the same metric, as stored in the runs).

Every reader takes the data root (`api.settings.data_root()`), so tests run on
`tests/fixtures/api/`. Paths below are relative to that root and are named in each response.
"""

from __future__ import annotations

import csv
import json
import math
from functools import lru_cache
from pathlib import Path
from typing import Any, NamedTuple

import pandas as pd
import yaml

from api.contract import (
    BASELINE,
    BASELINE_RUN,
    CENTRAL_ROW,
    COMPARISON_CAPTION,
    COMPARISON_LAYOUTS,
    FRAMING,
    LAYERS,
    POP_SHORT,
    POPULATIONS,
    TRADE_OFF_CAPTION,
    caption,
)

LINES_DIR = "cities/ksa/lines/geojson"
STATIONS = "cities/ksa/lines/stations.geojson"
ALIGNMENTS_DIR = "cities/ksa/alignments"
CORRIDORS_DIR = "cities/ksa/corridors"
REGIONS = "cities/ksa/zones/regions.geojson"
CANDIDATES = "cities/ksa/candidates.parquet"
LONGLIST = "runs/r2/long-list/longlist.parquet"
COUNTS = "runs/r2/long-list/counts.json"
SCORES = "runs/r2/score/scores.parquet"
SCORE_SUMMARY = "runs/r2/score/summary.json"
SCENARIOS_DIR = "scenarios"
CBA_DIR = "runs/cba"
TOP5_CSV = "runs/r6/top5/top5.csv"
TOP5_DIR = "runs/r6/top5"
PARETO = "runs/r6/pareto_front.csv"
FISCAL = "runs/r7/fiscal/fiscal.json"
VFM = "runs/r7/vfm/vfm.json"

# The five layouts of the R6 search (top5.csv). S6-L6 is not one of them: it is a comparison layout
# from the connecting-set search, scored outside runs/r6/top5/ (R8_L6_PANEL).
LAYOUTS = ("S6-L1", "S6-L2", "S6-L3", "S6-L4", "S6-L5")
L6_SCORE_CSV = "runs/r6/l6/score/S6-L6.csv"
L6_SCORE_JSON = "runs/r6/l6/score/score.json"
L6_LAYOUT = "runs/r6/l6/L6.layout.yaml"
ALL_LAYOUTS = LAYOUTS + COMPARISON_LAYOUTS
FAMILY_SCENARIO = {
    "trunk_gap": "S2",
    "branch_spur": "S3",
    "commuter_belt": "S4",
    "station_addition": "S5",
}
# Metrics read from the CBA results rows (names as in runs/cba/*/results.json).
CBA_METRICS = ("npv", "bcr", "pvb", "pvc", "npv_wei", "bcr_wei", "fiscal_cost", "pv_capex")


class Roots(NamedTuple):
    """Where registers (`cities/`, `scenarios/`) and run outputs (`runs/`) live. They are separate
    because `runs/` is gitignored at every depth, so test fixtures keep theirs elsewhere."""

    data: Path
    runs: Path


class NotFound(Exception):
    """A requested entity does not exist in the data root."""


class Refused(Exception):
    """A request the contract refuses (e.g. difference mode for a trade-off-only layout)."""


# ---------------------------------------------------------------- helpers


def clean(obj: Any) -> Any:
    """JSON-safe copy: non-finite floats -> None, numpy scalars/arrays -> Python."""
    if isinstance(obj, dict):
        return {str(k): clean(v) for k, v in obj.items()}
    if isinstance(obj, list | tuple):
        return [clean(v) for v in obj]
    if hasattr(obj, "tolist") and not isinstance(obj, str):
        return clean(obj.tolist())
    if isinstance(obj, float):
        return obj if math.isfinite(obj) else None
    if obj is pd.NA or obj is pd.NaT:
        return None
    return obj


def rng(d: dict[str, Any] | None, upper: bool = True) -> dict[str, float | None] | None:
    """{'P10','P50','P90'} (or lower-case) -> {'p10','p50','p90'}; None if absent."""
    if not d:
        return None
    keys = ("P10", "P50", "P90") if upper else ("p10", "p50", "p90")
    return clean({k.lower(): d.get(k) for k in keys})


def _p(root: Roots, rel: str) -> Path:
    if rel.startswith("runs/"):
        return root.runs / rel.removeprefix("runs/")
    return root.data / rel


def _mtime(path: Path) -> float:
    return path.stat().st_mtime if path.exists() else 0.0


@lru_cache(maxsize=512)
def _json_cached(path: str, mtime: float) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def read_json(root: Roots, rel: str) -> Any:
    path = _p(root, rel)
    if not path.exists():
        raise NotFound(rel)
    return _json_cached(str(path), _mtime(path))


@lru_cache(maxsize=512)
def _yaml_cached(path: str, mtime: float) -> Any:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


def read_yaml(root: Roots, rel: str) -> Any:
    path = _p(root, rel)
    if not path.exists():
        raise NotFound(rel)
    return _yaml_cached(str(path), _mtime(path))


def read_csv_rows(root: Roots, rel: str) -> list[dict[str, str]]:
    path = _p(root, rel)
    if not path.exists():
        raise NotFound(rel)
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def _num(raw: str | None) -> float | None:
    if raw is None or raw == "":
        return None
    try:
        val = float(raw)
    except ValueError:
        return None
    return val if math.isfinite(val) else None


# ---------------------------------------------------------------- layers


def lines_layer(root: Roots, layer: str) -> dict[str, Any]:
    """existing / committed / historical lines from cities/ksa/lines/geojson/<layer>.geojson."""
    rel = f"{LINES_DIR}/{layer}.geojson"
    fc = read_json(root, rel)
    feats = []
    for f in fc.get("features", []):
        props = dict(f.get("properties") or {})
        props["layer"] = layer  # the file is the layer; never re-styled as another layer
        props["layer_name"] = LAYERS[layer]
        feats.append({"type": "Feature", "geometry": f["geometry"], "properties": props})
    return {"type": "FeatureCollection", "source": rel, "features": feats}


def corridor_index(root: Roots) -> dict[str, dict[str, Any]]:
    """Every generated corridor YAML (cities/ksa/corridors/<family>/<id>.yaml)."""
    out: dict[str, dict[str, Any]] = {}
    base = _p(root, CORRIDORS_DIR)
    if not base.exists():
        return out
    for path in sorted(base.glob("*/*.yaml")):
        rel = str(path.relative_to(root.data))
        doc = read_yaml(root, rel) or {}
        cid = doc.get("id") or path.stem
        out[cid] = {
            "id": cid,
            "family": doc.get("family"),
            "scenario": FAMILY_SCENARIO.get(str(doc.get("family"))),
            "name_en": doc.get("name_en"),
            "name_ar": doc.get("name_ar"),
            "layer": doc.get("layer", "hypothetical"),
            "length_km_sketch": doc.get("length_km"),
            "stations": doc.get("stations") or [],
            "sketch": doc.get("alignment_sketch") or [],
            "source": rel,
        }
    return out


def hypothetical_layer(root: Roots) -> dict[str, Any]:
    """Hypothetical (ours): routed alignments where they exist, else the corridor sketch;
    station additions as the new (class `planned`) station point."""
    feats: list[dict[str, Any]] = []
    for cid, c in corridor_index(root).items():
        props_base = {
            "id": cid,
            "family": c["family"],
            "scenario": c["scenario"],
            "name_en": c["name_en"],
            "name_ar": c["name_ar"],
            "layer": "hypothetical",
            "layer_name": LAYERS["hypothetical"],
        }
        if c["family"] == "station_addition":
            for st in c["stations"]:
                if st.get("class") != "planned":
                    continue
                feats.append(
                    {
                        "type": "Feature",
                        "geometry": {"type": "Point", "coordinates": [st["lon"], st["lat"]]},
                        "properties": {
                            **props_base,
                            "kind": "station_addition",
                            "station_name_en": st.get("name_en"),
                            "station_name_ar": st.get("name_ar"),
                            "source": c["source"],
                        },
                    }
                )
            continue
        rel = f"{ALIGNMENTS_DIR}/{cid}.geojson"
        geom = None
        length = None
        kind = "sketch"
        if _p(root, rel).exists():
            for f in read_json(root, rel).get("features", []):
                if (f.get("properties") or {}).get("kind") == "routed":
                    geom = f["geometry"]
                    length = f["properties"].get("length_km")
                    kind = "routed"
                    break
        if geom is None and c["sketch"]:
            geom = {"type": "LineString", "coordinates": [[lon, lat] for lat, lon in c["sketch"]]}
            length = c["length_km_sketch"]
        if geom is None:
            continue
        feats.append(
            {
                "type": "Feature",
                "geometry": geom,
                "properties": {
                    **props_base,
                    "kind": kind,
                    "length_km": length,
                    "source": rel if kind == "routed" else c["source"],
                },
            }
        )
    return {
        "type": "FeatureCollection",
        "source": f"{ALIGNMENTS_DIR}; {CORRIDORS_DIR}",
        "features": feats,
    }


def stations(root: Roots) -> dict[str, Any]:
    fc = read_json(root, STATIONS)
    feats = []
    for f in fc.get("features", []):
        p = f.get("properties") or {}
        layer = p.get("layer") if p.get("layer") in LAYERS else "existing"
        feats.append(
            {
                "type": "Feature",
                "geometry": f["geometry"],
                "properties": {
                    "line_id": p.get("line_id"),
                    "name_en": p.get("name_en"),
                    "name_ar": p.get("name_ar"),
                    "class": p.get("class"),
                    "layer": layer,
                    "layer_name": LAYERS[layer],
                },
            }
        )
    return {"type": "FeatureCollection", "source": STATIONS, "features": feats}


def regions(root: Roots) -> dict[str, Any]:
    fc = read_json(root, REGIONS)
    return {"type": "FeatureCollection", "source": REGIONS, "features": fc.get("features", [])}


# ---------------------------------------------------------------- register and funnel

STAGES = ("not_long_listed", "served", "long_list", "short_list")


def register(root: Roots) -> list[dict[str, Any]]:
    cand = pd.read_parquet(_p(root, CANDIDATES))
    stage = {k: "not_long_listed" for k in cand["row_key"]}
    score_rank: dict[str, tuple[float | None, int | None]] = {}
    if _p(root, LONGLIST).exists():
        ll = pd.read_parquet(_p(root, LONGLIST), columns=["row_key", "pass_threshold", "served"])
        for key, passed, served in ll.itertuples(index=False):
            if bool(passed) and bool(served):
                stage[key] = "served"
    if _p(root, SCORES).exists():
        sc = pd.read_parquet(_p(root, SCORES), columns=["row_key", "short_list", "score", "rank"])
        for key, short, score, rank in sc.itertuples(index=False):
            stage[key] = "short_list" if bool(short) else "long_list"
            score_rank[key] = (float(score), int(rank))
    rows = []
    for r in cand.itertuples(index=False):
        raw = r.economic_roles if r.economic_roles is not None else []
        roles = list(dict.fromkeys(x.get("role") for x in raw))  # one entry per role
        sr = score_rank.get(r.row_key, (None, None))
        rows.append(
            clean(
                {
                    "row_key": r.row_key,
                    "name_en": r.name_en,
                    "name_ar": r.name_ar,
                    "region": r.region,
                    "governorate": r.governorate,
                    "lat": r.lat,
                    "lon": r.lon,
                    "population": r.population,
                    "pop_source_status": r.pop_source_status,
                    "economic_roles": roles,
                    "terrain_class": r.terrain_class,
                    "screened": bool(r.screened),
                    "exclusion_reason": r.exclusion_reason,
                    "stage": stage.get(r.row_key, "not_long_listed"),
                    "score": sr[0],
                    "rank": sr[1],
                }
            )
        )
    return rows


def funnel(root: Roots) -> dict[str, Any]:
    counts = read_json(root, COUNTS)
    regions_ = sorted(counts.get("all", {}))
    short: dict[str, int] = {}
    if _p(root, SCORES).exists():
        sc = pd.read_parquet(_p(root, SCORES), columns=["region", "short_list"])
        short = {k: int(v) for k, v in sc[sc["short_list"]].groupby("region").size().items()}
    per_region = [
        {
            "region": reg,
            "settlements": int(counts.get("all", {}).get(reg, 0)),
            "long_list": int(counts.get("long_threshold", {}).get(reg, 0)),
            "served": int(counts.get("served", {}).get(reg, 0)),
            "short_list": int(short.get(reg, 0)),
        }
        for reg in regions_
    ]
    corr = corridor_index(root)
    by_family: dict[str, int] = {}
    for c in corr.values():
        by_family[str(c["family"])] = by_family.get(str(c["family"]), 0) + 1
    cases = [p.name for p in sorted(_p(root, CBA_DIR).glob("CBA-S[2-5]-*")) if p.is_dir()]
    appraised: dict[str, int] = {}
    for name in cases:
        fam = name.split("-")[2]  # CBA-S2-trunk_gap-<id> -> trunk_gap
        appraised[fam] = appraised.get(fam, 0) + 1
    tot = {
        k: sum(r[k] for r in per_region)
        for k in ("settlements", "long_list", "served", "short_list")
    }
    stages = [
        {"stage": "settlements in the register", "count": tot["settlements"], "source": CANDIDATES},
        {"stage": "long list (CP1 filters)", "count": tot["long_list"], "source": COUNTS},
        {"stage": "served bucket (station additions)", "count": tot["served"], "source": COUNTS},
        {"stage": "short list (scored, top 60)", "count": tot["short_list"], "source": SCORES},
        {"stage": "corridors generated", "count": len(corr), "source": CORRIDORS_DIR},
        {"stage": "corridors appraised (CBA vs S1)", "count": len(cases), "source": CBA_DIR},
        {"stage": "optimised layouts (S6)", "count": len(LAYOUTS), "source": TOP5_CSV},
    ]
    return {
        "stages": stages,
        "per_region": per_region,
        "corridors_by_family": by_family,
        "appraised_by_family": appraised,
        "label_screening": "screening input, not a forecast",
    }


# ---------------------------------------------------------------- CBA


def _case_dirs(root: Roots) -> list[Path]:
    base = _p(root, CBA_DIR)
    return sorted(p for p in base.glob("CBA-*") if (p / "results.json").exists())


def _pick_row(rows: list[dict[str, Any]], population: str, horizon: int, rate_case: str):
    for r in rows:
        if (r["population"], int(r["horizon"]), r["rate_case"]) == (population, horizon, rate_case):
            return r
    return None


def cba_case(
    root: Roots, case: str, population: str, horizon: int, rate_case: str
) -> dict[str, Any]:
    rel = f"{CBA_DIR}/{case}/results.json"
    doc = read_json(root, rel)
    row = _pick_row(doc["results"], population, horizon, rate_case)
    if row is None:
        raise NotFound(f"{rel}: no row {population}/{horizon}/{rate_case}")
    cand = doc.get("candidate")
    cid = Path(cand).stem if cand else None
    return clean(
        {
            "case": doc["case"],
            "family": doc.get("family"),
            "scenario": doc.get("scenario"),
            "baseline": doc.get("baseline"),
            "candidate": cid,
            "units": doc.get("units"),
            "draws": doc.get("draws"),
            "seed": doc.get("seed"),
            "row": {"population": population, "horizon": horizon, "rate_case": rate_case},
            "metrics": {m: rng(row.get(m)) for m in CBA_METRICS},
            "source": rel,
        }
    )


def cba_cases(root: Roots, population: str, horizon: int, rate_case: str) -> list[dict[str, Any]]:
    return [cba_case(root, p.name, population, horizon, rate_case) for p in _case_dirs(root)]


# ---------------------------------------------------------------- scenarios and programmes


def _top5(root: Roots) -> dict[str, dict[str, str]]:
    return {r["layout"]: r for r in read_csv_rows(root, TOP5_CSV)}


def _scorecard_path(layout: str) -> str:
    return L6_SCORE_CSV if layout in COMPARISON_LAYOUTS else TOP5_CSV


def _score_path(layout: str) -> str:
    if layout in COMPARISON_LAYOUTS:
        return L6_SCORE_JSON
    return f"{TOP5_DIR}/{layout.split('-')[-1]}/score.json"


def _layout_path(layout: str) -> str:
    if layout in COMPARISON_LAYOUTS:
        return L6_LAYOUT
    return f"{TOP5_DIR}/{layout.split('-')[-1]}.layout.yaml"


def _scorecards(root: Roots) -> dict[str, dict[str, str]]:
    """Scorecard rows: the five search layouts from top5.csv, then S6-L6 from its own score file
    (never from top5.csv) when it exists."""
    out = _top5(root)
    if _p(root, L6_SCORE_CSV).exists():
        for r in read_csv_rows(root, L6_SCORE_CSV):
            if r["layout"] in COMPARISON_LAYOUTS:
                out[r["layout"]] = r
    return out


def _layout_score(root: Roots, layout: str) -> dict[str, Any]:
    return read_json(root, _score_path(layout))


def _central_appraisal(score: dict[str, Any], population: str) -> dict[str, Any] | None:
    for r in score.get("appraisal_rows", []):
        if (r["population"], int(r["horizon"]), r["rate_case"]) == (
            population,
            CENTRAL_ROW["horizon"],
            CENTRAL_ROW["rate_case"],
        ):
            return r
    return None


def programme(root: Roots, layout: str, population: str = "un_wpp_medium") -> dict[str, Any]:
    cards = _scorecards(root)
    if layout not in cards or layout not in FRAMING:
        raise NotFound(layout)
    t = cards[layout]
    score = _layout_score(root, layout)
    yml = read_yaml(root, _layout_path(layout))
    row = _central_appraisal(score, population)
    frame = FRAMING[layout]
    out: dict[str, Any] = {
        "id": layout,
        "role": frame["role"],
        "trade_off_only": frame["trade_off_only"],
        "comparison_only": layout in COMPARISON_LAYOUTS,
        "caption": caption(layout),
        "baseline": BASELINE,
        "corridors": [c["id"] for c in yml.get("corridors", [])],
        "phases": json.loads(t["phases"]) if t.get("phases") else {},
        "flags": t.get("flags") or None,
        "population": population,
        "appraisal_row": {**CENTRAL_ROW, "population": population},
        "metrics": {
            "npv": rng({k: row.get(f"npv_{k.lower()}") for k in ("P10", "P50", "P90")})
            if row
            else None,
            "bcr": rng({k: row.get(f"bcr_{k.lower()}") for k in ("P10", "P50", "P90")})
            if row
            else None,
            "pvc": rng({k: row.get(f"pvc_{k.lower()}") for k in ("P10", "P50", "P90")})
            if row
            else None,
            "capex": {
                "p10": _num(t["capex_p10"]),
                "p50": _num(t["capex_p50"]),
                "p90": _num(t["capex_p90"]),
            },
        },
        "npv_at_p50_cost": {POP_SHORT[p]: score["npv_at_p50_cost"].get(p) for p in POPULATIONS},
        "npv_at_p90_cost": {POP_SHORT[p]: score["npv_at_p90_cost"].get(p) for p in POPULATIONS},
        "robust_npv": _num(t["robust_npv"]),
        "access_gain_120": _num(t["access_gain_120"]),
        "new_route_km": _num(t["new_route_km"]),
        "units": score.get("units"),
        "source": [_scorecard_path(layout), _score_path(layout)],
    }
    if layout == "S6-L1":
        out["p90_cost_note"] = (
            "NPV at P90 cost {low} / {medium} / {high} low/medium/high SAR m, {src}".format(
                src=TOP5_CSV,
                **{k: _fmt_signed(_num(t[f"npv_p90cost_{k}"])) for k in ("low", "medium", "high")},
            )
        )
    return clean(out)


def _fmt_signed(v: float | None) -> str:
    if v is None:
        return "n/a"
    s = f"{abs(round(v)):,}"
    return f"−{s}" if v < 0 else f"+{s}"


def programmes(root: Roots, population: str = "un_wpp_medium") -> list[dict[str, Any]]:
    cards = _scorecards(root)
    return [programme(root, lay, population) for lay in ALL_LAYOUTS if lay in cards]


def scenarios(root: Roots) -> list[dict[str, Any]]:
    out = []
    for sid in ("S0", "S1", "S2", "S3", "S4", "S5"):
        rel = f"{SCENARIOS_DIR}/{sid}.yaml"
        if not _p(root, rel).exists():
            continue
        doc = read_yaml(root, rel) or {}
        out.append(
            {
                "id": sid,
                "kind": doc.get("kind"),
                "title": doc.get("title"),
                "baseline": doc.get("baseline"),
                "layers": doc.get("layers") or [],
                "lines": (doc.get("lines") or {}).get("include") or [],
                "candidates": [Path(c).stem for c in doc.get("candidates") or []],
                "role": "baseline for every comparison" if sid == BASELINE else None,
                "trade_off_only": False,
                "caption": None,
                "source": rel,
            }
        )
    for lay in ALL_LAYOUTS:
        rel = f"{SCENARIOS_DIR}/{lay}.yaml"
        if not _p(root, rel).exists():
            continue
        doc = read_yaml(root, rel) or {}
        frame = FRAMING[lay]
        out.append(
            {
                "id": lay,
                "kind": doc.get("kind"),
                "title": doc.get("title"),
                "baseline": doc.get("baseline"),
                "layers": doc.get("layers") or [],
                "lines": (doc.get("lines") or {}).get("include") or [],
                "candidates": [c["id"] for c in (doc.get("layout") or {}).get("corridors", [])],
                "role": frame["role"],
                "trade_off_only": frame["trade_off_only"],
                "comparison_only": lay in COMPARISON_LAYOUTS,
                "caption": caption(lay),
                "source": rel,
            }
        )
    return out


# ---------------------------------------------------------------- Pareto


def pareto(root: Roots) -> dict[str, Any]:
    front = []
    for r in read_csv_rows(root, PARETO):
        front.append(
            {
                "engine": r["engine"],
                "layout_hash": r["layout_hash"],
                "robust_npv": _num(r["robust_npv"]),
                "npv_band": {
                    "low": _num(r["npv_low"]),
                    "medium": _num(r["npv_medium"]),
                    "high": _num(r["npv_high"]),
                },
                "capex_p50": _num(r["capex_p50"]),
                "access_gain_60": _num(r["access_gain_60"]),
                "access_gain_120": _num(r["access_gain_120"]),
                "n_corridors": _num(r["n_corridors"]),
                "on_full_front": r["on_full_front"] == "True",
            }
        )
    top = []
    cards = _scorecards(root)
    for lay, t in cards.items():
        frame = FRAMING[lay]
        top.append(
            {
                "id": lay,
                "role": frame["role"],
                "trade_off_only": frame["trade_off_only"],
                "comparison_only": lay in COMPARISON_LAYOUTS,
                "kind": "comparison" if lay in COMPARISON_LAYOUTS else "search",
                "caption": caption(lay),
                "robust_npv": _num(t["robust_npv"]),
                "npv_band": {k: _num(t[f"npv_p50cost_{k}"]) for k in ("low", "medium", "high")},
                "npv_draws_medium": {
                    k: _num(t[f"npv_draws_{k}_medium"]) for k in ("p10", "p50", "p90")
                },
                "capex": {k: _num(t[f"capex_{k}"]) for k in ("p10", "p50", "p90")},
                "access_gain_120": _num(t["access_gain_120"]),
                "national_reach_gain_120": _num(t["national_reach_gain_120_reported_only"]),
                "n_corridors": _num(t["corridors"]),
            }
        )
    return clean(
        {
            "front": front,
            "layouts": top,
            "caption_trade_off": TRADE_OFF_CAPTION,
            "caption_comparison": COMPARISON_CAPTION,
            "objectives": {
                "robust_npv": "min over UN WPP low/medium/high of NPV at P50 cost, SAR m PV",
                "access_gain_120": "2025 population newly within 120 min of a metro by rail vs S1",
            },
            "source": [PARETO, TOP5_CSV]
            + ([L6_SCORE_CSV] if any(x in cards for x in COMPARISON_LAYOUTS) else []),
        }
    )


# ---------------------------------------------------------------- fiscal and VfM


def fiscal(root: Roots) -> dict[str, Any]:
    doc = read_json(root, FISCAL)
    pop = doc.get("robust_case", "un_wpp_low")

    def entity(name: str, body: dict[str, Any]) -> dict[str, Any]:
        models = []
        for mname, m in body.get("models", {}).items():
            by = (m.get("by_pop") or {}).get(pop) or {}
            upfront = by.get("upfront_public_capex") or {}
            models.append(
                {
                    "model": mname,
                    "kind": m.get("kind"),
                    "net_fiscal_cost_60y": rng(by.get("net_fiscal_cost_60y"), upper=False),
                    "net_fiscal_cost_30y": rng(by.get("net_fiscal_cost_30y"), upper=False),
                    "upfront_public_capex": {
                        k: (upfront.get(k) or {}).get("sum") for k in ("p10", "p50", "p90")
                    }
                    if upfront
                    else None,
                }
            )
        basis = body.get("basis", {})
        return {
            "entity": name,
            "role": FRAMING.get(name, {}).get("role"),
            "capex": rng(basis.get("capex"), upper=False),
            "judge_sha256": basis.get("judge_sha256"),
            "score": basis.get("score"),
            "models": models,
        }

    s1 = doc.get("baseline_s1") or {}
    s1_row = (s1.get("rows") or {}).get(f"{pop}|60") or {}
    return clean(
        {
            "units": doc.get("units"),
            "population_case": pop,
            "programmes": [entity(k, v) for k, v in doc.get("programmes", {}).items()],
            "corridors": [entity(k, v) for k, v in doc.get("corridors", {}).items()],
            "baseline_s1": {
                "case": s1.get("case"),
                "run": s1.get("run"),
                "fiscal_cost_60y": rng(s1_row.get("fiscal_cost")),
                "pv_capex": rng(s1_row.get("pv_capex")),
            },
            "assumption_ids": doc.get("assumption_ids"),
            "source": FISCAL,
        }
    )


def vfm(root: Roots) -> dict[str, Any]:
    doc = read_json(root, VFM)

    def entity(name: str, body: dict[str, Any]) -> dict[str, Any]:
        central = body.get("central", {})
        vals = [central.get("vfm")]
        for d in body.get("drivers", {}).values():
            vals += [d.get("vfm_at_low"), d.get("vfm_at_high")]
        vals = [v for v in vals if v is not None]
        return {
            "entity": name,
            "role": FRAMING.get(name, {}).get("role"),
            "psc": central.get("psc"),
            "ppp": central.get("ppp"),
            "vfm": {
                "low": min(vals) if vals else None,
                "central": central.get("vfm"),
                "high": max(vals) if vals else None,
            },
            "sign_central": body.get("sign_central"),
            "sign_robust_to_registered_ranges": body.get("sign_robust_to_registered_ranges"),
            "depends_on_unsourced": body.get("depends_on_unsourced"),
            "not_sourced_for_ksa": body.get("not_sourced_for_ksa"),
            "drivers": {
                k: {
                    "id": d.get("id"),
                    "sourcing": d.get("sourcing"),
                    "vfm_at_low": d.get("vfm_at_low"),
                    "vfm_at_high": d.get("vfm_at_high"),
                }
                for k, d in body.get("drivers", {}).items()
            },
        }

    return clean(
        {
            "units": doc.get("units"),
            "definition": doc.get("definition"),
            "population_case": doc.get("population_case"),
            "range_note": (
                "expected values; low/high = envelope of the one-at-a-time sweeps over the "
                "registered driver ranges (not P10/P50/P90)"
            ),
            "programmes": [entity(k, v) for k, v in doc.get("programmes", {}).items()],
            "corridors": [entity(k, v) for k, v in doc.get("corridors", {}).items()],
            "source": VFM,
        }
    )


# ---------------------------------------------------------------- difference mode


def _delta(a: float | None, b: float | None) -> float | None:
    return None if a is None or b is None else a - b


def difference(root: Roots, scenario: str, population: str = "un_wpp_medium") -> dict[str, Any]:
    """Scenario minus the baseline S1 on the same metrics.

    S6 layouts: modelled 2050 rail trips, passenger-km and per-line passengers (scenario and S1
    both stored in the layout's score.json), population within 60/120 min (reported only), and
    the appraisal ranges, which are increments over S1 by construction (S1 + layout minus S1).
    S2–S5 CBA cases: the appraisal ranges only (each case is S1 + candidate minus S1).
    """
    if scenario in (BASELINE, "S0"):
        raise Refused(f"{scenario}: difference mode compares a scenario against {BASELINE}")
    if scenario in FRAMING and FRAMING[scenario]["trade_off_only"]:
        raise Refused(f"{scenario}: {caption(scenario)}")
    if scenario in FRAMING:
        score = _layout_score(root, scenario)
        t = _top5(root)[scenario]
        prog = programme(root, scenario, population)
        loads = score.get("by_line_2050_medium") or score.get("loads_2050_medium") or {}
        loads_s1 = score.get("loads_2050_medium_S1") or {}
        lines = []
        for lid in sorted(set(loads) | set(loads_s1)):
            a = (loads.get(lid) or {}).get("passengers")
            b = (loads_s1.get(lid) or {}).get("passengers")
            lines.append(
                {
                    "line_id": lid,
                    "scenario": a,
                    "S1": b,
                    "delta": _delta(a, b) if b is not None else None,
                    "note": None if b is not None else "S1 value not stored in the run",
                }
            )
        covered = sorted(k for k, v in loads_s1.items() if (v or {}).get("passengers") is not None)
        coverage = {
            "s1_lines_covered": covered,
            "s1_lines_not_covered": sorted(set(loads) - set(covered)),
            "why": (
                "the layout score.json stores S1 per-line passengers only in "
                f"loads_2050_medium_S1 ({', '.join(covered)}: the load lines written by "
                "optimise.layout.demand_metrics); the other lines' S1 loads are not written to "
                "any run file (inputs/*/scalars.parquet hold network totals only), so no per-line "
                "difference is shown for them; network totals (rail trips, passenger-km) above "
                "cover every line"
            ),
        }
        nr = score.get("national_reach_reported_only") or {}
        within = nr.get("population_2025_within_min") or {}
        within_s1 = nr.get("S1_population_2025_within_min") or {}
        rows = [
            {
                "metric": "rail trips 2050 (UN WPP medium)",
                "unit": "trips/year",
                "scenario": score.get("rail_trips_2050_medium"),
                "S1": score.get("rail_trips_2050_medium_S1"),
            },
            {
                "metric": "rail passenger-km 2050 (UN WPP medium)",
                "unit": "million pkm/year",
                "scenario": score.get("rail_pkm_m_2050_medium"),
                "S1": score.get("rail_pkm_m_2050_medium_S1"),
            },
        ]
        for m in ("60", "120"):
            rows.append(
                {
                    "metric": f"2025 population within {m} min of a metro by rail (reported only)",
                    "unit": "persons",
                    "scenario": within.get(m),
                    "S1": within_s1.get(m),
                }
            )
        for r in rows:
            r["delta"] = _delta(r["scenario"], r["S1"])
        return clean(
            {
                "scenario": scenario,
                "baseline": BASELINE,
                "role": FRAMING[scenario]["role"],
                "population": population,
                "rows": rows,
                "lines_2050": lines,
                "lines_2050_coverage": coverage,
                "increments": {
                    "basis": "appraisal is S1 + layout minus S1 (increment by construction)",
                    **prog["metrics"],
                },
                "p90_cost_note": prog.get("p90_cost_note"),
                "added_corridors": prog["corridors"],
                "phases": prog["phases"],
                "access_gain_120": _num(t["access_gain_120"]),
                "source": prog["source"],
            }
        )
    case = scenario if scenario.startswith("CBA-") else f"CBA-{scenario}"
    c = cba_case(root, case, population, CENTRAL_ROW["horizon"], CENTRAL_ROW["rate_case"])
    if c["baseline"] != BASELINE:
        raise Refused(f"{case}: its baseline is {c['baseline']}, not {BASELINE}")
    return clean(
        {
            "scenario": case,
            "baseline": BASELINE,
            "role": None,
            "population": population,
            "rows": [],
            "lines_2050": [],
            "increments": {
                "basis": "appraisal is S1 + candidate minus S1 (increment by construction)",
                **c["metrics"],
            },
            "added_corridors": [c["candidate"]] if c["candidate"] else [],
            "source": c["source"],
            "baseline_run": BASELINE_RUN,
        }
    )
