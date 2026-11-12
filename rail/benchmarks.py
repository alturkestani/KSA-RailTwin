"""W5 benchmark tables: merge, validation, price-year conversion and the generated summary (R1b).

CLI:
  uv run python -m rail.benchmarks merge         (metrics-<slug>.csv -> metrics.csv; also overruns)
  uv run python -m rail.benchmarks validate --metrics cities/ksa/benchmarks/metrics.csv
  uv run python -m rail.benchmarks summarise --metrics cities/ksa/benchmarks/metrics.csv \
      --out docs/benchmarks/README.md
  uv run python -m rail.benchmarks normalised --out <csv>   (per-row SAR 2025 values)
  uv run python -m rail.benchmarks delta --before <csv> --out docs/benchmarks/normalisation-delta.md

Method: docs/benchmarks/METHOD.md. Conversion to SAR 2025 (A-cost-001) uses the project's ONLY price
index, `cities/ksa/costs/index.yaml` (CP2 P2a; A-cost-002; built by `costs.index_build`, which
folded in the former `index-r1b.yaml`): central = the source economy's GDP deflator (WDI) before
conversion, the 2025 rate to USD, then the peg; sensitivity = the price-year rate and the peg, then
the Saudi CPI (`-cti` factors). Series exceptions: A-cost-307. No figure is embedded here: factors,
peg and base year come from the index YAML, which carries their source and assumption ids.
"""

from __future__ import annotations

import csv
import datetime as dt
import re
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import typer
import yaml

from common import REPO_ROOT

BENCH_DIR = REPO_ROOT / "cities" / "ksa" / "benchmarks"
DOCS_DIR = REPO_ROOT / "docs" / "benchmarks"
SOURCES_DIR = REPO_ROOT / "docs" / "sources"
DEFAULT_INDEX = REPO_ROOT / "cities" / "ksa" / "costs" / "index.yaml"  # the only index (P2a)

SLUGS = [
    "france",
    "japan",
    "spain",
    "germany",
    "china",
    "south_korea",
    "italy",
    "morocco",
    "turkey",
    "uae",
    "egypt",
    "cautionary",
    "population_growth_peers",
]
SLUG_COUNTRY = {
    "france": "FRA",
    "japan": "JPN",
    "spain": "ESP",
    "germany": "DEU",
    "china": "CHN",
    "south_korea": "KOR",
    "italy": "ITA",
    "morocco": "MAR",
    "turkey": "TUR",
    "uae": "ARE",
    "egypt": "EGY",
}
METRIC_COLUMNS = [
    "row_id",
    "slug",
    "system",
    "metric",
    "scope",
    "value",
    "value_low",
    "value_high",
    "unit",
    "currency",
    "price_year",
    "year_observed",
    "source_id",
    "grade",
    "notes",
]
MERGED_COLUMNS = [*METRIC_COLUMNS, "country"]
OVERRUN_COLUMNS = [
    "obs_id",
    "project",
    "country",
    "kind",
    "baseline_desc",
    "baseline_value",
    "baseline_year",
    "outturn_desc",
    "outturn_value",
    "outturn_year",
    "unit",
    "currency",
    "price_basis",
    "ratio",
    "source_id",
    "grade",
    "notes",
]
METRICS = {
    "network_km",
    "opening_year",
    "cost_per_km",
    "cost_total",
    "ridership_annual",
    "ridership_vs_forecast",
    "farebox_recovery",
    "operating_ratio",
    "density_threshold",
    "city_size_threshold",
    "rail_share_by_distance",
    "station_spacing_km",
    "stopping_pattern",
    "cost_overrun_pct",
    "schedule_overrun_years",
    "delivery_model",
}
MONEY_METRICS = {"cost_per_km", "cost_total"}
COST_LEVELS = {"line", "average", "estimate", "package", "unbuilt", "other"}
RANGE_LEVELS = {"line", "average"}
GRADES = {"A", "B", "C", "D"}
SUMMARY_METRICS = [
    "cost_per_km",
    "ridership_vs_forecast",
    "farebox_recovery",
    "operating_ratio",
    "cost_overrun_pct",
    "schedule_overrun_years",
    "rail_share_by_distance",
    "station_spacing_km",
    "delivery_model",
]
NO_DATA = re.compile(r"no reliable data found", re.IGNORECASE)

app = typer.Typer(add_completion=False, help="W5 benchmark tables (R1b).", no_args_is_help=True)


