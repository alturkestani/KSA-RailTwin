"""Source helpers: the digit-by-digit bilingual check and an S-id resolution check.

CLI:
  uv run python -m common.sources bilingual-check EN.md AR.md
      Every numeric token of the two files must match as a MULTISET (each value the same number
      of times in both), digit by digit after normalisation. Exit 1 and print the missing / extra
      tokens per file otherwise.
  uv run python -m common.sources check FILE [FILE ...]
      Every `S-...` footnote or inline id cited in the files has a row in docs/sources/index.csv.
  uv run python -m common.sources licences-release [--write docs/licences-release.md]
      The per-item release-compatibility table (docs/licences.csv plus every track fragment
      docs/licences-*.csv), printed or written between the GENERATED markers of the release note.

Normalisation (applied to both files before tokenising):
- Arabic-Indic (U+0660-0669) and Eastern Arabic-Indic (U+06F0-06F9) digits -> ASCII 0-9.
- Arabic decimal separator U+066B -> '.'; Arabic thousands separator U+066C and ',' between a
  digit and exactly three digits -> removed (so 2,958 / 2٬958 -> 2958).
- Signs: U+2212 (minus), U+2012 / U+2013 / U+2014 (figure, en, em dash) and '-' mark a NEGATIVE
  number only when they come directly before a digit and are not preceded by a letter, a digit or
  another sign/dash-joined token (start of text, whitespace, a directional isolate U+2066-U+2069
  or one of `( [ / : ; = ~ ≈ < >` before it). So '−2,958' -> -2958, while '3–10' (a range),
  '2031–2035', 'S6-L1' and
  'A-cba-301' give unsigned tokens (3, 10; 2031, 2035; 6, 1; 301). A leading '+' is dropped
  (+1,631 == 1631). Arabic letters before a dash count as letters.
- Percent signs (% and U+066A) are ignored; the number before them is kept.

Skipped: the version header line (the first content line, `> **Document version:** ...`),
Markdown link and image targets `](...)`, autolinks `<http...>`, bare URLs, and, in the second
(Arabic) file only, lines identical to the canonical English label line
`> Labels: <LABEL>. <ALIGNMENT_LIMITATION>.` (common.labels): the Arabic file repeats that line
verbatim for the label test and carries its own Arabic rendering next to it, and it is the Arabic
rendering that is compared with the English file's label line. Everything else counts, including
footnotes, run paths and ids, so the two files must cite the same things.

Multiset, not set: a figure that appears twice in English and once in Arabic is a mismatch.
"""

from __future__ import annotations

import csv
import re
import sys
from collections import Counter
from pathlib import Path

import typer

from common import REPO_ROOT
from common.labels import ALIGNMENT_LIMITATION, LABEL

LABEL_LINE = f"> Labels: {LABEL}. {ALIGNMENT_LIMITATION}."

_DIGITS = {ord(c): str(i) for i, c in enumerate("٠١٢٣٤٥٦٧٨٩")}
_DIGITS.update({ord(c): str(i) for i, c in enumerate("۰۱۲۳۴۵۶۷۸۹")})
_DASHES = "−‒–—"
_SIGN_OK_BEFORE = set(" \t([/:;=~≈<>  ")
# Unicode directional isolates (LRI, RLI, FSI, PDI; FIX_R8 item 4) around numeric runs in the
# Arabic summary: a dash right after one is still a sign.
_SIGN_OK_BEFORE |= set("\u2066\u2067\u2068\u2069")

_LINK_TARGET = re.compile(r"\]\([^)]*\)")
_AUTOLINK = re.compile(r"<https?://[^>]*>")
_URL = re.compile(r"https?://\S+")
_THOUSANDS = re.compile(r"(?<=\d)[,٬](?=\d{3}(?!\d))")
_NUMBER = re.compile(r"(?P<sign>[-+]?)(?P<num>\d+(?:\.\d+)?)")
_SID = re.compile(r"\bS-[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*")

app = typer.Typer(add_completion=False, help="Source and bilingual checks.")


def normalise(text: str) -> str:
    """Digits to ASCII, Arabic separators, thousands separators removed, percent dropped."""
    text = text.translate(_DIGITS).replace("٫", ".")
    text = text.replace("%", " ").replace("٪", " ")
    # Repeat: 1,234,567 needs two passes of the look-behind pattern.
    prev = None
    while prev != text:
        prev, text = text, _THOUSANDS.sub("", text)
    return text


