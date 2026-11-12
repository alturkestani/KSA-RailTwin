# ruff: noqa
# Pilot builder script recovered by CP1_PREP (item 4, Q24), 31 Oct 2026.
# Origin: /tmp/alb/docs.py (last modified 2026-10-30 22:04 +03, pilot run PILOT_REGION_AL_BAHA).
# Role: wrote the region documents.
# Outputs named in the code: {R}/cities/ksa/regions/pilot-al_baha.parquet, {R}/docs/regions/pilot-al_baha.md.
# Archival copy: absolute paths rewritten to repository-relative ("./") or "~"; logic
# unchanged. It ran in the pilot worktree with network access (Nominatim/Overpass or
# citypopulation.de); re-running it is not part of the test suite.
# Label: pilot, proposed criteria pending CP1; screening input, not a forecast.

import math
import pandas as pd

R = "./"
p = pd.read_parquet(f"{R}/cities/ksa/regions/pilot-al_baha.parquet")


def f(v, nd=1):
    return (
        "–"
        if v is None or (isinstance(v, float) and math.isnan(v)) or v is pd.NA
        else (f"{v:,.{nd}f}" if isinstance(v, float) else str(v))
    )


def pop(r):
    if r.population is None or pd.isna(r.population):
        return "null (no place figure)"
    return f"{int(r.population):,} ({r.pop_source}, {r.pop_type}, {int(r.pop_year)})"


def tags(r):
    t = []
    if r.tag_10k:
        t.append("10k")
    if r.tag_5k:
        t.append("5k")
    if r.threshold_50k:
        t.append("50k")
    return ", ".join(t) or "–"


def roles(r):
    return ", ".join(f"{x['role']} ({x['source']})" for x in r.economic_roles) or "none sourced"


lines = [
    "| row | centre (EN / AR) | governorate (EN) | OSM id | lat, lon | population | tags | dist existing km (nearest) | dist metro km (nearest, tier) | economic roles | pilot sample | screened |",
    "|---|---|---|---|---|---|---|---|---|---|---|---|",
]
for r in p.itertuples():
    osm = "–" if pd.isna(r.osm_id) else str(int(r.osm_id))
    latlon = "NaN, NaN (not located)" if math.isnan(r.lat) else f"{r.lat:.5f}, {r.lon:.5f}"
    metro = (
        f"{f(r.dist_metro_km)} ({r.nearest_metro.split(' (')[0]}, tier {int(r.nearest_metro_tier)})"
        if not pd.isna(r.dist_metro_km)
        else "–"
    )
    ex = f"{f(r.dist_existing_km)} (Makkah Central)" if not pd.isna(r.dist_existing_km) else "–"
    sample = "yes" if r.pilot_sample else "no"
    scr = "yes" if r.screened else f"no: {r.exclusion_reason.split(':')[0]}"
    lines.append(
        f"| {r.row_id} | {r.name_en} / {r.name_ar} | {r.governorate} | {osm} | {latlon} | {pop(r)} | {tags(r)} | {ex} | {metro} | {roles(r)} | {sample} | {scr} |"
    )
TABLE = "\n".join(lines)

samp = p[p.pilot_sample]
srows = "\n".join(f"- **{r.name_en}** ({r.row_id}): {r.sample_reason}" for r in samp.itertuples())

notes = "\n".join(f"- **{r.row_id} {r.name_en}:** {r.notes}" for r in p.itertuples())

