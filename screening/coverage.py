"""Coverage audit `docs/coverage.md` (rule 2): one row per governorate, reconciled to the count.

CP2_PREP item 1 addendum 2 (31 Oct 2026): populations and the count come from the primary GASTAT
Census 2022 TA1 governorate export
(`data/ksa/tables/gastat/census2022_TA1_governorate_primary.xlsx`, S-cp2-gastat-007;
`screening.gastat`), checked row by row against the DataPulse relayed table
(S-cp2-gastat-001, joined by code) and the S-073 figures (all identical), so S-073 still supplies
the English/Arabic names and the order. Region totals are checked against the primary TA1/TA9
region tables (S-cp2-gastat-002/S-cp2-gastat-003).

Governorate universe: the 13 regions and 150 governorate rows of the Census 2022 administrative
list republished by citypopulation.de (S-073; archived HTML, manifest row
`citypop-admin-census2022`), plus the rows `docs/gastat-regions.md` flags as `conflict` (Abanat,
Al-Bayda). GASTAT's own list was unreachable on 2026-10-30 (S-072, S-090): the count reconciles
to the secondary 150 and every difference is explained row by row.

uv run python -m screening.coverage --register cities/ksa/candidates-pilot.parquet \
    --admin-html data/ksa/pilot-qassim/raw/citypop_admin.html --out docs/coverage.md
"""

from __future__ import annotations

import html
import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd
import typer

app = typer.Typer(add_completion=False, help="Build the coverage table docs/coverage.md.")

# citypopulation.de region name -> RegionRow.region slug (names as printed on S-073)
REGION_SLUG = {
    "Al-Bāḥah": "al_baha",
    "Al-Ḥudūd ash-Shamāliyah": "northern_borders",
    "Al-Jawf": "al_jouf",
    "Al-Madīnah al-Munuwarah": "madinah",
    "Al-Qaṣīm": "qassim",
    "Ar-Riyāḍ": "riyadh",
    "Ash-Sharqiyah": "eastern",
    "'Asīr": "asir",
    "Ḥā'il": "hail",
    "Jāzān": "jazan",
    "Makkah al-Mukarramah": "makkah",
    "Najrān": "najran",
    "Tabūk": "tabuk",
}
# Rows docs/gastat-regions.md adds from the Arabic Wikipedia list (S-075), status `conflict`.
CONFLICT_ROWS = [
    ("qassim", "Abanat", "أبانات"),
    ("eastern", "Al-Bayḍā", "البيضاء"),
]
# Register governorate names that differ from S-073 in spelling only (checked by hand, 30 Oct 2026)
ALIASES = {("jazan", "جيزان"): "جازان"}


@dataclass
class Gov:
    region: str
    region_name: str
    region_ar: str
    name_en: str
    name_ar: str
    population: int | None
    conflict: bool = False
    rows: list[dict] = field(default_factory=list)
    code: str | None = None  # relayed Census 2022 governorate code (S-cp2-gastat-001)


def norm_ar(s: str) -> str:
    s = re.sub(r"^محافظة\s+", "", str(s).strip())
    s = re.sub("[إأآٱ]", "ا", s).replace("ة", "ه").replace("ى", "ي")
    s = re.sub(r"[ً-ْـ]", "", s)  # harakat, tatweel
    return re.sub(r"\s+", "", s)


def norm_en(s: str) -> str:
    s = unicodedata.normalize("NFKD", str(s))
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    s = re.sub(r"[^a-z ]", "", s.replace("-", " "))
    s = re.sub(r"\b(al|ad|ar|as|ash|az|at|an|adh|aṭ)\b", "", s)
    return re.sub(r"\s+", "", s)


