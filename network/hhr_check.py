"""C-r1a-22 Haramain running-time decomposition (CP2_PREP item 5).

Splits the published Makkah-Jeddah (Al-Sulaymaniyah) time into (a) line-speed running at the
published operational speed, (b) acceleration and braking, (c) dwell at intermediate stops and
(d) a UIC 451-1 recovery margin, using the repo's kinematics (`network.graph.segment_minutes`).
The residual against the published time is what the model cannot explain from sourced inputs.

  uv run python -m network.hhr_check run --seed 1
writes runs/cp2_prep/item5/hhr-check/{components.csv,envelope.csv,summary.json,meta.json}.
Running times here are a timetable check, not a forecast.
"""

from __future__ import annotations

import itertools
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
import typer
import yaml

from common import REPO_ROOT
from common.runmeta import rng, seed_option, write_meta
from network.graph import segment_minutes

CONFIG = Path(__file__).with_name("hhr_check.yaml")
RUN_DIR = REPO_ROOT / "runs" / "cp2_prep" / "item5" / "hhr-check"
app = typer.Typer(add_completion=False, help="Haramain running-time decomposition (C-r1a-22).")


@dataclass(frozen=True)
class Components:
    """Minutes per component; `total` = running + dwell + recovery."""

    cruise_min: float  # (a) time at line speed
    accel_min: float  # (b) time spent accelerating to line speed
    decel_min: float  # (b) time spent braking from line speed
    accel_decel_loss_min: float  # (b) extra time over running the same km at line speed
    dwell_min: float  # (c)
    recovery_min: float  # (d)
    cruise_km: float
    accel_km: float
    decel_km: float

    @property
    def running_min(self) -> float:
        return self.cruise_min + self.accel_min + self.decel_min

    @property
    def total(self) -> float:
        return self.running_min + self.dwell_min + self.recovery_min


def decompose(
    km: float,
    cruise_kmh: float,
    accel_ms2: float,
    decel_ms2: float,
    stops: int,
    dwell_s: float,
    pct: float,
    min_per_100km: float,
) -> Components:
    """Kinematic split of one stop-to-stop run plus dwell and a UIC-style recovery margin.

    Recovery = pct x running time + min_per_100km x km / 100 (UIC 451-1 form).
    The running time equals `network.graph.segment_minutes` (checked in the tests).
    """
    v = cruise_kmh / 3.6
    acc_km = v * v / (2 * accel_ms2) / 1000.0
    dec_km = v * v / (2 * decel_ms2) / 1000.0
    if km < acc_km + dec_km:
        raise ValueError("segment too short to reach line speed; not the Makkah-Jeddah case")
    cruise_km = km - acc_km - dec_km
    acc_min, dec_min = v / accel_ms2 / 60.0, v / decel_ms2 / 60.0
    cruise_min = cruise_km / cruise_kmh * 60.0
    running = acc_min + dec_min + cruise_min
    loss = running - km / cruise_kmh * 60.0
    return Components(
        cruise_min=cruise_min,
        accel_min=acc_min,
        decel_min=dec_min,
        accel_decel_loss_min=loss,
        dwell_min=stops * dwell_s / 60.0,
        recovery_min=pct * running + min_per_100km * km / 100.0,
        cruise_km=cruise_km,
        accel_km=acc_km,
        decel_km=dec_km,
    )


def cruise_for_target(
    km: float, target_min: float, accel: float, decel: float, pct: float, per100: float
) -> float:
    """Uniform line speed (km/h) at which running + recovery equals `target_min` (bisection)."""

    def total(vk: float) -> float:
        return segment_minutes(km, vk, accel, decel) * (1 + pct) + per100 * km / 100.0

    lo, hi = 20.0, 400.0
    if not total(hi) <= target_min <= total(lo):
        return math.nan
    for _ in range(80):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if total(mid) > target_min else (lo, mid)
    return (lo + hi) / 2


def _v(node: Any, key: str = "value") -> Any:
    return node[key] if isinstance(node, dict) else node


