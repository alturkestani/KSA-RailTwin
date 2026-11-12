"""Drivable road graph from an OSM PBF/XML/OPL file, OSMnx-equivalent, without OSMnx.

Pipeline (path recorded as `osmium+networkx`):
1. `osmium tags-filter <in> w/highway=<drivable classes>` (referenced nodes kept),
2. `osmium add-locations-to-ways -f opl` (every way with its node ids and coordinates),
3. parse OPL; drop excluded ways (access, service=parking_aisle, ...; `road_speeds.yaml`),
4. one directed edge per consecutive node pair, honouring `oneway` (yes/true/1, -1/reverse,
   implied for motorway and roundabouts unless `oneway=no`),
5. edge length = WGS84 geodesic metres (pyproj.Geod), free-flow speed = numeric `maxspeed`
   (or `maxspeed:forward/backward`) x `maxspeed_factor`, else the class default speed.

If `import osmnx` succeeds, `build_graph(..., prefer_osmnx=True)` may use it instead; the path
that ran is returned in `RoadGraph.path` and written to meta.json.

`RoadGraph.csr()` collapses parallel edges to the fastest one and gives SciPy CSR matrices of
seconds and metres for fast Dijkstra; `largest_scc` restricts snapping to the largest strongly
connected component (as OSMnx does with `retain_all=False`).
"""

from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import networkx as nx
import numpy as np
import yaml
from pyproj import Geod
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components

SPEEDS_YAML = Path(__file__).with_name("road_speeds.yaml")
_OPL_ESC = re.compile(r"%([0-9a-fA-F]+)%")
_NUM = re.compile(r"(\d+(?:\.\d+)?)")
MIN_EDGE_S = 1e-3  # numerical floor so zero-length OSM segments stay edges in sparse Dijkstra
MPH_TO_KMH = 1.609344  # exact definition of the international mile


def load_speed_config(path: Path = SPEEDS_YAML) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


def osmium_bin() -> str:
    exe = shutil.which("osmium") or "/opt/homebrew/bin/osmium"
    if not Path(exe).exists():
        raise FileNotFoundError("osmium-tool not found (brew install osmium-tool)")
    return exe


def osmium_version() -> str:
    out = subprocess.run([osmium_bin(), "--version"], capture_output=True, text=True, check=True)
    return out.stdout.splitlines()[0].strip()


def _unescape(s: str) -> str:
    return _OPL_ESC.sub(lambda m: chr(int(m.group(1), 16)), s)


def parse_opl_way(line: str) -> tuple[int, dict[str, str], list[tuple[int, float, float]]] | None:
    """Parse one OPL way line `w<id> ... T<tags> N<nodes>`; None for non-way lines."""
    if not line.startswith("w"):
        return None
    parts = line.rstrip("\n").split(" ")
    wid = int(parts[0][1:])
    tags: dict[str, str] = {}
    nodes: list[tuple[int, float, float]] = []
    for p in parts[1:]:
        if p.startswith("T") and len(p) > 1:
            for kv in p[1:].split(","):
                k, _, v = kv.partition("=")
                tags[_unescape(k)] = _unescape(v)
        elif p.startswith("N") and len(p) > 1:
            for ref in p[1:].split(","):
                nid, xs, rest = ref[1:].partition("x")
                if not xs:  # no location in the extract
                    continue
                x, _, y = rest.partition("y")
                if not x or not y:
                    continue
                nodes.append((int(nid), float(x), float(y)))
    return wid, tags, nodes


def parse_maxspeed(v: str | None) -> float | None:
    """km/h from an OSM maxspeed value; None for none/signals/zone codes."""
    if not v:
        return None
    m = _NUM.search(v)
    if not m:
        return None
    kmh = float(m.group(1))
    if "mph" in v:
        kmh *= MPH_TO_KMH
    return kmh if kmh > 0 else None


