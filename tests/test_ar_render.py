"""common.ar_render and the Arabic typography rule (FIX_R8 item 4, docs/glossary.ar.md
§typography): every numeric run of the Arabic summary is in a left-to-right isolate, the HTML is
RTL with the bundled font, and (when Chrome is installed) the measured visual order is right."""

from __future__ import annotations

import re
import subprocess
from collections import Counter
from pathlib import Path

import pytest

from common import REPO_ROOT
from common.ar_render import (
    LRI,
    NBSP,
    PDI,
    VIEWPORTS,
    bidi_probe,
    chrome_usable,
    isolate_numeric_runs,
    md_to_html,
)
from common.labels import ALIGNMENT_LIMITATION, LABEL
from common.sources import compare, tokens

AR = REPO_ROOT / "docs/executive-summary.ar.md"
LABEL_LINE = f"> Labels: {LABEL}. {ALIGNMENT_LIMITATION}."


def test_isolate_numeric_runs() -> None:
    line = "قيمة −2,958 / −724 / +1,631 مليون (P10 / P50 / P90)، 3–10 كم، `runs/a-1` و2030"
    out = isolate_numeric_runs(line)
    nb = NBSP
    assert f"{LRI}−2,958{nb}/{nb}−724{nb}/{nb}+1,631{PDI}" in out
    # A fully numeric parenthetical sits inside its isolate (FIX_R8_RTL item 1).
    assert f"{LRI}(P10{nb}/{nb}P50{nb}/{nb}P90){PDI}" in out
    assert f"{LRI}3–10{PDI}" in out
    assert "`runs/a-1`" in out and f"{LRI}2030" not in out
    assert isolate_numeric_runs(out) == out  # idempotent
    assert tokens(out) == tokens(line)  # the bilingual check reads through isolates and NBSPs


def test_isolation_is_idempotent_and_migrates_the_old_form() -> None:
    old = f"ريال ({LRI}P10 / P50 / P90{PDI}) و{LRI}−894{PDI} الأخضر 2026[^S-cp1-060] على"
    once = isolate_numeric_runs(old)
    assert f"({LRI}P10" not in once and f"{LRI}(P10{NBSP}/" in once
    assert f"2026{LRI}[^S-cp1-060]{PDI} على" in once
    assert isolate_numeric_runs(once) == once
    for ln in AR.read_text(encoding="utf-8").splitlines()[1:]:
        if ln.strip() != LABEL_LINE:
            assert isolate_numeric_runs(isolate_numeric_runs(ln)) == isolate_numeric_runs(ln)
    # A footnote definition keeps its marker at the start of the line.
    fn = "[^S-054]: MEED، 2026-01-21؛ مصدر ثانوي"
    assert isolate_numeric_runs(fn) == fn


def test_no_line_break_inside_a_run() -> None:
    text = AR.read_text(encoding="utf-8")
    isolates = re.findall(f"{LRI}([^{PDI}]*){PDI}", text)
    assert len(isolates) > 20
    for iso in isolates:
        assert not re.search(r" [/–]|[/–] ", iso), iso  # only no-break spaces inside a run
    html = md_to_html(text, "../fonts")
    assert "span.nr { white-space: nowrap; }" in html
    spans = re.findall(f'<span class="nr">{LRI}[^<]*{PDI}</span>', html)
    assert len(spans) == len(isolates)


def test_footnote_markers_after_numbers_and_ids_are_isolated() -> None:
    text = AR.read_text(encoding="utf-8")
    pairs = re.findall(r"(\S+?)(?=\[\^S-[^\]]+\](?!:))", text)
    bare = re.findall(r"(?<!\u2066)\[\^S-[^\]]+\](?!:)", text)
    assert pairs and not bare, bare
    assert f"الكتاب الأخضر 2026{LRI}[^S-cp1-060]{PDI}" in text


def test_bilingual_check_reads_through_nbsp() -> None:
    plain = "قيمة −2,958 / −724 / +1,631 و 3–10"
    assert tokens(isolate_numeric_runs(plain)) == tokens(plain)
    assert tokens(f"{LRI}−2,958{NBSP}/{NBSP}−724{PDI}") == Counter({"-2958": 1, "-724": 1})
    en = (REPO_ROOT / "docs/executive-summary.en.md").read_text(encoding="utf-8")
    missing, extra = compare(en, AR.read_text(encoding="utf-8"))
    assert not missing and not extra


