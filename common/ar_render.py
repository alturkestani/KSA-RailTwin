"""Right-to-left render check of an Arabic Markdown deliverable (FIX_R8 item 4).

Markdown -> standalone HTML (`lang="ar"`, `dir="rtl"`, Noto Naskh Arabic from `common/fonts/`,
Noto Sans as the Latin fallback) -> PDF and PNG screenshots with the approved local headless
Google Chrome (licence register: "Google Chrome (headless, local)"). Nothing leaves the machine.

Blocks with Latin text and no Arabic letter (the version header, the English draft note and the
English label line) are set `dir="ltr"`; every other block, including table cells holding only
numbers, inherits the document's RTL direction, so the check sees what any RTL Markdown renderer
would show. Footnote references `[^S-x]` become superscripts and footnote definitions plain
paragraphs (no plugin needed).

CLI:
  uv run python -m common.ar_render html docs/executive-summary.ar.md OUT.html
  uv run python -m common.ar_render pdf OUT.html OUT.pdf
  uv run python -m common.ar_render shot OUT.html OUT.png [--width 900 --height 1273]
  uv run python -m common.ar_render crop-table FULL.png OUT.png
  uv run python -m common.ar_render bidi-probe OUT.html [--json OUT.json] [--viewports 900,480,360]
      Lays the page out in headless Chrome and measures, for every numeric run (a signed number,
      a slash- or dash-separated range of numbers, a `P10 / P50 / P90` label, with its
      parentheses when the whole parenthetical is the run), the on-screen x position of each
      character. A run passes when its characters appear left to right in their logical order
      (the English reading of the figure) on each line, so every minus or plus sign sits directly
      left of its digits. A run broken across lines fails (`order_ok` in the JSON still says
      whether its fragments kept LTR order and read top to bottom): Tariq's FIX_R8_RTL cases
      were fragments in order that an RTL reader still meets slash-first (`(/ P10`). Every
      footnote marker in RTL text must sit on the same line as, and on the reading-order side
      (left) of, the word or number it follows. Run once per viewport width (default 900 px
      plus the narrow 480 and 360 px; headless Chrome's window cannot go below 500 px, so
      every width is set on the root element `html { width: Npx }` inside a 900 px window, and
      the measured root width is reported).
      Exit 1 if anything fails on any viewport.

FIX_R8_RTL (6 Nov 2026): runs never break across lines (no-break spaces U+00A0 around ` / ` and
`–` inside a run in the source; `white-space: nowrap` on the span the HTML puts around every
isolate), a fully numeric parenthetical sits inside its isolate, and every footnote reference
`[^S-...]` in running text is its own isolate so it stays after the number or id it follows.
"""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

import typer
from markdown_it import MarkdownIt

from common import REPO_ROOT
from common.cli import make_app

CHROME = os.environ.get(
    "CHROME_PATH", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
)
FONT_DIR = REPO_ROOT / "common" / "fonts"
ARABIC = re.compile(r"[؀-ۿ]")
LATIN = re.compile(r"[A-Za-z]")
# Unicode directional isolates: LRI, RLI, FSI ... PDI.
LRI, RLI, FSI, PDI = "⁦", "⁧", "⁨", "⁩"
NBSP = "\u00a0"
# Probe viewports (CSS px): the default page width and two narrow ones (FIX_R8_RTL).
VIEWPORTS = (900, 480, 360)
# The table rule colour; crop-table finds the table by it.
TABLE_RULE = (31, 78, 121)

_FN_DEF = re.compile(r"^\[\^(S-[^\]]+)\]:\s*(.*)$", re.MULTILINE)
_FN_REF = re.compile(r"(⁦?)\[\^(S-[^\]]+)\](⁩?)")
_ISOLATE = re.compile(r"⁦([^⁦⁩<>]*)⁩")
_BLOCK = re.compile(r"<(p|li|th|td|h[1-6])(\b[^>]*)>(.*?)</\1>", re.DOTALL)
_TAGS = re.compile(r"<[^>]+>")