def way_directions(tags: dict[str, str], cfg: dict[str, Any]) -> tuple[bool, bool]:
    """(forward, backward) allowed."""
    ow = tags.get("oneway", "").lower()
    if ow in ("yes", "true", "1"):
        return True, False
    if ow in ("-1", "reverse"):
        return False, True
    if ow in ("no", "false", "0"):
        return True, True
    if tags.get("highway") in cfg.get("implied_oneway_highway", []):
        return True, False
    if tags.get("junction") in cfg.get("implied_oneway_junction", []):
        return True, False
    return True, True


def is_drivable(tags: dict[str, str], cfg: dict[str, Any]) -> bool:
    if tags.get("highway") not in cfg["drivable_classes"]:
        return False
    for key, bad in cfg.get("exclude", {}).items():
        if tags.get(key) in set(map(str, bad)):
            return False
    return True


def way_speeds(tags: dict[str, str], cfg: dict[str, Any]) -> tuple[float, float, str]:
    """(forward km/h, backward km/h, source) free-flow speeds."""
    factor = float(cfg["maxspeed_factor"]["value"])
    default = float(cfg["default_speed_kmh"][tags["highway"]]["value"])
    base = parse_maxspeed(tags.get("maxspeed"))
    fwd = parse_maxspeed(tags.get("maxspeed:forward")) or base
    bwd = parse_maxspeed(tags.get("maxspeed:backward")) or base
    src = "maxspeed" if (fwd or bwd) else "class_default"
    return (fwd * factor if fwd else default), (bwd * factor if bwd else default), src


@dataclass
class RoadGraph:
    """Directed road graph: node arrays + one row per directed edge."""

    node_ids: np.ndarray  # OSM node ids, index = graph index
    lon: np.ndarray
    lat: np.ndarray
    u: np.ndarray  # graph indices
    v: np.ndarray
    length_m: np.ndarray
    time_s: np.ndarray
    way_id: np.ndarray
    highway: np.ndarray
    path: str = "osmium+networkx"
    source: str = ""
    stats: dict[str, Any] = field(default_factory=dict)

    @property
    def n_nodes(self) -> int:
        return len(self.node_ids)

    @property
    def n_edges(self) -> int:
        return len(self.u)

    def to_networkx(self) -> nx.MultiDiGraph:
        g = nx.MultiDiGraph(crs="EPSG:4326", source=self.source, path=self.path)
        for i, (nid, x, y) in enumerate(zip(self.node_ids, self.lon, self.lat, strict=True)):
            g.add_node(i, osmid=int(nid), x=float(x), y=float(y))
        for k in range(self.n_edges):
            g.add_edge(
                int(self.u[k]),
                int(self.v[k]),
                osmid=int(self.way_id[k]),
                highway=str(self.highway[k]),
                length=float(self.length_m[k]),
                travel_time=float(self.time_s[k]),
            )
        return g

    def csr(self) -> tuple[csr_matrix, csr_matrix]:
        """(seconds, metres) CSR, parallel edges collapsed to the fastest."""
        n = self.n_nodes
        order = np.lexsort((self.time_s, self.v, self.u))
        u, v = self.u[order], self.v[order]
        keep = np.ones(len(u), bool)
        keep[1:] = (u[1:] != u[:-1]) | (v[1:] != v[:-1])
        u, v = u[keep], v[keep]
        t = np.maximum(self.time_s[order][keep], MIN_EDGE_S)
        m = self.length_m[order][keep]
        return csr_matrix((t, (u, v)), shape=(n, n)), csr_matrix((m, (u, v)), shape=(n, n))

    def largest_scc(self) -> np.ndarray:
        """Boolean mask of nodes in the largest strongly connected component."""
        t, _ = self.csr()
        _, labels = connected_components(t, directed=True, connection="strong")
        big = np.bincount(labels).argmax()
        return labels == big


