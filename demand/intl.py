"""International-visitor segment: foreign Umrah performers and Hajj pilgrims (R4; prompts/R4.md
"international-visitor segment"; CP4 requirement 5; the segment R3 lacked, A-demand-059).

Build rule:
- foreign arrivals 2025 from the GASTAT tables in data/ksa/tables/pilgrims/ (Umrah: the four 2025
  quarters, Q2 revised; Hajj 1446 by way of arrival), read by script;
- split by entry port with `cities/ksa/population/intl_airport_split.yaml` (row for the year, else
  the 1440-1442 AH pooled shares, A-intl-001; Hajj 2022 flight split as cross-check, A-intl-002);
- itinerary legs (A-intl-006/007): airport -> first holy city, Makkah <-> Madinah where the visit
  includes both, last city -> airport; land and sea arrivals have no airport leg (their inter-city
  legs are kept);
- rail trips per leg = rail share (A-intl-003, assumed, low/central/high) where the scenario's rail
  graph (access.railgraph) has a path between the leg's zones; per-line loads from the path;
- peaks: Ramadan month factor from the 1440 AH Hijri-month series (A-intl-004) and the Hajj arrival
  window (A-intl-005), as monthly and daily loads.

  uv run python -m demand.intl split --seed 1
  uv run python -m demand.intl run --scenario S1 --seed 1 --out runs/intl/S1-s1/

Label: synthetic demand, uncalibrated: scenario comparison, not a forecast. HHR status with the
segment: validation, not fitted.
"""

from __future__ import annotations

import json
import re
import warnings
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import typer
import yaml

from common import REPO_ROOT
from common.labels import LABEL
from common.runmeta import seed_option, write_meta

PILGRIMS = Path("data/ksa/tables/pilgrims")
SPLIT = Path("cities/ksa/population/intl_airport_split.yaml")
SEGMENT = Path("cities/ksa/population/intl_segment.yaml")
GRAVITY = Path("cities/ksa/assumptions/demand_gravity.yaml")
HIJRI = [
    "Moharram",
    "Safar",
    "Rabi1",
    "Rabi2",
    "Jumada1",
    "Jumada2",
    "Rajab",
    "Shaban",
    "Ramadan",
    "Shawwal",
    "Dhu al-qadah",
]
BULLETINS = {
    "1440": "umrah_statistics_bulletin_2019.xlsx",
    "1441": "umrah_statistics_bulletin_2020_(1).xlsx",
    "1442": "UMR_ANN2021_(1).xlsx",
}
QUARTERS_2025 = {
    "Q1": "Umrah Statistics  Q1 2025-EN (1).xlsx",
    "Q2": "Umrah Statistics Q2-2025-EN (1).xlsx",
    "Q3": "Umrah_Statistics_for_Q3_of_2025-EN_(1).xlsx",
    "Q4": "Umrah Statistics for Q4 of 2025 EN (1).xlsx",
}
QUARTERS_2024 = {
    "Q1": "Umrah_Statistics_Q1_of_2024__EN.xlsx",
    "Q2": "Umrah_Statistics_Q2_of_2024_EN.xlsx",
    "Q3": "Umrah_Statistics_Q3_of_2024_EN.xlsx",
    "Q4": "Umrah_Statistics_Q4_of_2024_EN.xlsx",
}
HAJJ_2025 = "Hajj_Statistics_2025_EN_(3).xlsx"
HAJJ_2022 = "Hajj_Statistics_2022_En.xlsx"
MONTHS = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]

app = typer.Typer(add_completion=False, help=__doc__, no_args_is_help=True)


@app.callback()
def _group() -> None:
    """International-visitor segment."""


def _v(node: Any) -> Any:
    return node["value"] if isinstance(node, dict) and "value" in node else node


def _sheets(path: Path) -> dict[str, pd.DataFrame]:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        x = pd.ExcelFile(path)
        return {s: x.parse(s, header=None).fillna("") for s in x.sheet_names}


