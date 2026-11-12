"""Shot rendering (R10 half 2) and the storyboard check.

CLI:
  uv run python -m film.render check film/storyboard/shots.yaml [--lines ...]   (= film.shots check)
  uv run python -m film.render shot sh-01-02 --lang en [--dur 12.3]
  uv run python -m film.render all --cut main --lang ar

How a shot is drawn (one engine for every renderer label in shots.yaml; the storyboard's
`deckgl_capture` / `manim` labels name the planned tools, see docs/film.md for the departure):
  1. Three 1920x1080 layers per shot and language, written as HTML with inline SVG and rendered
     by the local headless Google Chrome (the same approved tool as common.ar_render, so Arabic
     is shaped and right-to-left): A = context, B = the shot's data (highlighted lines, bars,
     card), O = transparent overlay (on-screen text, legend, footers, credits, labels).
  2. ffmpeg: A dissolves into B, a slow push-in moves the picture (never the overlay), the
     overlay sits on top, then H.264 1080p30.
Maps are drawn from the twin's own GeoJSON (cities/ksa/lines/geojson, alignments, regions);
on-screen figures are the storyboard's verified on_screen_text, and every number in it is
looked up in the shot's data_source files at render time (render manifest, `traced`).
Duration comes from the measured narration (film/voice/timing/<cut>-<lang>.csv) through the edit
list built by film.assemble; a shot without narration keeps its storyboard duration_s.
Output: film/renders/<cut>-<lang>/<shot>.mp4 (film/renders is a symlink to the external volume).
"""

from __future__ import annotations

import contextlib
import csv
import glob
import hashlib
import html
import json
import math
import os
import re
import subprocess
from pathlib import Path

import typer

from common import REPO_ROOT
from film.gate import require
from film.shots import load_shots, run_check

app = typer.Typer(add_completion=False, help="Shot renders (R10 half 2; gated).")

W, H, FPS = 1920, 1080, 30
SHOTS = REPO_ROOT / "film/storyboard/shots.yaml"
RENDERS = REPO_ROOT / "film/renders"
CHROME = os.environ.get(
    "CHROME_PATH", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
)
FONTS = REPO_ROOT / "common/fonts"
GEO = REPO_ROOT / "cities/ksa/lines/geojson"
DEM_DIR = Path(
    os.environ.get("FILM_DEM_DIR", "data/ksa/align/tiles/dem")
)  # cop-dem-glo30-align-3as-2026-11-01

COL = {
    "existing": "#1F4E79",
    "committed": "#D97706",
    "hypothetical": "#7C3AED",
    "historical": "#787878",
    "air": "#C9A3AE",
    "bg": "#F4F1EA",
    "land": "#FBFAF6",
    "ink": "#1B1B1B",
    "muted": "#5B5B5B",
    "teal": "#2A9D8F",
}
DASH = {"existing": "", "committed": "18 9", "hypothetical": "2 8", "historical": "1 10"}
LEGEND = {
    "en": [
        ("existing", "existing"),
        ("committed", "committed or under procurement"),
        ("hypothetical", "hypothetical (ours)"),
    ],
    "ar": [
        ("existing", "قائم"),
        ("committed", "ملتزم به أو قيد الطرح"),
        ("hypothetical", "افتراضي (من الدراسة)"),
    ],
}
FOOTER = {
    "en": (
        "synthetic demand, uncalibrated: scenario comparison, not a forecast",
        "not the official ranking",
    ),
    "ar": ("طلب تركيبي غير مُعايَر: مقارنة سيناريوهات، ليست توقعاً", "ليس الترتيب الرسمي"),
}
OSM = "© OpenStreetMap contributors"
COPERNICUS = (
    "produced using Copernicus WorldDEM-30 © DLR e.V. 2010-2014 and © Airbus Defence and Space "
    "GmbH 2014-2018 provided under COPERNICUS by the European Union and ESA; all rights reserved"
)
KSA_BBOX = (34.4, 16.2, 55.8, 32.3)  # lon0, lat0, lon1, lat1

# Map labels: script spellings (film/script/pronunciation.md) -> governorate point (coordinates
# from cities/ksa/zones/governorate_points.geojson, the twin's own zone points).
PLACES = {
    "Riyadh": ("الرياض", "Riyadh governorate"),
    "Jeddah": ("جدة", "Governorate of Jeddah"),
    "Makkah": ("مكة", "Makkah Al Mukarramah"),
    "Madinah": ("المدينة", "Al Madinah Al Munawwarah"),
    "Dammam": ("الدمام", "Dammam Governorate"),
    "Qurayyat": ("القريات", "Al Qurayyat"),
    "Abha": ("أبها", "Abha"),
    "Tabuk": ("تبوك", "Tabuk Governorate"),
    "Taif": ("الطائف", "Al Taif"),
    "Jazan": ("جازان", "Jazan"),
    "Najran": ("نجران", "Najran"),
    "Khamis Mushait": ("خميس مشيط", "Khamis Mushayt"),
    "Hail": ("حائل", "Hail"),
    "Qassim": ("القصيم", "Buraydah"),
    "Al-Kharj": ("الخرج", "Al Kharj"),
    "Al Jubayl": ("الجبيل", "Al Jubayl Governorate"),
    "Duruma": ("ضرما", "Duruma"),
    "Hofuf": ("الهفوف", "Al Ahsa Governorate"),
    "Al-Jumum": ("الجموم", "Al Jumum"),
}
METROS = ("Riyadh", "Jeddah", "Makkah", "Madinah", "Dammam")
BASE_NAMES = ("existing.geojson", "committed.geojson")
MAP_BOX = {"en": (40, 50, 1230, 870), "ar": (690, 50, 1880, 870)}


# ---------------------------------------------------------------- data helpers


def runs_root() -> Path:
    return Path(os.environ.get("RAILTWIN_RUNS_ROOT", REPO_ROOT / "runs"))


