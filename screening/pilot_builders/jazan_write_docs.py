# ruff: noqa
# Pilot builder script recovered by CP1_PREP (item 4, Q24), 31 Oct 2026.
# Origin: /tmp/jz/build/write_docs.py (last modified 2026-10-30 21:43 +03, pilot run PILOT_REGION_JAZAN).
# Role: wrote the region documents.
# Outputs named in the code: cities/ksa/regions/pilot-jazan.parquet, docs/regions/pilot-jazan.md.
# Archival copy: absolute paths rewritten to repository-relative ("./") or "~"; logic
# unchanged. It ran in the pilot worktree with network access (Nominatim/Overpass or
# citypopulation.de); re-running it is not part of the test suite.
# Label: pilot, proposed criteria pending CP1; screening input, not a forecast.

import json, csv
from pathlib import Path
import pyarrow as pa, pyarrow.parquet as pq
import pandas as pd

REPO = Path("./")
pq_path = REPO / "cities/ksa/regions/pilot-jazan.parquet"
# Parquet header metadata: governorate counts (GASTAT not reached; see docs/regions/pilot-jazan.md)
tbl = pq.read_table(pq_path)
meta = {
    b"governorates_gastat": b"unverified",
    b"governorates_listed": b"17",
    b"governorates_secondary_saudipedia": b"16",
    b"label": "screening input, not a forecast".encode(),
}
pq.write_table(tbl.replace_schema_metadata({**(tbl.schema.metadata or {}), **meta}), pq_path)

df = pd.read_parquet(pq_path)
# places >= 5,000 in the citypopulation Jazan 2022 places table (scratch parse of S-jazan-002), for the exclusions note
places = [
    l for l in Path("/tmp/jz/rows.txt").read_text(encoding="utf-8").splitlines() if " Place " in l
]
import re


def last_int(l):
    return int(re.findall(r"([\d,]+)\s*(?:→)?\s*$", l)[0].replace(",", ""))


pl = [(l, last_int(l)) for l in places]
n_places = len(pl)
n_5k = sum(1 for _, v in pl if v >= 5000)
n_10k = sum(1 for _, v in pl if v >= 10000)
n_50k = sum(1 for _, v in pl if v >= 50000)
in_reg = set(df.loc[df.population.notna(), "population"].astype(int))
print("places", n_places, ">=5k", n_5k, ">=10k", n_10k, ">=50k", n_50k)


def fmt(v, nd=1):
    return "" if pd.isna(v) else f"{v:,.{nd}f}"


def popfmt(v):
    return "–" if pd.isna(v) else f"{int(v):,}"


lines = [
    "| # | governorate | centre (EN / AR) | pop 2022 (S-jazan-002) | osm_id | lat, lon | 5k / 10k / 50k | dist existing km (Makkah HSR) | dist metro km | nearest metro | terrain | economic roles | sample |",
    "|---|---|---|---|---|---|---|---|---|---|---|---|---|",
]
for i, r in enumerate(df.itertuples(index=False), 1):
    roles = (
        ", ".join(x["role"] for x in r.economic_roles) if len(r.economic_roles) else "none sourced"
    )
    tags = f"{'Y' if r.tag_5k else 'N'} / {'Y' if r.tag_10k else 'N'} / {'Y' if r.threshold_50k else 'N'}"
    osm = "none (see Needs Opus 2)" if pd.isna(r.osm_id) else str(int(r.osm_id))
    centre = "centre" if r.is_governorate_centre else "town"
    lines.append(
        f"| {i} | {r.governorate} | {r.name_en} / {r.name_ar} ({centre}) | {popfmt(r.population)} | {osm} | {r.lat:.5f}, {r.lon:.5f} | {tags} | {fmt(r.dist_existing_km)} | {fmt(r.dist_metro_km)} | {r.nearest_metro} | {r.terrain_class} | {roles} | {'Y' if r.pilot_sample else ''} |"
    )
table = "\n".join(lines)


def nm(v):
    return "–" if pd.isna(v) else v


