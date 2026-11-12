"""Report and deck figures rendered from run outputs and registers (R8 tasks 1 and 4).

Every figure is drawn from files under `runs/`, `cities/ksa/` and `docs/` (no hand-drawn
figure, no result number typed into this module). Each figure carries the synthetic-demand
label, the judge id and seed, its source run ids and, where it shows a length, cost, travel time
or ridership, `common.labels.ALIGNMENT_LIMITATION`. Maps carry the OSM credit and a legend with
every rail layer. Output is deterministic: fixed seed, `svg.hashsalt`, no dates in metadata.

CLI:
  uv run python -m common.figures build --out docs/report/figures/ --deck docs/deck-figures/
  uv run python -m common.figures build --out docs/report/figures/ \
      --handoff logs/r8-figures-handoff.md
  uv run python -m common.figures list
"""

from __future__ import annotations

import csv
import glob
import json
import math
import textwrap
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")

import geopandas as gpd  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import typer  # noqa: E402
import yaml  # noqa: E402
from matplotlib import font_manager  # noqa: E402
from matplotlib.figure import Figure  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

from common import REPO_ROOT  # noqa: E402
from common.cli import make_app  # noqa: E402
from common.labels import ALIGNMENT_LIMITATION, LABEL  # noqa: E402

# ------------------------------------------------------------------ paths (repo-relative ids)
RUNS = Path("runs")
TOP5 = RUNS / "r6/top5/top5.csv"
TOP5_DIR = RUNS / "r6/top5"
JUDGE_META = RUNS / "r6/top5/L1/meta.json"
PARETO = RUNS / "r6/pareto_front.csv"
# S6-L6 (R8_L6_PANEL): a comparison layout from the connectivity search, scored by the full judge v3
# outside the top-5 directory (never read from or written to runs/r6/top5/).
L6_DIR = RUNS / "r6/l6"
L6_CSV = L6_DIR / "score/S6-L6.csv"
L6_META = L6_DIR / "score/meta.json"
L6_SEARCH = L6_DIR / "search.json"
L6_MAP = Path(
    "docs/report/figures/s6-l6-connected-map.png"
)  # optimise.connect map (S6_L6_CONNECTED)
CBA_DIR = RUNS / "cba"
S1_CASE = "CBA-S1-committed-programme"
FISCAL = RUNS / "r7/fiscal/fiscal.json"
VFM = RUNS / "r7/vfm/vfm.json"
LONGLIST_COUNTS = RUNS / "r2/long-list/counts.json"
SCORE_SUMMARY = RUNS / "r2/score/summary.json"
SCORES = RUNS / "r2/score/scores.parquet"
LINES = Path("cities/ksa/lines/geojson")
STATIONS = Path("cities/ksa/lines/stations.geojson")
ZONES = Path("cities/ksa/zones")
CORRIDORS = Path("cities/ksa/corridors")
ALIGNMENTS = Path("cities/ksa/alignments")  # frozen weights v1 only (never alignments-v2)
CANDIDATES = Path("cities/ksa/candidates.parquet")
BENCH_METRICS = Path("cities/ksa/benchmarks/metrics.csv")
ACCESS = RUNS / "access"
COVERAGE_MD = Path("docs/coverage.md")

OSM_CREDIT = "© OpenStreetMap contributors (ODbL)"
SCREENING_LABEL = "screening input, not a forecast"
FONT_DIR = Path(__file__).resolve().parent / "fonts"
LATIN_FONT = "Noto Sans"
ARABIC_FONT = "Noto Naskh Arabic"

# Decision framing (Tariq, R7 checkpoint, 4 Nov 2026; prompts/R8.md): words, not numbers.
CP7 = ["S6-L2", "S6-L1", "S6-L3"]
ILLUSTRATION = ["S6-L4", "S6-L5"]
ROLE = {
    "S6-L2": "central case",
    "S6-L1": "upside case: carries the Al-Kharj spur's P90 cost risk",
    "S6-L3": "reach alternative",
}
TRADEOFF_CAPTION = "S6-L4, S6-L5: trade-off illustration only: no recommendation"
COMPARISON = ["S6-L6"]
COMPARISON_ROLE = "comparison layout, not the recommended programme"
COMPARISON_CAPTION = (
    "S6-L6: " + COMPARISON_ROLE + " (connectivity comparison, not a search-front point)"
)
ACCESS_SITES = (
    "The judge still uses the access-model site overrides (A-r4-acc-004: Landbridge Jeddah with "
    "HHR Al-Sulaimaniyah, GCC Dammam with SAR Dammam) for door-to-door times; those are not "
    "rail-graph interchanges. The access model is unchanged."
)
COLOR = {
    "S1": "#6b6b6b",
    "S6-L2": "#1f5fa8",
    "S6-L1": "#c76a12",
    "S6-L3": "#6a4c93",
    "S6-L4": "#9a9a9a",
    "S6-L5": "#9a9a9a",
    "S6-L6": "#1a7f64",
}
LAYER_STYLE = {
    "existing": {"color": "#1b1b1b", "lw": 1.6, "ls": "-"},
    "committed": {"color": "#c0392b", "lw": 1.5, "ls": "--"},
    "historical": {"color": "#8d6e63", "lw": 1.1, "ls": ":"},
}
LAYER_NAME = {
    "existing": "existing",
    "committed": "committed / under procurement (announced/planned)",
    "historical": "historical (abandoned)",
    "hypothetical": "hypothetical (ours)",
}
FAMILY_NAME = {
    "trunk_gap": "S2 trunk gaps",
    "branch_spur": "S3 branches and spurs",
    "commuter_belt": "S4 commuter belts",
    "station_addition": "S5 station additions",
}
POP = {"un_wpp_low": "low", "un_wpp_medium": "medium", "un_wpp_high": "high"}

REPORT_SIZE = (11.0, 7.2)
DECK_SIZE = (13.333, 7.5)  # 16:9
REPORT_DPI = 200
DECK_DPI = 150


# ------------------------------------------------------------------ helpers
def _p(path: Path | str) -> Path:
    return REPO_ROOT / path


def load_json(path: Path | str) -> Any:
    return json.loads(_p(path).read_text(encoding="utf-8"))


def load_yaml(path: Path | str) -> Any:
    return yaml.safe_load(_p(path).read_text(encoding="utf-8"))


def fmt(x: float, digits: int = 0) -> str:
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "n/a"
    if isinstance(x, float) and math.isinf(x):
        return "unbounded" if x > 0 else "-unbounded"
    return f"{x:,.{digits}f}"


def rng3(p10: float, p50: float, p90: float, digits: int = 0) -> str:
    return f"{fmt(p10, digits)} / {fmt(p50, digits)} / {fmt(p90, digits)}"


def register_fonts() -> None:
    for ttf in sorted(FONT_DIR.glob("*.ttf")):
        font_manager.fontManager.addfont(str(ttf))
    plt.rcParams.update(
        {
            "font.family": [LATIN_FONT, ARABIC_FONT],
            "svg.hashsalt": "ksa-railtwin-r8-figures",
            "svg.fonttype": "path",
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.titlesize": 10,
            "axes.labelsize": 9,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "legend.fontsize": 7.5,
            "legend.frameon": False,
            "path.simplify": True,
        }
    )


def judge_info() -> dict[str, Any]:
    m = load_json(JUDGE_META)
    return {"sha": m["judge_sha256"], "seed": m["seed"], "name": m["judge"]}


def judge_text() -> str:
    j = judge_info()
    return f"judge v3 {j['sha'][:8]}… · seed {j['seed']}"


def _meta(path: Path | str) -> dict[str, Any]:
    return load_json(path)


def provenance_text(key: str) -> str:
    """One provenance phrase per run family, read from the runs' meta.json (seed, code version)."""
    if key == "judge_v3":
        return judge_text()
    if key == "r5_cba":
        m = _meta(CBA_DIR / S1_CASE / "meta.json")
        return f"R5 CBA runs/cba (economics.cba, code {m['code_version']}) · seed {m['seed']}"
    if key == "r6_front":
        return (
            "R6 full-judge front runs/r6/pareto_front.csv (judge v2-p5b, reproduced exactly by v3: "
            "docs/r6/judge-v3-backtest.md)"
        )
    if key == "r7_funding":
        m = _meta(FISCAL.parent / "meta.json")
        sha = judge_info()["sha"][:8]
        return f"R7 funding engine runs/r7 on judge v3 {sha}… scores · seed {m['seed']}"
    if key == "r2_screening":
        m = _meta(SCORE_SUMMARY.parent / "meta.json")
        return f"R2 screening runs/r2 (code {m['code_version']}) · seed {m['seed']}"
    if key == "r4_access":
        m = _meta(ACCESS / "S1" / "meta.json")
        return f"R4/R5 access runs/access (code {m['code_version']}) · seed {m['seed']}"
    if key == "l6_score":
        m = _meta(L6_META)
        return (
            f"S6-L6 full-judge score runs/r6/l6/score (judge v3 {m['judge_sha256'][:8]}… · seed "
            f"{m['seed']}, layout {m['layout_hash']})"
        )
    if key == "l6_search":
        m = _meta(L6_DIR / "meta.json")
        return (
            f"S6-L6 connecting-set search runs/r6/l6/search.json (optimise.connect, code "
            f"{m['code_version']}) · seed {m['seed']}"
        )
    if key == "bench":
        return "benchmark register cities/ksa/benchmarks (R1b)"
    if key == "registers":
        return "registers cities/ksa (lines, zones, corridors)"
    raise KeyError(key)


def provenance(spec: Any) -> str:
    return " · ".join(provenance_text(k) for k in spec.prov)


def top5() -> pd.DataFrame:
    return pd.read_csv(_p(TOP5)).set_index("layout")


def l6() -> pd.Series:
    """The S6-L6 scorecard row (the top5.csv columns) from runs/r6/l6/score/S6-L6.csv."""
    return pd.read_csv(_p(L6_CSV)).set_index("layout").loc["S6-L6"]


def cba_results(case: str) -> dict[str, Any]:
    return load_json(CBA_DIR / case / "results.json")


def cba_row(
    res: dict[str, Any], pop: str = "un_wpp_medium", horizon: int = 60, rate: str | None = None
) -> dict[str, Any]:
    rate = rate or res["central_rate_case"]
    for r in res["results"]:
        if r["population"] == pop and r["horizon"] == horizon and r["rate_case"] == rate:
            return r
    raise KeyError((res["case"], pop, horizon, rate))


def corridor_yaml(cid: str) -> dict[str, Any]:
    hits = sorted(glob.glob(str(_p(CORRIDORS) / "*" / f"{cid}.yaml")))
    if not hits:
        raise FileNotFoundError(cid)
    return yaml.safe_load(Path(hits[0]).read_text(encoding="utf-8"))


def layout_corridors(layout: str) -> list[dict[str, Any]]:
    """Corridors and phases of a CP7 layout from its frozen layout YAML (S6-L1 -> L1.layout)."""
    short = layout.replace("S6-", "")
    return load_yaml(TOP5_DIR / f"{short}.layout.yaml")["corridors"]


def short_id(cid: str) -> str:
    for fam in FAMILY_NAME:
        cid = cid.replace(f"-{fam}-", " ")
    return cid


@dataclass
class Ctx:
    deck: bool
    seed: int
    sources: list[str] = field(default_factory=list)
    numbers: list[tuple[str, str]] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    unit: str = ""

    def src(self, *ids: Path | str) -> None:
        for i in ids:
            s = str(i)
            if s not in self.sources:
                self.sources.append(s)

    def num(self, key: str, value: str) -> None:
        self.numbers.append((key, value))


@dataclass
class Spec:
    stem: str
    title_en: str
    title_ar: str
    draw: Callable[[Figure, list[float], Ctx], None]
    modelled: bool = True
    quantity: bool = True
    is_map: bool = False
    screening: bool = False
    caption: str = ""
    prov: tuple[str, ...] = ("judge_v3",)


# ------------------------------------------------------------------ layout of one figure
MIN_FONT = 6.2


def _width(fig: Figure, t: Any) -> float:
    return t.get_window_extent(renderer=fig.canvas.get_renderer()).width / (
        fig.dpi * fig.get_figwidth()
    )


def _fit_text(
    fig: Figure, x: float, y: float, s: str, size: float, wrap: bool = True, **kw: Any
) -> Any:
    """Place a line of text and shrink it until it fits inside the canvas (glyph hinting makes
    width non-linear in size, so iterate). Below MIN_FONT the text is wrapped onto two lines."""
    t = fig.text(x, y, s, fontsize=size, **kw)
    room = 0.985 - x
    for _ in range(8):
        w = _width(fig, t)
        if w <= room:
            return t
        new = t.get_fontsize() * room / w * 0.995
        if new < MIN_FONT and wrap:
            break
        t.set_fontsize(new)
    if _width(fig, t) <= room:
        return t
    half = len(s) // 2
    cut = s.rfind(" ", 0, half + 20)
    t.set_text(s[:cut] + "\n" + s[cut + 1 :] if cut > 0 else s)
    t.set_fontsize(size)
    for _ in range(8):
        w = _width(fig, t)
        if w <= room:
            break
        t.set_fontsize(t.get_fontsize() * room / w * 0.995)
    return t


def _note(fig: Figure, rect: list[float], text: str, fontsize: float = 7.5, **kw: Any) -> None:
    """One explanatory line between the title and the plot area (fitted to the canvas width)."""
    _fit_text(fig, rect[0], rect[1] + rect[3] + 0.045, text, fontsize, **kw)


def clipped_texts(fig: Figure) -> list[str]:
    """Every drawn text (figure texts, axes texts and titles, axis labels, tick labels inside the
    view, legend texts) that extends beyond the canvas. The build refuses to save such a figure."""
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    w, h = fig.dpi * fig.get_figwidth(), fig.dpi * fig.get_figheight()
    texts: list[Any] = list(fig.texts)
    for lg in fig.legends:
        texts += list(lg.get_texts()) + [lg.get_title()]
    for ax in fig.axes:
        texts += list(ax.texts) + [ax.title, ax._left_title, ax._right_title]
        if ax.get_legend() is not None:
            texts += list(ax.get_legend().get_texts()) + [ax.get_legend().get_title()]
        if not ax.axison:
            continue
        texts += [ax.xaxis.label, ax.yaxis.label]
        for axis, lim in ((ax.xaxis, ax.get_xlim()), (ax.yaxis, ax.get_ylim())):
            lo, hi = min(lim), max(lim)
            for tick in axis.get_major_ticks() + axis.get_minor_ticks():
                if lo - 1e-9 <= tick.get_loc() <= hi + 1e-9 and tick.label1.get_visible():
                    texts.append(tick.label1)
    out = []
    for t in texts:
        if not t.get_visible() or not t.get_text().strip():
            continue
        e = t.get_window_extent(renderer=r)
        if e.x0 < -0.5 or e.y0 < -0.5 or e.x1 > w + 0.5 or e.y1 > h + 0.5:
            out.append(t.get_text()[:80])
    return out