def resolve(token: str) -> list[Path]:
    """A data_source token -> existing files (runs/ through RAILTWIN_RUNS_ROOT)."""
    token = token.strip()
    if not token or token == "none":
        return []
    m = re.match(r"(.*riyadh-metro-l)(\d)\.geojson \.\. .*l(\d)\.geojson", token)
    if m:
        return [
            REPO_ROOT / f"{m.group(1)}{i}.geojson"
            for i in range(int(m.group(2)), int(m.group(3)) + 1)
        ]
    p = runs_root() / token[5:] if token.startswith("runs/") else REPO_ROOT / token.split(" ")[0]
    if p.is_dir():
        return sorted(
            Path(x) for x in glob.glob(str(p / "**/*"), recursive=True) if Path(x).is_file()
        )
    return [p] if p.exists() else []


def source_tokens(shot: dict) -> list[str]:
    return [t.strip() for t in re.split(r";", str(shot.get("data_source", ""))) if t.strip()]


def _geoms(path: Path) -> list[tuple[dict, dict]]:
    try:
        d = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    return [(f.get("properties") or {}, f.get("geometry") or {}) for f in d.get("features", [])]


def _parts(geom: dict) -> list[list[list[float]]]:
    t, c = geom.get("type"), geom.get("coordinates")
    if t == "LineString":
        return [c]
    if t in ("MultiLineString", "Polygon"):
        return list(c)
    if t == "MultiPolygon":
        return [ring for poly in c for ring in poly]
    return []


def place_xy() -> dict[str, tuple[float, float]]:
    pts = {
        f["properties"]["governorate"]: f["geometry"]["coordinates"]
        for f in json.loads(
            (REPO_ROOT / "cities/ksa/zones/governorate_points.geojson").read_text(encoding="utf-8")
        )["features"]
    }
    return {en: tuple(pts[gov]) for en, (_, gov) in PLACES.items() if gov in pts}


def layer_of(path: Path, props: dict) -> str:
    lay = str(props.get("layer", ""))
    if lay in DASH:
        return lay
    name = path.name
    if "historical" in name or "hejaz" in name:
        return "historical"
    if "alignments" in str(path) or name.startswith(("S2-", "S3-", "S4-", "RJ-")):
        return "hypothetical"
    if name in ("committed.geojson", "landbridge.geojson", "gcc-railway-ksa.geojson"):
        return "committed"
    return "existing"


def highlight_files(shot: dict) -> list[Path]:
    out: list[Path] = []
    for tok in source_tokens(shot):
        for p in resolve(tok):
            if p.suffix == ".geojson" and p.name not in ("regions.geojson", "stations.geojson"):
                out.append(p)
            elif p.suffix == ".yaml" and "layout" in p.name:
                out += layout_alignments(p)
    return out


def layout_alignments(path: Path) -> list[Path]:
    """Hypothetical corridors named in an R6 layout file -> their alignment GeoJSON."""
    text = path.read_text(encoding="utf-8")
    found = []
    for cid in sorted(set(re.findall(r"(S[2-4]-[a-z_]+-[a-z0-9-]+)", text))):
        for d in ("alignments-v2", "alignments"):
            p = REPO_ROOT / "cities/ksa" / d / f"{cid}.geojson"
            if p.exists():
                found.append(p)
                break
    return found


# ---------------------------------------------------------------- terrain (Copernicus GLO-30)


def hillshade_png(bbox: tuple[float, float, float, float], out: Path) -> Path | None:
    """Hillshade of the DEM windows inside bbox (lon0, lat0, lon1, lat1), grey on transparent."""
    if out.exists():
        return out
    import numpy as np
    import rasterio
    from PIL import Image
    from rasterio.merge import merge

    root = DEM_DIR if DEM_DIR.is_absolute() else REPO_ROOT / DEM_DIR
    files = []
    for f in glob.glob(str(root / "*.tif")):
        with rasterio.open(f) as s:
            b = s.bounds
        if b.right > bbox[0] and b.left < bbox[2] and b.top > bbox[1] and b.bottom < bbox[3]:
            files.append(f)
    if not files:
        return None
    res = max((bbox[2] - bbox[0]) / 1400, 0.0015)
    srcs = [rasterio.open(f) for f in files]
    try:
        arr, _ = merge(srcs, bounds=bbox, res=res, nodata=np.nan)
    finally:
        for s in srcs:
            s.close()
    z = arr[0].astype("float64")
    mask = np.isnan(z)
    zf = np.where(mask, np.nanmean(z), z)
    dy, dx = np.gradient(
        zf, res * 111_000, res * 111_000 * math.cos(math.radians(sum(bbox[1::2]) / 2))
    )
    slope = np.arctan(np.hypot(dx, dy) * 4.0)  # vertical exaggeration x4 (display only)
    aspect = np.arctan2(-dx, dy)
    az, alt = math.radians(315), math.radians(45)
    shade = np.sin(alt) * np.cos(slope) + np.cos(alt) * np.sin(slope) * np.cos(az - aspect)
    flat = math.sin(alt)
    g = np.where(shade < flat, 40, 255).astype("uint8")  # shadow dark, lit side light
    alpha = np.clip(np.abs(shade - flat) * 520, 0, 170)
    alpha = np.where(mask, 0, alpha).astype("uint8")  # flat ground and sea stay clear
    img = Image.fromarray(np.dstack([g, g, g, alpha]), "RGBA")
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out)
    return out


# ---------------------------------------------------------------- SVG drawing


