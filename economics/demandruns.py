"""Matched demand runs for the CBA (W4, R5): baseline and scenario on the same zones, seed,
population scenario, year and fitted constants (rule 6), reduced to the physical changes the
benefit streams need (economics.benefits.extract). Nothing but the reduced tables is written.

Groups = (population scenario, modelled year). 2025 is the calibration point and is shared by every
population scenario (un_wpp_medium_gastat2024, A-demand-040); 2040/2050/2060 run per scenario.
Each group runs its baseline once (S1, or S0 for the committed-programme check) and then every
case. Output: runs/cba/inputs/<group>/scalars.parquet (one row per case) and zones.parquet.

  uv run python -m economics.cli inputs --cases cities/ksa/cba --workers 4 --seed 1

Label: synthetic demand, uncalibrated: scenario comparison, not a forecast.
"""

from __future__ import annotations

import dataclasses
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from common import REPO_ROOT
from economics import benefits
from economics import params as prm

# R6 (CP6 P5b, A-r6-011): constants re-fitted with the R5 method on the split zone system
CALIBRATION = Path("runs/r6/demand/calibration-p5b-s1/calibration.json")
INPUTS = Path("runs/cba/inputs")
BASE_2025 = "un_wpp_medium_gastat2024"
POPULATIONS = ("un_wpp_low", "un_wpp_medium", "un_wpp_high")
YEARS = (2040, 2050, 2060)


def groups(populations: tuple[str, ...] = POPULATIONS, years: tuple[int, ...] = YEARS):
    out = [(BASE_2025, 2025)]
    out += [(p, y) for p in populations for y in years]
    return out


def group_id(pop: str, year: int) -> str:
    return f"{pop}-{year}"


def overrides(root: Path = REPO_ROOT, calibration: Path = CALIBRATION) -> dict[str, float]:
    cal = json.loads((root / calibration).read_text(encoding="utf-8"))
    return {a["parameter"]: float(a["fitted"]) for a in cal["adjustments"]}


def jeddah_zones(zones: pd.DataFrame) -> set[str]:
    return set(zones.loc[zones.metro.eq("Jeddah"), "zone_id"])


def run_group(
    pop: str,
    year: int,
    cases: list[dict[str, Any]],
    root: Path = REPO_ROOT,
    out_dir: Path = INPUTS,
) -> Path:
    """Run the baselines and every case of one (population, year) group."""
    from demand import gravity

    ov = overrides(root)
    p = prm.load(root)
    zones = gravity.zone_population(year, pop, root)
    jz = jeddah_zones(zones)
    base_cache: dict[str, dict[str, Any]] = {}
    coefs = gravity.coefficients(ov)
    b_car = abs(float(coefs.ivt["car"]))  # |b_ivt,car|: cost_min is in car in-vehicle minutes
    asc = {m: float(coefs.asc.get(m, 0.0)) for m in ("car", "rail", "air", "bus")}

    def run(scenario: str, candidate: str | None) -> dict[str, Any]:
        cfg = gravity.RunConfig(
            scenario, pop, year, ov, {}, root, network="r4", candidate=candidate
        )
        return gravity.run_model(cfg)

    rows, zrows = [], []
    for c in cases:
        b = c["baseline"]
        if b not in base_cache:
            base_cache[b] = run(b, None)
        scen = run(c["scenario_lines"], c.get("candidate_yaml"))
        ph = benefits.extract(base_cache[b], scen, zones, p, jz, b_car, asc)
        d = dataclasses.asdict(ph)
        um = d.pop("user_min")
        umz = d.pop("user_min_zone")
        wei = d.pop("wei_dlnED")
        # jobs per resident held at the zone's proxy rate (demand.gravity, A-demand-003)
        jobs = zones.jobs.fillna(0.0).to_numpy(dtype=float)
        d["wei_job_weighted_dlnED"] = float(np.nansum(jobs * wei))
        rows.append(
            {
                "case": c["id"],
                "population": pop,
                "year": year,
                **{f"user_min_{k}": v for k, v in um.items()},
                **d,
            }
        )
        zrows.append(
            pd.DataFrame(
                {
                    "case": c["id"],
                    "zone_id": zones.zone_id.to_numpy(),
                    **{f"user_min_{k}": v for k, v in umz.items()},
                    "wei_dlnED": wei,
                    "jobs": jobs,
                    "population": zones.population.to_numpy(),
                    "region": zones.region.to_numpy(),
                }
            )
        )
    od = root / out_dir / group_id(pop, year)
    od.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_parquet(od / "scalars.parquet", index=False)
    pd.concat(zrows, ignore_index=True).to_parquet(od / "zones.parquet", index=False)
    return od


def _worker(args: tuple[str, int, list[dict[str, Any]], str, str]) -> str:
    pop, year, cases, root, out_dir = args
    return str(run_group(pop, year, cases, Path(root), Path(out_dir)))


def run_all(
    cases: list[dict[str, Any]],
    root: Path = REPO_ROOT,
    out_dir: Path = INPUTS,
    workers: int = 4,
    populations: tuple[str, ...] = POPULATIONS,
    years: tuple[int, ...] = YEARS,
) -> list[str]:
    jobs = [(pop, y, cases, str(root), str(out_dir)) for pop, y in groups(populations, years)]
    if workers <= 1:
        return [_worker(j) for j in jobs]
    import multiprocessing as mp

    with mp.get_context("spawn").Pool(workers) as pool:
        return list(pool.imap_unordered(_worker, jobs))


def load_inputs(case_id: str, root: Path = REPO_ROOT, in_dir: Path = INPUTS) -> pd.DataFrame:
    """Scalars of one case over every group (rows: population x year)."""
    frames = []
    for g in sorted((root / in_dir).glob("*/scalars.parquet")):
        s = pd.read_parquet(g)
        frames.append(s[s.case == case_id])
    if not frames:
        raise FileNotFoundError(f"no CBA inputs under {root / in_dir}")
    return pd.concat(frames, ignore_index=True)


def load_zone_inputs(case_id: str, group: str, root: Path = REPO_ROOT, in_dir: Path = INPUTS):
    z = pd.read_parquet(root / in_dir / group / "zones.parquet")
    return z[z.case == case_id].reset_index(drop=True)


def series_for(sc: pd.DataFrame, pop: str, column: str) -> tuple[list[int], list[float]]:
    """Modelled years and values of one quantity for one population scenario (2025 shared)."""
    base = sc[(sc.population == BASE_2025) & (sc.year == 2025)]
    rest = sc[sc.population == pop].sort_values("year")
    years = [2025, *rest.year.astype(int).tolist()]
    vals = [float(base[column].iloc[0]) if len(base) else np.nan, *rest[column].tolist()]
    return years, vals
