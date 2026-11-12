"""R6 outputs: layout maps, the Pareto plot, scorecards and the fast-vs-full rank check.

  uv run python -m optimise.report map --layout <yaml> --out <png> [--title ...]
  uv run python -m optimise.report pareto --out runs/r6/pareto.png
  uv run python -m optimise.report ranks --out runs/r6/fast_vs_full.csv

Maps: existing and committed lines from the OSM-derived line layers (ODbL, credited on the
map), the layout's hypothetical corridors along their routed alignments coloured by phase, station
additions as markers. Every figure carries the synthetic-demand label.

Label: synthetic demand, uncalibrated: scenario comparison, not a forecast.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import typer
import yaml

from common import REPO_ROOT
from common.labels import LABEL

OSM = "Base lines: (c) OpenStreetMap contributors, ODbL 1.0; GASTAT/OSM boundaries"
PHASE_COLOURS = {2030: "#b2182b", 2035: "#ef8a62", 2040: "#67a9cf", 2050: "#2166ac"}
app = typer.Typer(add_completion=False, help=__doc__, no_args_is_help=True)


@app.callback()
def _group() -> None:
    """R6 reporting."""


def _gj(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8")).get("features", [])


def _lines(ax, feats, **kw) -> None:
    for f in feats:
        g = f.get("geometry") or {}
        parts = (
            [g["coordinates"]]
            if g.get("type") == "LineString"
            else g.get("coordinates", [])
            if g.get("type") == "MultiLineString"
            else []
        )
        for p in parts:
            a = np.asarray(p)
            if a.ndim == 2 and len(a) > 1:
                ax.plot(a[:, 0], a[:, 1], **kw)
                kw.pop("label", None)


def layout_map(
    layout: dict[str, Any], out: Path, title: str, root: Path = REPO_ROOT, note: str = ""
) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(9, 8.2))
    for f in _gj(root / "cities/ksa/zones/ksa.geojson"):
        g = f["geometry"]
        polys = [g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]
        for poly in polys:
            a = np.asarray(poly[0])
            ax.fill(a[:, 0], a[:, 1], color="#f3f1ec", lw=0.6, ec="#9a958a")
    _lines(
        ax,
        _gj(root / "cities/ksa/lines/geojson/existing.geojson"),
        color="#222",
        lw=1.6,
        label="existing (layer: existing)",
    )
    _lines(
        ax,
        _gj(root / "cities/ksa/lines/geojson/committed.geojson"),
        color="#555",
        lw=1.3,
        ls="--",
        label="committed / under procurement (announced/planned)",
    )
    seen = set()
    for c in sorted(layout.get("corridors", []), key=lambda c: int(c.get("phase", 2030))):
        ph = int(c.get("phase", 2030))
        col = PHASE_COLOURS[ph]
        lab = f"hypothetical (ours), phase {ph}" if ph not in seen else None
        if c["id"].startswith("S5-"):
            d = yaml.safe_load(
                (root / "cities/ksa/corridors/station_addition" / f"{c['id']}.yaml").read_text()
            )
            for s in d["stations"]:
                if s.get("class") == "planned":
                    ax.scatter(
                        s["lon"],
                        s["lat"],
                        s=46,
                        marker="D",
                        color=col,
                        ec="k",
                        lw=0.6,
                        zorder=5,
                        label=lab,
                    )
                    lab = None
        else:
            kw = {"color": col, "lw": 2.4, "zorder": 4}
            if lab:
                kw["label"] = lab
            feats = _gj(root / "cities/ksa/alignments" / f"{c['id']}.geojson")
            routed = [f for f in feats if (f.get("properties") or {}).get("kind") == "routed"]
            _lines(ax, routed or feats[:1], **kw)
            fam = {"S2": "trunk_gap", "S3": "branch_spur", "S4": "commuter_belt"}[c["id"][:2]]
            d = yaml.safe_load(
                (root / "cities/ksa/corridors" / fam / f"{c['id']}.yaml").read_text()
            )
            drop = set(c.get("drop_stations") or [])  # R6_V3 variants: dropped stations
            sts = [s for s in d["stations"] if s["id"] not in drop]
            ax.scatter(
                [s["lon"] for s in sts],
                [s["lat"] for s in sts],
                s=12,
                color=col,
                ec="k",
                lw=0.4,
                zorder=5,
            )
        seen.add(ph)
    ax.set_xlim(34.3, 56.0)
    ax.set_ylim(16.0, 32.5)
    ax.set_aspect(1.08)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title(title, fontsize=10)
    ax.legend(loc="lower left", fontsize=7, frameon=True)
    fig.text(0.01, 0.01, f"{OSM}. {LABEL}. {note}", fontsize=6.2, wrap=True)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=140, bbox_inches="tight")
    plt.close(fig)
    return out


@app.command("map")
def map_cmd(
    layout: Path = typer.Option(...),
    out: Path = typer.Option(...),
    title: str = typer.Option(""),
    root: Path = typer.Option(REPO_ROOT, hidden=True),
) -> None:
    d = yaml.safe_load(layout.read_text())
    layout_map(d, out, title or d.get("id", layout.stem), root)
    typer.echo(f"wrote {out}")


def full_scores(root: Path = REPO_ROOT) -> pd.DataFrame:
    """Every full-fidelity layout score under runs/r6 (library excluded), one row each."""
    rows = []
    for p in sorted((root / "runs/r6").rglob("score.json")):
        if "library" in p.parts or "judge-backtest" in str(p) or "tmp" in p.parts:
            continue
        s = json.loads(p.read_text())
        if not s.get("feasible") or "robust_npv" not in s:
            continue
        lay = p.parent / "layout-source.yaml"
        rows.append(
            {
                "run": str(p.parent.relative_to(root)),
                "robust_npv": s["robust_npv"],
                "capex_p50": s["capex_sar_m"]["capex_p50"],
                "access_gain_60": s.get("access_gain_60"),
                "access_gain_120": s.get("access_gain_120"),
                "n_corridors": s.get("n_corridors"),
                "layout": str(lay.relative_to(root)) if lay.exists() else None,
            }
        )
    return pd.DataFrame(rows)


@app.command("pareto")
def pareto_cmd(
    table: Path = typer.Option(..., help="CSV with engine, robust_npv, capex_p50, access_gain_60"),
    out: Path = typer.Option(...),
) -> None:
    """Robust NPV vs capex (colour: accessibility gain at 60 min), one marker per engine."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    df = pd.read_csv(table)
    fig, ax = plt.subplots(figsize=(8.5, 5.6))
    marks = {"milp": "s", "ga": "o", "agent": "^", "family": "X", "reference": "P"}
    sc = None
    for eng, g in df.groupby("engine"):
        sc = ax.scatter(
            g.capex_p50 / 1e3,
            g.robust_npv / 1e3,
            c=g.access_gain_120 / 1e6,
            cmap="viridis",
            marker=marks.get(eng, "o"),
            s=42,
            ec="k",
            lw=0.4,
            label=eng,
            vmin=0,
            vmax=max(df.access_gain_120.max() / 1e6, 0.1),
        )
    if sc is not None:
        fig.colorbar(sc, ax=ax, label="accessibility gain, 120 min door-to-door (M people, 2025)")
    for b in (100, 250, 500):
        ax.axvline(b, color="#999", lw=0.7, ls=":")
    ax.axhline(0, color="#444", lw=0.7)
    ax.set_xlabel("capex P50, uplifted (SAR bn, 2025 prices, undiscounted)")
    ax.set_ylabel("robust NPV (SAR bn, PV 2026): min over population cases at P50 cost")
    ax.legend(fontsize=8)
    ax.set_title("R6 full-judge scores (dotted: budget levels B1-B3)", fontsize=10)
    fig.text(0.01, 0.005, LABEL, fontsize=7)
    fig.savefig(out, dpi=140, bbox_inches="tight")
    plt.close(fig)
    typer.echo(f"wrote {out}")


