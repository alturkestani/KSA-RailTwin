"""Build `cities/ksa/costs/index.yaml`, the ONLY price and currency index of the project (CP2 P2a,
31 Oct 2026), from the raw series registered in `cities/ksa/sources.yaml` (World Bank WDI CPI, GDP
deflators and FX; Eurostat EA20 deflator). It serves the cost register (`costs.register`) and the
W5 benchmark tables (`rail.benchmarks`); the former R1b index (`index-r1b.yaml`, A-bench-001) is
folded in: its World Bank files (1985-2025, incl. PRT and the EMU exchange rate from 1999) fill the
years and economies the R1c files lack, and its source ids S-bench-idx-001..003 stay on the rows.

Base: 2025 SAR (A-cost-001). Rule (P2a; A-cost-002): SAR items are inflated with the Saudi CPI
(S-cost-idx-001, the World Bank relay of the GASTAT CPI); foreign-currency items are inflated with
the source economy's GDP deflator (World Bank WDI) BEFORE conversion, then converted at the 2025
average rate to USD and to SAR at the peg 3.75. Exceptions (A-cost-307): EUR without a euro-area
economy uses the Eurostat EA20 deflator; AED uses the UAE CPI. Two methods are written:
- `inflate_then_convert` (central, the P2a rule). EUR rows are also written per euro-area economy
  (`country:` FRA, DEU, ESP, ITA, PRT; that economy's WDI deflator), used when a figure's country
  is known (the benchmark rows); the country-less EUR row (EA20) serves the register.
- `convert_then_inflate` (sensitivity, A-cost-002): convert at the source year's average rate, then
  inflate with the Saudi CPI (ids suffixed `-cti`).
Each factor row has `id, method, from_currency, from_year, to_currency, to_year, factor, source,
price_series` and, for the per-economy EUR rows, `country` (`cost-register` skill).

CLI: uv run python -m costs.index_build --out cities/ksa/costs/index.yaml
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import typer
import yaml

from common import REPO_ROOT

RAW = REPO_ROOT / "data" / "ksa" / "costs"
RAW_BENCH = REPO_ROOT / "data" / "ksa" / "benchmarks"
OUT = REPO_ROOT / "cities" / "ksa" / "costs" / "index.yaml"
BASE_YEAR = 2025
FIRST_YEAR = 1985  # first year of the R1b World Bank files (manifest wb-wdi-*-2026-10-08)
YEARS = range(FIRST_YEAR, BASE_YEAR + 1)
PEG_YEARS = range(2000, BASE_YEAR + 1)  # the SAR rows keep the R1c span (Saudi CPI from 2000)
# Euro-area economies with a WDI GDP deflator: EUR figures located there use it (P2a).
EUR_ECONOMIES = ("FRA", "DEU", "ESP", "ITA", "PRT")
# Source ids of the R1b index rows (index-r1b.yaml, folded in at CP2 P2a).
BENCH_SRC = {"wb_defl": "S-bench-idx-001", "fx": "S-bench-idx-002", "fx_emu": "S-bench-idx-003"}

# currency -> (price series, economy code, source id of the series, FX economy code)
CURRENCIES: dict[str, dict[str, str]] = {
    "SAR": {"series": "wb_cpi", "eco": "SAU", "src": "S-cost-idx-001", "fx": "PEG"},
    "USD": {"series": "wb_defl", "eco": "USA", "src": "S-cost-idx-002", "fx": "USA"},
    "EUR": {"series": "eurostat", "eco": "EA20", "src": "S-cost-idx-004", "fx": "EMU"},
    "GBP": {"series": "wb_defl", "eco": "GBR", "src": "S-cost-idx-002", "fx": "GBR"},
    "CNY": {"series": "wb_defl", "eco": "CHN", "src": "S-cost-idx-002", "fx": "CHN"},
    "MAD": {"series": "wb_defl", "eco": "MAR", "src": "S-cost-idx-002", "fx": "MAR"},
    # UAE GDP deflator has no 2025 value in the WDI edition read; the CPI is used instead.
    "AED": {"series": "wb_cpi", "eco": "ARE", "src": "S-cost-idx-001", "fx": "ARE"},
    "JPY": {"series": "wb_defl", "eco": "JPN", "src": "S-cost-idx-002", "fx": "JPN"},
    "KRW": {"series": "wb_defl", "eco": "KOR", "src": "S-cost-idx-002", "fx": "KOR"},
    "TRY": {"series": "wb_defl", "eco": "TUR", "src": "S-cost-idx-002", "fx": "TUR"},
    "EGP": {"series": "wb_defl", "eco": "EGY", "src": "S-cost-idx-002", "fx": "EGY"},
    "CHF": {"series": "wb_defl", "eco": "CHE", "src": "S-cost-idx-002", "fx": "CHE"},
    "INR": {"series": "wb_defl", "eco": "IND", "src": "S-cost-idx-002", "fx": "IND"},
    "AUD": {"series": "wb_defl", "eco": "AUS", "src": "S-cost-idx-002", "fx": "AUS"},
    "CAD": {"series": "wb_defl", "eco": "CAN", "src": "S-cost-idx-002", "fx": "CAN"},
    "NAD": {"series": "wb_defl", "eco": "NAM", "src": "S-cost-idx-002", "fx": "NAM"},
}
# Figures priced in years after the base (2026 awards, a 2027 tariff) are treated as base-year
# prices: no 2026 annual index is published yet (A-cost-009).
# Factor = the base-year factor; id suffix `-asbase`.
LATER_YEARS = (BASE_YEAR + 1, BASE_YEAR + 2)
PEG_SAR_PER_USD = 3.75  # S-lb-020 (SAMA); A-cost-001
PEG_SOURCE = "S-lb-020"
FX_SOURCE = "S-cost-idx-003"

app = typer.Typer(add_completion=False, help="Build the cost price/FX index.")


def _wb(path: Path) -> dict[str, dict[int, float]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    out: dict[str, dict[int, float]] = {}
    for r in data[1]:
        if r["value"] is not None:
            out.setdefault(r["countryiso3code"], {})[int(r["date"])] = float(r["value"])
    return out


def _eurostat(path: Path) -> dict[int, float]:
    data = json.loads(path.read_text(encoding="utf-8"))
    pos = {str(i): int(y) for y, i in data["dimension"]["time"]["category"]["index"].items()}
    return {pos[k]: float(v) for k, v in data["value"].items()}


def _fill(
    primary: dict[str, dict[int, float]], extra: dict[str, dict[int, float]]
) -> tuple[dict[str, dict[int, float]], dict[str, set[int]]]:
    """Primary values win; `extra` fills missing (economy, year) cells. Returns the merged series
    and, per economy, the years taken from `extra` (so their source id can be cited)."""
    merged = {e: dict(v) for e, v in primary.items()}
    filled: dict[str, set[int]] = {}
    for eco, vals in extra.items():
        for y, v in vals.items():
            if y not in merged.setdefault(eco, {}):
                merged[eco][y] = v
                filled.setdefault(eco, set()).add(y)
    return merged, filled


def load_raw(raw: Path = RAW, raw_bench: Path | None = RAW_BENCH) -> dict[str, Any]:
    defl, fx = _wb(raw / "wb_NY.GDP.DEFL.ZS.json"), _wb(raw / "wb_PA.NUS.FCRF.json")
    fx_primary = {e: set(v) for e, v in fx.items()}
    filled: dict[str, dict[str, set[int]]] = {"wb_defl": {}, "fx": {}, "fx_emu": {}}
    if raw_bench is not None and (raw_bench / "wb_NY.GDP.DEFL.ZS.json").exists():
        defl, filled["wb_defl"] = _fill(defl, _wb(raw_bench / "wb_NY.GDP.DEFL.ZS.json"))
        fx, filled["fx"] = _fill(fx, _wb(raw_bench / "wb_PA.NUS.FCRF.json"))
        emu = raw_bench / "wb_EMU_PA.NUS.FCRF.json"
        if emu.exists():
            fx, filled["fx_emu"] = _fill(fx, _wb(emu))
    return {
        "wb_cpi": _wb(raw / "wb_FP.CPI.TOTL.json"),
        "wb_defl": defl,
        "fx": fx,
        "eurostat": {"EA20": _eurostat(raw / "eurostat_nama_10_gdp_EA20_PD15.json")},
        "filled": filled,
        "fx_primary": fx_primary,
    }


def _series_sources(r: dict[str, Any], series: str, eco: str, src: str) -> list[str]:
    out = [src]
    if series == "wb_defl" and r["filled"]["wb_defl"].get(eco):
        out.append(BENCH_SRC["wb_defl"])
    return out


def _fx_sources(r: dict[str, Any], eco: str) -> list[str]:
    out = [FX_SOURCE]
    if r["filled"]["fx"].get(eco):
        out.append(BENCH_SRC["fx"])
    if r["filled"]["fx_emu"].get(eco):
        out.append(BENCH_SRC["fx_emu"])
    return out


def _cite(r: dict[str, Any], kind: str, eco: str, year: int) -> list[str]:
    """Source ids for one cell: the R1b id where the R1b file filled it (index-r1b.yaml rows)."""
    if kind == "wb_defl":
        return [BENCH_SRC["wb_defl"]] if year in r["filled"]["wb_defl"].get(eco, set()) else []
    out = []
    if year in r["filled"]["fx"].get(eco, set()):
        out.append(BENCH_SRC["fx"])
    if year in r["filled"]["fx_emu"].get(eco, set()):
        out.append(BENCH_SRC["fx_emu"])
    return out


def _factor_rows(
    *,
    r: dict[str, Any],
    cur: str,
    country: str | None,
    p: dict[int, float],
    p_kind: str,
    p_eco: str,
    p_src: str,
    fx: dict[int, float],
    fx_eco: str | None,
    fx_src: str,
    sau_cpi: dict[int, float],
    series_id: str,
    with_cti: bool,
) -> list[dict[str, Any]]:
    """Central factors need the price series at y and the base plus the base-year rate; the
    `-cti` sensitivity needs the price-year rate and the Saudi CPI at y and the base. Sources
    are cited per cell used (R1c id, plus the R1b id where the R1b file filled the cell)."""
    rows: list[dict[str, Any]] = []
    tag = cur.lower() + (f"-{country.lower()}" if country else "")

    def p_ids(y: int) -> list[str]:
        extra = _cite(r, p_kind, p_eco, y) + _cite(r, p_kind, p_eco, BASE_YEAR)
        primary = [] if extra and p_src == BENCH_SRC["wb_defl"] else [p_src]
        return primary + extra

    def fx_ids(y: int) -> list[str]:
        if fx_eco is None:
            return [fx_src]
        extra = _cite(r, "fx", fx_eco, y)
        return extra if extra and y not in r["fx_primary"].get(fx_eco, set()) else [fx_src]

    for y in YEARS:
        itc = cti = None
        if y in p and BASE_YEAR in p and BASE_YEAR in fx:
            itc = p[BASE_YEAR] / p[y] / fx[BASE_YEAR] * PEG_SAR_PER_USD
        if with_cti and y in fx and y in sau_cpi and BASE_YEAR in sau_cpi:
            cti = (1.0 / fx[y]) * PEG_SAR_PER_USD * sau_cpi[BASE_YEAR] / sau_cpi[y]
        for method, f in (("inflate_then_convert", itc), ("convert_then_inflate", cti)):
            if f is None:
                continue
            if method == "inflate_then_convert":
                s = {*p_ids(y), *fx_ids(BASE_YEAR), PEG_SOURCE}
            else:
                s = {"S-cost-idx-001", *fx_ids(y), PEG_SOURCE}
            row: dict[str, Any] = {
                "id": f"I-{tag}-{y}-sar-{BASE_YEAR}"
                + ("" if method == "inflate_then_convert" else "-cti"),
                "method": method,
                "from_currency": cur,
                "from_year": y,
                "to_currency": "SAR",
                "to_year": BASE_YEAR,
                "factor": round(f, 6),
                "source": ", ".join(sorted(x for x in s if x.startswith("S-"))),
                "price_series": series_id if method == "inflate_then_convert" else "I-price-sar",
            }
            if country:
                row["country"] = country
            rows.append(row)
    return rows


def build(raw: Path = RAW, raw_bench: Path | None = RAW_BENCH) -> dict[str, Any]:
    r = load_raw(raw, raw_bench)
    sau_cpi = r["wb_cpi"]["SAU"]
    series: list[dict[str, Any]] = []
    fx_rows: list[dict[str, Any]] = []
    factors: list[dict[str, Any]] = []
    for cur, spec in CURRENCIES.items():
        p = r[spec["series"]][spec["eco"]]
        p_src = _series_sources(r, spec["series"], spec["eco"], spec["src"])
        series.append(
            {
                "id": f"I-price-{cur.lower()}",
                "currency": cur,
                "economy": spec["eco"],
                "kind": "cpi" if spec["series"] == "wb_cpi" else "gdp_deflator",
                "source": ", ".join(p_src),
                "values": {y: round(p[y], 6) for y in YEARS if y in p},
            }
        )
        if spec["fx"] == "PEG":
            fx = {y: PEG_SAR_PER_USD for y in PEG_YEARS}
            fx_src = [PEG_SOURCE]
        elif spec["fx"] == "USA":
            fx = dict.fromkeys(YEARS, 1.0)
            fx_src = ["definition (USD)"]
        else:
            fx = r["fx"][spec["fx"]]
            fx_src = _fx_sources(r, spec["fx"])
        fx_rows.append(
            {
                "id": f"I-fx-{cur.lower()}-usd",
                "currency": cur,
                "lcu_per_usd": {y: round(fx[y], 6) for y in YEARS if y in fx},
                "source": ", ".join(fx_src),
            }
        )
        fx_eco = spec["fx"] if spec["fx"] not in ("PEG", "USA") else None
        rows = _factor_rows(
            r=r,
            cur=cur,
            country=None,
            p=p,
            p_kind=spec["series"],
            p_eco=spec["eco"],
            p_src=spec["src"],
            fx=fx,
            fx_eco=fx_eco,
            fx_src=fx_src[0],
            sau_cpi=sau_cpi,
            series_id=f"I-price-{cur.lower()}",
            with_cti=True,
        )
        factors += rows
        if cur == "EUR":
            for eco in EUR_ECONOMIES:
                pe = r["wb_defl"].get(eco, {})
                pe_src = _series_sources(r, "wb_defl", eco, "S-cost-idx-002")
                if r["filled"]["wb_defl"].get(eco, set()) >= set(pe):  # only in the R1b file
                    pe_src = [BENCH_SRC["wb_defl"]]
                sid = f"I-price-eur-{eco.lower()}"
                series.append(
                    {
                        "id": sid,
                        "currency": "EUR",
                        "economy": eco,
                        "kind": "gdp_deflator",
                        "source": ", ".join(pe_src),
                        "values": {y: round(pe[y], 6) for y in YEARS if y in pe},
                    }
                )
                factors += _factor_rows(
                    r=r,
                    cur="EUR",
                    country=eco,
                    p=pe,
                    p_kind="wb_defl",
                    p_eco=eco,
                    p_src=pe_src[0],
                    fx=fx,
                    fx_eco=fx_eco,
                    fx_src=fx_src[0],
                    sau_cpi=sau_cpi,
                    series_id=sid,
                    with_cti=False,  # the sensitivity does not depend on the economy
                )
        base_f = [f for f in rows if f["from_year"] == BASE_YEAR]
        for f in base_f:
            for y in LATER_YEARS:
                factors.append(
                    {
                        **f,
                        "id": f["id"].replace(f"-{BASE_YEAR}-sar", f"-{y}-sar") + "-asbase",
                        "from_year": y,
                        "assumption_id": "A-cost-009",
                    }
                )
    return {
        "base": {"currency": "SAR", "price_year": BASE_YEAR, "assumption_id": "A-cost-001"},
        "method_central": "inflate_then_convert",
        "method_sensitivity": "convert_then_inflate",
        "method_assumption_id": "A-cost-002",
        "method_rule": (
            "CP2 P2a (Tariq, 31 Oct 2026): the only price index. SAR items: Saudi CPI. "
            "Foreign-currency items: the source economy's GDP deflator (World Bank WDI) before "
            "conversion, then the 2025 rate to USD and the peg 3.75 to SAR. Exceptions A-cost-307: "
            "EUR with no euro-area economy -> Eurostat EA20 deflator; AED -> UAE CPI (no 2025 WDI "
            "deflator); TWD and other currencies not listed -> no factor (not converted)."
        ),
        "peg_sar_per_usd": {"value": PEG_SAR_PER_USD, "source": PEG_SOURCE},
        "series_exceptions_assumption_id": "A-cost-307",
        "inputs": [
            {"source": "S-cost-idx-001", "manifest_id": "wb-fp-cpi-totl-2026-10"},
            {"source": "S-cost-idx-002", "manifest_id": "wb-ny-gdp-defl-zs-2026-10"},
            {"source": "S-cost-idx-003", "manifest_id": "wb-pa-nus-fcrf-2026-10"},
            {"source": "S-cost-idx-004", "manifest_id": "eurostat-nama10gdp-ea20-pd15-2026-10"},
            {
                "source": "S-bench-idx-001",
                "manifest_id": "wb-wdi-ny-gdp-defl-zs-2026-10-08",
                "note": "R1b file (ex index-r1b.yaml): deflators 1985-1999 and PRT",
            },
            {
                "source": "S-bench-idx-002",
                "manifest_id": "wb-wdi-pa-nus-fcrf-2026-10-08",
                "note": "R1b file (ex index-r1b.yaml): exchange rates 1985-1999",
            },
            {
                "source": "S-bench-idx-003",
                "manifest_id": "wb-wdi-pa-nus-fcrf-emu-2026-10-08",
                "note": "R1b file (ex index-r1b.yaml): EUR per USD 1999",
            },
            {"source": "S-lb-020", "manifest_id": "n/a (SAMA statement of the peg)"},
        ],
        "notes": (
            "Generated by `uv run python -m costs.index_build`; do not edit by hand. Raw series "
            "are manifest rows wb-fp-cpi-totl-2026-10, wb-ny-gdp-defl-zs-2026-10, "
            "wb-pa-nus-fcrf-2026-10, eurostat-nama10gdp-ea20-pd15-2026-10 and (folded in from "
            "the former R1b index) wb-wdi-ny-gdp-defl-zs-2026-10-08, "
            "wb-wdi-pa-nus-fcrf-2026-10-08, wb-wdi-pa-nus-fcrf-emu-2026-10-08 (CC BY 4.0; "
            "The World Bank, WDI; Eurostat; "
            "modified: re-based to 2025). Both World Bank editions are lastupdated 2026-10-08 and "
            "agree on every overlapping cell; the R1c files win, the R1b files fill gaps. Saudi "
            "CPI is the World Bank relay of the national (GASTAT) CPI; the GASTAT primary table is "
            "still to fetch. EUR 'PPP' figures (EC 2018 study) are treated as nominal EUR."
        ),
        "series": series,
        "fx": fx_rows,
        "factors": factors,
    }


@app.command()
def main(
    out: Path = typer.Option(OUT, "--out"),
    raw: Path = typer.Option(RAW, "--raw"),
    raw_bench: Path = typer.Option(RAW_BENCH, "--raw-bench", help="R1b World Bank files"),
) -> None:
    """Write the index YAML."""
    idx = build(raw, raw_bench)
    header = (
        "# Document version: cities/ksa/costs/index.yaml v1.1 | 31 Oct 2026 | "
        "Author: cost-estimator (R1c, costs.index_build); P2a single index by CP2_PREP | "
        "Status: draft\n"
        "# The only price and currency index (cost register and W5 benchmarks; CP2 P2a); "
        "generated, do not edit by hand.\n"
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(header + yaml.safe_dump(idx, sort_keys=False, allow_unicode=True), "utf-8")
    typer.echo(f"wrote {out}: {len(idx['factors'])} factors, {len(idx['series'])} series")


if __name__ == "__main__":
    app()