def wrap_role(lay: str, width: int = 26) -> str:
    return lay + "\n" + "\n".join(textwrap.wrap(ROLE[lay], width))


def footer_lines(spec: Spec, ctx: Ctx) -> list[str]:
    lines: list[str] = []
    if ctx.unit:
        lines.append(ctx.unit)
    if spec.screening:
        lines.append(f"{SCREENING_LABEL}; {LABEL}")
    else:
        lines.append(LABEL)
    srcs = "source: " + "; ".join(ctx.sources)
    wrap = 175 if ctx.deck else 150
    first, *rest = textwrap.wrap(f"{provenance(spec)} · {srcs}", wrap)
    lines.append(first)
    lines.extend(rest)
    if spec.quantity:
        lines.append(ALIGNMENT_LIMITATION)
    return lines


def render(spec: Spec, deck: bool, seed: int) -> tuple[Figure, Ctx, list[str]]:
    size = DECK_SIZE if deck else REPORT_SIZE
    fig = plt.figure(figsize=size, dpi=DECK_DPI if deck else REPORT_DPI)
    ctx = Ctx(deck=deck, seed=seed)
    top = 0.82 if deck else 0.9
    n_footer = 6
    bottom = 0.035 + 0.021 * n_footer
    rect = [0.07, bottom + 0.05, 0.9, top - bottom - 0.08]
    spec.draw(fig, rect, ctx)
    fig.text(0.02, 0.965, spec.title_en, fontsize=15 if deck else 13, weight="bold", va="top")
    if deck:
        fig.text(
            0.98,
            0.915,
            spec.title_ar,
            fontsize=15,
            ha="right",
            va="top",
            fontfamily=[ARABIC_FONT, LATIN_FONT],
        )
    lines = footer_lines(spec, ctx)
    y = 0.012 + 0.019 * (len(lines) - 1)
    for i, line in enumerate(lines):
        color = "#222222" if line == LABEL or line.startswith(SCREENING_LABEL) else "#444444"
        weight = "bold" if i == (1 if ctx.unit else 0) else "normal"
        _fit_text(fig, 0.02, y, line, 7.2, wrap=False, color=color, weight=weight, va="bottom")
        y -= 0.019
    bad = clipped_texts(fig)
    if bad:
        raise ValueError(f"{spec.stem} ({'deck' if deck else 'report'}): clipped text {bad}")
    return fig, ctx, lines


def save(fig: Figure, spec: Spec, ctx: Ctx, outdir: Path, deck: bool) -> list[Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    desc = " | ".join(
        [LABEL, provenance(spec), "source: " + "; ".join(ctx.sources)]
        + ([ALIGNMENT_LIMITATION] if spec.quantity else [])
        + ([OSM_CREDIT] if spec.is_map else [])
    )
    out = []
    svg = outdir / f"{spec.stem}.svg"
    fig.savefig(
        svg,
        format="svg",
        metadata={"Date": None, "Title": spec.title_en, "Description": desc},
    )
    png = outdir / f"{spec.stem}.png"
    fig.savefig(
        png,
        format="png",
        dpi=DECK_DPI if deck else REPORT_DPI,
        metadata={"Title": spec.title_en, "Description": desc},
    )
    out += [svg, png]
    plt.close(fig)
    return out


# ------------------------------------------------------------------ map helpers
def _aspect(ax: Any, lat: float) -> None:
    ax.set_aspect(1.0 / math.cos(math.radians(lat)))


def _base_layers(ax: Any, lw_scale: float = 1.0) -> list[Any]:
    regions = gpd.read_file(_p(ZONES / "regions.geojson"))
    # display-only simplification (~1 km) keeps the SVGs small; the data are not changed
    regions.boundary.simplify(0.01).plot(ax=ax, color="#c9c9c9", lw=0.5, zorder=1)
    ksa = gpd.read_file(_p(ZONES / "ksa.geojson")).boundary.simplify(0.01)
    ksa.plot(ax=ax, color="#8a8a8a", lw=0.8, zorder=1)
    handles = []
    for layer in ("historical", "committed", "existing"):
        g = gpd.read_file(_p(LINES / f"{layer}.geojson"))
        st = LAYER_STYLE[layer]
        g.plot(ax=ax, color=st["color"], lw=st["lw"] * lw_scale, ls=st["ls"], zorder=3)
    for layer in ("existing", "committed", "historical"):
        st = LAYER_STYLE[layer]
        handles.append(
            Line2D([], [], color=st["color"], lw=st["lw"], ls=st["ls"], label=LAYER_NAME[layer])
        )
    return handles


def _osm(ax: Any) -> None:
    ax.text(
        0.995,
        0.005,
        OSM_CREDIT,
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        fontsize=7,
        color="#333333",
        bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.8, "pad": 1.5},
        zorder=10,
    )


def _membership() -> dict[str, list[str]]:
    mem: dict[str, list[str]] = {}
    for lay in CP7:
        for c in layout_corridors(lay):
            mem.setdefault(c["id"], []).append(lay.replace("S6-", ""))
    return mem


def _phase(cid: str) -> int:
    for lay in CP7:
        for c in layout_corridors(lay):
            if c["id"] == cid:
                return int(c["phase"])
    raise KeyError(cid)


def _hyp_lines() -> list[tuple[str, gpd.GeoDataFrame]]:
    out = []
    for cid in _membership():
        if "station_addition" in cid:
            continue
        al = gpd.read_file(_p(ALIGNMENTS / f"{cid}.geojson"))
        if "kind" in al.columns:
            al = al[al["kind"] == "routed"]  # the routed v1 alignment, not the straight sketch
        out.append((cid, al))
    return out


def _planned_stations() -> list[tuple[str, dict[str, Any]]]:
    out = []
    for cid in _membership():
        if "station_addition" not in cid:
            continue
        y = corridor_yaml(cid)
        for s in y["stations"]:
            if s.get("class") == "planned":
                out.append((cid, s))
    return out


HYP_STYLE = {
    "branch_spur": {"color": "#c76a12", "lw": 2.2, "ls": "-."},
    "commuter_belt": {"color": "#6a4c93", "lw": 2.2, "ls": "--"},
}


def _draw_hyp(ax: Any, ctx: Ctx, label: bool = True) -> list[Any]:
    mem = _membership()
    handles = []
    for cid, g in _hyp_lines():
        fam = corridor_yaml(cid)["family"]
        st = HYP_STYLE[fam]
        g.plot(ax=ax, color=st["color"], lw=st["lw"], ls=st["ls"], zorder=5)
        ctx.src(ALIGNMENTS / f"{cid}.geojson")
        y = corridor_yaml(cid)
        lays = ", ".join(f"S6-{x}" for x in mem[cid])
        handles.append(
            Line2D(
                [],
                [],
                color=st["color"],
                lw=st["lw"],
                ls=st["ls"],
                label=f"{short_id(cid)} ({lays}; {_phase(cid)})",
            )
        )
        ctx.num(f"{cid} routed length_km (corridor YAML)", fmt(y["length_km"], 1))
    xs, ys = [], []
    planned = _planned_stations()
    mid_lon = float(np.median([s["lon"] for _, s in planned]))
    for cid, s in planned:
        xs.append(s["lon"])
        ys.append(s["lat"])
        lays = ", ".join(f"S6-{x}" for x in mem[cid])
        if label:
            # stations west of the median sit beside the Riyadh cluster: label below-left
            west = s["lon"] < mid_lon
            ax.annotate(
                f"{s['name_en']} ({lays}; {_phase(cid)})",
                (s["lon"], s["lat"]),
                xytext=(-6, -12) if west else (5, 4),
                textcoords="offset points",
                ha="right" if west else "left",
                fontsize=7,
                color="#1f5fa8",
                zorder=7,
                bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.75, "pad": 0.8},
            )
        ctx.src(CORRIDORS / "station_addition" / f"{cid}.yaml")
    ax.scatter(xs, ys, marker="*", s=110, color="#1f5fa8", edgecolor="white", lw=0.5, zorder=8)
    handles.insert(
        0,
        Line2D(
            [],
            [],
            marker="*",
            ls="",
            color="#1f5fa8",
            markersize=10,
            label="station additions (S6-L2 central case; also in S6-L1/L3 as labelled)",
        ),
    )
    return handles


# ------------------------------------------------------------------ fig01 national map
def draw_national_map(fig: Figure, rect: list[float], ctx: Ctx) -> None:
    ax = fig.add_axes([rect[0] - 0.04, rect[1], rect[2] * 0.62, rect[3]])
    layer_h = _base_layers(ax)
    st = gpd.read_file(_p(STATIONS))
    ex = st[st["layer"] == "existing"]
    ax.scatter(ex.geometry.x, ex.geometry.y, s=5, color="#1b1b1b", zorder=4)
    hyp_h = _draw_hyp(ax, ctx)
    _aspect(ax, 24.0)
    ax.set_axis_off()
    _osm(ax)
    # inset on the hypothetical lines around Riyadh (bounds from the alignments)
    lines = _hyp_lines()
    b = np.array([g.total_bounds for _, g in lines])
    x0, y0 = b[:, 0].min() - 0.35, b[:, 1].min() - 0.3
    x1, y1 = b[:, 2].max() + 0.35, b[:, 3].max() + 0.3
    ins = fig.add_axes([rect[0] + rect[2] * 0.6, rect[1] + rect[3] * 0.38, 0.32, rect[3] * 0.6])
    _base_layers(ins, lw_scale=1.3)
    _draw_hyp(ins, ctx)
    ins.set_xlim(x0, x1)
    ins.set_ylim(y0, y1)
    _aspect(ins, (y0 + y1) / 2)
    ins.set_xticks([])
    ins.set_yticks([])
    ins.set_xlabel("")
    ins.set_ylabel("")
    for s in ins.spines.values():
        s.set_visible(True)
        s.set_color("#888888")
    ins.set_title("Riyadh area (inset)", fontsize=8)
    _osm(ins)
    ax.plot([x0, x1, x1, x0, x0], [y0, y0, y1, y1, y0], color="#888888", lw=0.8, zorder=9)
    hyp_patch = Patch(facecolor="none", edgecolor="none", label=LAYER_NAME["hypothetical"] + ":")
    fig.legend(
        handles=layer_h + [hyp_patch] + hyp_h,
        loc="lower left",
        bbox_to_anchor=(rect[0] + rect[2] * 0.6, rect[1] - 0.02),
        fontsize=7.5,
        title="rail layers (never mixed)",
        title_fontsize=8,
        alignment="left",
    )
    ctx.src(
        LINES / "existing.geojson",
        LINES / "committed.geojson",
        LINES / "historical.geojson",
        STATIONS,
        TOP5_DIR / "L1.layout.yaml",
        TOP5_DIR / "L2.layout.yaml",
        TOP5_DIR / "L3.layout.yaml",
        ZONES / "regions.geojson",
    )
    for layer in ("existing", "committed", "historical"):
        g = gpd.read_file(_p(LINES / f"{layer}.geojson"))
        ctx.num(f"{layer} lines on the map", ", ".join(g["line_id"].tolist()))
    ctx.unit = (
        "Layers: existing / committed or under procurement (announced/planned) / historical / "
        "hypothetical (ours, alignment weights v1). Lon/lat (EPSG:4326)."
    )


# ------------------------------------------------------------------ fig02 funnel
def funnel_counts() -> list[tuple[str, int, str]]:
    settlements = len(pd.read_parquet(_p(ZONES / "settlements.parquet"), columns=["osm_id"]))
    register = len(pd.read_parquet(_p(CANDIDATES), columns=["row_key"]))
    summ = load_json(SCORE_SUMMARY)
    fams = {f: len(list((_p(CORRIDORS) / f).glob("*.yaml"))) for f in FAMILY_NAME}
    n_corr = sum(fams.values())
    n_cba = len([d for d in glob.glob(str(_p(CBA_DIR) / "CBA-S[2-5]-*")) if Path(d).is_dir()])
    t5 = top5()
    fam_txt = ", ".join(f"{FAMILY_NAME[f].split()[0]} {n}" for f, n in fams.items())
    return [
        (
            "settlement universe (OSM places + pilot rows)",
            settlements,
            str(ZONES / "settlements.parquet"),
        ),
        ("candidate register (13 region registers)", register, str(CANDIDATES)),
        ("long list", int(summ["n_long"]), str(SCORE_SUMMARY)),
        ("short list", int(summ["n_short"]), str(SCORE_SUMMARY)),
        (f"corridor candidates ({fam_txt})", n_corr, str(CORRIDORS)),
        ("corridor CBA cases (incl. variants)", n_cba, str(CBA_DIR)),
        (
            "CP7 programme layouts (S6-L1, S6-L2, S6-L3)",
            sum(1 for x in t5.index if x in CP7),
            str(TOP5),
        ),
    ]


def draw_funnel(fig: Figure, rect: list[float], ctx: Ctx) -> None:
    ax = fig.add_axes([rect[0] + 0.25, rect[1], rect[2] - 0.3, rect[3]])
    rows = funnel_counts()
    ys = np.arange(len(rows))[::-1]
    vals = [r[1] for r in rows]
    ax.barh(ys, vals, color=["#9fb7d6"] * 4 + ["#1f5fa8"] * 3, height=0.62)
    ax.set_xscale("log")
    ax.set_yticks(ys, [r[0] for r in rows])
    for y, v in zip(ys, vals, strict=True):
        ax.text(v * 1.08, y, fmt(v), va="center", fontsize=9)
    ax.set_xlim(1, max(vals) * 4)
    ax.set_xlabel("count (log scale)")
    for r in rows:
        ctx.num(r[0], fmt(r[1]))
        ctx.src(r[2])
    ctx.unit = (
        "Counts of rows/files; screening stages from the R2 funnel, corridors and cases from R5."
    )


# ------------------------------------------------------------------ fig03 coverage
def coverage_governorates() -> dict[str, int]:
    """Governorates per region from the generated `docs/coverage.md` "Per region" table (the
    GASTAT-reconciled count; 150 in total)."""
    text = _p(COVERAGE_MD).read_text(encoding="utf-8").split("## Per region", 1)[1]
    out: dict[str, int] = {}
    for line in text.split("## Reconciliation", 1)[0].splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) > 2 and cells[1].isdigit():
            out[cells[0]] = int(cells[1])
    return out