def _font_face(href_dir: str) -> str:
    faces = []
    for family, fname, weight in (
        ("Noto Naskh Arabic", "NotoNaskhArabic-Regular.ttf", 400),
        ("Noto Naskh Arabic", "NotoNaskhArabic-Bold.ttf", 700),
        ("Noto Sans", "NotoSans-Regular.ttf", 400),
        ("Noto Sans", "NotoSans-Bold.ttf", 700),
    ):
        faces.append(
            f"@font-face {{ font-family: '{family}'; font-weight: {weight}; "
            f"src: url('{href_dir}/{fname}') format('truetype'); }}"
        )
    return "\n".join(faces)


CSS_TEMPLATE = """
body { font-family: 'Noto Naskh Arabic', 'Noto Sans', serif; font-size: 15px; line-height: 1.7;
  max-width: 820px; margin: 24px auto; padding: 0 24px; color: #111; background: #fff; }
h1 { font-size: 24px; } h2 { font-size: 19px; margin-top: 1.4em; }
blockquote { margin: 0.6em 0; padding: 0.2em 0.9em; border-inline-start: 4px solid #999;
  color: #333; background: #f6f6f6; font-size: 13px; }
table { border-collapse: collapse; margin: 0.8em 0; font-size: 13.5px;
  border: 2px solid rgb(%d, %d, %d); }
th, td { border: 1px solid rgb(%d, %d, %d); padding: 4px 7px; vertical-align: top; }
th { background: #eef3f8; }
code { font-family: 'Noto Sans', monospace; font-size: 12px; background: #f1f1f1; }
sup { font-size: 10px; }
p.fn { font-size: 12px; color: #333; }
span.nr { white-space: nowrap; }
"""
CSS = CSS_TEMPLATE.replace("%d, %d, %d", ", ".join(map(str, TABLE_RULE)))


def _dir_ltr(m: re.Match[str]) -> str:
    tag, attrs, inner = m.group(1), m.group(2), m.group(3)
    text = _TAGS.sub("", inner)
    if LATIN.search(text) and not ARABIC.search(text):
        attrs += ' dir="ltr"'
    return f"<{tag}{attrs}>{inner}</{tag}>"


def md_to_html(text: str, font_href: str, title: str = "") -> str:
    """Standalone RTL HTML for an Arabic Markdown document."""
    text = _FN_DEF.sub(lambda m: f'<p class="fn"><sup>[{m.group(1)}]</sup> {m.group(2)}</p>', text)
    text = _FN_REF.sub(
        lambda m: f'<sup class="fnref">{m.group(1)}[{m.group(2)}]{m.group(3)}</sup>', text
    )
    md = MarkdownIt("commonmark", {"html": True}).enable("table")
    body = _BLOCK.sub(_dir_ltr, md.render(text))
    # Every isolate in a no-break span: a numeric run never wraps (FIX_R8_RTL item 1).
    body = _ISOLATE.sub(lambda m: f'<span class="nr">{LRI}{m.group(1)}{PDI}</span>', body)
    return (
        '<!DOCTYPE html>\n<html lang="ar" dir="rtl">\n<head>\n<meta charset="utf-8">\n'
        f"<title>{title}</title>\n<style>\n{_font_face(font_href)}\n{CSS}</style>\n</head>\n"
        f"<body>\n{body}</body>\n</html>\n"
    )


