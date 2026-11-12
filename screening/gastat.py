"""GASTAT population tables (CP2 P1a, item 1 addenda 1 and 2, 31 Oct 2026).

Reads the 21 committed files in `data/ksa/tables/gastat/` (manifest rows `gastat-*`):

- the primary TA1 Excel exports (addendum 2, `gastat_primary`, `verified`):
  `census2022_TA1_governorate_primary.xlsx` (150 governorates) and
  `census2022_TA1_city5k_primary.xlsx` (271 cities of 5,000 or more + "Other" 3,683,816): the
  value of record for governorates and cities from CP2 on;
- `census-2022-20260929.csv` (DataPulse relaying the GASTAT Census 2022 Tableau; `gastat_relayed`,
  `pop_source_status: secondary`): cross-check only since addendum 2 (identical on every row);
- TA1 (PDF) and TA9 (CSV) Census 2022 region tables (`gastat_primary`): check the relayed regions;
- Census 2010 preliminary results: governorates (`twzy_lskn_fy_lmhfzt.xlsx`) and cities > 5,000
  (EN listing) for the 2010→2022 growth method (A-screen-035);
- 2024 national estimate (35,300,280; publication PDF, no regional split).

Commands (outputs under `runs/gastat/`, gitignored; seed recorded for rule 10):

    uv run --with openpyxl python -m screening.gastat tables --seed 1
    uv run --with openpyxl python -m screening.gastat apply --seed 1
    uv run --with openpyxl --with rasterio python -m screening.gastat backtest --seed 1
    uv run python -m screening.gastat primary --seed 1     # addendum 2; after `apply`
"""

from __future__ import annotations

import json
import re
import subprocess
import unicodedata
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import typer
import yaml

from common.runmeta import rng, write_meta
from common.schemas import CORROBORATION_BAND, GRID_UNCORROBORATED, TAG_5K, TAG_10K, corroborates

app = typer.Typer(add_completion=False, help="GASTAT population tables (P1a addendum).")

ROOT = Path(__file__).resolve().parents[1]
GASTAT = Path("data/ksa/tables/gastat")
CENSUS22 = GASTAT / "census-2022-20260929.csv"
TA9 = GASTAT / (
    "TA9-Population2010-2022byRegionNationalityandGender_"
    "Population2010-2022byRegionNationalityandGender.csv"
)
TA1 = GASTAT / (
    "TA1-PopulationbyNationalitybyRegionGovernorateCityandGenderAR_"
    "NW_PopulationbyNationalitybyRegionGovernorateCityandNationalityAR.pdf"
)
GOV2010 = GASTAT / "twzy_lskn_fy_lmhfzt.xlsx"
CITIES2010_AR = GASTAT / "lntyj_lwly_ltdd_2010_nhyy_mntq_wmhfzt.xlsx"
CITIES2010 = GASTAT / (
    "lntyj_lwly_ltdd_2010_nhyy_mntq_wmhfzt_w_lmdn_lty_dd_sknh_yzyd_n_5000_nsm_1_0_0.xlsx"
)
EST2024_XLSX = GASTAT / "Population_Estimates_Statistics_2024_EN.xlsx"
# Primary Census 2022 TA1 Excel exports (item 1 addendum 2; Tariq, 31 Oct 2026): supersede the
# relayed file at governorate and city level
GOV_PRIMARY = GASTAT / "census2022_TA1_governorate_primary.xlsx"
CITY_PRIMARY = GASTAT / "census2022_TA1_city5k_primary.xlsx"
CROSSWALK = Path("screening/gastat_crosswalk.yaml")
ADMIN_HTML = Path("data/ksa/pilot-qassim/raw/citypop_admin.html")
UNIVERSE = Path("cities/ksa/zones/settlements.parquet")
GOV_GEOJSON = Path("cities/ksa/zones/governorates.geojson")
RUN = Path("runs/gastat")

# Source ids (docs/sources/index.csv)
S_RELAYED = "S-cp2-gastat-001"  # DataPulse census-2022 (relays GASTAT Census 2022 Tableau)
S_TA1, S_TA9 = "S-cp2-gastat-002", "S-cp2-gastat-003"
S_GOV2010, S_CITIES2010 = "S-cp2-gastat-004", "S-cp2-gastat-005"
S_EST2024 = "S-cp2-gastat-006"
S_GOV_PRIMARY, S_CITY_PRIMARY = "S-cp2-gastat-007", "S-cp2-gastat-008"
# manifest ids (cities/ksa/sources.yaml) = the universe's `pop_source` (addendum 2, step 3)
MID_GOV_PRIMARY = "gastat-census2022-ta1-governorate-xlsx"
MID_CITY_PRIMARY = "gastat-census2022-ta1-city5k-xlsx"
OTHER_PREFIX = "Other"  # the "Other (Less than 5000 inhabitants)" row of the city table
PRIMARY_TO_FIND = (
    "GASTAT Census 2022 Tableau TA1 'Population by Nationality by Region, Governorate, City and "
    "Gender' (governorate/city view; URL export renders blank, data/ksa/tables/gastat/README.md)"
)
CONFLICT_PCT = 2.0  # prompt CP2_PREP addendum: log a conflict row where figures differ by > 2 %
GROWTH_METHOD = "gastat2010_city_growth"  # A-screen-035

# GASTAT region codes 1..13 (TA9 `Max. REGION_CODE`, TA1 row order) -> repo region slug
REGION_ORDER = [
    "riyadh", "makkah", "madinah", "qassim", "eastern", "asir", "tabuk", "hail",
    "northern_borders", "jazan", "najran", "al_baha", "al_jouf",
]  # fmt: skip
RELAYED_REGION = {
    "Riyadh_Region": "riyadh", "Makkah_Region": "makkah", "Madinah_Region": "madinah",
    "Al_Qaseem_Region": "qassim", "Eastern_Province_Region": "eastern", "Aseer_Region": "asir",
    "Tabouk_Region": "tabuk", "Hail_Region": "hail", "Northern_Borders_Region": "northern_borders",
    "Jazan_Region": "jazan", "Najran_Region": "najran", "Al_Baha_Region": "al_baha",
    "Al_Jouf_Region": "al_jouf",
}  # fmt: skip
# Census 2010 cities list `Administrative Region` labels -> slug
REGION_2010 = {
    "riyadh": "riyadh", "makkah": "makkah", "madinah": "madinah", "al-qassim": "qassim",
    "qassim": "qassim", "eastern region": "eastern", "asir": "asir", "tabuk": "tabuk",
    "hail": "hail", "northern borders": "northern_borders", "northern border": "northern_borders",
    "jazan": "jazan", "jizan": "jazan", "najran": "najran", "al-baha": "al_baha",
    "al-bahah": "al_baha", "al baha": "al_baha", "al-jouf": "al_jouf", "al-jawf": "al_jouf",
    "al jouf": "al_jouf",
}  # fmt: skip


# --------------------------------------------------------------------------- normalisers
def norm_ar(s: Any) -> str:
    s = re.sub(r"\(.*?\)", "", str(s)).strip()
    s = re.sub(r"^محافظة\s*", "", s)
    s = re.sub("[إأآٱ]", "ا", s).replace("ة", "ه").replace("ى", "ي")
    s = re.sub(r"[ً-ْـ]", "", s)
    return re.sub(r"\s+", "", s)


def norm_en(s: Any) -> str:
    s = unicodedata.normalize("NFKD", str(s))
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    s = re.sub(r"\b(governorate|governorate of|of)\b", " ", s)
    s = re.sub(r"[^a-z ]", " ", s.replace("-", " "))
    s = re.sub(r"\b(al|ad|ar|as|ash|az|at|an|adh|el)\b", " ", s)
    return re.sub(r"\s+", "", s)


