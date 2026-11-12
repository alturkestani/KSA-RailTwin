"""CBA parameters: one loader for `cities/ksa/assumptions/cba_*.yaml` (W4, R5).

Each file holds `params: {key: {value, low, high, unit, price_year, currency, assumption_id |
sources, note}}`. Every key is sourced or a registered assumption with a range (CLAUDE.md, rule 1);
`Param.check()` refuses a parameter without either. Money is SAR at 2025 prices (A-cost-001).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from common import REPO_ROOT

ASSUMPTIONS = Path("cities/ksa/assumptions")
FILES = (
    "cba_appraisal.yaml",
    "cba_wei.yaml",
    "cba_externalities.yaml",
    "cba_freight.yaml",
    "cba_programme.yaml",
)


@dataclass(frozen=True)
class Param:
    key: str
    value: float
    low: float
    high: float
    unit: str = ""
    assumption_id: str = ""
    sources: tuple[str, ...] = ()
    note: str = ""
    file: str = ""
    extra: dict[str, Any] = field(default_factory=dict)

    def check(self) -> Param:
        if not (self.assumption_id or self.sources):
            raise ValueError(f"{self.file}:{self.key} has neither assumption_id nor sources")
        if not (min(self.low, self.high) <= self.value <= max(self.low, self.high)):
            raise ValueError(f"{self.file}:{self.key} value {self.value} outside [low, high]")
        return self

    @property
    def ids(self) -> list[str]:
        return [i for i in (self.assumption_id, *self.sources) if i]


def _num(x: Any) -> float | None:
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def parse(key: str, node: Any, file: str = "") -> Param | None:
    """A numeric parameter, or None for a non-numeric entry (notes, schedules are read raw)."""
    if not isinstance(node, dict):
        return None
    v = _num(node.get("value"))
    if v is None:
        return None
    lo = _num(node.get("low"))
    hi = _num(node.get("high"))
    src = node.get("sources") or node.get("source") or []
    if isinstance(src, str):
        src = [src]
    known = {"value", "low", "high", "unit", "assumption_id", "sources", "source", "note"}
    return Param(
        key=key,
        value=v,
        low=v if lo is None else lo,
        high=v if hi is None else hi,
        unit=str(node.get("unit", "")),
        assumption_id=str(node.get("assumption_id") or ""),
        sources=tuple(str(s) for s in src),
        note=str(node.get("note", "")),
        file=file,
        extra={k: x for k, x in node.items() if k not in known},
    ).check()


@dataclass
class Params:
    numeric: dict[str, Param]
    raw: dict[str, Any]

    def __getitem__(self, key: str) -> Param:
        return self.numeric[key]

    def get(self, key: str, default: float | None = None) -> float | None:
        p = self.numeric.get(key)
        return p.value if p else default

    def has(self, key: str) -> bool:
        return key in self.numeric


def load(root: Path = REPO_ROOT, files: tuple[str, ...] = FILES) -> Params:
    numeric: dict[str, Param] = {}
    raw: dict[str, Any] = {}
    for f in files:
        p = root / ASSUMPTIONS / f
        if not p.exists():
            continue
        doc = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        for k, node in (doc.get("params") or {}).items():
            raw[k] = node
            q = parse(k, node, f)
            if q is not None:
                if k in numeric:
                    raise ValueError(f"parameter {k} defined twice ({numeric[k].file}, {f})")
                numeric[k] = q
    return Params(numeric, raw)