# ---------------------------------------------------------------- io helpers
def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return [{k: (v or "").strip() for k, v in row.items()} for row in csv.DictReader(f)]


def write_csv(path: Path, rows: list[dict[str, Any]], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        w.writeheader()
        for row in rows:
            w.writerow({c: row.get(c, "") for c in columns})


def to_float(text: str) -> float | None:
    try:
        return float(str(text).replace(",", ""))
    except ValueError:
        return None


# ---------------------------------------------------------------- index
def load_index(path: Path = DEFAULT_INDEX) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


_TABLES: dict[int, dict[tuple[str, str, int, str], dict[str, Any]]] = {}


def _table(idx: dict[str, Any]) -> dict[tuple[str, str, int, str], dict[str, Any]]:
    """(method, currency, year, country or "") -> factor row of the single index."""
    key = id(idx)
    if key not in _TABLES:
        _TABLES[key] = {
            (f["method"], f["from_currency"], int(f["from_year"]), f.get("country") or ""): f
            for f in idx["factors"]
            if f["to_currency"] == idx["base"]["currency"]
            and int(f["to_year"]) == int(idx["base"]["price_year"])
        }
    return _TABLES[key]


def lookup(
    idx: dict[str, Any], method: str, currency: str, price_year: int, country: str | None
) -> dict[str, Any] | None:
    """The factor for a figure: the per-economy row where the index has one (EUR in a euro-area
    economy), else the currency row. None when the index has no factor."""
    t = _table(idx)
    return t.get((method, currency, price_year, country or "")) or t.get(
        (method, currency, price_year, "")
    )


def convert(
    value: float, currency: str, price_year: int, country: str | None, idx: dict[str, Any]
) -> dict[str, Any]:
    """SAR at the index base year: `central` (index method_central, the P2a rule) and
    `sensitivity` (method_sensitivity, `-cti`), each with the factor row used (`*_factor`).
    None where the index has no factor."""
    out: dict[str, Any] = {}
    for key, method in (
        ("central", idx["method_central"]),
        ("sensitivity", idx["method_sensitivity"]),
    ):
        f = lookup(idx, method, currency, price_year, country)
        out[key] = None if f is None else value * float(f["factor"])
        out[f"{key}_factor"] = f
    return out


# ---------------------------------------------------------------- validation
def known_source_ids(sources_dir: Path = SOURCES_DIR) -> set[str]:
    ids: set[str] = set()
    for path in sorted(sources_dir.glob("*.csv")):
        with path.open(encoding="utf-8", newline="") as f:
            for row in csv.DictReader(f):
                if row.get("id"):
                    ids.add(row["id"].strip())
    return ids


def validate_rows(rows: list[dict[str, str]], source_ids: set[str] | None = None) -> list[str]:
    problems: list[str] = []
    seen: set[str] = set()
    for i, r in enumerate(rows, start=2):
        rid = r.get("row_id") or f"line {i}"
        if rid in seen:
            problems.append(f"{rid}: duplicate row_id")
        seen.add(rid)
        if r.get("metric") not in METRICS:
            problems.append(f"{rid}: metric {r.get('metric')!r} not in the controlled list")
        for col in ("source_id", "currency", "price_year", "grade", "value"):
            if not r.get(col):
                problems.append(f"{rid}: {col} is blank")
        if r.get("grade") and r["grade"] not in GRADES:
            problems.append(f"{rid}: grade {r['grade']!r} not in A-D")
        if r.get("metric") in MONEY_METRICS:
            if r.get("currency") in ("", "n/a"):
                problems.append(f"{rid}: money row without a currency")
            py = r.get("price_year", "")
            if not re.fullmatch(r"\d{4}", py) and not (py == "unknown" and r.get("notes")):
                problems.append(
                    f"{rid}: money row needs a four-digit price year or 'unknown' + notes"
                )
        if source_ids is not None and r.get("source_id"):
            for sid in re.split(r"[;\s]+", r["source_id"]):
                if sid and sid not in source_ids:
                    problems.append(f"{rid}: source {sid} not in docs/sources/*.csv")
    return problems


# ---------------------------------------------------------------- summary
def _fmt(x: float | None, digits: int = 1, why: str = "not converted") -> str:
    return why if x is None else f"{x:,.{digits}f}"


def _dossier_stats(docs_dir: Path, slugs: list[str]) -> dict[str, dict[str, Any]]:
    out = {}
    for slug in slugs:
        path = docs_dir / f"{slug}.md"
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        out[slug] = {"exists": path.exists(), "no_data": len(NO_DATA.findall(text))}
    return out


def summarise_rows(
    rows: list[dict[str, str]],
    idx: dict[str, Any] | None,
    docs_dir: Path = DOCS_DIR,
    slugs: list[str] | None = None,
    levels: dict[str, str] | None = None,
    overruns: list[dict[str, str]] | None = None,
) -> str:
    slugs = slugs or SLUGS
    levels = levels or {}
    # A "|" inside a cell would break the Markdown tables.
    rows = [{k: (v or "").replace("|", "/") for k, v in r.items()} for r in rows]
    overruns = [{k: (v or "").replace("|", "/") for k, v in o.items()} for o in overruns or []]
    base = (
        {"currency": idx["base"]["currency"], "year": idx["base"]["price_year"]}
        if idx
        else {"currency": "SAR", "year": "n/a"}
    )
    today = dt.date.today().strftime("%d %b %Y")
    usable = [r for r in rows if r.get("grade") != "D"]
    grade_d = [r for r in rows if r.get("grade") == "D"]
    stats = _dossier_stats(docs_dir, slugs)
    lines = [
        f"> **Document version:** docs/benchmarks/README.md v1.1 | {today} | Author: "
        "rail.benchmarks summarise (generated; do not edit by hand); P2a single index by "
        "CP2_PREP | Status: draft",
        "",
        "# W5 global benchmarks: cross-country summary",
        "",
        "Generated by `uv run python -m rail.benchmarks summarise --metrics "
        "cities/ksa/benchmarks/metrics.csv --out docs/benchmarks/README.md`. Every cell traces "
        "to a row of `cities/ksa/benchmarks/metrics.csv` and its `S-bench-` source "
        "(`docs/sources/bench-*.csv`). Observed outcomes from other countries, not forecasts for "
        "Saudi Arabia. Grade D rows (unverified) are excluded from every total and range below "
        'and listed separately as "to verify". Method: `docs/benchmarks/METHOD.md`.',
        "",
        "## Dossier coverage (rule 2)",
        "",
        '| dossier | file | metric rows | grades A/B/C/D | "no reliable data found" entries |',
        "|---|---|---|---|---|",
    ]
    by_slug: dict[str, list[dict[str, str]]] = defaultdict(list)
    for r in rows:
        by_slug[r["slug"]].append(r)
    for slug in slugs:
        g = Counter(r["grade"] for r in by_slug[slug])
        st = stats.get(slug, {"exists": False, "no_data": 0})
        file_cell = f"[`{slug}.md`]({slug}.md)" if st["exists"] else "**missing**"
        grades = "/".join(str(g.get(k, 0)) for k in "ABCD")
        lines.append(
            f"| {slug} | {file_cell} | {len(by_slug[slug])} | {grades} | {st['no_data']} |"
        )
    total = Counter(r["grade"] for r in rows)
    lines += [
        "",
        f"Totals: {len(rows)} metric rows; grade A {total.get('A', 0)}, B {total.get('B', 0)}, "
        f"C {total.get('C', 0)}, D {total.get('D', 0)} (D excluded below).",
        "",
        f"## Cost per route-km (as published, and converted to {base['currency']} {base['year']})",
        "",
        "Conversion with the project's only price index, `cities/ksa/costs/index.yaml` (CP2 "
        "P2a; A-cost-002). Central: inflate with the source economy's GDP deflator (World Bank "
        "WDI) to 2025 before conversion, convert at the 2025 rate to USD, then SAR at the peg "
        "3.75 (EUR figures in a euro-area economy use that economy's deflator; series "
        "exceptions A-cost-307: EUR elsewhere uses the Eurostat EA20 deflator, AED the UAE CPI). "
        "Sensitivity (`-cti` factors): convert at the price-year rate and the peg, then inflate "
        "with the Saudi CPI. The before/after change against the former R1b routes A/B is "
        "logged in `normalisation-delta.md`. Cross-country cost comparisons are indicative: "
        "scope (rolling stock, land, stations, financing), terrain and tunnel share differ by "
        "line and are given in the scope column and the dossier. Level (from "
        "`cities/ksa/benchmarks/cost_levels.yaml`): `line` = a whole line or section, "
        "`average` = a network or speed-class average, `estimate` = the estimate at decision for "
        "a line now built, `package` = one contract or project lot, `unbuilt` = a line not yet "
        "in service, `other` = a cross-country average or model input.",
        "",
        f"| dossier | level | scope | as published | price year | grade | {base['currency']} m/km "
        f"{base['year']} central | sensitivity | factor ids | source |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]

    def order(r: dict[str, str]) -> int:
        return slugs.index(r["slug"]) if r["slug"] in slugs else len(slugs)

    cost_rows = [r for r in usable if r["metric"] == "cost_per_km"]
    converted: dict[str, list[float]] = defaultdict(list)
    for r in sorted(cost_rows, key=order):
        v = to_float(r["value"])
        conv: dict[str, Any] = {"central": None, "sensitivity": None}
        if idx and v is not None and re.fullmatch(r"\d{4}", r["price_year"]):
            conv = convert(v, r["currency"], int(r["price_year"]), r.get("country") or None, idx)
        why = (
            "not converted (price year unknown)"
            if r["price_year"] == "unknown"
            else "not converted"
        )
        level = levels.get(r["row_id"], "unclassified")
        for key in ("central", "sensitivity"):
            if conv[key] is not None and level in RANGE_LEVELS:
                converted[r["slug"]].append(conv[key])
        fids = " / ".join(
            conv[f"{k}_factor"]["id"] for k in ("central", "sensitivity") if conv.get(f"{k}_factor")
        )
        lines.append(
            f"| {r['slug']} | {level} | {r['scope']} | {r['value']} {r['currency']} {r['unit']} | "
            f"{r['price_year']} | {r['grade']} | {_fmt(conv['central'], why=why)} | "
            f"{_fmt(conv['sensitivity'], why=why)} | {fids or 'none'} | {r['source_id']} |"
        )
    if not cost_rows:
        lines.append("| (none) | | | | | | | | | |")
    lines += [
        "",
        "Range per dossier over `line` and `average` rows only, central and sensitivity pooled "
        f"(min / median / max, {base['currency']} m per route-km, {base['year']} prices). n counts "
        "converted values (two per row when both factors exist). A spread across sources and "
        "lines, not a P10/P50/P90 estimate and not a cost for any Saudi corridor:",
        "",
        "| dossier | n | min | median | max |",
        "|---|---|---|---|---|",
    ]
    for system, vals in sorted(
        converted.items(), key=lambda kv: slugs.index(kv[0]) if kv[0] in slugs else 99
    ):
        lines.append(
            f"| {system} | {len(vals)} | {_fmt(min(vals))} | {_fmt(statistics.median(vals))} | "
            f"{_fmt(max(vals))} |"
        )
    if overruns:
        lines += [
            "",
            "## Candidate reference-class observations (`overruns.csv`, grades A–C)",
            "",
            "Outturn or latest figure divided by the baseline, as recorded by the dossiers; the "
            "baseline differs by row (decision, award, earlier estimate). Candidate inputs for "
            "R1c; no uplift is set here.",
            "",
            "| obs | project | kind | baseline | latest | unit | ratio | grade | source |",
            "|---|---|---|---|---|---|---|---|---|",
        ]
        for o in overruns:
            if o.get("grade") == "D":
                continue
            lines.append(
                f"| {o['obs_id']} | {o['project']} | {o['kind']} | {o['baseline_value']} "
                f"({o['baseline_year']}) | {o['outturn_value']} ({o['outturn_year']}) | "
                f"{o['unit']} {o['currency']} | {o['ratio']} | {o['grade']} | {o['source_id']} |"
            )
        nd = sum(1 for o in overruns if o.get("grade") == "D")
        lines += ["", f"Grade D observations excluded: {nd}."]
    lines += ["", "## Other metrics (grades A–C)", ""]
    for metric in SUMMARY_METRICS[1:]:
        sel = [r for r in usable if r["metric"] == metric]
        lines += [f"### {metric}", ""]
        if not sel:
            lines += ["No grade A–C row in any dossier.", ""]
            continue
        lines += [
            "| system | scope | value | unit | year | grade | source |",
            "|---|---|---|---|---|---|---|",
        ]
        for r in sorted(sel, key=order):
            has_rng = r["value_low"] or r["value_high"]
            rng = f" ({r['value_low']}–{r['value_high']})" if has_rng else ""
            year = r["year_observed"] or r["price_year"]
            lines.append(
                f"| {r['system']} | {r['scope']} | {r['value']}{rng} | {r['unit']} | {year} | "
                f"{r['grade']} | {r['source_id']} |"
            )
        lines.append("")
    lines += [
        "## Gaps: dossiers with no grade A–C row for a core metric",
        "",
        "| dossier | missing core metrics |",
        "|---|---|",
    ]
    core = [
        "cost_per_km",
        "ridership_vs_forecast",
        "farebox_recovery|operating_ratio",
        "cost_overrun_pct",
    ]
    for slug in slugs:
        if slug == "population_growth_peers":
            continue
        have = {r["metric"] for r in by_slug[slug] if r["grade"] != "D"}
        missing = [m for m in core if not any(x in have for x in m.split("|"))]
        shown = [m.replace("|", " or ") for m in missing]
        lines.append(f"| {slug} | {', '.join(shown) if shown else 'none'} |")
    lines += ["", "## Grade D rows (to verify; excluded above)", ""]
    if grade_d:
        lines += ["| row | system | metric | value | source |", "|---|---|---|---|---|"]
        for r in grade_d:
            lines.append(
                f"| {r['row_id']} | {r['system']} | {r['metric']} | {r['value']} {r['unit']} | "
                f"{r['source_id']} |"
            )
    else:
        lines.append("None.")
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------- commands
@app.command()
def merge(bench_dir: Path = typer.Option(BENCH_DIR)) -> None:
    """Concatenate metrics-<slug>.csv and overruns-<slug>.csv into metrics.csv and overruns.csv."""
    metrics: list[dict[str, str]] = []
    overruns: list[dict[str, str]] = []
    for slug in SLUGS:
        m = bench_dir / f"metrics-{slug}.csv"
        if m.exists():
            for r in read_csv(m):
                r.setdefault("country", "")
                r["country"] = r.get("country") or SLUG_COUNTRY.get(slug, "")
                metrics.append(r)
        o = bench_dir / f"overruns-{slug}.csv"
        if o.exists():
            overruns.extend(read_csv(o))
    write_csv(bench_dir / "metrics.csv", metrics, MERGED_COLUMNS)
    write_csv(bench_dir / "overruns.csv", overruns, OVERRUN_COLUMNS)
    typer.echo(f"metrics.csv {len(metrics)} rows; overruns.csv {len(overruns)} rows")


@app.command()
def validate(metrics: Path = typer.Option(BENCH_DIR / "metrics.csv")) -> None:
    """Exit 1 on any blank required field, unknown metric or grade, or unknown source id."""
    problems = validate_rows(read_csv(metrics), known_source_ids())
    for p in problems:
        typer.echo(p)
    if problems:
        raise typer.Exit(1)
    typer.echo(f"OK: {metrics}")


@app.command()
def summarise(
    metrics: Path = typer.Option(BENCH_DIR / "metrics.csv"),
    out: Path = typer.Option(DOCS_DIR / "README.md"),
    index: Path = typer.Option(DEFAULT_INDEX),
) -> None:
    """Render the cross-country table with grades and the gaps list."""
    rows = read_csv(metrics)
    idx = load_index(index) if index.exists() else None
    levels_path = metrics.parent / "cost_levels.yaml"
    levels = yaml.safe_load(levels_path.read_text(encoding="utf-8")) if levels_path.exists() else {}
    unknown = sorted(v for v in (levels or {}).values() if v not in COST_LEVELS)
    if unknown:
        raise typer.BadParameter(f"cost_levels.yaml: unknown levels {set(unknown)}")
    ov_path = metrics.parent / "overruns.csv"
    ov = read_csv(ov_path) if ov_path.exists() else []
    text = summarise_rows(rows, idx, docs_dir=out.parent, levels=levels, overruns=ov)
    out.write_text(text, encoding="utf-8")
    typer.echo(f"wrote {out} ({len(rows)} rows)")


# ---------------------------------------------------------------- normalised values and delta
NORMALISED_COLUMNS = [
    "row_id",
    "slug",
    "level",
    "value",
    "currency",
    "price_year",
    "country",
    "central",
    "central_factor",
    "central_series",
    "sensitivity",
    "sensitivity_factor",
]


def normalised_rows(
    rows: list[dict[str, str]],
    idx: dict[str, Any],
    levels: dict[str, str] | None = None,
    slugs: list[str] | None = None,
) -> list[dict[str, Any]]:
    """The values `summarise` prints in the cost table, one dict per grade A-C cost_per_km row
    (same order), at full precision."""
    slugs = slugs or SLUGS
    levels = levels or {}

    def order(r: dict[str, str]) -> int:
        return slugs.index(r["slug"]) if r["slug"] in slugs else len(slugs)

    out = []
    sel = [r for r in rows if r.get("grade") != "D" and r["metric"] == "cost_per_km"]
    for r in sorted(sel, key=order):
        v = to_float(r["value"])
        conv: dict[str, Any] = {}
        if v is not None and re.fullmatch(r"\d{4}", r["price_year"]):
            conv = convert(v, r["currency"], int(r["price_year"]), r.get("country") or None, idx)
        cf, sf = conv.get("central_factor"), conv.get("sensitivity_factor")
        out.append(
            {
                "row_id": r["row_id"],
                "slug": r["slug"],
                "level": levels.get(r["row_id"], "unclassified"),
                "value": r["value"],
                "currency": r["currency"],
                "price_year": r["price_year"],
                "country": r.get("country", ""),
                "central": conv.get("central"),
                "central_factor": cf["id"] if cf else "",
                "central_series": cf.get("price_series", "") if cf else "",
                "sensitivity": conv.get("sensitivity"),
                "sensitivity_factor": sf["id"] if sf else "",
            }
        )
    return out


def _num(x: Any) -> float | None:
    return None if x in (None, "") else float(x)


def _pct(new: float, old: float) -> float:
    return (new - old) / old * 100.0


ROUNDING_PCT = 0.02  # |Δ%| at or below: index factors are stored to 6 decimals (costs.index_build)
EA20_CURRENCY = "EUR"


def _cause(
    measure: str, b: dict[str, str], a: dict[str, Any], old: float | None, new: float | None
) -> str:
    """Why a normalised value moved (deflator vs CPI, route A/B -> central/sensitivity)."""
    cur, py, eco = b["currency"], b["price_year"], b.get("route_a_economy", "")
    if not re.fullmatch(r"\d{4}", py):
        return "not converted before or after: price year unknown"
    if old is None and new is None:
        return f"not converted before or after: no {cur} series in either index"
    if measure == "central":
        series = a.get("central_series") or "none"
        if old is None:
            if cur == "AED":
                return (
                    "newly converted: UAE CPI (I-price-aed, A-cost-307); route A had no 2025 "
                    "UAE GDP deflator"
                )
            if cur == EA20_CURRENCY and series == "I-price-eur":
                return (
                    "newly converted: Eurostat EA20 deflator (I-price-eur, A-cost-307); route A "
                    "had no euro-area deflator for a EUR figure outside the euro area"
                )
            return f"newly converted ({series})"
        if new is None:
            return f"no longer converted: no central factor for {cur} {py}"
        if abs(_pct(new, old)) <= ROUNDING_PCT:
            return "same method and same WDI deflator (route A = central); factor rounding to 6 dp"
        return f"deflator series or exchange-rate row changed: route A {eco} -> {series}"
    # sensitivity
    if old is None:
        return "newly converted: convert-then-inflate factor exists where route B did not"
    if new is None:
        if int(py) < 2000:
            return (
                "no longer converted: the sensitivity needs the Saudi CPI at the price year "
                "(series from 2000, S-cost-idx-001); route B used the US deflator"
            )
        return f"no longer converted: no -cti factor for {cur} {py}"
    if cur == "USD":
        return (
            "route B = route A for USD (US GDP deflator) -> sensitivity: peg, then Saudi CPI "
            "(deflator vs CPI)"
        )
    return (
        "route B (price-year rate, then US GDP deflator) -> sensitivity (price-year rate, peg, "
        "then Saudi CPI): deflator vs CPI"
    )


def _f2(x: float | None) -> str:
    return "-" if x is None else f"{x:,.2f}"


def delta_markdown(
    before: list[dict[str, str]], after: list[dict[str, Any]], idx_path: str, before_path: str
) -> str:
    """Before (R1b routes A/B, index-r1b.yaml) vs after (central/sensitivity, the single index)."""
    by_id = {a["row_id"]: a for a in after}
    pairs: list[dict[str, Any]] = []
    for b in before:
        a = by_id.get(b["row_id"])
        if a is None:
            raise ValueError(f"{b['row_id']}: in the before table but not after")
        for measure, old_key in (("central", "route_a"), ("sensitivity", "route_b")):
            old, new = _num(b[old_key]), _num(a[measure])
            d = dp = None
            if old is not None and new is not None:
                d, dp = new - old, _pct(new, old)
            printed_changed = (f"{old:,.1f}" if old is not None else "-") != (
                f"{new:,.1f}" if new is not None else "-"
            )
            pairs.append(
                {
                    "row": b,
                    "after": a,
                    "measure": measure,
                    "old_label": "route A" if measure == "central" else "route B",
                    "old": old,
                    "new": new,
                    "d": d,
                    "dp": dp,
                    "changed": printed_changed,
                    "cause": _cause(measure, b, a, old, new),
                }
            )
    extra = sorted(set(by_id) - {b["row_id"] for b in before})
    both = [p for p in pairs if p["dp"] is not None]
    n_none = sum(p["old"] is None and p["new"] is None for p in pairs)

    def stats(sel: list[dict[str, Any]]) -> str:
        v = [abs(p["dp"]) for p in sel if p["dp"] is not None]
        if not v:
            return "n/a"
        return f"max {max(v):.3f} %, median {statistics.median(v):.3f} % (n = {len(v)})"

    today = dt.date.today().strftime("%d %b %Y")
    lines = [
        f"> **Document version:** docs/benchmarks/normalisation-delta.md v1.0 | {today} | Author: "
        "rail.benchmarks delta (generated; do not edit by hand), CP2_PREP item 2 | Status: draft",
        "",
        "# R1b benchmark normalisation: before vs after the single price index (CP2 P2a)",
        "",
        "Generated by `uv run python -m rail.benchmarks delta --before "
        f"{before_path} --out docs/benchmarks/normalisation-delta.md` (index `{idx_path}`). "
        "**Before** = the committed R1b conversion (`index-r1b.yaml`, A-bench-001: route A = "
        "source-economy GDP deflator then the 2025 rate and the peg; route B = price-year rate "
        "then the US GDP deflator and the peg), recomputed at full precision from the pre-P2a "
        f"code ({len(before)} rows) by `runs/cp2_prep/item2/before_normalised.py`, which checks "
        "every value cell by cell against the committed pre-P2a `README.md` at 1 dp and exits "
        "non-zero on any mismatch. **After** = `cities/ksa/costs/index.yaml`, the only index "
        "(CP2 P2a, "
        "A-cost-002): central = source-economy GDP deflator (WDI) before conversion, then the 2025 "
        "rate and the peg; sensitivity = price-year rate and the peg, then the Saudi CPI. Route A "
        "is compared with central, route B with sensitivity. Values: SAR million per route-km at "
        "2025 prices. Only `cost_per_km` rows of grade A-C were normalised before and after "
        "(`cost_total` and other metrics are not converted by `summarise`); these are observed "
        "outcomes abroad, not costs for a Saudi corridor, and not P10/P50/P90 estimates.",
        "",
        "## Summary",
        "",
        f"- Rows: {len(before)}; value pairs (row x measure): {len(pairs)}; pairs with a value "
        f"before and after: {len(both)}. Rows only in the after table: {len(extra)}.",
        f"- Changed (the 1-dp value printed in `README.md` differs, or a value appears or "
        f"disappears): {sum(p['changed'] for p in pairs)} of {len(pairs)} "
        f"(central {sum(p['changed'] for p in pairs if p['measure'] == 'central')}, "
        f"sensitivity {sum(p['changed'] for p in pairs if p['measure'] == 'sensitivity')}).",
        f"- |Δ%| over pairs with both values: all {stats(both)}; central vs route A "
        f"{stats([p for p in both if p['measure'] == 'central'])}; sensitivity vs route B "
        f"{stats([p for p in both if p['measure'] == 'sensitivity'])}.",
        f"- Newly converted: {sum(p['old'] is None and p['new'] is not None for p in pairs)}; "
        f"no longer converted: {sum(p['old'] is not None and p['new'] is None for p in pairs)}; "
        f"not converted before or after: {n_none}.",
        "",
        "| cause | pairs | changed | max |Δ%| |",
        "|---|---|---|---|",
    ]
    by_cause: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for p in pairs:
        by_cause[p["cause"]].append(p)
    for cause, sel in sorted(by_cause.items(), key=lambda kv: -len(kv[1])):
        v = [abs(p["dp"]) for p in sel if p["dp"] is not None]
        mx = f"{max(v):.3f} %" if v else "n/a"
        lines.append(f"| {cause} | {len(sel)} | {sum(p['changed'] for p in sel)} | {mx} |")
    lines += [
        "",
        "## Per-dossier range (`line` and `average` rows, both measures pooled)",
        "",
        "| dossier | n before | min / median / max before | n after | min / median / max after "
        "| Δ median % |",
        "|---|---|---|---|---|---|",
    ]

    def pooled(sel: list[dict[str, Any]], key: str) -> dict[str, list[float]]:
        out: dict[str, list[float]] = defaultdict(list)
        for p in sel:
            if p[key] is not None and p["row"]["level"] in RANGE_LEVELS:
                out[p["row"]["slug"]].append(p[key])
        return out

    pb, pa = pooled(pairs, "old"), pooled(pairs, "new")
    for slug in [s for s in SLUGS if s in pb or s in pa]:
        b_, a_ = pb.get(slug, []), pa.get(slug, [])

        def mmm(v: list[float]) -> str:
            return f"{min(v):,.1f} / {statistics.median(v):,.1f} / {max(v):,.1f}" if v else "-"

        dm = f"{_pct(statistics.median(a_), statistics.median(b_)):+.2f}" if a_ and b_ else "n/a"
        lines.append(f"| {slug} | {len(b_)} | {mmm(b_)} | {len(a_)} | {mmm(a_)} | {dm} |")
    lines += [
        "",
        "## Every normalised value",
        "",
        "| row | dossier | level | as published | price year | country | measure | before | "
        "after | Δ | Δ % | series before -> after | factor (after) | cause |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for p in pairs:
        b, a = p["row"], p["after"]
        fid = a["central_factor"] if p["measure"] == "central" else a["sensitivity_factor"]
        dp = "-" if p["dp"] is None else f"{p['dp']:+.3f}"
        if p["measure"] == "central":
            ser = f"deflator {b.get('route_a_economy') or '?'} -> {a['central_series'] or 'none'}"
        else:
            ser = "US deflator -> I-price-sar (Saudi CPI)"
        lines.append(
            f"| {b['row_id']} | {b['slug']} | {b['level']} | {b['value']} {b['currency']} | "
            f"{b['price_year']} | {b['country'] or '-'} | {p['old_label']} -> {p['measure']} | "
            f"{_f2(p['old'])} | {_f2(p['new'])} | {_f2(p['d'])} | {dp} | {ser} | {fid or 'none'} | "
            f"{p['cause']} |"
        )
    lines.append("")
    return "\n".join(lines)


def _levels(metrics: Path) -> dict[str, str]:
    path = metrics.parent / "cost_levels.yaml"
    return (yaml.safe_load(path.read_text(encoding="utf-8")) or {}) if path.exists() else {}


@app.command()
def normalised(
    metrics: Path = typer.Option(BENCH_DIR / "metrics.csv"),
    index: Path = typer.Option(DEFAULT_INDEX),
    out: Path = typer.Option(..., help="CSV of per-row SAR 2025 values"),
) -> None:
    """Write the per-row central and sensitivity values that `summarise` prints."""
    rows = normalised_rows(read_csv(metrics), load_index(index), _levels(metrics))
    write_csv(out, rows, NORMALISED_COLUMNS)
    typer.echo(f"wrote {out} ({len(rows)} rows)")


@app.command()
def delta(
    before: Path = typer.Option(..., help="before CSV (row_id, route_a, route_b, ...)"),
    metrics: Path = typer.Option(BENCH_DIR / "metrics.csv"),
    index: Path = typer.Option(DEFAULT_INDEX),
    out: Path = typer.Option(DOCS_DIR / "normalisation-delta.md"),
) -> None:
    """Before (R1b routes A/B) vs after (single index): every value, delta, cause, summary."""
    after = normalised_rows(read_csv(metrics), load_index(index), _levels(metrics))

    def rel(p: Path) -> str:
        r = p.resolve()
        return str(r.relative_to(REPO_ROOT)) if r.is_relative_to(REPO_ROOT) else p.name

    text = delta_markdown(read_csv(before), after, rel(index), rel(before))
    out.write_text(text, encoding="utf-8")
    typer.echo(f"wrote {out}")


if __name__ == "__main__":
    app()