def _signed(text: str) -> str:
    """Map every dash before a digit to '-' if it is a sign, else to a space (a separator)."""
    out = []
    for i, ch in enumerate(text):
        if (ch in _DASHES or ch == "-") and i + 1 < len(text) and text[i + 1].isdigit():
            before = text[i - 1] if i > 0 else " "
            out.append("-" if before in _SIGN_OK_BEFORE else " ")
        elif ch in _DASHES:
            out.append(" ")
        else:
            out.append(ch)
    return "".join(out)


def _content_lines(text: str, skip_label_line: bool) -> list[str]:
    lines = text.splitlines()
    i = 0
    if lines and lines[0].strip() == "---":
        try:
            i = lines.index("---", 1) + 1
        except ValueError:
            i = 0
    while i < len(lines) and not lines[i].strip():
        i += 1
    if i < len(lines) and lines[i].startswith("> **Document version:**"):
        i += 1
    kept = lines[i:]
    if skip_label_line:
        kept = [ln for ln in kept if ln.strip() != LABEL_LINE]
    return kept


def tokens(text: str, skip_label_line: bool = False) -> Counter[str]:
    """Multiset of normalised numeric tokens ('-2958', '1.52', '2026', ...)."""
    found: Counter[str] = Counter()
    for line in _content_lines(text, skip_label_line):
        line = _AUTOLINK.sub(" ", _LINK_TARGET.sub("]", line))
        line = _URL.sub(" ", line)
        line = _signed(normalise(line))
        for m in _NUMBER.finditer(line):
            start = m.start()
            if start > 0 and (line[start - 1].isdigit() or line[start - 1] == "."):
                continue
            sign = "-" if m["sign"] == "-" else ""
            num = m["num"]
            found[sign + num] += 1
    return found


def compare(en_text: str, ar_text: str) -> tuple[Counter[str], Counter[str]]:
    """(in English but missing from Arabic, in Arabic but missing from English), as multisets."""
    en, ar = tokens(en_text), tokens(ar_text, skip_label_line=True)
    return en - ar, ar - en


def _fmt(c: Counter[str]) -> str:
    return ", ".join(f"{k} ×{v}" if v > 1 else k for k, v in sorted(c.items()))


@app.command("bilingual-check")
def bilingual_check(en: Path, ar: Path) -> None:
    """Compare every numeric token of EN and AR (multiset, digit by digit after normalisation)."""
    en_text, ar_text = en.read_text(encoding="utf-8"), ar.read_text(encoding="utf-8")
    missing_ar, missing_en = compare(en_text, ar_text)
    n_en = sum(tokens(en_text).values())
    n_ar = sum(tokens(ar_text, skip_label_line=True).values())
    if not missing_ar and not missing_en:
        typer.echo(f"bilingual-check PASS: {n_en} numeric tokens in {en}, {n_ar} in {ar}; equal")
        return
    typer.echo(f"bilingual-check FAIL: {n_en} tokens in {en}, {n_ar} in {ar}")
    if missing_ar:
        typer.echo(f"  in {en} but not in {ar}: {_fmt(missing_ar)}")
    if missing_en:
        typer.echo(f"  in {ar} but not in {en}: {_fmt(missing_en)}")
    sys.exit(1)


def index_ids(root: Path = REPO_ROOT) -> set[str]:
    with (root / "docs/sources/index.csv").open(encoding="utf-8", newline="") as fh:
        return {r["id"] for r in csv.DictReader(fh)}


@app.command("check")
def check(files: list[Path]) -> None:
    """Every cited S-id in FILES has a row in docs/sources/index.csv (exit 1 otherwise)."""
    known = index_ids()
    bad = 0
    for f in files:
        text = _URL.sub(" ", f.read_text(encoding="utf-8"))
        for sid in sorted(set(_SID.findall(text)) - known):
            typer.echo(f"{f}: {sid} has no row in docs/sources/index.csv")
            bad += 1
    if bad:
        sys.exit(1)
    typer.echo(f"sources check PASS: {len(files)} file(s)")


# --- licence release note -------------------------------------------------------------------

LICENCE_CSV = Path("docs/licences.csv")
BEGIN = (
    "<!-- BEGIN GENERATED RELEASE TABLE "
    "(uv run python -m common.sources licences-release --write docs/licences-release.md) -->"
)
END = "<!-- END GENERATED RELEASE TABLE -->"

