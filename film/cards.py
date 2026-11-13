"""Social photo cards (SOCIAL_CARDS, Tariq 12 Nov 2026): five cards x two languages, 1080x1350;
cards 6 (method) and 7 (findings) added by PUBLISH_PDF_POST (Tariq, 13 Nov 2026); card 8
(connecting every region: the S6-L6 route map with city names) by FIX_PDF_CONNECTED (13 Nov 2026).

  uv run python -m film.cards render                 # all ten PNGs -> renders/out/social/cards/
  uv run python -m film.cards render --card 3 --lang ar
  uv run python -m film.cards check                  # jargon, word count, numbers vs sources

A thin wrapper around the film's moving-map engine (film/sim.py, film/sim_main.py): the same night
relief basemap from the study's Copernicus tiles, the same line colours, dashes and glow, the same
fonts and Chrome text layer (Arabic shaped right-to-left), drawn once at 1080x1350 instead of
1920x1080. The engine reads its frame size from the module globals sim.W / sim.H, so `card_size()`
sets them for the duration of one card and restores them.

Card text lives in docs/publish/social-cards.csv (one row per card and language; items are
`label = value [= range]` separated by ` | `). Every figure on a card is checked against the
value computed here from the repo file it cites (`figures()`), rounded as the film rounds; the
trace table is docs/publish/social-cards.md. Chart geometry (card 3 bars) is drawn from the exact
values, never from the rounded text. Maps draw modelled alignments only (DEM least-cost routes;
the 2-point straight sketches are never drawn, as in the film). Deterministic: no randomness.
"""

from __future__ import annotations

import csv
import html
import json
import re
import shutil
import subprocess
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from pathlib import Path

import numpy as np
import pandas as pd
import typer
import yaml
from PIL import Image, ImageFilter

from common import REPO_ROOT
from film import render as R
from film import sim, sim_main
from film.sim import DASH_PX, PAL, Cam, Canvas

app = typer.Typer(add_completion=False, help="Social photo cards (SOCIAL_CARDS).")

CW, CH = 1080, 1350
CARDS_CSV = REPO_ROOT / "docs/publish/social-cards.csv"
OUT = R.RENDERS / "out/social/cards"
WORK = R.RENDERS / "_cards"
LANGS = ("en", "ar")
MAX_WORDS = 25

FOOTER = {
    "en": "Independent simulation, not a government plan · github.com/alturkestani/KSA-RailTwin",
    "ar": "محاكاة مستقلة، مو خطة حكومية · github.com/alturkestani/KSA-RailTwin",
}
CREDIT = R.OSM + " (ODbL) · Relief: " + R.COPERNICUS
# Barred finance jargon (the prompt's list), English and Arabic forms.
JARGON = (
    r"\bNPVs?\b",
    r"\bBCRs?\b",
    r"\bP\s?(?:10|50|80|90)\b",
    r"\bcapex\b",
    r"present\s+values?",
    r"benefit[\s–-]*(?:to[\s–-]*)?cost\s+ratio",
    r"صافي\s*(?:ال)?قيم",
    r"قيم(?:ة|ه|ته|تها)?\s*(?:ال)?حالي",
    r"نسب(?:ة|ه)\s*(?:ال)?منفع",
    r"(?:ال)?نفقات\s*(?:ال)?رأسمالي",
    r"(?:ال)?مئين",
    r"شريحة\s*مئوية",
)
WORD = re.compile(r"\S*[A-Za-zء-ي]\S*")  # a word = a whitespace token with a letter in it
NUMBER = re.compile(r"\d[\d,]*(?:\.\d+)?")


# ---------------------------------------------------------------- card text


def load_cards() -> list[dict[str, str]]:
    with CARDS_CSV.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def card_row(card: int, lang: str) -> dict[str, str]:
    for r in load_cards():
        if int(r["card"]) == card and r["lang"] == lang:
            return r
    raise KeyError((card, lang))


def items(row: dict[str, str]) -> list[list[str]]:
    return [[f.strip() for f in it.split(" = ")] for it in row["items"].split(" | ") if it.strip()]


def body_text(row: dict[str, str]) -> str:
    """Everything counted as card body (footer, credits, legend and map labels excluded)."""
    parts = [row["title"], row["subtitle"], row["note"], row["chart_label"]]
    parts += [f for it in items(row) for f in it]
    return " ".join(p for p in parts if p)


def word_count(row: dict[str, str]) -> int:
    return len(WORD.findall(body_text(row)))


def jargon_hits(text: str) -> list[str]:
    return [m.group(0) for p in JARGON for m in re.finditer(p, text, re.IGNORECASE)]


def all_text(row: dict[str, str]) -> str:
    """Every visible string of a card (body, legend, footer, credit, label)."""
    legend = " ".join(lbl for _, lbl in R.LEGEND[row["lang"]])
    return " ".join([body_text(row), legend, FOOTER[row["lang"]], CREDIT, R.FOOTER[row["lang"]][0]])


# ---------------------------------------------------------------- figures (from the repo files)


def _hm(minutes: float) -> tuple[int, int]:
    m = int(round(minutes))
    return m // 60, m % 60