def coverage_table() -> pd.DataFrame:
    counts = load_json(LONGLIST_COUNTS)
    sc = pd.read_parquet(_p(SCORES))
    short = sc[sc["short_list"]].groupby("region").size()
    gov = coverage_governorates()
    reg = gpd.read_file(_p(ZONES / "regions.geojson"))[["region", "name_en"]]
    rows = []
    for _, r in reg.iterrows():
        k = r["region"]
        rows.append(
            {
                "region": k,
                "name": r["name_en"],
                "register_rows": counts["all"].get(k, 0),
                "long_list": counts["long_threshold"].get(k, 0),
                "served": counts["served"].get(k, 0),
                "short_list": int(short.get(k, 0)),
                "governorates": int(gov.get(k, 0)),
            }
        )
    return pd.DataFrame(rows).sort_values("register_rows", ascending=True)


def draw_coverage(fig: Figure, rect: list[float], ctx: Ctx) -> None:
    t = coverage_table()
    ax = fig.add_axes([rect[0] + 0.12, rect[1], rect[2] - 0.2, rect[3]])
    y = np.arange(len(t))
    h = 0.26
    ax.barh(y + h, t["register_rows"], h, color="#c9d6e8", label="register rows screened")
    ax.barh(y, t["long_list"], h, color="#6f95c6", label="long list")
    ax.barh(y - h, t["short_list"].clip(lower=0.0), h, color="#1f5fa8", label="short list")
    ax.set_xscale("symlog", linthresh=1)
    ax.set_yticks(y, [f"{n} ({g} gov.)" for n, g in zip(t["name"], t["governorates"], strict=True)])
    for yi, (_, r) in zip(y, t.iterrows(), strict=True):
        ax.text(
            r["register_rows"] * 1.1 + 0.5,
            yi + h,
            fmt(r["register_rows"]),
            va="center",
            fontsize=6.5,
        )
        ax.text(r["long_list"] * 1.1 + 0.5, yi, fmt(r["long_list"]), va="center", fontsize=6.5)
        ax.text(
            r["short_list"] * 1.1 + 0.5, yi - h, fmt(r["short_list"]), va="center", fontsize=6.5
        )
        ctx.num(
            f"{r['region']}: governorates / register / long / served / short",
            f"{r['governorates']} / {r['register_rows']} / {r['long_list']} / {r['served']} / "
            f"{r['short_list']}",
        )
    ax.set_xlim(0, t["register_rows"].max() * 3)
    ax.set_xlabel("count (symmetric log scale)")
    ax.legend(loc="lower right")
    ctx.num("regions", str(len(t)))
    ctx.num("governorates", str(int(t["governorates"].sum())))
    ctx.src(LONGLIST_COUNTS, SCORES, COVERAGE_MD, ZONES / "regions.geojson")
    ctx.unit = (
        f"All {len(t)} regions and {int(t['governorates'].sum())} governorates screened "
        "(none excluded; docs/coverage.md reconciliation)."
    )


# ------------------------------------------------------------------ fig04 BCR bands
def bcr_cases() -> pd.DataFrame:
    rows = []
    for d in sorted(glob.glob(str(_p(CBA_DIR) / "CBA-S[2-5]-*" / "results.json"))):
        res = json.loads(Path(d).read_text(encoding="utf-8"))
        r = cba_row(res)
        rows.append(
            {
                "case": res["case"],
                "family": res["family"],
                "p10": r["bcr"]["P10"],
                "p50": r["bcr"]["P50"],
                "p90": r["bcr"]["P90"],
                "run": str(Path(d).parent.relative_to(REPO_ROOT)),
            }
        )
    return pd.DataFrame(rows)


def draw_bcr(fig: Figure, rect: list[float], ctx: Ctx) -> None:
    t = bcr_cases()
    mem = _membership()
    fams = list(FAMILY_NAME)
    w = rect[2] / len(fams)
    finite = t[["p10", "p50", "p90"]].replace([np.inf, -np.inf], np.nan)
    xmax = float(np.nanmax(finite.to_numpy())) * 3
    xmin = float(np.nanmin(finite.to_numpy())) * 1.5
    for i, fam in enumerate(fams):
        s = t[t["family"] == fam].sort_values("p50")
        ax = fig.add_axes([rect[0] + i * w + w * 0.42, rect[1], w * 0.55, rect[3]])
        y = np.arange(len(s))
        for yi, (_, r) in zip(y, s.iterrows(), strict=True):
            cid = r["case"].replace("CBA-", "")
            hi = r["p90"] if math.isfinite(r["p90"]) else xmax
            col = "#c76a12" if cid in mem else "#1f5fa8"
            ax.plot([r["p10"], hi], [yi, yi], color=col, lw=2.2, alpha=0.55, solid_capstyle="butt")
            ax.plot(r["p50"], yi, "o", color=col, ms=3.5)
            if not math.isfinite(r["p90"]):
                ax.annotate(
                    "P90\nunbounded",
                    (xmax, yi),
                    xytext=(-2, 7),
                    textcoords="offset points",
                    fontsize=5.5,
                    va="center",
                )
            ctx.num(f"{cid} BCR P10/P50/P90", rng3(r["p10"], r["p50"], r["p90"], 2))
        ax.axvline(1.0, color="#c0392b", lw=0.8, ls="--")
        ax.set_xscale("symlog", linthresh=0.1)
        ax.set_xlim(xmin, xmax)
        labels = []
        for c in s["case"]:
            cid = c.replace("CBA-", "")
            tag = " *" if cid in mem else ""
            labels.append(short_id(cid).replace(cid.split("-")[0] + " ", "") + tag)
        ax.set_yticks(y, labels, fontsize=5.8 if len(s) > 15 else 6.5)
        ax.set_title(f"{FAMILY_NAME[fam]} ({len(s)})", fontsize=8.5)
        ax.set_xlabel("BCR (symlog)", fontsize=7)
        ax.tick_params(axis="x", labelsize=6)
    _note(
        fig,
        rect,
        "line = P10–P90, dot = P50; red dashed = BCR 1; * = corridor in S6-L1/L2/L3 (orange). "
        "S5 BCRs sit on a netted PVC near zero (negative, or unbounded where fares exceed "
        "costs): read S5 on NPV.",
        fontsize=7.5,
    )
    ctx.num("cases", str(len(t)))
    ctx.src(f"{CBA_DIR}/CBA-S2..S5-*/results.json ({len(t)} cases)")
    ctx.unit = (
        "BCR without wider impacts; UN WPP medium population, 60-year horizon, Green Book 2026 "
        "declining rate (the docs/cba.md §9 ranking basis); against S1; R5 CBA, 10,000 draws."
    )


# ------------------------------------------------------------------ fig05 programme NPV
def draw_programme_npv(fig: Figure, rect: list[float], ctx: Ctx) -> None:
    t = top5()
    res = cba_results(S1_CASE)
    s1 = cba_row(res)
    ax1 = fig.add_axes([rect[0] + 0.03, rect[1], rect[2] * 0.25, rect[3]])
    ax2 = fig.add_axes([rect[0] + rect[2] * 0.42, rect[1], rect[2] * 0.56, rect[3]])
    n = s1["npv"]
    ax1.plot([0, 0], [n["P10"] / 1e3, n["P90"] / 1e3], color=COLOR["S1"], lw=10, alpha=0.5)
    ax1.plot(0, n["P50"] / 1e3, "o", color="black", ms=6)
    ax1.set_xticks([0], ["S1 committed\nprogramme vs S0"])
    ax1.set_xlim(-0.8, 0.8)
    ax1.set_ylabel("NPV, SAR bn")
    ax1.axhline(0, color="#888", lw=0.7)
    ax1.set_title("S1 vs S0 (R5 CBA)", fontsize=9)
    for k in ("P10", "P50", "P90"):
        ax1.annotate(
            f"{k} {fmt(n[k] / 1e3, 1)}",
            (0, n[k] / 1e3),
            xytext=(12, 0),
            textcoords="offset points",
            fontsize=7,
            va="center",
        )
    ctx.num(
        "S1 vs S0 NPV P10/P50/P90 SAR m (medium, 60 y, Green Book 2026)",
        rng3(n["P10"], n["P50"], n["P90"]),
    )
    for i, lay in enumerate(CP7):
        r = t.loc[lay]
        p10, p50, p90 = (r[f"npv_draws_{q}_medium"] for q in ("p10", "p50", "p90"))
        ax2.plot(
            [i, i],
            [p10 / 1e3, p90 / 1e3],
            color=COLOR[lay],
            lw=14,
            alpha=0.45,
            solid_capstyle="butt",
        )
        ax2.plot(i, p50 / 1e3, "o", color="black", ms=6)
        ax2.plot(i, r["robust_npv"] / 1e3, "D", color=COLOR[lay], mec="black", ms=6)
        for v, lab in ((p10, "P10"), (p50, "P50"), (p90, "P90")):
            ax2.annotate(
                f"{lab} {fmt(v / 1e3, 1)}",
                (i, v / 1e3),
                xytext=(14, 0),
                textcoords="offset points",
                fontsize=7,
                va="center",
            )
        ctx.num(f"{lay} NPV draws P10/P50/P90 SAR m (medium)", rng3(p10, p50, p90))
        ctx.num(f"{lay} robust NPV SAR m (low pop, P50 cost)", fmt(r["robust_npv"]))
    ax2.set_xticks(range(3), [wrap_role(x) for x in CP7], fontsize=7.5)
    ax2.set_xlim(-0.6, 2.9)
    ax2.axhline(0, color="#888", lw=0.7)
    ax2.set_ylabel("incremental NPV over S1, SAR bn")
    ax2.set_title("CP7 layouts vs S1 (judge v3)", fontsize=9)
    ax2.legend(
        handles=[
            Line2D([], [], color="#777", lw=8, alpha=0.5, label="P10–P90 of 10,000 draws"),
            Line2D([], [], marker="o", ls="", color="black", label="P50"),
            Line2D(
                [],
                [],
                marker="D",
                ls="",
                color="#bbb",
                mec="black",
                label="robust NPV (low population, P50 cost)",
            ),
        ],
        loc="upper right",
    )
    ctx.src(CBA_DIR / S1_CASE / "results.json", TOP5)
    ctx.unit = (
        "SAR bn, 2025 prices, PV at 2026; UN WPP medium, 60 years, Green Book 2026 declining rate. "
        "Different baselines: S1 is measured against S0; the layouts are increments over S1."
    )


# ------------------------------------------------------------------ fig06 L1 P90 cost risk
def draw_l1_risk(fig: Figure, rect: list[float], ctx: Ctx) -> None:
    t = top5()
    ax = fig.add_axes([rect[0] + 0.02, rect[1], rect[2] * 0.95, rect[3]])
    pops = ("low", "medium", "high")
    w = 0.12
    for i, lay in enumerate(CP7):
        for j, p in enumerate(pops):
            a = t.loc[lay, f"npv_p50cost_{p}"] / 1e3
            b = t.loc[lay, f"npv_p90cost_{p}"] / 1e3
            x = i + (j - 1) * 2.4 * w
            alpha = 1.0 if lay == "S6-L1" else 0.45
            ax.bar(x - w / 2, a, w, color="#6f95c6", alpha=alpha)
            ax.bar(x + w / 2, b, w, color="#c0392b", alpha=alpha)
            ax.text(
                x + w / 2,
                b + (0.25 if b >= 0 else -0.25),
                fmt(b, 1),
                ha="center",
                va="bottom" if b >= 0 else "top",
                fontsize=6.5,
                weight="bold" if lay == "S6-L1" else "normal",
            )
            ax.text(x - w / 2, -0.2 if a >= 0 else a - 0.2, p, ha="center", va="top", fontsize=6)
        ctx.num(
            f"{lay} NPV at P50 cost low/medium/high SAR m",
            " / ".join(fmt(t.loc[lay, f"npv_p50cost_{p}"]) for p in pops),
        )
        ctx.num(
            f"{lay} NPV at P90 cost low/medium/high SAR m",
            " / ".join(fmt(t.loc[lay, f"npv_p90cost_{p}"]) for p in pops),
        )
    ax.axhline(0, color="#555", lw=0.8)
    ax.set_xticks(range(3), [f"{x}: {ROLE[x]}" for x in CP7], fontsize=8)
    ax.tick_params(axis="x", pad=14)
    ax.set_ylabel("incremental NPV over S1, SAR bn")
    ax.legend(
        handles=[
            Patch(color="#6f95c6", label="NPV at P50 capex"),
            Patch(color="#c0392b", label="NPV at P90 capex"),
        ],
        loc="upper right",
        title="bars per population case: low / medium / high",
        title_fontsize=7.5,
    )
    ctx.src(TOP5, TOP5_DIR / "L1/score.json")
    ctx.unit = (
        "SAR bn, 2025 prices, PV at 2026, 60 years, Green Book 2026 rate; capex quantile from the "
        "judge's draws; UN WPP low / medium / high. S6-L1 highlighted; S6-L2 and S6-L3 for scale."
    )


# ------------------------------------------------------------------ fig07 Pareto front
def _match_layouts(front: pd.DataFrame) -> dict[int, str]:
    t = top5()
    out = {}
    for lay in t.index:
        hit = front[
            (front["robust_npv"].round(1) == round(t.loc[lay, "robust_npv"], 1))
            & (front["capex_p50"].round(1) == round(t.loc[lay, "capex_p50"], 1))
        ]
        for i in hit.index:
            out[int(i)] = lay
    return out


