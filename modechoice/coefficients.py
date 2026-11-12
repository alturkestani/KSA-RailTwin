"""Coefficient loader for the intercity MNL (W8 mode choice).

Reads the R1d literature priors (`cities/ksa/assumptions/mode_choice_priors.yaml`, read-only)
into typed `Param` records (value, range, assumption id, source, status) and the R3 parameters
(`cities/ksa/assumptions/mode_choice_r3.yaml`). Coefficients are "literature-based until survey
results exist"; nothing here is estimated from Saudi data.

API used by `demand/gravity.py` and `demand/calibrate.py`:
    priors = load_priors()                      # dict[str, Param]: "asc.rail", "ivt.car", ...
    coefs = base_coefficients(priors)           # Coefficients at the prior central values
    coefs = corner(priors, {"ivt.rail": "low"}) # any key at its range "low"/"high"/"base"
    coefs = apply_overrides(coefs, {"asc.rail": -0.4}, priors)  # refuses values outside the range
    r3 = load_r3()                              # dict (the R3 YAML)
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any, Literal

import yaml

from common import REPO_ROOT

PRIORS_PATH = REPO_ROOT / "cities" / "ksa" / "assumptions" / "mode_choice_priors.yaml"
R3_PATH = REPO_ROOT / "cities" / "ksa" / "assumptions" / "mode_choice_r3.yaml"
MODES: tuple[str, ...] = ("car", "rail", "air", "bus")
NON_CAR: tuple[str, ...] = ("rail", "air", "bus")
COEF_LABEL = "coefficients literature-based until survey results exist"

# keys of the utility coefficients the MNL uses (all from the priors)
UTILITY_KEYS: tuple[str, ...] = (
    "asc.rail",
    "asc.air",
    "asc.bus",
    "ivt.car",
    "ivt.rail",
    "ivt.air",
    "ivt.bus",
    "access_egress",
    "headway",
    "cost",
    "on_time",
)
# design-only attribute priors with no network data yet (in the registry, not in the utility)
_ATTRIBUTE_PRIORS = (
    "comfort_upper_class",
    "women_only_or_family_carriage",
    "prayer_facilities",
    "luggage_large_allowance",
    "heat_shaded_transfer",
)
_SCALAR_PRIORS = {
    "access_egress": "access_egress_time",
    "headway": "headway",
    "cost": "cost",
    "on_time": "on_time_share",
}

Corner = Literal["low", "base", "high"]


@dataclass(frozen=True)
class Param:
    """One registered parameter: central value, [low, high] range, and its provenance."""

    key: str
    value: float
    low: float
    high: float
    unit: str
    assumption: str | None
    source: str | None
    status: str
    note: str = ""

    def at(self, which: Corner) -> float:
        return {"low": self.low, "base": self.value, "high": self.high}[which]

    def contains(self, x: float, tol: float = 1e-12) -> bool:
        return self.low - tol <= x <= self.high + tol


@dataclass(frozen=True)
class Coefficients:
    """Utility coefficients. Car is the reference alternative (ASC 0)."""

    asc: dict[str, float]
    ivt: dict[str, float]
    access_egress: float
    headway: float
    cost: float
    on_time: float
    tags: dict[str, str] = field(default_factory=dict)

    def flat(self) -> dict[str, float]:
        out = {f"asc.{m}": self.asc[m] for m in NON_CAR}
        out.update({f"ivt.{m}": self.ivt[m] for m in MODES})
        out.update(
            {
                "access_egress": self.access_egress,
                "headway": self.headway,
                "cost": self.cost,
                "on_time": self.on_time,
            }
        )
        return out

    @classmethod
    def from_flat(cls, flat: dict[str, float], tags: dict[str, str] | None = None) -> Coefficients:
        missing = [k for k in UTILITY_KEYS if k not in flat]
        if missing:
            raise KeyError(f"missing coefficients: {missing}")
        return cls(
            asc={"car": 0.0, **{m: float(flat[f"asc.{m}"]) for m in NON_CAR}},
            ivt={m: float(flat[f"ivt.{m}"]) for m in MODES},
            access_egress=float(flat["access_egress"]),
            headway=float(flat["headway"]),
            cost=float(flat["cost"]),
            on_time=float(flat["on_time"]),
            tags=dict(tags or {}),
        )


def _param(key: str, d: dict[str, Any]) -> Param:
    lo, hi = (float(x) for x in d["range"])
    if lo > hi:
        lo, hi = hi, lo
    value = d["value"]
    if not isinstance(value, int | float):
        raise TypeError(f"{key}: non-scalar value {value!r}")
    if d.get("assumption") is None and d.get("source") is None:
        raise ValueError(f"{key}: neither assumption nor source (rule 1)")
    return Param(
        key=key,
        value=float(value),
        low=lo,
        high=hi,
        unit=str(d.get("unit", "")),
        assumption=d.get("assumption"),
        source=d.get("source"),
        status=str(d.get("status", "")),
        note=str(d.get("note", "")),
    )


def load_priors(path: Path = PRIORS_PATH) -> dict[str, Param]:
    """Every scalar prior with its range and id. Keys: UTILITY_KEYS + attribute priors +
    'aux.late_arrival_mean_delay' + 'vot.<name>' (scalar VoT cross-check rows)."""
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    out: dict[str, Param] = {}
    for m in NON_CAR:
        out[f"asc.{m}"] = _param(f"asc.{m}", raw["asc"][m])
    for m in MODES:
        out[f"ivt.{m}"] = _param(f"ivt.{m}", raw["in_vehicle_time"][m])
    for key, yaml_key in _SCALAR_PRIORS.items():
        out[key] = _param(key, raw[yaml_key])
    for key in _ATTRIBUTE_PRIORS:
        out[key] = _param(key, raw[key])
    for key, d in raw.get("auxiliary", {}).items():
        out[f"aux.{key}"] = _param(f"aux.{key}", d)
    for key, d in raw.get("vot_cross_check", {}).items():
        if isinstance(d, dict) and isinstance(d.get("value"), int | float):
            out[f"vot.{key}"] = _param(f"vot.{key}", d)
    return out


def load_r3(path: Path = R3_PATH) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


def base_coefficients(priors: dict[str, Param] | None = None) -> Coefficients:
    priors = priors or load_priors()
    return corner(priors, {})


def corner(priors: dict[str, Param], settings: dict[str, Corner]) -> Coefficients:
    """Coefficients with each key in `settings` at its range end ('low' = numerically lowest)."""
    unknown = sorted(set(settings) - set(UTILITY_KEYS))
    if unknown:
        raise KeyError(f"not utility coefficients: {unknown}")
    flat = {k: priors[k].at(settings.get(k, "base")) for k in UTILITY_KEYS}
    tags = {k: v for k, v in settings.items() if v != "base"}
    return Coefficients.from_flat(flat, tags)


def apply_overrides(
    coefs: Coefficients,
    overrides: dict[str, float],
    priors: dict[str, Param] | None = None,
) -> Coefficients:
    """Calibration hook: set coefficients (e.g. {"asc.rail": -0.4}); refuses any value outside the
    prior's registered range or any key that is not a utility coefficient."""
    priors = priors or load_priors()
    flat = coefs.flat()
    for k, x in overrides.items():
        if k not in UTILITY_KEYS:
            raise KeyError(f"{k} is not a utility coefficient")
        p = priors[k]
        if not p.contains(float(x)):
            raise ValueError(
                f"{k}={x} outside its registered range [{p.low}, {p.high}] ({p.assumption})"
            )
        flat[k] = float(x)
    tags = dict(coefs.tags)
    tags.update({k: "override" for k in overrides})
    return Coefficients.from_flat(flat, tags)


def vot_ratios(r3: dict[str, Any], priors: dict[str, Param]) -> dict[str, float]:
    """Purpose -> VoT ratio to the non-work value (A-cba-010 via the priors' cross-check)."""
    pur = r3["purpose"]
    ref = priors[f"vot.{pur['vot_ratio_reference']}"].value
    return {p: priors[f"vot.{k}"].value / ref for p, k in pur["vot_key"].items()}


def r3_value(r3: dict[str, Any], *path: str, which: Corner = "base") -> float:
    """A scalar from the R3 YAML at its base value or range end."""
    node: Any = r3
    for p in path:
        node = node[p]
    if which == "base":
        return float(node["value"])
    lo, hi = sorted(float(x) for x in node["range"])
    return lo if which == "low" else hi


def with_tags(coefs: Coefficients, **tags: str) -> Coefficients:
    return replace(coefs, tags={**coefs.tags, **tags})