def figures() -> dict[int, dict[str, float]]:
    """Exact values per card, read from the files social-cards.md cites."""
    t5 = sim_main.top5()
    with sim.runs_file("r6/l6/score/S6-L6.csv").open(encoding="utf-8", newline="") as fh:
        l6 = next(csv.DictReader(fh))
    s1 = pd.read_parquet(
        sim.runs_file("cba/CBA-S1-committed-programme/draws.parquet"), columns=["capex"]
    )
    s1q = np.percentile(s1["capex"].to_numpy(), [10, 50, 90])  # as common/figures.py s1_capex()
    cba = sim_main.cba_central()
    with sim.runs_file("study/rj/score/score.csv").open(encoding="utf-8", newline="") as fh:
        rj = [float(r["bcr_p50_medium"]) for r in csv.DictReader(fh)]
    with sim.runs_file("study/rj/times-s1/times.csv").open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    best = min(rows, key=lambda r: float(r["d2d_p50_min"]))
    air = json.loads(sim.runs_file("study/rj/times-s1/air.json").read_text(encoding="utf-8"))
    runs, usd, paid = cost_totals()
    return {
        1: {"new_route_km": float(l6["new_route_km"])},
        2: {
            "s1_p10": s1q[0],
            "s1_p50": s1q[1],
            "s1_p90": s1q[2],
            "l6_p10": float(l6["capex_p10"]),
            "l6_p50": float(l6["capex_p50"]),
            "l6_p90": float(l6["capex_p90"]),
            "l2_p10": float(t5["S6-L2"]["capex_p10"]),
            "l2_p50": float(t5["S6-L2"]["capex_p50"]),
            "l2_p90": float(t5["S6-L2"]["capex_p90"]),
        },
        3: {
            "l2": float(t5["S6-L2"]["bcr_p50_medium"]),
            "l1": float(t5["S6-L1"]["bcr_p50_medium"]),
            "s1": float(cba["bcr"]["P50"]),
            "rj_min": min(rj),
            "rj_max": max(rj),
            "l6": float(l6["bcr_p50_medium"]),
        },
        4: {
            "air_min": float(air["air"]["door_to_door_model_min"]),
            "rail_min": float(best["d2d_p50_min"]),
            "rail_speed": float(best["speed_class"]),
        },
        5: {"runs": runs, "usd": usd, "paid_usd": paid},
        6: {},
        # Card 7 repeats card 3's middle-case values for three of its options.
        7: {
            "l2": float(t5["S6-L2"]["bcr_p50_medium"]),
            "s1": float(cba["bcr"]["P50"]),
            "l6": float(l6["bcr_p50_medium"]),
        },
        # Card 8: S6-L6's new line length, cost to build (middle and likely range), riyals back
        # per riyal (middle case), number of corridors and of required cities.
        8: {
            "km": float(l6["new_route_km"]),
            "l6_p10": float(l6["capex_p10"]),
            "l6_p50": float(l6["capex_p50"]),
            "l6_p90": float(l6["capex_p90"]),
            "l6": float(l6["bcr_p50_medium"]),
            "corridors": float(l6["corridors"]),
            "cities": float(len(l6_required_cities())),
        },
    }


# Card 5 says "As of commit cf504dc": the cost log is append-only, and its last row at cf504dc is
# this run_id. Later rows (from SOCIAL_CARDS on) are not counted (FIX_SOCIAL_CARDS, 13 Nov 2026).
AS_OF_LAST_RUN = "main-FIX_EXPORT_NAMES-try1"


def cost_totals() -> tuple[float, float, float]:
    """Claude runs (rows whose label is not PAID), their list-price USD, and paid TTS USD, from
    docs/cost-log.csv up to AS_OF_LAST_RUN: the definitions of `common.cost_log summary` and
    docs/spend-summary.md."""
    with (REPO_ROOT / "docs/cost-log.csv").open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    ids = [r["run_id"] for r in rows]
    assert AS_OF_LAST_RUN in ids, f"{AS_OF_LAST_RUN} not in docs/cost-log.csv"
    rows = rows[: ids.index(AS_OF_LAST_RUN) + 1]
    col = "usd_list" if "usd_list" in rows[0] else next(k for k in rows[0] if "usd" in k.lower())
    claude = [r for r in rows if r["label"] != "PAID"]
    paid = [r for r in rows if r["label"] == "PAID"]

    def tot(rs: list[dict]) -> float:
        return sum(float(r[col]) for r in rs if r[col] not in ("", "—"))

    return float(len(claude)), tot(claude), tot(paid)


def _bn(v: float) -> str:
    """SAR million -> billions as the cards round them: whole billions from 10 bn, else 1 dp."""
    b = v / 1000
    return f"{b:,.0f}" if b >= 10 else f"{b:.1f}"


