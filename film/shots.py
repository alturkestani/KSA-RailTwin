"""Storyboard shot list check (film/storyboard/shots.yaml).

CLI:
  uv run python -m film.shots check film/storyboard/shots.yaml [--lines film/script/lines.csv]
  uv run python -m film.shots storyboard film/storyboard/shots.yaml [--write]

The YAML is a list of shots, or a mapping with a `shots:` list. Each shot has: id
(`sh-NN-NN`, unique), section (1..8), type, duration_s (> 0), visual, data_source (a run path,
register file, `S-...` id, or `none` for title/text_card only), on_screen_text {en, ar},
narration_line_ids (list; checked against lines.csv for the shot's cut with --lines), cut,
transition, footer, renderer, osm_credit (true for every map_animation), ai_generated (if true,
`ai_label` is required), output (under film/renders/). Footer (FIX_HALF2_QUALITY, Tariq 8 Nov
2026): one closing notice per cut, `footer: synthetic` on the cut's last shot only (the last slide,
or the credits roll in the main cut), `none` everywhere else; no per-shot synthetic stamp.
No key or value may mention a logo unless it says "no logo".

Also checked: a shot that re-cuts (`reuse_of`) or holds (`held_frame_from`) other shots keeps their
OSM credit and `extra_credit` (chart re-cuts inherit neither);
`quote_label` is {en: bool, ar: bool}. With --lines: every narrated shot's duration_s equals the
sum of its covered lines' English est_seconds, and a language carries the quotation style exactly
when its covered lines are labelled `quote`. `storyboard` checks (or regenerates) the section-2
tables of storyboard.md from shots.yaml and meta.yaml.
"""

from __future__ import annotations

import csv
import re
from collections import defaultdict
from pathlib import Path

import typer
import yaml

SHOT_ID = re.compile(r"^sh-\d{2}-\d{2}$")
TYPES = (
    "map_animation",
    "chart",
    "title",
    "archival",
    "split_screen",
    "talking_label",
    "text_card",
)
CUTS = ("main", "trailer")
FOOTERS = ("synthetic", "synthetic+not_official", "none")
RENDERERS = ("deckgl_capture", "manim", "remotion", "blender", "ffmpeg_only", "sim_map")
NO_DATA_TYPES = ("title", "text_card")
REQUIRED = (
    "id",
    "section",
    "type",
    "duration_s",
    "visual",
    "data_source",
    "on_screen_text",
    "narration_line_ids",
    "cut",
    "transition",
    "footer",
    "renderer",
    "osm_credit",
    "output",
)

app = typer.Typer(add_completion=False, help="Storyboard shot-list checks.")


def load_shots(path: Path) -> list[dict]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = data.get("shots")
    if not isinstance(data, list):
        raise ValueError("expected a list of shots or a mapping with a `shots:` list")
    return data