# Flags carried into R8 (prompts/R8.md, R7-checkpoint answer 4): each is a release blocker to
# clear whatever the row's own columns say. (key, pattern on the item name, why it blocks).
NAMED_BLOCKERS: list[tuple[str, str, str]] = [
    (
        "B1 MoF FY2026 budget table",
        r"MoF FY2026",
        "no licence statement captured; republishing the table needs the terms",
    ),
    ("B2 PFRAM", r"PFRAM", "IMF terms of use not captured; concepts cited only"),
    (
        "B3 UNESCO CC BY-SA",
        r"UNESCO",
        "UNESCO data are CC BY-SA 4.0 (share-alike) or website terms not read",
    ),
    (
        "B4 IMF WEO terms",
        r"World Economic Outlook",
        "IMF copyright and usage terms not read; commercial reuse unclear",
    ),
    (
        "B5 CE Delft handbook",
        r"CE Delft",
        "EU reuse notice on the PDF not confirmed; commercial use unclear",
    ),
    (
        "B6 Wikipedia air-route set",
        r"Wikipedia airport pages",
        "route set built from CC BY-SA 4.0 pages: is the derived set share-alike?",
    ),
    (
        "B7 ODbL alignment sidecars",
        r"alignment cost surface",
        "committed sidecars cities/ksa/alignments/ and alignments-v2/ come from an OSM-derived "
        "cost surface: Produced Work or Derivative Database (ODbL share-alike)?",
    ),
    (
        "B8 model ids in the R0 row",
        r"claude-",
        "the R0 orchestrator row names model ids; public documents must not",
    ),
    (
        "B9 Nabrah AI",
        r"Nabrah",
        "publication and broadcast cleared in writing for the public voices on a paid plan "
        "(S-nabrah-005, 1 Nov 2026); attribution answered: attribute Nabrah on published audio",
    ),
]

# A named flag yields to the row's columns only when its approval records Tariq's decision of
# 7 Nov 2026 AST in FIX_LICENCE_CITE_FACTS (both strings required); otherwise it stays BLOCKER.
NAMED_FLAG_ANSWERED: tuple[str, ...] = ("7 Nov 2026 AST", "FIX_LICENCE_CITE_FACTS")


def named_flag_answered(r: dict[str, str]) -> bool:
    ap = r.get("approval") or ""
    return all(s in ap for s in NAMED_FLAG_ANSWERED)


# Model ids stay in docs/licences.md and the run records, never in a deliverable document
# (tests/test_cp2_housekeeping.py); the release note names the row and points there instead.
_MODEL_ID = re.compile(r"claude-(?:fable|opus|haiku|sonnet)-[0-9][0-9-]*")


def redact_model_ids(v: str) -> str:
    """Replace each model id with a pointer to the register row that records it."""
    v = _MODEL_ID.sub("[model id: see docs/licences.md]", v)
    return re.sub(
        r"(\[model id: see docs/licences\.md\](?:, )?)+", "[model ids: see docs/licences.md]", v
    )


def _cellv(v: str | None) -> str:
    return redact_model_ids(" ".join((v or "").split())).replace("|", "\\|")


def licence_rows(root: Path = REPO_ROOT) -> list[tuple[str, dict[str, str]]]:
    """(register file, row) for docs/licences.csv then every docs/licences-*.csv fragment."""
    files = [root / LICENCE_CSV] + sorted((root / "docs").glob("licences-*.csv"))
    out: list[tuple[str, dict[str, str]]] = []
    for f in files:
        if not f.exists():
            continue
        with f.open(encoding="utf-8", newline="") as fh:
            for r in csv.DictReader(fh):
                if (r.get("item") or "").strip():
                    out.append((f.relative_to(root).as_posix(), r))
    return out


# "superseded by the verified row X (R1a), kept for history" -> X (R1a)
_SUPERSEDED_BY = re.compile(
    r"superseded by (?:the )?(?:verified )?(?:row )?(.+?)(?:, kept for history|; R0 row kept|$)",
    re.IGNORECASE,
)