def _cells(row: Any) -> list[str]:
    return [str(v).strip() for v in row if str(v).strip()]


def _num(s: str) -> float:
    return float(str(s).replace(",", ""))


# --------------------------------------------------------------------------- readers
def port_table(year_ah: str, root: Path = REPO_ROOT) -> pd.DataFrame:
    """Table 3 of an Umrah bulletin: foreign performers by entry port x Hijri month."""
    sh = _sheets(root / PILGRIMS / BULLETINS[year_ah])
    d = next(df for name, df in sh.items() if name.strip() == "3.")
    rows = []
    for r in d.values:
        c = _cells(r)
        nums = [x for x in c if re.fullmatch(r"\d+(\.\d+)?", x)]
        names = [x for x in c if re.search(r"[A-Za-z]", x)]
        if len(nums) == 12 and names:
            vals = [_num(x) for x in nums]
            if year_ah == "1442":  # this bulletin prints Total first, then months in reverse
                total, months = vals[0], vals[1:][::-1]
            else:
                months, total = vals[:11], vals[11]
            rows.append({"port": names[0], **dict(zip(HIJRI, months, strict=True)), "total": total})
    return pd.DataFrame(rows)


def compute_split(root: Path = REPO_ROOT) -> dict[str, Any]:
    """Pooled 1440-1442 shares by model airport (+ land, sea) and the per-year range."""
    seg = yaml.safe_load((root / SEGMENT).read_text(encoding="utf-8"))
    p2a = seg["port_to_airport"]
    per_year = {}
    pooled: dict[str, float] = {}
    grand = 0.0
    for y in BULLETINS:
        t = port_table(y, root)
        t = t[t.port.str.lower() != "total"]
        tot = float(t.total.sum())
        grand += tot
        shares: dict[str, float] = {}
        for r in t.itertuples(index=False):
            key = p2a.get(r.port)
            if key is None:
                low = r.port.lower()
                if "islamic port" in low or "commercial port" in low:
                    key = "sea"
                elif "airport" in low or "air base" in low:
                    key = "air_other"
                else:
                    key = "land"
            shares[key] = shares.get(key, 0.0) + float(r.total)
            pooled[key] = pooled.get(key, 0.0) + float(r.total)
        per_year[y] = {"total": tot, "shares": {k: v / tot for k, v in sorted(shares.items())}}
    keys = sorted(pooled)
    out = {
        "pooled_total": grand,
        "shares": {k: round(pooled[k] / grand, 5) for k in keys},
        "range": {
            k: [
                round(min(per_year[y]["shares"].get(k, 0.0) for y in per_year), 5),
                round(max(per_year[y]["shares"].get(k, 0.0) for y in per_year), 5),
            ]
            for k in keys
        },
        "per_year": {
            y: {"total": v["total"], "shares": {k: round(s, 5) for k, s in v["shares"].items()}}
            for y, v in per_year.items()
        },
    }
    return out


def hijri_profile(root: Path = REPO_ROOT) -> dict[str, float]:
    t = port_table("1440", root)
    tot = t[t.port.str.lower() == "total"].iloc[0]
    return {m: float(tot[m]) for m in HIJRI}


def gregorian_months(files: dict[str, str], root: Path = REPO_ROOT) -> dict[str, float]:
    """Monthly external Umrah performers from the quarterly 'by sex and month' tables."""
    out: dict[str, float] = {}
    for f in files.values():
        sh = _sheets(root / PILGRIMS / f)
        for _name, d in sh.items():
            head = " ".join(str(v) for v in d.iloc[:4].values.ravel())
            if not (
                re.search("external", head, re.I)
                and re.search("month", head, re.I)
                and re.search("sex|gender", head, re.I)
            ) or re.search("age|region", head, re.I):
                continue
            for r in d.values:
                c = _cells(r)
                if c and c[0] in MONTHS:
                    out[c[0]] = _num(c[-1])
            break
    return {m: out[m] for m in MONTHS if m in out}


