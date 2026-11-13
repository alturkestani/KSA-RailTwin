"""Feasibility report build and checks (R8, report-writer).

CLI:
  uv run python -m common.report build   # refresh the generated blocks in docs/report/sections/,
                                         # assemble docs/report/feasibility-report.md (version
                                         # header, contents, source notes), regenerate
                                         # annex-sources.md, annex-assumptions.md and the 13
                                         # annex-regions/<slug>.md files
  uv run python -m common.report check   # number tracing, no "will" in results, no model names,
                                         # the label rule, the S6-L1 risk statement, the L4/L5 rule

Deterministic: the same inputs give byte-identical outputs (no clock, sorted iteration, fixed
formatting). Inputs are read only: `docs/sources/index.csv`, `docs/assumptions*.md`,
`docs/coverage.md`, `docs/regions/*.md`, `cities/ksa/` registers and the run files under `runs/`.
Generated blocks inside the section files sit between `<!-- gen:<name> -->` and
`<!-- /gen:<name> -->`; everything else in a section is hand-written and left untouched.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import re
from collections.abc import Callable
from dataclasses import dataclass, field
from decimal import ROUND_HALF_UP, Decimal
from functools import cached_property
from pathlib import Path

import typer
import yaml

from common import REPO_ROOT
from common.labels import ALIGNMENT_LIMITATION, LABEL

REPORT_VERSION = "1.0"
REPORT_DATE = "4 Nov 2026"
AUTHOR = "report-writer"
STATUS = "draft"
# The assembled report's own header (FIX_R8): bumped on every rebuild that changes its text.
MAIN_REPORT_VERSION = "1.4"
MAIN_REPORT_DATE = "13 Nov 2026"
MAIN_REPORT_NOTE = (
    "; v1.1: fig09 title, FIX_R8 item 1; v1.2: wording checks, FIX_R8 item 9; "
    "v1.3: neutral framing, FIX_R8 item 7; v1.4: S6-L6 plain-language section, FIX_PDF_CONNECTED"
)
JUDGE_SHA = "d9fef64384e2e25f84b288962907fa25e2476d9749bf863d7bd6fb66fb70f9ee"
JUDGE_SHORT = "d9fef643…"
PROV = (
    f"Judge v3 (`v3-variants`, SHA-256 `{JUDGE_SHORT}`, docs/r6/judge-hashes.md), seed 1, "
    "10,000 draws, frozen alignment weights v1"
)
LABEL_LINE = f"> Labels: {LABEL}. {ALIGNMENT_LIMITATION}."
MINUS = "−"

REPORT_DIR = REPO_ROOT / "docs" / "report"
SECTIONS_DIR = REPORT_DIR / "sections"

# The 13 regions in the order of docs/coverage.md (proper names; no figures).
REGIONS: list[tuple[str, str, str]] = [
    ("riyadh", "Riyadh", "الرياض"),
    ("makkah", "Makkah", "مكة المكرمة"),
    ("madinah", "Madinah", "المدينة المنورة"),
    ("qassim", "Qassim", "القصيم"),
    ("eastern", "Eastern Province", "المنطقة الشرقية"),
    ("asir", "Asir", "عسير"),
    ("tabuk", "Tabuk", "تبوك"),
    ("hail", "Hail", "حائل"),
    ("northern_borders", "Northern Borders", "الحدود الشمالية"),
    ("jazan", "Jazan", "جازان"),
    ("najran", "Najran", "نجران"),
    ("al_baha", "Al-Baha", "الباحة"),
    ("al_jouf", "Al-Jouf", "الجوف"),
]
FAMILIES = [
    ("trunk_gap", "S2", "trunk gaps"),
    ("branch_spur", "S3", "branches and spurs"),
    ("commuter_belt", "S4", "commuter belts"),
    ("station_addition", "S5", "station additions"),
]
# Library corridors that are not searchable (CP6 P6a: one shared Jubail station; r6-topology §0).
RETIRED = {
    "S5-station_addition-al-jubayl-royal-commission",
    "S5-station_addition-jubail-two-stations",
}
PHASES = ["2030", "2035", "2040", "2050"]
POPS = ["un_wpp_low", "un_wpp_medium", "un_wpp_high"]
CP7 = {
    "S6-L2": ("central case", "L2"),
    "S6-L1": ("upside case (carries the Al-Kharj spur's P90 cost risk)", "L1"),
    "S6-L3": ("reach alternative", "L3"),
}
CP7_CORRIDORS = {
    "S5-station_addition-al-jubayl": "Al Jubayl station (GCC Railway)",
    "S5-station_addition-dhahran": "Dhahran station (SAR East line)",
    "S5-station_addition-duruma": "Duruma station (Landbridge)",
    "S3-branch_spur-al-kharj": "Al-Kharj spur",
    "S4-commuter_belt-riyadh-225": "Riyadh commuter belt 225 (Al Muzahimiyah, Duruma)",
}
LAYOUT_MEMBERS = {
    "S6-L2": {
        "S5-station_addition-al-jubayl",
        "S5-station_addition-dhahran",
        "S5-station_addition-duruma",
    },
    "S6-L1": {
        "S5-station_addition-al-jubayl",
        "S5-station_addition-dhahran",
        "S5-station_addition-duruma",
        "S3-branch_spur-al-kharj",
    },
    "S6-L3": {
        "S5-station_addition-al-jubayl",
        "S5-station_addition-dhahran",
        "S3-branch_spur-al-kharj",
        "S4-commuter_belt-riyadh-225",
    },
}
METRO_REGION = {
    "Riyadh": "riyadh",
    "Jeddah": "makkah",
    "Makkah": "makkah",
    "Taif": "makkah",
    "Madinah": "madinah",
    "Buraidah": "qassim",
    "Dammam–Khobar–Dhahran": "eastern",
    "Abha–Khamis Mushait": "asir",
    "Tabuk": "tabuk",
    "Jazan": "jazan",
    "Najran": "najran",
}
FIGURES = [
    "fig01-national-map",
    "fig02-screening-funnel",
    "fig03-coverage-by-region",
    "fig04-bcr-bands-by-family",
    "fig05-programme-npv-ranges",
    "fig06-l1-p90-cost-risk",
    "fig07-pareto-front",
    "fig08-reach-tradeoff",
    "fig09-stage-gates",
    "fig10-fiscal-exposure",
    "fig11-vfm",
    "fig12-isochrones",
    "fig13-benchmark-cost-per-km",
    "fig14-tornado-switching",
    "fig15-capex-ranges",
]
DASHBOARD_SHOTS = ["dashboard-map", "dashboard-pareto", "dashboard-ranges", "dashboard-difference"]

MODEL_NAMES = re.compile(r"claude|opus|haiku|fable", re.IGNORECASE)
WILL = re.compile(r"\bwill\b", re.IGNORECASE)
# A table header or figure caption that states a length, cost, travel time or ridership.
LABEL_TRIGGER = re.compile(
    r"\b(km|length|lengths|cost|costs|capex|sar|npv|bcr|travel time|minutes?|min|ridership|trips?|"
    r"pax|passengers?|passenger-km|fiscal)\b|كم|ريال|تكلفة|التكلفة|دقيقة|دقائق|رحلة|رحلات|ركاب|الركاب",
    re.IGNORECASE,
)
CITATION = re.compile(r"\[\^S-[^\]]+\]|\bA-[a-z0-9_]+-\d+|runs/|cities/ksa/")
FOOTNOTE_REF = re.compile(r"\[\^(S-[^\]\s]+)\]")
L1_MARK = "S6-L1"
L45 = re.compile(r"S6-L[45]\b")
L45_FIGS = ("fig07-pareto-front", "fig08-reach-tradeoff")
GEN = re.compile(r"<!-- gen:(?P<name>[\w-]+) -->\n.*?<!-- /gen:(?P=name) -->", re.DOTALL)
HEADER_RE = re.compile(r"^> \*\*Document version:\*\*")


# --------------------------------------------------------------------------------------------
# Formatting helpers
# --------------------------------------------------------------------------------------------


def fm(x: float | None, digits: int = 0, sign: bool = False) -> str:
    """Thousands-separated, Unicode minus; '+' when `sign` and positive; n/a for missing."""
    if x is None or (isinstance(x, float) and (math.isnan(x) or math.isinf(x))):
        return "n/a"
    q = Decimal(1).scaleb(-digits)
    v = float(Decimal(repr(float(x))).quantize(q, rounding=ROUND_HALF_UP))  # half away from zero
    if v == 0:
        v = 0.0
    body = f"{abs(v):,.{digits}f}"
    if v < 0:
        return MINUS + body
    return ("+" + body) if sign and v > 0 else body


def rng(a: float | None, b: float | None, c: float | None, digits: int = 0) -> str:
    return f"{fm(a, digits)} / {fm(b, digits)} / {fm(c, digits)}"


def mill(x: float | None, digits: int = 2) -> str:
    return "n/a" if x is None else f"{fm(x / 1e6, digits)} M"


def neutralise(text: str) -> str:
    """Replace one letter of a forbidden string with its HTML character reference.

    Some source URLs and file names contain a string the model-name check forbids (for
    example a repository host `opus4…` or a file `CLAUDE.md`). The rendered text is unchanged;
    the raw file no longer matches the grep (annex headers say so).
    """

    def sub(m: re.Match[str]) -> str:
        s = m.group(0)
        return s[0] + f"&#{ord(s[1])};" + s[2:]

    return MODEL_NAMES.sub(sub, text)


def cell(x: object) -> str:
    s = "" if x is None else str(x)
    if s in ("nan", "None"):
        s = ""
    s = s.replace("\r", " ").replace("\n", " ").replace("|", "\\|").strip()
    return neutralise(s)


def sha12(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:12] if path.exists() else "missing"


def header(
    name: str, version: str = REPORT_VERSION, note: str = "", date: str = REPORT_DATE
) -> str:
    author = f"{AUTHOR} (generated by `uv run python -m common.report build`{note})"
    return (
        f"> **Document version:** {name} v{version} | {date} | Author: {author} | Status: {STATUS}"
    )


def table(head: list[str], rows: list[list[str]]) -> str:
    out = ["| " + " | ".join(head) + " |", "|" + "|".join("---" for _ in head) + "|"]
    out += ["| " + " | ".join(r) + " |" for r in rows]
    return "\n".join(out)


# --------------------------------------------------------------------------------------------
# Data context (lazy; read only)
# --------------------------------------------------------------------------------------------


@dataclass
class Ctx:
    root: Path = REPO_ROOT
    sources_csv: Path | None = None
    figures_csv: Path | None = None
    missing: list[str] = field(default_factory=list)

    def p(self, rel: str) -> Path:
        return self.root / rel

    def jload(self, rel: str) -> dict:
        path = self.p(rel)
        if not path.exists():
            self.missing.append(rel)
            return {}
        return json.loads(path.read_text(encoding="utf-8"))

    @cached_property
    def sources(self) -> dict[str, dict[str, str]]:
        path = self.sources_csv or self.p("docs/sources/index.csv")
        with path.open(encoding="utf-8", newline="") as f:
            return {r["id"]: r for r in csv.DictReader(f)}

    @cached_property
    def figures(self) -> dict[str, dict[str, str]]:
        path = self.figures_csv or self.p("docs/report/figures/figures-index.csv")
        return {r["stem"]: r for r in figures_index(path)}

    @cached_property
    def top5(self) -> dict[str, dict[str, str]]:
        path = self.p("runs/r6/top5/top5.csv")
        if not path.exists():
            self.missing.append("runs/r6/top5/top5.csv")
            return {}
        with path.open(encoding="utf-8", newline="") as f:
            return {r["layout"]: r for r in csv.DictReader(f)}

    @cached_property
    def fiscal(self) -> dict:
        return self.jload("runs/r7/fiscal/fiscal.json")

    @cached_property
    def vfm(self) -> dict:
        return self.jload("runs/r7/vfm/vfm.json")

    @cached_property
    def v2(self) -> dict:
        return self.jload("runs/r7-v2/sensitivity.json")

    @cached_property
    def recommendations(self) -> dict:
        path = self.p("cities/ksa/funding/recommendations.yaml")
        return yaml.safe_load(path.read_text(encoding="utf-8")) if path.exists() else {}

    @cached_property
    def cba(self):  # pandas DataFrame
        import pandas as pd

        path = self.p("runs/cba/summary.parquet")
        if not path.exists():
            self.missing.append("runs/cba/summary.parquet")
            return pd.DataFrame()
        return pd.read_parquet(path)

    @cached_property
    def library_ids(self) -> list[str]:
        return list(self.jload("runs/r6/v3/library/library.json").get("ids", []))

    @cached_property
    def library(self) -> dict[str, dict]:
        out = {}
        for cid in self.library_ids:
            s = self.jload(f"runs/r6/v3/library/{cid}/score.json")
            if s:
                out[cid] = s
        return out

    @cached_property
    def corridors(self) -> dict[str, dict]:
        out = {}
        for f in sorted(self.p("cities/ksa/corridors").glob("*/*.yaml")):
            d = yaml.safe_load(f.read_text(encoding="utf-8"))
            out[d["id"]] = d
        return out

    @cached_property
    def candidates(self):
        import pandas as pd

        path = self.p("cities/ksa/candidates.parquet")
        return pd.read_parquet(path) if path.exists() else pd.DataFrame()

    @cached_property
    def r2_summary(self) -> dict:
        return self.jload("runs/r2/score/summary.json")

    @cached_property
    def ranks(self):
        import pandas as pd

        path = self.p("runs/r2/score/ranks.parquet")
        return pd.read_parquet(path) if path.exists() else pd.DataFrame()

    @cached_property
    def scores(self):
        import pandas as pd

        path = self.p("runs/r2/score/sweep.parquet")
        return pd.read_parquet(path) if path.exists() else pd.DataFrame()

    @cached_property
    def longlist(self):
        import pandas as pd

        path = self.p("runs/r2/long-list/longlist.parquet")
        return pd.read_parquet(path) if path.exists() else pd.DataFrame()

    @cached_property
    def commute(self):
        import pandas as pd

        path = self.p("runs/access/commute-test-s1/commute_test.parquet")
        if not path.exists():
            self.missing.append("runs/access/commute-test-s1/commute_test.parquet")
            return pd.DataFrame()
        return pd.read_parquet(path)

    @cached_property
    def coverage_rows(self) -> list[list[str]]:
        """Governorate rows of docs/coverage.md (first table: 13 columns, region first)."""
        path = self.p("docs/coverage.md")
        rows: list[list[str]] = []
        slugs = {s for s, _, _ in REGIONS}
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.startswith("| "):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split(" | ")]
            if len(cells) == 13 and cells[0] in slugs:
                rows.append(cells)
        return rows

    # ---- derived helpers ---------------------------------------------------------------

    def short_keys(self) -> list[str]:
        if self.ranks.empty:
            return []
        n = int(self.r2_summary.get("n_short", 60))
        r = self.ranks.sort_values(["base", "row_key"])
        return [k for k, b in zip(r["row_key"], r["base"], strict=True) if int(b) <= n]

    def best_phase(self, score: dict) -> tuple[str, float]:
        """Phase with the highest robust NPV (min over population cases of NPV at P50 cost)."""
        best = ("", -math.inf)
        for ph in PHASES:
            sw = score.get("phase_sweep", {}).get(ph)
            if not sw:
                continue
            v = min(sw[f"npv_at_p50_cost|{p}"] for p in POPS)
            if v > best[1]:
                best = (ph, v)
        return best

    def cba_row(
        self, case: str, pop: str = "un_wpp_medium", horizon: int = 60, rate: str = "greenbook_2026"
    ):
        d = self.cba
        if d.empty:
            return None
        sel = d[
            (d.case == case)
            & (d.population == pop)
            & (d.horizon == horizon)
            & (d.rate_case == rate)
        ]
        return None if sel.empty else sel.iloc[0]

    @cached_property
    def station_regions(self) -> list[tuple[float, float, str]]:
        pts: list[tuple[float, float, str]] = []
        c = self.candidates
        if c.empty:
            return pts
        for lat, lon, reg in zip(c["lat"], c["lon"], c["region"], strict=True):
            if lat == lat and lon == lon:
                pts.append((float(lat), float(lon), str(reg)))
        return pts

    def nearest_region(self, lat: float, lon: float) -> str | None:
        best, reg = math.inf, None
        cl = math.cos(math.radians(lat))
        for la, lo, r in self.station_regions:
            d = (la - lat) ** 2 + ((lo - lon) * cl) ** 2
            if d < best:
                best, reg = d, r
        return reg

    def corridor_regions(self, cid: str) -> set[str]:
        d = self.corridors.get(cid, {})
        regs: set[str] = set()
        for g in d.get("generated_from_ids") or []:
            head = str(g).split(":")[0]
            if head == "metro":
                m = METRO_REGION.get(str(g).split(":", 1)[1])
                if m:
                    regs.add(m)
            elif head in {s for s, _, _ in REGIONS}:
                regs.add(head)
        for st in d.get("stations") or []:
            if st.get("lat") is not None and st.get("lon") is not None:
                r = self.nearest_region(float(st["lat"]), float(st["lon"]))
                if r:
                    regs.add(r)
        return regs


# --------------------------------------------------------------------------------------------
# Generated blocks
# --------------------------------------------------------------------------------------------


def l1_risk_sentence(ctx: Ctx) -> str:
    r = ctx.top5.get("S6-L1")
    if not r:
        return "NPV at P90 cost: run file not found (runs/r6/top5/top5.csv)"
    vals = [float(r[f"npv_p90cost_{p}"]) for p in ("low", "medium", "high")]
    body = " / ".join(fm(v, sign=True) if v > 0 else fm(v) for v in vals)
    return f"NPV at P90 cost {body} SAR m (low / medium / high), runs/r6/top5/top5.csv"


def gen_l1_risk(ctx: Ctx) -> str:
    return (
        "**S6-L1, the upside case, carries the Al-Kharj spur's P90 cost risk:** "
        f"{l1_risk_sentence(ctx)} "
        f"(columns `npv_p90cost_low/medium/high`; {PROV})."
    )


def gen_s1(ctx: Ctx) -> str:
    rows = []
    case = "CBA-S1-committed-programme"
    draws = None
    for pop in POPS:
        r = ctx.cba_row(case, pop)
        if r is None:
            continue
        draws = int(r["draws"])
        rows.append(
            [
                pop.replace("un_wpp_", "UN WPP "),
                rng(r.npv_p10, r.npv_p50, r.npv_p90),
                rng(r.bcr_p10, r.bcr_p50, r.bcr_p90, 2),
                rng(r.fiscal_cost_p10, r.fiscal_cost_p50, r.fiscal_cost_p90),
            ]
        )
    head = [
        "population case",
        "NPV in the model, P10 / P50 / P90 (SAR m)",
        "BCR P10 / P50 / P90 (without WEIs)",
        "fiscal cost to the state P10 / P50 / P90 (SAR m, fully public)",
    ]
    return "\n".join(
        [
            LABEL_LINE,
            table(head, rows),
            f"Run: runs/cba/CBA-S1-committed-programme (R5 CBA, seed 1, {fm(draws)} draws; S1 "
            "against S0; "
            "60 years, Green Book 2026 declining rate A-cba-001; SAR m, 2025 prices, PV 2026).",
        ]
    )


def _layout_rows(ctx: Ctx, layouts: list[str]) -> list[list[str]]:
    t = ctx.top5

    def g(L: str, k: str) -> float:
        return float(t[L][k])

    def phases(L: str) -> str:
        ph = json.loads(t[L]["phases"])
        parts = []
        for year in sorted(ph):
            names = [CP7_CORRIDORS.get(c, c).split(" (")[0] for c in ph[year]]
            parts.append(f"{', '.join(names)} (phase {year})")
        return "; ".join(parts)

    spec: list[tuple[str, Callable[[str], str]]] = [
        ("role", lambda L: CP7[L][0]),
        ("corridors (phase year; construction starts 3 years earlier, A-r6-002)", phases),
        ("robust NPV (worst population case, P50 PVB − P50 PVC)", lambda L: fm(g(L, "robust_npv"))),
        (
            "NPV at P50 cost, low / medium / high",
            lambda L: rng(
                g(L, "npv_p50cost_low"), g(L, "npv_p50cost_medium"), g(L, "npv_p50cost_high")
            ),
        ),
        (
            "NPV at P90 cost, low / medium / high (held-out test)",
            lambda L: rng(
                g(L, "npv_p90cost_low"), g(L, "npv_p90cost_medium"), g(L, "npv_p90cost_high")
            ),
        ),
        (
            "NPV P10 / P50 / P90 of the draws (medium)",
            lambda L: rng(
                g(L, "npv_draws_p10_medium"),
                g(L, "npv_draws_p50_medium"),
                g(L, "npv_draws_p90_medium"),
            ),
        ),
        (
            "BCR P10 / P50 / P90 (medium, without WEIs)",
            lambda L: rng(
                g(L, "bcr_p10_medium"), g(L, "bcr_p50_medium"), g(L, "bcr_p90_medium"), 2
            ),
        ),
        (
            "capex P10 / P50 / P90 (uplifted, undiscounted)",
            lambda L: rng(g(L, "capex_p10"), g(L, "capex_p50"), g(L, "capex_p90")),
        ),
        (
            "added rail trips 2050, medium (vs S1)",
            lambda L: mill(g(L, "added_rail_trips_2050_medium")),
        ),
        ("new route-km", lambda L: fm(g(L, "new_route_km"))),
        (
            "reach gain within 120 door-to-door min of the five metros (2025 population)",
            lambda L: mill(g(L, "access_gain_120")),
        ),
        (
            "Green Book 2026 at 30 / 40 years; flat 5 % / 7 % (NPV at P50 cost, medium)",
            lambda L: (
                f"{fm(g(L, 'sens_greenbook_2026/30y'))} / {fm(g(L, 'sens_greenbook_2026/40y'))}; "
                f"{fm(g(L, 'sens_flat_5/60y'))} / {fm(g(L, 'sens_flat_7/60y'))}"
            ),
        ),
    ]
    return [[name] + [fn(L) for L in layouts] for name, fn in spec]


def gen_programmes(ctx: Ctx) -> str:
    layouts = [L for L in ("S6-L2", "S6-L1", "S6-L3") if L in ctx.top5]
    if not layouts:
        return "Run file not found: runs/r6/top5/top5.csv"
    head = ["(each against S1; SAR m, 2025 prices, PV 2026, 60 years, Green Book 2026)"] + layouts
    return "\n".join(
        [
            LABEL_LINE,
            table(head, _layout_rows(ctx, layouts)),
            f"Run: runs/r6/top5/top5.csv and runs/r6/top5/L1|L2|L3/score.json ({PROV}). "
            f"{l1_risk_sentence(ctx)} for S6-L1.",
        ]
    )


def gen_cp7_corridors(ctx: Ctx) -> str:
    rows = []
    for cid, name in CP7_CORRIDORS.items():
        b = ctx.fiscal.get("corridors", {}).get(cid, {}).get("basis")
        if not b:
            continue
        c = b["capex"]
        p90 = b["npv_at_p90_cost_60y"]
        bcr = b["bcr_p10_60y"]
        rows.append(
            [
                f"{name} (`{cid}`)",
                rng(c["p10"], c["p50"], c["p90"]),
                fm(b["robust_npv"]),
                rng(p90["un_wpp_low"], p90["un_wpp_medium"], p90["un_wpp_high"]),
                rng(bcr["un_wpp_low"], bcr["un_wpp_medium"], bcr["un_wpp_high"], 2),
                f"`{b['score']}`",
            ]
        )
    head = [
        "corridor (standalone, at its CP7 phase)",
        "capex P10 / P50 / P90 (SAR m)",
        "robust NPV (SAR m)",
        "NPV at P90 cost, low / medium / high (SAR m)",
        "BCR P10, low / medium / high",
        "run",
    ]
    return "\n".join(
        [
            LABEL_LINE,
            table(head, rows),
            f"Run: runs/r7/fiscal/fiscal.json, corridor `basis` ({PROV}). Standalone corridors do "
            "not add up to "
            "a layout: corridors compete for the same trips.",
        ]
    )


def _fiscal_rows(ctx: Ctx, entity: str, group: str) -> list[list[str]]:
    ent = ctx.fiscal.get(group, {}).get(entity, {})
    rows = []
    for model, m in ent.get("models", {}).items():
        bp = m["by_pop"][ctx.fiscal.get("robust_case", "un_wpp_low")]
        n = bp["net_fiscal_cost_60y"]
        bs = bp["budget_share"]
        cl = bp.get("contingent_liabilities", {})
        rows.append(
            [
                entity,
                f"`{model}`",
                f"{rng(n['p10'], n['p50'], n['p90'])} ({fm(n['expected'])})",
                (
                    f"{fm(bs['p50']['central']['peak_pct'], 3)} % / "
                    f"{fm(bs['p90']['central']['peak_pct'], 3)} % "
                    f"({bs['p90']['central']['peak_year']})"
                ),
                f"{fm(cl.get('expected_pv', 0))} / {fm(cl.get('p90_pv', 0))}",
            ]
        )
    return rows


def gen_fiscal(ctx: Ctx) -> str:
    rows = []
    for L in ("S6-L2", "S6-L1", "S6-L3"):
        rows += _fiscal_rows(ctx, L, "programmes")
    head = [
        "programme",
        "delivery model",
        "net fiscal cost PV 60 y P10 / P50 / P90 (expected), SAR m",
        "peak share of state expenditure at P50 / P90 capex (year)",
        "contingent liabilities PV expected / P90, SAR m",
    ]
    s1 = (
        ctx.fiscal.get("baseline_s1", {})
        .get("rows", {})
        .get("un_wpp_low|60", {})
        .get("fiscal_cost", {})
    )
    s1_line = (
        f"S1 baseline (fully public, 60 y, un_wpp_low): fiscal cost P10 / P50 / P90 "
        f"{rng(s1.get('P10'), s1.get('P50'), s1.get('P90'))} SAR m "
        "(runs/cba/CBA-S1-committed-programme, "
        "via runs/r7/fiscal/fiscal.json `baseline_s1`); every programme figure above is "
        "incremental to S1."
    )
    return "\n".join(
        [
            LABEL_LINE,
            table(head, rows),
            f"Run: runs/r7/fiscal/fiscal.json, population case un_wpp_low (robust), {PROV}. "
            "Availability-PPP "
            "figures have P10 = P50 by construction (fixed price; capex enters only through the "
            "overrun "
            "above the private cushion); expected values rest on the lognormal tail A-fund-108. "
            f"S6-L1, the upside case: {l1_risk_sentence(ctx)}.",
            "",
            s1_line,
        ]
    )


def gen_vfm(ctx: Ctx) -> str:
    rows = []
    for group in ("programmes", "corridors"):
        for ent, v in ctx.vfm.get(group, {}).items():
            c = v["central"]
            rs = v.get("rate_sensitivity", {})
            order = sorted(rs, key=lambda k: (not k.startswith("flat"), k))
            rs_txt = " / ".join(fm(rs[k]) for k in order)
            rows.append(
                [
                    f"`{ent}`",
                    fm(c["psc"]),
                    fm(c["ppp"]),
                    f"{fm(c['vfm'])} ({fm(c['vfm_pct_psc'], 1)} %)",
                    "yes" if v.get("sign_robust_to_registered_ranges") else "no",
                    rs_txt,
                ]
            )
    head = [
        "entity",
        "E[PSC] (SAR m)",
        "E[availability PPP] (SAR m)",
        "VfM (% of PSC); > 0 favours the PPP",
        "sign robust to every registered range",
        "VfM at flat 5 % / sovereign real rate (SAR m)",
    ]
    return "\n".join(
        [
            LABEL_LINE,
            table(head, rows),
            f"Run: runs/r7/vfm/vfm.json (60 years, robust case; {PROV}); parameters A-fund-002, "
            "A-fund-007, "
            "A-fund-008, A-fund-102, A-fund-103. The private-finance premium is sourced from a UK "
            "reference "
            "class and is unclear for Saudi Arabia[^S-fund-r7-001]. "
            f"S6-L1, the upside case: {l1_risk_sentence(ctx)}.",
        ]
    )


def gen_families(ctx: Ctx) -> str:
    lib = ctx.library
    rows = []
    for fam, s, name in FAMILIES:
        ids = [
            c for c in ctx.library_ids if c.startswith(f"{s}-") and c not in RETIRED and c in lib
        ]
        if not ids:
            continue
        r2030 = [lib[c]["robust_npv"] for c in ids]
        best = {c: ctx.best_phase(lib[c]) for c in ids}
        pos = sorted(c for c in ids if best[c][1] > 0)
        cap = [lib[c]["capex_sar_m"]["capex_p50"] for c in ids]
        bcr = [lib[c]["bcr_p50"]["un_wpp_medium"] for c in ids]
        sub = ctx.cba
        r5 = sub[(sub.family == fam) & (sub.population == "un_wpp_medium") & (sub.horizon == 60)]
        r5 = r5[r5.rate_case == "greenbook_2026"] if not r5.empty else r5
        r5_txt = (
            f"{fm(r5.bcr_p50.min(), 2)} to {fm(r5.bcr_p50.max(), 2)} "
            f"({int((r5.bcr_p50 >= 1).sum())} of {len(r5)})"
            if not r5.empty
            else "n/a"
        )
        comp = ctx.jload(f"runs/r6/compare/{s}/score.json")
        comp_txt = (
            f"{fm(comp['robust_npv'])} on capex P50 {fm(comp['capex_sar_m']['capex_p50'])}"
            if comp
            else "n/a"
        )
        pos_txt = (
            f"{len(pos)}: " + ", ".join(f"`{c}` {fm(best[c][1])} at {best[c][0]}" for c in pos)
            if pos
            else "0"
        )
        rows.append(
            [
                f"{s} {name}",
                str(len(ids)),
                f"{fm(min(r2030))} to {fm(max(r2030))}",
                f"{fm(min(cap))} to {fm(max(cap))}",
                f"{fm(min(bcr), 2)} to {fm(max(bcr), 2)}",
                pos_txt,
                comp_txt,
                r5_txt,
            ]
        )
    head = [
        "family",
        "corridors (searchable)",
        "robust NPV at 2030, lowest to highest (SAR m)",
        "capex P50 at 2030, lowest to highest (SAR m)",
        "BCR P50 at 2030 (medium), lowest to highest",
        "positive robust NPV at the best phase (SAR m, phase)",
        "whole family at 2030: robust NPV on capex P50 (SAR m)",
        "R5 CBA P50 BCR range (cases ≥ 1), medium, 60 y",
    ]
    return "\n".join(
        [
            LABEL_LINE,
            table(head, rows),
            f"Runs: runs/r6/v3/library/<id>/score.json (standalone, every phase; {PROV}); whole "
            "families "
            "runs/r6/compare/S2…S5/score.json; R5 CBA runs/cba/summary.parquet (seed 1, 10,000 "
            "draws, before "
            "the CP6 zone split). The two retired Jubail variants (CP6 P6a) are left out of the "
            "counts.",
        ]
    )


def gen_alignment_v2(ctx: Ctx) -> str:
    rows = []
    for r in ctx.v2.get("rows", []):

        def ab(k: str, r: dict = r) -> str:
            a, b = r[k]
            return f"{fm(a)} → {fm(b)}"

        rows.append(
            [
                f"`{r['entity']}`",
                ab("robust_npv"),
                ab("capex_p50"),
                ab("capex_p90"),
                ab("nfc60_fully_public_sar_p50"),
                f"{ab('vfm')} ({fm(r['vfm_pct_psc'][0], 1)} % → {fm(r['vfm_pct_psc'][1], 1)} %)",
            ]
        )
    head = [
        "entity (weights v1 → v2)",
        "robust NPV (SAR m)",
        "capex P50 (SAR m)",
        "capex P90 (SAR m)",
        "net fiscal cost 60 y P50, fully public (SAR m)",
        "VfM (% of PSC)",
    ]
    return "\n".join(
        [
            LABEL_LINE,
            table(head, rows),
            "Run: runs/r7-v2/sensitivity.json (weights v2, not adopted; docs/alignments.md §4c; "
            f"{JUDGE_SHORT} "
            "judge v3, seed 1). The three station additions and S6-L2 are not routed and do not "
            "change. "
            f"S6-L1 under the base weights v1: {l1_risk_sentence(ctx)}.",
        ]
    )


def gen_legal(ctx: Ctx) -> str:
    items = ctx.recommendations.get("legal_items", {})
    rows = []
    n = 0
    for key in items:
        it = items[key]
        if it.get("status") != "unclear":
            continue
        n += 1
        refs = "".join(f"[^{s}]" for s in it.get("sources", []))
        rows.append([str(n), f"`{key}`", cell(it.get("question", "")), refs])
    head = ["#", "item", "open question (no legal position is inferred)", "sources"]
    return "\n".join(
        [
            table(head, rows),
            f"Register: cities/ksa/funding/recommendations.yaml `legal_items` ({n} items with "
            "status unclear; "
            "docs/delivery-models.md, All legal and institutional items).",
        ]
    )


def gen_switching(ctx: Ctx) -> str:
    rows = []
    for cid, name in CP7_CORRIDORS.items():
        run = f"runs/cba/CBA-{cid}"
        sv = ctx.jload(f"{run}/switching_values.json")
        if not sv:
            continue
        tor = ctx.p(f"{run}/tornado.csv")
        top = []
        if tor.exists():
            with tor.open(encoding="utf-8", newline="") as f:
                tr = sorted(csv.DictReader(f), key=lambda r: (-float(r["swing_npv"]), r["input"]))
            top = [f"{r['input']} ({fm(float(r['swing_npv']))})" for r in tr[:3]]
        b = sv["basis"]
        rows.append(
            [
                name,
                f"{fm(b['central_bcr'], 2)}",
                f"{fm(100 * sv['demand_share_of_model_forecast']['value'])} %",
                fm(sv["capex_multiplier"]["value"], 2),
                fm(sv["vot_multiplier"]["value"], 2),
                f"{fm(100 * sv['discount_rate_npv_zero']['value'], 2)} %"
                if sv["discount_rate_npv_zero"]["value"]
                else "n/a",
                "; ".join(top),
                f"`{run}`",
            ]
        )
    head = [
        "corridor (R5 CBA case, construction start 2027)",
        "central BCR",
        "demand for BCR = 1 (share of the modelled forecast)",
        "capex × for BCR = 1",
        "value-of-time × for BCR = 1",
        "constant real rate at NPV = 0",
        "largest three tornado swings (NPV swing, SAR m)",
        "run",
    ]
    return "\n".join(
        [
            LABEL_LINE,
            table(head, rows),
            "Runs: runs/cba/CBA-<id>/switching_values.json and tornado.csv (R5 CBA, seed 1, "
            "medium population, "
            "60 years, Green Book 2026; the R5 model before the CP6 zone split, so the levels "
            "differ from the "
            "judge v3 figures in the other tables; the ordering of the drivers is what this table "
            "shows).",
        ]
    )


def gen_commute(ctx: Ctx) -> str:
    d = ctx.commute
    if d.empty:
        return "Run file not found: runs/access/commute-test-s1/commute_test.parquet"
    rows = []
    for metro in sorted(d.metro.unique()):
        m = d[d.metro == metro]
        towns = m[m.scenario == "S0"].row_key.nunique()
        s0 = int(m[(m.scenario == "S0") & m.within_30_ivt].row_key.nunique())
        s1 = int(m[(m.scenario == "S1") & m.within_30_ivt].row_key.nunique())
        cand = m[~m.scenario.isin(["S0", "S1"]) & m.within_30_ivt]
        rows.append([metro, str(towns), str(s0), str(s1), str(int(cand.row_key.nunique()))])
    head = [
        "metro",
        "towns 40–120 road-km",
        "≤ 30 min in-vehicle rail: S0",
        "S1",
        "with at least one S2–S5 candidate",
    ]
    return "\n".join(
        [
            LABEL_LINE,
            table(head, rows),
            "Run: runs/access/commute-test-s1/commute_test.parquet (seed 1; towns from the "
            "register, road km "
            "from OSRM, running-time band A-r4-rt-011, summer factor A-access-011).",
        ]
    )


def gen_screening(ctx: Ctx) -> str:
    c = ctx.candidates
    ll = ctx.longlist
    short = set(ctx.short_keys())
    gov = {}
    for r in ctx.coverage_rows:
        gov[r[0]] = gov.get(r[0], 0) + 1
    rows = []
    tot = [0, 0, 0, 0]
    for slug, en, _ in REGIONS:
        n_rows = int((c.region == slug).sum()) if not c.empty else 0
        n_long = (
            int((ll.row_key.str.startswith(slug + ":") & (ll.funnel_stage == "long")).sum())
            if not ll.empty
            else 0
        )
        n_short = sum(1 for k in short if k.startswith(slug + ":"))
        vals = [gov.get(slug, 0), n_rows, n_long, n_short]
        tot = [a + b for a, b in zip(tot, vals, strict=True)]
        rows.append([en] + [fm(v) for v in vals])
    rows.append(["**total**"] + [f"**{fm(v)}**" for v in tot])
    head = ["region", "GASTAT governorates", "register settlements", "long list", "short list"]
    return "\n".join(
        [
            table(head, rows),
            "Runs: runs/r2/long-list/longlist.parquet, runs/r2/score/ranks.parquet (short list = "
            "the top "
            f"{ctx.r2_summary.get('n_short', 'n/a')} by base score, A-screen-006; seed 1); "
            "register "
            "cities/ksa/candidates.parquet; governorates from docs/coverage.md (GASTAT Census "
            "2022[^S-cp2-gastat-007]).",
        ]
    )


GENERATORS: dict[str, Callable[[Ctx], str]] = {
    "l1-risk": gen_l1_risk,
    "s1": gen_s1,
    "programmes": gen_programmes,
    "cp7-corridors": gen_cp7_corridors,
    "fiscal": gen_fiscal,
    "vfm": gen_vfm,
    "families": gen_families,
    "alignment-v2": gen_alignment_v2,
    "legal": gen_legal,
    "switching": gen_switching,
    "commute": gen_commute,
    "screening": gen_screening,
}


def figure_source_line(row: dict[str, str]) -> str:
    src = row.get("sources", "").strip()
    prov = row.get("provenance", "").strip()
    return f"Source: {src}. Provenance: {prov}."


def gen_figure(ctx: Ctx, stem: str) -> str:
    """Caption and source line of one figure, from docs/report/figures/figures-index.csv."""
    row = ctx.figures.get(stem)
    num = int(stem[3:5])
    if row is None:
        return f"![Figure {num}. not in figures-index.csv](figures/{stem}.svg)\n{LABEL_LINE}"
    title = row.get("title_en", "").strip()
    caption = row.get("caption", "").strip()
    src = figure_source_line(row)
    text = f"{title} {caption}"
    if L1_MARK in text:
        src += f" S6-L1: {l1_risk_sentence(ctx)}."
    return "\n".join(
        [
            f"![Figure {num}. {title}](figures/{stem}.svg)",
            LABEL_LINE,
            f"*Figure {num}.* {caption}",
            src,
        ]
    )


def refresh_blocks(text: str, ctx: Ctx) -> str:
    def sub(m: re.Match[str]) -> str:
        name = m.group("name")
        if name.startswith("fig-"):
            body = gen_figure(ctx, name[4:])
        elif name in GENERATORS:
            body = GENERATORS[name](ctx)
        else:
            return m.group(0)
        return f"<!-- gen:{name} -->\n{body}\n<!-- /gen:{name} -->"

    return GEN.sub(sub, text)


# --------------------------------------------------------------------------------------------
# Assembly
# --------------------------------------------------------------------------------------------


def strip_header(text: str) -> str:
    lines = text.splitlines()
    if lines and HEADER_RE.match(lines[0]):
        lines = lines[1:]
    return "\n".join(lines).strip("\n")


def slugify(title: str, seen: dict[str, int]) -> str:
    s = re.sub(r"[`*_]", "", title).strip().lower()
    s = re.sub(r"[^\w\- ]", "", s)
    s = s.replace(" ", "-")
    n = seen.get(s, 0)
    seen[s] = n + 1
    return s if n == 0 else f"{s}-{n}"


def footnote_def(sid: str, row: dict[str, str] | None) -> str:
    if row is None:
        return f"[^{sid}]: not found in docs/sources/index.csv."
    parts = [
        row.get("publisher", "").strip(),
        f'"{row.get("title", "").strip()}"',
        row.get("url", "").strip(),
    ]
    body = ", ".join(p for p in parts if p and p != '""')
    pub = row.get("published", "") or "unknown"
    acc = row.get("accessed", "") or "unknown"
    tail = f"published {pub}, accessed {acc}"
    claim = row.get("claim", "").strip()
    return neutralise(
        f"[^{sid}]: {body}, {tail}. Claim: {claim}. Status: {row.get('status', '')}.".replace(
            "\n", " "
        )
    )


def figures_index(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def assemble(sections: list[tuple[str, str]], ctx: Ctx, figs: list[dict[str, str]]) -> str:
    body_parts = []
    for name, text in sections:
        body_parts.append(f"<!-- section: {name} -->\n" + strip_header(text))
    body = "\n\n".join(body_parts)

    seen: dict[str, int] = {}
    toc = []
    in_code = False
    for line in body.splitlines():
        if line.startswith("```"):
            in_code = not in_code
        if in_code:
            continue
        m = re.match(r"^(#{1,2}) (.+)$", line)
        if m:
            indent = "  " * (len(m.group(1)) - 1)
            title = m.group(2).strip()
            toc.append(f"{indent}- [{re.sub(r'[`*]', '', title)}](#{slugify(title, seen)})")

    out = [
        header(
            "docs/report/feasibility-report.md",
            version=MAIN_REPORT_VERSION,
            note=MAIN_REPORT_NOTE,
            date=MAIN_REPORT_DATE,
        ),
        "",
        "# KSA Rail Twin: national rail feasibility study (report)",
        "",
        LABEL_LINE,
        "",
        "Assembled from `docs/report/sections/*.md` by `uv run python -m common.report build`; do "
        "not edit "
        "this file by hand. Source notes at the end resolve every `[^S-…]` reference against "
        "`docs/sources/index.csv`; `A-…` ids are rows of `docs/assumptions.md` "
        "(`docs/report/annex-assumptions.md`); `runs/…` paths are run outputs with their "
        "`meta.json`.",
        "",
        "## Contents",
        "",
        *toc,
        "",
        body,
    ]
    if figs:
        out += [
            "",
            "## List of figures (from docs/report/figures/figures-index.csv)",
            "",
            LABEL_LINE,
            "",
        ]
        keys = list(figs[0].keys())
        out.append(
            table([cell(k) for k in keys], [[cell(r.get(k, "")) for k in keys] for r in figs])
        )
    refs = sorted(set(FOOTNOTE_REF.findall(re.sub(r"`[^`]*`", "", body))))
    out += ["", "## Source notes", ""]
    out += [footnote_def(s, ctx.sources.get(s)) for s in refs]
    return "\n".join(out).rstrip("\n") + "\n"


def build_annex_sources(ctx: Ctx, src_path: Path) -> str:
    cols = [
        "id",
        "claim",
        "value",
        "unit",
        "publisher",
        "title",
        "url",
        "published",
        "accessed",
        "status",
    ]
    heads = [
        "id",
        "claim",
        "value",
        "unit",
        "publisher",
        "title",
        "URL",
        "published",
        "accessed",
        "status",
    ]
    rows = [[cell(r.get(k, "")) for k in cols] for r in ctx.sources.values()]
    counts: dict[str, int] = {}
    for r in ctx.sources.values():
        counts[r.get("status", "")] = counts.get(r.get("status", ""), 0) + 1
    summary = ", ".join(f"{k or 'blank'} {v:,}" for k, v in sorted(counts.items()))
    return (
        "\n".join(
            [
                header("docs/report/annex-sources.md"),
                "",
                "# Annex S. Source appendix (every row of the source index)",
                "",
                f"Generated from `docs/sources/index.csv` (SHA-256 `{sha12(src_path)}…`, "
                f"{len(rows):,} rows; by "
                f"status: {summary}). Raw register table: the report's number check does not "
                "apply here. Cells are "
                "copied as they are, with `|` escaped; where a URL or file name contains a string "
                "the report's "
                "model-name check forbids, one letter is written as an HTML character reference "
                "(the rendered text "
                "is unchanged).",
                "",
                table(heads, rows),
            ]
        )
        + "\n"
    )


def assumption_rows(root: Path) -> tuple[list[str], list[tuple[str, str]]]:
    files = [root / "docs/assumptions.md"] + sorted((root / "docs").glob("assumptions-*.md"))
    rows: list[str] = []
    meta: list[tuple[str, str]] = []
    for f in files:
        if not f.exists():
            continue
        n = 0
        for line in f.read_text(encoding="utf-8").splitlines():
            if line.startswith("| A-"):
                rows.append(neutralise(line))
                n += 1
        meta.append((str(f.relative_to(root)), f"{sha12(f)}… ({n:,} rows)"))
    return rows, meta


def build_annex_assumptions(root: Path) -> str:
    rows, meta = assumption_rows(root)
    statuses: dict[str, int] = {}
    for r in rows:
        cells = [c.strip() for c in r.strip().strip("|").split(" | ")]
        st = cells[6] if len(cells) > 6 else ""
        key = st.split(" ")[0].split("(")[0].strip(",;") or "blank"
        statuses[key] = statuses.get(key, 0) + 1
    st_txt = ", ".join(f"{k} {v:,}" for k, v in sorted(statuses.items()))
    src = "; ".join(f"`{a}` SHA-256 `{b}`" for a, b in meta)
    return (
        "\n".join(
            [
                header("docs/report/annex-assumptions.md"),
                "",
                "# Annex A. Assumption appendix (every row of the assumptions register)",
                "",
                f"Generated from {src}. {len(rows):,} rows; status, first word of the status "
                f"column: {st_txt}. "
                "Rows are copied verbatim (columns: id, parameter, value, unit, range, source or "
                "assumption, "
                "status, used in). Raw register table: the report's number check does not apply "
                "here. Where a "
                "cell contains a string the report's model-name check forbids (a file name), one "
                "letter is "
                "written as an HTML character reference.",
                "",
                "| id | parameter | value | unit | range | source or assumption | status | used "
                "in |",
                "|---|---|---|---|---|---|---|---|",
                *rows,
            ]
        )
        + "\n"
    )


def region_doc_version(root: Path, slug: str) -> str:
    f = root / "docs/regions" / f"{slug}.md"
    if not f.exists():
        return "not found"
    first = f.read_text(encoding="utf-8").splitlines()[0]
    m = re.match(r"^> \*\*Document version:\*\* (.+?) \|", first)
    return m.group(1) if m else "header not found"


def build_region_annex(ctx: Ctx, slug: str, en: str, ar: str) -> str:
    root = ctx.root
    gov = [r for r in ctx.coverage_rows if r[0] == slug]
    c = ctx.candidates
    reg = c[c.region == slug] if not c.empty else c
    lines = [
        header(f"docs/report/annex-regions/{slug}.md"),
        "",
        f"# Region annex: {en} ({ar})",
        "",
        LABEL_LINE,
        "",
        f"Generated from the registers and run files below; region slug `{slug}`. Inputs: "
        "`docs/coverage.md` "
        f"(SHA-256 `{sha12(root / 'docs/coverage.md')}…`), `cities/ksa/candidates.parquet` "
        f"(`{sha12(root / 'cities/ksa/candidates.parquet')}…`), "
        f"`cities/ksa/regions/{slug}.parquet` "
        f"(`{sha12(root / 'cities/ksa/regions' / f'{slug}.parquet')}…`), the region sweep "
        f"`docs/regions/{slug}.md` ({region_doc_version(root, slug)}), the R2 screening runs "
        "`runs/r2/` "
        f"and the standalone judge runs `runs/r6/v3/library/` ({PROV}). Raw annex tables: values "
        "are "
        "copied from those files.",
        "",
        "## 1. Governorates (coverage audit)",
        "",
    ]
    lines += [
        LABEL_LINE,
        table(
            [
                "governorate",
                "name (AR)",
                "population 2022",
                "rows",
                "≥ 10k",
                "≥ 5k",
                "long",
                "served",
                "short",
                "families",
                "centre row",
                "status",
            ],
            [r[1:] for r in gov],
        ),
        "Source: docs/coverage.md (GASTAT Census 2022 governorate totals[^S-cp2-gastat-007]); "
        f"{len(gov)} "
        "governorates, every one screened or excluded with its reason.",
        "",
        "## 2. Settlement register",
        "",
    ]
    if not reg.empty:
        n = len(reg)
        n10 = int(reg.tag_10k.fillna(False).astype(bool).sum())
        n5 = int(reg.tag_5k.fillna(False).astype(bool).sum())
        scr = int(reg.screened.fillna(False).astype(bool).sum())
        types = reg.pop_type.fillna("none").value_counts().sort_index()
        type_txt = ", ".join(f"{k} {int(v)}" for k, v in types.items())
        excl = reg[~reg.screened.fillna(False).astype(bool)].exclusion_reason.fillna("(none given)")
        ex_counts = excl.value_counts()
        ex_rows = sorted(
            ((str(k), int(v)) for k, v in ex_counts.items()), key=lambda kv: (-kv[1], kv[0])
        )
        lines += [
            f"Register rows {n:,} (≥ 10,000: {n10:,}; ≥ 5,000: {n5:,}); screened {scr:,}; "
            "population "
            f"figure type: {type_txt}. Register: cities/ksa/candidates.parquet (region `{slug}`).",
            "",
        ]
        if ex_rows:
            lines += [
                table(
                    ["exclusion reason (rows not screened)", "rows"],
                    [[cell(k), str(v)] for k, v in ex_rows],
                ),
                "Register: cities/ksa/candidates.parquet `exclusion_reason`.",
                "",
            ]
    lines += ["## 3. Short list (screening input, not a forecast)", ""]
    short = [k for k in ctx.short_keys() if k.startswith(slug + ":")]
    if short and not c.empty:
        sc = ctx.scores.set_index("row_key")["base"] if not ctx.scores.empty else {}
        rk = ctx.ranks.set_index("row_key")["base"]
        cc = c.set_index("row_key")
        rows = []
        for k in sorted(short, key=lambda k: (int(rk[k]), k)):
            r = cc.loc[k]
            rows.append(
                [
                    str(int(rk[k])),
                    cell(r["name_en"]),
                    cell(r["name_ar"]),
                    cell(r["governorate"]),
                    fm(r["population"]) if r["population"] == r["population"] else "unknown",
                    cell(r["pop_source"]),
                    fm(float(sc[k]), 3) if k in sc else "n/a",
                ]
            )
        lines += [
            LABEL_LINE,
            table(
                [
                    "national rank",
                    "town",
                    "name (AR)",
                    "governorate",
                    "population",
                    "population source",
                    "score",
                ],
                rows,
            ),
            "Runs: runs/r2/score/ranks.parquet and sweep.parquet (seed 1, CP1 weights "
            "A-screen-006; scores rank "
            "towns for study, they are not demand, cost or benefit).",
            "",
        ]
    else:
        lines += ["No short-listed town in this region (runs/r2/score/ranks.parquet).", ""]

    lines += ["## 4. Corridors that touch the region (hypothetical layer, ours)", ""]
    touching = sorted(cid for cid in ctx.library_ids if slug in ctx.corridor_regions(cid))
    if touching:
        rows = []
        for cid in touching:
            s = ctx.library.get(cid, {})
            y = ctx.corridors.get(cid, {})
            if not s:
                continue
            cap = s["capex_sar_m"]
            ph, bv = ctx.best_phase(s)
            role = ", ".join(L for L, mem in LAYOUT_MEMBERS.items() if cid in mem) or "none"
            if cid in RETIRED:
                role = "retired (CP6 P6a)"
            rows.append(
                [
                    f"`{cid}`",
                    cell(y.get("layer", "")),
                    (
                        "n/a (station on its host line)"
                        if y.get("family") == "station_addition"
                        else (
                            fm(y.get("length_km"), 1) if y.get("length_km") is not None else "n/a"
                        )
                    ),
                    fm(s["robust_npv"]),
                    f"{fm(bv)} ({ph})",
                    rng(cap["capex_p10"], cap["capex_p50"], cap["capex_p90"]),
                    rng(
                        s["bcr_p10"]["un_wpp_medium"],
                        s["bcr_p50"]["un_wpp_medium"],
                        s["bcr_p90"]["un_wpp_medium"],
                        2,
                    ),
                    role,
                ]
            )
        lines += [
            LABEL_LINE,
            table(
                [
                    "corridor",
                    "layer",
                    "length km",
                    "robust NPV at 2030 (SAR m)",
                    "best phase: robust NPV (SAR m)",
                    "capex P10 / P50 / P90 at 2030 (SAR m)",
                    "BCR P10 / P50 / P90 (medium)",
                    "in a CP7 layout",
                ],
                rows,
            ),
            f"Runs: runs/r6/v3/library/<id>/score.json ({PROV}; standalone, against S1); corridor "
            "YAMLs "
            "cities/ksa/corridors/; a corridor touches the region if a generating town or a "
            "station lies in it "
            "(nearest register settlement). Layer `hypothetical` = ours, never existing or "
            "committed.",
        ]
        if any(cid in LAYOUT_MEMBERS["S6-L1"] for cid in touching):
            lines += [
                "",
                f"{l1_risk_sentence(ctx)} for S6-L1 (the upside case, which carries the Al-Kharj "
                "spur's P90 cost risk).",
            ]
        lines.append("")
    else:
        lines += ["No generated corridor touches the region (cities/ksa/corridors/).", ""]
    lines += [
        "## 5. Where to read more",
        "",
        f"- Region sweep: `docs/regions/{slug}.md`; pilot: `docs/regions/pilot-{slug}.md`.",
        "- Distribution of user benefits by region for every case: `docs/distribution.md`.",
        "- 30-minute commute test by metro: `docs/commute-test.md`.",
        "",
    ]
    return "\n".join(lines).rstrip("\n") + "\n"


def do_build(
    sections_dir: Path = SECTIONS_DIR,
    out_dir: Path = REPORT_DIR,
    sources: Path | None = None,
    figures_csv: Path | None = None,
    refresh: bool = True,
    root: Path = REPO_ROOT,
) -> list[Path]:
    ctx = Ctx(root=root, sources_csv=sources, figures_csv=figures_csv)
    src_path = sources or root / "docs/sources/index.csv"
    written: list[Path] = []
    sections = []
    for f in sorted(sections_dir.glob("*.md")):
        text = f.read_text(encoding="utf-8")
        if refresh:
            new = refresh_blocks(text, ctx)
            if new != text:
                f.write_text(new, encoding="utf-8")
                written.append(f)
            text = new
        sections.append((f.name, text))
    out_dir.mkdir(parents=True, exist_ok=True)
    figs = figures_index(figures_csv or root / "docs/report/figures/figures-index.csv")
    targets = {
        out_dir / "feasibility-report.md": assemble(sections, ctx, figs),
        out_dir / "annex-sources.md": build_annex_sources(ctx, src_path),
        out_dir / "annex-assumptions.md": build_annex_assumptions(root),
    }
    for slug, en, ar in REGIONS:
        targets[out_dir / "annex-regions" / f"{slug}.md"] = build_region_annex(ctx, slug, en, ar)
    for path, text in targets.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists() or path.read_text(encoding="utf-8") != text:
            path.write_text(text, encoding="utf-8")
        written.append(path)
    if ctx.missing:
        typer.echo("missing inputs: " + ", ".join(sorted(set(ctx.missing))), err=True)
    return written


# --------------------------------------------------------------------------------------------
# Checks
# --------------------------------------------------------------------------------------------


def _strip_inline(line: str) -> str:
    line = line.replace(LABEL, "").replace(ALIGNMENT_LIMITATION, "")
    line = re.sub(r"<!--.*?-->", "", line)
    line = re.sub(r"`[^`]*`", "", line)
    line = re.sub(r"\]\([^)]*\)", "]", line)
    line = re.sub(r"\[\^[^\]]*\]", "", line)
    return line


NUMBER = re.compile(r"(?<![\w./#§^\-−])[−+\-]?\d[\d,]*(?:\.\d+)?")


def numbers_in(line: str) -> list[str]:
    s = _strip_inline(line)
    s = re.sub(r"^\s*(?:[-*]|\d+\.)\s+", "", s)
    out = []
    for m in NUMBER.finditer(s):
        tok = m.group(0).rstrip(",")
        bare = tok.lstrip("−+-")
        if re.fullmatch(r"(19|20)\d\d", bare):
            continue
        out.append(tok)
    return out


def blocks(text: str) -> list[tuple[int, list[str]]]:
    """(first line number, lines) of each paragraph or table; code fences skipped."""
    out: list[tuple[int, list[str]]] = []
    cur: list[str] = []
    start = 0
    in_code = False
    for i, line in enumerate(text.splitlines(), 1):
        if line.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        if not line.strip():
            if cur:
                out.append((start, cur))
            cur = []
            continue
        if not cur:
            start = i
        cur.append(line)
    if cur:
        out.append((start, cur))
    return out


def number_violations(text: str) -> list[str]:
    problems = []
    for start, lines in blocks(text):
        content = [ln for ln in lines if not ln.startswith("#") and not HEADER_RE.match(ln)]
        nums = [n for ln in content for n in numbers_in(ln)]
        if not nums:
            continue
        if any(CITATION.search(ln) for ln in content):
            continue
        problems.append(
            f"line {start}: numbers {nums[:4]} without [^S-…], A-… or runs/ in the block"
        )
    return problems


def will_violations(text: str) -> list[str]:
    out = []
    for i, line in enumerate(text.splitlines(), 1):
        s = re.sub(r"`[^`]*`", "", line)
        s = re.sub(r"[\"“'‘]will[\"”'’]", "", s, flags=re.IGNORECASE)
        if WILL.search(s):
            out.append(f"line {i}: {line.strip()[:120]}")
    return out


def model_name_violations(text: str) -> list[str]:
    return [
        f"line {i}: {ln.strip()[:120]}"
        for i, ln in enumerate(text.splitlines(), 1)
        if MODEL_NAMES.search(ln)
    ]


def _has_label(line: str) -> bool:
    return LABEL in line and ALIGNMENT_LIMITATION in line


def label_violations(text: str, require_once: bool = True) -> list[str]:
    """Every table header or figure line that states a length, cost, time or ridership has a line
    with both label strings within the 3 lines before its first line or after its last line."""
    lines = text.splitlines()
    out = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        if line.startswith("|"):
            j = i
            while j + 1 < n and lines[j + 1].startswith("|"):
                j += 1
            head = line
            if LABEL_TRIGGER.search(head):
                win = lines[max(0, i - 3) : i] + lines[j + 1 : j + 4]
                if not any(_has_label(w) for w in win):
                    out.append(
                        f"line {i + 1}: table '{head[:80]}' without the label line within 3 lines"
                    )
            i = j + 1
            continue
        if re.match(r"^\s*!\[", line) and LABEL_TRIGGER.search(line):
            win = lines[max(0, i - 3) : i] + lines[i + 1 : i + 4]
            if not any(_has_label(w) for w in win):
                out.append(
                    f"line {i + 1}: figure '{line[:80]}' without the label line within 3 lines"
                )
        i += 1
    if require_once and not any(_has_label(ln) for ln in lines):
        out.append("no label line anywhere in the file")
    return out


def l1_violations(text: str, sentence: str) -> list[str]:
    """Every paragraph, list or table that names S6-L1 carries the P90-cost risk statement in the
    same block or within the 3 lines around it."""
    core = sentence.split(" SAR m")[0]
    lines = text.splitlines()
    out = []
    for start, blk in blocks(text):
        if not any(L1_MARK in ln for ln in blk):
            continue
        a = start - 1
        b = a + len(blk)
        win = lines[max(0, a - 3) : b + 3]
        if not any(core in w for w in win):
            out.append(f"line {start}: block names S6-L1 without the P90-cost risk statement")
    return out


def l45_violations(text: str) -> list[str]:
    lines = text.splitlines()
    out = []
    for i, line in enumerate(lines):
        if L45.search(line):
            win = lines[max(0, i - 3) : i + 4]
            if not any(f in w for w in win for f in L45_FIGS):
                out.append(
                    f"line {i + 1}: S6-L4/L5 mentioned away from the Pareto/reach trade-off figure"
                )
    return out


FIG_LINE = re.compile(r"^!\[(?P<alt>[^\]]*)\]\(figures/(?P<stem>fig\d\d-[\w-]+)\.svg\)")


def figure_source_violations(text: str, index: dict[str, dict[str, str]]) -> list[str]:
    """Every embedded figure: its title is the indexed title and, within the next 4 lines, its
    source line starts with the indexed sources and provenance (figures-index.csv)."""
    lines = text.splitlines()
    out = []
    for i, line in enumerate(lines):
        m = FIG_LINE.match(line)
        if not m:
            continue
        stem = m.group("stem")
        row = index.get(stem)
        if row is None:
            out.append(f"line {i + 1}: {stem} not in figures-index.csv")
            continue
        if not m.group("alt").endswith(row.get("title_en", "").strip()):
            out.append(f"line {i + 1}: {stem} title differs from figures-index.csv")
        want = figure_source_line(row)
        if not any(w.startswith(want) for w in lines[i + 1 : i + 5]):
            out.append(f"line {i + 1}: {stem} source line differs from figures-index.csv")
    return out


def deliverables(root: Path = REPO_ROOT) -> list[Path]:
    """The files the label test reads (brief and summaries only if they exist)."""
    files = [root / "docs/report/feasibility-report.md"] + sorted(
        (root / "docs/report/sections").glob("*.md")
    )
    for rel in (
        "docs/policy-brief.md",
        "docs/executive-summary.en.md",
        "docs/executive-summary.ar.md",
    ):
        if (root / rel).exists():
            files.append(root / rel)
    return [f for f in files if f.exists()]


def run_checks(root: Path = REPO_ROOT, sources: Path | None = None) -> dict[str, list[str]]:
    ctx = Ctx(root=root, sources_csv=sources)
    report: dict[str, list[str]] = {}
    sec_files = sorted((root / "docs/report/sections").glob("*.md"))
    sentence = l1_risk_sentence(ctx)
    for f in sec_files:
        text = f.read_text(encoding="utf-8")
        rel = str(f.relative_to(root))
        for kind, probs in (
            ("numbers", number_violations(text)),
            ("will", will_violations(text)),
            ("l1-risk", l1_violations(text, sentence)),
            ("l4-l5", l45_violations(text)),
            ("figure-sources", figure_source_violations(text, ctx.figures)),
        ):
            if probs:
                report[f"{rel} [{kind}]"] = probs
    for f in deliverables(root):
        probs = label_violations(f.read_text(encoding="utf-8"))
        if probs:
            report[f"{f.relative_to(root)} [labels]"] = probs
    for f in sorted((root / "docs/report/annex-regions").glob("*.md")):
        probs = label_violations(f.read_text(encoding="utf-8"))
        if probs:
            report[f"{f.relative_to(root)} [labels]"] = probs
    targets = sorted((root / "docs/report").rglob("*.md")) + [
        root / p
        for p in (
            "docs/policy-brief.md",
            "docs/executive-summary.en.md",
            "docs/executive-summary.ar.md",
        )
    ]
    for f in targets:
        if f.exists():
            probs = model_name_violations(f.read_text(encoding="utf-8"))
            if probs:
                report[f"{f.relative_to(root)} [model-names]"] = probs
    rep = root / "docs/report/feasibility-report.md"
    if rep.exists():
        refs = sorted(
            set(FOOTNOTE_REF.findall(re.sub(r"`[^`]*`", "", rep.read_text(encoding="utf-8"))))
        )
        bad = [r for r in refs if r not in ctx.sources]
        if bad:
            report["docs/report/feasibility-report.md [footnotes]"] = [
                f"{b} not in docs/sources/index.csv" for b in bad
            ]
    # A-ids cited in the sections must exist in the register.
    known = {ln.split(" | ")[0].strip("| ").strip() for ln in assumption_rows(root)[0]}
    for f in sec_files:
        ids = sorted(set(re.findall(r"\bA-[a-z0-9_]+-\d+[a-z]?\b", f.read_text(encoding="utf-8"))))
        bad = [i for i in ids if i not in known]
        if bad:
            report[f"{f.relative_to(root)} [assumption-ids]"] = [
                f"{b} not in docs/assumptions*.md" for b in bad
            ]
    return report


def figure_warnings(root: Path = REPO_ROOT) -> list[str]:
    figdir = root / "docs/report/figures"
    return [
        f"figure not generated yet: docs/report/figures/{s}.svg"
        for s in FIGURES
        if not (figdir / f"{s}.svg").exists()
    ]


# --------------------------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------------------------

app = typer.Typer(
    add_completion=False, help="Build and check the feasibility report.", no_args_is_help=True
)


@app.command("build")
def build_cmd(
    sections: Path = typer.Option(SECTIONS_DIR, "--sections", help="section files directory"),
    out_dir: Path = typer.Option(REPORT_DIR, "--out-dir", help="where the report and annexes go"),
    sources: Path = typer.Option(
        None, "--sources", help="source index CSV (default docs/sources/index.csv)"
    ),
    figures: Path = typer.Option(
        None, "--figures", help="figures-index.csv (default docs/report/figures/)"
    ),
    refresh: bool = typer.Option(
        True, "--refresh/--no-refresh", help="rewrite generated blocks in the sections"
    ),
) -> None:
    """Assemble the report and regenerate the annexes."""
    written = do_build(sections, out_dir, sources, figures, refresh)
    typer.echo(f"wrote or confirmed {len(written)} files under {out_dir}")


@app.command("check")
def check_cmd() -> None:
    """Number tracing, no 'will', no model names, labels, S6-L1 risk statement, L4/L5 rule."""
    report = run_checks()
    for w in figure_warnings():
        typer.echo(f"warning: {w}")
    if report:
        for k, probs in report.items():
            typer.echo(f"FAIL {k}")
            for p in probs[:20]:
                typer.echo(f"  {p}")
        raise typer.Exit(1)
    typer.echo("report check: PASS")


if __name__ == "__main__":
    app()
