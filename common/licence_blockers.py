"""The licence release blockers, grouped by type, each with the one question that clears it
(FIX_R8 item 8; Tariq's R8-checkpoint review, 5 Nov 2026).

Reads the register exactly as the release note does (`common.sources.licence_rows` and
`release_status`: the rows graded BLOCKER in `docs/licences-release.md` section 5) and the B1-B9
questions from section 1 of that note. It clears nothing and changes no status: it only lists.
The Transit Costs Project row is a HARD STOP (Tariq): its dependency scan greps `docs/`,
`cities/ksa/benchmarks/` and the run metas under `runs/`.

CLI:
  uv run python -m common.licence_blockers write [--out docs/licences-blockers.md]
"""

from __future__ import annotations

import re
from pathlib import Path

import typer

from common import REPO_ROOT
from common.cli import make_app
from common.sources import licence_rows, redact_model_ids, release_status

OUT = REPO_ROOT / "docs" / "licences-blockers.md"
RELEASE_NOTE = REPO_ROOT / "docs" / "licences-release.md"
VERSION = "1.3"
DATE = "7 Nov 2026"

HARD_STOP = r"Transit Costs Project"
# Run logs, not deliverables: excluded from the dependency scan (they only narrate the work).
LOGS = {"docs/STATUS.md", "docs/cost-log.md"}
HARD_STOP_GREP = re.compile(r"transit ?costs|S-cost-civil-018|marron institute", re.IGNORECASE)

GROUPS = [
    ("press", "Press and secondary fact pages"),
    ("stats", "Statistical extracts and data tables with unclear terms"),
    ("database", "Databases with non-commercial or all-rights-reserved terms"),
    ("bysa", "CC BY-SA share-alike sources"),
    ("odbl", "ODbL derivative question"),
    ("models", "Models and voices"),
    ("fonts", "Fonts and media"),
    ("other", "Other (software, methods, reports and literature)"),
]

# (item regex, group, question or None = the B-question / the group default). First match wins.
CLASSIFY: list[tuple[str, str, str | None]] = [
    (r"^Claude Code", "models", None),
    (
        r"Coqui XTTS",
        "models",
        "Keep XTTS-v2 out of every release (CPML is non-commercial), or "
        "does Tariq accept a non-commercial-only film if it is ever used?",
    ),
    (r"^Nabrah AI", "models", None),
    (
        r"Transit Costs Project",
        "database",
        "Does the Marron Institute (NYU) grant written "
        "permission to use and republish figures from the database, or does it stay excluded?",
    ),
    (
        r"EPSG Geodetic",
        "database",
        "Do the IOGP EPSG terms allow redistributing software that "
        "reads CRS definitions from proj.db (no dataset copy shipped)?",
    ),
    (r"OpenStreetMap layers for the alignment|Alignment sidecars weights v2", "odbl", None),
    (r"^UNESCO|Search-extract web sources|Sources for the economic roles of the 24", "bysa", None),
    (r"^Wikipedia airport pages", "bysa", None),
    (
        r"^Wikivoyage",
        "bysa",
        "Is one cited port fact from Wikivoyage (CC BY-SA) and CruiseMapper "
        "a fact citation only, with no share-alike, once CruiseMapper's terms are read?",
    ),
    (r"^MoF FY2026|IMF World Economic|^IMF/World Bank PFRAM", "stats", None),
    (
        r"Saudi Open Data portal",
        "stats",
        "Does each data.gov.sa dataset the study uses carry an "
        "open licence that allows public and commercial reuse?",
    ),
    (
        r"^GLMM",
        "stats",
        "May the GLMM census figures be cited as facts, or must every stored "
        "value be replaced by the GASTAT original?",
    ),
    (
        r"^GASTAT Labour Market Statistics Q4 2025",
        "stats",
        "Does the GASTAT open-data policy "
        "(S-069) allow republishing the transcribed LFS extracts as derived tables?",
    ),
    (
        r"^GASTAT Labour Market Statistics bulletins",
        "stats",
        "Does the GASTAT open-data policy "
        "(S-069) cover citing the bulletin figures in a public, possibly commercial release?",
    ),
    (
        r"^World Bank CCKP",
        "stats",
        "Are the CRU TS 4.08 climatology values served by CCKP under "
        "CC BY 4.0 (or another open licence) for public and commercial reuse?",
    ),
    (
        r"^DfT TAG optimism bias workbook",
        "stats",
        "Do the Oxford Global Projects reference-class "
        "data inside the OGL workbook carry a third-party restriction on the transcribed "
        "percentiles?",
    ),
    (
        r"^xlogit",
        "other",
        "Which licence governs xlogit (MIT on PyPI or GPL-3.0 on GitHub), "
        "decided before it is installed?",
    ),
    (
        r"^Schittenhelm",
        "other",
        "Is the article's open-access licence one that allows citing the "
        "table values in a public, possibly commercial release?",
    ),
    (r"^Handbook on the external costs", "other", None),
]

