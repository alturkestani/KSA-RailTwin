"""PUBLISH_PDF_POST (Tariq, 13 Nov 2026): the PDF of the feasibility report (common/report_pdf.py).

Always: GitHub-style heading anchors, repository-link rewriting, source-note links, the label-line
table fix, and every `#…` link of the real report resolving to a heading. With poppler and the
committed PDF: A4, no private name in its text.
"""

from __future__ import annotations

import shutil

import pytest

from common import report_pdf as rp


def test_slug_matches_github() -> None:
    assert rp.slug("0.1 Scope") == "01-scope"
    assert rp.slug("3.6 Cost–benefit analysis (W4)") == "36-costbenefit-analysis-w4"
    assert rp.slug("5.5 The 200–800 km band") == "55-the-200800-km-band"


def test_repo_link() -> None:
    assert rp.repo_link("#01-scope") == "#01-scope"
    assert rp.repo_link("https://example.org/x") == "https://example.org/x"
    assert rp.repo_link("annex-regions/riyadh.md") == (
        f"{rp.REPO_URL}/blob/main/docs/report/annex-regions/riyadh.md"
    )
    assert rp.repo_link("../coverage.md#a") == f"{rp.REPO_URL}/blob/main/docs/coverage.md#a"


def test_footnotes_tables_and_figures(tmp_path) -> None:
    md = (
        "## A b\n\nText[^S-001] and `[^S-…]`.\n\n> Labels: x\n| a | b |\n|---|---|\n| 1 | 2 |\n\n"
        "![Figure 1. T](f.svg)\n\n## Source notes\n\n"
        "[^S-001]: Pub, https://example.org/p.pdf, accessed 2026-10-30.\n"
    )
    body = rp.md_to_body(md, figure_dir=tmp_path)
    assert '<h2 id="a-b">' in body
    assert '<a href="#fn-S-001">[S-001]</a>' in body and 'id="fn-S-001"' in body
    assert '<a href="https://example.org/p.pdf">https://example.org/p.pdf</a>,' in body
    assert "<code>[^S-…]</code>" in body
    assert "<table>" in body and "<blockquote>" in body
    assert "<figure>" in body and (tmp_path / "f.svg").as_uri() in body


def test_every_internal_link_of_the_report_resolves() -> None:
    body = rp.md_to_body(rp.SRC.read_text(encoding="utf-8"))
    ids, refs = rp.anchors(body)
    assert refs and refs <= ids
    assert len(rp.toc_ids(body)) >= 50


@pytest.mark.skipif(
    not (rp.OUT.exists() and shutil.which("pdfinfo") and shutil.which("pdftotext")),
    reason="PDF or poppler absent",
)
def test_committed_pdf_is_a4_without_private_names() -> None:
    import subprocess

    info = subprocess.run(["pdfinfo", str(rp.OUT)], capture_output=True, text=True).stdout
    assert "(A4)" in info
    hits = rp.private_name_count("\f".join(rp.page_texts(rp.OUT)))
    assert hits in (0, -1)  # -1: the private list is absent (public clone)