def hajj_2025(root: Path = REPO_ROOT) -> dict[str, Any]:
    sh = _sheets(root / PILGRIMS / HAJJ_2025)
    mode: dict[str, float] = {}
    window: dict[str, float] = {}
    for d in sh.values():
        head = " ".join(str(v) for v in d.iloc[:5].values.ravel()).lower()
        if "ways of arrival" in head:
            for r in d.values:
                c = _cells(r)
                if c and c[0] in ("By air", "By land", "By sea", "Total"):
                    mode[c[0].replace("By ", "").lower()] = _num(c[3])
        if "date of arrival" in head:
            for r in d.values:
                c = _cells(r)
                if len(c) == 2 and re.search(r"\d+/\d+", c[0]):
                    window[c[0]] = _num(c[1])
    return {"by_mode": mode, "arrival_date_shares": window}


def hajj_2022_flights(root: Path = REPO_ROOT) -> dict[str, float]:
    sh = _sheets(root / PILGRIMS / HAJJ_2022)
    out: dict[str, float] = {}
    for d in sh.values():
        for r in d.values:
            c = _cells(r)
            # Table 10: airport | incoming | outgoing (incoming flights are the arrival split)
            if (
                len(c) >= 3
                and re.search(r"King Abdulaziz|Prince Mohamm", c[0])
                and re.fullmatch(r"[\d,.]+", c[1])
            ):
                key = "MED" if "Prince" in c[0] else "JED"
                out.setdefault(key, _num(c[1]))
    return out


def umrah_2025(root: Path = REPO_ROOT) -> dict[str, Any]:
    seg = yaml.safe_load((root / SEGMENT).read_text(encoding="utf-8"))
    months = gregorian_months(QUARTERS_2025, root)
    q2 = ["April", "May", "June"]
    first = sum(months[m] for m in q2)
    rev = float(_v(seg["umrah_total"]["q2_2025_revised"]))
    revised = {m: (months[m] * rev / first if m in q2 else months[m]) for m in months}
    return {
        "months_first_release": months,
        "months": revised,
        "total": sum(revised.values()),
        "total_first_release": sum(months.values()),
        "q2_first_release": first,
        "q2_revised": rev,
    }


def airport_split(year: int, root: Path = REPO_ROOT) -> dict[str, Any]:
    """The drop-in row for `year` (else the latest earlier row, else the default)."""
    doc = yaml.safe_load((root / SPLIT).read_text(encoding="utf-8"))
    years = {int(k): v for k, v in (doc.get("years") or {}).items()}
    usable = [y for y in years if y <= year]
    if usable:
        row = years[max(usable)]
        return {
            "year_row": max(usable),
            "status": row.get("status", "sourced"),
            "shares": row["shares"],
            "range": row.get("range", {k: [v, v] for k, v in row["shares"].items()}),
            "source": row.get("source"),
        }
    d = doc["default"]
    return {
        "year_row": "default",
        "status": d["status"],
        "shares": d["shares"],
        "range": d["range"],
        "source": d["source"],
        "assumption": d["assumption"],
    }


# --------------------------------------------------------------------------- legs
def holy_zones(root: Path = REPO_ROOT) -> dict[str, str]:
    from demand.gravity import destination_zone

    grav = yaml.safe_load((root / GRAVITY).read_text(encoding="utf-8"))
    dest = grav["pilgrimage"]["destinations"]
    return {
        "makkah": destination_zone(dest["umrah"], root)[0],
        "madinah": destination_zone(dest["madinah_visit"], root)[0],
    }


def airport_zones(root: Path = REPO_ROOT) -> dict[str, str]:
    import geopandas as gpd

    from demand.supply import airports

    ap = airports(root)
    zg = gpd.read_file(root / "cities/ksa/zones/zones.geojson")[["zone_id", "geometry"]]
    pts = gpd.GeoDataFrame(ap, geometry=gpd.points_from_xy(ap.lon, ap.lat), crs=4326)
    j = gpd.sjoin(pts, zg, predicate="within")
    return dict(zip(j.iata, j.zone_id, strict=True))