def expected(card: int, lang: str, F: dict[int, dict[str, float]]) -> set[str]:
    """Rounded figures that must appear on the card (both languages use Western digits)."""
    f = F[card]
    if card in (1, 6):
        return set()
    if card == 7:
        return {f"{f['l2']:.0f}", f"{f['s1']:.1f}", f"{f['l6']:.2f}"}
    if card == 8:
        costs = {_bn(f[k]) for k in ("l6_p10", "l6_p50", "l6_p90")}
        counts = {f"{f['corridors']:.0f}", f"{f['cities']:.0f}"}
        return {f"{f['km']:,.0f}", f"{f['l6']:.2f}"} | costs | counts
    if card == 2:
        return {_bn(f[k]) for k in f}
    if card == 3:
        lo, hi = round(f["rj_min"], 1), round(f["rj_max"], 1)
        assert lo == hi, "the five Riyadh–Jeddah sketches no longer share one rounded value"
        return {f"{f['l2']:.0f}", f"{f['l1']:.1f}", f"{f['s1']:.1f}", f"{lo:.1f}", f"{f['l6']:.2f}"}
    if card == 4:
        ah, am = _hm(f["air_min"])
        rh, rm = _hm(f["rail_min"])
        return {str(ah), str(am), str(rh), str(rm), f"{f['rail_speed']:.0f}"}
    return {f"{f['runs']:.0f}", f"{f['usd']:,.0f}", f"{f['paid_usd']:.0f}"}


ALLOWED_EXTRA = {3: {"1"}}  # the line at 1 on card 3


def check_numbers(row: dict[str, str], F: dict[int, dict[str, float]]) -> list[str]:
    """Problems: an expected figure missing, or a number on the card that traces to nothing."""
    card = int(row["card"])
    want = expected(card, row["lang"], F)
    text = body_text(row)
    text = re.sub(r"\b[0-9a-f]{7}\b", " ", text)  # the commit SHA on card 5 is not a figure
    got = set(NUMBER.findall(text))
    probs = [f"card {card} {row['lang']}: missing {w}" for w in sorted(want - got)]
    extra = got - want - ALLOWED_EXTRA.get(card, set())
    probs += [f"card {card} {row['lang']}: untraced number {x}" for x in sorted(extra)]
    return probs


# ---------------------------------------------------------------- drawing (film engine)


@contextmanager
def card_size() -> Iterator[None]:
    old = sim.W, sim.H
    sim.W, sim.H = CW, CH
    try:
        yield
    finally:
        sim.W, sim.H = old


def fit(pts: np.ndarray, box: tuple[float, float, float, float]) -> Cam:
    """Camera that puts world points `pts` inside the screen box (x0, y0, x1, y1)."""
    u0, v0 = pts.min(axis=0)
    u1, v1 = pts.max(axis=0)
    x0, y0, x1, y1 = box
    z = min((x1 - x0) / max(u1 - u0, 1e-6), (y1 - y0) / max(v1 - v0, 1e-6))
    uc, vc = (u0 + u1) / 2, (v0 + v1) / 2
    return Cam(uc / sim.K, vc, z, cx=(x0 + x1) / 2, cy=(y0 + y1) / 2)