def _chrome(*args: str) -> None:
    subprocess.run(
        [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", *args],
        check=True,
        capture_output=True,
        timeout=120,
    )


_CHROME_USABLE: dict[str, bool] = {}


def chrome_usable() -> bool:
    """True when headless Chrome exists and dumps a blank page (PUBLISH_PREP: tests skip
    otherwise, e.g. on a machine without Chrome or where it cannot start)."""
    if CHROME not in _CHROME_USABLE:
        ok = os.path.exists(CHROME)
        if ok:
            try:
                _chrome("--dump-dom", "about:blank")
            except (OSError, subprocess.SubprocessError):
                ok = False
        _CHROME_USABLE[CHROME] = ok
    return _CHROME_USABLE[CHROME]


def table_bbox(png: Path, rule: tuple[int, int, int] = TABLE_RULE, tol: int = 40):
    """(left, top, right, bottom) of the pixels drawn in the table rule colour, or None."""
    import numpy as np
    from PIL import Image

    a = np.asarray(Image.open(png).convert("RGB")).astype(int)
    mask = np.abs(a - np.array(rule)).sum(axis=2) < tol
    ys, xs = np.nonzero(mask)
    if len(xs) == 0:
        return None
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1


# Numeric runs the probe measures (JS regex source; also used by the isolate test). A space
# inside a run may be a no-break space (U+00A0; `\s` matches it in Python and JavaScript). A
# parenthetical that holds nothing but a run is one run with its parentheses (FIX_R8_RTL).
_RUN_CORE = (
    r"(?:P\d{2}(?:\s/\sP\d{2})+)"
    r"|(?:[−+±]?\d[\d,.]*(?:\s?[/–]\s?[−+±]?\d[\d,.]*)+)"
    r"|(?:[−+±]\d[\d,.]*)"
)
RUN_PATTERN = rf"\((?:{_RUN_CORE})\)|{_RUN_CORE}"
_RUN = re.compile(RUN_PATTERN)
# The probe's pattern also finds a parenthetical whose isolate sits inside the parentheses
# (the pre-FIX_R8_RTL form `(LRI P10 / P50 / P90 PDI)`), so the parentheses are measured too.
PROBE_PATTERN = rf"\([\u2066-\u2069]?(?:{_RUN_CORE})[\u2066-\u2069]?\)|{_RUN_CORE}"
_CODE_OR_LINK = re.compile(r"`[^`]*`|\]\([^)]*\)")
# A footnote reference in running text (not a definition `[^S-x]:` at the start of a line).
_FN_INLINE = re.compile(r"\[\^S-[^\]]+\](?!:)")
_RUN_SPACE = re.compile(r"\s?([/–])\s?")


def isolate_numeric_runs(line: str) -> str:
    """Wrap every numeric run and every inline footnote reference of LINE (outside code spans
    and link targets) in LRI ... PDI, with no-break spaces around ` / ` and `–` inside a run.
    Existing LRI/PDI marks are removed first and set again, so the result is canonical and the
    function is idempotent (running it twice changes nothing)."""
    line = line.replace(LRI, "").replace(PDI, "")
    out, pos = [], 0
    for m in _CODE_OR_LINK.finditer(line):
        out.append(_isolate_plain(line[pos : m.start()]))
        out.append(m.group(0))
        pos = m.end()
    out.append(_isolate_plain(line[pos:]))
    return "".join(out)


def _nobreak(run: str) -> str:
    """No-break spaces where a run has spaces around `/` or `–` (none are added)."""
    return _RUN_SPACE.sub(lambda m: m.group(0).replace(" ", NBSP).replace("\t", NBSP), run)


def _isolate_plain(text: str) -> str:
    text = _RUN.sub(lambda m: f"{LRI}{_nobreak(m.group(0))}{PDI}", text)
    return _FN_INLINE.sub(lambda m: f"{LRI}{m.group(0)}{PDI}", text)


PROBE_JS = r"""
<script>
window.addEventListener('load', () => document.fonts.ready.then(() => {
  const re = new RegExp(%s, 'gu');
  const skip = (ch) => /\s|[⁦-⁩]/.test(ch);
  const rect = (node, i) => {
    const r = document.createRange();
    r.setStart(node, i); r.setEnd(node, i + 1);
    return r.getBoundingClientRect();
  };
  const runs = [];
  const nodes = [];
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  let node;
  while ((node = walker.nextNode())) {
    nodes.push(node);
    if (node.parentElement.closest('[dir="ltr"], code, pre, script')) continue;
    const t = node.nodeValue;
    for (const m of t.matchAll(re)) {
      const xs = [];
      for (let i = 0; i < m[0].length; i++) {
        if (skip(m[0][i])) continue;
        const b = rect(node, m.index + i);
        xs.push([m[0][i], b.left, b.top]);
      }
      let ok = true, wraps = 0;
      for (let k = 1; k < xs.length; k++) {
        const dy = xs[k][2] - xs[k - 1][2];
        if (dy < -4) { ok = false; break; }                                // later part above
        if (dy > 4) { wraps++; continue; }                                 // next fragment lower
        if (xs[k][1] < xs[k - 1][1] - 0.5) { ok = false; break; }          // visual order
      }
      // A run broken across lines fails even when its fragments keep their order: an RTL
      // reader meets the fragment's trailing `/` or `(` first (FIX_R8_RTL: no break in a run).
      runs.push({kind: 'run', run: m[0].replace(/[⁦-⁩]/g, ''), ok: ok && !wraps,
                 order_ok: ok, wraps});
    }
  }
  // Footnote markers in RTL text: left of (or below) the word or number they follow.
  for (const sup of document.querySelectorAll('sup')) {
    if (sup.closest('p.fn, [dir="ltr"]')) continue;
    const first = document.createTreeWalker(sup, NodeFilter.SHOW_TEXT).nextNode();
    if (!first) continue;
    let mi = nodes.indexOf(first), word = [], text = '';
    let mark = null;
    for (let i = 0; i < first.nodeValue.length; i++) {
      if (!skip(first.nodeValue[i])) { mark = rect(first, i); break; }
    }
    // Walk back over text nodes to the preceding word (chars back to a space or an isolate
    // start that follows a space); a preceding marker counts as the word.
    outer: for (let n = mi - 1; n >= 0; n--) {
      const v = nodes[n].nodeValue;
      for (let i = v.length - 1; i >= 0; i--) {
        if (/[⁦-⁩]/.test(v[i])) continue;
        if (/\s/.test(v[i])) { if (word.length) break outer; continue; }
        word.push(rect(nodes[n], i)); text = v[i] + text;
      }
      if (word.length && nodes[n].parentElement.closest('sup')) break;
    }
    if (!word.length || !mark) continue;
    const minLeft = Math.min(...word.map((b) => b.left));
    const lastTop = word[0].top;
    const lower = mark.top - lastTop > 4;
    const ok = !lower && mark.right <= minLeft + 1;
    runs.push({kind: 'marker', run: text + ' ' + sup.textContent.replace(/[⁦-⁩]/g, ''),
               ok, wraps: lower ? 1 : 0});
  }
  const pre = document.createElement('pre');
  pre.id = 'bidi-probe';
  pre.textContent = JSON.stringify({width: document.documentElement.getBoundingClientRect().width,
                                    runs});
  document.body.appendChild(pre);
}));
</script>
"""


def bidi_probe(html: Path, width: int = VIEWPORTS[0]) -> list[dict]:
    """Every numeric run and footnote marker of HTML laid out WIDTH CSS px wide, with ok = the
    visual order equals the logical reading order (see the module docstring)."""
    import json
    import tempfile

    page = html.read_text(encoding="utf-8")
    js = PROBE_JS % json.dumps(PROBE_PATTERN)
    # Headless Chrome's window is at least 500 px wide: set the width on the root element.
    style = f"<style>html {{ width: {width}px !important; }}</style>"
    page = page.replace("</head>", style + "</head>").replace("</body>", js + "</body>")
    with tempfile.NamedTemporaryFile(
        "w", suffix=".html", dir=html.resolve().parent, delete=False, encoding="utf-8"
    ) as fh:
        fh.write(page)
        tmp = Path(fh.name)
    try:
        res = subprocess.run(
            [
                CHROME,
                "--headless=new",
                "--disable-gpu",
                f"--window-size={max(width, VIEWPORTS[0])},1273",
                "--virtual-time-budget=5000",
                "--dump-dom",
                tmp.as_uri(),
            ],
            check=True,
            capture_output=True,
            timeout=120,
            text=True,
        )
    finally:
        tmp.unlink()
    m = re.search(r'<pre id="bidi-probe">(.*?)</pre>', res.stdout, re.DOTALL)
    if not m:
        raise RuntimeError("bidi probe produced no result")
    import html as _html

    out = json.loads(_html.unescape(m.group(1)))
    if abs(out["width"] - width) > 0.5:
        raise RuntimeError(f"bidi probe laid out {out['width']} px, not {width} px")
    return out["runs"]


app: typer.Typer = make_app("common.ar_render", "RTL render check of Arabic deliverables.")


@app.command("html")
def html_cmd(src: Path, out: Path) -> None:
    """Render SRC (Arabic Markdown) to standalone RTL HTML at OUT (fonts linked relatively)."""
    out.parent.mkdir(parents=True, exist_ok=True)
    href = os.path.relpath(FONT_DIR, out.parent.resolve())
    out.write_text(md_to_html(src.read_text(encoding="utf-8"), href, src.name), encoding="utf-8")
    typer.echo(f"wrote {out} ({out.stat().st_size:,} bytes)")


@app.command("pdf")
def pdf_cmd(html: Path, out: Path) -> None:
    """Print HTML to PDF with headless Chrome."""
    out.parent.mkdir(parents=True, exist_ok=True)
    _chrome("--no-pdf-header-footer", f"--print-to-pdf={out.resolve()}", html.resolve().as_uri())
    typer.echo(f"wrote {out} ({out.stat().st_size:,} bytes)")


@app.command("shot")
def shot_cmd(
    html: Path,
    out: Path,
    width: int = typer.Option(900, "--width"),
    height: int = typer.Option(1273, "--height"),
    scale: float = typer.Option(1.5, "--scale"),
) -> None:
    """Screenshot the top WIDTH x HEIGHT CSS pixels of HTML."""
    out.parent.mkdir(parents=True, exist_ok=True)
    _chrome(
        f"--window-size={width},{height}",
        f"--force-device-scale-factor={scale}",
        f"--screenshot={out.resolve()}",
        html.resolve().as_uri(),
    )
    typer.echo(f"wrote {out} ({out.stat().st_size:,} bytes)")


@app.command("crop-table")
def crop_table_cmd(full: Path, out: Path, pad: int = typer.Option(12, "--pad")) -> None:
    """Crop the first table (found by its rule colour) out of a full-page screenshot."""
    from PIL import Image

    box = table_bbox(full)
    if box is None:
        raise typer.Exit(1)
    img = Image.open(full)
    left, top, right, bottom = box
    crop = (max(0, left - pad), max(0, top - pad), right + pad, bottom + pad)
    img.crop(crop).save(out, optimize=True)
    typer.echo(f"wrote {out} ({out.stat().st_size:,} bytes; box {box})")


@app.command("bidi-probe")
def bidi_probe_cmd(
    html: Path,
    json_out: Path | None = typer.Option(None, "--json"),
    viewports: str = typer.Option(
        ",".join(map(str, VIEWPORTS)), "--viewports", help="Comma-separated CSS px widths."
    ),
) -> None:
    """Measure the visual order of every numeric run and footnote marker in HTML at each
    viewport width (exit 1 if any is wrong on any viewport)."""
    import json

    report, total_bad = {}, 0
    for w in (int(v) for v in viewports.split(",")):
        runs = bidi_probe(html, w)
        report[str(w)] = runs
        bad = [r for r in runs if not r["ok"]]
        total_bad += len(bad)
        for r in bad:
            typer.echo(f"WRONG  {w}px {r['kind']:6} {r['run']}")
        n_run = sum(r["kind"] == "run" for r in runs)
        n_mark = len(runs) - n_run
        bad_run = sum(r["kind"] == "run" for r in bad)
        typer.echo(
            f"bidi-probe {w}px: {n_run} numeric runs, {bad_run} wrong; "
            f"{n_mark} footnote markers, {len(bad) - bad_run} wrong; "
            f"{sum(r['wraps'] > 0 for r in runs)} wrapped"
        )
    if json_out is not None:
        json_out.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    if total_bad:
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