def legs(year: int, root: Path = REPO_ROOT, visit: str = "value") -> pd.DataFrame:
    """Annual leg volumes (persons per leg) by segment and arrival class."""
    seg = yaml.safe_load((root / SEGMENT).read_text(encoding="utf-8"))
    sp = airport_split(year, root)
    um = umrah_2025(root)
    hj = hajj_2025(root)
    vnode = seg["madinah_visit_share"]
    v = (
        float(vnode["value"])
        if visit == "value"
        else float(vnode["range"][0 if visit == "low" else 1])
    )
    first = seg["first_city"]
    hz = holy_zones(root)
    az = airport_zones(root)
    rows = []
    air_keys = [k for k in sp["shares"] if k in first]
    air_share = sum(sp["shares"][k] for k in air_keys)
    for segname, total, shares in (
        ("umrah", um["total"], dict(sp["shares"])),
        # Hajj: air arrivals split over the same airports (normalised); land and sea by mode
        ("hajj", None, None),
    ):
        if segname == "hajj":
            shares = {k: hj["by_mode"]["air"] * sp["shares"][k] / air_share for k in air_keys}
            shares["land"] = hj["by_mode"]["land"]
            shares["sea"] = hj["by_mode"]["sea"]
            persons = shares
        else:
            persons = {k: total * s for k, s in shares.items()}
        for k, n in persons.items():
            if k in first:
                c1 = first[k]
                c2 = "madinah" if c1 == "makkah" else "makkah"
                # the other holy city: share v (Madinah) or always (Makkah, Umrah and Hajj)
                p_other = v if c2 == "madinah" else 1.0
                rows += [
                    {
                        "segment": segname,
                        "entry": k,
                        "leg": "arrival",
                        "o": az.get(k),
                        "d": hz[c1],
                        "persons": n,
                    },
                    {
                        "segment": segname,
                        "entry": k,
                        "leg": "intercity_out",
                        "o": hz[c1],
                        "d": hz[c2],
                        "persons": n * p_other,
                    },
                    {
                        "segment": segname,
                        "entry": k,
                        "leg": "intercity_back",
                        "o": hz[c2],
                        "d": hz[c1],
                        "persons": n * p_other,
                    },
                    {
                        "segment": segname,
                        "entry": k,
                        "leg": "departure",
                        "o": hz[c1],
                        "d": az.get(k),
                        "persons": n,
                    },
                ]
            elif k in ("land", "sea"):
                # no airport leg; the Madinah visit as an inter-city round trip from Makkah
                rows += [
                    {
                        "segment": segname,
                        "entry": k,
                        "leg": "intercity_out",
                        "o": hz["makkah"],
                        "d": hz["madinah"],
                        "persons": n * v,
                    },
                    {
                        "segment": segname,
                        "entry": k,
                        "leg": "intercity_back",
                        "o": hz["madinah"],
                        "d": hz["makkah"],
                        "persons": n * v,
                    },
                ]
    df = pd.DataFrame(rows)
    df = df[df.o.notna() & df.d.notna() & (df.o != df.d) & (df.persons > 0)].reset_index(drop=True)
    return df


def rail_share(root: Path = REPO_ROOT) -> dict[str, float]:
    seg = yaml.safe_load((root / SEGMENT).read_text(encoding="utf-8"))
    n = seg["rail_share_given_path"]
    return {"value": float(n["value"]), "low": float(n["range"][0]), "high": float(n["range"][1])}


