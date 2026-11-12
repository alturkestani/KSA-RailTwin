"""FIX_FILM_STORY (Tariq, 10 Nov 2026): plain-language money lines, the north/south sequence and
the Arabic credits. Fast checks on committed files only."""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path

import pytest

from common import REPO_ROOT
from film import render

LINES = REPO_ROOT / "film/script/lines.csv"
SHOTS = REPO_ROOT / "film/storyboard/shots.yaml"
EDITS = REPO_ROOT / "film/storyboard/story-edits.csv"
ROUNDING = REPO_ROOT / "film/storyboard/rounding-log.csv"
NEW = ["m-08-14", "m-08-15", "m-08-16", "m-08-17", "m-08-18", "m-08-19"]
CHANGED = ["m-04-07"] + [f"m-08-0{i}" for i in range(1, 9)]
FINANCE = (
    "net present value",
    "npv",
    "present value",
    "robust value",
    "fiscal",
    "صافي القيمة الحالية",
    "بقيمتها الحالية",
    "المالية العامة",
    "الصامد",
)


def _main_rows() -> list[dict[str, str]]:
    with LINES.open(encoding="utf-8", newline="") as fh:
        return [r for r in csv.DictReader(fh) if r["cut"] == "main"]


def test_no_finance_terms_in_main_lines() -> None:
    for r in _main_rows():
        low = r["text"].lower()
        hits = [w for w in FINANCE if w in low]
        assert not hits, (r["lang"], r["line_id"], hits)


def test_new_lines_both_languages_with_tashkeel() -> None:
    rows = {(r["lang"], r["line_id"]): r for r in _main_rows()}
    for lid in NEW:
        assert ("en", lid) in rows and ("ar", lid) in rows
        ar = rows["ar", lid]
        assert ar["speech_text"] and ar["native_review"] == "pending"
    for lid in CHANGED:
        assert rows["ar", lid]["native_review"] == "pending"


def test_story_edits_list_every_change_and_m0806() -> None:
    with EDITS.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    got = {(r["line_id"], r["lang"]) for r in rows}
    for lid in CHANGED + NEW:
        assert (lid, "en") in got and (lid, "ar") in got
    m0806 = [r for r in rows if r["line_id"] == "m-08-06"]
    assert m0806 and all(r["kind"] == "meaning_unchanged" for r in m0806)
    assert all(r["figures_before"] == r["figures_after"] for r in m0806)


def test_rounding_log_is_correct() -> None:
    with ROUNDING.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    assert {r["line_id"] for r in rows} >= {"m-08-01", "m-08-02", "m-08-03", "m-08-04", "m-08-08"}
    for r in rows:
        ex = r["exact_value"].replace(",", "")
        rd = r["rounded_value"].replace(" million", "")
        if not re.fullmatch(r"-?\d+(\.\d+)?", ex):
            lo, hi = (float(x) for x in re.findall(r"\d+\.\d+", ex))
            assert round(lo, 1) == round(hi, 1) == float(rd), r
            continue
        v = float(ex) / (1e6 if "million" in r["rounded_value"] else 1)
        dec = len(rd.split(".")[1]) if "." in rd else 0
        if r["line_id"] == "m-08-16":
            assert round(v, -1) == float(rd), r
        else:
            assert round(v, dec) == float(rd), r


@pytest.mark.skipif(
    not (render.runs_root() / "r6/top5/top5.csv").exists(),
    reason="local gitignored inputs missing: runs/r6/top5/top5.csv",
)
def test_bcr_wording_matches_published_values() -> None:
    runs = render.runs_root()
    top5 = {
        r["layout"]: r for r in csv.DictReader((runs / "r6/top5/top5.csv").open(encoding="utf-8"))
    }
    if not top5:
        return
    en = {r["line_id"]: r["text"] for r in _main_rows() if r["lang"] == "en"}
    for lid, lay, want in (
        ("m-08-02", "S6-L2", "6"),
        ("m-08-03", "S6-L1", "2.3"),
        ("m-08-04", "S6-L3", "1.1"),
    ):
        v = float(top5[lay]["bcr_p50_medium"])
        assert f"{round(v, 1):g}" == want and f"about {want}" in en[lid]


def test_arabic_credits_have_no_elevenlabs() -> None:
    ar = " ".join(render.credits_lines("ar"))
    assert "ElevenLabs" not in ar and "George" not in ar
    assert "نبرة" in ar
    assert "George" in " ".join(render.credits_lines("en"))


def test_routed_lines_drop_the_straight_sketch(tmp_path: Path) -> None:
    from film.sim_main import routed_lines

    gj = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"kind": "routed"},
                "geometry": {
                    "type": "LineString",
                    "coordinates": [[40, 20], [40.1, 20.2], [40.3, 20.3]],
                },
            },
            {
                "type": "Feature",
                "properties": {"kind": "straight_sketch"},
                "geometry": {"type": "LineString", "coordinates": [[40, 20], [40.3, 20.3]]},
            },
        ],
    }
    p = tmp_path / "a.geojson"
    p.write_text(json.dumps(gj), encoding="utf-8")
    out = routed_lines(p)
    assert len(out) == 1 and len(out[0]) == 3


def test_render_manifest_has_every_main_shot() -> None:
    from film import shots

    main = [s["id"] for s in shots.load_shots(SHOTS) if s["cut"] == "main"]
    for lang in ("en", "ar"):
        path = REPO_ROOT / f"film/assemble/renders-main-{lang}.csv"
        with path.open(encoding="utf-8", newline="") as fh:
            rows = list(csv.DictReader(fh))
        assert [r["shot_id"] for r in rows] == main
        assert all(not r["figures_not_found"] for r in rows)
