"""BUILD_MOVIE: every main-cut shot has a moving-map scene (film/sim_main.py) with a legend,
and every scene draws at the start, middle and end without raising. Reads gitignored run outputs
(through RAILTWIN_RUNS_ROOT), so it skips cleanly in a fresh clone (tests/localdata.py)."""

from __future__ import annotations

import numpy as np
import pytest
import yaml

from common import REPO_ROOT
from film import render as R

NEEDED = (
    "r6/v3/national_reach.json",
    "r6/v3/results.tsv",
    "r6/top5/top5.csv",
    "r6/top5/L2.layout.yaml",
    "r7/fiscal/fiscal.json",
    "cba/CBA-S1-committed-programme/results.json",
    "study/rj/times-s1/times.csv",
    "study/rj/score/score.csv",
    "study/rj/align-s1/RJ-B/profile.parquet",
    "study/extra-travel/induced_summary.csv",
    "study/extra-travel/baseline/rj_baseline.json",
    "align/corridors-s1",
    "align/validation-v2-s1",
)
_missing = [r for r in NEEDED if not (R.runs_root() / r).exists()]
needs_runs = pytest.mark.skipif(
    bool(_missing), reason=f"local gitignored run outputs missing: {_missing}"
)


def main_ids() -> list[str]:
    d = yaml.safe_load((REPO_ROOT / "film/storyboard/shots.yaml").read_text(encoding="utf-8"))
    return [s["id"] for s in d["shots"] if s.get("cut") == "main"]


@pytest.fixture(scope="module")
def main_scenes():
    from film import sim, sim_main

    D = sim.data()
    return D, sim_main.scenes(D)


@needs_runs
def test_every_main_shot_has_a_scene(main_scenes) -> None:
    _, S = main_scenes
    ids = main_ids()
    assert ids, "no main shots"
    assert sorted(set(ids) - set(S)) == []


@needs_runs
def test_every_main_scene_has_a_legend_and_credits(main_scenes) -> None:
    _, S = main_scenes
    for sid in main_ids():
        sc = S[sid]
        assert sc.legend, sid
        if sid != "sh-08-14":  # the credits roll carries the OSM and Copernicus lines itself
            assert sc.credits_bar is True, sid


@needs_runs
def test_main_scenes_do_not_shadow_trailer_scenes(main_scenes) -> None:
    from film import sim

    D, S = main_scenes
    assert not set(S) & set(sim.scenes(D, {}))


@needs_runs
def test_titles_and_credits_flags(main_scenes) -> None:
    _, S = main_scenes
    for sid in ("sh-01-07", "sh-08-13"):
        assert S[sid].title and not S[sid].closing and not S[sid].roll, sid
    assert S["sh-08-14"].title and S["sh-08-14"].roll


@needs_runs
def test_closing_notice_only_in_the_credits(main_scenes) -> None:
    from film import sim

    _, S = main_scenes
    shots = {
        s["id"]: s
        for s in yaml.safe_load(
            (REPO_ROOT / "film/storyboard/shots.yaml").read_text(encoding="utf-8")
        )["shots"]
    }
    for lang in ("en", "ar"):
        notice = sim.CLOSING_NOTICE[lang].rstrip(".")
        for sid in main_ids():
            html_ = sim.overlay_html(shots[sid], lang, S[sid]) + sim.texts_html(lang, S[sid])
            n = html_.count(notice)
            assert n == (1 if sid == "sh-08-14" else 0), (sid, lang, n)
            for word in ("in the model", "في النموذج", "uncalibrated", "synthetic"):
                if sid != "sh-08-14":
                    assert word not in sim.texts_html(lang, S[sid]).lower(), (sid, word)


@needs_runs
def test_chart_labels_carry_no_numbers_outside_the_caption(main_scenes) -> None:
    """Text layers are words; any digit must also be in the shot's caption or be a checkpoint
    id read from docs/STATUS.md (sh-07-05)."""
    import re

    _, S = main_scenes
    shots = {
        s["id"]: s
        for s in yaml.safe_load(
            (REPO_ROOT / "film/storyboard/shots.yaml").read_text(encoding="utf-8")
        )["shots"]
    }
    for sid in main_ids():
        for _, _, en, ar, _, _ in S[sid].texts:
            for lang, txt in (("en", en), ("ar", ar)):
                cap = str(shots[sid]["on_screen_text"][lang])
                for num in re.findall(r"\d+", txt):
                    ok = num in cap or (sid == "sh-07-05" and re.fullmatch(r"CP\d", txt))
                    assert ok, (sid, lang, txt)


@needs_runs
@pytest.mark.parametrize("sid", main_ids())
def test_main_scene_draws(main_scenes, sid: str) -> None:
    from film import sim

    D, S = main_scenes
    sc = S[sid]
    T = 8.0
    rng = np.random.default_rng(1)
    ctx = {"rng": rng, "phase": rng.random(64)}
    for f in (0.0, 0.5, 1.0):
        cam = sim.layout(sim.cam_at(sc.keys, f), sc, "ar")
        c = sim.Canvas(cam)
        sc.draw(c, f * T, T, ctx)
        assert c.done().size == (sim.W, sim.H)
