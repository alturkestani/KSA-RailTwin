"""The bilingual film script: one lines table, checked line by line, rendered to Markdown.

CLI:
  uv run python -m film.script validate film/script/ [--timing PATH] [--ids-root PATH]
                                                     [--strict-runs] [--no-duration-limits]
  uv run python -m film.script estimate film/script/ [--timing PATH]
  uv run python -m film.script render   film/script/

Inputs in the script directory: `lines.csv` (columns in COLUMNS order) and `meta.yaml`
(version, date, author, status, title_ar/title_en, trailer_title_ar/trailer_title_en,
sections_ar/sections_en mapping section number -> title).

`render` writes main.ar.md, main.en.md, trailer.ar.md and trailer.en.md; `validate` fails if
they differ byte for byte from what `render` would write. `estimate` rewrites est_seconds from
the timing YAML (cities/ksa/assumptions/film_timing.yaml; A-film-002..004):
  estimate = round(chars / chars_per_second[lang] + pause_seconds, 1)
where chars = len(text with every whitespace run collapsed to one space, stripped).

`--ids-root` is the root used to resolve S-ids (docs/sources/*.csv with an `id` column),
A-ids (docs/assumptions.md, docs/assumptions-*.md, docs/study-*/assumptions.md,
film/assumptions-r10.md) and `doc:` / `run:` paths. `run:` paths may also resolve under the
main checkout's runs directory given by the environment variable RAILTWIN_RUNS_ROOT.
"""

from __future__ import annotations

import contextlib
import csv
import io
import os
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

import typer
import yaml

from common import REPO_ROOT

COLUMNS = [
    "cut",
    "lang",
    "line_id",
    "section",
    "text",
    "sources",
    "figure_values",
    "on_screen_label",
    "est_seconds",
    "native_review",
    "speech_text",
]
CUTS = ("main", "trailer")
LANGS = ("ar", "en")
# "none" (FIX_HALF2_QUALITY, Tariq 8 Nov 2026): the per-line synthetic stamp was dropped; the single
# closing notice sits on the last shot and in the credits (film.shots check). The column stays data.
LABELS = ("", "composite", "synthetic", "synthetic+not_official", "none", "archival", "quote")
TASHKEEL = re.compile("[\u064b-\u0652\u0670]")  # harakat, tanwin, shadda, sukun, dagger alif
DEFAULT_TIMING = REPO_ROOT / "cities/ksa/assumptions/film_timing.yaml"
DURATION_LIMITS = {"main": (480.0, 720.0), "trailer": (60.0, 90.0)}
OUTPUTS = [(cut, lang) for cut in CUTS for lang in LANGS]

LINE_ID = {"main": re.compile(r"^m-\d{2}-\d{2}$"), "trailer": re.compile(r"^t-\d{2}$")}
REVIEW_APPROVED = re.compile(r"^approved by [A-Z]{2,5} \d{4}-\d{2}-\d{2}$")
S_ID = re.compile(r"^S-[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*$")
A_ID = re.compile(r"^A-[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*$")
A_ID_ANY = re.compile(r"A-[A-Za-z0-9-]+")
ID_IN_TEXT = re.compile(r"\b[SA]-[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*|\b[mt]-\d{2}(?:-\d{2})?\b")
NUMBER = re.compile(r"\d+(?:\.\d+)?")

NOT_OFFICIAL_PREFIXES = ("S-xt-", "A-xt-", "S-rj-", "A-rj-")
NOT_OFFICIAL_DOCS = ("doc:docs/rj-routes-study.md", "doc:docs/extra-travel-study.md")
BANNED = (
    "Transit Costs",
    "Vision 2040",
    "will reduce",
    "will increase",
    "will create",
    "will save",
    "will cut",
    "guarantee",
)
BANNED_AR_SYNTHETIC = ("سوف", "رؤية 2040")