def peaks(root: Path = REPO_ROOT) -> dict[str, Any]:
    hp = hijri_profile(root)
    year_mean = sum(hp.values()) / 12.0  # Dhu al-Hijjah (Hajj month) carries no Umrah entries
    g24 = gregorian_months(QUARTERS_2024, root)
    g25 = umrah_2025(root)["months"]
    # Ramadan 1445 = 11 Mar-9 Apr 2024 (March holds most of it); Ramadan 1446 = 1-30 Mar 2025
    r24 = g24["March"] / (sum(g24.values()) / 12.0)
    r25 = g25["March"] / (sum(g25.values()) / 12.0)
    hj = hajj_2025(root)
    win = sum(
        v
        for k, v in hj["arrival_date_shares"].items()
        if not k.lower().startswith("from the beginning")
    )
    return {
        "ramadan_month_factor": {
            "value": round(hp["Ramadan"] / year_mean, 3),
            "range": [round(min(r24, r25), 3), round(hp["Ramadan"] / year_mean, 3)],
            "basis": {"1440_AH": hp["Ramadan"] / year_mean, "2024_March": r24, "2025_March": r25},
            "assumption": "A-intl-004",
        },
        "hajj_window_share": {"value": round(win, 4), "days": 29, "assumption": "A-intl-005"},
        "months_2025": g25,
        "hijri_1440": hp,
    }


# --------------------------------------------------------------------------- scenario run
def run_segment(
    scenario: str, root: Path = REPO_ROOT, candidate: Path | None = None, year: int = 2025
) -> dict[str, Any]:
    from access import railgraph

    lg = legs(year, root)
    pairs = lg[["o", "d"]].drop_duplicates().reset_index(drop=True)
    los = railgraph.rail_los(pairs, scenario, root, candidate)
    lg = lg.merge(
        los[["o", "d", "avail_rail", "rail_path", "rail_line"]], on=["o", "d"], how="left"
    )
    sh = rail_share(root)
    pk = peaks(root)
    for case in ("value", "low", "high"):
        lg[f"rail_{case}"] = np.where(lg.avail_rail.fillna(False), lg.persons * sh[case], 0.0)
    by_line: dict[str, dict[str, float]] = {}
    for r in lg.itertuples(index=False):
        if not r.avail_rail or not isinstance(r.rail_path, str):
            continue
        for leg in r.rail_path.split("|"):
            ln = leg.split(":")[0]
            d = by_line.setdefault(ln, {"value": 0.0, "low": 0.0, "high": 0.0})
            for case in d:
                d[case] += getattr(r, f"rail_{case}")
    # seat-capacity ceiling for Hajj (a ceiling, not riders): >2 M HHR seats in Hajj 1446
    hajj_legs = float(lg[(lg.segment == "hajj") & lg.avail_rail.fillna(False)].persons.sum())
    # peak loads per line: Ramadan month (Umrah x factor / 12), Hajj window (arrival legs)
    ram = pk["ramadan_month_factor"]["value"]
    win = pk["hajj_window_share"]["value"]
    peak: dict[str, dict[str, float]] = {}
    for r in lg.itertuples(index=False):
        if not r.avail_rail or not isinstance(r.rail_path, str):
            continue
        for leg in r.rail_path.split("|"):
            ln = leg.split(":")[0]
            p = peak.setdefault(
                ln, {"ramadan_month": 0.0, "hajj_window_arrivals": 0.0, "average_month": 0.0}
            )
            p["average_month"] += r.rail_value / 12.0
            if r.segment == "umrah":
                p["ramadan_month"] += r.rail_value * ram / 12.0
            elif r.leg in ("arrival", "intercity_out"):
                p["hajj_window_arrivals"] += r.rail_value * win
    for p in peak.values():
        p["ramadan_daily"] = p["ramadan_month"] / 30.0
        p["hajj_window_daily"] = p["hajj_window_arrivals"] / 29.0
        p["average_daily"] = p["average_month"] * 12.0 / 365.0
    return {
        "legs": lg,
        "by_line": by_line,
        "peaks": peak,
        "hajj_legs_with_rail": hajj_legs,
        "peaks_inputs": {k: pk[k] for k in ("ramadan_month_factor", "hajj_window_share")},
    }


