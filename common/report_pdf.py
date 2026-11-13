"""PDF of the feasibility report (PUBLISH_PDF_POST, Tariq 13 Nov 2026).

  uv run python -m common.report_pdf build    # docs/report/feasibility-report.pdf (+ the copy in
                                              # film/renders/out/social/ when the volume is there)
  uv run python -m common.report_pdf check    # pages, links, size, private-name count

Presentation only: the text is docs/report/feasibility-report.md as it stands (its sections,
figures and source notes); nothing is added to it except a cover page, page numbers in the
existing Contents list and a running footer. Markdown -> HTML with markdown-it-py (already a
dependency, used by common/ar_render.py), HTML -> A4 PDF with headless Chrome (licence register:
"Google Chrome (headless, local)"). Nothing leaves the machine.

- Heading ids follow GitHub's slug rule, so the report's own `#…` links (Contents, cross
  references) work inside the PDF.
- `[^S-…]` references link to their source note at the end; URLs in the notes are live links.
- Relative links to repository files become links to the public repository
  (`REPO_URL/blob/main/…`).
- Figures stay vector (SVG) where the report uses SVG.
- Contents page numbers: pass 1 prints with placeholders, `pdftotext` finds the page of each
  heading, pass 2 prints with the numbers; a third extraction confirms they did not move.
"""

from __future__ import annotations

import datetime as dt
import html
import os
import posixpath
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import typer
from markdown_it import MarkdownIt

from common import REPO_ROOT
from common.ar_render import CHROME, FONT_DIR

app = typer.Typer(add_completion=False, help="PDF of the feasibility report.", no_args_is_help=True)

REPORT_DIR = REPO_ROOT / "docs" / "report"
SRC = REPORT_DIR / "feasibility-report.md"
OUT = REPORT_DIR / "feasibility-report.pdf"
SOCIAL_COPY = REPO_ROOT / "film" / "renders" / "out" / "social" / "feasibility-report.pdf"
REPO_URL = "https://github.com/alturkestani/KSA-RailTwin"
AUTHOR = "Dr. Tariq Alturkestani"
TITLE = "KSA Rail Twin"
SUBTITLE = "A national rail feasibility study for Saudi Arabia"
NOT_A_PLAN = "Independent simulation, not a government plan"
LICENCE = "Apache-2.0"
PRIVATE_LIST = REPO_ROOT / ".publish" / "private-names.txt"

_FN_DEF = re.compile(r"^\[\^(S-[A-Za-z0-9_.-]+)\]:\s*(.*)$", re.MULTILINE)
_FN_REF = re.compile(r"\[\^(S-[A-Za-z0-9_.-]+)\]")
_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
_HEADING = re.compile(r"<h([1-6])>(.*?)</h\1>", re.DOTALL)
_QUOTE_TABLE = re.compile(r"^(>[^\n]*)\n(\|)", re.MULTILINE)
_TAGS = re.compile(r"<[^>]+>")
_HREF = re.compile(r'href="([^"]*)"')
_IMG_PARA = re.compile(r"<p>((?:<img [^>]*>\s*)+)</p>")
_IMG = re.compile(r'<img src="([^"]*)" alt="([^"]*)"\s*/?>')
_URL = re.compile(r"https?://[^\s<>\"]+")
_TRAIL = ".,;:)"


# ---------------------------------------------------------------- Markdown -> HTML


def slug(text: str) -> str:
    """GitHub's heading anchor: lower case, drop punctuation except - and _, spaces to -."""
    t = html.unescape(_TAGS.sub("", text)).strip().lower()
    t = re.sub(r"[^\w\- ]", "", t)
    return t.replace(" ", "-")


def repo_link(href: str, base: str = "docs/report") -> str:
    """Rewrite a relative repository link to the public repository; keep anchors and URLs."""
    if not href or href.startswith(("#", "http://", "https://", "mailto:")):
        return href
    path, _, frag = href.partition("#")
    full = posixpath.normpath(posixpath.join(base, path))
    return f"{REPO_URL}/blob/main/{full}" + (f"#{frag}" if frag else "")


def _autolink(text: str) -> str:
    def one(m: re.Match[str]) -> str:
        url = m.group(0)
        tail = ""
        while url and url[-1] in _TRAIL:
            tail = url[-1] + tail
            url = url[:-1]
        return f'<a href="{url}">{url}</a>{tail}'

    return _URL.sub(one, text)


