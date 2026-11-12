"""R8 report build: reproducible, source-driven appendix, 13 region annexes (seconds)."""

from __future__ import annotations

import csv
import shutil
from pathlib import Path

import pytest

from common import REPO_ROOT
from common.report import (
    REGIONS,
    SECTIONS_DIR,
    Ctx,
    do_build,
    fm,
    label_violations,
    neutralise,
    number_violations,
    refresh_blocks,
)

NEEDS_RUNS = pytest.mark.skipif(
    not (REPO_ROOT / "runs/r6/v3/library/library.json").exists() or not SECTIONS_DIR.exists(),
    reason="run outputs (runs/r6, runs/r7, runs/cba) or report sections not in this checkout",
)


def _snapshot(d: Path) -> dict[str, bytes]:
    return {str(p.relative_to(d)): p.read_bytes() for p in sorted(d.rglob("*.md"))}


@NEEDS_RUNS
def test_build_is_reproducible(tmp_path: Path) -> None:
    a, b = tmp_path / "a", tmp_path / "b"
    do_build(out_dir=a, refresh=False)
    first = _snapshot(a)
    do_build(out_dir=a, refresh=False)
    do_build(out_dir=b, refresh=False)
    assert _snapshot(a) == first
    assert _snapshot(b) == first
    assert "feasibility-report.md" in first


@NEEDS_RUNS
def test_committed_report_matches_a_fresh_build(tmp_path: Path) -> None:
    """The committed report and annexes are what `build` produces from the committed sections."""
    do_build(out_dir=tmp_path, refresh=False)
    for rel, data in _snapshot(tmp_path).items():
        committed = REPO_ROOT / "docs/report" / rel
        assert committed.exists(), rel
        assert committed.read_bytes() == data, (
            f"{rel} is stale: run `uv run python -m common.report build`"
        )


@NEEDS_RUNS
def test_changed_source_row_changes_the_appendix(tmp_path: Path) -> None:
    src = REPO_ROOT / "docs/sources/index.csv"
    with src.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fields = list(reader.fieldnames or [])
        rows = list(reader)
    rows[0]["claim"] = "TEST-ONLY changed claim for the appendix test"
    alt = tmp_path / "index.csv"
    with alt.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    base, changed = tmp_path / "base", tmp_path / "changed"
    do_build(out_dir=base, refresh=False)
    do_build(out_dir=changed, sources=alt, refresh=False)
    a = (base / "annex-sources.md").read_text(encoding="utf-8")
    b = (changed / "annex-sources.md").read_text(encoding="utf-8")
    assert a != b
    assert "TEST-ONLY changed claim" in b and "TEST-ONLY changed claim" not in a
    # every row of the index is in the appendix
    assert sum(1 for line in a.splitlines() if line.startswith("| S-")) == len(rows)


@NEEDS_RUNS
def test_region_annex_has_13_files(tmp_path: Path) -> None:
    do_build(out_dir=tmp_path, refresh=False)
    files = sorted((tmp_path / "annex-regions").glob("*.md"))
    assert len(files) == 13
    assert {f.stem for f in files} == {s for s, _, _ in REGIONS}
    for f in files:
        text = f.read_text(encoding="utf-8")
        assert text.startswith("> **Document version:**")
        assert "## 1. Governorates (coverage audit)" in text
        assert label_violations(text) == []


@NEEDS_RUNS
def test_assumption_appendix_has_every_row(tmp_path: Path) -> None:
    do_build(out_dir=tmp_path, refresh=False)
    reg = (REPO_ROOT / "docs/assumptions.md").read_text(encoding="utf-8")
    n = sum(1 for line in reg.splitlines() if line.startswith("| A-"))
    annex = (tmp_path / "annex-assumptions.md").read_text(encoding="utf-8")
    assert sum(1 for line in annex.splitlines() if line.startswith("| A-")) >= n


@NEEDS_RUNS
def test_generated_blocks_are_current() -> None:
    ctx = Ctx()
    for f in sorted(SECTIONS_DIR.glob("*.md")):
        text = f.read_text(encoding="utf-8")
        assert refresh_blocks(text, ctx) == text, f"{f.name}: generated blocks stale"


@NEEDS_RUNS
def test_l1_headline_matches_top5_columns() -> None:
    with (REPO_ROOT / "runs/r6/top5/top5.csv").open(encoding="utf-8", newline="") as f:
        row = {r["layout"]: r for r in csv.DictReader(f)}["S6-L1"]
    vals = [round(float(row[f"npv_p90cost_{p}"])) for p in ("low", "medium", "high")]
    assert vals == [-2958, -724, 1631]


def test_helpers(tmp_path: Path) -> None:
    assert fm(-2957.6) == "−2,958"
    assert fm(1630.8, sign=True) == "+1,631"
    assert fm(float("nan")) == "n/a"
    assert "&#" in neutralise("https://opus4.example/x") and "opus" not in neutralise("opus")
    assert number_violations("A figure of 1,234 SAR m.\n") != []
    assert number_violations("A figure of 1,234 SAR m (runs/x).\n") == []
    assert number_violations("Built in 2030.\n") == []
    shutil.rmtree(tmp_path, ignore_errors=True)