def _int(x: Any) -> int | None:
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return None
    return int(str(x).replace(",", "").strip())


# --------------------------------------------------------------------------- readers
def read_census2022(path: Path = CENSUS22) -> pd.DataFrame:
    """Tidy relayed Census 2022: level (ksa/region/governorate/city), code, region, metrics."""
    d = pd.read_csv(path, comment="#")
    d.columns = [c.split(" ")[0] for c in d.columns]
    rows: list[dict[str, Any]] = []
    for geo, g in d.groupby("geo", sort=False):
        m = dict(zip(g.metric, g.value, strict=True))
        if "city_population" in m:
            level, pre = "city", "city_population"
        elif geo == "KSA":
            level, pre = "ksa", "population"
        elif str(geo).startswith("gov:"):
            level, pre = "governorate", "population"
        else:
            level, pre = "region", "population"
        rows.append(
            {
                "level": level,
                "code": str(geo)[4:] if level == "governorate" else str(geo),
                "region": RELAYED_REGION.get(str(geo)),
                "population": _int(m[pre]),
                "saudi": _int(m.get(f"{pre}_saudi")),
                "non_saudi": _int(m.get(f"{pre}_non_saudi")),
                "male": _int(m.get(f"{pre}_male")),
                "female": _int(m.get(f"{pre}_female")),
                "city_governorate_population": _int(m.get("governorate_population")),
                "source": S_RELAYED,
                "label": "gastat_relayed",
            }
        )
    return pd.DataFrame(rows)


def read_ta9(path: Path = TA9) -> pd.DataFrame:
    d = pd.read_csv(path)
    d = d[d["Max. REGION_CODE"].notna() & (d.Region != "All")].copy()
    d["region"] = [REGION_ORDER[int(c) - 1] for c in d["Max. REGION_CODE"]]
    d["population"] = d.Mesure_absolute.map(_int)
    return d[["region", "Year", "population"]].rename(columns={"Year": "year"})


def read_ta9_total(path: Path = TA9, year: int = 2022) -> int:
    d = pd.read_csv(path)
    return int(_int(d[(d.Region == "All") & (d.Year == year)].Mesure_absolute.iloc[0]) or 0)


def read_ta1(path: Path = TA1) -> pd.DataFrame:
    """Census 2022 region totals from the TA1 Tableau PDF (pdftotext; rows in GASTAT code order).

    Each data line carries three numbers: non-Saudi, Saudi, total (right-to-left layout)."""
    txt = subprocess.run(
        ["pdftotext", "-layout", str(path), "-"], capture_output=True, text=True, check=True
    ).stdout
    triples = []
    for line in txt.splitlines():
        nums = re.findall(r"\d{1,3}(?:,\d{3})+|\d{4,}", line)
        if len(nums) == 3:
            a, b, c = (int(n.replace(",", "")) for n in nums)
            if a + b == c:
                triples.append((a, b, c))
    triples = [t for t in triples if t[2] != sum(x[2] for x in triples) - t[2]]  # drop KSA total
    if len(triples) != 13:
        raise ValueError(f"TA1: expected 13 region rows, found {len(triples)}")
    return pd.DataFrame(
        [
            {"region": REGION_ORDER[i], "non_saudi": a, "saudi": b, "population": c}
            for i, (a, b, c) in enumerate(triples)
        ]
    )


def read_est2024(path: Path = EST2024_XLSX) -> int:
    """2024 mid-year national estimate: the `Total` row, `Total 2024` total column (EN xlsx)."""
    import openpyxl

    ws = openpyxl.load_workbook(path, read_only=True, data_only=True).worksheets[0]
    head = None
    for r in ws.iter_rows(values_only=True):
        if head is None and r and any(v == "Total 2024" for v in r):
            head = list(r).index("Total 2024") + 2  # Female, Male, Total under each heading
        if r and r[0] == "Total" and head is not None:
            return int(r[head])
    raise ValueError("2024 national total not found")


def read_gov2010(path: Path = GOV2010) -> pd.DataFrame:
    """Census 2010 (preliminary) governorate totals, one sheet per region in GASTAT code order."""
    import openpyxl  # optional dependency: uv run --with openpyxl

    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    rows = []
    for i in range(1, 14):
        ws = wb[f"{i} (2)"]
        for r in ws.iter_rows(values_only=True):
            name, total = r[0], r[10] if len(r) > 10 else None
            if not isinstance(name, str) or not isinstance(total, (int, float)):
                continue
            if "الجملة" in name or "المجموع" in name or "اجمالي" in name or "إجمالي" in name:
                continue
            rows.append(
                {
                    "region": REGION_ORDER[i - 1],
                    "name_ar_2010": re.sub(r"\s+", " ", name).strip(),
                    "pop_2010": int(total),
                }
            )
    return pd.DataFrame(rows)


def read_cities2010(path: Path = CITIES2010) -> pd.DataFrame:
    import openpyxl

    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    ws = wb["City"]
    rows, keys = [], []
    for r in ws.iter_rows(values_only=True):
        if len(r) < 11 or not isinstance(r[0], str) or r[1] is None:
            continue
        parts = [r[2], r[3], r[5], r[6]]  # Saudi M, F; non-Saudi M, F (totals may be formulas)
        if not all(isinstance(v, (int, float)) for v in parts):
            continue
        name, reg, total = r[0], r[1], sum(parts)
        # A printed total that disagrees with its parts is a file defect (Al Seeh: xlsx 103,216 vs
        # parts 234,607; the PDF census31-prim-05 prints 234,607): keep the sum, flag the row.
        printed = int(r[10]) if isinstance(r[10], (int, float)) else None
        slug = REGION_2010.get(str(reg).strip().lower())
        if slug is None:
            raise ValueError(f"cities 2010: unknown region label {reg!r} for {name!r}")
        keys.append(tuple(parts))
        rows.append(
            {
                "city_2010": name.strip(),
                "region": slug,
                "pop_2010": int(total),
                "xlsx_total_defect": printed is not None and printed != int(total),
            }
        )
    out = pd.DataFrame(rows)
    # Arabic names from the AR workbook (sheet المدن): same rows, paired on the four count cells
    ws_ar = openpyxl.load_workbook(CITIES2010_AR, read_only=True, data_only=True)["المدن"]
    ar = {
        (r[2], r[3], r[5], r[6]): str(r[0]).strip()
        for r in ws_ar.iter_rows(values_only=True)
        if len(r) > 6
        and isinstance(r[0], str)
        and all(isinstance(v, int) for v in (r[2], r[3], r[5], r[6]))
    }
    out["city_2010_ar"] = [ar.get(k) for k in keys]
    if out.city_2010_ar.isna().any():
        raise ValueError(
            f"cities 2010: no Arabic row for {out[out.city_2010_ar.isna()].city_2010.tolist()}"
        )
    return out


def read_admin_ar() -> pd.DataFrame:
    """citypopulation.de admin list (S-073): EN, AR and Census 2022 governorate totals."""
    from screening.coverage import parse_admin

    return pd.DataFrame(
        [
            {
                "region": g.region,
                "name_en_s073": g.name_en,
                "name_ar": g.name_ar,
                "pop_s073": g.population,
            }
            for g in parse_admin(ADMIN_HTML)
        ]
    )


def load_crosswalk(path: Path = CROSSWALK) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) if path.exists() else {}


