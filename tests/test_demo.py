"""R9: the fixture-scale demo (`make demo`, `common.demo`) on invented fixtures, in seconds."""

from __future__ import annotations

import json

from common import demo
from common.labels import LABEL


def test_screening_and_cba_steps(tmp_path) -> None:
    inp = demo.load_inputs()
    scr = demo.screening_step(inp, tmp_path / "screening", seed=1)
    assert scr["settlements"] == len(inp["screening"]["dist_existing_km"])
    assert 0 < scr["long_list"] <= scr["settlements"]
    assert (tmp_path / "screening" / "meta.json").exists()
    cb = demo.cba_step(inp, tmp_path / "cba", seed=1)
    assert cb["label"] == LABEL and cb["fixture"] is True
    for row in cb["results"].values():
        npv = row["npv"]
        assert npv["P10"] <= npv["P50"] <= npv["P90"]
    again = demo.cba_step(inp, tmp_path / "cba2", seed=1)
    assert again["results"] == cb["results"]  # deterministic for a seed (rule 10)


def test_dashboard_step_answers_with_labels(tmp_path) -> None:
    summary = demo.dashboard_step(demo.load_inputs(), tmp_path / "dash")
    assert summary["url"].startswith("http://127.0.0.1:")
    assert all(summary["endpoints"].values()), summary["endpoints"]
    meta = json.loads((tmp_path / "dash" / "api_meta.json").read_text(encoding="utf-8"))
    assert meta["label"] == LABEL
