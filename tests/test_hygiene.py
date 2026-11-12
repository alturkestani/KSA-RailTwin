"""Repository hygiene that R0 acceptance relies on (fast, no network)."""

import csv
import re
import subprocess
import tomllib

from common import REPO_ROOT


def _tracked() -> list[str]:
    out = subprocess.run(
        ["git", "ls-files"], cwd=REPO_ROOT, capture_output=True, text=True, check=True
    )
    return out.stdout.splitlines()


def test_no_payloads_tracked() -> None:
    allowed = re.compile(r"^data/(README\.md|ksa/tables/.+)$")
    bad = [
        f
        for f in _tracked()
        if re.match(r"^(data|runs|movies|film/renders|film/audio|logs)/", f)
        and not allowed.match(f)
    ]
    assert bad == []


def test_no_absolute_home_paths_tracked() -> None:
    pat = re.compile(r"/Users/[a-z]|/home/[a-z][a-z0-9_-]*/")
    hits = []
    for f in _tracked():
        p = REPO_ROOT / f
        if not p.is_file() or p.suffix in {".parquet"}:
            continue
        text = p.read_text(encoding="utf-8", errors="ignore")
        if pat.search(text):
            hits.append(f)
    assert hits == []


def _canon(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def test_every_dependency_in_licence_register() -> None:
    pyproject = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    deps = pyproject["project"]["dependencies"] + pyproject["dependency-groups"]["dev"]
    names = {_canon(re.split(r"[<>=~!\[ ;]", d)[0]) for d in deps}
    with (REPO_ROOT / "docs" / "licences.csv").open(encoding="utf-8", newline="") as f:
        rows = {_canon(r["item"].split(" ")[0]): r for r in csv.DictReader(f)}
    missing = sorted(n for n in names if n not in rows)
    assert missing == []
    assert all(rows[n]["open"] == "Y" and rows[n]["licence"] for n in names)