def parse_admin(path: Path) -> list[Gov]:
    """Region and governorate rows (EN, AR, Census 2022) from the archived S-073 page."""
    text = path.read_text(encoding="utf-8")
    trs = re.findall(
        r'<tr[^>]*itemtype="http://schema.org/AdministrativeArea"[^>]*>(.*?)</tr>', text, re.S
    )
    govs: list[Gov] = []
    region = region_ar = ""
    for tr in trs:
        cells = [
            html.unescape(re.sub(r"<[^>]+>", " ", c)).strip()
            for c in re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)
        ]
        cells = [re.sub(r"\s+", " ", c) for c in cells]
        name = re.sub(r"\s*\[.*\]$", "", cells[0]).strip()
        status, ar, pop = cells[1], cells[2], cells[3]
        if status == "Region":
            region, region_ar = name, ar
            continue
        if status != "Governorate":
            raise ValueError(f"unexpected status {status!r} for {name}")
        govs.append(
            Gov(
                REGION_SLUG[region],
                region,
                region_ar,
                name,
                ar,
                int(pop.replace(",", "")) if pop else None,
            )
        )
    return govs


def build(register: pd.DataFrame, admin: Path) -> tuple[list[Gov], list[dict]]:
    govs = parse_admin(admin)
    for slug, en, ar in CONFLICT_ROWS:
        ref = next(g for g in govs if g.region == slug)
        govs.append(Gov(slug, ref.region_name, ref.region_ar, en, ar, None, conflict=True))
    by_ar = {(g.region, norm_ar(g.name_ar)): g for g in govs}
    by_en = {(g.region, norm_en(g.name_en)): g for g in govs}
    unmatched = []
    for rec in register.to_dict(orient="records"):
        ar = ALIASES.get((rec["region"], norm_ar(rec["governorate_ar"])), rec["governorate_ar"])
        g = by_ar.get((rec["region"], norm_ar(ar))) or by_en.get(
            (rec["region"], norm_en(rec["governorate"]))
        )
        if g is None:
            unmatched.append(rec)
        else:
            g.rows.append(rec)
    return govs, unmatched


# Governorates with no register row, and conflict rows: the reason, from the pilot status blocks.
NO_ROW_REASON = {
    (
        "al_baha",
        "Al-Qarā",
    ): "not yet swept: the Al-Baha pilot withheld the centre row (no coordinate "
    "source; RegionRow requires lat/lon); docs/status/pilot-al_baha.md",
    (
        "madinah",
        "Wādī al-Fara'",
    ): "not yet swept: the centre is not named in the sources the Madinah "
    "pilot reached; docs/status/pilot-madinah.md (Needs judgement, item 3)",
    ("makkah", "Al-'Arḍiyāt"): "not yet swept: the Makkah pilot withheld the centre row (no "
    "coordinates); docs/status/pilot-makkah.md",
    (
        "qassim",
        "Abanat",
    ): "conflict row: listed only by the Arabic Wikipedia table (S-075 page), not "
    "by S-073; the Qassim pilot filed an excluded Abanat row under An-Nabhāniyah (OSM boundary)",
    ("eastern", "Al-Bayḍā"): "conflict row: Arabic Wikipedia and Saudipedia list 13 Eastern "
    "governorates, S-073 lists 12; the Eastern pilot's row is excluded (centre not located)",
}


def _cell(x: object) -> str:
    # pilot notes say "Needs Opus judgement"; no model names in documents (CLAUDE.md)
    text = re.sub(r"\bOpus\s+", "", str(x))
    return text.replace("|", "\\|").replace("\n", " ")


def _short(text: str, n: int = 140) -> str:
    text = " ".join(str(text).split())
    return text if len(text) <= n else text[: n - 1].rstrip() + "…"


def row_status(g: Gov) -> tuple[str, str]:
    if g.conflict or not g.rows:
        reason = NO_ROW_REASON.get((g.region, g.name_en), "not yet swept: no register row")
        if g.conflict and g.rows:
            reason += "; register rows: " + ", ".join(r["name_en"] for r in g.rows)
        return ("conflict" if g.conflict else "not yet swept"), reason
    screened = [r for r in g.rows if r["screened"]]
    centres = [r["name_en"] for r in g.rows if r["is_governorate_centre"]]
    notes = [f"centre row: {', '.join(centres)}" if centres else "no centre row"]
    nopop = sum(r["population"] is None or pd.isna(r["population"]) for r in g.rows)
    if nopop:
        notes.append(f"{nopop} row(s) without a sourced population")
    if screened:
        return "screened", "; ".join(notes)
    first = g.rows[0].get("exclusion_reason") or ""
    return f"excluded: {_short(first, 120)}", "; ".join(notes)