LEGEND = {
    "en": (
        "On-screen labels: composite = a composite character, not a real person; "
        "synthetic = synthetic demand, uncalibrated: scenario comparison, not a forecast; "
        "synthetic+not_official = synthetic, from a side study, not the official ranking; "
        "archival = archival material; quote = a sourced quotation."
    ),
    "ar": (
        "تسميات الشاشة: composite = شخصية مركّبة وليست شخصًا حقيقيًا؛ "
        "synthetic = طلب تركيبي غير مُعايَر: مقارنة سيناريوهات وليست توقعًا؛ "
        "synthetic+not_official = تركيبي من دراسة جانبية وليس الترتيب الرسمي؛ "
        "archival = مادة أرشيفية؛ quote = اقتباس موثّق المصدر."
    ),
}
RUNTIME_WORD = {"en": "Estimated running time", "ar": "المدة التقديرية"}
ON_SCREEN = {"en": "on screen", "ar": "على الشاشة"}

_DIGITS = {ord(c): str(i) for i, c in enumerate("٠١٢٣٤٥٦٧٨٩")}
_DIGITS.update({ord(c): str(i) for i, c in enumerate("۰۱۲۳۴۵۶۷۸۹")})
_THOUSANDS = re.compile(r"(?<=\d)[,٬](?=\d)")

app = typer.Typer(add_completion=False, help="Film script: validate, estimate, render.")


@dataclass
class Report:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


# --- reading -------------------------------------------------------------------------------


def read_lines(script_dir: Path) -> list[dict[str, str]]:
    with (script_dir / "lines.csv").open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames not in (COLUMNS, COLUMNS[:-1]):  # speech_text optional (older files)
            raise ValueError(
                f"lines.csv header must be {','.join(COLUMNS)}, got {reader.fieldnames}"
            )
        return [{**{c: "" for c in COLUMNS}, **r} for r in reader]


def write_lines(script_dir: Path, rows: list[dict[str, str]]) -> None:
    path = script_dir / "lines.csv"
    head = path.read_text(encoding="utf-8").split("\n", 1)[0] if path.exists() else ""
    keep = "speech_text" in head.split(",") or any(r.get("speech_text") for r in rows)
    cols = COLUMNS if keep else COLUMNS[:-1]  # an older file without speech_text stays as it was
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=cols, quoting=csv.QUOTE_MINIMAL, lineterminator="\n")
    w.writeheader()
    w.writerows([{c: r.get(c, "") for c in cols} for r in rows])
    path.write_text(buf.getvalue(), encoding="utf-8")


def read_meta(script_dir: Path) -> dict:
    return yaml.safe_load((script_dir / "meta.yaml").read_text(encoding="utf-8"))


def duration_allowance(script_dir: Path) -> dict[str, dict]:
    """Optional meta.yaml `duration_allowance`: {"<cut>/<lang>": {seconds, reason}}."""
    try:
        return dict(read_meta(script_dir).get("duration_allowance") or {})
    except (OSError, yaml.YAMLError, AttributeError):
        return {}


def read_timing(path: Path) -> dict[str, float]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return {
        "ar": float(data["ar_chars_per_second"]["value"]),
        "en": float(data["en_chars_per_second"]["value"]),
        "pause": float(data["pause_seconds"]["value"]),
    }


# --- helpers -------------------------------------------------------------------------------


def collapse(text: str) -> str:
    return " ".join(text.split())


def strip_tashkeel(text: str) -> str:
    """The vocalised speech text minus its diacritics: must equal the accepted spoken base."""
    return collapse(TASHKEEL.sub("", text))


def read_say(script_dir: Path) -> dict[tuple[str, str, str], str]:
    """Spoken-number overrides (film/voice/say.csv next to the script directory), if any."""
    path = script_dir.parent / "voice" / "say.csv"
    if not path.exists():
        return {}
    with path.open(encoding="utf-8", newline="") as fh:
        return {(r["cut"], r["lang"], r["line_id"]): r["say"] for r in csv.DictReader(fh)}