# --------------------------------------------------------------------------- crosswalks
def governorates_2022(cw: dict[str, Any] | None = None) -> pd.DataFrame:
    """The 150 relayed governorates with region, Arabic name, the S-073 figure (joined on the
    identical Census 2022 value, then checked by Arabic name), the OSM polygon id and 2010 total."""
    cw = cw if cw is not None else load_crosswalk()
    c22 = read_census2022()
    g = c22[c22.level == "governorate"][["code", "population"]].copy()
    adm = read_admin_ar()
    g = g.merge(adm, left_on="population", right_on="pop_s073", how="left", validate="1:1")
    if g.region.isna().any():
        raise ValueError(f"no S-073 row for {g[g.region.isna()].code.tolist()}")
    g["diff_s073_pct"] = 100 * (g.pop_s073 - g.population) / g.population
    # OSM polygons (149) by normalised Arabic name within the region; overrides in the crosswalk
    osm = json.loads(GOV_GEOJSON.read_text(encoding="utf-8"))
    polys = pd.DataFrame([f["properties"] for f in osm["features"]])
    polys["k"] = polys.name_ar.map(norm_ar)
    g["k"] = g.name_ar.map(norm_ar)
    over = cw.get("gov_osm", {}) or {}
    gid = []
    for _, r in g.iterrows():
        if r.code in over:
            gid.append(over[r.code])
            continue
        hit = polys[(polys.region == r.region) & (polys.k == r.k)]
        gid.append(hit.gov_id.iloc[0] if len(hit) == 1 else None)
    g["gov_id"] = gid
    # Census 2010 governorate (Arabic) within the region; overrides in the crosswalk
    g10 = read_gov2010()
    g10["k"] = g10.name_ar_2010.map(norm_ar)
    over10 = cw.get("gov_2010", {}) or {}
    p10, n10 = [], []
    for _, r in g.iterrows():
        key = over10.get(r.code, r.k)
        if key is None:
            p10.append(None), n10.append(None)
            continue
        hit = g10[(g10.region == r.region) & (g10.k == norm_ar(key))]
        if len(hit) == 0:  # seat governorates carry "(مقر الامارة)" etc.; try a prefix match
            hit = g10[(g10.region == r.region) & g10.k.str.startswith(norm_ar(key))]
        p10.append(int(hit.pop_2010.iloc[0]) if len(hit) == 1 else None)
        n10.append(hit.name_ar_2010.iloc[0] if len(hit) == 1 else None)
    g["pop_2010"], g["name_ar_2010"] = p10, n10
    g["growth_2010_2022"] = g.population / g.pop_2010
    g["growth_basis"] = np.where(g.pop_2010.notna(), "governorate", "region")
    ta9 = read_ta9().pivot(index="region", columns="year", values="population")
    reg_growth = (ta9[2022] / ta9[2010]).to_dict()
    g.loc[g.pop_2010.isna(), "growth_2010_2022"] = g.loc[g.pop_2010.isna(), "region"].map(
        reg_growth
    )
    return g.drop(columns=["k", "pop_s073"]).rename(columns={"population": "pop_2022"})


def region_check() -> pd.DataFrame:
    """Relayed region totals and the sum of relayed governorates vs primary TA1 and TA9."""
    c22 = read_census2022()
    reg = c22[c22.level == "region"].set_index("region").population
    govs = governorates_2022()
    gsum = govs.groupby("region").pop_2022.sum()
    ta1 = read_ta1().set_index("region").population
    ta9 = read_ta9()
    ta9 = ta9[ta9.year == 2022].set_index("region").population
    out = pd.DataFrame(
        {
            "relayed_region": reg,
            "relayed_gov_sum": gsum,
            "ta1_primary": ta1,
            "ta9_primary": ta9,
            "n_governorates": govs.groupby("region").size(),
        }
    ).loc[REGION_ORDER]
    out["match"] = (
        (out.relayed_region == out.ta1_primary)
        & (out.relayed_gov_sum == out.ta1_primary)
        & (out.ta9_primary == out.ta1_primary)
    )
    return out.reset_index(names="region")


# --------------------------------------------------------------------------- growth method
PLACE_RANK = {"city": 0, "town": 1, "village": 2, "hamlet": 3}


def _pick(cand: pd.DataFrame) -> str | None:
    if len(cand) > 1:
        cand = cand.assign(_r=cand.place.map(PLACE_RANK).fillna(9)).sort_values("_r")
        cand = cand[cand._r == cand._r.iloc[0]]
    return cand.settlement_id.iloc[0] if len(cand) == 1 else None


def _match_city(reg: pd.DataFrame, en: str, ar: str) -> tuple[str | None, str]:
    """Arabic name (normalised) within the region, then the English name (no fuzzy matching: a
    fuzzy pass produced a false match in testing, Al Qarah -> Al Qar`a')."""
    k_ar = norm_ar(ar)
    if k_ar and (sid := _pick(reg[reg.k_ar == k_ar])):
        return sid, "Arabic name within region"
    if sid := _pick(reg[reg.k == norm_en(en)]):
        return sid, "English name within region"
    return None, "unmatched"


def cities2010_matched(univ: pd.DataFrame, govs: pd.DataFrame, cw: dict[str, Any]) -> pd.DataFrame:
    """Census 2010 cities > 5k joined to settlements (normalised English name within the region;
    one unique node with place city/town preferred; overrides in the crosswalk) and grown at the
    settlement governorate's 2010→2022 ratio: pop_2022_est = pop_2010 × gov_2022 / gov_2010."""
    c10 = read_cities2010()
    over = cw.get("city_2010", {}) or {}
    univ = univ.copy()
    univ["k"] = univ.name_en.map(norm_en)
    univ["k_ar"] = univ.name_ar.map(lambda x: norm_ar(x) if isinstance(x, str) else "")
    growth = govs.dropna(subset=["gov_id"]).set_index("gov_id")
    out = []
    for _, r in c10.iterrows():
        sid = over.get(f"{r.city_2010}|{r.pop_2010}", over.get(r.city_2010))
        if sid == "none":
            sid = None
            how = "crosswalk: no settlement"
        elif sid is not None:
            how = "crosswalk"
        else:
            sid, how = _match_city(univ[univ.region == r.region], r.city_2010, r.city_2010_ar)
        rec = {**r.to_dict(), "settlement_id": sid, "match": how}
        if sid is not None:
            s = univ[univ.settlement_id == sid].iloc[0]
            rec["gov_id"] = s.gov_id
            gr = growth.loc[s.gov_id] if s.gov_id in growth.index else None
            rec["gov_code"] = None if gr is None else gr.code
            rec["growth"] = None if gr is None else gr.growth_2010_2022
            rec["pop_2022_est"] = (
                None
                if gr is None or pd.isna(gr.growth_2010_2022)
                else (round(r.pop_2010 * gr.growth_2010_2022))
            )
        out.append(rec)
    return pd.DataFrame(out)


# --------------------------------------------------------------------------- commands
@app.callback()
def _main() -> None:
    """GASTAT population tables (P1a addendum)."""


@app.command("tables")
def tables_cmd(seed: int = typer.Option(1, "--seed", min=0), run_dir: Path = RUN) -> None:
    """Write the tidy relayed/primary tables, the governorate crosswalk and the region check."""
    rng(seed)
    run_dir.mkdir(parents=True, exist_ok=True)
    c22 = read_census2022()
    c22.to_csv(run_dir / "census2022_relayed.csv", index=False)
    govs = governorates_2022()
    govs.to_csv(run_dir / "governorates_2022.csv", index=False)
    rc = region_check()
    rc.to_csv(run_dir / "region_check.csv", index=False)
    ksa = int(c22[c22.level == "ksa"].population.iloc[0])
    summary = {
        "governorates": int(len(govs)),
        "governorate_sum": int(govs.pop_2022.sum()),
        "ksa_relayed": ksa,
        "ksa_ta9_primary": read_ta9_total(),
        "cities": int((c22.level == "city").sum()),
        "regions_matching_primary": int(rc.match.sum()),
        "gov_s073_identical": int((govs.diff_s073_pct.abs() < 1e-9).sum()),
        "gov_with_osm_polygon": int(govs.gov_id.notna().sum()),
        "gov_with_2010_total": int(govs.pop_2010.notna().sum()),
        "national_2024_estimate": read_est2024(),
    }
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    write_meta(
        run_dir,
        seed,
        {"crosswalk": CROSSWALK.read_text(encoding="utf-8") if CROSSWALK.exists() else ""},
        {"step": "screening.gastat tables", "summary": summary},
    )
    typer.echo(json.dumps(summary))


