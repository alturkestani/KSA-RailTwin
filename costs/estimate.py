"""Corridor cost estimator: P10/P50/P90 capex, opex and renewals for one line YAML, every input
traced to a cost-register id; then reference-class uplifts (`costs.rcf`) give P50/P80 budgets.

Inputs
- `--corridor`  line YAML (`LineSpec`): length, line type, track, electrification, stations by
                class, services (headway, span) and the running-time parameters.
- `--register`  cost register; money values are normalised to the index base (2025 SAR) in memory.
- `--uplifts`   reference-class uplifts.
- `--profile`   costing profiles by line type (`costs/config/profiles.yaml`): terrain and structure
                shares, system choices, fleet and operating parameters; each real-world value
                carries an assumption id. A corridor may override them with a `costing:` block
                in a sidecar (`--costing`).
- `--map`       component -> register id map (`costs/config/estimate_map.yaml`).

Method (docs/costs.md section 6): every register item is a PERT draw on low/central/high
(A-cost-004); all capex items share one uniform draw and all opex items another (comonotonic,
A-cost-003; asset lives a third), so ranges do not shrink by diversification. Contingency is
reported but NOT added to the uplifted budget: the reference-class uplift replaces it (A-cost-008).

CLI:
  uv run python -m costs.estimate --corridor tests/fixtures/corridor.yaml \
      --register cities/ksa/costs/cost_register.yaml --uplifts cities/ksa/costs/uplifts.yaml \
      --seed 1 --out runs/costs/fixture/
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import typer
import yaml

from common import REPO_ROOT
from common.labels import LABEL
from common.runmeta import rng as make_rng
from common.runmeta import seed_option, write_meta
from common.schemas import LineSpec, load_uplifts
from costs import rcf
from costs.register import INDEX, REGISTER, normalised_lookup

CONFIG = Path(__file__).resolve().parent / "config"
PROFILES = CONFIG / "profiles.yaml"
MAP = CONFIG / "estimate_map.yaml"
UPLIFTS = REPO_ROOT / "cities" / "ksa" / "costs" / "uplifts.yaml"
HORIZONS = (30, 40, 60)

app = typer.Typer(add_completion=False, help="Corridor capex/opex/renewal ranges with uplifts.")


class TraceError(KeyError):
    """A component maps to no usable register id."""


# --------------------------------------------------------------------------- helpers
def _val(x: Any) -> float:
    """Profile values are {value, assumption_id} dicts or plain numbers (fixtures)."""
    return float(x["value"]) if isinstance(x, dict) else float(x)


def _item(reg: dict[str, dict[str, Any]], rid: str, unit: str | None = None) -> dict[str, Any]:
    if rid not in reg:
        raise TraceError(f"register id {rid} not in the register")
    it = reg[rid]
    if it["status"] == "unknown":
        raise TraceError(f"register id {rid} is `unknown`: it cannot be costed")
    if unit and it["unit"] != unit:
        raise TraceError(f"register id {rid} has unit {it['unit']}, expected {unit}")
    return it


def _draw(it: dict[str, Any], u: np.ndarray) -> np.ndarray:
    return rcf.pert(None, it["low"], it["central"], it["high"], len(u), u)  # type: ignore[arg-type]


def running_minutes(line: LineSpec, stops: int) -> float:
    """End-to-end minutes: length at cruise + per-stop dwell and acceleration/braking loss."""
    rtm = line.running_time_model
    v = _val(rtm["cruise_kmh"].model_dump()) / 3.6
    a = _val(rtm["accel_ms2"].model_dump())
    d = _val(rtm["decel_ms2"].model_dump())
    dwell = _val(rtm["dwell_s"].model_dump())
    loss_per_stop = v / (2 * a) + v / (2 * d)  # seconds lost vs cruising through
    cruise_s = (line.length_km or 0.0) * 1000 / v
    inter = max(stops - 2, 0)
    return (cruise_s + inter * (dwell + loss_per_stop) + loss_per_stop) / 60.0


def span_hours(span: str | None, default: str | None) -> float:
    s = span or default
    if not s:
        raise ValueError("service has no span and no default span")
    a, b = s.split("-")
    h = lambda t: int(t.split(":")[0]) + int(t.split(":")[1]) / 60  # noqa: E731
    return (h(b) - h(a)) % 24 or 24.0


def operations(line: LineSpec, prof: dict[str, Any]) -> dict[str, Any]:
    """Fleet (trainsets) and annual train-km from the service plan (A-cost-005..007)."""
    default_span = next((s.span for s in line.services if s.span), None)
    turn = _val(prof["turnaround_min"])
    spare = _val(prof["fleet_spare_share"])
    days = _val(prof["operating_days_per_year"])
    fleet_in_service = 0
    train_km = 0.0
    services = []
    for s in line.services:
        stops = len(line.stations) if s.stops == "all" else len(s.stops)
        run = running_minutes(line, stops)
        cycle = 2 * (run + turn)
        need = math.ceil(cycle / s.headway_min)
        trips_day = 2 * span_hours(s.span, default_span) * 60 / s.headway_min
        km_yr = trips_day * (line.length_km or 0.0) * days
        fleet_in_service += need
        train_km += km_yr
        services.append(
            {"id": s.id, "run_min": round(run, 2), "trainsets": need, "train_km_yr": round(km_yr)}
        )
    fleet = math.ceil(fleet_in_service * (1 + spare))
    return {"fleet": fleet, "train_km_yr": train_km, "services": services}


# --------------------------------------------------------------------------- estimate
def _pctiles(x: np.ndarray) -> dict[str, float]:
    return {f"P{p}": float(np.percentile(x, p)) for p in (10, 50, 90)}


def estimate(
    line: LineSpec,
    reg: dict[str, dict[str, Any]],
    prof: dict[str, Any],
    cmap: dict[str, Any],
    seed: int,
    draws: int,
) -> tuple[dict[str, Any], pd.DataFrame, list[dict[str, Any]]]:
    """Base capex, opex per year and renewals (draws) for one corridor; every component is traced
    to the register ids it used (`trace`)."""
    rng = make_rng(seed)
    u_cap = rng.uniform(1e-6, 1 - 1e-6, draws)
    u_opx = rng.uniform(1e-6, 1 - 1e-6, draws)
    u_life = rng.uniform(1e-6, 1 - 1e-6, draws)  # asset lives: their own common draw (A-cost-003)
    L = float(line.length_km or 0.0)
    lt = line.line_type
    trace: list[dict[str, Any]] = []
    comp: dict[str, np.ndarray] = {}

    def row(name: str, group: str, ids: list[str], qty: Any, qty_unit: str, x: np.ndarray) -> None:
        trace.append(
            {
                "component": name,
                "group": group,
                "register_id": ", ".join(ids),
                "status": "/".join(sorted({reg[i]["status"] for i in ids})),
                "quantity": None if qty is None else round(float(qty), 4),
                "quantity_unit": qty_unit,
                "unit": "/".join(reg[i]["unit"] for i in ids),
                **_pctiles(x),
            }
        )

    def add(
        name: str, group: str, rid: str, qty: float, qty_unit: str, units: tuple[str, ...]
    ) -> None:
        it = _item(reg, rid)
        if it["unit"] not in units:
            raise TraceError(f"register id {rid} has unit {it['unit']}, expected one of {units}")
        x = _draw(it, u_cap) * qty
        comp[name] = x
        row(name, group, [rid], qty, qty_unit, x)

    def share(v: Any, u: np.ndarray) -> tuple[np.ndarray, list[str]]:
        """A share given as a number/assumption dict, or drawn from a register row (unit pct)."""
        if isinstance(v, dict) and "register_id" in v:
            it = _item(reg, v["register_id"], "pct")
            return _draw(it, u) / 100.0, [v["register_id"]]
        return np.full(len(u), _val(v)), []

    # --- structures (km on tunnel / viaduct) and the at-grade remainder
    st_sh: dict[str, np.ndarray] = {}
    for s in ("tunnel", "viaduct"):
        sh, ids = share(prof["structure_shares"][s], u_cap)
        st_sh[s] = sh
        if np.any(sh > 0):
            it = _item(reg, cmap["structure"][s], "SAR_m_per_km")
            x = _draw(it, u_cap) * sh * L
            comp[f"structure[{s}]"] = x
            row(
                f"structure[{s}]",
                "construction",
                [cmap["structure"][s], *ids],
                None,
                "km = share x route-km",
                x,
            )
    at_grade = 1.0 - st_sh["tunnel"] - st_sh["viaduct"]
    if np.any(at_grade < 0):
        raise ValueError("structure shares exceed 1")
    # --- civil and track by terrain on the at-grade km, plus terrain premia
    terr = {k: _val(v) for k, v in prof["terrain_shares"].items()}
    if abs(sum(terr.values()) - 1) > 1e-6:
        raise ValueError("terrain shares must sum to 1")
    base_id = cmap["line_base"][lt]
    base_it = _item(reg, base_id, "SAR_m_per_km")
    base = _draw(base_it, u_cap)
    for t, sh in terr.items():
        if sh <= 0:
            continue
        x = base * sh * L * at_grade
        comp[f"civil_track[{t}]"] = x
        row(f"civil_track[{t}]", "construction", [base_id], sh * L, "route-km (at-grade share)", x)
        prem = cmap["terrain_premium"].get(t) if t != "flat_desert" else None
        if prem:
            pit = _item(reg, prem)
            if pit["unit"] == "pct":  # % uplift over the base on that terrain
                px = x * _draw(pit, u_cap) / 100.0
            elif pit["unit"] == "SAR_m_per_km":
                px = _draw(pit, u_cap) * sh * L
            else:
                raise TraceError(f"terrain premium {prem} has unit {pit['unit']}")
            comp[f"terrain_premium[{t}]"] = px
            row(f"terrain_premium[{t}]", "construction", [prem], sh * L, "route-km", px)
    # --- systems per route-km
    sig = prof["signalling"]
    add(
        f"signalling[{sig}]",
        "systems",
        cmap["signalling"][lt][sig],
        L,
        "route-km",
        ("SAR_m_per_km",),
    )
    for name, rid in (cmap.get("systems_per_km", {}).get(lt) or {}).items():
        add(name, "systems", rid, L, "route-km", ("SAR_m_per_km",))
    if line.electrified:
        add(
            "electrification_ocs",
            "systems",
            cmap["electrification"][lt],
            L,
            "route-km",
            ("SAR_m_per_km",),
        )
        spacing = _val(prof["substation_spacing_km"])
        n_sub = max(1, math.ceil(L / spacing))
        add(
            "power_substations",
            "systems",
            cmap["power"][lt],
            n_sub,
            "substations",
            ("SAR_m_per_unit",),
        )
    # --- stations by class
    classes: dict[str, int] = {}
    for st in line.stations:
        classes[st.class_] = classes.get(st.class_, 0) + 1
    for cls, n in sorted(classes.items()):
        add(
            f"station[{cls}]",
            "construction",
            cmap["station"][lt][cls],
            n,
            "stations",
            ("SAR_m_per_station",),
        )
    # --- depots and rolling stock
    ops = operations(line, prof)
    add(
        "depot",
        "systems",
        cmap["depot"][lt],
        _val(prof["depots"]),
        "depots",
        ("SAR_m_per_unit", "SAR_m_lump"),
    )
    traction = "electric" if line.electrified else prof.get("traction_if_not_electric", "diesel")
    add(
        f"rolling_stock[{traction}]",
        "rolling_stock",
        cmap["rolling_stock"][lt][traction],
        ops["fleet"],
        "trainsets",
        ("SAR_m_per_trainset",),
    )
    construction = sum(v for k, v in comp.items() if not k.startswith("rolling_stock"))
    # --- percentage items on construction (excl. rolling stock)
    for name in ("land", "utilities", "design_pm"):
        rid = cmap[name][lt] if isinstance(cmap[name], dict) else cmap[name]
        it = _item(reg, rid, "pct_of_capex")
        x = construction * _draw(it, u_cap) / 100.0
        comp[name] = x
        row(name, "construction" if name != "land" else "land", [rid], None, "% of construction", x)
    capex_base = sum(comp.values())
    rid = cmap["contingency"]
    contingency = capex_base * _draw(_item(reg, rid, "pct_of_capex"), u_cap) / 100.0
    row("contingency (reported, not added)", "contingency", [rid], None, "% of base", contingency)

    # --- opex per year: each entry = product of register rows x driver
    drivers = {
        "train_km": ops["train_km_yr"],
        "route_km": L,
        "route_km_dunes": L * terr.get("dunes", 0.0),
    }
    opex: dict[str, np.ndarray] = {}
    for o in cmap["opex"][lt]:
        x = np.full(draws, drivers[o["driver"]] * float(o.get("to_sar_m", 1.0)))
        for rid in o["ids"]:
            it = _item(reg, rid)
            v = _draw(it, u_opx)
            x = x * (v / 100.0 if it["unit"] in ("pct", "pct_per_yr", "pct_of_capex") else v)
        opex[o["name"]] = x
        row(f"opex[{o['name']}]", "opex_per_year", o["ids"], drivers[o["driver"]], o["driver"], x)
    opex_total = sum(opex.values()) if opex else np.zeros(draws)
    staffing = None
    sz = cmap.get("staffing", {})
    if sz.get(lt):
        fte = _draw(_item(reg, sz[lt], "fte_per_km"), u_opx) * L
        share_it = _item(reg, sz["saudisation_share"], "pct")
        saudi = fte * _draw(share_it, u_opx) / 100.0
        staffing = {
            "fte": _pctiles(fte),
            "saudi_fte": _pctiles(saudi),
            "register_ids": [sz[lt], sz["saudisation_share"]],
            "note": "Saudisation share (A-cost-300) splits headcount, not wages",
        }
        row("staffing_fte (headcount, not cost)", "staffing", [sz[lt]], L, "route-km", fte)
        row(
            "saudi_fte (headcount)",
            "staffing",
            [sz[lt], sz["saudisation_share"]],
            None,
            "share of FTE",
            saudi,
        )

    # --- renewals over 30/40/60 years: component capex x renewal shares, once per asset life
    ren: dict[int, np.ndarray] = {h: np.zeros(draws) for h in HORIZONS}
    for r in cmap["renewals"]:
        parts = [v for k, v in comp.items() if any(k.startswith(p) for p in r["components"])]
        if not parts:
            continue
        life = _draw(_item(reg, r["life_id"], "years"), u_life)
        amount = sum(parts)
        sids = r.get("share_ids", [])
        if isinstance(sids, dict):  # per line type, with a `default`
            sids = sids.get(lt, sids["default"])
        for sid in sids:
            amount = amount * _draw(_item(reg, sid, "pct"), u_cap) / 100.0
        for h in HORIZONS:
            ren[h] = ren[h] + np.floor((h - 1e-9) / life) * amount
        row(
            f"renewal[{r['name']}]",
            "renewal",
            [r["life_id"], *sids],
            None,
            "renewal per life cycle of " + "+".join(r["components"]),
            amount,
        )

    df = pd.DataFrame(
        {
            "draw": np.arange(draws),
            "capex_base": capex_base,
            "rolling_stock": sum(v for k, v in comp.items() if k.startswith("rolling_stock")),
            "contingency": contingency,
            "opex_per_year": opex_total,
            **{f"renewals_{h}y": ren[h] for h in HORIZONS},
        }
    )
    summary = {
        "label": LABEL,
        "note": "cost ranges, price year 2025, SAR million, not a budget",
        "corridor": line.id,
        "fixture": line.fixture,
        "line_type": lt,
        "length_km": L,
        "operations": ops,
        "capex_base_sar_m": _pctiles(capex_base),
        "contingency_sar_m_reported_not_added": _pctiles(contingency),
        "opex_sar_m_per_year": _pctiles(opex_total),
        "renewals_sar_m_undiscounted": {f"{h}y": _pctiles(ren[h]) for h in HORIZONS},
        "staffing": staffing,
    }
    return summary, df, trace


def _pct_row(name: str, rid: str, it: dict[str, Any], x: np.ndarray) -> dict[str, Any]:
    return {
        "component": name,
        "group": "construction",
        "register_id": rid,
        "status": it["status"],
        "quantity": None,
        "quantity_unit": "% of construction",
        "unit": "pct_of_capex",
        "P10": float(np.percentile(x, 10)),
        "P50": float(np.percentile(x, 50)),
        "P90": float(np.percentile(x, 90)),
    }


def load_profile(line: LineSpec, profiles: Path, costing: Path | None) -> dict[str, Any]:
    prof = dict(yaml.safe_load(profiles.read_text(encoding="utf-8"))["profiles"][line.line_type])
    if costing:
        prof |= yaml.safe_load(costing.read_text(encoding="utf-8")).get("costing", {})
    return prof


def assumption_ids(obj: Any) -> set[str]:
    out: set[str] = set()
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k.endswith("assumption_id") and isinstance(v, str):
                out.add(v)
            out |= assumption_ids(v)
    elif isinstance(obj, list):
        for v in obj:
            out |= assumption_ids(v)
    return out


@app.command()
def main(
    corridor: Path = typer.Option(..., "--corridor"),
    register: Path = typer.Option(REGISTER, "--register"),
    uplifts: Path = typer.Option(UPLIFTS, "--uplifts"),
    out: Path = typer.Option(..., "--out"),
    seed: int = seed_option(),
    draws: int = typer.Option(10_000, "--draws", min=100),
    profiles: Path = typer.Option(PROFILES, "--profiles"),
    cmap_path: Path = typer.Option(MAP, "--map"),
    costing: Path | None = typer.Option(None, "--costing", help="optional `costing:` override"),
    index: Path = typer.Option(INDEX, "--index"),
) -> None:
    """Write base.yaml, trace.csv, distribution.parquet, rcf/ and meta.json under --out."""
    line = LineSpec.model_validate(yaml.safe_load(corridor.read_text(encoding="utf-8")))
    reg = normalised_lookup(register, index)
    prof = load_profile(line, profiles, costing)
    cmap = yaml.safe_load(cmap_path.read_text(encoding="utf-8"))
    summary, df, trace = estimate(line, reg, prof, cmap, seed, draws)
    ups = load_uplifts(uplifts)
    stage = (
        prof.get("appraisal_stage", {}).get("value", "strategic")
        if isinstance(prof.get("appraisal_stage"), dict)
        else prof.get("appraisal_stage", "strategic")
    )
    base_rcf = {
        "line_type": line.line_type,
        "stage": stage,
        "capex": {"unit": "SAR_m (2025)"},
        "schedule_years": {
            k: float(prof["construction_years"][k]) for k in ("low", "central", "high")
        },
    }
    rcf_summary, rcf_df = rcf.apply(
        base_rcf, ups, seed, draws, base_draws=df["capex_base"].to_numpy()
    )
    summary["capex_uplifted_sar_m"] = rcf_summary["capex"]["uplifted"]
    summary["schedule"] = rcf_summary.get("schedule")
    summary["uplifts_used"] = rcf_summary["uplifts_used"]
    out.mkdir(parents=True, exist_ok=True)
    (out / "rcf").mkdir(exist_ok=True)
    (out / "base.yaml").write_text(yaml.safe_dump(summary, sort_keys=False), "utf-8")
    (out / "rcf" / "summary.yaml").write_text(yaml.safe_dump(rcf_summary, sort_keys=False), "utf-8")
    rcf_df.to_parquet(out / "rcf" / "distribution.parquet", index=False)
    df.to_parquet(out / "distribution.parquet", index=False)
    pd.DataFrame(trace).to_csv(out / "trace.csv", index=False)
    used = sorted({i for t in trace for i in t["register_id"].split(", ")})
    write_meta(
        out,
        seed,
        {
            "corridor": yaml.safe_load(corridor.read_text("utf-8")),
            "profile": prof,
            "map": cmap,
            "draws": draws,
        },
        {
            "register_ids": used,
            "assumptions": sorted(
                assumption_ids(prof)
                | set(cmap.get("assumptions", []))
                | {reg[i]["assumption_id"] for i in used if reg[i].get("assumption_id")}
                | (
                    {"A-cost-009"}
                    if any(
                        reg[i].get("index_factor", {}).get("id", "").endswith("asbase")
                        for i in used
                    )
                    else set()
                )
                | {"A-cost-001", "A-cost-002", "A-cost-003", "A-cost-004", "A-cost-008"}
                | {v["assumption_id"] for v in rcf_summary["uplifts_used"].values()}
            ),
            "register": str(register.relative_to(REPO_ROOT))
            if register.is_absolute() and register.is_relative_to(REPO_ROOT)
            else str(register),
        },
    )
    c, u = summary["capex_base_sar_m"], summary["capex_uplifted_sar_m"]
    typer.echo(
        f"{line.id}: capex base P10 {c['P10']:,.0f} / P50 {c['P50']:,.0f} / "
        f"P90 {c['P90']:,.0f} SAR m; "
        f"uplifted P50 {u['P50']:,.0f} / P80 {u['P80']:,.0f}; {LABEL}"
    )


if __name__ == "__main__":
    app()
