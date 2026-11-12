# ruff: noqa: E501  (GASTAT file names are long literals)
"""Register the 21 GASTAT tables in data/ksa/tables/gastat/ in the manifest (CP2_PREP item 1 addendum).

Reads the folder's sources.csv and sources_tableau_2022.csv (url, retrieved_at_utc, licence, sha256 per file) and calls
`common.manifest add` once per file not yet in cities/ksa/sources.yaml. Idempotent.

    uv run python scripts/register_gastat_tables.py
"""

from __future__ import annotations

import csv
import re
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / "data" / "ksa" / "tables" / "gastat"
MANIFEST = ROOT / "cities" / "ksa" / "sources.yaml"
# sources.csv: the 19 files of the addendum; sources_tableau_2022.csv: the two primary TA1 Excel
# exports of addendum 2 (Tariq, 31 Oct 2026 15:25)
SOURCE_LISTS = ["sources.csv", "sources_tableau_2022.csv"]

SHORT = {
    "Population_Estimates_Statistics_2024_EN.xlsx": "est2024-stats-en-xlsx",
    "Population_Estimates_Publication_2024.xlsx": "est2024-pub-ar-xlsx",
    "Population_Estimates_Publication_2024_EN.pdf": "est2024-pub-en-pdf",
    "Population_Estimates_Publication_2024_AR.pdf": "est2024-pub-ar-pdf",
    "twzy_lskn_fy_lmhfzt.xlsx": "census2010-gov-xlsx",
    "census31-prim-04.pdf": "census2010-gov-pdf",
    "twzy_lskn_fy_lmnzq_ldry_(1).xlsx": "census2010-region-xlsx",
    "lntyj_lwly_ltdd_2010_nhyy_mntq_wmhfzt.xlsx": "census2010-cities5k-ar-xlsx",
    "lntyj_lwly_ltdd_2010_nhyy_mntq_wmhfzt_w_lmdn_lty_dd_sknh_yzyd_n_5000_nsm_1_0_0.xlsx": (
        "census2010-cities5k-en-xlsx"
    ),
    "census31-prim-05.pdf": "census2010-cities5k-pdf",
    "lntyj_ltfsylyh_llmmlk.xlsx": "census2010-detailed-xlsx",
    "1_VGA_templatized_20230607_1600_Census_2022_Documentation_compressed.pdf": "census2022-methodology-pdf",
    "TA9-Population2010-2022byRegionNationalityandGender_Population2010-2022byRegionNationalityandGender.csv": (
        "census2022-ta9-csv"
    ),
    "TA2-PopulationinbroadAgeGroupsbyRegionCityNationalityandGenderAR_NW-PopulationinbroadAgeGroupsbyRegionCityNationalityandGenderAR.csv": (
        "census2022-ta2-csv"
    ),
    "TA1-PopulationbyNationalitybyRegionGovernorateCityandGenderAR_NW_PopulationbyNationalitybyRegionGovernorateCityandNationalityAR.pdf": (
        "census2022-ta1-pdf"
    ),
    "census2022_TA1_governorate_primary.xlsx": "census2022-ta1-governorate-xlsx",
    "census2022_TA1_city5k_primary.xlsx": "census2022-ta1-city5k-xlsx",
    "census-2022-20260929.csv": "census2022-relayed-datapulse-csv",
    "census-2022-dictionary.csv": "census2022-relayed-datapulse-dict",
    "population-region-20260928.csv": "popregion-relayed-datapulse-csv",
    "population-region-dictionary.csv": "popregion-relayed-datapulse-dict",
}


def main() -> int:
    have = {r["id"] for r in yaml.safe_load(MANIFEST.read_text())["sources"]}
    rows = [
        r
        for f in SOURCE_LISTS
        if (FOLDER / f).exists()
        for r in csv.DictReader((FOLDER / f).open(encoding="utf-8"))
    ]
    added = 0
    for r in rows:
        fid = "gastat-" + SHORT[r["file_name"]]
        if fid in have:
            continue
        relayed = r["primary_or_relayed"] == "relayed"
        publisher = (
            "DataPulse (relaying GASTAT; not official)"
            if relayed
            else "GASTAT (General Authority for Statistics)"
        )
        licence = "GASTAT data use policy (attribution required)" + (
            "; DataPulse processing" if relayed else ""
        )
        accessed = r["retrieved_at_utc"][:10]
        notes = (
            f"CP2_PREP item 1 addendum{' 2' if r['file_name'].startswith('census2022_TA1') else ''}; {'gastat_relayed' if relayed else 'gastat_primary'}; "
            f"retrieved {r['retrieved_at_utc']}; {re.sub(r'\s+', ' ', r['notes'])}"
        )
        cmd = [
            sys.executable,
            "-m",
            "common.manifest",
            "add",
            "--id",
            fid,
            "--name",
            r["title"],
            "--publisher",
            publisher,
            "--url",
            r["source_url"],
            "--edition",
            r["reference_year"],
            "--licence",
            licence,
            "--path",
            str((FOLDER / r["file_name"]).relative_to(ROOT)),
            "--used-in",
            "screening,network,demand",
            "--accessed",
            accessed,
            "--notes",
            notes,
        ]
        subprocess.run(cmd, check=True, cwd=ROOT)
        added += 1
    print(f"registered {added} new rows ({len(rows)} files in {' + '.join(SOURCE_LISTS)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
