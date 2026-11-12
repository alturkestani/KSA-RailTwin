"""R6 search engines on toy problems (no judge, seconds)."""

from __future__ import annotations

from types import SimpleNamespace

import numpy as np

from optimise import search


def toy(n: int = 4) -> SimpleNamespace:
    P = len(search.PHASES)
    # corridor values per phase and population: corridor 0 positive, 1 negative, 2 positive but
    # expensive, 3 positive only if deferred (all populations equal)
    v = np.array(
        [
            [10, 9, 8, 6],
            [-5, -4, -3, -2],
            [20, 18, 16, 12],
            [-1, 0.5, 1, 2],
        ],
        dtype=float,
    )[:n]
    pvb = np.repeat(np.clip(v, 0, None)[:, :, None], 3, axis=2)
    pvc = np.repeat(np.clip(-v, 0, None)[:, :, None], 3, axis=2)
    capex = np.array([[1.0] * P, [1.0] * P, [5.0] * P, [1.0] * P])[:n]
    return SimpleNamespace(ids=[f"c{i}" for i in range(n)], pvb=pvb, pvc=pvc, capex=capex)


def test_milp_picks_best_phase_within_budget() -> None:
    f = toy()
    g = search.milp(f, ceiling=2.5, deps={})
    # within capex 2.5: corridor 0 at 2030 (10) and corridor 3 at 2050 (2); never 1; 2 too dear
    assert g.tolist() == [1, 0, 0, 4]
    g = search.milp(f, ceiling=10.0, deps={})
    assert g.tolist() == [1, 0, 1, 4]


def test_milp_respects_dependencies() -> None:
    f = toy()
    # corridor 3 needs corridor 1 built no later than itself; with capex 2.5 the pair plus
    # corridor 0 does not fit, so corridor 3 drops out
    g = search.milp(f, ceiling=2.5, deps={3: [1]})
    assert g.tolist() == [1, 0, 0, 0]


def test_repair_moves_dependent_to_dependency_phase() -> None:
    g = np.array([1, 3, 0])
    out = search.repair(g, {0: [1]})
    assert out.tolist() == [3, 3, 0]


def test_nondominated_sort_and_dominates() -> None:
    F = np.array([[3, -1, 0], [2, -1, 0], [1, 0, 5], [3, -1, 0]])
    fronts = search.nondominated_sort(F)
    assert set(fronts[0]) == {0, 2, 3}
    assert fronts[1] == [1]
    assert search.dominates(F[0], F[1])
    assert not search.dominates(F[0], F[3])


def test_layout_hash_order_free() -> None:
    a = {"corridors": [{"id": "x", "phase": 2030}, {"id": "y", "phase": 2035}]}
    b = {"corridors": [{"phase": 2035, "id": "y"}, {"id": "x", "phase": 2030}]}
    assert search.layout_hash(a) == search.layout_hash(b)