class Proj:
    def __init__(self, bbox: tuple[float, float, float, float], box=(60, 60, 1860, 900)):
        lon0, lat0, lon1, lat1 = bbox
        self.k = math.cos(math.radians((lat0 + lat1) / 2))
        x0, y0, x1, y1 = box
        sx = (x1 - x0) / ((lon1 - lon0) * self.k)
        sy = (y1 - y0) / (lat1 - lat0)
        self.s = min(sx, sy)
        cx, cy = (lon0 + lon1) / 2, (lat0 + lat1) / 2
        self.ox = (x0 + x1) / 2 - cx * self.k * self.s
        self.oy = (y0 + y1) / 2 + cy * self.s
        self.bbox = bbox
        self.box = box

    def __call__(self, lon: float, lat: float) -> tuple[float, float]:
        return lon * self.k * self.s + self.ox, self.oy - lat * self.s

    def extent(self) -> tuple[float, float, float, float]:
        """Lon/lat of the whole frame (for the hillshade image)."""
        lon0 = (0 - self.ox) / (self.k * self.s)
        lon1 = (W - self.ox) / (self.k * self.s)
        lat1 = (self.oy - 0) / self.s
        lat0 = (self.oy - H) / self.s
        return lon0, lat0, lon1, lat1


def path_d(proj: Proj, coords: list[list[float]], close: bool = False) -> str:
    pts = [proj(c[0], c[1]) for c in coords if len(c) >= 2]
    if len(pts) < 2:
        return ""
    d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return d + (" Z" if close else "")


def line_svg(proj: Proj, path: Path, width: float, opacity: float = 1.0) -> str:
    out = []
    for props, geom in _geoms(path):
        lay = layer_of(path, props)
        dash = DASH[lay]
        attrs = f'stroke="{COL[lay]}" stroke-width="{width}" fill="none" opacity="{opacity}"'
        attrs += ' stroke-linecap="round" stroke-linejoin="round"'
        if dash:
            attrs += f' stroke-dasharray="{dash}"'
        for part in _parts(geom):
            d = path_d(proj, part)
            if d:
                out.append(f'<path d="{d}" {attrs}/>')
    return "\n".join(out)


def bbox_of(paths: list[Path], pad: float = 0.25) -> tuple[float, float, float, float] | None:
    xs, ys = [], []
    for p in paths:
        for _, g in _geoms(p):
            for part in _parts(g):
                for c in part:
                    xs.append(c[0])
                    ys.append(c[1])
    if not xs:
        return None
    w, h = max(xs) - min(xs), max(ys) - min(ys)
    m = max(w, h) * pad + 0.3
    return min(xs) - m, min(ys) - m, max(xs) + m, max(ys) + m


def shot_places(shot: dict) -> list[str]:
    text = " ".join(str(v) for v in (shot.get("on_screen_text") or {}).values())
    text += " " + str(shot.get("visual", ""))
    names = [en for en, (ar, _) in PLACES.items() if en in text or ar in text]
    return names


def map_bbox(shot: dict, hl: list[Path]) -> tuple[float, float, float, float]:
    vis = str(shot.get("visual", "")).lower()
    if "national" in vis and not shot_places(shot):
        return KSA_BBOX
    xy = place_xy()
    b = bbox_of([p for p in hl if p.name not in BASE_NAMES])
    pts = [xy[n] for n in shot_places(shot) if n in xy]
    if b is None and not pts:
        return KSA_BBOX
    lons = [p[0] for p in pts] + ([b[0], b[2]] if b else [])
    lats = [p[1] for p in pts] + ([b[1], b[3]] if b else [])
    lon0, lon1, lat0, lat1 = min(lons), max(lons), min(lats), max(lats)
    if (lon1 - lon0) > 14 or (lat1 - lat0) > 11:
        return KSA_BBOX
    m = 0.6
    return lon0 - m, lat0 - m, lon1 + m, lat1 + m


def map_svg(shot: dict, lang: str, full: bool, assets: Path) -> str:
    hl = highlight_files(shot)
    bbox = map_bbox(shot, hl)
    proj = Proj(bbox, box=MAP_BOX[lang])
    parts = [f'<rect width="{W}" height="{H}" fill="{COL["bg"]}"/>']
    for _, g in _geoms(REPO_ROOT / "cities/ksa/zones/regions.geojson"):
        for ring in _parts(g):
            d = path_d(proj, ring, close=True)
            if d:
                parts.append(
                    f'<path d="{d}" fill="{COL["land"]}" stroke="#C9C2B4" stroke-width="1.2"/>'
                )
    if shot.get("extra_credit"):
        lon0, lat0, lon1, lat1 = proj.extent()
        tag = hashlib.sha1(repr(bbox).encode()).hexdigest()[:10]
        hs = hillshade_png((lon0, lat0, lon1, lat1), assets / f"hillshade-{tag}.png")
        if hs:
            parts.append(f'<image href="{hs.as_uri()}" x="0" y="0" width="{W}" height="{H}"/>')
    base = [GEO / "existing.geojson", GEO / "committed.geojson"]
    for p in base:
        parts.append(line_svg(proj, p, 3.0, 0.55 if full else 0.85))
    if full:
        for p in hl:
            if p.name in ("existing.geojson", "committed.geojson") and len(hl) > 1:
                continue
            parts.append(line_svg(proj, p, 7.0))
    xy = place_xy()
    names = list(dict.fromkeys([*shot_places(shot), *METROS]))
    taken: list[tuple[float, float, float, float]] = []
    for n in names:
        if n not in xy:
            continue
        x, y = proj(*xy[n])
        if not (0 < x < W and 0 < y < H):
            continue
        big = n in shot_places(shot)
        r = 9 if big else 6
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{COL["ink"]}"/>')
        label = PLACES[n][0] if lang == "ar" else n
        size = 30 if big else 22
        anchor = "end" if lang == "ar" else "start"
        dx = -14 if lang == "ar" else 14
        tw = len(label) * size * 0.55
        # candidate spots next to the point: before/after side, above/below; first free wins
        side = -1 if lang == "ar" else 1
        spots = [
            (side, -10),
            (side, size + 4),
            (-side, -10),
            (-side, size + 4),
            (0, -16),
            (0, size + 14),
        ]
        for sx, oy in spots:
            ax = x + sx * 14
            anchor = "middle" if sx == 0 else ("end" if sx < 0 else "start")
            bx0 = ax - tw / 2 if sx == 0 else (ax - tw if sx < 0 else ax)
            ly = y + oy
            box = (bx0, ly - size, bx0 + tw, ly + 4)
            if not any(
                box[0] < b[2] and b[0] < box[2] and box[1] < b[3] and b[1] < box[3] for b in taken
            ):
                break
        dx = ax - x
        taken.append(box)
        parts.append(
            f'<text x="{x + dx:.1f}" y="{ly:.1f}" font-size="{size}" text-anchor="{anchor}" '
            f'fill="{COL["ink"]}" class="lbl" direction="{"rtl" if lang == "ar" else "ltr"}">'
            f"{html.escape(label)}</text>"
        )
    if full and "air" in str(shot.get("visual", "")).lower() and "Riyadh" in xy and "Jeddah" in xy:
        (x1, y1), (x2, y2) = proj(*xy["Riyadh"]), proj(*xy["Jeddah"])
        cx, cy = (x1 + x2) / 2, min(y1, y2) - 160
        parts.append(
            f'<path d="M{x1:.1f},{y1:.1f} Q{cx:.1f},{cy:.1f} {x2:.1f},{y2:.1f}" '
            f'stroke="{COL["air"]}" stroke-width="5" fill="none"/>'
        )
        parts.append(
            f'<text x="{cx:.1f}" y="{cy + 70:.1f}" font-size="26" text-anchor="middle" '
            f'fill="{COL["muted"]}">{"جوّي" if lang == "ar" else "air"}</text>'
        )
    return "\n".join(parts)


