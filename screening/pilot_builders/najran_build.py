# ruff: noqa
# Pilot builder script recovered by CP1_PREP (item 4, Q24), 31 Oct 2026.
# Origin: /tmp/najran_work/build.py (last modified 2026-10-30 22:02 +03, pilot run PILOT_REGION_NAJRAN).
# Role: built the region register.
# Outputs named in the code: cities/ksa/regions/pilot-najran.csv, cities/ksa/regions/pilot-najran.parquet, cities/ksa/regions/pilot-najran.parquet; docs/regions/pilot-najran.md, docs/regions/pilot-najran.md, docs/regions/pilot-najran.md; cities/ksa/regions/pilot-najran.parquet, docs/sources/pilot-najran.csv.
# Archival copy: absolute paths rewritten to repository-relative ("./") or "~"; logic
# unchanged. It ran in the pilot worktree with network access (Nominatim/Overpass or
# citypopulation.de); re-running it is not part of the test suite.
# Label: pilot, proposed criteria pending CP1; screening input, not a forecast.

import csv, json, math
import pandas as pd

ACC = "2026-10-30"
CP = "https://www.citypopulation.de/en/saudiarabia/admin/"
CPN = "https://citypopulation.de/en/saudiarabia/najran/"
SRC_COLS = "id,claim,value,unit,url,publisher,title,published,accessed,locator,quote,status,primary_to_find,used_in".split(
    ","
)
SOURCES = [
    [
        "S-najran-001",
        "Najran region governorate list and Census 2022 governorate populations (7 rows incl. the regional capital; rows sum to the region total)",
        "592,300 region total; 7 rows",
        "persons; rows",
        "https://www.citypopulation.de/en/saudiarabia/admin/",
        "citypopulation.de (source line credits General Statistics Authority)",
        "Saudi Arabia: administrative divisions, Najrān Region (census 2022)",
        "2022-05-10 (census reference, S-071)",
        ACC,
        "Najrān governorate table",
        '"Source: General Statistics Authority, Kingdom of Saudi Arabia." (WebFetch extraction; table rows as printed)',
        "secondary",
        "GASTAT primary table (portal.saudicensus.sa, unreachable on 2026-10-30; S-090)",
        "docs/regions/pilot-najran.md; cities/ksa/regions/pilot-najran.parquet",
    ],
    [
        "S-najran-002",
        "Census 2022 localities of Najran region with at least 2,500 inhabitants: Najrān 381,431; Sharūrah 89,456; Al-Mish'alīah 23,252; Ḥubūnā 12,738; Al-Wadī'ah 8,365; Khubāsh 7,182; Yadamah 4,983; Badr al-Janūb 2,709",
        "see claim",
        "persons",
        "https://citypopulation.de/en/saudiarabia/najran/",
        "citypopulation.de (source line credits General Statistics Authority)",
        "Saudi Arabia: Najrān Region, places (census 2022)",
        "2022-05-10 (census reference, S-071)",
        ACC,
        "Places (localities with at least 2,500 inhabitants) table",
        '"Source: General Statistics Authority, Kingdom of Saudi Arabia (web)."',
        "secondary",
        "GASTAT census locality table (primary not reachable; S-090)",
        "docs/regions/pilot-najran.md; cities/ksa/regions/pilot-najran.parquet",
    ],
    [
        "S-najran-003",
        "Najran Province: six governorates plus the regional capital; about 65 administrative centres (search snippet, page not opened)",
        "6 governorates + capital",
        "governorates",
        "https://saudipedia.com/en/article/1145/geography/provinces-and-cities/najran-province",
        "Saudipedia",
        "Najran Province",
        "unknown",
        ACC,
        "search snippet",
        "not captured verbatim",
        "secondary",
        "GASTAT governorate list (S-073, S-090)",
        "docs/regions/pilot-najran.md",
    ],
    [
        "S-najran-004",
        "OpenStreetMap place nodes (place=*) and railway ways (railway=rail, construction, proposed, disused, abandoned) from the GCC states extract; node and way IDs in the register",
        "OSM extract 2026-10-14",
        "OSM IDs",
        "https://download.geofabrik.de/asia/gcc-states-latest.osm.pbf",
        "Geofabrik GmbH / OpenStreetMap contributors (ODbL 1.0)",
        "OpenStreetMap GCC states extract (manifest id osm-gcc-2026-10-14)",
        "2026-10-14",
        ACC,
        "local file, SHA-256 fffc7e74...6ad2073 (cities/ksa/sources.yaml)",
        "© OpenStreetMap contributors (ODbL)",
        "verified",
        "none needed (coordinates and IDs only)",
        "cities/ksa/regions/pilot-najran.parquet; docs/regions/pilot-najran.md",
    ],
    [
        "S-najran-005",
        "Najran University is located in the city of Najran",
        "Najran city",
        "text",
        "https://portal.nu.edu.sa/en/geographical-location",
        "Najran University",
        "Geographical Location",
        "unknown",
        ACC,
        "search snippet of university portal",
        '"located in the city of Najran" (paraphrase from search summary)',
        "secondary",
        "none for pilot",
        "docs/regions/pilot-najran.md",
    ],
    [
        "S-najran-006",
        "Najran airport (Najran Domestic/Regional Airport, EAM/OENG) opened for domestic and international traffic",
        "airport in service (route list not verified)",
        "text",
        "https://timesaerospace.aero/news/airports/najran-airport-opens-for-domestic-and-international-traffic",
        "Times Aerospace",
        "Najran Airport opens for domestic and international traffic",
        "unknown",
        ACC,
        "search snippet",
        "not captured verbatim; current operations not verified",
        "secondary",
        "current route network (not needed for pilot)",
        "docs/regions/pilot-najran.md",
    ],
    [
        "S-najran-007",
        "Al-Wadiah is a town in Sharūrah governorate with a crossing to Yemen; the area is served by Sharūrah Domestic Airport",
        "border crossing and airport",
        "text",
        "https://en.wikipedia.org/wiki/Al-Wadiah",
        "Wikipedia (CC BY-SA; facts only)",
        "Al-Wadiah",
        "unknown",
        ACC,
        "search summary",
        "not captured verbatim",
        "secondary",
        "official border-status source (not needed for pilot)",
        "docs/regions/pilot-najran.md",
    ],
    [
        "S-najran-008",
        "Sarawat Mountains intersect the Najran region (with Al-Baha, Asir and Jazan)",
        "escarpment",
        "text",
        "https://saudipedia.com/en/article/1006/geography/mountains/sarawat-mountains",
        "Saudipedia",
        "Sarawat Mountains",
        "unknown",
        ACC,
        "search snippet",
        "not captured verbatim",
        "secondary",
        "DEM classification (R1a, Copernicus or SRTM)",
        "docs/regions/pilot-najran.md",
    ],
    [
        "S-najran-009",
        "Najran valley runs west to east and merges into the eastern desert; Sharūrah sits at the desert margin (dune claim weakly sourced)",
        "desert description",
        "text",
        "https://saudipedia.com/en/sharurah-governorate",
        "Saudipedia (page not opened; search summary)",
        "Sharurah Governorate",
        "unknown",
        ACC,
        "search summary",
        "not captured verbatim; the dune claim traces to an unnamed source and is treated as assumed",
        "unverified",
        "DEM classification (R1a)",
        "docs/regions/pilot-najran.md",
    ],
    [
        "S-najran-010",
        "Governor of Najran supervised the departure of Yemeni pilgrims from the Al-Wadiah border crossing (border crossing in operation)",
        "operating crossing",
        "text",
        "https://english.ajel.sa/saudi-arabia/governor-of-najran-supervises-facilitating-departure-of-yemeni-pilgrims-from-al-wadeeah-border-crossing",
        "Saudi Press Agency partner feed (ajel.sa)",
        "Governor of Najran supervises facilitating departure of Yemeni pilgrims from Al-Wadeeah border crossing",
        "unknown",
        ACC,
        "search snippet",
        "not captured verbatim; date not captured",
        "secondary",
        "official crossing status (Ministry of Interior)",
        "docs/regions/pilot-najran.md",
    ],
]
with open("docs/sources/pilot-najran.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(SRC_COLS)
    w.writerows(SOURCES)

# ----- register rows -----
R = 6371.0088


def hav(a, b):
    la1, lo1 = map(math.radians, a)
    la2, lo2 = map(math.radians, b)
    d = (
        math.sin((la2 - la1) / 2) ** 2
        + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    )
    return 2 * R * math.asin(math.sqrt(d))


D = json.load(open("/tmp/najran_work/dist.json", encoding="utf-8"))


def ex(k):
    return D["existing"][k]


def mt(k):
    return D["metro"][k]


def row(**kw):
    base = dict(
        region="najran",
        road_min_existing=None,
        road_min_committed=None,
        road_min_metro=None,
        dist_committed_km=None,
        nearest_committed=None,
        nearest_committed_station=None,
        economic_roles=[],
        terrain_class=None,
        screened=True,
        exclusion_reason=None,
        pilot_sample=False,
        threshold_50k=False,
        pop_year=2022,
        tag_10k=False,
        tag_5k=False,
        notes="",
        osm_place_tag="",
        road_min_method="pending R1a skims",
    )
    base.update(kw)
    return base


HHR = "Haramain high-speed rail (OSM segment near Makkah)"
RIY_DAM = "Riyadh–Dammam line (OSM, named 'قطار الدمام - الخط الثاني')"
rows = []
rows.append(
    row(
        name_ar="نجران",
        name_en="Najrān",
        governorate="Najrān",
        governorate_ar="نجران",
        is_governorate_centre=True,
        osm_id=982548735,
        lat=17.54398,
        lon=44.22468,
        population=381431,
        pop_source="S-najran-002",
        pop_type="secondary",
        tag_10k=True,
        tag_5k=True,
        threshold_50k=True,
        pilot_sample=False,
        dist_existing_km=ex("najran")[0],
        nearest_existing=HHR,
        dist_metro_km=mt("najran")[0],
        nearest_metro="Najrān (tertiary)",
        economic_roles=[
            {"role": "administrative", "source": "S-najran-001"},
            {"role": "university", "source": "S-najran-005"},
            {"role": "airport", "source": "S-najran-006"},
        ],
        terrain_class="mixed",
        sources=[
            "S-najran-001",
            "S-najran-002",
            "S-najran-004",
            "S-najran-005",
            "S-najran-006",
            "S-najran-008",
        ],
        notes="Regional capital. Governorate population 421,902 (S-najran-001) is the governorate total; the row uses the city figure 381,431 (S-najran-002). OSM place=city.",
    )
)
rows.append(
    row(
        name_ar="شرورة",
        name_en="Sharūrah",
        governorate="Sharūrah",
        governorate_ar="شرورة",
        is_governorate_centre=True,
        osm_id=1013646681,
        lat=17.49123,
        lon=47.11261,
        population=89456,
        pop_source="S-najran-002",
        pop_type="secondary",
        tag_10k=True,
        tag_5k=True,
        threshold_50k=True,
        dist_existing_km=ex("sharurah")[0],
        nearest_existing=RIY_DAM,
        dist_metro_km=mt("sharurah")[0],
        nearest_metro="Najrān (tertiary)",
        economic_roles=[
            {"role": "administrative", "source": "S-najran-001"},
            {"role": "airport", "source": "S-najran-007"},
        ],
        terrain_class="dunes",
        sources=["S-najran-001", "S-najran-002", "S-najran-004", "S-najran-007", "S-najran-009"],
        notes='Governorate population 100,199 incl. Al-Khirkhīr (S-najran-001); the town row uses 89,456 (S-najran-002). Dune terrain is an assumption (A-najran-terrain-001). The airport role rests on the airport name in S-najran-007 ("Sharurah Domestic Airport"); its location is not verified.',
    )
)
rows.append(
    row(
        name_ar="المشعلية",
        name_en="Al-Mish'alīah",
        governorate="Najrān",
        governorate_ar="نجران",
        is_governorate_centre=False,
        osm_id=4213220389,
        lat=17.75783,
        lon=44.46435,
        population=23252,
        pop_source="S-najran-002",
        pop_type="secondary",
        tag_10k=True,
        tag_5k=True,
        pilot_sample=True,
        dist_existing_km=ex("almishalia")[0],
        nearest_existing=HHR,
        dist_metro_km=mt("almishalia")[0],
        nearest_metro="Najrān (tertiary)",
        terrain_class="mixed",
        sources=["S-najran-002", "S-najran-004", "S-najran-008"],
        osm_place_tag="village",
        notes="Pilot sample (5k–50k, non-centre, near a tertiary metro). Reason: largest sourced non-centre locality in Najrān governorate; tests the OSM tag mismatch (OSM place=village against a census 'Place' of 23,252). Also the closest sample town to Najrān (≈35 km) for the commuter-belt test.",
    )
)
rows.append(
    row(
        name_ar="حبونا",
        name_en="Ḥubūnā",
        governorate="Ḥubūnā",
        governorate_ar="حبونا",
        is_governorate_centre=True,
        osm_id=11871306300,
        lat=17.85185,
        lon=44.02316,
        population=12738,
        pop_source="S-najran-002",
        pop_type="secondary",
        tag_10k=True,
        tag_5k=True,
        pilot_sample=True,
        dist_existing_km=ex("hubuna")[0],
        nearest_existing=HHR,
        dist_metro_km=mt("hubuna")[0],
        nearest_metro="Najrān (tertiary)",
        economic_roles=[{"role": "administrative", "source": "S-najran-001"}],
        terrain_class="mixed",
        sources=["S-najran-001", "S-najran-002", "S-najran-004"],
        osm_place_tag="town",
        notes="Pilot sample: governorate centre within 5k–50k. Tests a centre below a governorate total (governorate 24,823 vs centre 12,738; S-najran-001, S-najran-002). OSM also holds a governorate node at 17.78333, 44.2 (n6769844117); the town node is used as the centre.",
    )
)
rows.append(
    row(
        name_ar="خباش",
        name_en="Khubāsh",
        governorate="Khubāsh",
        governorate_ar="خباش",
        is_governorate_centre=True,
        osm_id=8503374507,
        lat=17.54985,
        lon=44.74113,
        population=7182,
        pop_source="S-najran-002",
        pop_type="secondary",
        tag_10k=False,
        tag_5k=True,
        pilot_sample=True,
        dist_existing_km=ex("khubash_village")[0],
        nearest_existing=HHR,
        dist_metro_km=mt("khubash_village")[0],
        nearest_metro="Najrān (tertiary)",
        economic_roles=[{"role": "administrative", "source": "S-najran-001"}],
        terrain_class="mixed",
        sources=["S-najran-001", "S-najran-002", "S-najran-004"],
        osm_place_tag="village",
        notes="Pilot sample: 5k–10k governorate centre. Tests the centre's coordinates: OSM has a village node 'خباش' (n8503374507) and a governorate node (n6774251958, 17.66667, 45.25, distance to existing rail 708.0 km, to Najrān 109.5 km). The village node is used; choice to be confirmed (see Needs Opus judgement). Governorate 7,834 (S-najran-001).",
    )
)
rows.append(
    row(
        name_ar="الوديعه",
        name_en="Al-Wadī'ah",
        governorate="Sharūrah",
        governorate_ar="شرورة",
        is_governorate_centre=False,
        osm_id=1236473531,
        lat=17.05751,
        lon=47.08815,
        population=8365,
        pop_source="S-najran-002",
        pop_type="secondary",
        tag_10k=False,
        tag_5k=True,
        pilot_sample=True,
        dist_existing_km=ex("wadiah")[0],
        nearest_existing=RIY_DAM,
        dist_metro_km=mt("wadiah")[0],
        nearest_metro="Najrān (tertiary)",
        economic_roles=[{"role": "border_crossing", "source": "S-najran-010"}],
        terrain_class="dunes",
        sources=["S-najran-002", "S-najran-004", "S-najran-007", "S-najran-009", "S-najran-010"],
        osm_place_tag="village",
        notes="Pilot sample: non-centre town with a border crossing (role). Reason: tests a sourced economic role on a sub-10k town and the border-crossing role. Spelling in OSM: الوديعة. Dune terrain is an assumption (A-najran-terrain-001). Border status to verify with official sources.",
    )
)
rows.append(
    row(
        name_ar="يدمة",
        name_en="Yadamah",
        governorate="Yadamah",
        governorate_ar="يدمة",
        is_governorate_centre=True,
        osm_id=6774224946,
        lat=18.52917,
        lon=44.20306,
        population=4983,
        pop_source="S-najran-002",
        pop_type="secondary",
        tag_10k=False,
        tag_5k=False,
        screened=False,
        dist_existing_km=ex("yadamah")[0],
        nearest_existing=HHR,
        dist_metro_km=mt("yadamah")[0],
        nearest_metro="Najrān (tertiary)",
        economic_roles=[{"role": "administrative", "source": "S-najran-001"}],
        terrain_class="mixed",
        sources=["S-najran-001", "S-najran-002", "S-najran-004"],
        osm_place_tag="village",
        exclusion_reason="Centre population 4,983 is below the 5,000 sensitivity threshold (A-screen-002). Kept as the governorate-centre coverage row (rule 2). Governorate total 16,160 (S-najran-001) is not used as the centre figure.",
    )
)
rows.append(
    row(
        name_ar="بدر الجنوب",
        name_en="Badr al-Janūb",
        governorate="Badr al-Janūb",
        governorate_ar="بدر الجنوب",
        is_governorate_centre=True,
        osm_id=9327906415,
        lat=17.88137,
        lon=43.71636,
        population=2709,
        pop_source="S-najran-002",
        pop_type="secondary",
        tag_10k=False,
        tag_5k=False,
        screened=False,
        dist_existing_km=ex("badr")[0],
        nearest_existing=HHR,
        dist_metro_km=mt("badr")[0],
        nearest_metro="Najrān (tertiary)",
        economic_roles=[{"role": "administrative", "source": "S-najran-001"}],
        terrain_class="mixed",
        sources=["S-najran-001", "S-najran-002", "S-najran-004"],
        osm_place_tag="town",
        exclusion_reason="Centre population 2,709 is below 5,000 (A-screen-002). Kept as the governorate-centre coverage row (rule 2). Governorate total 7,991 (S-najran-001).",
    )
)
rows.append(
    row(
        name_ar="ثار",
        name_en="Thār",
        governorate="Thār",
        governorate_ar="ثار",
        is_governorate_centre=True,
        osm_id=6774275597,
        lat=17.97488,
        lon=44.11082,
        population=None,
        pop_source=None,
        pop_type=None,
        tag_10k=False,
        tag_5k=False,
        screened=False,
        dist_existing_km=ex("thar")[0],
        nearest_existing=HHR,
        dist_metro_km=mt("thar")[0],
        nearest_metro="Najrān (tertiary)",
        economic_roles=[{"role": "administrative", "source": "S-najran-001"}],
        terrain_class="mixed",
        sources=["S-najran-001", "S-najran-002", "S-najran-004"],
        osm_place_tag="town",
        exclusion_reason="No sourced centre population: Thār is not in the census locality table (places ≥2,500, S-najran-002), so the centre figure is null (not guessed). Governorate total 13,391 (S-najran-001) is not used. Kept as coverage row (rule 2).",
    )
)

df = pd.DataFrame(rows)
df["population"] = df["population"].astype("Int64")
df.loc[df["name_en"].isin(["Najrān", "Sharūrah"]), "osm_place_tag"] = "city"
df.loc[df["population"].isna(), "pop_year"] = None
df["pop_year"] = df["pop_year"].astype("Int64")
for c in ["economic_roles"]:
    df[c] = df[c].apply(lambda v: v)
df["road_min_method"] = "pending R1a skims"
df["dist_method"] = "haversine (A-screen-pilot-001)"
df["screen_stage"] = "pilot"
df.to_parquet("cities/ksa/regions/pilot-najran.parquet", index=False)
flat = df.copy()
flat["economic_roles"] = flat["economic_roles"].apply(
    lambda v: "; ".join(f"{r['role']}:{r['source']}" for r in v)
)
flat["sources"] = flat["sources"].apply(lambda v: "; ".join(v))
flat.to_csv("cities/ksa/regions/pilot-najran.csv", index=False, encoding="utf-8")
print(len(df), "rows written")
print(
    df[
        [
            "name_en",
            "governorate",
            "population",
            "pop_type",
            "tag_5k",
            "tag_10k",
            "threshold_50k",
            "pilot_sample",
            "screened",
            "dist_existing_km",
            "dist_metro_km",
        ]
    ].to_string()
)
