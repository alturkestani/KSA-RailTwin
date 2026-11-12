# ruff: noqa
# Pilot builder script recovered by CP1_PREP (item 4, Q24), 31 Oct 2026.
# Origin: /tmp/asir-scripts/gen_doc.py (last modified 2026-10-30 21:28 +03, pilot run PILOT_REGION_ASIR).
# Role: wrote the region documents.
# Outputs named in the code: {REPO}/cities/ksa/regions/pilot-asir.parquet, {REPO}/docs/regions/pilot-asir.md.
# Archival copy: absolute paths rewritten to repository-relative ("./") or "~"; logic
# unchanged. It ran in the pilot worktree with network access (Nominatim/Overpass or
# citypopulation.de); re-running it is not part of the test suite.
# Label: pilot, proposed criteria pending CP1; screening input, not a forecast.

"""Generates docs/regions/pilot-asir.md from the Parquet register (keeps figures in sync)."""

import sys

import pandas as pd

REPO = "./"
df = pd.read_parquet(f"{REPO}/cities/ksa/regions/pilot-asir.parquet")


def fmt_pop(v):
    return "null" if pd.isna(v) else f"{int(v):,}"


def fmt_km(v):
    return "" if pd.isna(v) else f"{v:,.1f}"


rows_md = []
for _, r in df.iterrows():
    flags = []
    if r["threshold_50k"]:
        flags.append("50k")
    if r["tag_10k"]:
        flags.append("10k")
    elif r["tag_5k"]:
        flags.append("5k")
    roles = "; ".join(x["role"] for x in r["economic_roles"]) or "none sourced"
    rows_md.append(
        f"| {r['name_en']} | {r['name_ar']} | {r['governorate']} | {fmt_pop(r['population'])} | "
        f"{', '.join(flags) or '-'} | {fmt_km(r['dist_existing_km'])} | {fmt_km(r['dist_committed_km'])} | "
        f"{fmt_km(r['dist_metro_km'])} | {r['nearest_metro']} | {r['terrain_class']} | {roles} | "
        f"{'yes' if r['pilot_sample'] else ''} | {'yes' if r['screened'] else 'no'} |"
    )

gov_rows = [
    ("Abha", "أبها", 422243),
    ("Ahad Rafidah", "أحد رفيدة", 107894),
    ("Al-Amwah", "الأمواه", 10969),
    ("Al-Birk", "البرك", 22583),
    ("Al-Harjah", "الحرجة", 18503),
    ("Al-Majaridah", "المجاردة", 48302),
    ("An-Nimas", "النماص", 38409),
    ("Balqarn", "بالقرن", 60012),
    ("Bariq", "بارق", 44880),
    ("Bisha", "بيشة", 202096),
    ("Khamis Mushait", "خميس مشيط", 601305),
    ("Muhayil", "محايل", 230537),
    ("Rijal Alma", "رجال ألمع", 50825),
    ("Sarat Abidah", "سراة عبيدة", 57123),
    ("Tanumah", "تنومة", 17756),
    ("Tarib", "طريب", 22298),
    ("Tathlith", "تثليث", 36451),
    ("Zahran al-Janub", "ظهران الجنوب", 32099),
]
gov_total = sum(g[2] for g in gov_rows)
assert gov_total == 2024285, gov_total
gov_md = "\n".join(f"| {e} | {a} | {p:,} |" for e, a, p in gov_rows)

sample = df[df["pilot_sample"]]
sample_md = "\n".join(
    f"- **{r['name_en']}** ({fmt_pop(r['population'])}): {r['pilot_reason']}"
    for _, r in sample.iterrows()
)
min_comm = df["dist_committed_km"].min()
min_exist = df["dist_existing_km"].min()

