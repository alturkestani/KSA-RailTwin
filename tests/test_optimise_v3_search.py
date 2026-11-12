"""R6_V3 extended fast model on a toy option set (no judge, seconds)."""

from __future__ import annotations

import numpy as np

from optimise import search as se
from optimise import variants as va

P = len(se.PHASES)


def toy() -> va.FastV:
    """Corridor c0: base (value 5 at any phase, capex 4) and a cheaper variant (value 6, capex 2);
    corridor c1: base only (value 3, capex 3)."""
    f = va.FastV.__new__(va.FastV)
    f.ids = ["c0", "c1"]
    f.opts = [("c0", {}, "c0"), ("c0", {"electrified": False}, "c0-vx"), ("c1", {}, "c1")]
    f.index = {"c0": 0, "c1": 1}
    f.opt_corr = np.array([0, 0, 1])
    f.offs = np.array([0, 2])
    f.nopt = np.array([2, 1])
    f.maxval = f.nopt * P
    val = np.array([5.0, 6.0, 3.0])
    f.pvb = np.repeat(np.repeat(val[:, None, None], P, axis=1), 3, axis=2)
    f.pvc = np.zeros_like(f.pvb)
    f.pvc90 = np.zeros_like(f.pvb)
    f.capex = np.repeat(np.array([4.0, 2.0, 3.0])[:, None], P, axis=1)
    f.popv = np.array([1.0, 2.0])
    f.metros = ["m"]
    f.reach = {b: np.zeros((3, 1, 2), dtype=bool) for b in ("60", "120")}
    f.reach["120"][0, 0, 0] = True
    f.reach["120"][1, 0, 1] = True
    return f


def test_milp_chooses_one_option_per_corridor() -> None:
    f = toy()
    g = va.milp(f, ceiling=5.0, deps={})
    # within capex 5: the variant (6, capex 2) and c1 (3, capex 3); never both c0 options
    o, ph = f.decode(g)
    assert sorted(o.tolist()) == [1, 2]
    assert f.score(g)["robust_npv"] == 9.0
    assert f.score(g)["n_variants"] == 1


def test_genome_layout_round_trip_and_reach_union() -> None:
    f = toy()
    g = np.array([1 + 1 * P + 2, 1 + 0])  # c0 variant at phase index 2, c1 base at 2030
    lay = f.layout_of(g, "t")
    assert lay["corridors"][0] == {"id": "c0", "phase": se.PHASES[2], "electrified": False}
    assert lay["corridors"][1] == {"id": "c1", "phase": se.PHASES[0]}
    assert f.genome_of(lay).tolist() == g.tolist()
    assert f.score(g)["access_gain_120"] == 2.0


def test_repair_moves_phase_and_keeps_option() -> None:
    f = toy()
    g = np.array([1 + 1 * P + 0, 1 + 3])  # c0 variant 2030 depends on c1 at 2050
    r = va.repair(f, g, {0: [1]})
    o, ph = f.decode(r)
    assert o.tolist() == [1, 2]
    assert ph.tolist() == [3, 3]


def test_backtest_leaves_and_nan_equality() -> None:
    d = {"a": {"b": [1.0, float("nan")]}, "c": "x"}
    lv = va.leaves(d)
    assert set(lv) == {"/a/b[0]", "/a/b[1]", "/c"}
    assert va.same(float("nan"), float("nan"))
    assert not va.same(1.0, 1.0 + 1e-12)


def test_first_front_matches_r6_sort() -> None:
    rng = np.random.default_rng(3)
    F = np.round(rng.normal(size=(60, 3)), 1)
    F[5] = F[4]  # duplicates stay together
    assert va.first_front(F) == sorted(se.nondominated_sort(F)[0])