def speech_text_errors(row: dict[str, str], say: dict[tuple[str, str, str], str]) -> list[str]:
    """speech_text (Arabic only) is the accepted spoken line with full tashkeel added: removing
    the diacritics must give back the accepted text (or its say.csv override) character for
    character, so no digit, name or word can change (FIX_HALF2_QUALITY item 3)."""
    st = row.get("speech_text", "")
    if not st:
        return []
    if row["lang"] != "ar":
        return ["speech_text is for Arabic rows only"]
    key = (row["cut"], row["lang"], row["line_id"])
    bases = {strip_tashkeel(row["text"])}  # the accepted text may carry a few marks of its own
    if key in say:
        bases.add(strip_tashkeel(say[key]))
    if strip_tashkeel(st) not in bases:
        return ["speech_text minus tashkeel differs from the accepted text and its say override"]
    if NUMBER.findall(normalise(st)) != NUMBER.findall(normalise(strip_tashkeel(st))):
        return ["speech_text digits changed"]
    return []


def estimate_seconds(text: str, lang: str, timing: dict[str, float]) -> float:
    return round(len(collapse(text)) / timing[lang] + timing["pause"], 1)


def normalise(text: str) -> str:
    """Arabic-Indic/Persian digits -> ASCII, ٫ -> '.', thousands separators removed, ٪ -> %."""
    text = text.translate(_DIGITS).replace("٫", ".").replace("٪", "%")
    return _THOUSANDS.sub("", text)


def number_tokens(text: str) -> list[str]:
    """Numeric tokens of normalised text, ignoring S-/A- ids and line ids."""
    return NUMBER.findall(ID_IN_TEXT.sub(" ", normalise(text)))


def figure_tokens(figure_values: str) -> list[str]:
    out: list[str] = []
    for v in split_list(figure_values):
        out += NUMBER.findall(normalise(v))
    return out


def split_list(value: str) -> list[str]:
    return [t.strip() for t in value.split(";") if t.strip()]


def known_s_ids(root: Path) -> set[str]:
    ids: set[str] = set()
    for f in sorted((root / "docs/sources").glob("*.csv")):
        with f.open(encoding="utf-8", newline="") as fh:
            reader = csv.DictReader(fh)
            if reader.fieldnames and "id" in reader.fieldnames:
                ids |= {r["id"].strip() for r in reader if r.get("id")}
    return ids


def known_a_ids(root: Path) -> set[str]:
    files = [root / "docs/assumptions.md", root / "film/assumptions-r10.md"]
    files += sorted((root / "docs").glob("assumptions-*.md"))
    files += sorted((root / "docs").glob("study-*/assumptions.md"))
    ids: set[str] = set()
    for f in files:
        if not f.is_file():
            continue
        for line in f.read_text(encoding="utf-8").splitlines():
            if line.startswith("|"):
                cells = line.split("|")
                if len(cells) > 2:
                    ids |= {a.rstrip("-") for a in A_ID_ANY.findall(cells[1])}
    return ids


def _safe_rel(path: str) -> bool:
    return bool(path) and not path.startswith("/") and ".." not in Path(path).parts


def run_path_exists(path: str, root: Path) -> bool | None:
    """True/False if resolvable; None when not under the root and no runs root is configured."""
    if (root / path).exists():
        return True
    runs_root = os.environ.get("RAILTWIN_RUNS_ROOT")
    if not runs_root:
        return None
    rr = Path(runs_root)
    rest = path[len("runs/") :] if path.startswith("runs/") else path
    return (rr / rest).exists() or (rr / path).exists()


def mmss(seconds: float) -> str:
    s = int(round(seconds))
    return f"{s // 60}:{s % 60:02d}"


# --- render --------------------------------------------------------------------------------


def _section_titles(meta: dict, lang: str) -> dict[int, str]:
    return {int(k): str(v) for k, v in (meta.get(f"sections_{lang}") or {}).items()}