def line_ids_by_cut(lines_csv: Path) -> dict[str, set[str]]:
    out: dict[str, set[str]] = defaultdict(set)
    with lines_csv.open(encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            out[r["cut"]].add(r["line_id"])
    return out


def _logo_hits(obj: object, path: str = "") -> list[str]:
    hits: list[str] = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if "logo" in str(k).lower():
                hits.append(f"key {path}{k}")
            hits += _logo_hits(v, f"{path}{k}.")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            hits += _logo_hits(v, f"{path}{i}.")
    elif isinstance(obj, str):
        low = obj.lower()
        if "logo" in low and "no logo" not in low:
            hits.append(f"value at {path.rstrip('.')}: {obj!r}")
    return hits


def check_shots(shots: list[dict], line_ids: dict[str, set[str]] | None = None) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()
    for i, s in enumerate(shots):
        if not isinstance(s, dict):
            errors.append(f"shot #{i + 1}: not a mapping")
            continue
        sid = str(s.get("id", f"#{i + 1}"))
        err = errors.append
        for k in REQUIRED:
            if k not in s:
                err(f"{sid}: missing key {k}")
        if not SHOT_ID.match(sid):
            err(f"{sid}: id must match sh-NN-NN")
        if sid in seen:
            err(f"{sid}: duplicate id")
        seen.add(sid)
        sec = s.get("section")
        if not (isinstance(sec, int) and not isinstance(sec, bool) and 1 <= sec <= 8):
            err(f"{sid}: section must be an integer 1..8")
        typ = s.get("type")
        if typ not in TYPES:
            err(f"{sid}: type {typ!r} not in {TYPES}")
        dur = s.get("duration_s")
        if isinstance(dur, bool) or not isinstance(dur, int | float) or dur <= 0:
            err(f"{sid}: duration_s must be a number > 0")
        if not (isinstance(s.get("visual"), str) and s["visual"].strip()):
            err(f"{sid}: visual must be a non-empty string")
        ds = s.get("data_source")
        if not (isinstance(ds, str) and ds.strip()):
            err(f"{sid}: data_source must be a non-empty string")
            ds = ""
        elif ds == "none" and typ not in NO_DATA_TYPES:
            err(f"{sid}: data_source 'none' is only allowed for {NO_DATA_TYPES}")
        ost = s.get("on_screen_text")
        if not (
            isinstance(ost, dict)
            and isinstance(ost.get("en"), str)
            and isinstance(ost.get("ar"), str)
        ):
            err(f"{sid}: on_screen_text must have string keys en and ar")
        nl = s.get("narration_line_ids")
        cut = s.get("cut")
        if cut not in CUTS:
            err(f"{sid}: cut {cut!r} not in {CUTS}")
        if not isinstance(nl, list) or not all(isinstance(x, str) for x in nl):
            err(f"{sid}: narration_line_ids must be a list of strings")
        elif line_ids is not None:
            known = line_ids.get(str(cut), set())
            for lid in nl:
                if lid not in known:
                    err(f"{sid}: narration line {lid} not in lines.csv for cut {cut}")
        if not isinstance(s.get("transition"), str):
            err(f"{sid}: transition must be a string")
        footer = s.get("footer")
        if footer not in FOOTERS:
            err(f"{sid}: footer {footer!r} not in {FOOTERS}")
        if s.get("renderer") not in RENDERERS:
            err(f"{sid}: renderer {s.get('renderer')!r} not in {RENDERERS}")
        osm = s.get("osm_credit")
        if not isinstance(osm, bool):
            err(f"{sid}: osm_credit must be true or false")
        elif typ == "map_animation" and not osm:
            err(f"{sid}: map_animation needs osm_credit: true (OSM, ODbL)")
        ai = s.get("ai_generated", False)
        if not isinstance(ai, bool):
            err(f"{sid}: ai_generated must be true or false")
        elif ai and not (isinstance(s.get("ai_label"), str) and s["ai_label"].strip()):
            err(f"{sid}: ai_generated shots need a non-empty ai_label")
        out = s.get("output")
        if not (isinstance(out, str) and out.startswith("film/renders/")):
            err(f"{sid}: output must start with film/renders/")
        for hit in _logo_hits(s):
            err(f"{sid}: logo mention ({hit}); entity logos are not allowed")
    return errors


def duration_by_cut(shots: list[dict]) -> dict[str, float]:
    tot: dict[str, float] = defaultdict(float)
    for s in shots:
        d = s.get("duration_s") if isinstance(s, dict) else None
        if isinstance(d, int | float) and not isinstance(d, bool):
            tot[str(s.get("cut"))] += float(d)
    return dict(tot)


FOOTER_RANK = {"none": 0, "synthetic": 1, "synthetic+not_official": 2}
INHERIT_KEYS = ("reuse_of", "held_frame_from")


def check_inheritance(shots: list[dict]) -> list[str]:
    """A shot that re-cuts (`reuse_of`) or holds (`held_frame_from`) another shot's picture keeps
    that picture's credits: OSM and any extra (Copernicus) credit. A `chart` re-cut takes only the
    data panel, so it inherits neither. (Footers are no longer inherited: FIX_HALF2_QUALITY.)"""
    by_id = {str(s.get("id")): s for s in shots if isinstance(s, dict)}
    errors: list[str] = []
    for s in by_id.values():
        sid = str(s.get("id"))
        for key in INHERIT_KEYS:
            refs = s.get(key)
            if refs is None:
                continue
            if not isinstance(refs, list) or not all(isinstance(r, str) for r in refs):
                errors.append(f"{sid}: {key} must be a list of shot ids")
                continue
            for ref in refs:
                src = by_id.get(ref)
                if src is None:
                    errors.append(f"{sid}: {key} names unknown shot {ref}")
                    continue
                if key == "reuse_of" and s.get("type") == "chart":
                    continue  # a chart re-cut takes the data panel only, not the map frame
                if src.get("osm_credit") is True and s.get("osm_credit") is not True:
                    errors.append(f"{sid}: shows {ref}'s map ({key}) but osm_credit is not true")
                if src.get("extra_credit") and s.get("extra_credit") != src.get("extra_credit"):
                    errors.append(f"{sid}: {key} {ref} needs extra_credit {src['extra_credit']!r}")
    return errors


def check_closing_notice(shots: list[dict]) -> list[str]:
    """FIX_HALF2_QUALITY (Tariq, 8 Nov 2026): the synthetic notice is said once, at the end. Each
    cut's last shot carries `footer: synthetic` (rendered in both languages, Arabic in glossary
    term 4 wording); every other shot carries `footer: none`."""
    errors: list[str] = []
    by_cut: dict[str, list[dict]] = defaultdict(list)
    for s in shots:
        if isinstance(s, dict):
            by_cut[str(s.get("cut"))].append(s)
    for cut, items in by_cut.items():
        for s in items[:-1]:
            if s.get("footer") != "none":
                errors.append(f"{s.get('id')}: footer must be none (single closing notice, {cut})")
        if items and items[-1].get("footer") != "synthetic":
            errors.append(f"{items[-1].get('id')}: last {cut} shot must carry footer synthetic")
    return errors


def check_quote_labels(shots: list[dict]) -> list[str]:
    """`quote_label` is per language ({en: bool, ar: bool}): the quotation style must never be set
    on a language whose script paraphrases."""
    errors: list[str] = []
    for s in shots:
        if not isinstance(s, dict) or "quote_label" not in s:
            continue
        q = s["quote_label"]
        if not (isinstance(q, dict) and set(q) == {"en", "ar"}):
            errors.append(f"{s.get('id')}: quote_label must be a mapping with en and ar booleans")
        elif not all(isinstance(v, bool) for v in q.values()):
            errors.append(f"{s.get('id')}: quote_label values must be true or false")
    return errors


def load_line_rows(lines_csv: Path) -> dict[tuple[str, str, str], dict[str, str]]:
    """lines.csv rows keyed by (cut, lang, line_id)."""
    with lines_csv.open(encoding="utf-8", newline="") as fh:
        return {(r["cut"], r["lang"], r["line_id"]): r for r in csv.DictReader(fh)}


def covered_seconds(shot: dict, rows: dict, lang: str) -> float:
    cut = str(shot.get("cut"))
    total = 0.0
    for lid in shot.get("narration_line_ids") or []:
        row = rows.get((cut, lang, lid))
        if row is not None:
            total += float(row["est_seconds"])
    return round(total, 1)


def check_durations(shots: list[dict], rows: dict) -> list[str]:
    """duration_s = the sum of the covered lines' English est_seconds (shots without lines, such
    as the credits roll, are timed on their own)."""
    errors: list[str] = []
    for s in shots:
        if not isinstance(s, dict) or not s.get("narration_line_ids"):
            continue
        want = covered_seconds(s, rows, "en")
        dur = s.get("duration_s")
        if isinstance(dur, int | float) and abs(float(dur) - want) > 0.05:
            errors.append(f"{s.get('id')}: duration_s {dur} != covered English lines {want}")
    return errors


def check_quote_lines(shots: list[dict], rows: dict) -> list[str]:
    """A language may carry the quotation style only if every covered line in that language is
    labelled `quote`; an English `quote` line needs the English quotation style."""
    errors: list[str] = []
    for s in shots:
        if not isinstance(s, dict):
            continue
        q = s.get("quote_label") if isinstance(s.get("quote_label"), dict) else {}
        cut = str(s.get("cut"))
        for lang in ("en", "ar"):
            labels = [
                rows[(cut, lang, lid)]["on_screen_label"]
                for lid in s.get("narration_line_ids") or []
                if (cut, lang, lid) in rows
            ]
            if q.get(lang) is True and any(lab != "quote" for lab in labels):
                errors.append(
                    f"{s.get('id')}: quote_label.{lang} is true but a covered {lang} line "
                    "is not a quotation (paraphrase)"
                )
            if q.get(lang) is not True and "quote" in labels:
                errors.append(f"{s.get('id')}: covers a {lang} quote line without quote_label")
    return errors


FOOTER_TEXT = {
    "none": "none",
    "synthetic": "synthetic",
    "synthetic+not_official": "synthetic + not official",
}


def _flat(text: object) -> str:
    return " ".join(str(text).split())


def storyboard_row(s: dict) -> str:
    q = s.get("quote_label") if isinstance(s.get("quote_label"), dict) else {}
    extras = [
        name
        for name, on in (
            ("composite label", bool(s.get("composite_label"))),
            ("quotation", any(q.values())),
            ("OSM credit", s.get("osm_credit") is True),
            ("legend", bool(s.get("layer_legend"))),
            ("Copernicus credit", bool(s.get("extra_credit"))),
        )
        if on
    ]
    footer = FOOTER_TEXT.get(str(s.get("footer")), str(s.get("footer")))
    if extras:
        footer += "; " + ", ".join(extras)
    ost = s.get("on_screen_text") or {}
    cells = [
        str(s.get("id")),
        f"{float(s.get('duration_s', 0)):.1f}",
        f"{s.get('type')} / {s.get('renderer')}",
        _flat(s.get("visual", "")),
        f"`{_flat(s.get('data_source', ''))}`",
        _flat(ost.get("en", "")),
        _flat(ost.get("ar", "")),
        ", ".join(s.get("narration_line_ids") or []),
        footer,
        _flat(s.get("transition", "")),
    ]
    return "| " + " | ".join(cells) + " |"


TABLE_HEAD = (
    "| Shot | s | Type / renderer | Visual | Data source | On screen (EN) | On screen (AR) "
    "| Lines | Footer | Transition |\n|---|---|---|---|---|---|---|---|---|---|"
)


def storyboard_tables(shots: list[dict], meta: dict) -> str:
    """The section-2 shot tables of storyboard.md, generated from shots.yaml and meta.yaml."""
    out: list[str] = []
    for cut in CUTS:
        for sec in range(1, 9):
            group = [s for s in shots if s.get("cut") == cut and s.get("section") == sec]
            if not group:
                continue
            total = sum(float(s["duration_s"]) for s in group)
            en = meta["sections_en"][sec]
            ar = meta["sections_ar"][sec]
            out.append(
                f"#### {cut.capitalize()} cut, section {sec}: {en} / {ar} "
                f"({len(group)} shots, {total:.1f} s)\n\n{TABLE_HEAD}\n"
                + "\n".join(storyboard_row(s) for s in group)
            )
    return "\n\n".join(out) + "\n"


TABLES_START = "#### "
TABLES_END = "\n## 3."


def check_storyboard(md_text: str, shots: list[dict], meta: dict) -> list[str]:
    """storyboard.md section 2 must equal the tables generated from shots.yaml + meta.yaml (shot
    durations, section titles and on-screen text included)."""
    start, end = md_text.find(TABLES_START), md_text.find(TABLES_END)
    if start < 0 or end < 0:
        return ["storyboard.md: shot tables or section 3 heading not found"]
    have = md_text[start:end].rstrip("\n") + "\n"
    want = storyboard_tables(shots, meta)
    if have == want:
        return []
    have_l, want_l = have.splitlines(), want.splitlines()
    for i, (a, b) in enumerate(zip(have_l, want_l, strict=False)):
        if a != b:
            return [
                f"storyboard.md table line {i + 1} differs from shots.yaml:\n  md:  {a}\n  gen: {b}"
            ]
    return [f"storyboard.md tables have {len(have_l)} lines, shots.yaml gives {len(want_l)}"]


def write_storyboard(md_path: Path, shots: list[dict], meta: dict) -> None:
    text = md_path.read_text(encoding="utf-8")
    start, end = text.find(TABLES_START), text.find(TABLES_END)
    if start < 0 or end < 0:
        raise ValueError("storyboard.md: shot tables or section 3 heading not found")
    new = text[:start] + storyboard_tables(shots, meta) + text[end:]
    md_path.write_text(new, encoding="utf-8")


def run_check(shots_yaml: Path, lines: Path | None) -> int:
    """Print the result; return the exit code."""
    try:
        shots = load_shots(shots_yaml)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        typer.echo(f"FAIL {shots_yaml}: {exc}")
        return 1
    ids = line_ids_by_cut(lines) if lines else None
    errors = check_shots(shots, ids)
    errors += check_inheritance(shots) + check_quote_labels(shots) + check_closing_notice(shots)
    if lines:
        rows = load_line_rows(lines)
        errors += check_durations(shots, rows) + check_quote_lines(shots, rows)
    for e in errors:
        typer.echo(f"FAIL {e}")
    sums = duration_by_cut(shots)
    durs = ", ".join(f"{c} {sums.get(c, 0.0):.1f} s" for c in CUTS)
    if errors:
        typer.echo(f"film.shots check FAIL: {len(errors)} error(s); {len(shots)} shots ({durs})")
        return 1
    typer.echo(f"film.shots check PASS: {len(shots)} shots ({durs})")
    return 0


@app.callback()
def _main() -> None:
    """Storyboard shot-list checks."""


@app.command()
def check(
    shots_yaml: Path,
    lines: Path | None = typer.Option(None, "--lines", help="lines.csv to check narration ids"),
) -> None:
    """Validate the shot list; exit 1 on any error."""
    code = run_check(shots_yaml, lines)
    if code:
        raise typer.Exit(code)


@app.command()
def storyboard(
    shots_yaml: Path,
    md: Path = typer.Option(Path("film/storyboard/storyboard.md"), "--md"),
    meta: Path = typer.Option(Path("film/script/meta.yaml"), "--meta"),
    write: bool = typer.Option(False, "--write", help="rewrite the section-2 tables"),
) -> None:
    """Check (or with --write regenerate) the storyboard.md shot tables from shots.yaml."""
    shot_list = load_shots(shots_yaml)
    meta_d = yaml.safe_load(meta.read_text(encoding="utf-8"))
    if write:
        write_storyboard(md, shot_list, meta_d)
    errors = check_storyboard(md.read_text(encoding="utf-8"), shot_list, meta_d)
    for e in errors:
        typer.echo(f"FAIL {e}")
    if errors:
        raise typer.Exit(1)
    typer.echo(f"film.shots storyboard PASS: {md} matches {shots_yaml}")


if __name__ == "__main__":
    app()