# --------------------------------------------------------------------------- apply
def city_targets(cw: dict[str, Any] | None = None) -> pd.DataFrame:
    """Relayed Census 2022 cities -> pilot register row_key and settlement_id.

    Automatic join: the register row and the settlement carrying the identical figure (the
    aggregators relay the same census table). Crosswalk rows cover the rest; a city combined with
    another (Al-Hofuf + Al-Mubarraz) gives one target holding the sum."""
    cw = cw if cw is not None else load_crosswalk()
    over = cw.get("city_2022", {}) or {}
    c22 = read_census2022()
    cities = c22[c22.level == "city"].set_index("code").population
    reg = pd.read_parquet("cities/ksa/candidates-pilot.parquet")
    univ = pd.read_parquet(UNIVERSE)
    rows = []
    done: set[str] = set()
    for code, pop in cities.items():
        if code in done:
            continue
        o = over.get(code)
        if o:
            parts = [code] + ([o["combined_with"]] if o.get("combined_with") else [])
            done.update(parts)
            value = int(sum(int(cities[p]) for p in parts))
            row_key, sid = o.get("row_key"), o.get("settlement_id")
            how = "crosswalk" + (" (combined: " + " + ".join(parts) + ")" if len(parts) > 1 else "")
        else:
            value, parts = int(pop), [code]
            rk = reg[reg.population == value].row_key.tolist()
            si = univ[univ.population == value].settlement_id.tolist()
            if len(rk) != 1 or len(si) != 1:
                raise ValueError(f"city {code}: {len(rk)} register / {len(si)} settlement matches")
            row_key, sid, how = rk[0], si[0], "identical figure"
        rows.append(
            {
                "code": " + ".join(parts),
                "relayed": value,
                "row_key": row_key,
                "settlement_id": sid,
                "match": how,
            }
        )
    return pd.DataFrame(rows)


def _note(old: Any, old_src: Any, new: int) -> str:
    if old is None or (isinstance(old, float) and np.isnan(old)):
        return f"CP2 P1a addendum: Census 2022 relayed {new:,} ({S_RELAYED}); no earlier figure"
    pct = 100 * (new - float(old)) / float(old)
    return (
        f"CP2 P1a addendum: Census 2022 relayed {new:,} ({S_RELAYED}) replaces {int(old):,} "
        f"({old_src}; {pct:+.1f} %)"
    )


def apply_registers(targets: pd.DataFrame, regions: Path, dry_run: bool) -> list[dict[str, Any]]:
    """Write the relayed city figures into the pilot region registers (parquet + csv)."""
    import pyarrow.parquet as pq

    from screening.cp1_fixes.apply import _add_source, _records, _tags, write_register
    from screening.merge import row_key

    by_key = targets.dropna(subset=["row_key"]).set_index("row_key")
    log = []
    for path in sorted(regions.glob("pilot-*.parquet")):
        recs = _records(path)
        meta = {
            k: v for k, v in (pq.read_schema(path).metadata or {}).items() if b"pandas" not in k
        }
        changed = False
        for rec in recs:
            k = row_key(rec)
            if k not in by_key.index:
                continue
            t = by_key.loc[k]
            new = int(t.relayed)
            old, old_src = rec.get("population"), rec.get("pop_source")
            if (old_src == S_RELAYED and old == new) or old_src == S_CITY_PRIMARY:
                continue  # unchanged, or already on the primary figure (addendum 2 supersedes)
            note = _note(old, old_src, new)
            rec.update(
                population=float(new),
                pop_source=S_RELAYED,
                pop_year=2022,
                pop_type="official",
                pop_source_status="secondary",
                primary_to_find=PRIMARY_TO_FIND,
            )
            _add_source(rec, S_RELAYED)
            _tags(rec)
            rec["notes"] = f"{rec['notes']} | {note}" if rec.get("notes") else note
            changed = True
            log.append(
                {
                    "table": path.name,
                    "key": k,
                    "code": t.code,
                    "previous": old,
                    "previous_source": old_src,
                    "relayed": new,
                    "diff_pct": None if old is None else round(100 * (new - old) / old, 3),
                }
            )
        if changed and not dry_run:
            write_register(path, recs, meta)
    return log


def apply_universe(
    targets: pd.DataFrame, univ: pd.DataFrame, c10: pd.DataFrame
) -> tuple[pd.DataFrame, list[dict[str, Any]]]:
    """Relayed city figures into the settlement universe, the A-screen-035 corroboration value
    on grid rows matched to a Census 2010 city, then the P1a gate on `tag_10k`."""
    from screening.funnel import population_basis, tag_10k_rule

    u = univ.copy()
    log = []
    for _, t in targets.dropna(subset=["settlement_id"]).iterrows():
        i = u.index[u.settlement_id == t.settlement_id]
        if len(i) != 1:
            raise ValueError(f"settlement {t.settlement_id} not found")
        i = i[0]
        old, old_src, old_type = u.at[i, "population"], u.at[i, "pop_source"], u.at[i, "pop_type"]
        if (old_src == S_RELAYED and old == t.relayed) or old_src == MID_CITY_PRIMARY:
            continue
        u.loc[i, ["population", "pop_year", "pop_type", "pop_source", "pop_source_status"]] = [
            int(t.relayed),
            2022,
            "official",
            S_RELAYED,
            "secondary",
        ]
        u.at[i, "pop_method"] = "GASTAT Census 2022 relayed (DataPulse; CP2 P1a addendum)"
        u.at[i, "pop_licence"] = "GASTAT data use policy (attribution)"
        u.at[i, "pop_quality"] = "tabulated_secondary"
        log.append(
            {
                "table": UNIVERSE.name,
                "key": t.settlement_id,
                "code": t.code,
                "previous": old,
                "previous_source": old_src,
                "previous_type": old_type,
                "relayed": int(t.relayed),
                "diff_pct": round(100 * (t.relayed - old) / old, 3) if old else None,
            }
        )
    # A-screen-035: the grown Census 2010 figure as a corroboration value on grid-only rows
    u["pop_corroboration"] = None
    u["pop_corroboration_value"] = np.nan
    est = c10.dropna(subset=["settlement_id", "pop_2022_est"]).set_index("settlement_id")
    grid = u.pop_type == "grid"
    for i in u.index[grid & u.settlement_id.isin(est.index)]:
        u.at[i, "pop_corroboration"] = GROWTH_METHOD
        u.at[i, "pop_corroboration_value"] = float(
            est.loc[u.at[i, "settlement_id"], "pop_2022_est"]
        )
    pb = population_basis(u)
    u["population_basis"] = pb["population_basis"]
    u["tag_10k"] = tag_10k_rule(u)
    u["tag_5k"] = (u.population >= TAG_5K).fillna(False)
    gated = grid & (u.population >= TAG_10K) & ~u["tag_10k"]
    u["exclusion_reason"] = np.where(gated, GRID_UNCORROBORATED, None)
    return u, log


def conflicts_table(log: list[dict[str, Any]]) -> pd.DataFrame:
    df = pd.DataFrame(log)
    if df.empty:
        return df
    df["conflict"] = df.diff_pct.abs() > CONFLICT_PCT
    return df


