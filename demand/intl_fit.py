"""Fit of the international rail share against the observed HHR 2025 total (R5, CP5 decision H3a).

The international segment (demand.intl) puts a share s of every foreign-visitor leg with a rail
path on rail (A-intl-003). HHR riders are resident trips (demand.gravity at the calibration point)
plus s x the international legs on HHR, which is linear in s, so the exact fit is

    s* = (observed HHR 2025 - resident HHR) / (international HHR legs at s = 1)

H3a makes s a `calibrated` parameter. The HHR 2025 total is then a calibration target, not
independent validation. The replacement validation check (A-intl-008, A-intl-009) is the
Ramadan month profile: the modelled HHR Ramadan factor (Ramadan month / mean month) against the
observed GASTAT monthly HHR series (March 2025 = Ramadan 1446), which the fit does not use.

  uv run python -m demand.intl_fit fit --calibration runs/r5/demand/calibration-r5-s1 \
      --seed 1 --out runs/r5/demand/intl-fit-s1/

Label: synthetic demand, uncalibrated: scenario comparison, not a forecast (the HHR total is
calibrated at 2025 only).
"""

from __future__ import annotations

import json
import warnings
from pathlib import Path
from typing import Any

import pandas as pd
import typer
import yaml

from common import REPO_ROOT
from common.labels import LABEL
from common.runmeta import seed_option, write_meta
from demand import intl

RAIL_TABLES = Path("data/ksa/calibration/gastat_rail_tables_2025/railway_tables_2025_en.xlsx")
CALIB = Path("cities/ksa/assumptions/demand_calibration.yaml")
TOL_RAMADAN = 0.15  # A-intl-009 (by analogy with A-demand-032)

app = typer.Typer(add_completion=False, help=__doc__, no_args_is_help=True)


@app.callback()
def _group() -> None:
    """International rail-share fit (H3a)."""


def observed_hhr(root: Path = REPO_ROOT) -> float:
    cal = yaml.safe_load((root / CALIB).read_text(encoding="utf-8"))
    return float(next(t["value"] for t in cal["targets"] if t["id"] == "rail-hhr-pax-2025"))


def observed_monthly_hhr(root: Path = REPO_ROOT) -> list[float]:
    """GASTAT rail tables 2025, sheet 1-2: HHR passengers by month (Jan..Dec 2025)."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        m = pd.read_excel(root / RAIL_TABLES, sheet_name="1-2", header=None).fillna("")
    return next(
        [float(x) for x in [str(v).strip() for v in r if str(v).strip()][2:14]]
        for r in m.values
        if str(r[0]).strip() == "Haramain High Speed Railway"
    )


def exact_share(observed: float, resident: float, legs_at_one: float) -> float:
    """s* such that resident + s* x legs_at_one = observed."""
    if legs_at_one <= 0:
        raise ValueError("no international legs with an HHR path")
    return (observed - resident) / legs_at_one


def ramadan_factor(resident: float, intl_year: float, intl_ramadan_month: float) -> float:
    """Ramadan month / mean month; resident demand is flat across months (no seasonal profile)."""
    return (resident / 12.0 + intl_ramadan_month) / ((resident + intl_year) / 12.0)


def fit(calibration: Path, root: Path = REPO_ROOT) -> dict[str, Any]:
    tot = json.loads((calibration / "od" / "totals.json").read_text(encoding="utf-8"))
    resident = float(tot["rail_by_line"]["hhr"]["passengers"])
    obs = observed_hhr(root)
    seg = intl.run_segment("S0", root)
    s0 = intl.rail_share(root)["value"]
    hhr = seg["by_line"].get("hhr", {"value": 0.0})
    legs_at_one = float(hhr["value"]) / s0
    ram_at_one = float(seg["peaks"].get("hhr", {}).get("ramadan_month", 0.0)) / s0
    s_star = exact_share(obs, resident, legs_at_one)
    months = observed_monthly_hhr(root)
    ram_obs = months[2] / (sum(months) / 12.0)  # March 2025 = Ramadan 1446
    ram_mod = ramadan_factor(resident, s_star * legs_at_one, s_star * ram_at_one)
    dev = ram_mod / ram_obs - 1.0
    prior = intl.rail_share(root)
    return {
        "label": LABEL,
        "status": "calibrated (2025 HHR total is a calibration target, not independent validation)",
        "observed_hhr_2025": obs,
        "resident_hhr_2025": resident,
        "international_hhr_legs_at_share_1": legs_at_one,
        "fitted_share": s_star,
        "fitted_total": resident + s_star * legs_at_one,
        "deviation_after_fit_pct": 100.0 * ((resident + s_star * legs_at_one) / obs - 1.0),
        "prior": {"central": prior["value"], "range": [prior["low"], prior["high"]]},
        "inside_prior_range": prior["low"] <= s_star <= prior["high"],
        "validation_check": {
            "name": "HHR Ramadan month profile (GASTAT monthly series, March 2025 = Ramadan 1446)",
            "assumption_ids": ["A-intl-008", "A-intl-009"],
            "observed_factor": ram_obs,
            "modelled_factor": ram_mod,
            "deviation_pct": 100.0 * dev,
            "tolerance": TOL_RAMADAN,
            "pass": abs(dev) <= TOL_RAMADAN,
            "note": "not used by the fit; resident demand carries no monthly profile, so the "
            "modelled factor comes from the international segment's Ramadan month factor only",
        },
        "calibration_run": str(calibration),
    }


@app.command("fit")
def fit_cmd(
    calibration: Path = typer.Option(Path("runs/r5/demand/calibration-r5-s1")),
    seed: int = seed_option(),
    out: Path = typer.Option(Path("runs/r5/demand/intl-fit-s1")),
    root: Path = typer.Option(REPO_ROOT, hidden=True),
) -> None:
    """Fit the international rail share to the HHR 2025 total and run the Ramadan check."""
    r = fit(calibration, root)
    out.mkdir(parents=True, exist_ok=True)
    (out / "fit.json").write_text(json.dumps(r, indent=1) + "\n", encoding="utf-8")
    write_meta(out, seed, {"calibration": str(calibration)}, extra={"label": LABEL})
    typer.echo(json.dumps(r, indent=1))


if __name__ == "__main__":
    app()
