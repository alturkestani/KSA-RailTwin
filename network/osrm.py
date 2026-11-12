"""OSRM (MLD) preparation, a local `osrm-routed` server and batched /table queries.

Preparation writes ONLY under `data/ksa/osrm/<pbf-stem>/`: the PBF is symlinked there (osrm-extract
writes its outputs next to its input, and `data/osm/` is read-only), then
`osrm-extract -p car.lua`, `osrm-partition`, `osrm-customize`. Each step runs under
`/usr/bin/time -l` and the wall time, peak RSS and output size go to `prep_stats.json`.

CLI:
  uv run python -m network.osrm prepare --pbf data/osm/jeddah.osm.pbf [--threads N]
  uv run python -m network.osrm estimate --pbf data/osm/gcc-states-latest.osm.pbf
  uv run python -m network.osrm calibrate --osrm-dir data/ksa/osrm/jeddah   (prints scale YAML)
"""

from __future__ import annotations

import contextlib
import hashlib
import json
import os
import re
import shutil
import socket
import subprocess
import time
import urllib.error
import urllib.request
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import numpy as np
import typer
import yaml

from common import REPO_ROOT

OSRM_ROOT = REPO_ROOT / "data" / "ksa" / "osrm"
SCALE_YAML = Path(__file__).with_name("osrm_scale.yaml")
PROFILE_CANDIDATES = [
    Path("/opt/homebrew/share/osrm-backend/profiles/car.lua"),
    Path("/opt/homebrew/share/osrm/profiles/car.lua"),
    Path("/usr/local/share/osrm/profiles/car.lua"),
]
STEPS = ("extract", "partition", "customize")
app = typer.Typer(add_completion=False, help="OSRM MLD preparation, estimate and table queries.")


def osrm_bin(name: str) -> str:
    exe = shutil.which(f"osrm-{name}") or f"/opt/homebrew/bin/osrm-{name}"
    if not Path(exe).exists():
        raise FileNotFoundError(f"osrm-{name} not found (brew install osrm-backend)")
    return exe


def osrm_version() -> str:
    out = subprocess.run([osrm_bin("routed"), "--version"], capture_output=True, text=True)
    return (out.stdout or out.stderr).strip().splitlines()[-1]


def car_profile() -> Path:
    for p in PROFILE_CANDIDATES:
        if p.exists():
            return p
    raise FileNotFoundError("car.lua not found in the Homebrew share dir")


def pbf_stem(pbf: Path) -> str:
    name = Path(pbf).name
    for suf in (".osm.pbf", ".pbf", ".osm"):
        if name.endswith(suf):
            return name[: -len(suf)]
    return Path(pbf).stem


def osrm_dir_for(pbf: Path, root: Path = OSRM_ROOT) -> Path:
    return root / pbf_stem(pbf)


def base_path(osrm_dir: Path) -> Path:
    """`<dir>/<stem>.osrm` (the MLD file set prefix)."""
    return Path(osrm_dir) / f"{Path(osrm_dir).name}.osrm"


def is_prepared(osrm_dir: Path) -> bool:
    b = base_path(osrm_dir)
    return all(Path(str(b) + s).exists() for s in (".mldgr", ".cells", ".partition"))


def dir_bytes(p: Path) -> int:
    return sum(f.stat().st_size for f in Path(p).iterdir() if f.is_file() and not f.is_symlink())


def sha256_file(path: Path, chunk: int = 1 << 20) -> str:
    """SHA-256 of a file (rule 10: skims and graphs record the PBF hash)."""
    h = hashlib.sha256()
    with open(Path(path).resolve(), "rb") as f:
        while b := f.read(chunk):
            h.update(b)
    return h.hexdigest()


def disk_free_bytes(path: Path = REPO_ROOT) -> int:
    return shutil.disk_usage(path).free


_RSS = re.compile(r"(\d+)\s+maximum resident set size")
_FOOT = re.compile(r"(\d+)\s+peak memory footprint")


def _timed(cmd: list[str], log) -> tuple[float, int, int]:
    """Run under /usr/bin/time -l; return (wall s, peak RSS bytes, peak footprint bytes).

    macOS reports both; the footprint also counts compressed and swapped pages, so it is the
    better guide to memory pressure on an 18 GB machine."""
    t0 = time.monotonic()
    proc = subprocess.run(["/usr/bin/time", "-l", *cmd], capture_output=True, text=True)
    wall = time.monotonic() - t0
    log.write(f"$ {' '.join(cmd)}\n{proc.stdout}\n{proc.stderr}\n")
    log.flush()
    if proc.returncode != 0:
        raise RuntimeError(f"{cmd[0]} failed ({proc.returncode}); see log")
    m, f = _RSS.search(proc.stderr), _FOOT.search(proc.stderr)
    return wall, int(m.group(1)) if m else -1, int(f.group(1)) if f else -1


