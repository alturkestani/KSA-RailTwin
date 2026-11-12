# ruff: noqa: E501
"""Markdown tables for docs/network-evaluation.md and docs/commute-test.md, generated from the R4
run outputs (never hand-copied). Writes runs/r4/doc-tables/r4-*.md fragments that the two documents
include verbatim between `<!-- r4:<name> -->` markers.
  uv run python scripts/r4_doc_tables.py
Label: synthetic demand, uncalibrated: scenario comparison, not a forecast.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
R = ROOT / "runs"


def fmt(x: float, nd: int = 1) -> str:
    if x is None or (isinstance(x, float) and pd.isna(x)):
        return "n/a"
    return f"{x:,.{nd}f}"


def md(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    out += ["| " + " | ".join(str(v) for v in r) + " |" for r in df.itertuples(index=False)]
    return "\n".join(out)


def gate() -> str:
    f = json.loads((R / "access/running_time/factors-s1/factors.json").read_text())
    rows = [
        {
            "pair": p["id"],
            "published min": fmt(p["published_min"], 0),
            "source": p["published_source"],
            "kinematic min": fmt(p["model_min"]),
            "error %": fmt(p["error_pct"]),
            "published / kinematic": fmt(p["factor"], 3),
        }
        for p in f["pairs"]
    ]
    g = [
        {
            "gate pair": x["id"],
            "published": fmt(x["published_min"], 0),
            "kinematic": fmt(x["kinematic_min"]),
            "leave-one-out factor": fmt(x["loo_factor"], 3),
            "predicted": fmt(x["predicted_min"]),
            "error %": fmt(x["error_pct"]),
            "±10 %": "pass" if x["pass"] else "FAIL",
        }
        for x in f["gate"]
    ]
    gen = f["generic"]
    return (
        md(pd.DataFrame(rows))
        + "\n\n"
        + md(pd.DataFrame(g))
        + f"\n\nGeneric timetable factor (planned and hypothetical lines, A-r4-rt-011): **{gen['value']}** (median of the current pairs), range {gen['range'][0]}–{gen['range'][1]} (all pairs). Run `runs/access/running_time/factors-s1/`."
    )


def landbridge() -> str:
    def t(p):
        return json.loads(p.read_text())

    r3 = {
        s: t(R / f"demand/{s}-un_wpp_medium_gastat2024-2025-base-s1/totals.json")
        for s in ("S0", "S1")
    }
    r4 = {s: t(R / f"r4/demand/{s}-r4-2025-base-s1/totals.json") for s in ("S0", "S1")}
    rows = []
    for tag, d, rid in (
        (
            "R3 (single line, no wait in line choice, centroid sites)",
            r3,
            "runs/demand/S*-un_wpp_medium_gastat2024-2025-base-s1",
        ),
        ("R4 (rail graph, located sites, transfers)", r4, "runs/r4/demand/S*-r4-2025-base-s1"),
    ):
        hhr0, hhr1 = (
            d["S0"]["rail_by_line"]["hhr"]["passengers"],
            d["S1"]["rail_by_line"]["hhr"]["passengers"],
        )
        rows.append(
            {
                "model": tag,
                "rail S0 (M)": fmt(d["S0"]["by_mode"]["rail"] / 1e6, 2),
                "rail S1 (M)": fmt(d["S1"]["by_mode"]["rail"] / 1e6, 2),
                "S1 − S0 rail (M)": fmt(
                    (d["S1"]["by_mode"]["rail"] - d["S0"]["by_mode"]["rail"]) / 1e6, 2
                ),
                "HHR S1 − S0 (M)": fmt((hhr1 - hhr0) / 1e6, 2),
                "Landbridge S1 (M)": fmt(
                    d["S1"]["rail_by_line"].get("landbridge", {}).get("passengers", 0) / 1e6, 2
                ),
                "S1 − S0 car (M)": fmt(
                    (d["S1"]["by_mode"]["car"] - d["S0"]["by_mode"]["car"]) / 1e6, 2
                ),
                "runs": rid,
            }
        )
    return md(pd.DataFrame(rows))


def calibration() -> str:
    c = json.loads((R / "r4/demand/calibration-r4-s1/calibration.json").read_text())
    adj = pd.DataFrame(
        [
            {
                "constant": a["parameter"],
                "prior": a["prior"],
                "R4 fitted": round(a["fitted"], 3),
                "range": f"{a['range'][0]} to {a['range'][1]}",
                "at bound": a["at_bound"],
                "assumption": a["assumption"],
            }
            for a in c["adjustments"]
        ]
    )
    fit = pd.DataFrame(
        [
            {
                "target": x["id"],
                "observed": fmt(x["observed"], 0),
                "modelled": fmt(x["modelled"], 0),
                "deviation %": fmt(x["deviation_pct"]),
                "status": x["status"],
            }
            for x in c["fit_targets"]
        ]
    )
    u = c["unbounded_diagnostic"]["x"]
    return (
        md(adj)
        + "\n\n"
        + md(fit)
        + f"\n\nUnbounded diagnostic (not adopted): asc.rail {u['asc.rail']:.2f}, asc.air {u['asc.air']:.2f}, asc.bus {u['asc.bus']:.2f}. Run `runs/r4/demand/calibration-r4-s1/`."
    )


def airports() -> str:
    t = pd.read_csv(R / "r4/demand/calibration-r4-s1/targets_table.csv")
    a = t[t.id.str.match(r"air-dom-[a-z]+-2025:departures")]
    rows = [
        {
            "airport": x.id.split("-")[2].upper(),
            "observed dep.": fmt(x.observed, 0),
            "modelled": fmt(x.modelled, 0),
            "deviation %": fmt(x.deviation_pct),
            "status": x.status,
        }
        for x in a.itertuples()
    ]
    return md(pd.DataFrame(rows))


def hhr() -> str:
    h = json.loads((R / "network-eval/hhr-validation-s1/hhr_validation.json").read_text())
    rows = [
        {
            "scenario": r["scenario"],
            "intl rail share": {"value": "central 0.176", "low": "low 0.026", "high": "high 0.470"}[
                r["rail_share_case"]
            ],
            "resident (M)": fmt(r["resident"] / 1e6, 2),
            "international (M)": fmt(r["international"] / 1e6, 2),
            "total (M)": fmt(r["total"] / 1e6, 2),
            "observed 2025 (M)": fmt(r["observed_2025"] / 1e6, 2),
            "without %": fmt(r["deviation_without_pct"]),
            "with %": fmt(r["deviation_with_pct"]),
            "with inside ±15 %": "yes" if r["within_tolerance_with"] else "no",
            "status": r["status"],
        }
        for r in h["rows"]
    ]
    return (
        md(pd.DataFrame(rows))
        + f"\n\nRail share that would reproduce HHR exactly (S0, diagnostic, not adopted): {h['implied_rail_share_for_exact_fit_S0']:.3f}. "
        f"Ramadan check: observed HHR March 2025 / mean month = {h['ramadan_factor_observed_march_2025']:.2f} (GASTAT Table 1-2); modelled S0 central = {h['ramadan_factor_model_central_S0']:.2f}. Run `runs/network-eval/hhr-validation-s1/`."
    )


def peaks() -> str:
    rows = []
    for s in ("S0", "S1"):
        t = json.loads((R / f"intl/{s}-s1/totals.json").read_text())
        for ln, p in t["peaks"].items():
            rows.append(
                {
                    "scenario": s,
                    "line": ln,
                    "intl average day": fmt(p["average_daily"], 0),
                    "intl Ramadan day": fmt(p["ramadan_daily"], 0),
                    "intl Hajj-window day (arrival legs)": fmt(p["hajj_window_daily"], 0),
                    "intl rail trips/yr central (low–high)": f"{fmt(t['rail_by_line'][ln]['value'], 0)} ({fmt(t['rail_by_line'][ln]['low'], 0)}–{fmt(t['rail_by_line'][ln]['high'], 0)})",
                }
            )
    return (
        md(pd.DataFrame(rows))
        + "\n\nRuns `runs/intl/S0-s1/`, `runs/intl/S1-s1/` (central rail share 0.176; daily = month / 30, Hajj window / 29). "
        + "The peak loads are proportional to the rail share: at the low and high ends of A-intl-003 multiply them by "
        + "0.026 / 0.176 = 0.15 and 0.470 / 0.176 = 2.67; at the share that reproduces HHR 2025 (0.033) by 0.19."
    )


def isochrones() -> str:
    d = pd.read_parquet(R / "access/isochrones-summary-s1/reached_all.parquet")
    s = d[d.scenario.isin(["S0", "S1"])]
    rows = []
    for (metro, sc), g in s.groupby(["metro", "scenario"], sort=False):

        def pop(m, b, g=g):
            return fmt(float(g[(g["mode"] == m) & (g.band_min == b)].population.iloc[0]) / 1e6, 2)

        rows.append(
            {
                "metro": metro,
                "scenario": sc,
                "boarding stations": g.main_station.iloc[0] or "none within 90 road-min",
                "in-vehicle 30/45/60 (M)": f"{pop('in_vehicle', 30)} / {pop('in_vehicle', 45)} / {pop('in_vehicle', 60)}",
                "door-to-door 30/45/60 (M)": f"{pop('door_to_door', 30)} / {pop('door_to_door', 45)} / {pop('door_to_door', 60)}",
                "car peak 30/45/60 (M)": f"{pop('car_peak', 30)} / {pop('car_peak', 45)} / {pop('car_peak', 60)}",
            }
        )
    df = pd.DataFrame(rows).sort_values(["metro", "scenario"])
    cand = d[~d.scenario.isin(["S0", "S1"])].merge(
        s[s.scenario == "S1"][["metro", "mode", "band_min", "population"]],
        on=["metro", "mode", "band_min"],
        suffixes=("", "_s1"),
    )
    cand["delta"] = cand.population - cand.population_s1
    top = (
        cand[(cand["mode"] == "in_vehicle") & (cand.band_min == 60)]
        .groupby(["scenario"])
        .delta.sum()
        .sort_values(ascending=False)
    )
    best = pd.DataFrame(
        {
            "candidate": top.index[:12],
            "in-vehicle 60 min, population added vs S1 over all metros (M)": [
                fmt(v / 1e6, 2) for v in top.values[:12]
            ],
        }
    )
    neg = cand[cand.delta < -1]
    return (
        md(df)
        + "\n\nPopulation: WPP medium anchored to GASTAT 2024, 2025 (the R3 calibration point, R3 zones). Runs `runs/access/<scenario>/reached.parquet`, GeoJSON `runs/access/<scenario>/<metro>/isochrone_*.geojson`, all rows `runs/access/isochrones-summary-s1/reached_all.parquet`.\n\n"
        + "**Candidates adding the most in-vehicle 60-minute reach** (sum over the 11 metros, change against S1):\n\n"
        + md(best)
        + (
            "\n\nNo candidate has less reach than S1 in any metro, mode or band."
            if neg.empty
            else f"\n\nCandidates with less reach than S1 somewhere: {', '.join(sorted(neg.scenario.unique()))}."
        )
    )


def commute() -> str:
    ct = pd.read_parquet(R / "access/commute-test-s1/commute_test.parquet")
    out = []
    for metro, g in ct.groupby("metro"):
        towns = g[["row_key", "town", "road_km", "car_peak_min", "population"]].drop_duplicates(
            "row_key"
        )
        rows = []
        for t in towns.sort_values("road_km").itertuples():
            gg = g[g.row_key == t.row_key]
            s0 = gg[gg.scenario == "S0"].iloc[0]
            s1 = gg[gg.scenario == "S1"].iloc[0]
            cands = gg[~gg.scenario.isin(["S0", "S1"])].dropna(subset=["ivt_min"])
            if len(cands):
                b = cands.sort_values("ivt_min").iloc[0]
                best = (
                    f"{b.scenario}: {fmt(b.ivt_min)} ({fmt(b.ivt_min_low)}–{fmt(b.ivt_min_high)}) in-vehicle, {fmt(b.d2d_min, 0)} door-to-door; "
                    f"≤ 30: {'yes' if b.within_30_ivt else 'no'}; in the model, car trips fell by {fmt(-b.car_trip_change_pct_hi)}–{fmt(-b.car_trip_change_pct_lo)} %"
                )
            else:
                best = "no candidate serves this pair by rail"

            def cell(r):
                if pd.isna(r.ivt_min):
                    return "no rail"
                return (
                    f"{fmt(r.ivt_min)} / {fmt(r.d2d_min, 0)} ({'yes' if r.within_30_ivt else 'no'})"
                )

            rows.append(
                {
                    "town": t.town,
                    "road km": fmt(t.road_km, 0),
                    "car AM peak min": fmt(t.car_peak_min, 0),
                    "S0 in-vehicle / door-to-door (≤ 30?)": cell(s0),
                    "S1": cell(s1),
                    "best candidate (run id)": best,
                }
            )
        n30 = {
            s: int(g[(g.scenario == s) & g.within_30_ivt].row_key.nunique()) for s in ("S0", "S1")
        }
        nbest = int(g[~g.scenario.isin(["S0", "S1"]) & g.within_30_ivt].row_key.nunique())
        out.append(
            f"### {metro} (tier {int(g.tier.iloc[0])})\n\nLabel: synthetic demand, uncalibrated: scenario comparison, not a forecast. "
            f"Towns 40–120 road-km: {len(towns)}. Towns with a ≤ 30-minute in-vehicle rail time: S0 {n30['S0']}, S1 {n30['S1']}, with at least one S2–S5 candidate {nbest}.\n\n"
            + md(pd.DataFrame(rows))
        )
    return "\n\n".join(out)


def summary() -> str:
    rows = []
    for s in ("S2", "S3", "S4", "S5"):
        d = pd.read_parquet(R / f"network-eval/{s}/summary.parquet")
        rows.append(
            {
                "family": s,
                "candidates": len(d),
                "km (sum)": fmt(d.km.sum(), 0),
                "capex base P50, SAR bn (sum, range of P10–P90 sums)": f"{fmt(d.capex_p50.sum() / 1e3)} ({fmt(d.capex_p10.sum() / 1e3)}–{fmt(d.capex_p90.sum() / 1e3)})"
                + (
                    " (station item, spread since R5 H10a; see the uplifted column)"
                    if s == "S5"
                    else ""
                ),
                "capex uplifted P50, SAR bn (sum, P10–P90 sums)": f"{fmt(d.capex_uplifted_p50.sum() / 1e3)} ({fmt(d.capex_uplifted_p10.sum() / 1e3)}–{fmt(d.capex_uplifted_p90.sum() / 1e3)})",
                "candidates adding ≤ 30-min towns vs S1": int(
                    (d.towns_within_30_new_vs_s1 > 0).sum()
                ),
                "file": f"runs/network-eval/{s}/summary.parquet",
            }
        )
    return md(pd.DataFrame(rows))


def main() -> None:
    out = ROOT / "runs/r4/doc-tables"
    out.mkdir(parents=True, exist_ok=True)
    parts = {
        "gate": gate,
        "landbridge": landbridge,
        "calibration": calibration,
        "airports": airports,
        "hhr": hhr,
        "peaks": peaks,
        "isochrones": isochrones,
        "commute": commute,
        "summary": summary,
    }
    for name, fn in parts.items():
        (out / f"r4-{name}.md").write_text(fn() + "\n", encoding="utf-8")
    for doc in ("docs/network-evaluation.md", "docs/commute-test.md"):
        p = ROOT / doc
        if not p.exists():
            continue
        s = p.read_text(encoding="utf-8")
        for name in parts:
            block = (out / f"r4-{name}.md").read_text(encoding="utf-8").rstrip()
            s = re.sub(
                rf"<!-- r4:{name} -->.*?<!-- /r4:{name} -->",
                lambda _m, b=block, n=name: f"<!-- r4:{n} -->\n{b}\n<!-- /r4:{n} -->",
                s,
                flags=re.S,
            )
        p.write_text(s, encoding="utf-8")
    print("ok")


if __name__ == "__main__":
    main()