NUM = re.compile(r"[−+-]?\d[\d,]*(?:\.\d+)?")
RANGE = re.compile(r"([−+-]?\d[\d,]*(?:\.\d+)?)\s*(?:to|–|-|و)\s*([−+]?\d[\d,]*(?:\.\d+)?)")


def _num(s: str) -> float:
    return float(s.replace("−", "-").replace(",", ""))


def chart_svg(shot: dict, lang: str, full: bool) -> str:
    """Range bars parsed from the (verified) English on-screen text; a zero line when signed."""
    en = str((shot.get("on_screen_text") or {}).get("en", ""))
    parts = [f'<rect width="{W}" height="{H}" fill="{COL["bg"]}"/>']
    ranges = [(_num(a), _num(b)) for a, b in RANGE.findall(en)]
    ranges = [(min(a, b), max(a, b)) for a, b in ranges if a != b]
    if not ranges:
        nums = [_num(n) for n in NUM.findall(en) if not re.fullmatch(r"(19|20)\d\d", n)]
        nums = [n for n in nums if n != 0][:4]
        if nums and full:
            top = max(abs(n) for n in nums)
            for i, n in enumerate(nums):
                y = 300 + i * 110
                w = 1300 * abs(n) / top
                parts.append(
                    f'<rect x="300" y="{y}" width="{w:.0f}" height="60" rx="6" '
                    f'fill="{COL["teal"]}" opacity="0.85"/>'
                )
                parts.append(
                    f'<text x="{300 + w + 20:.0f}" y="{y + 44}" font-size="36" fill="{COL["ink"]}" '
                    f'direction="ltr">{n:,.10g}</text>'
                )
        return "\n".join(parts)
    lo = min(0.0, min(a for a, _ in ranges))
    hi = max(0.0, max(b for _, b in ranges))
    span = (hi - lo) or 1.0
    x0, x1 = 260, 1660

    def X(v: float) -> float:
        return x0 + (v - lo) / span * (x1 - x0)

    parts.append(f'<line x1="{x0}" y1="640" x2="{x1}" y2="640" stroke="#999" stroke-width="2"/>')
    if lo < 0 < hi:
        parts.append(
            f'<line x1="{X(0):.0f}" y1="240" x2="{X(0):.0f}" y2="660" stroke="{COL["ink"]}" '
            f'stroke-width="4"/><text x="{X(0):.0f}" y="700" font-size="30" text-anchor="middle" '
            f'direction="ltr">0</text>'
        )
    for i, (a, b) in enumerate(ranges[:4]):
        y = 280 + i * 90
        if full:
            hatched = "indicative" in en.lower() and i == 0
            fill = "#9E9E9E" if hatched else COL["teal"]
            parts.append(
                f'<rect x="{X(a):.0f}" y="{y}" width="{max(X(b) - X(a), 6):.0f}" '
                'height="54" rx="6" '
                f'fill="{fill}" opacity="0.85"/>'
            )
            for v, anc, dx in ((a, "end", -12), (b, "start", 12)):
                parts.append(
                    f'<text x="{X(v) + dx:.0f}" y="{y + 39}" font-size="32" text-anchor="{anc}" '
                    f'fill="{COL["ink"]}" direction="ltr">{v:,.10g}</text>'
                )
    return "\n".join(parts)


def archival_svg(shot: dict, full: bool, assets: Path) -> str:
    imgs = sorted((assets / "archival").glob("loc-*.jpg"))
    parts = [f'<rect width="{W}" height="{H}" fill="#111"/>']
    if imgs:
        img = imgs[1 if full and len(imgs) > 1 else 0]
        parts.append(
            f'<image href="{img.as_uri()}" x="160" y="40" width="1600" height="640" '
            'preserveAspectRatio="xMidYMid meet" filter="url(#sepia)"/>'
        )
    return "\n".join(parts)


# ---------------------------------------------------------------- HTML pages


def font_css() -> str:
    faces = []
    for fam, files in (
        ("Noto Naskh Arabic", ("NotoNaskhArabic-Regular.ttf", "NotoNaskhArabic-Bold.ttf")),
        ("Noto Sans", ("NotoSans-Regular.ttf", "NotoSans-Bold.ttf")),
    ):
        for weight, f in zip((400, 700), files, strict=True):
            faces.append(
                f"@font-face{{font-family:'{fam}';font-weight:{weight};"
                f"src:url('{(FONTS / f).as_uri()}')}}"
            )
    return "".join(faces)