def render_text(rows: list[dict[str, str]], meta: dict, cut: str, lang: str) -> str:
    """The Markdown for one (cut, lang); deterministic."""
    name = f"film/script/{cut}.{lang}.md"
    header = (
        f"> **Document version:** {name} v{meta['version']} | {meta['date']} | "
        f"Author: {meta['author']} | Status: {meta['status']}"
    )
    title = meta[f"title_{lang}"] if cut == "main" else meta[f"trailer_title_{lang}"]
    mine = [r for r in rows if r["cut"] == cut and r["lang"] == lang]
    total = sum(float(r["est_seconds"] or 0) for r in mine)
    titles = _section_titles(meta, lang)
    body: list[str] = [f"# {title}", "", f"> {RUNTIME_WORD[lang]}: {mmss(total)}. {LEGEND[lang]}"]
    for sec in sorted({int(r["section"]) for r in mine}):
        body += ["", f"## {sec}. {titles.get(sec, '')}".rstrip()]
        for r in (r for r in mine if int(r["section"]) == sec):
            para = f"**{r['line_id']}** {collapse(r['text'])} [^{r['line_id']}]"
            if r["on_screen_label"] not in ("", "none"):
                para += f" *({ON_SCREEN[lang]}: {r['on_screen_label']})*"
            body += ["", para]
    if mine:
        body.append("")
        body += [f"[^{r['line_id']}]: {'; '.join(split_list(r['sources']))}" for r in mine]
    if lang == "ar":
        body = ['<div dir="rtl">', "", *body, "", "</div>"]
    return "\n".join([header, "", *body]) + "\n"


def render_all(script_dir: Path) -> dict[str, str]:
    rows, meta = read_lines(script_dir), read_meta(script_dir)
    return {f"{c}.{lg}.md": render_text(rows, meta, c, lg) for c, lg in OUTPUTS}


# --- validate ------------------------------------------------------------------------------


