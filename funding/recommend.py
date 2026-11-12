# ruff: noqa: E501  (long judgement and legal strings, wrapped by hand)
"""Recommendation per corridor family and CP7 programme (W6, R7): writes
`cities/ksa/funding/recommendations.yaml` from the analyst's judgement below and the evidence in
`runs/r7/fiscal/fiscal.json` and `runs/r7/vfm/vfm.json` (numbers are never typed by hand).

Rule 9: options side by side, the recommendation argued from the evidence and marked as the
analyst's judgement; no advocacy for any entity. Legal items cite the instrument or are "unclear"
with the question (docs/funding.md, Saudi-frame table).

    uv run python -m funding.recommend build
    uv run python -m funding.recommend check
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import typer
import yaml

from common import REPO_ROOT
from common.labels import LABEL
from funding import models as fmodels
from funding.sources import known_source_ids, unknown_ids

OUT = REPO_ROOT / "cities" / "ksa" / "funding" / "recommendations.yaml"
FISCAL = REPO_ROOT / "runs" / "r7" / "fiscal" / "fiscal.json"
VFM = REPO_ROOT / "runs" / "r7" / "vfm" / "vfm.json"

# --------------------------------------------------------------------------- legal preconditions
LEGAL: dict[str, dict[str, Any]] = {
    "sar_mandate": {
        "status": "clear",
        "text": "SAR took over the Saudi Railways Organization's responsibilities from 1 Apr 2021; "
        "2016 and 2019 decisions give it ownership of intercity rail infrastructure and of "
        "operational railway projects (SAR's own history page).",
        "sources": ["S-fund-033"],
    },
    "sar_ownership_form": {
        "status": "unclear",
        "question": "Who are SAR's shareholders per its commercial registration or articles, and "
        "what is its legal form?",
        "sources": ["S-fund-034", "S-fund-035"],
    },
    "fiscal_reporting": {
        "status": "unclear",
        "question": "Are SAR's capex and debt consolidated in general-government statistics or the "
        "budget, and would PPP payment commitments or guarantees be disclosed? (fully public via "
        "budget, PIF or SAR differ in reporting, not in the risk the state carries)",
        "sources": ["S-fund-029", "S-fund-026"],
    },
    "pif_role": {
        "status": "unclear",
        "question": "Does PIF currently finance SAR's capex (equity, loans or guarantees), and what "
        "do Arts. 3-4 of the official PIF Law text say on domestic infrastructure and guarantees?",
        "sources": ["S-lb-012", "S-lb-009", "S-fund-036", "S-fund-037"],
    },
    "railway_law_concession": {
        "status": "clear",
        "text": "Railway Law M/159: concession contracts are tendered upon TGA approval in "
        "accordance with relevant laws (Art. 32); TGA may allow a concessionaire to use railway "
        "land and protection zones (Art. 33); TGA sets the policy for usage fees, the fees charged "
        "under use agreements for access to the network (Arts. 1 and 18).",
        "sources": ["S-fund-013", "S-fund-014", "S-fund-016"],
    },
    "fare_setting_authority": {
        "status": "unclear",
        "question": "Who sets and approves passenger fares on intercity and commuter rail (the "
        "state rail company, TGA, a ministry or a concession contract)? Railway Law Art. 18 covers "
        "usage (access) fees under use agreements, not passenger fares; no source read settles it.",
        "sources": ["S-fund-016", "S-fund-012"],
    },
    "railway_law_regulation": {
        "status": "unclear",
        "question": "Which cases of the Railway Law Implementing Regulation allow transfer of "
        "existing assets to a concessionaire, and has TGA published a usage-fee policy?",
        "sources": ["S-fund-054", "S-fund-055"],
    },
    "psp_law_steps": {
        "status": "clear",
        "text": "PSP Law M/63: a PPP is a contract of 5 years or more with two or more of design, "
        "build, manage, operate, maintain or finance (Art. 1); MoF refers projects to NCP for a "
        "preliminary viability study within 60 business days (Art. 7); MoF ensures funds and "
        "allocations and approves support (Art. 8; extra support by Council of Ministers "
        "resolution, Art. 10); term up to 30 years unless the relevant agency approves longer "
        "(Art. 20); termination with compensation that may include lost revenues (Art. 28); "
        "arbitration with the relevant agency's approval (Art. 34).",
        "sources": [
            "S-fund-001",
            "S-fund-003",
            "S-fund-004",
            "S-fund-005",
            "S-fund-002",
            "S-fund-007",
            "S-fund-008",
        ],
    },
    "psp_regulations_thresholds": {
        "status": "unclear",
        "question": "What do the amended (2023/2024) Implementing Regulations say on the SAR 200 m "
        "PPP threshold (reported by secondary sources), procurement methods, the VfM study and MoF "
        "fiscal approval?",
        "sources": ["S-fund-041", "S-fund-053", "S-fund-042"],
    },
    "psp_relevant_agency": {
        "status": "unclear",
        "question": "For an intercity or commuter rail PPP, which body is the relevant and the "
        "executive agency (Art. 2 governing rules), and is SAR a contracting authority under "
        "Art. 4?",
        "sources": ["S-fund-010"],
    },
    "psp_railway_interaction": {
        "status": "unclear",
        "question": "Does a rail concession tendered under Railway Law Art. 32 also follow PSP Law "
        "procedures (NCP study, MoF approval)?",
        "sources": ["S-fund-013", "S-fund-003"],
    },
    "ncp_vfm_method": {
        "status": "unclear",
        "question": "Has NCP published a VfM or PSC method (the R7 test follows the Green Book "
        "logic as a named reference)?",
        "sources": ["S-fund-030", "S-fund-056", "S-fund-024"],
    },
    "om_contract_status": {
        "status": "unclear",
        "question": "Is a 5-year-plus O&M-only rail contract (as on Haramain) a PPP under PSP Law "
        "Art. 1, with NCP and MoF steps, or ordinary government procurement?",
        "sources": ["S-fund-001", "S-fund-039"],
    },
    "host_line_procurement": {
        "status": "unclear",
        "question": "Can a station on a committed host line (GCC Railway in design; the Landbridge "
        "in phased delivery after the PPP talks ended) be added within the host line's procurement, "
        "and under what procurement model are the Landbridge phases being let?",
        "sources": ["S-029", "S-059", "S-lb-001", "S-060"],
    },
    "lvc_instruments": {
        "status": "unclear",
        "question": "Which Saudi instruments (development rights on railway land under Railway Law "
        "Art. 33, municipal fees, the white-land fee) could legally be earmarked for rail?",
        "sources": ["S-fund-014"],
    },
    "land_expropriation": {
        "status": "unclear",
        "question": "What expropriation procedure and timetable apply to a new rail alignment "
        "(not reviewed in R1d or R7)?",
        "sources": ["S-fund-014", "S-fund-006"],
    },
}
LEGAL_BY_MODEL = {
    "fully_public_sar": [
        "sar_mandate",
        "fare_setting_authority",
        "sar_ownership_form",
        "fiscal_reporting",
        "pif_role",
        "land_expropriation",
    ],
    "public_with_private_om": [
        "fare_setting_authority",
        "sar_mandate",
        "om_contract_status",
        "psp_law_steps",
    ],
    "ppp_dbfom_availability": [
        "psp_law_steps",
        "fare_setting_authority",
        "psp_regulations_thresholds",
        "psp_relevant_agency",
        "psp_railway_interaction",
        "ncp_vfm_method",
    ],
    "ppp_dbfom_demand_risk": [
        "psp_law_steps",
        "fare_setting_authority",
        "railway_law_concession",
        "railway_law_regulation",
        "psp_railway_interaction",
    ],
    "lvc_station_area_development": ["lvc_instruments", "railway_law_concession"],
    "hybrid_public_dbfm_plus_station_lvc": ["psp_law_steps", "lvc_instruments"],
}

# --------------------------------------------------------------------------- judgement
PRECEDENTS = {
    "fully_public_sar": "Haramain: public design-build packages plus an EPC + O&M contract; the state "
    "carried cost and demand; about six years late; 2023 ridership about an eighth of the design "
    "projection (secondary) (S-fund-261, S-fund-265). Spain ADIF/AVE: public build through an "
    "off-budget entity; ex-post returns nil to minimal where demand is thin (S-fund-237, S-fund-239).",
    "public_with_private_om": "Haramain O&M by Renfe for SAR, extended to 2038 (secondary, "
    "S-fund-039); HSL-Zuid shows the State can end up with operating damage costs (S-fund-044).",
    "ppp_dbfom_availability": "Sydney Metro Northwest: availability PPP, the State kept demand "
    "(S-fund-045); LGV SEA's equity cushion was about 20% of its private financing (S-fund-227).",
    "ppp_dbfom_demand_risk": "LGV SEA: demand risk largely on the concessionaire, 48% grantor "
    "contribution, 73% of senior debt state-guaranteed, traffic below forecast (S-fund-223, "
    "S-fund-227, S-fund-229); China: lines below about 40 M passengers a year do not service "
    "their debt (S-fund-250).",
    "lvc_station_area_development": "Hong Kong Rail-plus-Property: development rights instead of "
    "cash; the government judged property 'may barely bridge' the gap on two lines (S-fund-048, "
    "S-fund-218).",
    "hybrid_public_dbfm_plus_station_lvc": "LGV Bretagne-Pays de la Loire DBFM (S-fund-043) with "
    "Rail-plus-Property-type development rights (S-fund-048).",
}

JUDGEMENT: dict[str, dict[str, Any]] = {
    "station_addition": {
        "recommended": "fully_public_sar",
        "delivery_note": "capital works let together with, or as a variation of, the host line's "
        "works by the host line's owner; O&M through the host line's operating arrangement. Who "
        "finances (budget, PIF or the state rail company) changes reporting, not risk (unclear "
        "items fiscal_reporting, pif_role).",
        "reasoning": [
            "Small, interface-bound works: each station is an addition to a line someone else "
            "builds or runs; a standalone station SPV would carry the interface with the host line.",
            "The availability PPP costs the state more in expected PV in every registered "
            "parameter range (VfM below); the sign changes only at a bid far below the "
            "un-uplifted base estimate (switching value of A-fund-007).",
            "Fares do not finance the station: the standalone fare increment is small or "
            "negative (the stop lengthens through journeys), so a revenue-based model has "
            "nothing to carry.",
        ],
        "conditions": "Dhahran and Al Jubayl (2030) carry a P10 BCR above 1 in every population "
        "case; Duruma (2050) does not (stage-gate it at its construction start). Al Jubayl's and "
        "Duruma's host lines are committed, not existing: the delivery route depends on the host "
        "line's procurement (unclear item host_line_procurement).",
    },
    "branch_spur": {
        "recommended": "fully_public_sar",
        "delivery_note": "public capital delivery with an explicit stage gate before construction "
        "starts (2047 for the 2050 phase, A-r6-002), a P90 budget line and contracts that share "
        "the cost tail (target cost with pain/gain); O&M in-house or by a contracted operator "
        "(public_with_private_om has the same fiscal exposure in the model).",
        "reasoning": [
            "The spur's value is real in the model (robust NPV positive at P50 cost) but its cost "
            "tail is wide: at P90 capex the state's exposure rises under every model, because the "
            "overrun at P90 is many times any plausible private equity cushion (A-fund-102): risk "
            "transfer above the cushion is nominal and returns to the state as a contingent "
            "liability.",
            "The availability PPP has a negative VfM across every registered range; the "
            "financing premium (S-fund-r7-001) costs about what the transferred overrun is worth.",
            "A demand-risk PPP is not a fit: the P10 BCR is below 1 in every population case and "
            "fares cover well under half of opex and renewals (skill rule). In the model it needs a "
            "construction grant larger than the contract capex (the grant pre-pays the operating "
            "deficit), so its fiscal cost is close to public delivery while the 'transferred' demand "
            "risk sits on a revenue stream the minimum revenue guarantee then backstops.",
        ],
        "conditions": "Carry the P90 cost risk explicitly (CP7-1): the L1 programme turns negative "
        "at P90 cost in the low and medium population cases. A non-electrified spur narrows that "
        "loss but lowers the robust NPV (docs/r6-topology.md §0.2); keep it as a design option at "
        "the stage gate.",
    },
    "commuter_belt": {
        "recommended": "fully_public_sar",
        "delivery_note": "only if the reach objective is chosen (S6-L3): public capital delivery, "
        "a stage gate before 2047, O&M in-house or contracted.",
        "reasoning": [
            "No model makes the belt self-financing: fares are a few per cent of opex and "
            "renewals in the model, and its standalone robust NPV is negative.",
            "Private finance adds cost (negative VfM across every registered range) and a "
            "demand-risk concession has no revenue to carry (P10 BCR far below 1).",
            "It is a reach option, bought at a fiscal cost; the decision is about reach, not "
            "about delivery.",
        ],
        "conditions": "In the model the belt is an island (it touches neither S1 nor another "
        "layout corridor, R6 flag) and turns Duruma negative next to it (docs/r6-topology.md §0).",
    },
}

PROGRAMME_NOTE = {
    "S6-L2": "cost-robust layout (CP7-1): the three station additions, each delivered with its "
    "host line.",
    "S6-L1": "highest robust NPV (CP7-1): L2 plus the Al-Kharj spur; the spur's P90 cost risk is "
    "carried in every figure below.",
    "S6-L3": "reach alternative (CP7-1): Al Jubayl and Dhahran stations, the Al-Kharj spur and the "
    "Riyadh commuter belt 225.",
}


def _r(d: dict[str, float]) -> dict[str, float]:
    return {k: round(float(d[k]), 3) for k in ("p10", "p50", "p90", "expected") if k in d}


def model_evidence(ent: dict[str, Any], vfm: dict[str, Any], rp: str) -> dict[str, Any]:
    out = {}
    for m, ex in ent["models"].items():
        r = ex["by_pop"][rp]
        cl = r["contingent_liabilities"]
        out[m] = {
            "kind": ex["kind"],
            "net_fiscal_cost_pv": {f"{h}y": _r(r[f"net_fiscal_cost_{h}y"]) for h in (30, 40, 60)},
            "upfront_public_capex_undiscounted": _r(
                {q: r["upfront_public_capex"][q]["sum"] for q in ("p10", "p50", "p90")}
            ),
            "budget_share_peak_pct_p90_capex": round(
                r["budget_share"]["p90"]["central"]["peak_pct"], 3
            ),
            "budget_share_peak_year": r["budget_share"]["p90"]["central"]["peak_year"],
            "contingent_liabilities_pv": {k: round(float(v), 1) for k, v in cl.items()},
            "legal_preconditions": LEGAL_BY_MODEL[m],
            "precedent": PRECEDENTS[m],
        }
        if "lvc_break_even_pv" in ex:
            out[m]["lvc_break_even_pv"] = round(ex["lvc_break_even_pv"], 1)
    out["_vfm_availability_vs_public"] = {
        "vfm_expected_pv": round(vfm["central"]["vfm"], 1),
        "vfm_pct_of_psc": round(vfm["central"]["vfm_pct_psc"], 1),
        "sign": vfm["sign_central"],
        "sign_robust_to_registered_ranges": vfm["sign_robust_to_registered_ranges"],
        "switching_values": {
            k: (None if d["switching_value"] is None else round(d["switching_value"], 4))
            for k, d in vfm["drivers"].items()
        },
        "rate_sensitivity": {k: round(v, 1) for k, v in vfm["rate_sensitivity"].items()},
    }
    return out


def basis_evidence(b: dict[str, Any], rp: str) -> dict[str, Any]:
    return {
        "score": b["score"],
        "judge_sha256": b["judge_sha256"],
        "robust_npv": round(b["robust_npv"], 1),
        "capex": {k: round(v, 1) for k, v in b["capex"].items()},
        "bcr_p10_60y": {k: round(v, 2) for k, v in b["bcr_p10_60y"].items()},
        "npv_at_p90_cost_60y": {k: round(v, 1) for k, v in b["npv_at_p90_cost_60y"].items()},
        "fare_over_opex_60y": round(b["fare_over_opex_60y"][rp], 3),
        "fiscal_series_method": b["fiscal_series_method"],
        "judge_fiscal_cost_p50_60y": round(b["judge_fiscal_cost_p50_60y"][rp], 1),
        "phases": {p["corridor"]: p["phase"] for p in b["parts"]},
    }


def build(root: Path = REPO_ROOT) -> dict[str, Any]:
    fis = json.loads((root / "runs/r7/fiscal/fiscal.json").read_text())
    vfm = json.loads((root / "runs/r7/vfm/vfm.json").read_text())
    rp = fis["robust_case"]
    fam_of = {"S3": "branch_spur", "S4": "commuter_belt", "S5": "station_addition"}
    corridors = {}
    for cid, ent in fis["corridors"].items():
        fam = fam_of[cid.split("-")[0]]
        j = JUDGEMENT[fam]
        corridors[cid] = {
            "family": fam,
            "recommended_model": j["recommended"],
            "judgement": "analyst's judgement (rule 9): best fit given the evidence below; not "
            "advocacy for any entity",
            "delivery_note": j["delivery_note"],
            "reasoning": j["reasoning"],
            "conditions": j["conditions"],
            "alternatives_considered": [m for m in ent["models"] if m != j["recommended"]],
            "risk_matrices": [
                f"cities/ksa/funding/risk_matrix_{cid}--{m}.yaml" for m in ent["models"]
            ],
            "basis": basis_evidence(ent["basis"], rp),
            "options": model_evidence(ent, vfm["corridors"][cid], rp),
        }
    programmes = {}
    for sid, ent in fis["programmes"].items():
        parts = ent["basis"]["parts"]
        programmes[sid] = {
            "note": PROGRAMME_NOTE[sid],
            "recommended_package": {
                p["corridor"]: corridors[p["corridor"]]["recommended_model"] for p in parts
            },
            "judgement": "analyst's judgement: the corridor recommendations combined; the "
            "programme figures are the layout's own judge score (corridors interact)",
            "alternatives_considered": [m for m in ent["models"] if m != "fully_public_sar"],
            "risk_matrices": [
                f"cities/ksa/funding/risk_matrix_{sid}--{m}.yaml" for m in ent["models"]
            ],
            "basis": basis_evidence(ent["basis"], rp),
            "options": model_evidence(ent, vfm["programmes"][sid], rp),
            "budget_envelope": "B1 = SAR 100 bn capex (A-r6-003, CP7-2): capex P90 "
            f"{ent['basis']['capex']['p90']:,.0f} SAR m",
        }
    return {
        "version": "1.0",
        "label": LABEL,
        "units": "SAR million, 2025 prices; PV at 2026, Green Book 2026 schedule",
        "population_case": f"{rp} (robust case: the worst of the three, R6 convention); "
        "medium and high in runs/r7/fiscal/fiscal.json",
        "judge": "v3-variants, SHA-256 d9fef64384e2e25f84b288962907fa25e2476d9749bf863d7bd6fb66fb70f9ee"
        " (docs/r6/judge-hashes.md)",
        "international_pilgrim_segment": "carries no user benefits (CP6 P8a, CP7-4); it is not "
        "added to any fiscal or revenue figure",
        "legal_items": LEGAL,
        "corridors": corridors,
        "programmes": programmes,
    }


def check(d: dict[str, Any], root: Path = REPO_ROOT) -> list[str]:
    errs = []
    ids = {o.id for o in fmodels.load_models().options}
    cited: list[str] = []
    for v in LEGAL.values():
        cited += v["sources"]
        if v["status"] == "unclear" and not v.get("question"):
            errs.append("an unclear legal item needs its question")
    for grp in ("corridors", "programmes"):
        for k, v in d[grp].items():
            ms = [m for m in v["options"] if not m.startswith("_")]
            for m in ms:
                if m not in ids:
                    errs.append(f"{k}: unknown model {m}")
                for f in v["risk_matrices"]:
                    if not (root / f).exists():
                        errs.append(f"{k}: missing {f}")
            if len(ms) < 2:
                errs.append(f"{k}: needs alternatives")
    missing = unknown_ids(cited, known_source_ids())
    if missing:
        errs.append(f"unknown S-ids: {missing}")
    return errs


app = typer.Typer(add_completion=False, help=__doc__, no_args_is_help=True)


@app.callback()
def _group() -> None:
    """Recommendations (R7)."""


@app.command("build")
def build_cmd(out: Path = typer.Option(OUT, "--out")) -> None:
    d = build()
    errs = check(d)
    if errs:
        raise typer.BadParameter("; ".join(errs))
    head = (
        "# > **Document version:** cities/ksa/funding/recommendations.yaml v1.2 | 4 Nov 2026 | "
        "Author: FIX_R7 (basis fields and availability legal list checked, item 2); R7 builder "
        "(funding.recommend build; generated) | Status: draft\n"
        f"# Label: {LABEL}\n"
    )
    Path(out).write_text(head + yaml.safe_dump(d, sort_keys=False, allow_unicode=True, width=100))
    typer.echo(f"wrote {out}: {len(d['corridors'])} corridors, {len(d['programmes'])} programmes")


@app.command("check")
def check_cmd(path: Path = typer.Option(OUT, "--path")) -> None:
    errs = check(yaml.safe_load(Path(path).read_text()))
    if errs:
        typer.echo("FAIL: " + "; ".join(errs))
        raise typer.Exit(1)
    typer.echo(f"OK {path}")


if __name__ == "__main__":
    app()
