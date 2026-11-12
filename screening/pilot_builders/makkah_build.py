# ruff: noqa
# Pilot builder script recovered by CP1_PREP (item 4, Q24), 31 Oct 2026.
# Origin: /tmp/pilot_makkah/build.py (last modified 2026-10-30 21:12 +03, pilot run PILOT_REGION_MAKKAH).
# Role: built the region register.
# Outputs named in the code: none written to files.
# Archival copy: absolute paths rewritten to repository-relative ("./") or "~"; logic
# unchanged. It ran in the pilot worktree with network access (Nominatim/Overpass or
# citypopulation.de); re-running it is not part of the test suite.
# Label: pilot, proposed criteria pending CP1; screening input, not a forecast.

"""Pilot sweep of Makkah region: builds Parquet + CSV against common/schemas.py:RegionRow.

Inputs are the values recorded in docs/sources/pilot-makkah.csv (citypopulation.de Makkah page,
2026-10-30; OSM via Nominatim, 2026-10-30). Distances: haversine (A-screen-pilot-001).
"""

import math
import pandas as pd
from common.schemas import RegionRow

R_EARTH = 6371.0088


def hav(a, b):
    la1, lo1 = map(math.radians, a)
    la2, lo2 = map(math.radians, b)
    d = (
        math.sin((la2 - la1) / 2) ** 2
        + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    )
    return round(2 * R_EARTH * math.asin(math.sqrt(d)), 1)


# existing HHR stations located in OSM (Nominatim, 2026-10-30)
EXISTING = {
    "HHR Makkah station (قطار الحرمين السريع - مكة), OSM node 10956967098": (
        21.4176557,
        39.7885323,
    ),
    "HHR King Abdullah Economic City station, OSM node 2147398509": (22.4218244, 39.1917461),
    "HHR KAIA airport station (قطار الحرمين السريع - مطار الملك عبدالعزيز الدولي), OSM node 7227897402": (
        21.6605044,
        39.1738182,
    ),
}
# metro reference points (A-screen-013); city/governorate centre used as the point
METRO = {
    "Makkah (tier 1)": (21.4208470, 39.8268690, 1),
    "Jeddah (tier 1)": (21.5504432, 39.1742363, 1),
    "Taif (tier 2)": (21.2702801, 40.4158308, 2),
}

S_CITYPOP = "S-makkah-001"
S_OSM = "S-makkah-002"
S_GOV = "S-073"