def test_every_numeric_run_of_the_ar_summary_is_isolated() -> None:
    lines = AR.read_text(encoding="utf-8").splitlines()
    bad = [
        f"line {i + 1}: {ln[:80]}"
        for i, ln in enumerate(lines)
        if i > 0 and ln.strip() != LABEL_LINE and isolate_numeric_runs(ln) != ln
    ]
    assert not bad, bad
    assert sum(ln.count("−") for ln in lines[1:] if ln.strip() != LABEL_LINE) > 0


def test_html_is_rtl_with_the_bundled_font() -> None:
    html = md_to_html(AR.read_text(encoding="utf-8"), "../fonts")
    assert '<html lang="ar" dir="rtl">' in html
    assert "url('../fonts/NotoNaskhArabic-Regular.ttf')" in html
    assert '<p dir="ltr">Labels:' in html  # the English label line renders LTR
    committed = REPO_ROOT / "docs/report/figures/executive-summary.ar.html"
    assert committed.stat().st_size < 300_000
    assert "/Users/" not in committed.read_text(encoding="utf-8")


def _probe(*args: object) -> list[dict]:
    """bidi_probe, but a Chrome process failure (not an assertion) skips: PUBLISH_PREP saw
    headless Chrome pass the about:blank check and then fail under an empty HOME."""
    try:
        return bidi_probe(*args)
    except (OSError, subprocess.SubprocessError) as e:
        pytest.skip(f"headless Chrome failed to run: {type(e).__name__}")


@pytest.mark.skipif(not chrome_usable(), reason="headless Chrome not installed or not usable")
def test_bidi_probe_measures_order(tmp_path: Path) -> None:
    html = md_to_html("قيمة −2,958 / −724 و 3–10 كم\n\nقيمة ⁦−2,958 / −724⁩ كم\n", ".")
    page = tmp_path / "p.html"
    page.write_text(html, encoding="utf-8")
    runs = _probe(page)
    assert [r["ok"] for r in runs] == [False, False, True]


@pytest.mark.skipif(not chrome_usable(), reason="headless Chrome not installed or not usable")
@pytest.mark.parametrize("width", VIEWPORTS)
def test_probe_zero_on_default_and_narrow_viewports(width: int) -> None:
    committed = REPO_ROOT / "docs/report/figures/executive-summary.ar.html"
    runs = _probe(committed, width)
    assert sum(r["kind"] == "run" for r in runs) >= 29
    assert sum(r["kind"] == "marker" for r in runs) == 5
    assert [r for r in runs if not r["ok"] or r["wraps"]] == []


@pytest.mark.skipif(not chrome_usable(), reason="headless Chrome not installed or not usable")
def test_probe_flags_wrapped_runs_and_misplaced_markers(tmp_path: Path) -> None:
    # An isolated run with plain spaces and no nowrap wraps at 360 px: it fails even though
    # its fragments keep their order. The same run from isolate_numeric_runs stays on one line.
    long = "قيمة " * 8
    run = "−2,958 / −724 / +1,631 / −2,958 / −724 / +1,631"
    md = (
        f"{long}{LRI}{run}{PDI} مليون\n\n"
        + isolate_numeric_runs(f"{long}{run} مليون")
        + "\n\nالخط S6-L1[^S-x] هو\n\n"
        + isolate_numeric_runs("الخط S6-L1[^S-x] هو")
        + "\n"
    )
    html = md_to_html(md, ".").replace(
        f'<span class="nr">{LRI}{run}{PDI}</span>', f"{LRI}{run}{PDI}"
    )
    page = tmp_path / "p.html"
    page.write_text(html, encoding="utf-8")
    runs = _probe(page, 360)
    nums = [r for r in runs if r["kind"] == "run"]
    marks = [r for r in runs if r["kind"] == "marker"]
    assert nums[0]["wraps"] and nums[0]["order_ok"] and not nums[0]["ok"]
    assert nums[1]["ok"] and not nums[1]["wraps"]
    assert [m["ok"] for m in marks] == [False, True]
