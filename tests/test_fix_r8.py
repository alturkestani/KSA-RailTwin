"""FIX_R8 (Tariq's R8-checkpoint review, 5 Nov 2026): fig09 title, licence blockers file,
wording checks on the summaries, brief and report."""

from __future__ import annotations

import csv
import re

from common import REPO_ROOT
from common.figures import SPECS

FIG09_EN = "Phasing (2030, 2050) and stage gates (2027, 2047)"
FIG09_AR = "المراحل (2030 و2050) وبوابات القرار (2027 و2047)"


def test_fig09_title_in_spec_and_deck_csv() -> None:
    spec = next(s for s in SPECS if s.stem == "fig09-stage-gates")
    assert (spec.title_en, spec.title_ar) == (FIG09_EN, FIG09_AR)
    with (REPO_ROOT / "docs/deck-figures/figures.csv").open(encoding="utf-8") as fh:
        row = next(r for r in csv.DictReader(fh) if r["file"] == "fig09-stage-gates.png")
    assert (row["title_en"], row["title_ar"]) == (FIG09_EN, FIG09_AR)
    with (REPO_ROOT / "docs/report/figures/figures-index.csv").open(encoding="utf-8") as fh:
        row = next(r for r in csv.DictReader(fh) if r["stem"] == "fig09-stage-gates")
    assert row["title_en"] == FIG09_EN
    report = (REPO_ROOT / "docs/report/feasibility-report.md").read_text(encoding="utf-8")
    assert f"![Figure 9. {FIG09_EN}](figures/fig09-stage-gates.svg)" in report


# ------------------------------------------------------------------ item 9: wording checks
WORDING_FILES = [
    "docs/executive-summary.en.md",
    "docs/executive-summary.ar.md",
    "docs/policy-brief.md",
    "docs/report/feasibility-report.md",
    *sorted(
        str(p.relative_to(REPO_ROOT)) for p in (REPO_ROOT / "docs/report/sections").glob("*.md")
    ),
]
IN_MODEL = re.compile(r"in the model|In the model|في النموذج")


def _blocks(rel: str) -> list[tuple[str, list[str]]]:
    """Paragraphs and tables of a file, each with the heading above it."""
    out, heading, cur = [], "", []
    for line in (REPO_ROOT / rel).read_text(encoding="utf-8").splitlines():
        if line.startswith("#"):
            heading = line
        if not line.strip():
            if cur:
                out.append((heading, cur))
            cur = []
        else:
            cur.append(line)
    if cur:
        out.append((heading, cur))
    return out


def _sentences(rel: str) -> list[str]:
    text = (REPO_ROOT / rel).read_text(encoding="utf-8")
    return [s for s in re.split(r"(?<=[.؛;])\s+|\n", text) if s.strip()]


def test_s1_negative_npv_is_in_the_model() -> None:
    """9a: every S1 NPV (−337,555 / −60,103) sits in a paragraph, table header or heading that
    says 'in the model'."""
    bad = []
    for rel in WORDING_FILES:
        for heading, block in _blocks(rel):
            text = "\n".join(block)
            if "−60,103" not in text and "−337,555" not in text:
                continue
            if not (IN_MODEL.search(text) or IN_MODEL.search(heading)):
                bad.append(f"{rel}: {block[0][:80]}")
    assert not bad, bad


def test_al_kharj_4231_is_a_layout_difference() -> None:
    """9b: 4,231 is always the difference between S6-L1 and the layout without the spur."""
    additive = re.compile(
        r"of which|from the spur|contributes|is the spur|of the 11|of its 11|منه إلى الفرع|يعود"
    )
    bad = []
    for rel in [*WORDING_FILES, "docs/r6-topology.md"]:
        for s in _sentences(rel):
            hit = re.search(r"(?<![\d,.])(4,?231(?![\d,])|4\.2\d? ?(bn|billion))", s)
            if hit and (additive.search(s) or not re.search(r"difference|الفرق", s)):
                bad.append(f"{rel}: {s[:120]}")
    assert not bad, bad


