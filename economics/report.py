"""Summary table and generated documentation sections of the CBA (W4, R5).

`build_summary` flattens every runs/cba/<case>/results.json into runs/cba/summary.parquet (one row
per case x population scenario x horizon x rate case, every output as P10/P50/P90). `write`
renders the results section of docs/cba.md from that table only (never hand-typed), between the
markers BEGIN/END GENERATED RESULTS. `write_distribution` and `write_scorecard` write
docs/distribution.md and docs/cba-scorecard.md.

Label: synthetic demand, uncalibrated: scenario comparison, not a forecast.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

from common import REPO_ROOT
from common.labels import LABEL

BEGIN = "<!-- BEGIN GENERATED RESULTS (uv run python -m economics.cba report) -->"
END = "<!-- END GENERATED RESULTS -->"
FAMILIES = (
    ("trunk_gap", "S2 trunk gaps"),
    ("branch_spur", "S3 branches and spurs"),
    ("commuter_belt", "S4 commuter belts"),
    ("station_addition", "S5 station additions"),
    ("committed_programme", "S1 committed programme (vs S0)"),
)
POP, HZ, RC = "un_wpp_medium", 60, "greenbook_2026"
OUTS = (
    "pvb",
    "pvc",
    "npv",
    "npv_wei",
    "bcr",
    "bcr_wei",
    "eirr",
    "firr",
    "payback_years",
    "fiscal_cost",
    "pv_capex",
    "pv_opex_renewals",
    "pv_residual",
    "opening_year",
)


def build_summary(root: Path = REPO_ROOT) -> pd.DataFrame:
    rows = []
    for rj in sorted((root / "runs/cba").glob("CBA-*/results.json")):
        r = json.loads(rj.read_text(encoding="utf-8"))
        sv = json.loads((rj.parent / "switching_values.json").read_text(encoding="utf-8"))
        for x in r["results"]:
            row: dict[str, Any] = {
                "case": r["case"],
                "family": r["family"],
                "scenario": r["scenario"],
                "baseline": r["baseline"],
                "candidate": r["candidate"],
                "cost_run": r["cost_run"],
                "population": x["population"],
                "horizon": x["horizon"],
                "rate_case": x["rate_case"],
                "draws": r["draws"],
                "run_id": f"runs/cba/{rj.parent.name}",
                "label": LABEL,
            }
            for k, v in x.items():
                if isinstance(v, dict) and "P50" in v:
                    for q in ("P10", "P50", "P90"):
                        row[f"{k}_{q.lower()}"] = v.get(q)
            for k in ("demand_share_of_model_forecast", "capex_multiplier", "vot_multiplier"):
                row[f"sv_{k}"] = sv[k].get("value")
                row[f"sv_{k}_bound"] = sv[k].get("bound")
            row["sv_discount_rate_npv_zero"] = sv["discount_rate_npv_zero"].get("value")
            rows.append(row)
    return pd.DataFrame(rows)


def f(x: Any, d: int = 2, scale: float = 1.0, pct: bool = False) -> str:
    if x is None or (isinstance(x, float) and (math.isnan(x))):
        return "n/a"
    if isinstance(x, float) and math.isinf(x):
        return "∞" if x > 0 else "−∞"
    v = float(x) / scale
    if pct:
        return f"{100 * v:.1f} %"
    return f"{v:,.{d}f}"


def band(r: pd.Series, k: str, d: int = 2, scale: float = 1.0, pct: bool = False) -> str:
    def g(q: str) -> Any:
        return r.get(f"{k}_{q}")

    lo, mid, hi = g("p10"), g("p50"), g("p90")
    if pct:
        lo = "< −50 %" if lo is None else f(lo, pct=True)
        hi = "< −50 %" if hi is None else f(hi, pct=True)
        mid = "< −50 %" if mid is None else f(mid, pct=True)
        return f"{lo} / {mid} / {hi}"
    return f"{f(lo, d, scale)} / {f(mid, d, scale)} / {f(hi, d, scale)}"


def short(case: str) -> str:
    return case.replace("CBA-", "")


def sv_text(r: pd.Series, k: str, as_pct: bool = False) -> str:
    v = r.get(f"sv_{k}")
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return str(r.get(f"sv_{k}_bound") or "n/a")
    return f"{100 * v:.0f} %" if as_pct else f"{v:.2f}"


def results_markdown(df: pd.DataFrame) -> str:
    out: list[str] = []
    out.append(
        f"**{LABEL}.** Every figure below is a P10 / P50 / P90 range over the Monte Carlo draws "
        "(10,000 per case, seed 1), SAR bn at 2025 prices, present value at 2026, against the "
        "matched baseline (S1 for S2–S5; S0 for S1). In the model, these are scenario "
        "comparisons on synthetic, uncalibrated demand; they are not forecasts. Generated from "
        "`runs/cba/summary.parquet` by `uv run python -m economics.cba report`."
    )
    out.append("")
    c = df[(df.population == POP) & (df.horizon == HZ) & (df.rate_case == RC)]
    out.append(
        "Ranking basis: UN WPP medium population scenario, 60-year horizon, Green Book 2026 "
        "declining social rate (A-cba-001). BCR without wider impacts ranks; the BCR with wider "
        "impacts (TAG A2.4) is shown beside it, never added to the core BCR. Demand switching "
        "value = share of the modelled forecast at which BCR = 1 (central inputs); capex "
        "switching value = multiplier on central uplifted capex at which BCR = 1."
    )
    out.append("")
    for fam, title in FAMILIES:
        g = c[c.family == fam].sort_values("bcr_p50", ascending=False)
        if g.empty:
            continue
        out.append(f"#### {title} ({len(g)} cases)")
        out.append("")
        out.append(
            "| rank | case | BCR P10 / P50 / P90 | BCR with WEIs P10 / P50 / P90 | NPV SAR bn "
            "P10 / P50 / P90 | EIRR P10 / P50 / P90 | demand for BCR = 1 | capex × for BCR = 1 "
            "| run |"
        )
        out.append("|---|---|---|---|---|---|---|---|---|")
        for i, (_, r) in enumerate(g.iterrows(), 1):
            out.append(
                f"| {i} | {short(r.case)} | {band(r, 'bcr')} | {band(r, 'bcr_wei')} | "
                f"{band(r, 'npv', 1, 1000)} | {band(r, 'eirr', pct=True)} | "
                f"{sv_text(r, 'demand_share_of_model_forecast', True)} | "
                f"{sv_text(r, 'capex_multiplier')} | `{r.run_id}` |"
            )
        out.append("")
    out.append("#### P50 BCR range across cases, by horizon, rate case and population scenario")
    out.append("")
    out.append(
        "Each cell: lowest and highest case P50 BCR (without WEIs) in the family, and the "
        "number of cases whose P50 BCR is at least 1. Ranges, not points."
    )
    out.append("")
    out.append(
        "| family | population | horizon | Green Book 2026 | TAG declining | 5 % | 7 % | "
        "drawn rate |"
    )
    out.append("|---|---|---|---|---|---|---|---|")
    for fam, _title in FAMILIES:
        for pop in ("un_wpp_low", "un_wpp_medium", "un_wpp_high"):
            for h in (30, 40, 60):
                cells = []
                for rc in ("greenbook_2026", "tag_declining", "flat_5", "flat_7", "drawn"):
                    g = df[
                        (df.family == fam)
                        & (df.population == pop)
                        & (df.horizon == h)
                        & (df.rate_case == rc)
                    ]
                    if g.empty:
                        cells.append("n/a")
                        continue
                    b = g.bcr_p50.astype(float)
                    cells.append(f"{f(b.min())}–{f(b.max())} ({int((b >= 1).sum())}/{len(b)})")
                if all(x == "n/a" for x in cells):
                    continue
                out.append(f"| {fam} | {pop} | {h} | " + " | ".join(cells) + " |")
    out.append("")
    out.append("#### Fiscal cost, FIRR and payback (same ranking basis)")
    out.append("")
    out.append(
        "| case | fiscal cost to the state SAR bn P10 / P50 / P90 | FIRR P10 / P50 / P90 | "
        "payback years after opening P10 / P50 / P90 | opening year P10 / P50 / P90 |"
    )
    out.append("|---|---|---|---|---|")
    for fam, _t in FAMILIES:
        for _, r in c[c.family == fam].sort_values("bcr_p50", ascending=False).iterrows():
            out.append(
                f"| {short(r.case)} | {band(r, 'fiscal_cost', 1, 1000)} | "
                f"{band(r, 'firr', pct=True)} | {band(r, 'payback_years', 0)} | "
                f"{band(r, 'opening_year', 0)} |"
            )
    out.append("")
    out.append(
        "FIRR '< −50 %' means no internal rate of return in the search bracket (fares do not "
        "recover the costs); payback '∞' means the discounted net flow is still negative at the "
        "horizon end."
    )
    return "\n".join(out)


def write(summary: Path, doc: Path, root: Path = REPO_ROOT) -> None:
    df = pd.read_parquet(summary)
    body = results_markdown(df)
    text = doc.read_text(encoding="utf-8")
    if BEGIN not in text or END not in text:
        raise ValueError(f"{doc} has no generated-results markers")
    a, rest = text.split(BEGIN, 1)
    _, b = rest.split(END, 1)
    doc.write_text(a + BEGIN + "\n" + body + "\n" + END + b, encoding="utf-8")


# --------------------------------------------------------------------------- distribution
def write_distribution(root: Path = REPO_ROOT) -> None:
    from economics import cba, distribution
    from economics import params as prm

    p = prm.load(root)
    head = (root / "docs/distribution.md").read_text(encoding="utf-8")
    marker = "<!-- BEGIN GENERATED TABLES (uv run python -m economics.cli distribution) -->"
    end = "<!-- END GENERATED TABLES -->"
    a, rest = head.split(marker, 1)
    _, b = rest.split(end, 1)
    lines: list[str] = [f"**{LABEL}.**", ""]
    for cp in sorted((root / "cities/ksa/cba").glob("CBA-*.yaml")):
        case = cba.load_case(cp)
        run = root / "runs/cba" / case.id
        if not (run / "draws.parquet").exists():
            lines += [f"#### {short(case.id)}", "", "not appraised (no run).", ""]
            continue
        draws = pd.read_parquet(run / "draws.parquet")
        t = distribution.table(case, p, draws, root=root)
        res = json.loads((run / "results.json").read_text())
        cen = next(
            x
            for x in res["results"]
            if x["population"] == POP and x["horizon"] == HZ and x["rate_case"] == RC
        )
        lines += [f"#### {short(case.id)}", ""]
        lines += [
            "Who gains (user benefits by region, origin/destination halves, shares from the "
            "medium scenario at 2050; PV SAR m, P10 / P50 / P90):",
            "",
            "| region | population share | benefit share | benefit ÷ population share | user "
            "benefit PV SAR m P10 / P50 / P90 |",
            "|---|---|---|---|---|",
        ]
        for _, r in t["regions"].iterrows():
            lines.append(
                f"| {r.region} | {f(r.population_share, pct=True)} | "
                f"{f(r.benefit_share, pct=True)} | {f(r.benefit_to_population, 2)} | "
                f"{f(r.user_benefit_pv_p10, 0)} / {f(r.user_benefit_pv_p50, 0)} / "
                f"{f(r.user_benefit_pv_p90, 0)} |"
            )
        lines.append("")
        if len(t["bands"]):
            lines += [
                "Income-band proxy (regions by Saudi unemployment tercile, LFS Q4 2025; not "
                "household income, A-cba-311):",
                "",
                "| proxy band | population share | benefit share |",
                "|---|---|---|",
            ]
            for _, r in t["bands"].iterrows():
                lines.append(
                    f"| {r.proxy_band} | {f(r.population_share, pct=True)} | "
                    f"{f(r.benefit_share, pct=True)} |"
                )
            lines.append("")
        fc = cen["fiscal_cost"]
        rv = cen.get("pv_fare_revenue", {})
        lines += [
            "Who pays: fiscal cost to the state (fully public delivery, A-cba-312) PV SAR m "
            f"{f(fc['P10'], 0)} / {f(fc['P50'], 0)} / {f(fc['P90'], 0)}; fares paid by users PV "
            f"SAR m {f(rv.get('P10'), 0)} / {f(rv.get('P50'), 0)} / {f(rv.get('P90'), 0)}. "
            "Fare-to-income ratios: not available (no income-by-zone source, docs/social.md B4).",
            "",
        ]
        lo = t["left_out"]
        served = ", ".join(t["served_regions"]) or "none"
        if len(lo):
            txt = "; ".join(
                f"{r.region}: {int(r.towns)} towns, {f(r.population, 0)} persons"
                for _, r in lo.iterrows()
            )
        else:
            txt = "none"
        lines += [
            f"Who is left out (served regions: {served}): towns of 10,000+ more than "
            f"{p['access_distance_km'].value:.0f} km from every station after the case: {txt}. "
            "Freight-only route-km of the case: 0 (passenger or mixed service).",
            "",
        ]
    (root / "docs/distribution.md").write_text(
        a + marker + "\n" + "\n".join(lines) + "\n" + end + b, encoding="utf-8"
    )


# --------------------------------------------------------------------------- scorecard
def write_scorecard(root: Path = REPO_ROOT) -> None:
    """Qualitative scorecard rows per case from the corridor YAMLs and the register (roles of
    the towns a case serves); not monetised and not added to any BCR."""
    doc = root / "docs/cba-scorecard.md"
    text = doc.read_text(encoding="utf-8")
    marker = "<!-- BEGIN GENERATED SCORECARD (uv run python -m economics.cli scorecard) -->"
    end = "<!-- END GENERATED SCORECARD -->"
    a, rest = text.split(marker, 1)
    _, b = rest.split(end, 1)
    reg = pd.read_parquet(root / "cities/ksa/candidates.parquet")
    keymap = {str(k): r for k, r in zip(reg.row_key, reg.itertuples(), strict=True)}
    zones = pd.read_parquet(root / "runs/zones/zones.parquet")
    lines = [
        f"**{LABEL}.** Qualitative only: not monetised, not added to any BCR.",
        "",
        "| case | regions served | towns served (register) | economic roles at served towns | "
        "Hajj/Umrah node served | giga-project or tourism role served | lagging region served "
        "(Saudi unemployment above the Kingdom 7.2 %) |",
        "|---|---|---|---|---|---|---|",
    ]
    from economics import params as prm

    p = prm.load(root)
    un = p.raw["lfs_q4_2025_saudi_unemployment_pct"]["by_region"]
    for cp in sorted((root / "cities/ksa/cba").glob("CBA-*.yaml")):
        d = yaml.safe_load(cp.read_text(encoding="utf-8"))
        if not d.get("candidate"):
            lines.append(
                f"| {short(d['id'])} | programme (Landbridge, Riyadh Rail Link, GCC section) | "
                "n/a | n/a | n/a | n/a | n/a |"
            )
            continue
        c = yaml.safe_load((root / d["candidate"]).read_text(encoding="utf-8"))
        keys = [str(k) for k in c.get("generated_from_ids", [])]
        towns = [keymap[k] for k in keys if k in keymap]
        metros = [k.split(":", 1)[1] for k in keys if k.startswith("metro:")]
        regions = sorted(
            {t.region for t in towns}
            | {r for m in metros for r in zones.loc[zones.metro.eq(m), "region"]}
        )

        def _roles(t: Any) -> list[str]:
            v = t.economic_roles
            if v is None or (isinstance(v, float) and math.isnan(v)):
                return []
            return [str(x.get("role")) for x in list(v) if isinstance(x, dict)]

        roles = sorted({x for t in towns for x in _roles(t)} | {"metro" for _ in metros[:1]})
        names = [str(t.name_en) for t in towns] + [f"{m} (metro)" for m in metros]
        hajj = any("hajj" in r or "umrah" in r for r in roles)
        giga = any(("giga" in r) or ("tourism" in r) or ("heritage" in r) for r in roles)
        lag = [r for r in regions if float(un.get(r, 0)) > 7.2]
        lines.append(
            f"| {short(d['id'])} | {', '.join(regions) or 'n/a'} | "
            f"{', '.join(names) or 'n/a'} | {', '.join(roles) or 'none'} | "
            f"{'yes' if hajj else 'no'} | {'yes' if giga else 'no'} | "
            f"{', '.join(lag) or 'no'} |"
        )
    doc.write_text(a + marker + "\n" + "\n".join(lines) + "\n" + end + b, encoding="utf-8")


def quantiles(x: np.ndarray) -> dict[str, float]:
    return {f"P{q}": float(np.percentile(x, q)) for q in (10, 50, 90)}


# --------------------------------------------------------------------------- generated blocks
def matrix_markdown() -> str:
    from economics import benefits

    lines = [
        "| stream | channel it counts | channels it excludes | contains | in the totals as | "
        "method |",
        "|---|---|---|---|---|---|",
    ]
    for k, s in benefits.MATRIX.items():
        lines.append(
            f"| {k} | {s['channel']} | {', '.join(s['excludes']) or '—'} | "
            f"{', '.join(s.get('contains', [])) or '—'} | {s['in']} | {s['method']} |"
        )
    return "\n".join(lines)


def params_markdown(root: Path = REPO_ROOT) -> str:
    from economics import params as prm

    p = prm.load(root)
    lines = [
        "| key | value | low | high | unit | file | ids |",
        "|---|---|---|---|---|---|---|",
    ]
    for k in sorted(p.numeric):
        q = p.numeric[k]
        lines.append(
            f"| {k} | {q.value:g} | {q.low:g} | {q.high:g} | {q.unit} | {q.file} | "
            f"{', '.join(q.ids)} |"
        )
    return "\n".join(lines)


def jubail_markdown(df: pd.DataFrame) -> str:
    """CP5 H8: one shared Jubail station or two, from the results (in the model)."""
    ids = {
        "one station: Al Jubayl": "CBA-S5-station_addition-al-jubayl",
        "one station: Jubail Industrial City (Royal Commission)": (
            "CBA-S5-station_addition-al-jubayl-royal-commission"
        ),
        "two stations": "CBA-S5-station_addition-jubail-two-stations",
    }
    c = df[(df.population == POP) & (df.horizon == HZ) & (df.rate_case == RC)]
    lines = [
        "| option | BCR P10 / P50 / P90 | NPV SAR bn P10 / P50 / P90 | PV capex SAR bn P10 / P50 "
        "/ P90 | EIRR P10 / P50 / P90 |",
        "|---|---|---|---|---|",
    ]
    rows = {}
    for name, cid in ids.items():
        g = c[c.case == cid]
        if g.empty:
            lines.append(f"| {name} | not run | | | |")
            continue
        r = g.iloc[0]
        rows[name] = r
        lines.append(
            f"| {name} | {band(r, 'bcr')} | {band(r, 'npv', 2, 1000)} | "
            f"{band(r, 'pv_capex', 2, 1000)} | {band(r, 'eirr', pct=True)} |"
        )
    if len(rows) == 3:
        two = rows["two stations"]
        best_one = max((v for k, v in rows.items() if k != "two stations"), key=lambda r: r.npv_p50)
        col = f"npv|{POP}|{RC}"
        d2 = pd.read_parquet(REPO_ROOT / two.run_id / "draws.parquet", columns=[col])[col]
        d1 = pd.read_parquet(REPO_ROOT / best_one.run_id / "draws.parquet", columns=[col])[col]
        diff = (d2.to_numpy() - d1.to_numpy()) / 1000.0  # paired: the same cost-run draws
        q = np.percentile(diff, [10, 50, 90])
        lines += [
            "",
            "In the model (medium population, 60 years, Green Book 2026), NPV of two stations "
            f"minus the better single station ({short(best_one.case)}), paired by draw: SAR bn "
            f"{q[0]:,.2f} / {q[1]:,.2f} / {q[2]:,.2f} (P10 / P50 / P90; "
            f"{100 * float((diff < 0).mean()):.0f} % of draws negative). "
            + (
                "**Recommendation (in the model): one shared station**, because the second "
                "station lowers NPV in most draws and adds no reach."
                if q[1] <= 0
                else "**Recommendation (in the model): two stations**, because the second "
                "station raises NPV in most draws; check the P10 before committing."
            ),
            "",
            accessibility_markdown(),
        ]
    return "\n".join(lines)


def accessibility_markdown(root: Path = REPO_ROOT) -> str:
    """Population reached in-vehicle from the Dammam metro station per Jubail option
    (`uv run python -m access.isochrones --metro dammam --scenario S1 --candidate <yaml>
    --minutes 30,45,60,90,120 --mode in_vehicle --out runs/r5/jubail-iso/`)."""
    opts = {
        "Al Jubayl": "S5-station_addition-al-jubayl",
        "Jubail Industrial City": "S5-station_addition-al-jubayl-royal-commission",
        "two stations": "S5-station_addition-jubail-two-stations",
    }
    lines = [
        "Accessibility gain (in the model): population within each in-vehicle band of the "
        "Dammam–Khobar–Dhahran main station, S1 plus the option (`runs/r5/jubail-iso/`):",
        "",
        "| option | 30 min | 45 min | 60 min | 90 min | 120 min |",
        "|---|---|---|---|---|---|",
    ]
    allr = root / "runs/access/isochrones-summary-s1/reached_all.parquet"
    if allr.exists():
        a = pd.read_parquet(allr)
        a = a[
            (a.scenario == "S1")
            & (a.metro == "Dammam–Khobar–Dhahran")
            & (a["mode"] == "in_vehicle")
        ].set_index("band_min")
        lines.append(
            "| S1 (baseline) | "
            + " | ".join(f"{a.population.get(b, float('nan')):,.0f}" for b in (30, 45, 60, 90, 120))
            + " |"
        )
    for name, cid in opts.items():
        f_ = root / "runs/r5/jubail-iso" / cid / "reached.parquet"
        if not f_.exists():
            lines.append(f"| {name} | not run | | | | |")
            continue
        r = pd.read_parquet(f_)
        r = r[r["mode"] == "in_vehicle"].set_index("band_min").population
        lines.append(
            f"| {name} | "
            + " | ".join(f"{r.get(b, float('nan')):,.0f}" for b in (30, 45, 60, 90, 120))
            + " |"
        )
    return "\n".join(lines)


BLOCKS = {
    "MATRIX": ("<!-- BEGIN GENERATED MATRIX -->", "<!-- END GENERATED MATRIX -->"),
    "PARAMS": ("<!-- BEGIN GENERATED PARAMETERS -->", "<!-- END GENERATED PARAMETERS -->"),
    "JUBAIL": ("<!-- BEGIN GENERATED JUBAIL -->", "<!-- END GENERATED JUBAIL -->"),
}


def replace_block(text: str, begin: str, end: str, body: str) -> str:
    if begin not in text or end not in text:
        raise ValueError(f"missing markers {begin}")
    a, rest = text.split(begin, 1)
    _, b = rest.split(end, 1)
    return a + begin + "\n" + body + "\n" + end + b


def write_all(summary: Path, doc: Path, root: Path = REPO_ROOT) -> None:
    write(summary, doc, root)
    df = pd.read_parquet(summary)
    t = doc.read_text(encoding="utf-8")
    t = replace_block(t, *BLOCKS["MATRIX"], matrix_markdown())
    t = replace_block(t, *BLOCKS["PARAMS"], params_markdown(root))
    t = replace_block(t, *BLOCKS["JUBAIL"], jubail_markdown(df))
    doc.write_text(t, encoding="utf-8")