def md_to_body(text: str, figure_dir: Path = REPORT_DIR) -> str:
    """The report body as HTML (no <html> wrapper)."""
    text = _COMMENT.sub("", text)
    # A table written straight under a "> Labels" line would be read as part of the quote
    # (lazy continuation); the report means a label line, then the table.
    text = _QUOTE_TABLE.sub(r"\1\n\n\2", text)
    # Each source note becomes its own paragraph with a marker the HTML pass turns into an anchor.
    text = _FN_DEF.sub(lambda m: f"\n@@FNDEF:{m.group(1)}@@ {m.group(2)}\n", text)
    text = _FN_REF.sub(lambda m: f"@@FNREF:{m.group(1)}@@", text)
    md = MarkdownIt("commonmark", {"html": False}).enable("table")
    body = md.render(text)

    seen: dict[str, int] = {}

    def heading(m: re.Match[str]) -> str:
        level, inner = m.group(1), m.group(2)
        s = slug(inner)
        n = seen.get(s, 0)
        seen[s] = n + 1
        hid = s if n == 0 else f"{s}-{n}"
        return f'<h{level} id="{hid}">{inner}</h{level}>'

    body = _HEADING.sub(heading, body)
    body = re.sub(
        r"<p>@@FNDEF:([^@]+)@@ (.*?)</p>",
        lambda m: (
            f'<p class="fn" id="fn-{m.group(1)}"><span class="fnid">[{m.group(1)}]</span> '
            f"{_autolink(m.group(2))}</p>"
        ),
        body,
        flags=re.DOTALL,
    )
    body = re.sub(
        r"@@FNREF:([^@]+)@@",
        lambda m: f'<sup class="fnref"><a href="#fn-{m.group(1)}">[{m.group(1)}]</a></sup>',
        body,
    )
    body = _HREF.sub(lambda m: f'href="{html.escape(repo_link(html.unescape(m.group(1))))}"', body)

    def figures(m: re.Match[str]) -> str:
        out = []
        for src, alt in _IMG.findall(m.group(1)):
            uri = (figure_dir / html.unescape(src)).resolve().as_uri()
            cap = "" if alt.startswith("Figure ") else f"<figcaption>{alt}</figcaption>"
            out.append(f'<figure><img src="{uri}" alt="{alt}">{cap}</figure>')
        return "\n".join(out)

    return _IMG_PARA.sub(figures, body)


def anchors(body: str) -> tuple[set[str], set[str]]:
    """(ids defined, #targets linked) in an HTML body."""
    ids = set(re.findall(r'\bid="([^"]+)"', body))
    refs = {h[1:] for h in re.findall(r'href="(#[^"]+)"', body)}
    return ids, refs


# ---------------------------------------------------------------- page layout


def _fonts() -> str:
    faces = []
    for family, fname, weight in (
        ("Noto Sans", "NotoSans-Regular.ttf", 400),
        ("Noto Sans", "NotoSans-Bold.ttf", 700),
        ("Noto Naskh Arabic", "NotoNaskhArabic-Regular.ttf", 400),
        ("Noto Naskh Arabic", "NotoNaskhArabic-Bold.ttf", 700),
    ):
        uri = (FONT_DIR / fname).resolve().as_uri()
        faces.append(
            f"@font-face {{ font-family: '{family}'; font-weight: {weight}; "
            f"src: url('{uri}') format('truetype'); }}"
        )
    return "\n".join(faces)


