"""The locked R6 judge: a read-only copy of the demand model + appraisal (R6 design B).

`freeze` builds `judge/<name>/` from a git ref with `git archive` (a read-only git operation;
`git worktree` is not allowed in track runs, `prompts/_common.md`), APFS-clones the `runs/` inputs
the judge reads (`cp -c`, no new disk), links `data/` to the manifest-hashed data, makes the copy
read-only (`chmod -R a-w`) and writes the SHA-256 of every file to
`runs/r6/judge/<name>.hash.json`. `verify` recomputes the full hash; `fingerprint` is the fast
per-evaluation check (path, size, mtime of every file). A mismatch aborts.

  uv run python -m optimise.judge freeze --ref r5 --name v1-r5
  uv run python -m optimise.judge verify --name v1-r5

Label: synthetic demand, uncalibrated: scenario comparison, not a forecast.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import tarfile
import tempfile
from pathlib import Path

import typer

from common import REPO_ROOT
from common.labels import LABEL

JUDGE_DIR = Path("judge")
HASHES = Path("runs/r6/judge")
# runs/ inputs the demand model and the appraisal read (grep of the judge modules, R6 start)
RUN_INPUTS = (
    "runs/zones",
    "runs/skims/r3-zones",
    "runs/skims/r4-stations",
    "runs/access/running_time/factors-s1",
    "runs/r5/demand/calibration-r5-s1",
    "runs/r6/demand/calibration-p5b-s1",
    "runs/r5/demand/intl-fit-s1",
    "runs/costs",
    "runs/network-eval/costing",
)

app = typer.Typer(add_completion=False, help=__doc__, no_args_is_help=True)


@app.callback()
def _group() -> None:
    """R6 judge."""


def judge_root(name: str, root: Path = REPO_ROOT) -> Path:
    return root / JUDGE_DIR / name


def _files(base: Path) -> list[Path]:
    out = []
    for dp, dn, fn in os.walk(base, followlinks=False):
        dn[:] = sorted(d for d in dn if d not in ("__pycache__", ".pytest_cache", ".ruff_cache"))
        for f in sorted(fn):
            if f.endswith(".pyc"):
                continue
            p = Path(dp) / f
            if p.is_symlink():
                continue  # data/ links: hashed through the manifest (cities/ksa/sources.yaml)
            out.append(p)
    return out


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def full_hash(base: Path) -> tuple[str, dict[str, str]]:
    files = {str(p.relative_to(base)): sha256_file(p) for p in _files(base)}
    h = hashlib.sha256("".join(f"{k}\0{v}\n" for k, v in sorted(files.items())).encode())
    return h.hexdigest(), files


def fingerprint(base: Path) -> str:
    """Fast check: path, size and mtime of every file (an edit changes size or mtime)."""
    h = hashlib.sha256()
    for p in _files(base):
        st = p.stat()
        h.update(f"{p.relative_to(base)}\0{st.st_size}\0{st.st_mtime_ns}\n".encode())
    return h.hexdigest()


def record_path(name: str, root: Path = REPO_ROOT) -> Path:
    return root / HASHES / f"{name}.hash.json"


def load_record(name: str, root: Path = REPO_ROOT) -> dict:
    return json.loads(record_path(name, root).read_text(encoding="utf-8"))


def check_fingerprint(name: str, root: Path = REPO_ROOT) -> None:
    rec = load_record(name, root)
    fp = fingerprint(judge_root(name, root))
    if fp != rec["fingerprint"]:
        raise SystemExit(
            f"JUDGE MISMATCH: judge/{name} fingerprint {fp[:12]} != {rec['fingerprint'][:12]}"
        )


def check_full(name: str, root: Path = REPO_ROOT) -> str:
    rec = load_record(name, root)
    h, _ = full_hash(judge_root(name, root))
    if h != rec["sha256"]:
        raise SystemExit(f"JUDGE MISMATCH: judge/{name} sha256 {h[:12]} != {rec['sha256'][:12]}")
    return h


def _git(args: list[str], root: Path) -> str:
    return subprocess.run(
        ["git", *args], cwd=root, capture_output=True, text=True, check=True
    ).stdout


@app.command("freeze")
def freeze_cmd(
    ref: str = typer.Option(..., help="git ref (tag or commit) of the judge code"),
    name: str = typer.Option(..., help="judge/<name>/"),
    runs_from: Path = typer.Option(
        None, help="directory whose runs/ inputs are cloned (default: this checkout)"
    ),
    root: Path = typer.Option(REPO_ROOT, hidden=True),
) -> None:
    """Build judge/<name>/ read-only and record its hash."""
    dst = judge_root(name, root)
    if dst.exists():
        raise SystemExit(f"{dst} exists; a frozen judge is never rebuilt in place")
    commit = _git(["rev-parse", f"{ref}^{{commit}}"], root).strip()
    dst.mkdir(parents=True)
    with tempfile.TemporaryDirectory() as td:
        tar = Path(td) / "judge.tar"
        subprocess.run(["git", "archive", "-o", str(tar), commit], cwd=root, check=True)
        with tarfile.open(tar) as t:
            t.extractall(dst, filter="data")
    src_runs = (runs_from or root).resolve()
    for rel in RUN_INPUTS:
        s = src_runs / rel
        if not s.exists():
            raise SystemExit(f"judge input missing: {s}")
        (dst / rel).parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["cp", "-cR", str(s), str(dst / rel)], check=True)
    # data/: the archive holds data/README.md and data/ksa/tables; the rest is gitignored data
    # registered in the manifest, linked (never copied) and hashed through the manifest
    data = dst / "data"
    data.mkdir(exist_ok=True)
    real = (root / "data").resolve()
    for item in sorted(real.iterdir()):
        t = data / item.name
        if not t.exists():
            t.symlink_to(item.resolve() if item.is_symlink() else item)
        elif item.name == "ksa":
            for sub in sorted(item.iterdir()):
                ts = t / sub.name
                if not ts.exists():
                    ts.symlink_to(sub.resolve())
    for p in dst.rglob("__pycache__"):
        shutil.rmtree(p)
    subprocess.run(["chmod", "-R", "a-w", str(dst)], check=True)
    h, files = full_hash(dst)
    rec = {
        "label": LABEL,
        "name": name,
        "ref": ref,
        "commit": commit,
        "runs_inputs": list(RUN_INPUTS),
        "runs_from": str(src_runs.relative_to(root)) if src_runs != root.resolve() else ".",
        "data": "symlinked; hashed by the manifest (cities/ksa/sources.yaml) in every run meta",
        "n_files": len(files),
        "sha256": h,
        "fingerprint": fingerprint(dst),
        "files": files,
    }
    out = record_path(name, root)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    typer.echo(f"judge/{name}: {commit[:10]} {len(files)} files sha256 {h}")


@app.command("verify")
def verify_cmd(
    name: str = typer.Option(...), root: Path = typer.Option(REPO_ROOT, hidden=True)
) -> None:
    """Full SHA-256 check of judge/<name>/ against its record."""
    h = check_full(name, root)
    check_fingerprint(name, root)
    typer.echo(f"judge/{name} intact: sha256 {h}")


if __name__ == "__main__":
    app()
