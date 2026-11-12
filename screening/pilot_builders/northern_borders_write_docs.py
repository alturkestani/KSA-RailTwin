# ruff: noqa
# Pilot builder script recovered by CP1_PREP (item 4, Q24), 31 Oct 2026.
# Origin: /tmp/nbpilot/write_docs.py (last modified 2026-10-30 21:44 +03, pilot run PILOT_REGION_NORTHERN_BORDERS).
# Role: wrote the region documents.
# Outputs named in the code: docs/regions/pilot-northern_borders.md.
# Archival copy: absolute paths rewritten to repository-relative ("./") or "~"; logic
# unchanged. It ran in the pilot worktree with network access (Nominatim/Overpass or
# citypopulation.de); re-running it is not part of the test suite.
# Label: pilot, proposed criteria pending CP1; screening input, not a forecast.

import csv, json
from pathlib import Path

REPO = Path("./")
rows = json.load(open("/tmp/nbpilot/rows.json"))
osm = json.load(open("/tmp/nb_places.json"))["elements"]
used_osm = {r["osm_id"] for r in rows}
lbl = "screening input, not a forecast"


def pop(r):
    return f"{r['population']:,}" if r["population"] is not None else "null"


def roles(r):
    return ", ".join(f"{x['role']} ({x['source']})" for x in r["economic_roles"]) or "none sourced"


def trow(r):
    tags = "/".join(
        [
            "50k" if r["threshold_50k"] else "-",
            "10k" if r["tag_10k"] else "-",
            "5k" if r["tag_5k"] else "-",
        ]
    )
    return (
        f"| {r['name_en']} | {r['name_ar']} | {r['governorate']} | {'yes' if r['is_governorate_centre'] else 'no'} | "
        f"{pop(r)} | {r['pop_type'] or 'null'} | {r['pop_year'] or 'null'} | {', '.join(r['sources'][:2])}… | {tags} | "
        f"{r['dist_existing_km']} km ({r['nearest_existing']}) | {r['dist_metro_km']} km, {r['nearest_metro']} (tier {r['nearest_metro_tier']}) | "
        f"{roles(r)} | {r['terrain_class']} (assumed) | {'yes' if r['screened'] else 'no'} | {'yes' if r['pilot_sample'] else 'no'} |"
    )


tbl = "\n".join(trow(r) for r in rows)
exc_osm = []
for e in osm:
    if e["id"] in used_osm:
        continue
    t = e["tags"]
    exc_osm.append(
        f"| {t.get('name:en') or t.get('name')} | {t.get('name:ar') or t.get('name') or ''} | {t.get('place')} | {e['type']} {e['id']} | not in the ≥2,500 secondary list; population unsourced |"
    )
exc_osm_txt = "\n".join(exc_osm)
import hashlib

