"""R1c: corridor estimator on the fixture corridor. The test register, map and profile below are
invented (fixture); the last tests check the real map against the real register."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml
from typer.testing import CliRunner

from common.schemas import LineSpec, load_cost_register
from costs import estimate

REPO = Path(__file__).resolve().parents[1]
REAL_REGISTER = REPO / "cities" / "ksa" / "costs" / "cost_register.yaml"
REAL_UPLIFTS = REPO / "cities" / "ksa" / "costs" / "uplifts.yaml"


def _row(rid: str, unit: str, lo: float, c: float, hi: float, cat: str = "system") -> dict:
    return {
        "id": rid,
        "item": f"fixture {rid}",
        "category": cat,
        "line_type": "n/a",
        "terrain": "n/a",
        "unit": unit,
        "currency": "SAR",
        "price_year": 2025,
        "low": lo,
        "central": c,
        "high": hi,
        "source": "assumed",
        "status": "assumed",
        "assumption_id": "A-fixture",
    }


FIX_ROWS = [
    _row("C-fx-base", "SAR_m_per_km", 20, 30, 45, "line_type"),
    _row("C-fx-dunes", "pct", 5, 10, 20, "terrain"),
    _row("C-fx-tunnel", "SAR_m_per_km", 150, 200, 300, "structure"),
    _row("C-fx-viaduct", "SAR_m_per_km", 60, 80, 120, "structure"),
    _row("C-fx-etcs2", "SAR_m_per_km", 1, 1.5, 2),
    _row("C-fx-ocs", "SAR_m_per_km", 2, 3, 4, "electrification"),
    _row("C-fx-st-term", "SAR_m_per_station", 200, 300, 500, "station"),
    _row("C-fx-st-int", "SAR_m_per_station", 50, 80, 120, "station"),
    _row("C-fx-depot", "SAR_m_per_unit", 300, 400, 600, "depot"),
    _row("C-fx-emu", "SAR_m_per_trainset", 40, 50, 70, "rolling_stock"),
    _row("C-fx-land", "pct_of_capex", 4, 6, 8, "land"),
    _row("C-fx-sub", "SAR_m_per_unit", 50, 80, 100, "power"),
    _row("C-fx-tel", "SAR_m_per_km", 0.5, 1, 2),
    _row("C-fx-vshare", "pct", 1, 5, 15, "structure"),
    _row("C-fx-renew", "pct", 70, 100, 120, "renewal"),
    _row("C-fx-util", "pct_of_capex", 1, 2, 4, "utilities"),
    _row("C-fx-dpm", "pct_of_capex", 8, 12, 18, "design_pm"),
    _row("C-fx-cont", "pct_of_capex", 10, 20, 30, "contingency"),
    _row("C-fx-op", "SAR_per_train_km", 60, 90, 140, "opex"),
    _row("C-fx-mow", "SAR_m_per_km_per_yr", 0.1, 0.2, 0.3, "opex"),
    _row("C-fx-life-rs", "years", 25, 30, 35, "renewal"),
]
FIX_MAP = {
    "line_base": {"conventional_passenger": "C-fx-base"},
    "terrain_premium": {"dunes": "C-fx-dunes", "sabkha": None},
    "structure": {"tunnel": "C-fx-tunnel", "viaduct": "C-fx-viaduct"},
    "signalling": {"conventional_passenger": {"etcs_l2": "C-fx-etcs2"}},
    "systems_per_km": {"conventional_passenger": {"telecom": "C-fx-tel"}},
    "electrification": {"conventional_passenger": "C-fx-ocs"},
    "power": {"conventional_passenger": "C-fx-sub"},
    "station": {
        "conventional_passenger": {"terminal": "C-fx-st-term", "intermediate": "C-fx-st-int"}
    },
    "depot": {"conventional_passenger": "C-fx-depot"},
    "rolling_stock": {"conventional_passenger": {"electric": "C-fx-emu"}},
    "land": {"conventional_passenger": "C-fx-land"},
    "utilities": "C-fx-util",
    "design_pm": "C-fx-dpm",
    "contingency": "C-fx-cont",
    "opex": {
        "conventional_passenger": [
            {"name": "train_ops", "ids": ["C-fx-op"], "driver": "train_km", "to_sar_m": 1e-6},
            {"name": "mow", "ids": ["C-fx-mow"], "driver": "route_km"},
            {"name": "sand", "ids": ["C-fx-mow", "C-fx-dunes"], "driver": "route_km_dunes"},
        ]
    },
    "renewals": [
        {
            "name": "rolling_stock",
            "life_id": "C-fx-life-rs",
            "components": ["rolling_stock"],
            "share_ids": ["C-fx-renew"],
        }
    ],
}
FIX_PROFILE = {
    "terrain_shares": {"flat_desert": 0.8, "dunes": 0.2},
    "structure_shares": {"tunnel": 0.0, "viaduct": {"register_id": "C-fx-vshare"}},
    "substation_spacing_km": 50,
    "signalling": "etcs_l2",
    "depots": 1,
    "turnaround_min": 15,
    "fleet_spare_share": 0.1,
    "operating_days_per_year": 365,
    "construction_years": {"low": 4, "central": 5, "high": 7},
    "appraisal_stage": "strategic",
}


@pytest.fixture
def line(fixtures: Path) -> LineSpec:
    return LineSpec.model_validate(yaml.safe_load((fixtures / "corridor.yaml").read_text()))


def _reg() -> dict[str, dict]:
    return {r["id"]: dict(r) for r in FIX_ROWS}


def test_estimate_ranges_and_trace(line: LineSpec) -> None:
    s, df, trace = estimate.estimate(line, _reg(), FIX_PROFILE, FIX_MAP, seed=1, draws=2000)
    c = s["capex_base_sar_m"]
    assert c["P10"] <= c["P50"] <= c["P90"] and c["P10"] < c["P90"]
    assert s["opex_sar_m_per_year"]["P50"] > 0
    assert s["operations"]["fleet"] >= 2 and s["operations"]["train_km_yr"] > 0
    ids = {i for t in trace for i in t["register_id"].split(", ")}
    assert ids <= set(_reg())  # every input traces to a register id
    assert any(t["component"].startswith("terrain_premium[dunes]") for t in trace)
    assert any(t["component"] == "structure[viaduct]" for t in trace)
    # rolling stock (30-year life) is renewed once inside 40 years, never inside 25
    r = s["renewals_sar_m_undiscounted"]
    assert r["60y"]["P50"] >= r["40y"]["P50"] > 0
    assert s["label"].startswith("synthetic demand, uncalibrated")


def test_estimate_deterministic(line: LineSpec) -> None:
    a = estimate.estimate(line, _reg(), FIX_PROFILE, FIX_MAP, seed=1, draws=1000)
    b = estimate.estimate(line, _reg(), FIX_PROFILE, FIX_MAP, seed=1, draws=1000)
    assert a[0] == b[0] and a[1].equals(b[1])


def test_unknown_or_missing_id_is_refused(line: LineSpec) -> None:
    reg = _reg()
    reg["C-fx-ocs"] = {**reg["C-fx-ocs"], "status": "unknown", "low": None}
    with pytest.raises(estimate.TraceError):
        estimate.estimate(line, reg, FIX_PROFILE, FIX_MAP, seed=1, draws=100)
    bad_map = {**FIX_MAP, "utilities": "C-fx-nope"}
    with pytest.raises(estimate.TraceError):
        estimate.estimate(line, _reg(), FIX_PROFILE, bad_map, seed=1, draws=100)


def _map_ids(obj: object) -> set[str]:
    if isinstance(obj, str):
        return {obj} if obj.startswith("C-") else set()
    if isinstance(obj, dict):
        return set().union(*(_map_ids(v) for v in obj.values())) if obj else set()
    if isinstance(obj, list):
        return set().union(*(_map_ids(v) for v in obj)) if obj else set()
    return set()


@pytest.mark.skipif(not REAL_REGISTER.exists(), reason="register not built yet")
def test_real_map_resolves_to_register() -> None:
    reg = {i.id: i for i in load_cost_register(REAL_REGISTER)}
    cmap = yaml.safe_load(estimate.MAP.read_text())
    ids = _map_ids(cmap)
    assert ids, "map is empty"
    missing = sorted(i for i in ids if i not in reg)
    unknown = sorted(i for i in ids if i in reg and reg[i].status == "unknown")
    assert missing == [] and unknown == []


@pytest.mark.skipif(
    not (REAL_REGISTER.exists() and REAL_UPLIFTS.exists()), reason="register not built yet"
)
def test_readme_command_is_deterministic(fixtures: Path, tmp_path: Path) -> None:
    outs = []
    for k in ("a", "b"):
        out = tmp_path / k
        args = [
            "--corridor", str(fixtures / "corridor.yaml"),
            "--register", str(REAL_REGISTER),
            "--uplifts", str(REAL_UPLIFTS),
            "--seed", "1", "--draws", "2000", "--out", str(out),
        ]  # fmt: skip
        res = CliRunner().invoke(estimate.app, args)
        assert res.exit_code == 0, res.output
        outs.append(out)
    a, b = (yaml.safe_load((o / "base.yaml").read_text()) for o in outs)
    assert a == b
    meta = json.loads((outs[0] / "meta.json").read_text())
    assert meta["seed"] == 1 and meta["register_ids"]
    trace = (outs[0] / "trace.csv").read_text()
    reg_ids = {i.id for i in load_cost_register(REAL_REGISTER)}
    for rid in meta["register_ids"]:
        for part in rid.split(", "):
            assert part in reg_ids and part in trace


@pytest.mark.skipif(not REAL_REGISTER.exists(), reason="register not built yet")
def test_reconcile_covers_every_line_type() -> None:
    from costs import reconcile

    bu, rec, _ = reconcile.reconcile(seed=1, draws=500)
    assert set(bu["line_type"]) == set(reconcile.LINE_TYPES)
    assert set(rec["line_type"]) == set(reconcile.LINE_TYPES)  # every type has a top-down check
    assert (bu["infra_P10"] <= bu["infra_P50"]).all() and (bu["infra_P50"] <= bu["infra_P90"]).all()
    big = rec[(rec["gap_vs_central_pct"].abs() > 30) & ~rec["within_td_range"]]
    assert big["flag"].all()  # every large gap is flagged, none is averaged away
