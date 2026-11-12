"""Bottom-up vs top-down reconciliation per line type (docs/costs.md section 5).

For each line type, a hypothetical reference corridor (A-cost-018; costs/config/reconcile.yaml) is
costed bottom-up with `costs.estimate`; its capex per route-km (excluding and including rolling
stock) is compared with every top-down per-km row of the register named for that line type. A gap
of more than 30 % against the top-down central value is flagged, never averaged away.

CLI:
  uv run python -m costs.reconcile --seed 1 --out runs/costs/reconcile/
"""

from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import typer
import yaml

from common.labels import LABEL
from common.runmeta import seed_option, write_meta
from common.schemas import LineSpec, load_uplifts
from costs import rcf
from costs.estimate import MAP, PROFILES, UPLIFTS, estimate
from costs.register import INDEX, REGISTER, normalised_lookup

CONFIG = Path(__file__).resolve().parent / "config" / "reconcile.yaml"
LINE_TYPES = ("hsr", "conventional_passenger", "mixed", "commuter", "upgrade")

app = typer.Typer(add_completion=False, help="Bottom-up vs top-down reconciliation.")


def reference_line(lt: str, ref: dict[str, Any]) -> LineSpec:
    L = float(ref["length_km"])
    today = dt.date(2026, 10, 31)
    st = [
        ("ref-a", 0.0, "terminal"),
        ("ref-b", round(L / 3, 1), "intermediate"),
        ("ref-c", round(2 * L / 3, 1), "intermediate"),
        ("ref-d", L, "terminal"),
    ]
    a = ref["assumption_id"]
    return LineSpec.model_validate(
        {
            "id": f"ref-{lt.replace('_', '-')}",
            "name_en": f"Reference corridor ({lt})",
            "name_ar": "ممر مرجعي",
            "layer": "hypothetical",
            "status": "generated",
            "source": a,
            "line_type": lt,
            "track": "double",
            "electrified": True,
            "length_km": L,
            "generated_from": "costs/config/reconcile.yaml (reference shape, not a proposal)",
            "rules_hash": "reference",
            "fixture": True,
            "stations": [
                {
                    "id": i,
                    "name_en": i,
                    "name_ar": i,
                    "km_post": k,
                    "lat": 24.0,
                    "lon": 45.0,
                    "class": c,
                    "source": a,
                }
                for i, k, c in st
            ],  # fmt: skip
            "services": [
                {
                    "id": "all",
                    "stops": "all",
                    "headway_min": 60,
                    "span": "06:00-23:00",
                    "sampled": today,
                    "source": a,
                }
            ],  # fmt: skip
            "running_time_model": {
                "cruise_kmh": {"value": ref["cruise_kmh"][lt], "assumption_id": a},
                "accel_ms2": {"value": ref["accel_ms2"], "assumption_id": a},
                "decel_ms2": {"value": ref["decel_ms2"], "assumption_id": a},
                "dwell_s": {"value": ref["dwell_s"], "assumption_id": a},
            },
        }
    )


def reconcile(seed: int, draws: int) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    cfg = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    reg = normalised_lookup(REGISTER, INDEX)
    profiles = yaml.safe_load(PROFILES.read_text(encoding="utf-8"))["profiles"]
    cmap = yaml.safe_load(MAP.read_text(encoding="utf-8"))
    ups = load_uplifts(UPLIFTS)
    bu_rows, rows = [], []
    for lt in LINE_TYPES:
        line = reference_line(lt, cfg["reference"])
        _, df, _ = estimate(line, reg, profiles[lt], cmap, seed, draws)
        L = line.length_km or 1.0
        all_in_d = df["capex_base"].to_numpy()
        infra_d = all_in_d - df["rolling_stock"].to_numpy()
        stage = profiles[lt]["appraisal_stage"]["value"]
        u = rcf.select(ups, "capex", lt, stage)
        m = rcf.draw(u, np.random.default_rng(seed), draws)
        q = lambda x, ps=(10, 50, 90), L=L: {  # noqa: E731
            f"P{p}": float(np.percentile(x, p)) / L for p in ps
        }
        infra_p, all_in, upl = q(infra_d), q(all_in_d), q(all_in_d * m, (50, 80))
        rs_p50 = float(np.median(df["rolling_stock"]))
        bu_rows.append(
            {
                "line_type": lt,
                "infra_P10": infra_p["P10"],
                "infra_P50": infra_p["P50"],
                "infra_P90": infra_p["P90"],
                "all_in_P10": all_in["P10"],
                "all_in_P50": all_in["P50"],
                "all_in_P90": all_in["P90"],
                "uplifted_all_in_P50": upl["P50"],
                "uplifted_all_in_P80": upl["P80"],
                "uplift_id": u.id,
                "rolling_stock_P50_per_km": rs_p50 / L,
            }
        )
        for td in cfg["top_down"].get(lt, []):
            it = reg[td["id"]]
            bu = infra_p["P50"] if td["scope"] == "infra" else all_in["P50"]
            lo, c, hi = it["low"], it["central"], it["high"]
            gap = (bu - c) / c * 100.0
            within = lo <= bu <= hi
            rows.append(
                {
                    "line_type": lt,
                    "top_down_id": td["id"],
                    "scope": td["scope"],
                    "td_low": lo,
                    "td_central": c,
                    "td_high": hi,
                    "bottom_up_P50": bu,
                    "gap_vs_central_pct": gap,
                    "within_td_range": within,
                    "flag": (abs(gap) > cfg["gap_flag_pct"]) and not within,
                    "note": td["note"],
                }
            )
    meta = {"label": LABEL, "unit": "SAR m per route-km, 2025 prices", "seed": seed}
    return pd.DataFrame(bu_rows), pd.DataFrame(rows), meta


@app.command()
def main(
    seed: int = seed_option(),
    draws: int = typer.Option(10_000, "--draws", min=100),
    out: Path = typer.Option(Path("runs/costs/reconcile"), "--out"),
) -> None:
    """Write bottom_up.csv, reconcile.csv and meta.json."""
    bu, rec, meta = reconcile(seed, draws)
    out.mkdir(parents=True, exist_ok=True)
    bu.to_csv(out / "bottom_up.csv", index=False)
    rec.to_csv(out / "reconcile.csv", index=False)
    write_meta(
        out,
        seed,
        yaml.safe_load(CONFIG.read_text("utf-8")),
        {**meta, "assumptions": ["A-cost-018"]},
    )
    typer.echo(
        f"{len(rec)} comparisons, {int(rec['flag'].sum())} flagged (> 30 % and outside range)"
    )


if __name__ == "__main__":
    app()
