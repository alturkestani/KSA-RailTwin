# ruff: noqa
# Pilot builder script recovered by CP1_PREP (item 4, Q24), 31 Oct 2026.
# Origin: /tmp/qassim_build/build.py (last modified 2026-10-30 21:31 +03, pilot run PILOT_REGION_QASSIM).
# Role: built the region register.
# Outputs named in the code: pilot-qassim.csv, pilot-qassim.parquet.
# Archival copy: absolute paths rewritten to repository-relative ("./") or "~"; logic
# unchanged. It ran in the pilot worktree with network access (Nominatim/Overpass or
# citypopulation.de); re-running it is not part of the test suite.
# Label: pilot, proposed criteria pending CP1; screening input, not a forecast.

"""Build the Qassim pilot register from archived raw sources (scratch script, not committed).

Inputs: data/ksa/pilot-qassim/raw/ (citypopulation.de pages, OSM Nominatim JSON, OSM Overpass rail JSON).
Outputs: cities/ksa/regions/pilot-qassim.{parquet,csv} (paths relative to the worktree root).
"""

import json
import math
import sys
from pathlib import Path

import pandas as pd

ROOT = Path("./")
RAW = ROOT / "data/ksa/pilot-qassim/raw"
OUT = ROOT / "cities/ksa/regions"
OUT.mkdir(parents=True, exist_ok=True)

BURAYDAH = (26.3316670, 43.9716670)  # OSM node 1236365110 (place=city)
STATION_QASSIM = (26.4922762, 44.0915573)  # OSM node 7985031321, Wikidata Q85874780
STATION_MAJMAAH_BOX = (25.9207722, 45.4197342)  # OSM node 7985031031 (outside Qassim, in box)

ov = json.loads((RAW / "overpass_rail_qassim_box.json").read_text(encoding="utf-8"))
SEGS = [
    [(p["lat"], p["lon"]) for p in e["geometry"]]
    for e in ov["elements"]
    if e["type"] == "way"
    and e.get("tags", {}).get("railway") == "rail"
    and e["tags"].get("name") == "قطار الشمال"
    and e["tags"].get("usage") == "main"
]


def hav(lat1, lon1, lat2, lon2):
    r = 6371.0088
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = p2 - p1
    dl = math.radians(lon2 - lon1)
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(h))


def dist_line(lat, lon):
    best = min(
        hav(lat, lon, a + (c - a) * k / 10, b + (d - b) * k / 10)
        for g in SEGS
        for (a, b), (c, d) in zip(g, g[1:], strict=False)
        for k in range(11)
    )
    return round(best, 1)


# (name_en, name_ar, governorate_en, governorate_ar, is_centre, osm_type, osm_id, lat, lon,
#  pop, pop_note, roles, sample, sample_reason, excluded_reason, notes)
R_TERRAIN = "flat_desert"
ROLE_ADMIN = [{"role": "administrative", "source": "S-qassim-004"}]
ROLE_TOURISM = [{"role": "tourism", "source": "S-qassim-009"}]
ROLE_AGRI = [{"role": "agriculture", "source": "S-qassim-009"}]

GOV = {
    "Al-'Asyāḥ": "الأسياح",
    "Al-Badā'i'a": "البدائع",
    "Al-Bukayriyah": "البكيرية",
    "Al-Midhnab": "المذنب",
    "An-Nabhāniyah": "النبهانية",
    "Ar-Rass": "الرس",
    "Ash-Shimāiyah": "الشماسية",
    "Buraydah": "بريدة",
    "Ḍariyah": "ضرية",
    "Riyāḍ al-Khabrā'": "رياض الخبراء",
    "'Unaīzah": "عنيزة",
    "'Uqalt aṣ-Ṣuqūr": "عقلة الصقور",
    "'Uyūn al-Jiwā'": "عيون الجواء",
}