@app.command("holdout")
def holdout_cmd(
    top: int = typer.Option(25),
    root: Path = typer.Option(REPO_ROOT, hidden=True),
) -> None:
    """Overfitting check (A-r6-012): layouts of the holdout GA runs (scored on low + medium at
    P50 cost) ranked by that score, then re-ranked on the held-out tests: the high case at P50 cost
    and the robust NPV at P90 cost; flag rank drops > 5 places. runs/r6/holdout.csv."""
    from optimise.search import Fast

    fast = Fast(root)
    rows = []
    for d in sorted((root / "runs/r6/ga").glob("*-holdout")):
        f = pd.read_csv(d / "front.csv")
        for k in f.k:
            lay = yaml.safe_load((d / "layouts" / f"{k:03d}.yaml").read_text())
            s = fast.score(fast.genome_of(lay))
            rows.append(
                {
                    "run": d.name,
                    "layout": f"{d.name}/layouts/{k:03d}.yaml",
                    "search_score": min(s["npv"]["un_wpp_low"], s["npv"]["un_wpp_medium"]),
                    "test_high_p50": s["npv"]["un_wpp_high"],
                    "test_p90cost": min(s["npv_p90cost"].values()),
                    "capex_p50": s["capex_p50"],
                    "n": s["n"],
                }
            )
    df = pd.DataFrame(rows).drop_duplicates(["search_score", "test_high_p50", "capex_p50"])
    df = df.sort_values("search_score", ascending=False).head(top).reset_index(drop=True)
    df["rank_search"] = np.arange(1, len(df) + 1)
    for t in ("test_high_p50", "test_p90cost"):
        df[f"rank_{t}"] = df[t].rank(ascending=False, method="min").astype(int)
        df[f"drop_{t}"] = df[f"rank_{t}"] - df.rank_search
    df["flag_rank_drop_gt5"] = (df.drop_test_high_p50 > 5) | (df.drop_test_p90cost > 5)
    df.to_csv(root / "runs/r6/holdout.csv", index=False)
    typer.echo(df.to_string())


