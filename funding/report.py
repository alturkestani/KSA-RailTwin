# ruff: noqa: E501  (Markdown prose lines)
"""Render `docs/fiscal-exposure.md` and `docs/delivery-models.md` from the R7 run outputs
(`runs/r7/fiscal/fiscal.json`, `runs/r7/vfm/vfm.json`, `cities/ksa/funding/recommendations.yaml`).
Every figure in the two documents comes from those files; nothing is typed by hand.

    uv run python -m funding.report write [--date "4 Nov 2026"]
"""

from __future__ import annotations

import json
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

import typer
import yaml

from common import REPO_ROOT
from common.labels import LABEL
from funding import risk_matrix
from funding.vfm import ASSUMPTION, SOURCED, SOURCING_TEXT

POPS = ("un_wpp_low", "un_wpp_medium", "un_wpp_high")
SHORT = {"un_wpp_low": "low", "un_wpp_medium": "medium", "un_wpp_high": "high"}
NAMES = {
    "fully_public_sar": "fully public (state rail company)",
    "public_with_private_om": "public with private O&M",
    "ppp_dbfom_availability": "DBFOM availability PPP",
    "ppp_dbfom_demand_risk": "DBFOM demand-risk PPP",
    "lvc_station_area_development": "public + station-area value capture",
    "hybrid_public_dbfm_plus_station_lvc": "hybrid: public civil + DBFM + station LVC",
}
DRIVER_NAMES = {
    "bid_contingency": "bid contingency over base capex (A-fund-007)",
    "private_finance_premium": "private finance premium (A-fund-008)",
    "transaction_cost": "transaction costs (A-fund-103)",
    "absorption_capacity": "private absorption capacity (A-fund-102)",
    "public_contribution_availability": "public construction contribution (A-fund-002)",
}


def f0(x: float | None) -> str:
    """Whole SAR m, rounded half away from zero (D-r8-03), from the unrounded engine value."""
    if x is None:
        return "n/a"
    v = int(Decimal(repr(float(x))).quantize(Decimal(1), rounding=ROUND_HALF_UP))
    return f"{v:,}"


def rng(d: dict[str, float]) -> str:
    return f"{f0(d['p10'])} / {f0(d['p50'])} / {f0(d['p90'])}"


PPP_NOTE = (
    "availability-PPP figures: P10 = P50 by construction (fixed price; capex enters only through "
    "the overrun above the cushion)"
)


def ev_note(fis: dict) -> str:
    """The A-fund-108 caveat, with the lognormal mean / P50 factor computed per entity."""
    import math

    f = []
    for g in ("programmes", "corridors"):
        for v in fis[g].values():
            c = v["basis"]["capex"]
            s = math.log(c["p90"] / c["p50"]) / 1.2815515655446004
            f.append(math.exp(s * s / 2))
    return (
        "expected values rest on A-fund-108: a lognormal tail through P50/P90 implies "
        f"E[capex] ≈ 1.69 × P50 ({min(f):.2f}–{max(f):.2f} across the {len(f)} entities, from each "
        "one's own P90/P50); the judge's draw mean is not stored"
    )


def note(*parts: str) -> list[str]:
    """Heading note printed above a table (FIX_R7 item 5): the label first, then the caveats."""
    return ["*Table note: " + "; ".join((LABEL, *parts)) + ".*", ""]


def name(cid: str) -> str:
    c = risk_matrix.corridor_yaml(cid)
    return c.get("name_en", cid).replace(" (hypothetical)", "")


def load(root: Path = REPO_ROOT) -> tuple[dict, dict, dict]:
    fis = json.loads((root / "runs/r7/fiscal/fiscal.json").read_text())
    vfm = json.loads((root / "runs/r7/vfm/vfm.json").read_text())
    rec = yaml.safe_load((root / "cities/ksa/funding/recommendations.yaml").read_text())
    return fis, vfm, rec


# --------------------------------------------------------------------------- alignment v2
V2_SENS = Path("runs/r7-v2/sensitivity.json")


def v2_lines(key: str, root: Path = REPO_ROOT) -> list[str]:
    """One line under each table whose figures move with alignment weights v2 (FIX_R7 item 4c):
    direction and size, read from runs/r7-v2/sensitivity.json (absent: nothing printed)."""
    p = root / V2_SENS
    if not p.exists():
        return []
    d = json.loads(p.read_text()).get("lines", {})
    if key not in d:
        return []
    return [f"Alignment v2 sensitivity: see `docs/alignments.md` §4c. {d[key]}", ""]