def page(body: str, transparent: bool, lang: str) -> str:
    bg = "transparent" if transparent else COL["bg"]
    return f"""<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><style>
{font_css()}
html,body{{margin:0;width:{W}px;height:{H}px;overflow:hidden;background:{bg};}}
body{{font-family:'Noto Sans','Noto Naskh Arabic',sans-serif;color:{COL["ink"]};
  letter-spacing:normal}}
[lang=ar],.ar{{font-family:'Noto Naskh Arabic','Noto Sans',serif}}
svg text{{font-family:'Noto Sans','Noto Naskh Arabic',sans-serif}}
.cap{{position:absolute;left:80px;right:80px;bottom:120px;font-size:40px;line-height:1.35;
  background:rgba(255,255,255,.92);padding:20px 30px;border-radius:10px}}
.side{{position:absolute;top:200px;width:560px;font-size:38px;line-height:1.38;
  background:rgba(255,255,255,.94);padding:24px 30px;border-radius:10px}}
.card{{position:absolute;left:160px;right:160px;top:260px;font-size:58px;line-height:1.4;
  text-align:center}}
.title{{position:absolute;left:120px;right:120px;top:380px;font-size:80px;font-weight:700;
  text-align:center;line-height:1.3}}
.src{{font-size:26px;color:{COL["muted"]};margin-top:8px}}
.foot{{position:absolute;left:40px;bottom:22px;font-size:24px;line-height:1.35;
  background:rgba(255,255,255,.88);padding:6px 12px;border-radius:6px;max-width:1100px}}
.cred{{position:absolute;right:40px;bottom:22px;font-size:20px;color:#333;text-align:right;
  background:rgba(255,255,255,.88);padding:6px 12px;border-radius:6px;max-width:720px}}
.leg{{position:absolute;bottom:190px;font-size:24px;background:rgba(255,255,255,.92);
  padding:10px 16px;border-radius:8px}}
.leg div{{display:flex;align-items:center;gap:12px;margin:4px 0}}
.comp{{position:absolute;top:36px;font-size:28px;background:{COL["ink"]};color:#fff;
  padding:8px 16px;border-radius:6px}}
.q{{font-style:italic}}
</style></head><body>{body}</body></html>"""


def legend_html(lang: str) -> str:
    rows = []
    for lay, label in LEGEND[lang]:
        dash = DASH[lay]
        svg = (
            f'<svg width="70" height="14"><line x1="2" y1="7" x2="68" y2="7" stroke="{COL[lay]}" '
            f'stroke-width="6" stroke-linecap="round"'
            + (f' stroke-dasharray="{dash}"' if dash else "")
            + "/></svg>"
        )
        rows.append(f"<div>{svg}<span>{html.escape(label)}</span></div>")
    side = "left:60px" if lang == "ar" else "right:60px"
    d = "rtl" if lang == "ar" else "ltr"
    return f'<div class="leg" dir="{d}" style="{side}">{"".join(rows)}</div>'


def overlay_body(shot: dict, lang: str) -> str:
    d = "rtl" if lang == "ar" else "ltr"
    text = str((shot.get("on_screen_text") or {}).get(lang, ""))
    typ = shot.get("type")
    quote = bool((shot.get("quote_label") or {}).get(lang))
    body = html.escape(text).replace(" · ", "<br>")
    if quote:
        body = f'<span class="q">{body}</span>'
    out = []
    cap = shot.get("source_caption") or {}
    src = f'<div class="src">{html.escape(str(cap.get(lang, "")))}</div>' if cap else ""
    arch = shot.get("archival_credit")
    if arch:
        val = arch.get(lang, "") if isinstance(arch, dict) else str(arch)
        src += f'<div class="src">{html.escape(str(val))}</div>'
    if typ == "title" and shot.get("id") == "sh-08-14":
        out.append(credits_roll_html(lang))
    elif typ == "title":
        out.append(f'<div class="title" dir="{d}">{body}{src}</div>')
    elif typ in ("text_card",) and not shot.get("held_frame_from"):
        out.append(f'<div class="card" dir="{d}">{body}{src}</div>')
    elif typ in ("map_animation", "split_screen") or shot.get("held_frame_from"):
        side = "left:60px" if lang == "ar" else "right:60px"
        out.append(f'<div class="side" dir="{d}" style="{side}">{body}{src}</div>')
    else:
        out.append(f'<div class="cap" dir="{d}">{body}{src}</div>')
    if shot.get("layer_legend"):
        out.append(legend_html(lang))
    comp = shot.get("composite_label")
    if comp:
        side = "left:60px" if lang == "ar" else "right:60px"
        out.append(
            f'<div class="comp" dir="{d}" style="{side}">{html.escape(str(comp[lang]))}</div>'
        )
    foot = shot.get("footer")
    if foot in ("synthetic", "synthetic+not_official"):
        lines = [FOOTER[lang][0]] + ([FOOTER[lang][1]] if foot == "synthetic+not_official" else [])
        out.append(f'<div class="foot" dir="{d}">{"<br>".join(map(html.escape, lines))}</div>')
    creds = []
    if shot.get("osm_credit"):
        creds.append(OSM)
    if shot.get("extra_credit"):
        creds.append(COPERNICUS)
    if shot.get("ai_generated"):
        creds.append(str(shot.get("ai_label")))
    if creds:
        out.append(f'<div class="cred" dir="ltr">{"<br>".join(map(html.escape, creds))}</div>')
    return "\n".join(out)