ROWS = [
    # centres (governorate rows: centre = governorate name)
    dict(
        name_en="Al-'Asyāḥ",
        name_ar="الأسياح",
        gov="Al-'Asyāḥ",
        centre=True,
        osm=("node", 11081595197, 26.7958412, 44.2036285),
        pop=None,
        pop_src=["S-qassim-002"],
        roles=[],
        notes="Centre place row not in citypopulation Qassim list; governorate total 35,533 (S-qassim-001) is not the centre's population, so population left null.",
    ),
    dict(
        name_en="Al-Badā'i'a",
        name_ar="البدائع",
        gov="Al-Badā'i'a",
        centre=True,
        osm=("node", 6770266310, 25.9877958, 43.7334802),
        pop=48474,
        pop_src=["S-qassim-002"],
        roles=[],
        notes="Below 50k.",
    ),
    dict(
        name_en="Al-Bukayriyah",
        name_ar="البكيرية",
        gov="Al-Bukayriyah",
        centre=True,
        osm=("relation", 12406850, 26.1499429, 43.6653550),
        pop=43229,
        pop_src=["S-qassim-002"],
        roles=[],
        notes="Coordinates are the OSM boundary-relation centroid (no place node found by Nominatim, Latin or Arabic query). Replace with the place node in R2. Below 50k.",
    ),
    dict(
        name_en="Al-Midhnab",
        name_ar="المذنب",
        gov="Al-Midhnab",
        centre=True,
        osm=("relation", 12406843, 25.8596075, 44.2209063),
        pop=33341,
        pop_src=["S-qassim-002"],
        roles=[],
        notes="Coordinates are the OSM boundary-relation centroid (no place node found). Below 50k.",
    ),
    dict(
        name_en="An-Nabhāniyah",
        name_ar="النبهانية",
        gov="An-Nabhāniyah",
        centre=True,
        osm=("way", 302790288, 25.8555674, 43.0813273),
        pop=5221,
        pop_src=["S-qassim-002"],
        roles=[],
        notes="Below 10k; above 5k.",
    ),
    dict(
        name_en="Ar-Rass",
        name_ar="الرس",
        gov="Ar-Rass",
        centre=True,
        osm=("node", 346703530, 25.8685205, 43.5038978),
        pop=107902,
        pop_src=["S-qassim-002", "S-qassim-003"],
        roles=ROLE_AGRI,
        threshold50=True,
        notes="Economic role from secondary search snippet (S-qassim-009), unverified against a primary source.",
    ),
    dict(
        name_en="Ash-Shimāiyah",
        name_ar="الشماسية",
        gov="Ash-Shimāiyah",
        centre=True,
        osm=("node", 1236365190, 26.3183330, 44.2630560),
        pop=5719,
        pop_src=["S-qassim-002"],
        roles=[],
        notes="Governorate centre smaller than the non-centre sample town Qibah (11,506); tests the centre-vs-town edge across governorates.",
    ),
    dict(
        name_en="Buraydah",
        name_ar="بريدة",
        gov="Buraydah",
        centre=True,
        osm=("node", 1236365110, 26.3316670, 43.9716670),
        pop=571169,
        pop_src=["S-qassim-002", "S-qassim-003"],
        roles=ROLE_ADMIN,
        threshold50=True,
        notes="Regional capital; the nearest approved metro (tier 2) for the Qassim rows.",
    ),
    dict(
        name_en="Ḍariyah",
        name_ar="ضرية",
        gov="Ḍariyah",
        centre=True,
        osm=("relation", 12406851, 24.9308875, 42.5833004),
        pop=5485,
        pop_src=["S-qassim-002"],
        roles=[],
        coord_flag=True,
        notes="COORDINATE UNRESOLVED: no Qassim place node found (Latin and Arabic queries). The boundary-relation centroid at 24.93N, 42.58E looks too far south for Ḍariyah in Qassim, so distances are invalid. Replace before R2.",
    ),
    dict(
        name_en="Riyāḍ al-Khabrā'",
        name_ar="رياض الخبراء",
        gov="Riyāḍ al-Khabrā'",
        centre=True,
        osm=("node", 734945198, 26.0547858, 43.5580679),
        pop=25588,
        pop_src=["S-qassim-002"],
        roles=[],
        notes="Below 50k.",
    ),
    dict(
        name_en="'Unaīzah",
        name_ar="عنيزة",
        gov="'Unaīzah",
        centre=True,
        osm=("way", 785290146, 26.0908582, 43.9864354),
        pop=183319,
        pop_src=["S-qassim-002", "S-qassim-003"],
        roles=ROLE_TOURISM,
        threshold50=True,
        notes="Economic role from secondary search snippet (date-season festival), unverified against a primary source.",
    ),
    dict(
        name_en="'Uqalt aṣ-Ṣuqūr",
        name_ar="عقلة الصقور",
        gov="'Uqalt aṣ-Ṣuqūr",
        centre=True,
        osm=("node", 747671382, 25.8283880, 42.1979070),
        pop=None,
        pop_src=["S-qassim-002"],
        roles=[],
        notes="Centre place row not in the citypopulation Qassim list (Hijrat 'Uqlat aṣ-Ṣuqūr, 9,717, is a separate place). Population left null.",
    ),
    dict(
        name_en="'Uyūn al-Jiwā'",
        name_ar="عيون الجواء",
        gov="'Uyūn al-Jiwā'",
        centre=True,
        osm=("node", 1237556276, 26.4945913, 43.6377184),
        pop=15619,
        pop_src=["S-qassim-002"],
        roles=[],
        notes="OSM place node is named 'Al Jiwa' (inside the 'Uyūn al-Jiwā' governorate boundary, relation 12406842).",
    ),
    # excluded: sub-locality named Abanat (AR Wikipedia 14th row), not a GASTAT-listed governorate
    dict(
        name_en="Abanat (sub-locality, not a governorate row)",
        name_ar="أبانات",
        gov="An-Nabhāniyah",
        centre=False,
        osm=("node", 11350920607, 25.4445031, 42.7036929),
        pop=None,
        pop_src=[],
        roles=[],
        excluded=True,
        excluded_reason="Not in the 13-governorate list (S-qassim-001, S-qassim-002, S-qassim-004). Appears only in the Arabic Wikipedia count (S-075 family). OSM village nodes sit inside the An-Nabhāniyah governorate boundary (relation 12406848). Kept as an excluded row for the audit trail pending GASTAT confirmation.",
        notes="Governorate attribution inferred from the OSM boundary, not from a source.",
    ),
    # pilot sample: non-centre towns 5k-50k
    dict(
        name_en="Al-Quwārah",
        name_ar="القوارة",
        gov="Buraydah",
        centre=False,
        osm=("node", 747671390, 26.7818580, 43.4668500),
        pop=5646,
        pop_src=["S-qassim-002"],
        roles=[],
        sample=True,
        sample_reason="Near (<25 km) with no sourced role: tests the near arm of the stratification. No sourced role found in this pass.",
    ),
    dict(
        name_en="Al-Malīdā'",
        name_ar="المليداء",
        gov="Buraydah",
        centre=False,
        osm=("node", 1237555392, 26.3182830, 43.7807599),
        pop=6967,
        pop_src=["S-qassim-002"],
        roles=[],
        sample=True,
        sample_reason="Mid band (25-100 km) by distance but within 31 km of the line; no sourced role. Tests the mid band with a small town inside Buraydah governorate.",
    ),
    dict(
        name_en="Al-Khubarā'",
        name_ar="الخبراء",
        gov="Buraydah",
        centre=False,
        osm=("node", 1237557434, 26.0700478, 43.6244595),
        pop=16906,
        pop_src=["S-qassim-002"],
        roles=[],
        sample=True,
        sample_reason="Mid band (25-100 km), largest non-centre town in the sample (16,906), no sourced role. Tests a sample town above 10k.",
    ),
    dict(
        name_en="Qibah",
        name_ar="قبة",
        gov="Al-'Asyāḥ",
        centre=False,
        osm=("node", 747671189, 27.4024971, 44.3241290),
        pop=11506,
        pop_src=["S-qassim-002"],
        roles=[],
        sample=True,
        sample_reason="Far (>100 km): tests the far arm and a non-centre town larger than its governorate centre (Al-'Asyāḥ centre pop null); also larger than Ash-Shimāiyah centre (5,719). No sourced role.",
    ),
    dict(
        name_en="Dakhnah",
        name_ar="دخنة",
        gov="Ar-Rass",
        centre=False,
        osm=("node", 747667497, 25.3610001, 43.6140003),
        pop=6354,
        pop_src=["S-qassim-002"],
        roles=[],
        sample=True,
        sample_reason="Far (>100 km) with no sourced role: second far-arm town and a non-centre town in the Ar-Rass governorate.",
    ),
]


