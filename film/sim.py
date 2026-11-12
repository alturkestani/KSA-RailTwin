"""Moving-map renderer for the film (FIX_HALF2_QUALITY): the twin running, not slides.

Tariq rejected the R10_HALF2 picture (two static HTML cards cross-fading with a push-in). This
engine draws every frame: a camera moves over a relief basemap computed from the study's own
Copernicus GLO-30 tiles (cop-dem-glo30-align-3as-2026-11-01), the twin's GeoJSON is drawn on top
(regions, existing / committed lines from cities/ksa/lines/geojson, hypothetical alignments from
runs/align), trains run along the lines, air seats flow along an arc, population dots grow,
alignments draw over the terrain and the optimiser's logged attempts appear one by one. Text is
not drawn here: captions (full sentences), legend, labels and credits are HTML rendered by the
local headless Chrome (Arabic shaped right-to-left, as in film.render), composited per frame.

Used by film.render for shots with `renderer: sim_map` (shot choreography: SCENES below, keyed by
shot id). Output: film/renders/<cut>-<lang>/<shot>.mp4, 1080p30 H.264, frames piped to ffmpeg.
Moving dots are illustrative (they show where lines run, not timetables) except where a caption
says they are scaled to a modelled quantity (the Riyadh–Jeddah door-to-door race, sh-04-51).
Deterministic: no randomness except numpy's generator seeded by `--seed` (rule 10).
Basemaps are cached under FILM_SIM_CACHE (default: the external volume's cache/sim).
"""

from __future__ import annotations

import csv
import hashlib
import html
import json
import math
import os
import subprocess
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import yaml
from PIL import Image, ImageDraw, ImageFilter

from common import REPO_ROOT
from film import render as R

W, H, FPS = 1920, 1080, 30
SS = 2  # supersampling for anti-aliased vectors
LAT0 = 24.0
K = math.cos(math.radians(LAT0))  # one fixed projection for the whole film (no wobble)
CY = 0.43  # camera target sits a little above the frame centre (captions sit at the bottom)
CACHE = Path(
    os.environ.get("FILM_SIM_CACHE", "/Volumes/Extreme_SSD/Projects/KSA-RailTwin/cache/sim")
)
NATIONAL = (33.0, 14.5, 57.5, 33.5)  # lon0, lat0, lon1, lat1 of the national basemap
NATIONAL_RES = 0.0125  # degrees of latitude per basemap pixel

PAL = {
    "sea": (8, 13, 24),
    "low": (34, 37, 44),
    "high": (92, 80, 64),
    "existing": (86, 204, 242),
    "committed": (255, 181, 71),
    "hypothetical": (199, 146, 255),
    "air": (244, 143, 177),
    "city": (255, 233, 186),
    "warn": (255, 120, 108),
    "region": (120, 132, 150),
    "white": (242, 242, 236),
    "good": (126, 217, 154),
    "historical": (196, 178, 150),  # main cut only (BUILD_MOVIE): the closed Hejaz Railway
}
DASH_PX = {"existing": None, "committed": (22, 12), "hypothetical": (5, 9)}
LEGEND_COL = {
    k: "#{:02x}{:02x}{:02x}".format(*PAL[k]) for k in ("existing", "committed", "hypothetical")
}
GEO = REPO_ROOT / "cities/ksa/lines/geojson"
# Legend rows outside the three rail layers (main cut only; the trailer legends never use them).
EXTRA_LEGEND = {
    "historical": {"en": "historical (closed)", "ar": "تاريخي (مغلق)", "dash": "2 7"},
}


# ---------------------------------------------------------------- geometry


def world(lonlat: np.ndarray) -> np.ndarray:
    a = np.asarray(lonlat, dtype="float64").reshape(-1, 2)
    return np.column_stack([a[:, 0] * K, a[:, 1]])


def load_lines(path: Path) -> list[np.ndarray]:
    out = []
    for _, geom in R._geoms(path):
        for part in R._parts(geom):
            pts = [p[:2] for p in part if len(p) >= 2]
            if len(pts) >= 2:
                out.append(world(np.array(pts)))
    return out


def load_layer(name: str) -> list[np.ndarray]:
    return load_lines(GEO / name)


def runs_file(rel: str) -> Path:
    return R.runs_root() / rel


def places() -> dict[str, tuple[float, float]]:
    """Script spellings -> lon/lat (film.render.PLACES via governorate points) plus the three
    central-case station additions (their YAML station coordinates)."""
    pts = dict(R.place_xy())
    for name, cid in (
        ("Dhahran", "dhahran"),
        ("Al Jubayl", "al-jubayl"),
        ("Duruma", "duruma"),
    ):
        p = REPO_ROOT / f"cities/ksa/corridors/station_addition/S5-station_addition-{cid}.yaml"
        if p.exists():
            st = yaml.safe_load(p.read_text(encoding="utf-8")).get("stations") or []
            hit = [s for s in st if s.get("id", "").replace("_", "-") == cid] or st[-1:]
            if hit:
                pts[name + " station"] = (float(hit[0]["lon"]), float(hit[0]["lat"]))
    return pts


AR_NAMES = {k: v[0] for k, v in R.PLACES.items()} | {
    "Dhahran station": "الظهران",
    "Al Jubayl station": "الجبيل",
    "Duruma station": "ضرما",
}


# Label side per place (both languages) where the default (right in English, left in Arabic)
# would collide with a neighbour.
LABEL_SIDE = {"Jeddah": "l", "Makkah": "r", "Riyadh": "r", "Duruma station": "l", "Taif": "r"}


def cumlen(p: np.ndarray) -> np.ndarray:
    return np.concatenate([[0.0], np.cumsum(np.hypot(*np.diff(p, axis=0).T))])


def partial(p: np.ndarray, frac: float) -> np.ndarray:
    """The first `frac` of a polyline by length."""
    c = cumlen(p)
    if frac >= 1 or c[-1] == 0:
        return p
    s = max(frac, 0.0) * c[-1]
    i = int(np.searchsorted(c, s))
    if i == 0:
        return p[:1]
    f = (s - c[i - 1]) / max(c[i] - c[i - 1], 1e-12)
    return np.vstack([p[:i], p[i - 1] + f * (p[i] - p[i - 1])])


def at(p: np.ndarray, frac: float) -> np.ndarray:
    c = cumlen(p)
    s = (frac % 1.0) * c[-1]
    i = min(max(int(np.searchsorted(c, s)), 1), len(p) - 1)
    f = (s - c[i - 1]) / max(c[i] - c[i - 1], 1e-12)
    return p[i - 1] + f * (p[i] - p[i - 1])


def segment(p: np.ndarray, f0: float, f1: float) -> np.ndarray:
    c = cumlen(p)
    s0, s1 = max(f0, 0) * c[-1], min(f1, 1) * c[-1]
    inner = p[(c > s0) & (c < s1)]
    return np.vstack([at(p, s0 / c[-1]), inner, at(p, s1 / c[-1] if s1 < c[-1] else 0.999999)])


def chain(lines: list[np.ndarray], start: np.ndarray, gap: float = 0.08) -> np.ndarray:
    """Join line pieces into one path starting near `start` (greedy nearest-endpoint walk)."""
    pieces = [x for x in lines if len(x) >= 2]
    if not pieces:
        return np.zeros((0, 2))
    path = None
    cur = np.asarray(start, dtype="float64")
    while pieces:
        best, bi, rev = 1e9, -1, False
        for i, x in enumerate(pieces):
            for r, end in ((False, x[0]), (True, x[-1])):
                d = float(np.hypot(*(end - cur)))
                if d < best:
                    best, bi, rev = d, i, r
        if path is not None and best > gap:
            break
        x = pieces.pop(bi)
        x = x[::-1] if rev else x
        path = x if path is None else np.vstack([path, x])
        cur = path[-1]
    return path if path is not None else np.zeros((0, 2))