def prepare(
    pbf: Path, root: Path = OSRM_ROOT, threads: int | None = None, log_path: Path | None = None
) -> dict[str, Any]:
    """osrm-extract/partition/customize (MLD) into `<root>/<stem>/`; returns prep stats."""
    pbf = Path(pbf)
    out = osrm_dir_for(pbf, root)
    out.mkdir(parents=True, exist_ok=True)
    suffix = pbf.name[len(pbf_stem(pbf)) :] or ".osm.pbf"  # keep the format suffix (.osm/.pbf)
    link = out / f"{out.name}{suffix}"
    if link.is_symlink() or link.exists():
        link.unlink()
    link.symlink_to(os.path.relpath(pbf.resolve(), out))
    base = base_path(out)
    thr = ["-t", str(threads)] if threads else []
    log_path = log_path or (out / "prep.log")
    stats: dict[str, Any] = {
        "pbf": os.path.relpath(pbf, REPO_ROOT) if pbf.is_absolute() else str(pbf),
        "pbf_bytes": pbf.resolve().stat().st_size,
        "pbf_sha256": sha256_file(pbf),
        "osrm_version": osrm_version(),
        "profile": str(car_profile()),
        "algorithm": "mld",
        "threads": threads or os.cpu_count(),
        "disk_free_before": disk_free_bytes(),
        "steps": {},
    }
    with open(log_path, "a", encoding="utf-8") as log:
        cmds = {
            "extract": [osrm_bin("extract"), "-p", str(car_profile()), *thr, str(link)],
            "partition": [osrm_bin("partition"), *thr, str(base)],
            "customize": [osrm_bin("customize"), *thr, str(base)],
        }
        for step in STEPS:
            wall, rss, foot = _timed(cmds[step], log)
            stats["steps"][step] = {
                "wall_s": round(wall, 2),
                "peak_rss_bytes": rss,
                "peak_footprint_bytes": foot,
            }
    stats["output_bytes"] = dir_bytes(out)
    stats["disk_free_after"] = disk_free_bytes()
    stats["wall_s_total"] = round(sum(s["wall_s"] for s in stats["steps"].values()), 2)
    stats["peak_rss_bytes"] = max(s["peak_rss_bytes"] for s in stats["steps"].values())
    stats["peak_footprint_bytes"] = max(s["peak_footprint_bytes"] for s in stats["steps"].values())
    stats["profile"] = os.path.basename(stats["profile"])
    (out / "prep_stats.json").write_text(json.dumps(stats, indent=2) + "\n", encoding="utf-8")
    return stats


# --------------------------------------------------------------------------- estimate
def load_scale(path: Path = SCALE_YAML) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


def point_from_stats(stats: dict[str, Any], name: str) -> dict[str, Any]:
    """One measured reference point for osrm_scale.yaml."""
    return {
        "name": name,
        "pbf_mb": round(stats["pbf_bytes"] / 1e6, 3),
        "wall_s": stats["wall_s_total"],
        "peak_rss_mb": round(stats["peak_rss_bytes"] / 1e6, 1),
        "peak_footprint_mb": round(stats.get("peak_footprint_bytes", -1) / 1e6, 1),
        "output_mb": round(stats["output_bytes"] / 1e6, 1),
    }


def fit(points: list[dict[str, Any]], key: str) -> tuple[float, float]:
    """Least-squares affine fit `key = a + b * pbf_mb` (one point: b = key / mb, a = 0)."""
    x = np.array([p["pbf_mb"] for p in points], float)
    y = np.array([p[key] for p in points], float)
    if len(x) == 1:
        return 0.0, float(y[0] / x[0])
    b, a = np.polyfit(x, y, 1)
    return float(a), float(b)


def estimate(pbf_bytes: int, scale: dict[str, Any]) -> dict[str, Any]:
    """Affine extrapolation from the measured reference points (see osrm_scale.yaml).

    The worst case also scales the slope by `slope_margin` (registered assumption) because the
    reference clips are denser urban areas than the national desert extract, or the reverse.
    """
    mb = pbf_bytes / 1e6
    pts = scale["points"]
    margin = float(scale["slope_margin"]["value"])
    out: dict[str, Any] = {
        "pbf_mb": round(mb, 1),
        "model": "affine least squares",
        "n_points": len(pts),
    }
    keys = [("wall_s", "minutes", 60.0), ("peak_rss_mb", "peak_ram_gib", 2**30 / 1e6)]
    if all("peak_footprint_mb" in p for p in pts):
        keys.append(("peak_footprint_mb", "peak_footprint_gib", 2**30 / 1e6))
    for key, name, div in (
        *keys,
        ("output_mb", "disk_gib", 2**30 / 1e6),
    ):
        a, b = fit(pts, key)
        out[name] = round((a + b * mb) / div, 2)
        out[f"{name}_worst"] = round((a + b * mb * margin) / div, 2)
    return out