def build_row(r):
    otype, oid, lat, lon = (
        r["osm"][0],
        r["osm"][1],
        r["osm"][2] if len(r["osm"]) > 2 else None,
        r["osm"][3] if len(r["osm"]) > 3 else None,
    )
    excluded = r.get("excluded", False)
    pop = r["pop"]
    dl = dist_line(lat, lon) if lat is not None else None
    dm = round(hav(lat, lon, *BURAYDAH), 1)
    dst = round(hav(lat, lon, *STATION_QASSIM), 1)
    tag10 = pop is not None and pop >= 10000
    tag5 = pop is not None and pop >= 5000
    return {
        "name_ar": r["name_ar"],
        "name_en": r["name_en"],
        "region": "qassim",
        "governorate": r["gov"],
        "governorate_ar": GOV[r["gov"]],
        "is_governorate_centre": r["centre"],
        "osm_id": oid,
        "lat": lat,
        "lon": lon,
        "population": pop,
        "pop_source": "S-qassim-002" if pop is not None else None,
        "pop_year": 2022 if pop is not None else None,
        "pop_type": "secondary" if pop is not None else None,
        "tag_10k": tag10,
        "tag_5k": tag5,
        "dist_existing_km": dl,
        "road_min_existing": None,
        "nearest_existing": "SAR Riyadh–Qurayyat passenger line (OSM geometry, operating)",
        "dist_committed_km": None,
        "road_min_committed": None,
        "nearest_committed": None,
        "nearest_committed_station": None,
        "dist_metro_km": dm,
        "road_min_metro": None,
        "nearest_metro": "Buraydah (tier 2)",
        "economic_roles": r["roles"],
        "terrain_class": R_TERRAIN,
        "screened": not excluded,
        "exclusion_reason": r.get("excluded_reason") if excluded else None,
        "sources": sorted(
            set(
                r["pop_src"]
                + ["S-qassim-001", "S-qassim-006", "S-qassim-007", "S-qassim-005"]
                + ([s["source"] for s in r["roles"]] if r["roles"] else [])
            )
        ),
        # extra (pilot-only) columns: not in common/schemas.py:RegionRow
        "name_osm_type": otype,
        "threshold_50k": bool(r.get("threshold50", False)),
        "pilot_sample": bool(r.get("sample", False)),
        "nearest_metro_tier": 2,
        "dist_method": "haversine",
        "dist_station_qassim_km": dst,
        "road_min_method": "pending R1a skims",
        "terrain_status": "assumed (A-qassim-terrain-001)",
        "coord_flag": bool(r.get("coord_flag", False)),
        "notes": (
            r.get("notes", "") + (" " + r["sample_reason"] if r.get("sample") else "")
        ).strip(),
    }


rows = [build_row(r) for r in ROWS]
df = pd.DataFrame(rows)

# Schema-enforced fields (canonical RegionRow) and pilot-only extras, kept separate.
df.to_parquet(OUT / "pilot-qassim.parquet", index=False)
csv = df.copy()
csv["economic_roles"] = csv["economic_roles"].apply(lambda v: json.dumps(v, ensure_ascii=False))
csv["sources"] = csv["sources"].apply(lambda v: ";".join(v))
csv.to_csv(OUT / "pilot-qassim.csv", index=False, encoding="utf-8")
print(len(df), "rows written")
print(
    df[
        [
            "name_en",
            "governorate",
            "population",
            "dist_existing_km",
            "dist_metro_km",
            "pilot_sample",
            "is_governorate_centre",
            "screened",
        ]
    ].to_string()
)