doc = f"""> **Document version:** docs/regions/pilot-asir.md v1.0 | 30 Oct 2026 | Author: region-scout (pilot, PILOT_REGION_ASIR) | Status: draft

# Asir (عسير) pilot region sweep, coarse

Screening input, not a forecast. Synthetic demand, uncalibrated: scenario comparison, not a forecast.
Pilot scope: a coarse sweep to test the schema (PROJECT.md W2 full register is R2, `REGION_ASIR`). Research only; no downloads; no grids or PBF extracts beyond the local OSM symlink already in the manifest.

## Header

- `governorates_gastat`: **18** (secondary: citypopulation.de's census-2022 governorate table, which credits GASTAT; **S-asir-001**). The GASTAT primary table was not reached: `portal.saudicensus.sa` returned a DNS failure on 30 Oct 2026 (S-072, S-090).
- `governorates_listed`: **18** (rows in `cities/ksa/regions/pilot-asir.parquet`, one centre row each).
- **Discrepancy flagged, not resolved:** the English Wikipedia infobox and the Arabic Wikipedia table give 17 governorate rows for Asir, and Saudipedia gives 18 plus Abha (`docs/gastat-regions.md`, S-074 to S-076). The 18 used here include Abha as its own governorate row, as the census table does. Primary GASTAT confirmation is still needed before R2.
- Register: `cities/ksa/regions/pilot-asir.parquet` (18 rows, 36 columns) and `pilot-asir.csv` (same rows and ids). Both validate against `common.schemas.RegionRow`, which was extended additively for the pilot (see Schema changes below). `screening.region_sweep` does not exist in this worktree, so the validation is `common.schemas.load_region_register`.

## Coverage

Every governorate has one row (its centre). The table below holds the census governorate totals (S-asir-001). These are perimeter populations, not settlement sizes, so they are not used as the populations in the register.

| governorate (EN) | governorate (AR) | population 2022 (governorate) |
|---|---|---|
{gov_md}
| **Total (Asir region, census 2022)** | | **{gov_total:,}** (matches the region total on S-asir-001) |

Centre populations are the census place-table values (places of at least 2,500 inhabitants, S-asir-001). Where a centre is not in that table, its population is `null` and it is not guessed.

## Register rows (generated from the Parquet)

| name (EN) | name (AR) | governorate | population (centre, 2022) | tags | dist. existing (km) | dist. committed (km) | dist. metro (km) | nearest metro (tier) | terrain | economic roles | pilot sample | screened |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
{chr(10).join(rows_md)}

Distances are straight-line (haversine) from OSM coordinates; road minutes are empty (`road_min_method: pending R1a skims`, A-screen-pilot-001). Abha and Khamis Mushait show 0.0 km to metro because they are the metro nodes themselves.

## Towns of 50,000 or more (threshold_50k)

Five centre rows reach 50,000 in the census place table: Abha (334,290), Ahad Rafidah (79,202), Bisha (115,537), Khamis Mushait (535,065) and Muhayil (97,967). The place table lists no non-centre settlement in Asir at 50,000 or more.

Two governorate totals are at or above 50,000 while their centre is not in the place table, or is below 50,000: Balqarn (60,012), Rijal Alma (50,825) and Sarat Abidah (57,123, centre 19,855). These are listed under "Needs Opus judgement".

## Pilot sample of towns between 5,000 and 50,000

Five rows carry `pilot_sample: true`, each with a reason in the register:
{sample_md}

Stratification result, stated plainly:
- **Near rail (under 25 km of an existing or committed station):** no Asir centre qualifies. The nearest is {min_comm:,.0f} km to a committed station and {min_exist:,.0f} km to an existing one. The near stratum is empty and is not filled with a town from another region.
- **Far rail (over 100 km):** every row qualifies (all centres are over 280 km from any station used here).
- **With a sourced economic role:** no sampled town in the 5,000–50,000 band has a sourced role. The sourced roles (airport, military, mining exploration, heritage) sit with Abha, Khamis Mushait, Bisha and Rijal Alma, which are either outside the band or have no sourced population.

## Exclusions

- **Balqarn** (centre): `screened = false`. OSM has no node named بالقرن. The coordinates are provisional on the village جوف بلقرن, and the centre is not assigned. Reason recorded in the register.
- No other row is excluded.

## Needs Opus judgement

1. **Balqarn centre.** Which settlement is the governorate seat? The candidates are جوف بلقرن, شعف بلقرن and نخال بلقرن (OSM villages). The row is excluded until this is decided.
2. **Al-Harjah centre.** Three OSM nodes are named الحرجة (19.58N 41.98E village; 17.92N 43.37E town; 21.86N 40.18E hamlet). The row uses the first, unconfirmed.
3. **Governorate totals at or above 50k with no matching centre** (Balqarn, Rijal Alma, Sarat Abidah): does the 50k tag apply to the governorate perimeter or only to settlements? The register tags settlements only.
4. **Tarib centre name.** The row is named "Fir'ah Tarib" from OSM فرعة طريب matched to the census place فرعه طريب. It is not confirmed as the governorate seat.
5. **Al-Amwah.** The Arabic name is from the aggregator. The centre population is `null`. Its OSM node is named "Al Amoah".
6. **Bariq, Rijal Alma.** Centre populations are `null` (not in the census place table). Rijal Alma is in a governorate of 50,825.
7. **Terrain for non-Abha centres** is `mixed` by assumption (A-screen-pilot-002); no DEM was used. Abha is classed `escarpment_mountain` from the Sarawat escarpment description (S-asir-007), not from elevation data.
8. **Mining role at Bisha** is exploration only (Muhaddad site, S-asir-009). No production data was found, so the role is recorded as exploration and not as an operating mine.

## Rail layers (kept apart)

- **Existing:** Haramain / HHR station nodes (Makkah, Madinah, KAEC, Jeddah airport, Riyadh; S-asir-004, S-asir-005). Jeddah Al-Sulaymaniyah has no coordinate in the sources used and is omitted (A-screen-pilot-005). No existing line serves Asir.
- **Committed / under procurement:** Saudi Landbridge (Riyadh–Jeddah leg), intermediate stations Al Jumum, Al Muwayh and Ad Dawadimi (S-asir-006). Layer `committed`, never existing. The intermediate station names conflict across sources (Jumoum/Jamuma; Muwai/Moya; Dawadmi/Al-Doadmi). The coordinates come from OSM places matched by name (A-screen-pilot-003). A 2026 report says contracts are not yet signed.
- **Not used:** the GCC railway and the Riyadh Rail Link, which do not serve Asir. Their station lists were not loaded for the pilot.

## Metro set

Tiers from A-screen-013 (primary Riyadh, Jeddah, Makkah, Madinah, Dammam–Khobar; secondary Taif, Buraidah, Tabuk, Abha–Khamis Mushait; tertiary Jazan, Najran). The nearest metro is chosen across all tiers. Metro coordinates are OSM city-node proxies (A-screen-pilot-004).

## Schema changes (additive; `common/schemas.py`)

- `pop_type` accepts `secondary` (aggregator figures, flagged).
- New optional fields: `threshold_50k` (population >= 50,000, validated), `pilot_sample` and `pilot_reason` (reason required when set), `distance_method`, `primary_to_find`.
- `TAG_50K` constant (pilot only, not a CP1 threshold).
- Existing rows and fixtures are unaffected (all new fields default to off or null).

## Licences and attribution

- Map data: © OpenStreetMap contributors, ODbL 1.0. Place and station coordinates come from the local GCC extract (`osm-gcc-2026-10-14`, already in `cities/ksa/sources.yaml`).
- Population figures: citypopulation.de (T. Brinkhoff), crediting GASTAT; terms not checked, used for facts with citation only, not copied (see `docs/data-sources.md`).

## Sources

See `docs/sources/pilot-asir.csv` (S-asir-001 to S-asir-010) and the existing S-072, S-074 to S-076 and S-090 in `docs/sources/index.csv`.
"""

open(f"{REPO}/docs/regions/pilot-asir.md", "w", encoding="utf-8").write(doc)
print("ok", len(doc))
sys.exit(0)
