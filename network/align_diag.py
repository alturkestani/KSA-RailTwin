# ruff: noqa: E501
"""Why do routed validation lines drift from the real ones? (FIX_R7 item 4a)

For each validation line (HHR, SAR North, SAR East) the mean offset that `network.align validate`
reports (0.5 x [mean distance of routed samples to OSM + mean distance of OSM samples to the routed
line], 2,000 samples each, `network.align.compare`) is split **exactly** into station-to-station legs
and into causes. Every sample gets one cause, in this order (thresholds A-align-110..113):

1. `within_1km`: offset <= 1 km. DEM resolution (3" = 90 m), the curve smoothing (up to 1.5 km,
   A-align-052) and the OSM digitisation live here.
2. `urban_approach`: the sample lies within 25 km of a station whose 3 km neighbourhood is at least
   15 % urban or built-up (OSM landuse / WorldCover 50).
3. the cause of its leg, read from the leg's cost decomposition on the routing surface. The real
   (OSM) leg and the routed leg are both costed along their own geometry with the same edge cost as
   the router (length x grade term or structure factor x (1 + area penalties) x corridor factor). If
   the real leg costs at most 2 % more than the routed leg, the surface is indifferent between them:
   `lateral_freedom_flat` (median relief < 40 m) or `lateral_freedom_relief`. Otherwise the largest
   positive component of the cost difference names the cause: an area penalty (`avoids_<area>`: the
   router avoided sand, a wadi, a protected area ... that the real line crosses), the grade term
   (`grade_choice`: the real line takes grades or structures the surface avoids), or the length and
   corridor terms (`unseen_corridor`: the real line is longer with no surface reason, e.g. a
   historic or engineering corridor).

The cost decomposition samples the surface every 90 m along each line; it is a diagnostic, not the
router's Dijkstra cost (which works on a 16-connected grid), so ratios are approximate.

    uv run python -m network.align_diag diagnose --run runs/align/validation-s1 --out runs/align/diag-v1-s1

Label: hypothetical alignment (ours): indicative engineering sketch, not a design.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import typer
from scipy import ndimage

from common import REPO_ROOT
from common.runmeta import seed_option, write_meta
from network import align as al
from network import align_data as ad

LABEL = al.LABEL
# diagnostic thresholds (registered as A-align-110..113)
RESOLUTION_KM = 1.0  # A-align-110
URBAN_STATION_KM = 25.0  # A-align-111
URBAN_STATION_RADIUS_KM = 3.0  # A-align-111
URBAN_STATION_SHARE = 0.15  # A-align-111
INDIFFERENT_RATIO = 1.02  # A-align-112
FLAT_RELIEF_M = 40.0  # A-align-113 (= mixed_relief_m, A-align-060)
AREAS = ("urban", "protected", "military", "sand", "sabkha", "wadi", "water")
N_SAMPLES = 2000  # as network.align.compare

app = typer.Typer(add_completion=False, help=__doc__, no_args_is_help=True)


@app.callback()
def _group() -> None:
    """Validation-offset diagnosis (FIX_R7 item 4a)."""


def _stations_xy(c: dict[str, Any], t: Any) -> np.ndarray:
    st = sorted(c["stations"], key=lambda s: float(s["km_post"]))
    x, y = t.transform([float(s["lon"]) for s in st], [float(s["lat"]) for s in st])
    return np.column_stack([x, y])


def urban_stations(c: dict[str, Any], root: Path) -> dict[str, float]:
    """Urban/built-up share within URBAN_STATION_RADIUS_KM of each station (3" cells)."""
    out = {}
    for s in c["stations"]:
        la, lo = float(s["lat"]), float(s["lon"])
        d = URBAN_STATION_RADIUS_KM / 110.574 + 0.01
        g = al.read_grid((lo - d * 1.2, la - d, lo + d * 1.2, la + d), 1, root)
        H, W = g.dem.shape
        lat = g.lat(np.arange(H))[:, None] * np.ones((1, W))
        lon = g.lon(np.arange(W))[None, :] * np.ones((H, 1))
        inside = al.gc_km(lat, lon, la, lo) <= URBAN_STATION_RADIUS_KM
        u = (g.flags & (ad.FLAGS["urban"] | ad.FLAGS["builtup"])) > 0
        out[s["id"]] = round(float(u[inside].mean()) if inside.any() else 0.0, 3)
    return out


def surface_cost(
    lat: np.ndarray,
    lon: np.ndarray,
    kl: al.Klass,
    w: dict[str, Any],
    exclude: list[str],
    root: Path,
) -> dict[str, float]:
    """Edge cost of a polyline on the router's 3" surface, split into components (SAR-free units:
    metre-equivalents). length = plain length; grade = extra from the grade term or structures;
    <area> = extra from each area penalty; corridor = (negative) corridor bonus."""
    pad = 0.05
    g = al.read_grid((lon.min() - pad, lat.min() - pad, lon.max() + pad, lat.max() + pad), 1, root)
    step_c = int(
        round(
            float(al._v(w["router"]["coarse_arcsec"]))
            / float(al._v(w["data"]["resolution_arcsec"]))
        )
    )
    gc = al.read_grid(
        (lon.min() - pad, lat.min() - pad, lon.max() + pad, lat.max() + pad), step_c, root
    )
    facc_c = al.flow_accumulation_km2(gc)
    H, W = g.dem.shape
    rr = np.arange(H)[:, None] * np.ones((1, W))
    cc = np.arange(W)[None, :] * np.ones((H, 1))
    facc = al.nearest_flags(gc, g.lat(rr).ravel(), g.lon(cc).ravel(), facc_c).reshape(H, W)
    rail = al.rail_mask(g, exclude, root)
    _, corr = al.penalty_surface(g, w, facc, rail)
    Wt = w["weights"]
    f = g.flags

    def on(k: str) -> np.ndarray:
        return (f & ad.FLAGS[k]) > 0

    parts = {
        "urban": float(al._v(Wt["urban"])) * (on("urban") | on("builtup")),
        "protected": float(al._v(Wt["protected"])) * on("protected"),
        "military": float(al._v(Wt["military"])) * on("military"),
        "sand": float(al._v(Wt["sand"])) * on("sand"),
        "sabkha": float(al._v(Wt["sabkha"])) * on("sabkha"),
        "wadi": float(al._v(Wt["wadi"]))
        * (on("waterway") | (facc >= float(al._v(w["wadi"]["flow_accumulation_km2"])))),
        "water": float(al._v(Wt["water"])) * on("water"),
    }
    dy, _ = al.cell_m(g)
    sig_m = float(al._v(w["router"]["grade_smoothing_m"]))
    zf = np.where(np.isnan(g.dem), np.nanmean(g.dem), g.dem)
    zs = ndimage.gaussian_filter(zf.astype(np.float64), sigma=max(sig_m / dy, 0.5), mode="nearest")
    # resample the polyline every ~90 m
    t = al.to_xy(lat, lon, float(lat.mean()), float(lon.mean()))
    x, y = t.transform(lon, lat)
    xy = al.resample(np.column_stack([x, y]), 90.0)
    ql, qa = t.transform(xy[:, 0], xy[:, 1], direction="INVERSE")
    qa, ql = np.asarray(qa), np.asarray(ql)
    z = al.bilinear(g, qa, ql, zs)
    L = np.hypot(*np.diff(xy, axis=0).T)
    gr = np.abs(np.diff(z)) / np.maximum(L, 1e-6)
    wg = float(al._v(Wt["grade"]))
    kx = float(al._v(Wt.get("structure_grade_exponent", 0.0)))
    over = np.maximum(gr / kl.cap, 1.0) ** kx
    base = np.where(gr <= kl.cap, 1.0 + wg * (gr / kl.cap) ** 2, kl.sf * over)
    pv = {k: al.nearest_flags(g, qa, ql, v.astype(float)) for k, v in parts.items()}
    pmid = {k: 0.5 * (v[:-1] + v[1:]) for k, v in pv.items()}
    ptot = sum(pmid.values())
    cv = al.nearest_flags(g, qa, ql, corr.astype(np.uint8)).astype(bool)
    cf = np.where(cv[:-1] & cv[1:], 1.0 - float(al._v(Wt["corridor_bonus"])), 1.0)
    total = L * base * (1.0 + ptot) * cf
    out = {"length": float(L.sum()), "grade": float((L * (base - 1.0)).sum())}
    for k, v in pmid.items():
        out[k] = float((L * base * v).sum())
    out["corridor"] = float((L * base * (1.0 + ptot) * (cf - 1.0)).sum())
    out["total"] = float(total.sum())
    hw = al.nearest_flags(
        g, qa, ql, ndimage.binary_dilation(on("highway"), iterations=22).astype(np.uint8)
    )
    out["near_highway_share"] = float(hw.mean())  # within ~2 km of a highway
    return out


def diagnose_line(
    lid: str, run: Path, w: dict[str, Any], root: Path
) -> tuple[pd.DataFrame, pd.DataFrame]:
    from shapely.geometry import LineString, Point
    from shapely.ops import substring

    spec = w["validation"]["lines"][lid]
    kl = al.line_class(spec["class"], w, root)
    exclude = al.VALIDATION_EXCLUDE.get(lid, [lid])
    c = al.line_as_corridor(lid, root)
    prof = pd.read_parquet(run / lid / "profile.parquet")
    osm, _ = al.osm_line(lid, root, main_only=True)
    lat0, lon0 = float(prof.lat.mean()), float(prof.lon.mean())
    t = al.to_xy(np.zeros(1), np.zeros(1), lat0, lon0)
    pxy = np.column_stack(t.transform(prof.lon.to_numpy(), prof.lat.to_numpy()))
    rl = LineString(pxy)
    ol = al._proj(t, osm)
    a, b = ol.project(Point(rl.coords[0])), ol.project(Point(rl.coords[-1]))
    ol = substring(ol, min(a, b), max(a, b))
    if a > b:
        ol = LineString(list(ol.coords)[::-1])
    dr = np.linspace(0, rl.length, N_SAMPLES)
    do = np.linspace(0, ol.length, N_SAMPLES)
    pr = np.array([rl.interpolate(d).coords[0] for d in dr])
    po = np.array([ol.interpolate(d).coords[0] for d in do])
    d_ro = np.array([ol.distance(Point(p)) for p in pr]) / 1000
    d_or = np.array([rl.distance(Point(p)) for p in po]) / 1000
    # legs: routed samples by the profile's leg; OSM samples by the stations projected on the OSM line
    from scipy.spatial import cKDTree

    leg_r = prof.leg.to_numpy()[cKDTree(pxy).query(pr)[1]]
    sxy = _stations_xy(c, t)
    cuts = np.array([ol.project(Point(p)) for p in sxy])
    leg_o = np.clip(np.searchsorted(cuts[1:-1], do, side="right"), 0, len(sxy) - 2)
    st = sorted(c["stations"], key=lambda s: float(s["km_post"]))
    ush = urban_stations(c, root)
    urban_xy = np.array([sxy[i] for i, s in enumerate(st) if ush[s["id"]] >= URBAN_STATION_SHARE])

    def near_urban(p: np.ndarray) -> np.ndarray:
        if len(urban_xy) == 0:
            return np.zeros(len(p), bool)
        return cKDTree(urban_xy).query(p)[0] / 1000 <= URBAN_STATION_KM

    # per-leg surface cost of the OSM and the routed geometry
    ilat = lambda xy: np.asarray(t.transform(xy[:, 0], xy[:, 1], direction="INVERSE")[1])  # noqa: E731
    ilon = lambda xy: np.asarray(t.transform(xy[:, 0], xy[:, 1], direction="INVERSE")[0])  # noqa: E731
    legs = []
    for li in range(len(st) - 1):
        oxy = (
            np.array(substring(ol, cuts[li], cuts[li + 1]).coords)
            if cuts[li + 1] > cuts[li]
            else po[leg_o == li]
        )
        rxy = pxy[prof.leg.to_numpy() == li]
        co = surface_cost(ilat(oxy), ilon(oxy), kl, w, exclude, root)
        cr = surface_cost(ilat(rxy), ilon(rxy), kl, w, exclude, root)
        rel = float(np.median(prof.relief_m[prof.leg == li]))
        ratio = co["total"] / cr["total"]
        diff = {k: co[k] - cr[k] for k in ("length", "grade", *AREAS, "corridor")}
        if ratio <= INDIFFERENT_RATIO:
            cause = "lateral_freedom_flat" if rel < FLAT_RELIEF_M else "lateral_freedom_relief"
        else:
            comp = {
                "grade_choice": diff["grade"],
                "unseen_corridor": diff["length"] + diff["corridor"],
                **{f"avoids_{k}": diff[k] for k in AREAS},
            }
            cause = max(comp, key=lambda k: comp[k])
        legs.append(
            {
                "line": lid,
                "leg": li,
                "from": st[li]["id"],
                "to": st[li + 1]["id"],
                "osm_km": round(co["length"] / 1000, 2),
                "routed_km": round(cr["length"] / 1000, 2),
                "cost_osm_km_eq": round(co["total"] / 1000, 2),
                "cost_routed_km_eq": round(cr["total"] / 1000, 2),
                "cost_ratio": round(ratio, 4),
                **{f"d_{k}_km_eq": round(v / 1000, 2) for k, v in diff.items()},
                "osm_near_highway": round(co["near_highway_share"], 3),
                "routed_near_highway": round(cr["near_highway_share"], 3),
                "median_relief_m": rel,
                "leg_cause": cause,
            }
        )
    L = pd.DataFrame(legs)
    leg_cause = dict(zip(L.leg, L.leg_cause, strict=True))

    def causes(d: np.ndarray, p: np.ndarray, lg: np.ndarray) -> np.ndarray:
        u = near_urban(p)
        return np.array(
            [
                "within_1km"
                if di <= RESOLUTION_KM
                else "urban_approach"
                if ui
                else leg_cause[int(gi)]
                for di, ui, gi in zip(d, u, lg, strict=True)
            ]
        )

    S = pd.concat(
        [
            pd.DataFrame(
                {
                    "line": lid,
                    "side": "routed_to_osm",
                    "leg": leg_r,
                    "offset_km": d_ro,
                    "cause": causes(d_ro, pr, leg_r),
                }
            ),
            pd.DataFrame(
                {
                    "line": lid,
                    "side": "osm_to_routed",
                    "leg": leg_o,
                    "offset_km": d_or,
                    "cause": causes(d_or, po, leg_o),
                }
            ),
        ],
        ignore_index=True,
    )
    # contribution of each sample to the symmetric mean offset: 0.5 x d / N on its side
    S["contribution_km"] = 0.5 * S.offset_km / N_SAMPLES
    leg_off = S.groupby("leg").contribution_km.sum()
    L["offset_contribution_km"] = L.leg.map(leg_off).fillna(0.0).round(3)
    L["leg_mean_offset_km"] = [
        round(float(0.5 * (d_ro[leg_r == i].mean() + d_or[leg_o == i].mean())), 3) for i in L.leg
    ]
    L["station_urban_share_from"] = [ush[s] for s in L["from"]]
    return L, S


@app.command("diagnose")
def diagnose_cmd(
    run: Path = typer.Option(Path("runs/align/validation-s1")),
    weights: Path = typer.Option(None),
    seed: int = seed_option(),
    out: Path = typer.Option(Path("runs/align/diag-v1-s1")),
    root: Path = typer.Option(REPO_ROOT, hidden=True),
) -> None:
    """Split each validation line's mean offset by leg and cause."""
    run = run if run.is_absolute() else root / run
    out = out if out.is_absolute() else root / out
    w = al.load_weights(weights, root)
    legs, samples = [], []
    for lid in w["validation"]["lines"]:
        L, S = diagnose_line(lid, run, w, root)
        legs.append(L)
        samples.append(S)
    L = pd.concat(legs, ignore_index=True)
    S = pd.concat(samples, ignore_index=True)
    C = S.pivot_table(
        index="line", columns="cause", values="contribution_km", aggfunc="sum", fill_value=0.0
    )
    C["mean_offset_km"] = C.sum(axis=1)
    out.mkdir(parents=True, exist_ok=True)
    L.to_csv(out / "legs.csv", index=False)
    C.round(3).to_csv(out / "causes.csv")
    S.groupby(["line", "leg", "cause"]).contribution_km.sum().round(4).reset_index().to_csv(
        out / "leg_causes.csv", index=False
    )
    write_meta(
        out,
        seed,
        {"weights": w, "run": str(run.relative_to(root))},
        extra={
            "label": LABEL,
            "weights_hash": al.weights_hash(w),
            "thresholds": {
                "resolution_km": RESOLUTION_KM,
                "urban_station_km": URBAN_STATION_KM,
                "urban_station_radius_km": URBAN_STATION_RADIUS_KM,
                "urban_station_share": URBAN_STATION_SHARE,
                "indifferent_ratio": INDIFFERENT_RATIO,
                "flat_relief_m": FLAT_RELIEF_M,
            },
        },
    )
    pd.set_option("display.width", 250)
    typer.echo(L.to_string(index=False))
    typer.echo(C.round(3).to_string())


if __name__ == "__main__":
    app()
