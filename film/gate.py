"""The half-2 gate shared by voice, render, assemble and subs build (R10_HALF2, 7 Nov 2026).

Until R10_HALF2 the gate refused unconditionally. Now every half-2 command calls `require()`
before it writes anything, and the gate opens only when all of these hold:

1. the half-2 launch is recorded: `docs/status/r10.md` has a line starting with LAUNCH_MARKER
   (Tariq's explicit launch, prompts/R10_HALF2.md);
2. the output volume (/Volumes/Extreme_SSD) is mounted;
3. `film/renders` and `film/audio` resolve (through their symlinks) inside the external output
   root /Volumes/Extreme_SSD/Projects/KSA-RailTwin, so no media lands on the internal disk;
4. the output volume has at least 50 GiB free (the render gate, prompts/R10_HALF2.md DISK GATE);
5. the next write (the caller's estimate) leaves at least 10 GB free on the output volume and
   on the internal disk that holds the home directory.

Overrides for tests only: FILM_EXTERNAL_VOLUME, FILM_EXTERNAL_ROOT, FILM_HOME_VOLUME.
"""

from __future__ import annotations

import os
import shutil
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

import typer

from common import REPO_ROOT

GATE_MESSAGE = "R10 half 2 gate closed: nothing written"
LAUNCH_MARKER = "R10_HALF2 launch recorded:"
EXTERNAL_VOLUME = "/Volumes/Extreme_SSD"
EXTERNAL_ROOT = "/Volumes/Extreme_SSD/Projects/KSA-RailTwin"
RENDER_GATE_BYTES = 50 * 1024**3  # >= 50 GiB free on the output volume
FLOOR_BYTES = 10 * 1000**3  # never take either volume under 10 GB free
OUTPUT_DIRS = ("film/renders", "film/audio")


@dataclass
class GateReport:
    ok: bool
    failures: list[str] = field(default_factory=list)
    lines: list[str] = field(default_factory=list)


def _gib(n: float) -> str:
    return f"{n / 1024**3:.1f} GiB"


def evaluate(
    estimate_bytes: int = 0,
    *,
    root: Path = REPO_ROOT,
    volume: str | None = None,
    external_root: str | None = None,
    home_volume: str | None = None,
    usage: Callable[[str], object] = shutil.disk_usage,
    is_mount: Callable[[str], bool] = os.path.ismount,
) -> GateReport:
    """Check every gate condition; never writes anything."""
    volume = volume or os.environ.get("FILM_EXTERNAL_VOLUME", EXTERNAL_VOLUME)
    external_root = external_root or os.environ.get("FILM_EXTERNAL_ROOT", EXTERNAL_ROOT)
    home_volume = home_volume or os.environ.get("FILM_HOME_VOLUME", str(Path.home()))
    rep = GateReport(ok=True)
    fail = rep.failures.append

    status = root / "docs" / "status" / "r10.md"
    text = status.read_text(encoding="utf-8") if status.exists() else ""
    if not any(line.startswith(LAUNCH_MARKER) for line in text.splitlines()):
        fail(f"half-2 launch not recorded ({LAUNCH_MARKER!r} line in docs/status/r10.md)")

    mounted = is_mount(volume)
    if not mounted:
        fail(f"output volume {volume} is not mounted")

    ext = Path(external_root).resolve() if mounted else None
    for rel in OUTPUT_DIRS:
        p = root / rel
        if not p.exists():
            fail(f"{rel} does not exist (expected a symlink into {external_root})")
            continue
        real = p.resolve()
        if ext is None or not (real == ext or ext in real.parents):
            fail(f"{rel} resolves to {real}, not inside {external_root}")
        else:
            rep.lines.append(f"{rel} -> {real}")

    est = max(int(estimate_bytes), 0)
    if mounted:
        free_out = int(usage(volume).free)  # type: ignore[attr-defined]
        rep.lines.append(f"output volume {volume}: {_gib(free_out)} free; next write {_gib(est)}")
        if free_out < RENDER_GATE_BYTES:
            fail(f"output volume has {_gib(free_out)} free, below the 50 GiB render gate")
        if free_out - est < FLOOR_BYTES:
            fail(f"next write ({_gib(est)}) would take {volume} under 10 GB free")
    free_home = int(usage(home_volume).free)  # type: ignore[attr-defined]
    rep.lines.append(f"internal disk ({home_volume}): {_gib(free_home)} free")
    if free_home < FLOOR_BYTES:
        fail(f"internal disk has {_gib(free_home)} free, under the 10 GB floor")
    rep.ok = not rep.failures
    return rep


def require(estimate_bytes: int = 0, *, quiet: bool = False, **kw: object) -> GateReport:
    """Open the gate or exit 2 with the reasons (nothing written)."""
    rep = evaluate(estimate_bytes, **kw)  # type: ignore[arg-type]
    if not rep.ok:
        typer.echo(GATE_MESSAGE)
        for f in rep.failures:
            typer.echo(f"  gate: {f}")
        raise typer.Exit(2)
    if not quiet:
        for line in rep.lines:
            typer.echo(f"  gate ok: {line}")
    return rep


def refuse(message: str = GATE_MESSAGE) -> None:
    """Print a message and exit 2, with no side effects (kept for callers that must stay shut)."""
    typer.echo(message)
    raise typer.Exit(2)