def orient(p: np.ndarray, start: np.ndarray) -> np.ndarray:
    """The polyline running away from `start`."""
    return p if np.hypot(*(p[0] - start)) <= np.hypot(*(p[-1] - start)) else p[::-1]


def arc(a: np.ndarray, b: np.ndarray, lift: float = 0.18, n: int = 64) -> np.ndarray:
    """A curved flight path (screen-friendly bezier; not a great circle) from a to b."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    mid = (a + b) / 2
    nrm = np.array([-(b - a)[1], (b - a)[0]])
    ctrl = mid + nrm * lift
    t = np.linspace(0, 1, n)[:, None]
    return (1 - t) ** 2 * a + 2 * (1 - t) * t * ctrl + t**2 * b


# ---------------------------------------------------------------- camera


@dataclass
class Cam:
    lon: float
    lat: float
    z: float  # pixels per degree of latitude
    cx: float = W / 2  # screen point the camera target sits on (layout-dependent)
    cy: float = H * CY

    def screen(self, pts: np.ndarray) -> np.ndarray:
        x = (pts[:, 0] - self.lon * K) * self.z + self.cx
        y = self.cy - (pts[:, 1] - self.lat) * self.z
        return np.column_stack([x, y])

    def extent(self) -> tuple[float, float, float, float]:
        """World extent (u0, v0, u1, v1) of the frame."""
        u0 = self.lon * K - self.cx / self.z
        u1 = self.lon * K + (W - self.cx) / self.z
        v1 = self.lat + self.cy / self.z
        v0 = self.lat - (H - self.cy) / self.z
        return u0, v0, u1, v1


def ease(x: float) -> float:
    x = min(max(x, 0.0), 1.0)
    return x * x * x * (x * (6 * x - 15) + 10)  # smootherstep


def cam_at(keys: list[tuple[float, Cam]], f: float) -> Cam:
    """Camera at shot fraction f from (fraction, Cam) keys; zoom interpolates in log space."""
    if f <= keys[0][0]:
        return keys[0][1]
    for (f0, a), (f1, b) in zip(keys, keys[1:], strict=False):
        if f <= f1:
            e = ease((f - f0) / max(f1 - f0, 1e-9))
            z = math.exp(math.log(a.z) + (math.log(b.z) - math.log(a.z)) * e)
            return Cam(a.lon + (b.lon - a.lon) * e, a.lat + (b.lat - a.lat) * e, z)
    return keys[-1][1]


# ---------------------------------------------------------------- basemap (Copernicus relief)


@dataclass
class Base:
    rgb: np.ndarray  # (h, w, 3) uint8
    u0: float
    v1: float
    r: float  # world units (= degrees of latitude) per pixel

    def covers(self, ext: tuple[float, float, float, float]) -> bool:
        h, w = self.rgb.shape[:2]
        return (
            ext[0] >= self.u0
            and ext[2] <= self.u0 + w * self.r
            and ext[3] <= self.v1
            and ext[1] >= self.v1 - h * self.r
        )

    def crop(self, cam: Cam) -> Image.Image:
        u0, v0, u1, v1 = cam.extent()
        box = ((u0 - self.u0) / self.r, (self.v1 - v1) / self.r)
        box += ((u1 - self.u0) / self.r, (self.v1 - v0) / self.r)
        img = self.image()
        return img.transform(
            (W, H), Image.Transform.EXTENT, box, Image.Resampling.BILINEAR, fillcolor=PAL["sea"]
        )

    def image(self) -> Image.Image:
        if not hasattr(self, "_img"):
            self._img = Image.fromarray(self.rgb, "RGB")
        return self._img


def dem_dir() -> Path:
    return R.DEM_DIR if R.DEM_DIR.is_absolute() else REPO_ROOT / R.DEM_DIR


def ksa_mask(shape: tuple[int, int], transform) -> np.ndarray:
    from rasterio.features import rasterize

    geoms = [g for _, g in R._geoms(REPO_ROOT / "cities/ksa/zones/ksa.geojson")]
    return rasterize(
        [(g, 1) for g in geoms], out_shape=shape, transform=transform, fill=0, dtype="uint8"
    ).astype(bool)


def build_base(bbox: tuple[float, float, float, float], r: float) -> Base:
    """Relief basemap over bbox (lon0, lat0, lon1, lat1) at r degrees of latitude per pixel:
    hypsometric tint x hillshade inside the Kingdom, dimmed outside, sea dark. Cached."""
    key = hashlib.sha256(f"v4|{bbox}|{r}".encode()).hexdigest()[:16]
    npz = CACHE / f"base-{key}.npz"
    lon0, lat0, lon1, lat1 = bbox
    if npz.exists():
        d = np.load(npz)
        return Base(d["rgb"], float(d["origin"][0]) * K, float(d["origin"][1]), r)
    import rasterio
    from rasterio.merge import merge

    files = []
    for f in sorted(dem_dir().glob("*.tif")):
        with rasterio.open(f) as s:
            b = s.bounds
        if b.right > lon0 and b.left < lon1 and b.top > lat0 and b.bottom < lat1:
            files.append(f)
    xres, yres = r / K, r
    srcs = [rasterio.open(f) for f in files]
    try:
        arr, tr = merge(srcs, bounds=bbox, res=(xres, yres), nodata=np.nan)
    finally:
        for s in srcs:
            s.close()
    z = arr[0].astype("float32")
    h, w = z.shape
    inside = ksa_mask((h, w), tr)
    nod = np.isnan(z)
    if nod.any() and (~nod).any():  # tile seams and gaps: nearest valid elevation
        from scipy.ndimage import distance_transform_edt

        idx = distance_transform_edt(nod, return_distances=False, return_indices=True)
        z = z[tuple(idx)]
        nod = np.zeros_like(nod)
    zf = np.where(nod, 0.0, z)
    dy, dx = np.gradient(zf, r * 111_000, xres * 111_000 * K)
    exag = 3.0 if r >= 0.005 else 1.8  # display exaggeration only
    slope = np.arctan(np.hypot(dx, dy) * exag)
    aspect = np.arctan2(-dx, dy)
    shade = np.zeros_like(zf)
    for az, wgt in ((315, 0.6), (270, 0.25), (0, 0.15)):  # soft multi-directional light
        a, alt = math.radians(az), math.radians(42)
        shade += wgt * (
            np.sin(alt) * np.cos(slope) + np.cos(alt) * np.sin(slope) * np.cos(a - aspect)
        )
    shade = np.clip((shade - 0.25) / 0.75, 0, 1.2)
    t = np.clip(zf / 2400.0, 0, 1)[..., None] ** 0.7
    low, high = np.array(PAL["low"], "float32"), np.array(PAL["high"], "float32")
    col = (low * (1 - t) + high * t) * (0.55 + 0.75 * shade[..., None])
    land = inside & (zf > 0.5)  # the Kingdom only; seas and neighbours share the night tone
    sea = np.array(PAL["sea"], "float32")
    out = np.where(land[..., None], col, sea)
    rgb = np.clip(out, 0, 255).astype("uint8")
    CACHE.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(npz, rgb=rgb, origin=np.array([tr.c, tr.f]))
    return Base(rgb, tr.c * K, tr.f, r)


# ---------------------------------------------------------------- drawing


class Canvas:
    """Supersampled RGBA vector layer for one frame."""

    def __init__(self, cam: Cam):
        self.cam = cam
        self.img = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.img, "RGBA")

    def xy(self, pts: np.ndarray) -> list[tuple[float, float]]:
        s = self.cam.screen(pts) * SS
        return [tuple(p) for p in s]

    def visible(self, pts: np.ndarray, pad: float = 200) -> bool:
        s = self.cam.screen(pts)
        return not (
            s[:, 0].max() < -pad
            or s[:, 0].min() > W + pad
            or s[:, 1].max() < -pad
            or s[:, 1].min() > H + pad
        )

    def line(self, pts, col, width: float, alpha: float = 1.0, dash=None) -> None:
        if len(pts) < 2 or alpha <= 0 or not self.visible(pts):
            return
        rgba = (*col, int(255 * min(alpha, 1)))
        w = max(int(round(width * SS)), 1)
        if not dash:
            self.d.line(self.xy(pts), fill=rgba, width=w, joint="curve")
            return
        s = self.cam.screen(pts) * SS
        c = np.concatenate([[0], np.cumsum(np.hypot(*np.diff(s, axis=0).T))])
        on, off = dash[0] * SS, dash[1] * SS
        start = 0.0
        while start < c[-1]:
            end = min(start + on, c[-1])
            idx = (c > start) & (c < end)
            seg = [np.interp(start, c, s[:, 0]), np.interp(start, c, s[:, 1])]
            pts2 = [tuple(seg)] + [tuple(p) for p in s[idx]]
            pts2.append((np.interp(end, c, s[:, 0]), np.interp(end, c, s[:, 1])))
            self.d.line(pts2, fill=rgba, width=w, joint="curve")
            start = end + off

    def dot(self, p, col, radius: float, alpha: float = 1.0) -> None:
        x, y = self.cam.screen(np.asarray(p, float).reshape(1, 2))[0] * SS
        r = radius * SS
        if -50 < x < W * SS + 50 and -50 < y < H * SS + 50 and alpha > 0:
            self.d.ellipse((x - r, y - r, x + r, y + r), fill=(*col, int(255 * min(alpha, 1))))

    def ring(self, p, col, radius_px: float, width: float, alpha: float) -> None:
        x, y = self.cam.screen(np.asarray(p, float).reshape(1, 2))[0] * SS
        r = radius_px * SS
        if alpha > 0:
            self.d.ellipse(
                (x - r, y - r, x + r, y + r),
                outline=(*col, int(255 * min(alpha, 1))),
                width=max(int(width * SS), 1),
            )

    def rect(self, box, col, alpha: float) -> None:
        x0, y0, x1, y1 = (v * SS for v in box)
        self.d.rectangle((x0, y0, x1, y1), fill=(*col, int(255 * min(alpha, 1))))

    def done(self) -> Image.Image:
        return self.img.reduce(SS)


def comet(c: Canvas, path: np.ndarray, f: float, col, tail: float = 0.05, width=3.0) -> None:
    """A train: bright head with a fading tail along the path (f = head position 0..1)."""
    if len(path) < 2:
        return
    steps = 6
    for k in range(steps):
        a0 = f - tail * (k + 1) / steps
        a1 = f - tail * k / steps
        if a1 <= 0:
            continue
        c.line(segment(path, max(a0, 0), a1), col, width, alpha=0.9 * (1 - k / steps))
    c.dot(at(path, min(f, 0.9999)), (255, 255, 255), width * 1.25, 1.0)


# ---------------------------------------------------------------- text layers (Chrome)


def css() -> str:
    return f"""{R.font_css()}