# name_en, name_ar, governorate_en, governorate_ar, is_centre, osm_type, osm_id, lat, lon,
# coords_method, citypop_place_pop (secondary, None if no census place row), governorate_total_secondary,
# existing-network flags handled below
ROWS = [
    # ---- governorate centres (17 governorates; Al-Ardiyat withheld: no coordinates found)
    dict(
        name_en="'Āḍam",
        name_ar="أضم",
        gov="'Āḍam",
        gov_ar="أضم",
        centre=True,
        osm_type="relation",
        osm_id=12429531,
        lat=20.4195865,
        lon=40.8442355,
        method="boundary centroid (Nominatim relation; no place node found)",
        pop_sec=9022,
        gov_tot=33958,
    ),
    dict(
        name_en="Al-Jumūm",
        name_ar="الجموم",
        gov="Al-Jumūm",
        gov_ar="الجموم",
        centre=True,
        osm_type="node",
        osm_id=1236466181,
        lat=21.6211680,
        lon=39.6989787,
        method="OSM place node",
        pop_sec=41089,
        gov_tot=89575,
    ),
    dict(
        name_en="Al-Kāmil",
        name_ar="الكامل",
        gov="Al-Kāmil",
        gov_ar="الكامل",
        centre=True,
        osm_type="node",
        osm_id=1237964645,
        lat=22.2640213,
        lon=39.7982315,
        method="OSM place node",
        pop_sec=3151,
        gov_tot=14370,
    ),
    dict(
        name_en="Khulaīṣ",
        name_ar="خليص",
        gov="Khulaīṣ",
        gov_ar="خليص",
        centre=True,
        osm_type="node",
        osm_id=724120971,
        lat=22.1551359,
        lon=39.3202072,
        method="OSM place node",
        pop_sec=20139,
        gov_tot=51338,
    ),
    dict(
        name_en="Al-Līth",
        name_ar="الليث",
        gov="Al-Līth",
        gov_ar="الليث",
        centre=True,
        osm_type="relation",
        osm_id=12429525,
        lat=20.1451486,
        lon=40.2701391,
        method="boundary centroid (Nominatim relation; no place node found)",
        pop_sec=20811,
        gov_tot=73753,
    ),
    dict(
        name_en="Al-Muwayh",
        name_ar="المويه",
        gov="Al-Muwayh",
        gov_ar="المويه",
        centre=True,
        osm_type="node",
        osm_id=1236449504,
        lat=22.4365659,
        lon=41.7619350,
        method="OSM place node",
        pop_sec=7278,
        gov_tot=29065,
    ),
    dict(
        name_en="Al-Qunfudhah",
        name_ar="القنفذة",
        gov="Al-Qunfudhah",
        gov_ar="القنفذة",
        centre=True,
        osm_type="relation",
        osm_id=12429518,
        lat=19.1264288,
        lon=41.0788747,
        method="boundary centroid (Nominatim relation; no place node found)",
        pop_sec=42447,
        gov_tot=205188,
    ),
    dict(
        name_en="Ranyah",
        name_ar="رنية",
        gov="Ranyah",
        gov_ar="رنية",
        centre=True,
        osm_type="node",
        osm_id=5924471509,
        lat=21.2571996,
        lon=42.8501935,
        method="OSM place node",
        pop_sec=28681,
        gov_tot=49854,
    ),
    dict(
        name_en="Al-Khurmah",
        name_ar="الخرمة",
        gov="Al-Khurmah",
        gov_ar="الخرمة",
        centre=True,
        osm_type="node",
        osm_id=1236454949,
        lat=21.9080694,
        lon=42.0317930,
        method="OSM place node",
        pop_sec=28491,
        gov_tot=38744,
    ),
    dict(
        name_en="Turubah",
        name_ar="تربة",
        gov="Turubah",
        gov_ar="تربة",
        centre=True,
        osm_type="relation",
        osm_id=12429522,
        lat=21.2172851,
        lon=41.5874689,
        method="boundary centroid (Nominatim relation; no place node found)",
        pop_sec=28279,
        gov_tot=41769,
    ),
    dict(
        name_en="Maysān",
        name_ar="ميسان",
        gov="Maysān",
        gov_ar="ميسان",
        centre=True,
        osm_type="node",
        osm_id=295919318,
        lat=20.7371829,
        lon=40.8386833,
        method="OSM place node (no census place row: unmapped)",
        pop_sec=None,
        gov_tot=28765,
    ),
    dict(
        name_en="Makkah al-Mukarramah",
        name_ar="مكة المكرمة",
        gov="Makkah al-Mukarramah",
        gov_ar="مكة المكرمة",
        centre=True,
        osm_type="relation",
        osm_id=12429517,
        lat=21.4208470,
        lon=39.8268690,
        method="boundary centroid (Nominatim relation; no place node found)",
        pop_sec=2385509,
        gov_tot=2427924,
    ),
    dict(
        name_en="Jiddah",
        name_ar="جدة",
        gov="Jiddah",
        gov_ar="جدة",
        centre=True,
        osm_type="node",
        osm_id=1933393717,
        lat=21.5504432,
        lon=39.1742363,
        method="OSM place node",
        pop_sec=3712917,
        gov_tot=3751722,
    ),
    dict(
        name_en="Aṭ-Ṭa'if",
        name_ar="الطائف",
        gov="Aṭ-Ṭa'if",
        gov_ar="الطائف",
        centre=True,
        osm_type="node",
        osm_id=1236468526,
        lat=21.2702801,
        lon=40.4158308,
        method="OSM place node",
        pop_sec=563282,
        gov_tot=913374,
    ),
    dict(
        name_en="Rābigh",
        name_ar="رابغ",
        gov="Rābigh",
        gov_ar="رابغ",
        centre=True,
        osm_type="relation",
        osm_id=12429524,
        lat=22.7989669,
        lon=39.0335547,
        method="boundary centroid (Nominatim relation; no place node found)",
        pop_sec=72928,
        gov_tot=112383,
    ),
    dict(
        name_en="Baḥrah",
        name_ar="بحرة",
        gov="Baḥrah",
        gov_ar="بحرة",
        centre=True,
        osm_type="node",
        osm_id=1237963667,
        lat=21.4012724,
        lon=39.4500096,
        method="OSM place node",
        pop_sec=70118,
        gov_tot=94603,
    ),
    # ---- non-centre settlements
    dict(
        name_en="Al-Ḥawiyah",
        name_ar="الحوية",
        gov="Aṭ-Ṭa'if",
        gov_ar="الطائف",
        centre=False,
        osm_type="node",
        osm_id=295933353,
        lat=21.4448658,
        lon=40.5029502,
        method="OSM place node",
        pop_sec=171610,
        gov_tot=913374,
        note="governorate per OSM (Taif); verify against GASTAT",
    ),
    dict(
        name_en="Thuwal",
        name_ar="ثول",
        gov="Jiddah",
        gov_ar="جدة",
        centre=False,
        osm_type="node",
        osm_id=443345673,
        lat=22.2833454,
        lon=39.1128145,
        method="OSM place node",
        pop_sec=26957,
        gov_tot=None,
        note="governorate per OSM and en.wikipedia snippet (Jeddah Governorate); citypopulation governorate not checked",
    ),
]