def credits_roll_html(lang: str) -> str:
    """The closing credits card (sh-08-14); text from credits_lines()."""
    lines = credits_lines(lang)
    body = "".join(
        f"<div>{ltr_isolate(html.escape(x)) if lang == 'ar' else html.escape(x)}</div>"
        for x in lines
    )
    d = "rtl" if lang == "ar" else "ltr"
    return (
        f'<div dir="{d}" style="position:absolute;left:200px;right:200px;top:70px;'
        f'font-size:27px;line-height:1.45;text-align:center">{body}</div>'
    )


def ltr_isolate(text: str) -> str:
    """Wrap Latin runs in an Arabic line in LTR isolates (bdi dir=ltr)."""
    return re.sub(
        r"([A-Za-z©][A-Za-z0-9©().,;:&'/_ -]*[A-Za-z0-9)])",
        lambda m: f'<bdi dir="ltr">{m.group(1)}</bdi>',
        text,
    )


def credits_lines(lang: str) -> list[str]:
    """Closing credits: fixed lines (Nabrah, Claude, KSA Rail Twin, data credits) plus the rows of
    film/rights_log.csv with status `used` that the delivered film shows or depends on (fonts,
    archival images, tools), named from the register's item and attribution columns. The full
    register is docs/credits.md and film/rights_log.csv (named on the card)."""
    rows = list(csv.DictReader((REPO_ROOT / "film/rights_log.csv").open(encoding="utf-8")))
    used = [r for r in rows if r["status"] == "used"]
    fonts = [r["item"] for r in used if r["type"] == "font"]
    images = sorted({r["attribution"].strip() for r in used if r["type"] == "image"})
    tools = [
        r["item"].split(" (")[0]
        for r in used
        if r["type"] == "tool" and ("render" in r["used_in"] or "encode" in r["used_in"])
    ]
    if lang == "en":
        return [
            "KSA Rail Twin: a research film, not an official film of any ministry or company",
            "Synthetic demand, uncalibrated: a scenario comparison, not a forecast.",
            "Voices: ElevenLabs voice George (English); Nabrah public voices Daniah, Norah, "
            "Abdullah (Arabic)",
            "Built with Claude (Anthropic)",
            "Map data © OpenStreetMap contributors (ODbL); statistics: GASTAT (derived tables)",
            "SAR / HHR published facts; OAG; GACA",
            COPERNICUS,
            "Copernicus data is provided without liability for its use",
            "Archival photographs: " + "; ".join(images) + " (public domain)",
            "Fonts: " + ", ".join(fonts) + " (SIL OFL 1.1)",
            "Tools: " + ", ".join(tools),
            "Full credits and licences: docs/credits.md and film/rights_log.csv",
        ]
    return [
        "التوأم الرقمي للسكك الحديدية في السعودية: فيلم بحثي، مو فيلم رسمي لأي وزارة أو شركة",
        FOOTER["ar"][0] + ".",
        # FIX_FILM_STORY (Tariq, 10 Nov 2026): George does not speak in the Arabic cut.
        "الأصوات: نبرة (الأصوات العامة دانية ونورة وعبدالله)",
        "بُني باستخدام Claude (Anthropic)",
        "بيانات الخرائط: © OpenStreetMap contributors (ODbL)؛ "
        "الإحصاءات: الهيئة العامة للإحصاء (جداول مشتقة)",
        "معلومات منشورة من سار وقطار الحرمين؛ OAG؛ الهيئة العامة للطيران المدني",
        COPERNICUS,
        "Copernicus data is provided without liability for its use",
        "صور أرشيفية: " + "; ".join(images) + " (public domain)",
        "الخطوط: " + ", ".join(fonts) + " (SIL OFL 1.1)",
        "الأدوات: " + ", ".join(tools),
        "القائمة الكاملة: docs/credits.md و film/rights_log.csv",
    ]


def chrome_png(html_text: str, png: Path, transparent: bool) -> None:
    png.parent.mkdir(parents=True, exist_ok=True)
    src = png.with_suffix(".html")
    src.write_text(html_text, encoding="utf-8")
    args = [
        CHROME,
        "--headless=new",
        "--disable-gpu",
        "--hide-scrollbars",
        "--force-device-scale-factor=1",
        f"--window-size={W},{H}",
        "--allow-file-access-from-files",
        f"--screenshot={png}",
    ]
    if transparent:
        args.append("--default-background-color=00000000")
    subprocess.run([*args, src.as_uri()], check=True, capture_output=True, timeout=120)


def picture_svg(shot: dict, lang: str, full: bool, assets: Path) -> str:
    typ = shot.get("type")
    if typ in ("map_animation", "split_screen") or shot.get("held_frame_from"):
        src = shot
        if shot.get("held_frame_from"):
            src = SHOT_INDEX.get(shot["held_frame_from"][0], shot) | {
                "on_screen_text": shot["on_screen_text"]
            }
        return map_svg(src, lang, full, assets)
    if typ == "chart":
        return chart_svg(shot, lang, full)
    if typ == "archival":
        return archival_svg(shot, full, assets)
    return f'<rect width="{W}" height="{H}" fill="{"#111" if typ == "title" else COL["bg"]}"/>'


SHOT_INDEX: dict[str, dict] = {}


def build_layers(shot: dict, lang: str, outdir: Path, assets: Path) -> dict[str, Path]:
    defs = (
        '<defs><filter id="sepia"><feColorMatrix type="matrix" values="0.39 0.77 0.19 0 0 '
        '0.35 0.69 0.17 0 0 0.27 0.53 0.13 0 0 0 0 0 1 0"/></filter></defs>'
    )
    out = {}
    for key, full in (("A", False), ("B", True)):
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}">{defs}'
        svg += picture_svg(shot, lang, full, assets) + "</svg>"
        p = outdir / f"{shot['id']}.{key}.png"
        chrome_png(page(svg, False, lang), p, False)
        out[key] = p
    o = outdir / f"{shot['id']}.O.png"
    chrome_png(page(overlay_body(shot, lang), True, lang), o, True)
    out["O"] = o
    if shot.get("type") == "title":
        dark = "<style>body{color:#fff}.title{color:#fff}</style>"
        chrome_png(page(dark + overlay_body(shot, lang), True, lang), o, True)
    return out