def draw_pareto(fig: Figure, rect: list[float], ctx: Ctx) -> None:
    f = pd.read_csv(_p(PARETO))
    f = f[f["capex_p50"] > 0].copy()
    m = _match_layouts(f)
    t = top5()
    ax = fig.add_axes([rect[0] + 0.02, rect[1], rect[2] * 0.5, rect[3]])
    ins = fig.add_axes([rect[0] + rect[2] * 0.62, rect[1], rect[2] * 0.37, rect[3]])
    for a in (ax, ins):
        on = f[f["on_full_front"]]
        off = f[~f["on_full_front"]]
        for d, face in ((on, "#1f5fa8"), (off, "white")):
            a.errorbar(
                d["capex_p50"] / 1e3,
                d["npv_medium"] / 1e3,
                yerr=[
                    (d["npv_medium"] - d["npv_low"]) / 1e3,
                    (d["npv_high"] - d["npv_medium"]) / 1e3,
                ],
                fmt="o",
                ms=4,
                mfc=face,
                mec="#1f5fa8",
                ecolor="#9fb7d6",
                elinewidth=0.8,
                lw=0,
            )
        for lay in m.values():
            if lay not in CP7:
                continue
            r = t.loc[lay]
            x = r["capex_p50"] / 1e3
            a.errorbar(
                x,
                r["npv_draws_p50_medium"] / 1e3,
                yerr=[
                    [(r["npv_draws_p50_medium"] - r["npv_draws_p10_medium"]) / 1e3],
                    [(r["npv_draws_p90_medium"] - r["npv_draws_p50_medium"]) / 1e3],
                ],
                xerr=[
                    [(r["capex_p50"] - r["capex_p10"]) / 1e3],
                    [(r["capex_p90"] - r["capex_p50"]) / 1e3],
                ],
                fmt="s",
                ms=7,
                color=COLOR[lay],
                mec="black",
                elinewidth=1.6,
                capsize=3,
                alpha=0.9,
                zorder=6,
            )
            if a is ins:
                a.annotate(
                    lay,
                    (x, r["npv_draws_p50_medium"] / 1e3),
                    xytext=(6, 6),
                    textcoords="offset points",
                    fontsize=8,
                    weight="bold",
                    color=COLOR[lay],
                )
        a.axhline(0, color="#888", lw=0.6)
    ax.set_xscale("log")
    ax.set_xlabel("capex P50, SAR bn (log)")
    ax.set_ylabel("NPV over S1, SAR bn")
    ax.set_title("all front points (R6 full-judge scores)", fontsize=9)
    lim = t.loc[CP7, "capex_p90"].max() / 1e3 * 1.15
    ins.set_xlim(0, lim)
    lo = t.loc[CP7, "npv_draws_p10_medium"].min() / 1e3 * 1.15
    hi = t.loc[CP7, "npv_draws_p90_medium"].max() / 1e3 * 1.1
    ins.set_ylim(lo, hi)
    ins.set_xlabel("capex, SAR bn")
    ins.set_title("zoom: S6-L1, S6-L2, S6-L3 with P10–P90 (capex and NPV draws)", fontsize=9)
    ax.legend(
        handles=[
            Line2D(
                [],
                [],
                marker="o",
                ls="",
                mfc="#1f5fa8",
                mec="#1f5fa8",
                label="on the full front (dot = medium, bar = low–high population)",
            ),
            Line2D(
                [], [], marker="o", ls="", mfc="white", mec="#1f5fa8", label="off the full front"
            ),
            Line2D(
                [],
                [],
                marker="s",
                ls="",
                color="#999",
                mec="black",
                label="CP7 layout: P50, bars P10–P90",
            ),
        ],
        loc="lower left",
        fontsize=7,
    )
    _note(
        fig,
        rect,
        TRADEOFF_CAPTION + " (shown as unlabelled front points). Empty layout (capex 0) omitted.",
        fontsize=7.5,
    )
    ctx.num("front points plotted (capex > 0)", str(len(f)))
    ctx.num("on full front", str(int(f["on_full_front"].sum())))
    for i, lay in sorted(m.items(), key=lambda kv: kv[1]):
        ctx.num(f"{lay} matched front row hash", str(f.loc[i, "layout_hash"]))
    for lay in CP7:
        r = t.loc[lay]
        ctx.num(
            f"{lay} capex P10/P50/P90 SAR m", rng3(r["capex_p10"], r["capex_p50"], r["capex_p90"])
        )
    ctx.src(PARETO, TOP5)
    ctx.notes.append(
        "Front points: R6 full-judge scores (judge v2-p5b); judge v3 reproduces v2 exactly on the "
        "back-test (docs/r6/judge-v3-backtest.md); CP7 layouts: judge v3 (runs/r6/top5)."
    )
    ctx.unit = (
        "SAR bn, 2025 prices, PV at 2026, 60 years, Green Book 2026 rate. Front: robust objective "
        "space of R6; CP7 layouts re-scored with judge v3 (identical values on the back-test)."
    )


# ------------------------------------------------------------------ fig08 reach trade-off
def draw_reach(fig: Figure, rect: list[float], ctx: Ctx) -> None:
    t = top5()
    f = pd.read_csv(_p(PARETO))
    f = f[f["capex_p50"] > 0]
    ax = fig.add_axes([rect[0] + 0.02, rect[1], rect[2] * 0.95, rect[3]])
    ax.scatter(
        f["capex_p50"] / 1e3,
        f["access_gain_120"] / 1e6,
        s=12,
        color="#d5dce6",
        label="R6 front points (capex P50)",
        zorder=1,
    )
    for lay in CP7 + ILLUSTRATION:
        r = t.loc[lay]
        y = r["access_gain_120"] / 1e6
        ax.errorbar(
            r["capex_p50"] / 1e3,
            y,
            xerr=[
                [(r["capex_p50"] - r["capex_p10"]) / 1e3],
                [(r["capex_p90"] - r["capex_p50"]) / 1e3],
            ],
            fmt="s" if lay in CP7 else "^",
            ms=8,
            color=COLOR[lay],
            mec="black",
            capsize=3,
            elinewidth=1.5,
            zorder=5,
        )
        role = ROLE.get(lay, "trade-off illustration only: no recommendation")
        ax.annotate(
            f"{lay} ({role})\nrobust NPV {fmt(r['robust_npv'] / 1e3, 1)} bn",
            (r["capex_p50"] / 1e3, y),
            xytext=(8, -14 if lay in ("S6-L2",) else 6),
            textcoords="offset points",
            fontsize=7,
            color=COLOR[lay] if lay in CP7 else "#555555",
        )
        ctx.num(
            f"{lay} capex P10/P50/P90 SAR m", rng3(r["capex_p10"], r["capex_p50"], r["capex_p90"])
        )
        ctx.num(f"{lay} access gain 120 min (persons, five metros)", fmt(r["access_gain_120"]))
        ctx.num(f"{lay} robust NPV SAR m", fmt(r["robust_npv"]))
    # S6-L6: a connectivity comparison (not a search-front point), read from its own score file
    r = l6()
    y = r["access_gain_120"] / 1e6
    ax.errorbar(
        r["capex_p50"] / 1e3,
        y,
        xerr=[
            [(r["capex_p50"] - r["capex_p10"]) / 1e3],
            [(r["capex_p90"] - r["capex_p50"]) / 1e3],
        ],
        fmt="D",
        ms=8,
        mfc="white",
        color=COLOR["S6-L6"],
        mec=COLOR["S6-L6"],
        mew=1.8,
        capsize=3,
        elinewidth=1.5,
        zorder=5,
    )
    ax.annotate(
        f"S6-L6 ({COMPARISON_ROLE};\nconnectivity comparison, not a search-front point)\n"
        f"robust NPV {fmt(r['robust_npv'] / 1e3, 1)} bn; national reach gain "
        f"+{fmt(r['national_reach_gain_120_reported_only'] / 1e6, 2)} M (reported only)",
        (r["capex_p50"] / 1e3, y),
        xytext=(-10, 14),
        textcoords="offset points",
        ha="right",
        fontsize=7,
        color=COLOR["S6-L6"],
    )
    ctx.num("S6-L6 capex P10/P50/P90 SAR m", rng3(r["capex_p10"], r["capex_p50"], r["capex_p90"]))
    ctx.num("S6-L6 access gain 120 min (persons, five metros)", fmt(r["access_gain_120"]))
    ctx.num("S6-L6 robust NPV SAR m", fmt(r["robust_npv"]))
    ctx.num(
        "S6-L6 national reach gain 120 min (persons, reported only, A-r6-104)",
        fmt(r["national_reach_gain_120_reported_only"]),
    )
    ax.set_xscale("log")
    ax.set_xlabel("capex, SAR bn (log): P50 with P10–P90 bar")
    ax.set_ylabel(
        "people newly within 120 door-to-door minutes of the five metros, million (A-r6-007)"
    )
    ax.legend(loc="center right")
    _note(
        fig, rect, TRADEOFF_CAPTION + "; " + COMPARISON_CAPTION + ".", fontsize=8.5, weight="bold"
    )
    ctx.src(TOP5, PARETO, L6_CSV)
    ctx.unit = (
        "Capex SAR bn undiscounted, 2025 prices, uplifted (P10/P50/P90 of the judge's draws); "
        "reach "
        "= five-metro 120-minute door-to-door gain over S1 (deterministic network measure)."
    )


# ------------------------------------------------------------------ fig09 stage gates
def draw_stage_gates(fig: Figure, rect: list[float], ctx: Ctx) -> None:
    from optimise.layout import START_LAG

    t = top5()
    fis = load_json(FISCAL)
    ax = fig.add_axes([rect[0] + 0.2, rect[1], rect[2] - 0.22, rect[3]])
    rows: list[tuple[str, str, int]] = []
    for lay in CP7:
        phases = json.loads(t.loc[lay, "phases"])
        for ph in sorted(phases):
            for cid in sorted(phases[ph]):
                rows.append((lay, cid, int(ph)))
    y = len(rows) + len(CP7)
    yt, yl = [], []
    starts = set()
    last = None
    for lay, cid, ph in rows:
        if lay != last:
            y -= 1
            r = t.loc[lay]
            ax.text(
                2025.2,
                y,
                f"{lay}: {ROLE[lay]}  ·  layout capex P10/P50/P90 "
                f"{rng3(r['capex_p10'], r['capex_p50'], r['capex_p90'])} SAR m",
                fontsize=7.5,
                weight="bold",
                color=COLOR[lay],
                va="center",
            )
            ctx.num(
                f"{lay} layout capex P10/P50/P90 SAR m",
                rng3(r["capex_p10"], r["capex_p50"], r["capex_p90"]),
            )
            last = lay
        y -= 1
        start = ph - START_LAG
        starts.add(start)
        ax.barh(y, START_LAG, left=start, color=COLOR[lay], alpha=0.55, height=0.55)
        ax.plot(ph, y, "|", color="black", ms=12, mew=2)
        cap = fis["corridors"][cid]["basis"]["capex"]
        ax.text(
            ph + 0.6,
            y,
            f"standalone capex P10/P50/P90 {rng3(cap['p10'], cap['p50'], cap['p90'])}",
            fontsize=6.8,
            va="center",
        )
        yt.append(y)
        yl.append(short_id(cid))
        ctx.num(f"{lay} {cid} phase / construction start", f"{ph} / {start}")
        ctx.num(
            f"{cid} standalone capex P10/P50/P90 SAR m", rng3(cap["p10"], cap["p50"], cap["p90"])
        )
    for s in sorted(starts):
        ax.axvline(s, color="#c0392b", ls=":", lw=1)
        ax.text(
            s, len(rows) + len(CP7) - 0.3, f"gate {s}", color="#c0392b", fontsize=7, ha="center"
        )
    ax.set_yticks(yt, yl, fontsize=7.5)
    ax.set_ylim(-0.7, len(rows) + len(CP7) + 0.3)
    ax.set_xlim(2025, 2066)
    ax.set_xlabel("year")
    l1 = t.loc["S6-L1"]
    _note(
        fig,
        rect,
        f"bar = construction window (phase − {START_LAG} … phase − 1, A-r6-002); tick = planned "
        "opening (the judge draws the opening year); gate = decision before construction starts. "
        f"S6-L1 NPV at P90 cost low/medium/high: {fmt(l1['npv_p90cost_low'])} / "
        f"{fmt(l1['npv_p90cost_medium'])} / {fmt(l1['npv_p90cost_high'])} SAR m.",
        fontsize=7.2,
    )
    ctx.src(TOP5, FISCAL, "optimise/layout.py START_LAG (A-r6-002)")
    ctx.unit = (
        "Capex SAR m, undiscounted, 2025 prices, uplifted. Standalone corridor capex (judge v3 "
        "runs "
        "at the CP7 phase) does not add up to a layout. Only the three CP7 layouts are phased."
    )


# ------------------------------------------------------------------ fig10 fiscal exposure
MODEL_NAME = {
    "fully_public_sar": "fully public",
    "ppp_dbfom_availability": "availability PPP",
    "ppp_dbfom_demand_risk": "demand-risk concession",
}


def draw_fiscal(fig: Figure, rect: list[float], ctx: Ctx) -> None:
    d = load_json(FISCAL)
    case = d["robust_case"]
    ax = fig.add_axes([rect[0] + 0.02, rect[1], rect[2] * 0.66, rect[3]])
    axs = fig.add_axes([rect[0] + rect[2] * 0.8, rect[1], rect[2] * 0.17, rect[3]])
    models = list(MODEL_NAME)
    cols = {
        "fully_public_sar": "#1f5fa8",
        "ppp_dbfom_availability": "#c76a12",
        "ppp_dbfom_demand_risk": "#6a4c93",
    }
    w = 0.25
    for i, lay in enumerate(CP7):
        for j, mdl in enumerate(models):
            x = i + (j - 1) * w
            if mdl not in d["programmes"][lay]["models"]:
                ax.text(
                    x,
                    0.3,
                    "not assessed",
                    rotation=90,
                    ha="center",
                    va="bottom",
                    fontsize=6.5,
                    color="#555555",
                )
                ctx.num(f"{lay} {mdl}", "not assessed in runs/r7/fiscal/fiscal.json")
                continue
            v = d["programmes"][lay]["models"][mdl]["by_pop"][case]["net_fiscal_cost_60y"]
            ax.bar(
                x,
                (v["p90"] - v["p10"]) / 1e3,
                w * 0.8,
                bottom=v["p10"] / 1e3,
                color=cols[mdl],
                alpha=0.45,
            )
            ax.plot([x - w * 0.4, x + w * 0.4], [v["p50"] / 1e3] * 2, color="black", lw=1.5)
            ax.plot(x, v["expected"] / 1e3, "D", color="white", mec="black", ms=4)
            ax.text(x, v["p90"] / 1e3 + 0.4, fmt(v["p50"] / 1e3, 1), ha="center", fontsize=6.5)
            ctx.num(
                f"{lay} {mdl} NFC 60 y P10/P50/P90 (expected) SAR m",
                f"{rng3(v['p10'], v['p50'], v['p90'])} ({fmt(v['expected'])})",
            )
    ax.set_xticks(range(3), [wrap_role(x) for x in CP7], fontsize=7.5)
    ax.set_ylabel("net fiscal cost to the state, PV 60 years, SAR bn")
    ax.set_title(f"CP7 layouts, incremental to S1 (population case: {POP[case]})", fontsize=9)
    ax.legend(
        handles=[Patch(color=cols[m], alpha=0.45, label=MODEL_NAME[m]) for m in models]
        + [
            Line2D([], [], color="black", label="P50 (number above bar)"),
            Line2D([], [], marker="D", ls="", mfc="white", mec="black", label="expected value"),
        ],
        loc="upper left",
    )
    b = d["baseline_s1"]["rows"][f"{case}|60"]["fiscal_cost"]
    axs.bar(
        0, (b["P90"] - b["P10"]) / 1e3, 0.5, bottom=b["P10"] / 1e3, color=COLOR["S1"], alpha=0.45
    )
    axs.plot([-0.25, 0.25], [b["P50"] / 1e3] * 2, color="black", lw=1.5)
    for k in ("P10", "P50", "P90"):
        axs.text(0.3, b[k] / 1e3, f"{k} {fmt(b[k] / 1e3, 1)}", fontsize=6.8, va="center")
    axs.set_xticks([0], ["S1 vs S0\nfully public"])
    axs.set_xlim(-0.5, 1.3)
    axs.set_title("baseline S1", fontsize=9)
    ctx.num(f"S1 fiscal cost 60 y {case} P10/P50/P90 SAR m", rng3(b["P10"], b["P50"], b["P90"]))
    _note(
        fig,
        rect,
        "Availability PPP: P10 = P50 by construction (fixed price). PPP and concession columns are "
        "the sorted values of the three capex-quantile runs (labelled by rank, verify-R7 O8).",
        fontsize=7.2,
    )
    ctx.src(FISCAL, CBA_DIR / S1_CASE)
    ctx.unit = "SAR bn, 2025 prices, PV at 2026 on the Green Book 2026 schedule; bar = P10–P90."


