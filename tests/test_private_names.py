"""FIX_EXPORT_NAMES (12 Nov 2026): the private-name list lives only in the gitignored
`.publish/private-names.txt`; no tracked file may contain any of its terms (the milestone prompt
that quotes the list is the one exception, and it is dropped from the public export)."""

from __future__ import annotations

import re
import subprocess

import pytest

from common import REPO_ROOT

LIST = REPO_ROOT / ".publish" / "private-names.txt"
EXEMPT = {"prompts/FIX_EXPORT_NAMES.md"}


def _tracked() -> list[str]:
    out = subprocess.run(
        ["git", "ls-files", "-z"], cwd=REPO_ROOT, capture_output=True, text=True, check=True
    )
    return [f for f in out.stdout.split("\0") if f]


def _pattern() -> re.Pattern[bytes]:
    terms = []
    for line in LIST.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        term = line.split("\t", 1)[0]
        terms.append(r"[ _-]?".join(re.escape(w) for w in term.split(" ")))
    assert terms, "private-name list is empty"
    return re.compile("|".join(terms).encode(), re.IGNORECASE)


@pytest.mark.skipif(not LIST.exists(), reason="private-name list absent (public clone)")
def test_no_tracked_file_names_a_private_term() -> None:
    pat = _pattern()
    hits = []
    for f in _tracked():
        p = REPO_ROOT / f
        if f in EXEMPT or not p.is_file():
            continue
        if pat.search(p.read_bytes()):
            hits.append(f)
    assert hits == []


def test_private_list_is_gitignored_and_prompt_excluded() -> None:
    ignored = subprocess.run(
        ["git", "check-ignore", "-q", ".publish/private-names.txt"], cwd=REPO_ROOT
    )
    assert ignored.returncode == 0
    assert ".publish/private-names.txt" not in _tracked()
    exclude = REPO_ROOT / "docs" / "publish" / "export-exclude.txt"
    lines = exclude.read_text(encoding="utf-8").splitlines()
    assert all(e in lines for e in EXEMPT)