# ---------------------------------------------------------------- figure tracing


def _variants(tok: str) -> set[str]:
    t = tok.replace("−", "-").lstrip("+-")
    out = {t, t.replace(",", "")}
    if "," in t:
        out.add(t.replace(",", " "))
    try:
        v = float(t.replace(",", ""))
    except ValueError:
        return out
    out |= {f"{v:g}", f"{v:,.0f}" if v >= 1000 else f"{v:g}", f"{v:.1f}", f"{v:.2f}"}
    if v >= 1_000_000:
        out |= {f"{v / 1e6:.2f}", f"{v / 1e6:.1f}"}
    return out


def source_text(shot: dict) -> str:
    chunks = []
    ids = []
    for tok in source_tokens(shot):
        if re.match(r"^[SA]-[\w-]+$", tok):
            ids.append(tok)
            continue
        for p in resolve(tok):
            if p.suffix in (".png", ".parquet", ".jpg") or p.stat().st_size > 30_000_000:
                continue
            with contextlib.suppress(OSError):
                chunks.append(p.read_text(encoding="utf-8", errors="ignore"))
    if ids:
        for f in (
            glob.glob(str(REPO_ROOT / "docs/sources/*.csv"))
            + glob.glob(str(REPO_ROOT / "docs/assumptions*.md"))
            + [str(REPO_ROOT / "film/assumptions-r10.md")]
        ):
            for line in Path(f).read_text(encoding="utf-8", errors="ignore").splitlines():
                if any(line.startswith((i + ",", f'"{i}",')) or f"| {i} |" in line for i in ids):
                    chunks.append(line)
    return "\n".join(chunks)


SRC_NUM = re.compile(r"[-−]?\d[\d,]*(?:\.\d+)?(?:[eE][-+]?\d+)?")


def _value_match(tok: str, values: list[float]) -> bool:
    """A decimal token equals some source value rounded at the token's precision, with the same
    sign, at unit scale 1, 1e3, 1e6 or 1e9 (run files hold millions where the screen says
    billions). Integers and years must match as text (see _variants)."""
    t = tok.replace("−", "-").replace(",", "").lstrip("+")
    if "." not in t:
        return False
    want = float(t)
    dec = len(t.split(".")[1])
    for v in values:
        for scale in (1.0, 1e3, 1e6, 1e9):
            if round(v / scale, dec) == want:
                return True
    return False


def trace_figures(shot: dict) -> tuple[list[str], list[str]]:
    """Every number in the EN on-screen text, found / not found in the shot's data sources
    (as text, or by value at the token's precision and a 1/1e3/1e6/1e9 unit scale)."""
    en = str((shot.get("on_screen_text") or {}).get("en", ""))
    text = source_text(shot)
    values = []
    for s in SRC_NUM.findall(text):
        with contextlib.suppress(ValueError):
            values.append(float(s.replace("−", "-").replace(",", "")))
    found, missing = [], []
    for tok in NUM.findall(en):
        if re.fullmatch(r"\d", tok.lstrip("+-−")):
            continue
        if any(v and v in text for v in _variants(tok)) or _value_match(tok, values):
            found.append(tok)
        else:
            missing.append(tok)
    return found, missing


# ---------------------------------------------------------------- encoding


def encode(layers: dict[str, Path], dur: float, out: Path, transition: str) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    n = max(int(round(dur * FPS)), 1)
    x = min(max(dur * 0.25, 0.4), 2.5)
    fade = 0.4 if any(k in transition for k in ("fade", "dissolve")) else 0.0
    zoom = (
        f"zoompan=z='1+0.035*on/{n}':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
        f":s={W}x{H}:fps={FPS}"
    )
    flt = (
        f"[0:v]fps={FPS},format=yuv420p[a];[1:v]fps={FPS},format=yuv420p[b];"
        f"[a][b]xfade=transition=fade:duration={min(1.0, dur / 3):.2f}:offset={x:.2f}[ab];"
        f"[ab]{zoom}[z];[z][2:v]overlay=0:0:shortest=0,format=yuv420p"
    )
    if fade:
        flt += f",fade=t=in:st=0:d={fade}"
    flt += f",trim=duration={dur:.3f}[v]"
    loop = ["-loop", "1", "-framerate", str(FPS), "-t", f"{dur + 1:.3f}", "-i"]
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y"]
    cmd += loop + [str(layers["A"])] + loop + [str(layers["B"])] + loop + [str(layers["O"])]
    cmd += ["-filter_complex", flt, "-map", "[v]", "-r", str(FPS), "-c:v", "libx264"]
    cmd += ["-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", "-an", str(out)]
    subprocess.run(cmd, check=True)


def shot_durations(cut: str, lang: str) -> dict[str, float]:
    """Durations from the edit list written by film.assemble edl (measured narration)."""
    p = REPO_ROOT / f"film/assemble/edl-{cut}-{lang}.csv"
    if not p.exists():
        return {}
    with p.open(encoding="utf-8", newline="") as fh:
        return {r["shot_id"]: float(r["duration_s"]) for r in csv.DictReader(fh)}