# ------------------------------------------------------------------ fig11 VfM
def draw_vfm(fig: Figure, rect: list[float], ctx: Ctx) -> None:
    v = load_json(VFM)
    fis = load_json(FISCAL)
    case = v["population_case"]
    ents = [(k, "programmes") for k in CP7] + [(k, "corridors") for k in v["corridors"]]
    ax = fig.add_axes([rect[0] + 0.02, rect[1] + 0.04, rect[2] * 0.97, rect[3] - 0.04])
    w = 0.36
    for i, (ent, grp) in enumerate(ents):
        c = v[grp][ent]["central"]
        mods = fis[grp][ent]["models"]
        for j, (mdl, key, col) in enumerate(
            (("fully_public_sar", "psc", "#1f5fa8"), ("ppp_dbfom_availability", "ppp", "#c76a12"))
        ):
            q = mods[mdl]["by_pop"][case]["net_fiscal_cost_60y"]
            x = i + (j - 0.5) * w
            ax.bar(x, c[key] / 1e3, w * 0.9, color=col, alpha=0.75)
            ax.errorbar(
                x,
                q["p50"] / 1e3,
                yerr=[[(q["p50"] - q["p10"]) / 1e3], [(q["p90"] - q["p50"]) / 1e3]],
                fmt="_",
                color="black",
                ms=8,
                capsize=2,
                lw=0.9,
            )
        rs = v[grp][ent]["rate_sensitivity"]
        ax.text(
            i,
            max(c["ppp"], c["psc"]) / 1e3 * 1.0 + 1.2,
            f"VfM {fmt(c['vfm'])}\n({fmt(c['vfm_pct_psc'], 1)} %)",
            ha="center",
            fontsize=6.3,
        )
        ctx.num(
            f"{ent} E[PSC] / E[PPP] / VfM / % PSC SAR m",
            f"{fmt(c['psc'])} / {fmt(c['ppp'])} / {fmt(c['vfm'])} / {fmt(c['vfm_pct_psc'], 1)} %",
        )
        ctx.num(f"{ent} VfM at flat 5 % / sovereign rate", " / ".join(fmt(x) for x in rs.values()))
    ax.set_xticks(
        range(len(ents)),
        [
            ROLE.get(e, "").split(":")[0] + ("\n" if e in ROLE else "") + short_id(e)
            for e, _ in ents
        ],
        fontsize=6.8,
    )
    ax.set_ylabel("expected net fiscal cost, PV 60 years, SAR bn")
    ax.legend(
        handles=[
            Patch(color="#1f5fa8", alpha=0.75, label="E[public sector comparator]"),
            Patch(color="#c76a12", alpha=0.75, label="E[availability PPP]"),
            Line2D(
                [],
                [],
                marker="_",
                color="black",
                ls="",
                ms=10,
                label="P50 with P10–P90 of the model's net fiscal cost",
            ),
        ],
        loc="upper left",
    )
    _note(
        fig,
        rect,
        f"{v['definition']}. Negative = public delivery cheaper in expected PV; the sign "
        "holds across every registered parameter range (runs/r7/vfm/vfm.json).",
        fontsize=7.2,
    )
    ctx.src(VFM, FISCAL)
    ctx.unit = (
        f"SAR bn, 2025 prices, PV at 2026, 60 years, population case {POP[case]}; expected values "
        "use the lognormal capex mean (A-fund-108); corridors are standalone runs."
    )


# ------------------------------------------------------------------ fig12 isochrones
def _iso(scen: str, metro: str) -> gpd.GeoDataFrame:
    return gpd.read_file(_p(ACCESS / scen / metro / "isochrone_door_to_door.geojson"))


def _d2d(scen: str, metro_prefix: str) -> pd.DataFrame:
    r = pd.read_parquet(_p(ACCESS / scen / "reached.parquet"))
    return r[(r["metro"].str.startswith(metro_prefix)) & (r["mode"] == "door_to_door")]


def dammam_explanation(ctx: Ctx) -> str:
    """Why S1 reaches so few people door-to-door in Dammam, from the run files: the measure counts
    only zones reached by a rail ride (same-station trips are excluded: access/railgraph.py sets
    the diagonal of the minutes matrix to infinity), so a second station close to Dammam brings the
    metro's own zones within reach. Bands with no zone are listed."""
    s1 = _d2d("S1", "Dammam").set_index("band_min")
    dh = _d2d("S5-station_addition-dhahran", "Dammam").set_index("band_min")
    y = corridor_yaml("S5-station_addition-dhahran")
    st = {x["id"]: x for x in y["stations"]}
    gap = abs(st["dammam"]["km_post"] - st["dhahran"]["km_post"])
    runs = [
        ("S0", "Jeddah"),
        ("S1", "Jeddah"),
        ("S1", "Dammam"),
        ("S5-station_addition-dhahran", "Dammam"),
    ]
    allr = pd.concat([_d2d(sc, mp) for sc, mp in runs])
    nz = allr.groupby("band_min")["zones"].max()
    drawn = sorted(int(b) for b in nz.index if nz[b] > 0)
    empty = sorted(int(b) for b in nz.index if nz[b] == 0)
    n1 = int(s1.loc[120, "zones"])
    ctx.num(
        "Dammam S1 d2d 120 min: zones / population / outside metro",
        f"{int(s1.loc[120, 'zones'])} / {fmt(s1.loc[120, 'population'])} / "
        f"{fmt(s1.loc[120, 'population_outside_metro'])}",
    )
    ctx.num(
        "Dammam +Dhahran d2d 90 min: zones / population / outside metro",
        f"{int(dh.loc[90, 'zones'])} / {fmt(dh.loc[90, 'population'])} / "
        f"{fmt(dh.loc[90, 'population_outside_metro'])}",
    )
    ctx.num(
        "Dammam +Dhahran d2d 120 min: zones / population",
        f"{int(dh.loc[120, 'zones'])} / {fmt(dh.loc[120, 'population'])}",
    )
    ctx.num(
        "Dhahran–Dammam distance along sar-east-passenger, km (corridor YAML km posts)", fmt(gap, 1)
    )
    ctx.src(
        ACCESS / "S1/reached.parquet",
        ACCESS / "S5-station_addition-dhahran/reached.parquet",
        "access/railgraph.py (same-station trips excluded)",
    )
    return (
        "Door-to-door counts only zones reached by a rail ride (same-station trips excluded). "
        f"Dammam, S1: {n1} zone{'s' if n1 != 1 else ''} within 120 min "
        f"({fmt(s1.loc[120, 'population'])} people, outside the metro); the Dhahran station "
        f"{fmt(gap, 1)} km from Dammam adds a short ride that puts the metro's own zones within "
        f"reach ({int(dh.loc[90, 'zones'])} zones within 90 min, "
        f"{int(dh.loc[120, 'zones'])} within "
        f"120). Bands drawn: {' and '.join(map(str, drawn))} min; {', '.join(map(str, empty))} "
        "min reach no zone in these runs."
    )


def draw_isochrones(fig: Figure, rect: list[float], ctx: Ctx) -> None:
    panels = [
        (
            "jeddah",
            [("S0", "#c76a12"), ("S1", "#1f5fa8")],
            "Jeddah: S0 vs S1 (committed programme)",
        ),
        (
            "dammam",
            [("S1", "#c76a12"), ("S5-station_addition-dhahran", "#1f5fa8")],
            "Dammam–Khobar–Dhahran: S1 vs S1 + Dhahran station (in S6-L1, L2, L3)",
        ),
    ]
    w = rect[2] / 2
    for k, (metro, scens, title) in enumerate(panels):
        ax = fig.add_axes([rect[0] + k * w, rect[1] + 0.12, w * 0.95, rect[3] - 0.19])
        gs = [(_iso(s, metro), s, c) for s, c in scens]
        bounds = np.array([g.total_bounds for g, _, _ in gs])
        x0, y0 = bounds[:, 0].min() - 0.3, bounds[:, 1].min() - 0.3
        x1, y1 = bounds[:, 2].max() + 0.3, bounds[:, 3].max() + 0.3
        hs = []
        for n_g, (g, s, c) in enumerate(gs):
            base = n_g == 0  # the matched baseline: outline only, so the scenario stays visible
            for _, row in g.sort_values("band_min", ascending=False).iterrows():
                alpha = 0.3 if row["band_min"] >= 120 else 0.6
                geo = gpd.GeoSeries([row.geometry])
                if base:
                    geo.plot(ax=ax, facecolor="none", edgecolor=c, lw=1.6, hatch="///", zorder=6)
                else:
                    geo.plot(ax=ax, color=c, alpha=alpha, edgecolor=c, lw=0.8, zorder=2)
                lab = "S1 + Dhahran station" if s.startswith("S5") else s
                hs.append(
                    Patch(
                        facecolor="none" if base else c,
                        edgecolor=c,
                        hatch="///" if base else None,
                        alpha=1.0 if base else alpha,
                        label=f"{lab}, within {int(row['band_min'])} min: "
                        f"{fmt(row['population'])} people",
                    )
                )
                ctx.num(
                    f"{metro} {s} door-to-door within {int(row['band_min'])} min population",
                    fmt(row["population"]),
                )
            ctx.src(ACCESS / s / metro / "isochrone_door_to_door.geojson")
        layer_h = _base_layers(ax)
        st = gpd.read_file(_p(STATIONS))
        ex = st[st["layer"] == "existing"]
        ax.scatter(ex.geometry.x, ex.geometry.y, s=8, color="#1b1b1b", zorder=4)
        if metro == "dammam":
            for _cid, s in _planned_stations():
                if x0 <= s["lon"] <= x1 and y0 <= s["lat"] <= y1:
                    ax.scatter(
                        [s["lon"]],
                        [s["lat"]],
                        marker="*",
                        s=120,
                        color="#1f5fa8",
                        edgecolor="white",
                        zorder=8,
                    )
        ax.set_xlim(x0, x1)
        ax.set_ylim(y0, y1)
        _aspect(ax, (y0 + y1) / 2)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xlabel("")
        ax.set_ylabel("")
        ax.set_title(title, fontsize=9)
        _osm(ax)
        hyp = Line2D(
            [],
            [],
            marker="*",
            ls="",
            color="#1f5fa8",
            markersize=9,
            label="hypothetical (ours): station addition",
        )
        ax.legend(handles=hs, loc="upper left", bbox_to_anchor=(0, -0.01), fontsize=7)
    fig.legend(
        handles=layer_h + [hyp],
        loc="lower center",
        bbox_to_anchor=(0.5, rect[1] - 0.035),
        ncol=4,
        fontsize=7,
        title="rail layers",
        title_fontsize=7.5,
    )
    ctx.src(STATIONS, LINES / "existing.geojson", LINES / "committed.geojson")
    # two-line note: placed inside the content area, above the shortened map axes
    _note(fig, [rect[0], rect[1], rect[2], rect[3] - 0.06], dammam_explanation(ctx), fontsize=7.2)
    ctx.unit = (
        "Population reachable door-to-door from the metro's main station (road access, terminal, "
        "wait, ride, egress, summer factor; R4/R5 method). Deterministic network measure: no draws."
    )


# ------------------------------------------------------------------ fig13 benchmarks
def bench_rows() -> list[dict[str, Any]]:
    from rail.benchmarks import load_index, normalised_rows, read_csv

    levels = load_yaml(BENCH_METRICS.parent / "cost_levels.yaml") or {}
    return normalised_rows(read_csv(_p(BENCH_METRICS)), load_index(), levels)


def draw_bench(fig: Figure, rect: list[float], ctx: Ctx) -> None:
    rows = bench_rows()
    conv = [r for r in rows if r["central"] is not None]
    slugs = []
    for r in conv:
        if r["slug"] not in slugs:
            slugs.append(r["slug"])
    rng = np.random.default_rng(ctx.seed)
    ax = fig.add_axes([rect[0] + 0.02, rect[1] + 0.05, rect[2] * 0.97, rect[3] - 0.05])
    lv_col = {
        "line": "#1f5fa8",
        "estimate": "#7fb3e0",
        "average": "#2e8b57",
        "package": "#c76a12",
        "unbuilt": "#9a9a9a",
        "other": "#6a4c93",
        "unclassified": "#cccccc",
    }
    for i, s in enumerate(slugs):
        sel = [r for r in conv if r["slug"] == s]
        vals = np.array([r["central"] for r in sel])
        jit = rng.uniform(-0.18, 0.18, len(sel))
        ax.scatter(
            i + jit,
            vals,
            s=16,
            c=[lv_col.get(r["level"], "#ccc") for r in sel],
            edgecolor="white",
            lw=0.3,
            zorder=3,
        )
        med = float(np.median(vals))
        ax.plot([i - 0.3, i + 0.3], [med, med], color="black", lw=1.2)
        ctx.num(
            f"{s}: n converted / median SAR m/km 2025 / min / max",
            f"{len(sel)} / {fmt(med, 1)} / {fmt(vals.min(), 1)} / {fmt(vals.max(), 1)}",
        )
    # this study: corridors with a routed alignment in the CP7 layouts (capex / routed length)
    fis = load_json(FISCAL)
    xi = len(slugs) + 0.5
    k = 0
    for cid in _membership():
        if "station_addition" in cid:
            continue
        cap = fis["corridors"][cid]["basis"]["capex"]
        km = corridor_yaml(cid)["length_km"]
        x = xi + k * 0.5
        lo, mid, hi = cap["p10"] / km, cap["p50"] / km, cap["p90"] / km
        ax.errorbar(
            x,
            mid,
            yerr=[[mid - lo], [hi - mid]],
            fmt="D",
            color="#c0392b",
            capsize=3,
            ms=6,
            zorder=5,
        )
        ax.annotate(
            short_id(cid),
            (x, hi),
            xytext=(0, 4),
            textcoords="offset points",
            fontsize=6.5,
            ha="center",
            rotation=90,
            va="bottom",
        )
        ctx.num(
            f"{cid} capex per routed km P10/P50/P90 SAR m/km (judge v3 capex / {fmt(km, 1)} km)",
            rng3(lo, mid, hi, 1),
        )
        ctx.src(CORRIDORS / f"{corridor_yaml(cid)['family']}/{cid}.yaml")
        k += 1
    ax.set_yscale("log")
    ax.set_xticks(
        list(range(len(slugs))) + [xi + 0.25],
        [s.replace("_", " ") for s in slugs] + ["this study\n(hypothetical)"],
        rotation=30,
        ha="right",
        fontsize=7.5,
    )
    ax.set_ylabel("cost per route-km, SAR m per km, 2025 prices (log)")
    ax.legend(
        handles=[
            Line2D([], [], marker="o", ls="", color=c, label=lv)
            for lv, c in lv_col.items()
            if any(r["level"] == lv for r in conv)
        ]
        + [
            Line2D([], [], color="black", label="country median"),
            Line2D(
                [],
                [],
                marker="D",
                ls="",
                color="#c0392b",
                label="this study: capex P10/P50/P90 ÷ routed length",
            ),
        ],
        loc="lower left",
        bbox_to_anchor=(0, 1.0),
        ncol=5,
        fontsize=7,
    )
    n_skip = len(rows) - len(conv)
    ctx.num(
        "benchmark cost_per_km rows grade A–C / converted / not converted",
        f"{len(rows)} / {len(conv)} / {n_skip}",
    )
    ctx.src(
        BENCH_METRICS,
        "cities/ksa/costs/index.yaml",
        BENCH_METRICS.parent / "cost_levels.yaml",
        FISCAL,
        "docs/benchmarks/README.md",
    )
    ctx.unit = (
        "SAR m per route-km at 2025 prices: central conversion of cities/ksa/costs/index.yaml "
        f"(A-cost-002); grade D excluded; {n_skip} rows with an unknown price year not converted. "
        "Scope differs by line (indicative)."
    )


