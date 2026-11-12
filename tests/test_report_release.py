"""docs/licences-release.md: every register item appears with a release status, the named carried
flags are listed as release blockers, and the generated table is current."""

from __future__ import annotations

import csv
import re
from pathlib import Path

import pytest

from common import REPO_ROOT
from common.sources import (
    BEGIN,
    END,
    NAMED_BLOCKERS,
    licence_rows,
    named_flag_answered,
    redact_model_ids,
    release_status,
    release_table,
)

NOTE = REPO_ROOT / "docs" / "licences-release.md"

# The flags carried from R1d-R7 (prompts/R8.md, R7-checkpoint answer 4), as the note must name them.
CARRIED = [
    "MoF FY2026",
    "PFRAM",
    "UNESCO CC BY-SA",
    "IMF WEO",
    "CE Delft",
    "Wikipedia air-route set",
    "cities/ksa/alignments/",
    "alignments-v2/",
    "model ids in the R0 licence row",
    "Nabrah AI",
]


def _norm(s: str) -> str:
    return redact_model_ids(" ".join(s.replace("\\|", "|").split()))


@pytest.fixture(scope="module")
def note() -> str:
    return _norm(NOTE.read_text(encoding="utf-8"))


def test_every_register_item_listed(note: str) -> None:
    with (REPO_ROOT / "docs" / "licences.csv").open(encoding="utf-8", newline="") as fh:
        items = [r["item"] for r in csv.DictReader(fh)]
    assert len(items) > 200
    missing = [i for i in items if _norm(i) not in note]
    assert not missing, missing


def test_fragment_items_listed(note: str) -> None:
    for src, r in licence_rows():
        assert _norm(r["item"]) in note, (src, r["item"])


@pytest.mark.parametrize("flag", CARRIED)
def test_carried_flag_is_a_blocker(note: str, flag: str) -> None:
    assert flag in note
    section = note.split("## 1. Release blockers to clear", 1)[1].split("## 2.", 1)[0]
    assert flag in section, f"{flag} is not in the blockers section"


def test_named_blocker_rows_are_blockers() -> None:
    """A named flag forces BLOCKER unless the row's approval records Tariq's 7 Nov 2026 AST
    FIX_LICENCE_CITE_FACTS decision (prompts/FIX_LICENCE_NAMED_FLAGS.md); then the row is graded
    by its columns, exactly as a row with no named flag."""
    rows = [r for _, r in licence_rows()]
    # B8 was answered by renaming the R0 row (Tariq, 7 Nov 2026 AST; FIX_LICENCE_CITE_FACTS):
    # no row carries model ids any more, so its pattern must match nothing.
    answered_by_rename = {"B8"}
    for key, pat, _ in NAMED_BLOCKERS:
        hit = [r for r in rows if re.search(pat, r["item"])]
        if key.split()[0] in answered_by_rename:
            assert not hit, f"{key}: a register row names model ids again"
            continue
        assert hit, f"{key}: no register row matches {pat!r}"
        for r in hit:
            if named_flag_answered(r):
                assert release_status(r) == release_status({**r, "item": "x"}), (key, r["item"])
            else:
                assert release_status(r)[0] == "BLOCKER", (key, r["item"])


def test_named_flag_yields_only_to_both_strings() -> None:
    base = {
        "item": "Nabrah AI",
        "licence": "MIT",
        "open": "Y",
        "commercial_use": "Y",
        "attribution": "none",
        "obligations": "none",
        "status": "verified",
    }
    both = "Tariq, 7 Nov 2026 AST (approved; FIX_LICENCE_CITE_FACTS)"
    assert release_status({**base, "approval": both})[0] == "COMPATIBLE"
    assert release_status({**base, "approval": ""})[0] == "BLOCKER"
    assert release_status({**base, "approval": "Tariq, 7 Nov 2026 AST"})[0] == "BLOCKER"
    assert release_status({**base, "approval": "FIX_LICENCE_CITE_FACTS"})[0] == "BLOCKER"
    # The answered flag grades by its columns: unclear terms still block.
    assert release_status({**base, "approval": both, "licence": "unclear"})[0] == "BLOCKER"


def test_named_flag_rows_with_and_without_the_approval() -> None:
    rows = {r["item"]: r for _, r in licence_rows()}
    nabrah = next(r for i, r in rows.items() if i.startswith("Nabrah AI"))
    assert named_flag_answered(nabrah)
    assert release_status(nabrah) == release_status({**nabrah, "item": "x"})
    assert release_status(nabrah)[0] != "BLOCKER"
    stripped = {**nabrah, "approval": ""}
    cat, why = release_status(stripped)
    assert cat == "BLOCKER" and why.startswith("B9 Nabrah AI"), why
    assert "unanswered" not in why