def map_frame(cam: Cam, draw: Callable[[Canvas], None], dim: float = 1.0) -> np.ndarray:
    """One frame as film.sim.frame_at composes it: relief crop, vectors, glow (float RGB)."""
    with card_size():
        base = sim.build_base(sim.NATIONAL, sim.NATIONAL_RES)
        frame = np.asarray(base.crop(cam), dtype="float32") / 255.0 * dim
        c = Canvas(cam)
        draw(c)
        vec = c.done()
    v = np.asarray(vec, dtype="float32") / 255.0
    glow = (
        vec.resize((CW // 4, CH // 4), Image.Resampling.BILINEAR)
        .filter(ImageFilter.GaussianBlur(3.5))
        .resize((CW, CH), Image.Resampling.BILINEAR)
    )
    g = np.asarray(glow, dtype="float32") / 255.0
    a = v[..., 3:4]
    frame = frame * (1 - a) + v[..., :3] * a
    frame = frame + g[..., :3] * g[..., 3:4] * 0.9
    return np.clip(frame, 0, 1)


def l6_geometry() -> tuple[list[np.ndarray], list[np.ndarray]]:
    """S6-L6 line alignments (routed, never straight sketches) and its station points."""
    l6 = yaml.safe_load(sim.runs_file("r6/l6/L6.layout.yaml").read_text(encoding="utf-8"))
    ids = [c["id"] for c in l6.get("corridors") or []]
    lines = [g for cid in ids if not cid.startswith("S5-") for g in sim_main.corridor_geom(cid)[0]]
    pts = [p for cid in ids if cid.startswith("S5-") for p in sim_main.corridor_geom(cid)[1]]
    for cid in ids:
        fam = cid.split("-")[1]
        y = REPO_ROOT / f"cities/ksa/corridors/{fam}/{cid}.yaml"
        if y.exists():
            for st in yaml.safe_load(y.read_text(encoding="utf-8")).get("stations") or []:
                pts.append(sim.world(np.array([st["lon"], st["lat"]]))[0])
    return lines, pts


def l6_required_cities() -> list[str]:
    """The required cities of S6-L6 (A-r6-132), as listed in cities/ksa/assumptions/r6_l6.yaml."""
    y = yaml.safe_load(
        (REPO_ROOT / "cities/ksa/assumptions/r6_l6.yaml").read_text(encoding="utf-8")
    )
    return [c["city"] for c in y["required"]]


def l6_stations() -> dict[str, dict]:
    """Station id -> station record (name_en, name_ar, lat, lon) of the S6-L6 corridor YAMLs."""
    l6 = yaml.safe_load(sim.runs_file("r6/l6/L6.layout.yaml").read_text(encoding="utf-8"))
    out: dict[str, dict] = {}
    for cid in [c["id"] for c in l6.get("corridors") or []]:
        y = REPO_ROOT / f"cities/ksa/corridors/{cid.split('-')[1]}/{cid}.yaml"
        if y.exists():
            for st in yaml.safe_load(y.read_text(encoding="utf-8")).get("stations") or []:
                out.setdefault(st["id"], st)
    return out


def kingdom_cam(box: tuple[float, float, float, float]) -> Cam:
    D = sim.data()
    return fit(np.concatenate(D.border), box)


def network(c: Canvas, alpha: float = 1.0, l6: bool = True, width: float = 3.2) -> None:
    D = sim.data()
    sim.base_network(c, D, 0.0, alpha=alpha, trains=False)
    if l6:
        lines, _ = l6_geometry()
        for g in lines:
            c.line(g, PAL["hypothetical"], width, 0.95 * alpha, DASH_PX["hypothetical"])


def town(c: Canvas, name: str, r: float = 6.0) -> None:
    sim.town(c, sim.data(), name, r=r)


def place_xy(cam: Cam, name: str) -> tuple[float, float] | None:
    p = sim.data().places.get(name)
    if p is None:
        return None
    with card_size():
        x, y = cam.screen(np.asarray(p).reshape(1, 2))[0]
    return float(x), float(y)


# ---------------------------------------------------------------- text layer (Chrome)


def css() -> str:
    return f"""{R.font_css()}
html,body{{margin:0;width:{CW}px;height:{CH}px;overflow:hidden;background:#080D18}}
body{{font-family:'Noto Sans','Noto Naskh Arabic',sans-serif;color:#F2F2EC;letter-spacing:normal}}
[dir=rtl]{{font-family:'Noto Naskh Arabic','Noto Sans',serif}}
.bg{{position:absolute;left:0;top:0;width:{CW}px;height:{CH}px}}
.head{{position:absolute;left:64px;right:64px;top:56px;background:rgba(7,11,20,.80);
  padding:26px 34px 28px;border-radius:14px}}
.head[dir=ltr]{{border-left:6px solid #56CCF2}} .head[dir=rtl]{{border-right:6px solid #56CCF2}}
.t{{font-size:58px;font-weight:700;line-height:1.22;color:#FFF7E6}}
[dir=rtl] .t{{font-size:60px;line-height:1.4}}
.st{{font-size:34px;line-height:1.4;color:#E6E1D6;margin-top:10px}}
.panel{{position:absolute;left:64px;right:64px;background:rgba(7,11,20,.82);border-radius:14px;
  padding:28px 34px}}
.note{{font-size:30px;line-height:1.4;color:#D8D2C4}}
.leg{{position:absolute;font-size:24px;background:rgba(7,11,20,.78);padding:12px 18px;
  border-radius:10px;line-height:1.55}}
.leg div{{display:flex;align-items:center;gap:12px}}
.lbl{{position:absolute;font-size:27px;font-weight:700;color:#FFF3DA;white-space:nowrap;
  text-shadow:0 0 6px #000,0 0 3px #000,0 0 12px #000}}
.foot{{position:absolute;left:0;right:0;bottom:0;padding:34px 48px 22px;text-align:center;
  background:linear-gradient(to bottom,rgba(7,11,20,0),rgba(7,11,20,.92) 30%)}}
.f1{{font-size:26px;line-height:1.4;color:#F2F2EC;font-weight:700}}
.f0{{font-size:21px;line-height:1.4;color:#C9CED6;margin-bottom:6px}}
.f2{{font-size:14px;line-height:1.35;color:#A7AFBB;margin-top:8px}}
.row{{display:flex;align-items:baseline;gap:20px;margin:0 0 26px}}
.row:last-child{{margin-bottom:0}}
.row .k{{flex:1;font-size:36px;line-height:1.3;color:#E8ECF2}}
.row .v{{font-size:64px;font-weight:700;color:#FFF7E6;line-height:1.1}}
.row .r{{font-size:30px;color:#C9CED6;min-width:190px}}
.hdr{{display:flex;gap:20px;font-size:26px;color:#AEB6C2;margin:0 0 18px}}
.big{{font-size:120px;font-weight:700;line-height:1.05;color:#FFF7E6}}
"""


def page(body: str, lang: str) -> str:
    return (
        f'<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><style>{css()}'
        f"</style></head><body>{body}</body></html>"
    )


def chrome_png(html_text: str, png: Path) -> None:
    png.parent.mkdir(parents=True, exist_ok=True)
    src = png.with_suffix(".html")
    src.write_text(html_text, encoding="utf-8")
    args = [R.CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars"]
    args += ["--force-device-scale-factor=1", f"--window-size={CW},{CH}"]
    args += ["--allow-file-access-from-files", f"--screenshot={png}"]
    subprocess.run([*args, src.as_uri()], check=True, capture_output=True, timeout=120)


RANGE_RUN = re.compile(r"\d[\d,.]*(?:–\d[\d,.]*)?")


def esc(text: str, lang: str) -> str:
    """HTML text; in Arabic, Latin runs and number ranges (48–468) are LTR isolates, so a range
    keeps its low–high order inside a right-to-left line."""
    t = html.escape(text)
    if lang != "ar":
        return t
    t = R.ltr_isolate(t)
    return RANGE_RUN.sub(lambda m: f'<bdi dir="ltr">{m.group(0)}</bdi>', t)


def head_html(row: dict[str, str], lang: str) -> str:
    d = "rtl" if lang == "ar" else "ltr"
    st = f'<div class="st">{esc(row["subtitle"], lang)}</div>' if row["subtitle"] else ""
    return f'<div class="head" dir="{d}"><div class="t">{esc(row["title"], lang)}</div>{st}</div>'


def foot_html(lang: str, modelled: bool) -> str:
    d = "rtl" if lang == "ar" else "ltr"
    lab = f'<div class="f0" dir="{d}">{esc(R.FOOTER[lang][0], lang)}</div>' if modelled else ""
    return (
        f'<div class="foot">{lab}<div class="f1" dir="{d}">{esc(FOOTER[lang], lang)}</div>'
        f'<div class="f2" dir="ltr">{html.escape(CREDIT)}</div></div>'
    )


def legend_html(lang: str, top: int, side: str = "") -> str:
    rows = []
    for lay, label in R.LEGEND[lang]:
        dash = {"committed": "16 9", "hypothetical": "3 8"}.get(lay, "")
        svg = (
            f'<svg width="64" height="14"><line x1="3" y1="7" x2="61" y2="7" '
            f'stroke="{sim.LEGEND_COL[lay]}" stroke-width="6" stroke-linecap="round"'
            + (f' stroke-dasharray="{dash}"' if dash else "")
            + "/></svg>"
        )
        rows.append(f"<div>{svg}<span>{html.escape(label)}</span></div>")
    d = "rtl" if lang == "ar" else "ltr"
    side = side or ("left:64px" if lang == "ar" else "right:64px")
    return f'<div class="leg" dir="{d}" style="{side};top:{top}px">{"".join(rows)}</div>'


def labels_html(cam: Cam, names: list[str], lang: str, side: dict[str, str]) -> str:
    out = []
    for n in names:
        xy = place_xy(cam, n)
        if xy is None:
            continue
        x, y = xy
        t = sim.AR_NAMES.get(n, n) if lang == "ar" else n
        d = "rtl" if lang == "ar" else "ltr"
        left = side.get(n, "r") == "l"
        pos = f"right:{CW - x + 14:.0f}px" if left else f"left:{x + 14:.0f}px"
        out.append(
            f'<div class="lbl" dir="{d}" style="{pos};top:{y - 19:.0f}px">{html.escape(t)}</div>'
        )
    return "".join(out)


def compose(bg: np.ndarray, body: str, lang: str, name: str) -> Path:
    WORK.mkdir(parents=True, exist_ok=True)
    bg_png = WORK / f"{name}-bg.png"
    Image.fromarray((bg * 255 + 0.5).astype("uint8"), "RGB").save(bg_png)
    full = f'<img class="bg" src="{bg_png.as_uri()}">' + body
    staged = WORK / f"{name}.png"  # Chrome writes its .html beside the PNG: keep it in WORK
    chrome_png(page(full, lang), staged)
    OUT.mkdir(parents=True, exist_ok=True)
    png = OUT / f"{name}.png"
    shutil.copyfile(staged, png)
    return png


# ---------------------------------------------------------------- the five cards


SIDE5 = {"Tabuk": "l", "Abha": "l", "Khamis Mushait": "r", "Najran": "r", "Jazan": "l"}


def card1(lang: str, F: dict) -> tuple[np.ndarray, str]:
    """The S6-L6 connected network over today's and the committed lines."""
    row = card_row(1, lang)
    cam = kingdom_cam((40, 360, 1040, 1110))
    _, st = l6_geometry()

    def draw(c: Canvas) -> None:
        network(c, 1.0, l6=True, width=3.6)
        for p in st:
            c.dot(p, PAL["white"], 3.2, 0.9)
        for n in ("Tabuk", "Abha", "Khamis Mushait", "Najran", "Jazan", "Riyadh", "Jeddah"):
            town(c, n, r=7 if n in SIDE5 else 5)

    bg = map_frame(cam, draw)
    d = "rtl" if lang == "ar" else "ltr"
    names = ["Tabuk", "Abha", "Khamis Mushait", "Najran", "Jazan", "Riyadh", "Jeddah"]
    body = head_html(row, lang)
    body += legend_html(lang, 340, "right:64px")  # NE corner: no line under it
    body += labels_html(cam, names, lang, SIDE5 | {"Riyadh": "r", "Jeddah": "l"})
    side = "right:64px;left:auto"  # over the Empty Quarter's southern edge, clear of the lines
    body += (
        f'<div class="panel note" dir="{d}" style="top:1040px;{side};width:300px;'
        f'padding:16px 24px">{esc(row["note"], lang)}</div>'
    )
    return bg, body + foot_html(lang, True)


def card2(lang: str, F: dict) -> tuple[np.ndarray, str]:
    """Cost to build: middle and likely range (P10–P90 columns, no percentile labels)."""
    row = card_row(2, lang)
    cam = kingdom_cam((60, 300, 1020, 1100))
    bg = map_frame(cam, lambda c: network(c, 0.55, l6=True, width=2.6), dim=0.55)
    d = "rtl" if lang == "ar" else "ltr"
    hdr = [f.strip() for f in row["chart_label"].split(" | ")]
    rows = "".join(
        f'<div class="row"><div class="k">{esc(k, lang)}</div>'
        f'<div class="v">{esc(v, lang)}</div><div class="r">{esc(r, lang)}</div></div>'
        for k, v, r in items(row)
    )
    body = head_html(row, lang)
    body += (
        f'<div class="panel" dir="{d}" style="top:330px">'
        f'<div class="hdr"><div style="flex:1"></div><div>{esc(hdr[0], lang)}</div>'
        f'<div style="min-width:190px">{esc(hdr[1], lang)}</div></div>{rows}</div>'
        f'<div class="panel note" dir="{d}" style="top:900px">{esc(row["note"], lang)}</div>'
    )
    return bg, body + foot_html(lang, True)


def card3(lang: str, F: dict) -> tuple[np.ndarray, str]:
    """Riyals back per riyal spent (middle case): bars from the exact values, a line at 1."""
    row = card_row(3, lang)
    f = F[3]
    vals = [f["l2"], f["l1"], f["s1"], (f["rj_min"] + f["rj_max"]) / 2, f["l6"]]
    cam = kingdom_cam((60, 300, 1020, 1100))
    bg = map_frame(cam, lambda c: network(c, 0.45, l6=True, width=2.4), dim=0.45)
    d = "rtl" if lang == "ar" else "ltr"
    vmax = 6.5
    bw = 560  # bar track width (px); 1 sits at bw / vmax
    one = bw / vmax
    start = "right" if lang == "ar" else "left"
    end = "left" if lang == "ar" else "right"
    bars = []
    for (label, txt), v in zip(items(row), vals, strict=True):
        col = "#7ED99A" if v >= 1 else "#FF786C"
        w = max(bw * v / vmax, 4)
        bars.append(
            f'<div style="margin:0 0 26px"><div style="font-size:32px;color:#E8ECF2;'
            f'margin-bottom:6px">{esc(label, lang)}</div>'
            f'<div style="position:relative;height:50px">'
            f'<div style="position:absolute;{start}:0;top:6px;width:{w:.1f}px;height:38px;'
            f'background:{col};border-radius:4px"></div>'
            f'<div style="position:absolute;{start}:{one - 2:.1f}px;top:-4px;height:58px;'
            'border-left:4px solid #F2F2EC"></div>'
            f'<div style="position:absolute;{end}:0;top:-6px;font-size:46px;'
            f'font-weight:700;color:#FFF7E6">{esc(txt, lang)}</div></div></div>'
        )
    body = head_html(row, lang)
    body += (
        f'<div class="panel" dir="{d}" style="top:300px;padding-bottom:28px">'
        f'<div style="position:relative">{"".join(bars)}</div>'
        f'<div style="font-size:30px;font-weight:700;color:#FFF7E6;margin-top:6px">'
        f"{esc(row['chart_label'], lang)}</div></div>"
    )
    return bg, body + foot_html(lang, True)


def card4(lang: str, F: dict) -> tuple[np.ndarray, str]:
    """Riyadh–Jeddah door to door: the modelled flight against the fastest modelled train."""
    row = card_row(4, lang)
    D = sim.data()
    _, route = sim.air_over_rail()
    rj = sorted(sim.runs_file("study/rj/align-s1").glob("RJ-*/alignment.geojson"))
    rj_lines = [x for p in rj for x in sim.load_lines(p) if len(x) > 2]  # no 2-point sketches
    best = max(
        sim.load_lines(sim.runs_file(f"study/rj/align-s1/{route}/alignment.geojson")), key=len
    )
    air = sim.arc(D.places["Riyadh"], D.places["Jeddah"], lift=-0.20)
    pts = np.vstack([D.places["Riyadh"], D.places["Jeddah"]] + [best])
    cam = fit(pts, (150, 620, 930, 1000))

    def draw(c: Canvas) -> None:
        sim.base_network(c, D, 0.0, alpha=0.6, trains=False)
        for g in rj_lines:
            c.line(g, PAL["hypothetical"], 2.0, 0.35, dash=DASH_PX["hypothetical"])
        c.line(best, PAL["hypothetical"], 4.2, 0.95, dash=DASH_PX["hypothetical"])
        c.line(air, PAL["air"], 3.0, 0.9, dash=(10, 8))
        for n in ("Riyadh", "Jeddah"):
            town(c, n, r=8)

    bg = map_frame(cam, draw)
    d = "rtl" if lang == "ar" else "ltr"
    (k1, v1), (k2, v2) = items(row)
    rows = (
        f'<div class="row"><div class="k" style="color:#F48FB1">{esc(k1, lang)}</div>'
        f'<div class="v">{esc(v1, lang)}</div></div>'
        f'<div class="row"><div class="k" style="color:#C792FF">{esc(k2, lang)}</div>'
        f'<div class="v">{esc(v2, lang)}</div></div>'
    )
    body = head_html(row, lang)
    body += f'<div class="panel" dir="{d}" style="top:300px">{rows}</div>'
    body += labels_html(cam, ["Riyadh", "Jeddah"], lang, {"Riyadh": "r", "Jeddah": "l"})
    body += f'<div class="panel note" dir="{d}" style="top:1010px">{esc(row["note"], lang)}</div>'
    return bg, body + foot_html(lang, True)


def card5(lang: str, F: dict) -> tuple[np.ndarray, str]:
    """How it was made: Claude runs and list-price USD, paid voices, open code."""
    row = card_row(5, lang)
    cam = kingdom_cam((60, 300, 1020, 1100))
    bg = map_frame(cam, lambda c: network(c, 0.5, l6=False), dim=0.45)
    d = "rtl" if lang == "ar" else "ltr"
    rows = "".join(
        f'<div class="row"><div class="v" style="min-width:330px">{esc(v, lang)}</div>'
        f'<div class="k">{esc(k, lang)}</div></div>'
        for k, v in items(row)
    )
    body = head_html(row, lang)
    body += f'<div class="panel" dir="{d}" style="top:300px">{rows}</div>'
    body += f'<div class="panel note" dir="{d}" style="top:960px">{esc(row["note"], lang)}</div>'
    return bg, body + foot_html(lang, False)


def card6(lang: str, F: dict) -> tuple[np.ndarray, str]:
    """How the study worked: five steps, top to bottom, joined by arrows (no figures)."""
    row = card_row(6, lang)
    cam = kingdom_cam((60, 300, 1020, 1100))
    bg = map_frame(cam, lambda c: network(c, 0.5, l6=True, width=2.4), dim=0.45)
    d = "rtl" if lang == "ar" else "ltr"
    cols = ("#56CCF2", "#7ED99A", "#F2C94C", "#C792FF", "#FFF7E6")
    steps = []
    for i, ((label,), col) in enumerate(zip(items(row), cols, strict=True)):
        if i:
            steps.append(
                '<div style="font-size:40px;line-height:1;color:#AEB6C2;margin:6px 0 6px;'
                'padding-inline-start:14px">↓</div>'
            )
        steps.append(
            f'<div style="display:flex;align-items:center;gap:24px">'
            f'<div style="flex:none;width:26px;height:26px;border-radius:50%;background:{col}">'
            f'</div><div style="font-size:46px;font-weight:700;line-height:1.25;'
            f'color:#FFF7E6">{esc(label, lang)}</div></div>'
        )
    body = head_html(row, lang)
    body += f'<div class="panel" dir="{d}" style="top:300px">{"".join(steps)}</div>'
    return bg, body + foot_html(lang, True)


def card7(lang: str, F: dict) -> tuple[np.ndarray, str]:
    """Main findings: riyals back per riyal for three options (middle case) and Riyadh–Jeddah."""
    row = card_row(7, lang)
    f = F[7]
    vals = [f["l2"], f["s1"], f["l6"]]
    cam = kingdom_cam((60, 300, 1020, 1100))
    bg = map_frame(cam, lambda c: network(c, 0.45, l6=True, width=2.4), dim=0.45)
    d = "rtl" if lang == "ar" else "ltr"
    rows = "".join(
        f'<div class="row"><div class="v" style="min-width:200px;color:'
        f'{"#7ED99A" if v >= 1 else "#FF786C"}">{esc(txt, lang)}</div>'
        f'<div class="k">{esc(label, lang)}</div></div>'
        for (label, txt), v in zip(items(row), vals, strict=True)
    )
    body = head_html(row, lang)
    body += (
        f'<div class="panel" dir="{d}" style="top:300px">'
        f'<div class="hdr">{esc(row["chart_label"], lang)}</div>{rows}</div>'
        f'<div class="panel note" dir="{d}" style="top:860px">{esc(row["note"], lang)}</div>'
    )
    return bg, body + foot_html(lang, True)


# Card 8 city labels: (English, side, dy) for the film's places (Arabic from sim.AR_NAMES), and
# (station id in the S6-L6 corridor YAMLs, English, side, dy) for towns the film has no place for
# (Arabic from the YAML's name_ar). Side "l" puts the label left of the dot; dy nudges it (px).
PLACES8 = [
    ("Tabuk", "l", 0),
    ("Madinah", "r", 0),
    ("Jeddah", "l", 0),
    ("Taif", "r", 0),
    ("Riyadh", "r", 0),
    ("Al-Kharj", "r", 0),
    ("Dammam", "r", 12),
    ("Al Jubayl", "r", -14),
    ("Abha", "l", 0),
    ("Najran", "r", 0),
    ("Jazan", "l", 0),
]
TOWNS8 = [
    ("sakaka", "Sakaka", "l", 0),
    ("arar", "Arar", "r", 0),
    ("hafar-al-batin", "Hafar Al-Batin", "l", 0),
    ("yanbu", "Yanbu", "l", 0),
    ("bisha", "Bisha", "r", 0),
]


def card8(lang: str, F: dict) -> tuple[np.ndarray, str]:
    """Connecting every region: the 16 S6-L6 corridors with city names, plus three figures."""
    row = card_row(8, lang)
    cam = kingdom_cam((80, 280, 1000, 905))
    _, st = l6_geometry()
    stations = l6_stations()
    D = sim.data()
    marks = [(n, sim.AR_NAMES.get(n, n), D.places[n], side, dy) for n, side, dy in PLACES8]
    for sid, en, side, dy in TOWNS8:
        s = stations[sid]
        p = sim.world(np.array([s["lon"], s["lat"]]))[0]
        marks.append((en, s["name_ar"], p, side, dy))

    def draw(c: Canvas) -> None:
        network(c, 1.0, l6=True, width=3.6)
        for p in st:
            c.dot(p, PAL["white"], 3.0, 0.85)
        for n, _, _ in PLACES8:
            town(c, n, r=6)
        for _, _, p, _, _ in marks[len(PLACES8) :]:
            c.dot(p, PAL["white"], 6.0, 1.0)

    bg = map_frame(cam, draw)
    d = "rtl" if lang == "ar" else "ltr"
    body = head_html(row, lang)
    body += legend_html(lang, 290, "right:40px")  # NE corner (Gulf): no line under it
    for en, ar, p, side, dy in marks:
        with card_size():
            x, y = cam.screen(np.asarray(p).reshape(1, 2))[0]
        pos = f"right:{CW - x + 14:.0f}px" if side == "l" else f"left:{x + 14:.0f}px"
        t = ar if lang == "ar" else en
        top = y - 19 + dy
        body += f'<div class="lbl" dir="{d}" style="{pos};top:{top:.0f}px">{html.escape(t)}</div>'
    # Each cell: the value, its label, then the likely range (cost only).
    cells = "".join(
        f'<div style="flex:1;text-align:center"><div style="font-size:54px;font-weight:700;'
        f'color:#FFF7E6;line-height:1.15">{esc(it[1], lang)}</div>'
        f'<div style="font-size:27px;color:#E8ECF2;line-height:1.3;margin-top:4px">'
        f"{esc(it[0], lang)}</div>"
        + (
            f'<div style="font-size:25px;color:#C9CED6;margin-top:2px">{esc(it[2], lang)}</div>'
            if len(it) > 2
            else ""
        )
        + "</div>"
        for it in items(row)
    )
    body += (
        f'<div class="panel" dir="{d}" style="top:925px;padding:16px 20px;display:flex;'
        f'gap:16px;align-items:flex-start">{cells}</div>'
    )
    return bg, body + foot_html(lang, True)


CARDS = {1: card1, 2: card2, 3: card3, 4: card4, 5: card5, 6: card6, 7: card7, 8: card8}
NAMES = {
    1: "network",
    2: "cost",
    3: "payback",
    4: "riyadh-jeddah",
    5: "how-made",
    6: "method",
    7: "findings",
    8: "connected",
}


def card_name(card: int, lang: str) -> str:
    return f"card{card}-{NAMES[card]}-{lang}"


@app.command()
def render(
    card: int = typer.Option(0, "--card", help="1-8; 0 = all"),
    lang: str = typer.Option("", "--lang", help="en or ar; empty = both"),
) -> None:
    """Render the cards to renders/out/social/cards/ (fails if a figure does not trace)."""
    F = figures()
    probs = [p for r in load_cards() for p in check_numbers(r, F)]
    if probs:
        raise SystemExit("figures do not trace:\n" + "\n".join(probs))
    for k in [card] if card else sorted(CARDS):
        for lg in [lang] if lang else LANGS:
            bg, body = CARDS[k](lg, F)
            png = compose(bg, body, lg, card_name(k, lg))
            typer.echo(f"film.cards {card_name(k, lg)}: {png} {Image.open(png).size}")


@app.command()
def check() -> None:
    """Jargon, word count and figures of every card row."""
    probs = []
    rows = load_cards()
    for r in rows:
        if hits := jargon_hits(all_text(r)):
            probs.append(f"card {r['card']} {r['lang']}: jargon {hits}")
        if (n := word_count(r)) > MAX_WORDS:
            probs.append(f"card {r['card']} {r['lang']}: {n} words")
    F = figures()
    probs += [p for r in rows for p in check_numbers(r, F)]
    for r in rows:
        typer.echo(f"card {r['card']} {r['lang']}: {word_count(r)} words")
    if probs:
        raise SystemExit("\n".join(probs))
    typer.echo("film.cards check: ok")


@app.command()
def trace() -> None:
    """Print the exact values and the rounded card values (for social-cards.md)."""
    F = figures()
    for k, f in F.items():
        for name, v in f.items():
            typer.echo(f"card {k}\t{name}\t{v!r}")
        typer.echo(f"card {k}\texpected\t{sorted(expected(k, 'en', F))}")


if __name__ == "__main__":
    app()