# ------------------------------------------------------------------ fig14 tornado
def draw_tornado(fig: Figure, rect: list[float], ctx: Ctx) -> None:
    cases = [
        (S1_CASE, "S1 committed programme vs S0"),
        (
            "CBA-S3-branch_spur-al-kharj",
            "Al-Kharj spur vs S1 (the corridor behind S6-L1's P90 risk)",
        ),
    ]
    w = rect[2] / 2
    for k, (case, title) in enumerate(cases):
        tor = pd.read_csv(_p(CBA_DIR / case / "tornado.csv")).sort_values("swing_npv")
        sw = load_json(CBA_DIR / case / "switching_values.json")
        c = sw["basis"]["central_npv_sar_m"] / 1e3
        ax = fig.add_axes([rect[0] + k * w + w * 0.38, rect[1] + 0.1, w * 0.58, rect[3] - 0.1])
        y = np.arange(len(tor))
        for yi, (_, r) in zip(y, tor.iterrows(), strict=True):
            lo, hi = r["npv_low"] / 1e3, r["npv_high"] / 1e3
            ax.barh(yi, lo - c, left=c, color="#6f95c6", height=0.6)
            ax.barh(yi, hi - c, left=c, color="#c76a12", height=0.6)
            ctx.num(
                f"{case} tornado {r['input']}: NPV at low / high input SAR m",
                f"{fmt(r['npv_low'])} / {fmt(r['npv_high'])}",
            )
        ax.axvline(c, color="black", lw=0.8)
        ax.set_yticks(y, tor["input"], fontsize=6.5)
        ax.set_xlabel("NPV, SAR bn", fontsize=8)
        ax.set_title(title, fontsize=8.5)
        dem = sw["demand_share_of_model_forecast"]["value"]
        txt = (
            f"central NPV {fmt(c, 1)} bn, BCR {fmt(sw['basis']['central_bcr'], 2)}\n"
            f"switching values (BCR = 1): demand {fmt(dem * 100)} % of the modelled forecast; "
            f"capex × {fmt(sw['capex_multiplier']['value'], 2)}; "
            f"VoT × {fmt(sw['vot_multiplier']['value'], 2)}\n"
            "NPV = 0 at a constant real rate of "
            f"{fmt(sw['discount_rate_npv_zero']['value'] * 100, 2)} %"
        )
        fig.text(rect[0] + k * w, rect[1] - 0.005, txt, fontsize=6.8, va="top")
        ctx.num(
            f"{case} central NPV SAR m / BCR",
            f"{fmt(sw['basis']['central_npv_sar_m'])} / {fmt(sw['basis']['central_bcr'], 3)}",
        )
        ctx.num(
            f"{case} switching: demand share / capex x / VoT x / rate",
            f"{fmt(dem, 4)} / {fmt(sw['capex_multiplier']['value'], 4)} / "
            f"{fmt(sw['vot_multiplier']['value'], 4)} / "
            f"{fmt(sw['discount_rate_npv_zero']['value'], 5)}",
        )
        ctx.src(CBA_DIR / case / "tornado.csv", CBA_DIR / case / "switching_values.json")
    fig.legend(
        handles=[
            Patch(color="#6f95c6", label="input at its low (P10/low) value"),
            Patch(color="#c76a12", label="input at its high (P90/high) value"),
        ],
        loc="lower left",
        bbox_to_anchor=(rect[0], rect[1] + rect[3] + 0.025),
        ncol=2,
    )
    ctx.unit = (
        "One-at-a-time P10/P90 swings on the deterministic central row (draw medians, UN WPP "
        "medium, "
        "60 years, Green Book 2026); SAR bn, 2025 prices, PV at 2026 (R5 CBA, docs/cba.md §6)."
    )


# ------------------------------------------------------------------ fig15 capex ranges
def s1_capex() -> tuple[float, float, float]:
    d = pd.read_parquet(_p(CBA_DIR / S1_CASE / "draws.parquet"), columns=["capex"])
    q = np.percentile(d["capex"].to_numpy(), [10, 50, 90])
    return float(q[0]), float(q[1]), float(q[2])


def draw_capex(fig: Figure, rect: list[float], ctx: Ctx) -> None:
    t = top5()
    ax = fig.add_axes([rect[0] + 0.2, rect[1], rect[2] - 0.25, rect[3]])
    items = [("S1", "S1 committed programme (vs S0)", s1_capex())] + [
        (
            lay,
            f"{lay}: " + "\n".join(textwrap.wrap(f"{ROLE[lay]} (increment over S1)", 30)),
            (t.loc[lay, "capex_p10"], t.loc[lay, "capex_p50"], t.loc[lay, "capex_p90"]),
        )
        for lay in CP7
    ]
    for i, (key, _lab, (p10, p50, p90)) in enumerate(items[::-1]):
        ax.plot(
            [p10 / 1e3, p90 / 1e3],
            [i, i],
            color=COLOR[key],
            lw=12,
            alpha=0.5,
            solid_capstyle="butt",
        )
        ax.plot(p50 / 1e3, i, "o", color="black", ms=6)
        for v, q in ((p10, "P10"), (p50, "P50"), (p90, "P90")):
            ax.annotate(
                f"{q} {fmt(v / 1e3, 1)}",
                (v / 1e3, i),
                xytext=(0, 11),
                textcoords="offset points",
                fontsize=7,
                ha="center",
            )
        ctx.num(f"{key} capex P10/P50/P90 SAR m", rng3(p10, p50, p90))
    ax.set_yticks(range(len(items)), [x[1] for x in items[::-1]], fontsize=8)
    ax.set_ylim(-0.6, len(items) - 0.3)
    ax.set_xscale("log")
    ax.set_xlabel("capex, SAR bn (log), undiscounted, uplifted")
    ctx.src(CBA_DIR / S1_CASE / "draws.parquet", TOP5)
    ctx.unit = (
        "SAR bn, 2025 prices, undiscounted, reference-class uplift included. S1: P10/P50/P90 of "
        "the "
        "10,000 R5 draws; layouts: the judge v3 capex quantiles."
    )


# ------------------------------------------------------------------ fig16 S6-L6 map
def draw_l6_map(fig: Figure, rect: list[float], ctx: Ctx) -> None:
    """The connected-system map written by `optimise.connect map` (S6_L6_CONNECTED), embedded as
    is (no geometry is redrawn), with the S6-L6 scorecard and the labels beside it."""
    img = plt.imread(_p(L6_MAP))
    h, w = img.shape[:2]
    fh, fw = fig.get_figheight(), fig.get_figwidth()
    ah = rect[3] + 0.04
    aw = ah * fh * w / h / fw
    ax = fig.add_axes([0.02, rect[1] - 0.02, aw, ah])
    ax.imshow(img, interpolation="antialiased")
    ax.set_axis_off()
    r = l6()
    s = load_json(L6_SEARCH)
    x0 = 0.02 + aw + 0.02
    lines = [
        ("S6-L6: " + COMPARISON_ROLE, 9.5, "bold", COLOR["S6-L6"]),
        (
            "Connectivity comparison: not a search-front point, not a reach trade-off.",
            7.5,
            "normal",
            "#222",
        ),
        ("No recommendation, no delivery model, no stage-gate.", 7.5, "normal", "#222"),
        ("", 4, "normal", "#222"),
        ("Full judge v3, against S1 (SAR m, 2025 prices, PV 2026):", 8, "bold", "#222"),
        (
            f"robust NPV {fmt(r['robust_npv'])} (min over UN WPP low / medium / high)",
            7.5,
            "normal",
            "#222",
        ),
        (
            "capex P10 / P50 / P90 " + rng3(r["capex_p10"], r["capex_p50"], r["capex_p90"]),
            7.5,
            "normal",
            "#222",
        ),
        (
            "BCR P10 / P50 / P90 (medium) "
            + rng3(r["bcr_p10_medium"], r["bcr_p50_medium"], r["bcr_p90_medium"], 2),
            7.5,
            "normal",
            "#222",
        ),
        (
            f"added rail trips 2050 (medium) +{fmt(r['added_rail_trips_2050_medium'] / 1e6, 2)} M",
            7.5,
            "normal",
            "#222",
        ),
        (
            f"five-metro 120-min reach gain {fmt(r['access_gain_120'] / 1e6, 2)} M (A-r6-007)",
            7.5,
            "normal",
            "#222",
        ),
        (
            f"national reach gain +{fmt(r['national_reach_gain_120_reported_only'] / 1e6, 2)} M "
            "(reported only, A-r6-104)",
            7.5,
            "normal",
            "#222",
        ),
        (
            f"{int(r['corridors'])} library options; {fmt(r['new_route_km'])} new route-km",
            7.5,
            "normal",
            "#222",
        ),
        ("", 4, "normal", "#222"),
        ("Map legend (rail layers, never mixed): existing;", 7.5, "normal", "#222"),
        ("committed / under procurement (announced/planned);", 7.5, "normal", "#222"),
        ("historical (abandoned); hypothetical (ours).", 7.5, "normal", "#222"),
        ("", 4, "normal", "#222"),
    ]
    lines += [(x, 7.3, "normal", "#444") for x in textwrap.wrap(ACCESS_SITES, 62)]
    y = rect[1] + rect[3]
    for text, size, weight, color in lines:
        _fit_text(fig, x0, y, text, size, weight=weight, color=color, va="top")
        y -= 0.006 + size / 72 / fh * 1.25
    _note(fig, rect, COMPARISON_CAPTION + ".", fontsize=8.5, weight="bold")
    ctx.num("S6-L6 robust NPV SAR m", fmt(r["robust_npv"]))
    ctx.num("S6-L6 capex P10/P50/P90 SAR m", rng3(r["capex_p10"], r["capex_p50"], r["capex_p90"]))
    ctx.num(
        "S6-L6 BCR P10/P50/P90 medium",
        rng3(r["bcr_p10_medium"], r["bcr_p50_medium"], r["bcr_p90_medium"], 2),
    )
    ctx.num("S6-L6 library options", str(int(r["corridors"])))
    ctx.num("connecting-set search runs", ", ".join(sorted(s.get("runs", {}))))
    ctx.src(L6_MAP, L6_SEARCH, L6_CSV, "scenarios/S6-L6.yaml")
    ctx.notes.append(
        "The map image is the file optimise.connect map wrote at S6_L6_CONNECTED; it is embedded "
        "unchanged (no new geometry). " + ACCESS_SITES
    )
    ctx.unit = (
        "SAR million, 2025 prices; NPV PV at 2026, 60 years, Green Book 2026; capex undiscounted, "
        "uplifted. Map: lon/lat, one rail-graph component (A-r6-130)."
    )