# existing-network distance, per row, computed against EXISTING; Jeddah central station not located
# economic roles: only what a source in this pilot supports
ROLES = {
    "Thuwal": [dict(role="university", source="S-makkah-003")],
}
SOURCES_EXTRA = {
    "Thuwal": ["S-makkah-004"],
}

PILOT_SAMPLE = {
    "Al-Jumūm": "near (24.5 km to HHR Makkah station); announced Landbridge stop claimed by owner (S-062, identity S-063), not published; no sourced economic role; tests near-without-role and keeps the announced stop out of existing",
    "Thuwal": "near (17.4 km to HHR KAEC station); sourced economic role (university, KAUST); non-centre town with population above a governorate centre (Khulaīṣ 20,139); governorate ambiguity (Jiddah per OSM)",
    "Khulaīṣ": "mid band (32.5 km to KAEC, 95 km to Makkah station: neither near nor far); no sourced role; centre smaller than non-centre Thuwal (schema edge)",
    "Al-Khurmah": "far (238 km to nearest located HHR station); no sourced role; governorate centre with OSM place node",
    "Al-Qunfudhah": "far (288 km to nearest located HHR station); coastal; no sourced port role (search 30 Oct 2026 found none); centre coordinates from boundary centroid (method edge)",
}
SAMPLE_KEYS = {"Al-Jumūm", "Thuwal", "Khulaīṣ", "Al-Khurmah", "Al-Qunfudhah"}