GROUP_QUESTION = {
    "press": "Is citing a published fact with its source and access date enough (no text, table "
    "or image reproduced), so that no permission is needed?",
    "stats": "May the cited figures be republished in a public, possibly commercial release, "
    "and under which attribution?",
    "other": "Do the terms allow this use in a public, possibly commercial release?",
}


def classify(item: str) -> tuple[str, str | None]:
    for pat, group, q in CLASSIFY:
        if re.search(pat, item):
            return group, q
    return "press", None


def b_questions(note: Path = RELEASE_NOTE) -> dict[str, str]:
    """{'B1': question, ...} from section 1 of the release note."""
    text = note.read_text(encoding="utf-8") if note.exists() else ""
    out = {}
    for m in re.finditer(r"^- \*\*(B\d) [^*]+\*\*.*?\*Question:\* (.+)$", text, re.MULTILINE):
        out[m.group(1)] = m.group(2).strip()
    return out


def blocker_rows(root: Path = REPO_ROOT) -> list[dict[str, str]]:
    """Every BLOCKER row with its section-5 number, group and clearing question."""
    bq = b_questions(root / "docs" / "licences-release.md")
    rows = []
    for i, (src, r) in enumerate(licence_rows(root), start=1):
        cat, why = release_status(r)
        if cat != "BLOCKER":
            continue
        item = r.get("item", "")
        group, q = classify(item)
        b = re.match(r"(B\d)\b", why)
        if q is None and b:
            q = bq.get(b.group(1))
        if q is None and group == "odbl":
            q = bq.get("B7")  # alignments-v2 carries the same Produced Work question as B7
        if q is None:
            q = GROUP_QUESTION.get(group, GROUP_QUESTION["other"])
        rows.append(
            {
                "n": str(i),
                "register": src,
                "item": item,
                "b": b.group(1) if b else "",
                "reason": why,
                "terms": "; ".join(
                    f"{k}: {(r.get(k) or '').strip()}"
                    for k in ("licence", "open", "commercial_use", "obligations", "status")
                    if (r.get(k) or "").strip()
                ),
                "used_in": (r.get("used_in") or "").strip(),
                "group": group,
                "question": q,
                "hard_stop": "Y" if re.search(HARD_STOP, item) else "",
            }
        )
    return rows