def validate_dir(
    script_dir: Path,
    timing_path: Path = DEFAULT_TIMING,
    ids_root: Path = REPO_ROOT,
    strict_runs: bool = False,
    duration_limits: bool = True,
) -> tuple[Report, list[dict[str, str]]]:
    rep = Report()
    try:
        rows = read_lines(script_dir)
    except (OSError, ValueError) as exc:
        rep.errors.append(f"lines.csv: {exc}")
        return rep, []
    timing = read_timing(timing_path)
    s_ids, a_ids = known_s_ids(ids_root), known_a_ids(ids_root)
    say = read_say(script_dir)
    seen: set[tuple[str, str, str]] = set()

    for n, r in enumerate(rows, start=2):
        where = f"lines.csv row {n} ({r.get('cut')}/{r.get('lang')}/{r.get('line_id')})"
        err = rep.errors.append
        cut, lang, lid = r["cut"], r["lang"], r["line_id"]
        # a. schema and enums
        if cut not in CUTS:
            err(f"{where}: cut {cut!r} not in {CUTS}")
        if lang not in LANGS:
            err(f"{where}: lang {lang!r} not in {LANGS}")
        if cut in LINE_ID and not LINE_ID[cut].match(lid):
            err(f"{where}: line_id {lid!r} does not match {LINE_ID[cut].pattern}")
        key = (cut, lang, lid)
        if key in seen:
            err(f"{where}: duplicate line_id for ({cut}, {lang})")
        seen.add(key)
        if not (r["section"].isdigit() and 1 <= int(r["section"]) <= 8):
            err(f"{where}: section {r['section']!r} must be an integer 1..8")
        if not r["text"].strip():
            err(f"{where}: empty text")
        if r["on_screen_label"] not in LABELS:
            err(f"{where}: on_screen_label {r['on_screen_label']!r} not in {LABELS}")
        review = r["native_review"]
        ok_review = review == "pending" or REVIEW_APPROVED.match(review)
        if lang == "en":
            ok_review = ok_review or review == "n/a"
        if not ok_review:
            err(f"{where}: native_review {review!r} invalid for lang {lang}")
        # b. sources present; c./d. resolvable
        sources = split_list(r["sources"])
        if not sources:
            err(f"{where}: no source")
        for tok in sources:
            if tok.startswith("S-"):
                if not S_ID.match(tok):
                    err(f"{where}: malformed S-id {tok!r}")
                elif tok not in s_ids:
                    err(f"{where}: {tok} not found in docs/sources/*.csv")
            elif tok.startswith("A-"):
                if not A_ID.match(tok):
                    err(f"{where}: malformed A-id {tok!r}")
                elif tok not in a_ids:
                    err(f"{where}: {tok} not found in any assumptions register")
            elif tok.startswith("doc:"):
                path = tok[4:].split("#", 1)[0]
                if not _safe_rel(path):
                    err(f"{where}: doc path {path!r} must be repo-relative")
                elif not (ids_root / path).exists():
                    err(f"{where}: doc path {path} does not exist")
            elif tok.startswith("run:"):
                path = tok[4:]
                if not _safe_rel(path):
                    err(f"{where}: run path {path!r} must be repo-relative")
                    continue
                found = run_path_exists(path, ids_root)
                if found is False:
                    err(f"{where}: run path {path} not found (repo or RAILTWIN_RUNS_ROOT)")
                elif found is None:
                    msg = f"{where}: run path {path} unverifiable (set RAILTWIN_RUNS_ROOT)"
                    (rep.errors if strict_runs else rep.warnings).append(msg)
            else:
                err(f"{where}: source token {tok!r} is not S-, A-, run: or doc:")
        # e. every number in the text is a declared figure value
        figs = set(figure_tokens(r["figure_values"]))
        for v in split_list(r["figure_values"]):
            if not NUMBER.fullmatch(normalise(v).lstrip("-+").rstrip("%")):
                err(f"{where}: figure_values entry {v!r} is not numeric")
        missing = sorted({t for t in number_tokens(r["text"]) if t not in figs})
        if missing:
            err(f"{where}: numbers in text not in figure_values: {', '.join(missing)}")
        # g. labels
        label = r["on_screen_label"]
        not_official = any(t.startswith(NOT_OFFICIAL_PREFIXES) for t in sources) or any(
            t.split("#", 1)[0] in NOT_OFFICIAL_DOCS for t in sources
        )
        modelled = not_official or any(t.startswith("run:") for t in sources)
        # FIX_HALF2_QUALITY (Tariq, 8 Nov 2026): a modelled line may carry "none" (the stamp
        # dropped in favour of the single closing notice); it may not pose as composite/quote.
        if not_official and label not in ("synthetic+not_official", "none"):
            err(f"{where}: side-study source needs on_screen_label synthetic+not_official or none")
        elif modelled and not (label.startswith("synthetic") or label == "none"):
            err(f"{where}: run: source needs on_screen_label synthetic* or none")
        for msg in speech_text_errors(r, say):
            err(f"{where}: {msg}")
        # h. banned phrases
        low = r["text"].lower()
        for phrase in BANNED:
            if phrase.lower() in low:
                err(f"{where}: banned phrase {phrase!r}")
        if lang == "ar" and (label.startswith("synthetic") or modelled):
            norm = normalise(r["text"])
            for phrase in BANNED_AR_SYNTHETIC:
                if phrase in norm:
                    err(f"{where}: banned phrase {phrase!r} in a synthetic line")
        # i. duration estimate
        if lang in LANGS:
            want = estimate_seconds(r["text"], lang, timing)
            try:
                got = float(r["est_seconds"])
            except ValueError:
                err(f"{where}: est_seconds {r['est_seconds']!r} is not a number (run estimate)")
            else:
                if abs(got - want) > 0.05:
                    err(f"{where}: est_seconds {got} != estimate {want} (run estimate)")

    # f. bilingual parity
    for cut in CUTS:
        by = {
            lang: {r["line_id"]: r for r in rows if r["cut"] == cut and r["lang"] == lang}
            for lang in LANGS
        }
        ar, en = by["ar"], by["en"]
        for lid in sorted(set(ar) - set(en)):
            rep.errors.append(f"{cut}/{lid}: in ar but not in en")
        for lid in sorted(set(en) - set(ar)):
            rep.errors.append(f"{cut}/{lid}: in en but not in ar")
        for lid in sorted(set(ar) & set(en)):
            if ar[lid]["section"] != en[lid]["section"]:
                rep.errors.append(f"{cut}/{lid}: section differs between ar and en")
            fa = Counter(figure_tokens(ar[lid]["figure_values"]))
            fe = Counter(figure_tokens(en[lid]["figure_values"]))
            if fa != fe:
                rep.errors.append(
                    f"{cut}/{lid}: figure_values differ (ar {sorted(fa.elements())}, "
                    f"en {sorted(fe.elements())})"
                )

    # i. totals
    if duration_limits:
        for cut, lang in OUTPUTS:
            total = 0.0
            for r in rows:
                if r["cut"] == cut and r["lang"] == lang:
                    with contextlib.suppress(ValueError):
                        total += float(r["est_seconds"])
            lo, hi = DURATION_LIMITS[cut]
            allow = duration_allowance(script_dir).get(f"{cut}/{lang}")
            if allow and hi < total <= hi + float(allow["seconds"]):
                # FIX_MBS_TITLE: a recorded, named excess over the ceiling (meta.yaml) is reported
                # as a warning, never silently; anything beyond it is still an error.
                rep.warnings.append(
                    f"{cut}/{lang}: spoken estimate {total:.1f} s over {hi:.0f} s within the "
                    f"recorded allowance of {float(allow['seconds']):.1f} s ({allow['reason']})"
                )
            elif total > hi:
                rep.errors.append(f"{cut}/{lang}: total {total:.1f} s outside [{lo:.0f}, {hi:.0f}]")
            elif total < lo:
                # FIX_HALF2_QUALITY: after the refrain cut the spoken estimate may fall under the
                # floor; the delivered cut (narration + shot heads/tails, film/assemble/edl-*.csv)
                # is what must stay inside the limits (tests/test_film_quality.py).
                rep.warnings.append(
                    f"{cut}/{lang}: spoken estimate {total:.1f} s under {lo:.0f} s "
                    "(delivered length checked on the edit list)"
                )

    # j. rendered Markdown up to date
    try:
        expected = render_all(script_dir)
    except (KeyError, ValueError, TypeError, OSError, yaml.YAMLError) as exc:
        rep.errors.append(f"render failed: {exc!r} (check meta.yaml)")
    else:
        for fname, text in expected.items():
            f = script_dir / fname
            if not f.is_file() or f.read_bytes() != text.encode("utf-8"):
                rep.errors.append(f"{fname} is missing or stale: run `film.script render`")
    return rep, rows


