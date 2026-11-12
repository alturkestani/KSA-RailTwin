"""Render the R5 90/120-minute door-to-door band section of docs/commute-test.md (CP5 H9a) from
runs/access/isochrones-summary-s1/reached_all.parquet and runs/access/commute-test-s1/by_metro.csv.

  uv run python scripts/r5_commute_bands.py

Label: synthetic demand, uncalibrated: scenario comparison, not a forecast.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/commute-test.md"
BEGIN = "<!-- BEGIN GENERATED R5 BANDS (uv run python scripts/r5_commute_bands.py) -->"
END = "<!-- END GENERATED R5 BANDS -->"


def body() -> str:
    r = pd.read_parquet(ROOT / "runs/access/isochrones-summary-s1/reached_all.parquet")
    b = pd.read_csv(ROOT / "runs/access/commute-test-s1/by_metro.csv")
    d = r[r["mode"] == "door_to_door"]
    n_cand = d.scenario.nunique() - 2
    lines = [
        "**Synthetic demand, uncalibrated: scenario comparison, not a forecast.** The 30–60 "
        "minute door-to-door bands reach no zone anywhere (R4), so R5 adds 90 and 120 minutes "
        "to `access.isochrones` (`BANDS`) and two columns to the 30-minute test "
        "(`within_90_d2d`, `within_120_d2d`). Runs: "
        f"`runs/access/isochrones-summary-s1/reached_all.parquet` (S0, S1 and {n_cand} "
        "candidates; 11 metros) and `runs/access/commute-test-s1/`. Door-to-door = road access, "
        "terminal time, wait, rides and transfers, egress, with the summer factor (R4 method).",
        "",
        "Population reached door-to-door from each metro's main station:",
        "",
        "| metro | S0 within 90 min | S0 within 120 min | S1 within 90 min | S1 within 120 min |",
        "|---|---|---|---|---|",
    ]

    def g(s: str, m: str, bm: int) -> str:
        x = d[(d.scenario == s) & (d.metro == m) & (d.band_min == bm)].population
        return f"{x.iloc[0]:,.0f}" if len(x) else "n/a"

    for m in sorted(d.metro.unique()):
        lines.append(
            f"| {m} | {g('S0', m, 90)} | {g('S0', m, 120)} | {g('S1', m, 90)} | {g('S1', m, 120)} |"
        )
    s1 = d[d.scenario == "S1"].set_index(["metro", "band_min"]).population
    c = d[~d.scenario.isin(["S0", "S1"])].copy()
    c["gain"] = [
        p - s1.get((m, bm), 0.0) for p, m, bm in zip(c.population, c.metro, c.band_min, strict=True)
    ]
    lines += ["", "Largest door-to-door gains over S1 among the candidates (in the model):", ""]
    for bm in (90, 120):
        t = c[(c.band_min == bm) & (c.gain > 0)].sort_values("gain", ascending=False).head(8)
        lines += [
            f"| {bm}-min band: candidate | metro | population within {bm} min | gain vs S1 |",
            "|---|---|---|---|",
        ]
        if t.empty:
            lines.append("| none | | | |")
        for x in t.itertuples():
            lines.append(f"| {x.scenario} | {x.metro} | {x.population:,.0f} | +{x.gain:,.0f} |")
        k = int((c[c.band_min == bm].gain > 0).sum())
        lines += ["", f"Metro–candidate pairs with any gain at {bm} min: {k}.", ""]
    lines += [
        "Towns of the 30-minute test (40–120 road-km from a metro) within the bands "
        "(`by_metro.csv`):",
        "",
        "| metro | towns | S0: within 30 in-vehicle | S0: within 90 door-to-door | S0: within 120 "
        "door-to-door | S1: within 90 door-to-door | S1: within 120 door-to-door |",
        "|---|---|---|---|---|---|---|",
    ]
    for m in sorted(b.metro.unique()):
        x0 = b[(b.scenario == "S0") & (b.metro == m)].iloc[0]
        x1 = b[(b.scenario == "S1") & (b.metro == m)].iloc[0]
        lines.append(
            f"| {m} | {x0.towns} | {x0.towns_within_30} | {x0.towns_within_90_d2d} | "
            f"{x0.towns_within_120_d2d} | {x1.towns_within_90_d2d} | "
            f"{x1.towns_within_120_d2d} |"
        )
    return "\n".join(lines)


def main() -> None:
    t = DOC.read_text(encoding="utf-8")
    a, rest = t.split(BEGIN, 1)
    _, z = rest.split(END, 1)
    DOC.write_text(a + BEGIN + "\n" + body() + "\n" + END + z, encoding="utf-8")


if __name__ == "__main__":
    main()