@app.command("scorecards")
def scorecards_cmd(root: Path = typer.Option(REPO_ROOT, hidden=True)) -> None:
    """runs/r6/top5/<L>-scorecard.md and runs/r6/top5/top5.csv from the all-case full scores."""
    rows = []
    P = ("un_wpp_low", "un_wpp_medium", "un_wpp_high")
    for k in ("L1", "L2", "L3", "L4", "L5"):
        s = json.loads((root / "runs/r6/top5" / k / "score.json").read_text())
        ar = pd.DataFrame(s["appraisal_rows"])
        med = ar[(ar.population == "un_wpp_medium")]
        sens = {
            f"{r.rate_case}/{r.horizon}y": r.npv_at_p50_cost
            for r in med.itertuples()
            if r.horizon == 60 or r.rate_case == "greenbook_2026"
        }
        loads = s.get("loads_2050_medium") or {}
        loads1 = s.get("loads_2050_medium_S1") or {}
        rk = sum(
            float(
                json.loads((root / "cities/ksa/alignments" / f"{c}.json").read_text()).get(
                    "length_km", 0.0
                )
            )
            for c in s["corridors"]
            if not c.startswith("S5-") and (root / "cities/ksa/alignments" / f"{c}.json").exists()
        )
        dtrips = (s["rail_trips_2050_medium"] or 0) - (s["rail_trips_2050_medium_S1"] or 0)
        row = {
            "layout": f"S6-{k}",
            "corridors": len(s["corridors"]),
            "robust_npv": s["robust_npv"],
            **{f"npv_p50cost_{p.split('_')[-1]}": s["npv_at_p50_cost"][p] for p in P},
            **{f"npv_p90cost_{p.split('_')[-1]}": s["npv_at_p90_cost"][p] for p in P},
            "npv_draws_p10_medium": s["npv_p10"]["un_wpp_medium"],
            "npv_draws_p50_medium": s["npv_p50"]["un_wpp_medium"],
            "npv_draws_p90_medium": s["npv_p90"]["un_wpp_medium"],
            "bcr_p10_medium": s["bcr_p10"]["un_wpp_medium"],
            "bcr_p50_medium": s["bcr_p50"]["un_wpp_medium"],
            "bcr_p90_medium": s["bcr_p90"]["un_wpp_medium"],
            "pv_wei_indicative_medium": s["pv_wei_p50_indicative"]["un_wpp_medium"],
            **{k2: v for k2, v in s["capex_sar_m"].items()},
            "rail_trips_2050_medium": s["rail_trips_2050_medium"],
            "added_rail_trips_2050_medium": dtrips,
            "added_rail_pkm_m_2050_medium": (s["rail_pkm_m_2050_medium"] or 0)
            - (s["rail_pkm_m_2050_medium_S1"] or 0),
            "new_route_km": rk,
            "added_trips_per_new_route_km": dtrips / rk if rk else None,
            "access_gain_60": s.get("access_gain_60"),
            "access_gain_120": s.get("access_gain_120"),
            "co2_pv_p50_medium": float(
                med[(med.horizon == 60) & (med.rate_case == "greenbook_2026")].pv_carbon_p50.iloc[0]
            ),
            "hhr_pax_2050": (loads.get("hhr") or {}).get("passengers"),
            "hhr_pax_2050_S1": (loads1.get("hhr") or {}).get("passengers"),
            "landbridge_pax_2050": (loads.get("landbridge") or {}).get("passengers"),
            "landbridge_pax_2050_S1": (loads1.get("landbridge") or {}).get("passengers"),
            "flags": "; ".join(s.get("flags", [])),
            "phases": json.dumps(s["phases"]),
            **{f"sens_{k3}": v for k3, v in sens.items()},
        }
        rows.append(row)
    df = pd.DataFrame(rows)
    df.to_csv(root / "runs/r6/top5/top5.csv", index=False)
    typer.echo(df.T.to_string())


if __name__ == "__main__":
    app()