# ------------------------------------------------------------------ registry
SPECS: list[Spec] = [
    Spec(
        "fig01-national-map",
        "National rail map: existing, committed, historical and hypothetical layers",
        "الشبكة الوطنية: الخطوط القائمة والملتزم بها والتاريخية والافتراضية",
        draw_national_map,
        modelled=False,
        is_map=True,
        prov=("registers", "judge_v3"),
        caption="Map of the existing, committed/under-procurement (announced/planned) and "
        "historical lines with the hypothetical CP7 additions: the station additions of S6-L2 "
        "(also in S6-L1/S6-L3 as labelled), the Al-Kharj spur (S6-L1, S6-L3) and the Riyadh belt "
        "225 (S6-L3) on the frozen v1 alignments, with a Riyadh inset.",
    ),
    Spec(
        "fig02-screening-funnel",
        "Screening funnel: settlement universe to CP7 programme layouts",
        "مسار الفرز: من التجمعات السكانية إلى خيارات البرنامج",
        draw_funnel,
        modelled=False,
        quantity=False,
        screening=True,
        prov=("r2_screening", "registers", "r5_cba", "judge_v3"),
        caption="Log-scale bars of the count at each stage: settlement universe, candidate "
        "register, long list, short list, corridor candidates by family, corridor CBA cases and "
        "the three CP7 layouts.",
    ),
    Spec(
        "fig03-coverage-by-region",
        "Coverage: every region screened",
        "تغطية الفرز: المناطق الثلاث عشرة كلها",
        draw_coverage,
        modelled=False,
        quantity=False,
        screening=True,
        prov=("r2_screening", "registers"),
        caption="For each of the 13 regions: register rows screened, long list and short list "
        "(symmetric log scale), with the number of governorates in the label.",
    ),
    Spec(
        "fig04-bcr-bands-by-family",
        "BCR ranges per corridor case, by family (P10/P50/P90)",
        "نطاقات نسبة المنافع إلى التكاليف لكل ممر حسب العائلة",
        draw_bcr,
        prov=("r5_cba",),
        caption="P10–P90 line and P50 dot of the BCR without wider impacts for every R5 corridor "
        "CBA case against S1, in four family panels (S2–S5); UN WPP medium, 60 years, Green Book "
        "2026; corridors of the CP7 layouts in orange.",
    ),
    Spec(
        "fig05-programme-npv-ranges",
        "Programme NPV ranges: S1, and the CP7 layouts against S1",
        "نطاقات صافي القيمة الحالية: البرنامج الملتزم به والخيارات الثلاثة",
        draw_programme_npv,
        prov=("r5_cba", "judge_v3"),
        caption="Left: NPV of the S1 committed programme against S0, P10/P50/P90 (R5 CBA). Right: "
        "incremental NPV over S1 of S6-L2 (central), S6-L1 (upside, carries the Al-Kharj spur's "
        "P90 cost risk) and S6-L3 (reach), P10–P90 of the judge v3 draws with P50 and the robust "
        "NPV; UN WPP medium, 60 years, Green Book 2026.",
    ),
    Spec(
        "fig06-l1-p90-cost-risk",
        "S6-L1 upside case: NPV at P50 and at P90 capex",
        "الحالة الأعلى عائداً S6-L1: صافي القيمة الحالية عند التكلفة الوسيطة وتكلفة P90",
        draw_l1_risk,
        prov=("judge_v3",),
        caption="Incremental NPV over S1 at P50 and at P90 capex for the low, medium and high "
        "population cases: S6-L1 highlighted (the Al-Kharj spur's P90 cost risk), S6-L2 and "
        "S6-L3 faint for scale.",
    ),
    Spec(
        "fig07-pareto-front",
        "Pareto front: NPV against capex",
        "جبهة باريتو: صافي القيمة الحالية مقابل التكلفة الرأسمالية",
        draw_pareto,
        prov=("r6_front", "judge_v3"),
        caption="R6 full-judge front points (medium-population NPV at P50 cost against capex P50, "
        "bar = low–high population) with S6-L1, S6-L2 and S6-L3 marked by P10–P90 of the NPV "
        "draws and of capex in a zoom panel; S6-L4/L5 are unlabelled front points (trade-off "
        "illustration only). S6-L6 is not on the R6 front (it was built by the connectivity "
        "search, not the NPV/reach search) and is shown in Figures 8 and 16.",
    ),
    Spec(
        "fig08-reach-tradeoff",
        "Cost against reach: S6-L1 to S6-L6",
        "المفاضلة بين التكلفة والتغطية (توضيح ومقارنة فقط)",
        draw_reach,
        prov=("judge_v3", "r6_front", "l6_score"),
        caption="Capex P50 with P10–P90 bars against the five-metro 120-minute door-to-door reach "
        "gain over S1 (A-r6-007) for S6-L1 to S6-L6, over the R6 front points. S6-L4 and S6-L5 are "
        "reach trade-off illustrations from the search only: no recommendation. S6-L6 is a "
        "connectivity comparison (the smallest-capex connecting set), not a search-front point and "
        "not a recommendation; its national reach gain is +6.64 M (reported only, A-r6-104), "
        "which the plotted five-metro measure does not show.",
    ),
    Spec(
        "fig09-stage-gates",
        "Phasing (2030, 2050) and stage gates (2027, 2047)",
        "المراحل (2030 و2050) وبوابات القرار (2027 و2047)",
        draw_stage_gates,
        prov=("judge_v3", "r7_funding"),
        caption="For each corridor of S6-L2, S6-L1 and S6-L3: construction window (phase − 3 to "
        "phase − 1, A-r6-002), planned opening at the phase year and the decision gate at each "
        "construction start, with layout capex and standalone corridor capex P10/P50/P90 and the "
        "S6-L1 NPV at P90 cost.",
    ),
    Spec(
        "fig10-fiscal-exposure",
        "Fiscal exposure by delivery model (60-year PV)",
        "الانكشاف المالي حسب نموذج التنفيذ",
        draw_fiscal,
        prov=("r7_funding", "r5_cba"),
        caption="Net fiscal cost to the state (PV 60 years, low population) of each CP7 layout "
        "under fully public delivery, availability PPP and demand-risk concession: P10–P90 bar, "
        "P50 line and expected value; S1 baseline (fully public, against S0) beside.",
    ),
    Spec(
        "fig11-vfm",
        "Value for money: public sector comparator against availability PPP",
        "القيمة مقابل المال: المقارن الحكومي مقابل الشراكة بين القطاعين العام والخاص "
        "بنظام مدفوعات الإتاحة",
        draw_vfm,
        prov=("r7_funding",),
        caption="Expected net fiscal cost (PV 60 years, low population) of the public sector "
        "comparator and of an availability PPP for the three CP7 layouts and their five "
        "corridors, with P10/P50/P90 whiskers and the VfM difference (% of PSC).",
    ),
    Spec(
        "fig12-isochrones",
        "Door-to-door isochrones: Jeddah and Dammam",
        "نطاقات الوصول من الباب إلى الباب: جدة والدمام",
        draw_isochrones,
        modelled=True,
        is_map=True,
        prov=("r4_access", "registers"),
        caption="Door-to-door isochrones from each metro's boarding stations: Jeddah S0 "
        "(hatched) against S1 (filled); Dammam–Khobar–Dhahran S1 (hatched) against S1 plus the "
        "Dhahran station addition of all three CP7 layouts (filled); the bands drawn are the ones "
        "that reach at least one zone (listed on the figure).",
    ),
    Spec(
        "fig13-benchmark-cost-per-km",
        "Benchmark cost per route-km, converted to SAR 2025",
        "تكلفة الكيلومتر في التجارب الدولية بأسعار 2025",
        draw_bench,
        prov=("bench", "r7_funding"),
        caption="Cost per route-km of the grade A–C benchmark rows (SAR m per km, 2025 prices, "
        "central conversion, log scale) by country with the country median, beside capex "
        "P10/P50/P90 ÷ routed length of the two routed CP7 lines (Al-Kharj spur, Riyadh belt 225).",
    ),
    Spec(
        "fig14-tornado-switching",
        "Tornado and switching values: S1 and the Al-Kharj spur",
        "تحليل الحساسية وقيم التحول",
        draw_tornado,
        prov=("r5_cba",),
        caption="One-at-a-time NPV tornado (each input at its low/P10 and high/P90 value) and the "
        "switching values for the S1 committed programme against S0 and the Al-Kharj spur against "
        "S1 (R5 CBA, docs/cba.md §6).",
    ),
    Spec(
        "fig15-capex-ranges",
        "Capex ranges: S1 and the CP7 layouts",
        "نطاقات التكلفة الرأسمالية",
        draw_capex,
        prov=("r5_cba", "judge_v3"),
        caption="Undiscounted uplifted capex P10/P50/P90 (log scale) of S1 (the 10,000 R5 draws) "
        "and of the increments over S1 of S6-L2, S6-L1 and S6-L3 (judge v3 quantiles).",
    ),
    Spec(
        "fig16-l6-connected-map",
        "S6-L6: one connected rail system (comparison layout, not the recommended programme)",
        "S6-L6: منظومة سكك حديدية واحدة متصلة (مخطط للمقارنة، لا البرنامج الموصى به)",
        draw_l6_map,
        is_map=True,
        prov=("l6_search", "l6_score", "registers"),
        caption="The existing connected-system map of S6-L6 from the connecting-set search "
        "(S6_L6_CONNECTED), reused unchanged: S1 lines and the 16 library options of S6-L6 as one "
        "rail-graph component, the corridors joining an S1 island highlighted and the 18 required "
        "cities annotated, beside the S6-L6 full-judge v3 scorecard. Comparison layout, not the "
        "recommended programme; the access-model site overrides (A-r4-acc-004) are not rail-graph "
        "interchanges.",
    ),
]
STEMS = [s.stem for s in SPECS]

GENERAL_NOTES = [
    "verify-R8 fixes (docs/status/verify-R8.md): (1) text that would leave the canvas is shrunk "
    "or wrapped and the build refuses to save a clipped figure (clipped_texts); fig09 now shows "
    "the full S6-L1 P90-cost statement. (2) Footers print each figure's own provenance from "
    "the runs' "
    "meta.json; the judge v3 line appears only where judge v3 runs (or the R7 engine on judge v3 "
    "scores) are drawn: fig14 and fig04 now say R5 CBA. (3) fig12 explains the Dammam S1 reach "
    "from the run files and lists the bands drawn. (4) fig01 labels of stations west of the "
    "median longitude (Duruma) sit below-left on a white box, clear of the Riyadh cluster. (5) "
    "figures-index.csv carries caption, exact sources and provenance per stem.",
    "fig12 Dammam reason (run files, not inferred): door-to-door counts only zones reached by a "
    "rail ride, because access/railgraph.py sets the diagonal of the minutes matrix to infinity "
    "(no same-station trip); with Dammam as the only boarding station the nearest other station "
    "is far, so only one zone outside the metro is within 120 min; the Dhahran station "
    "(km posts in its corridor YAML) adds a short ride that brings the metro's zones within 90 "
    "and 120 min. Numbers in the fig12 table below.",
    "Figures print money in SAR bn to one decimal (SAR m for capex labels); the tables below give "
    "SAR m to the unit, so a report sentence can cite either with the run id.",
    "The S6-L1 NPV at P90 cost (low / medium / high) shown on fig06 and fig09 equals "
    "-2,958 / -724 / +1,631 SAR m (runs/r6/top5/L1/score.json npv_at_p90_cost; checked by "
    "tests/test_report_figures.py).",
    "Weights v1 only: no input under alignments-v2, top5-v2 or runs/r7-v2 is read (the test greps "
    "every SVG for those names).",
    "Arabic titles (15, short) were written natively by the figures builder, as the coordinator's "
    "task asked. prompts/R8.md R7-checkpoint answer 2 asks that Arabic text be drafted with open "
    "local models first; that step was not run for these titles: flagged for the coordinator "
    "(re-draft with the local-models skill if required; the titles live in common/figures.py "
    "SPECS and docs/deck-figures/figures.csv).",
    "Arabic shaping is done by matplotlib 3.11 itself (bundled libraqm/HarfBuzz/SheenBidi); no "
    "reshaping package was added to pyproject.toml.",
    "Fonts: Noto Sans 2.015 and Noto Naskh Arabic 2.021 (OFL-1.1) in common/fonts/ with their OFL "
    "texts; SHA-256 and URLs in docs/licences.csv (R8 figure rows).",
]

# Ambiguities met while building each figure and the choice made (printed in the handoff).
CHOICES: dict[str, str] = {
    "fig01-national-map": "The brief names S6-L2 corridors and stations; S6-L2 is three station "
    "additions only, so the map also draws the two routed lines of S6-L1/S6-L3 (Al-Kharj spur, "
    "Riyadh belt 225) on the frozen v1 alignments (`kind == routed`, never alignments-v2), with "
    "each item's layout membership and phase in its label. Region and national outlines are "
    "simplified for display only (~1 km).",
    "fig02-screening-funnel": "Settlement universe = rows of cities/ksa/zones/settlements.parquet "
    "(OSM places + pilot rows); register = candidates.parquet; long/short list = R2 score summary; "
    "corridor candidates = YAML files under cities/ksa/corridors (R5 H4a regenerated set, not the "
    "R2 count of docs/candidates.md); CBA cases include the two-station Jubail variant.",
    "fig03-coverage-by-region": "Governorates per region are read from the generated Per-region "
    "table of docs/coverage.md (150, reconciled to GASTAT); counting distinct governorate names in "
    "candidates.parquet gives 151 (one name variant) and was not used.",
    "fig04-bcr-bands-by-family": "Basis = the docs/cba.md §9 ranking basis (UN WPP medium, 60 y, "
    "central rate case greenbook_2026 from each results.json). S5 BCRs with an unbounded P90 are "
    "drawn to the axis edge and marked; negative S5 BCRs are real (netted PVC) and read on NPV.",
    "fig05-programme-npv-ranges": "S1 is against S0 (R5 CBA) and the layouts are increments over "
    "S1 (judge v3), so they sit on separate panels. Layout ranges = npv_draws P10/P50/P90 at UN "
    "WPP medium; robust NPV (low population at P50 cost) marked separately.",
    "fig06-l1-p90-cost-risk": "S6-L2 and S6-L3 drawn faint beside S6-L1 for scale (all three "
    "against S1).",
    "fig07-pareto-front": "runs/r6/pareto_front.csv holds the R6 full-judge front (judge v2-p5b); "
    "v3 reproduces v2 exactly on the back-test, and the CP7 layouts match their front rows by "
    "robust NPV and capex. Front points show the medium-population NPV at P50 cost with a low–high "
    "population bar (the file has no P10/P90); the CP7 layouts carry P10/P90 of the draws and of "
    "capex. S6-L4/L5 are unlabelled front points. The v3 re-score (runs/r6/v3/rescore) was not "
    "plotted.",
    "fig08-reach-tradeoff": "Reach = access_gain_120 (A-r6-007, five metros); the national reach "
    "columns are reported-only (A-r6-104) and are not plotted. S6-L6 (R8_L6_PANEL) is read from "
    "runs/r6/l6/score/S6-L6.csv, never from top5.csv, and drawn as an open diamond: a "
    "connectivity comparison, not a search-front point.",
    "fig16-l6-connected-map": "The map is the existing optimise.connect output, embedded unchanged "
    "(Tariq, R8_L6_PANEL item 4: no new geometry); the scorecard and labels beside it are read "
    "from runs/r6/l6/score/S6-L6.csv.",
    "fig09-stage-gates": "Gate year = construction start = phase − START_LAG (optimise.layout, "
    "A-r6-002). The three station additions have identical standalone capex ranges in "
    "runs/r7/fiscal/fiscal.json (the same unit station cost), not a copying error.",
    "fig10-fiscal-exposure": "Population case = fiscal.json robust_case (un_wpp_low), as in "
    "docs/fiscal-exposure.md. S6-L2 has no demand-risk concession in fiscal.json: marked 'not "
    "assessed'. S1 baseline = baseline_s1 rows '<robust_case>|60'.",
    "fig11-vfm": "Bars are the expected values VfM is defined on; whiskers are the P10/P50/P90 of "
    "the same net fiscal cost series from fiscal.json, so every bar carries a range.",
    "fig12-isochrones": "No layout-level isochrone run exists; the Dhahran station addition "
    "(common to S6-L1, L2, L3) is the access run used, against S1, and Jeddah shows S0 vs S1. The "
    "matched baseline is drawn hatched (outline), the scenario filled. Isochrones are a "
    "deterministic network measure with no P10/P90.",
    "fig13-benchmark-cost-per-km": "Values via rail.benchmarks.normalised_rows (grade A–C, central "
    "conversion); rows without a known price year are not converted (count in the footer). This "
    "study's points = standalone judge v3 capex P10/P50/P90 ÷ routed length of the two routed "
    "CP7 lines; scope differs from the benchmarks.",
    "fig14-tornado-switching": "docs/cba.md §6 defines the tornado per case; S1 (the programme all "
    "layouts are measured against) and the Al-Kharj spur (the corridor behind S6-L1's P90 cost "
    "risk) are shown. These are R5 CBA cases, not judge v3 runs: a standalone appraisal with "
    "construction from 2027 (A-cba-301), not the spur's 2050 CP7 phase.",
    "fig15-capex-ranges": "S1 capex P10/P50/P90 = numpy percentiles of the 10,000 R5 draws "
    "(identical to the capex P10/P90 used in the S1 tornado); layouts = judge v3 capex quantiles. "
    "S1 is against S0, the layouts are increments.",
}