def hard_stop_hits(root: Path = REPO_ROOT) -> tuple[list[str], int]:
    """(file:line hits of the Transit Costs Project under docs/, cities/ksa/benchmarks/ and the
    run metas, number of run metas scanned)."""
    hits = []
    targets = sorted((root / "docs").rglob("*")) + sorted(
        (root / "cities/ksa/benchmarks").rglob("*")
    )
    for p in targets:
        if not p.is_file() or p.suffix not in {".md", ".csv", ".yaml", ".yml", ".json"}:
            continue
        rel = p.relative_to(root).as_posix()
        if p.name == "licences-blockers.md" or rel.startswith("docs/status/") or rel in LOGS:
            continue
        for k, line in enumerate(p.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
            if HARD_STOP_GREP.search(line):
                hits.append(f"{p.relative_to(root).as_posix()}:{k}")
    metas = sorted((root / "runs").rglob("meta.json")) if (root / "runs").exists() else []
    for p in metas:
        if HARD_STOP_GREP.search(p.read_text(encoding="utf-8", errors="ignore")):
            hits.append(p.relative_to(root).as_posix())
    return hits, len(metas)


def _cell(s: str) -> str:
    return redact_model_ids(" ".join(s.split())).replace("|", "\\|")


def render(root: Path = REPO_ROOT) -> str:
    rows = blocker_rows(root)
    hits, n_meta = hard_stop_hits(root)
    hs = [r for r in rows if r["hard_stop"]]
    counts = {g: sum(r["group"] == g for r in rows) for g, _ in GROUPS}
    out = [
        f"> **Document version:** docs/licences-blockers.md v{VERSION} | {DATE} | Author: FIX_R8 "
        "builder (generated by `uv run python -m common.licence_blockers write`); R9 (v1.1: B9 "
        "Nabrah row narrowed to attribution) | Status: draft",
        "",
        "# Licence release blockers (list only; nothing cleared)",
        "",
        "Every row of the licence and openness register that `docs/licences-release.md` section 5 "
        "grades **BLOCKER** (same rule, `common.sources.release_status`, applied to "
        "`docs/licences.csv` and any `docs/licences-*.csv` fragment), grouped by type, with the "
        "terms text the register captured, where the item is used and the one question that "
        "clears it. B1–B9 questions are quoted from section 1 of the release note. No status in "
        "`docs/licences.csv` is changed here; Tariq decides each row (rule 12).",
        "",
        f"**Count: {len(rows)} BLOCKER rows** (register of {len(licence_rows(root))} rows). "
        "Tariq's review cited 48; no committed version of the release note shows 48: the R8 "
        "track's note had 47 and the INTEGRATE_R8 note has 46, the difference being Google "
        "Chrome, closed by Tariq's approval on 4 Nov 2026.",
        "",
        "| group | rows |",
        "|---|---|",
        *[f"| {title} | {counts[g]} |" for g, title in GROUPS],
        f"| **total** | **{len(rows)}** |",
        "",
        "## HARD STOP: Transit Costs Project (NYU Marron Institute)",
        "",
    ]
    for r in hs:
        out += [
            f"Register row #{r['n']} ({r['register']}): {r['item']}. Terms captured: "
            f"{r['terms']}. Used in: {r['used_in'] or 'not stated'}.",
            "",
        ]
    out += [
        "**No release may include any figure, table or benchmark derived from the Transit Costs "
        "Project until its terms are resolved** (Tariq, 5 Nov 2026). The register records the "
        'database as "All rights reserved (no licence stated)"; the release table\'s reason '
        'line reads "non-commercial terms" because `commercial use` is N, but the captured '
        "terms are all-rights-reserved, a stricter case.",
        "",
        f"Dependency scan (`docs/` without the status logs `docs/STATUS.md` and `docs/status/`, "
        f"`cities/ksa/benchmarks/` and {n_meta:,} run metas "
        "`runs/**/meta.json`; pattern `transit ?costs|S-cost-civil-018|marron institute`): "
        f"{len(hits)} hits, listed below. **No figure, table, benchmark row or run draws a value "
        "from it**: the run metas and `cities/ksa/benchmarks/` have no hit, and the cost row "
        "that names it (C-line-type-commuter-atgrade-034) has low / central / high = null and "
        "status `unknown` (it records that the database was searched and not used).",
        "",
        "| file:line | what it is |",
        "|---|---|",
    ]
    for h in hits:
        out.append(f"| `{h}` | {_hit_kind(h)} |")
    if not hits:
        out.append("| (none) | |")
    out += [""]
    for g, title in GROUPS:
        grp = [r for r in rows if r["group"] == g]
        out += [f"## {title} ({len(grp)})", ""]
        if not grp:
            out += ["None in the register.", ""]
            continue
        out += [
            "| # | item | flag | terms captured (register text) | used in "
            "| question that clears it |",
            "|---|---|---|---|---|---|",
        ]
        for r in grp:
            flag = r["b"] or r["reason"]
            if r["hard_stop"]:
                flag = "**HARD STOP**; " + flag
            out.append(
                f"| {r['n']} | {_cell(r['item'])} | {_cell(flag)} | {_cell(r['terms'])} | "
                f"{_cell(r['used_in'])} | {_cell(r['question'])} |"
            )
        out.append("")
    out += [
        "`#` is the row number in `docs/licences-release.md` section 5 (register order: "
        "`docs/licences.csv`, then any fragment). Regenerate after any register change: "
        "`uv run python -m common.licence_blockers write`.",
        "",
    ]
    return "\n".join(out)


def _hit_kind(h: str) -> str:
    if "sources/index" in h or "annex-sources" in h or "cost-civil.csv" in h:
        return "source-index citation S-cost-civil-018 (the licence page itself; no data)"
    if "licences" in h:
        return "licence register / release note row"
    if "assumptions" in h:
        return (
            "A-cost-013 reason text: searched, not used "
            "(proxy taken from C-line-type-conv-ec-base-006)"
        )
    if "costs.md" in h or "cost-notes" in h:
        return "cost note: searched, not used (row -034 unknown)"
    if "STATUS" in h or "status/" in h:
        return "status log"
    return "mention"


app: typer.Typer = make_app("common.licence_blockers", "Licence release blockers list.")


@app.command("write")
def write_cmd(out: Path = typer.Option(OUT, "--out")) -> None:
    """Write the grouped blockers list."""
    out.write_text(render(), encoding="utf-8")
    typer.echo(f"wrote {out} ({len(blocker_rows())} BLOCKER rows)")


if __name__ == "__main__":
    app()