CSS = """
@page { size: A4; margin: 18mm 16mm 20mm 16mm;
  @bottom-left { content: "KSA Rail Twin · Independent simulation, not a government plan";
    font: 7.5pt 'Noto Sans', sans-serif; color: #666; }
  @bottom-right { content: counter(page) " / " counter(pages);
    font: 7.5pt 'Noto Sans', sans-serif; color: #666; } }
@page :first { @bottom-left { content: none; } @bottom-right { content: none; } }
html { font-family: 'Noto Sans', 'Noto Naskh Arabic', sans-serif; font-size: 9.6pt;
  line-height: 1.45; color: #111; }
body { margin: 0; }
h1 { font-size: 17pt; line-height: 1.25; margin: 0 0 8pt; color: #12263f; break-after: avoid; }
h1.sec { break-before: page; }
h2 { font-size: 12.5pt; margin: 14pt 0 5pt; color: #12263f; break-after: avoid; }
h3, h4 { font-size: 10.5pt; margin: 10pt 0 4pt; break-after: avoid; }
p, li { orphans: 2; widows: 2; }
a { color: #1f4e79; text-decoration: none; overflow-wrap: anywhere; }
code { font-family: 'Noto Sans', sans-serif; font-size: 0.92em; background: #f1f1f1;
  padding: 0 2px; overflow-wrap: anywhere; }
blockquote { margin: 6pt 0; padding: 3pt 9pt; border-left: 3pt solid #9aa7b5;
  background: #f4f6f8; color: #333; font-size: 8.6pt; }
table { border-collapse: collapse; margin: 6pt 0 9pt; font-size: 7.4pt; line-height: 1.3;
  width: 100%; }
thead { display: table-header-group; }
tr { break-inside: avoid; }
th, td { border: 0.6pt solid #b8c2cc; padding: 2pt 3.5pt; vertical-align: top;
  overflow-wrap: anywhere; text-align: left; }
th { background: #e9eef4; }
figure { margin: 8pt 0; text-align: center; break-inside: avoid; }
figure img { max-width: 100%; max-height: 215mm; }
figcaption { font-size: 8.4pt; color: #333; margin-top: 3pt; }
sup.fnref { font-size: 6.5pt; line-height: 0; }
p.fn { font-size: 7.6pt; line-height: 1.35; margin: 0 0 3pt; overflow-wrap: anywhere; }
p.fn .fnid { font-weight: 700; }
#contents + ul { font-size: 9pt; }
#contents + ul li { list-style: none; }
#contents + ul, #contents + ul ul { padding-left: 14pt; }
.toc-row { display: flex; gap: 6pt; }
.toc-row a { flex: none; }
.toc-row .dots { flex: 1; border-bottom: 0.6pt dotted #999; margin-bottom: 3pt; }
.toc-row .pg { flex: none; min-width: 16pt; text-align: right; }
.cover { height: 255mm; display: flex; flex-direction: column; break-after: page; }
.cover .band { background: #12263f; color: #fff; padding: 26mm 14mm 16mm; }
.cover .t { font-size: 34pt; font-weight: 700; line-height: 1.1; }
.cover .st { font-size: 15pt; margin-top: 6pt; color: #dfe7f0; }
.cover .np { display: inline-block; margin-top: 14pt; padding: 4pt 9pt; border: 1pt solid #fff;
  font-size: 11pt; font-weight: 700; }
.cover .meta { padding: 14mm 14mm 0; font-size: 11pt; line-height: 1.7; }
.cover .meta b { display: inline-block; min-width: 34mm; color: #12263f; }
.cover .label { margin: auto 14mm 0; padding: 6pt 9pt; background: #f4f6f8;
  border-left: 3pt solid #9aa7b5; font-size: 8.6pt; color: #333; }
"""


def cover(build_date: str, commit: str, label: str) -> str:
    rows = [
        ("Author", AUTHOR),
        ("Date", build_date),
        ("Repository", f'<a href="{REPO_URL}">{REPO_URL.removeprefix("https://")}</a>'),
        ("Licence", f"{LICENCE} (code); data credits in the report and the repository"),
        ("Built from", f"commit <code>{commit}</code> of the repository"),
    ]
    meta = "<br>".join(f"<b>{k}</b> {v}" for k, v in rows)
    return (
        '<section class="cover"><div class="band">'
        f'<div class="t">{TITLE}</div><div class="st">{SUBTITLE}</div>'
        f'<div class="np">{NOT_A_PLAN}</div></div>'
        f'<div class="meta">{meta}</div>'
        f'<div class="label">{html.escape(label)}</div></section>'
    )


def _toc_span(body: str) -> tuple[int, int]:
    """Start and end of the Contents list: from its heading to the next top-level heading."""
    h = re.search(r'<h2 id="contents">.*?</h2>', body, re.S)
    if not h:
        raise SystemExit("report_pdf: Contents list not found")
    nxt = body.find("<h1", h.end())
    return h.end(), nxt if nxt > 0 else len(body)


def toc_ids(body: str) -> list[str]:
    a, b = _toc_span(body)
    return re.findall(r'href="#([^"]+)"', body[a:b])