@app.command("split")
def split_cmd(
    seed: int = seed_option(),
    out: Path = typer.Option(Path("runs/intl/split-s1")),
    root: Path = typer.Option(REPO_ROOT, hidden=True),
) -> None:
    """Compute the 1440-1442 AH entry shares and write them into intl_airport_split.yaml default."""
    s = compute_split(root)
    flights = hajj_2022_flights(root)
    fsum = sum(flights.values())
    air = {k: v for k, v in s["shares"].items() if k in ("JED", "MED")}
    asum = sum(air.values())
    s["cross_check_hajj_2022_flights"] = {
        "flights": flights,
        "flight_shares": {k: round(v / fsum, 4) for k, v in flights.items()},
        "umrah_1440_1442_shares_of_JED_MED": {k: round(v / asum, 4) for k, v in air.items()},
        "assumption": "A-intl-002",
    }
    run = root / out
    run.mkdir(parents=True, exist_ok=True)
    (run / "split_1440_1442.json").write_text(json.dumps(s, indent=1) + "\n")
    text = (root / SPLIT).read_text(encoding="utf-8")
    doc = yaml.safe_load(text)
    doc["default"]["shares"] = s["shares"]
    doc["default"]["range"] = s["range"]
    head = "".join(line + "\n" for line in text.splitlines() if line.startswith("#"))
    (root / SPLIT).write_text(
        head + yaml.safe_dump(doc, sort_keys=False, width=120), encoding="utf-8"
    )
    write_meta(run, seed, {"split": s}, extra={"label": LABEL})
    typer.echo(
        json.dumps(
            {k: s[k] for k in ("shares", "range", "cross_check_hajj_2022_flights")}, indent=1
        )
    )


@app.command("run")
def run_cmd(
    scenario: str = typer.Option("S0"),
    candidate: Path | None = typer.Option(None),
    seed: int = seed_option(),
    out: Path = typer.Option(Path("runs/intl/S0-s1")),
    root: Path = typer.Option(REPO_ROOT, hidden=True),
) -> None:
    """International legs, rail trips per line (low/central/high share) and peak loads."""
    res = run_segment(scenario, root, candidate)
    run = root / out
    run.mkdir(parents=True, exist_ok=True)
    res["legs"].to_parquet(run / "legs.parquet", index=False)
    um, hj = umrah_2025(root), hajj_2025(root)
    tot = {
        "label": LABEL,
        "scenario": scenario,
        "candidate": str(candidate) if candidate else None,
        "umrah_2025": {
            k: um[k] for k in ("total", "total_first_release", "q2_first_release", "q2_revised")
        },
        "hajj_2025": hj,
        "airport_split": airport_split(2025, root),
        "persons_by_leg": res["legs"].groupby(["segment", "leg"]).persons.sum().round(0).to_dict(),
        "rail_by_line": {
            k: {c: round(x, 0) for c, x in v.items()} for k, v in res["by_line"].items()
        },
        "peaks": {k: {c: round(x, 0) for c, x in v.items()} for k, v in res["peaks"].items()},
        "peaks_inputs": res["peaks_inputs"],
        "hajj_legs_with_rail": round(res["hajj_legs_with_rail"], 0),
        "status": "validation, not fitted",
    }
    tot["persons_by_leg"] = {f"{a}|{b}": v for (a, b), v in tot["persons_by_leg"].items()}
    (run / "totals.json").write_text(json.dumps(tot, indent=1, default=float) + "\n")
    write_meta(
        run,
        seed,
        {
            "segment": yaml.safe_load((root / SEGMENT).read_text()),
            "split": tot["airport_split"],
            "scenario": scenario,
            "candidate": str(candidate),
        },
        extra={"label": LABEL},
    )
    typer.echo(
        json.dumps(
            {k: tot[k] for k in ("umrah_2025", "rail_by_line", "peaks")}, indent=1, default=float
        )
    )


if __name__ == "__main__":
    app()