SHA_P = hashlib.sha256(
    open(REPO / "data/ksa/northern_borders/osm_places_nb.json", "rb").read()
).hexdigest()
SHA_R = hashlib.sha256(
    open(REPO / "data/ksa/northern_borders/osm_rail_nb.json", "rb").read()
).hexdigest()
N_EXC = len(exc_osm)
# Linah: two OSM objects (town node and village way) for one place; no sourced population or governorate
md = f"""> **Document version:** docs/regions/pilot-northern_borders.md v1.0 | 30 Oct 2026 | Author: region-scout (pilot, PILOT_REGION_NORTHERN_BORDERS) | Status: draft

# Northern Borders (الحدود الشمالية): coarse pilot sweep

Slug `northern_borders` · Register `cities/ksa/regions/pilot-northern_borders.parquet` (CSV twin alongside) · Access date for every source: 30 Oct 2026 (Asia/Riyadh) · Label: **{lbl}**.

This is the pilot. It tests the `region-sweep` schema on one region with a coarse, high-cut-off sweep. It is not the full register (`REGION_NORTHERN_BORDERS`, R2).

## Governorate count

- `governorates_gastat: null`: **not verified.** The GASTAT primary table was not reachable on 30 Oct 2026 (`portal.saudicensus.sa` DNS failure; S-072, S-090).
- `governorates_listed: 4`: Arar (region seat and governorate), Rafha, Turaif and Al-Uwayqilah. Each has a row for its centre.
- **Discrepancy flagged, both sources cited.** Citypopulation.de (S-001) and the English Wikipedia governorate table (S-003) list 4 units, Arar included. Saudipedia's Arabic article (S-002) says "three governorates" plus an administrative capital, Arar. OSM holds four governorate boundary relations (Arar 12413339, Rafha 12413338, Turaif 12413340, Al-Uwayqilah 12413341). The count of 4 treats Arar as a governorate, which matches S-001, S-003 and OSM. It stays unconfirmed until GASTAT's table is read.

## Summary

| item | value |
|---|---|
| Register rows | {len(rows)} (4 governorate centres, 4 others) |
| Towns ≥ 50,000 (`threshold_50k`) | 3: Arar, Rafha, Turaif (locality figures) |
| Towns 5,000–50,000 | 2: Al-Uwayqilah (governorate centre), Rawdat Habas |
| Pilot sample (`pilot_sample: true`) | 5 rows, with a reason each. **Only 2 are in the 5–50k band** (see the sample section) |
| Population source | all populated rows: S-northern_borders-001 (secondary aggregator; `pop_type: secondary`) |
| Existing line | SAR North (OSM way geometry, `layer: existing`): main line and branches |
| Committed line | none sourced in the region (see Exclusions and Needs Opus judgement) |

## Rows

Columns: population is the **locality** figure (Census 2022, secondary), tags are `50k/10k/5k`, distances are great-circle (haversine, A-screen-pilot-001) to the nearest OSM vertex of the named SAR North line, and to the nearest metro centre in the A-screen-013 set. Road minutes are null (`road_min_method: pending R1a skims`). Terrain classes are assumed (A-screen-pilot-002).

| name (EN) | name (AR) | governorate | centre | population 2022 | pop_type | pop_year | sources (first two)… | tags | dist existing (line) | dist metro (tier) | economic roles (source) | terrain | screened | pilot_sample |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
{tbl}

Full source lists per row are in the Parquet/CSV `sources` column.

## Sample rationale (task 3)

The brief asks for 4–6 towns between 5,000 and 50,000. **Only two places in this region meet that band** in the secondary list (S-001, which covers places of at least 2,500 people): Al-Uwayqilah (17,055) and Rawdat Habas (5,620). The sample therefore holds those two plus three below-band controls, with reasons:

| row | band | why it is in the sample |
|---|---|---|
| Al-Uwayqilah | 5–50k | in band; governorate centre; more than 100 km from the existing line; administrative role |
| Rawdat Habas | 5–50k | in band; non-centre; more than 100 km from the existing line; no sourced economic role |
| Talah at-Tamiat | below 5k (3,770) | control: far from the line; OSM 'village' tag and a probable name match ('At Timyat') |
| Sha'bih Nasab | below 5k (3,430) | control: far from the line; OSM 'town' tag on a 3,430 place (tag/size mismatch) |
| Hazm al-Jalamid | no population | near (14 km) the line; mining role; population unsourced, so null: tests the null-population path |

Coverage of the distance and role strata: near (under 25 km) is one row (Hazm); far (over 100 km) is four; with a sourced economic role is one (Hazm, mining) plus the administrative roles of the centres.

**Schema edges not testable here.** The "governorate centre smaller than a non-centre town" case does not occur: Al-Uwayqilah (17,055) is larger than every non-centre town in the list. No town is split across governorates in the sources read. The "unmapped OSM place" case is Mazar'at Jaza' al-Yarman (below). Two tag-level edges are recorded: OSM population tags are 2010 values (Arar 167,057; Rafha 52,712; Turaif 48,108; Rawdat Habas 5,532) and are not used; and Linah appears twice in OSM (a town node and a village way).

## Exclusions (rule 2: none silent)

**Excluded from the register (no coordinates):** Mazar'at Jaza' al-Yarman (مزرعة جزاء اليرمان), Turaif governorate, 2,545 (S-001). No OSM object was found by name (Nominatim search, 30 Oct 2026), so there are no coordinates to register. Kept in this list as the unmapped-place edge case.

**Excluded from the register (no sourced population ≥ 2,500):** the {N_EXC} other OSM place objects inside the region (Overpass, S-northern_borders-005; this count includes duplicate ways for places also present as nodes, e.g. Linah, Daydeeb and Lawqah). None appears in the secondary list of places at or above 2,500 people (S-001), so their population is below 2,500 or unsourced. Their names are listed here so the omission is visible. Linah (لينة) is an OSM town node and a village way for one place. Its governorate is not sourced, so it is excluded too.

| name (EN) | name (AR) | OSM place | OSM object | reason |
|---|---|---|---|---|
{exc_osm_txt}

## Sources

Ids in this list are the pilot's own (`S-northern_borders-nnn`, see `docs/sources/pilot-northern_borders.csv`), plus existing repository ids (S-017, S-018, S-022 for the SAR North line; S-072 and S-090 for the GASTAT failure).

- **S-northern_borders-001** citypopulation.de, Northern Borders region page: Census 2022 governorate and locality figures, source line "General Statistics Authority, Kingdom of Saudi Arabia (web)". Secondary; GASTAT primary to find.
- **S-northern_borders-002** Saudipedia, منطقة الحدود الشمالية (Arabic): governorate list and category, 2022 figures. Search summary, not read in full.
- **S-northern_borders-003** English Wikipedia, Northern Borders Province: governorate table and regional total (CC BY-SA; facts only).
- **S-northern_borders-004** OpenStreetMap via Nominatim (ODbL 1.0, © OpenStreetMap contributors): coordinates, OSM ids, governorate boundaries, the Rafha aerodrome relation 11881620, metro city nodes.
- **S-northern_borders-005** OpenStreetMap via Overpass (ODbL 1.0): place objects and railway ways in the region box. Raw JSON archived at `data/ksa/northern_borders/osm_places_nb.json` and `osm_rail_nb.json` (gitignored; SHA-256 `{SHA_P}` and `{SHA_R}`).
- **S-northern_borders-006** Wikipedia, Arar border crossing (Saudi–Iraqi crossing between Arar and An Nukhayb).
- **S-northern_borders-007** Al Jazeera, 18 Nov 2020: the Arar crossing reopened after 30 years.
- **S-northern_borders-008** Wikipedia, Jalamid: Ma'aden phosphate mine site near the Iraqi border.
- **S-northern_borders-009** MEED, minerals railway: Al Jalamid to Ras Al Khair (about 1,390 km; about 4 Mt/yr capacity). Search summary.
- **S-northern_borders-010** Wikipedia, Nafud desert: an erg in north-central Saudi Arabia, about 65,000 km². Region-level only.
- **S-northern_borders-011** MEED, GCC rail link tender: Saudi section about 672 km, Al-Khafji to Al-Batha, at tender stage. Search summary.
- **S-northern_borders-012** Arab News headline: "The 1,392-km railway line between Hazm Al-Jalameed, Northern Borders and Ras Al Khair" (title only).
- **S-017, S-018, S-022** existing: SAR network and Riyadh–Qurayyat line (passenger), from DATASCOUT_1H.
- **S-054** existing: Landbridge Riyadh–Jeddah (MEED), cited for the committed-line note.

## Needs Opus judgement

1. **Governorate count (3 or 4).** S-002 says "three governorates" plus an administrative capital (Arar). S-001, S-003 and OSM give 4 units with Arar as a governorate. GASTAT's table is needed to settle it. Unresolved.
2. **Sample band.** Only 2 of 5 sample rows are in the 5–50k band. The region has no further 5–50k towns in the secondary list. Is the below-band control set acceptable, or should the pilot accept a lower band for this region?
3. **Terrain.** All terrain classes are assumed (A-screen-pilot-002). Rafha is 'dunes' by regional description (S-010), not by DEM. Arar, Turaif and the others are 'flat_desert' by default, with no sourced class. The DEM pass (R1a) should settle it.
4. **Hazm al-Jalamid.** Population unsourced (null). Mining role sourced (S-008, S-009). The OSM geometry near Hazm has a named SAR North branch (14 km) and unnamed branch segments (19 km). Are the unnamed ways part of the phosphate line? Opus should decide whether to add them to the existing layer.
5. **Committed layer.** Nothing committed is sourced for this region. The unnamed OSM 'construction' segments near 31.60 N, 38.99–39.00 E (ways 1408864679–81) are a possible branch under construction, with no source. They are not labelled committed. Opus should decide whether an OSM observation can count as a source, or whether the layer waits for a published source.
6. **Existing-line status.** The named SAR North ways are labelled `existing` on the strength of S-017, S-018 and S-022. Those sources do not give the freight/passenger status of the Jouf–Qurayyat and phosphate branches, and the Al Haditha stop is listed as 'proposed' in one older source. Passenger status per branch is unverified.
7. **Name variants.** 'Turaif' (GASTAT) vs 'Turayf' (OSM). 'At Timyat' (OSM) vs 'Ṭala'h at-Tamiat' (GASTAT): a probable match, unconfirmed. Turaibil (Iraq–Jordan crossing) is not Saudi and is not used.
8. **Road minutes and metro distances.** All road minutes are pending R1a skims. Metro distances are straight-line only; Tabuk and Buraidah are the nearest tier-2 centres for every row.

## Licences and attribution

- OpenStreetMap data (ODbL 1.0): © OpenStreetMap contributors. Used for coordinates, OSM ids, railway geometry and place lists. Derived distances are not a database extract; share-alike must be checked before any public release (licence register, R2).
- Census figures: citypopulation.de states its source as GASTAT. Its own licence was not checked: treat as unclear until the GASTAT primary table is read.
- Wikipedia text (CC BY-SA): facts only, nothing copied.

## Method notes

- Haversine (great-circle) distances, rounded to 0.1 km, to the nearest vertex of each OSM railway way (A-screen-pilot-001). OSM vertex spacing adds a small error.
- Existing line: OSM ways whose name contains "قطار الشمال", excluding `service=siding|yard|crossover`. Treated as in service (A-screen-pilot-005).
- Metro centres: OSM city nodes. The Makkah centre is the region relation centroid; it is not the nearest metro for any row (checked).
- Population: locality figures, not governorate totals (A-screen-pilot-003).

{lbl[0].upper() + lbl[1:]}. Not a forecast; no demand or ridership is modelled here.
"""
(REPO / "docs/regions").mkdir(parents=True, exist_ok=True)
(REPO / "docs/regions/pilot-northern_borders.md").write_text(md, encoding="utf-8")
print("md chars", len(md))
