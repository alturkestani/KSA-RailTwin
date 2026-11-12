"""S6_L6_CONNECTED: component counts under the current interchange rules (S1 = 3), the measured
gaps, the connector MILP on a toy item graph, and S6-L6 = one component with every required city
on the graph and none of the FIX_HHR chord-band corridors; the scenario YAML validates; the map
exists, is under 1 MB and is idempotent.

Label: synthetic demand, uncalibrated: scenario comparison, not a forecast."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
import yaml

from common import REPO_ROOT
from common.schemas import Scenario
from network import graph as ng
from optimise import connect as cn
from tests.localdata import needs_local

L6 = REPO_ROOT / cn.SCENARIO
SEARCH = REPO_ROOT / "runs/r6/l6/search.json"


def test_interchange_rules_unchanged() -> None:
    ic = ng.load_params()["interchange"]
    assert ic["walk_max_km"]["value"] == 0.4
    assert ic["same_name_max_km"]["value"] == 3.0


def test_s1_has_three_components_with_the_measured_gaps() -> None:
    s = cn.summary(cn.rail_graph([]))
    assert s["n_components"] == 3
    lines = [set(c["lines"]) for c in s["components"]]
    assert lines[1] == {"hhr"} and lines[2] == {"gcc-railway-ksa"}
    assert {"landbridge", "sar-east-passenger", "sar-north-passenger"} <= lines[0]
    gaps = {(g["a"], g["b"]): g["km"] for g in s["gaps"]}
    assert gaps[("landbridge:jeddah", "hhr:jeddah")] == pytest.approx(8.21, abs=0.005)
    assert gaps[("sar-east-passenger:dammam", "gcc-railway-ksa:dammam")] == pytest.approx(
        3.74, abs=0.005
    )


def test_l4_and_l5_add_the_belt_fragments() -> None:
    s4 = cn.summary(cn.rail_graph(cn.scenario_items("S6-L4")))
    s5 = cn.summary(cn.rail_graph(cn.scenario_items("S6-L5")))
    assert s4["n_components"] == 4 and s5["n_components"] == 4
    g4 = {(g["a"], g["b"]): g["km"] for g in s4["gaps"]}
    g5 = {(g["a"], g["b"]): g["km"] for g in s5["gaps"]}
    assert g4[("hhr:makkah", "S4-commuter_belt-makkah-045:makkah")] == pytest.approx(
        3.98, abs=0.005
    )
    assert g5[("hhr:madinah", "S4-commuter_belt-madinah-045:madinah")] == pytest.approx(
        8.96, abs=0.005
    )


def _toy() -> dict:
    """Root R and island I (S1); options a (R-I directly, capex 10), b (R-c, 4), c (c-I, 4),
    d (isolated, 1). Min capex connecting R and I: a (10) vs b + c (8): b + c."""
    st = {
        "R": {"lat": 24.0, "lon": 46.0, "name_en": "R"},
        "I": {"lat": 24.0, "lon": 47.0, "name_en": "I"},
        "M": {"lat": 24.5, "lon": 46.5, "name_en": "M"},
        "D": {"lat": 20.0, "lon": 40.0, "name_en": "D"},
    }

    def opt(name: str, k: int, *pts: str) -> dict:
        return {"kind": "opt", "name": name, "id": name, "variant": {}, "opt": k,
                "stations": [st[p] for p in pts], "host": None}  # fmt: skip

    nodes = [
        {"kind": "s1", "name": "S1-c0", "stations": [st["R"]], "host": None},
        {"kind": "s1", "name": "S1-c1", "stations": [st["I"]], "host": None},
        opt("a", 0, "R", "I"),
        opt("b", 1, "R", "M"),
        opt("c", 2, "M", "I"),
        opt("d", 3, "D"),
    ]
    edges = []
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            if cn._linked(nodes[i]["stations"], nodes[j]["stations"], 0.4, 3.0):
                edges.append((i, j))
    fast = SimpleNamespace(capex=np.array([[10.0], [4.0], [4.0], [1.0]]))
    return {"fast": fast, "nodes": nodes, "edges": edges, "n_s1": 2}


def test_milp_picks_min_capex_connected_set() -> None:
    m = _toy()
    sel = cn.solve(m, {})
    assert {m["nodes"][k]["name"] for k in sel} == {"b", "c"}
    # dropping one corridor of that set leaves the direct option
    sel2 = cn.solve(m, {}, forbid=[{"b", "c"}])
    assert {m["nodes"][k]["name"] for k in sel2} == {"a"}
    # a city only d covers forces d, which cannot connect: infeasible
    assert cn.solve(m, {"x": [5]}) is None


def _l6_items() -> list[dict]:
    d = yaml.safe_load(L6.read_text(encoding="utf-8"))
    return d["layout"]["corridors"]


def test_l6_yaml_validates_and_is_labelled() -> None:
    d = yaml.safe_load(L6.read_text(encoding="utf-8"))
    Scenario.model_validate(d)
    assert d["label"] == "comparison layout, not the recommended programme"
    assert d["layer"] == "hypothetical (ours)"
    assert d["baseline"] == "S1" and d["kind"] == "comparison_layout"
    for c in d["candidates"]:
        assert (REPO_ROOT / c).exists()
    assert len(d["candidates"]) == len(d["layout"]["corridors"])


def test_l6_is_one_component_with_every_required_city() -> None:
    ch = cn.check(_l6_items())
    assert ch["n_components"] == 1
    assert ch["all_required_on_graph"]
    req = [c for c, v in ch["cities"].items() if v["required"]]
    assert len(req) == 18


def test_l6_has_no_chord_band_corridor() -> None:
    chord = set(cn.params()["search"]["chord_band"])
    assert not {c["id"] for c in _l6_items()} & chord


@needs_local("runs/r6/v3/library/library.json", "runs/r6/v3/library/variants.json")
def test_l6_items_are_library_options() -> None:
    from optimise import variants as va

    fast = va.FastV()
    g = fast.genome_of({"corridors": _l6_items()})
    assert int((g > 0).sum()) == len(_l6_items())


@pytest.mark.skipif(not SEARCH.exists(), reason="no runs/r6/l6/search.json")
def test_map_exists_small_and_idempotent(tmp_path: Path) -> None:
    from typer.testing import CliRunner

    live = REPO_ROOT / cn.MAP
    assert live.exists() and live.stat().st_size < 1_000_000
    r = CliRunner()
    for k in (1, 2):
        res = r.invoke(cn.app, ["map", "--dest", str(tmp_path / f"m{k}.png")])
        assert res.exit_code == 0, res.output
    a, b = (tmp_path / "m1.png").read_bytes(), (tmp_path / "m2.png").read_bytes()
    assert a == b == live.read_bytes()