@app.command("apply")
def apply_cmd(
    seed: int = typer.Option(1, "--seed", min=0),
    regions: Path = typer.Option(Path("cities/ksa/regions/archive/pilot"), "--regions"),
    universe: Path = typer.Option(UNIVERSE, "--universe"),
    run_dir: Path = RUN / "apply",
    dry_run: bool = typer.Option(False, "--dry-run"),
) -> None:
    """Relayed Census 2022 city figures into the pilot registers and the settlement universe
    (governorate figures already equal S-073: no register change); A-screen-035 corroboration;
    P1a gate on the universe's `tag_10k`. Conflicts > 2 % are listed in conflicts.csv."""
    rng(seed)
    cw = load_crosswalk()
    run_dir.mkdir(parents=True, exist_ok=True)
    targets = city_targets(cw)
    targets.to_csv(run_dir / "city_targets.csv", index=False)
    univ = pd.read_parquet(universe)
    govs = governorates_2022(cw)
    c10 = cities2010_matched(univ, govs, cw)
    reg_log = apply_registers(targets, regions, dry_run)
    new_univ, uni_log = apply_universe(targets, univ, c10)
    c10 = cities2010_matched(new_univ, govs, cw)  # re-read pop_type after the relayed update
    c10 = c10.merge(
        new_univ[["settlement_id", "name_en", "pop_type", "population"]],
        on="settlement_id",
        how="left",
    )
    c10["rel_diff"] = (c10.population - c10.pop_2022_est).abs() / c10.population
    c10["within_band"] = [
        bool(pd.notna(p) and pd.notna(e) and corroborates(p, e))
        for p, e in zip(c10.population, c10.pop_2022_est, strict=True)
    ]
    c10.to_csv(run_dir / "cities2010_growth.csv", index=False)
    conf = conflicts_table(reg_log + uni_log)
    conf.to_csv(run_dir / "conflicts.csv", index=False)
    if not dry_run:
        new_univ.to_parquet(universe, index=False)
    by_type = c10.dropna(subset=["pop_2022_est"]).groupby("pop_type")
    summary = {
        "city_targets": int(len(targets)),
        "register_rows_changed": int(len(reg_log)),
        "universe_rows_changed": int(len(uni_log)),
        "conflicts_gt_2pct": int(conf.conflict.sum()) if len(conf) else 0,
        "cities2010": int(len(c10)),
        "cities2010_matched": int(c10.settlement_id.notna().sum()),
        "cities2010_with_estimate_by_type": {k: int(len(v)) for k, v in by_type},
        "cities2010_within_band_by_type": {k: int(v.within_band.sum()) for k, v in by_type},
        "cities2010_median_abs_rel_diff_by_type": {
            k: round(float(v.rel_diff.median()), 4) for k, v in by_type
        },
        # back-test of the growth method itself against the official 2022 city figures
        "growth_method_backtest_official": {
            "n": int(len(off := c10[(c10.pop_type == "official") & c10.pop_2022_est.notna()])),
            "median_abs_pct_error": round(100 * float(off.rel_diff.median()), 1),
            "iqr_abs_pct_error": [
                round(100 * float(off.rel_diff.quantile(0.25)), 1),
                round(100 * float(off.rel_diff.quantile(0.75)), 1),
            ],
            "within_30pct": int(off.within_band.sum()),
        },
        "grid_rows_with_corroboration_value": int(new_univ.pop_corroboration.notna().sum()),
        "grid_corroborated": int((new_univ.population_basis == "grid_corroborated").sum()),
        "universe_by_basis": new_univ.population_basis.value_counts().to_dict(),
        "universe_tag_10k_before": int(univ.tag_10k.sum()),
        "universe_tag_10k_after": int(new_univ.tag_10k.sum()),
        "dry_run": dry_run,
    }
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    write_meta(
        run_dir,
        seed,
        {"crosswalk": CROSSWALK.read_text(encoding="utf-8"), "band": CORROBORATION_BAND},
        {
            "step": "screening.gastat apply",
            "assumptions": ["A-screen-031", "A-screen-032", "A-screen-033", "A-screen-035"],
            "summary": summary,
        },
    )
    typer.echo(json.dumps(summary, ensure_ascii=False))


# --------------------------------------------------------------------------- back-test
WORLDPOP = Path("data/ksa/grids/sau_ppp_2020_UNadj_constrained.tif")  # the grid fallback raster


def _ratio_stats(r: pd.Series) -> dict[str, Any]:
    r = r.dropna()
    err = (r - 1).abs()
    return {
        "n": int(len(r)),
        "median_ratio": round(float(r.median()), 4),
        "iqr_ratio": [round(float(r.quantile(0.25)), 4), round(float(r.quantile(0.75)), 4)],
        "median_abs_pct_error": round(100 * float(err.median()), 1),
        "within_30pct": int((err <= CORROBORATION_BAND).sum()),
    }


def governorate_grid_sums(govs: pd.DataFrame, raster: Path = WORLDPOP) -> pd.Series:
    """WorldPop 2020 (100 m, constrained, UN-adjusted) summed inside each governorate polygon."""
    import rasterio
    import rasterio.mask

    feats = {
        f["properties"]["gov_id"]: f["geometry"]
        for f in json.loads(GOV_GEOJSON.read_text(encoding="utf-8"))["features"]
    }
    out = {}
    with rasterio.open(raster) as src:
        nodata = src.nodata
        for gid in govs.gov_id.dropna():
            arr, _ = rasterio.mask.mask(src, [feats[gid]], crop=True, filled=True)
            a = arr[0].astype("float64")
            if nodata is not None:
                a[a == nodata] = 0.0
            out[gid] = float(np.nansum(np.clip(a, 0, None)))
    return pd.Series(out)


@app.command("backtest")
def backtest_cmd(
    seed: int = typer.Option(1, "--seed", min=0),
    run_dir: Path = RUN / "backtest",
    universe: Path = typer.Option(UNIVERSE, "--universe"),
) -> None:
    """Re-run the WorldPop back-test against the relayed Census 2022 totals: the grid summed inside
    each governorate polygon (149 of 150 have one) and the settlement grid allocation (A-r1a-004
    radius circle, nearest-settlement) for the 60 cities. Ratio = grid / census. Report only."""
    rng(seed)
    run_dir.mkdir(parents=True, exist_ok=True)
    govs = governorates_2022()
    sums = governorate_grid_sums(govs)
    govs["grid_sum"] = govs.gov_id.map(sums)
    govs["ratio"] = govs.grid_sum / govs.pop_2022
    govs[["code", "region", "gov_id", "pop_2022", "grid_sum", "ratio"]].to_csv(
        run_dir / "governorates.csv", index=False
    )
    univ = pd.read_parquet(universe)
    tg = city_targets().merge(
        univ[["settlement_id", "name_en", "place", "grid_population"]], on="settlement_id"
    )
    tg["ratio"] = tg.grid_population / tg.relayed
    tg.to_csv(run_dir / "cities.csv", index=False)
    summary = {
        "raster": str(WORLDPOP),
        "governorates": _ratio_stats(govs.ratio),
        "governorates_sum_grid": round(float(govs.grid_sum.sum())),
        "governorates_sum_census": int(govs.pop_2022[govs.grid_sum.notna()].sum()),
        "cities": _ratio_stats(tg.ratio),
        "earlier_backtest_164_rows": {"median_ratio": 0.637, "iqr_ratio": [0.332, 1.104]},
    }
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    write_meta(
        run_dir,
        seed,
        {"raster": str(WORLDPOP), "radius_assumption": "A-r1a-004"},
        {"step": "screening.gastat backtest", "report_only": True, "summary": summary},
    )
    typer.echo(json.dumps(summary))