def labels_present(spec: Spec) -> str:
    out = ["synthetic", "provenance"] + (["judge-v3"] if "judge_v3" in spec.prov else [])
    if spec.screening:
        out.append("screening")
    if spec.quantity:
        out.append("alignment")
    if spec.is_map:
        out.append("osm")
    return ";".join(out)


def label_text(spec: Spec) -> str:
    parts = [LABEL, provenance(spec)]
    if spec.quantity:
        parts.append(ALIGNMENT_LIMITATION)
    if spec.is_map:
        parts.append(OSM_CREDIT)
    return " | ".join(parts)


def build_all(
    out: Path, deck: Path | None, seed: int, handoff: Path | None, only: list[str] | None = None
) -> list[tuple[Spec, Ctx]]:
    register_fonts()
    done: list[tuple[Spec, Ctx]] = []
    for spec in SPECS:
        if only and spec.stem not in only:
            continue
        fig, ctx, _ = render(spec, deck=False, seed=seed)
        save(fig, spec, ctx, out, deck=False)
        if deck is not None:
            fig_d, ctx_d, _ = render(spec, deck=True, seed=seed)
            save(fig_d, spec, ctx_d, deck, deck=True)
        done.append((spec, ctx))
    _write_index(out, done)
    if deck is not None:
        _write_deck_csv(deck, done)
    if handoff is not None:
        _write_handoff(handoff, done)
    return done


def _write_index(out: Path, done: list[tuple[Spec, Ctx]]) -> None:
    with (out / "figures-index.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(
            ["stem", "title_en", "caption", "sources", "provenance", "labels_present", "files"]
        )
        for spec, ctx in done:
            w.writerow(
                [
                    spec.stem,
                    spec.title_en,
                    spec.caption,
                    "; ".join(ctx.sources),
                    provenance(spec),
                    labels_present(spec),
                    f"{spec.stem}.svg; {spec.stem}.png",
                ]
            )


def _write_deck_csv(deck: Path, done: list[tuple[Spec, Ctx]]) -> None:
    with (deck / "figures.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["file", "title_en", "title_ar", "source_run_ids", "label"])
        for spec, ctx in done:
            w.writerow(
                [
                    f"{spec.stem}.png",
                    spec.title_en,
                    spec.title_ar,
                    "; ".join(ctx.sources),
                    label_text(spec),
                ]
            )


def _write_handoff(path: Path, done: list[tuple[Spec, Ctx]]) -> None:
    j = judge_info()
    lines = [
        "> **Document version:** logs/r8-figures-handoff.md v1.0 | 4 Nov 2026 | Author: "
        "report-writer (figures) | Status: draft",
        "",
        "# R8 figures handoff (generated by `uv run python -m common.figures build --handoff`)",
        "",
        f"Label on every figure: **{LABEL}**. Judge {j['name']} SHA-256 `{j['sha']}`, seed "
        f"{j['seed']}: printed only on figures built from judge v3 runs; every figure prints its "
        "own provenance (run family, code version, seed). Alignment limitation (figures with "
        "a length, cost, travel time or ridership): "
        f'"{ALIGNMENT_LIMITATION}". Maps: "{OSM_CREDIT}".',
        "",
        "Numbers below are printed at full rounding as shown on (or used by) the figure; cite them "
        "with the source run id listed for the figure. SAR million unless the key says otherwise.",
        "",
        "## General notes",
        "",
        *[f"- {n}" for n in GENERAL_NOTES],
        "",
    ]
    for spec, ctx in done:
        lines += [
            f"## {spec.stem}: {spec.title_en}",
            "",
            f"- Arabic title: {spec.title_ar}",
            f"- Caption: {spec.caption}",
            f"- Unit / basis: {ctx.unit}",
            f"- Sources: {'; '.join(f'`{s}`' for s in ctx.sources)}",
            f"- Provenance: {provenance(spec)}",
            f"- Labels present: {labels_present(spec)}",
        ]
        for n in ctx.notes:
            lines.append(f"- Note: {n}")
        if spec.stem in CHOICES:
            lines.append(f"- Ambiguity and choice made: {CHOICES[spec.stem]}")
        lines += ["", "| key | value |", "|---|---|"]
        lines += [f"| {k} | {v} |" for k, v in ctx.numbers]
        lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ------------------------------------------------------- Jeddah HHR detail (FIX_HHR_JEDDAH)
JEDDAH_EXTENT = (39.08, 21.43, 39.36, 21.76)  # lon/lat window: Al-Sulaimaniyah, junction, KAIA
STITCH_KM = 5.0  # a segment longer than this inside the window is drawn as a stitch (not a track)


HYPO_STYLE = {"color": "#1f77b4", "lw": 2.0, "ls": "-"}  # routed hypothetical corridor overlay


def jeddah_hhr_map(
    geojson: Path,
    out: Path,
    title: str,
    corridor: Path | None = None,
    extent: tuple[float, float, float, float] | None = None,
) -> dict[str, Any]:
    """Jeddah close-up of the HHR alignment in `geojson` (one feature, LineString or
    MultiLineString), with the committed/historical layers, the stations and the OSM credit.
    Segments over STITCH_KM inside the window are overdrawn in red and labelled: they join two
    vertices with no track between them. Returns the counts printed on the map.
    FIX_HHR_REROUTE (additive): `corridor` overlays a routed hypothetical alignment (the `routed`
    feature of a `cities/ksa/alignments/<id>.geojson`) and `extent` (w, s, e, n) widens the
    window; without them the output is unchanged."""
    from rail.osm import haversine_km

    register_fonts()
    w, s_, e, n = JEDDAH_EXTENT if extent is None else extent
    gj = json.loads(_p(geojson).read_text(encoding="utf-8"))
    f = gj["features"][0]
    g = f["geometry"]
    parts = [g["coordinates"]] if g["type"] == "LineString" else g["coordinates"]
    names = f["properties"].get("parts") or ["main"] * len(parts)
    fig, ax = plt.subplots(figsize=(7.5, 8.2))
    gpd.read_file(_p(ZONES / "regions.geojson")).boundary.plot(
        ax=ax, color="#9ab", lw=0.6, zorder=1
    )
    for layer in ("historical", "committed"):
        st = LAYER_STYLE[layer]
        gpd.read_file(_p(LINES / f"{layer}.geojson")).plot(
            ax=ax, color=st["color"], lw=st["lw"], ls=st["ls"], zorder=2
        )
    st = LAYER_STYLE["existing"]
    stitches = []
    for name, c in zip(names, parts, strict=True):
        xs, ys = [p[0] for p in c], [p[1] for p in c]
        ax.plot(xs, ys, color=st["color"], lw=2.2 if name == "main" else 1.8, zorder=3)
        if extent is not None:
            # wider windows hold long straight OSM ways: mark only true stitches (FIX_HHR_REROUTE)
            from rail.hhr_check import stitch_jumps

            true_stitch = {j["index"] for j in stitch_jumps(c, STITCH_KM)}
        for i, (a, b) in enumerate(zip(c, c[1:], strict=False)):
            inside = all(w <= q[0] <= e and s_ <= q[1] <= n for q in (a, b))
            km = haversine_km(a[1], a[0], b[1], b[0])
            if extent is not None and i not in true_stitch:
                continue
            if inside and km > STITCH_KM:
                stitches.append(km)
                ax.plot([a[0], b[0]], [a[1], b[1]], color="#d62728", lw=2.6, zorder=4)
                ax.annotate(
                    f"stitched segment {km:.1f} km:\nno track here",
                    ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2),
                    xytext=(-95, -10),
                    textcoords="offset points",
                    fontsize=8,
                    color="#d62728",
                    arrowprops={"arrowstyle": "-", "color": "#d62728", "lw": 0.8},
                )
    branch = [c for nm, c in zip(names, parts, strict=True) if nm == "branch"]
    for c in branch:
        ax.plot(*c[0], marker="D", ms=6, color="#ff7f0e", zorder=6)
        ax.annotate("junction", c[0], xytext=(8, -4), textcoords="offset points", fontsize=8)
    sta = gpd.read_file(_p(STATIONS))
    sta = sta.cx[w:e, s_:n]
    for r in sta.itertuples():
        col = LAYER_STYLE.get(r.layer, LAYER_STYLE["existing"])["color"]
        ax.plot(r.geometry.x, r.geometry.y, "o", ms=6, mfc="white", mec=col, mew=1.6, zorder=5)
        ax.annotate(
            f"{r.name_en} ({r.layer})",
            (r.geometry.x, r.geometry.y),
            xytext=(7, 4),
            textcoords="offset points",
            fontsize=8,
            zorder=7,
        )
    if extent is None:
        ax.annotate("to KAEC / Madinah", (39.25, n - 0.01), fontsize=8, ha="center", color="#333")
        ax.annotate("to Makkah", (e - 0.01, 21.47), fontsize=8, ha="right", color="#333")
    routed_km = None
    if corridor is not None:
        cg = json.loads(_p(corridor).read_text(encoding="utf-8"))
        rf = next(x for x in cg["features"] if x["properties"].get("kind") == "routed")
        rc = rf["geometry"]["coordinates"]
        ax.plot(
            [p[0] for p in rc],
            [p[1] for p in rc],
            color=HYPO_STYLE["color"],
            lw=HYPO_STYLE["lw"],
            ls=HYPO_STYLE["ls"],
            zorder=4,
        )
        routed_km = rf["properties"].get("length_km")
    ax.set_xlim(w, e)
    ax.set_ylim(s_, n)
    _aspect(ax, (s_ + n) / 2)
    ax.set_xlabel("longitude")
    ax.set_ylabel("latitude")
    ax.set_title(title, fontsize=10)
    handles = [
        Line2D(
            [],
            [],
            color=LAYER_STYLE[k]["color"],
            lw=LAYER_STYLE[k]["lw"],
            ls=LAYER_STYLE[k]["ls"],
            label=LAYER_NAME[k],
        )
        for k in ("existing", "committed", "historical")
    ]
    if corridor is not None:
        handles.insert(
            1,
            Line2D(
                [],
                [],
                color=HYPO_STYLE["color"],
                lw=HYPO_STYLE["lw"],
                ls=HYPO_STYLE["ls"],
                label=f"{LAYER_NAME['hypothetical']}: routed corridor, {routed_km} km",
            ),
        )
    if stitches:
        handles.append(Line2D([], [], color="#d62728", lw=2.6, label="stitched segment (no track)"))
    if branch:
        handles.append(Line2D([], [], marker="D", color="#ff7f0e", lw=0, label="branch junction"))
    ax.legend(
        handles=handles,
        loc="lower left" if extent is None else "upper left",
        bbox_to_anchor=None if extent is None else (1.02, 1.0),
        fontsize=7.5,
        title="rail layers (never mixed)",
        title_fontsize=8,
        frameon=True,
        framealpha=0.92,
    )
    km = [
        round(sum(haversine_km(a[1], a[0], b[1], b[0]) for a, b in zip(c, c[1:], strict=False)), 2)
        for c in parts
    ]
    foot = f"Alignment {geojson}: {g['type']}, parts {names}, km {km}. Lon/lat (EPSG:4326)."
    if corridor is not None:
        foot += (
            f"\nCorridor {corridor} (hypothetical, ours): indicative engineering sketch, not a "
            "design. Synthetic demand, uncalibrated: scenario comparison, not a forecast."
        )
    fig.text(0.01, 0.01 if corridor is None else -0.01, foot, fontsize=6.5)
    _osm(ax)
    out = _p(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=150, bbox_inches="tight", metadata={"Software": None})
    plt.close(fig)
    res = {"parts": names, "km": km, "stitches_km": [round(x, 2) for x in stitches]}
    if corridor is not None:
        res["corridor_km"] = routed_km
    return res


# ------------------------------------------------------------------ CLI
app: typer.Typer = make_app("common.figures", "Report and deck figures from run outputs.")


@app.command()
def build(
    ctx: typer.Context,
    out: Path = typer.Option(Path("docs/report/figures"), "--out"),
    deck: Path | None = typer.Option(None, "--deck", help="also write 16:9 deck figures here"),
    handoff: Path | None = typer.Option(None, "--handoff", help="write the numbers handoff here"),
    only: list[str] | None = typer.Option(None, "--only", help="render these stems only"),
) -> None:
    """Render every figure (SVG + PNG) from run outputs and registers."""
    seed = (ctx.obj or {}).get("seed") or 1
    done = build_all(out, deck, seed, handoff, only)
    typer.echo(f"wrote {len(done)} figures to {out}" + (f" and {deck}" if deck else ""))


@app.command("deck")
def deck_cmd(
    ctx: typer.Context,
    out: Path = typer.Option(Path("docs/deck-figures"), "--out"),
    report: Path = typer.Option(Path("docs/report/figures"), "--report"),
) -> None:
    """Render report and 16:9 deck figures together."""
    seed = (ctx.obj or {}).get("seed") or 1
    done = build_all(report, out, seed, None)
    typer.echo(f"wrote {len(done)} figures to {report} and {out}")


@app.command("list")
def list_cmd() -> None:
    """List figure stems and titles."""
    for s in SPECS:
        typer.echo(f"{s.stem}\t{s.title_en}")


@app.command("jeddah-hhr")
def jeddah_hhr_cmd(
    geojson: Path = typer.Option(LINES / "hhr.geojson", "--geojson"),
    out: Path = typer.Option(Path("docs/report/figures/hhr-jeddah-after.png"), "--out"),
    title: str = typer.Option("Haramain line in Jeddah", "--title"),
    corridor: Path = typer.Option(None, "--corridor", help="routed corridor GeoJSON to overlay"),
    extent: str = typer.Option("", "--extent", help="w,s,e,n (default: the Jeddah window)"),
) -> None:
    """Jeddah close-up of an HHR alignment file (FIX_HHR_JEDDAH before/after screenshots;
    FIX_HHR_REROUTE re-route maps with --corridor and --extent)."""
    ext = tuple(float(x) for x in extent.split(",")) if extent else None
    typer.echo(json.dumps(jeddah_hhr_map(geojson, out, title, corridor, ext)))  # type: ignore[arg-type]


if __name__ == "__main__":
    app()
