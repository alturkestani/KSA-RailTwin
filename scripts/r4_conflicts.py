# ruff: noqa: E501
"""Append the R4 conflict rows (C-r4-tga-*, C-r4-intl-*) to docs/sources/conflicts.md. GASTAT values
are computed from the GASTAT workbooks by script; TGA values are the relayed figures in the source rows.
  uv run python scripts/r4_conflicts.py
"""

from __future__ import annotations

import warnings
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
WB = ROOT / "data/ksa/calibration/gastat_rail_tables_2025/railway_tables_2025_en.xlsx"
MARK = "## R4 (1 Nov 2026, R4 builder): TGA vs GASTAT in the calibration tables, and the pilgrim tables"


def monthly() -> pd.DataFrame:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        d = pd.read_excel(WB, sheet_name="1-2", header=None).fillna("")
    rows = {}
    for r in d.values:
        c = [str(v).strip() for v in r if str(v).strip()]
        if len(c) == 15 and c[1] in ("Intercity", "Intracity"):
            rows[c[0]] = [float(x) for x in c[2:14]]
    return pd.DataFrame(rows, index=range(1, 13))


def q(s: pd.Series, k: int) -> int:
    return int(s.loc[3 * k - 2 : 3 * k].sum())


def main() -> None:
    m = monthly()
    hhr, east, north = m["Haramain High Speed Railway"], m["East Train"], m["North Train"]
    metro = m["Riyadh Metro"]
    total = int(m.sum().sum())
    f = lambda x: f"{x:,}"  # noqa: E731
    rows = [
        (
            "C-r4-tga-001",
            "intercity rail passengers by line, Q3 2025",
            f"GASTAT Table 1-2 (data: TGA), Jul-Sep summed: HHR {f(q(hhr, 3))}, East {f(q(east, 3))}, North {f(q(north, 3))}",
            "TGA Q3 2025 via Argaam: HHR 2.07 M, East 0.38 M, North 0.25 M (S-r3-cal-008, secondary)",
            "agree to the rounding of the relayed figures",
            "checked, no conflict; the model uses GASTAT (grade A primary table)",
        ),
        (
            "C-r4-tga-002",
            "intercity rail passengers by line, Q4 2025",
            f"GASTAT Table 1-2, Oct-Dec summed: HHR {f(q(hhr, 4))}, East {f(q(east, 4))}, North {f(q(north, 4))}",
            "TGA Q4 2025 via Argaam: HHR 2.30 M, East 0.37 M, North 0.23 M (S-r3-cal-009, secondary)",
            "agree to rounding",
            "checked, no conflict; GASTAT used",
        ),
        (
            "C-r4-tga-003",
            "intercity rail passengers, Q1 and Q2 2025",
            f"GASTAT Table 1-2: Q1 {f(q(hhr, 1) + q(east, 1) + q(north, 1))}, Q2 {f(q(hhr, 2) + q(east, 2) + q(north, 2))}",
            "TGA/Argaam Q1 3.4 M, Q2 2.7 M (as recorded in C-r3-002; unverified)",
            "about +0.77 M (TGA higher)",
            "open (C-r3-002 carried): no TGA Q1/Q2 2025 bulletin was read in R4; GASTAT used because it is the primary annual table and its Q3/Q4 match TGA exactly (C-r4-tga-001/002)",
        ),
        (
            "C-r4-tga-004",
            "all rail passengers incl. intracity, 2025",
            f"GASTAT Table 1-2 total: {f(total)}",
            "Argaam's sum of the TGA quarters: 157.9 M (S-r3-cal-009, secondary)",
            f"{(157.9e6 / total - 1) * 100:+.1f} %",
            "not used for calibration (context only, intracity outside the model); GASTAT recorded",
        ),
        (
            "C-r4-tga-005",
            "Riyadh Metro passengers, Q3 2025",
            f"GASTAT Table 1-2, Jul-Sep: {f(q(metro, 3))}",
            "TGA via Argaam: 25.2 M (S-r3-cal-008)",
            "agree to rounding",
            "checked, no conflict; intracity, not a model target",
        ),
        (
            "C-r4-tga-006",
            "intercity rail 2025 national total",
            "GASTAT 10,938,371 (S-r3-cal-001)",
            "TGA/Argaam 11.7 M (S-r3-cal-009)",
            "+7.0 %",
            "as C-r3-001 (the whole gap sits in Q1-Q2, C-r4-tga-003); GASTAT used (A-demand-038)",
        ),
        (
            "C-r4-tga-007",
            "intercity bus passengers, 2022",
            "GASTAT Land Transport Statistics 2022 edition via Argaam: 39.1 M (S-r3-cal-024, unverified)",
            "TGA/PTA route-month dataset as analysed by Alhawiti and Alghuson (2026): 4.39 M in 2022 (S-soc-021, peer-reviewed abstract)",
            "about 8.9 times",
            "open: different scopes (GASTAT likely counts Umrah and non-scheduled coaches); the model's bus target stays TGA Q2-Q4 2025 (A-demand-039), whose scheduled-service scope matches the bus nodes rule (A-r4-bus-002)",
        ),
        (
            "C-r4-tga-008",
            "intercity bus passengers, Q2 2025 by region",
            "no GASTAT comparator (no 2025 GASTAT bus table is open)",
            "TGA via Argaam: 958,000 national, Makkah 226,890, Riyadh 222,960, Eastern 144,970 ... (S-r3-cal-020)",
            "not comparable",
            "no conflict to resolve; the national figure enters the Q2-Q4 target (A-demand-039); the regional split is unused",
        ),
        (
            "C-r4-tga-009",
            "North Line passengers, Q3 2026",
            "no GASTAT 2026 table yet",
            "TGA via Asharq Al-Awsat: 258,600 (S-hail-004)",
            "not comparable",
            "outside the 2025 calibration year; recorded only",
        ),
        (
            "C-r4-tga-010",
            "SAR-operated networks, 2024 (SAR statement, not TGA)",
            "GASTAT intercity 2024: 11,590,197 (S-r3-cal-001)",
            "SAR via Argaam: 13.7 M across its networks (S-r3-cal-006)",
            "+18.2 %",
            "scope: SAR's networks probably include the Al Mashaaer metro (as in its 2023 statement, S-r3-cal-007); GASTAT used",
        ),
        (
            "C-r4-intl-001",
            "foreign Umrah performers, Q1 2024",
            "GASTAT Q1 2024 workbook, Table 9 (Jan-Mar): 5,893,474",
            "5,794,564 'PDF text' (prompts/R4.md and the pilgrims README); the Q1 2024 bulletin PDF in the folder prints 5,893,474 ('The total number of external Umrah performers was 5,893,474 in Q1 of 2024'), and 5,794,564 appears in none of the 44 files (pdftotext search, 1 Nov 2026)",
            "+1.7 % (table vs the brief's text figure)",
            "the table is used (prompts/R4.md); both logged; the text figure is not reproducible from the files in hand (unverified). Enters only the 2024 series, not the 2025 segment",
        ),
        (
            "C-r4-intl-002",
            "foreign Umrah performers, Q2 2025",
            "Umrah Statistics Q2 2025 EN.pdf and the Q2 workbook (Table 1.10): 1,405,116; upload stamp 9 Aug 2026 (URL t=1786339722854), workbook modified 6 Aug 2026",
            "Umrah Statistics for Q2 - 2025 - EN.pdf: 1,324,418; upload stamp 19 Nov 2025 (URL t=1763544957806); the pilgrims README calls this file the revised one",
            "-5.7 % (earlier vs later upload)",
            "the later release (1,405,116) is used as the revised one (prompts/R4.md 'use the revised release'), 2025 total 18,033,038; 1,324,418 (total 17,952,340) is the sensitivity. The README's labelling looks reversed: flagged for Tariq (CP5)",
        ),
        (
            "C-r4-intl-003",
            "airport split of foreign arrivals at KAIA vs PMIA",
            "Umrah 1440-1442 AH pooled shares of the two airports: KAIA 69.7 %, PMIA 30.3 % (computed, runs/intl/split-s1)",
            "Hajj 1443 / 2022 incoming pilgrim flights: KAIA 2,450 (65.6 %), PMIA 1,287 (34.4 %) (Hajj_Statistics_2022 Table 10)",
            "KAIA share 4.1 points higher in the Umrah split",
            "cross-check only (A-intl-002): flights are not passengers; the Umrah shares stay the assumed constant (A-intl-001) until a dated row arrives in intl_airport_split.yaml",
        ),
    ]
    out = [
        MARK,
        "",
        "| id | quantity | value A | value B | difference | resolution |",
        "|---|---|---|---|---|---|",
    ]
    out += ["| " + " | ".join(r) + " |" for r in rows]
    p = ROOT / "docs/sources/conflicts.md"
    s = p.read_text(encoding="utf-8")
    if MARK in s:
        s = s[: s.index(MARK)].rstrip() + "\n"
    s = s.rstrip() + "\n\n" + "\n".join(out) + "\n"
    s = s.replace(
        "docs/sources/conflicts.md v0.10 | 31 Oct 2026 | Author: ",
        "docs/sources/conflicts.md v0.11 | 1 Nov 2026 | Author: R4 (C-r4-tga-001…010, C-r4-intl-001…003); ",
        1,
    )
    p.write_text(s, encoding="utf-8")
    print("\n".join(out))


if __name__ == "__main__":
    main()