# ------------------------------------------------------------------- primary TA1 (addendum 2)
GROWTH_GUARD = (0.5, 2.5)  # A-screen-038: 2022/2010 ratio a bridged or direct match must fall in
GRID_GUARD = 0.05  # A-screen-038: an unbridged name match needs grid_population / census ≥ this
TIER_ORDER = ["crosswalk", "relayed figure", "identical figure", "2010 bridge (name)",
              "universe (name)", "2010 bridge (skeleton)"]  # fmt: skip


def read_primary(path: Path) -> pd.DataFrame:
    """A TA1 Excel export: name, Total, Saudi, Non-Saudi; checks the parts and the Total row."""
    d = pd.read_excel(path)
    d.columns = ["name", "total", "saudi", "non_saudi"]
    d["name"] = d.name.astype(str).str.strip()
    tot = d[d.name == "Total"]
    d = d[d.name != "Total"].reset_index(drop=True)
    for c in ("total", "saudi", "non_saudi"):
        d[c] = d[c].map(_int)
        if len(tot) != 1 or int(d[c].sum()) != int(_int(tot[c].iloc[0]) or 0):
            raise ValueError(f"{path.name}: column {c} does not sum to its Total row")
    if not (d.saudi + d.non_saudi == d.total).all():
        raise ValueError(f"{path.name}: Saudi + non-Saudi != Total")
    return d


def read_gov_primary(path: Path = GOV_PRIMARY) -> pd.DataFrame:
    return read_primary(path)


def read_city_primary(path: Path = CITY_PRIMARY) -> tuple[pd.DataFrame, int]:
    """The cities of 5,000 or more and the "Other (Less than 5000 inhabitants)" total."""
    d = read_primary(path)
    other = d.name.str.startswith(OTHER_PREFIX)
    if other.sum() != 1:
        raise ValueError("city table: expected one 'Other' row")
    return d[~other].reset_index(drop=True), int(d[other].total.iloc[0])


def key_light(s: Any) -> str:
    """Name key: diacritics, apostrophes, spaces and articles removed; a glued leading "Al" dropped
    (the TA1 export writes "Alkhubar", "Albahah")."""
    s = unicodedata.normalize("NFKD", str(s))
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    s = re.sub(r"[`'’ʿʾ]", "", s).replace("-", " ")
    s = re.sub(r"[^a-z ]", " ", s)
    stop = {"al", "ad", "ar", "as", "ash", "az", "at", "an", "adh", "el", "governorate", "of"}
    s = "".join(w for w in s.split() if w not in stop)
    return s[2:] if s.startswith("al") and len(s) > 4 else s


def key_skeleton(s: Any) -> str:
    """Consonant skeleton of `key_light` (transliteration variants: Bariduh/Buraydah -> brd)."""
    s = key_light(s)
    for a, b in [("kh", "k"), ("gh", "g"), ("q", "k"), ("dh", "d"), ("th", "t"), ("sh", "s"),
                 ("ph", "f"), ("z", "d")]:  # fmt: skip
        s = s.replace(a, b)
    s = re.sub(r"h$", "", s)
    s = re.sub(r"[aeiouyw]", "", s)
    return re.sub(r"(.)\1+", r"\1", s)