def toc_numbers(body: str, pages: dict[str, int] | None) -> str:
    """Give every link in the Contents list a page number (placeholder when pages is None)."""
    a, b = _toc_span(body)

    def row(m: re.Match[str]) -> str:
        target = m.group(1)
        pg = "000" if pages is None else str(pages.get(target, "?"))
        return (
            f'<span class="toc-row"><a href="#{target}">{m.group(2)}</a>'
            f'<span class="dots"></span><span class="pg">{pg}</span></span>'
        )

    toc = re.sub(r'<a href="#([^"]+)">(.*?)</a>', row, body[a:b])
    return body[:a] + toc + body[b:]


def section_breaks(body: str) -> str:
    """Each numbered top-level section (h1) starts a new page; the report title does not."""
    return re.sub(r'<h1 id="(\d[^"]*)">', r'<h1 class="sec" id="\1">', body)


def page_html(body: str, head: str) -> str:
    return (
        '<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        f"<title>{TITLE}: national rail feasibility study (report)</title>\n"
        f'<meta name="author" content="{AUTHOR}">\n'
        f"<style>\n{_fonts()}\n{CSS}</style>\n</head>\n<body>\n{head}\n{body}</body>\n</html>\n"
    )


def print_pdf(html_path: Path, pdf: Path) -> None:
    subprocess.run(
        [
            CHROME,
            "--headless=new",
            "--disable-gpu",
            "--allow-file-access-from-files",
            "--no-pdf-header-footer",
            "--generate-pdf-document-outline",
            f"--print-to-pdf={pdf.resolve()}",
            html_path.resolve().as_uri(),
        ],
        check=True,
        capture_output=True,
        timeout=300,
    )


def page_texts(pdf: Path) -> list[str]:
    out = subprocess.run(
        ["pdftotext", "-enc", "UTF-8", str(pdf), "-"],
        check=True,
        capture_output=True,
        stdin=subprocess.DEVNULL,
    ).stdout.decode("utf-8")
    return out.split("\f")


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def heading_pages(pdf: Path, body: str) -> dict[str, int]:
    """Page (1-based) of each heading id, found by its text at the start of a line, searching
    forward from the end of the Contents list so the Contents entries themselves never match."""
    texts = page_texts(pdf)
    heads = [
        (hid, _norm(html.unescape(_TAGS.sub("", inner))))
        for _lvl, hid, inner in re.findall(r'<h([1-6])[^>]*id="([^"]+)"[^>]*>(.*?)</h\1>', body)
    ]
    # Lines of every page, with their page number; the Contents ends on the page holding the
    # first section heading after it, so start at the page after the last Contents entry.
    lines = [(i + 1, _norm(ln)) for i, t in enumerate(texts) for ln in t.splitlines()]
    toc_last = "8.5 Workstream documents"
    idx = next(k for k, (_p, ln) in enumerate(lines) if ln.startswith(toc_last))
    first_body = next(
        k for k, (_p, ln) in enumerate(lines) if k > idx and ln.startswith("0. Front matter")
    )
    pages: dict[str, int] = {}
    k = first_body
    for hid, text in heads:
        key = text[:40]
        for j in range(k, len(lines)):
            if lines[j][1].startswith(key):
                pages[hid] = lines[j][0]
                k = j + 1
                break
    return pages


def git_commit() -> str:
    def git(*args: str) -> str:
        return subprocess.run(
            ["git", *args], cwd=REPO_ROOT, capture_output=True, text=True, check=True
        ).stdout.strip()

    dirty = git("status", "--porcelain", "--untracked-files=no")
    return git("rev-parse", "--short=7", "HEAD") + ("-dirty" if dirty else "")


def build_pdf(out: Path, build_date: str, commit: str) -> dict[str, object]:
    from common.labels import LABEL

    body = section_breaks(md_to_body(SRC.read_text(encoding="utf-8")))
    ids, refs = anchors(body)
    missing = sorted(refs - ids)
    if missing:
        raise SystemExit(f"report_pdf: {len(missing)} internal links have no target: {missing}")
    head = cover(build_date, commit, f"Labels: {LABEL}.")
    with tempfile.TemporaryDirectory(prefix="report-pdf-") as tmp:
        t = Path(tmp)
        page1 = t / "pass1.html"
        page1.write_text(page_html(toc_numbers(body, None), head), encoding="utf-8")
        print_pdf(page1, t / "pass1.pdf")
        pages = heading_pages(t / "pass1.pdf", body)
        attempts = 0
        for _ in range(3):
            attempts += 1
            final = t / "final.html"
            final.write_text(page_html(toc_numbers(body, pages), head), encoding="utf-8")
            print_pdf(final, t / "final.pdf")
            again = heading_pages(t / "final.pdf", body)
            if again == pages:
                break
            pages = again
        else:
            raise SystemExit("report_pdf: Contents page numbers did not settle")
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(t / "final.pdf", out)
    toc = toc_ids(body)
    unresolved = [i for i in toc if i not in pages]
    if unresolved:
        raise SystemExit(f"report_pdf: no page found for Contents entries {unresolved}")
    return {"internal_links": len(refs), "toc_entries": len(toc), "attempts": attempts}