doc = f"""> **Document version:** docs/regions/pilot-al_baha.md v1.0 | 30 Oct 2026 | Author: region-scout (PILOT_REGION_AL_BAHA) | Status: draft

# Al-Baha (الباحة) pilot sweep, slug `al_baha`

**Screening input, not a forecast.** Label: synthetic demand, uncalibrated: scenario comparison, not a forecast. This is the coarse pilot sweep that tests the register schema; the full Al-Baha register is `REGION_AL_BAHA` in R2. Access date for every source: 30 Oct 2026 (Asia/Riyadh). Source ids are in `docs/sources/pilot-al_baha.csv` (`S-al_baha-nnn`) and in the Kingdom index (`S-070`, `S-072`, `S-090`).

## Governorate count

| source | count | status |
|---|---|---|
| citypopulation.de, Al-Bahah region table (credits GASTAT, census 2022-05-10): 9 governorates plus the Al-Bāḥah row | 10 rows | secondary (`S-al_baha-001`) |
| Wikipedia, Al-Bahah Province: 9 governorates listed, plus Al-Baha city as provincial capital | 9 (+ capital) | secondary (`S-al_baha-005`) |
| Saudipedia (search snippet, `docs/gastat-regions.md`): 9 governorates, plus the emirate | 9 (+ capital) | secondary (`S-073`/`S-076` family) |
| GASTAT official governorate list | **not reachable**: portal.saudicensus.sa did not resolve (`S-090`); governorate count unverified (`S-072`) | unverified |

`governorates_gastat: unknown` · `governorates_listed: 10` (rows; 9 governorates plus the Al-Bāḥah row, which is the regional capital). **Flagged, not resolved:** the listed count and the GASTAT count are both unverified. The register has one row per governorate centre, which is 10 rows: the 9 governorates and the Al-Bāḥah row. Read the GASTAT list before R2 (see Needs Opus judgement).

## Register rows (10)

Generated from `cities/ksa/regions/pilot-al_baha.parquet` (the CSV carries the same rows and ids). Populations are **secondary** (citypopulation.de, credits GASTAT); every value is a settlement (place) figure, not a governorate total. Distances are great-circle, method `A-screen-pilot-001`. Road minutes are empty (`pending R1a skims`).

{TABLE}

Committed lines (Landbridge, GCC, Riyadh Rail Link): `dist_committed_km` is empty for every row. No station coordinates for the committed lines are in the sources (for example Al-Jumum is unlocated, `S-062`/`S-063`), so the distance is not guessed. None of the three is labelled existing.

Existing rail: the only existing stations used are the Haramain HSR stations Makkah Central (OSM node 10956967098, 21.41766 N, 39.78853 E) and Jeddah Al-Sulaymaniyah (OSM way 485762503). Makkah Central is nearer in every row, so the table uses it. Al-Baha has no existing line in the sources. Distances are to the station, not the alignment; the alignment could be closer, so these are station-based values.

Metro (A-screen-013, approved tiers): the nearest metro for every row is Taif or Abha (secondary tier). Makkah (primary) is 232 km or more from every row, so it is never nearest here. Makkah distance is taken to the Haramain station as a proxy: no Makkah city coordinate is sourced.

Terrain: `escarpment_mountain` for all rows, from the Sarawat Mountains range (`S-al_baha-009`). This is a region-level class, not a DEM result. The DEM was not sampled (pilot, no downloads). The word "escarpment" is not on the Wikipedia page and the UNESCO tentative-list page returned 403, so the wording is unverified; see the assumption register.

## Pilot sample (6 rows, `pilot_sample: true`)

The brief asks for 4–6 towns between 5,000 and 50,000 across near and far, with and without a sourced role. In Al-Baha no sampled town is near (< 25 km) to a line: all six are between 213 and 253 km from Makkah Central. The "near" stratum is empty and is recorded as empty, not filled.

{srows}

Sample edge cases tested: an OSM place missing (Baljurashī, no place node), a governorate seat tagged `place=village` (Al-Ḥajrah, not sampled but listed), and two conflicting centre candidates (Qilwah, Banī Ḥasan). A governorate centre smaller than a non-centre town could not be tested: no non-centre town in Al-Baha has a sourced population in these sources.

## Exclusions (rule 2: every governorate is in the register)

- **Al-Qarā** (row AB-06): `screened: false`. The centre is not located: no OSM place node was found and no coordinate source exists. Its governorate total is 19,586 (`S-al_baha-001`); that total is not used as a centre population. The row stays so that every governorate has a row. It fails the schema because coordinates are required (see the report).
- No other row is excluded. Rows without a town population (Al-Ḥajrah, Ghāmid az-Zinād) stay screened with `population: null`.

## Economic roles (sourced only)

- Administrative (governorate seat): all 10 rows, `S-al_baha-001` (citypopulation governorate table).
- Airport: Al-Aqiq (row AB-02), King Saud Domestic Airport, domestic only, "located in Al-Aqiq" (`S-al_baha-010`, Wikipedia). No distance from the town to the airport was sourced.
- Region-level, not attached to a town: summer tourism and honey (about 1,000 t, about 20 % of Kingdom production, no year, AJEL 27 Jul 2025, `S-al_baha-011`). Pomegranate and "over 8,000 tons" figures from a search snippet are not verified and are not used. Heritage villages (Dhee Ain and others) come from a travel guide (weak) and are not used.
- University: no sourced campus in Baljurashī, Al-Makhwāh, Qilwah, Al-Aqiq or Banī Ḥasan. Al-Baha University's Wikipedia page returned 404. Left empty.
- Giga-project, Hajj/Umrah, mining, port, border crossing, military, industrial city: none found for Al-Baha in the sources read.

## Needs Opus judgement

1. **Schema (`common/schemas.py`, not editable by this track; additive-only rule).** `RegionRow` rejects `pop_type: secondary` (10 populated rows), so validation passes only with `secondary` mapped to `official`, which is a validation-only substitute and is not written to the file. `RegionRow` has no `threshold_50k`, `pilot_sample`, `sample_reason`, `nearest_metro_tier`, `road_min_method`, `notes` or `primary_to_find`, and it forbids extras, so those are extra Parquet columns. The brief's `dist_km_existing` naming is the schema's `dist_existing_km`; the schema name is used. The brief's `coastal_plain` is `coastal` in the schema; not needed for Al-Baha.
2. **Al-Qarā coordinates.** `lat`/`lon` are required by `RegionRow`. Options: locate the centre (GASTAT or OSM), or make coordinates optional for `screened: false` rows.
3. **Governorate count.** 10 rows (citypopulation) versus 9 (Wikipedia and Saudipedia). GASTAT's list is unreachable. Decide whether the Al-Bāḥah row is a governorate or the regional capital, after the GASTAT list is read.
4. **Baljurashī, 50k rule.** Governorate total 51,787 (≥ 50k) but town 35,985 (< 50k). The threshold is applied to settlements, so `threshold_50k` is false. Confirm.
5. **Banī Ḥasan and Qilwah centres.** Banī Ḥasan: OSM town vs Saudipedia's Bidan / Wadi Al-Sadr. Qilwah: town node 8506335688 vs governorate node 6768458212 (20.0000 N, 41.0833 E). Both kept as conflicts.
6. **Al-Ḥajrah centre tagged `place=village`** in OSM, while being a governorate seat. Kept as-is; the tag is OSM's. Population unsourced.
7. **Committed-line distances.** Not computed: no sourced station coordinates. Needed for the R1a line layer.
8. **Terrain.** Region-level class; per-town class needs the DEM (R1a).

## Notes per row

{notes}

## Sources

Full rows in `docs/sources/pilot-al_baha.csv`. Summary:

- `S-al_baha-001` citypopulation.de, Al-Bahah region admin table (census 2022-05-10, region total 339,174): https://www.citypopulation.de/en/saudiarabia/admin/ (secondary; credits GASTAT)
- `S-al_baha-002` citypopulation.de, Al-Bahah region place table: https://citypopulation.de/en/saudiarabia/bahah/ (secondary; credits GASTAT)
- `S-al_baha-003` citypopulation.de, Baljurashī place page: https://citypopulation.de/en/saudiarabia/bahah/baljurashī/12002__baljurashī/ (secondary)
- `S-al_baha-004` Wikipedia, Baljurashi (coordinates only): https://en.wikipedia.org/wiki/Baljurashi (secondary)
- `S-al_baha-005` Wikipedia, Al-Bahah Province (governorate list; no named source): https://en.wikipedia.org/wiki/Al-Bahah_Province (secondary)
- `S-al_baha-006` OpenStreetMap place nodes via Nominatim (ODbL): https://nominatim.openstreetmap.org/ (verified; IDs and coordinates)
- `S-al_baha-007` OpenStreetMap Haramain station nodes (ODbL): verified
- `S-al_baha-008` Wikipedia, Haramain high-speed railway (opened 11 Oct 2018): https://en.wikipedia.org/wiki/Haramain_high-speed_railway (secondary)
- `S-al_baha-009` Wikipedia, Sarawat Mountains: https://en.wikipedia.org/wiki/Sarawat_Mountains (secondary)
- `S-al_baha-010` Wikipedia, Al-Aqiq (airport location): https://en.wikipedia.org/wiki/Al-Aqiq (secondary)
- `S-al_baha-011` AJEL, honey article (27 Jul 2025): https://english.ajel.sa/lifestyle/al-baha-honey-blending-culinary-tradition-with-economic-and-tourism-growth (secondary; region-level)
- `S-al_baha-012` Saudipedia, Bni Hasan governorate: https://saudipedia.com/en/bni-hasan-governorate (secondary)
- Kingdom index: `S-070` (13 regions, verified); `S-072` (governorate count, unverified); `S-090` (GASTAT portal, unreachable).

Label: synthetic demand, uncalibrated: scenario comparison, not a forecast. Screening input, not a forecast.
"""
open(f"{R}/docs/regions/pilot-al_baha.md", "w", encoding="utf-8").write(doc)
print("written", len(doc))