# --------------------------------------------------------------------------- server + table
def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@contextlib.contextmanager
def server(osrm_dir: Path, max_table: int = 1000, timeout_s: float = 120) -> Iterator[str]:
    """Start `osrm-routed --algorithm mld` on localhost; yield the base URL; stop it after."""
    if not is_prepared(osrm_dir):
        raise FileNotFoundError(f"{osrm_dir} is not an MLD-prepared OSRM dir (run prepare)")
    port = free_port()
    cmd = [osrm_bin("routed"), "--algorithm", "mld", "--ip", "127.0.0.1", "--port", str(port)]
    cmd += ["--max-table-size", str(max_table), str(base_path(osrm_dir))]
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    url = f"http://127.0.0.1:{port}"
    try:
        t0 = time.monotonic()
        while True:
            if proc.poll() is not None:
                raise RuntimeError("osrm-routed exited during start-up")
            try:
                urllib.request.urlopen(f"{url}/nearest/v1/driving/0,0", timeout=1)
                break
            except urllib.error.HTTPError:
                break  # server answers (400 for a bad point is fine)
            except OSError:
                if time.monotonic() - t0 > timeout_s:
                    raise TimeoutError("osrm-routed did not start") from None
                time.sleep(0.2)
        yield url
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()


def _get(url: str) -> dict[str, Any]:
    with urllib.request.urlopen(url, timeout=600) as r:
        return json.loads(r.read().decode("utf-8"))


def table(
    url: str,
    src_lonlat: np.ndarray,
    dst_lonlat: np.ndarray,
    batch: int = 100,
) -> dict[str, np.ndarray]:
    """Full sources x destinations matrices: duration_s, distance_m (NaN = no route),
    plus src_snap_m / dst_snap_m (distance from the input point to the snapped road)."""
    ns, nd = len(src_lonlat), len(dst_lonlat)
    dur = np.full((ns, nd), np.nan)
    dist = np.full((ns, nd), np.nan)
    ssnap = np.full(ns, np.nan)
    dsnap = np.full(nd, np.nan)
    for i0 in range(0, ns, batch):
        si = np.arange(i0, min(ns, i0 + batch))
        for j0 in range(0, nd, batch):
            dj = np.arange(j0, min(nd, j0 + batch))
            pts = np.vstack([src_lonlat[si], dst_lonlat[dj]])
            coords = ";".join(f"{x:.6f},{y:.6f}" for x, y in pts)
            srcs = ";".join(map(str, range(len(si))))
            dsts = ";".join(map(str, range(len(si), len(si) + len(dj))))
            q = (
                f"{url}/table/v1/driving/{coords}?sources={srcs}&destinations={dsts}"
                "&annotations=duration,distance"
            )
            res = _get(q)
            if res.get("code") != "Ok":
                raise RuntimeError(f"OSRM table: {res.get('code')} {res.get('message')}")
            d = np.array(res["durations"], dtype=float)  # None -> nan
            m = np.array(res["distances"], dtype=float)
            dur[np.ix_(si, dj)] = d
            dist[np.ix_(si, dj)] = m
            ssnap[si] = [w.get("distance", np.nan) for w in res["sources"]]
            dsnap[dj] = [w.get("distance", np.nan) for w in res["destinations"]]
    return {"duration_s": dur, "distance_m": dist, "src_snap_m": ssnap, "dst_snap_m": dsnap}


# --------------------------------------------------------------------------- CLI
@app.command("prepare")
def prepare_cmd(
    pbf: Path = typer.Option(..., exists=True),
    root: Path = typer.Option(OSRM_ROOT, help="output root (default data/ksa/osrm)"),
    threads: int = typer.Option(0, help="0 = all cores"),
    log: Path = typer.Option(None, help="log file (default <dir>/prep.log)"),
) -> None:
    """Run osrm-extract/partition/customize (MLD) and write prep_stats.json."""
    stats = prepare(pbf, root, threads or None, log)
    typer.echo(json.dumps(stats, indent=2))


@app.command("estimate")
def estimate_cmd(
    pbf: Path = typer.Option(..., exists=True),
    scale: Path = typer.Option(SCALE_YAML),
    gate_gib: float = typer.Option(15.0, help="minimum free GiB after the output (disk gate)"),
) -> None:
    """Dry run: estimated minutes, peak RAM and disk for preparing a PBF; checks the disk gate."""
    sc = load_scale(scale)
    est = estimate(Path(pbf).resolve().stat().st_size, sc)
    free = disk_free_bytes() / 2**30
    est["disk_free_gib_now"] = round(free, 1)
    est["disk_free_gib_after"] = round(free - est["disk_gib_worst"], 1)
    est["gate_gib"] = gate_gib
    est["gate_ok"] = est["disk_free_gib_after"] >= gate_gib
    est["max_minutes"] = sc["max_minutes"]
    est["time_ok"] = est["minutes_worst"] <= sc["max_minutes"]
    typer.echo(json.dumps(est, indent=2))


@app.command("calibrate")
def calibrate_cmd(osrm_dir: Path = typer.Option(..., exists=True)) -> None:
    """Print a reference point (for osrm_scale.yaml `points:`) from a prep_stats.json."""
    stats = json.loads((osrm_dir / "prep_stats.json").read_text(encoding="utf-8"))
    typer.echo(yaml.safe_dump([point_from_stats(stats, osrm_dir.name)], sort_keys=False))


if __name__ == "__main__":
    app()