def release_status(r: dict[str, str]) -> tuple[str, str]:
    """(category, reason). Categories: BLOCKER, VERIFY, OBLIGATIONS, COMPATIBLE, NOT IN RELEASE."""
    item = r.get("item") or ""
    st = (r.get("status") or r.get("notes") or "").lower()
    com = (r.get("commercial_use") or "").strip().lower()
    op = (r.get("open") or "").strip().lower()
    lic = (r.get("licence") or "").lower()
    ob = (r.get("obligations") or "").lower()
    ap = (r.get("approval") or "").strip()
    att = (r.get("attribution") or r.get("attribution_required") or "").strip().lower()
    for key, pat, why in NAMED_BLOCKERS:
        if re.search(pat, item) and not named_flag_answered(r):
            return "BLOCKER", f"{key}: {why}"
    if (
        "superseded" in st
        or st.startswith("not used")
        or "; not used" in st
        or "not available" in st
        or "unreachable" in st
        or st.startswith("planned")
    ):
        extra = "" if com in ("y", "n/a", "") else f"; commercial use {com}: clear before any use"
        sup = _SUPERSEDED_BY.search(r.get("status") or "")
        if sup:
            by = sup.group(1).strip().rstrip(".,;")
            return (
                "NOT IN RELEASE",
                f"superseded by a more specific versioned row ({by}), which carries the release "
                f"status of this source; this generic row is kept for history{extra}",
            )
        return "NOT IN RELEASE", f"not used or superseded per the register{extra}"
    if "blocked" in st:
        return "BLOCKER", "marked blocked in the register"
    if com.startswith("n") and com != "n/a":
        return "BLOCKER", "commercial use not allowed (non-commercial terms)"
    if (
        "unclear" in com
        or "unclear" in op
        or "unclear" in lic
        or com.startswith(("to read", "likely"))
    ):
        return "BLOCKER", "commercial use or terms unclear in the register"
    # An explicit "FLAG:" in the obligations counts, not words like "GPL flags" or "used as flags".
    if (
        "flag" in st
        or "flag:" in ob
        or ap.lower().startswith("flag")
        or "before release" in ap.lower()
    ):
        return "BLOCKER", "flagged in the register"
    if op == "n" and not ap:
        return "BLOCKER", "not open and no recorded approval"
    pending = ("to confirm", "to verify", "to check", "not read", "to re-read")
    if (not st.startswith("verified") and "unverified" in st) or any(w in st for w in pending):
        return "VERIFY", "licence or terms still to confirm"
    if op == "n":
        return "OBLIGATIONS", f"proprietary; approval recorded ({ap}); fact or tool use only"
    if (
        "share-alike" in ob
        or "share-alike" in lic
        or "-sa" in lic
        or "by-sa" in lic
        or "odbl" in lic
    ):
        return "OBLIGATIONS", "attribution; share-alike on derived databases or copied text"
    if att not in ("", "none", "n/a") or ob not in ("", "none", "n/a"):
        return "OBLIGATIONS", "attribution or notice as stated in the register"
    return "COMPATIBLE", "open; commercial use allowed; no obligation beyond the licence notice"


def release_table(root: Path = REPO_ROOT) -> str:
    head = (
        "| # | register | item | version | licence | open | commercial use | release status "
        "| reason | approval |\n"
        "|---|---|---|---|---|---|---|---|---|---|"
    )
    lines = [head]
    for i, (src, r) in enumerate(licence_rows(root), start=1):
        cat, why = release_status(r)
        cells = [
            str(i),
            src.removeprefix("docs/"),
            r.get("item", ""),
            r.get("version", ""),
            r.get("licence", ""),
            r.get("open", ""),
            r.get("commercial_use", ""),
            f"**{cat}**" if cat == "BLOCKER" else cat,
            why,
            r.get("approval", ""),
        ]
        lines.append("| " + " | ".join(_cellv(c) for c in cells) + " |")
    lines += [
        "",
        "Proprietary or not-open items (`open` = N), with the approval the register records "
        "(an empty approval is a blocker unless the item is not in the release):",
        "",
        "| # | item | approval recorded | release status |",
        "|---|---|---|---|",
    ]
    for i, (_src, r) in enumerate(licence_rows(root), start=1):
        if (r.get("open") or "").strip().upper().startswith("N"):
            cat, _ = release_status(r)
            ap = r.get("approval") or "none recorded"
            lines.append(f"| {i} | {_cellv(r.get('item'))} | {_cellv(ap)} | {cat} |")
    return "\n".join(lines)


@app.command("licences-release")
def licences_release(write: Path | None = typer.Option(None, "--write")) -> None:
    """Print the release table, or write it between the GENERATED markers of WRITE."""
    table = release_table()
    if write is None:
        typer.echo(table)
        return
    text = write.read_text(encoding="utf-8")
    if BEGIN not in text or END not in text:
        typer.echo(f"{write}: GENERATED markers not found")
        sys.exit(1)
    pre, rest = text.split(BEGIN, 1)
    _, post = rest.split(END, 1)
    write.write_text(f"{pre}{BEGIN}\n{table}\n{END}{post}", encoding="utf-8")
    typer.echo(f"{write}: {len(licence_rows())} register rows written")


if __name__ == "__main__":
    app()