def primary_vs_relayed() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Governorate by governorate and city by city: primary TA1 vs the relayed DataPulse file.
    Join on the English name key, then on the identical total for names that differ."""
    c22 = read_census2022()
    out = []
    for level, prim in (("governorate", read_gov_primary()), ("city", read_city_primary()[0])):
        rel = c22[c22.level == level][["code", "population", "saudi", "non_saudi"]].copy()
        rel["k"] = rel.code.map(key_light)
        prim = prim.assign(k=prim.name.map(key_light))
        m = prim.merge(rel, on="k", how="left", suffixes=("", "_rel"))
        m["join"] = np.where(m.code.notna(), "name", None)
        miss = m.code.isna()
        by_val = rel.set_index("population")
        for i in m.index[miss]:
            if m.at[i, "total"] in by_val.index:
                hit = by_val.loc[m.at[i, "total"]]
                cols = ["code", "population", "saudi_rel", "non_saudi_rel", "join"]
                vals = [hit.code, m.at[i, "total"], hit.saudi, hit.non_saudi, "identical total"]
                m.loc[i, cols] = vals
        m["level"] = level
        unmatched_rel = sorted(set(rel.code) - set(m.code.dropna()))
        m.attrs["unmatched_relayed"] = unmatched_rel
        out.append(m)
    res = []
    for m in out:
        m = m.rename(
            columns={"population": "total_rel", "code": "relayed_name", "name": "primary_name"}
        )
        for c in ("total", "saudi", "non_saudi"):
            m[f"diff_{c}"] = m[c] - m[f"{c}_rel"]
        m["diff_pct"] = 100 * m.diff_total / m.total
        res.append(m.drop(columns=["k"]))
    return res[0], res[1]


def primary_city_targets(
    univ: pd.DataFrame, c10: pd.DataFrame, cw: dict[str, Any] | None = None
) -> pd.DataFrame:
    """The 271 primary cities -> settlement_id, by tier (TIER_ORDER); stricter tiers win a
    settlement claimed twice. No region in the export, so a name must be unique nationally, or be
    bridged through the Census 2010 cities list (which carries the region and the Arabic name),
    with the 2022/2010 ratio inside GROWTH_GUARD (A-screen-038)."""
    cw = cw if cw is not None else load_crosswalk()
    over = cw.get("city_primary", {}) or {}
    cities, _ = read_city_primary()
    rel = city_targets(cw)
    rel_by_val = {int(v): sid for v, sid in zip(rel.relayed, rel.settlement_id, strict=True)}
    u = univ.assign(
        k1=univ.name_en.map(lambda x: key_light(x) if isinstance(x, str) else ""),
        k2=univ.name_en.map(lambda x: key_skeleton(x) if isinstance(x, str) else ""),
    )
    b = c10.dropna(subset=["settlement_id"]).assign(
        k1=lambda x: x.city_2010.map(key_light), k2=lambda x: x.city_2010.map(key_skeleton)
    )
    c10_all = c10.assign(k1=c10.city_2010.map(key_light), k2=c10.city_2010.map(key_skeleton))
    pop2010 = b.groupby("settlement_id").pop_2010.max()
    tab = univ[univ.pop_type.isin(["official", "derived"])]
    grid = univ.set_index("settlement_id").grid_population
    lo, hi = GROWTH_GUARD

    def guard(sid: str, total: int) -> bool:
        p10 = pop2010.get(sid)
        if p10 is not None:
            return lo <= total / p10 <= hi
        g = grid.get(sid)
        return g is not None and pd.notna(g) and g / total >= GRID_GUARD

    rows = []
    for _, r in cities.iterrows():
        rec: dict[str, Any] = {"city": r["name"], "total": int(r.total), "saudi": int(r.saudi),
                               "non_saudi": int(r.non_saudi), "settlement_id": None,
                               "combined_with": None, "tier": None, "reason": None}  # fmt: skip
        k1, k2 = key_light(r["name"]), key_skeleton(r["name"])
        o = over.get(r["name"])
        if o is not None:
            if o == "none":
                rec["reason"] = "crosswalk: no settlement (see screening/gastat_crosswalk.yaml)"
            else:
                o = o if isinstance(o, dict) else {"settlement_id": o}
                rec.update(settlement_id=o["settlement_id"], tier="crosswalk",
                           combined_with=o.get("combined_with"))  # fmt: skip
            rows.append(rec)
            continue
        if int(r.total) in rel_by_val:
            rec.update(settlement_id=rel_by_val[int(r.total)], tier="relayed figure")
            rows.append(rec)
            continue
        same = tab[tab.population == int(r.total)]
        if (
            len(same) == 1 and int((cities.total == r.total).sum()) == 1
        ):  # citypopulation.de relays the same census table (addendum 1)
            rec.update(settlement_id=same.settlement_id.iloc[0], tier="identical figure")
            rows.append(rec)
            continue
        for tier, frame, key in (
            ("2010 bridge (name)", b, ("k1", k1)),
            ("universe (name)", u, ("k1", k1)),
            ("2010 bridge (skeleton)", b, ("k2", k2)),
        ):
            cand = frame[frame[key[0]] == key[1]] if key[1] else frame.iloc[0:0]
            if tier.startswith("2010"):
                if len(c10_all[c10_all[key[0]] == key[1]]) != 1 or len(cand) != 1:
                    continue  # a 2010 name must be unique in the 2010 list and matched
                sid = cand.settlement_id.iloc[0]
            else:
                sid = _pick(cand) if len(cand) else None
            if sid is None:
                continue
            if not guard(sid, int(r.total)):
                rec["reason"] = f"{tier}: {sid} fails the plausibility guard (A-screen-038)"
                continue
            rec.update(settlement_id=sid, tier=tier, reason=None)
            break
        if rec["settlement_id"] is None and rec["reason"] is None:
            n1, n2 = int((u.k1 == k1).sum()), int((u.k2 == k2).sum())
            rec["reason"] = (
                "no OSM settlement with this name (name variant, facility, camp or merged place)"
                if n1 == 0 and n2 == 0
                else f"ambiguous name: {n1} exact / {n2} spelling-variant candidates and no region "
                "in the export to choose between them"
            )
        rows.append(rec)
    t = pd.DataFrame(rows)
    t["tier_rank"] = t.tier.map({k: i for i, k in enumerate(TIER_ORDER)})
    # a settlement claimed by more than one city (not a declared combination): the strictest tier
    # keeps it; equal tiers -> none keeps it
    for sid, g in t.dropna(subset=["settlement_id"]).groupby("settlement_id"):
        if len(g) == 1 or g.combined_with.notna().all():
            continue
        best = g.tier_rank.min()
        keep = g.index[g.tier_rank == best]
        drop = g.index.difference(keep) if len(keep) == 1 else g.index
        names = ", ".join(g.city)
        t.loc[drop, "reason"] = f"settlement {sid} also claimed by: {names}"
        t.loc[drop, ["settlement_id", "tier"]] = None
    t = t.merge(
        univ[["settlement_id", "name_en", "name_ar", "region", "gov_id", "place", "pop_type",
              "population", "grid_population", "pilot_row_key"]].rename(
            columns={"population": "population_before", "pop_type": "pop_type_before"}),
        on="settlement_id", how="left",
    )  # fmt: skip
    t["pop_2010"] = t.settlement_id.map(pop2010)
    t["ratio_2022_2010"] = t.total / t.pop_2010
    return t.drop(columns=["tier_rank"])


CONTROL_FLAG = "control_total_flag"  # A-screen-037 (new optional universe column)
RADIUS_KM = {"city": 10.0, "town": 3.0, "village": 1.5, "hamlet": 1.0}  # A-r1a-004
RADIUS_OTHER_KM = 1.5  # A-r1a-004 "other"


def _haversine_km(lat1: Any, lon1: Any, lat2: Any, lon2: Any) -> Any:
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dlat, dlon = p2 - p1, np.radians(lon2) - np.radians(lon1)
    a = np.sin(dlat / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dlon / 2) ** 2
    return 2 * 6371.0088 * np.arcsin(np.sqrt(a))


def primary_values(t: pd.DataFrame) -> pd.DataFrame:
    """One value of record per matched settlement (a declared combination holds the sum)."""
    m = t.dropna(subset=["settlement_id"])
    return (
        m.groupby("settlement_id")
        .agg(primary=("total", "sum"), cities=("city", lambda x: " + ".join(x)))
        .reset_index()
    )


def apply_primary_universe(
    univ: pd.DataFrame, vals: pd.DataFrame
) -> tuple[pd.DataFrame, list[dict[str, Any]]]:
    """Primary figure on every matched settlement: official, verified, no corroboration needed."""
    from screening.funnel import population_basis, tag_10k_rule

    u = univ.copy()
    log = []
    for v in vals.itertuples():
        i = u.index[u.settlement_id == v.settlement_id][0]
        old, old_src = u.at[i, "population"], u.at[i, "pop_source"]
        log.append(
            {
                "table": UNIVERSE.name,
                "key": v.settlement_id,
                "code": v.cities,
                "previous": old,
                "previous_source": old_src,
                "previous_type": u.at[i, "pop_type"],
                "primary": int(v.primary),
                "diff_pct": round(100 * (v.primary - old) / old, 3) if old else None,
            }  # fmt: skip
        )
        u.loc[i, ["population", "pop_year", "pop_type", "pop_source", "pop_source_status"]] = [
            int(v.primary), 2022, "official", MID_CITY_PRIMARY, "verified"]  # fmt: skip
        u.at[i, "pop_method"] = "GASTAT Census 2022 TA1 primary export, city ≥ 5,000 (CP2 P1a)"
        u.at[i, "pop_licence"] = "GASTAT data use policy (attribution)"
        u.at[i, "pop_quality"] = "tabulated_primary"
        u.at[i, "pop_corroboration"] = None
        u.at[i, "pop_corroboration_value"] = np.nan
    pb = population_basis(u)
    u["population_basis"] = pb["population_basis"]
    u["tag_10k"] = tag_10k_rule(u)
    u["tag_5k"] = (u.population >= TAG_5K).fillna(False)
    gated = (u.pop_type == "grid") & (u.population >= TAG_10K) & ~u["tag_10k"]
    u["exclusion_reason"] = np.where(gated, GRID_UNCORROBORATED, None)
    return u, log


def apply_primary_registers(
    vals: pd.DataFrame, univ: pd.DataFrame, regions: Path, dry_run: bool
) -> list[dict[str, Any]]:
    """Primary figure on the pilot register rows of the matched settlements (`pilot_row_key`)."""
    import pyarrow.parquet as pq

    from screening.cp1_fixes.apply import _add_source, _records, _tags, write_register
    from screening.merge import row_key

    keys = univ.set_index("settlement_id").pilot_row_key
    by_key = {
        keys[v.settlement_id]: v
        for v in vals.itertuples()
        if isinstance(keys.get(v.settlement_id), str)
    }
    log = []
    for path in sorted(regions.glob("pilot-*.parquet")):
        recs = _records(path)
        meta = {
            k: v for k, v in (pq.read_schema(path).metadata or {}).items() if b"pandas" not in k
        }
        changed = False
        for rec in recs:
            k = row_key(rec)
            if k not in by_key:
                continue
            v = by_key[k]
            new, old, old_src = int(v.primary), rec.get("population"), rec.get("pop_source")
            if old_src == S_CITY_PRIMARY and old == new:
                continue
            pct = None if old is None else 100 * (new - old) / old
            note = (
                f"CP2 P1a addendum 2: GASTAT Census 2022 TA1 primary {new:,} ({S_CITY_PRIMARY}; "
                f"{v.cities}) replaces {'none' if old is None else f'{int(old):,}'} ({old_src}"
                + ("" if pct is None else f"; {pct:+.1f} %")
                + ")"
            )
            rec.update(population=float(new), pop_source=S_CITY_PRIMARY, pop_year=2022,
                       pop_type="official", pop_source_status="verified",
                       primary_to_find=None)  # fmt: skip
            _add_source(rec, S_CITY_PRIMARY)
            _tags(rec)
            rec["notes"] = f"{rec['notes']} | {note}" if rec.get("notes") else note
            changed = True
            log.append({"table": path.name, "key": k, "code": v.cities, "previous": old,
                        "previous_source": old_src, "primary": new,
                        "diff_pct": None if pct is None else round(pct, 3)})  # fmt: skip
        if changed and not dry_run:
            write_register(path, recs, meta)
    return log


def control_total(
    u: pd.DataFrame, vals: pd.DataFrame, other: int
) -> tuple[pd.DataFrame, pd.Series, dict[str, Any]]:
    """A-screen-037. Grid (WorldPop-filled) population of settlements not matched to a primary
    city, per region, beside the region's primary residual (TA1 region total − matched cities).
    Rows in a region above its residual are flagged: inside a matched city's allocation radius
    (A-r1a-004) = possible double counting with the city extent; otherwise grid over-count or
    boundary mismatch. The flag is reporting only; no population changes."""
    ta1 = read_ta1().set_index("region").population
    matched = u.settlement_id.isin(vals.settlement_id)
    mc = u[matched].merge(vals, on="settlement_id")
    grid = u[~matched & (u.pop_type == "grid")]
    tab = u[~matched & u.pop_type.isin(["official", "derived"])]
    reg = (
        pd.DataFrame(
            {
                "ta1_total": ta1,
                "matched_cities": mc.groupby("region").primary.sum(),
                "n_matched": mc.groupby("region").size(),
                "grid_unmatched": grid.groupby("region").population.sum(),
                "n_grid_unmatched": grid.groupby("region").size(),
                "tabulated_unmatched": tab.groupby("region").population.sum(),
            }
        )
        .loc[REGION_ORDER]
        .fillna(0)
    )
    reg["residual"] = reg.ta1_total - reg.matched_cities
    reg["grid_minus_residual"] = reg.grid_unmatched - reg.residual
    reg["exceeds"] = reg.grid_minus_residual > 0
    flag = pd.Series(None, index=u.index, dtype=object)
    cl = mc[["lat", "lon", "place"]].to_numpy()
    for i in grid.index[grid.region.isin(reg.index[reg.exceeds])]:
        if not (u.at[i, "population"] > 0):
            continue
        d = _haversine_km(u.at[i, "lat"], u.at[i, "lon"], cl[:, 0].astype(float),
                          cl[:, 1].astype(float))  # fmt: skip
        rad = np.array([RADIUS_KM.get(p, RADIUS_OTHER_KM) for p in cl[:, 2]])
        flag[i] = (
            "inside a matched city's A-r1a-004 radius: possible double counting with the city "
            "extent"
            if (d <= rad).any()
            else "grid over-count or boundary mismatch (region grid sum exceeds the residual)"
        )
    summary = {
        "other_lt_5000_national": other,
        "grid_unmatched_national": round(float(reg.grid_unmatched.sum())),
        "grid_exceeds_other": bool(reg.grid_unmatched.sum() > other),
        "residual_national": int(reg.residual.sum()),
        "unmatched_primary_cities_total": int(reg.residual.sum()) - other,
        "regions_exceeding_residual": [str(r) for r in reg.index[reg.exceeds]],
        "rows_flagged": int(flag.notna().sum()),
        "rows_flagged_by_reason": flag.value_counts().to_dict(),
    }
    return reg.reset_index(names="region"), flag, summary


@app.command("primary")
def primary_cmd(
    seed: int = typer.Option(1, "--seed", min=0),
    regions: Path = typer.Option(Path("cities/ksa/regions/archive/pilot"), "--regions"),
    universe: Path = typer.Option(UNIVERSE, "--universe"),
    run_dir: Path = RUN / "primary",
    dry_run: bool = typer.Option(False, "--dry-run"),
) -> None:
    """Addendum 2: primary TA1 vs relayed cross-check; the 271 primary cities into the settlement
    universe and the pilot registers (official, verified); the control total (A-screen-037); the
    WorldPop back-test against the matched primary cities (report only). Run after `apply`."""
    rng(seed)
    cw = load_crosswalk()
    run_dir.mkdir(parents=True, exist_ok=True)
    gx, cx = primary_vs_relayed()
    gx.to_csv(run_dir / "crosscheck_governorates.csv", index=False)
    cx.to_csv(run_dir / "crosscheck_cities.csv", index=False)
    univ = pd.read_parquet(universe)
    c10 = cities2010_matched(univ, governorates_2022(cw), cw)
    t = primary_city_targets(univ, c10, cw)
    t.to_csv(run_dir / "city_matches.csv", index=False)
    vals = primary_values(t)
    reg_log = apply_primary_registers(vals, univ, regions, dry_run)
    new_univ, uni_log = apply_primary_universe(univ, vals)
    _, other = read_city_primary()
    ct, flag, ct_sum = control_total(new_univ, vals, other)
    new_univ[CONTROL_FLAG] = flag
    ct.to_csv(run_dir / "control_total.csv", index=False)
    cols = ["settlement_id", "name_en", "region", "place", "population", CONTROL_FLAG]
    new_univ.loc[flag.notna(), cols].to_csv(run_dir / "control_flags.csv", index=False)
    conf = pd.DataFrame(reg_log + uni_log)
    if len(conf):
        conf["conflict"] = conf.diff_pct.abs() > CONFLICT_PCT
    conf.to_csv(run_dir / "changes.csv", index=False)
    # back-test: WorldPop allocation of the matched settlement vs the primary figure
    bt = vals.merge(univ[["settlement_id", "name_en", "region", "place", "grid_population"]],
                    on="settlement_id")  # fmt: skip
    bt["ratio"] = bt.grid_population / bt.primary
    bt.to_csv(run_dir / "backtest_cities.csv", index=False)
    if not dry_run:
        new_univ.to_parquet(universe, index=False)
    tiers = t.tier.value_counts().to_dict()
    summary = {
        "governorates_primary": int(len(gx)),
        "governorates_identical_to_relayed": int(
            ((gx.diff_total == 0) & (gx.diff_saudi == 0) & (gx.diff_non_saudi == 0)).sum()
        ),
        "governorate_joins": gx["join"].value_counts().to_dict(),
        "cities_primary": int(len(cx)),
        "cities_in_relayed": int(cx.relayed_name.notna().sum()),
        "relayed_cities_identical": int(
            ((cx.diff_total == 0) & (cx.diff_saudi == 0) & (cx.diff_non_saudi == 0)).sum()
        ),
        "city_joins": cx["join"].value_counts().to_dict(),
        "cities_matched": int(t.settlement_id.notna().sum()),
        "settlements_matched": int(len(vals)),
        "cities_unmatched": int(t.settlement_id.isna().sum()),
        "matched_by_tier": {k: int(v) for k, v in tiers.items()},
        "unmatched_by_reason": t[t.settlement_id.isna()]
        .reason.str.split(":")
        .str[0]
        .str.slice(0, 60)
        .value_counts()
        .to_dict(),
        "matched_population": int(vals.primary.sum()),
        "register_rows_changed": int(len(reg_log)),
        "universe_rows_changed": int(len(uni_log)),
        "changes_gt_2pct": int(conf.conflict.sum()) if len(conf) else 0,
        "control_total": ct_sum,
        "backtest_cities": _ratio_stats(bt.ratio),
        "backtest_earlier": {"relayed_59": 0.4803, "tabulated_164": 0.637},
        "universe_by_basis": new_univ.population_basis.value_counts().to_dict(),
        "universe_tag_10k_before": int(univ.tag_10k.sum()),
        "universe_tag_10k_after": int(new_univ.tag_10k.sum()),
        "dry_run": dry_run,
    }
    (run_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    write_meta(
        run_dir,
        seed,
        {
            "crosswalk": CROSSWALK.read_text(encoding="utf-8"),
            "growth_guard": GROWTH_GUARD,
            "grid_guard": GRID_GUARD,
        },  # fmt: skip
        {
            "step": "screening.gastat primary",
            "assumptions": ["A-screen-031", "A-screen-037", "A-screen-038", "A-r1a-004"],
            "summary": summary,
        },  # fmt: skip
    )
    typer.echo(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    app()