def render_one(shot: dict, lang: str, dur: float) -> dict:
    cut = shot["cut"]
    outdir = RENDERS / f"{cut}-{lang}"
    mp4 = outdir / f"{shot['id']}.mp4"
    if shot.get("renderer") == "sim_map":  # FIX_HALF2_QUALITY: moving map, film/sim.py
        from film import sim

        tmp = mp4.with_suffix(".new.mp4")
        sim.render_shot(shot, lang, dur, tmp)
        tmp.replace(mp4)  # the old card render is kept until its replacement exists
    else:
        layers = build_layers(shot, lang, outdir / "frames", RENDERS / "_assets")
        encode(layers, dur, mp4, str(shot.get("transition", "")))
    found, missing = trace_figures(shot)
    return {
        "shot_id": shot["id"],
        "cut": cut,
        "lang": lang,
        "type": shot.get("type"),
        "duration_s": f"{dur:.3f}",
        "output": str(mp4.relative_to(REPO_ROOT)),
        "footer": shot.get("footer"),
        "osm_credit": shot.get("osm_credit"),
        "copernicus": bool(shot.get("extra_credit")),
        "figures_traced": " ".join(found),
        "figures_not_found": " ".join(missing),
    }


MANIFEST_FIELDS = [
    "shot_id",
    "cut",
    "lang",
    "type",
    "duration_s",
    "output",
    "footer",
    "osm_credit",
    "copernicus",
    "figures_traced",
    "figures_not_found",
]


def write_manifest(rows: list[dict], cut: str, lang: str) -> Path:
    p = REPO_ROOT / f"film/assemble/renders-{cut}-{lang}.csv"
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=MANIFEST_FIELDS)
        w.writeheader()
        w.writerows(rows)
    return p


# ---------------------------------------------------------------- CLI


@app.callback()
def _main() -> None:
    """Shot renders (R10 half 2; gated)."""


@app.command()
def check(
    shots_yaml: Path,
    lines: Path | None = typer.Option(None, "--lines", help="lines.csv to check narration ids"),
) -> None:
    """Validate the shot list (same as film.shots check)."""
    code = run_check(shots_yaml, lines)
    if code:
        raise typer.Exit(code)


def _index() -> list[dict]:
    shots = load_shots(SHOTS)
    SHOT_INDEX.clear()
    SHOT_INDEX.update({s["id"]: s for s in shots})
    return shots


@app.command()
def shot(
    shot_id: str,
    lang: str = typer.Option(..., "--lang"),
    dur: float = typer.Option(0.0, "--dur", help="override duration (s)"),
) -> None:
    """Render one shot for one language."""
    shots = _index()
    s = SHOT_INDEX.get(shot_id)
    if s is None:
        typer.echo(f"unknown shot {shot_id}")
        raise typer.Exit(1)
    d = dur or shot_durations(s["cut"], lang).get(shot_id) or float(s["duration_s"])
    require(int(d * 1.2e6) + 30_000_000)
    row = render_one(s, lang, d)
    typer.echo(json.dumps(row, ensure_ascii=False))
    del shots


@app.command("all")
def all_(
    cut: str = typer.Option(..., "--cut"),
    lang: str = typer.Option(..., "--lang"),
    jobs: int = typer.Option(1, "--jobs", help="parallel shot renders (FIX_HALF2_QUALITY)"),
) -> None:
    """Render every shot of one cut in one language (durations from the edit list)."""
    shots = [s for s in _index() if s["cut"] == cut]
    durs = shot_durations(cut, lang)
    if not durs:
        typer.echo(f"no edit list film/assemble/edl-{cut}-{lang}.csv: run film.assemble edl first")
        raise typer.Exit(1)
    total = sum(durs.values())
    require(int(total * 1.2e6) + len(shots) * 30_000_000)
    rows = []
    if jobs > 1:
        from concurrent.futures import ProcessPoolExecutor

        with ProcessPoolExecutor(max_workers=jobs) as ex:
            futs = [ex.submit(render_one, s, lang, durs[s["id"]]) for s in shots]
            for s, fut in zip(shots, futs, strict=True):
                rows.append(fut.result())
                typer.echo(f"{s['id']} {lang} {rows[-1]['duration_s']} s")
    for s in shots if jobs <= 1 else []:
        require(int(durs[s["id"]] * 1.2e6) + 30_000_000, quiet=True)  # re-checked per shot
        rows.append(render_one(s, lang, durs[s["id"]]))
        typer.echo(f"{s['id']} {lang} {rows[-1]['duration_s']} s")
    p = write_manifest(rows, cut, lang)
    typer.echo(f"film.render all: {len(rows)} shots ({total:.1f} s) -> {p}")


@app.command()
def trace(cut: str = typer.Option(..., "--cut"), lang: str = typer.Option(..., "--lang")) -> None:
    """Refresh the render manifest without rendering (reads only): one row per shot of the cut in
    storyboard order (FIX_FILM_STORY: shots rendered one by one with `shot` are added), duration
    from the edit list, then the figure columns."""
    shots = [s for s in _index() if s["cut"] == cut]
    p = REPO_ROOT / f"film/assemble/renders-{cut}-{lang}.csv"
    old = {}
    if p.exists():
        with p.open(encoding="utf-8", newline="") as fh:
            old = {r["shot_id"]: r for r in csv.DictReader(fh)}
    durs = shot_durations(cut, lang)
    rows = []
    for s in shots:
        mp4 = RENDERS / f"{cut}-{lang}" / f"{s['id']}.mp4"
        r = dict(old.get(s["id"]) or {})
        r.update(
            shot_id=s["id"],
            cut=cut,
            lang=lang,
            type=s.get("type"),
            duration_s=f"{durs.get(s['id'], float(s['duration_s'])):.3f}",
            output=str(mp4.relative_to(REPO_ROOT)) if mp4.exists() else "missing",
            footer=s.get("footer"),
            osm_credit=s.get("osm_credit"),
            copernicus=bool(s.get("extra_credit")),
        )
        rows.append(r)
    for r in rows:
        found, missing = trace_figures(SHOT_INDEX[r["shot_id"]])
        r["figures_traced"], r["figures_not_found"] = " ".join(found), " ".join(missing)
    write_manifest(rows, cut, lang)
    n = sum(len(r["figures_not_found"].split()) for r in rows)
    typer.echo(f"film.render trace {cut}-{lang}: {n} figure(s) not found in data sources")


if __name__ == "__main__":
    app()