# --- commands ------------------------------------------------------------------------------


@app.command()
def validate(
    script_dir: Path,
    timing: Path = typer.Option(DEFAULT_TIMING, "--timing"),
    ids_root: Path = typer.Option(REPO_ROOT, "--ids-root"),
    strict_runs: bool = typer.Option(False, "--strict-runs"),
    no_duration_limits: bool = typer.Option(False, "--no-duration-limits"),
) -> None:
    """Check every rule on lines.csv and the rendered Markdown; exit 1 on any error."""
    rep, rows = validate_dir(script_dir, timing, ids_root, strict_runs, not no_duration_limits)
    for w in rep.warnings:
        typer.echo(f"WARN {w}")
    for e in rep.errors:
        typer.echo(f"FAIL {e}")
    if rep.errors:
        typer.echo(f"film.script validate FAIL: {len(rep.errors)} error(s)")
        raise typer.Exit(1)
    counts = Counter((r["cut"], r["lang"]) for r in rows)
    totals = {
        k: sum(float(r["est_seconds"]) for r in rows if (r["cut"], r["lang"]) == k) for k in counts
    }
    parts = ", ".join(
        f"{c}/{lg} {counts[(c, lg)]} lines {mmss(totals.get((c, lg), 0))}" for c, lg in OUTPUTS
    )
    typer.echo(
        f"film.script validate PASS: {len(rows)} lines ({parts}); {len(rep.warnings)} warning(s)"
    )


@app.command()
def estimate(script_dir: Path, timing: Path = typer.Option(DEFAULT_TIMING, "--timing")) -> None:
    """Rewrite est_seconds in lines.csv from the timing YAML (row order kept)."""
    t = read_timing(timing)
    rows = read_lines(script_dir)
    for r in rows:
        if r["lang"] in LANGS:
            r["est_seconds"] = f"{estimate_seconds(r['text'], r['lang'], t):.1f}"
    write_lines(script_dir, rows)
    typer.echo(f"film.script estimate: {len(rows)} lines updated")


@app.command()
def render(script_dir: Path) -> None:
    """Write main.ar.md, main.en.md, trailer.ar.md and trailer.en.md."""
    for fname, text in render_all(script_dir).items():
        (script_dir / fname).write_bytes(text.encode("utf-8"))
        typer.echo(f"wrote {script_dir / fname}")


if __name__ == "__main__":
    app()