def build_from_opl_lines(lines, cfg: dict[str, Any], source: str = "") -> RoadGraph:
    idx: dict[int, int] = {}
    lons: list[float] = []
    lats: list[float] = []
    eu: list[int] = []
    ev: list[int] = []
    espeed: list[float] = []
    eway: list[int] = []
    ehw: list[str] = []
    n_ways = n_kept = n_maxspeed = 0
    for line in lines:
        parsed = parse_opl_way(line)
        if parsed is None:
            continue
        n_ways += 1
        wid, tags, nodes = parsed
        if len(nodes) < 2 or not is_drivable(tags, cfg):
            continue
        n_kept += 1
        fwd_ok, bwd_ok = way_directions(tags, cfg)
        fwd, bwd, src = way_speeds(tags, cfg)
        n_maxspeed += src == "maxspeed"
        gi = []
        for nid, x, y in nodes:
            j = idx.get(nid)
            if j is None:
                j = idx[nid] = len(lons)
                lons.append(x)
                lats.append(y)
            gi.append(j)
        for a, b in zip(gi, gi[1:], strict=False):
            if a == b:
                continue
            if fwd_ok:
                eu.append(a), ev.append(b), espeed.append(fwd), eway.append(wid)
                ehw.append(tags["highway"])
            if bwd_ok:
                eu.append(b), ev.append(a), espeed.append(bwd), eway.append(wid)
                ehw.append(tags["highway"])
    lon, lat = np.asarray(lons), np.asarray(lats)
    u, v = np.asarray(eu, dtype=np.int64), np.asarray(ev, dtype=np.int64)
    if len(u):
        _, _, dist = Geod(ellps="WGS84").inv(lon[u], lat[u], lon[v], lat[v])
        length = np.asarray(dist, float)
    else:
        length = np.zeros(0)
    speed = np.asarray(espeed, float)
    time_s = length / (speed / 3.6) if len(u) else np.zeros(0)
    node_ids = np.empty(len(idx), dtype=np.int64)
    for nid, j in idx.items():
        node_ids[j] = nid
    return RoadGraph(
        node_ids=node_ids,
        lon=lon,
        lat=lat,
        u=u,
        v=v,
        length_m=length,
        time_s=time_s,
        way_id=np.asarray(eway, dtype=np.int64),
        highway=np.asarray(ehw, dtype=object),
        source=source,
        stats={"ways_read": n_ways, "ways_kept": n_kept, "ways_with_maxspeed": n_maxspeed},
    )


def osmium_opl(pbf: Path, cfg: dict[str, Any], workdir: Path) -> Path:
    """Filter drivable highways and write OPL with node locations; returns the OPL path."""
    exe = osmium_bin()
    filt = workdir / "highways.osm.pbf"
    opl = workdir / "highways.opl"
    expr = "w/highway=" + ",".join(cfg["drivable_classes"])
    subprocess.run(
        [exe, "tags-filter", str(pbf), expr, "-o", str(filt), "--overwrite", "--no-progress"],
        check=True,
        capture_output=True,
    )
    subprocess.run(
        [exe, "add-locations-to-ways", str(filt), "-f", "opl,add_metadata=false"]
        + ["-o", str(opl), "--overwrite", "--no-progress"],
        check=True,
        capture_output=True,
    )
    return opl


def osmnx_available() -> bool:
    try:
        import osmnx  # noqa: F401
    except ImportError:
        return False
    return True  # pragma: no cover - osmnx is not a project dependency


def build_graph(pbf: Path, cfg: dict[str, Any] | None = None) -> RoadGraph:
    """Drivable graph from an OSM file (.pbf/.osm/.opl readable by osmium).

    Always the osmium+networkx path: OSMnx reads only XML or Overpass, not PBF, so even when it
    is importable the PBF route is this one; `osmnx_available()` is recorded in meta.json.
    """
    cfg = cfg or load_speed_config()
    with tempfile.TemporaryDirectory(prefix="r1a-roads-") as tmp:
        opl = osmium_opl(Path(pbf), cfg, Path(tmp))
        with opl.open(encoding="utf-8") as fh:
            g = build_from_opl_lines(fh, cfg, source=str(pbf))
    g.path = "osmium+networkx"
    return g