# ---------------------------------------------------------------- checks


def pdf_pages(pdf: Path) -> int:
    info = subprocess.run(
        ["pdfinfo", str(pdf)], capture_output=True, text=True, check=True, stdin=subprocess.DEVNULL
    ).stdout
    return int(re.search(r"^Pages:\s+(\d+)", info, re.M).group(1))


def pdf_urls(pdf: Path) -> list[str]:
    out = subprocess.run(
        ["pdfinfo", "-url", str(pdf)],
        capture_output=True,
        text=True,
        check=True,
        stdin=subprocess.DEVNULL,
    ).stdout
    return [ln.split()[-1] for ln in out.splitlines()[1:] if ln.strip()]


def pdf_internal_links(pdf: Path) -> int:
    with tempfile.TemporaryDirectory(prefix="report-pdf-x-") as tmp:
        x = Path(tmp) / "x"
        subprocess.run(
            ["pdftohtml", "-xml", "-i", "-q", str(pdf), str(x)],
            check=True,
            capture_output=True,
            stdin=subprocess.DEVNULL,
        )
        return len(re.findall(r'<a href="x\.html#', (Path(tmp) / "x.xml").read_text("utf-8")))


def private_name_count(text: str) -> int:
    """Hits of the gitignored private-name list (same pattern as tests/test_private_names.py)."""
    if not PRIVATE_LIST.exists():
        return -1
    terms = []
    for line in PRIVATE_LIST.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        term = line.split("\t", 1)[0]
        terms.append(r"[ _-]?".join(re.escape(w) for w in term.split(" ")))
    pat = re.compile("|".join(terms), re.IGNORECASE)
    return len(pat.findall(text))


@app.command()
def build(
    out: Path = typer.Option(OUT, "--out"),
    copy: bool = typer.Option(True, "--copy/--no-copy", help="also copy to the social folder"),
    date: str = typer.Option("", "--date", help="cover date; default today (Asia/Riyadh)"),
) -> None:
    """Build the A4 PDF of docs/report/feasibility-report.md."""
    if not os.path.exists(CHROME):
        raise SystemExit(f"report_pdf: Chrome not found at {CHROME} (set CHROME_PATH)")
    riyadh = dt.timezone(dt.timedelta(hours=3))
    build_date = date or dt.datetime.now(riyadh).strftime("%-d %B %Y")
    commit = git_commit()
    stats = build_pdf(out, build_date, commit)
    typer.echo(f"report_pdf: {out} built from {commit} on {build_date}")
    typer.echo(f"report_pdf: {stats}")
    if copy and SOCIAL_COPY.parent.parent.exists():
        SOCIAL_COPY.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(out, SOCIAL_COPY)
        typer.echo(f"report_pdf: copied to {SOCIAL_COPY.relative_to(REPO_ROOT)}")


@app.command()
def check(pdf: Path = typer.Option(OUT, "--pdf")) -> None:
    """Pages, size, links and the private-name count of a built PDF (counts only)."""
    text = "\f".join(page_texts(pdf))
    urls = pdf_urls(pdf)
    report = {
        "pages": pdf_pages(pdf),
        "bytes": pdf.stat().st_size,
        "external_links": len(urls),
        "repo_links": sum(u.startswith(REPO_URL) for u in urls),
        "internal_links": pdf_internal_links(pdf),
        "private_name_hits": private_name_count(text),
        "a4": "(A4)" in subprocess.check_output(["pdfinfo", str(pdf)], text=True),
    }
    for k, v in report.items():
        typer.echo(f"{k}\t{v}")
    if report["private_name_hits"] > 0 or not report["a4"]:
        raise SystemExit("report_pdf check: FAIL")
    typer.echo("report_pdf check: ok")


if __name__ == "__main__":
    app()