n_reg_5k = int((df.population.fillna(0) >= 5000).sum())
n_5k_out = n_5k - n_reg_5k
md = f"""> **Document version:** docs/regions/pilot-jazan.md v1.0 | 30 Oct 2026 | Author: region-scout (pilot, track pilot-jazan) | Status: draft

# Jazan (جازان) pilot sweep: coarse register

**Label: screening input, not a forecast.** This is the pilot (`PILOT_REGION_JAZAN`) of the region-sweep schema. It is not the full Jazan register (`REGION_JAZAN` in R2). Accessed 30 Oct 2026 (Asia/Riyadh). Source ids: `docs/sources/pilot-jazan.csv` (S-jazan-nnn) and the global index `docs/sources/index.csv`.

## 1. Governorate count

| source | count | status |
|---|---|---|
| GASTAT official list | **not read**: portal.saudicensus.sa did not connect on 30 Oct 2026 (S-jazan-015, S-090) | unverified |
| citypopulation.de, Census 2022 administrative list (S-jazan-001; global S-073) | **17** | secondary |
| Saudipedia, Jazan Emirate (S-jazan-003) | 16 (3 class A: Sabya, Abu Arish, Samtah; 13 class B; about 41 centres) | secondary |

Header key: `governorates_gastat: unverified` (Parquet metadata); `governorates_listed: 17`. **The discrepancy (16 vs 17) is flagged, not resolved.** The register carries 17 governorate rows, one per governorate of the citypopulation list, each with its centre. citypopulation marks Aṭ-Ṭuwāl, Fayfā and Harūb with a previous parent governorate (Ṣāmiṭah, Jīzān, Al-'Aydābī), so a newer-governorate effect is one possible reason for 16 vs 17. That is a hypothesis, not checked. Acceptance: 17 governorates listed; GASTAT count to be confirmed (Needs Opus judgement 1).

## 2. What the register holds

- **20 rows:** 17 governorate centres (every governorate has at least one row) and 3 non-centre sample towns.
- **Towns ≥ 50,000 (Census 2022, secondary):** Jizan 173,919; Sabya 72,086; Abu Arish 69,632. Tagged `threshold_50k`.
- **Population missing (null, not guessed):** Al Harth, Ar Rayth, Harub, Fayfa. Their centres do not appear in the citypopulation places table (places of at least 2,500). Governorate-level totals exist, but a centre figure would be a guess.
- **Rail, by layer:**
  - *Existing:* the only existing line near Jazan is the Haramain HSR. Its nearest station to the region is Makkah (OSM node 10956967098, S-jazan-008), about 480–640 km from every row. No existing line or station lies in Jazan.
  - *Committed / under procurement:* no Jazan line or station is in any source. `dist_committed_km` is therefore null for every row. The Landbridge alignment (announced, Jeddah–Riyadh) has no published station coordinates in the repo, so no distance is computed.
  - *Hypothetical:* none; not a register field.
- **Metro (A-screen-013):** nearest approved metro by haversine. Jazan (tier 3) for 17 rows; Abha–Khamis Mushait (tier 2) for Ad Darb (60.1 km), Abu as Sadad (61.9 km) and Ar Rayth (77.6 km).
- **Road minutes:** null everywhere; `road_min_method: pending R1a skims`.
- **Distances:** great-circle haversine between OSM coordinates (A-screen-pilot-001), not road distances.

## 3. The register (generated from `cities/ksa/regions/pilot-jazan.parquet`)

{table}

Population is the Census 2022 value from citypopulation.de (secondary, crediting GASTAT; `pop_type: secondary`, `pop_year: 2022`). The `5k / 10k / 50k` column shows the tags. `terrain` is assumed by rule (A-screen-pilot-002) pending DEM classes; see Needs Opus 4.

## 4. Sample rationale (5 rows, `pilot_sample: true`)

The brief asked for 4–6 towns that test schema edges and a spread of roles. Jazan has no existing or committed rail line, so **no row is near (<25 km) an existing line; all 20 rows are far (>100 km).** The sample spans the other axes:

| row | why it was chosen |
|---|---|
| Abu as Sadad (9,940; non-centre, Ad Darb) | **Schema edge:** a non-centre town larger than its governorate centre Ad Darb (5,216). No sourced economic role. |
| Farasan (10,118; governorate centre, island) | **With roles:** tourism and heritage (S-jazan-010, -011). Coastal island centre. |
| Samtah (43,301; governorate centre) | **With role:** agriculture (S-jazan-012, a search snippet). Below 50k, so tests the threshold. |
| Al Zabyah (11,287; non-centre, Sabya) | **Without role:** about 5 km from Sabya (72,086), so it sits inside a 50k town's reach. |
| Misliyah (5,559; non-centre, Bish) | **Without role, 5k band:** `tag_5k` only (not `tag_10k`), tests the sensitivity tag. |

Other edges in the pilot: **unmapped OSM place**, Al Harth (no `place=*` node in the box query). Its coordinates are a Nominatim boundary centroid (S-jazan-006), a placeholder rather than a settlement point. **Town split across governorates:** not found in the sources, so not tested.

## 5. Exclusions

- **No row is excluded** (`screened: true` for all 20).
- **Not in the pilot (out of scope, not excluded):** the other places in the Census 2022 list. The citypopulation table has {n_places} places (≥ 2,500); {n_5k} reach 5,000 and {n_10k} reach 10,000. The register keeps {n_reg_5k} of the {n_5k} places at or above 5,000 (the 17 centres where they are 5k+, plus 3 sample towns). The other {n_5k_out} are out of pilot scope. The full R2 register must cover them under A-screen-001 (10k) and A-screen-002 (5k sensitivity).

## 6. Sources

Full list with access date and status: `docs/sources/pilot-jazan.csv`. Summary:
- Population and governorate list: S-jazan-001, S-jazan-002 (citypopulation.de, secondary, crediting GASTAT; global S-073).
- Governorate count, second opinion: S-jazan-003 (Saudipedia, secondary).
- Coordinates and `osm_id`: S-jazan-005 (OSM Overpass, ODbL), S-jazan-006 (Nominatim, Al Harth), S-jazan-007 (Najran, metro check).
- Existing rail: S-jazan-008 (OSM Makkah HHR station), cross-checked with S-001 (sar.hhr.sa).
- Economic roles: S-jazan-009 (JCPDI port and zone; secondary, location conflict), S-jazan-010 and -011 (Farasan), S-jazan-012 (Samtah).
- Terrain: S-jazan-013 (Wikipedia, approximate).
- GASTAT not reached: S-jazan-015 (and S-090).

## 7. Needs Opus judgement

1. **Governorate count, 16 vs 17.** Saudipedia (16) vs citypopulation (17). GASTAT's own table is needed to settle it (portal.saudicensus.sa unreachable; stats.gov.sa reachable but its census table was not located). Pilot keeps 17 rows.
2. **Al Harth centre.** No OSM `place=*` node was found in the box query. The coordinate is the Nominatim boundary bbox centre (16.7842, 43.1529; relation 12430365), a placeholder. The Arabic centre name is the governorate name, not confirmed. Needs a real place node or a GASTAT locality record.
3. **Jizan port location.** The JCPDI port is reported 60 km north of Jizan in one source and 60 km south-east in another (S-jazan-009). The port and the industrial zone are attached to the Jizan centre row as roles without coordinates for the zone. Confirm before using in any document.
4. **Terrain classes are rule-based.** Coastal below longitude 42.75 E; mixed east of it; Fayfa escarpment_mountain (S-jazan-013). This is A-screen-pilot-002 and is not a DEM read. Copernicus DEM classes are needed in R2.
5. **Centre populations missing** for Ar Rayth, Harub, Fayfa and Al Harth (the governorate totals exist, the centre places do not in the 2022 places table). Needs the GASTAT locality table.
6. **Roles that were not sourced.** Sabya and Abu Arish (50k+) have only the administrative role (governorate centre). Al Tuwal is on the Yemen border, but no crossing is sourced: `border_crossing` not assigned.
7. **Samtah agriculture** rests on a search snippet of the Saudipedia page. Read the page before using the role.
8. **Governorate reassignments.** Aṭ-Ṭuwāl, Fayfā and Harūb are marked with a previous parent on citypopulation (see section 1). The governorate membership of their settlements should be checked in the GASTAT admin table.

## 8. Schema notes (for the coordinator)

- `common/schemas.py:RegionRow` allows `pop_type` ∈ {{official, derived, grid}}. The pilot uses `secondary` (the brief's instruction). The validation used a local subclass that accepts `secondary` and changes nothing else (`PILOT_REGION_JAZAN` status block).
- The brief's extra fields (`threshold_50k`, `pilot_sample`, `sample_reason`, `nearest_metro_tier`, `terrain_basis`, `primary_to_find`, `road_min_method`, `dist_method`) are not in `RegionRow` (strict). They are written as extra Parquet/CSV columns and are not validated.
- `uv run python -m screening.region_sweep validate` does not exist yet (`screening/cli.py` is the R0 skeleton). The check was run as `RegionRow` validation with the subclass above.

Label: **screening input, not a forecast.**
"""
(REPO / "docs/regions/pilot-jazan.md").write_text(md, encoding="utf-8")
print("md chars", len(md))