html,body{{margin:0;width:{W}px;height:{H}px;overflow:hidden;background:transparent}}
body{{font-family:'Noto Sans','Noto Naskh Arabic',sans-serif;color:#F2F2EC;letter-spacing:normal}}
[dir=rtl]{{font-family:'Noto Naskh Arabic','Noto Sans',serif}}
.cap{{position:absolute;left:96px;right:96px;bottom:96px;font-size:35px;line-height:1.42;
  background:rgba(7,11,20,.80);padding:20px 30px 22px;border-radius:12px}}
.cap[dir=ltr]{{border-left:5px solid #56CCF2}} .cap[dir=rtl]{{border-right:5px solid #56CCF2}}
.cap .src,.side .src{{font-size:22px;color:#AEB6C2;margin-top:8px}}
.side{{position:absolute;top:50%;transform:translateY(-50%);width:520px;font-size:35px;
  line-height:1.42;background:rgba(7,11,20,.80);padding:24px 30px;border-radius:12px}}
.side[dir=ltr]{{left:64px;border-left:5px solid #56CCF2}}
.side[dir=rtl]{{right:64px;border-right:5px solid #56CCF2}}
.leg{{position:absolute;top:44px;font-size:22px;background:rgba(7,11,20,.72);padding:12px 18px;
  border-radius:10px;line-height:1.5}}
.leg div{{display:flex;align-items:center;gap:12px}}
.pill{{position:absolute;top:44px;font-size:24px;background:rgba(7,11,20,.72);padding:8px 16px;
  border-radius:8px;color:#FFE9BA}}
.cred{{position:absolute;left:0;right:0;bottom:0;font-size:15px;line-height:1.35;
  color:#A7AFBB;text-align:center;padding:26px 96px 14px;
  background:linear-gradient(to bottom,rgba(7,11,20,0),rgba(7,11,20,.85) 45%)}}
.title{{position:absolute;left:120px;right:120px;top:300px;text-align:center;font-size:84px;
  font-weight:700;line-height:1.25;color:#FFF7E6}}
.notice{{position:absolute;left:160px;right:160px;top:520px;text-align:center;font-size:34px;
  line-height:1.4;color:#E6E1D6}}
.small{{position:absolute;left:160px;right:160px;top:640px;text-align:center;font-size:22px;
  line-height:1.5;color:#AEB6C2}}
.lbl{{position:absolute;font-size:24px;color:#E8ECF2}}
.lbl.b{{font-weight:700;color:#FFF7E6}}
.title.main{{top:330px;font-size:62px;line-height:1.3}}
.rolltitle{{position:absolute;left:0;right:0;top:64px;text-align:center;font-size:50px;
  font-weight:700;color:#FFF7E6}}
.roll{{position:absolute;left:170px;right:170px;top:170px;text-align:center;font-size:23px;
  line-height:1.42;color:#C9CED6}}
.roll div{{margin:0 0 7px}}
.roll .n{{font-size:31px;color:#FFF3DA;margin:6px 0 16px}}
.lbl.s{{font-size:20px;color:#C9CED6}}
"""


def page(body: str, lang: str) -> str:
    return (
        f'<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><style>{css()}'
        f"</style></head><body>{body}</body></html>"
    )


def legend_html(lang: str, layers: tuple[str, ...]) -> str:
    rows = []
    for lay, label in R.LEGEND[lang]:
        if lay not in layers:
            continue
        dash = {"committed": "16 9", "hypothetical": "3 8"}.get(lay, "")
        svg = (
            f'<svg width="64" height="14"><line x1="3" y1="7" x2="61" y2="7" '
            f'stroke="{LEGEND_COL[lay]}" stroke-width="6" stroke-linecap="round"'
            + (f' stroke-dasharray="{dash}"' if dash else "")
            + "/></svg>"
        )
        rows.append(f"<div>{svg}<span>{html.escape(label)}</span></div>")
    for lay in layers:
        ex = EXTRA_LEGEND.get(lay)
        if ex:
            col = "#{:02x}{:02x}{:02x}".format(*PAL[lay])
            svg = (
                f'<svg width="64" height="14"><line x1="3" y1="7" x2="61" y2="7" '
                f'stroke="{col}" stroke-width="6" stroke-linecap="round" '
                f'stroke-dasharray="{ex["dash"]}"/></svg>'
            )
            rows.append(f"<div>{svg}<span>{html.escape(ex[lang])}</span></div>")
    side = "left:96px" if lang == "ar" else "right:96px"
    d = "rtl" if lang == "ar" else "ltr"
    return f'<div class="leg" dir="{d}" style="{side}">{"".join(rows)}</div>'


def credit_html(shot: dict) -> str:
    creds = []
    if shot.get("osm_credit"):
        creds.append(R.OSM + " (ODbL)")
    if shot.get("extra_credit"):
        creds.append("Relief: " + R.COPERNICUS)
    return f'<div class="cred" dir="ltr">{"<br>".join(map(html.escape, creds))}</div>'


def texts_html(lang: str, scene: Scene) -> str:
    """Chart and panel labels (a separate layer so they can appear with their panel)."""
    d = "rtl" if lang == "ar" else "ltr"
    out = []
    for x, y, en, ar, cls, anchor in scene.texts:
        t = ar if lang == "ar" else en
        pos = f"left:{x}px;top:{y}px" if anchor == "l" else f"right:{W - x}px;top:{y}px"
        if anchor == "c":
            pos = f"left:{x - 400}px;width:800px;text-align:center;top:{y}px"
        out.append(f'<div class="lbl {cls}" dir="{d}" style="{pos}">{html.escape(t)}</div>')
    return page("\n".join(out), lang)


def overlay_html(shot: dict, lang: str, scene: Scene) -> str:
    d = "rtl" if lang == "ar" else "ltr"
    out = []
    text = str(shot["on_screen_text"][lang])
    src = (shot.get("source_caption") or {}).get(lang, "")
    if scene.title and scene.roll:  # main-cut credits (BUILD_MOVIE): notice once, inside the roll
        out.append(f'<div class="rolltitle" dir="{d}">{html.escape(text)}</div>')
        out.append(roll_html(lang))
    elif scene.title:
        cls = "title" if scene.closing else "title main"
        out.append(f'<div class="{cls}" dir="{d}">{html.escape(text)}</div>')
        notice = CLOSING_NOTICE[lang] if shot.get("footer") == "synthetic" else ""
        if notice:
            out.append(f'<div class="notice" dir="{d}">{html.escape(notice)}</div>')
        if scene.closing:
            small = closing_credits(lang)
            out.append(
                f'<div class="small" dir="{d}">'
                + "<br>".join(
                    R.ltr_isolate(html.escape(x)) if lang == "ar" else html.escape(x) for x in small
                )
                + "</div>"
            )
    else:
        srch = f'<div class="src">{html.escape(src)}</div>' if src else ""
        cls = "side" if scene.side else "cap"
        out.append(f'<div class="{cls}" dir="{d}">{html.escape(text)}{srch}</div>')
    if scene.legend:
        out.append(legend_html(lang, scene.legend))
    comp = shot.get("composite_label")
    if comp:
        side = "right:96px" if lang == "ar" else "left:96px"
        if scene.side:  # above the side caption (the legend is on the map side)
            side = "right:64px" if lang == "ar" else "left:64px"
        out.append(f'<div class="pill" dir="{d}" style="{side}">{html.escape(comp[lang])}</div>')
    if scene.credits_bar is None and not scene.title:
        out.append(credit_html(shot))
    elif scene.credits_bar:  # main cut: OSM-derived lines over the Copernicus relief, every frame
        out.append(credit_html({"osm_credit": True, "extra_credit": True}))
    return page("\n".join(out), lang)


def roll_html(lang: str) -> str:
    """The main-cut credits (sh-08-14): film.render.credits_lines, whose second line is the single
    closing notice (set larger, shown once)."""
    d = "rtl" if lang == "ar" else "ltr"
    rows = []
    for i, x in enumerate(R.credits_lines(lang)):
        t = R.ltr_isolate(html.escape(x)) if lang == "ar" else html.escape(x)
        rows.append(f'<div class="n">{t}</div>' if i == 1 else f"<div>{t}</div>")
    return f'<div class="roll" dir="{d}">{"".join(rows)}</div>'


# The single closing notice (Tariq, 8 Nov 2026): glossary term 4 in the Arabic wording.
CLOSING_NOTICE = {
    "en": "Synthetic demand, uncalibrated: a scenario comparison, not a forecast.",
    "ar": R.FOOTER["ar"][0] + ".",
}


def closing_credits(lang: str) -> list[str]:
    if lang == "en":
        return [
            "Narration: ElevenLabs voice George (English); Nabrah public voices Daniah, Norah "
            "and Abdullah (Arabic)",
            "Map data © OpenStreetMap contributors (ODbL) · statistics: GASTAT (derived) · "
            "relief: Copernicus WorldDEM-30 © DLR e.V. 2010-2014 and © Airbus Defence and "
            "Space GmbH 2014-2018, provided under COPERNICUS by the European Union and ESA",
            "KSA Rail Twin: a research film, not an official film of any ministry or company",
        ]
    # FIX_TRAILER_AR (Tariq, 12 Nov 2026): no ElevenLabs audio in the Arabic trailer, so no
    # George / ElevenLabs credit; the Nabrah attribution and the closing notice stay.
    return [
        "التعليق الصوتي: أصوات نبرة العامة دانية ونورة وعبدالله (العربية)",
        "بيانات الخرائط: © OpenStreetMap contributors (ODbL)",
        "الإحصاءات: الهيئة العامة للإحصاء (جداول مشتقة)",
        "التضاريس: Copernicus WorldDEM-30 © DLR e.V. 2010-2014 and © Airbus Defence and Space "
        "GmbH 2014-2018, provided under COPERNICUS by the European Union and ESA",
        "التوأم الرقمي للسكك الحديدية في السعودية: فيلم بحثي، مو فيلم رسمي لأي وزارة أو شركة",
    ]


def label_sprites(names: list[str], lang: str, out: Path) -> dict[str, Image.Image]:
    """Place-name sprites (one Chrome screenshot, cropped per cell): text with a dark halo."""
    cell_w, cell_h, cols = 640, 72, 3
    cells = []
    for i, n in enumerate(names):
        x, y = (i % cols) * cell_w, (i // cols) * cell_h
        t = AR_NAMES.get(n, n) if lang == "ar" else n.replace(" station", "")
        cells.append(
            f'<div style="position:absolute;left:{x + 8}px;top:{y + 8}px;font-size:27px;'
            f"font-weight:700;color:#FFF3DA;text-shadow:0 0 6px #000,0 0 3px #000,0 0 12px #000"
            f'" dir="{"rtl" if lang == "ar" else "ltr"}">{html.escape(t)}</div>'
        )
    png = out / f"labels-{lang}.png"
    R.chrome_png(page("".join(cells), lang), png, transparent=True)
    sheet = Image.open(png).convert("RGBA")
    sprites = {}
    for i, n in enumerate(names):
        x, y = (i % cols) * cell_w, (i // cols) * cell_h
        cell = sheet.crop((x, y, x + cell_w - 40, y + cell_h - 4))  # gutter: no neighbour glow
        bb = cell.getchannel("A").getbbox()
        sprites[n] = cell.crop(bb) if bb else cell
    return sprites


# ---------------------------------------------------------------- scenes


@dataclass
class Scene:
    keys: list[tuple[float, Cam]]
    draw: Callable[[Canvas, float, float, dict], None]
    labels: list[tuple[str, float]] = field(default_factory=list)  # (place, appear at fraction)
    legend: tuple[str, ...] = ()
    texts: list[tuple] = field(default_factory=list)  # (x, y, en, ar, cls, anchor l/r/c)
    texts_at: float = 0.0  # shot fraction at which the chart labels fade in (with their panel)
    title: bool = False
    dim: Callable[[float], float] = lambda f: 1.0
    zoom_detail: bool = False
    side: bool = False  # caption in a side column (national views), map in the rest
    # BUILD_MOVIE additions (main cut); the defaults keep the trailer frames byte-identical.
    closing: bool = True  # title scenes: append closing_credits() (trailer); main titles: False
    roll: bool = False  # title scene shows the credits roll (credits_lines) instead
    credits_bar: bool | None = None  # None: from the shot flags (trailer); True: OSM + relief
    label_side: dict[str, str] = field(default_factory=dict)  # per-scene LABEL_SIDE overrides
    insets: list[Inset] = field(default_factory=list)  # framed photographs (archival)


@dataclass
class Inset:
    """A framed photograph composited over the map with a slow push-in (main cut, sh-02-01)."""

    path: Path
    box: tuple[int, int, int, int]  # x, y, w, h on screen
    t0: float = 0.0  # shot fraction at which it fades in
    zoom: tuple[float, float] = (1.0, 1.08)  # push-in from / to


def inset_prep(ins: Inset) -> dict:
    x, y, w, h = ins.box
    img = Image.open(ins.path).convert("RGB")
    iw, ih = img.size
    if iw / ih > w / h:  # centre crop to the box aspect
        cw = int(ih * w / h)
        img = img.crop(((iw - cw) // 2, 0, (iw - cw) // 2 + cw, ih))
    else:
        ch = int(iw * h / w)
        img = img.crop((0, (ih - ch) // 2, iw, (ih - ch) // 2 + ch))
    z1 = max(ins.zoom)
    big = img.resize((int(w * z1), int(h * z1)), Image.Resampling.LANCZOS)
    return {"ins": ins, "big": big, "z1": z1}


def inset_draw(frame: np.ndarray, p: dict, f: float) -> np.ndarray:
    """Composite one framed photograph: fade in at t0, push in over the shot."""
    ins: Inset = p["ins"]
    a = fr(f, ins.t0, ins.t0 + 0.08)
    if a <= 0:
        return frame
    x, y, w, h = ins.box
    big: Image.Image = p["big"]
    z = ins.zoom[0] + (ins.zoom[1] - ins.zoom[0]) * ease(f)
    ww, wh = big.size[0] / z, big.size[1] / z  # z = 1: the whole photograph; z1: 1:1 pixels
    cx, cy = big.size[0] / 2, big.size[1] / 2
    box = (cx - ww / 2, cy - wh / 2, cx + ww / 2, cy + wh / 2)
    img = np.asarray(big.resize((w, h), Image.Resampling.BILINEAR, box=box), "float32") / 255.0
    b = 4  # shadow, cream border, photograph
    y0, y1 = max(y - b - 6, 0), min(y + h + b + 10, H)
    x0, x1 = max(x - b - 6, 0), min(x + w + b + 10, W)
    frame[y0:y1, x0:x1] *= 1 - 0.55 * a
    rim = np.array([0.95, 0.91, 0.84], "float32")
    sl = (slice(y - b, y + h + b), slice(x - b, x + w + b))
    frame[sl] = frame[sl] * (1 - a) + rim * a
    frame[y : y + h, x : x + w] = frame[y : y + h, x : x + w] * (1 - a) + img * a
    return frame


class Data:
    """Geometry shared by the scenes (loaded once per process)."""

    def __init__(self) -> None:
        self.regions = load_lines(REPO_ROOT / "cities/ksa/zones/regions.geojson")
        self.border = load_lines(REPO_ROOT / "cities/ksa/zones/ksa.geojson")
        self.existing = load_layer("existing.geojson")
        self.committed = load_layer("committed.geojson")
        self.places = {k: world(np.array(v))[0] for k, v in places().items()}
        north = load_layer("sar-north-passenger.geojson")
        self.north = chain(north, self.places["Riyadh"], gap=0.25)
        self.hhr = chain(load_layer("hhr.geojson"), self.places["Makkah"], gap=0.25)
        self.east = chain(load_layer("sar-east-passenger.geojson"), self.places["Riyadh"], 0.25)
        zones = json.loads(
            (REPO_ROOT / "cities/ksa/zones/zones.geojson").read_text(encoding="utf-8")
        )["features"]
        z = [
            (
                f["properties"]["point_lon"],
                f["properties"]["point_lat"],
                f["properties"]["population_2022"],
            )
            for f in zones
            if f["properties"].get("population_2022")
        ]
        z.sort(key=lambda r: -r[2])
        self.pop = np.array(z, dtype="float64")
        self.pop_xy = world(self.pop[:, :2])

    def trains(self) -> list[tuple[np.ndarray, float, float]]:
        """(path, phase, speed in path-lengths per second): illustrative only."""
        out = []
        for path, n, sp in ((self.north, 2, 0.045), (self.hhr, 3, 0.07), (self.east, 2, 0.07)):
            if len(path) >= 2:
                for k in range(n):
                    out.append((path, k / n, sp))
        return out


def base_network(
    c: Canvas, D: Data, t: float, alpha: float = 1.0, trains: bool = True, committed: bool = True
) -> None:
    for g in D.regions:
        c.line(g, PAL["region"], 1.0, 0.22 * alpha)
    for g in D.border:
        c.line(g, PAL["region"], 1.6, 0.55 * alpha)
    if committed:
        for g in D.committed:
            c.line(g, PAL["committed"], 2.6, 0.75 * alpha, dash=DASH_PX["committed"])
    for g in D.existing:
        c.line(g, PAL["existing"], 2.8, 0.9 * alpha)
    if trains:
        for path, ph, sp in D.trains():
            comet(c, path, (ph + sp * t) % 1.0, PAL["existing"], tail=0.06, width=3.2)


def town(c: Canvas, D: Data, name: str, col=None, r: float = 5.0, alpha: float = 1.0) -> None:
    p = D.places.get(name)
    if p is not None:
        c.dot(p, (0, 0, 0), r + 2.5, 0.5 * alpha)
        c.dot(p, col or PAL["city"], r, alpha)


def pulse(c: Canvas, D: Data, name: str, t: float, t0: float, col) -> None:
    p = D.places.get(name)
    if p is None or t < t0:
        return
    for k in range(2):
        ph = ((t - t0) * 0.9 + k * 0.5) % 1.0
        c.ring(p, col, 8 + 46 * ph, 3.0, (1 - ph) * 0.9)
    c.dot(p, col, 7, 1.0)


def fr(t: float, a: float, b: float) -> float:
    return min(max((t - a) / max(b - a, 1e-9), 0.0), 1.0)


def scenes(D: Data, T: dict[str, float]) -> dict[str, Scene]:
    """Choreography of the trailer shots (shot id -> Scene). T = shot durations (s)."""
    P = D.places
    S: dict[str, Scene] = {}
    nat = Cam(44.6, 23.6, 72)

    # t-01 four journeys -------------------------------------------------------------------
    air = arc(P["Riyadh"], P["Jeddah"], lift=-0.22)

    def d01(c: Canvas, t: float, T_: float, ctx: dict) -> None:
        base_network(c, D, t, trains=False)
        f = t / T_
        comet(c, D.north, 0.05 + 0.9 * ease(fr(f, 0.0, 0.55)), PAL["existing"], 0.08, 4.0)
        a = ease(fr(f, 0.25, 0.55))
        if a > 0:
            c.line(partial(air, a), PAL["air"], 2.6, 0.95, dash=(10, 8))
            c.dot(at(air, min(a, 0.999)), (255, 255, 255), 4.5)
        if f > 0.5:
            pulse(c, D, "Abha", t, 0.5 * T_, PAL["city"])
        if f > 0.7:
            pulse(c, D, "Tabuk", t, 0.7 * T_, PAL["city"])
        for n in ("Riyadh", "Jeddah", "Qurayyat"):
            town(c, D, n)

    S["sh-01-51"] = Scene(
        keys=[(0.0, Cam(43.2, 27.6, 110)), (0.55, Cam(43.0, 25.6, 74)), (1.0, Cam(44.6, 24.1, 61))],
        draw=d01,
        labels=[
            ("Riyadh", 0.0),
            ("Qurayyat", 0.35),
            ("Jeddah", 0.4),
            ("Abha", 0.52),
            ("Tabuk", 0.72),
        ],
        legend=("existing", "committed"),
        side=True,
    )

    # t-02 Jeddah-Riyadh seats --------------------------------------------------------------
    air2 = arc(P["Jeddah"], P["Riyadh"], lift=0.22)

    def d02(c: Canvas, t: float, T_: float, ctx: dict) -> None:
        base_network(c, D, t)
        c.line(air2, PAL["air"], 2.2, 0.55)
        rng = ctx["rng"]
        for k in range(26):  # seat flow both ways (illustrative particles)
            ph = (ctx["phase"][k] + t * 0.22) % 1.0
            path = air2 if k % 2 == 0 else air2[::-1]
            c.dot(at(path, ph), PAL["air"], 3.2, 0.95)
        del rng
        for n in ("Riyadh", "Jeddah", "Makkah"):
            town(c, D, n, r=6)

    S["sh-01-52"] = Scene(
        keys=[(0.0, Cam(43.0, 23.15, 140)), (1.0, Cam(43.0, 23.0, 165))],
        draw=d02,
        labels=[("Riyadh", 0.0), ("Jeddah", 0.0), ("Makkah", 0.2)],
        legend=("existing", "committed"),
    )

    # t-03 five towns, no station within 10 km ------------------------------------------------
    five = ["Taif", "Tabuk", "Abha", "Najran", "Jazan"]

    def d03(c: Canvas, t: float, T_: float, ctx: dict) -> None:
        base_network(c, D, t)
        km10 = 10 / 111.0  # world units (degrees of latitude) for 10 km
        for i, n in enumerate(five):
            t0 = (0.08 + 0.15 * i) * T_
            if t >= t0 and n in P:
                c.ring(P[n], PAL["warn"], km10 * c.cam.z, 2.5, 0.95)  # true-scale 10 km
                pulse(c, D, n, t, t0, PAL["warn"])

    S["sh-02-51"] = Scene(
        keys=[(0.0, Cam(42.0, 23.4, 64)), (1.0, Cam(41.6, 22.9, 72))],
        draw=d03,
        side=True,
        labels=[(n, 0.08 + 0.15 * i) for i, n in enumerate(five)]
        + [("Riyadh", 0.0), ("Jeddah", 0.0)],
        legend=("existing", "committed"),
    )

    # t-04 population -----------------------------------------------------------------------
    def d04(c: Canvas, t: float, T_: float, ctx: dict) -> None:
        base_network(c, D, t, alpha=0.6, trains=False)
        n = len(D.pop)
        shown = int(n * ease(fr(t / T_, 0.05, 0.75)))
        pmax = D.pop[0, 2]
        for i in range(shown):
            r = 1.6 + 26 * math.sqrt(D.pop[i, 2] / pmax)
            age = fr(t / T_, 0.05 + 0.7 * i / n, 0.05 + 0.7 * i / n + 0.08)
            c.dot(D.pop_xy[i], PAL["city"], r * (0.5 + 0.5 * age), 0.30 + 0.25 * age)
            c.dot(D.pop_xy[i], (255, 250, 235), max(r * 0.28, 1.2), 0.85)

    S["sh-03-51"] = Scene(
        keys=[(0.0, Cam(45.0, 24.3, 58)), (1.0, Cam(44.8, 24.1, 63))],
        draw=d04,
        side=True,
        labels=[
            ("Riyadh", 0.2),
            ("Jeddah", 0.25),
            ("Makkah", 0.3),
            ("Madinah", 0.35),
            ("Dammam", 0.4),
        ],
    )

    # t-05 door-to-door race ------------------------------------------------------------------
    rj = sorted(runs_file("study/rj/align-s1").glob("RJ-*/alignment.geojson"))
    rj_lines = [x for p in rj for x in load_lines(p) if len(x) > 2]  # no 2-point sketches
    ratio, route = air_over_rail()
    race_rail = orient(
        max(load_lines(runs_file(f"study/rj/align-s1/{route}/alignment.geojson")), key=len),
        P["Riyadh"],
    )
    air5 = arc(P["Riyadh"], P["Jeddah"], lift=-0.20)

    def d05(c: Canvas, t: float, T_: float, ctx: dict) -> None:
        base_network(c, D, t, alpha=0.55, trains=False)
        for g in rj_lines:
            c.line(g, PAL["hypothetical"], 2.4, 0.75, dash=DASH_PX["hypothetical"])
        c.line(air5, PAL["air"], 2.0, 0.6, dash=(10, 8))
        f = fr(t / T_, 0.08, 0.92)
        comet(c, race_rail, min(f, 0.999), PAL["hypothetical"], 0.05, 4.0)
        fa = min(f / ratio, 0.999)
        comet(c, air5, fa, PAL["air"], 0.05, 4.0)
        for n in ("Riyadh", "Jeddah"):
            town(c, D, n, r=6)

    S["sh-04-51"] = Scene(
        keys=[(0.0, Cam(43.1, 23.5, 118)), (1.0, Cam(43.1, 23.3, 128))],
        draw=d05,
        labels=[("Riyadh", 0.0), ("Jeddah", 0.0)],
        legend=("existing", "hypothetical"),
        texts=[],
    )

    # t-06 terrain: the Taif escarpment ---------------------------------------------------------
    taif = [
        x
        for cid in (
            "S3-branch_spur-at-ta-if",
            "S4-commuter_belt-taif-270",
            "S4-commuter_belt-makkah-090",
        )
        for x in load_lines(runs_file(f"align/corridors-s1/{cid}/alignment.geojson"))
    ]
    spur = chain(
        load_lines(runs_file("align/corridors-s1/S3-branch_spur-at-ta-if/alignment.geojson")),
        P["Makkah"],
        gap=0.3,
    )

    def d06(c: Canvas, t: float, T_: float, ctx: dict) -> None:
        f = t / T_
        for g in D.existing:
            c.line(g, PAL["existing"], 3.0, 0.9)
        for path, ph, sp in D.trains()[2:5]:
            comet(c, path, (ph + sp * t) % 1.0, PAL["existing"], 0.03, 3.4)
        for g in taif:
            if g is not spur:
                c.line(g, PAL["hypothetical"], 2.6, 0.45 * fr(f, 0.4, 0.8), dash=(5, 9))
        a = ease(fr(f, 0.05, 0.85))
        if a > 0 and len(spur) >= 2:
            c.line(partial(spur, a), PAL["hypothetical"], 4.0, 0.95, dash=(6, 7))
            c.dot(at(spur, min(a, 0.999)), (255, 255, 255), 5)
        for n in ("Taif", "Makkah", "Al-Jumum"):
            town(c, D, n, r=6)

    S["sh-06-51"] = Scene(
        keys=[(0.0, Cam(40.0, 21.42, 950)), (1.0, Cam(40.22, 21.36, 1350))],
        draw=d06,
        labels=[("Makkah", 0.0), ("Taif", 0.3)],
        legend=("existing", "hypothetical"),
        zoom_detail=True,
    )

    # t-07 the judge: every attempt -------------------------------------------------------------
    pts, kept = attempts()
    px0, py0, px1, py1 = 300, 200, 1620, 820

    def d07(c: Canvas, t: float, T_: float, ctx: dict) -> None:
        base_network(c, D, t, alpha=0.35)
        c.rect((px0 - 30, py0 - 40, px1 + 30, py1 + 40), (7, 11, 20), 0.72)
        c.line(world_px([(px0, py1), (px1, py1)], c.cam), PAL["region"], 1.5, 0.8)
        c.line(world_px([(px0, py1), (px0, py0)], c.cam), PAL["region"], 1.5, 0.8)
        n = int(len(pts) * ease(fr(t / T_, 0.05, 0.85)))
        for i in range(n):
            x = px0 + pts[i, 0] * (px1 - px0)
            y = py1 - pts[i, 1] * (py1 - py0)
            col = PAL["good"] if kept[i] else PAL["existing"]
            big = bool(kept[i])
            c.dot(world_px([(x, y)], c.cam)[0], col, 7.0 if big else 1.7, 0.95 if big else 0.6)

    S["sh-07-51"] = Scene(
        keys=[(0.0, nat), (1.0, Cam(44.6, 23.6, 76))],
        draw=d07,
        texts=[
            (px0, py1 + 18, "cost (capital, median) →", "التكلفة (رأس المال، الوسيط) →", "", "l"),
            (
                px0 + 10,
                py0 - 34,
                "↑ benefits minus costs (worst population case)",
                "↑ المنافع ناقص التكاليف (أسوأ حالة للسكان)",
                "",
                "l",
            ),
            (
                px1,
                py0 - 34,
                "green: kept after the judge's full score",
                "الأخضر: مخططات انقبلت بعد تقييم الحَكَم الكامل",
                "",
                "r",
            ),
        ],
    )

    # t-08 central case ------------------------------------------------------------------------
    st3 = ["Al Jubayl station", "Dhahran station", "Duruma station"]
    bx0, bx1, by = 200, 820, 260

    def d08(c: Canvas, t: float, T_: float, ctx: dict) -> None:
        base_network(c, D, t)
        for i, n in enumerate(st3):
            pulse(c, D, n, t, (0.1 + 0.12 * i) * T_, PAL["good"])
        a = ease(fr(t / T_, 0.35, 0.7))
        c.rect((bx0 - 40, by - 90, bx1 + 40, by + 120), (7, 11, 20), 0.72 * fr(t / T_, 0.25, 0.4))
        if a > 0:
            lo, hi = 4.0, 5.6  # billion SAR, the on-screen range (runs/r6/top5/top5.csv, S6-L2)
            scale = (bx1 - bx0) / 6.0
            x0 = bx0  # break-even (zero) at the left end of the axis
            c.line(world_px([(x0, by - 50), (x0, by + 50)], c.cam), PAL["white"], 2, 0.8 * a)
            c.line(world_px([(bx0, by), (bx1, by)], c.cam), PAL["region"], 1.5, 0.7 * a)
            xa, xb = x0 + lo * scale, x0 + (lo + (hi - lo) * a) * scale
            c.rect((xa, by - 18, xb, by + 18), PAL["good"], 0.95 * a)

    S["sh-08-51"] = Scene(
        keys=[(0.0, Cam(48.1, 25.75, 190)), (1.0, Cam(48.1, 25.7, 215))],
        draw=d08,
        labels=[("Riyadh", 0.0), (st3[0], 0.1), (st3[1], 0.22), (st3[2], 0.34)],
        texts_at=0.3,
        texts=[
            (bx0, by + 44, "break-even", "التعادل", "", "c"),
            (bx0 + 4.0 * (bx1 - bx0) / 6.0, by - 66, "4.0", "4.0", "b", "c"),
            (bx0 + 5.6 * (bx1 - bx0) / 6.0, by - 66, "5.6 billion SAR", "5.6 مليار ريال", "b", "c"),
        ],
    )

    # t-09 who pays ---------------------------------------------------------------------------
    bars = fiscal_bars()
    gx0, gx1, gy = 520, 1700, 330

    def d09(c: Canvas, t: float, T_: float, ctx: dict) -> None:
        base_network(c, D, t, alpha=0.35)
        c.rect((gx0 - 440, gy - 120, gx1 + 40, gy + 300), (7, 11, 20), 0.75)
        vmax = max(b[2] for b in bars) * 1.05
        c.line(world_px([(gx0, gy - 60), (gx0, gy + 250)], c.cam), PAL["white"], 2, 0.8)
        for i, (_, p10, p90, p50) in enumerate(bars):
            a = ease(fr(t / T_, 0.15 + 0.15 * i, 0.55 + 0.15 * i))
            y = gy + i * 150
            xa = gx0 + p10 / vmax * (gx1 - gx0)
            xb = gx0 + (p10 + (p90 - p10) * a) / vmax * (gx1 - gx0)
            if a > 0:
                c.rect((xa, y - 20, xb, y + 20), PAL["warn"], 0.9)
                xm = gx0 + p50 / vmax * (gx1 - gx0)
                if a > 0.95:
                    c.rect((xm - 2, y - 30, xm + 2, y + 30), PAL["white"], 0.95)

    S["sh-08-52"] = Scene(
        keys=[(0.0, nat), (1.0, Cam(44.6, 23.6, 78))],
        draw=d09,
        texts=[
            (gx0 - 20, gy - 18, "Fully public", "تنفيذ حكومي كامل", "b", "r"),
            (gx0 - 20, gy + 132, "PPP, availability", "شراكة، بدفعات إتاحة", "b", "r"),
            (
                gx0 + 6,
                gy - 104,
                "zero: the state pays nothing net",
                "الصفر: الدولة ما تدفع شي",
                "",
                "l",
            ),
            (
                gx1,
                gy + 220,
                "net cost to the state →   bar: range of outcomes · white mark: median",
                "صافي التكلفة على الدولة →   العمود: نطاق النتائج · العلامة البيضاء: الوسيط",
                "",
                "r",
            ),
        ],
    )

    # t-10 closing: the whole network at night ------------------------------------------------
    def d10(c: Canvas, t: float, T_: float, ctx: dict) -> None:
        base_network(c, D, t)
        for n in (
            "Riyadh",
            "Jeddah",
            "Makkah",
            "Madinah",
            "Dammam",
            "Tabuk",
            "Abha",
            "Jazan",
            "Najran",
            "Hail",
            "Qassim",
            "Qurayyat",
        ):
            town(c, D, n, r=4.5)

    S["sh-08-53"] = Scene(
        keys=[(0.0, Cam(44.0, 24.4, 84)), (1.0, Cam(44.8, 24.2, 60))],
        draw=d10,
        side=True,
        labels=[("Riyadh", 0.1), ("Jeddah", 0.1), ("Dammam", 0.2), ("Tabuk", 0.3), ("Abha", 0.35)],
        legend=("existing", "committed"),
    )

    S["sh-08-54"] = Scene(
        keys=[(0.0, Cam(44.6, 23.8, 68)), (1.0, Cam(44.6, 23.8, 64))],
        draw=lambda c, t, T_, ctx: base_network(c, D, t, alpha=0.6),
        title=True,
        dim=lambda f: 0.45,
    )
    del T
    return S


def world_px(xy, cam: Cam) -> np.ndarray:
    """Screen pixel positions -> world coordinates under `cam` (for chart panels)."""
    a = np.asarray(xy, dtype="float64").reshape(-1, 2)
    u = (a[:, 0] - cam.cx) / cam.z + cam.lon * K
    v = (cam.cy - a[:, 1]) / cam.z + cam.lat
    return np.column_stack([u, v])


def air_over_rail() -> tuple[float, str]:
    """Air door-to-door time / fastest rail door-to-door time, Riyadh–Jeddah (p50 minutes,
    runs/study/rj/times-s1/times.csv: air = d2d_p50_min - vs_air_d2d_model_min)."""
    rows = list(csv.DictReader(runs_file("study/rj/times-s1/times.csv").open(encoding="utf-8")))
    best = min(rows, key=lambda r: float(r["d2d_p50_min"]))
    rail = float(best["d2d_p50_min"])
    air = rail - float(best["vs_air_d2d_model_min"])
    return air / rail, best["route"]


def attempts() -> tuple[np.ndarray, np.ndarray]:
    """runs/r6/results.tsv: every logged layout evaluation, normalised (capex_p50, robust_npv)."""
    rows = list(csv.DictReader(runs_file("r6/results.tsv").open(encoding="utf-8"), delimiter="\t"))
    xs, ys, kept = [], [], []
    for r in rows:
        try:
            x, y = float(r["capex_p50"]), float(r["robust_npv"])
        except (TypeError, ValueError):
            continue
        xs.append(x)
        ys.append(y)
        kept.append(r.get("decision", "") == "kept")  # the agent loop's kept layouts
    xa, ya = np.array(xs), np.array(ys)
    lo_x, hi_x = np.percentile(xa, [0.5, 99.5])
    lo_y, hi_y = np.percentile(ya, [0.5, 99.5])
    pts = np.column_stack(
        [np.clip((xa - lo_x) / (hi_x - lo_x), 0, 1), np.clip((ya - lo_y) / (hi_y - lo_y), 0, 1)]
    )
    return pts, np.array(kept)


def fiscal_bars() -> list[tuple[str, float, float, float]]:
    """Central case (S6-L2) net fiscal cost over 60 years by delivery model, robust population
    case (runs/r7/fiscal/fiscal.json): (model, p10, p90, p50) in SAR million."""
    d = json.loads(runs_file("r7/fiscal/fiscal.json").read_text(encoding="utf-8"))
    out = []
    for name, m in d["programmes"]["S6-L2"]["models"].items():
        c = m["by_pop"][d["robust_case"]]["net_fiscal_cost_60y"]
        out.append((name, c["p10"], c["p90"], c["p50"]))
    return out


# ---------------------------------------------------------------- frame loop


def layout(cam: Cam, sc: Scene, lang: str) -> Cam:
    """Place the camera target: centre of the map area beside a side caption, else a little
    above the frame centre (bottom caption)."""
    if sc.side:
        cam.cx = (W - 584) / 2 if lang == "ar" else 584 + (W - 584) / 2
        cam.cy = H / 2
    return cam


def scene_for(D: Data, sid: str) -> Scene:
    """The trailer scenes first (unchanged), else the main-cut scenes (film/sim_main.py)."""
    sc = scenes(D, {}).get(sid)
    if sc is None:
        from film import sim_main  # lazy: sim_main imports this module

        sc = sim_main.scenes(D)[sid]
    return sc


def prepare(shot: dict, lang: str, dur: float, work: Path, seed: int = 1) -> dict:
    """Everything a frame needs: scene, text layers (Chrome), label sprites, basemaps, ctx."""
    D = data()
    sc = scene_for(D, shot["id"])
    work.mkdir(parents=True, exist_ok=True)
    ov_png = work / f"overlay-{lang}.png"
    R.chrome_png(overlay_html(shot, lang, sc), ov_png, transparent=True)
    ov = np.asarray(Image.open(ov_png).convert("RGBA"), dtype="float32") / 255.0
    tx = None
    if sc.texts:
        tx_png = work / f"texts-{lang}.png"
        R.chrome_png(texts_html(lang, sc), tx_png, transparent=True)
        tx = np.asarray(Image.open(tx_png).convert("RGBA"), dtype="float32") / 255.0
    names = [n for n, _ in sc.labels]
    sprites = label_sprites(names, lang, work) if names else {}
    national = build_base(NATIONAL, NATIONAL_RES)
    detail = None
    n = max(int(round(dur * FPS)), 1)
    if sc.zoom_detail:
        exts = [
            layout(cam_at(sc.keys, i / max(n - 1, 1)), sc, lang).extent()
            for i in (0, n // 2, n - 1)
        ]
        u0 = min(e[0] for e in exts) - 0.05
        u1 = max(e[2] for e in exts) + 0.05
        v0 = min(e[1] for e in exts) - 0.05
        v1 = max(e[3] for e in exts) + 0.05
        zmax = max(k[1].z for k in sc.keys)
        r = max(1.0 / zmax, 0.0009)
        detail = build_base((u0 / K, v0, u1 / K, v1), round(r, 5))
    rng = np.random.default_rng(seed)
    ctx = {"rng": rng, "phase": rng.random(64)}
    return {
        "D": D,
        "sc": sc,
        "lang": lang,
        "dur": dur,
        "n": n,
        "ov": ov,
        "tx": tx,
        "sprites": sprites,
        "national": national,
        "detail": detail,
        "ctx": ctx,
        "insets": [inset_prep(x) for x in sc.insets],
        "fade_in": 0.35 if "fade in" in str(shot.get("transition", "")) else 0.0,
        "fade_out": 0.6 if "fade to black" in str(shot.get("transition", "")) else 0.0,
    }


def frame_at(P: dict, i: int) -> np.ndarray:
    """Frame i of the shot as uint8 RGB (H, W, 3)."""
    D, sc, lang, dur, n = P["D"], P["sc"], P["lang"], P["dur"], P["n"]
    detail, national, sprites = P["detail"], P["national"], P["sprites"]
    ov, tx = P["ov"], P["tx"]
    t = i / FPS
    f = i / max(n - 1, 1)
    cam = layout(cam_at(sc.keys, f), sc, lang)
    base = detail if detail is not None and detail.covers(cam.extent()) else national
    frame = np.asarray(base.crop(cam), dtype="float32") / 255.0 * sc.dim(f)
    c = Canvas(cam)
    sc.draw(c, t, dur, P["ctx"])
    vec = c.done()
    v = np.asarray(vec, dtype="float32") / 255.0
    glow = (
        vec.resize((W // 4, H // 4), Image.Resampling.BILINEAR)
        .filter(ImageFilter.GaussianBlur(3.5))
        .resize((W, H), Image.Resampling.BILINEAR)
    )
    g = np.asarray(glow, dtype="float32") / 255.0
    a = v[..., 3:4]
    frame = frame * (1 - a) + v[..., :3] * a
    frame = frame + g[..., :3] * g[..., 3:4] * 0.9
    for name, appear in sc.labels:
        p = D.places.get(name)
        spr = sprites.get(name)
        if p is None or spr is None or f < appear:
            continue
        x, y = cam.screen(p.reshape(1, 2))[0]
        al = fr(f, appear, appear + 0.08)
        sw, sh = spr.size
        side = sc.label_side.get(name) or LABEL_SIDE.get(name, "l" if lang == "ar" else "r")
        left = side == "l"
        ox = x - sw - 14 if left else x + 14
        oy = y - sh / 2
        frame = paste(frame, spr, int(ox), int(oy), al)
    for ip in P["insets"]:
        frame = inset_draw(frame, ip, f)
    oa = fr(t, 0.15, 0.6) if not sc.title else fr(t, 0.2, 0.9)
    frame = frame * (1 - ov[..., 3:4] * oa) + ov[..., :3] * ov[..., 3:4] * oa
    if tx is not None:
        ta = min(oa, fr(f, sc.texts_at, sc.texts_at + 0.06))
        frame = frame * (1 - tx[..., 3:4] * ta) + tx[..., :3] * tx[..., 3:4] * ta
    k = 1.0
    if P["fade_in"]:
        k = min(k, fr(t, 0, P["fade_in"]))
    if P["fade_out"]:
        k = min(k, fr(dur - t, 0, P["fade_out"]))
    frame = np.clip(frame * k, 0, 1)
    return (frame * 255 + 0.5).astype("uint8")


def render_shot(shot: dict, lang: str, dur: float, out: Path, seed: int = 1) -> dict:
    """Render one sim_map shot to `out` (H.264 1080p30). Returns a small log dict."""
    P = prepare(shot, lang, dur, out.parent / "sim" / shot["id"], seed)
    n = P["n"]
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "rawvideo"]
    cmd += ["-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-"]
    cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p"]
    cmd += ["-r", str(FPS), "-an", str(out)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    assert proc.stdin is not None
    try:
        for i in range(n):
            proc.stdin.write(frame_at(P, i).tobytes())
    finally:
        proc.stdin.close()
        rc = proc.wait()
    if rc:
        raise RuntimeError(f"ffmpeg exited {rc} for {out}")
    return {"frames": n, "detail_basemap": P["detail"] is not None}


def paste(frame: np.ndarray, spr: Image.Image, x: int, y: int, alpha: float) -> np.ndarray:
    s = np.asarray(spr, dtype="float32") / 255.0
    h, w = s.shape[:2]
    x0, y0, x1, y1 = max(x, 0), max(y, 0), min(x + w, W), min(y + h, H)
    if x0 >= x1 or y0 >= y1:
        return frame
    sub = s[y0 - y : y1 - y, x0 - x : x1 - x]
    a = sub[..., 3:4] * alpha
    frame[y0:y1, x0:x1] = frame[y0:y1, x0:x1] * (1 - a) + sub[..., :3] * a
    return frame


_DATA: Data | None = None


def data() -> Data:
    global _DATA
    if _DATA is None:
        _DATA = Data()
    return _DATA