def render(
    govs: list[Gov],
    unmatched: list[dict],
    withheld: dict,
    stages: pd.DataFrame | None,
    short_keys: set[str],
    primary: dict[str, tuple[int, int]] | None = None,
) -> str:
    primary = primary or {}
    stage_of = (
        {} if stages is None else dict(zip(stages["row_key"], stages["funnel_stage"], strict=True))
    )
    lines = [
        "> **Document version:** docs/coverage.md v0.5 | 31 Oct 2026 | Author: screening-analyst "
        "(PILOT_MERGE); CP2_PREP item 1 addenda (GASTAT primary TA1 count and totals); generated "
        "by "
        "`screening.coverage` | Status: draft (pilot; R2 fills every governorate)",
        "",
        "# Coverage audit (pilot draft)",
        "",
        "Label: **pilot, proposed criteria pending CP1; screening input, not a forecast.** Rule 2: "
        "every region and every governorate appears below, as screened (with the result), "
        "excluded (with the reason) or not yet swept. Generated by `uv run python -m "
        "screening.coverage` from `cities/ksa/candidates-pilot.parquet`, the funnel run "
        "`runs/screening-pilot/` (seed 1), the primary GASTAT Census 2022 TA1 governorate table "
        "(S-cp2-gastat-007) and the archived Census 2022 administrative list (S-073, names).",
        "",
        "**Governorate universe and count.** `governorates_gastat: 150 (primary TA1 export, 31 "
        "Oct 2026)`. The 150 governorates and their Census 2022 totals are the GASTAT TA1 "
        "governorate table exported by Tariq from the GASTAT Tableau dashboard on 31 Oct 2026 "
        "(S-cp2-gastat-007; file `data/ksa/tables/gastat/census2022_TA1_governorate_primary.xlsx`, "
        "manifest row `gastat-census2022-ta1-governorate-xlsx`; `pop_source_status: verified`). "
        "The rows sum to 32,175,224, the primary national total (TA9, S-cp2-gastat-003), and every "
        "region's governorate sum equals the primary TA1 and TA9 region total (table below). All "
        "150 figures are identical to the DataPulse relayed table (S-cp2-gastat-001, now a "
        "cross-check only; C-gastat-001) and to the citypopulation.de admin list (S-073), which "
        "supplies the English and Arabic names and the order; the two `conflict` rows flagged in "
        "`docs/gastat-regions.md` are kept with their reasons.",
        "",
        "Columns: rows = rows in the pilot register matched to the governorate; ≥50k = rows "
        "tagged `threshold_50k` (settlement population ≥ 50,000, A-screen-014); sample = "
        "`pilot_sample` rows; long = rows on the long list at 10,000 (A-screen-001), excluding "
        "the served bucket; short = rows on the short list (A-screen-006). Status = the "
        "region sweep's `screened` flag; governorate centres enter the long list regardless of "
        "it (rule 2), so an excluded centre can still show long = 1 (its exclusion note is "
        "carried as a data flag in `docs/screening-pilot.md`).",
        "",
        "| # | region (EN / AR) | governorate (EN / AR) | Census 2022 pop. (primary, "
        "S-cp2-gastat-007) | rows | ≥50k "
        "| sample | long | short | status | notes |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    total_pop = 0
    for i, g in enumerate(govs, 1):
        status, notes = row_status(g)
        keys = [r["row_key"] for r in g.rows]
        long_n = sum(stage_of.get(k) == "long" for k in keys)
        served = [r["name_en"] for r in g.rows if stage_of.get(r["row_key"]) == "served"]
        if served:
            notes += f"; served bucket (≤ 10 km, A-screen-004): {', '.join(served)}"
        short_n = sum(k in short_keys for k in keys)
        pop = f"{g.population:,}" if g.population is not None else "none (not in S-cp2-gastat-007)"
        total_pop += g.population or 0
        lines.append(
            "| "
            + " | ".join(
                _cell(x)
                for x in (
                    i,
                    f"{g.region_name} / {g.region_ar}",
                    f"{g.name_en} / {g.name_ar}",
                    pop,
                    len(g.rows),
                    sum(bool(r.get("threshold_50k")) for r in g.rows),
                    sum(bool(r.get("pilot_sample")) for r in g.rows),
                    long_n,
                    short_n,
                    status,
                    notes,
                )
            )
            + " |"
        )
    n_s073 = sum(not g.conflict for g in govs)
    regions = sorted({g.region for g in govs})
    lines += [
        "",
        "## Reconciliation",
        "",
        f"- Regions listed: **{len(regions)} / 13** (S-070, verified).",
        f"- `governorates_gastat`: **{n_s073} (primary TA1 export, 31 Oct 2026)** "
        "(S-cp2-gastat-007; regions S-cp2-gastat-002, S-cp2-gastat-003).",
        f"- The primary count equals the relayed count (S-cp2-gastat-001) and the earlier working "
        f"count (S-073): **{n_s073}**, with identical figures for every governorate. Other "
        "secondary counts: 139 (S-074, "
        "infobox; its text says 136), 136 (S-075), 150 (S-076). See `docs/gastat-regions.md`.",
        f"- `governorates_in_table`: **{len(govs)}** = {n_s073} (S-073) + "
        f"{len(govs) - n_s073} conflict rows. Difference explained row by row:",
    ]
    for g in govs:
        if g.conflict:
            lines.append(
                f"  - {g.name_en} ({g.region_name}): {NO_ROW_REASON[(g.region, g.name_en)]}."
            )
    lines += [
        f"- Population check: the {n_s073} primary governorate rows sum to **{total_pop:,}** "
        "persons; the primary TA9 table (S-cp2-gastat-003) and S-077 give the Census 2022 total as "
        "32,175,224.",
        "- Register rows not matched to any governorate: "
        + (
            "; ".join(
                f"{r['name_en']} ({r['region']}): governorate `{r['governorate']}`, screened "
                f"{r['screened']}"
                for r in unmatched
            )
            or "none"
        )
        + ".",
        "- Pilot rows withheld before writing (no coordinates): Al-'Arḍiyāt (Makkah pilot). "
        "Withheld at the pilot merge (no coordinates): "
        + (
            "; ".join(
                f"{', '.join(w['name_en'] for w in v)} ({k})" for k, v in sorted(withheld.items())
            )
            or "none"
        )
        + ".",
        "",
        "### Per region",
        "",
        "| region | governorates (primary TA1) | primary governorate sum | primary TA1 / TA9 "
        "region total | match | conflict rows | with ≥ 1 register row | screened | excluded | "
        "not yet swept | register rows |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for reg in regions:
        gs = [g for g in govs if g.region == reg]
        st = [row_status(g)[0] for g in gs]
        gsum = sum(g.population or 0 for g in gs if not g.conflict)
        prim = primary.get(reg, (None, None))
        ok = prim[0] == prim[1] == gsum
        lines.append(
            f"| {gs[0].region_name} | {sum(not g.conflict for g in gs)} | {gsum:,} | "
            f"{prim[0]:,} / {prim[1]:,} | {'yes' if ok else 'NO'} | "
            f"{sum(g.conflict for g in gs)} | {sum(bool(g.rows) for g in gs)} | "
            f"{st.count('screened')} | {sum(s.startswith('excluded') for s in st)} | "
            f"{st.count('not yet swept')} | {sum(len(g.rows) for g in gs)} |"
        )
    st_all = [row_status(g)[0] for g in govs]
    n_match = sum(
        primary.get(r, (None, None))[0]
        == primary.get(r, (None, None))[1]
        == sum(g.population or 0 for g in govs if g.region == r and not g.conflict)
        for r in regions
    )
    lines += [
        f"| **total** | **{n_s073}** | **{total_pop:,}** | "
        f"**{sum(p[0] for p in primary.values()):,} / {sum(p[1] for p in primary.values()):,}** | "
        f"**{n_match} / 13** | "
        f"**{sum(g.conflict for g in govs)}** | "
        f"**{sum(bool(g.rows) for g in govs)}** | **{st_all.count('screened')}** | "
        f"**{sum(s.startswith('excluded') for s in st_all)}** | "
        f"**{st_all.count('not yet swept')}** | **{sum(len(g.rows) for g in govs)}** |",
        "",
        "Sources: S-070, S-072, S-073, S-074, S-075, S-076, S-077, S-090, S-cp2-gastat-001, "
        "S-cp2-gastat-002, S-cp2-gastat-003, S-cp2-gastat-007 in "
        "`docs/sources/index.csv`; register row sources in the per-region pilot files.",
        "",
    ]
    return "\n".join(lines)


@app.command("pilot")
def main(
    register: Path = typer.Option(Path("cities/ksa/candidates-pilot.parquet"), "--register"),
    admin_html: Path = typer.Option(
        Path("data/ksa/pilot-qassim/raw/citypop_admin.html"), "--admin-html"
    ),
    run_dir: Path = typer.Option(Path("runs/screening-pilot"), "--run-dir"),
    national_total: int = typer.Option(32_175_224, "--national-total", help="S-077"),
    out: Path = typer.Option(Path("docs/coverage.md"), "--out"),
) -> None:
    """Write the coverage table."""
    import json

    import pyarrow.parquet as pq

    from screening.gastat import governorates_2022, primary_vs_relayed, read_ta1, read_ta9

    reg = pd.read_parquet(register)
    govs, unmatched = build(reg, admin_html)
    relayed = governorates_2022().set_index(["region", "name_ar"])
    gx, _ = primary_vs_relayed()
    prim = dict(zip(gx.relayed_name, gx.total, strict=True))  # relayed code -> primary total
    for g in govs:
        if g.conflict:
            continue
        r = relayed.loc[(g.region, g.name_ar)]
        if not g.population == int(r.pop_2022) == int(prim[r.code]):  # all 150 identical
            raise typer.BadParameter(
                f"{g.name_en}: S-073 {g.population} / relayed {r.pop_2022} / primary {prim[r.code]}"
            )
        g.population, g.code = int(prim[r.code]), r.code
    total = sum(g.population or 0 for g in govs if not g.conflict)
    if total != national_total:
        raise typer.BadParameter(f"primary rows sum to {total:,}, not the national total")
    ta1 = read_ta1().set_index("region").population
    ta9 = read_ta9()
    ta9 = ta9[ta9.year == 2022].set_index("region").population
    primary = {k: (int(ta1[k]), int(ta9[k])) for k in ta1.index}
    withheld = json.loads(pq.read_schema(register).metadata[b"merge_report"])["withheld_rows"]
    ll_path, sc_path = (
        run_dir / "long-list" / "longlist.parquet",
        run_dir / "score" / "scores.parquet",
    )
    stages = pd.read_parquet(ll_path) if ll_path.exists() else None
    short = set()
    if sc_path.exists():
        sc = pd.read_parquet(sc_path)
        short = set(sc.loc[sc["short_list"], "row_key"])
    out.write_text(render(govs, unmatched, withheld, stages, short, primary), encoding="utf-8")
    typer.echo(
        f"wrote {out}: {len(govs)} governorate rows, {len(unmatched)} unmatched register rows"
    )


# ============================================================================ R2 national table
NATIONAL_LABEL = "screening input, not a forecast"
FAMILY_LABEL = {"trunk_gap": "S2", "branch_spur": "S3", "commuter_belt": "S4",
                "station_addition": "S5"}  # fmt: skip


def national_rows(
    register: pd.DataFrame,
    longlist: pd.DataFrame,
    scores: pd.DataFrame,
    corridors: pd.DataFrame,
) -> tuple[pd.DataFrame, list[str]]:
    """One row per GASTAT governorate (primary TA1, S-cp2-gastat-007): register rows mapped by
    normalised Arabic name within the region, then by English name key. Returns the table and the
    register rows that map to no governorate (must be empty)."""
    from screening.gastat import REGION_ORDER, governorates_2022, key_light, read_gov_primary
    from screening.gastat import norm_ar as g_norm_ar

    g = governorates_2022()
    prim = read_gov_primary().assign(k=lambda d: d.name.map(key_light)).set_index("k").total
    g["pop_primary"] = g.code.map(key_light).map(prim)
    if g.pop_primary.isna().any() or (g.pop_primary != g.pop_2022).any():
        raise ValueError("primary TA1 and relayed governorate figures differ (C-gastat-001)")
    g["ka"] = g.name_ar.map(g_norm_ar)
    g["ke"] = g.name_en_s073.map(key_light)
    reg = register.copy()
    reg["ka"] = reg.governorate_ar.map(g_norm_ar)
    reg["ke"] = reg.governorate.map(key_light)
    gid = []
    for r in reg.itertuples():
        hit = g[(g.region == r.region) & (g.ka == r.ka)]
        if len(hit) != 1:
            hit = g[(g.region == r.region) & (g.ke == r.ke)]
        if len(hit) != 1:  # the primary export's own English spelling (e.g. Yanbu, Al Mahd)
            hit = g[(g.region == r.region) & (g.code.map(key_light) == r.ke)]
        gid.append(hit.code.iloc[0] if len(hit) == 1 else None)
    reg["gov_code"] = gid
    unmapped = reg[reg.gov_code.isna()].row_key.tolist()
    ll = longlist.set_index("row_key")
    reg["long"] = reg.row_key.map(ll.funnel_stage).eq("long")
    reg["served"] = reg.row_key.map(ll.funnel_stage).eq("served")
    reg["short"] = reg.row_key.isin(set(scores[scores.short_list].row_key))
    fam_of: dict[str, set[str]] = {}
    for c in corridors.itertuples():
        for k in str(c.generated_from).split(";"):
            fam_of.setdefault(k, set()).add(FAMILY_LABEL[c.family])
    reg["families"] = reg.row_key.map(lambda k: fam_of.get(k, set()))
    from screening.funnel import tag_10k_rule

    reg["t10"] = tag_10k_rule(reg)
    out = []
    order = {r: i for i, r in enumerate(REGION_ORDER)}
    g = g.assign(o=g.region.map(order)).sort_values(["o", "code"])
    for gv in g.itertuples():
        rows = reg[reg.gov_code == gv.code]
        scr = rows[rows.screened.astype(bool)]
        fams = sorted(set().union(*rows.families)) if len(rows) else []
        if len(scr):
            status = "screened"
        elif rows.long.any() or rows.served.any():
            status = (
                "screened (the centre passes by rule 2; the sweep flagged it: "
                + "; ".join(sorted({str(x) for x in rows.exclusion_reason}))
                + ")"
            )
        elif len(rows):
            status = "excluded: " + "; ".join(sorted({str(x) for x in rows.exclusion_reason}))
        else:
            status = "excluded: no register row (rule 2 gap)"
        out.append({
            "region": gv.region, "governorate_en": gv.code, "governorate_ar": gv.name_ar,
            "population": int(gv.pop_primary), "rows": len(rows), "ge_10k": int(rows.t10.sum()),
            "ge_5k": int(rows.tag_5k.astype(bool).sum()), "long": int(rows.long.sum()),
            "served": int(rows.served.sum()), "short": int(rows.short.sum()),
            "families": ", ".join(fams) or "none",
            "centre": ", ".join(rows[rows.is_governorate_centre.astype(bool)].name_en) or "none",
            "status": status,
        })  # fmt: skip
    return pd.DataFrame(out), unmapped


N_GASTAT = 150  # S-cp2-gastat-007 (primary TA1 governorate export: 150 rows + Total)


def reconcile(t: pd.DataFrame, unmapped: list[str], n_gastat: int = N_GASTAT) -> list[str]:
    """Rule 2 checks on the national table; an empty list = reconciled."""
    err = []
    if len(t) != n_gastat or t.governorate_en.duplicated().any():
        err.append(f"coverage has {len(t)} rows, GASTAT {n_gastat}")
    if t.region.nunique() != 13:
        err.append(f"{t.region.nunique()} regions, not 13")
    if unmapped:
        err.append(f"register rows without a governorate: {unmapped[:5]}")
    if (t.rows == 0).any():
        err.append(f"governorates without rows: {list(t[t.rows == 0].governorate_en)}")
    return err


@app.command("national")
def national_cmd(
    register: Path = typer.Option(Path("cities/ksa/candidates.parquet"), "--register"),
    run: Path = typer.Option(Path("runs/r2"), "--run"),
    out: Path = typer.Option(Path("docs/coverage.md"), "--out"),
) -> None:
    """R2 coverage table: exactly one row per GASTAT governorate, reconciled to the count."""
    import datetime as dt

    reg = pd.read_parquet(register)
    t, unmapped = national_rows(
        reg,
        pd.read_parquet(run / "long-list" / "longlist.parquet"),
        pd.read_parquet(run / "score" / "scores.parquet"),
        pd.read_csv(run / "corridors" / "corridors.csv"),
    )
    ct = pd.read_csv(run / "control_total" / "control_total.csv")
    n_gastat = N_GASTAT
    errors = reconcile(t, unmapped)
    if errors:
        raise typer.BadParameter("; ".join(errors))
    today = dt.date(2026, 10, 31).isoformat()
    L = [
        f"> **Document version:** docs/coverage.md v2.0 | {today} | Author: screening-analyst "
        "(R2, national) | Status: draft",
        "",
        "# Coverage audit: every GASTAT governorate (R2, national)",
        "",
        f"Label: {NATIONAL_LABEL}. Generated by `uv run python -m screening.coverage national` "
        "from `cities/ksa/candidates.parquet` and the R2 funnel and corridor runs (`runs/r2/`, "
        "seed 1). Populations: GASTAT Census 2022, primary TA1 governorate export "
        "(S-cp2-gastat-007), identical to the relayed table on all 150 rows (C-gastat-001). "
        "Columns: register rows swept; rows at or above 10,000 under the P1a rule (grid-only "
        "figures need corroboration, A-screen-031…033); rows at or above 5,000 (`tag_5k`); "
        "long list (A-screen-001/003, centres by rule 2) and served bucket (within 10 km of an "
        "existing station, A-screen-004); short list (top 60 plus stable, A-screen-006); "
        "corridor families whose generating short-list ids lie in the governorate.",
        "",
        "| region | governorate | name (AR) | population 2022 (S-cp2-gastat-007) | rows | ≥ 10k "
        "| ≥ 5k | long | served | short | families | centre row | status |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in t.itertuples():
        L.append(
            f"| {r.region} | {_cell(r.governorate_en)} | {_cell(r.governorate_ar)} | "
            f"{r.population:,} | {r.rows} | {r.ge_10k} | {r.ge_5k} | {r.long} | {r.served} | "
            f"{r.short} | {r.families} | {_cell(_short(r.centre, 60))} | "
            f"{_cell(_short(r.status, 160))} |"
        )
    reg_t = t.groupby("region", sort=False).agg(
        governorates=("governorate_en", "size"), rows=("rows", "sum"), ge_10k=("ge_10k", "sum"),
        long=("long", "sum"), short=("short", "sum"))  # fmt: skip
    L += ["", "## Per region", "",
          "| region | governorates | rows | ≥ 10k | long | short | grid scale factor "
          "(A-screen-040) "
          "| register grid sum before → after |", "|---|---|---|---|---|---|---|---|"]  # fmt: skip
    cti = ct.set_index("region")
    for reg_name, r in reg_t.iterrows():
        c = cti.loc[reg_name]
        L.append(
            f"| {reg_name} | {r.governorates} | {r.rows} | {r.ge_10k} | {r.long} | {r.short} | "
            f"{c.grid_scale_factor:.4f} | {c.register_grid_before:,.0f} → "
            f"{c.register_grid_after:,.0f} |"
        )
    excl = t[t.status.str.startswith("excluded")]
    L += [
        "",
        "## Reconciliation",
        "",
        f"governorates in table = {len(t)}; governorates_gastat = {n_gastat} (primary TA1 "
        "governorate export, S-cp2-gastat-007); regions = "
        f"{t.region.nunique()} of 13; register rows = {len(reg)}, every one mapped to a "
        "governorate (0 unmapped); governorates with no register row = "
        f"{int((t.rows == 0).sum())}; governorates excluded = {len(excl)}"
        + (f" ({', '.join(excl.governorate_en)}; reason in the status column)" if len(excl) else "")
        + ".",
    ]
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    typer.echo(f"wrote {out}: {len(t)} governorates = GASTAT {n_gastat}")


if __name__ == "__main__":
    app()