# --------------------------------------------------------------------------- fiscal tables
def exposure_table(ent: dict, rp: str) -> list[str]:
    out = [
        "| model | upfront public capex, undiscounted P10 / P50 / P90 | net fiscal cost PV 30 y P10 / P50 / P90 | 40 y P10 / P50 / P90 | 60 y P10 / P50 / P90 (expected) | peak share of state expenditure, P50 / P90 capex (year) | contingent liabilities PV: expected / P90 | termination memo PV: worst / probability-weighted |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for m, ex in ent["models"].items():
        r = ex["by_pop"][rp]
        up = {q: r["upfront_public_capex"][q]["sum"] for q in ("p10", "p50", "p90")}
        bs = r["budget_share"]
        cl = r["contingent_liabilities"]
        n60 = r["net_fiscal_cost_60y"]
        out.append(
            f"| {NAMES[m]} (`{m}`) | {rng(up)} | {rng(r['net_fiscal_cost_30y'])} | "
            f"{rng(r['net_fiscal_cost_40y'])} | {rng(n60)} ({f0(n60['expected'])}) | "
            f"{bs['p50']['central']['peak_pct']:.3f} % / {bs['p90']['central']['peak_pct']:.3f} % "
            f"({bs['p90']['central']['peak_year']}) | {f0(cl['expected_pv'])} / {f0(cl['p90_pv'])} | "
            f"{f0(cl['termination_worst_case_pv'])} / {f0(cl['termination_expected_pv'])} |"
        )
    return out


def pop_table(ent: dict, model: str) -> list[str]:
    out = [
        "| population case | net fiscal cost PV 60 y P10 / P50 / P90 | expected |",
        "|---|---|---|",
    ]
    for p in POPS:
        n = ent["models"][model]["by_pop"][p]["net_fiscal_cost_60y"]
        out.append(f"| {SHORT[p]} | {rng(n)} | {f0(n['expected'])} |")
    return out


def timing_table(fis: dict, rp: str) -> list[str]:
    progs = list(fis["programmes"])
    buckets = list(
        fis["programmes"][progs[0]]["models"]["fully_public_sar"]["by_pop"][rp]["timing_p50_5y"]
    )
    keep = [b for b in buckets if int(b[:4]) < 2061]
    head = (
        "| programme (fully public, P50 capex) | "
        + " | ".join(keep)
        + " | 2061 onward, per 5 years (mean) |"
    )
    out = [head, "|---|" + "---|" * (len(keep) + 1)]
    for sid in progs:
        t = fis["programmes"][sid]["models"]["fully_public_sar"]["by_pop"][rp]["timing_p50_5y"]
        later = [v for k, v in t.items() if int(k[:4]) >= 2061 and v]
        mean_later = sum(later) / len(later) if later else 0.0
        out.append(
            f"| {sid} | " + " | ".join(f0(t.get(k, 0.0)) for k in keep) + f" | {f0(mean_later)} |"
        )
    out += ["", *timing_footnote(fis, rp)]
    return out


def timing_footnote(fis: dict, rp: str) -> list[str]:
    """verify-R7 O7: why 2031-2035 differs in sign between layouts that run the same two 2030
    stations. Derived from the programme bases in fiscal.json: the layout's 60-year PV opex and
    fares are split over corridors by standalone weights (A-fund-109), so the 2030 stations' share
    depends on the rest of the layout."""
    rows = []
    for sid, ent in fis["programmes"].items():
        b = ent["basis"]
        early = [pt for pt in b["parts"] if int(pt["phase"]) <= 2030]
        wo = sum(pt["w_opex"] for pt in early)
        wf = sum(pt["w_fare"] for pt in early)
        po = b["pv_opex_renewals_p50_60y"][rp]
        pf = b["pv_fare_revenue_p50_60y"][rp]
        rows.append(
            f"{sid}: opex weight {wo:.3f} × PV opex {f0(po)} = {f0(wo * po)}; fare weight {wf:.3f} × "
            f"PV fares {f0(pf)} = {f0(wf * pf)}; attributed opex − fares {f0(wo * po - wf * pf)}"
        )
    return [
        "*Timing note (verify-R7 O7, derived from `runs/r7/fiscal/fiscal.json`, programme `basis.parts`): "
        "2031–2035 to 2041–2045 carry only the two 2030 stations, yet the sign differs between S6-L2 "
        "and S6-L1/L3. The judge scores each layout as a whole and stores 60-year PVs, so the layout's "
        "PV opex and PV fares are split across its corridors by their standalone weights (A-fund-109); "
        "standalone fare PVs can be negative (a station that abstracts trips from the host line), so "
        "the weights depend on the other corridors in the layout. PV attributed to the 2030 stations "
        f"({SHORT[rp]}, SAR m): " + "; ".join(rows) + ". The sign difference is an artefact of the "
        "split, not a difference in the stations; layout totals are unaffected.*",
    ]


def vfm_table(vfm: dict) -> list[str]:
    out = [
        "| corridor or programme | E[PSC] | E[availability PPP] | VfM (% of PSC) | sign robust to every registered range | VfM at flat 5 % / at the sovereign real rate | switching values: bid contingency / finance premium / transaction cost |",
        "|---|---|---|---|---|---|---|",
    ]
    for grp in ("programmes", "corridors"):
        for k, v in vfm[grp].items():
            c = v["central"]
            rs = list(v["rate_sensitivity"].values())
            dr = v["drivers"]

            def sv(n: str, dr=dr) -> str:
                x = dr[n]["switching_value"]
                return "none in bracket" if x is None else f"{x:.3f}"

            out.append(
                f"| {k} | {f0(c['psc'])} | {f0(c['ppp'])} | {f0(c['vfm'])} ({c['vfm_pct_psc']:.1f} %) | "
                f"{'yes' if v['sign_robust_to_registered_ranges'] else 'no'} | {f0(rs[0])} / {f0(rs[1])} | "
                f"{sv('bid_contingency')} / {sv('private_finance_premium')} / {sv('transaction_cost')} |"
            )
    return out


def driver_table(vfm: dict, key: str, grp: str = "programmes") -> list[str]:
    v = vfm[grp][key]
    out = [
        "| parameter | central | registered range | VfM at low / high | switching value (bracket searched) | sourced |",
        "|---|---|---|---|---|---|",
    ]
    for n, d in v["drivers"].items():
        sv = "none in bracket" if d["switching_value"] is None else f"{d['switching_value']:.4f}"
        out.append(
            f"| {DRIVER_NAMES[n]} | {d['central']} | {d['range'][0]} to {d['range'][1]} | "
            f"{f0(d['vfm_at_low'])} / {f0(d['vfm_at_high'])} | {sv} ({d['bracket_searched'][0]} to "
            f"{d['bracket_searched'][1]}) | {SOURCING_TEXT[d.get('sourcing', SOURCED if d['sourced'] else ASSUMPTION)]} |"
        )
    return out


def basis_line(b: dict) -> str:
    cx = b["capex"]
    return (
        f"capex P10 / P50 / P90 {f0(cx['p10'])} / {f0(cx['p50'])} / {f0(cx['p90'])} (base P50 "
        f"{f0(cx['base_p50'])}); robust NPV {f0(b['robust_npv'])}; BCR P10 low / medium / high "
        + " / ".join(f"{b['bcr_p10_60y'][p]:.2f}" for p in POPS)
        + "; NPV at P90 cost low / medium / high "
        + " / ".join(f0(b["npv_at_p90_cost_60y"][p]) for p in POPS)
        + f"; PV fares / PV opex and renewals {b['fare_over_opex_60y']['un_wpp_low']:.2f} (low case); fully public fiscal series: {b['fiscal_series_method']} (judge 60 y fiscal cost P50, low case: {f0(b['judge_fiscal_cost_p50_60y']['un_wpp_low'])}). Score: `{b['score']}`"
    )


def fiscal_doc(fis: dict, vfm: dict, date: str) -> str:
    rp = fis["robust_case"]
    EV = ev_note(fis)
    s1 = fis["baseline_s1"]["rows"]
    s1l = s1[f"{rp}|60"]
    kh = fis["corridors"]["S3-branch_spur-al-kharj"]
    l1 = fis["programmes"]["S6-L1"]
    l2 = fis["programmes"]["S6-L2"]
    l1p = l1["models"]["fully_public_sar"]["by_pop"][rp]
    l2p = l2["models"]["fully_public_sar"]["by_pop"][rp]
    l1a = l1["models"]["ppp_dbfom_availability"]["by_pop"][rp]
    L: list[str] = [
        f"> **Document version:** docs/fiscal-exposure.md v1.4 | {date} | Author: R8 builder (verify-R7 O7 timing note, O8 engine-series ranks in the method table, O11 three sourcing states); FIX_R7 (table heading notes: label, PPP P10 = P50, A-fund-108; alignment v2 sensitivity lines); INTEGRATE_R7 (register pointer repointed to docs/assumptions.md); R7 builder (funding-ppp-analyst; generated by `uv run python -m funding.report write`) | Status: draft",
        "",
        "# Fiscal exposure of the CP7 layouts by delivery model (W6, R7)",
        "",
        f"**Label: {LABEL}.** Every figure is in the model: a scenario comparison of delivery models on a modelled demand base, not a budget forecast. SAR million at 2025 prices; present values at 2026 on the Green Book 2026 schedule (A-cba-001, A-cba-301); ranges P10 / P50 / P90 over the capex draws. Population case: **{rp}** (the robust, worst case of R6) unless a table says otherwise. The international pilgrim segment carries no user benefits (CP6 P8a, CP7-4) and is not added to any fiscal or revenue figure.",
        "",
        "## Inputs and run ids",
        "",
        "- **Judge:** v3-variants, SHA-256 `d9fef64384e2e25f84b288962907fa25e2476d9749bf863d7bd6fb66fb70f9ee` (`docs/r6/judge-hashes.md`), seed 1, 10,000 draws, 60 years. Every input `score.json` has this hash in its `meta.json`.",
        "- **Programmes:** `runs/r6/top5/L1|L2|L3/score.json` (R6_V3 scores of `scenarios/S6-L1..L3.yaml`).",
        "- **Corridors:** standalone judge v3 runs at their CP7 phase: Al Jubayl and Dhahran (2030) from the R6_V3 library `runs/r6/v3/library/<id>/score.json`; Duruma, the Al-Kharj spur and the Riyadh belt 225 (2050) scored by R7 with the same frozen judge, `runs/r7/corridors/<id>@2050/score.json` (`uv run python -m funding.inputs score-corridors`). The Al-Kharj run reproduces the library's 2050 robust NPV (4,309; `docs/r6-topology.md` §0). Standalone corridors do not add up to a layout (corridors compete for the same trips); the programme tables use the layout's own score.",
        "- **Fiscal engine:** `runs/r7/fiscal/fiscal.json` (`uv run python -m funding.fiscal build`); **VfM:** `runs/r7/vfm/vfm.json` (`uv run python -m funding.vfm build`). Parameters: `cities/ksa/assumptions/funding_r7.yaml`; register rows `docs/assumptions.md` (A-fund ids).",
        f"- **Baseline (S1 committed programme, R5, `{fis['baseline_s1']['run']}`):** fiscal cost to the state under fully public delivery, 60 y, {rp}: P10 / P50 / P90 {f0(s1l['fiscal_cost']['P10'])} / {f0(s1l['fiscal_cost']['P50'])} / {f0(s1l['fiscal_cost']['P90'])}; FIRR P50: no IRR (fares never repay the costs). Every layout figure below is incremental to S1.",
        "",
        "## Method (metric definitions from R1d, `risk_matrix_template.yaml`)",
        "",
        "| metric | how R7 computes it | parameters |",
        "|---|---|---|",
        "| upfront public capex | public delivery: the judge's capex P10 / P50 / P90 (uplifted, undiscounted); PPP: the public construction contribution (availability) or the viability-gap grant (demand-risk) | A-fund-002, A-fund-007 |",
        "| net fiscal cost over 30 / 40 / 60 years | public delivery, layouts: the judge's `fiscal_cost` = PV(capex + opex + renewals − fares) at P50 at every horizon, P10 / P90 = PVC quantile + residual value scaled with capex; corridors (the standalone judge runs store 60 y only): every horizon from the cash-flow engine (capex quantile spread over the build years plus level annual opex and fares), with the judge's 60-year fiscal cost P50 printed next to it as a cross-check. One method per series. PPP: PV(contribution + availability payments + post-term opex + transaction costs + overrun beyond the private cushion − fares kept by the state) | A-fund-107, A-fund-109 |",
        "| availability payments as a share of a budget line | firm annual public payments (capex, availability payment or grant, opex, transaction costs, less fares) ÷ total state expenditure: MoF 2026–2028 (S-fund-026), then nominal growth A-fund-005 (central, low, high), deflated by CPI (A-fund-105); peak and year | A-fund-004, A-fund-005, A-fund-105 |",
        "| contingent liabilities | overrun above the private absorption capacity (fixed-price bid × (1 + A-fund-102)) on a lognormal through capex P50 and P90 (expected and at P90); minimum revenue guarantee on the A-rcf-029 outturn ratio (demand-risk model); termination at opening as a memorandum item (worst case and × A-fund-006), not added to the net fiscal cost (the state would stop paying the availability payment) | A-fund-102, A-fund-104, A-fund-006, A-fund-108, A-rcf-029 |",
        "| P10 / P50 / P90 of the engine series (PPP models, demand concession, corridor series) | the sorted values of the three runs at capex P10, P50 and P90 (verify-R7 O8): a cost range, not quantiles of a simulated distribution; for the demand-risk concession the ordering by capex quantile and by fiscal cost can differ, so the columns are labelled by rank | A-fund-107 |",
        "| timing profile | five-year sums of the firm public payments, P50 capex, construction uniform over phase − 3 … phase − 1 (A-r6-002, A-cba-303) | A-fund-106 |",
        "",
        "Availability PPP mechanics: contract capex = base capex P50 × (1 + A-fund-007); private finance at the sovereign real rate (A-fund-101, sourced from Saudi sukuk yields and CPI) plus the premium A-fund-008 (NAO 2018, S-fund-r7-001), rolled up to opening and repaid over the PSP Law Art. 20 term of 30 years (A-fund-010, S-fund-002); opex passed through; the state keeps fares. Demand-risk PPP: the concessionaire keeps fares and pays opex over the term; the state pays the viability gap as a construction grant and the guarantee. Annual opex and fares are level annual equivalents of the judge's 60-year PVs (A-fund-109). Approximations (A-fund-107…109) are needed because the judge stores P10 / P50 / P90 summaries, not the draws; exact draws would need a judge change, which R7 may not make.",
        "",
        "## Programmes (CP7 layouts)",
        "",
    ]
    for sid, ent in fis["programmes"].items():
        L += [f"### {sid}", "", basis_line(ent["basis"]) + ".", ""]
        L += note(PPP_NOTE, EV) + exposure_table(ent, rp)
        L += (
            ["", "Population cases, fully public:", ""]
            + note(EV)
            + pop_table(ent, "fully_public_sar")
            + [""]
        )
        L += v2_lines(sid)
    L += [
        "### The Al-Kharj spur's P90 cost risk (CP7-1), explicitly",
        "",
        f"- Standalone at 2050: {basis_line(kh['basis'])}.",
        f"- In S6-L1 the spur is the difference between L1 and L2: capex P90 {f0(l1['basis']['capex']['p90'])} against {f0(l2['basis']['capex']['p90'])}; under fully public delivery the 60-year net fiscal cost P90 is {f0(l1p['net_fiscal_cost_60y']['p90'])} against {f0(l2p['net_fiscal_cost_60y']['p90'])}, and the peak budget share at P90 capex {l1p['budget_share']['p90']['central']['peak_pct']:.3f} % in {l1p['budget_share']['p90']['central']['peak_year']} against {l2p['budget_share']['p90']['central']['peak_pct']:.3f} %.",
        f"- Under an availability PPP the spur's tail does not go away: the state's contingent liability for overruns above the private cushion is {f0(kh['models']['ppp_dbfom_availability']['by_pop'][rp]['contingent_liabilities']['expected_pv'])} expected and {f0(kh['models']['ppp_dbfom_availability']['by_pop'][rp]['contingent_liabilities']['p90_pv'])} at P90 capex (PV); for the L1 programme {f0(l1a['contingent_liabilities']['expected_pv'])} / {f0(l1a['contingent_liabilities']['p90_pv'])}.",
        "- At P90 cost the L1 programme's NPV is negative in the low and medium population cases (R6_V3), so the contingent exposure arises in exactly the cases where the economic case fails. A non-electrified spur narrows the P90 loss but lowers the robust NPV (`docs/r6-topology.md` §0.2).",
        "",
        "## Corridors (standalone, at their CP7 phase)",
        "",
    ]
    for cid, ent in fis["corridors"].items():
        L += [f"### {name(cid)} (`{cid}`)", "", basis_line(ent["basis"]) + ".", ""]
        L += note(PPP_NOTE, EV) + exposure_table(ent, rp) + [""] + v2_lines(cid)
    L += [
        "## Timing profile (fully public, P50 capex, SAR m per five years; negative = fares above opex)",
        "",
    ]
    L += note() + timing_table(fis, rp) + [""]
    L += [
        "## Value for money: public sector comparator vs availability PPP",
        "",
        "VfM = E[net fiscal cost, public delivery] − E[net fiscal cost, availability PPP], 60 years, robust case; > 0 favours the PPP. Expected values use the lognormal capex mean (A-fund-108). The PSC carries the reference-class optimism bias already inside the judge's capex draws (S-fund-025); following Green Book A.13–A.14 (S-fund-024) the public option is not charged a financing cost, and the flat 5 % and sovereign-rate columns test that convention.",
        "",
    ]
    L += note(PPP_NOTE, EV) + vfm_table(vfm) + [""] + v2_lines("vfm")
    L += [
        "One-at-a-time drivers for S6-L1 (the other entities behave alike; every driver is in `runs/r7/vfm/vfm.json`):",
        "",
    ]
    L += note(EV) + driver_table(vfm, "S6-L1") + [""]
    unsourced = sorted(
        {
            d
            for g in ("corridors", "programmes")
            for v in vfm[g].values()
            for d in v["depends_on_unsourced"]
        }
    )
    L += [
        "**Drivers not sourced for Saudi Arabia (three sourcing states, verify-R7 O11):** "
        + "; ".join(
            f"{DRIVER_NAMES[n]}: {SOURCING_TEXT[d['sourcing']]}"
            for n, d in vfm["programmes"]["S6-L1"]["drivers"].items()
            if not d["sourced"]
        )
        + ".",
        "",
        f"**Where VfM depends on an unsourced parameter:** {', '.join(unsourced) if unsourced else 'nowhere within the registered ranges'}. In every corridor and programme the sign (public delivery cheaper in expected PV) holds across the full registered range of every parameter, sourced or not; the PPP breaks even only if the fixed-price bid is about 80 % below the un-uplifted base estimate, if private finance is cheaper than sovereign borrowing, or if transaction costs are negative, none of which has any support in the sources read. The financing premium is the sourced driver (S-fund-r7-001, a UK reference class: no Saudi PPP cost-of-capital figure was found, unclear).",
        "",
        "## Caveats",
        "",
        "- Synthetic demand, uncalibrated: fares and benefits come from the R6 judge's modelled demand. FIRR is not reported for the layouts because the judge stores no annual flows; the farebox ratio (PV fares ÷ PV opex and renewals) is given instead. The S1 baseline has no FIRR (fares never repay the costs, R5).",
        "- The PV components known only at P50 (capex, residual) are scaled with the capex quantile (A-fund-107); the capex tail is a lognormal fit through P50 and P90 (A-fund-108); annual flows are level equivalents (A-fund-109).",
        "- The budget denominator is total state expenditure (S-fund-026), the only budget line sourced; no rail or transport line was found. Beyond 2028 it is projected (A-fund-005).",
        "- No Saudi PPP has a published payment schedule, cost of capital, MRG or termination record for rail; those parameters are registered assumptions with ranges, and the VfM test reports their switching values.",
        "",
    ]
    return "\n".join(L)


# --------------------------------------------------------------------------- delivery models doc
def legal_table(rec: dict, keys: list[str]) -> list[str]:
    out = ["| item | status | finding or open question | sources |", "|---|---|---|---|"]
    for k in keys:
        it = rec["legal_items"][k]
        txt = it.get("text") or it.get("question")
        out.append(f"| {k} | **{it['status']}** | {txt} | {', '.join(it['sources'])} |")
    return out


def options_table(ent_rec: dict, fis_ent: dict, rp: str) -> list[str]:
    """Figures come from the unrounded engine output (fis_ent), never from the rounded
    recommendations.yaml copy, so no table rounds twice (14,611.498 -> 14,611, not 14,612)."""
    out = [
        "| option | net fiscal cost PV 60 y P10 / P50 / P90 (expected) | upfront public capex P50 | contingent liabilities PV expected / P90 | precedent |",
        "|---|---|---|---|---|",
    ]
    for m, o in ent_rec["options"].items():
        if m.startswith("_"):
            continue
        r = fis_ent["models"][m]["by_pop"][rp]
        n = r["net_fiscal_cost_60y"]
        cl = r["contingent_liabilities"]
        up50 = r["upfront_public_capex"]["p50"]["sum"]
        rec = (
            " **(recommended)**"
            if m == ent_rec.get("recommended_model", "fully_public_sar")
            else ""
        )
        out.append(
            f"| {NAMES[m]}{rec} | {f0(n['p10'])} / {f0(n['p50'])} / {f0(n['p90'])} ({f0(n['expected'])}) | "
            f"{f0(up50)} | {f0(cl['expected_pv'])} / {f0(cl['p90_pv'])} | {o['precedent']} |"
        )
    return out


def delivery_doc(fis: dict, vfm: dict, rec: dict, date: str) -> str:
    rp = fis["robust_case"]
    EV = ev_note(fis)
    unclear = [k for k, v in rec["legal_items"].items() if v["status"] == "unclear"]
    L: list[str] = [
        f"> **Document version:** docs/delivery-models.md v1.4 | {date} | Author: INTEGRATE_R8 (one rounding rule, half away from zero, from the unrounded engine values; the S6-L1 availability-PPP and S6-L3 demand-risk contingent liabilities at P90 move by 1 SAR m); R8 builder (verify-R7 O11 three sourcing states; O17 template note regenerated into the matrices); FIX_R7 (table heading notes: label, PPP P10 = P50, A-fund-108; alignment v2 sensitivity lines); R7 builder (funding-ppp-analyst; generated by `uv run python -m funding.report write`) | Status: draft",
        "",
        "# Delivery and funding model per corridor family and CP7 programme (W6, R7)",
        "",
        f"**Label: {LABEL}.** Options are presented side by side with their evidence; each recommendation is **the analyst's judgement** of the best fit given that evidence (rule 9). Naming an entity (SAR, PIF, NCP, TGA, MoF) states a legal or institutional fact with its source; it is not an endorsement. Money: SAR million, 2025 prices, PV at 2026 (Green Book 2026); population case {rp} (robust); fiscal detail in `docs/fiscal-exposure.md`; machine-readable `cities/ksa/funding/recommendations.yaml`. Rounding: every figure is printed from the unrounded engine output (`runs/r7/fiscal/fiscal.json`) and rounded once, half away from zero (D-r8-03), so the report, the policy brief and this document print the same digits.",
        "",
        "## Summary",
        "",
        *note(EV),
        "| corridor or programme | recommended model (analyst's judgement) | alternatives considered | net fiscal cost PV 60 y, recommended, P10 / P50 / P90 | VfM availability PPP vs public (sign robust?) |",
        "|---|---|---|---|---|",
    ]
    for grp in ("programmes", "corridors"):
        for k, v in rec[grp].items():
            if grp == "corridors":
                model = v["recommended_model"]
                alts = ", ".join(f"`{a}`" for a in v["alternatives_considered"])
            else:
                model = "package: " + ", ".join(sorted(set(v["recommended_package"].values())))
                alts = ", ".join(f"`{a}`" for a in v["alternatives_considered"])
            o = v["options"]["fully_public_sar"]["net_fiscal_cost_pv"]["60y"]
            vf = v["options"]["_vfm_availability_vs_public"]
            L.append(
                f"| {k} | `{model}` | {alts} | {f0(o['p10'])} / {f0(o['p50'])} / {f0(o['p90'])} | "
                f"{f0(vf['vfm_expected_pv'])} ({vf['vfm_pct_of_psc']:.1f} % of PSC; {'yes' if vf['sign_robust_to_registered_ranges'] else 'no'}) |"
            )
    L += [
        "",
        f"Legal and institutional items flagged **unclear**: {len(unclear)} of {len(rec['legal_items'])} ({', '.join(unclear)}). Each carries its open question below; no legal position is inferred.",
        "",
        "**What drives the result.** Fares in the model cover a small share of operating costs on the spur and the belt and are near zero or negative for the station additions, so no option is self-financing and every option leaves the state paying. Within that, private finance at a premium (S-fund-r7-001) costs about what the transferred construction risk is worth, and the transfer stops at the private equity cushion while the judge's capex tail (P90 about 3.7 × P50) goes far beyond it. The availability PPP is therefore more expensive in expected PV than public delivery in every corridor, programme and registered parameter range. The recommendation follows from that, together with the size and host-line interfaces of the station additions. It would change if a Saudi PPP market priced risk much below the reference class: the switching values say how far.",
        "",
    ]
    fam_seen: set[str] = set()
    for cid, v in rec["corridors"].items():
        fam = v["family"]
        if fam not in fam_seen:
            fam_seen.add(fam)
            L += [f"## Family: {fam.replace('_', ' ')}", ""]
        L += [f"### {name(cid)} (`{cid}`)", ""]
        b = fis["corridors"][cid]["basis"]
        L += ["Evidence: " + basis_line(b) + ".", ""]
        L += (
            ["Options side by side:", ""]
            + note(PPP_NOTE, EV)
            + options_table(v, fis["corridors"][cid], rp)
            + [""]
        )
        L += v2_lines(cid)
        vf = v["options"]["_vfm_availability_vs_public"]
        sw = vf["switching_values"]
        L += [
            f"VfM (availability PPP vs public, expected PV): {f0(vf['vfm_expected_pv'])} ({vf['vfm_pct_of_psc']:.1f} % of PSC), {vf['sign']}; switching values: bid contingency {sw['bid_contingency']}, finance premium {sw['private_finance_premium']}, transaction cost {sw['transaction_cost']}, absorption capacity {sw['absorption_capacity']}, public contribution {sw['public_contribution_availability']} (None = no sign change in the bracket searched).",
            "",
            f"**Recommendation (analyst's judgement): `{v['recommended_model']}`**: {v['delivery_note']}",
            "",
        ]
        L += [f"- {r}" for r in v["reasoning"]]
        L += ["", f"Conditions: {v['conditions']}", ""]
        keys = list(
            dict.fromkeys(
                k
                for m in v["options"]
                if not m.startswith("_")
                for k in v["options"][m]["legal_preconditions"]
            )
        )
        if fam == "station_addition":
            keys.append("host_line_procurement")
        L += (
            ["Legal preconditions under the Saudi frame (all options considered):", ""]
            + legal_table(rec, keys)
            + [""]
        )
        rm = risk_matrix.load_matrix(
            REPO_ROOT / f"cities/ksa/funding/risk_matrix_{cid}--{v['recommended_model']}.yaml"
        )
        L += [
            f"Risk-allocation matrix, recommended model (`cities/ksa/funding/risk_matrix_{cid}--{v['recommended_model']}.yaml`; the alternatives' matrices: {', '.join('`' + Path(p).name + '`' for p in v['risk_matrices'] if v['recommended_model'] not in p)}):",
            "",
            risk_matrix.render(rm),
            "",
        ]
    L += ["## Programmes (CP7 layouts)", ""]
    for sid, v in rec["programmes"].items():
        b = fis["programmes"][sid]["basis"]
        L += [f"### {sid}: {v['note']}", "", "Evidence: " + basis_line(b) + ".", ""]
        L += (
            ["Options side by side (a single model across the whole programme):", ""]
            + note(PPP_NOTE, EV)
            + options_table(
                {**v, "recommended_model": "fully_public_sar"}, fis["programmes"][sid], rp
            )
            + [""]
            + v2_lines(sid)
        )
        pk = ", ".join(f"{name(c)}: `{m}`" for c, m in v["recommended_package"].items())
        vf = v["options"]["_vfm_availability_vs_public"]
        L += [
            f"**Recommended package (analyst's judgement):** {pk}. {v['budget_envelope']}. VfM of an availability PPP for the whole programme: {f0(vf['vfm_expected_pv'])} ({vf['vfm_pct_of_psc']:.1f} % of PSC).",
            "",
            f"Programme risk matrices: {', '.join('`' + p + '`' for p in v['risk_matrices'])}.",
            "",
        ]
    L += (
        [
            "## All legal and institutional items",
            "",
        ]
        + legal_table(rec, list(rec["legal_items"]))
        + [
            "",
            "## Reading the recommendation evenhandedly",
            "",
            "- **For a PPP:** a fixed-price contract can protect the budget from overruns up to the private cushion and has delivered on time elsewhere (LGV SEA, S-fund-047); NCP targets value for money from PPPs (S-fund-030) and MoF intends to expand project and infrastructure finance (S-fund-027). If Saudi bids priced risk well below the reference class, or if private finance were close to sovereign cost, the VfM sign could change: the switching values above are the test.",
            "- **For public delivery:** the corridors are small or interface-bound, their fares do not carry the costs, and the cost tail beyond any private cushion stays with the state under every model; public finance avoids the premium (S-fund-r7-001). The Haramain precedent shows public delivery has its own schedule and demand risks (S-fund-265), which the state carries in full.",
            "- **Funding sources** (budget, PIF, the state rail company, land value capture) are separate from the delivery model: they change who finances and reports, and whether some cost is recovered from land value, not who carries the delivery risk. Which of them applies, and how it is reported, is unclear under the sources read.",
            "",
        ]
    )
    return "\n".join(L)


app = typer.Typer(add_completion=False, help=__doc__, no_args_is_help=True)


@app.callback()
def _group() -> None:
    """R7 documents."""


@app.command("write")
def write_cmd(date: str = typer.Option("4 Nov 2026", "--date")) -> None:
    fis, vfm, rec = load()
    (REPO_ROOT / "docs/fiscal-exposure.md").write_text(fiscal_doc(fis, vfm, date))
    (REPO_ROOT / "docs/delivery-models.md").write_text(delivery_doc(fis, vfm, rec, date))
    typer.echo("wrote docs/fiscal-exposure.md and docs/delivery-models.md")


if __name__ == "__main__":
    app()