def build():
    recs, csv_rows = [], []
    for r in ROWS:
        name = r["name_en"]
        d_ex = {k: hav((r["lat"], r["lon"]), v) for k, v in EXISTING.items()}
        k_near = min(d_ex, key=d_ex.get)
        d_met = {k: (hav((r["lat"], r["lon"]), (v[0], v[1])), v[2]) for k, v in METRO.items()}
        k_met = min(d_met, key=lambda k: d_met[k][0])
        pop_sec = r["pop_sec"]
        is_sample = name in SAMPLE_KEYS
        thr50 = pop_sec is not None and pop_sec >= 50_000
        srcs = [S_CITYPOP, S_OSM]
        if name == "Thuwal":
            srcs += ["S-makkah-003", "S-makkah-004"]
        if r["centre"]:
            srcs.append(S_GOV)
        rec = dict(
            name_ar=r["name_ar"],
            name_en=name,
            region="makkah",
            governorate=r["gov"],
            governorate_ar=r["gov_ar"],
            is_governorate_centre=r["centre"],
            osm_id=r["osm_id"],
            lat=r["lat"],
            lon=r["lon"],
            population=None,  # secondary only: pop_type 'secondary' is not in RegionRow (see status block)
            pop_source=None,
            pop_year=None,
            pop_type=None,
            tag_10k=False,
            tag_5k=False,
            dist_existing_km=d_ex[k_near],
            road_min_existing=None,
            nearest_existing=k_near,
            dist_committed_km=None,
            road_min_committed=None,
            nearest_committed=None,
            nearest_committed_station=None,
            dist_metro_km=d_met[k_met][0],
            road_min_metro=None,
            nearest_metro=k_met,
            economic_roles=ROLES.get(name, []),
            terrain_class=None,
            screened=True,
            exclusion_reason=None,
            sources=srcs,
            fixture=False,
        )
        if name == "Al-Kāmil":
            rec["screened"] = False
            rec["exclusion_reason"] = (
                "governorate centre kept for coverage (rule 2); secondary population 3,151 is below 5,000"
            )
        if name == "Jiddah":
            rec["nearest_existing"] = (
                "HHR KAIA airport station (Jeddah central station not located: distance overstated)"
            )
            rec["dist_existing_km"] = d_ex[
                "HHR KAIA airport station (قطار الحرمين السريع - مطار الملك عبدالعزيز الدولي), OSM node 7227897402"
            ]
        if name == "Al-Jumūm":
            rec["nearest_committed"] = (
                "Landbridge (committed): 'Jumoum' intermediate stop (S-062; identity owner-stated S-063)"
            )
            rec["nearest_committed_station"] = "Jumoum (location unpublished)"
        # validate row against the schema
        RegionRow.model_validate(rec)
        recs.append(rec)
        csv_rows.append(
            dict(
                osm_type=r["osm_type"],
                osm_id=r["osm_id"],
                name_en=name,
                name_ar=r["name_ar"],
                governorate=r["gov"],
                is_governorate_centre=r["centre"],
                lat=r["lat"],
                lon=r["lon"],
                coords_method=r["method"],
                population_secondary=pop_sec,
                pop_source_secondary=S_CITYPOP if pop_sec else None,
                governorate_total_secondary=r["gov_tot"],
                threshold_50k=thr50,
                threshold_10k_secondary=bool(pop_sec and pop_sec >= 10_000),
                threshold_5k_secondary=bool(pop_sec and pop_sec >= 5_000),
                pilot_sample=is_sample,
                sample_reason=PILOT_SAMPLE.get(name, "") if is_sample else "",
                dist_existing_km=rec["dist_existing_km"],
                nearest_existing=rec["nearest_existing"],
                dist_metro_km=rec["dist_metro_km"],
                nearest_metro=rec["nearest_metro"],
                economic_roles=";".join(
                    f"{x['role']}:{x['source']}" for x in rec["economic_roles"]
                ),
                screened=rec["screened"],
                exclusion_reason=rec["exclusion_reason"] or "",
                notes=r.get("note", ""),
                sources=";".join(srcs),
            )
        )
    return recs, csv_rows


if __name__ == "__main__":
    import sys

    out = sys.argv[1]
    recs, csv_rows = build()
    ids = [r["osm_id"] for r in recs]
    assert len(ids) == len(set(ids)), "duplicate osm_id"
    df = pd.DataFrame.from_records(recs)
    df["population"] = pd.array([None] * len(df), dtype="Int64")
    df.to_parquet(out + ".parquet", index=False)
    pd.DataFrame.from_records(csv_rows).to_csv(out + ".csv", index=False, encoding="utf-8")
    print("rows", len(recs))