def test_transit_costs_and_xtts_stay_blockers() -> None:
    items = [r for _, r in licence_rows()]
    for prefix in ("Transit Costs Project database", "Coqui XTTS-v2"):
        hit = [r for r in items if r["item"].startswith(prefix)]
        assert hit, prefix
        assert all(release_status(r)[0] == "BLOCKER" for r in hit), prefix


def test_measured_blocker_total() -> None:
    # Measured in FIX_LICENCE_CITE_TERMS (7 Nov 2026): 94 XTTS-v2 and 189 Transit Costs
    # (commercial use N). 191 MoF FY2026 and 193 PFRAM record citation-only use in their
    # licence cells and are graded by their columns.
    blockers = [r["item"] for _, r in licence_rows() if release_status(r)[0] == "BLOCKER"]
    assert len(blockers) == 2, blockers
    assert all(i.startswith(("Coqui XTTS-v2", "Transit Costs Project")) for i in blockers)


CITE_ONLY = {
    "MoF FY2026 pre-budget statement": (
        "no licence statement captured; facts and derived study table cited only; "
        "MoF table not republished"
    ),
    "IMF/World Bank PFRAM": (
        "IMF terms of use not captured; concepts cited only; Excel tool not used"
    ),
}


@pytest.mark.parametrize("prefix", sorted(CITE_ONLY))
def test_citation_only_licence_cells_are_not_blockers(prefix: str) -> None:
    hit = [r for _, r in licence_rows() if r["item"].startswith(prefix)]
    assert len(hit) == 1, prefix
    r = hit[0]
    assert r["licence"] == CITE_ONLY[prefix]
    assert "unclear" not in r["licence"].lower()
    assert named_flag_answered(r)
    assert release_status(r)[0] == "OBLIGATIONS", release_status(r)
    # Putting "unclear" back on the licence cell makes the row BLOCKER again.
    assert release_status({**r, "licence": f"unclear ({r['licence']})"})[0] == "BLOCKER"


def test_unclear_and_blocked_rows_are_blockers() -> None:
    for _, r in licence_rows():
        st = (r.get("status") or "").lower()
        in_release = release_status(r)[0] != "NOT IN RELEASE"
        unclear = "unclear" in (r.get("commercial_use") or "").lower() or "blocked" in st
        if unclear and in_release:
            assert release_status(r)[0] == "BLOCKER", r["item"]


def test_proprietary_without_approval_flagged() -> None:
    for _, r in licence_rows():
        if (r.get("open") or "").strip().upper() == "N" and not (r.get("approval") or "").strip():
            assert release_status(r)[0] in ("BLOCKER", "NOT IN RELEASE"), r["item"]


def test_generated_table_is_current() -> None:
    text = NOTE.read_text(encoding="utf-8")
    body = text.split(BEGIN, 1)[1].split(END, 1)[0].strip()
    assert body == release_table().strip(), (
        "regenerate: uv run python -m common.sources licences-release --write "
        "docs/licences-release.md"
    )


def test_release_status_rules() -> None:
    base = {
        "item": "x",
        "licence": "MIT",
        "open": "Y",
        "commercial_use": "Y",
        "attribution": "none",
    }
    assert release_status({**base, "obligations": "none", "status": "verified"})[0] == "COMPATIBLE"
    assert (
        release_status({**base, "commercial_use": "unclear", "status": "verified"})[0] == "BLOCKER"
    )
    assert release_status({**base, "commercial_use": "N", "status": "verified"})[0] == "BLOCKER"
    assert release_status({**base, "status": "planned; unverified"})[0] == "NOT IN RELEASE"
    assert release_status({**base, "status": "unverified: confirm"})[0] == "VERIFY"
    assert release_status({**base, "licence": "ODbL-1.0", "status": "verified"})[0] == "OBLIGATIONS"
    assert (
        release_status({**base, "open": "N", "status": "verified", "approval": ""})[0] == "BLOCKER"
    )
    assert release_status({**base, "item": "Nabrah AI", "status": "verified"})[0] == "BLOCKER"


def test_note_has_version_header() -> None:
    first = Path(NOTE).read_text(encoding="utf-8").splitlines()[0]
    assert first.startswith("> **Document version:** docs/licences-release.md v")


def test_superseded_rows_name_their_versioned_row() -> None:
    by_item = {r["item"]: r for _, r in licence_rows()}
    for generic in (
        "UN World Population Prospects",
        "GHSL (Global Human Settlement Layer)",
        "WorldPop",
    ):
        cat, why = release_status(by_item[generic])
        assert cat == "NOT IN RELEASE"
        assert "superseded by a more specific versioned row" in why, (generic, why)