def test_120_minute_reach_is_door_to_door_from_the_five_metros() -> None:
    """9c: every 120-minute reach figure says door-to-door from the five metros; the national
    reach (A-r6-104) always says 'reported only'."""
    reach = re.compile(r"within 120|120-minute reach|120 دقيقة|reach gain")
    qual = re.compile(r"five metros|five-metro|المدن الخمس الكبرى")
    bad = []
    for rel in WORDING_FILES:
        for s in _sentences(rel):
            if "national reach" in s.lower():
                if "reported" not in s or "only" not in s:
                    bad.append(f"{rel}: {s[:120]}")
                continue
            if reach.search(s) and not qual.search(s) and "isochrone" not in s.lower():
                bad.append(f"{rel}: {s[:120]}")
    assert not bad, bad


# ------------------------------------------------------------------ item 8: licence blockers
def test_licence_blockers_file_parses_and_matches_the_register() -> None:
    from common.licence_blockers import GROUPS, blocker_rows

    text = (REPO_ROOT / "docs/licences-blockers.md").read_text(encoding="utf-8")
    assert text.startswith("> **Document version:** docs/licences-blockers.md v")
    rows = blocker_rows()
    assert f"**Count: {len(rows)} BLOCKER rows**" in text
    # HARD STOP first, then the eight groups in order.
    heads = re.findall(r"^## (.+)$", text, re.MULTILINE)
    assert heads[0].startswith("HARD STOP: Transit Costs Project")
    assert [h.rsplit(" (", 1)[0] for h in heads[1:]] == [t for _, t in GROUPS]
    table_ids = re.findall(r"^\| (\d+) \| ", text, re.MULTILINE)
    assert sorted(table_ids, key=int) == sorted((r["n"] for r in rows), key=int)
    assert sum(1 for r in rows if r["hard_stop"]) == 1
    assert all(r["question"].strip() for r in rows)
    assert not re.search(r"claude-|opus-|haiku-|fable-", text)


def test_no_licence_status_changed_since_r8() -> None:
    import subprocess

    tag = subprocess.run(
        ["git", "rev-parse", "-q", "--verify", "refs/tags/r8"], cwd=REPO_ROOT, capture_output=True
    )
    if tag.returncode != 0:
        return  # no tag in this checkout (CI): nothing to compare against
    old = subprocess.run(
        ["git", "show", "refs/tags/r8:docs/licences.csv"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    keys = ("licence", "open", "commercial_use", "status", "approval")

    def state(text: str) -> dict[str, tuple[str, ...]]:
        return {r["item"]: tuple(r[k] for k in keys) for r in csv.DictReader(text.splitlines())}

    now = (REPO_ROOT / "docs/licences.csv").read_text(encoding="utf-8")
    # R9 (Tariq, 7 Nov 2026, prompts/R9_LAUNCH.md item 2): the Nabrah AI row may change
    # (written confirmation S-nabrah-005). FIX_LICENCE_CITE_FACTS (Tariq, 7 Nov 2026 AST): the
    # rows below (docs/licences.csv row numbers, as the release note prints them) may change;
    # row 1 was renamed, so its r8 name is matched by prefix. Every other row keeps its r8 state.
    cite_facts_rows = (
        1, 7, 117, 118, 119, 120, 121, 122, 123, 125, 127, 132, 133, 136, 141, 146, 147, 148,
        149, 153, 168, 183, 188, 191, 193, 194, 195, 196, 197, 201, 203, 204, 205, 221, 234,
        235, 236, 237, 238, 246, 260, 262, 263, 290,
    )  # fmt: skip
    items = [r["item"] for r in csv.DictReader(now.splitlines())]
    approved = {items[n - 1] for n in cite_facts_rows}
    assert len(approved) == len(cite_facts_rows)
    assert any(k.startswith("Nabrah AI") for k in approved)
    old_approved = (approved & set(state(old))) | {
        k for k in state(old) if k.startswith("Claude Code /")
    }
    assert len(old_approved) == len(approved)
    # PUBLISH_EXPORT (Tariq, 12 Nov 2026, Q8): one new row for the shipped figure inputs.
    new_rows = {"KSA Rail Twin figure inputs (run-output subset; docs/publish/figure-inputs/)"}
    a = {k: v for k, v in state(now).items() if k not in approved and k not in new_rows}
    b = {k: v for k, v in state(old).items() if k not in old_approved}
    assert a == b, "a licence status changed since tag r8"