def load(path: Path = CONFIG) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def analyse(cfg: dict[str, Any]) -> dict[str, Any]:
    km = _v(cfg["segment"]["km"])
    r, d, m = cfg["running"], cfg["dwell"], cfg["recovery"]
    stops = _v(d["intermediate_stops"])
    central = decompose(
        km,
        _v(r["cruise_kmh"]),
        _v(r["accel_ms2"]),
        _v(r["decel_ms2"]),
        stops,
        _v(d["dwell_s"]),
        _v(m["pct"]),
        _v(m["min_per_100km"]),
    )
    env = []
    for a, b, p, q in itertools.product(
        (_v(r["accel_ms2"], "low"), _v(r["accel_ms2"]), _v(r["accel_ms2"], "high")),
        (_v(r["decel_ms2"], "low"), _v(r["decel_ms2"]), _v(r["decel_ms2"], "high")),
        (_v(m["pct"], "low"), _v(m["pct"], "high")),
        (_v(m["min_per_100km"], "low"), _v(m["min_per_100km"], "high")),
    ):
        c = decompose(km, _v(r["cruise_kmh"]), a, b, stops, _v(d["dwell_s"]), p, q)
        env.append(
            {
                "accel_ms2": a,
                "decel_ms2": b,
                "pct": p,
                "min_per_100km": q,
                "running_min": c.running_min,
                "recovery_min": c.recovery_min,
                "total_min": c.total,
            }
        )
    envdf = pd.DataFrame(env)
    pub = {k: _v(v) for k, v in cfg["published_minutes"].items()}
    tol = _v(cfg["tolerance_min"])
    lo_t, hi_t = float(envdf.total_min.min()), float(envdf.total_min.max())
    resid = {
        k: {"central": t - central.total, "vs_envelope_low": t - hi_t, "vs_envelope_high": t - lo_t}
        for k, t in pub.items()
    }
    implied = {
        k: cruise_for_target(
            km, t, _v(r["accel_ms2"]), _v(r["decel_ms2"]), _v(m["pct"]), _v(m["min_per_100km"])
        )
        for k, t in pub.items()
    }
    target = pub["opening_2018"]
    return {
        "km": km,
        "central": {
            **central.__dict__,
            "running_min": central.running_min,
            "total_min": central.total,
        },
        "graph_segment_minutes": segment_minutes(
            km, _v(r["cruise_kmh"]), _v(r["accel_ms2"]), _v(r["decel_ms2"])
        ),
        "envelope_total_min": [lo_t, hi_t],
        "published_min": pub,
        "residual_min": resid,
        "implied_uniform_line_speed_kmh": implied,
        "tolerance_min": tol,
        "closes_43": abs(target - central.total) <= tol,
        "closes_43_anywhere_in_envelope": lo_t - tol <= target <= hi_t + tol,
        "envelope": envdf,
    }


@app.callback()
def main() -> None:
    """Haramain running-time decomposition (C-r1a-22)."""


@app.command()
def run(seed: int = seed_option(), config: Path = CONFIG, run_dir: Path = RUN_DIR) -> None:
    """Write the decomposition table, the parameter envelope and a summary."""
    rng(seed)
    cfg = load(config)
    res = analyse(cfg)
    run_dir.mkdir(parents=True, exist_ok=True)
    c = res["central"]
    comp = pd.DataFrame(
        [
            ("a line-speed running (cruise at 300 km/h)", c["cruise_min"], c["cruise_km"]),
            ("b acceleration 0 -> 300 km/h", c["accel_min"], c["accel_km"]),
            ("b braking 300 -> 0 km/h", c["decel_min"], c["decel_km"]),
            ("c dwell at intermediate stops", c["dwell_min"], 0.0),
            ("d recovery margin (UIC 451-1)", c["recovery_min"], 0.0),
            ("total", c["total_min"], res["km"]),
        ],
        columns=["component", "minutes", "km"],
    )
    comp.to_csv(run_dir / "components.csv", index=False)
    res["envelope"].to_csv(run_dir / "envelope.csv", index=False)
    summary = {k: v for k, v in res.items() if k != "envelope"}
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    write_meta(
        run_dir,
        seed,
        cfg,
        {
            "assumptions": [
                "A-r1a-033",
                "A-r1a-034",
                "A-r1a-035",
                "A-hhr-001",
                "A-hhr-002",
                "A-hhr-003",
            ]
        },
    )
    typer.echo(comp.to_string(index=False))
    typer.echo(
        json.dumps(
            {
                k: summary[k]
                for k in (
                    "envelope_total_min",
                    "residual_min",
                    "implied_uniform_line_speed_kmh",
                    "closes_43",
                )
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    app()
